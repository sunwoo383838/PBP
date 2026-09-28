"""조건 설정 (configs/conditions.yaml). 사다리 4단은 이 설정만으로 전환한다."""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, ValidationError, model_validator

from ._base import Contract


class ConfigError(ValueError):
    """설정 파일이 계약을 어김: 없는 이름, 선언 밖 키, 모순된 조합."""


class IngressConfig(Contract):
    fanout: int = Field(ge=1)                   # 담당자 수 상한
    assemble: bool                              # 증거 + 응답으로 조립 (LLM ②)
    requery: bool                               # 빠진 항목 재질의 1회


class EgressConfig(Contract):
    history: bool                               # egress_log 기록을 관련 기록으로 제공


class Condition(Contract):
    agent_tool: Literal["ask_agent", "ask_group", "ask"]
    directory: Literal["agent_cards", "group_cards"]
    card_mode: Literal["static", "dynamic"] = "static"
    ingress: IngressConfig | None
    egress: EgressConfig | None

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


def load_conditions(path: Path) -> dict[str, Condition]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not raw:
        raise ConfigError(f"{path}: 조건 이름 → 설정 매핑이어야 한다")
    out = {}
    for name, body in raw.items():
        try:
            out[name] = Condition.model_validate(body)
        except ValidationError as e:
            raise ConfigError(f"{path}: 조건 '{name}' 오류\n{e}") from e
    return out


def resolve_condition(conditions: dict[str, Condition], name: str) -> Condition:
    if name not in conditions:
        raise ConfigError(f"존재하지 않는 조건 '{name}' (정의된 조건: {', '.join(conditions)})")
    return conditions[name]
