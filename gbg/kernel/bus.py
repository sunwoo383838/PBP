"""동기 요청(ask) 처리.

응답자는 라운드 시작 시점의 자기 이력 + 그 요청만 보고 답한다. 문답은 라운드 끝에 양쪽 이력에 커밋된다.
응답자가 다시 다른 곳에 묻는 중첩 요청은 허용하되, 홉 상한을 넘는 요청은 error로 끊는다.
"""
from typing import TYPE_CHECKING

from gbg.contracts.envelope import Request, Response

if TYPE_CHECKING:
    from .scheduler import AgentContext, Kernel


def error_response(rid: str, reason: str, day: int) -> Response:
    return Response(rid=rid, status="error", answer=reason, values=[], missing=[], referral_to=None, need=[], as_of=day)


class Bus:
    def __init__(self, kernel: "Kernel", hop_limit: int):
        self.kernel, self.hop_limit = kernel, hop_limit

    async def ask(self, ctx: "AgentContext", to_agent: str, question: str, purpose: str | None) -> Response:
        from .scheduler import AgentContext, AgentFailure, FatalError
        k = self.kernel
        span = ctx.span.child()                                      # 이 문답 전체가 한 슬롯을 차지한다
        rid = f"{ctx.task_id}/" + ".".join(str(x) for x in span.prefix[2:])
        to = k.members.get(to_agent)
        req = Request(rid=rid, from_group=ctx.group, from_agent=ctx.agent_id, to_group=to.group if to else "",
                      to_agent=to_agent, question=question, purpose=purpose, origin_task=ctx.task_id,
                      hop=ctx.hop + 1, lineage=[*ctx.lineage, ctx.group])
        head = {"task_id": ctx.task_id, "rid": rid, "from_agent": ctx.agent_id, "to_agent": to_agent}
        refused = "hop_limit" if req.hop > self.hop_limit else ("agent_unavailable" if not k.is_active(to_agent) else None)
        span.emit("message", f"agent:{ctx.agent_id}", {**head, "kind": "request", "delivered": refused is None,
                                                       "request": req.model_dump(mode="json")})
        if refused:
            resp, actor = error_response(rid, refused, ctx.day), "kernel"
        else:
            rctx = AgentContext(k, span, to_agent, to.group, to.role, ctx.day, ctx.round, ctx.task_id, req.hop,
                                req.lineage, k.stores.history.entries(to_agent))
            actor = f"agent:{to_agent}"
            try:
                resp = await k.agents[to_agent].respond(rctx, req)
                if resp.rid != rid:
                    resp = resp.model_copy(update={"rid": rid})
            except FatalError:
                raise
            except AgentFailure as e:
                resp = error_response(rid, e.reason, ctx.day)
            except Exception as e:
                resp = error_response(rid, f"agent_exception:{type(e).__name__}", ctx.day)
        span.emit("message", actor, {**head, "kind": "response", "response": resp.model_dump(mode="json")})
        return resp
