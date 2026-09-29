"""worldgen 채점 입력 (오프라인 전용): private 원장 적재, 정답 판정(verify), need 목록.
실행 프로세스는 이 모듈을 쓰지 않는다 (private/은 채점기만 읽는다).
"""
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .adapter import WorldgenAdapter


@dataclass
class Private:
    tasks: dict                                 # wid → TimelineEvent (교차 작업, max_day까지)
    gold: dict                                  # wid → 정답 원장 행
    fragments: dict                             # fid → 조각
    names: dict                                 # 엔티티 id → 이름·별칭 (catalog, 실행 중 catalog, 조각 target)
    seed: int | None
    computed: dict = None                       # wid → sem → [(엔티티 표면형, 허용 값들)] (계산형 need의 중간값)


def _jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_private(scenario: Path, max_day: int | None = None) -> Private:
    a = WorldgenAdapter()
    a.load(scenario / "harness")
    tasks = {e.task_id: e for e in a.events() if e.kind == "cross" and (max_day is None or e.day <= max_day)}
    gold = {g["wid"]: g for g in _jsonl(scenario / "private" / "gold.jsonl") if g["wid"] in tasks}
    frags = {f["fid"]: f for f in _jsonl(scenario / "private" / "fragments.jsonl")}
    names: dict[str, list[str]] = {}

    def add(ent, *xs):
        for x in xs:
            if x and x != ent and x not in names.setdefault(ent, []):
                names[ent].append(x)
    for items in json.loads((scenario / "harness" / "snapshot_day0" / "catalog.json").read_text(encoding="utf-8")).values():
        for k, v in items.items():
            if isinstance(v, dict):
                add(k.split("/", 1)[1], v.get("name"), v.get("alias"))
    for e in _jsonl(scenario / "harness" / "timeline.jsonl"):             # 실행 중 catalog (입사자·새 품목)
        if e.get("type") == "catalog_upsert" and isinstance(e.get("value"), dict):
            add(e["key"].split("/", 1)[1], e["value"].get("name"), e["value"].get("alias"))
    for f in frags.values():                                               # 조각 target의 이름 (이름 필드 없는 품목 포함)
        parts = (f.get("key") or "").split("/")
        if len(parts) > 2 and (n := target_name(f.get("target") or "")):
            add(parts[2], n)
    computed = {}
    if (scenario / "private" / "db_versions.jsonl").exists() and (scenario / "private" / "rulebook_full.json").exists():
        versions = defaultdict(dict)
        for x in _jsonl(scenario / "private" / "db_versions.jsonl"):
            versions[x["key"]][x["v"]] = x
        rules = json.loads((scenario / "private" / "rulebook_full.json").read_text(encoding="utf-8"))
        computed = {w: need_values(g, frags, versions, rules) for w, g in gold.items()}
    return Private(tasks, gold, frags, names, a.manifest.get("params", {}).get("seed"), computed)


_TARGET = [re.compile(p) for p in (r"^(?:HR record|Transfer|Equipment tier|Offer|Hire) of (.+)$", r"^In-house stock (.+)$",
                                     r"^(.+) capex(?: balance)?$", r"^(.+) seats$")]


def target_name(target: str) -> str | None:
    """조각 target에서 엔티티 이름: 'HR record of Ok Dain' → 'Ok Dain', 'In-house stock laptop (basic)' → 'laptop (basic)'."""
    for p in _TARGET:
        if m := p.match(target.strip()):
            return m.group(1).strip()
    return None


# ─────────────────────────── 계산형 need의 중간값 (worldgen tracing.py와 같은 계산) ───────────────────────────
def need_values(g: dict, frags: dict, versions: dict, rules: dict) -> dict:
    """sem → [(엔티티 표면형들, 허용 값들)]. 계산형 need(집행 가능액·가용 좌석·가용 재고·배분 인원)만.
    출처(sources)에 기록된 버전과 조각 값으로 tracing.py의 fin_available·it_free·it_stock·it_inventory·hr_headcount를
    다시 계산한다. 출처가 모자라 계산할 수 없으면 뺀다."""
    out = {}
    for n in g["needs"]:
        try:
            v = _need_value(n, g, frags, versions, rules)
        except (KeyError, StopIteration, TypeError, IndexError):
            v = None
        if v:
            out[n["sem"]] = v
    return out


def _val(s: dict, versions: dict):
    return versions[s["key"]][s["v"]]["value"]


def _frag_sources(n: dict, frags: dict, suffix: str) -> list[dict]:
    return [frags[s["frag"]["fid"]] for s in n["sources"] if s["type"] == "frag" and s.get("role") != "distractor"
            and (frags[s["frag"]["fid"]].get("key") or "").endswith(suffix)]


def _need_value(n: dict, g: dict, frags: dict, versions: dict, rules: dict):
    grp, parts, day = n["group"], n["sem"].split("/"), g["day"]
    keyed = {s["key"]: s for s in n["sources"] if s.get("key") and "v" in s}
    if parts[-1] == "budget_schedule":                                     # fin_available: 잔액 − 기간 안 차감 대상
        dept = parts[1]
        rem = _val(keyed[f"{grp}/line/{dept}/remaining"], versions)
        pol = rules[f"{grp}.pending_deduction"]["params"]
        q = next(s for s in n["sources"] if s["type"] == "db_query" and s.get("query", "").startswith("SELECT commit"))
        reads = {k: v for k, v in q.get("reads", [])}
        pend = []
        for x in q["result"]:
            if x.startswith("earmark:"):
                e = frags[x.split(":", 1)[1]]["value"]
                pend.append((e["amount"], e["end"]))
                continue
            key = f"{grp}/commit/{x}/status"
            if key in keyed:
                st = _val(keyed[key], versions)
            elif key in reads:
                st = versions[key][reads[key]]["value"]
            else:
                st = next(frags[s["frag"]["fid"]]["value"] for s in n["sources"] if s["type"] == "frag"
                          and frags[s["frag"]["fid"]].get("key") == key)
            last = st["expected_settle"] - (1 if pol["deduct_until"] == "day_before_settle" else 0)
            pend.append((st["amount"], last))
        return [([dept], [rem - sum(a for a, last in pend if last >= day)])]
    if parts[1] == "license":                                              # it_free: 좌석 − 사용 − 기간 안 예약
        sw = parts[2]
        v = _val(keyed[f"{grp}/lic/{sw}/seats"], versions)
        free = v["seats"] - v["used"] - sum(f["value"]["n"] for f in _frag_sources(n, frags, "/reserve"))
        return [([sw], sorted({free, max(0, free)}))]
    if parts[1] in ("stock", "inventory"):                                 # it_stock / it_inventory: 수량 − 유효 홀드
        out = []
        for key, s in sorted(keyed.items()):
            if not key.endswith("/qty"):
                continue
            iid = key.split("/")[2]
            holds = [f for f in _frag_sources(n, frags, "/hold") if f["key"].split("/")[2] == iid]
            if holds or parts[1] == "stock":
                q = (_val(s, versions) or 0) - len(holds)
                out.append(([iid], sorted({q, max(0, q)})))
        return out or None
    if parts[-1].startswith("planning_headcount"):                         # hr_headcount: 등록 인원 ± 발효 이동 + 입사 확정
        dept = parts[1]
        q = next(s for s in n["sources"] if s["type"] == "db_query" and s.get("query", "").startswith("COUNT("))
        adj = sum(1 if f["value"]["to"] == dept else -1 for f in _frag_sources(n, frags, "/transfer"))
        adj += len(_frag_sources(n, frags, "/start"))
        if not adj and not any(s["type"] == "frag" for s in n["sources"]):
            return None
        return [([dept], [q["result"] + adj])]
    return None


def _norm_slot(slot, v):
    if v is None:
        return None
    if slot.type == "set":
        return sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in v)
    if slot.type in ("int", "number") and isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def verify(task, answer: dict | None, gold_row: dict) -> dict:
    """닫힌 슬롯 전부 일치 = exact. 답이 없으면(제출 실패) 모든 슬롯 오답."""
    slots = task.output_schema.slots
    want = gold_row["gold"]
    hits = {s.name: answer is not None and _norm_slot(s, answer.get(s.name)) == _norm_slot(s, want.get(s.name))
            for s in slots}
    return {"exact": bool(hits) and all(hits.values()), "slots": hits}


def strata(gold_row: dict) -> dict:
    """층화 보고용 과제 속성."""
    return {"class": gold_row.get("state_class"), "c_ops": bool(gold_row.get("c_ops")),
            "template": gold_row.get("template"), "max_holders": gold_row.get("max_holders"),
            "n_groups": gold_row.get("n_groups"), "day": gold_row.get("day"),
            "critical_disc": sorted((gold_row.get("critical_disc") or {}).keys())}
