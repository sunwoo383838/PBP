"""그룹별 버전 DB. query(key, day)는 그날까지 등록된(db_day ≤ day) 최신 버전만 돌려준다.

아직 등록되지 않은 최신값(등록 지연 중)은 반환하지 않는다. 그 값은 처리한 에이전트의 이력에만 있다.
"""
from gbg.contracts.schemas import DbRecord, DbVersion


class VersionedDB:
    def __init__(self, records: dict[str, list[DbRecord]]):
        self._db = {g: {r.key: list(r.versions) for r in rs} for g, rs in records.items()}

    def add(self, group: str, key: str, version: DbVersion):
        vs = self._db.setdefault(group, {}).setdefault(key, [])
        if version.v != len(vs) + 1:
            raise ValueError(f"{group}:{key}: 버전 {version.v}가 {len(vs) + 1}번째 자리에 옴")
        vs.append(version)

    def query(self, group: str, key: str, day: int) -> DbVersion | None:
        vs = [v for v in self._db.get(group, {}).get(key, []) if v.db_day <= day]
        return vs[-1] if vs else None

    def dump(self):
        return {g: {k: [v.model_dump(mode="json") for v in vs] for k, vs in sorted(t.items())}
                for g, t in sorted(self._db.items())}
