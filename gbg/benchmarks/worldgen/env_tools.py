"""worldgen 환경 도구: db.query(entity, record_type), entity.search(query), rulebook.read.

도구 스키마(record type 목록과 의미)와 실행 중 권한 검사는 모두 record_policy.yaml에서 나온다. 권한은 그룹 단위라서
같은 그룹 구성원은 역할과 무관하게 같은 도구를 받는다. 스키마에는 physical key도 레코드 목록도 없다.
도구 함수는 스키마를 믿지 않고 호출자 그룹을 다시 확인한다.
"""
from gbg.contracts.schemas import ToolSpec
from gbg.kernel.tools import Resource, Tool, ToolCall, ToolOutput

from .records import RecordPolicy, RecordService, load_policy

POLICY = load_policy()

RULEBOOK = ToolSpec(
    name="rulebook.read", description="Read a rule by id, or search the rulebook.",
    parameters={"type": "object", "properties": {"id": {"type": "string"}, "search": {"type": "string"}},
                "additionalProperties": False},
    resources=["rulebook"])

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
        description="Look up one record type for an entity in the database. "
                    "Returns the latest version registered as of today.",
        parameters={"type": "object", "properties": {
            "entity": {"type": "string", "description": "The entity ID or a known name of the entity."},
            "record_type": {"type": "string", "enum": types, "description": "Record types you can read:\n" + meanings}},
            "required": ["entity", "record_type"], "additionalProperties": False},
        resources=["db"])


def domain_specs(domain: str, policy: RecordPolicy = POLICY) -> list[ToolSpec]:
    """그룹 도메인의 도구 명세. 역할·조건과 무관하다."""
    q = db_query_spec(policy, domain)
    return ([q, SEARCH] if q else []) + [RULEBOOK]


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

    def local(r):                                                         # 그룹 접두어 없는 id, group 필드 없음
        prefix = f"{r.group}."
        return {"id": r.id[len(prefix):] if r.id.startswith(prefix) else r.id, "title": r.title, "text": r.body}

    def rulebook_read(call: ToolCall):
        if "id" in call.args:
            rid = call.args["id"]
            r = stores.rulebook.read(call.group, rid) or stores.rulebook.read(call.group, f"{call.group}.{rid}")
            return [] if r is None else [local(r)]
        return [local(r) for r in stores.rulebook.search(call.group, call.args.get("search", ""))]

    db = (Resource("db", "r"),)
    return [Tool("db.query", "structured record lookup", db, db_query),
            Tool("entity.search", SEARCH.description, db, entity_search),
            Tool("rulebook.read", RULEBOOK.description, (Resource("rulebook", "r"),), rulebook_read)]
