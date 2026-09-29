"""지표 (채점기, 오프라인). 원장(ledger.build)에서 조건 하나의 헤드라인·설명·층화 지표를 낸다.

    헤드라인  Acc_exact(원리상 풀 수 있는 과제 기준, 전체 기준 병기), 과제당 토큰, tok/success(실패 포함 전체 토큰 ÷ 성공 수)
    설명      슬롯 정답률, need 전달률, 게이트 분포와 게이트별 도달·조건부 실패율, 호출 분포(p50·p95), 예산 소진·응답자
              단계 상한 비율, 제출 실패
    층화      등급(A–D), C_ops, 템플릿, 보유자 수(max_holders), 관여 그룹 수
게이트 순서: L_req → L_route → L_sel(window·answer·search·assembly) → L_state → L_use. 오류 코드(E_*)는 따로 센다.
"""
from collections import Counter, defaultdict

from .redirects import summarize as summarize_redirects

GATE_ORDER = ["L_req", "L_route", "L_sel", "L_state", "L_use", "ok"]


def _stage(gate: str | None) -> str | None:
    if gate is None:
        return None
    return "L_sel" if gate.startswith("L_sel") else gate


def _pct(xs: list[float], q: float):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * q))] if xs else None


def _acc(rows: list[dict]) -> dict:
    n = len(rows)
    k = sum(r["exact"] for r in rows)
    return {"n": n, "exact": k, "acc": round(k / n, 4) if n else None}


def gate_table(needs: list[dict]) -> dict:
    """게이트별 실패 수, 도달 수(그 게이트까지 온 need), 조건부 실패율. 오류 코드는 따로."""
    unjudged = sum(r["gate"] == "unjudged" for r in needs)
    needs = [r for r in needs if r["gate"] != "unjudged"]
    stages = [_stage(r["gate"]) for r in needs]
    errors = Counter(s for s in stages if s and s.startswith("E_"))
    gated = [s for s in stages if s in GATE_ORDER]
    out, remaining = {}, len(gated)
    for gname in GATE_ORDER[:-1]:
        fail = sum(s == gname for s in gated)
        out[gname] = {"reached": remaining, "failed": fail, "conditional_failure": round(fail / remaining, 4) if remaining else None}
        remaining -= fail
    out["ok"] = {"reached": remaining}
    detail = Counter(r["gate"] for r in needs if r["gate"] and r["gate"].startswith("L_sel"))
    return {"stages": out, "L_sel_detail": dict(detail), "errors": dict(errors), "needs": len(needs), "unjudged": unjudged,
            "lost": sum(s != "ok" for s in stages if s is not None)}


def summarize(ledger: dict) -> dict:
    tasks, needs = ledger["tasks"], ledger["needs"]
    reach = [t for t in tasks if not t["unreachable"]]
    tokens = sum(t["tokens"] for t in tasks)
    success = sum(t["exact"] for t in tasks)
    slots = [v for t in tasks for v in t["slots"].values()]
    scored = [r for r in needs if r["scored"] and not r["unreachable"]]
    strata = {}
    for key in ("class", "c_ops", "template", "max_holders", "n_groups"):
        by = defaultdict(list)
        for t in reach:
            by[str(t.get(key))].append(t)
        strata[key] = {k: _acc(v) for k, v in sorted(by.items())}
    calls = [t["calls"] for t in tasks]
    return {
        "headline": {"acc_exact": _acc(reach), "acc_exact_all": _acc(tasks), "unreachable_tasks": len(tasks) - len(reach),
                     "tokens_per_task": round(tokens / len(tasks)) if tasks else None,
                     "tok_per_success": round(tokens / success) if success else None},
        "slot_acc": round(sum(slots) / len(slots), 4) if slots else None,
        "need_delivery": round(sum(r["delivered"] for r in scored) / len(scored), 4) if scored else None,
        "gates": gate_table([r for r in needs if not r["unreachable"]]),
        "calls": {"mean": round(sum(calls) / len(calls), 1) if calls else None, "p50": _pct(calls, .5), "p95": _pct(calls, .95),
                  "max": max(calls, default=None)},
        "budget": {"exhausted": sum(bool(t["exhausted_by"]) for t in tasks),
                   "exhausted_rate": round(sum(bool(t["exhausted_by"]) for t in tasks) / len(tasks), 4) if tasks else None,
                   "tasks_with_responder_step_cap": sum(t["responder_step_caps"] > 0 for t in tasks),
                   "submit_failures": sum(t["error"] is not None for t in tasks),
                   "errors": dict(Counter(t["error"] for t in tasks if t["error"]))},
        "components": {c: {"calls": sum(t["components"].get(c, {}).get("calls", 0) for t in tasks),
                           "tokens": sum(t["components"].get(c, {}).get("tokens", 0) for t in tasks)}
                       for c in sorted({c for t in tasks for c in t["components"]})},
        "strata": strata,
        "redirects": summarize_redirects([t["redirects"] for t in tasks if "redirects" in t]),
    }
