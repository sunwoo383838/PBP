"""Stage 1 수용 기준 (커널, LLM 없음).

1. 같은 픽스처·조건·시드로 두 번 실행 → WAL 해시 동일.
2. 동시 실행 순서를 일부러 섞어도(테스트용 지연 주입) WAL 동일.
3. 3일차 중간에 강제 종료 후 재개한 런과 연속 런의 WAL 동일.
4. 허용되지 않은 자원 접근은 거부되고 obs/access.jsonl에 기록.
5. 홉 상한 초과가 error로 끝나고 무한 대기 없음.
"""
import ast
import asyncio
import json
import random
from pathlib import Path

import pytest

from gbg.agents.scripted import ScriptedAgent, fixed_answer
from gbg.contracts.access import load_access
from gbg.contracts.conditions import ConfigError, load_conditions
from gbg.contracts.envelope import Response
from gbg.kernel.rng import NamedRNG
from gbg.kernel.runner import KernelParams, RunConfigError, Runner
from gbg.kernel.tools import Resource, Tool, ToolRegistry
from gbg.tests.support import boundary_kwargs, load_adapter

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = load_conditions(ROOT / "configs" / "conditions.yaml")
ACCESS = load_access(ROOT / "configs" / "access.yaml", CONDITIONS)


class Crash(BaseException):
    """강제 종료 흉내. Exception이 아니므로 커널이 삼키지 않는다."""


# ─────────────────────────── 테스트 도구와 에이전트 ───────────────────────────
CALLS = []


def make_tools():
    reg = ToolRegistry(ACCESS)
    reg.register(Tool(name="db.read", description="그룹 DB 읽기", resources=(Resource("db", "r", target="group"),),
                      fn=lambda call: CALLS.append(("db.read", call.agent, call.args.get("group"))) or {"group": call.args.get("group", call.group)}))
    reg.register(Tool(name="history.peek", description="그룹 이력 엿보기", resources=(Resource("group_history", "r"),),
                      fn=lambda call: CALLS.append(("history.peek", call.agent)) or "leak"))
    return reg


def peer_of(groups):
    """다른 그룹의 첫 구성원에게 묻는다 (그룹 이름 정렬 순으로 다음 그룹)."""
    order = sorted(groups)
    return lambda group: groups[order[(order.index(group) + 1) % len(order)]]


class JitterAgent(ScriptedAgent):
    """작업마다 도구 호출 + 교차 작업이면 peer에게 질문. 지연은 테스트 전용 난수로 섞는다."""
    def __init__(self, agent_id, group, peer, jitter):
        super().__init__(agent_id, peer=lambda task: peer(group))
        self.group, self.jitter = group, jitter

    async def _sleep(self):
        if self.jitter:
            await asyncio.sleep(self.jitter.random() * 0.003)

    async def work(self, ctx, task):
        await self._sleep()
        await ctx.call_tool("db.read")
        await self._sleep()
        await ctx.call_tool("history.peek")
        await ctx.call_tool("db.read", group="OTHER-GROUP")
        await self._sleep()
        return await super().work(ctx, task)

    async def respond(self, ctx, request):
        await self._sleep()
        return Response(rid=request.rid, status="ok", answer=str(len(ctx.history)), values=[], missing=[],
                        referral_to=None, need=[], as_of=ctx.day)


def factory(adapter, jitter_seed=None):
    first = {g.id: sorted(m.agent_id for m in g.members)[0] for g in adapter.groups()}
    peer = peer_of(first)
    jit = random.Random(jitter_seed) if jitter_seed is not None else None
    return lambda agent_id, group, role: JitterAgent(agent_id, group, peer, jit)


def make_runner(run_dir, scenario="worldgen_mini", *, seed=7, condition="direct", jitter_seed=None, fault=None,
                agent_factory=None):
    adapter = load_adapter(scenario)
    return Runner(adapter, condition=condition, seed=seed, run_dir=run_dir, conditions=CONDITIONS, access=ACCESS,
                  tools=make_tools(), agent_factory=agent_factory or factory(adapter, jitter_seed),
                  params=KernelParams(), fault=fault, **boundary_kwargs())


def wal_events(run_dir):
    return [json.loads(x) for x in (Path(run_dir) / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]


def tree_bytes(run_dir):
    run_dir = Path(run_dir)
    return {p.relative_to(run_dir).as_posix(): p.read_bytes() for p in sorted(run_dir.rglob("*")) if p.is_file()}


@pytest.fixture(scope="module")
def baseline(tmp_path_factory):
    d = tmp_path_factory.mktemp("baseline")
    h = make_runner(d).run()
    return d, h


# ─────────────────────────── 1. 결정론 ───────────────────────────
def test_same_seed_same_wal(baseline, tmp_path):
    d, h = baseline
    assert make_runner(tmp_path).run() == h
    assert tree_bytes(tmp_path) == tree_bytes(d), "그룹·obs 파일까지 동일해야 한다"
    types = {e["type"] for e in wal_events(d)}
    assert {"task_delivered", "tool_call", "tool_result", "message", "answer", "round_commit",
            "agent_leave", "agent_join", "world_update"} <= types


def test_wal_seq_is_dense_and_rounds_ordered(baseline):
    d, _ = baseline
    ev = wal_events(d)
    assert [e["seq"] for e in ev] == list(range(1, len(ev) + 1))
    assert [(e["day"], e["round"]) for e in ev] == sorted((e["day"], e["round"]) for e in ev)
    commits = [e for e in ev if e["type"] == "round_commit"]
    assert len(commits) == 5 * 5                                              # 5일 × (라운드 0, 작업 1~3, 하루 끝 4)
    assert ev[-1]["type"] == "round_commit"


def test_world_updates_are_in_wal(baseline):
    d, _ = baseline
    adapter = load_adapter("worldgen_mini")
    world = [e for e in adapter.events() if e.kind not in ("cross", "agent_join", "agent_leave", "spawn", "despawn")]
    logged = [e for e in wal_events(d) if e["type"] == "world_update"]
    assert [e["payload"]["eid"] for e in logged] == [e.eid for e in world], "세계 사건은 seq 순서대로 전부 WAL에"
    assert all(e["payload"]["kind"] == w.kind and e["payload"]["data"] == w.payload for e, w in zip(logged, world))
    assert all(e["day"] == w.day and e["round"] == w.round for e, w in zip(logged, world))
    joins = [e["payload"]["agent"] for e in wal_events(d) if e["type"] == "agent_join"]
    leaves = [e["payload"]["agent"] for e in wal_events(d) if e["type"] == "agent_leave"]
    assert joins == ["fin-tyo.w00002", "fin-sel.n0001"] and leaves == ["fin-tyo.w00002", "fin-sel.a2"]


def test_every_task_answered_once(baseline):
    d, _ = baseline
    adapter = load_adapter("worldgen_mini")
    tasks = {e.task_id for e in adapter.events() if e.kind == "cross"}          # 로컬 작업은 재생만 (에이전트 수행 없음)
    answers = [e["payload"]["task_id"] for e in wal_events(d) if e["type"] == "answer"]
    assert sorted(answers) == sorted(tasks)


# ─────────────────────────── 2. 실행 순서 섞기 ───────────────────────────
@pytest.mark.parametrize("jitter_seed", [1, 2, 3])
def test_timing_jitter_does_not_change_wal(baseline, tmp_path, jitter_seed):
    _, h = baseline
    assert make_runner(tmp_path, jitter_seed=jitter_seed).run() == h


# ─────────────────────────── 3. 강제 종료 후 재개 ───────────────────────────
def crash_in_agent(agent_id, day):
    class Bomb(JitterAgent):
        async def work(self, ctx, task):
            if ctx.agent_id == agent_id and ctx.day == day:
                raise Crash
            return await super().work(ctx, task)
    return Bomb


def crash_at(stage, day, after=0):
    count = {"n": 0}
    def fault(point, info):
        if point == stage and info["day"] == day:
            count["n"] += 1
            if count["n"] > after:
                raise Crash
    return fault


@pytest.mark.parametrize("how", ["agent", "wal_event", "side_file", "before_marker"])
def test_resume_after_crash_mid_day3(baseline, tmp_path, how):
    d, h = baseline
    adapter = load_adapter("worldgen_mini")
    if how == "agent":
        runner = make_runner(tmp_path, agent_factory=_bomb_factory(adapter, "hr-sel.a3", 3))
    else:
        runner = make_runner(tmp_path, fault=crash_at(how, 3, after=2))
    with pytest.raises(Crash):
        runner.run()
    committed = [e for e in wal_events(tmp_path) if e["type"] == "round_commit"]
    assert committed and committed[-1]["day"] <= 3

    assert make_runner(tmp_path).run() == h
    assert tree_bytes(tmp_path) == tree_bytes(d), "재개 후 그룹·obs 파일도 연속 런과 같아야 한다"


def _bomb_factory(adapter, agent_id, day):
    first = {g.id: sorted(m.agent_id for m in g.members)[0] for g in adapter.groups()}
    peer = peer_of(first)
    Bomb = crash_in_agent(agent_id, day)
    return lambda aid, group, role: Bomb(aid, group, peer, None)


def test_resume_refuses_different_config(tmp_path):
    with pytest.raises(Crash):
        make_runner(tmp_path, fault=crash_at("wal_event", 2)).run()
    with pytest.raises(RunConfigError):
        make_runner(tmp_path, seed=8).run()
    with pytest.raises(RunConfigError):
        make_runner(tmp_path, condition="routing").run()


def test_unknown_condition_rejected(tmp_path):
    with pytest.raises(ConfigError):
        make_runner(tmp_path, condition="gateway")


# ─────────────────────────── 4. 접근 중재 ───────────────────────────
def test_denied_access_is_refused_and_logged(baseline):
    d, _ = baseline
    access = [json.loads(x) for x in (d / "obs" / "access.jsonl").read_text(encoding="utf-8").splitlines()]
    denied = [a for a in access if not a["allowed"]]
    assert denied and all(a["subject"].startswith("agent:") for a in denied)
    assert {(a["tool"], a["resource"], a["scope"]) for a in denied} == {
        ("history.peek", "group_history", "own"), ("db.read", "db", "other")}
    assert all(("db.read", "db", "own") == (a["tool"], a["resource"], a["scope"]) for a in access if a["allowed"])
    results = [e for e in wal_events(d) if e["type"] == "tool_result"]
    assert all(not r["payload"]["ok"] and r["payload"]["error"] == "access_denied"
               for r in results if r["payload"]["tool"] == "history.peek")
    seqs = {e["seq"] for e in wal_events(d)}
    assert all(a["seq"] in seqs for a in access), "접근 기록은 WAL 사건을 가리킨다"


def test_denied_tool_is_not_executed(tmp_path):
    CALLS.clear()
    make_runner(tmp_path).run()
    assert not any(c[0] == "history.peek" for c in CALLS)
    assert not any(c[0] == "db.read" and c[2] == "OTHER-GROUP" for c in CALLS)
    assert any(c[0] == "db.read" for c in CALLS)


# ─────────────────────────── 5. 홉 상한 ───────────────────────────
class Forwarder(ScriptedAgent):
    """받은 질문을 다음 에이전트에게 계속 넘긴다 (순환)."""
    def __init__(self, agent_id, nxt):
        super().__init__(agent_id)
        self.nxt = nxt

    async def work(self, ctx, task):
        r = await ctx.ask(self.nxt, task.text)
        return {"status": r.status, **fixed_answer(task.output_schema)}

    async def respond(self, ctx, request):
        return await ctx.ask(self.nxt, request.question)


def test_hop_limit_ends_in_error(tmp_path):
    adapter = load_adapter("silo_mini")
    agents = sorted(m.agent_id for g in adapter.groups() for m in g.members)
    nxt = {a: agents[(i + 1) % len(agents)] for i, a in enumerate(agents)}
    runner = make_runner(tmp_path, "silo_mini", agent_factory=lambda aid, g, role: Forwarder(aid, nxt[aid]))
    asyncio.run(asyncio.wait_for(asyncio.to_thread(runner.run), timeout=20))
    ev = wal_events(tmp_path)
    reqs = [e["payload"]["request"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"]
    assert max(r["hop"] for r in reqs) == KernelParams().hop_limit + 1        # 상한 다음 홉은 요청만 남고 거부
    refused = [e for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
               and e["payload"]["response"]["status"] == "error"]
    assert refused and all(e["payload"]["response"]["answer"] == "hop_limit" for e in refused)
    answers = [e for e in ev if e["type"] == "answer"]
    assert len(answers) == 16 and all(a["payload"]["answer"]["status"] == "error" for a in answers)


# ─────────────────────────── 실행 의미론 ───────────────────────────
def test_tasks_run_in_seq_order_and_see_earlier_tasks(tmp_path):
    """과제는 seq 순서로 하나씩 돈다. 과제 안에서는 세계가 멈추고, 다음 과제는 앞 과제의 반영분을 본다."""
    make_runner(tmp_path, "silo_mini").run()
    ev = wal_events(tmp_path)
    delivered = [e["payload"]["task_id"] for e in ev if e["type"] == "task_delivered"]
    adapter = load_adapter("silo_mini")
    assert delivered == [e.task_id for e in adapter.events() if e.kind != "world"], "도착 seq 순서 그대로"
    spans = {}                                                                  # 과제마다 WAL 사건이 연속 구간
    for i, e in enumerate(ev):
        if "task_id" in e["payload"]:
            spans.setdefault(e["payload"]["task_id"], []).append(i)
    assert all(v == list(range(v[0], v[-1] + 1)) for v in spans.values()), "과제 사이에 다른 과제 사건이 끼지 않는다"
    answers = [int(e["payload"]["response"]["answer"]) for e in ev
               if e["type"] == "message" and e["payload"]["kind"] == "response"]
    assert answers[0] == 1, "첫 응답자는 워밍업 이력(안내 한 줄)만 본다"
    assert max(answers) > 1, "뒤 과제의 응답자는 앞 과제에서 쌓인 이력을 본다"


def test_named_rng_streams():
    r = NamedRNG(7)
    a = [r.stream("x", 1).random() for _ in range(3)]
    assert a[0] == a[1] == a[2], "같은 이름은 매번 처음부터 같은 흐름"
    s1, s2 = r.stream("x", 1), r.stream("x", 2)
    assert [s1.random() for _ in range(3)] != [s2.random() for _ in range(3)]
    assert NamedRNG(7).stream("x").random() != NamedRNG(8).stream("x").random()


def test_no_global_random_or_wall_clock():
    banned_calls = {("time", "time"), ("time", "time_ns"), ("datetime", "now"), ("datetime", "today"),
                    ("datetime", "utcnow"), ("date", "today")}
    for path in (ROOT / "gbg").rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and path.name != "rng.py":
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                assert "random" not in names, f"{path}: random은 kernel/rng.py의 NamedRNG로만"
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                assert (node.value.id, node.attr) not in banned_calls, f"{path}: 벽시계 {node.value.id}.{node.attr}"
