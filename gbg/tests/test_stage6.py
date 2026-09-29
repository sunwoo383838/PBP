"""Stage 6: 참조 행과 사다리 중간 단계는 조건 설정의 한 항목이고 Stage 5 코드 위의 플래그로만 동작한다.

실행 대상: 본 실행 direct·routing·ingress·i_e·full_load, 기준 셀에서만 ingress_read·ingress_sel·gateway_rag.
후속(코드만, 실행 거부): ingress_no_requery, egress_no_history, retrieval_oracle. 조건에서 뺀 reveal_holders·
responder_session: ephemeral 플래그의 코드도 남아 있으므로 테스트 전용 조건으로 검사한다.
retrieval_oracle 외 조건에서 oracle_evidence가 마운트되면 실행을 거부한다.
"""
import json
import re

import pytest

from gbg.contracts.conditions import ConditionSet, ConfigError
from gbg.tests import test_stage3 as T
from gbg.tests.support import FIXTURES
from gbg.tests.test_stage5 import FRAGS, GOLD, _recall, _tools, oracle, run

DEFERRED = {"ingress_no_requery", "egress_no_history", "retrieval_oracle"}


def with_conditions(**extra) -> ConditionSet:
    """설정 + 테스트 전용 조건. 후속 조건은 blocked를 풀어 코드를 검사한다."""
    base = {n: (c.model_copy(update={"blocked": None}) if n in DEFERRED else c) for n, c in T.CONDITIONS.items()}
    return ConditionSet({**base, **extra}, T.CONDITIONS.defaults)


def _flag(name: str, **update):
    c = T.CONDITIONS[name]
    return c.model_copy(update={"ingress": c.ingress.model_copy(update=update)} if update else {})


def _diff(cond, base):
    c, b = T.CONDITIONS[cond].model_dump(), T.CONDITIONS[base].model_dump()
    out = {}
    for k in c:
        if isinstance(c[k], dict) and isinstance(b[k], dict):
            out.update({f"{k}.{x}": c[k][x] for x in c[k] if c[k][x] != b[k].get(x)})
        elif c[k] != b[k]:
            out[k] = c[k]
    return out


def test_each_condition_is_one_entry_and_differs_by_flags_only():
    assert _diff("gateway_rag", "ingress") == {"ingress.internal_query": False, "ingress.requery": False}
    assert _diff("ingress_sel", "ingress") == {"ingress.requery": False, "ingress.boundary_state": False,
                                               "ingress.version_marks": False}
    assert _diff("ingress_read", "routing") == {"ingress.deliver": "read"}
    assert {k: v for k, v in _diff("ingress_no_requery", "ingress").items() if k != "blocked"} == {"ingress.requery": False}
    assert {k: v for k, v in _diff("egress_no_history", "i_e").items() if k != "blocked"} == {"egress.history": False}
    assert {k: v for k, v in _diff("retrieval_oracle", "ingress").items() if k != "blocked"} == {"ingress.evidence": "oracle"}
    assert all(T.CONDITIONS[n].blocked for n in DEFERRED), "후속: 코드만 두고 실행하지 않는다"


# ─────────────────────────── 기준 셀에서만 도는 조건 ───────────────────────────
def test_gateway_rag_answers_from_group_records_without_asking_members(tmp_path):
    _, ev = run(tmp_path, "gateway_rag")
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"].get("stage") == "ingress"]
    assert dec and all(d["action"] == "coordinate" for d in dec)
    assert not any(e["type"] == "message" and e["actor"].startswith("boundary:") and e["payload"]["kind"] == "request"
                   for e in ev), "Ingress의 6·9단계 생략"
    hit, n = _recall(ev)
    assert hit == n, "스크립트 조립자는 증거를 모두 싣는다: 떠난 처리자의 조각도 그룹 기록으로 도달"


def test_ingress_read_attaches_records_to_forwarded_replies(tmp_path):
    _, ev = run(tmp_path, "ingress_read", max_day=1)
    got = [e["payload"]["response"]["answer"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "response"
           and e["actor"].startswith("boundary:")]
    assert got and all(a.startswith("[Reply 1] ") and "\n\n[Group records]\n[E1] " in a for a in got)


def test_ingress_sel_assembles_without_state_versions_or_requery(tmp_path):
    prompts = []

    def script(req):
        if "answer" in _tools(req):
            prompts.append(req["messages"][1]["content"])
        return oracle(req, assemble_missing=[["x"]] if "answer" in _tools(req) else None)
    _, ev = run(tmp_path, "ingress_sel", script=script)
    assert prompts and not any("Database versions:" in p or "Earlier exchanges" in p for p in prompts)
    assert all(d["requery"] == [] for d in (e["payload"] for e in ev if e["type"] == "boundary_decision"
                                              and e["payload"].get("action") == "select"))


# ─────────────────────────── 후속·뺀 조건의 코드 (테스트 전용 조건으로) ───────────────────────────
def test_deferred_conditions_are_refused_by_the_runner(tmp_path):
    for name in DEFERRED:
        with pytest.raises(ConfigError, match=name):
            run(tmp_path / name, name)


def test_ingress_no_requery_never_requeries(tmp_path):
    def script(req):
        return oracle(req, assemble_missing=[["settlement day"]] * 20 if "answer" in _tools(req) else None)
    _, ev = run(tmp_path, "ingress_no_requery", script=script, conditions=with_conditions())
    dec = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"].get("action") == "select"]
    assert dec and all(d["requery"] == [] for d in dec)


def test_egress_no_history_gives_requester_context_instead_of_egress_log(tmp_path):
    seen = []

    def script(req):
        if "dispatch" in _tools(req):
            seen.append(req["messages"][1]["content"])
        return oracle(req)
    run(tmp_path, "egress_no_history", script=script, max_day=1, conditions=with_conditions())
    assert seen and all("The requester's own work and records:" in u and "Related records of this desk" not in u for u in seen)
    assert any("requester work:" in u for u in seen)


def test_reveal_holders_code_lists_holders_for_direct_asks(tmp_path):
    """조건에서 뺐지만 코드가 남은 reveal_holders: 담당자 목록만 돌려주고 요청자는 ask_agent로 직접 묻는다."""
    def script(req):
        tools, msgs = _tools(req), req["messages"]
        if "submit" in tools and "ask_agent" in tools and len(msgs) > 2:
            last = msgs[-1]["content"] or ""
            ids = re.findall(r"agent-[0-9a-f]{10}", last)
            if ids and "Members who may hold this" in last:
                return T.mk([("ask_agent", {"agent_id": i, "question": "What do you hold on this?"}) for i in ids])
        return oracle(req)
    conds = with_conditions(reveal=_flag("routing", reveal_holders=True))
    _, ev = run(tmp_path, "reveal", script=script, conditions=conds)
    rev = [e["payload"] for e in ev if e["type"] == "boundary_decision" and e["payload"].get("revealed")]
    w5 = next(d for d in rev if d["task_id"] == "W-005")
    assert "fin-sel.a2" in w5["revealed"], "이탈자도 목록에 남는다"
    direct = [e["payload"] for e in ev if e["type"] == "message" and e["payload"]["kind"] == "request"
              and e["actor"].startswith("agent:") and e["payload"].get("to_agent") and e["payload"].get("serving") is None]
    asked_a2 = [m for m in direct if m["task_id"] == "W-005" and m["to_agent"] == "fin-sel.a2"]
    assert asked_a2 and not asked_a2[0]["delivered"], "목록에 있어도 닿지 못한다"


def test_retrieval_oracle_code_uses_exported_fragments_and_mount_is_guarded(tmp_path):
    from gbg.cli.export_oracle import export
    mount = tmp_path / "oracle_evidence"
    assert export(FIXTURES / "worldgen_mini", mount) == len(GOLD)
    w3 = json.loads((mount / "W-003.json").read_text(encoding="utf-8"))
    assert {x["text"] for x in w3["FIN-SEL"]} == {FRAGS["FR-C2"]["text"], FRAGS["FR-C3"]["text"]}
    conds = with_conditions()
    with pytest.raises(ConfigError, match="oracle_evidence"):
        run(tmp_path / "x", "ingress", oracle_evidence=mount)             # 다른 조건에 마운트: 거부
    with pytest.raises(ConfigError, match="oracle_evidence"):
        run(tmp_path / "y", "retrieval_oracle", conditions=conds)         # 마운트 없이: 거부
    prompts = []

    def script(req):
        if "answer" in _tools(req):
            prompts.append(req["messages"][1]["content"])
        return oracle(req)
    _, ev = run(tmp_path / "run", "retrieval_oracle", script=script, oracle_evidence=mount, conditions=conds)
    assert any(FRAGS["FR-C3"]["text"] in p for p in prompts), "H2 조각도 증거 블록에 (정답 조각으로 대체)"
    hit, n = _recall(ev)
    assert hit == n
