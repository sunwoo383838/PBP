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


ITEM_SOURCES = ("db", "history", "rule", "unknown")


class Item(Contract):
    """응답의 값 하나 (응답자 reply, 게이트웨이 answer, Routing 전달, Egress 묶음 공통). entity·value는 원문 그대로.
    LLM은 entity·attribute·value·status·ref를 쓰고, source·day는 코드가 ref(도구 결과 D#, 이력 줄 H#, 규정 id,
    게이트웨이의 R#·E#·D#·S#)를 따라가 채운다: DB = 등록일, 이력 = 줄의 날짜, 규정 = "fixed", 풀리지 않으면 "unknown"."""
    entity: str                                 # ID·이름 원문
    attribute: str                              # 무엇의 값인가
    value: str                                  # 값 원문 (ID·금액 변형 없음)
    status: str                                 # 기록에 적힌 상태 (없으면 빈 문자열)
    ref: str                                    # 근거 ID
    source: Literal["db", "history", "rule", "unknown"] = "unknown"
    day: str = "unknown"                        # 등록일·기록일 (정수 문자열) | "fixed" | "unknown"


class Redirect(Contract):
    """소관 밖 항목의 안내 (out_of_scope) 또는 증거 기반 referral (ownership_exception)."""
    entity: str
    attribute: str
    referral_to: str
    reason: Literal["out_of_scope", "ownership_exception"]


class Conflict(Contract):
    """접수부 조립의 충돌 표시: 응답끼리 또는 응답과 그룹 기록이 다른 항목."""
    item: str
    note: str
    refs: list[str]


class Proposal(Contract):
    """접수부 조립의 제안 값: 담당자 답과 다른 값을 근거(refs 필수)와 함께 제안한다. 담당자 답은 바꾸지 않는다."""
    item: str
    value: str
    refs: list[str] = Field(min_length=1)
    rationale: str


def render_items(items) -> str:
    """사람·LLM이 읽는 한 줄씩의 표기. 항목은 dict 또는 Item (옛 기록의 status_or_as_of도 읽는다)."""
    rows = [x.model_dump() if isinstance(x, Item) else x for x in items]
    return "\n".join(f"- {x['entity']} | {x['attribute']} | {x['value']} | {x.get('status', x.get('status_or_as_of', ''))} | "
                     f"{x.get('source', 'unknown')}, day {x.get('day', 'unknown')}: {x['ref']}" for x in rows)


def render_response(r: dict) -> str:
    """응답(dict)의 이력·전달용 표기: 요약 + 항목 + missing."""
    parts = [r.get("answer") or ""]
    if r.get("items"):
        parts.append(render_items(r["items"]))
    if r.get("missing"):
        parts.append("missing: " + "; ".join(r["missing"]))
    for x in r.get("conflicts") or []:
        parts.append(f"conflict: {x['item']}: {x['note']} ({' '.join(x['refs'])})")
    for x in r.get("proposals") or []:
        parts.append(f"proposed: {x['item']} = {x['value']} ({' '.join(x['refs'])}) — {x['rationale']}")
    for x in r.get("redirects") or []:
        parts.append(f"not handled there: {x['entity']} {x['attribute']} → ask {x['referral_to']}")
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
    redirects: list[Redirect] = []              # 소관 밖 항목 안내 (missing에도 들어 있다)
    conflicts: list[Conflict] = []              # 접수부 조립 (Ingress·I+E): 충돌 표시
    proposals: list[Proposal] = []              # 접수부 조립: 제안 값 (근거 필수)

    @model_validator(mode="after")
    def _status_fields(self):
        if (self.status == "referral") != (self.referral_to is not None):
            raise ValueError("referral_to는 status=referral일 때만, 그리고 반드시 있어야 한다")
        if self.status == "need_more" and not self.need:
            raise ValueError("need_more에는 need 항목이 있어야 한다")
        return self


# ─────────────────────────── 응답 도구 공통 스키마 ───────────────────────────
ITEM_FIELDS = {                                                             # LLM이 쓰는 필드 (source·day는 코드가 채운다)
    "entity": "The ID or name the value is about, copied exactly as it appears in the record.",
    "attribute": "What the value is (for example 'remaining capex budget', 'holder', 'status').",
    "value": "The value copied exactly as it appears in the record (do not reformat IDs or amounts).",
    "status": "The status the record states, if any (for example 'pending', 'held until day 9'); otherwise empty.",
    "ref": "The ID of what the value is taken from, as shown in your input: a lookup result (for example D2), a line "
           "of your records (for example H120), or a rule id.",
}


def items_schema(ref_description: str | None = None) -> dict:
    props = {k: {"type": "string", "description": d} for k, d in ITEM_FIELDS.items()}
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


def check_items(args: dict, ref_ok=None, resolve=None) -> tuple[bool, object]:
    """reply·answer 도구 인자 검사. (True, (answer, items, missing)) 또는 (False, 오류 설명). ref_ok(ref) → 오류 문자열|None.
    resolve(item dict) → (source, day): ref를 따라가 코드가 채운다 (없으면 unknown)."""
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
        if not x["entity"].strip() or not x["value"].strip():
            return False, f"items[{i}]: entity and value must not be empty"
        if ref_ok and (err := ref_ok(x["ref"])):
            return False, f"items[{i}].ref: {err}"
        source, day = resolve(x) if resolve else ("unknown", "unknown")
        out.append(Item(**x, source=source, day=str(day)))
    return True, (answer, out, missing)
