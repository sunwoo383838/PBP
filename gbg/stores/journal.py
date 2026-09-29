"""일지: 엔티티 → H0 원문 항목. 스냅샷 + 실행 중 추가(발견성 H0로 표시된 로컬 작업)."""
from gbg.contracts.schemas import JournalRecord


class Journal:
    def __init__(self, seeds: dict[str, list[JournalRecord]]):
        self._j: dict[str, dict[str, list[JournalRecord]]] = {}
        for g, recs in seeds.items():
            for r in recs:
                self.add(g, r)

    def add(self, group: str, rec: JournalRecord):
        self._j.setdefault(group, {}).setdefault(rec.entity, []).append(rec)

    def lookup(self, group: str, entity: str) -> list[JournalRecord]:
        return list(self._j.get(group, {}).get(entity, []))

    def records(self, group: str) -> list:
        return [r for ent in sorted(self._j.get(group, {})) for r in self._j[group][ent]]

    def dump(self):
        return {g: {e: [r.model_dump(mode="json") for r in rs] for e, rs in sorted(t.items())}
                for g, t in sorted(self._j.items())}
