"""worldgen 환경 도구: db.query(entity, record_type), entity.search(query), rulebook.read.

도구 스키마(record type 목록과 의미)와 실행 중 권한 검사는 모두 role_policy.yaml에서 나온다. 스키마에는
physical key도 레코드 목록도 없다. 도구 함수는 스키마를 믿지 않고 호출자 역할을 저장소에서 다시 확인한다.
"""
from gbg.contracts.schemas import ToolSpec
from gbg.kernel.tools import Resource, Tool, ToolCall, ToolOutput

from .records import RecordService, RolePolicy, load_policy

POLICY = load_policy()

RULEBOOK = ToolSpec(
    name="rulebook.read", description="Read a rule of your group by id, or search your group's rulebook.",
    parameters={"type": "object", "properties": {"id": {"type": "string"}, "search": {"type": "string"}},
                "additionalProperties": False},
    resources=["rulebook"])

SEARCH = ToolSpec(
    name="entity.search",
    description="Find entities in your group by ID or name. Returns entity IDs you can use with db.query.",
    parameters={"type": "object", "properties": {"query": {"type": "string", "description": "Part of an ID or a name."}},
                "required": ["query"], "additionalProperties": False},
    resources=["db"])


def db_query_spec(policy: RolePolicy, role: str) -> ToolSpec | None:
    types = policy.types_for(role)
    if not types:
        return None
    meanings = "\n".join(f"- {t}: {policy.record_types[t].description}" for t in types)
    return ToolSpec(
        name="db.query",
        description="Look up one record type for an entity in your group's database. "
                    "Returns the latest version registered as of today.",
        parameters={"type": "object", "properties": {
            "entity": {"type": "string", "description": "The entity ID or a known name of the entity."},
            "record_type": {"type": "string", "enum": types, "description": "Record types you can read:\n" + meanings}},
            "required": ["entity", "record_type"], "additionalProperties": False},
        resources=["db"])


def role_specs(role: str, policy: RolePolicy = POLICY) -> list[ToolSpec]:
    """역할의 도구 명세. 조건과 무관하다 (모든 조건의 에이전트가 같은 역할이면 같은 도구를 받는다)."""
    q = db_query_spec(policy, role)
    return ([q, SEARCH] if q else []) + [RULEBOOK]


def all_specs(policy: RolePolicy = POLICY) -> list[ToolSpec]:
    return role_specs(next(iter(policy.roles)), policy)


def make_tools(stores, aliases: dict[str, dict[str, list[str]]], policy: RolePolicy = POLICY) -> list[Tool]:
    svc = RecordService(policy, aliases, stores.db)
    role_of = lambda agent: stores.members[agent][1]

    def db_query(call: ToolCall):
        entity, rtype = call.args.get("entity"), call.args.get("record_type")
        if not isinstance(entity, str) or not isinstance(rtype, str):
            visible, log = svc._miss("UNKNOWN_TYPE", {"group": call.group, "role": role_of(call.agent),
                                                     "entity_input": entity, "record_type": rtype})
        else:
            visible, log = svc.lookup(call.group, role_of(call.agent), entity, rtype, call.day)
        return ToolOutput(visible, [("db_lookups", {"tool": "db.query", **log})])

    def entity_search(call: ToolCall):
        q = call.args.get("query")
        visible, log = svc.search(call.group, role_of(call.agent), q if isinstance(q, str) else "", call.day)
        return ToolOutput(visible, [("db_lookups", {"tool": "entity.search", **log})])

    def rulebook_read(call: ToolCall):
        if "id" in call.args:
            r = stores.rulebook.read(call.group, call.args["id"])
            return [] if r is None else [r.model_dump(mode="json")]
        return [r.model_dump(mode="json") for r in stores.rulebook.search(call.group, call.args.get("search", ""))]

    db = (Resource("db", "r"),)
    return [Tool("db.query", "structured record lookup", db, db_query),
            Tool("entity.search", SEARCH.description, db, entity_search),
            Tool("rulebook.read", RULEBOOK.description, (Resource("rulebook", "r"),), rulebook_read)]
