"""외부 분석용 패키지: /root/project/g2g/output/analysis_package/
  tables/  runs.csv, tasks.csv, llm_calls.csv.gz, gateway_decisions.csv, messages.csv.gz, retrievals.csv.gz, batches.csv
  agg/     결과 요약 표(조건·셀·모델·유형·템플릿·일자 창·비용)
  logs/    런마다 WAL(events.jsonl.gz)과 obs(gateway·messages·retrievals·batches·llm .jsonl.gz)
  meta/    설정·동결 커밋·변경 이력·시나리오(정답 원장·과제)·채점 검토·보고서
"""
import csv, gzip, json, shutil, sys, statistics as st, datetime
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0, "/root/project/g2g_main/code")
from gbg.benchmarks.worldgen.scoring import load_private, verify
from gbg.scoring.reachability import unreachable

M = Path("/root/project/g2g_main"); OUT = Path("/root/project/g2g/output/analysis_package")
for d in ("tables", "agg", "logs", "meta/scenarios"): (OUT / d).mkdir(parents=True, exist_ok=True)
PRICE = {"qwen3.5-27b": (0.26, 2.60), "qwen3.5-9b": (0.10, 0.15), "deepseek-v4-flash": (0.09, 0.18)}   # $/M in, out
TPD = {"base": 10, "R1": 5, "D3": 6, "R3": 15}
NG = {"base": 10, "R1": 5, "D3": 6, "R3": 15}

def runs():
    for p in sorted(M.glob("runs/*/*/s*")):
        yield p, "main", "base", p.parts[-3], p.parts[-2], p.name, 15, M / "scenarios" / f"D5_{p.name}_T45", "code"
    for p in sorted(M.glob("runs_g/*/*/s*")):
        yield p, "gcell", p.parts[-3], "qwen3.5-27b", p.parts[-2], p.name, 10, next((M / "scenarios_g" / p.parts[-3]).glob(f"D*_{p.name}_T45")), "code"
    for p in sorted(M.glob("runs_appx/*/s*")):
        yield p, "appendix", "base", "qwen3.5-27b", p.parts[-2], p.name, 10, M / "scenarios" / f"D5_{p.name}_T45", "code_appx"

def W(name, header, rows, gz=False):
    path = OUT / "tables" / (name + (".gz" if gz else ""))
    f = gzip.open(path, "wt", newline="", encoding="utf-8") if gz else open(path, "w", newline="", encoding="utf-8")
    with f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

pv = {}
R_runs, R_tasks, R_llm, R_gw, R_msg, R_ret, R_bat = [], [], [], [], [], [], []
for run, exp, cell, model, cond, seed, cap, sc, code in runs():
    rid = f"{exp}/{cell}/{model}/{cond}/{seed}"
    if sc not in pv:
        p = load_private(sc); pv[sc] = (p, set(unreachable(list(p.gold.values()))))
    p, un = pv[sc]
    # LLM 호출 (obs/llm + timing)
    timing = [json.loads(l) for l in open(run / "timing/llm.jsonl")]
    span = {}
    for x in timing:
        a, b = x["t_s"] - x["latency_ms"] / 1000, x["t_s"]; s = span.get(x["task_id"]); span[x["task_id"]] = (min(a, s[0]), max(b, s[1])) if s else (a, b)
    cost = defaultdict(float); calls_n = defaultdict(int)
    pin, pout = PRICE[model]
    for l in open(run / "obs/llm.jsonl"):
        x = json.loads(l); u = x.get("usage") or {}
        c = 0 if x.get("cached") else (u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout) / 1e6
        cost[x.get("task_id")] += c; calls_n[x.get("task_id")] += 1
        R_llm.append([rid, x.get("day"), x.get("round"), x.get("task_id"), x.get("agent"), x.get("component"), x.get("boundary_step"),
                      x.get("step"), int(bool(x.get("final"))), int(bool(x.get("cached"))), x.get("attempts"), x.get("latency_ms"),
                      u.get("prompt_tokens"), u.get("completion_tokens"), x.get("provider_cached_tokens"), x.get("finish_reason"), round(c, 6)])
    # WAL: 답, 경계 결정, 라운드 커밋
    done_day = 0; answers = {}
    with open(run / "wal/events.jsonl") as f:
        for l in f:
            if '"type":"answer"' in l:
                e = json.loads(l); answers[e["payload"].get("task_id")] = (e, e["payload"])
            elif '"type":"boundary_decision"' in l:
                e = json.loads(l); q = e["payload"]
                R_gw.append([rid, e["day"], e.get("round"), q.get("task_id"), q.get("rid"), q.get("stage"), q.get("group"), q.get("from_group"),
                             q.get("action"), "|".join(q.get("selected") or []), "|".join(q.get("proposed") or []), q.get("referral_to"),
                             q.get("status"), len(q.get("additions") or []), len(q.get("conflicts") or []), len(q.get("proposals") or []),
                             len(q.get("proposals_dropped") or []), "|".join(q.get("requery") or []) if isinstance(q.get("requery"), list) else q.get("requery"),
                             len(q.get("sources") or []), q.get("question", "")[:300]])
            elif '"round_commit"' in l:
                e = json.loads(l)
                if e["round"] == 3: done_day = max(done_day, e["day"])
    scored = correct = 0; tot_calls = tot_tok = 0
    for w, (e, a) in answers.items():
        if w not in p.gold: continue
        g = p.gold[w]; ans = a.get("answer")
        v = verify(p.tasks[w], ans, g) if ans is not None else {"exact": False, "slots": {k: False for k in g["gold"]}}
        b = a.get("budget") or {}; bc = b.get("by_component") or {}
        within = g["day"] <= cap; reach = w not in un
        if within and reach: scored += 1; correct += v["exact"]
        calls = sum(x.get("calls", 0) for x in bc.values()); toks = sum(x.get("tokens", 0) for x in bc.values()); tot_calls += calls; tot_tok += toks
        sp = span.get(w)
        R_tasks.append([rid, exp, cell, model, cond, seed, w, g["day"], g["round"], g["template"], g.get("family"), g["state_class"],
                        int(bool(g.get("c_ops"))), g["n_groups"], g.get("R"), g.get("max_holders"), g.get("path_len"), int(within), int(reach),
                        int(v["exact"]), sum(v["slots"].values()), len(v["slots"]), json.dumps(ans, ensure_ascii=False, sort_keys=True),
                        json.dumps(g["gold"], ensure_ascii=False, sort_keys=True), a.get("error"),
                        *(bc.get(k, {}).get("calls", 0) for k in ("requester", "responder", "boundary")),
                        *(bc.get(k, {}).get("tokens", 0) for k in ("requester", "responder", "boundary")),
                        int(bool(b.get("budget_exhausted"))), b.get("exhausted_by"), int(bool(b.get("final_call_used"))),
                        b.get("requester_asks"), b.get("responder_step_cap"), calls_n.get(w, 0), round(cost.get(w, 0), 6),
                        round(sp[1] - sp[0], 1) if sp else None, g["surface"].split("\n")[0]])
    sup = (run / "supervise.jsonl").read_text().splitlines()
    t0 = datetime.datetime.fromisoformat(json.loads(sup[0])["at"])
    restarts = sum(1 for x in sup if '"restart"' in x)
    R_runs.append([rid, exp, cell, NG[cell], TPD[cell], model, cond, seed, cap, done_day, scored, correct,
                   round(correct / scored, 4) if scored else None, tot_calls, tot_tok, round(sum(cost.values()), 2), len(timing),
                   restarts, (M / code / "FROZEN_COMMIT").read_text().strip()[:7], sc.name])
    # obs: 메시지·검색·묶음
    for name, sink in (("messages", R_msg), ("retrievals", R_ret), ("batches", R_bat)):
        f = run / "obs" / f"{name}.jsonl"
        if not f.exists(): continue
        for l in open(f):
            x = json.loads(l)
            if name == "messages":
                sink.append([rid, x.get("day"), x.get("round"), x.get("task_id"), x.get("rid"), x.get("kind"), x.get("via"), x.get("from_agent"),
                             x.get("from_group"), x.get("to_agent"), x.get("to_group"), int(bool(x.get("crossing"))), x.get("hop"),
                             x.get("origin_task"), x.get("serving"), x.get("chars")])
            elif name == "retrievals":
                c = x.get("candidates"); sel = x.get("selected") or []
                if isinstance(c, list):                                   # 게이트웨이 검색 (후보 목록)
                    src, ncand = "gateway", len(c)
                    nsel = sum(1 for y in c if y.get("reason") == "selected"); ncut = sum(1 for y in c if y.get("reason") == "cap_cut")
                    agents = "|".join(sorted({y.get("agent", "") for y in c if y.get("reason") == "selected"}))
                else:                                                     # full_load search_memory (후보 수만)
                    src, ncand, nsel, ncut = x.get("tool") or "search_memory", c, len(sel), None
                    agents = "|".join(sorted({y.get("agent", "") for y in sel if isinstance(y, dict)}))
                sink.append([rid, x.get("day"), x.get("round"), x.get("rid") or x.get("task_id"), src, x.get("group"),
                             int(bool(x.get("cap_reached"))), x.get("cap"), ncand, nsel, ncut, x.get("tokens"),
                             len(x.get("outside_top_k") or []), agents, (x.get("query") or "")[:300]])
            else:
                sink.append([rid, x.get("seq"), x.get("day"), x.get("round"), x.get("size"), "|".join(x.get("tasks") or [])])
    # 원 로그 압축
    L = OUT / "logs" / rid.replace("/", "__"); L.mkdir(parents=True, exist_ok=True)
    for src, dst in [(run / "wal/events.jsonl", "events.jsonl.gz"), *[(run / "obs" / f"{n}.jsonl", f"obs_{n}.jsonl.gz")
                     for n in ("gateway", "messages", "retrievals", "batches", "llm")], (run / "timing/llm.jsonl", "timing_llm.jsonl.gz")]:
        if src.exists():
            with open(src, "rb") as fi, gzip.open(L / dst, "wb", compresslevel=6) as fo: shutil.copyfileobj(fi, fo)
    for n in ("manifest.json", "run.json", "supervise.jsonl", "retarget.jsonl"):
        if (run / n).exists(): shutil.copy(run / n, L / n)
    print("done", rid, flush=True)

W("runs.csv", ["run_id", "experiment", "cell", "n_groups", "tasks_per_day", "model", "condition", "seed", "target_days", "completed_days",
               "n_scored", "n_correct", "accuracy", "llm_calls_budget", "tokens_budget", "cost_usd_est", "llm_calls_timing", "restarts",
               "code_commit", "scenario"], R_runs)
W("tasks.csv", ["run_id", "experiment", "cell", "model", "condition", "seed", "task_id", "day", "round", "template", "family", "state_class",
                "c_ops", "n_groups", "reasoning_tier", "max_holders", "path_len", "within_target_days", "reachable", "exact", "slots_correct",
                "slots_total", "answer_json", "gold_json", "error", "calls_requester", "calls_responder", "calls_boundary", "tokens_requester",
                "tokens_responder", "tokens_boundary", "budget_exhausted", "exhausted_by", "final_call_used", "requester_asks",
                "responder_step_caps", "llm_calls", "cost_usd_est", "wall_seconds", "surface"], R_tasks)
W("llm_calls.csv", ["run_id", "day", "round", "task_id", "agent", "component", "boundary_step", "step", "final", "cached", "attempts",
                    "latency_ms", "prompt_tokens", "completion_tokens", "provider_cached_tokens", "finish_reason", "cost_usd_est"], R_llm, gz=True)
W("gateway_decisions.csv", ["run_id", "day", "round", "task_id", "rid", "stage", "group", "from_group", "action", "selected", "proposed",
                            "referral_to", "status", "n_additions", "n_conflicts", "n_proposals", "n_proposals_dropped", "requery",
                            "n_sources_cited", "question"], R_gw)
W("messages.csv", ["run_id", "day", "round", "task_id", "rid", "kind", "via", "from_agent", "from_group", "to_agent", "to_group",
                   "crossing", "hop", "origin_task", "serving", "chars"], R_msg, gz=True)
W("retrievals.csv", ["run_id", "day", "round", "rid_or_task", "source", "group", "cap_reached", "cap_tokens", "n_candidates",
                     "n_selected", "n_cap_cut", "evidence_tokens", "n_outside_top_k", "selected_agents", "query"], R_ret, gz=True)
W("batches.csv", ["run_id", "seq", "day", "round", "size", "tasks"], R_bat)
print("tables", len(R_runs), len(R_tasks), len(R_llm), len(R_gw), len(R_msg), len(R_ret))
