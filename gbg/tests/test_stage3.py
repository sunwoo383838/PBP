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
from gbg.tests.support import load_adapter

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
    return {"number": 0, "string": "", "boolean": False, "array": []}[schema["type"]]


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
            calls.append(("db.query", {"entity": "E-SEL-1000", "record_type": rtype}))
        if "shard.read" in tools:
            calls.append(("shard.read", {}))
        if finish == "submit" and "ask_agent" in tools and "[Task L-" not in msgs[1]["content"]:
            to = _first_directory_agent(msgs[0]["content"])
            calls.append(("ask_agent", {"agent_id": to, "question": "Could you check this case for me?"}))
        if calls:
            return mk(calls)
    if finish == "submit":
        props = tools["submit"]["parameters"]["properties"]
        return mk([("submit", {k: _default(v) for k, v in props.items()})])
    return mk([("reply", {"answer": "unknown", "missing": []})])


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


def llm_runner(tmp, llm, *, condition="direct", name="worldgen_mini", max_day=1):
    a = load_adapter(name)
    rt = AgentRuntime(CONDITIONS[condition], a.role_tools, ContextBuilder(TOK.count, P.context.raw_window, P.context.summary),
                      P.agent.max_steps, P.agent.format_retries)
    return Runner(a, condition=condition, seed=7, run_dir=tmp, conditions=CONDITIONS, access=ACCESS,
                  tools=ToolRegistry(ACCESS), env_tools=a.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt),
                  params=P.kernel, llm=llm, tokens=TOK.count, max_day=max_day)


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


def test_request_is_deterministic_greedy_and_thinking_off():
    b = backend("SCRIPTED", script=auto_reply)
    req = b.build_request([{"role": "user", "content": "x"}], [])
    assert req["model"] == "Qwen/Qwen3-32B" and req["temperature"] == 0
    assert req["reasoning_effort"] == "none" and "chat_template_kwargs" not in req
    assert "tools" not in req and "tool_choice" not in req
    req = b.build_request([{"role": "user", "content": "x"}], [{"type": "function", "function": {"name": "f"}}])
    assert req["tool_choice"] == "auto"


def test_backoff_on_429_and_5xx(tmp_path):
    waits = []
    async def sleep(s):
        waits.append(s)
    server = FakeDeepInfra(fail_first=[429, 503])
    b = backend("LIVE", ResponseCache(tmp_path / "c.sqlite"), server.transport(), params=P.llm, sleep=sleep)
    res = asyncio.run(b.complete([{"role": "user", "content": "x"}], []))
    assert res.attempts == 3 and server.calls == 3 and waits == [1.0, 2.0]


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
    assert "- fin-sel.a1 |" in systems["direct"] and "- FIN-SEL |" in systems["routing"]
    assert "hr-sel.a1 |" not in systems["direct"], "디렉터리에 자기 자신은 없다"
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
                return mk([("submit", {"grade": "two"})])
        return auto_reply(req)
    return script


def test_format_error_retries_once_then_records(tmp_path):
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=_flaky("L-001", 99)))
    runner.run()
    ev = wal(tmp_path)
    bad = [e for e in ev if e["type"] == "answer" and e["payload"]["task_id"] == "L-001"]
    assert len(bad) == 1 and bad[0]["payload"]["error"] == "format_error" and bad[0]["payload"]["answer"] is None
    calls = [e for e in ev if e["type"] == "llm_call" and e["payload"]["task_id"] == "L-001"]
    assert len(calls) == 1 + P.agent.format_retries, "원래 시도 + 재시도 1회"
    others = [e for e in ev if e["type"] == "answer" and e["payload"]["task_id"] != "L-001"]
    assert others and all(e["payload"].get("error") is None for e in others), "런은 계속된다"


def test_format_error_recovers_within_retry(tmp_path):
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=_flaky("L-001", 1)))
    runner.run()
    ans = next(e for e in wal(tmp_path) if e["type"] == "answer" and e["payload"]["task_id"] == "L-001")
    assert ans["payload"].get("error") is None and ans["payload"]["answer"] == {"grade": 0}


def test_step_limit(tmp_path):
    loop_forever = lambda req: mk([("rulebook.read", {"search": "x"})]) if "submit" in str(req["tools"]) else auto_reply(req)
    llm_runner(tmp_path, backend("SCRIPTED", script=loop_forever)).run()
    ans = [e for e in wal(tmp_path) if e["type"] == "answer"]
    assert ans and all(e["payload"]["error"] == "step_limit" for e in ans)
    per_task = {}
    for e in wal(tmp_path):
        if e["type"] == "llm_call" and e["payload"]["task_id"].startswith(("L-", "W-")) and e["actor"] == f"agent:{e['payload']['agent']}":
            per_task.setdefault((e["payload"]["task_id"], e["payload"]["agent"]), 0)
            per_task[(e["payload"]["task_id"], e["payload"]["agent"])] += 1
    assert max(per_task.values()) == P.agent.max_steps


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
    warm = len(load_adapter("worldgen_mini").initial_state("HR-SEL").histories["hr-sel.a2"])
    new = runner.stores.history.entries("hr-sel.a2")[warm:]
    assert new and all(e.tokens == TOK.count(e.text) for e in new)


def test_answer_digest_keeps_categories_drops_numbers(tmp_path):
    def script(req):
        tools = {t["function"]["name"] for t in req["tools"]}
        if "submit" in tools and "[Task W-" in req["messages"][1]["content"] and len(req["messages"]) > 2:
            props = next(t for t in req["tools"] if t["function"]["name"] == "submit")["function"]["parameters"]["properties"]
            if "decision" in props:
                return mk([("submit", {"decision": "approve", "available": 2508100})])
        return auto_reply(req)
    runner = llm_runner(tmp_path, backend("SCRIPTED", script=script))
    runner.run()
    e = next(e for e in runner.stores.history.entries("hr-sel.a3") if e.text.startswith("[Submitted W-002]"))
    assert "decision=approve" in e.digest and "2508100" not in e.digest and not looks_like_amount(e.digest)


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
