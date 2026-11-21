"""리버탈 조건 (2026-11-22): ingress_plain_sym, ingress_no_requery, rag_only. 기존 조건은 건드리지 않고 이 조건에서만 켜진다."""
import asyncio
from types import SimpleNamespace

import pytest

from gbg.boundary import prompts as P
from gbg.boundary.module import BoundaryModule
from gbg.contracts.conditions import Condition
from gbg.contracts.envelope import Conflict, Item, Proposal, Request, Response
from gbg.tests import test_stage3 as T
from gbg.tests.test_stage5 import _tools, oracle, run

REQ = Request(rid="r1", from_group="A", from_agent="a.1", to_group="B", to_agent=None, question="q?", purpose=None,
              origin_task="W-00001", hop=1, lineage=["A"])


def _item(v, ref="D1"):
    return Item(entity="X-1", attribute="amount", value=v, status="", ref=ref)


def _reply(missing=(), status=None):
    return Response(rid="r1", status=status or ("partial" if missing else "ok"), answer="I found 100.",
                    items=[_item("100")], missing=list(missing), referral_to=None, need=[], as_of=3)


def _out(missing=(), summary="Record E1 adds 200."):
    """조립 결과 (_assemble의 반환: 구성원 항목 + additions)."""
    items = [_item("100", "Reply 1: D1"), _item("200", "[E1]")]
    return Response(rid="r1", status="partial" if missing else "ok", answer=summary, items=items, missing=list(missing),
                    referral_to=None, need=[], as_of=3, conflicts=[Conflict(item="X-1", note="differs", refs=["[E1]"])],
                    proposals=[Proposal(item="X-1", value="200", refs=["[E1]"], rationale="later record")])


def _fake(cond_name, out):
    """sidecar()·_with_replies()를 그대로 부르기 위한 최소 모듈: 준비·조립은 주어진 결과를 돌려준다."""
    c = T.CONDITIONS[cond_name]
    cond = c if c.sidecar is None else c.model_copy(update={"ingress": c.sidecar})
    m = SimpleNamespace(group="B", cond=cond, _gw={})
    m._ctx = lambda ctx, span, req: SimpleNamespace(day=3, round=1, task_id="W-00001", actor="boundary:B")

    async def prepare(*a):
        return "q?", SimpleNamespace(attribute="amount", entities=[]), [], None

    async def assemble(*a):
        return out
    m._prepare, m._assemble = prepare, assemble
    m._forward = lambda *a: BoundaryModule._forward(m, *a)
    return m


def _sidecar(reply, out):
    m = _fake("sidecar", out)
    span = SimpleNamespace(emit=lambda *a, **k: None)
    ctx = SimpleNamespace(kernel=SimpleNamespace(stores=None), task_id="W-00001")
    return asyncio.run(BoundaryModule.sidecar(m, ctx, span, REQ, "b.1", reply))


def _plain(replies, out, on_failure="forward"):
    m = _fake("ingress_plain_sym", out)
    m.cond = m.cond.model_copy(update={"ingress": m.cond.ingress.model_copy(update={"on_failure": on_failure})})
    trace = {}
    resp = BoundaryModule._with_replies(m, SimpleNamespace(day=3), REQ, out, replies, trace)
    return resp, trace


def test_rebuttal_conditions_load_and_invalid_combinations_are_rejected():
    c = T.CONDITIONS
    sym, side = c["ingress_plain_sym"].ingress, c["sidecar"].sidecar
    assert sym.reply_text and sym.on_failure == "forward" and not (sym.requery or sym.boundary_state)
    assert sym.model_dump(exclude={"reply_text", "on_failure"}) == side.model_dump(exclude={"reply_text", "on_failure"})
    nr, ing = c["ingress_no_requery"], c["ingress"]
    assert nr.blocked is None and not nr.ingress.requery
    assert nr.ingress.model_dump(exclude={"requery"}) == ing.ingress.model_dump(exclude={"requery"})   # 재질의 하나만 다르다
    rag = c["rag_only"].ingress
    assert not rag.internal_query and not rag.boundary_state and rag.version_marks
    assert c["gateway_rag"].ingress.model_dump(exclude={"boundary_state"}) == rag.model_dump(exclude={"boundary_state"})
    base = c["routing"].model_dump()
    with pytest.raises(ValueError):                                              # forward에 reply_text 불가
        Condition.model_validate({**base, "ingress": {"deliver": "forward", "reply_text": True}})
    with pytest.raises(ValueError):                                              # 묻지 않는 창구에 reply_text 불가
        Condition.model_validate({**base, "ingress": {"deliver": "assemble", "internal_query": False, "reply_text": True}})
    with pytest.raises(ValueError):                                              # sidecar 설정에는 두 플래그를 쓸 수 없다
        Condition.model_validate({**c["direct"].model_dump(), "sidecar": {"deliver": "assemble", "on_failure": "forward"}})


@pytest.mark.parametrize("reply_missing,out_missing", [(["due date"], []), ([], ["due date"]), ([], []),
                                                       (["due date"], ["due date", "owner"])])
def test_plain_sym_response_equals_sidecar_for_one_member(reply_missing, out_missing):
    """구성원 답 1개와 같은 조립 결과에서 ingress_plain_sym의 Response가 sidecar의 Response와 모든 필드에서 같다."""
    reply, out = _reply(reply_missing), _out(out_missing)
    side = _sidecar(reply, out)
    sym, trace = _plain([("b.1", reply)], out)
    assert sym.model_dump() == side.model_dump()
    assert trace["assembly_fallback"] is False


def test_plain_sym_joins_several_replies_and_merges_their_missing():
    r1, r2 = _reply(["owner"]), _reply(["due date", "owner"]).model_copy(update={"answer": "Not in my records."})
    sym, _ = _plain([("b.1", r1), ("b.2", r2)], _out(["amount"]))
    assert sym.answer == ("[Reply 1] (partial) I found 100.\n[Reply 2] (partial) Not in my records."
                          "\n\n[Notes from the group's records] Record E1 adds 200.")
    assert sym.missing == ["owner", "due date", "amount"] and sym.status == "partial"
    empty, _ = _plain([("b.1", _reply())], _out(summary=""))
    assert empty.answer == "[Reply 1] (ok) I found 100." and empty.status == "ok"


def test_plain_sym_assembly_failure_forwards_replies_or_keeps_the_error():
    failed = Response(rid="r1", status="error", answer="assembly_failed", items=[], missing=[], referral_to=None,
                      need=[], as_of=3)
    replies = [("b.1", _reply(["owner"]))]
    fwd, trace = _plain(replies, failed)
    routing = BoundaryModule._forward(_fake("routing", failed), SimpleNamespace(day=3), REQ, replies, None, {})
    assert trace["assembly_fallback"] is True and fwd.model_dump() == routing.model_dump()
    assert fwd.answer.startswith("[Reply 1] (partial) I found 100.") and fwd.items[0].ref == "Reply 1: D1"
    err, trace = _plain(replies, failed, on_failure="error")
    assert err.status == "error" and err.answer == "assembly_failed" and trace["assembly_fallback"] is False
    none, trace = _plain([], failed)
    assert none.status == "error" and trace["assembly_fallback"] is False      # 답이 없으면 기존 오류


def test_plain_sym_end_to_end_keeps_member_text_without_requery_or_state(tmp_path):
    systems = []

    def script(req):
        if "answer" in _tools(req):
            systems.append((req["messages"][0]["content"], req["messages"][1]["content"]))
        return oracle(req)
    _, ev = run(tmp_path, "ingress_plain_sym", script=script, max_day=1)
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision"]
    assert dec and all(d["requery"] == [] for d in dec if "requery" in d)
    assert any("assembly_fallback" in d for d in dec)
    assert systems and all("Earlier exchanges of this desk" not in u and "[S1]" not in s for s, u in systems)
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["payload"]["to_agent"] is None and not e["payload"].get("serving")]           # 창구 → 요청자
    assert resp and all(x["answer"].startswith("[Reply 1]") for x in resp if x["status"] in ("ok", "partial"))


def test_rag_only_answers_from_records_without_asking_members(tmp_path):
    seen = {"assemble": [], "ask": []}

    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "answer" in tools:
            seen["assemble"].append((msgs[0]["content"], msgs[1]["content"], tools["answer"]["description"]))
        if "submit" in tools and "ask_group" in tools:
            seen["ask"].append(tools["ask_group"]["description"])
        return oracle(req)
    _, ev = run(tmp_path, "rag_only", script=script, max_day=1)
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision"]
    assert dec and all(d["action"] == "coordinate" for d in dec)
    assert not [e for e in ev if e["type"] == "llm_call" and e["payload"]["component"] == "responder"]
    assert not [e for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
                and e["payload"]["from_agent"].startswith("boundary:")]          # 구성원에게 간 메시지 없음
    assert seen["assemble"] and all(s.startswith("You are the intake desk of a business group. No member is asked")
                                    and "Replies:" not in u and d == P.ANSWER_TOOL_RECORDS["description"]
                                    for s, u, d in seen["assemble"])
    assert seen["ask"] and all("without asking its members" in d for d in seen["ask"])

