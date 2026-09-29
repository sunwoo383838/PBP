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


ITEM_SOURCES = ("db", "history", "rule")


class Item(Contract):
    """응답의 값 하나 (응답자 reply, 게이트웨이 answer, Egress 묶음 공통). entity·value는 원문 그대로."""
    entity: str                                 # ID·이름 원문
    attribute: str                              # 무엇의 값인가
    value: str                                  # 값 원문 (ID·금액 변형 없음)
    status_or_as_of: str                        # 상태 또는 기준 시점 (예: "pending", "as of day 5", "v3 registered day 12")
    source: Literal["db", "history", "rule"]
    ref: str                                    # 근거 위치: 조회한 기록 종류·키, 이력 일차, 규정 id, 게이트웨이는 [R1]·[E3]·[D2]


def render_items(items) -> str:
    """사람·LLM이 읽는 한 줄씩의 표기. 항목은 dict 또는 Item."""
    rows = [x.model_dump() if isinstance(x, Item) else x for x in items]
    return "\n".join(f"- {x['entity']} | {x['attribute']} | {x['value']} | {x['status_or_as_of']} | {x['source']}: {x['ref']}"
                     for x in rows)


def render_response(r: dict) -> str:
    """응답(dict)의 이력·전달용 표기: 요약 + 항목 + missing."""
    parts = [r.get("answer") or ""]
    if r.get("items"):
        parts.append(render_items(r["items"]))
    if r.get("missing"):
        parts.append("missing: " + "; ".join(r["missing"]))
    return "\n".join(p for p in parts if p)


class Response(Contract):
    rid: str
    status: Literal["ok", "partial", "referral", "need_more", "error"]
    answer: str                                 # 짧은 요약 (없어도 된다)
    items: list[Item]
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


# ─────────────────────────── 응답 도구 공통 스키마 ───────────────────────────
ITEM_FIELDS = {
    "entity": "The ID or name the value is about, copied exactly as it appears in the record.",
    "attribute": "What the value is (for example 'remaining capex budget', 'holder', 'status').",
    "value": "The value copied exactly as it appears in the record (do not reformat IDs or amounts).",
    "status_or_as_of": "The record's status and the day it is valid from: for a database value its registered day (for "
                       "example 'registered day 5'), for a record the day of the record (for example 'pending, day 7').",
    "source": "Where the value comes from: db (a database lookup), history (your records), rule (a rule).",
    "ref": "The exact location: the record type and key looked up, the day of the record, or the rule id.",
}


def items_schema(ref_description: str | None = None) -> dict:
    props = {k: {"type": "string", "description": d} for k, d in ITEM_FIELDS.items()}
    props["source"] = {"enum": list(ITEM_SOURCES), "description": ITEM_FIELDS["source"]}
    if ref_description:
        props["ref"] = {"type": "string", "description": ref_description}
    return {"type": "array", "description": "One entry per value found. Give at least one item or one missing entry.",
            "items": {"type": "object", "properties": props, "required": list(ITEM_FIELDS), "additionalProperties": False}}


def answer_parameters(ref_description: str | None = None) -> dict:
    return {"type": "object", "properties": {
        "items": items_schema(ref_description),
        "missing": {"type": "array", "items": {"type": "string"}, "description": "Requested items you could not confirm."},
        "answer": {"type": "string", "description": "Optional short summary."}},
        "required": ["items", "missing"], "additionalProperties": False}


def check_items(args: dict, ref_ok=None) -> tuple[bool, object]:
    """reply·answer 도구 인자 검사. (True, (answer, items, missing)) 또는 (False, 오류 설명). ref_ok(ref) → 오류 문자열|None."""
    items, missing, answer = args.get("items"), args.get("missing", []), args.get("answer", "")
    if not isinstance(items, list) or not isinstance(missing, list) or not all(isinstance(m, str) for m in missing):
        return False, "items must be a list and missing a list of strings"
    if not isinstance(answer, str):
        return False, "answer must be a string"
    if not items and not missing:
        return False, "give at least one item or one missing entry"
    out = []
    for i, x in enumerate(items):
        if not isinstance(x, dict) or set(x) != set(ITEM_FIELDS):
            return False, f"items[{i}] must have exactly the fields {list(ITEM_FIELDS)}"
        if not all(isinstance(x[k], str) for k in ITEM_FIELDS):
            return False, f"items[{i}]: every field must be a string (copy numbers as text)"
        if x["source"] not in ITEM_SOURCES:
            return False, f"items[{i}].source must be one of {list(ITEM_SOURCES)}"
        if not x["entity"].strip() or not x["value"].strip():
            return False, f"items[{i}]: entity and value must not be empty"
        if ref_ok and (err := ref_ok(x["ref"])):
            return False, f"items[{i}].ref: {err}"
        out.append(Item(**x))
    return True, (answer, out, missing)
