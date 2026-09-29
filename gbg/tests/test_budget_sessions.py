"""조건 개정(2026-09-28) 반영: 순차 실행과 정답 기준 시점, 과제 예산, 요청자 권한, 응답자 세션, 실행 거부 조건."""
import json
from gbg.contracts.card import public_id
from pathlib import Path

import pytest

from gbg.agents.scripted import ScriptedAgent
from gbg.contracts.conditions import (
    Budget, ConditionSet, ConfigError, Defaults, FinalReserve, RequesterPolicy, load_conditions,
)
from gbg.contracts.envelope import Response
from gbg.contracts.schemas import TimelineEvent
from gbg.kernel.runner import Runner
from gbg.kernel.tools import ToolRegistry
from gbg.tests.support import load_adapter
from gbg.tests.test_stage3 import ACCESS, CONDITIONS, P, TOK, auto_reply, backend, llm_runner, mk, wal

ROOT = Path(__file__).resolve().parents[2]


def with_defaults(calls=None, tokens=None, reserve_calls=1, reserve_tokens=0, max_asks=None, requery=True, **cond_updates):
    d = Defaults(budget=Budget(calls=calls, tokens=tokens), final_reserve=FinalReserve(calls=reserve_calls, tokens=reserve_tokens),
                 requester=RequesterPolicy(max_asks=max_asks, requery=requery))
    conds = {n: (c.model_copy(update=cond_updates) if n == "direct" else c) for n, c in CONDITIONS.items()}
    return ConditionSet(conds, d)


def run_llm(tmp, script=auto_reply, conditions=CONDITIONS, name="worldgen_mini", max_day=1):
    llm_runner(tmp, backend("SCRIPTED", script=script), name=name, max_day=max_day, conditions=conditions).run()
    return wal(tmp)


def answers(ev):
    return {e["payload"]["task_id"]: e["payload"] for e in ev if e["type"] == "answer"}


# ─────────────────────────── 실행 거부 조건 ───────────────────────────
def test_blocked_condition_is_refused(tmp_path):
    a = load_adapter("worldgen_mini")
    with pytest.raises(ConfigError, match="direct_dyncard"):
        Runner(a, condition="direct_dyncard", seed=7, run_dir=tmp_path, conditions=CONDITIONS, access=ACCESS,
               tools=ToolRegistry(ACCESS), agent_factory=lambda *x: ScriptedAgent(x[0]))
    assert not (tmp_path / "wal").exists()


# ─────────────────────────── 과제 예산 ───────────────────────────
def test_unlimited_budget_records_consumption_by_component(tmp_path):
    ev = run_llm(tmp_path)
    ans = answers(ev)
    calls = [e for e in ev if e["type"] == "llm_call"]
    for tid, a in ans.items():
        mine = [c for c in calls if c["payload"]["task_id"] == tid]
        b = a["budget"]
        assert b["used"]["calls"] == len(mine) and not b["budget_exhausted"]
        assert b["used"]["tokens"] == sum(c["payload"]["usage"]["prompt_tokens"] + c["payload"]["usage"]["completion_tokens"]
                                          for c in mine)
        for comp in ("requester", "responder"):
            assert b["by_component"][comp]["calls"] == sum(c["payload"]["component"] == comp for c in mine)
        assert b["by_component"]["requester"]["directory_tokens"] > 0 and b["by_component"]["requester"]["tool_def_tokens"] > 0
    w = ans["W-001"]["budget"]
    assert w["by_component"]["responder"]["calls"] > 0, "중첩 요청(응답자 호출)도 같은 과제 예산에 합산"


def test_call_budget_reserves_final_answer(tmp_path):
    ev = run_llm(tmp_path, conditions=with_defaults(calls=3))
    ans = answers(ev)
    w = ans["W-001"]
    assert w["budget"]["budget_exhausted"] and w["budget"]["final_call_used"]
    assert w["budget"]["used"]["calls"] <= 3 and w.get("error") is None and w["answer"], "예약된 호출로 답했다"
    final = [e for e in ev if e["type"] == "llm_call" and e["payload"]["task_id"] == "W-001" and e["payload"]["final"]]
    assert len(final) == 1 and final[0]["payload"]["component"] == "requester"
    for a in ans.values():
        assert a["budget"]["used"]["calls"] <= 3


def test_final_call_offers_only_submit(tmp_path):
    seen = []
    def spy(req):
        seen.append(req)
        return auto_reply(req)
    run_llm(tmp_path, script=spy, conditions=with_defaults(calls=2))
    finals = [r for r in seen if any("budget for this task is used up" in (m.get("content") or "") for m in r["messages"])]
    assert finals and all([t["function"]["name"] for t in r["tools"]] == ["submit"] for r in finals)


def test_responder_hits_budget_and_requester_gets_error(tmp_path):
    ev = run_llm(tmp_path, conditions=with_defaults(calls=3))
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["payload"]["task_id"] == "W-001"]
    assert any(r["status"] == "error" and r["answer"] == "budget_exhausted" for r in resp)


def test_token_admission_counts_estimate_and_reserve():
    from gbg.kernel.budget import BudgetExhausted, TaskBudget
    b = TaskBudget("T", "a", with_defaults(tokens=1000, reserve_tokens=200).defaults)
    b.admit(False, estimate=800)                                                # 0 + 800 + 200 ≤ 1000
    b.charge("requester", {"prompt_tokens": 500, "completion_tokens": 50}, None, False)
    with pytest.raises(BudgetExhausted):
        b.admit(False, estimate=300)                                            # 550 + 300 + 200 > 1000
    assert b.exhausted
    b.admit(True, estimate=10_000)                                              # 최종 호출은 토큰으로 막지 않는다


def test_token_budget_run(tmp_path):
    # 호출당 프롬프트 추정 약 1,300토큰: 첫 호출은 0 + 1,300 + 1,000 ≤ 2,500로 허용, 둘째 호출은 거부 → 최종 호출
    ev = run_llm(tmp_path, conditions=with_defaults(tokens=2500, reserve_tokens=1000))
    ans = answers(ev)
    assert ans["W-001"]["budget"]["budget_exhausted"] and ans["W-001"]["budget"]["final_call_used"]
    for tid, a in ans.items():
        nonfinal = sum(c["payload"]["usage"]["prompt_tokens"] + c["payload"]["usage"]["completion_tokens"]
                       for c in ev if c["type"] == "llm_call" and c["payload"]["task_id"] == tid and not c["payload"]["final"])
        assert nonfinal <= 2500, tid


# ─────────────────────────── 요청자 권한 ───────────────────────────
class TwoAsks(ScriptedAgent):
    async def work(self, ctx, task):
        rs = [await ctx.ask("fin-sel.a1", "same question") for _ in range(2)]
        return {"statuses": [r.status + ":" + r.answer for r in rs]}


def run_scripted(tmp, conditions, factory):
    a = load_adapter("worldgen_mini")
    Runner(a, condition="direct", seed=7, run_dir=tmp, conditions=conditions, access=ACCESS, tools=ToolRegistry(ACCESS),
           env_tools=a.make_tools, agent_factory=factory, params=P.kernel, max_day=1).run()
    return wal(tmp)


@pytest.mark.parametrize("policy,second", [({"max_asks": 1}, "error:max_asks"),
                                           ({"requery": False}, "error:requery_not_allowed"),
                                           ({}, "ok:unknown")])
def test_requester_policy(tmp_path, policy, second):
    ev = run_scripted(tmp_path, with_defaults(**policy), lambda aid, g, role: TwoAsks(aid))
    got = answers(ev)["W-001"]["answer"]["statuses"]
    assert got[0] == "ok:unknown" and got[1] == second


# ─────────────────────────── 응답자 세션 ───────────────────────────
class ToolResponder(ScriptedAgent):
    """교차 작업이면 fin-sel.a1에게 묻고, 응답할 때는 환경 도구를 한 번 쓴다."""
    async def work(self, ctx, task):
        if task.kind == "cross" and ctx.agent_id != "fin-sel.a1":
            await ctx.ask("fin-sel.a1", "Check 영업1팀 budget please.")
        return {}

    async def respond(self, ctx, request):
        await ctx.call_tool("entity.search", query="영업")
        return Response(rid=request.rid, status="ok", answer="about 영업1팀", values=[], missing=[],
                        referral_to=None, need=[], as_of=ctx.day)


@pytest.mark.parametrize("session", ["persistent", "ephemeral"])
def test_responder_session(tmp_path, session):
    run_dir = tmp_path / session
    a = load_adapter("worldgen_mini")
    r = Runner(a, condition="direct", seed=7, run_dir=run_dir, conditions=with_defaults(responder_session=session),
               access=ACCESS, tools=ToolRegistry(ACCESS), env_tools=a.make_tools,
               agent_factory=lambda aid, g, role: ToolResponder(aid), params=P.kernel, max_day=1)
    r.run()
    warm = len(a.initial_state("FIN-SEL").histories["fin-sel.a1"])
    new = [e.text for e in r.stores.history.entries("fin-sel.a1")[warm:]]
    asked = [e.text for e in r.stores.history.entries("hr-sel.a3")]
    if session == "ephemeral":
        assert new and all(t.startswith("[Handled a request from ") for t in new if "request" in t or "Question" in t)
        assert not any(t.startswith(("[Question from", "[Tool call] entity.search", "[Answer to")) for t in new)
    else:
        assert any(t.startswith("[Question from") for t in new) and any(t.startswith("[Tool call] entity.search") for t in new)
    assert any(t.startswith(f"[Question to {public_id('fin-sel.a1')}]") for t in asked), "요청자 쪽 이력은 세션 규칙과 무관"


# ─────────────────────────── 정답 기준 시점 ───────────────────────────
class InjectedAdapter:
    """W-001 바로 앞에 같은 날 등록되는 DB 쓰기를 끼워 넣는다 (seq는 다시 매김)."""
    def __new__(cls):
        a = load_adapter("worldgen_mini")
        evs = list(a._events)
        i = next(k for k, e in enumerate(evs) if e.task_id == "W-001")
        w = evs[i]
        write = TimelineEvent(eid="EV-X", seq=1, day=w.day, round=w.round, kind="db_register", group="FIN-SEL",
                              payload={"key": "FIN-SEL/line/영업1팀/remaining",
                                       "version": {"v": 2, "day": w.day, "db_day": w.day, "value": 999_001}})
        evs.insert(i, write)
        a._events = [e.model_copy(update={"seq": n}) for n, e in enumerate(evs, 1)]
        return a


class Looker(ScriptedAgent):
    async def work(self, ctx, task):
        r = await ctx.call_tool("db.query", entity="영업1팀", record_type="budget_line_balance")
        return {"seen": r["result"].get("record")}


def test_task_sees_world_as_of_its_arrival(tmp_path):
    a = InjectedAdapter()
    Runner(a, condition="direct", seed=7, run_dir=tmp_path, conditions=CONDITIONS, access=ACCESS,
           tools=ToolRegistry(ACCESS), env_tools=a.make_tools, agent_factory=lambda aid, g, role: Looker(aid),
           params=P.kernel, max_day=1).run()
    ans = answers(wal(tmp_path))
    assert ans["W-001"]["answer"]["seen"] == 999_001, "같은 라운드라도 도착 seq보다 앞선 세계 이벤트는 보인다"
