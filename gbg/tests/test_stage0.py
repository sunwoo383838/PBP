"""Stage 0 수용 기준.

1. 모든 스키마와 어댑터 인터페이스가 pydantic 모델·Protocol로 정의되고, 픽스처가 검증을 통과한다.
2. 조건 설정과 접근 표가 로드되고, 존재하지 않는 조건·자원 이름은 로드 시 오류.
3. 픽스처 두 개: worldgen_mini(worldgen 4.2 형식 축소판: 도메인 2, 지역 2, 그룹 4, specialist 5명 + swarm 1,
   5일, 교차 과제 8개), silo_mini(에이전트 8명을 그룹 4개로, 전역 질문 2개).
4. 코어 패키지가 gbg.benchmarks를 import하지 않음.
"""
import ast
import json
import shutil
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from gbg.contracts.access import AccessTable, load_access
from gbg.contracts.adapter import BenchmarkAdapter
from gbg.contracts.card import AgentCard, GroupCard
from gbg.contracts.conditions import ConfigError, load_conditions, resolve_condition
from gbg.contracts.envelope import Request, Response
from gbg.contracts.events import Event
from gbg.contracts.schemas import DbRecord, TimelineEvent
from gbg.tests.support import load_adapter

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = ROOT / "configs"
FIXTURES = Path(__file__).parent / "fixtures"
CORE_PACKAGES = ["contracts", "kernel", "stores", "llm", "retrieval", "agents", "boundary", "scorer"]


# ─────────────────────────── 픽스처 읽기 (어댑터 경유, private은 테스트만) ───────────────────────────
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.fixture(scope="module", params=["worldgen_mini", "silo_mini"])
def adapter(request):
    return load_adapter(request.param)


# ─────────────────────────── 1. 스키마 · Protocol · 픽스처 검증 ───────────────────────────
def test_adapter_protocol_is_structural():
    class Dummy:
        name = "dummy"
        def load(self, public_dir): ...
        def groups(self): ...
        def initial_state(self, group): ...
        def events(self): ...
        def env_tools(self): ...
        def tag(self, group, text): ...
        def verify(self, task_id, answer, private_dir): ...
        def needs(self, task_id, private_dir): ...

    class Missing:
        name = "missing"
        def load(self, public_dir): ...

    assert isinstance(Dummy(), BenchmarkAdapter)
    assert not isinstance(Missing(), BenchmarkAdapter)


def test_fixture_groups_and_cards(adapter):
    groups = adapter.groups()
    assert groups
    for g in groups:
        assert g.card.group == g.id and g.card.endpoint == f"boundary:{g.id}"
        members = {m.agent_id for m in g.members}
        assert set(g.card_targets.values()) <= members
        for m in g.members:
            assert m.card is None or (m.card.group == g.id and m.card.occupant == m.agent_id)


def test_fixture_initial_state(adapter):
    for g in adapter.groups():
        init = adapter.initial_state(g.id)
        members = {m.agent_id for m in g.members}
        assert init.group == g.id and set(init.histories) <= members
        assert all(x.agent in members for x in init.journal + init.activity)
        assert all(r.key.startswith(g.id + "/") for r in init.db) or adapter.name != "worldgen"


def test_fixture_events_in_seq_order(adapter):
    events = list(adapter.events())
    keys = [(e.day, e.round, e.seq) for e in events]
    assert keys == sorted(keys) and [e.seq for e in events] == sorted({e.seq for e in events})
    assert all(0 <= e.round <= 4 for e in events)


def test_fixture_event_targets_exist(adapter):
    known = {m.agent_id for g in adapter.groups() for m in g.members}
    known |= {e.agent for e in adapter.events() if e.kind in ("agent_join", "spawn")}
    groups = {g.id for g in adapter.groups()}
    for e in adapter.events():
        if e.group is not None:
            assert e.group in groups, e
        if e.agent is not None:
            assert e.agent in known, e


def test_worldgen_mini_shape_and_gold():
    a = load_adapter("worldgen_mini")
    groups = {g.id: g for g in a.groups()}
    assert sorted(groups) == ["FIN-SEL", "FIN-TYO", "HR-SEL", "HR-TYO"]
    assert {g.topology for g in groups.values()} == {"specialist", "swarm"}
    for g in groups.values():
        if g.topology == "specialist":
            active = [m for m in g.members if m.active]
            assert len(active) == 5 and len({m.role for m in active}) == 4, g.id
    assert groups["HR-SEL"].card_targets["records"] == "hr-sel.a2", "중복 담당 a1은 card 대상이 아니다"
    events = list(a.events())
    cross = [e for e in events if e.kind == "cross"]
    assert len(cross) == 8 and max(e.day for e in events) == 5
    assert all(e.request is not None and e.output_schema for e in cross)
    gold = read_jsonl(FIXTURES / "worldgen_mini" / "private" / "gold.jsonl")
    assert {g["wid"] for g in gold} == {e.task_id for e in cross}
    assert {g["state_class"] for g in gold} == {"A", "B", "C", "D"}
    kinds = {e.kind for e in events}
    assert kinds == {"db_register", "catalog", "transcript", "index", "spawn", "despawn", "agent_leave", "agent_join",
                     "local", "cross", "world"}, "4.2 사건 종류를 모두 담는다"


def test_silo_mini_shape():
    a = load_adapter("silo_mini")
    groups = a.groups()
    work = [e for e in a.events() if e.kind == "cross"]
    assert len(groups) == 4 and sum(len(g.members) for g in groups) == 8
    agents = {m.agent_id for g in groups for m in g.members}
    qs = {e.task_id.split(".")[0] for e in work}
    assert len(qs) == 2
    for q in qs:
        assert {e.agent for e in work if e.task_id.startswith(q + ".")} == agents, "전역 질문은 전 에이전트에 도착"


def test_fixture_builder_is_deterministic(tmp_path):
    from gbg.tests.fixtures.build_fixtures import build
    build(tmp_path)
    for name in ("worldgen_mini", "silo_mini"):
        committed = sorted(p.relative_to(FIXTURES / name) for p in (FIXTURES / name).rglob("*") if p.is_file())
        fresh = sorted(p.relative_to(tmp_path / name) for p in (tmp_path / name).rglob("*") if p.is_file())
        assert committed == fresh
        for rel in committed:
            assert (FIXTURES / name / rel).read_bytes() == (tmp_path / name / rel).read_bytes(), rel


def test_schema_rejects_bad_records():
    ok = {"eid": "x", "seq": 1, "day": 1, "round": 1, "kind": "cross", "group": "G", "agent": "a",
          "task_id": "W-1", "text": "t", "request": {}, "output_schema": {"slots": [{"name": "s", "type": "int"}]}}
    TimelineEvent.model_validate(ok)
    for bad in [{"task_id": None}, {"request": None}, {"output_schema": None},       # cross에는 과제 필드 필수
                {"kind": "local"},                                                   # output_schema·request는 cross만
                {"surprise": 1},                                                     # 선언 밖 필드 금지
                {"output_schema": {"slots": [{"name": "s", "type": "enum"}]}},       # enum에는 options
                {"round": -1}]:
        with pytest.raises(ValidationError):
            TimelineEvent.model_validate({**ok, **bad})
    base = {"eid": "x", "seq": 1, "day": 1, "round": 0}
    TimelineEvent.model_validate({**base, "kind": "transcript", "agent": "a",
                                  "payload": {"role": "user", "text": "t", "tokens": 3, "summary": "t"}})
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**base, "kind": "transcript", "agent": "a", "payload": {"text": "t"}})
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**base, "kind": "db_register", "group": "G", "payload": {"key": "k"}})
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**base, "kind": "agent_join", "group": "G", "agent": "a", "payload": {}})
    # DB: 순서 무관, 빈틈 허용, 같은 버전 두 번은 거부
    v = lambda n: {"v": n, "day": 0, "db_day": 0, "value": n}
    DbRecord.model_validate({"key": "k", "versions": [v(3), v(1)]})
    with pytest.raises(ValidationError):
        DbRecord.model_validate({"key": "k", "versions": [v(2), v(2)]})

    resp = {"rid": "r1", "status": "ok", "answer": "a", "items": [], "missing": [], "referral_to": None,
            "need": [], "as_of": 3}
    Response.model_validate(resp)
    with pytest.raises(ValidationError):
        Response.model_validate({**resp, "status": "referral"})                 # referral이면 referral_to 필수
    with pytest.raises(ValidationError):
        Response.model_validate({**resp, "referral_to": "FIN-TYO"})             # referral 아니면 referral_to 금지
    with pytest.raises(ValidationError):
        Response.model_validate({**resp, "status": "need_more"})                # need_more면 need 필수

    Request.model_validate({"rid": "r1", "from_group": "A", "from_agent": "a.a1", "to_group": "B", "to_agent": None,
                            "question": "q", "purpose": None, "origin_task": "W-1", "hop": 1, "lineage": ["A"]})
    Event.model_validate({"seq": 1, "day": 1, "round": 1, "type": "round_commit", "actor": "kernel", "payload": {}})
    with pytest.raises(ValidationError):
        Event.model_validate({"seq": 1, "day": 1, "round": 1, "type": "gossip", "actor": "kernel", "payload": {}})


def test_card_kinds_are_distinct():
    skill = {"id": "s", "name": "s", "description": "d", "tags": [], "examples": []}
    AgentCard.model_validate({"name": "n", "description": "d", "version": 1, "skills": [skill], "group": "G",
                              "scope": None, "occupant": "g.a1"})
    GroupCard.model_validate({"name": "n", "description": "d", "version": 1, "skills": [skill], "group": "G",
                              "service_scope": None, "endpoint": "boundary:G"})
    with pytest.raises(ValidationError):
        GroupCard.model_validate({"name": "n", "description": "d", "version": 1, "skills": [skill], "group": "G",
                                  "service_scope": None, "endpoint": "agent:x"})


# ─────────────────────────── 2. 조건 설정 ───────────────────────────
def test_conditions_load_ladder_and_reference_rows():
    conds = load_conditions(CONFIGS / "conditions.yaml")
    assert list(conds) == ["direct", "routing", "ingress_read", "ingress_sel", "ingress", "i_e", "full_load",
                           "direct_relay", "retrieve", "sidecar", "gateway_rag",   # 부록 3종 (2026-09-30)
                           "ingress_no_requery", "egress_no_history", "retrieval_oracle"]
    assert not {"routing_reveal", "direct_dyncard", "direct_ephemeral", "ingress_raw", "coordinator"} & set(conds)
    fl = conds["full_load"]
    assert fl.agent_tool == "search_memory" and fl.ingress is None and fl.budget_limit, "참조 행: 과제 예산은 다른 조건과 같다"
    assert conds["direct"].agent_tool == "ask_agent" and conds["direct"].directory == "agent_cards"
    assert conds["direct"].ingress is None and conds["direct"].egress is None
    assert conds["routing"].ingress.deliver == "forward" and not conds["routing"].ingress.reveal_holders
    assert conds["ingress_read"].ingress.deliver == "read"
    sel, ing = conds["ingress_sel"].ingress, conds["ingress"].ingress
    assert sel.deliver == ing.deliver == conds["i_e"].ingress.deliver == "assemble"
    assert not (sel.requery or sel.boundary_state or sel.version_marks) and ing.requery and ing.boundary_state and ing.version_marks
    assert {n for n, c in conds.items() if c.blocked} == {"ingress_no_requery", "egress_no_history", "retrieval_oracle"}, "후속"
    assert "ingress_raw" not in conds, "새 Routing과 같아져서 없앴다"
    assert conds["i_e"].agent_tool == "ask" and conds["i_e"].egress.history
    assert all(c.card_mode == "static" for c in conds.values())
    assert all(c.responder_session == "persistent" for c in conds.values())
    d = conds.defaults
    assert (d.budget.calls, d.budget.tokens) == (300, 4000000), "본 실행 상한 (2026-09-30 사용자 결정)"
    assert d.final_reserve.calls == 1 and d.requester.max_asks is None and d.requester.requery


@pytest.mark.parametrize("defaults", [
    None,                                                                       # defaults 없음
    {"budget": {"calls": 1, "tokens": None}, "final_reserve": {"calls": 1, "tokens": 0},
     "requester": {"max_asks": None, "requery": True}},                        # 예약분이 상한 이상
    {"budget": {"calls": None, "tokens": None}, "final_reserve": {"calls": 0, "tokens": 0},
     "requester": {"max_asks": None, "requery": True}},                        # 최종 답변 호출 예약 0
])
def test_bad_defaults_rejected(tmp_path, defaults):
    raw = yaml.safe_load((CONFIGS / "conditions.yaml").read_text(encoding="utf-8"))
    if defaults is None:
        raw.pop("defaults")
    else:
        raw["defaults"] = defaults
    p = tmp_path / "conditions.yaml"
    p.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_conditions(p)


def test_unknown_condition_name_errors():
    conds = load_conditions(CONFIGS / "conditions.yaml")
    assert resolve_condition(conds, "routing") is conds["routing"]
    with pytest.raises(ConfigError):
        resolve_condition(conds, "gateway")


@pytest.mark.parametrize("patch", [
    {"agent_tool": "ask_everyone"},                                            # 없는 도구
    {"directory": "agent_cards"},                                              # ask_group인데 에이전트 디렉터리
    {"ingress": None},                                                         # 그룹에 묻는데 받을 경계 모듈 없음
    {"egress": {"history": True}},                                             # Egress는 ask 도구에서만
    {"card_mode": "live"},
    {"cache": True},                                                           # 선언 밖 키
    {"ingress": {"deliver": "assemble", "reveal_holders": True}},                      # 담당자 공개는 forward만
    {"ingress": {"deliver": "read", "version_marks": True}},                          # 버전 표시는 조립하는 게이트웨이만
    {"ingress": {"deliver": "forward", "requery": True}},                             # 재질의도 조립하는 게이트웨이만
    {"ingress": {"deliver": "forward", "fanout": 3}},                                 # 인원 상한 없음 (과제 예산이 상한)
    {"budget": {"calls": 10, "tokens": 1000}},                                 # 예산은 조건별로 못 바꾼다
    {"responder_session": "shared"},
])
def test_bad_condition_rejected_at_load(tmp_path, patch):
    raw = yaml.safe_load((CONFIGS / "conditions.yaml").read_text(encoding="utf-8"))
    raw["routing"] = {**raw["routing"], **patch}
    p = tmp_path / "conditions.yaml"
    p.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_conditions(p)


# ─────────────────────────── 2. 접근 표 ───────────────────────────
@pytest.fixture(scope="module")
def access() -> AccessTable:
    return load_access(CONFIGS / "access.yaml", load_conditions(CONFIGS / "conditions.yaml"))


@pytest.mark.parametrize("subject,action,resource,scope,expected", [
    # 문서의 접근 표 그대로
    ("agent", "context", "own_history", "own", True),
    ("agent", "r", "own_history", "own", False),                              # ContextBuilder로만
    ("kernel", "w", "own_history", "own", True),
    ("agent", "r", "group_history", "own", False),
    ("boundary", "w", "group_history", "own", False),
    ("kernel", "w", "group_history", "own", True),
    ("agent", "r", "db", "own", True),
    ("agent", "w", "db", "own", False),
    ("boundary", "r", "rulebook", "own", True),
    ("agent", "r", "index", "own", False),
    ("boundary", "r", "index", "own", True),
    ("boundary", "r", "egress_log", "own", True),
    ("kernel", "w", "egress_log", "own", True),
    ("agent", "r", "db", "other", False),                                     # 다른 그룹의 모든 자원
    ("boundary", "r", "group_history", "other", False),
    ("boundary", "r", "db", "other", False),
    ("kernel", "r", "db", "other", True),
    ("kernel", "w", "db", "own", False),                                      # DB는 시나리오대로만 바뀜
    ("kernel", "w", "group_history", "other", True),
    ("kernel", "w", "obs", "any", True),
    ("kernel", "r", "obs", "any", False),
    ("agent", "w", "obs", "any", False),
    ("boundary", "w", "obs", "any", False),
    ("kernel", "r", "private", "any", False),                                 # 누구도 private 불가
    ("boundary", "r", "private", "any", False),
    ("agent", "r", "private", "any", False),
])
def test_access_table_matches_plan(access, subject, action, resource, scope, expected):
    for cond in ("direct", "routing", "ingress_read", "ingress_sel", "ingress", "i_e", "full_load", "gateway_rag"):
        if cond == "full_load" and subject == "agent" and action == "r" and (
                (scope == "other" and resource in ("db", "rulebook", "group_history")) or
                (scope == "own" and resource == "group_history")):
            continue                                                       # full_load만: 모든 그룹 조회·이력 (아래 테스트)
        assert access.allows(subject, action, resource, scope, cond) is expected


def test_boundary_search_is_same_for_all_boundary_conditions(access):
    """담당자 선택용 검색(색인 + catalog + 그룹 이력)은 모든 경계 조건이 같다. 에이전트는 다른 그룹 이력을 못 읽는다."""
    for cond in ("routing", "ingress_read", "ingress_sel", "ingress", "i_e", "gateway_rag"):
        assert access.allows("boundary", "r", "group_history", "own", cond), cond
        assert access.allows("boundary", "r", "index", "own", cond), cond
        assert access.allows("boundary", "r", "db", "own", cond), cond
    for cond in ("direct", "routing", "ingress", "i_e"):
        assert not access.allows("agent", "r", "group_history", "other", cond), cond
    for res in ("db", "rulebook", "group_history"):
        assert access.allows("agent", "r", res, "other", "full_load"), res
    assert not access.allows("agent", "r", "index", "other", "full_load"), "색인은 경계 모듈 전용"


def test_access_unknown_names_rejected(access):
    with pytest.raises(ConfigError):
        access.allows("agent", "r", "shard", "own", "direct")                 # 없는 자원
    with pytest.raises(ConfigError):
        access.allows("agent", "r", "db", "own", "gateway")                   # 없는 조건
    with pytest.raises(ConfigError):
        access.allows("admin", "r", "db", "own", "direct")                    # 없는 주체


@pytest.mark.parametrize("mutate", [
    lambda raw: raw["rules"].append({"subject": "agent", "resource": "shard", "scope": "own", "perm": "r"}),
    lambda raw: raw["rules"].append({"subject": "agent", "resource": "private", "scope": "any", "perm": "r"}),
    lambda raw: raw["rules"].append({"subject": "agent", "resource": "obs", "scope": "own", "perm": "r"}),
    lambda raw: raw["overrides"].update({"oracle_load": [{"subject": "agent", "resource": "group_history", "scope": "other", "perm": "r"}]}),
    lambda raw: raw["rules"].append({"subject": "agent", "resource": "db", "scope": "own", "perm": "x"}),
])
def test_bad_access_table_rejected_at_load(tmp_path, mutate):
    raw = yaml.safe_load((CONFIGS / "access.yaml").read_text(encoding="utf-8"))
    mutate(raw)
    p = tmp_path / "access.yaml"
    p.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_access(p, load_conditions(CONFIGS / "conditions.yaml"))


# ─────────────────────────── 4. 벤치마크 중립 ───────────────────────────
def _imports(path: Path, package: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:                                                   # 상대 import → 절대 이름으로
                base = package.split(".")[: len(package.split(".")) - node.level + 1]
                yield ".".join(base + ([node.module] if node.module else []))
            else:
                yield node.module or ""


def test_core_does_not_import_benchmarks():
    gbg = ROOT / "gbg"
    checked = 0
    for pkg in CORE_PACKAGES:
        for path in (gbg / pkg).rglob("*.py") if (gbg / pkg).exists() else []:
            package = ".".join(path.relative_to(ROOT).parts[:-1])
            for name in _imports(path, package):
                assert not (name == "gbg.benchmarks" or name.startswith("gbg.benchmarks.")), f"{path}: {name}"
            checked += 1
    assert checked > 0


def test_import_ban_detects_violation(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("from ..benchmarks.worldgen import adapter\n", encoding="utf-8")
    assert "gbg.benchmarks.worldgen" in set(_imports(bad, "gbg.kernel"))
