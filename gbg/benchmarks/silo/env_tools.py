"""SILO 환경 도구. shard.read는 새 접근 자원 없이, 호출자 자신의 조각만 돌려준다 (승인된 결정)."""
from gbg.contracts.schemas import ToolSpec
from gbg.kernel.tools import Tool, ToolCall

SPECS = [
    ToolSpec(name="shard.read", description="Read the elements of the shard you hold.",
             parameters={"type": "object", "properties": {}}, resources=[]),
]


def make_tools(stores) -> list[Tool]:
    def shard_read(call: ToolCall):
        shards = stores.env[call.group].get("shards", {})
        return {"agent": call.agent, "words": shards.get(call.agent, [])}

    return [Tool(name="shard.read", description=SPECS[0].description, resources=(), fn=shard_read)]
