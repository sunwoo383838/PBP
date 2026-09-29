"""worldgen 구조화 조회 도구: db.query(entity, record_type), entity.search (그룹 단위 권한, catalog 기반 이름 해소).

- 스키마에는 그룹 도메인이 읽을 수 있는 record type과 의미만 있고 physical key·레코드 목록은 없다.
- 스키마와 실행 중 권한은 같은 record_policy에서 나오고, 백엔드가 권한을 다시 검사한다.
- 같은 그룹이면 역할과 무관하게, 같은 역할·그룹이면 조건과 무관하게 같은 도구를 받는다.
- 에이전트에게는 HIT / NOT_FOUND / AMBIGUOUS / INVALID_TYPE만 보이고, 원래 라벨은 obs에만 남는다.
- NOT_FOUND·AMBIGUOUS에는 후보 없이 일반 힌트만 준다.
- entity.search는 자기 그룹, 현재 시점(catalog 추가·DB 등록), 발견성(등록된 것만)을 지킨다.
- 도구 정의 토큰은 호출마다 고정비로 기록된다.
"""
import asyncio
import json
from pathlib import Path

import pytest

from gbg.agents.scripted import ScriptedAgent
from gbg.benchmarks.worldgen import env_tools
from gbg.benchmarks.worldgen.records import HINTS, load_policy
from gbg.contracts.access import load_access
from gbg.contracts.conditions import load_conditions
from gbg.contracts.schemas import DbVersion
from gbg.kernel.runner import Runner
from gbg.kernel.tools import ToolCall, ToolRegistry
from gbg.tests.support import load_adapter

ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = load_conditions(ROOT / "configs" / "conditions.yaml")
ACCESS = load_access(ROOT / "configs" / "access.yaml", CONDITIONS)
VISIBLE_STATES = {"HIT", "NOT_FOUND", "AMBIGUOUS", "INVALID_TYPE"}


def run_until(tmp, day, factory=lambda aid, g, role: ScriptedAgent(aid)):
    a = load_adapter("worldgen_mini")
    r = Runner(a, condition="direct", seed=7, run_dir=tmp, conditions=CONDITIONS, access=ACCESS,
               tools=ToolRegistry(ACCESS), env_tools=a.make_tools, agent_factory=factory, max_day=day)
    r.run()
    return a, r


class Tools:
    def __init__(self, tmp, day=5, policy=None):
        self.adapter, self.runner = run_until(tmp, day)
        self.stores = self.runner.stores
        kw = {"policy": policy} if policy else {}
        self.tools = {t.name: t for t in env_tools.make_tools(self.stores, self.adapter.domain_of(), **kw)}

    def call(self, tool, agent, day, **args):
        group = self.stores.members[agent][0]
        out = asyncio.run(self.tools[tool].invoke(ToolCall(agent, group, day, 1, args)))
        (_, log), = out.obs
        return out.result, log


@pytest.fixture(scope="module")
def t(tmp_path_factory):
    return Tools(tmp_path_factory.mktemp("tools"))


def q(t, agent, day, entity, rtype):
    return t.call("db.query", agent, day, entity=entity, record_type=rtype)


# ─────────────────────────── 스키마 ───────────────────────────
def test_schema_lists_domain_types_and_meanings_only():
    p = load_policy()
    for domain in ("HR", "IT", "FIN", "PROC", "LEGAL"):
        spec = next(s for s in env_tools.domain_specs(domain) if s.name == "db.query")
        rt = spec.parameters["properties"]["record_type"]
        assert rt["enum"] == p.types_for(domain) and "catalog_entry" in rt["enum"]
        assert all(p.record_types[x].description in rt["description"] for x in rt["enum"])
    assert "budget_line_balance" not in env_tools.domain_specs("HR")[0].parameters["properties"]["record_type"]["enum"]
    dumped = json.dumps([s.model_dump() for d in ("HR", "IT", "FIN", "PROC", "LEGAL") for s in env_tools.domain_specs(d)],
                        ensure_ascii=False)
    for leak in ("{group}", "{entity}", "/emp/", "/line/", "/commit/", "FIN-SEL", "E-SEL-", "CMT-"):
        assert leak not in dumped, f"스키마에 내부 key나 레코드가 보인다: {leak}"


def test_same_tools_for_all_roles_in_group_and_all_conditions():
    from gbg.llm.agent_loop import REPLY_TOOL, AgentRuntime, LLMAgent
    a = load_adapter("worldgen_mini")
    env_names = {"db.query", "entity.search", "rulebook.read"}
    per = set()
    for name, c in CONDITIONS.items():
        agent = LLMAgent("x", AgentRuntime(c, a.group_tools, None, 6, 1))
        per.add(json.dumps([x for x in agent.tool_schemas("FIN-SEL", REPLY_TOOL) if x["function"]["name"] in env_names],
                           sort_keys=True))
    assert len(per) == 1, "조건이 달라도 환경 도구는 같다"
    assert a.group_tools("FIN-SEL") == a.group_tools("FIN-TYO"), "같은 도메인이면 같다 (역할은 권한에 쓰지 않는다)"


def test_schema_and_authorization_come_from_same_policy(tmp_path):
    p = load_policy().model_copy(deep=True)
    p.record_types["budget_line_balance"].domains = ["PROC"]                      # 정책 한 곳만 바꾼다
    spec = next(s for s in env_tools.domain_specs("FIN", p) if s.name == "db.query")
    assert "budget_line_balance" not in spec.parameters["properties"]["record_type"]["enum"]
    t2 = Tools(tmp_path, day=1, policy=p)
    vis, log = q(t2, "fin-sel.a1", 1, "영업1팀", "budget_line_balance")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "TYPE_NOT_PERMITTED"


# ─────────────────────────── 조회 ───────────────────────────
def test_hit_by_id_and_catalog_name_without_key(t):
    for name in ("E-SEL-1000", "하린 과장", "김하린", "  김하린 ", "e-sel-1000"):
        vis, log = q(t, "hr-sel.a4", 5, name, "employee_profile")                # 역할과 무관 (recruiting)
        assert vis["status"] == "HIT" and vis["entity"] == "E-SEL-1000" and vis["record"]["dept"] == "영업1팀", name
    assert set(vis) == {"status", "entity", "record_type", "registered_day", "record"}
    assert "HR-SEL/" not in json.dumps(vis, ensure_ascii=False) and log["keys"] == ["HR-SEL/emp/E-SEL-1000/profile"]


def test_current_value_is_max_registered_version(t):
    vis, log = q(t, "hr-sel.a1", 5, "지우 과장", "employee_profile")             # v3이 v2보다 먼저 등록됨
    assert vis["record"]["grade"] == 3 and log["version"] == 3


def test_catalog_entry(t):
    vis, _ = q(t, "fin-sel.a4", 5, "CMT-00004", "catalog_entry")
    assert vis["status"] == "HIT" and vis["record"]["department"] == "개발1팀"


def test_other_group_entity_looks_like_not_found(t):
    vis, log = q(t, "fin-sel.a1", 5, "営業1課", "budget_line_balance")
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]} and log["label"] == "PERMISSION_DENIED"
    vis, _ = q(t, "fin-tyo.c0", 5, "営業1課", "budget_line_balance")
    assert vis["status"] == "HIT"


def test_no_record_and_unknown_name(t):
    vis, log = q(t, "fin-sel.a1", 5, "영업1팀", "budget_line_base")
    assert vis["status"] == "HIT"
    vis, log = q(t, "fin-sel.a1", 5, "CMT-00004", "provisional_approval")
    assert vis["status"] == "HIT" and vis["record"]["amount"] == 301_200
    vis, log = q(t, "hr-sel.a1", 5, "E-TYO-1000", "employee_profile")            # 다른 그룹 직원
    assert vis["status"] == "NOT_FOUND" and log["label"] == "PERMISSION_DENIED"
    vis, log = q(t, "hr-sel.a1", 5, "없는 사람", "employee_profile")
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]} and log["label"] == "NOT_FOUND"
    vis, log = q(t, "fin-sel.a1", 5, "CMT-00002", "provisional_approval")        # 이력에만 있는 건: DB·catalog에 없다
    assert vis["status"] == "NOT_FOUND" and log["label"] == "NOT_FOUND"


def test_ambiguous_gives_no_candidates(tmp_path):
    t2 = Tools(tmp_path, day=1)
    t2.stores.catalog.upsert("HR-SEL", "employees/E-SEL-1002",
                             {"employee_id": "E-SEL-1002", "name": "이서준", "alias": "지우 과장", "region": "SEL"})
    vis, log = q(t2, "hr-sel.a1", 1, "지우 과장", "employee_profile")
    assert vis == {"status": "AMBIGUOUS", "hint": HINTS["AMBIGUOUS"]} and log["candidates"] == 2
    assert "E-SEL" not in json.dumps(vis)


def test_invalid_type_labels_and_backend_recheck(t):
    vis, log = q(t, "hr-sel.a3", 5, "하린 과장", "budget_line_balance")          # HR 그룹 도메인 밖
    assert vis == {"status": "INVALID_TYPE", "hint": HINTS["INVALID_TYPE"]} and log["label"] == "TYPE_NOT_PERMITTED"
    vis, log = q(t, "hr-sel.a1", 5, "하린 과장", "salary")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "UNKNOWN_TYPE"
    vis, log = q(t, "fin-sel.a1", 5, "CMT-00001", "budget_line_balance")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "KIND_MISMATCH"


def test_multi_record_type_matches_catalog_department_ordered_and_limited(tmp_path):
    t2 = Tools(tmp_path, day=1)
    vis, _ = q(t2, "fin-sel.a1", 1, "영업1팀", "department_provisional_approvals")
    assert [r["id"] for r in vis["records"]] == ["CMT-00001"]
    vis, _ = q(t2, "fin-sel.a1", 1, "개발1팀", "department_provisional_approvals")
    assert [r["id"] for r in vis["records"]] == ["CMT-00004"], "1일차 catalog 추가·DB 등록분만"
    for i, cid in enumerate(["CMT-00090", "CMT-00050", "CMT-00070", "CMT-00060", "CMT-00080", "CMT-00040"]):
        t2.stores.catalog.upsert("FIN-SEL", f"commits/{cid}", {"commit_id": cid, "department": "영업1팀"})
        t2.stores.db.add("FIN-SEL", f"FIN-SEL/commit/{cid}/status",
                         DbVersion(v=1, day=1, db_day=1, value={"status": "pending", "amount": 1000 + i}))
    vis, log = q(t2, "fin-sel.a1", 1, "영업1팀", "department_provisional_approvals")
    assert [r["id"] for r in vis["records"]] == ["CMT-00001", "CMT-00040", "CMT-00050", "CMT-00060", "CMT-00070"]
    assert vis["truncated"] and log["total"] == 7


# ─────────────────────────── entity.search ───────────────────────────
def search(t, agent, day, query):
    return t.call("entity.search", agent, day, query=query)


def test_search_is_group_scoped_tick_aware_and_discoverable_only(tmp_path):
    t1 = Tools(tmp_path / "d1", day=1)
    vis, _ = search(t1, "fin-sel.a1", 1, "영업")
    assert {"entity": "영업1팀", "kind": "department", "name": "영업1팀"} in vis["entities"]
    vis, _ = search(t1, "fin-sel.a1", 1, "営業")                                  # 다른 그룹
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]}
    vis, _ = search(t1, "fin-sel.a2", 1, "CMT")
    assert [e["entity"] for e in vis["entities"]] == ["CMT-00001", "CMT-00004"], "CMT-00002·00003은 이력에만 있어 발견되지 않는다"
    vis, _ = search(t1, "hr-sel.a4", 1, "하린")
    assert vis["entities"] == [{"entity": "E-SEL-1000", "kind": "employee", "name": "김하린"}]


def test_search_before_catalog_upsert(tmp_path):
    a = load_adapter("worldgen_mini")
    from gbg.stores import Stores
    s = Stores.from_adapter(a, card_mode="static", rounds_per_day=3)             # 1일차 사건 반영 전
    tool = next(x for x in env_tools.make_tools(s, a.domain_of()) if x.name == "entity.search")
    out = asyncio.run(tool.invoke(ToolCall("fin-sel.a1", "FIN-SEL", 0, 1, {"query": "CMT"})))
    assert [e["entity"] for e in out.result["entities"]] == ["CMT-00001"]


def test_search_ordering_and_limit(tmp_path):
    p = load_policy().model_copy(update={"search_limit": 2})
    t2 = Tools(tmp_path, day=1, policy=p)
    vis, _ = search(t2, "hr-sel.a1", 1, "E-SEL")
    assert [e["entity"] for e in vis["entities"]] == ["E-SEL-1000", "E-SEL-1001"] and vis["truncated"]


# ─────────────────────────── 실행 중 기록 ───────────────────────────
class Prober(ScriptedAgent):
    async def work(self, ctx, task):
        await ctx.call_tool("db.query", entity="営業1課", record_type="budget_line_balance")
        await ctx.call_tool("db.query", entity="하린 과장", record_type="budget_line_balance")
        await ctx.call_tool("db.query", entity="영업1팀", record_type="budget_line_balance")
        return await super().work(ctx, task)


def test_labels_go_to_obs_and_only_visible_states_to_wal(tmp_path):
    run_until(tmp_path, 5, lambda aid, g, role: Prober(aid))
    events = [json.loads(x) for x in (tmp_path / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    seen = [e["payload"] for e in events if e["type"] == "tool_result"]
    seen_text = json.dumps(seen, ensure_ascii=False)
    for hidden in ("PERMISSION_DENIED", "TYPE_NOT_PERMITTED", "KIND_MISMATCH", "/line/", "/emp/"):
        assert hidden not in seen_text, hidden
    assert {p["result"]["status"] for p in seen if p["tool"] == "db.query"} <= VISIBLE_STATES
    labels = {json.loads(x)["label"] for x in (tmp_path / "obs" / "db_lookups.jsonl").read_text(encoding="utf-8").splitlines()}
    assert {"PERMISSION_DENIED", "TYPE_NOT_PERMITTED", "HIT"} <= labels


def test_tool_definition_tokens_are_logged_as_fixed_cost(tmp_path):
    from gbg.tests.test_stage3 import auto_reply, backend, llm_runner
    llm_runner(tmp_path, backend("SCRIPTED", script=auto_reply)).run()
    windows = [json.loads(x) for x in (tmp_path / "obs" / "context_windows.jsonl").read_text(encoding="utf-8").splitlines()]
    assert windows and all(w["tool_def_tokens"] > 0 for w in windows)
    per = {}
    for w in windows:
        per.setdefault((w["agent"], w["task_id"], w["serving"]), set()).add(w["tool_def_tokens"])
    assert all(len(v) == 1 for v in per.values()), "같은 호출 경로 안에서 도구 정의 토큰은 고정"
