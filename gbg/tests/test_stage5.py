"""Stage 5 수용 기준: 조건과 경계 모듈 (LLM 붙이기 전에 스크립트 오라클로).

요청자·경계 모듈 LLM 단계·응답자를 스크립트로 흉내 낸다. 응답자는 오라클이다: 자기 이력에 있는 조각 원문을 그대로
답한다. 경계 모듈의 스크립트는 검색 결과에 나온 처리자를 고르고(route), 조립 때 응답과 증거를 모두 싣는다(answer).
"""
import json
import re
from pathlib import Path

import pytest

from gbg.contracts.card import public_id
from gbg.kernel.runner import Runner
from gbg.kernel.tools import ToolRegistry
from gbg.llm.agent_loop import AgentRuntime, LLMAgent
from gbg.llm.context_builder import ContextBuilder
from gbg.tests import test_stage3 as T
from gbg.tests.support import FIXTURES, boundary_kwargs, load_adapter

PRIV = FIXTURES / "worldgen_mini" / "private"
GOLD = {g["wid"]: g for g in map(json.loads, (PRIV / "gold.jsonl").read_text(encoding="utf-8").splitlines())}
FRAGS = {f["fid"]: f for f in map(json.loads, (PRIV / "fragments.jsonl").read_text(encoding="utf-8").splitlines())}
SURFACE = {w["wid"]: w["surface"] for w in map(json.loads, (FIXTURES / "worldgen_mini" / "harness" / "work.jsonl")
                                               .read_text(encoding="utf-8").splitlines())}
ALIASES = ["하린 과장", "지우 과장", "도윤 대리", "서준 선임", "小野さん", "佐藤さん", "영업1팀", "개발1팀", "開発1課", "営業1課",
           "CMT-00001", "CMT-00002", "E-SEL-1000", "E-SEL-1001"]
KEYWORD = [("spend", "Budget"), ("grade", "record"), ("status", "approval")]


def _tools(req):
    return {t["function"]["name"]: t["function"] for t in req.get("tools", [])}


def _task(text: str) -> dict | None:
    m = re.search(r"\[Task (W-\d+)\]", text.split("[Current task]\n", 1)[-1])
    return GOLD.get(m.group(1)) if m else None


def _call(name, args):
    return T.mk([(name, args)])


def oracle(req, *, route_referral: dict | None = None, assemble_missing: list | None = None, interpret_missing=None):
    """스크립트 LLM: 도구 목록으로 역할을 알아본다."""
    tools, msgs = _tools(req), req["messages"]
    system, user = msgs[0]["content"], msgs[1]["content"]
    if "interpret" in tools:
        ents = [a for a in ALIASES if a in user]
        return _call("interpret", {"entities": ents, "attribute": "requested information",
                                   "missing": interpret_missing(user) if interpret_missing else []})
    if "route" in tools:
        if route_referral:
            for ent, group in route_referral.items():
                if ent in user:
                    return _call("route", {"action": "referral", "agents": [], "referral_to": group})
        members = re.findall(r"^- (\S+) \|", user.split("Members:\n", 1)[1].split("\n\n", 1)[0], re.M)
        records = user.split("Group records found:\n", 1)[1]
        agents = [a for a in members if f"] {a} · " in records]
        return _call("route", {"action": "select", "agents": agents or members[:1]})
    if "answer" in tools:
        body = "\n".join(re.findall(r"^\[(?:R|E)\d+\] .*$", user, re.M))
        missing = assemble_missing.pop(0) if assemble_missing else []
        return _call("answer", {"answer": body, "values": [], "missing": missing})
    if "dispatch" in tools:
        q = user.split("Question: ", 1)[1].split("\nPurpose:", 1)[0]
        g = next((GOLD[w] for w, surf in SURFACE.items() if surf in q), None)
        group = g["needs"][0]["group"] if g else re.findall(r"^- (\S+) \|", system, re.M)[0]
        return _call("dispatch", {"targets": [{"group": group, "question": q}], "entity": "subject", "attr": "info"})
    if "reply" in tools:                                                   # 오라클 응답자: 자기가 가진 조각 원문
        own = "\n".join(l for l in user.splitlines()                     # 남에게 받은 답은 제외
                         if re.match(r"\(day -?\d+ #\d+ \w+\) (?!\[(Answer|Question|Handled|Reply))", l))
        held = [f["text"] for f in FRAGS.values() if f["text"] in own]
        return _call("reply", {"answer": "\n".join(held) or "unknown", "missing": []})
    if "submit" in tools:
        if len(msgs) == 2 and (g := _task(user)):
            need = g["needs"][0]
            q = user.split("[Current task]\n", 1)[-1].split("] ", 1)[1].split("\n", 1)[0]
            if "ask_group" in tools:
                return _call("ask_group", {"group": need["group"], "question": q})
            if "ask" in tools:
                return _call("ask", {"question": q, "purpose": f"to complete task {g['wid']}"})
            if "ask_agent" in tools:
                region = need["group"].split("-")[1]
                word = next((w for k, w in KEYWORD if k in q), "")
                lines = [l for l in system.split("<<DIRECTORY>>\n", 1)[1].splitlines()
                         if f"Region: {region}" in l and word.lower() in l.lower()]
                if lines:
                    return _call("ask_agent", {"agent_id": lines[0][2:].split(" | ")[0], "question": q})
        props = tools["submit"]["parameters"]["properties"]
        return _call("submit", {k: T._default(v) for k, v in props.items()})
    return T.mk([])


def run(tmp, condition, script=oracle, name="worldgen_mini", max_day=None, conditions=T.CONDITIONS):
    a = load_adapter(name)
    rt = AgentRuntime(conditions[condition], a.group_tools,
                      ContextBuilder(T.TOK.count, T.P.context.raw_window, T.P.context.summary), T.P.agent.max_steps,
                      T.P.agent.format_retries)
    r = Runner(a, condition=condition, seed=7, run_dir=tmp, conditions=conditions, access=T.ACCESS,
               tools=ToolRegistry(T.ACCESS), env_tools=a.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt),
               params=T.P.kernel, llm=T.backend("SCRIPTED", script=script), tokens=T.TOK.count, max_day=max_day,
               **boundary_kwargs())
    r.run()
    return r, T.wal(tmp)


def _requester_answers(events) -> dict[str, str]:
    """과제마다 요청자가 받은 답 원문 (경계 조건은 그룹 응답, Direct는 에이전트 응답)."""
    out: dict[str, str] = {}
    for e in events:
        p = e["payload"]
        if e["type"] == "message" and p["kind"] == "response" and p.get("serving") is None \
                and not str(p["from_agent"]).startswith("boundary:"):
            out[p["task_id"]] = out.get(p["task_id"], "") + p["response"]["answer"]
    return out


def _recall(events) -> tuple[int, int]:
    got = _requester_answers(events)
    hit = n = 0
    for wid, g in GOLD.items():
        for need in g["needs"]:
            for fid in need.get("critical_components") or []:
                n += 1
                hit += FRAGS[fid]["text"] in got.get(wid, "")
    return hit, n


def _chosen(events) -> dict[str, list[str]]:
    """과제마다 요청이 도착한 담당자 (Direct: 요청자가 고른 에이전트, 경계 조건: 경계 모듈이 고른 담당자)."""
    out: dict[str, list[str]] = {}
    for e in events:
        p = e["payload"]
        if e["type"] == "boundary_decision" and p.get("stage") == "ingress":
            out.setdefault(p["task_id"], []).extend(p.get("selected", []))
        elif e["type"] == "message" and p["kind"] == "request" and e["actor"].startswith("agent:") \
                and p.get("to_agent") and p.get("serving") is None:
            out.setdefault(p["task_id"], []).append(p["to_agent"])
    return out


# ─────────────────────────── 흐름 ───────────────────────────
def test_routing_forwards_original_request_and_returns_replies_verbatim(tmp_path):
    r, ev = run(tmp_path, "routing")
    decisions = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["stage"] == "ingress"]
    assert decisions and all(d["deliver"] == "forward" and d["router_guard"] == [] for d in decisions)
    inner = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["actor"].startswith("boundary:")]
    for d in decisions:
        sent = [m for m in inner if m["rid"].startswith(d["rid"] + ".") or m["rid"].startswith(d["rid"])]
        assert sent and all(m["request"]["question"] == d["question"] for m in sent), "요청 원문 그대로"
    got = [e["payload"]["response"]["answer"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
           and e["actor"].startswith("boundary:")]
    assert got and all(a.startswith("[Reply 1] ") for a in got if a)
    assert not (tmp_path / "obs" / "run_invalid.jsonl").exists()


def test_boundary_calls_are_charged_to_the_task_budget(tmp_path):
    r, ev = run(tmp_path, "ingress", max_day=1)
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    assert answers and all(a["budget"]["by_component"]["boundary"]["calls"] >= 3 for a in answers)   # 해석·선택·조립
    llm = [json.loads(x) for x in (tmp_path / "obs" / "llm.jsonl").read_text(encoding="utf-8").splitlines()]
    assert {x["component"] for x in llm} >= {"requester", "boundary", "responder"}
    assert all(x["tokens"] == x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"] for x in llm)


def test_selection_has_no_headcount_limit(tmp_path):
    """검색 결과의 처리자 전원을 고른다 (최대 3명 삭제)."""
    r, ev = run(tmp_path, "routing")
    chosen = _chosen(ev)
    assert max(len(set(v)) for v in chosen.values()) >= 2


# ─────────────────────────── 수용 기준 ───────────────────────────
def test_routing_hits_handler_more_often_than_direct_on_state_B(tmp_path):
    def hit_rate(events):
        chosen, hit, n = _chosen(events), 0, 0
        for wid, g in GOLD.items():
            if g.get("state_class") != "B":
                continue
            holders = {FRAGS[f]["agent"] for need in g["needs"] for f in need.get("critical_components") or []}
            n += 1
            hit += bool(holders & set(chosen.get(wid, [])))
        return hit / n
    _, direct = run(tmp_path / "d", "direct")
    _, routing = run(tmp_path / "r", "routing")
    assert hit_rate(routing) > hit_rate(direct)


def test_ingress_recall_is_complete_and_routing_is_lower(tmp_path):
    """오라클 응답자 기준: Ingress는 떠난 처리자의 이력도 증거로 조립해 조각을 모두 전달하고, Routing은 활동 중인
    담당자의 응답만 전달한다."""
    _, ingress = run(tmp_path / "i", "ingress")
    _, routing = run(tmp_path / "r", "routing")
    hi, n = _recall(ingress)
    hr, _ = _recall(routing)
    assert hi == n and hr < hi


def test_ie_learns_referral_and_routes_directly_next_time(tmp_path):
    """소유권 예외: FIN-SEL이 영업1팀 건을 FIN-TYO로 보낸다(referral). I+E는 재전송하고 egress_log에 남긴 뒤, 같은
    (엔티티, 속성) 요청은 처음부터 FIN-TYO로 보낸다 (코드가 LLM 결정을 덮어씀)."""
    def script(req):
        tools = _tools(req)
        if "route" in tools and "Request from HR-SEL" in req["messages"][1]["content"] \
                and "FIN-SEL" in req["messages"][0]["content"]:
            return oracle(req, route_referral={"영업1팀": "FIN-TYO", "하린 과장": "FIN-TYO", "서준 선임": "FIN-TYO"})
        if "dispatch" in tools:
            out = oracle(req)
            args = json.loads(out["tool_calls"][0]["arguments"])
            args["entity"], args["attr"] = "영업1팀", "available budget"
            return _call("dispatch", args)
        return oracle(req)
    _, ev = run(tmp_path, "i_e", script=script)
    egress = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["stage"] == "egress"]
    first = next(d for d in egress if any(x["status"] == "referral" for x in d.get("log", [])))
    assert [x["to_group"] for x in first["log"]][:2] == ["FIN-SEL", "FIN-TYO"], "referral 받고 FIN-TYO로 1회 재전송"
    later = [d for d in egress if d["group"] == first["group"] and d["task_id"] > first["task_id"]
             and d.get("entity") == "영업1팀"]                              # egress_log는 그룹마다
    assert later and all(d["referral_override"] == "FIN-TYO" and d["targets"][0]["group"] == "FIN-TYO" for d in later)


def test_core_conditions_run_on_both_benchmarks_without_core_changes(tmp_path):
    for name in ("worldgen_mini", "silo_mini"):
        for cond in ("direct", "routing", "ingress", "i_e"):
            _, ev = run(tmp_path / name / cond, cond, name=name, max_day=1)
            assert any(e["type"] == "answer" for e in ev), (name, cond)


# ─────────────────────────── 조립 세부 ───────────────────────────
def test_ingress_requery_version_marks_and_boundary_state(tmp_path):
    prompts = []

    def script(req):
        tools = _tools(req)
        if "answer" in tools:
            prompts.append(req["messages"][1]["content"])
        if "ask_group" in tools and len(req["messages"]) == 2 and "[Task W-008]" in req["messages"][1]["content"]:
            return _call("ask_group", {"group": "FIN-SEL", "question": SURFACE["W-002"]})   # 같은 엔티티를 다시 묻는다
        return oracle(req, assemble_missing=[["settlement day"]] if len(prompts) == 1 else None)
    _, ev = run(tmp_path, "ingress", script=script)
    ing = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["stage"] == "ingress"
           and e["payload"].get("action") == "select"]
    assert ing[0]["requery"], "빠진 항목이 있으면 1회 재질의"
    follow = [e["payload"]["request"]["question"] for e in ev if e["type"] == "message"
              and e["payload"]["kind"] == "request" and e["actor"].startswith("boundary:")]
    assert any(q.startswith("Follow-up from your group's intake desk") and "settlement day" in q for q in follow)
    assert any("Database versions:\n[D1]" in p for p in prompts), "버전 표시: DB 키·버전 번호"
    assert any("Earlier exchanges of this desk:\n[S1]" in p for p in prompts), "경계 상태: 같은 엔티티의 과거 문답"


def test_ingress_sel_definition_has_no_state_versions_or_requery():
    sel = T.CONDITIONS["ingress_sel"].ingress
    assert sel.deliver == "assemble" and not (sel.requery or sel.boundary_state or sel.version_marks)


def test_need_more_when_interpretation_is_missing_items(tmp_path):
    def script(req):
        return oracle(req, interpret_missing=lambda u: ["which department"] if "Is CMT-00001" in u else [])
    _, ev = run(tmp_path, "routing", script=script)
    nm = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"].get("action") == "need_more"]
    assert nm
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["actor"].startswith("boundary:") and e["payload"]["response"]["status"] == "need_more"]
    assert resp and resp[0]["need"] == ["which department"]


def test_boundary_budget_exhaustion_sends_requester_to_final_answer(tmp_path):
    conds = T.load_conditions(T.ROOT / "configs" / "conditions.yaml")
    conds.defaults = conds.defaults.model_copy(update={"budget": conds.defaults.budget.model_copy(update={"calls": 3})})
    _, ev = run(tmp_path, "ingress", max_day=1, conditions=conds)
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    assert answers and all(a["budget"]["used"]["calls"] <= 3 for a in answers)
    assert any(e["payload"]["response"]["answer"] == "budget_exhausted" for e in ev
               if e["type"] == "message" and e["payload"]["kind"] == "response")


# ─────────────────────────── full_load (참조 행) ───────────────────────────
def _full_load_script(loads):
    """요청자: 필요한 그룹의 이력을 두 번 불러오고(두 번째는 캐시), 다른 그룹 DB도 조회한 뒤 제출."""
    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "submit" in tools and "load_group_history" in tools:
            g = _task(msgs[1]["content"])
            n = sum(1 for m in msgs if m["role"] == "tool")
            if g and n < loads:
                return _call("load_group_history", {"group": g["needs"][0]["group"]})
            if g and n == loads and "db.query" in tools:
                return _call("db.query", {"group": g["needs"][0]["group"], "entity": "영업1팀",
                                          "record_type": tools["db.query"]["parameters"]["properties"]["record_type"]["enum"][0]})
        return oracle(req)
    return script


def test_full_load_tools_history_cache_and_no_budget_cap(tmp_path):
    sent = []
    inner = _full_load_script(2)

    def script(req):
        sent.append(_tools(req))
        return inner(req)
    r, ev = run(tmp_path, "full_load", script=script)
    schemas = next(t for t in sent if "submit" in t)
    assert "group" in schemas["db.query"]["parameters"]["properties"] and "load_group_history" in schemas
    types = schemas["db.query"]["parameters"]["properties"]["record_type"]["enum"]
    assert set(r.adapter.group_tools("HR-SEL")[0].parameters["properties"]["record_type"]["enum"]) < set(types), \
        "모든 그룹의 기록 종류"
    fl = [json.loads(x) for x in (tmp_path / "obs" / "full_load.jsonl").read_text(encoding="utf-8").splitlines()]
    first, again = fl[0], fl[1]
    assert not first["cached"] and again["cached"], "같은 과제 안에서 같은 그룹 재호출은 캐시"
    results = [e["payload"] for e in ev if e["type"] == "tool_result" and e["payload"]["tool"] == "load_group_history"]
    w5 = next(p for p in results if p["task_id"] == "W-005")
    assert FRAGS["FR-C1"]["text"] in w5["result"]["records"], "이탈자(fin-sel.a2)의 이력도 포함"
    assert public_id("fin-sel.a2") in w5["result"]["records"] and "fin-sel" not in w5["result"]["records"]
    days = [int(m) for m in re.findall(r"^\(day (-?\d+) ·", w5["result"]["records"], re.M)]
    assert days == sorted(days), "시간순"
    llm = [json.loads(x) for x in (tmp_path / "obs" / "llm.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(x["cached_tool_result"] for x in llm), "캐시된 결과가 들어간 호출은 따로 표시"
    assert all(x["tokens"] == x["usage"]["prompt_tokens"] + x["usage"]["completion_tokens"] for x in llm)
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    assert all(a["budget"]["limit"] == {"calls": None, "tokens": None} for a in answers), "참조 행: 상한 미적용"
    q = [e["payload"] for e in ev if e["type"] == "tool_result" and e["payload"]["tool"] == "db.query"]
    assert q and all(x["ok"] for x in q), "다른 그룹 DB 조회 허용"


def test_full_load_truncates_oldest_lines_at_limit(tmp_path):
    from gbg.kernel.full_load import load_history_tool
    from gbg.kernel.tools import ToolCall
    from gbg.stores import Stores
    s = Stores.from_adapter(load_adapter("worldgen_mini"), card_mode="static", rounds_per_day=3)
    cache = {}
    full = load_history_tool(s, T.TOK.count, 10**9, lambda: cache).fn(ToolCall("hr-sel.a1", "HR-SEL", 1, 1, {"group": "FIN-SEL"}))
    cache.clear()
    cut = load_history_tool(s, T.TOK.count, 200, lambda: cache).fn(ToolCall("hr-sel.a1", "HR-SEL", 1, 1, {"group": "FIN-SEL"}))
    assert not full.result["truncated"] and cut.result["truncated"]
    rec = cut.obs[0][1]
    assert rec["tokens"] <= 200 and rec["dropped_tokens"] > 0 and rec["truncated"]
    assert full.result["records"].endswith(cut.result["records"]), "오래된 줄부터 버린다"


def test_full_load_orders_by_day_round_and_wal_seq(tmp_path):
    """같은 날 안에서는 (라운드, WAL 순번)으로 섞는다: 에이전트 이름 순으로 묶지 않는다."""
    r, ev = run(tmp_path, "direct", max_day=2)
    from gbg.kernel.full_load import load_history_tool
    from gbg.kernel.tools import ToolCall
    out = load_history_tool(r.stores, T.TOK.count, 10**9, lambda: {}).fn(ToolCall("hr-sel.a1", "HR-SEL", 2, 1, {"group": "FIN-SEL"}))
    entries = sorted(((e.day, e.round, e.order, a) for a, (g, _) in r.stores.members.items() if g == "FIN-SEL"
                      for e in r.stores.history.entries(a) if e.day >= 1), key=lambda x: (x[0], x[1], x[2]))
    assert entries and all(o is not None for _, _, o, _ in entries), "실행 중 항목은 WAL 순번을 가진다"
    shown = [public_id(a) for *_, a in entries]
    got = [m for m in re.findall(r"^\(day \d+ · (agent-\w+)\)", out.result["records"], re.M)]
    assert got[-len(shown):] == shown
