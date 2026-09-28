"""worldgen 환경 도구: 자기 그룹의 DB와 규정만 읽는다 (접근 가드가 자원을 확인)."""
from gbg.contracts.schemas import ToolSpec
from gbg.kernel.tools import Resource, Tool, ToolCall

SPECS = [
    ToolSpec(name="db.query", description="자기 그룹 DB에서 키 하나를 조회한다. 오늘 등록된 최신 버전만 보인다.",
             parameters={"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]},
             resources=["db"]),
    ToolSpec(name="rulebook.read", description="자기 그룹 규정을 id로 읽거나 검색어로 찾는다.",
             parameters={"type": "object", "properties": {"id": {"type": "string"}, "search": {"type": "string"}}},
             resources=["rulebook"]),
]


def make_tools(stores) -> list[Tool]:
    def db_query(call: ToolCall):
        key = call.args["key"]
        v = stores.db.query(call.group, key, call.day)
        return {"key": key, "value": "ABSENT"} if v is None else {"key": key, "value": v.value, "v": v.v}

    def rulebook_read(call: ToolCall):
        if "id" in call.args:
            r = stores.rulebook.read(call.group, call.args["id"])
            return [] if r is None else [r.model_dump(mode="json")]
        return [r.model_dump(mode="json") for r in stores.rulebook.search(call.group, call.args.get("search", ""))]

    fns = {"db.query": db_query, "rulebook.read": rulebook_read}
    return [Tool(name=s.name, description=s.description, resources=tuple(Resource(r, "r") for r in s.resources),
                 fn=fns[s.name]) for s in SPECS]
