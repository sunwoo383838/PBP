"""Stage 2 수용 기준 (시나리오 로더와 저장소, worldgen 4.2 형식).

1. 픽스처를 로드하고 private/ 접근 시도가 예외를 낸다.
2. db.query가 등록 시점을 반영한다 (등록 전 버전은 보이지 않고, 현재값은 등록된 최대 버전).
3. 스크립트 에이전트로 5일 실행 후, 모든 투영(card 레지스트리 포함)을 WAL만으로 재생성한 결과가 실행 중 투영과 동일.
4. 에이전트 이탈 후에도 이력이 보존되고, 후임의 이력은 인수인계 줄부터 시작.
5. card 대상이 떠난 직후 라운드부터 디렉터리에 없고, 후임이 같은 역할 card로 나타난다. 중복 담당은 디렉터리에 없다.
6. card_mode: dynamic에서 같은 색인이면 동적 요약이 바이트 동일하고, static에서는 요약이 붙지 않는다.
+ card 누출 검사: 금액처럼 보이는 표현(쉼표 없는 숫자, 만/억 단위, 근사 표현 포함)은 전부 차단, 차단은 obs/cards.jsonl에 기록.
+ 4.2 사건: 이력 줄(tx), catalog, 하루 끝 색인, swarm 워커 생성·소멸.
"""
import asyncio
import json
from pathlib import Path

import pytest

from gbg.agents.scripted import ScriptedAgent
from gbg.benchmarks.common import PrivateAccessError
from gbg.benchmarks.silo.adapter import SiloAdapter
from gbg.benchmarks.worldgen.adapter import AnswerSchemaError, WorldgenAdapter
from gbg.contracts.access import load_access
from gbg.contracts.conditions import ConditionSet, load_conditions
from gbg.contracts.events import Event
from gbg.contracts.params import KernelParams
from gbg.kernel.runner import Runner
from gbg.kernel.tools import ToolCall, ToolRegistry
from gbg.stores import Stores
from gbg.stores.cards import CardLeakChecker, looks_like_amount
from gbg.tests.support import FIXTURES, load_adapter

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = load_conditions(ROOT / "configs" / "conditions.yaml")
ACCESS = load_access(ROOT / "configs" / "access.yaml", CONDITIONS)
DYNAMIC = ConditionSet({**CONDITIONS, "direct": CONDITIONS["direct"].model_copy(update={"card_mode": "dynamic"})},
                       CONDITIONS.defaults)


class EnvAgent(ScriptedAgent):
    """과제마다 환경 도구를 한 번 쓰고, 다른 그룹의 card 대상 한 명에게 묻는다."""
    def __init__(self, agent_id, group, peer, env_call):
        super().__init__(agent_id, peer=lambda task: peer[group])
        self.env_call = env_call

    async def work(self, ctx, task):
        name, args = self.env_call(task)
        await ctx.call_tool(name, **args)
        return await super().work(ctx, task)


def env_call_for(name):
    if name == "silo_mini":
        return lambda task: ("shard.read", {})
    return lambda task: ("entity.search", {"query": "E-"})


def run(tmp, name="worldgen_mini", conditions=CONDITIONS):
    a = load_adapter(name)
    first = {g.id: (sorted(g.card_targets.values()) or sorted(m.agent_id for m in g.members))[0] for g in a.groups()}
    order = sorted(first)
    peer = {g: first[order[(order.index(g) + 1) % len(order)]] for g in order}
    runner = Runner(a, condition="direct", seed=7, run_dir=tmp, conditions=conditions, access=ACCESS,
                    tools=ToolRegistry(ACCESS), env_tools=a.make_tools,
                    agent_factory=lambda aid, g, role: EnvAgent(aid, g, peer, env_call_for(name)))
    runner.run()
    return runner


def wal(tmp):
    return [Event.model_validate_json(x) for x in (Path(tmp) / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]


def replay(name, events, conditions=CONDITIONS):
    s = Stores.from_adapter(load_adapter(name), card_mode=conditions["direct"].card_mode,
                            rounds_per_day=KernelParams().rounds_per_day)
    for ev in events:
        s.apply(ev)
    return s


def upto(events, day, rnd):
    return [e for e in events if (e.day, e.round) <= (day, rnd)]


@pytest.fixture(scope="module")
def wg_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("wg")
    return d, run(d)


# ─────────────────────────── 1. 로더와 private 거부 ───────────────────────────
@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_load_fixture(name):
    a = load_adapter(name)
    assert a.groups() and list(a.events())
    for g in a.groups():
        assert a.initial_state(g.id).group == g.id


def test_private_access_is_refused():
    w = FIXTURES / "worldgen_mini"
    for bad in (w / "private", w):
        with pytest.raises(PrivateAccessError):
            WorldgenAdapter().load(bad)
    a = load_adapter("worldgen_mini")
    for rel in ("../private/gold.jsonl", str((w / "private" / "gold.jsonl").resolve()), "../manifest.json"):
        with pytest.raises(PrivateAccessError):
            a.read(rel)
    s = FIXTURES / "silo_mini"
    with pytest.raises(PrivateAccessError):
        SiloAdapter().load(s / "private")
    with pytest.raises(PrivateAccessError):
        load_adapter("silo_mini").read_public("../private/gold.jsonl")


def test_answer_types_are_enforced(tmp_path):
    import shutil
    h = tmp_path / "harness"
    shutil.copytree(FIXTURES / "worldgen_mini" / "harness", h)
    shutil.copy(FIXTURES / "worldgen_mini" / "manifest.json", tmp_path / "manifest.json")
    rows = [json.loads(x) for x in (h / "work.jsonl").read_text(encoding="utf-8").splitlines()]
    rows[0]["answer_types"] = dict(reversed(list(rows[0]["answer_types"].items())))   # 슬롯 순서가 answer_slots와 다름
    (h / "work.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    with pytest.raises(AnswerSchemaError):
        WorldgenAdapter().load(h)
    cross = {e.task_id: e for e in load_adapter("worldgen_mini").events() if e.kind == "cross"}
    slots = cross["W-001"].output_schema.slots
    assert [(s.name, s.type, s.format) for s in slots] == [("dept", "id", "department"), ("grade", "int", None)]
    status = cross["W-005"].output_schema.slots
    assert status[0].type == "enum" and "pending" in status[0].options and status[1].nullable


def _mutated(tmp_path, rel, fn):
    import shutil
    root = tmp_path / "sc"
    shutil.copytree(FIXTURES / "worldgen_mini", root, ignore=shutil.ignore_patterns("private"))
    p = root / rel
    if p.suffix == ".jsonl":
        rows = fn([json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()])
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    else:
        p.write_text(json.dumps(fn(json.loads(p.read_text(encoding="utf-8"))), ensure_ascii=False), encoding="utf-8")
    return root / "harness"


def _drop(key):
    def f(rows):
        rows[0].pop(key)
        return rows
    return f


@pytest.mark.parametrize("rel, fn", [
    ("manifest.json", lambda m: {**m, "generator": "worldgen_v4.3"}),                          # generator
    ("harness/work.jsonl", _drop("answer_types")),                                             # 답 형식
    ("harness/work.jsonl", lambda rows: [{**rows[0], "request": {**rows[0]["request"], "scope": {
        k: v for k, v in rows[0]["request"]["scope"].items() if k != "other_region_seats"}}}, *rows[1:]]),
    ("harness/snapshot_day0/index/journal.json",
     lambda j: {g: [{k: v for k, v in x.items() if k != "entities"} for x in es] for g, es in j.items()}),
    ("harness/timeline.jsonl", lambda rows: [
        {**r, "entries": [{k: v for k, v in x.items() if k != "entities"} for x in r["entries"]]}
        if r["type"] == "index_batch" else r for r in rows]),
])
def test_adapter_rejects_non_44_output(tmp_path, rel, fn):
    """출력 체크리스트 대신 적재 검사: generator=worldgen_v4.4, 과제별 answer_types·request.scope(other_region_seats),
    색인 항목(snapshot journal·activity, index_batch)의 entities."""
    from gbg.benchmarks.worldgen.adapter import ScenarioFormatError
    with pytest.raises((ScenarioFormatError, AnswerSchemaError)):
        WorldgenAdapter().load(_mutated(tmp_path, rel, fn))


def test_rulebook_has_bodies_only():
    s = replay("worldgen_mini", [])
    rules = s.rulebook.read_all("FIN-SEL")
    assert rules and all(set(r.model_dump()) == {"id", "group", "body", "title"} for r in rules)
    assert s.rulebook.read("FIN-SEL", "HR-SEL.transfer_effective_day") is None
    assert s.rulebook.search("FIN-SEL", "provisional approvals")


# ─────────────────────────── 2. 등록 시점과 최대 버전 ───────────────────────────
def test_db_registration_and_max_version(wg_run):
    d, _ = wg_run
    events = wal(d)
    line = "FIN-SEL/line/개발1팀/remaining"
    s1, s2 = replay("worldgen_mini", upto(events, 1, 4)), replay("worldgen_mini", upto(events, 2, 0))
    assert s1.db.query("FIN-SEL", line, 1).value == 2_874_300                    # 2일차 등록 전
    assert s2.db.query("FIN-SEL", line, 2).value == 2_417_900
    prof = "HR-SEL/emp/E-SEL-1003/profile"                                        # 버전 3이 1일차, 2가 2일차에 등록
    assert s1.db.query("HR-SEL", prof, 1).v == 3 and s2.db.query("HR-SEL", prof, 2).v == 3
    assert [v.v for v in s2.db.versions("HR-SEL", prof)] == [1, 2, 3]
    assert s2.db.query("HR-SEL", line, 5) is None                                 # 다른 그룹 DB


def test_db_query_tool_hides_keys():
    s = replay("worldgen_mini", [])
    tool = next(t for t in load_adapter("worldgen_mini").make_tools(s) if t.name == "db.query")
    out = asyncio.run(tool.invoke(ToolCall("fin-sel.a1", "FIN-SEL", 1, 1, {"entity": "개발1팀",
                                                                        "record_type": "budget_line_balance"})))
    assert out.result["record"] == 2_874_300 and "FIN-SEL/" not in json.dumps(out.result, ensure_ascii=False)


def test_shard_read_is_caller_only():
    a = load_adapter("silo_mini")
    tool = next(t for t in a.make_tools(replay("silo_mini", [])) if t.name == "shard.read")
    out = asyncio.run(tool.invoke(ToolCall("g1.a2", "G1", 1, 1, {"agent": "g1.a1"})))
    assert tool.resources == () and out == {"agent": "g1.a2", "words": ["apple", "river", "maple", "tiger"]}


# ─────────────────────────── 3. WAL만으로 재생성 ───────────────────────────
@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_projections_rebuild_from_wal(tmp_path, name):
    runner = run(tmp_path, name)
    assert replay(name, wal(tmp_path)).dump() == runner.stores.dump()


def test_projections_rebuild_from_wal_dynamic(tmp_path):
    runner = run(tmp_path, conditions=DYNAMIC)
    assert replay("worldgen_mini", wal(tmp_path), DYNAMIC).dump() == runner.stores.dump()


# ─────────────────────────── 4. 이탈과 인수인계 ───────────────────────────
def test_history_preserved_after_leave_and_successor_starts_with_handover(wg_run):
    d, runner = wg_run
    before = replay("worldgen_mini", [e for e in wal(d) if (e.day, e.round) < (3, 0)])
    leaver = runner.stores.history.entries("fin-sel.a2")
    assert leaver and leaver == before.history.entries("fin-sel.a2"), "떠난 뒤에도 이력은 그대로 남는다"
    succ = runner.stores.history.entries("fin-sel.n0001")
    assert succ and succ[0].text.startswith("[Handover]") and "CMT-00001" in succ[0].entities


# ─────────────────────────── 5. 디렉터리 ───────────────────────────
def test_directory_follows_card_targets_leave_and_join(wg_run):
    d, _ = wg_run
    events = wal(d)
    at = lambda day, rnd: replay("worldgen_mini", upto(events, day, rnd))
    ids = lambda s: [c.occupant for c in s.cards.directory("agent_cards")]
    s0 = at(2, 4)
    assert "fin-sel.a2" in ids(s0) and "fin-sel.a3" not in ids(s0), "같은 역할의 중복 담당은 디렉터리에 없다"
    assert "hr-sel.a2" in ids(s0) and "hr-sel.a1" not in ids(s0)
    assert "fin-tyo.c0" in ids(s0) and not any(".w" in a for a in ids(s0)), "swarm은 coordinator만, 워커는 없다"
    s3 = at(3, 0)
    assert "fin-sel.a2" not in ids(s3) and "fin-sel.n0001" not in ids(s3), "card 대상이 떠난 직후 라운드부터"
    s4 = at(4, 0)
    assert "fin-sel.n0001" in ids(s4) and s4.cards.targets["FIN-SEL"]["payables"] == "fin-sel.n0001"
    old = next(c for c in s0.cards.directory("agent_cards") if c.occupant == "fin-sel.a2")
    new = next(c for c in s4.cards.directory("agent_cards") if c.occupant == "fin-sel.n0001")
    same = lambda c: c.model_dump(exclude={"occupant", "version"})
    assert same(old) == same(new) and new.version == old.version + 1
    assert sorted(c.group for c in s4.cards.directory("group_cards")) == ["FIN-SEL", "FIN-TYO", "HR-SEL", "HR-TYO"]


# ─────────────────────────── 6. 동적 card ───────────────────────────
def test_static_never_attaches_summary(wg_run):
    _, runner = wg_run
    base = {m.agent_id: m.card for g in load_adapter("worldgen_mini").groups() for m in g.members}
    for c in runner.stores.cards.directory("agent_cards"):
        if c.occupant in base:
            assert c == base[c.occupant]


def test_dynamic_summary_is_deterministic_and_after_day_end(tmp_path):
    runner = run(tmp_path, conditions=DYNAMIC)
    events = wal(tmp_path)
    r1 = replay("worldgen_mini", events, DYNAMIC).cards.render("agent_cards")
    assert r1 == replay("worldgen_mini", events, DYNAMIC).cards.render("agent_cards") == \
        runner.stores.cards.render("agent_cards")
    updated = [c for c in runner.stores.cards.directory("agent_cards") if c.scope and c.scope.startswith("Currently handles:")]
    assert updated and all(CardLeakChecker(set(), set()).check(c) == [] for c in updated)
    mid = replay("worldgen_mini", upto(events, 1, 3), DYNAMIC)
    assert not any(c.scope and c.scope.startswith("Currently handles:") for c in mid.cards.directory("agent_cards")), \
        "하루 끝(라운드 4) 커밋 전에는 갱신 없음"


# ─────────────────────────── card 누출 검사 ───────────────────────────
@pytest.mark.parametrize("text", [
    "2417900", "2,417,900", "잔액 2.417.900", "241만", "241만 7천원", "약 240만원", "240만원가량", "240만 정도",
    "2.4M", "$2.4k", "₩2,417,900", "¥389,100", "389100円", "240万円", "二百四十万円", "수백만 원", "3억", "삼억 원",
    "about 2400", "~1500", "1,000", "１２３４５", "약 50", "300 내외", "USD 1200", "1200 USD", "2.4 million",
    "300만 원", "5천원", "3억.", "천만원",
])
def test_amount_like_is_blocked(text):
    assert looks_like_amount(text), text


@pytest.mark.parametrize("text", [
    "영업1팀·개발1팀 예산", "3급 장비 등급 판단", "월 마감, 취소 확정", "HR-SEL 인사기록", "15일까지 임시 대리",
    "SEL 지역 영업1팀, 개발1팀", "Sales-A 지원", "営業1課 예산", "G1 조각 보유자", "2팀 만큼 지원",
])
def test_scope_text_is_allowed(text):
    assert not looks_like_amount(text), text


def test_leak_checker_blocks_ids_names_and_length():
    chk = CardLeakChecker({"박도윤", "도윤 대리"}, allowed={"영업1팀"})
    card = next(m.card for g in load_adapter("worldgen_mini").groups() for m in g.members if m.card)
    assert chk.check(card) == []
    for bad in ({"scope": "CMT-00001 in progress"}, {"scope": "E-SEL-1001"}, {"scope": "도윤 대리 case"},
                {"description": "x" * 1000}, {"scope": "영업1팀 about KRW 2.4 million"}):
        assert chk.check(card.model_copy(update=bad)), bad


def test_blocked_update_is_logged_and_not_published():
    s = replay("worldgen_mini", [], DYNAMIC)
    before = s.cards.render("agent_cards")
    obs = s.cards.update_scope("fin-sel.a1", "Currently handles: 영업1팀, balance KRW 3120400", day=1, seq=9)
    assert s.cards.render("agent_cards") == before
    assert obs and obs[0][1]["status"] == "blocked" and obs[0][1]["seq"] == 9 and "amount" in obs[0][1]["reasons"]


def test_blocked_cards_reach_obs_file(tmp_path, monkeypatch):
    from gbg.stores import cards as cards_mod
    real = cards_mod.CardRegistry.summarize
    monkeypatch.setattr(cards_mod.CardRegistry, "summarize",
                        lambda self, agent, cats: (real(self, agent, cats) or "") + " (about KRW 3 million)")
    run(tmp_path, conditions=DYNAMIC)
    log = [json.loads(x) for x in (tmp_path / "obs" / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
    assert log and all(r["status"] == "blocked" for r in log)
    seqs = {e.seq: e for e in wal(tmp_path)}
    assert all(seqs[r["seq"]].type == "round_commit" and seqs[r["seq"]].round == 4 for r in log)


# ─────────────────────────── 4.2 사건: 이력 줄 · catalog · 색인 · 워커 ───────────────────────────
def test_transcript_lines_and_task_delivery_in_history(wg_run):
    _, runner = wg_run
    h = runner.stores.history.entries("hr-sel.a3")
    texts = [e.text for e in h]
    i = texts.index("[Task] Apply the grade adjustment for 지우 과장")
    assert texts[i + 1] == "[Tool result] Recorded: E-SEL-1003 grade 2." and h[i + 1].role == "tool", "로컬 작업은 재생 줄로"
    assert not any(t.startswith("[Task L-") for t in texts), "로컬 작업은 에이전트에게 배달되지 않는다"
    task = next(e for e in h if e.text.startswith("[Task W-002]"))
    assert "Request:" in task.text and "영업1팀" in task.text
    assert [e.seq for e in h] == list(range(1, len(h) + 1))


def test_catalog_upsert_and_index_updates(wg_run):
    _, runner = wg_run
    s0 = replay("worldgen_mini", [])
    assert s0.catalog.get("FIN-SEL", "commits/CMT-00004") is None
    assert runner.stores.catalog.get("FIN-SEL", "commits/CMT-00004")["department"] == "개발1팀"
    j = [x.text for x in runner.stores.index.journal("FIN-SEL")]
    assert "개발1팀 capex balance registered at KRW 2,417,900." in j and len(j) > len(s0.index.journal("FIN-SEL"))
    assert "fin-sel.a3" in runner.stores.index.holders("FIN-SEL", "CMT-00004")


def test_swarm_worker_spawn_and_despawn(wg_run):
    d, runner = wg_run
    events = wal(d)
    joins = [e for e in events if e.type == "agent_join" and e.payload["kind"] == "spawn"]
    leaves = [e for e in events if e.type == "agent_leave" and e.payload["kind"] == "despawn"]
    assert [e.payload["agent"] for e in joins] == [e.payload["agent"] for e in leaves] == ["fin-tyo.w00002"]
    assert runner.stores.members["fin-tyo.w00002"] == ("FIN-TYO", "worker")
    assert not runner.kernel.is_active("fin-tyo.w00002")
    assert runner.stores.history.entries("fin-tyo.w00002")[0].text.startswith("[Task] Check the 営業1課")
