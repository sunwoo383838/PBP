"""공개 시나리오 형식(contracts/schemas.py 모듈 docstring)을 읽는 어댑터 기반.

load는 public/ 디렉터리만 받고, 그 밖의 경로(private/, 시나리오 루트, 상위 경로)는 예외로 거부한다.
"""
import json
from collections.abc import Iterator
from pathlib import Path

from gbg.contracts.schemas import (
    GroupInit, GroupSnapshot, GroupSpec, Need, RuleText, TimelineEvent, ToolSpec, Verdict, WorldInit,
)


class PrivateAccessError(PermissionError):
    """실행 코드가 공개분 밖(특히 private/)을 읽으려 함."""


class PublicScenarioAdapter:
    name = "public"

    def load(self, public_dir: Path) -> None:
        pub = Path(public_dir).resolve()
        if pub.name != "public" or "private" in pub.parts:
            raise PrivateAccessError(f"{public_dir}: 공개분(public/) 디렉터리만 로드한다")
        self._pub = pub
        self._world = WorldInit.model_validate_json(self.read_public("world_init.json"))
        if self._world.benchmark != self.name:
            raise ValueError(f"{pub}: {self._world.benchmark} 시나리오를 {self.name} 어댑터로 읽음")
        self._rules = [RuleText.model_validate(x) for x in json.loads(self.read_public("rulebook.json"))]
        self._snap = {g.id: GroupSnapshot.model_validate_json(self.read_public(f"snapshot_day0/{g.id}.json"))
                      for g in self._world.groups}
        rows = [TimelineEvent.model_validate_json(x)
                for f in ("timeline.jsonl", "work.jsonl") for x in self.read_public(f).splitlines() if x]
        self._events = sorted(rows, key=lambda e: e.seq)
        self._aliases = {g: self._alias_table(s) for g, s in self._snap.items()}

    def read_public(self, rel: str) -> str:
        path = (self._pub / rel).resolve()
        if not path.is_relative_to(self._pub) or "private" in path.parts:
            raise PrivateAccessError(f"{rel}: 공개분 밖의 경로")
        return path.read_text(encoding="utf-8")

    # ── BenchmarkAdapter ──
    def groups(self) -> list[GroupSpec]:
        return list(self._world.groups)

    def initial_state(self, group: str) -> GroupInit:
        s = self._snap[group]
        return GroupInit(**s.model_dump(), rules=[r for r in self._rules if r.group == group])

    def events(self) -> Iterator[TimelineEvent]:
        return iter(self._events)

    def env_tools(self) -> list[ToolSpec]:
        return []

    def make_tools(self, stores) -> list:
        """env_tools()의 명세에 구현을 붙인 커널 도구."""
        return []

    def tag(self, group: str, text: str) -> list[str]:
        """정확 일치 태깅: 그룹 별칭표의 엔티티 id와 별칭이 원문에 그대로 있으면 태그 (별칭 해소는 Stage 4)."""
        return sorted({e for surface, e in self._aliases.get(group, []) if surface in text})

    @staticmethod
    def _alias_table(snap: GroupSnapshot) -> list[tuple[str, str]]:
        pairs = {(e, e) for e in snap.aliases} | {(a, e) for e, al in snap.aliases.items() for a in al}
        return sorted(pairs, key=lambda p: (-len(p[0]), p))

    # 오프라인 채점은 Stage 7
    def verify(self, task_id: str, answer: dict, private_dir: Path) -> Verdict:
        raise NotImplementedError("Stage 7")

    def needs(self, task_id: str, private_dir: Path) -> list[Need] | None:
        raise NotImplementedError("Stage 7")
