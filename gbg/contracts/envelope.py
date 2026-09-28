"""그룹 경계를 넘는 요청과 응답."""
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from ._base import Contract


class Request(Contract):
    rid: str
    from_group: str
    from_agent: str
    to_group: str
    to_agent: str | None                        # Direct만 지정, 게이트웨이 조건은 None
    question: str
    purpose: str | None
    origin_task: str
    hop: int = Field(ge=0)
    lineage: list[str]                          # 요청이 지나온 그룹, 출발 그룹부터


class SourcedValue(Contract):
    value: JsonValue
    source: str                                 # 인용 id (응답 담당자, 증거 [E1] 등)


class Response(Contract):
    rid: str
    status: Literal["ok", "partial", "referral", "need_more", "error"]
    answer: str
    values: list[SourcedValue]
    missing: list[str]
    referral_to: str | None
    need: list[str]                             # need_more일 때 보완이 필요한 항목
    as_of: int                                  # 응답 기준 일차

    @model_validator(mode="after")
    def _status_fields(self):
        if (self.status == "referral") != (self.referral_to is not None):
            raise ValueError("referral_to는 status=referral일 때만, 그리고 반드시 있어야 한다")
        if self.status == "need_more" and not self.need:
            raise ValueError("need_more에는 need 항목이 있어야 한다")
        return self
