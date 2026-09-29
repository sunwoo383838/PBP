"""그룹 색인 (경계 모듈 전용): 일지(H0 원문), 활동 흔적(H1 "누가 무엇을 처리"), 엔티티 → 처리자.

시나리오 스냅샷에서 시작해 하루 끝 index 이벤트로 늘어난다. 에이전트는 이 색인을 읽을 수 없다(접근 표).
"""
from gbg.contracts.schemas import IndexEntry


class GroupIndex:
    def __init__(self, journal: dict[str, list[IndexEntry]], activity: dict[str, list[IndexEntry]],
                 entity: dict[str, dict[str, list[str]]]):
        self._j = {g: list(v) for g, v in journal.items()}
        self._a = {g: list(v) for g, v in activity.items()}
        self._e = {g: {k: list(v) for k, v in m.items()} for g, m in entity.items()}

    def add(self, group: str, kind: str, entry: IndexEntry):
        if kind == "journal":
            self._j.setdefault(group, []).append(entry)
        elif kind == "activity":
            self._a.setdefault(group, []).append(entry)
        else:
            raise ValueError(f"알 수 없는 색인 종류 '{kind}'")
        for e in entry.entities:
            agents = self._e.setdefault(group, {}).setdefault(e, [])
            if entry.agent not in agents:
                agents.append(entry.agent)

    def journal(self, group: str) -> list[IndexEntry]:
        return list(self._j.get(group, []))

    def activity(self, group: str) -> list[IndexEntry]:
        return list(self._a.get(group, []))

    def holders(self, group: str, entity: str) -> list[str]:
        return list(self._e.get(group, {}).get(entity, []))

    def entities(self, group: str) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._e.get(group, {}).items()}

    def dump(self):
        d = lambda m: {g: [e.model_dump(mode="json") for e in v] for g, v in sorted(m.items())}
        return {"journal": d(self._j), "activity": d(self._a),
                "entity": {g: dict(sorted(m.items())) for g, m in sorted(self._e.items())}}
