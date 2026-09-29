"""스크립트 에이전트: LLM 없이 고정 답을 내는 더미. 커널·경계 모듈 테스트용."""
from collections.abc import Callable

from gbg.contracts.envelope import Request, Response
from gbg.contracts.schemas import OutputSchema, TimelineEvent

_DEFAULT = {"int": 0, "number": 0, "id": "", "bool": False, "set": [], "list": []}


def fixed_answer(schema: OutputSchema | None) -> dict:
    """닫힌 슬롯마다 고정값: enum은 첫 선택지, 나머지는 형식별 기본값."""
    if schema is None:
        return {}
    return {s.name: (s.options[0] if s.type == "enum" else _DEFAULT[s.type]) for s in schema.slots}


class ScriptedAgent:
    def __init__(self, agent_id: str, peer: Callable[[TimelineEvent], str | None] | None = None):
        self.agent_id, self.peer = agent_id, peer

    async def work(self, ctx, task: TimelineEvent) -> dict:
        """교차 작업이면 peer에게 한 번 묻고, 고정 답을 낸다."""
        if task.kind == "cross" and self.peer and (to := self.peer(task)):
            await ctx.ask(to, task.text)
        return fixed_answer(task.output_schema)

    async def respond(self, ctx, request: Request) -> Response:
        return Response(rid=request.rid, status="ok", answer="unknown", values=[], missing=[], referral_to=None,
                        need=[], as_of=ctx.day)
