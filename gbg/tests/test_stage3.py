"""Stage 3 수용 기준 (LLM 백엔드와 ContextBuilder).

1. 픽스처 1일치를 LIVE로 돌린 뒤 REPLAY로 다시 돌리면 API 호출 0회, WAL 동일.
2. 같은 이력이면 ContextBuilder 출력이 바이트 동일.
3. 조건별 시스템 프롬프트 diff가 도구·디렉터리 블록 외에 0줄.
4. 형식 오류 주입 시 재시도 1회 후 format_error가 기록되고 런이 계속된다.

LIVE는 DeepInfra 응답 형식을 흉내 내는 가짜 HTTP 서버로 검증한다. 실제 API 검증은
DEEPINFRA_API_KEY와 GBG_LIVE=1이 있을 때만 돈다 (test_real_deepinfra_live_then_replay).
"""
import asyncio
import json
import os
from gbg.contracts.card import public_id
from pathlib import Path

import httpx
import pytest

from gbg.agents.prompts import strip_condition_blocks
from gbg.contracts.access import load_access
from gbg.contracts.conditions import load_conditions
from gbg.contracts.params import TokenizerParams, load_params
from gbg.contracts.schemas import HistoryEntry
from gbg.kernel.runner import Runner
from gbg.kernel.scheduler import AgentContext, Span
from gbg.kernel.tools import ToolRegistry
from gbg.llm.agent_loop import AgentRuntime, LLMAgent
from gbg.llm.backend import LLMBackend, LLMError, ReplayMiss, normalize
from gbg.llm.cache import ResponseCache
from gbg.llm.context_builder import ContextBuilder
from gbg.llm.tokenizer import TokenizerError, load_tokenizer, tokenizer_path
from gbg.stores.cards import looks_like_amount
from gbg.tests.support import boundary_kwargs, load_adapter

ROOT = Path(__file__).resolve().parents[2]
P = load_params(ROOT / "configs" / "params.yaml")
CONDITIONS = load_conditions(ROOT / "configs" / "conditions.yaml")
ACCESS = load_access(ROOT / "configs" / "access.yaml", CONDITIONS)
TOK = load_tokenizer(P.tokenizer)
FAST = P.llm.model_copy(update={"retry": P.llm.retry.model_copy(update={"base_delay_s": 0.0})})


# ─────────────────────────── 가짜 모델 ───────────────────────────
def _default(schema):
    if "anyOf" in schema:
        return None
    if "enum" in schema:
        return schema["enum"][0]
    return {"integer": 0, "number": 0, "string": "", "boolean": False, "array": []}[schema["type"]]


def _first_directory_agent(system):
    lines = system.split("<<DIRECTORY>>\n", 1)[1].splitlines()
    return lines[0].split(" | ")[0][2:] if lines and lines[0].startswith("- ") else None


def auto_reply(req):
    """첫 단계: 환경 도구(교차 작업이면 ask_agent도), 다음 단계: submit / reply."""
    tools = {t["function"]["name"]: t["function"] for t in req.get("tools", [])}
    msgs = req["messages"]
    finish = "submit" if "submit" in tools else "reply"
    if len(msgs) == 2:
        calls = []
        if "db.query" in tools:
            rtype = tools["db.query"]["parameters"]["properties"]["record_type"]["enum"][0]
            calls.append(("db.query", {"entity": "영업1팀", "record_type": rtype}))
        if "shard.read" in tools:
            calls.append(("shard.read", {}))
        if finish == "submit" and "ask_agent" in tools:
            to = _first_directory_agent(msgs[0]["content"])
            calls.append(("ask_agent", {"agent_id": to, "question": "Could you check this case for me?"}))
        if calls:
            return mk(calls)
    if finish == "submit":
        props = tools["submit"]["parameters"]["properties"]
        return mk([("submit", {k: _default(v) for k, v in props.items()})])
    return mk([("reply", {"answer": "unknown", "items": [], "missing": ["unknown"]})])


def mk(calls, content=None):
    return {"content": content, "finish_reason": "tool_calls" if calls else "stop",
            "tool_calls": [{"name": n, "arguments": json.dumps(a, ensure_ascii=False)} for n, a in calls],
            "usage": {"prompt_tokens": 100, "completion_tokens": 10}}


def openai_json(resp, n):
    return {"id": f"cmpl-{n}", "choices": [{"index": 0, "finish_reason": resp["finish_reason"], "message": {
        "role": "assistant", "content": resp["content"],
        "tool_calls": [{"id": f"srv-{n}-{i}", "type": "function", "function": c} for i, c in enumerate(resp["tool_calls"])]}}],
        "usage": resp["usage"]}


class FakeDeepInfra:
    """httpx 전송 계층. 앞의 fail_first개 요청은 주어진 상태 코드로 실패시킨다."""
    def __init__(self, fail_first=(), reply=auto_reply):
        self.calls, self.bodies, self.fail = 0, [], list(fail_first)
        self.reply = reply

    def __call__(self, request: httpx.Request):
        self.calls += 1
        body = json.loads(request.content)
        self.bodies.append(body)
        if self.fail:
            return httpx.Response(self.fail.pop(0), json={"error": "busy"})
        return httpx.Response(200, json=openai_json(self.reply(body), self.calls))

    def transport(self):
        return httpx.MockTransport(self)


def no_api(request):
    raise AssertionError("REPLAY 모드에서 API를 불렀다")


async def _no_sleep(_):
    return None


def backend(mode, cache=None, transport=None, script=None, model="qwen3-32b", params=FAST, sleep=_no_sleep):
    return LLMBackend(params, mode=mode, model=model, cache=cache, script=script, transport=transport,
                      api_key="test", sleep=sleep)


def llm_runner(tmp, llm, *, condition="direct", name="worldgen_mini", max_day=1, conditions=CONDITIONS):
    a = load_adapter(name)
    rt = AgentRuntime(CONDITIONS[condition], a.group_tools, ContextBuilder(TOK.count, P.context.raw_window, P.context.summary),
                      P.agent.max_steps, P.agent.format_retries)
    return Runner(a, condition=condition, seed=7, run_dir=tmp, conditions=conditions, access=ACCESS,
                  tools=ToolRegistry(ACCESS), env_tools=a.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt),
                  params=P.kernel, llm=llm, tokens=TOK.count, max_day=max_day, **boundary_kwargs())


def wal(d):
    return [json.loads(x) for x in (Path(d) / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]


def obs(d, name):
    p = Path(d) / "obs" / f"{name}.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


# ─────────────────────────── 1. LIVE → REPLAY ───────────────────────────
def test_live_then_replay_makes_zero_calls(tmp_path):
    cache = ResponseCache(tmp_path / "cache.sqlite")
    server = FakeDeepInfra()
    live = backend("LIVE", cache, server.transport())
    h_live = llm_runner(tmp_path / "live", live).run()
    assert server.calls > 0 and live.api_calls == server.calls

    replay = backend("REPLAY", cache, httpx.MockTransport(no_api))
    h_replay = llm_runner(tmp_path / "replay", replay).run()
    assert replay.api_calls == 0 and h_replay == h_live

    ev = wal(tmp_path / "live")
    answers = [e for e in ev if e["type"] == "answer"]
    assert answers and all(e["payload"].get("error") is None for e in answers)
    assert any(e["type"] == "message" for e in ev), "교차 작업이 ask_agent로 다른 그룹에 물었다"
    assert {e["day"] for e in ev} == {1}


@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_replay_is_stable_across_runs(tmp_path, name):
    cache = ResponseCache(tmp_path / "cache.sqlite")
    h1 = llm_runner(tmp_path / "a", backend("LIVE", cache, FakeDeepInfra().transport()), name=name).run()
    h2 = llm_runner(tmp_path / "b", backend("REPLAY", cache, httpx.MockTransport(no_api)), name=name).run()
    h3 = llm_runner(tmp_path / "c", backend("REPLAY", cache, httpx.MockTransport(no_api)), name=name).run()
    assert h1 == h2 == h3


def test_replay_miss_stops_the_run(tmp_path):
    cache = ResponseCache(tmp_path / "cache.sqlite")
    with pytest.raises(ReplayMiss):
        llm_runner(tmp_path / "r", backend("REPLAY", cache, httpx.MockTransport(no_api))).run()


def test_request_sampling_follows_model_card_and_thinking_off():
    """temperature 0(사용자 결정) + Qwen3.5 non-thinking 권장 샘플링 값. 재현은 캐시·WAL로 한다."""
    b = backend("SCRIPTED", script=auto_reply)
    req = b.build_request([{"role": "user", "content": "x"}], [])
    assert req["model"] == "Qwen/Qwen3-32B" and req["temperature"] == 0
    assert (req["top_p"], req["top_k"], req["min_p"], req["presence_penalty"], req["repetition_penalty"]) == (0.8, 20, 0, 1.5, 1.0)
    assert req["reasoning_effort"] == "none" and "chat_template_kwargs" not in req
    assert "tools" not in req and "tool_choice" not in req
    req = b.build_request([{"role": "user", "content": "x"}], [{"type": "function", "function": {"name": "f"}}])
    assert req["tool_choice"] == "auto"


def test_backoff_on_429_and_5xx(tmp_path):
    waits = []
    async def sleep(s):
        waits.append(s)
    server = FakeDeepInfra(fail_first=[429, 503, 429, 429, 503])
    b = backend("LIVE", ResponseCache(tmp_path / "c.sqlite"), server.transport(), params=P.llm, sleep=sleep)
    res = asyncio.run(b.complete([{"role": "user", "content": "x"}], []))
    assert res.attempts == 6 and server.calls == 6
    assert waits == [3.0, 1.0, 6.0, 12.0, 2.0], "429는 3초부터 두 배씩, 5xx는 따로 1초부터"


def test_rate_limit_backoff_outlasts_5xx_limit_and_caps(tmp_path):
    """429는 5xx 시도 한도(6회)를 쓰지 않고 계속 늘어난 간격으로 재시도한다 (상한 600초)."""
    waits = []
    async def sleep(s):
        waits.append(s)
    server = FakeDeepInfra(fail_first=[429] * 10)
    b = backend("LIVE", ResponseCache(tmp_path / "c.sqlite"), server.transport(), params=P.llm, sleep=sleep)
    res = asyncio.run(b.complete([{"role": "user", "content": "x"}], []))
    assert res.attempts == 11 and waits == [3.0, 6.0, 12.0, 24.0, 48.0, 96.0, 192.0, 384.0, 600.0, 600.0]


def test_backoff_gives_up_and_4xx_is_fatal(tmp_path):
    cache = ResponseCache(tmp_path / "c.sqlite")
    b = backend("LIVE", cache, FakeDeepInfra(fail_first=[500] * 10).transport())
    with pytest.raises(LLMError, match="6회"):
        asyncio.run(b.complete([{"role": "user", "content": "x"}], []))
    b = backend("LIVE", cache, FakeDeepInfra(fail_first=[400]).transport())
    with pytest.raises(LLMError, match="거부"):
        asyncio.run(b.complete([{"role": "user", "content": "y"}], []))
    assert len(cache) == 0


def test_identical_inflight_requests_call_api_once(tmp_path):
    server = FakeDeepInfra()
    b = backend("LIVE", ResponseCache(tmp_path / "c.sqlite"), server.transport())
    async def both():
        m = [{"role": "user", "content": "같은 요청"}]
        return await asyncio.gather(b.complete(m, []), b.complete(m, []))
    r1, r2 = asyncio.run(both())
    assert server.calls == 1 and r1.message == r2.message and r1.key == r2.key


def test_think_blocks_are_stripped():
    raw = {"choices": [{"finish_reason": "stop", "message": {"content": "<think>음</think>\n답", "tool_calls": None}}]}
    n = normalize(raw)
    assert n["content"] == "답" and n["thinking_stripped"]
    raw = {"choices": [{"finish_reason": "stop", "message": {"content": "391", "reasoning_content": "Okay, let me think"}}]}
    assert normalize(raw)["reasoning_leaked"]


# ─────────────────────────── 2. ContextBuilder ───────────────────────────
def _history(n, text="처리 기록 원문입니다. " * 20):
    return tuple(HistoryEntry(seq=i, day=i // 5, role=["user", "assistant", "tool"][i % 3], text=f"#{i} {text}",
                              tokens=TOK.count(f"#{i} {text}"), entities=[], digest=f"{i // 5}일차 항목 {i} 처리")
                 for i in range(1, n + 1))


def test_context_builder_is_byte_identical():
    h = _history(300)
    b1 = ContextBuilder(TOK.count, P.context.raw_window, P.context.summary)
    b2 = ContextBuilder(TOK.count, P.context.raw_window, P.context.summary)
    c1, c2 = b1.build("시스템", h, "과제", 7), b2.build("시스템", tuple(h), "과제", 7)
    assert json.dumps(c1.messages, ensure_ascii=False) == json.dumps(c2.messages, ensure_ascii=False)
    assert c1.composition == c2.composition


def test_context_window_and_summary_budgets():
    h = _history(300)
    c = ContextBuilder(TOK.count, P.context.raw_window, P.context.summary).build("시스템", h, "과제", 0).composition
    raw, summ = c["raw"], c["summary"]
    assert raw["last_seq"] == 300 and raw["tokens"] <= P.context.raw_window
    assert raw["tokens"] + h[raw["first_seq"] - 2].tokens > P.context.raw_window, "창은 넘기 직전까지 채운다"
    assert summ["last_seq"] == raw["first_seq"] - 1, "요약은 창 바로 앞에서 시작한다"
    assert 0 < summ["tokens"] <= P.context.summary
    assert c["dropped"] == summ["first_seq"] - 1 and c["history_len"] == 300


def test_context_short_history_has_no_summary():
    c = ContextBuilder(TOK.count, P.context.raw_window, P.context.summary).build("s", _history(3), "t", 0)
    assert c.composition["raw"]["n"] == 3 and c.composition["summary"]["n"] == 0
    assert "[Earlier records" not in c.messages[1]["content"]


# ─────────────────────────── 3. 조건별 시스템 프롬프트 ───────────────────────────
def test_system_prompt_differs_only_in_condition_blocks(tmp_path):
    a = load_adapter("worldgen_mini")
    systems = {}
    for cond in ("direct", "routing", "ingress", "i_e"):
        runner = llm_runner(tmp_path / cond, backend("SCRIPTED", script=auto_reply), condition=cond)
        k = runner.kernel
        for g in a.groups():
            for m in g.members:
                k.add_member(m.agent_id, g.id, m.role)
        ctx = AgentContext(k, Span([], (1, "T")), "hr-sel.a1", "HR-SEL", "records", 1, 1, "T", 0, [], ())
        systems[cond], _ = k.agents["hr-sel.a1"].system(ctx)
    stripped = {c: strip_condition_blocks(s) for c, s in systems.items()}
    assert len(set(stripped.values())) == 1, "도구·디렉터리 블록 밖은 조건 간 한 줄도 다르면 안 된다"
    assert systems["direct"] != systems["routing"] != systems["i_e"]
    assert f"- {public_id('fin-sel.a1')} | Region: SEL |" in systems["direct"] and "- FIN-SEL |" in systems["routing"]
    assert public_id("hr-sel.a1") not in systems["direct"], "디렉터리에 자기 자신은 없다"
    for g in a.groups():                                                 # Direct에는 그룹 개념이 전혀 없다
        assert g.id not in systems["direct"] and g.id.lower() not in systems["direct"]
        assert all(m.agent_id not in systems["direct"] for m in g.members)
    assert "- HR-SEL |" not in systems["routing"], "그룹 디렉터리에 자기 그룹은 없다"


# ─────────────────────────── 4. 형식 오류 ───────────────────────────
def _flaky(bad_task, times):
    """bad_task 과제에서 처음 times번은 형식을 어긴다 (글로만 답하거나 슬롯 오류)."""
    seen = {"n": 0}
    def script(req):
        content = req["messages"][1]["content"]
        if f"[Task {bad_task}]" in content and "submit" in {t["function"]["name"] for t in req["tools"]}:
            if seen["n"] < times:
                seen["n"] += 1
                if seen["n"] % 2:
                    return mk([], content="The grade is 2.")
                return mk([("submit", {"dept": "영업1팀", "grade": "two"})])
        return auto_reply(req)
    return script


def test_format_error_retries_once_then_records(tmp_path):
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=_flaky("W-001", 99)))
    runner.run()
    ev = wal(tmp_path)
    bad = [e for e in ev if e["type"] == "answer" and e["payload"]["task_id"] == "W-001"]
    assert len(bad) == 1 and bad[0]["payload"]["error"] == "format_error" and bad[0]["payload"]["answer"] is None
    calls = [e for e in ev if e["type"] == "llm_call" and e["payload"]["task_id"] == "W-001"
             and e["payload"]["component"] == "requester"]
    assert len(calls) == 1 + P.agent.format_retries, "원래 시도 + 재시도 1회"
    others = [e for e in ev if e["type"] == "answer" and e["payload"]["task_id"] != "W-001"]
    assert others and all(e["payload"].get("error") is None for e in others), "런은 계속된다"


def test_format_error_recovers_within_retry(tmp_path):
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=_flaky("W-001", 1)))
    runner.run()
    ans = next(e for e in wal(tmp_path) if e["type"] == "answer" and e["payload"]["task_id"] == "W-001")
    assert ans["payload"].get("error") is None and ans["payload"]["answer"] == {"dept": "", "grade": 0}


def test_no_step_cap_task_budget_is_the_limit(tmp_path):
    """단계 상한은 없다: 도구만 되풀이하는 요청자는 과제 예산(호출 수)에 닿고, 예약된 최종 호출로 제출한다."""
    forced = []

    def loop_forever(req):
        if isinstance(req.get("tool_choice"), dict):
            forced.append(req["tool_choice"]["function"]["name"])
        return (mk([("entity.search", {"query": "x"})]) if len(req["tools"]) > 1 and "submit" in str(req["tools"])
                else auto_reply(req))
    conds = load_conditions(ROOT / "configs" / "conditions.yaml")
    conds.defaults = conds.defaults.model_copy(update={"budget": conds.defaults.budget.model_copy(update={"calls": 20})})
    llm_runner(tmp_path, backend("SCRIPTED", script=loop_forever), conditions=conds).run()
    ans = [e["payload"] for e in wal(tmp_path) if e["type"] == "answer"]
    lim = conds.defaults.budget.calls
    assert ans and all(a.get("error") is None and a["budget"]["budget_exhausted"] and a["budget"]["final_call_used"]
                       and a["budget"]["exhausted_by"] == "calls" and a["budget"]["used"]["calls"] <= lim for a in ans)
    assert forced and set(forced) == {"submit"}, "최종 호출은 제출 도구를 강제한다"


def test_safety_steps_end_with_a_submit_only_call(tmp_path):
    """예산 상한이 없는 조건(full_load)을 위한 안전 한도: 닿으면 실패가 아니라 제출 전용 호출 1회로 끝낸다."""
    a = load_adapter("worldgen_mini")
    rt = AgentRuntime(CONDITIONS["direct"], a.group_tools, ContextBuilder(TOK.count, P.context.raw_window, P.context.summary),
                      None, P.agent.format_retries, safety_steps=3)
    loop_forever = lambda req: (mk([("entity.search", {"query": "x"})]) if len(req["tools"]) > 1 and "submit" in str(req["tools"])
                                else auto_reply(req))
    conds = load_conditions(ROOT / "configs" / "conditions.yaml")                  # 예산 상한이 없는 조건에서만 안전 한도
    conds.defaults = conds.defaults.model_copy(update={"budget": conds.defaults.budget.model_copy(update={"calls": None, "tokens": None})})
    Runner(a, condition="direct", seed=7, run_dir=tmp_path, conditions=conds, access=ACCESS, tools=ToolRegistry(ACCESS),
           env_tools=a.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt), params=P.kernel,
           llm=backend("SCRIPTED", script=loop_forever), tokens=TOK.count, max_day=1).run()
    ans = [e["payload"] for e in wal(tmp_path) if e["type"] == "answer"]
    assert ans and all(x.get("error") is None and x["budget"]["used"]["calls"] == 4 for x in ans), "3단계 + 최종 1회"


# ─────────────────────────── 기록 ───────────────────────────
def test_every_llm_call_logs_context_window(tmp_path):
    llm_runner(tmp_path, backend("SCRIPTED", script=auto_reply)).run()
    calls = [e for e in wal(tmp_path) if e["type"] == "llm_call"]
    windows, stats = obs(tmp_path, "context_windows"), obs(tmp_path, "llm")
    assert len(windows) == len(calls) == len(stats)
    assert {w["seq"] for w in windows} == {c["seq"] for c in calls}
    assert all(w["directory_tokens"] > 0 and w["system_tokens"] > w["directory_tokens"] for w in windows)
    assert all(c["payload"]["key"] and c["payload"]["message"] for c in calls)


def test_history_tokens_use_pinned_tokenizer(tmp_path):
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=auto_reply))
    runner.run()
    h = runner.stores.history.entries("hr-sel.a3")
    harness = ("[Task W-", "[Tool call]", "[Tool result] db.query", "[Tool result] entity.search", "[Submitted",
               "[Question", "[Answer")
    mine = [e for e in h if e.text.startswith(harness)]
    assert mine and all(e.tokens == TOK.count(e.text) for e in mine), "하네스가 만든 항목은 고정 토크나이저로 센다"
    replayed = next(e for e in h if e.text == "[Tool result] Recorded: E-SEL-1003 grade 2.")
    assert replayed.tokens == int(len(replayed.text) * 1.1), "worldgen 이력 줄은 산출물의 토큰 수를 그대로 쓴다"


def test_answer_digest_keeps_categories_drops_numbers(tmp_path):
    def script(req):
        tools = {t["function"]["name"] for t in req["tools"]}
        if "submit" in tools and "[Task W-005]" in req["messages"][1]["content"] and len(req["messages"]) > 2:
            return mk([("submit", {"status": "pending", "amount": 612300})])
        return auto_reply(req)
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=script), max_day=3)
    runner.run()
    e = next(e for e in runner.stores.history.entries("hr-sel.a3") if e.text.startswith("[Submitted W-005]"))
    assert "status=pending" in e.digest and "612300" not in e.digest and not looks_like_amount(e.digest)


# ─────────────────────────── 토크나이저 ───────────────────────────
def test_tokenizer_is_pinned_and_verified(tmp_path, monkeypatch):
    assert TOK.count("가승인 검토 시작") == TOK.count("가승인 검토 시작") > 0
    assert TOK.params.revision == "9216db5781bf21249d130ec9da846c4624c16137"
    bad = TokenizerParams(repo=P.tokenizer.repo, revision=P.tokenizer.revision, sha256="0" * 64)
    with pytest.raises(TokenizerError):
        tokenizer_path(bad)


# ─────────────────────────── 실제 DeepInfra (선택) ───────────────────────────
@pytest.mark.skipif(os.environ.get("GBG_LIVE") != "1", reason="GBG_LIVE=1일 때만 실제 API를 부른다 (키: 환경 변수 또는 gbg/llm/secrets.py)")
def test_real_deepinfra_live_then_replay(tmp_path):
    cache = ResponseCache(tmp_path / "cache.sqlite")
    live = LLMBackend(P.llm, mode="LIVE", model="qwen3-32b", cache=cache)
    h1 = llm_runner(tmp_path / "live", live).run()
    assert live.api_calls > 0
    replay = LLMBackend(P.llm, mode="REPLAY", model="qwen3-32b", cache=cache)
    assert llm_runner(tmp_path / "replay", replay).run() == h1 and replay.api_calls == 0
    flagged = [r for (r,) in cache.db.execute("SELECT response FROM responses")
               if "thinking_stripped" in json.loads(r) or "reasoning_leaked" in json.loads(r)]
    assert not flagged, "thinking이 꺼지지 않았다 (reasoning_content 또는 <think> 블록)"


def test_service_tier_is_sent_but_not_part_of_the_cache_key(tmp_path):
    """priority는 처리 순서만 바꾼다: 요청에는 싣고, 캐시 키에는 넣지 않아 기존 응답을 그대로 재사용한다."""
    fake = FakeDeepInfra()
    cache = ResponseCache(tmp_path / "c.sqlite")
    default = LLMBackend(FAST, mode="LIVE", model="qwen3-32b", cache=cache, transport=fake.transport(), api_key="t",
                         sleep=_no_sleep)
    prio = LLMBackend(FAST.model_copy(update={"service_tier": "priority"}), mode="LIVE", model="qwen3-32b", cache=cache,
                      transport=fake.transport(), api_key="t", sleep=_no_sleep)
    msgs = [{"role": "user", "content": "hi"}]
    a = asyncio.run(prio.complete(msgs, []))
    assert fake.bodies[-1]["service_tier"] == "priority"
    b = asyncio.run(default.complete(msgs, []))
    assert b.cached and a.key == b.key and fake.calls == 1


def test_seed_per_call_is_derived_from_request_and_recorded(tmp_path):
    seen = []

    def script(req):
        seen.append(req.get("seed"))
        return auto_reply(req)
    b = LLMBackend(P.llm, mode="SCRIPTED", model="qwen3-32b", script=script, api_key="t")
    m = [{"role": "user", "content": "x"}]
    r1, r2 = asyncio.run(b.complete(m, [])), asyncio.run(b.complete(m, []))
    r3 = asyncio.run(b.complete([{"role": "user", "content": "y"}], []))
    assert r1.seed is not None and r1.seed == r2.seed == seen[0] and r3.seed != r1.seed


def test_cache_store_retries_on_lock_and_serialises_threads(tmp_path, monkeypatch):
    """캐시 잠금: 다른 프로세스가 쓰기 잠금을 잡고 있어도 기다렸다가 성공, 여러 스레드가 같은 연결을 써도 안전."""
    import sqlite3, threading, time as _t
    from gbg.llm import sqlite_store
    from gbg.llm.cache import ResponseCache
    c = ResponseCache(tmp_path / "c.sqlite")
    monkeypatch.setattr(sqlite_store.SqliteStore, "MAX_WAIT_S", 20.0)
    other = sqlite3.connect(tmp_path / "c.sqlite", isolation_level=None, timeout=0, check_same_thread=False)
    other.execute("BEGIN IMMEDIATE")                                       # 쓰기 잠금을 잡는다
    c.db.db.execute("PRAGMA busy_timeout=10")                             # 대기 대신 재시도 경로를 타게
    threading.Timer(0.3, lambda: other.execute("COMMIT")).start()
    req = {"model": "m", "messages": []}
    assert c.put("k", req, {"ok": 1}) == {"ok": 1}
    errs = []

    def worker(i):
        try:
            for j in range(20):
                c.put(f"k{i}-{j}", req, {"i": i})
                c.get(f"k{i}-{j}")
        except Exception as e:
            errs.append(e)
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert not errs and len(c) == 81
