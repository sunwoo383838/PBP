"""그룹별 catalog: 업무 마스터 데이터(직원 이름·별칭·ID, 재고, 공급사·견적, 등록된 가승인 등).

그 그룹 구성원이 도구로 볼 수 있다. 시나리오 스냅샷에서 시작해 catalog 이벤트로 갱신된다.
키는 "<종류>/<엔티티 id>" 형식이다 (예: employees/E-SEL-1000).
"""


class Catalog:
    def __init__(self, entries: dict[str, dict]):
        self._c = {g: dict(v) for g, v in entries.items()}

    def upsert(self, group: str, key: str, value):
        self._c.setdefault(group, {})[key] = value

    def get(self, group: str, key: str):
        return self._c.get(group, {}).get(key)

    def items(self, group: str) -> list[tuple[str, object]]:
        return sorted(self._c.get(group, {}).items())

    def entity_keys(self, group: str) -> dict[str, str]:
        """엔티티 id → catalog 키."""
        return {k.split("/", 1)[1]: k for k in self._c.get(group, {}) if "/" in k}

    def dump(self):
        return {g: dict(sorted(v.items())) for g, v in sorted(self._c.items())}
