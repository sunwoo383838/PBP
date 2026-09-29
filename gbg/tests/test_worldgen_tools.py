"""worldgen 구조화 조회 도구: db.query(entity, record_type), entity.search.

- 스키마에는 역할이 읽을 수 있는 record type과 의미만 있고 physical key·레코드 목록은 없다.
- 스키마와 실행 중 권한은 같은 role_policy에서 나오고, 백엔드가 권한을 다시 검사한다.
- 에이전트에게는 HIT / NOT_FOUND / AMBIGUOUS / INVALID_TYPE만 보이고, 원래 라벨은 obs에만 남는다.
- NOT_FOUND·AMBIGUOUS에는 후보 없이 일반 힌트만 준다.
- entity.search는 자기 그룹, 현재 tick, 발견성(등록된 레코드만)을 지킨다.
- 모든 조건의 에이전트가 같은 역할이면 같은 환경 도구를 받고, 도구 정의 토큰은 고정비로 기록된다.
"""
import asyncio
import json
from pathlib import Path

import pytest

from gbg.benchmarks.worldgen import env_tools
from gbg.benchmarks.worldgen.records import HINTS, load_policy
from gbg.contracts.events import Event
from gbg.contracts.schemas import DbVersion
from gbg.kernel.tools import ToolCall
from gbg.stores import Stores
from gbg.tests.support import load_adapter

ROOT = Path(__file__).resolve().parents[2]
VISIBLE_STATES = {"HIT", "NOT_FOUND", "AMBIGUOUS", "INVALID_TYPE"}


def stores_at(adapter, day):
    """픽스처의 db_write 세계 이벤트를 day까지 반영한 저장소."""
    s = Stores.from_adapter(adapter, card_mode="static", rounds_per_day=3)
    seq = 0
    for te in adapter.events():
        if te.kind == "world" and te.day <= day:
            seq += 1
            if te.action == "db_write":
                s.apply(Event(seq=seq, day=te.day, round=te.round, type="world_update", actor="kernel",
                              payload={"eid": te.eid, "action": "db_write", "group": te.group, "agent": None, "data": te.payload}))
            elif te.action in ("agent_join", "agent_leave"):
                s.apply(Event(seq=seq, day=te.day, round=te.round, type=te.action, actor="kernel",
                              payload={"agent": te.agent, "group": te.group, "role": te.payload.get("role", ""),
                                       "from": te.payload.get("from"), "handover_notes": [], "entities": []}))
    return s


class Tools:
    def __init__(self, day=5, adapter=None, policy=None):
        self.adapter = adapter or load_adapter("worldgen_mini")
        self.stores = stores_at(self.adapter, day)
        kw = {"policy": policy} if policy else {}
        self.tools = {t.name: t for t in env_tools.make_tools(
            self.stores, {g: s.aliases for g, s in self.adapter._snap.items()}, **kw)}

    def call(self, tool, agent, day, **args):
        group = self.stores.members[agent][0]
        out = asyncio.run(self.tools[tool].invoke(ToolCall(agent, group, day, 1, args)))
        (_, log), = out.obs
        return out.result, log


def q(t, agent, day, entity, rtype):
    return t.call("db.query", agent, day, entity=entity, record_type=rtype)


# ─────────────────────────── 스키마 ───────────────────────────
def test_schema_lists_role_types_and_meanings_only():
    p = load_policy()
    for role, types in p.roles.items():
        spec = next(s for s in env_tools.role_specs(role) if s.name == "db.query")
        rt = spec.parameters["properties"]["record_type"]
        assert rt["enum"] == types
        for t in types:
            assert p.record_types[t].description in rt["description"]
    dumped = json.dumps([s.model_dump() for r in p.roles for s in env_tools.role_specs(r)], ensure_ascii=False)
    for leak in ("{group}", "{entity}", "/emp/", "/line/", "/commit/", "FIN-SEL", "HR-SEL", "E-SEL-", "CMT-"):
        assert leak not in dumped, f"스키마에 내부 key나 레코드가 보인다: {leak}"
    assert env_tools.role_specs("records")[0].parameters["properties"]["record_type"]["enum"] == \
        ["employee_profile", "employee_transfer"]


def test_schema_and_authorization_come_from_same_policy():
    p = load_policy().model_copy(deep=True)
    p.roles["budgeting"] = ["department_provisional_approvals"]                 # 정책 한 곳만 바꾼다
    spec = next(s for s in env_tools.role_specs("budgeting", p) if s.name == "db.query")
    assert spec.parameters["properties"]["record_type"]["enum"] == ["department_provisional_approvals"]
    t = Tools(policy=p)
    vis, log = q(t, "fin-sel.a1", 3, "영업1팀", "budget_line_balance")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "TYPE_NOT_PERMITTED"


def test_same_env_tools_across_conditions():
    from gbg.contracts.conditions import load_conditions
    from gbg.llm.agent_loop import AgentRuntime, LLMAgent, REPLY_TOOL
    conds = load_conditions(ROOT / "configs" / "conditions.yaml")
    a = load_adapter("worldgen_mini")
    per_cond = {}
    for name, c in conds.items():
        agent = LLMAgent("fin-sel.a1", AgentRuntime(c, a.role_tools, None, 6, 1))
        per_cond[name] = [t for t in agent.tool_schemas("budgeting", REPLY_TOOL)
                          if t["function"]["name"] in {"db.query", "entity.search", "rulebook.read"}]
    assert len({json.dumps(v, sort_keys=True) for v in per_cond.values()}) == 1
    assert len(per_cond["direct"]) == 3


# ─────────────────────────── 조회 ───────────────────────────
def test_hit_by_id_and_alias_returns_latest_registered_version_without_key():
    t = Tools()
    vis, log = q(t, "fin-sel.a2", 1, "개발1팀", "budget_line_balance")
    assert vis["status"] == "HIT" and vis["record"] == 2_874_300 and log["version"] == 1 and log["newer_pending"]
    vis, _ = q(t, "fin-sel.a2", 2, "개발1팀", "budget_line_balance")
    assert vis["record"] == 2_417_900
    for name in ("E-SEL-1000", "하린 과장", "김하린", "  김하린 ", "e-sel-1000"):
        vis, log = q(t, "hr-sel.a1", 1, name, "employee_profile")
        assert vis["status"] == "HIT" and vis["entity"] == "E-SEL-1000" and vis["record"]["dept"] == "영업1팀", name
    assert set(vis) == {"status", "entity", "record_type", "registered_day", "record"}
    assert "HR-SEL/" not in json.dumps(vis, ensure_ascii=False) and log["keys"] == ["HR-SEL/emp/E-SEL-1000/profile"]


def test_not_yet_available_looks_like_not_found():
    t = Tools()
    vis, log = q(t, "hr-sel.a1", 1, "도윤 대리", "employee_transfer")           # 0일차 승인, 2일차 등록
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]} and log["label"] == "NOT_YET_AVAILABLE"
    vis, log = q(t, "hr-sel.a1", 2, "도윤 대리", "employee_transfer")
    assert vis["status"] == "HIT" and vis["record"]["to"] == "영업1팀"


def test_other_group_entity_looks_like_not_found():
    t = Tools()
    vis, log = q(t, "fin-sel.a1", 3, "営業1課", "budget_line_balance")
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]} and log["label"] == "PERMISSION_DENIED"
    vis, _ = q(t, "fin-tyo.a1", 3, "営業1課", "budget_line_balance")
    assert vis["status"] == "HIT"


def test_no_record_and_unknown_name():
    t = Tools()
    vis, log = q(t, "hr-sel.a1", 3, "하린 과장", "employee_transfer")
    assert vis["status"] == "NOT_FOUND" and log["label"] == "NO_RECORD"
    vis, log = q(t, "hr-sel.a1", 3, "없는 사람", "employee_profile")
    assert vis["status"] == "NOT_FOUND" and log["label"] == "NOT_FOUND"
    vis, log = q(t, "fin-sel.a3", 5, "CMT-00002", "provisional_approval")      # 이력에만 있는 건: DB로는 없다
    assert vis["status"] == "NOT_FOUND"


def test_ambiguous_gives_no_candidates():
    a = load_adapter("worldgen_mini")
    a._snap["HR-SEL"].aliases["E-SEL-1002"].append("지우 과장")                # 두 직원이 같은 별칭
    t = Tools(adapter=a)
    vis, log = q(t, "hr-sel.a1", 1, "지우 과장", "employee_profile")
    assert vis == {"status": "AMBIGUOUS", "hint": HINTS["AMBIGUOUS"]} and log["candidates"] == 2
    assert "E-SEL" not in json.dumps(vis)
    vis, _ = q(t, "hr-sel.a1", 1, "E-SEL-1003", "employee_profile")
    assert vis["status"] == "HIT"


def test_invalid_type_labels_and_backend_recheck():
    t = Tools()
    vis, log = q(t, "hr-sel.a3", 3, "하린 과장", "employee_transfer")           # 급여 역할은 스키마에 없는 유형
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "TYPE_NOT_PERMITTED"
    vis, log = q(t, "hr-sel.a1", 3, "하린 과장", "salary")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "UNKNOWN_TYPE"
    vis, log = q(t, "hr-sel.a1", 3, "영업1팀", "employee_profile")
    assert vis["status"] == "INVALID_TYPE" and log["label"] == "KIND_MISMATCH"
    assert set(vis) == {"status", "hint"}


def test_multi_record_type_is_ordered_and_limited():
    t = Tools()
    vis, log = q(t, "fin-sel.a1", 2, "영업1팀", "department_provisional_approvals")   # 2일차 확정, 3일차 등록
    assert vis["status"] == "NOT_FOUND" and log["label"] == "NOT_YET_AVAILABLE"
    vis, _ = q(t, "fin-sel.a1", 3, "영업1팀", "department_provisional_approvals")
    assert [r["id"] for r in vis["records"]] == ["CMT-00001"] and not vis["truncated"]
    for i, cid in enumerate(["CMT-00090", "CMT-00050", "CMT-00070", "CMT-00060", "CMT-00080", "CMT-00040"]):
        t.stores.db.add("FIN-SEL", f"FIN-SEL/commit/{cid}/status",
                        DbVersion(v=1, day=1, db_day=1, value={"status": "pending", "amount": 1000 + i, "dept": "영업1팀"}))
    vis, log = q(t, "fin-sel.a1", 3, "영업1팀", "department_provisional_approvals")
    assert [r["id"] for r in vis["records"]] == ["CMT-00001", "CMT-00040", "CMT-00050", "CMT-00060", "CMT-00070"]
    assert vis["truncated"] and log["total"] == 7


# ─────────────────────────── entity.search ───────────────────────────
def search(t, agent, day, query):
    return t.call("entity.search", agent, day, query=query)


def test_search_is_group_scoped_tick_aware_and_discoverable_only():
    t = Tools()
    vis, _ = search(t, "fin-sel.a1", 1, "영업")
    assert vis["entities"] == [{"entity": "영업1팀", "kind": "department", "name": "영업1팀"}]
    vis, log = search(t, "fin-sel.a1", 1, "営業")                              # 다른 그룹
    assert vis == {"status": "NOT_FOUND", "hint": HINTS["NOT_FOUND"]}
    vis, _ = search(t, "fin-sel.a3", 2, "CMT")                                 # 아직 등록 전
    assert vis["status"] == "NOT_FOUND"
    vis, _ = search(t, "fin-sel.a3", 3, "CMT")
    assert [e["entity"] for e in vis["entities"]] == ["CMT-00001"], "CMT-00002는 이력에만 있어 발견되지 않는다"
    vis, _ = search(t, "hr-sel.a3", 3, "영업1팀")                              # 급여 역할은 부서 레코드를 못 읽음
    assert vis["status"] == "NOT_FOUND"
    vis, _ = search(t, "hr-sel.a1", 1, "하린")
    assert vis["entities"] == [{"entity": "E-SEL-1000", "kind": "employee", "name": "김하린"}]


def test_search_ordering_and_limit():
    p = load_policy().model_copy(update={"search_limit": 2})
    t = Tools(policy=p)
    vis, _ = search(t, "hr-sel.a1", 1, "E-SEL")
    assert [e["entity"] for e in vis["entities"]] == ["E-SEL-1000", "E-SEL-1001"] and vis["truncated"]


# ─────────────────────────── 실행 중 기록 ───────────────────────────
def test_labels_go_to_obs_and_only_visible_states_to_wal(tmp_path):
    from gbg.agents.scripted import ScriptedAgent
    from gbg.contracts.access import load_access
    from gbg.contracts.conditions import load_conditions
    from gbg.kernel.runner import Runner
    from gbg.kernel.tools import ToolRegistry

    class Prober(ScriptedAgent):
        async def work(self, ctx, task):
            await ctx.call_tool("db.query", entity="営業1課", record_type="budget_line_balance")
            await ctx.call_tool("db.query", entity="도윤 대리", record_type="employee_transfer")
            return await super().work(ctx, task)

    conds = load_conditions(ROOT / "configs" / "conditions.yaml")
    access = load_access(ROOT / "configs" / "access.yaml", conds)
    a = load_adapter("worldgen_mini")
    Runner(a, condition="direct", seed=7, run_dir=tmp_path, conditions=conds, access=access,
           tools=ToolRegistry(access), env_tools=a.make_tools,
           agent_factory=lambda aid, g, role: Prober(aid)).run()
    events = [json.loads(x) for x in (tmp_path / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    seen = [e["payload"] for e in events if e["type"] == "tool_result"]               # 에이전트가 받은 도구 결과
    seen_text = json.dumps(seen, ensure_ascii=False)
    for hidden in ("PERMISSION_DENIED", "NOT_YET_AVAILABLE", "TYPE_NOT_PERMITTED", "/line/", "/emp/"):
        assert hidden not in seen_text, hidden
    states = {p["result"]["status"] for p in seen if p["tool"] == "db.query"}
    assert states <= VISIBLE_STATES and "HIT" in states
    labels = {json.loads(x)["label"] for x in (tmp_path / "obs" / "db_lookups.jsonl").read_text(encoding="utf-8").splitlines()}
    assert {"PERMISSION_DENIED", "TYPE_NOT_PERMITTED", "NOT_YET_AVAILABLE", "HIT"} <= labels


def test_tool_definition_tokens_are_logged_as_fixed_cost(tmp_path):
    from gbg.tests.test_stage3 import auto_reply, backend, llm_runner
    llm_runner(tmp_path, backend("SCRIPTED", script=auto_reply)).run()
    windows = [json.loads(x) for x in (tmp_path / "obs" / "context_windows.jsonl").read_text(encoding="utf-8").splitlines()]
    assert windows and all(w["tool_def_tokens"] > 0 for w in windows)
    per_agent = {}
    for w in windows:
        per_agent.setdefault((w["agent"], w["task_id"]), set()).add(w["tool_def_tokens"])
    assert all(len(v) == 1 for v in per_agent.values()), "같은 호출 경로 안에서 도구 정의 토큰은 고정"
