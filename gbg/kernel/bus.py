"""동기 요청(ask) 처리.

응답자는 라운드 시작 시점의 자기 이력 + 그 요청만 보고 답한다. 문답은 라운드 끝에 양쪽 이력에 커밋된다.
응답자가 다시 다른 곳에 묻는 중첩 요청은 허용하되, 홉 상한을 넘는 요청은 error로 끊는다.

요청 경로 세 가지:
    ask           에이전트 → 에이전트 (Direct의 ask_agent, 경계 모듈의 내부 질의)
    ask_group     에이전트 또는 Egress → 그룹 B의 경계 모듈(Ingress)
    ask_egress    에이전트 → 자기 그룹의 경계 모듈(Egress, I+E의 ask)
"""
from typing import TYPE_CHECKING

from gbg.contracts.envelope import Request, Response

from .budget import BudgetExhausted

if TYPE_CHECKING:
    from .scheduler import AgentContext, Kernel


def error_response(rid: str, reason: str, day: int) -> Response:
    return Response(rid=rid, status="error", answer=reason, values=[], missing=[], referral_to=None, need=[], as_of=day)


class Bus:
    def __init__(self, kernel: "Kernel", hop_limit: int):
        self.kernel, self.hop_limit = kernel, hop_limit

    def _rid(self, ctx: "AgentContext", span) -> str:
        return f"{ctx.task_id}/" + ".".join(str(x) for x in span.prefix[2:])

    def _request(self, ctx: "AgentContext", rid: str, to_group: str, to_agent: str | None, question: str,
                 purpose: str | None, hop: int | None = None) -> Request:
        return Request(rid=rid, from_group=ctx.group, from_agent=ctx.agent_id, to_group=to_group, to_agent=to_agent,
                       question=question, purpose=purpose, origin_task=ctx.task_id,
                       hop=ctx.hop + 1 if hop is None else hop, lineage=[*ctx.lineage, ctx.group])

    async def ask(self, ctx: "AgentContext", to_agent: str, question: str, purpose: str | None,
                  hop: int | None = None) -> Response:
        """에이전트에게 직접. 경계 모듈의 내부 질의는 hop을 넘겨 원 요청의 홉을 유지한다."""
        k = self.kernel
        span = ctx.span.child()
        rid = self._rid(ctx, span)
        to = k.members.get(to_agent)
        req = self._request(ctx, rid, to.group if to else "", to_agent, question, purpose, hop)
        head = {"task_id": ctx.task_id, "rid": rid, "from_agent": ctx.agent_id, "to_agent": to_agent,
                "to_group": req.to_group, "serving": ctx.serving}
        refused = self._requester_policy(ctx, to_agent, question)
        if refused is None and req.hop > self.hop_limit:
            refused = "hop_limit"
        if refused is None and not k.is_active(to_agent):
            refused = "agent_unavailable"
        span.emit("message", ctx.actor, {**head, "kind": "request", "delivered": refused is None,
                                          "request": req.model_dump(mode="json")})
        if refused:
            resp, actor = error_response(rid, refused, ctx.day), "kernel"
        else:
            resp, actor = await self._respond(ctx, span, req, to_agent, to.group, to.role), f"agent:{to_agent}"
        span.emit("message", actor, {**head, "kind": "response", "question": question,
                                      "response": resp.model_dump(mode="json")})
        return resp

    async def _respond(self, ctx: "AgentContext", span, req: Request, agent: str, group: str, role: str) -> Response:
        from .scheduler import AgentContext, FatalError
        from .errors import AgentFailure
        k = self.kernel
        rctx = AgentContext(k, span, agent, group, role, ctx.day, ctx.round, ctx.task_id, req.hop, req.lineage,
                            k.stores.history.entries(agent), serving=req.rid)
        try:
            resp = await k.agents[agent].respond(rctx, req)
            return resp if resp.rid == req.rid else resp.model_copy(update={"rid": req.rid})
        except FatalError:
            raise
        except AgentFailure as e:
            return error_response(req.rid, e.reason, ctx.day)
        except Exception as e:
            return error_response(req.rid, f"agent_exception:{type(e).__name__}", ctx.day)

    async def ask_group(self, ctx: "AgentContext", group: str, question: str, purpose: str | None = None) -> Response:
        """그룹 B의 경계 모듈(Ingress)에게. 요청자 또는 A의 Egress가 부른다."""
        k = self.kernel
        span = ctx.span.child()
        rid = self._rid(ctx, span)
        req = self._request(ctx, rid, group, None, question, purpose)
        head = {"task_id": ctx.task_id, "rid": rid, "from_agent": ctx.agent_id, "to_agent": None, "to_group": group,
                "serving": ctx.serving}
        refused = self._requester_policy(ctx, f"group:{group}", question)
        if refused is None and req.hop > self.hop_limit:
            refused = "hop_limit"
        if refused is None and (group not in k.boundaries or group == ctx.group):
            refused = "unknown_group"
        span.emit("message", ctx.actor, {**head, "kind": "request", "delivered": refused is None,
                                          "request": req.model_dump(mode="json")})
        actor = f"boundary:{group}"
        if refused:
            resp, actor = error_response(rid, refused, ctx.day), "kernel"
        else:
            try:
                resp = await k.boundaries[group].ingress(ctx, span, req)
            except BudgetExhausted:                                         # 경계 모듈이 예산에 막힘: 요청자는 최종 답변으로
                resp = error_response(rid, "budget_exhausted", ctx.day)
        span.emit("message", actor, {**head, "kind": "response", "question": question,
                                      "response": resp.model_dump(mode="json")})
        return resp

    async def ask_egress(self, ctx: "AgentContext", question: str, purpose: str | None) -> Response:
        """자기 그룹의 경계 모듈(Egress)에게 (I+E). 대상 그룹은 Egress가 정한다."""
        k = self.kernel
        span = ctx.span.child()
        rid = self._rid(ctx, span)
        req = self._request(ctx, rid, "", None, question, purpose, hop=ctx.hop)   # Egress는 홉을 늘리지 않는다
        head = {"task_id": ctx.task_id, "rid": rid, "from_agent": ctx.agent_id, "to_agent": None, "to_group": "",
                "serving": ctx.serving}
        refused = self._requester_policy(ctx, "egress", question)
        span.emit("message", ctx.actor, {**head, "kind": "request", "delivered": refused is None,
                                          "request": req.model_dump(mode="json")})
        actor = f"boundary:{ctx.group}"
        if refused:
            resp, actor = error_response(rid, refused, ctx.day), "kernel"
        else:
            try:
                resp = await k.boundaries[ctx.group].egress(ctx, span, req)
            except BudgetExhausted:
                resp = error_response(rid, "budget_exhausted", ctx.day)
        span.emit("message", actor, {**head, "kind": "response", "question": question,
                                      "response": resp.model_dump(mode="json")})
        return resp

    def _requester_policy(self, ctx: "AgentContext", to: str, question: str) -> str | None:
        """요청자 권한 (defaults.requester): 과제 담당자의 질문 수 상한과 같은 질문 반복 허용 여부."""
        b = self.kernel.budget
        if b is None or ctx.component != "requester":
            return None
        pol = self.kernel.defaults.requester
        b.asks += 1
        if pol.max_asks is not None and b.asks > pol.max_asks:
            return "max_asks"
        if not pol.requery and (to, question) in b.asked:
            return "requery_not_allowed"
        b.asked.add((to, question))
        return None
