"""worldgen 환경 도구: db.query(entity, record_type), entity.search(query). 그룹 규정은 도구가 아니라 모든 LLM 호출의
system에 고정으로 들어간다(자기 그룹 규정만).

도구 스키마(record type 목록과 의미)와 실행 중 권한 검사는 모두 record_policy.yaml에서 나온다. 권한은 그룹 단위라서
같은 그룹 구성원은 역할과 무관하게 같은 도구를 받는다. 스키마에는 physical key도 레코드 목록도 없다.
도구 함수는 스키마를 믿지 않고 호출자 그룹을 다시 확인한다.
"""
from gbg.contracts.schemas import ToolSpec
from gbg.kernel.tools import Resource, Tool, ToolCall, ToolOutput

from .records import RecordPolicy, RecordService, load_policy

POLICY = load_policy()

SEARCH = ToolSpec(
    name="entity.search",
    description="Find entities by ID or name. Returns entity IDs you can use with db.query.",
    parameters={"type": "object", "properties": {"query": {"type": "string", "description": "Part of an ID or a name."}},
                "required": ["query"], "additionalProperties": False},
    resources=["db"])


def db_query_spec(policy: RecordPolicy, domain: str) -> ToolSpec | None:
    types = policy.types_for(domain)
    if not types:
        return None
    meanings = "\n".join(f"- {t}: {policy.record_types[t].description}" for t in types)
    return ToolSpec(
        name="db.query",
        description="Look up one record type for an entity in the database. Returns the latest version registered as "
                    "of today. The entity can be given directly as an ID or a name; use entity.search only if db.query "
                    "returns NOT_FOUND. If a name matches several entities, the candidates are returned with their IDs.",
        parameters={"type": "object", "properties": {
            "entity": {"type": "string", "description": "The entity ID or a known name of the entity."},
            "record_type": {"type": "string", "enum": types, "description": "Record types you can read:\n" + meanings}},
            "required": ["entity", "record_type"], "additionalProperties": False},
        resources=["db"])


def domain_specs(domain: str, policy: RecordPolicy = POLICY) -> list[ToolSpec]:
    """그룹 도메인의 도구 명세. 역할·조건과 무관하다."""
    q = db_query_spec(policy, domain)
    return [q, SEARCH] if q else []                                     # 규정은 도구가 아니라 system에 고정 (2026-09-29)


def make_tools(stores, domain_of: dict[str, str], policy: RecordPolicy = POLICY) -> list[Tool]:
    svc = RecordService(policy, stores, domain_of)

    def db_query(call: ToolCall):
        entity, rtype = call.args.get("entity"), call.args.get("record_type")
        if not isinstance(entity, str) or not isinstance(rtype, str):
            visible, log = svc._miss("UNKNOWN_TYPE", {"group": call.group, "entity_input": entity, "record_type": rtype})
        else:
            visible, log = svc.lookup(call.group, entity, rtype, call.day)
        return ToolOutput(visible, [("db_lookups", {"tool": "db.query", **log})])

    def entity_search(call: ToolCall):
        q = call.args.get("query")
        visible, log = svc.search(call.group, q if isinstance(q, str) else "", call.day)
        return ToolOutput(visible, [("db_lookups", {"tool": "entity.search", **log})])

    db = (Resource("db", "r"),)
    return [Tool("db.query", "structured record lookup", db, db_query),
            Tool("entity.search", SEARCH.description, db, entity_search)]
