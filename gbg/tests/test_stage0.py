"""Stage 0 수용 기준.

1. 모든 스키마와 어댑터 인터페이스가 pydantic 모델·Protocol로 정의되고, 픽스처가 검증을 통과한다.
2. 조건 설정과 접근 표가 로드되고, 존재하지 않는 조건·자원 이름은 로드 시 오류.
3. 픽스처 두 개: worldgen_mini(도메인 2, 지역 2, 그룹 4, 그룹당 3명, 5일, 교차 작업 10개),
   silo_mini(에이전트 8명을 그룹 4개로, 전역 질문 2개).
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
from gbg.contracts.schemas import (
    GoldRecord, GroupSnapshot, Manifest, RuleText, TimelineEvent, WorldInit,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIGS = ROOT / "configs"
FIXTURES = Path(__file__).parent / "fixtures"
CORE_PACKAGES = ["contracts", "kernel", "stores", "llm", "retrieval", "agents", "boundary", "scorer"]


# ─────────────────────────── 픽스처 읽기 (테스트 전용: private 포함) ───────────────────────────
def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Scenario:
    def __init__(self, name):
        pub, priv = FIXTURES / name / "public", FIXTURES / name / "private"
        self.manifest = Manifest.model_validate_json((pub / "manifest.json").read_text(encoding="utf-8"))
        self.world = WorldInit.model_validate_json((pub / "world_init.json").read_text(encoding="utf-8"))
        self.rules = [RuleText.model_validate(x) for x in json.loads((pub / "rulebook.json").read_text(encoding="utf-8"))]
        self.snapshots = {p.stem: GroupSnapshot.model_validate_json(p.read_text(encoding="utf-8"))
                          for p in sorted((pub / "snapshot_day0").glob("*.json"))}
        self.timeline = [TimelineEvent.model_validate(x) for x in read_jsonl(pub / "timeline.jsonl")]
        self.work = [TimelineEvent.model_validate(x) for x in read_jsonl(pub / "work.jsonl")]
        self.gold = [GoldRecord.model_validate(x) for x in read_jsonl(priv / "gold.jsonl")]
        self.rule_params = json.loads((priv / "rulebook_params.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=["worldgen_mini", "silo_mini"])
def scenario(request):
    return Scenario(request.param)


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


def test_fixture_manifest_and_groups(scenario):
    groups = {g.id for g in scenario.world.groups}
    assert scenario.world.benchmark == scenario.manifest.benchmark
    assert set(scenario.snapshots) == groups
    for g in scenario.world.groups:
        assert g.card.group == g.id and g.card.endpoint == f"boundary:{g.id}"
        for m in g.members:
            assert m.card.group == g.id and m.card.occupant == m.agent_id


def test_fixture_snapshot_agents_exist(scenario):
    members = {g.id: {m.agent_id for m in g.members} for g in scenario.world.groups}
    for gid, snap in scenario.snapshots.items():
        assert snap.group == gid
        assert set(snap.histories) <= members[gid]
        assert all(r.agent in members[gid] for r in snap.activity + snap.journal)


def test_fixture_timeline_sorted_and_unique(scenario):
    events = sorted(scenario.timeline + scenario.work, key=lambda e: e.seq)
    keys = [(e.day, e.round, e.seq) for e in events]
    assert keys == sorted(keys), "seq 순서와 (day, round) 순서가 어긋남"
    assert len({e.seq for e in events}) == len(events)
    assert all(1 <= e.day <= scenario.manifest.days for e in events)
    assert all(e.kind == "cross" for e in scenario.work)
    assert all(e.kind != "cross" for e in scenario.timeline)


def test_fixture_event_targets_exist(scenario):
    known = {m.agent_id for g in scenario.world.groups for m in g.members}
    known |= {e.agent for e in scenario.timeline if e.kind == "world" and e.action == "agent_join"}
    groups = {g.id for g in scenario.world.groups}
    for e in scenario.timeline + scenario.work:
        assert e.group in groups
        if e.agent is not None:
            assert e.agent in known, e


def test_fixture_gold_covers_tasks(scenario):
    tasks = {e.task_id for e in scenario.timeline + scenario.work if e.kind in ("local", "cross")}
    gold = {g.task_id for g in scenario.gold}
    assert gold == tasks
    cross = {e.task_id for e in scenario.work}
    for g in scenario.gold:
        if g.task_id in cross:
            assert g.needs, f"{g.task_id}: 교차 작업에 need가 없음"
            assert g.state_class is not None


def test_fixture_rulebook_split(scenario):
    ids = [r.id for r in scenario.rules]
    assert len(ids) == len(set(ids))
    assert set(scenario.rule_params) == set(ids), "규정 본문(공개)과 파라미터(비공개)의 id가 어긋남"
    groups = {g.id for g in scenario.world.groups}
    assert all(r.group in groups for r in scenario.rules)


def test_fixture_rule_sources_resolve(scenario):
    ids = {r.id for r in scenario.rules}
    for g in scenario.gold:
        for n in g.needs:
            for s in n.sources:
                if s.type == "rule":
                    assert s.id in ids


def test_worldgen_mini_shape():
    s = Scenario("worldgen_mini")
    assert s.manifest.benchmark == "worldgen" and s.manifest.days == 5
    assert len({g.id.split("-")[0] for g in s.world.groups}) == 2
    assert len({g.id.split("-")[1] for g in s.world.groups}) == 2
    assert len(s.world.groups) == 4
    assert all(len(g.members) == 3 for g in s.world.groups)
    assert len(s.work) == 10


def test_silo_mini_shape():
    s = Scenario("silo_mini")
    assert s.manifest.benchmark == "silo"
    assert len(s.world.groups) == 4
    assert sum(len(g.members) for g in s.world.groups) == 8
    assert len({e.task_id.split(".")[0] for e in s.work}) == 2
    agents = {m.agent_id for g in s.world.groups for m in g.members}
    for q in {e.task_id.split(".")[0] for e in s.work}:
        assert {e.agent for e in s.work if e.task_id.startswith(q + ".")} == agents, "전역 질문은 전 에이전트에 도착"


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
          "task_id": "W-1", "text": "t", "output_schema": {"slots": [{"name": "s", "type": "number"}]}}
    TimelineEvent.model_validate(ok)
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**ok, "task_id": None})                   # 작업에는 task_id 필수
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**ok, "kind": "world"})                   # world에는 action 필수
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**ok, "surprise": 1})                     # 선언 밖 필드 금지
    with pytest.raises(ValidationError):
        TimelineEvent.model_validate({**ok, "output_schema": {"slots": [{"name": "s", "type": "enum"}]}})

    resp = {"rid": "r1", "status": "ok", "answer": "a", "values": [], "missing": [], "referral_to": None,
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
def test_conditions_load_ladder():
    conds = load_conditions(CONFIGS / "conditions.yaml")
    assert list(conds) == ["direct", "routing", "ingress", "i_e"]
    assert conds["direct"].agent_tool == "ask_agent" and conds["direct"].directory == "agent_cards"
    assert conds["direct"].ingress is None and conds["direct"].egress is None
    assert conds["routing"].ingress.fanout == 1 and not conds["routing"].ingress.assemble
    assert conds["ingress"].ingress.fanout == 3 and conds["ingress"].ingress.requery
    assert conds["i_e"].agent_tool == "ask" and conds["i_e"].egress.history
    assert all(c.card_mode == "static" for c in conds.values())


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
    ("boundary", "r", "group_history", "own", True),
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
    for cond in ("direct", "routing", "ingress", "i_e"):
        assert access.allows(subject, action, resource, scope, cond) is expected


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
    lambda raw: raw["overrides"].update({"full_load": [{"subject": "agent", "resource": "group_history", "scope": "other", "perm": "r"}]}),
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
