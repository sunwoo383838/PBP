"""오프라인 회수율 평가 (LLM 없음).

원격 need 중 이력에만 있는 조각(frag 출처)에 대해 질의를 만들어, 증거 블록에 그 조각이 담긴 이력 항목이 들어가는지 본다.
발견성(H0/H1/H2)별, 일차별, BM25 단독 대 하이브리드로 보고한다.

- 조각의 위치: 조각의 카나리 값이 원문에 들어 있는 그룹 이력 항목 (쉼표·공백을 지운 정규화 매칭).
  카나리가 없는 조각은 측정하지 않고 skipped로 센다.
- 발견성: 그 항목이 일지에 있으면 H0, 활동 색인에 있으면 H1, 둘 다 없으면 H2.
- 질의: need의 엔티티 표면형(그 그룹 별칭표의 첫 이름) + 속성 키워드 (semantic_key = 그룹/엔티티/속성).
"""
from collections import defaultdict
from dataclasses import asdict, dataclass

from gbg.contracts.schemas import GoldRecord, TimelineEvent

from .evidence import build_evidence, contains, entry_matches
from .hybrid import GroupRetriever


@dataclass(frozen=True)
class Case:
    task_id: str
    need_id: str
    group: str
    day: int
    disc: str
    fid: str
    query: str
    entities: tuple[str, ...]
    attr: str
    targets: tuple[tuple[str, int], ...]


def build_cases(stores, tasks: dict[str, TimelineEvent], gold: list[GoldRecord],
                aliases: dict[str, dict[str, list[str]]]) -> tuple[list[Case], dict[str, int]]:
    cases, skipped = [], defaultdict(int)
    for g in gold:
        task = tasks.get(g.task_id)
        if task is None or task.kind != "cross":
            continue
        for n in g.needs:
            if n.state_class is None:                                   # 로컬 need
                continue
            parts = n.semantic_key.split("/")
            entity, attr = (parts[1] if len(parts) > 2 else None), parts[-1]
            surface = (aliases.get(n.group, {}).get(entity) or [entity])[0] if entity else ""
            agents = sorted(a for a, (grp, _) in stores.members.items() if grp == n.group)
            journal = {(r.agent, r.seq) for r in stores.journal.records(n.group)}
            activity = {(r.agent, r.seq) for r in stores.activity.records(n.group)}
            for s in n.sources:
                if s.type != "frag":
                    continue
                if not s.canary:
                    skipped["no_canary"] += 1
                    continue
                targets = tuple((a, e.seq) for a in agents for e in stores.history.entries(a)
                                if e.day <= task.day and entry_matches(e, s.canary))
                if not targets:
                    skipped["unlocatable"] += 1
                    continue
                disc = "H0" if any(t in journal for t in targets) else ("H1" if any(t in activity for t in targets) else "H2")
                cases.append(Case(g.task_id, n.need_id, n.group, task.day, disc, s.fid,
                                  f"{surface} {attr.replace('_', ' ')}".strip(), (entity,) if entity else (), attr, targets))
    return cases, dict(skipped)


async def evaluate(retrievers: dict[str, GroupRetriever], cases: list[Case], modes=("hybrid", "bm25")) -> dict:
    report = {"cases": len(cases), "modes": {}}
    for mode in modes:
        rows = []
        for c in cases:
            ev = await build_evidence(retrievers[c.group], c.query, list(c.entities), c.attr, mode)
            rows.append({**asdict(c), "hit": contains(ev.items, list(c.targets)), "cap_reached": ev.cap_reached})
        by = lambda key: {k: _rate([r for r in rows if r[key] == k]) for k in sorted({r[key] for r in rows})}
        report["modes"][mode] = {"recall": _rate(rows), "by_disc": by("disc"), "by_day": by("day"), "rows": rows}
    return report


def _rate(rows: list[dict]) -> dict:
    return {"n": len(rows), "hit": sum(r["hit"] for r in rows),
            "recall": round(sum(r["hit"] for r in rows) / len(rows), 4) if rows else None}
