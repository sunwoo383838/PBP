"""도구 등록부. 도구마다 필요한 자원을 선언하고, 접근 가드가 호출 전에 그 자원을 확인한다."""
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from gbg.contracts.access import AccessTable
from gbg.contracts.conditions import ConfigError


@dataclass(frozen=True)
class Resource:
    name: str                                   # 접근 표의 자원 이름
    action: Literal["r", "w"]
    target: str | None = None                   # 대상 그룹·에이전트를 담은 인자 이름. None이면 호출자 자신의 것


@dataclass(frozen=True)
class ToolCall:
    """도구 함수가 받는 호출 정보."""
    agent: str
    group: str
    day: int
    round: int
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    resources: tuple[Resource, ...]
    fn: Callable[[ToolCall], Any]

    async def invoke(self, call: ToolCall):
        out = self.fn(call)
        return await out if inspect.isawaitable(out) else out


class ToolRegistry:
    def __init__(self, access: AccessTable):
        self.access = access
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ConfigError(f"도구 '{tool.name}' 중복 등록")
        for r in tool.resources:
            if r.name not in self.access.spec.resources:
                raise ConfigError(f"도구 '{tool.name}': 접근 표에 없는 자원 '{r.name}'")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)
