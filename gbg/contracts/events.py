"""WAL 사건. 커밋 순서는 (작업 id, 사건 순번)으로 고정되고 seq가 그 순서다."""
from typing import Literal

from pydantic import Field, JsonValue

from ._base import Contract

EventType = Literal[
    "task_delivered", "llm_call", "tool_call", "tool_result", "message", "answer",
    "boundary_decision", "retrieval", "round_commit", "agent_join", "agent_leave",
]


class Event(Contract):
    seq: int = Field(ge=1)
    day: int = Field(ge=0)
    round: int = Field(ge=0)
    type: EventType
    actor: str                                  # agent:<id> | boundary:<group> | kernel
    payload: dict[str, JsonValue]
