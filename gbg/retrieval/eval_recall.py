"""오프라인 회수율 평가 (LLM 없음). worldgen 4.2 private 원장(gold.jsonl, fragments.jsonl)을 읽는 오프라인 도구다.

원격 need의 결정 필수 성분 중 이력에만 있는 조각(frag 출처)에 대해 두 가지를 잰다.
    index   정확 조회(색인 + catalog 한 단계, 라우터와 공통)가 조각에 닿는가: 조각 원문이 일지 결과에 있거나(H0),
            조각 보유자가 처리자 목록에 있다(H1). H0·H1 90% 기준은 이 수치에 적용한다.
    hybrid, bm25  게이트웨이 증거 블록에 조각 원문이 들어가는가.
발견성(H0/H1/H2)별, 일차별로 보고한다. H2는 기준 없이 보고만 한다.

- 조각의 위치: fragments.jsonl의 원문이 들어 있는 보유자 이력 항목, 또는 같은 원문의 일지 항목.
- 질의: need의 엔티티 표면형(ID + catalog 이름·별칭) + 속성 키워드. semantic key(그룹/…/…)에서 알려진 엔티티(catalog·
  DB에 있는 ID나 부서)인 칸을 엔티티로, 나머지 칸을 속성으로 본다. 위치는 형식마다 다르다(예: IT-SEL/eligibility/E-SEL-1019).
"""
from collections import defaultdict
from dataclasses import asdict, dataclass

from .evidence import build_evidence
from .hybrid import GroupRetriever
from .lookup import index_lookup
from .normalize import normalize


@dataclass(frozen=True)
class Case:
    task_id: str
    need: str
    group: str
    day: int
    round: int
    disc: str
    fid: str
    query: str
    entities: tuple[str, ...]
    attr: str
    text: str                                   # 조각 원문
    holders: tuple[str, ...]


def _critical(need: dict) -> set[str] | None:
    crit = need.get("critical_components")
    if crit is None:
        return None
    return {c if isinstance(c, str) else c.get("fid") for c in crit}


def parse_sem(sem: str, names: dict[str, list[str]]) -> tuple[tuple[str, ...], str]:
    """semantic key → (엔티티들, 속성). names에 있는 칸이 모두 엔티티다 (예: PROC-SEL/quotes/laptop → laptop)."""
    parts = sem.split("/")[1:]
    ents = tuple(dict.fromkeys(p for p in parts if p in names))
    attr = " ".join(p for p in parts if p not in ents)
    return ents, attr


def build_cases(gold: list[dict], fragments: dict[str, dict], names: dict[str, list[str]] | None = None
                ) -> tuple[list[Case], dict[str, int]]:
    """names: 알려진 엔티티 → 표면형(이름·별칭). 없으면 semantic key의 두 번째 칸을 엔티티로 본다."""
    cases, skipped = [], defaultdict(int)
    for g in gold:
        for n in g["needs"]:
            if n.get("local"):
                continue
            if names is None:
                parts = n["sem"].split("/")
                ents, attr = ((parts[1],) if len(parts) > 2 else ()), parts[-1]
            else:
                ents, attr = parse_sem(n["sem"], names)
            surface = " ".join(dict.fromkeys(x for e in ents for x in [*(names or {}).get(e, []), e]))
            crit = _critical(n)
            for s in n["sources"]:
                if s["type"] != "frag":
                    continue
                fid = s["frag"]["fid"]
                if crit is not None and fid not in crit:
                    skipped["not_critical"] += 1
                    continue
                f = fragments.get(fid)
                if f is None or not f.get("text"):
                    skipped["no_fragment_text"] += 1
                    continue
                holders = tuple(sorted({h["agent"] for h in s["frag"].get("holders", [])} | {f["agent"]}))
                cases.append(Case(g["wid"], n["sem"], n["group"], g["day"], g.get("round", 0),
                                  s["frag"].get("disc") or f.get("disc", "?"),
                                  fid, f"{surface} {attr.replace('_', ' ')}".strip(), ents,
                                  attr, f["text"], holders))
    cases.sort(key=lambda c: (c.day, c.round, c.task_id, c.fid))
    return cases, dict(skipped)


def hit(items, case: Case) -> bool:
    """증거 블록에 조각 원문이 들어간 항목(이력 줄 또는 일지 항목)이 있는가."""
    want = normalize(case.text)
    return any(want in normalize(it.text) for it in items)


def index_hit(retriever: GroupRetriever, case: Case) -> bool:
    lk = index_lookup(retriever.stores, case.group, list(case.entities), retriever.p.catalog_link_fields)
    want = normalize(case.text)
    return any(want in normalize(x.text) for x in lk.journal) or bool(set(case.holders) & set(lk.holders))


async def evaluate(retrievers: dict[str, GroupRetriever], cases: list[Case], modes=("hybrid", "bm25"),
                   advance=None) -> dict:
    """advance(case)가 있으면 사례마다 그 과제 도착 직전까지의 세계를 반영한 뒤 평가한다 (사례는 시간순)."""
    report = {"cases": len(cases), "modes": {}}
    modes = ("index", *modes)
    by_mode = {m: [] for m in modes}
    for c in cases:
        if advance:
            advance(c)
        by_mode["index"].append({**asdict(c), "hit": index_hit(retrievers[c.group], c), "cap_reached": False})
        for mode in modes[1:]:
            ev = await build_evidence(retrievers[c.group], c.query, list(c.entities), mode)
            by_mode[mode].append({**asdict(c), "hit": hit(ev.items, c), "cap_reached": ev.cap_reached})
    for mode in modes:
        rows = by_mode[mode]
        by = lambda key: {k: _rate([r for r in rows if r[key] == k]) for k in sorted({r[key] for r in rows})}
        report["modes"][mode] = {"recall": _rate(rows), "by_disc": by("disc"), "by_day": by("day"), "rows": rows}
    return report


def _rate(rows: list[dict]) -> dict:
    return {"n": len(rows), "hit": sum(r["hit"] for r in rows),
            "recall": round(sum(r["hit"] for r in rows) / len(rows), 4) if rows else None}
