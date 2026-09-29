"""활동 색인: 엔티티 → (에이전트, 이력 항목 seq, 날짜, 역할). 그룹 내부 전용.

로컬 작업의 답이 커밋될 때 그 작업의 엔티티 태그로 갱신한다.
"""
from gbg.contracts.schemas import ActivityRecord


class ActivityIndex:
    def __init__(self, seeds: dict[str, list[ActivityRecord]]):
        self._idx: dict[str, dict[str, list[ActivityRecord]]] = {}
        for g, recs in seeds.items():
            for r in recs:
                self.add(g, r)

    def add(self, group: str, rec: ActivityRecord):
        self._idx.setdefault(group, {}).setdefault(rec.entity, []).append(rec)

    def lookup(self, group: str, entity: str) -> list[ActivityRecord]:
        return list(self._idx.get(group, {}).get(entity, []))

    def by_agent(self, group: str) -> dict[str, list[ActivityRecord]]:
        out: dict[str, list[ActivityRecord]] = {}
        for ent in sorted(self._idx.get(group, {})):
            for r in self._idx[group][ent]:
                out.setdefault(r.agent, []).append(r)
        return out

    def records(self, group: str) -> list:
        return [r for ent in sorted(self._idx.get(group, {})) for r in self._idx[group][ent]]

    def dump(self):
        return {g: {e: [r.model_dump(mode="json") for r in rs] for e, rs in sorted(t.items())}
                for g, t in sorted(self._idx.items())}
