"""부록 조건 (2026-09-30): direct_relay, retrieve, sidecar. 기존 조건은 건드리지 않고 이 조건에서만 켜진다."""
import json
import re

import pytest

from gbg.contracts.conditions import Condition, ConditionSet, RelayConfig
from gbg.tests import test_stage3 as T
from gbg.tests.test_stage5 import _tools, oracle, run


def _set(**over) -> ConditionSet:
    conds = dict(T.CONDITIONS)
    conds.update(over)
    return ConditionSet(conds, T.CONDITIONS.defaults)


def _members(system: str) -> list[str]:
    part = system.split("Members of your group", 1)[1] if "Members of your group" in system else ""
    return re.findall(r"^- (\S+) \|", part, re.M)


def test_appendix_conditions_load_and_invalid_combinations_are_rejected():
    c = T.CONDITIONS
    assert c["direct_relay"].relay.max_asks == 3 and c["direct_relay"].agent_tool == "ask_agent"
    assert c["retrieve"].ingress.deliver == "read" and c["retrieve"].budget_bonus_calls == 1
    assert c["sidecar"].sidecar.deliver == "assemble" and c["sidecar"].sidecar.version_marks
    assert not (c["sidecar"].sidecar.requery or c["sidecar"].sidecar.boundary_state)
    base = c["routing"].model_dump()
    with pytest.raises(ValueError):
        Condition.model_validate({**base, "relay": {"max_asks": 3}})             # relay는 Direct에만
    with pytest.raises(ValueError):
        Condition.model_validate({**c["direct"].model_dump(), "sidecar": {"deliver": "assemble", "requery": True}})


def test_direct_relay_responder_asks_own_group_colleagues_up_to_the_limit(tmp_path):
    """요청자에게 직접 받은 응답자만(홉 1) 자기 그룹 동료에게 되묻고, 받은 요청 하나당 max_asks번까지. 동료는 되묻지 못한다."""
    conds = _set(direct_relay=T.CONDITIONS["direct_relay"].model_copy(update={"relay": RelayConfig(max_asks=1)}))
    seen = []

    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "reply" in tools:
            seen.append(("ask_colleague" in tools, _members(msgs[0]["content"])))
            if "ask_colleague" in tools and len(msgs) == 2:
                ms = _members(msgs[0]["content"])
                return T.mk([("ask_colleague", {"agent_id": m, "question": "Do your records have this?"}) for m in ms[:2]])
        return oracle(req)
    _, ev = run(tmp_path, "direct_relay", script=script, max_day=1, conditions=conds)
    relay = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["payload"].get("serving")]
    assert relay, "응답자의 되묻기가 없다"
    by = {}
    for p in relay:
        by.setdefault(p["serving"], []).append(p)
        assert p["request"]["from_group"] == p["request"]["to_group"]           # 자기 그룹 동료에게만
    for ps in by.values():
        assert sum(p["delivered"] for p in ps) <= 1                              # 상한 1
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["payload"].get("serving")]
    if any(len(ps) > 1 for ps in by.values()):
        assert any(r["status"] == "error" and r["answer"] == "relay_limit" for r in resp)
    assert any(not can for can, _ in seen)                                       # 동료(홉 2)에게는 도구가 없다
    assert all(ms for can, ms in seen if can)                                    # 되물을 수 있는 응답자는 동료 명단을 본다


def test_direct_responders_still_cannot_ask(tmp_path):
    seen = []

    def script(req):
        if "reply" in _tools(req):
            seen.append(set(_tools(req)))
        return oracle(req)
    run(tmp_path, "direct", script=script, max_day=1)
    assert seen and all("ask_colleague" not in t and "ask_agent" not in t for t in seen)


def test_retrieve_forwards_replies_and_records_and_adds_one_call(tmp_path):
    descs = []

    def script(req):
        if "submit" in _tools(req) and "ask_group" in _tools(req):
            descs.append(_tools(req)["ask_group"]["description"])
        return oracle(req)
    r, ev = run(tmp_path, "retrieve", script=script, max_day=1)
    assert descs and all("records found" in d for d in descs)
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["payload"].get("to_group") and not e["payload"].get("serving")]
    assert any("[Group records]" in x["answer"] for x in resp)
    cfg = json.loads((tmp_path / "run.json").read_text())
    assert cfg["defaults"]["budget"]["calls"] == T.CONDITIONS.defaults.budget.calls + 1
    routing_cfg = T.CONDITIONS["routing"]
    assert routing_cfg.budget_bonus_calls == 0


def test_sidecar_keeps_the_agent_reply_and_adds_group_records(tmp_path):
    """받은 에이전트 혼자 답하고, 그 에이전트의 모듈이 그룹 기록으로 보탠다. 다른 구성원에게 묻지 않고 상태가 없다."""
    r, ev = run(tmp_path, "sidecar", max_day=1)
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision"]
    assert dec and all(d["stage"] == "sidecar" and d["selected"] == [d["agent"]] for d in dec)
    inner = [e for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
             and (e["payload"].get("serving") or "").count("/")]
    assert not [e for e in inner if e["payload"]["from_agent"].startswith("boundary:")]   # 내부 질의 없음
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["payload"]["to_agent"] and not e["payload"].get("serving")]
    assert resp and all(x["answer"].startswith("[Reply 1]") for x in resp if x["status"] != "error")
    assert not any(r.stores.boundary_log.lookup(g, ["영업1팀", "개발1팀"]) for g in r.kernel.sidecars)
    calls = [e["payload"] for e in ev if e["type"] == "llm_call" and e["payload"]["component"] == "boundary"]
    assert calls                                                                 # 모듈 호출은 과제 예산의 boundary 몫
