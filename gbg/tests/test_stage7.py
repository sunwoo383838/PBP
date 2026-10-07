"""Stage 7 채점기 수용 기준: 오라클 런 Acc_exact 100%, 오답 런 0%, 누출 검사, 게이트 합 = 전체 손실, 부트스트랩."""
import json

from gbg.benchmarks.worldgen.scoring import load_private, strata, verify
from gbg.scoring import bootstrap, checks, ledger, metrics
from gbg.tests.support import FIXTURES

PRIV = load_private(FIXTURES / "worldgen_mini")


def _events(answer_of) -> list[dict]:
    """과제마다 task_delivered + answer 사건 (답은 answer_of(gold 행))."""
    out = []
    for wid, g in PRIV.gold.items():
        te = PRIV.tasks[wid]
        out.append({"type": "task_delivered", "actor": "kernel", "day": te.day, "round": te.round,
                    "payload": {"task_id": wid, "agent": te.agent}})
        out.append({"type": "answer", "actor": f"agent:{te.agent}", "day": te.day, "round": te.round,
                    "payload": {"task_id": wid, "agent": te.agent, "answer": answer_of(g),
                                "budget": {"by_component": {"requester": {"calls": 3, "tokens": 900}}}}})
    return out


def _summary(answer_of):
    led = ledger.build(_events(answer_of), PRIV, verify, strata)
    return led, metrics.summarize(led)


def test_oracle_run_is_100_and_wrong_run_is_0():
    led, s = _summary(lambda g: g["gold"])
    assert s["headline"]["acc_exact_all"]["acc"] == 1.0 and s["headline"]["tok_per_success"] == 900
    led, s = _summary(lambda g: {k: "__not_the_answer__" for k in g["gold"]})     # 교차 정보 없이 낸 답
    assert s["headline"]["acc_exact_all"]["acc"] == 0.0 and s["headline"]["tok_per_success"] is None


def test_submit_failure_is_wrong_and_coded():
    ev = _events(lambda g: g["gold"])
    ev[1]["payload"] = {**ev[1]["payload"], "answer": None, "error": "budget_exhausted"}
    led = ledger.build(ev, PRIV, verify, strata)
    t = next(t for t in led["tasks"] if t["task_id"] == ev[1]["payload"]["task_id"])
    assert not t["exact"] and t["error"] == "E_budget"


def test_leak_check_reports_answer_only_identifiers():
    clean = {"k1": [{"role": "user", "content": "What is the budget of Dev Team 2?"}]}
    assert checks.leak(clean)["ok"]
    dirty = {"k1": [{"role": "user", "content": "see FR-00623 and FIN-SEL/line/Dev Team 2/remaining"}]}
    r = checks.leak(dirty)
    assert not r["ok"] and {h["kind"] for h in r["hits"]} == {"fragment_id", "physical_key"}
    assert checks.leak(dirty, agent_keys=set())["n"] == 1, "경계 모듈 입력의 DB 키(버전 표시)는 허용"
    assert not checks.card_leak({"k": [{"content": "ask fin-sel.a3"}]},
                                [{"type": "llm_call", "payload": {"key": "k", "component": "requester"}}])["ok"]


def test_gate_sum_equals_total_loss():
    needs = [{"gate": g, "unreachable": False} for g in
             ["ok", "L_request", "L_reach", "L_observe.search", "L_select", "L_respond", "L_observe.window", "E_budget", "unjudged", "ok"]]
    t = metrics.gate_table(needs)
    failed = sum(v["failed"] for k, v in t["stages"].items() if k != "ok") + sum(t["errors"].values())
    assert failed == t["lost"] == 7 and t["stages"]["ok"]["reached"] == 2 and t["unjudged"] == 1
    assert t["stages"]["L_observe"]["reached"] == 6 and t["stages"]["L_observe"]["failed"] == 2
    assert t["stages"]["L_respond"]["reached"] == 4 and t["stages"]["L_select"]["reached"] == 3
    assert t["L_observe_detail"] == {"L_observe.search": 1, "L_observe.window": 1}


def test_paired_bootstrap_is_deterministic_and_judges_margins():
    rows = [{"world": w, "task_id": f"T{i}", "day": 1 + i % 10, "condition": c, "exact": (c == "b" and i % 2 == 0)}
            for w in ("s1", "s2") for i in range(20) for c in ("a", "b")]
    r1, r2 = bootstrap.paired(rows, "a", "b"), bootstrap.paired(rows, "a", "b")
    assert r1 == r2 and r1["n"] == 40 and r1["diff"] == 0.5 and r1["ci95"][0] > 0
    assert bootstrap.noninferior(r1, 0.05) and not bootstrap.equivalent(r1, 0.05)
