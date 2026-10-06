"""analysis_package/agg: tables/tasks.csv에서 요약 표. 비교는 (실험·셀·모델·시드)마다 비교 조건이 모두 답한 공통 과제,
일수 상한 안(within_target_days=1), 원리상 풀 수 있는 과제(reachable=1)만. 비용·호출은 공통 과제 기준 평균."""
import csv, json, random, shutil
from collections import defaultdict
from pathlib import Path
OUT = Path("/root/project/g2g/output/analysis_package"); T = OUT / "tables"; A = OUT / "agg"; A.mkdir(exist_ok=True)
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1"]
by = defaultdict(dict)                                                     # (exp, cell, model, seed) → cond → task → row
for r in rows:
    by[(r["experiment"], r["cell"], r["model"], r["seed"])].setdefault(r["condition"], {})[r["task_id"]] = r
C4 = ["direct", "routing", "ingress", "full_load"]; APX = ["direct_relay", "retrieve", "sidecar"]

def common(exp_cell_model, conds, maxday=None):
    out = []
    for (exp, cell, model, seed), d in by.items():
        if (cell, model) != exp_cell_model or not all(c in d for c in conds): continue
        if exp == "appendix" and not set(conds) & set(APX): continue
        tasks = set.intersection(*[set(d[c]) for c in conds])
        for t in tasks:
            if maxday and int(d[conds[0]][t]["day"]) > maxday: continue
            out.append({c: d[c][t] for c in conds})
    return out

def full_set(cell, model, conds):                                         # 본 실험·부록 런을 한데 모아 공통 과제
    d = defaultdict(dict)
    for (exp, c2, m2, seed), dd in by.items():
        if c2 == cell and m2 == model:
            for c, tasks in dd.items(): d[seed].setdefault(c, {}).update(tasks)
    out = []
    for seed, dd in d.items():
        if not all(c in dd for c in conds): continue
        for t in set.intersection(*[set(dd[c]) for c in conds]): out.append({c: dd[c][t] for c in conds})
    return out

def boot(items, a, b, n=2000):
    d = [int(x[a]["exact"]) - int(x[b]["exact"]) for x in items]
    if not d: return (None, None, None)
    rnd = random.Random(0); m = sorted(sum(d[rnd.randrange(len(d))] for _ in d) / len(d) for _ in range(n))
    return round(sum(d) / len(d), 4), round(m[int(.025 * n)], 4), round(m[int(.975 * n)], 4)

def write(name, header, data):
    with open(A / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(data)

def stats(items, c):
    xs = [x[c] for x in items]; n = len(xs)
    if not n: return [0, None, None, None, None, None, None]
    acc = sum(int(x["exact"]) for x in xs) / n
    calls = sum(int(x["llm_calls"]) for x in xs) / n
    tok = sum(int(x["tokens_requester"]) + int(x["tokens_responder"]) + int(x["tokens_boundary"]) for x in xs) / n
    cost = sum(float(x["cost_usd_est"]) for x in xs) / n
    exh = sum(int(x["budget_exhausted"]) for x in xs) / n
    return [n, round(acc, 4), round(calls, 1), round(tok), round(cost, 4), round(cost / acc, 4) if acc else None, round(exh, 4)]

H = ["n_tasks", "accuracy", "llm_calls_per_task", "tokens_per_task", "cost_usd_per_task", "cost_usd_per_success", "budget_exhausted_rate"]
# 1. 조건별 (셀·모델)
data = []
for cell, model, conds, maxday in [("base", m, C4, None) for m in ("qwen3.5-27b", "qwen3.5-9b", "deepseek-v4-flash")] + \
        [(c, "qwen3.5-27b", C4, None) for c in ("R1", "D3", "R3")] + [("base", "qwen3.5-27b", C4, 10)]:
    it = full_set(cell, model, conds) if maxday is None else [x for x in full_set(cell, model, conds) if int(x["direct"]["day"]) <= maxday]
    g = boot(it, "ingress", "direct")
    for c in conds:
        data.append([cell, model, f"1-{maxday or (15 if cell == 'base' else 10)}", c, *stats(it, c), *(g if c == "ingress" else (None,) * 3)])
write("by_condition.csv", ["cell", "model", "days", "condition", *H, "gap_vs_direct", "ci_low", "ci_high"], data)
# 2. 부록 7조건
it = [x for x in full_set("base", "qwen3.5-27b", C4 + APX) if int(x["direct"]["day"]) <= 10]
write("appendix_7conditions.csv", ["condition", *H], [[c, *stats(it, c)] for c in C4 + APX])
# 3. 층화 (27B: 기준 셀 15일 + G 셀 10일, 4조건 공통)
pool = full_set("base", "qwen3.5-27b", C4) + sum((full_set(c, "qwen3.5-27b", C4) for c in ("R1", "D3", "R3")), [])
data = []
for field in ("state_class", "c_ops", "n_groups", "template", "reasoning_tier", "max_holders"):
    vals = sorted({x["direct"][field] for x in pool}, key=lambda v: (len(v), v))
    for v in vals:
        sub = [x for x in pool if x["direct"][field] == v]
        accs = [round(sum(int(x[c]["exact"]) for x in sub) / len(sub), 4) for c in C4]
        data.append([field, v, len(sub), *accs, round(accs[2] - accs[0], 4)])
write("strata_27b.csv", ["field", "value", "n_tasks", *C4, "gap_ingress_direct"], data)
# 4. 일자 창 (기준 셀, 모델별)
data = []
for model in ("qwen3.5-27b", "qwen3.5-9b", "deepseek-v4-flash"):
    it = full_set("base", model, C4)
    for lo, hi in ((1, 5), (6, 10), (11, 15)):
        sub = [x for x in it if lo <= int(x["direct"]["day"]) <= hi]
        if sub: data.append([model, f"{lo}-{hi}", len(sub), *[round(sum(int(x[c]["exact"]) for x in sub) / len(sub), 4) for c in C4]])
write("by_day_window.csv", ["model", "days", "n_tasks", *C4], data)
# 5. 경계 결정 요약
gw = defaultdict(lambda: defaultdict(list))
for r in csv.DictReader(open(T / "gateway_decisions.csv", encoding="utf-8")):
    k = r["run_id"].split("/")[1:4] + [r["run_id"].split("/")[3]]
    key = ("/".join(r["run_id"].split("/")[:4]), r["stage"])
    gw[key]["n_selected"].append(len([x for x in r["selected"].split("|") if x]))
    gw[key]["referral"].append(r["action"] == "referral")
    for f in ("n_additions", "n_conflicts", "n_proposals", "n_proposals_dropped"): gw[key][f].append(int(r[f] or 0))
    gw[key]["requery"].append(bool(r["requery"] and r["requery"] not in ("[]", "None")))
data = [[k[0], k[1], len(v["n_selected"]), *(round(sum(v[f]) / len(v[f]), 3) for f in ("n_selected", "referral", "n_additions", "n_conflicts",
         "n_proposals", "n_proposals_dropped", "requery"))] for k, v in sorted(gw.items())]
write("gateway_summary.csv", ["run_group", "stage", "n_decisions", "mean_members_selected", "referral_rate", "mean_additions",
                              "mean_conflicts", "mean_proposals", "mean_proposals_dropped", "requery_rate"], data)
# 6. 런 묶음 비용
runs = list(csv.DictReader(open(T / "runs.csv", encoding="utf-8")))
agg = defaultdict(lambda: [0, 0.0, 0, 0])
for r in runs:
    k = (r["experiment"], r["cell"], r["model"], r["condition"]); agg[k][0] += 1; agg[k][1] += float(r["cost_usd_est"]); agg[k][2] += int(r["llm_calls_timing"]); agg[k][3] += int(r["n_scored"])
write("cost_by_run_group.csv", ["experiment", "cell", "model", "condition", "n_runs", "cost_usd_est", "llm_calls", "n_scored_tasks"],
      [[*k, *v[:1], round(v[1], 2), *v[2:]] for k, v in sorted(agg.items())])
print("agg done")
