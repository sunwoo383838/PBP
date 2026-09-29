"""경계 상태: 경계 모듈(Ingress)이 조립해 보낸 교차 문답과 제공한 버전. boundary_decision 사건으로만 쌓인다."""
from gbg.retrieval.normalize import normalize


class BoundaryLog:
    def __init__(self):
        self._log: dict[str, list[dict]] = {}

    def add(self, group: str, rec: dict):
        self._log.setdefault(group, []).append(rec)

    def lookup(self, group: str, entities: list[str]) -> list[dict]:
        """같은 엔티티를 다룬 과거 문답 (오래된 것부터)."""
        want = {normalize(e) for e in entities}
        return [r for r in self._log.get(group, []) if want & {normalize(e) for e in r["entities"]}]

    def dump(self):
        return {g: list(rs) for g, rs in sorted(self._log.items())}
