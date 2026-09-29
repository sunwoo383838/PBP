"""그룹별 버전 DB. 버전은 등록 이벤트로 들어오며 순서가 버전 순서와 다를 수 있고 빈틈도 있다.

query(key, day)는 그날까지 등록된(db_day ≤ day) 버전 중 **가장 큰 버전**을 돌려준다.
아직 등록되지 않은 최신값은 반환하지 않는다. 그 값은 처리한 에이전트의 이력에만 있다.
"""
from gbg.contracts.schemas import DbRecord, DbVersion


class VersionedDB:
    def __init__(self, records: dict[str, list[DbRecord]]):
        self._db: dict[str, dict[str, dict[int, DbVersion]]] = {}
        for g, rs in records.items():
            for r in rs:
                for v in r.versions:
                    self.add(g, r.key, v)

    def add(self, group: str, key: str, version: DbVersion):
        vs = self._db.setdefault(group, {}).setdefault(key, {})
        if version.v in vs:
            raise ValueError(f"{group}:{key}: 버전 {version.v}가 이미 등록됨")
        vs[version.v] = version

    def groups(self) -> list[str]:
        return sorted(self._db)

    def keys(self, group: str) -> list[str]:
        return sorted(self._db.get(group, {}))

    def versions(self, group: str, key: str) -> list[DbVersion]:
        """등록된 전체 버전 (버전 순). 에이전트 조회 경로는 query만 쓴다."""
        vs = self._db.get(group, {}).get(key, {})
        return [vs[v] for v in sorted(vs)]

    def query(self, group: str, key: str, day: int) -> DbVersion | None:
        vs = [v for v in self.versions(group, key) if v.db_day <= day]
        return max(vs, key=lambda v: v.v) if vs else None

    def dump(self):
        return {g: {k: [v.model_dump(mode="json") for v in self.versions(g, k)] for k in sorted(t)}
                for g, t in sorted(self._db.items())}
