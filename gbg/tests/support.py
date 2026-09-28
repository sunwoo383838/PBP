"""테스트 전용 도우미: 공개 시나리오 형식을 그대로 읽는 최소 어댑터.

실제 벤치마크 어댑터(load, private 거부, 태깅)는 Stage 2에서 gbg/benchmarks/<name>/에 만든다.
"""
import json
from pathlib import Path

from gbg.contracts.schemas import GroupInit, GroupSnapshot, RuleText, TimelineEvent, WorldInit

FIXTURES = Path(__file__).parent / "fixtures"


class PublicScenarioAdapter:
    def __init__(self, name: str):
        self.name = name
        self.load(FIXTURES / name / "public")

    def load(self, public_dir):
        pub = Path(public_dir)
        self._world = WorldInit.model_validate_json((pub / "world_init.json").read_text(encoding="utf-8"))
        self._rules = [RuleText.model_validate(x) for x in json.loads((pub / "rulebook.json").read_text(encoding="utf-8"))]
        self._snap = {p.stem: GroupSnapshot.model_validate_json(p.read_text(encoding="utf-8"))
                      for p in (pub / "snapshot_day0").glob("*.json")}
        rows = []
        for f in ("timeline.jsonl", "work.jsonl"):
            rows += [TimelineEvent.model_validate_json(x) for x in (pub / f).read_text(encoding="utf-8").splitlines() if x]
        self._events = sorted(rows, key=lambda e: e.seq)

    def groups(self):
        return list(self._world.groups)

    def initial_state(self, group):
        s = self._snap[group]
        return GroupInit(**s.model_dump(), rules=[r for r in self._rules if r.group == group])

    def events(self):
        return iter(self._events)

    def env_tools(self):
        return []

    def tag(self, group, text):
        return []

    def verify(self, task_id, answer, private_dir):
        raise NotImplementedError

    def needs(self, task_id, private_dir):
        return None
