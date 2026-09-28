"""Stage 2 수용 기준 (시나리오 로더와 저장소).

1. 픽스처를 로드하고 private/ 접근 시도가 예외를 낸다.
2. db.query가 등록 지연을 반영한다 (지연 중인 버전은 반환되지 않음).
3. 스크립트 에이전트로 5일 실행 후, 모든 투영(card 레지스트리 포함)을 WAL만으로 재생성한 결과가 실행 중 투영과 동일.
4. 에이전트 이탈 후에도 이력이 보존되고, 후임의 이력은 인수인계 노트부터 시작.
5. 이탈 직후 라운드부터 디렉터리에 떠난 에이전트가 없고 후임이 같은 역할 card로 나타난다.
6. card_mode: dynamic에서 같은 활동 색인이면 동적 요약이 바이트 동일하고, static에서는 요약이 붙지 않는다.
+ card 누출 검사: 금액처럼 보이는 표현(쉼표 없는 숫자, 만/억 단위, 근사 표현 포함)은 전부 차단, 차단은 obs/cards.jsonl에 기록.
"""
import json
import re
from pathlib import Path

import pytest

from gbg.agents.scripted import ScriptedAgent, fixed_answer
from gbg.benchmarks.common import PrivateAccessError
from gbg.benchmarks.silo.adapter import SiloAdapter
from gbg.benchmarks.worldgen.adapter import WorldgenAdapter
from gbg.contracts.access import load_access
from gbg.contracts.conditions import load_conditions
from gbg.contracts.events import Event
from gbg.kernel.runner import KernelParams, Runner
from gbg.kernel.tools import ToolCall, ToolRegistry
from gbg.stores import Stores
from gbg.stores.cards import CardLeakChecker, looks_like_amount

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
CONDITIONS = load_conditions(ROOT / "configs" / "conditions.yaml")
ACCESS = load_access(ROOT / "configs" / "access.yaml", CONDITIONS)
DYNAMIC = {**CONDITIONS, "direct": CONDITIONS["direct"].model_copy(update={"card_mode": "dynamic"})}
ADAPTERS = {"worldgen_mini": WorldgenAdapter, "silo_mini": SiloAdapter}


def adapter(name="worldgen_mini"):
    a = ADAPTERS[name]()
    a.load(FIXTURES / name / "public")
    return a


class EnvAgent(ScriptedAgent):
    """작업마다 환경 도구를 한 번 쓰고, 교차 작업이면 다른 그룹 첫 구성원에게 묻는다."""
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
    return lambda task: ("db.query", {"key": f"{task.group}/line/{'개발1팀' if 'SEL' in task.group else '開発1課'}/remaining"})


def run(tmp, name="worldgen_mini", conditions=CONDITIONS):
    a = adapter(name)
    first = {g.id: sorted(m.agent_id for m in g.members)[0] for g in a.groups()}
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
    s = Stores.from_adapter(adapter(name), card_mode=conditions["direct"].card_mode,
                            rounds_per_day=KernelParams().rounds_per_day)
    for ev in events:
        s.apply(ev)
    return s


@pytest.fixture(scope="module")
def wg_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("wg")
    return d, run(d)


# ─────────────────────────── 1. 로더와 private 거부 ───────────────────────────
@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_load_fixture(name):
    a = adapter(name)
    assert a.groups() and list(a.events())
    for g in a.groups():
        init = a.initial_state(g.id)
        assert init.group == g.id


@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_private_access_is_refused(name):
    a = ADAPTERS[name]()
    with pytest.raises(PrivateAccessError):
        a.load(FIXTURES / name / "private")
    with pytest.raises(PrivateAccessError):
        a.load(FIXTURES / name)                                   # 시나리오 루트도 거부: public/만 받는다
    b = adapter(name)
    with pytest.raises(PrivateAccessError):
        b.read_public("../private/gold.jsonl")
    with pytest.raises(PrivateAccessError):
        b.read_public(str((FIXTURES / name / "private" / "gold.jsonl").resolve()))


def test_rulebook_has_bodies_only():
    s = replay("worldgen_mini", [])
    rules = s.rulebook.read_all("FIN-SEL")
    assert rules and all(set(r.model_dump()) == {"id", "group", "body"} for r in rules)
    assert s.rulebook.read("FIN-SEL", "HR-SEL.transfer_effective") is None    # 다른 그룹 규정은 안 보임
    assert s.rulebook.search("FIN-SEL", "가승인")


# ─────────────────────────── 2. 등록 지연 ───────────────────────────
def test_db_query_respects_registration_lag():
    s = replay("worldgen_mini", [])
    key = "FIN-SEL/line/개발1팀/remaining"
    assert s.db.query("FIN-SEL", key, day=1).value == 2_874_300              # 0일차 조정은 2일차 등록
    assert s.db.query("FIN-SEL", key, day=2).value == 2_417_900
    assert s.db.query("FIN-SEL", "FIN-SEL/commit/CMT-00002/status", day=5) is None   # 없는 레코드
    assert s.db.query("HR-SEL", key, day=5) is None                          # 다른 그룹 DB


def test_db_query_tracks_world_updates(wg_run):
    d, _ = wg_run
    events = wal(d)
    s = replay("worldgen_mini", [e for e in events if e.day <= 3])
    key = "HR-SEL/emp/E-SEL-1001/profile"
    assert s.db.query("HR-SEL", key, day=3).value["dept"] == "개발1팀"      # 3일차 발효, 4일차 등록
    assert s.db.query("HR-SEL", key, day=4).value["dept"] == "영업1팀"


def test_db_query_tool_goes_through_lag(wg_run):
    _, runner = wg_run
    tool = next(t for t in runner.kernel.tools._tools.values() if t.name == "db.query")
    call = lambda day: ToolCall("fin-sel.a1", "FIN-SEL", day, 1, {"key": "FIN-SEL/line/개발1팀/remaining"})
    import asyncio
    assert asyncio.run(tool.invoke(call(1))) == {"key": "FIN-SEL/line/개발1팀/remaining", "value": 2_874_300, "v": 1}
    assert asyncio.run(tool.invoke(call(2)))["value"] == 2_417_900
    absent = asyncio.run(tool.invoke(ToolCall("fin-sel.a1", "FIN-SEL", 2, 1, {"key": "FIN-SEL/nope"})))
    assert absent == {"key": "FIN-SEL/nope", "value": "ABSENT"}


def test_shard_read_is_caller_only():
    a = adapter("silo_mini")
    s = replay("silo_mini", [])
    tool = next(t for t in a.make_tools(s) if t.name == "shard.read")
    assert tool.resources == ()
    import asyncio
    out = asyncio.run(tool.invoke(ToolCall("g1.a2", "G1", 1, 1, {"agent": "g1.a1"})))
    assert out == {"agent": "g1.a2", "words": ["apple", "river", "maple", "tiger"]}   # 인자와 무관하게 자기 조각


# ─────────────────────────── 3. WAL만으로 재생성 ───────────────────────────
@pytest.mark.parametrize("name", ["worldgen_mini", "silo_mini"])
def test_projections_rebuild_from_wal(tmp_path, name):
    runner = run(tmp_path, name)
    live = runner.stores.dump()
    assert replay(name, wal(tmp_path)).dump() == live


def test_projections_rebuild_from_wal_dynamic(tmp_path):
    runner = run(tmp_path, conditions=DYNAMIC)
    assert replay("worldgen_mini", wal(tmp_path), DYNAMIC).dump() == runner.stores.dump()


# ─────────────────────────── 4. 이탈과 인수인계 ───────────────────────────
def test_history_preserved_after_leave_and_successor_starts_with_handover(wg_run):
    d, runner = wg_run
    events = wal(d)
    before = replay("worldgen_mini", [e for e in events if (e.day, e.round) < (3, 0)])
    after = runner.stores
    leaver = after.history.entries("fin-sel.a3")
    assert leaver and leaver == before.history.entries("fin-sel.a3"), "떠난 뒤에도 이력은 그대로 남는다"
    succ = after.history.entries("fin-sel.n0001")
    assert succ and succ[0].text.startswith("[인수인계]") and succ[0].role == "user"
    assert "CMT-00001" in succ[0].entities


# ─────────────────────────── 5. 디렉터리 ───────────────────────────
def test_directory_after_leave_and_join(wg_run):
    d, _ = wg_run
    events = wal(d)
    at = lambda day, rnd: replay("worldgen_mini", [e for e in events if (e.day, e.round) <= (day, rnd)])
    ids = lambda s: [c.occupant for c in s.cards.directory("agent_cards")]
    assert "fin-sel.a3" in ids(at(2, 3))
    assert "fin-sel.a3" not in ids(at(3, 0))                                 # 이탈 직후 라운드부터
    assert "fin-sel.n0001" not in ids(at(3, 3))
    s4 = at(4, 0)
    assert "fin-sel.n0001" in ids(s4)
    old = next(c for c in at(2, 3).cards.directory("agent_cards") if c.occupant == "fin-sel.a3")
    new = next(c for c in s4.cards.directory("agent_cards") if c.occupant == "fin-sel.n0001")
    same = lambda c: c.model_dump(exclude={"occupant", "version"})
    assert same(old) == same(new) and new.version == old.version + 1
    groups = at(4, 0).cards.directory("group_cards")
    assert sorted(c.group for c in groups) == ["FIN-SEL", "FIN-TYO", "HR-SEL", "HR-TYO"]


# ─────────────────────────── 6. 동적 card ───────────────────────────
def test_static_never_attaches_summary(wg_run):
    _, runner = wg_run
    base = {m.agent_id: m.card for g in adapter().groups() for m in g.members}
    for c in runner.stores.cards.directory("agent_cards"):
        if c.occupant in base:
            assert c == base[c.occupant]


def test_dynamic_summary_is_deterministic_and_next_day(tmp_path):
    runner = run(tmp_path, conditions=DYNAMIC)
    events = wal(tmp_path)
    s1 = replay("worldgen_mini", events, DYNAMIC)
    s2 = replay("worldgen_mini", events, DYNAMIC)
    r1 = s1.cards.render("agent_cards")
    assert r1 == s2.cards.render("agent_cards") == runner.stores.cards.render("agent_cards")
    updated = [c for c in runner.stores.cards.directory("agent_cards") if c.scope and c.scope.startswith("담당 범위:")]
    assert updated, "로컬 작업을 한 에이전트의 담당 범위가 갱신돼야 한다"
    # 1일차 작업은 1일차 마지막 라운드 커밋 뒤에 반영된다: 1일차 3라운드까지는 갱신 없음
    mid = replay("worldgen_mini", [e for e in events if (e.day, e.round) <= (1, 2)], DYNAMIC)
    assert not any(c.scope and c.scope.startswith("담당 범위:") for c in mid.cards.directory("agent_cards"))
    for c in updated:
        assert CardLeakChecker(set(), set()).check(c) == []


def test_same_activity_same_summary():
    a, b = replay("worldgen_mini", [], DYNAMIC), replay("worldgen_mini", [], DYNAMIC)
    for s in (a, b):
        s.cards.day_end(day=1, activity=s.activity, seq=1)
    assert a.cards.render("agent_cards") == b.cards.render("agent_cards")


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
    names = {"박도윤", "도윤 대리"}
    chk = CardLeakChecker(names, allowed={"영업1팀"})
    card = adapter().groups()[0].members[0].card
    assert chk.check(card) == []
    assert chk.check(card.model_copy(update={"scope": "CMT-00001 처리 중"}))
    assert chk.check(card.model_copy(update={"scope": "E-SEL-1001 담당"}))
    assert chk.check(card.model_copy(update={"scope": "도윤 대리 건 담당"}))
    assert chk.check(card.model_copy(update={"description": "x" * 1000}))
    assert chk.check(card.model_copy(update={"scope": "영업1팀 예산 약 240만원"}))


def test_blocked_update_is_logged_and_not_published():
    s = replay("worldgen_mini", [], DYNAMIC)
    before = s.cards.render("agent_cards")
    obs = s.cards.update_scope("fin-sel.a1", "담당 범위: 영업1팀 잔액 3120400원", day=1, seq=9)
    assert s.cards.render("agent_cards") == before
    assert obs and obs[0][0] == "cards" and obs[0][1]["status"] == "blocked" and obs[0][1]["seq"] == 9
    assert "amount" in obs[0][1]["reasons"]


def test_blocked_cards_reach_obs_file(tmp_path, monkeypatch):
    from gbg.stores import cards as cards_mod
    real = cards_mod.CardRegistry.summarize
    monkeypatch.setattr(cards_mod.CardRegistry, "summarize",
                        lambda self, agent, cats: (real(self, agent, cats) or "") + " 약 300만원")
    run(tmp_path, conditions=DYNAMIC)
    log = [json.loads(x) for x in (tmp_path / "obs" / "cards.jsonl").read_text(encoding="utf-8").splitlines()]
    assert log and all(r["status"] == "blocked" for r in log)
    seqs = {e.seq: e for e in wal(tmp_path)}
    assert all(seqs[r["seq"]].type == "round_commit" and seqs[r["seq"]].round == 3 for r in log)


# ─────────────────────────── 이력 · 색인 ───────────────────────────
def test_history_rendering(wg_run):
    _, runner = wg_run
    h = runner.stores.history
    entries = h.entries("hr-sel.a2")
    warm = adapter().initial_state("HR-SEL").histories["hr-sel.a2"]
    assert list(entries[: len(warm)]) == warm, "워밍업 이력이 앞에 그대로"
    run_part = entries[len(warm):]
    task = next(e for e in run_part if e.text.startswith("[과제 L-001]"))
    assert task.role == "user" and "E-SEL-1003" in task.entities
    tool = run_part[run_part.index(task) + 1]
    assert tool.role == "tool" and tool.text.startswith("[db.query]")
    assert [e.seq for e in entries] == list(range(1, len(entries) + 1))
    cum = h.cumulative("hr-sel.a2")
    assert cum == sorted(cum) and cum[-1] == sum(e.tokens for e in entries)
    for e in run_part:
        assert not re.search(r"\d{1,3}(,\d{3})+|\d{5,}", e.digest), e.digest


def test_activity_updated_on_local_task(wg_run):
    _, runner = wg_run
    recs = runner.stores.activity.lookup("HR-SEL", "E-SEL-1003")
    assert recs and recs[-1].agent == "hr-sel.a2" and recs[-1].day == 1
    entry = runner.stores.history.entries("hr-sel.a2")[recs[-1].seq - 1]
    assert entry.text.startswith("[답 제출 L-001]")
    assert runner.stores.activity.lookup("FIN-SEL", "E-SEL-1003") == [], "색인은 그룹 내부 전용"


def test_journal_runtime_addition(wg_run):
    _, runner = wg_run
    rec = runner.stores.journal.lookup("FIN-TYO", "開発1課")
    assert rec and rec[-1].agent == "fin-tyo.a2"
    assert runner.stores.history.entries("fin-tyo.a2")[rec[-1].seq - 1].text.startswith("[답 제출 L-006]")


def test_egress_log_seed():
    s = replay("worldgen_mini", [])
    assert [r.to_group for r in s.egress_log.lookup("FIN-SEL", "E-SEL-1001", "profile")] == ["HR-SEL"]
    assert s.egress_log.lookup("FIN-SEL", "E-SEL-1001") and s.egress_log.lookup("HR-SEL", "E-SEL-1001") == []
