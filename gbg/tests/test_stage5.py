"""Stage 5 수용 기준: 조건과 경계 모듈 (LLM 붙이기 전에 스크립트 오라클로).

요청자·경계 모듈 LLM 단계·응답자를 스크립트로 흉내 낸다. 응답자는 오라클이다: 자기 이력에 있는 조각 원문을 그대로
답한다. 경계 모듈의 스크립트는 검색 결과에 나온 처리자를 고르고(route), 조립 때 응답과 증거를 모두 싣는다(answer).
"""
import json
import re
from pathlib import Path

import pytest

from gbg.contracts.card import public_id
from gbg.contracts.envelope import render_response
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


def oracle(req, *, route_referral: dict | None = None, assemble_missing: list | None = None):
    """스크립트 LLM: 도구 목록으로 역할을 알아본다."""
    tools, msgs = _tools(req), req["messages"]
    system, user = msgs[0]["content"], msgs[1]["content"]
    if "interpret" in tools:
        ents = [a for a in ALIASES if a in user]
        return _call("interpret", {"entities": ents, "attribute": "requested information"})
    if "route" in tools:
        if route_referral:
            for ent, group in route_referral.items():
                if ent in user:
                    cites = re.findall(r"^\[(E\d+)\]", user.split("Group records found:\n", 1)[1], re.M)
                    return _call("route", {"action": "referral", "agents": [], "referral_to": group, "evidence": cites[:1]})
        members = re.findall(r"^- (\S+) \|", user.split("Members:\n", 1)[1].split("\n\n", 1)[0], re.M)
        records = user.split("Group records found:\n", 1)[1]
        agents = [a for a in members if f"] {a} · " in records]
        return _call("route", {"action": "select", "agents": agents or members[:1]})
    if "answer" in tools:                                                  # 담당자 답은 코드가 그대로 전달: 증거 줄을 additions로
        records = user.split("Group records:\n", 1)[1].split("\n\n", 1)[0] if "Group records:\n" in user else ""
        missing = assemble_missing.pop(0) if assemble_missing else []
        adds, cur = [], None
        for l in records.splitlines():                                     # 증거는 에피소드 전체(여러 줄)
            if m := re.match(r"\[(E\d+)\]", l):
                cur = m.group(1)
            if l.strip() and cur:
                adds.append({"entity": "record", "attribute": "text", "value": l, "status": "", "ref": f"[{cur}]"})
        return _call("answer", {"additions": adds, "conflicts": [], "proposals": [], "missing": missing})
    if "dispatch" in tools:
        q = user.split("Question: ", 1)[1].split("\nPurpose:", 1)[0]
        g = next((GOLD[w] for w, surf in SURFACE.items() if surf in q), None)
        group = g["needs"][0]["group"] if g else re.findall(r"^- (\S+) \|", system, re.M)[0]
        return _call("dispatch", {"targets": [{"group": group, "question": q}], "entity": "subject", "attr": "info"})
    if "reply" in tools:                                                   # 오라클 응답자: 자기가 가진 조각 원문
        own = "\n".join(l for l in user.splitlines()                     # 남에게 받은 답은 제외
                         if re.match(r"\[H\d+\] \(day -?\d+ \w+\) (?!\[(Answer|Question|Handled|Reply))", l))
        held = [f["text"] for f in FRAGS.values() if f["text"] in own]
        return _call("reply", {"items": [{"entity": "record", "attribute": "text", "value": h, "status": "",
                                          "ref": "own records"} for h in held],
                               "missing": [] if held else ["unknown"]})
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


def run(tmp, condition, script=oracle, name="worldgen_mini", max_day=None, conditions=T.CONDITIONS, **extra):
    a = load_adapter(name)
    rt = AgentRuntime(conditions[condition], a.group_tools,
                      ContextBuilder(T.TOK.count, T.P.context.raw_window, T.P.context.summary), T.P.agent.max_steps,
                      T.P.agent.format_retries, T.P.agent.safety_steps, T.P.agent.responder_max_steps,
                      tuple(T.P.agent.responder_exclude_tools))
    access = T.ACCESS if conditions is T.CONDITIONS else T.load_access(T.ROOT / "configs" / "access.yaml", conditions)
    r = Runner(a, condition=condition, seed=7, run_dir=tmp, conditions=conditions, access=access,
               tools=ToolRegistry(access), env_tools=a.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt),
               params=T.P.kernel, llm=T.backend("SCRIPTED", script=script), tokens=T.TOK.count, max_day=max_day,
               **boundary_kwargs(), **extra)
    r.run()
    return r, T.wal(tmp)


def _requester_answers(events) -> dict[str, str]:
    """과제마다 요청자가 받은 답 원문 (경계 조건은 그룹 응답, Direct는 에이전트 응답)."""
    out: dict[str, str] = {}
    for e in events:
        p = e["payload"]
        if e["type"] == "message" and p["kind"] == "response" and p.get("serving") is None \
                and not str(p["from_agent"]).startswith("boundary:"):
            out[p["task_id"]] = out.get(p["task_id"], "") + render_response(p["response"])
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
    assert decisions and all(d["deliver"] == "forward" for d in decisions)
    inner = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["actor"].startswith("boundary:")]
    for d in decisions:
        sent = [m for m in inner if m["rid"].startswith(d["rid"] + ".") or m["rid"].startswith(d["rid"])]
        assert sent and all(m["request"]["question"] == d["question"] for m in sent), "요청 원문 그대로"
    got = [e["payload"]["response"]["answer"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
           and e["actor"].startswith("boundary:")]
    assert got and all(a.startswith("[Reply 1] ") for a in got if a)


def test_router_output_leak_stops_the_run_as_a_bug(tmp_path):
    """라우터가 만든 출력(선택 결과·referral 사유)에 검색 결과의 값이 들어가면 버그: 실행을 멈춘다."""
    from gbg.kernel.errors import FatalError

    def script(req):
        if "route" in _tools(req):
            records = req["messages"][1]["content"].split("Group records found:\n", 1)[1]
            amount = re.search(r"\d{1,3}(?:,\d{3})+", records)
            if amount:
                return _call("route", {"action": "referral", "agents": [], "referral_to": "FIN-TYO",
                                       "evidence": [amount.group(0)]})                    # 인용 칸에 값을 넣은 버그 흉내
        return oracle(req)
    with pytest.raises(FatalError, match="라우터 출력"):
        run(tmp_path, "routing", script=script)


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
    """재질의는 새 정보가 있을 때만: 증거에 그 항목의 이력 구간이 있으면 그 구간을 첨부해 현 역할 담당자에게.
    새 정보가 없는 빠진 항목(아무 기록에도 없는 것)은 재질의하지 않고 missing으로 남긴다."""
    prompts, seen = [], set()

    def script(req):
        tools = _tools(req)
        user = req["messages"][1]["content"]
        if "answer" in tools:
            prompts.append(user)
            if "KRW 1,850,000" in user and "W-002" not in seen:            # 증거(FR-C1)에 정산일 기록이 있는 항목
                seen.add("W-002")
                return oracle(req, assemble_missing=[["settlement day of the provisional approval"]])
            if "Check the current department" in user and "W-001" not in seen:   # 어떤 기록에도 없는 항목
                seen.add("W-001")
                return oracle(req, assemble_missing=[["favourite colour of the employee"]])
        if "ask_group" in tools and len(req["messages"]) == 2 and "[Task W-008]" in user:
            return _call("ask_group", {"group": "FIN-SEL", "question": SURFACE["W-002"]})   # 같은 엔티티를 다시 묻는다
        return oracle(req)
    _, ev = run(tmp_path, "ingress", script=script)
    ing = {e["payload"]["task_id"]: e["payload"] for e in ev if e["type"] == "boundary_decision"
           and e["payload"]["stage"] == "ingress" and e["payload"].get("action") == "select"}
    assert ing["W-002"]["requery"] and ing["W-002"]["requery_basis"]["with_excerpt"], "이력 구간을 첨부해 재질의"
    assert ing["W-001"]["requery"] == [], "새 정보가 없으면 재질의하지 않는다"
    follow = [e["payload"]["request"]["question"] for e in ev if e["type"] == "message"
              and e["payload"]["kind"] == "request" and e["actor"].startswith("boundary:")]
    assert any(q.startswith("Follow-up from your group's intake desk") and "settlement due day 8" in q for q in follow)
    assert any("Database versions:\n[D1]" in p for p in prompts), "버전 표시: DB 키·버전 번호"
    assert any("Earlier exchanges of this desk:\n[S1]" in p for p in prompts), "경계 상태: 같은 엔티티의 과거 문답"


def test_ingress_sel_definition_has_no_state_versions_or_requery():
    sel = T.CONDITIONS["ingress_sel"].ingress
    assert sel.deliver == "assemble" and not (sel.requery or sel.boundary_state or sel.version_marks)


def test_no_need_more_step_ambiguous_requests_go_to_members(tmp_path):
    """need_more 단계는 모든 조건에서 끈다: 엔티티가 없는 모호한 요청도 담당자에게 그대로 전달하고, 되묻기는 담당자가 한다."""
    def script(req):
        tools = _tools(req)
        if "ask_group" in tools and len(req["messages"]) == 2 and "[Task W-005]" in req["messages"][1]["content"]:
            return _call("ask_group", {"group": "FIN-SEL", "question": "Is that item still alive?"})   # 엔티티 없음
        return oracle(req)
    _, ev = run(tmp_path, "routing", script=script)
    assert not any(e["type"] == "boundary_decision" and e["payload"].get("action") == "need_more" for e in ev)
    w5 = next(e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["task_id"] == "W-005")
    assert w5["entities"] == [] and w5["action"] == "select" and w5["selected"], "담당자에게 그대로 전달"


def test_boundary_budget_exhaustion_sends_requester_to_final_answer(tmp_path):
    conds = T.load_conditions(T.ROOT / "configs" / "conditions.yaml")
    conds.defaults = conds.defaults.model_copy(update={"budget": conds.defaults.budget.model_copy(update={"calls": 3})})
    _, ev = run(tmp_path, "ingress", max_day=1, conditions=conds)
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    assert answers and all(a["budget"]["used"]["calls"] <= 3 for a in answers)
    assert any(e["payload"]["response"]["answer"] == "budget_exhausted" for e in ev
               if e["type"] == "message" and e["payload"]["kind"] == "response")


# ─────────────────────────── full_load (참조 행) ───────────────────────────
def _full_load_run(tmp_path):
    """요청자: 조직 전체 DB 조회(group 인자 없음) → 같은 질의로 기억 검색 두 번(두 번째는 캐시) → 제출."""
    sent = []

    def script(req):
        tools, msgs = _tools(req), req["messages"]
        sent.append((msgs[0]["content"], tools))
        if "submit" in tools and "search_memory" in tools:
            n = sum(1 for m in msgs if m["role"] == "tool")
            if n == 0:
                return _call("db.query", {"entity": "E-SEL-1000", "record_type": "employee_profile"})
            if n in (1, 2):
                return _call("search_memory", {"query": "CMT-00001 provisional approval settlement"})
        return oracle(req)
    r, ev = run(tmp_path, "full_load", script=script)
    return r, ev, sent


def test_full_load_is_one_agent_over_the_whole_organization(tmp_path):
    """정의: 권한 분할이 없는 단일 에이전트. 도구에 group 인자가 없고, 조회는 조직 전체에서 출처 그룹만 표시, 묻는
    도구·디렉터리 없음, 전 그룹 규정, 다른 조건과 같은 과제 예산."""
    r, ev, sent = _full_load_run(tmp_path)
    system, schemas = next((sm, t) for sm, t in sent if "submit" in t)
    assert "group" not in schemas["db.query"]["parameters"]["properties"]
    assert "group" not in schemas["entity.search"]["parameters"]["properties"]
    types = schemas["db.query"]["parameters"]["properties"]["record_type"]["enum"]
    assert set(r.adapter.group_tools("HR-SEL")[0].parameters["properties"]["record_type"]["enum"]) < set(types)
    assert not {"ask_agent", "ask_group", "ask", "load_group_history"} & set(schemas)
    assert "there is no one to ask" in system and "You cannot look these up" not in system
    assert "<<DIRECTORY>>\n(none)" in system
    assert all(f"[Rules of {g}]" in system for g in ("FIN-SEL", "HR-SEL", "HR-TYO", "FIN-TYO"))
    q = [e["payload"] for e in ev if e["type"] == "tool_result" and e["payload"]["tool"] == "db.query"]
    assert q and all(x["ok"] and x["result"]["status"] == "HIT" for x in q)
    assert all([h["group"] for h in x["result"]["results"]] == ["HR-SEL"] for x in q), "출처 그룹만 표시"
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    lim = T.CONDITIONS.defaults.budget
    assert answers and all(a["budget"]["limit"] == {"calls": lim.calls, "tokens": lim.tokens} for a in answers), \
        "다른 조건과 같은 과제 예산"


def test_full_load_search_memory_is_gateway_search_over_the_whole_organization(tmp_path):
    r, ev, _ = _full_load_run(tmp_path)
    res = [e["payload"] for e in ev if e["type"] == "tool_result" and e["payload"]["tool"] == "search_memory"]
    assert res and all(x["ok"] for x in res)
    first = res[0]["result"]["records"]
    assert FRAGS["FR-C1"]["text"] in first, "떠난 구성원(fin-sel.a2)의 이력도 검색된다"
    heads = [x for x in first.splitlines() if x.startswith("[E")]
    assert any(re.match(rf"\[E\d+\] FIN-SEL · {public_id('fin-sel.a2')} · day -?\d+", x) for x in heads), \
        "머리: 그룹 · 에이전트(공개 id) · day"
    assert "entities: " in first, "에피소드 머리에 엔티티 키"
    assert len({x.split(" · ")[0].split(" ")[1] for x in heads}) > 1, "여러 그룹에서"
    fl = [json.loads(x) for x in (tmp_path / "obs" / "full_load.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(not x["cached"] for x in fl) and any(x["cached"] for x in fl), "같은 과제 안 같은 질의는 캐시"
    acc = [json.loads(x) for x in (tmp_path / "obs" / "access.jsonl").read_text(encoding="utf-8").splitlines()]
    mem = [x for x in acc if x.get("tool") == "search_memory"]
    assert mem and all(x["allowed"] and x["scope"] == "all" for x in mem)
    retr = [json.loads(x) for x in (tmp_path / "obs" / "retrievals.jsonl").read_text(encoding="utf-8").splitlines()]
    org = [x for x in retr if x.get("org")]
    assert org and org[0]["tokens"] <= T.P.retrieval.evidence_cap, "게이트웨이와 같은 증거 상한 하나"


def test_full_load_miss_hint_does_not_point_to_groups(tmp_path):
    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "submit" in tools and "search_memory" in tools and not any(m["role"] == "tool" for m in msgs):
            return _call("db.query", {"entity": "없는 사람", "record_type": "employee_profile"})
        return oracle(req)
    _, ev = run(tmp_path, "full_load", script=script, max_day=1)
    q = [e["payload"]["result"] for e in ev if e["type"] == "tool_result" and e["payload"]["tool"] == "db.query"]
    assert q and all(x["status"] == "NOT_FOUND" and "group" not in x["hint"] and "area" not in x["hint"] for x in q)


def test_several_tool_calls_in_one_step_all_run(tmp_path):
    """요청자는 한 단계에서 여러 도구를 부를 수 있다 (모든 조건 동일). 단계 상한은 없다 (과제 예산이 상한)."""
    assert T.P.agent.max_steps is None

    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "submit" in tools and len(msgs) == 2 and "[Task W-001]" in msgs[1]["content"]:
            return T.mk([("ask_group", {"group": "HR-SEL", "question": "grade of 하린 과장?"}),
                         ("ask_group", {"group": "HR-TYO", "question": "grade of 하린 과장?"})])
        return oracle(req)
    _, ev = run(tmp_path, "routing", script=script, max_day=1)
    asked = [e["payload"]["to_group"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["payload"]["task_id"] == "W-001" and e["actor"] == "agent:fin-sel.a1"]
    assert asked == ["HR-SEL", "HR-TYO"]


def test_referral_without_recorded_agreement_goes_to_members(tmp_path):
    """referral은 합의 기록의 인용 id가 증거 블록에 있을 때만. 근거가 없으면 그룹 안 담당자에게 전달한다."""
    def script(req):
        if "route" in _tools(req):
            return _call("route", {"action": "referral", "agents": [], "referral_to": "FIN-TYO", "evidence": ["E99"]})
        return oracle(req)
    _, ev = run(tmp_path, "routing", script=script, max_day=1)
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"].get("stage") == "ingress"]
    assert dec and all(d["action"] == "select" and d["selected"] and d["referral_rejected"]["to"] == "FIN-TYO" for d in dec)


def test_responders_get_no_communication_tools(tmp_path):
    sent = []

    def script(req):
        sent.append((_tools(req), req["messages"][0]["content"]))
        return oracle(req)
    run(tmp_path, "routing", script=script, max_day=1)
    replies = [(t, sysm) for t, sysm in sent if "reply" in t]
    assert replies and all(not {"ask_agent", "ask_group", "ask"} & set(t) for t, _ in replies)
    assert all("<<DIRECTORY>>\n(none)\n<</DIRECTORY>>" in sysm for _, sysm in replies)


def test_task_prompt_has_today_and_answer_conventions(tmp_path, monkeypatch):
    """모든 조건에서 과제 프롬프트에 오늘 일차와 답 작성 규칙(answer_slots를 '|'로 이은 키)을 붙인다."""
    from gbg.benchmarks.worldgen import adapter as A
    monkeypatch.setitem(A.ANSWER_CONVENTIONS, "dept|grade", {"dept": "the department name as written in HR", "grade": "integer"})
    monkeypatch.setitem(A.ANSWER_CONVENTIONS, "_general", ["Return exactly the listed slots as JSON."])
    monkeypatch.delitem(A.ANSWER_CONVENTIONS, "available|n_deducted", raising=False)
    seen = []

    def script(req):
        seen.append(req["messages"][1]["content"])
        return oracle(req)
    run(tmp_path, "direct", script=script, max_day=1)
    w1 = next(u for u in seen if "[Task W-001]" in u.split("[Current task]\n")[-1])
    cur = w1.split("[Current task]\n")[-1]
    assert cur.startswith("Today is day 1.\n[Task W-001]")
    assert "Answer conventions:\n- Return exactly the listed slots as JSON.\n- dept: the department name as written in HR" in cur
    w2 = next(u for u in seen if "[Task W-002]" in u.split("[Current task]\n")[-1]).split("[Current task]\n")[-1]
    assert "Answer conventions" not in w2, "규칙이 없는 형식에는 붙이지 않는다"


def test_answer_conventions_file_covers_every_worldgen_answer_format():
    """answer_conventions.json: 형식·null 규칙만. 픽스처가 아니라 실제 4.4 답 형식 15종의 키를 모두 가진다."""
    from gbg.benchmarks.worldgen.adapter import ANSWER_CONVENTIONS
    keys = {k for k in ANSWER_CONVENTIONS if not k.startswith("_")}
    assert len(keys) == 15 and ANSWER_CONVENTIONS["_general"]
    for k in keys:
        assert set(k.split("|")) == set(ANSWER_CONVENTIONS[k]), k


def test_route_tool_has_no_free_text_reason_and_raw_output_stays_in_wal(tmp_path):
    from gbg.boundary.prompts import ROUTE_TOOL
    assert set(ROUTE_TOOL["parameters"]["properties"]) == {"action", "agents", "referral_to", "evidence", "items"}
    assert set(ROUTE_TOOL["parameters"]["properties"]["items"]["items"]["properties"]) == {"entity", "attribute", "scope", "target_group"}, "항목별 선택지만, 자유 문장 사유 없음"
    _, ev = run(tmp_path, "routing", max_day=1)
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision"]
    assert dec and all("reason" not in d for d in dec)
    raw = [e for e in ev if e["type"] == "llm_call" and e["actor"].startswith("boundary:")
           and any(c["name"] == "route" for c in e["payload"]["message"]["tool_calls"])]
    assert raw, "라우터 LLM의 원출력은 llm_call 사건으로 WAL에 남는다"


def test_responder_loop_is_capped_at_ten_steps_then_replies(tmp_path):
    """응답자 루프는 모든 조건에서 최대 10단계. 닿으면 reply 전용 호출 1회로 그때까지 확인한 것을 답한다."""
    assert T.P.agent.responder_max_steps == 10

    def script(req):
        tools = _tools(req)
        if "reply" in tools and len(tools) > 1:                            # 응답자는 도구만 되풀이한다
            return _call("entity.search", {"query": "x"})
        if "reply" in tools:
            assert req["tool_choice"] == {"type": "function", "function": {"name": "reply"}}, "답 전용 호출은 reply 강제"
        return oracle(req)
    _, ev = run(tmp_path, "direct", script=script, max_day=1)
    per = {}
    for e in ev:
        p = e["payload"]
        if e["type"] == "llm_call" and p.get("component") == "responder":
            per[(p["task_id"], p["serving"])] = per.get((p["task_id"], p["serving"]), 0) + 1
    assert per and max(per.values()) == 11, "10단계 + reply 전용 1회"
    resp = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
            and e["actor"].startswith("agent:") and e["payload"].get("serving") is None]
    assert resp and all(r["status"] != "error" for r in resp)
    answers = [e["payload"] for e in ev if e["type"] == "answer"]
    assert sum(a["budget"]["responder_step_cap"] for a in answers) == len(per), "responder_step_cap으로 센다"


def test_responder_has_no_entity_search_and_sees_its_records_scope(tmp_path):
    seen = []

    def script(req):
        tools = _tools(req)
        if "reply" in tools:
            seen.append((set(tools), req["messages"][0]["content"], req["messages"][1]["content"]))
        return oracle(req)
    run(tmp_path, "direct", script=script, max_day=1)
    assert seen and all("entity.search" not in t and "db.query" in t for t, _, _ in seen)
    assert all("[Your area's records]\nYour area's records contain only:" in sm and "without looking it up" in sm
               for _, sm, _ in seen), "응답자 자신의 system에 기록 범위 (종류만)"
    assert all("Your area's rules are in the system section above; do not search for them." in u for _, _, u in seen)


def test_gateway_conditions_can_ask_own_group_members_only(tmp_path):
    """그룹 안 질문은 모든 조건에서 허용 (worldgen 규격 message.send: 그룹 내부). 경계 조건의 요청자는 자기 그룹
    구성원 목록(그룹 표시만)을 받고 ask_agent로 묻는다. 다른 그룹 구성원에게는 거부된다."""
    seen = {}

    def script(req):
        tools, msgs = _tools(req), req["messages"]
        system, user = msgs[0]["content"], msgs[1]["content"]
        if "submit" in tools and len(msgs) == 2 and _task(user):
            assert "ask_agent" in tools and "ask_group" in tools
            block = system.split("Members of your group (", 1)[1]
            seen["group"] = block.split(")", 1)[0]
            own = re.findall(r"^- (\S+) \|", block.split("\n\n", 1)[0], re.M)
            seen["own"] = own
            other = public_id("hr-sel.a1" if seen["group"] != "HR-SEL" else "fin-sel.a1")
            return T.mk([("ask_agent", {"agent_id": own[0], "question": "What do your records say?"}),
                         ("ask_agent", {"agent_id": other, "question": "What do your records say?"})])
        if "submit" in tools:
            seen["results"] = [m["content"] for m in msgs if m["role"] == "tool"]
        return oracle(req)
    _, ev = run(tmp_path, "routing", script=script, max_day=1)
    assert seen["own"], "자기 그룹 구성원 목록"
    assert any('"ok": true' in r for r in seen["results"]) and any("not_a_member_of_your_group" in r for r in seen["results"])
    asks = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
            and e["payload"].get("to_agent") and not e["actor"].startswith("boundary:")]
    assert asks and all(a["to_group"] == a["request"]["from_group"] for a in asks if a["delivered"]), "경계를 넘는 직접 질의는 없다"


def test_every_llm_call_gets_own_rules_period_and_records_notes(tmp_path):
    """G6: 경계 모듈의 모든 LLM 호출(해석·선택·조립·재조립·Egress 정리)과 요청자·응답자 호출이 자기 그룹 규정 블록,
    'until day N' 규약, 기록과 DB 문장을 받는다 (모든 조건 같은 문장)."""
    from gbg.agents.prompts import PERIOD_NOTE, RECORDS_NOTE
    for cond in ("i_e", "direct", "routing"):
        seen: dict[str, list[str]] = {}

        def script(req):
            name = next((n for n in ("interpret", "route", "answer", "dispatch", "reply", "submit") if n in _tools(req)), "?")
            seen.setdefault(name, []).append(req["messages"][0]["content"])
            return oracle(req)
        run(tmp_path / cond, cond, script=script, max_day=1)
        want = {"i_e": {"interpret", "route", "answer", "dispatch", "reply", "submit"}, "direct": {"reply", "submit"},
                "routing": {"interpret", "route", "reply", "submit"}}[cond]
        assert want <= set(seen), (cond, set(seen))
        for name, systems in seen.items():
            assert all(re.search(r"\[Rules of [^\]]+\]", s) and PERIOD_NOTE in s and RECORDS_NOTE in s for s in systems), (cond, name)
    assert "group" not in RECORDS_NOTE.lower(), "Direct에 그룹 개념을 드러내지 않는다"


def test_gateway_version_rule_and_request_wording():
    from gbg.agents.prompts import COMMON, COMMON_FULL_LOAD
    from gbg.boundary import prompts as BP
    assert "Operational notes" not in BP.VERSION_RULE
    assert "Do not use task IDs" in COMMON and "Do not use task IDs" not in COMMON_FULL_LOAD
    assert "Do not add task IDs" in BP.DISPATCH_SYSTEM


def test_requery_only_for_items_of_this_group_and_second_assembly_keeps_the_draft(tmp_path):
    """재질의는 missing 항목이 이 그룹의 증거나 색인 엔티티에 걸릴 때만, 질문은 그 항목에 한정(원 요청은 맥락),
    2차 조립은 1차 답을 초안으로 받는다."""
    prompts, seen = [], set()

    def script(req):
        tools = _tools(req)
        user = req["messages"][1]["content"]
        if "answer" in tools:
            prompts.append(user)
            if "KRW 1,850,000" in user and "W-002" not in seen:
                seen.add("W-002")                                          # 이 그룹 항목 + 다른 그룹 소관 항목
                return oracle(req, assemble_missing=[["settlement day of the provisional approval",
                                                      "favourite colour of the employee"]])
        return oracle(req)
    _, ev = run(tmp_path, "ingress", script=script)
    w2 = next(e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["stage"] == "ingress"
              and e["payload"]["task_id"] == "W-002" and e["payload"].get("action") == "select")
    assert w2["requery_items"] == ["settlement day of the provisional approval"], "걸리지 않는 항목은 missing으로 둔다"
    follow = [e["payload"]["request"]["question"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
              and e["actor"].startswith("boundary:") and e["payload"]["task_id"] == "W-002"
              and e["payload"]["request"]["question"].startswith("Follow-up")]
    assert follow and all("For context, the original request was:" in q and "favourite colour" not in q for q in follow)
    assert any("Your first additions, conflicts and proposals for this request (draft):" in p and "missing: ['settlement day" in p for p in prompts)


# ─────────────────────────── 소관 밖 재라우팅 (out_of_scope) ───────────────────────────
def _route_script(plan):
    """plan: (그룹, 과제 표지 문자열) → route items. 나머지는 오라클."""
    def script(req):
        tools, system, user = _tools(req), req["messages"][0]["content"], req["messages"][1]["content"]
        if "route" in tools:
            group = re.search(r"This group: (\S+)", system).group(1)
            for (g, mark), items in plan.items():
                if g == group and mark in user:
                    out = oracle(req)
                    args = json.loads(out["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]) \
                        if "choices" in out else None
                    members = re.findall(r"^- (\S+) \|", user.split("Members:\n", 1)[1].split("\n\n", 1)[0], re.M)
                    return _call("route", {"action": "select", "agents": (args or {}).get("agents") or members[:1],
                                           "items": items})
        return oracle(req)
    return script


def test_out_of_scope_items_are_checked_by_code_and_returned_to_the_requester(tmp_path):
    here = {"entity": "하린 과장", "attribute": "grade", "scope": "here"}
    plan = {("HR-SEL", "하린 과장"): [
        here,
        {"entity": "하린 과장", "attribute": "laptop asset tag", "scope": "elsewhere", "target_group": "HR-TYO"},   # 받아들임
        {"entity": "하린 과장", "attribute": "profile grade", "scope": "elsewhere", "target_group": "HR-TYO"},      # 기록 종류와 겹침
        {"entity": "하린 과장", "attribute": "budget", "scope": "elsewhere", "target_group": "FIN-SEL"}]}          # 요청이 지나온 그룹
    _, ev = run(tmp_path, "ingress", script=_route_script(plan), max_day=1)
    d = next(e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["task_id"] == "W-001"
             and e["payload"]["stage"] == "ingress")
    assert [x["attribute"] for x in d["redirects"]] == ["laptop asset tag"]
    assert {x["attribute"]: x["why"] for x in d["redirects_rejected"]} == {"profile grade": "own_records_or_rules",
                                                                        "budget": "invalid_target"}
    resp = next(e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
                and e["payload"]["task_id"] == "W-001" and e["actor"] == "boundary:HR-SEL")
    assert resp["redirects"] == [{"entity": "하린 과장", "attribute": "laptop asset tag", "referral_to": "HR-TYO",
                                  "reason": "out_of_scope"}]
    assert "하린 과장 laptop asset tag" in resp["missing"] and resp["status"] == "partial" and d["selected"], "나머지는 담당자가 답한다"


def test_all_items_out_of_scope_returns_referral_without_asking_members(tmp_path):
    plan = {("HR-SEL", "하린 과장"): [{"entity": "하린 과장", "attribute": "laptop asset tag", "scope": "elsewhere",
                                    "target_group": "HR-TYO"}]}
    _, ev = run(tmp_path, "routing", script=_route_script(plan), max_day=1)
    d = next(e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["task_id"] == "W-001")
    assert d["action"] == "out_of_scope" and "selected" not in d
    resp = next(e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
                and e["payload"]["task_id"] == "W-001" and e["actor"] == "boundary:HR-SEL")
    assert resp["status"] == "referral" and resp["referral_to"] == "HR-TYO" and resp["items"] == []
    assert "HR-TYO" in resp["answer"] and "hr-" not in resp["answer"].lower().replace("hr-tyo", ""), "안내에는 그룹 이름만"
    assert not any(e["type"] == "message" and e["payload"]["kind"] == "request" and e["actor"] == "boundary:HR-SEL"
                   and e["payload"]["task_id"] == "W-001" for e in ev), "담당자를 부르지 않는다"


def test_ie_egress_resends_out_of_scope_items_once_and_logs_them(tmp_path):
    item = {"entity": "하린 과장", "attribute": "laptop asset tag", "scope": "elsewhere"}
    plan = {("HR-SEL", "하린 과장"): [{**item, "target_group": "HR-TYO"}],
            ("HR-TYO", "하린 과장"): [{**item, "target_group": "FIN-TYO"}]}                # 재발신 요청은 다시 돌려보낼 수 없다
    r, ev = run(tmp_path, "i_e", script=_route_script(plan), max_day=1)
    ing = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"]["task_id"] == "W-001"
           and e["payload"]["stage"] == "ingress"]
    tyo = next(d for d in ing if d["group"] == "HR-TYO")
    assert tyo["redirects"] == [] and tyo["redirects_rejected"][0]["why"] == "rerouted_request"
    asks = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
            and e["actor"] == "boundary:FIN-SEL" and e["payload"]["task_id"] == "W-001"]
    assert [a["to_group"] for a in asks] == ["HR-SEL", "HR-TYO"] and asks[1]["request"]["hop"] == 2
    assert "only this part is needed: 하린 과장 laptop asset tag" in asks[1]["request"]["question"]
    log = r.kernel.stores.egress_log.lookup("FIN-SEL", "하린 과장", "laptop asset tag")
    assert any(x.status == "referral" and x.referral_to == "HR-TYO" and x.reason == "out_of_scope" for x in log)


# ─────────────────────────── 출처·시점 (코드가 ref를 따라가 채움) ───────────────────────────
def test_reftable_resolves_lookup_history_and_rule_ids():
    from gbg.contracts.schemas import HistoryEntry
    from gbg.llm.agent_loop import RefTable
    h = [HistoryEntry.model_construct(seq=120, day=7, role="assistant", text="x", digest="x", tokens=1)]
    t = RefTable(h, ["hold_policy"])
    t.add("D1", {"id": "D1", "ok": True, "result": {"status": "HIT", "entity": "CAD", "registered_day": 5, "record": {}}})
    t.add("D2", {"id": "D2", "ok": True, "result": {"status": "HIT", "records": [
        {"id": "CMT-1", "registered_day": 3, "record": {}}, {"id": "CMT-2", "registered_day": 4, "record": {}}]}})
    t.add("D3", {"id": "D3", "ok": True, "result": {"status": "HIT", "entity": "INV-1", "record": {"cost": 1}}})
    r = lambda ref, ent="x": t.resolve({"ref": ref, "entity": ent})
    assert r("D1") == ("db", "5") and r("D2", "CMT-2") == ("db", "4") and r("D2") == ("db", "unknown")
    assert r("D3") == ("db", "fixed"), "등록일 없는 고정 자료(catalog)"
    assert r("H120") == ("history", "7") and r("hold_policy") == ("rule", "fixed")
    assert r("my notes") == ("unknown", "unknown") and r("D9") == ("unknown", "unknown")


def test_gateway_items_get_source_and_day_from_cited_evidence(tmp_path):
    _, ev = run(tmp_path, "ingress", max_day=2)
    items = [x for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
             and e["actor"].startswith("boundary:") for x in e["payload"]["response"]["items"]]
    cited_e = [x for x in items if re.match(r"\[E\d+\]", x["ref"])]
    assert cited_e and all(x["source"] == "history" and re.fullmatch(r"-?\d+", x["day"]) for x in cited_e)


# ─────────────────────────── 조립 단조성 · 공통 지식 ───────────────────────────
def test_assembly_passes_member_items_unchanged_and_adds_cited_notes(tmp_path):
    """담당자 items는 그대로 전달하고, 게이트웨이는 additions·conflicts·proposals만 더한다. 제안은 근거 인용 필수,
    없는 인용은 형식 오류로 되돌린다 (format_retries 1회)."""
    tries = {"KRW 1,850,000": 0, "KRW 2,300,000": 0}
    good = {"additions": [], "missing": [],
            "conflicts": [{"item": "available budget", "note": "reply and record differ", "refs": ["[R1]", "[E1]"]}],
            "proposals": [{"item": "available budget", "value": "999", "refs": ["[E1]"], "rationale": "newer record"}]}
    bad = {"KRW 1,850,000": [],  "KRW 2,300,000": ["[E99]"]}                  # 근거 없음 / 없는 인용

    def script(req):
        tools, user = _tools(req), req["messages"][1]["content"]
        mark = next((m for m in tries if "answer" in tools and m in user.split("Replies:", 1)[0]), None)
        if mark:
            tries[mark] += 1
            if tries[mark] == 1:
                return _call("answer", {**good, "proposals": [{**good["proposals"][0], "refs": bad[mark]}]})
            return _call("answer", good)
        return oracle(req)
    _, ev = run(tmp_path, "ingress", script=script)
    assert tries == {"KRW 1,850,000": 2, "KRW 2,300,000": 2}, "근거 없는 제안·없는 인용은 되돌린다"
    inner = [e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
             and e["payload"]["task_id"] == "W-002" and e["actor"].startswith("agent:") and e["payload"].get("serving")]
    resp = next(e["payload"]["response"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
                and e["payload"]["task_id"] == "W-002" and e["actor"].startswith("boundary:"))
    member = [x for r in inner for x in r["items"]]
    passed = [x for x in resp["items"] if x["ref"].startswith("Reply ")]
    assert member and [(x["entity"], x["value"], x["day"]) for x in passed] == \
        [(x["entity"], x["value"], x["day"]) for x in member], "담당자 답은 그대로"
    assert resp["proposals"] == good["proposals"] and resp["conflicts"][0]["refs"] == ["[R1]", "[E1]"]


def test_common_knowledge_is_in_every_role_and_gateway_uses_the_same_sentences(tmp_path):
    from gbg.agents.prompts import COMM_TOOLS, KNOWLEDGE
    from gbg.boundary import prompts as BP
    seen = []

    def script(req):
        seen.append(req["messages"][0]["content"])
        return oracle(req)
    run(tmp_path, "i_e", script=script, max_day=1)
    assert seen and all(k in s for s in seen for k in KNOWLEDGE), "모든 역할·모든 호출의 규정 블록"
    body = lambda k: k[2:]
    assert body(KNOWLEDGE[0]) in BP.ASSEMBLE_SYSTEM and body(KNOWLEDGE[2]) in BP.ASSEMBLE_SYSTEM
    assert body(KNOWLEDGE[1]) in BP.VERSION_RULE and body(KNOWLEDGE[3]) in BP.DISPATCH_SYSTEM
    assert all("group" not in k.lower() for k in KNOWLEDGE), "Direct에 그룹 개념을 드러내지 않는다"
    assert "returns each member's reply as is." in COMM_TOOLS["ask_group_forward"][1]
    assert "proposed values" in COMM_TOOLS["ask_group"][1] and "proposed values" in COMM_TOOLS["ask"][1]
    r = LLMAgent("x", AgentRuntime(T.CONDITIONS["routing"], None, None, None, 1)).comm()
    i = LLMAgent("x", AgentRuntime(T.CONDITIONS["ingress"], None, None, None, 1)).comm()
    assert r[0] == "ask_group_forward" and i[0] == "ask_group"


def test_oldest_tool_results_are_elided_when_the_prompt_would_overflow():
    """입력이 컨텍스트 한도를 넘으면 이번 루프의 가장 오래된 도구 결과부터 생략 (모든 조건 동일). 마지막 결과는 남긴다."""
    from types import SimpleNamespace
    agent = LLMAgent("x", AgentRuntime(T.CONDITIONS["direct"], None, ContextBuilder(len, 1, 1), None, 1))
    ctx = SimpleNamespace(kernel=SimpleNamespace(llm=SimpleNamespace(params=SimpleNamespace(context_length=2600, max_tokens=100))))
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    for i in range(3):
        msgs += [{"role": "assistant", "content": ""}, {"role": "tool", "tool_call_id": str(i), "content": "x" * 1000}]
    agent._fit(ctx, msgs, 2, 0)
    tools = [m["content"] for m in msgs if m["role"] == "tool"]
    assert tools[0] == LLMAgent.ELIDED and tools[-1] == "x" * 1000
    assert len(json.dumps(msgs, ensure_ascii=False, sort_keys=True)) <= int((2600 - 100) * 0.9)
