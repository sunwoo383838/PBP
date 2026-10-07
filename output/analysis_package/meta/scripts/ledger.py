"""원장 (채점기, 오프라인): 실행 하나(WAL + 캐시 프롬프트)와 정답 원장에서 과제 원장과 need 원장을 만든다.

    과제 원장  과제마다 제출 답, 판정(verify), 오류(형식·예산 등), 예산 요약(호출·토큰·처음 걸린 상한·응답자 단계 상한),
              구성요소별 호출·토큰, 원리상 풀 수 없음 표시(reachability), 층화 속성
    need 원장  원격 need마다 전달 판정(delivery.py)과 손실 고리(gates.py: request·reach·observe·respond·select, 전달되면
              ok). 과제가 제출 실패·예산 소진이면 고리 대신 그 오류 코드(E_format, E_budget, E_error)를 단다 (고리와 따로
              센다). 판정할 조각이 없는 need(DB·규정만)는 unjudged로 집계에서 뺀다
    과제 결과  outcome: correct / use(모든 원격 need가 ok·unjudged인데 오답) / lost(어떤 need가 끊김) / 오류 코드
벤치마크 고유 부분(verify, 층화 속성, private 원장)은 호출자가 넘긴다.
"""
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

from .delivery import need_delivery
from .gates import need_gates
from .reachability import unreachable
from .proposals import proposal_uptake
from .redirects import redirect_metrics


def load_events(run_dir: Path) -> list[dict]:
    return [json.loads(x) for x in (Path(run_dir) / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines() if x]


def load_prompts(cache: Path | None, keys: set[str]) -> dict:
    """llm_call key → 요청 messages (응답 캐시에서)."""
    if cache is None or not Path(cache).exists() or not keys:
        return {}
    db = sqlite3.connect(cache)
    out = {}
    for k in keys:
        row = db.execute("select request from responses where key = ?", (k,)).fetchone()
        if row:
            out[k] = json.loads(row[0]).get("messages", [])
    return out


def _error_code(ans: dict | None) -> str | None:
    if ans is None:
        return "E_no_answer"
    err = ans.get("error")
    if err is None:
        return None
    if err.startswith("agent_exception"):                                  # 하네스 예외: 오답이 아니라 하네스 실패
        return "E_harness"
    if "budget" in err:
        return "E_budget"
    if "format" in err:
        return "E_format"
    return "E_error"


def build(events: list[dict], priv, verify, strata, prompts: dict | None = None) -> dict:
    """priv: tasks·gold·fragments·names를 가진 객체. verify(task, answer, gold_row), strata(gold_row)."""
    by_task: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        t = e["payload"].get("task_id")
        if t in priv.gold:
            by_task[t].append(e)
    delivery = need_delivery(events, {w: priv.gold[w] for w in by_task}, priv.fragments, names=priv.names,
                             computed=getattr(priv, "computed", None))["needs"]
    unreach = unreachable([priv.gold[w] for w in by_task])
    tasks, needs = [], []
    for wid in sorted(by_task):
        es, g = by_task[wid], priv.gold[wid]
        ans = next((e["payload"] for e in es if e["type"] == "answer"), None)
        answer = (ans or {}).get("answer") if ans and ans.get("error") is None else None
        v = verify(priv.tasks[wid], answer, g)
        llm = [e["payload"] for e in es if e["type"] == "llm_call"]
        err = _error_code(ans)
        budget = (ans or {}).get("budget") or {}                          # 커널의 과제 예산 집계 (토큰 규칙의 원본)
        comp = {k: {"calls": v.get("calls", 0), "tokens": v.get("tokens", 0)} for k, v in (budget.get("by_component") or {}).items()}
        if not comp:                                                       # 예산 집계가 없으면 llm_call 사건 수만
            comp = defaultdict(lambda: {"calls": 0, "tokens": 0})
            for x in llm:
                comp[x.get("component", "?")]["calls"] += 1
        tasks.append({"task_id": wid, "day": g.get("day"), "exact": v["exact"], "slots": v["slots"], "error": err,
                      "unreachable": wid in unreach, "unreachable_why": unreach.get(wid, []),
                      "calls": sum(v_["calls"] for v_ in comp.values()), "tokens": sum(v_["tokens"] for v_ in comp.values()),
                      "components": {k: dict(v_) for k, v_ in comp.items()},
                      "exhausted_by": budget.get("exhausted_by"), "responder_step_caps": budget.get("responder_step_cap", 0),
                      **strata(g)})
        rows = [r for r in delivery if r["task_id"] == wid]
        tasks[-1]["redirects"] = redirect_metrics(es, g, priv.fragments, priv.names, rows)   # 소관 밖 안내·항목 시점
        tasks[-1]["proposals"] = proposal_uptake(es, wid, answer)            # 접수부 제안 값을 따랐는가
        gates = {x["need"]: x for x in need_gates(es, g, priv.fragments, rows, prompts or {}, None, priv.names)}
        n0 = len(needs)
        for r in rows:
            gt = gates.get(r["need"], {})
            if not r["scored"]:                                            # 판정할 조각이 없는 need (DB·규정만): 게이트 없음
                gate = "unjudged"
            elif err and gt.get("gate") != "ok":
                gate = err
            else:
                gate = gt.get("gate")
            needs.append({"task_id": wid, "need": r["need"], "class": r["class"], "c_ops": r["c_ops"], "domain": r["domain"],
                          "scored": r["scored"], "delivered": r["delivered"], "gate": gate,
                          "gate_detail": {k: gt[k] for k in gt if k not in ("need", "group", "gate")},
                          "unreachable": wid in unreach, "frags": r["frags"]})
        mine = needs[n0:]                                                  # 과제 단위 결과: use = 모든 원격 need가 충족됐는데 오답
        tasks[-1]["outcome"] = err or ("correct" if v["exact"] else "use" if all(n["gate"] in ("ok", "unjudged") for n in mine)
                                       else "lost")
    return {"tasks": tasks, "needs": needs}
