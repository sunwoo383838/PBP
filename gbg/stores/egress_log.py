"""그룹의 나간 요청 기록: (엔티티, 속성) → 요청과 결과. 스냅샷(워밍업 교류) + 실행 중 추가(Egress, Stage 5)."""
from gbg.contracts.schemas import EgressRecord


class EgressLog:
    def __init__(self, seeds: dict[str, list[EgressRecord]]):
        self._log = {g: list(rs) for g, rs in seeds.items()}

    def add(self, group: str, rec: EgressRecord):
        self._log.setdefault(group, []).append(rec)

    def lookup(self, group: str, entity: str, attr: str | None = None) -> list[EgressRecord]:
        return [r for r in self._log.get(group, []) if r.entity == entity and (attr is None or r.attr == attr)]

    def dump(self):
        return {g: [r.model_dump(mode="json") for r in rs] for g, rs in sorted(self._log.items())}
