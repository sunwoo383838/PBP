"""A2A AgentCard 형식의 card.

card는 그룹 밖에 공개되는 역량 광고다. 담을 수 있는 것은 무엇을 할 수 있고 어떤 범위를 맡는가뿐이다.
개별 건, 수치, 진행 중인 건의 내용, 내부 결정과 근거, 개인 식별 정보, 규정 세부 파라미터는 담지 않는다
(발행 전 누출 검사는 stores/cards.py).
"""
from typing import Literal

from pydantic import Field, model_validator

from ._base import Contract


class AgentSkill(Contract):
    id: str
    name: str
    description: str
    tags: list[str] = []
    examples: list[str] = []


class _Card(Contract):
    name: str
    description: str
    version: int = Field(ge=1)                  # 구조·범위 갱신마다 증가
    skills: list[AgentSkill]
    group: str


class AgentCard(_Card):
    """Direct의 요청자가 보는 card."""
    kind: Literal["agent"] = "agent"
    scope: str | None                           # 담당 범위 (부서·지역·업무 범주 수준)
    occupant: str                               # 현재 점유자 agent id


class GroupCard(_Card):
    """Routing·Ingress·I+E의 요청자와 Egress가 보는 card."""
    kind: Literal["group"] = "group"
    service_scope: str | None
    endpoint: str                               # 경계 모듈 = boundary:<group>

    @model_validator(mode="after")
    def _boundary(self):
        if self.endpoint != f"boundary:{self.group}":
            raise ValueError("그룹 card의 엔드포인트는 자기 그룹의 경계 모듈(boundary:<group>)이다")
        return self
