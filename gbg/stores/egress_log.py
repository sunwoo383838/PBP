"""그룹의 나간 요청 기록: (엔티티, 속성) → 요청과 결과. 스냅샷(워밍업 교류) + 실행 중 추가(Egress, Stage 5)."""
from gbg.contracts.schemas import EgressRecord


class EgressLog:
    def __init__(self, seeds: dict[str, list[EgressRecord]]):
        self._log = {g: list(rs) for g, rs in seeds.items()}

    def add(self, group: str, rec: EgressRecord):
        self._log.setdefault(group, []).append(rec)

    def all(self, group: str) -> list[EgressRecord]:
        return list(self._log.get(group, []))

    def lookup(self, group: str, entity: str, attr: str | None = None) -> list[EgressRecord]:
        return [r for r in self._log.get(group, []) if r.entity == entity and (attr is None or r.attr == attr)]

    def referral(self, group: str, entity: str, attr: str, day: int) -> str | None:
        """같은 (엔티티, 속성)의 가장 최근 referral이 가리키는 그룹. 그 뒤 그 그룹에 보낸 요청도 referral로
        돌아왔으면 유효하지 않다."""
        recs = [r for r in self.lookup(group, entity, attr) if r.day <= day]
        refs = [i for i, r in enumerate(recs) if r.status == "referral" and r.referral_to]
        if not refs:
            return None
        i = refs[-1]
        to = recs[i].referral_to
        if any(r.to_group == to and r.status == "referral" for r in recs[i + 1:]):
            return None
        return to

    def dump(self):
        return {g: [r.model_dump(mode="json") for r in rs] for g, rs in sorted(self._log.items())}
