"""조건 설정 (configs/conditions.yaml). 사다리 4단과 참조 행을 이 설정만으로 전환한다.

defaults(과제 예산, 최종 답변 예약, 요청자 권한)는 모든 조건에 똑같이 적용되고 조건별로 바꿀 수 없다.
"""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, ValidationError, model_validator

from ._base import Contract


class ConfigError(ValueError):
    """설정 파일이 계약을 어김: 없는 이름, 선언 밖 키, 모순된 조합."""


class Budget(Contract):
    calls: int | None = Field(ge=1)             # B_CALLS, None = 상한 없음
    tokens: int | None = Field(ge=1)            # B_TOKENS


class FinalReserve(Contract):
    calls: int = Field(ge=1)                    # 최종 답변용 호출 (최소 1)
    tokens: int = Field(ge=0)


class RequesterPolicy(Contract):
    max_asks: int | None = Field(ge=1)          # None = 예산 안에서 무제한
    requery: bool                               # 같은 대상에게 같은 질문을 다시 할 수 있는가


class Defaults(Contract):
    budget: Budget
    final_reserve: FinalReserve
    requester: RequesterPolicy

    @model_validator(mode="after")
    def _reserve_fits(self):
        b, r = self.budget, self.final_reserve
        if b.calls is not None and b.calls <= r.calls:
            raise ValueError("budget.calls는 final_reserve.calls보다 커야 한다")
        if b.tokens is not None and b.tokens <= r.tokens:
            raise ValueError("budget.tokens는 final_reserve.tokens보다 커야 한다")
        return self


class IngressConfig(Contract):
    fanout: int = Field(ge=0)                   # 담당자 수 상한 (0 = 보유자 목록만 공개)
    assemble: bool                              # 증거 + 응답으로 조립 (LLM ②)
    requery: bool                               # 빠진 항목 재질의 1회
    reveal_holders: bool = False                # 보유자 목록만 돌려주고 요청자가 직접 묻는다
    boundary_state: bool = False                # 경계 상태(과거 교차 문답·제공 버전·진행 중 요청)를 조립에 쓴다
    version_marks: bool = False                 # 조립 답에 버전 표시 (같은 DB 키·버전 번호로 묶은 사실)

    @model_validator(mode="after")
    def _reveal(self):
        if (self.fanout == 0) != self.reveal_holders:
            raise ValueError("fanout 0은 reveal_holders=true일 때만, reveal_holders=true는 fanout 0일 때만 허용한다")
        if self.reveal_holders and (self.assemble or self.requery):
            raise ValueError("reveal_holders는 조립·재질의 없이 보유자 목록만 돌려준다")
        if not self.assemble and (self.requery or self.boundary_state or self.version_marks):
            raise ValueError("재질의·경계 상태·버전 표시는 조립(assemble)하는 게이트웨이에만 있다")
        return self


class EgressConfig(Contract):
    history: bool                               # egress_log 기록을 관련 기록으로 제공


class Condition(Contract):
    agent_tool: Literal["ask_agent", "ask_group", "ask"]
    directory: Literal["agent_cards", "group_cards"]
    card_mode: Literal["static", "dynamic"] = "static"
    responder_session: Literal["persistent", "ephemeral"] = "persistent"
    ingress: IngressConfig | None
    egress: EgressConfig | None
    blocked: str | None = None                  # 설정에는 있지만 실행기가 거부하는 조건 (사유)

    @model_validator(mode="after")
    def _consistent(self):
        direct = self.agent_tool == "ask_agent"
        if direct != (self.directory == "agent_cards"):
            raise ValueError("ask_agent는 에이전트 card 디렉터리와, 그룹 도구는 그룹 card 디렉터리와 짝이다")
        if direct and (self.ingress or self.egress):
            raise ValueError("Direct 요청은 경계 모듈을 지나지 않는다")
        if not direct and self.ingress is None:
            raise ValueError("그룹에 묻는 조건은 받는 쪽 Ingress가 있어야 한다")
        if (self.egress is not None) != (self.agent_tool == "ask"):
            raise ValueError("Egress는 ask(question, purpose) 도구와 짝이다")
        return self


class ConditionSet(dict):
    """조건 이름 → Condition. 모든 조건에 공통인 defaults를 함께 들고 다닌다."""
    def __init__(self, conditions: dict[str, Condition], defaults: Defaults):
        super().__init__(conditions)
        self.defaults = defaults


def load_conditions(path: Path) -> ConditionSet:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "defaults" not in raw:
        raise ConfigError(f"{path}: defaults 블록과 조건 이름 → 설정 매핑이 필요하다")
    try:
        defaults = Defaults.model_validate(raw.pop("defaults"))
    except ValidationError as e:
        raise ConfigError(f"{path}: defaults 오류\n{e}") from e
    if not raw:
        raise ConfigError(f"{path}: 조건이 하나도 없다")
    out = {}
    for name, body in raw.items():
        try:
            out[name] = Condition.model_validate(body)
        except ValidationError as e:
            raise ConfigError(f"{path}: 조건 '{name}' 오류\n{e}") from e
    return ConditionSet(out, defaults)


def resolve_condition(conditions: dict[str, Condition], name: str) -> Condition:
    if name not in conditions:
        raise ConfigError(f"존재하지 않는 조건 '{name}' (정의된 조건: {', '.join(conditions)})")
    return conditions[name]
