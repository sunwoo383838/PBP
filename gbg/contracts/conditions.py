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
    """받는 쪽 경계 모듈. 담당자 선택은 모든 경계 조건이 같다: 요청 해석 → 별칭 해소 → referral·need_more →
    그룹 기록 검색(색인 entities + catalog 연결 + 하이브리드 이력 검색) → LLM이 검색 결과를 보고 담당자 선택.
    인원 상한은 없고 과제 예산이 상한이다. 조건마다 다른 것은 전달 방식뿐이다."""
    deliver: Literal["forward", "read", "assemble"]
    # forward  = 요청 원문을 담당자들에게 그대로, 응답 원문을 요청자에게 그대로 (Routing. 검색 결과는 선택에만)
    # read     = forward + 검색된 기록 원문 첨부 (ingress_read)
    # assemble = 게이트웨이 LLM이 증거와 응답으로 조립 (ingress_sel, Ingress, I+E)
    requery: bool = False                       # 빠진 항목 재질의
    boundary_state: bool = False                # 경계 상태(과거 교차 문답·제공 버전·진행 중 요청)를 조립에 쓴다
    version_marks: bool = False                 # 조립 답에 버전 표시 (같은 DB 키·버전 번호로 묶은 사실)
    reveal_holders: bool = False                # 전달하지 않고 담당자 목록만 돌려준다 (요청자가 직접 묻는다)
    internal_query: bool = True                 # False = 담당자에게 묻지 않고 그룹 기록만으로 조립 (gateway_rag)
    evidence: Literal["search", "oracle"] = "search"   # oracle = 증거 블록을 정답 조각으로 대체 (retrieval_oracle)

    @model_validator(mode="after")
    def _deliver(self):
        if self.reveal_holders and self.deliver != "forward":
            raise ValueError("reveal_holders는 forward(Routing)에서만: 담당자 목록만 돌려준다")
        if self.deliver != "assemble" and (self.requery or self.boundary_state or self.version_marks):
            raise ValueError("재질의·경계 상태·버전 표시는 조립(assemble)하는 게이트웨이에만 있다")
        if not self.internal_query and (self.deliver != "assemble" or self.requery):
            raise ValueError("internal_query: false(gateway_rag)는 조립하는 게이트웨이에서만, 재질의 없이")
        if self.evidence == "oracle" and self.deliver != "assemble":
            raise ValueError("evidence: oracle(retrieval_oracle)은 조립하는 게이트웨이에서만")
        return self


class EgressConfig(Contract):
    history: bool                               # egress_log 기록을 관련 기록으로 제공. False = 요청자 자신의 이력과
                                                # card만 제공 (참조 행 egress_no_history)


class RelayConfig(Contract):
    """[부록 direct_relay] 응답자가 자기 그룹 동료에게 되묻기 (한 단계). 요청자에게는 응답자의 답만 간다."""
    max_asks: int = 3                           # 받은 요청 하나당 동료에게 되물을 수 있는 횟수


class Condition(Contract):
    agent_tool: Literal["ask_agent", "ask_group", "ask", "search_memory"]
    directory: Literal["agent_cards", "group_cards"]
    card_mode: Literal["static", "dynamic"] = "static"
    responder_session: Literal["persistent", "ephemeral"] = "persistent"
    ingress: IngressConfig | None
    egress: EgressConfig | None
    blocked: str | None = None                  # 설정에는 있지만 실행기가 거부하는 조건 (사유)
    budget_limit: bool = True                   # False = 과제 예산 상한 미적용, 소비량만 기록 (지금은 쓰는 조건 없음)
    relay: RelayConfig | None = None            # [부록 direct_relay] Direct 응답자의 그룹 안 되묻기
    sidecar: IngressConfig | None = None        # [부록 sidecar] Direct에서 받은 에이전트마다 붙는 검색·조립 모듈 (그 에이전트 혼자 답함)
    budget_bonus_calls: int = 0                 # [부록 retrieve] 요청자 호출 추가분 (원문 근거를 직접 읽는 부담)

    @model_validator(mode="after")
    def _consistent(self):
        direct = self.agent_tool == "ask_agent"
        load = self.agent_tool == "search_memory"                      # full_load: 분할 없는 단일 에이전트, 묻지 않는다
        if direct != (self.directory == "agent_cards"):
            raise ValueError("ask_agent는 에이전트 card 디렉터리와, 그룹 도구는 그룹 card 디렉터리와 짝이다")
        if (direct or load) and (self.ingress or self.egress):
            raise ValueError("Direct·full_load 요청은 경계 모듈을 지나지 않는다")
        if not (direct or load) and self.ingress is None:
            raise ValueError("그룹에 묻는 조건은 받는 쪽 Ingress가 있어야 한다")
        if (self.egress is not None) != (self.agent_tool == "ask"):
            raise ValueError("Egress는 ask(question, purpose) 도구와 짝이다")
        if (self.relay or self.sidecar) and not direct:
            raise ValueError("relay·sidecar는 Direct(ask_agent)에만 붙는다")
        if self.relay and self.sidecar:
            raise ValueError("relay와 sidecar는 함께 쓰지 않는다")
        if self.sidecar and (self.sidecar.deliver != "assemble" or self.sidecar.requery or self.sidecar.boundary_state
                             or not self.sidecar.internal_query or self.sidecar.evidence != "search"):
            raise ValueError("sidecar는 검색·조립만 한다: deliver assemble, 재질의·경계 상태 없음 (요청 간 상태 공유 없음)")
        if self.budget_bonus_calls < 0:
            raise ValueError("budget_bonus_calls는 0 이상")
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
