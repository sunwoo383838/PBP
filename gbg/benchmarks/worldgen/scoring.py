"""worldgen 채점 입력 (오프라인 전용): private 원장 적재, 정답 판정(verify), need 목록.
실행 프로세스는 이 모듈을 쓰지 않는다 (private/은 채점기만 읽는다).
"""
import json
from dataclasses import dataclass
from pathlib import Path

from .adapter import WorldgenAdapter


@dataclass
class Private:
    tasks: dict                                 # wid → TimelineEvent (교차 작업, max_day까지)
    gold: dict                                  # wid → 정답 원장 행
    fragments: dict                             # fid → 조각
    names: dict                                 # 엔티티 id → 이름·별칭 (catalog)
    seed: int | None


def _jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def load_private(scenario: Path, max_day: int | None = None) -> Private:
    a = WorldgenAdapter()
    a.load(scenario / "harness")
    tasks = {e.task_id: e for e in a.events() if e.kind == "cross" and (max_day is None or e.day <= max_day)}
    gold = {g["wid"]: g for g in _jsonl(scenario / "private" / "gold.jsonl") if g["wid"] in tasks}
    frags = {f["fid"]: f for f in _jsonl(scenario / "private" / "fragments.jsonl")}
    names: dict[str, list[str]] = {}
    for items in json.loads((scenario / "harness" / "snapshot_day0" / "catalog.json").read_text(encoding="utf-8")).values():
        for k, v in items.items():
            if isinstance(v, dict):
                names.setdefault(k.split("/", 1)[1], []).extend(x for x in (v.get("name"), v.get("alias")) if x)
    return Private(tasks, gold, frags, names, a.manifest.get("params", {}).get("seed"))


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
