"""AAMAS 논문 Experiments 섹션용 분석: 표(LaTeX)·그림(PDF/PNG)·수치(JSON/MD).
입력: output/analysis_package/{tables,meta}.  출력: output/paper/{tables,figures,numbers.json,numbers.md}
비교 원칙: (셀·모델·시드)마다 비교 조건이 모두 답한 공통 과제, 일수 상한 안, 원리상 풀 수 있는 과제. 정확도 = 답 전체 정확 일치.
구간 = 과제 단위 짝 부트스트랩 95% (2000회, seed 0). 짝 비교 p = McNemar 정확 검정."""
import csv, gzip, json, math, random
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PKG = Path("/root/project/g2g/output/analysis_package"); T = PKG / "tables"
OUT = Path("/root/project/g2g/output/paper"); (OUT / "figures").mkdir(parents=True, exist_ok=True); (OUT / "tables").mkdir(exist_ok=True)
MODELS = ["qwen3.5-27b", "deepseek-v4-flash", "qwen3.5-9b"]
MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
C4 = ["direct", "routing", "ingress", "full_load"]; APX = ["direct_relay", "retrieve", "sidecar"]; ALL7 = C4 + APX
CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load", "direct_relay": "Direct+relay",
      "retrieve": "Retrieve", "sidecar": "Sidecar"}
CLASSES = ["A", "B", "C", "D"]
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73", "direct_relay": "#bbbbbb",
       "retrieve": "#d55e00", "sidecar": "#56b4e9"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5,
                     "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
NUM = {}

# ─────────────────────────── 데이터 ───────────────────────────
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1"]
for r in rows:
    r["exact"] = int(r["exact"]); r["day"] = int(r["day"]); r["c_ops"] = int(r["c_ops"]); r["n_groups"] = int(r["n_groups"])
    r["tokens"] = int(r["tokens_requester"]) + int(r["tokens_responder"]) + int(r["tokens_boundary"])
    r["calls"] = int(r["calls_requester"]) + int(r["calls_responder"]) + int(r["calls_boundary"])
    r["cost"] = float(r["cost_usd_est"]); r["exh"] = int(r["budget_exhausted"]); r["noans"] = int(r["error"] not in ("", "None"))
by = defaultdict(lambda: defaultdict(dict))                                # (cell, model, seed) → cond → task → row
for r in rows:
    by[(r["cell"], r["model"], r["seed"])][r["condition"]][r["task_id"]] = r
SEEDS = ["s12", "s13", "s14"]

def common(cell, model, conds, maxday=None, templates=None):
    out = []
    for s in SEEDS:
        d = by.get((cell, model, s), {})
        if not all(c in d for c in conds): continue
        for t in sorted(set.intersection(*[set(d[c]) for c in conds])):   # 정렬: 부트스트랩 재현성
            r0 = d[conds[0]][t]
            if maxday and r0["day"] > maxday: continue
            if templates and r0["template"] not in templates: continue
            out.append({c: d[c][t] for c in conds})
    return out

RNG = np.random.default_rng(0)
def boot(items, a, b, B=2000):
    d = np.array([x[a]["exact"] - x[b]["exact"] for x in items], float)
    if len(d) == 0: return None
    idx = RNG.integers(0, len(d), (B, len(d))); m = np.sort(d[idx].mean(1))
    return {"mean": float(d.mean()), "lo": float(m[int(.025 * B)]), "hi": float(m[int(.975 * B)]), "n": int(len(d))}
def mcnemar(items, a, b):
    bb = sum(1 for x in items if x[a]["exact"] and not x[b]["exact"]); cc = sum(1 for x in items if not x[a]["exact"] and x[b]["exact"])
    n = bb + cc; k = min(bb, cc)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return {"a_only": bb, "b_only": cc, "p": p}
def acc(items, c, f=lambda r: True):
    xs = [x[c]["exact"] for x in items if f(x[c])]; return (sum(xs) / len(xs), len(xs)) if xs else (float("nan"), 0)
def mean(items, c, key): xs = [x[c][key] for x in items]; return sum(xs) / len(xs) if xs else float("nan")
def fmt_ci(b): return f"{b['mean']*100:+.1f} [{b['lo']*100:+.1f}, {b['hi']*100:+.1f}]"
def pct(x): return f"{x*100:.1f}"

# ─────────────────────────── 1. 주 결과 (기준 셀, 모델별) ───────────────────────────
main = {}
for m in MODELS:
    it = common("base", m, C4, 15)
    main[m] = {"n": len(it), "acc": {c: acc(it, c)[0] for c in C4},
               "d_route": boot(it, "routing", "direct"), "d_sel": boot(it, "ingress", "routing"), "d_total": boot(it, "ingress", "direct"),
               "d_full": boot(it, "ingress", "full_load"), "mcn_total": mcnemar(it, "ingress", "direct"), "mcn_sel": mcnemar(it, "ingress", "routing"),
               "mcn_route": mcnemar(it, "routing", "direct"),
               "cost": {c: {"calls": mean(it, c, "calls"), "tokens": mean(it, c, "tokens"), "usd": mean(it, c, "cost"),
                            "exh": mean(it, c, "exh"), "noans": mean(it, c, "noans")} for c in C4},
               "by_class": {}, "by_window": {}}
    for k in CLASSES + ["c_ops"]:
        f = (lambda r, k=k: r["state_class"] == k) if k != "c_ops" else (lambda r: r["c_ops"] == 1)
        sub = [x for x in it if f(x["direct"])]
        main[m]["by_class"][k] = {"n": len(sub), "acc": {c: acc(sub, c)[0] for c in C4},
                                  "d_route": boot(sub, "routing", "direct"), "d_sel": boot(sub, "ingress", "routing"), "d_total": boot(sub, "ingress", "direct")}
    for lo, hi in ((1, 5), (6, 10), (11, 15)):
        sub = [x for x in it if lo <= x["direct"]["day"] <= hi]
        main[m]["by_window"][f"{lo}-{hi}"] = {"n": len(sub), "acc": {c: acc(sub, c)[0] for c in C4}, "d_total": boot(sub, "ingress", "direct")}
NUM["main"] = main

# ─────────────────────────── 2. 규모 (G 셀, 27B, 1~10일) ───────────────────────────
CELLS = [("R1", 5), ("D3", 6), ("base", 10), ("R3", 15)]
cell_items = {c: common(c, "qwen3.5-27b", C4, 10) for c, _ in CELLS}
shared_t = set.intersection(*[{x["direct"]["template"] for x in v} for v in cell_items.values()])
scale = {"shared_templates": sorted(shared_t), "cells": {}}
for c, g in CELLS:
    it = cell_items[c]; its = [x for x in it if x["direct"]["template"] in shared_t]
    scale["cells"][c] = {"G": g, "n_all": len(it), "acc_all": {k: acc(it, k)[0] for k in C4}, "d_total_all": boot(it, "ingress", "direct"),
                         "n_shared": len(its), "acc_shared": {k: acc(its, k)[0] for k in C4}, "d_total_shared": boot(its, "ingress", "direct"),
                         "d_route_shared": boot(its, "routing", "direct"), "d_sel_shared": boot(its, "ingress", "routing")}
pool = common("base", "qwen3.5-27b", C4, 15) + sum((cell_items[c] for c in ("R1", "D3", "R3")), [])
scale["by_groups_involved"] = {}
for lo, hi, lab in ((2, 2, "2"), (3, 3, "3"), (4, 4, "4"), (5, 99, "5+")):
    sub = [x for x in pool if lo <= x["direct"]["n_groups"] <= hi]
    scale["by_groups_involved"][lab] = {"n": len(sub), "acc": {k: acc(sub, k)[0] for k in C4}, "d_total": boot(sub, "ingress", "direct"),
                                        "d_route": boot(sub, "routing", "direct"), "d_sel": boot(sub, "ingress", "routing")}
scale["pooled_by_class"] = {}
for k in CLASSES + ["c_ops"]:
    f = (lambda r, k=k: r["state_class"] == k) if k != "c_ops" else (lambda r: r["c_ops"] == 1)
    sub = [x for x in pool if f(x["direct"])]
    scale["pooled_by_class"][k] = {"n": len(sub), "acc": {c: acc(sub, c)[0] for c in C4}, "d_route": boot(sub, "routing", "direct"), "d_sel": boot(sub, "ingress", "routing")}
scale["pooled_n"] = len(pool)
NUM["scale"] = scale
# 템플릿별 (27B 합산)
tpl = {}
for t in sorted({x["direct"]["template"] for x in pool}):
    sub = [x for x in pool if x["direct"]["template"] == t]
    tpl[t] = {"n": len(sub), "acc": {c: acc(sub, c)[0] for c in C4}, "d_total": boot(sub, "ingress", "direct")}
NUM["templates"] = tpl

# ─────────────────────────── 3. 변형 (부록 7조건, 27B, 1~10일) ───────────────────────────
it7 = common("base", "qwen3.5-27b", ALL7, 10)
var = {"n": len(it7), "cond": {}}
for c in ALL7:
    var["cond"][c] = {"acc": acc(it7, c)[0], "by_class": {k: acc(it7, c, lambda r, k=k: r["state_class"] == k)[0] for k in CLASSES},
                      "c_ops": acc(it7, c, lambda r: r["c_ops"] == 1)[0], "calls": mean(it7, c, "calls"), "tokens": mean(it7, c, "tokens"),
                      "usd": mean(it7, c, "cost"), "exh": mean(it7, c, "exh"),
                      "vs_direct": boot(it7, c, "direct") if c != "direct" else None, "vs_ingress": boot(it7, c, "ingress") if c != "ingress" else None,
                      "mcn_vs_ingress": mcnemar(it7, c, "ingress") if c != "ingress" else None}
NUM["variants"] = var

# ─────────────────────────── 4. 게이트웨이 동작 ───────────────────────────
gw_rows = list(csv.DictReader(open(T / "gateway_decisions.csv", encoding="utf-8")))
gws = {}
for m in MODELS:
    for cond in ("routing", "ingress"):
        rs = [g for g in gw_rows if g["run_id"].startswith(f"main/base/{m}/{cond}/") and g["stage"] == "ingress"]
        if not rs: continue
        n = len(rs)
        gws[f"{m}/{cond}"] = {"n": n, "members_selected": sum(len([x for x in g["selected"].split("|") if x]) for g in rs) / n,
                              "referral_rate": sum(g["action"] == "referral" for g in rs) / n,
                              "out_of_scope_rate": sum(g["action"] == "out_of_scope" for g in rs) / n,
                              "additions": sum(int(g["n_additions"] or 0) for g in rs) / n, "conflicts": sum(int(g["n_conflicts"] or 0) for g in rs) / n,
                              "proposals": sum(int(g["n_proposals"] or 0) for g in rs) / n, "dropped": sum(int(g["n_proposals_dropped"] or 0) for g in rs) / n,
                              "requery_rate": sum(bool(g["requery"]) and g["requery"] not in ("[]", "None", "") for g in rs) / n,
                              "any_addition_rate": sum(int(g["n_additions"] or 0) > 0 for g in rs) / n}
NUM["gateway"] = gws
# 조립이 기록을 보탠 과제 vs 아닌 과제의 정확도 (ingress, 모델별, 기준 셀)
gw_by_task = defaultdict(lambda: {"adds": 0, "conf": 0, "prop": 0, "req": 0, "n": 0})
for g in gw_rows:
    if g["stage"] != "ingress": continue
    k = (g["run_id"], g["task_id"]); d = gw_by_task[k]; d["n"] += 1
    d["adds"] += int(g["n_additions"] or 0); d["conf"] += int(g["n_conflicts"] or 0); d["prop"] += int(g["n_proposals"] or 0)
    d["req"] += bool(g["requery"]) and g["requery"] not in ("[]", "None", "")
addeff = {}
for m in MODELS:
    it = common("base", m, C4, 15); res = {}
    for k in CLASSES + ["all"]:
        sub = [x for x in it if k == "all" or x["direct"]["state_class"] == k]
        w = [x for x in sub if gw_by_task.get((x["ingress"]["run_id"], x["ingress"]["task_id"]), {"adds": 0})["adds"] > 0]
        wo = [x for x in sub if gw_by_task.get((x["ingress"]["run_id"], x["ingress"]["task_id"]), {"adds": 0})["adds"] == 0]
        res[k] = {"with_add_n": len(w), "with_add_acc": acc(w, "ingress")[0], "with_add_direct": acc(w, "direct")[0],
                  "without_n": len(wo), "without_acc": acc(wo, "ingress")[0], "without_direct": acc(wo, "direct")[0]}
    addeff[m] = res
NUM["assembly_additions"] = addeff

# ─────────────────────────── 5. 담당자 도달률 (request mediation) ───────────────────────────
def load_gold(name):
    return {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / "meta/scenarios" / name / "gold.jsonl.gz", "rt", encoding="utf-8"))}
GOLD = {s: load_gold(f"scenarios__D5_{s}_T45") for s in SEEDS}
def candidates(g):
    """교차 그룹 need마다 (그룹, 후보 에이전트 집합): 결정 필수 조각의 활동 중 보유자, 없으면 need의 card 담당자."""
    out = []
    for n in g["needs"]:
        if n["group"] == g["root"]: continue
        crit = set(n.get("critical_components") or []); cand = set()
        for s in n["sources"]:
            if s["type"] == "frag" and s["frag"]["fid"] in crit:
                cand |= {h["agent"] for h in s["frag"].get("holders", []) if h.get("active")}
        if not cand and n.get("card"): cand = {n["card"]}
        if cand: out.append((n["group"], cand, bool(crit)))
    return out
contacted = defaultdict(set)                                               # (run_id, task) → 요청자가 직접 닿은 에이전트 (direct 계열)
with gzip.open(T / "messages.csv.gz", "rt", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["kind"] == "request" and r["via"] == "agent" and not r["serving"] and not r["from_agent"].startswith("boundary:") and r["to_agent"]:
            contacted[(r["run_id"], r["task_id"])].add(r["to_agent"])
selected = defaultdict(set)                                                # (run_id, task) → 게이트웨이가 고른 담당자
for g in gw_rows:
    if g["stage"] == "ingress":
        selected[(g["run_id"], g["task_id"])] |= {x for x in g["selected"].split("|") if x}
reach = {}
for m in MODELS:
    it = common("base", m, C4, 15); res = {}
    for cond in ("direct", "routing", "ingress"):
        per = defaultdict(lambda: [0, 0])                                     # class → [reached, total]
        for x in it:
            r = x[cond]; g = GOLD[r["seed"]][r["task_id"]]
            got = contacted[(r["run_id"], r["task_id"])] if cond == "direct" else selected[(r["run_id"], r["task_id"])]
            for grp, cand, _ in candidates(g):
                hit = bool(got & cand); k = r["state_class"]
                per[k][0] += hit; per[k][1] += 1; per["all"][0] += hit; per["all"][1] += 1
        res[cond] = {k: {"rate": v[0] / v[1] if v[1] else float("nan"), "n": v[1]} for k, v in per.items()}
    reach[m] = res
NUM["reach"] = reach
# 부록 변형의 도달률 (27B, 1~10일)
reach7 = {}
for cond in ALL7:
    if cond == "full_load": continue
    per = [0, 0]
    for x in it7:
        r = x[cond]; g = GOLD[r["seed"]][r["task_id"]]
        got = selected[(r["run_id"], r["task_id"])] if cond in ("routing", "ingress", "retrieve") else contacted[(r["run_id"], r["task_id"])]
        for grp, cand, _ in candidates(g):
            per[0] += bool(got & cand); per[1] += 1
    reach7[cond] = per[0] / per[1] if per[1] else float("nan")
NUM["reach_variants"] = reach7

# ─────────────────────────── 6. 비용·운영 ───────────────────────────
runs = list(csv.DictReader(open(T / "runs.csv", encoding="utf-8")))
NUM["ops"] = {"n_runs": len(runs), "total_cost_usd": sum(float(r["cost_usd_est"]) for r in runs), "total_llm_calls": sum(int(r["llm_calls_timing"]) for r in runs),
              "restarts": sum(int(r["restarts"]) for r in runs), "n_scored_rows": len(rows)}

# 비A(B–D) 묶음: f8(b)의 대조군 대비용. 주 RNG 흐름(기존 CI)을 바꾸지 않도록 별도 RNG로 맨 끝에서 계산
RNG_MAIN, RNG = RNG, np.random.default_rng(1)
for m in MODELS:
    sub = [x for x in common("base", m, C4, 15) if x["direct"]["state_class"] != "A"]
    NUM["main"][m]["by_class"]["notA"] = {"n": len(sub), "acc": {c: acc(sub, c)[0] for c in C4},
                                          "d_route": boot(sub, "routing", "direct"), "d_sel": boot(sub, "ingress", "routing"), "d_total": boot(sub, "ingress", "direct")}
RNG = RNG_MAIN
json.dump(NUM, open(OUT / "numbers.json", "w"), ensure_ascii=False, indent=1, default=float)

# ─────────────────────────── LaTeX 표 ───────────────────────────
def tex(name, body):
    (OUT / "tables" / name).write_text(body, encoding="utf-8")
# T1 주 결과
L = [r"\begin{tabular}{llcccc ccc}", r"\toprule",
     r"Backbone & $n$ & Direct & Routing & Ingress & Full-load & $\Delta_{\text{route}}$ & $\Delta_{\text{sel}}$ & $\Delta_{\text{total}}$ \\",
     r"\midrule"]
for m in MODELS:
    d = main[m]; a = d["acc"]
    L.append(f"{MN[m]} & {d['n']} & {pct(a['direct'])} & {pct(a['routing'])} & \\textbf{{{pct(a['ingress'])}}} & {pct(a['full_load'])} & "
             f"{fmt_ci(d['d_route'])} & {fmt_ci(d['d_sel'])} & {fmt_ci(d['d_total'])} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t1_main.tex", "\n".join(L))
# T2 변형
L = [r"\begin{tabular}{l cc l r cccc rr}", r"\toprule",
     r"Condition & Med. & Sel. & Where & Acc. & A & B & C & D & Calls & Tokens (k) \\", r"\midrule"]
FACT = {"direct": ("--", "--", "requester (cards)"), "direct_relay": ("--", "--", "responder asks peers"), "routing": (r"\checkmark", "--", "gateway picks responder"),
        "retrieve": (r"\checkmark", "raw", "records to requester"), "sidecar": ("--", r"\checkmark", "per-agent module"), "ingress": (r"\checkmark", r"\checkmark", "group gateway"),
        "full_load": ("n/a", "n/a", "no partition (ref.)")}
for c in ["direct", "direct_relay", "routing", "retrieve", "sidecar", "ingress", "full_load"]:
    v = var["cond"][c]; f = FACT[c]
    L.append(f"{CN[c]} & {f[0]} & {f[1]} & {f[2]} & {pct(v['acc'])} & " + " & ".join(pct(v["by_class"][k]) for k in CLASSES)
             + f" & {v['calls']:.0f} & {v['tokens']/1000:.0f} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t2_variants.tex", "\n".join(L))
# T3 등급별 (모델별)
L = [r"\begin{tabular}{ll r cccc cc}", r"\toprule", r"Backbone & Class & $n$ & Direct & Routing & Ingress & Full-load & $\Delta_{\text{route}}$ & $\Delta_{\text{sel}}$ \\", r"\midrule"]
for m in MODELS:
    for k in CLASSES:
        d = main[m]["by_class"][k]; a = d["acc"]
        klab = k if k != "c_ops" else r"$C_{\text{ops}}$"; mlab = MN[m] if k == "A" else ""
        L.append(f"{mlab} & {klab} & {d['n']} & {pct(a['direct'])} & {pct(a['routing'])} & {pct(a['ingress'])} & {pct(a['full_load'])} & "
                 f"{fmt_ci(d['d_route'])} & {fmt_ci(d['d_sel'])} \\\\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
tex("t3_by_class.tex", "\n".join(L))
# T4 게이트웨이 동작
L = [r"\begin{tabular}{l r c c c c c c c}", r"\toprule", r"Run group & Decisions & Members/req. & Referral & Additions & Conflicts & Proposals & Dropped & Requery \\", r"\midrule"]
for k, v in gws.items():
    m, c = k.split("/")
    L.append(f"{MN[m]} {CN[c]} & {v['n']} & {v['members_selected']:.2f} & {pct(v['referral_rate'])}\\% & {v['additions']:.2f} & {v['conflicts']:.2f} & {v['proposals']:.2f} & {v['dropped']:.2f} & {pct(v['requery_rate'])}\\% \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t4_gateway.tex", "\n".join(L))
# T5 규모
# 위: 1~10일, 모든 셀에 있는 11개 템플릿(셀 간 비교용 n_shared). 오른쪽 두 열: 같은 기간의 모든 템플릿(n_all).
# 아래: 기준 셀 1~15일 + G 셀 1~10일, 모든 템플릿 풀링(1,162)
L = [r"\begin{tabular}{l c r cccc c r c}", r"\toprule",
     r"Cell & $G$ & $n_{\text{shared}}$ & Direct & Routing & Ingress & Full-load & $\Delta_{\text{total}}$ (shared) & $n_{\text{all}}$ & $\Delta_{\text{total}}$ (all) \\", r"\midrule"]
for c, g in CELLS:
    v = scale["cells"][c]; a = v["acc_shared"]
    L.append(f"{c if c != 'base' else 'D5·R2 (base)'} & {g} & {v['n_shared']} & {pct(a['direct'])} & {pct(a['routing'])} & {pct(a['ingress'])} & {pct(a['full_load'])} & {fmt_ci(v['d_total_shared'])} & {v['n_all']} & {fmt_ci(v['d_total_all'])} \\\\")
L += [r"\midrule", r"\multicolumn{10}{l}{\textit{By number of groups a task spans (base cell days 1--15 and the three other cells days 1--10, all templates)}} \\"]
for lab, v in scale["by_groups_involved"].items():
    a = v["acc"]; L.append(f"{lab} groups & -- & {v['n']} & {pct(a['direct'])} & {pct(a['routing'])} & {pct(a['ingress'])} & {pct(a['full_load'])} & {fmt_ci(v['d_total'])} & & \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t5_scale.tex", "\n".join(L))
# T6 비용
L = [r"\begin{tabular}{ll r r r r r}", r"\toprule", r"Backbone & Condition & Acc. & Calls/task & Tokens/task (k) & USD/task & USD/success \\", r"\midrule"]
for m in MODELS:
    for c in C4:
        a = main[m]["acc"][c]; v = main[m]["cost"][c]
        L.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & {pct(a)} & {v['calls']:.1f} & {v['tokens']/1000:.0f} & {v['usd']:.3f} & {v['usd']/a:.3f} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t6_cost.tex", "\n".join(L))
# T7 도달률
L = [r"\begin{tabular}{ll cccc c}", r"\toprule", r"Backbone & Condition & A & B & C & D & All \\", r"\midrule"]
for m in MODELS:
    for c in ("direct", "routing", "ingress"):
        v = reach[m][c]
        L.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & " + " & ".join(pct(v.get(k, {'rate': float('nan')})['rate']) for k in CLASSES) + f" & {pct(v['all']['rate'])} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t7_reach.tex", "\n".join(L))
# T8 템플릿
L = [r"\begin{tabular}{l r cccc c}", r"\toprule", r"Task type & $n$ & Direct & Routing & Ingress & Full-load & $\Delta_{\text{total}}$ \\", r"\midrule"]
for t, v in sorted(tpl.items(), key=lambda kv: -kv[1]["d_total"]["mean"]):
    a = v["acc"]; L.append(f"{t.replace('_', ' ')} & {v['n']} & {pct(a['direct'])} & {pct(a['routing'])} & {pct(a['ingress'])} & {pct(a['full_load'])} & {fmt_ci(v['d_total'])} \\\\")
L += [r"\bottomrule", r"\end{tabular}"]
tex("t8_templates.tex", "\n".join(L))

# ─────────────────────────── 그림 ───────────────────────────
def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig)
XL = list(CLASSES); KEYS = list(CLASSES)
# F1 등급별 정확도 (27B, DeepSeek)
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.3), sharey=True)
for ax, m in zip(axes, MODELS[:2]):
    bc = main[m]["by_class"]; x = np.arange(len(KEYS)); w = 0.26
    for i, c in enumerate(["direct", "routing", "ingress"]):
        ax.bar(x + (i - 1) * w, [bc[k]["acc"][c] for k in KEYS], w, color=COL[c], label=CN[c])
    ax.plot(x, [bc[k]["acc"]["full_load"] for k in KEYS], "D", color=COL["full_load"], ms=4, label="Full-load (ref.)", zorder=5)
    ax.set_xticks(x); ax.set_xticklabels([f"{l}\n(n={bc[k]['n']})" for l, k in zip(XL, KEYS)]); ax.set_title(MN[m]); ax.set_ylim(0, 1)
    ax.grid(axis="y", lw=0.3, alpha=0.5)
axes[0].set_ylabel("Exact-match accuracy"); axes[0].legend(loc="upper right", ncol=2, frameon=False)
save(fig, "f1_accuracy_by_class")
# F2 격차 분해 (Δ_route, Δ_sel) 등급별
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2), sharey=True)
for ax, m in zip(axes, MODELS[:2]):
    bc = main[m]["by_class"]; x = np.arange(len(KEYS)); w = 0.36
    for i, (dk, lab, col) in enumerate((("d_route", r"$\Delta_{route}$ (Routing $-$ Direct)", COL["routing"]), ("d_sel", r"$\Delta_{sel}$ (Ingress $-$ Routing)", COL["ingress"]))):
        v = [bc[k][dk] for k in KEYS]
        ax.bar(x + (i - .5) * w, [b["mean"] * 100 for b in v], w, color=col, label=lab,
               yerr=[[(b["mean"] - b["lo"]) * 100 for b in v], [(b["hi"] - b["mean"]) * 100 for b in v]], capsize=2, error_kw={"lw": .7})
    ax.axhline(0, color="k", lw=.6); ax.set_xticks(x); ax.set_xticklabels(XL); ax.set_title(MN[m]); ax.grid(axis="y", lw=.3, alpha=.5)
axes[0].set_ylabel("Accuracy gain (pp)"); axes[0].legend(loc="upper left", frameon=False)
save(fig, "f2_gap_decomposition")
# F3 규모: (a) G, (b) 걸린 그룹 수
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2))
ax = axes[0]
for c, g in CELLS:
    v = scale["cells"][c]["d_total_shared"]; ax.errorbar(g, v["mean"] * 100, yerr=[[(v["mean"] - v["lo"]) * 100], [(v["hi"] - v["mean"]) * 100]], fmt="o", color=COL["ingress"], capsize=3)
ax.set_xlabel("Number of groups $G$ in the organization"); ax.set_ylabel(r"$\Delta_{total}$ (pp)"); ax.set_xticks([5, 6, 10, 15]); ax.axhline(0, color="k", lw=.6); ax.set_ylim(0, 40)
ax.set_title("(a) Organization size (Qwen3.5-27B, days 1–10)"); ax.grid(lw=.3, alpha=.5)
ax = axes[1]; labs = list(scale["by_groups_involved"]); xs = np.arange(len(labs))
for i, (dk, lab, col) in enumerate((("d_route", r"$\Delta_{route}$", COL["routing"]), ("d_sel", r"$\Delta_{sel}$", COL["ingress"]))):
    v = [scale["by_groups_involved"][l][dk] for l in labs]
    ax.bar(xs + (i - .5) * .36, [b["mean"] * 100 for b in v], .36, color=col, label=lab, yerr=[[(b["mean"] - b["lo"]) * 100 for b in v], [(b["hi"] - b["mean"]) * 100 for b in v]], capsize=2, error_kw={"lw": .7})
ax.set_xticks(xs); ax.set_xticklabels([f"{l}\n(n={scale['by_groups_involved'][l]['n']})" for l in labs]); ax.set_xlabel("Groups a task spans"); ax.axhline(0, color="k", lw=.6)
ax.set_title("(b) Task breadth (all 27B cells)"); ax.legend(frameon=False); ax.grid(axis="y", lw=.3, alpha=.5)
save(fig, "f3_scale")
# F4 정확도 vs 비용 (7조건)
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for c in ALL7:
    v = var["cond"][c]; ax.scatter(v["tokens"] / 1000, v["acc"], s=40, color=COL[c], edgecolor="k", lw=.5, zorder=5)
    dx, dy = {"direct": (8, -0.03), "direct_relay": (8, 0.012), "routing": (8, -0.03), "retrieve": (8, 0.012), "sidecar": (-8, 0.02), "ingress": (8, 0.012), "full_load": (8, 0.012)}[c]
    ax.annotate(CN[c], (v["tokens"] / 1000 + dx, v["acc"] + dy), fontsize=7, ha="left" if dx > 0 else "right")
ax.set_xlabel("Tokens per task (k, all components)"); ax.set_ylabel("Exact-match accuracy"); ax.set_ylim(0.25, 0.65); ax.grid(lw=.3, alpha=.5)
ax.set_title("Qwen3.5-27B, base cell, days 1–10 (n=%d)" % var["n"], fontsize=7.5)
save(fig, "f4_accuracy_vs_cost")
# F5 일자 창 (3모델)
fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.0), sharey=True)
for ax, m in zip(axes, MODELS):
    bw = main[m]["by_window"]; labs = list(bw)
    for c in C4:
        ax.plot(range(3), [bw[l]["acc"][c] for l in labs], "-o", ms=3, color=COL[c], label=CN[c])
    ax.set_xticks(range(3)); ax.set_xticklabels(labs); ax.set_xlabel("Days"); ax.set_title(MN[m]); ax.grid(lw=.3, alpha=.5); ax.set_ylim(0, .8)
axes[0].set_ylabel("Accuracy"); axes[0].legend(frameon=False, fontsize=6.5)
save(fig, "f5_by_day_window")
# F6 담당자 도달률
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1), sharey=True)
for ax, m in zip(axes, MODELS[:2]):
    x = np.arange(4); w = .27
    for i, c in enumerate(("direct", "routing", "ingress")):
        ax.bar(x + (i - 1) * w, [reach[m][c].get(k, {"rate": 0})["rate"] for k in CLASSES], w, color=COL[c], label=CN[c])
    ax.set_xticks(x); ax.set_xticklabels([f"{k}\n(n={reach[m]['direct'].get(k, {'n': 0})['n']})" for k in CLASSES]); ax.set_title(MN[m]); ax.set_ylim(0, 1); ax.grid(axis="y", lw=.3, alpha=.5)
axes[0].set_ylabel("Cross-group needs whose\nholder was contacted")
h, l = axes[0].get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.22))
save(fig, "f6_responder_reach")
# F7 9B 등급별 (부록)
fig, ax = plt.subplots(figsize=(3.4, 2.1)); bc = main["qwen3.5-9b"]["by_class"]; x = np.arange(len(KEYS)); w = .26
for i, c in enumerate(["direct", "routing", "ingress"]):
    ax.bar(x + (i - 1) * w, [bc[k]["acc"][c] for k in KEYS], w, color=COL[c], label=CN[c])
ax.plot(x, [bc[k]["acc"]["full_load"] for k in KEYS], "D", color=COL["full_load"], ms=4, label="Full-load", zorder=5)
ax.set_xticks(x); ax.set_xticklabels(XL); ax.set_ylim(0, 1); ax.set_title("Qwen3.5-9B"); ax.legend(frameon=False, ncol=2); ax.grid(axis="y", lw=.3, alpha=.5); ax.set_ylabel("Accuracy")
save(fig, "f7_9b_by_class")

# ─────────────────────────── 수치 요약 (md) ───────────────────────────
md = ["# numbers (auto)", ""]
for m in MODELS:
    d = main[m]; md.append(f"## {MN[m]} base n={d['n']}: " + ", ".join(f"{c} {pct(d['acc'][c])}" for c in C4))
    md.append(f"  route {fmt_ci(d['d_route'])} p={d['mcn_route']['p']:.2g} ({d['mcn_route']}); sel {fmt_ci(d['d_sel'])} p={d['mcn_sel']['p']:.2g}; total {fmt_ci(d['d_total'])} p={d['mcn_total']['p']:.2g} ({d['mcn_total']}); vs full {fmt_ci(d['d_full'])}")
    for k in KEYS:
        b = d["by_class"][k]; md.append(f"  {k} n={b['n']}: " + ", ".join(f"{c} {pct(b['acc'][c])}" for c in C4) + f" | route {fmt_ci(b['d_route'])} | sel {fmt_ci(b['d_sel'])} | total {fmt_ci(b['d_total'])}")
    for w_, b in d["by_window"].items(): md.append(f"  days {w_} n={b['n']}: " + ", ".join(f"{c} {pct(b['acc'][c])}" for c in C4) + f" | total {fmt_ci(b['d_total'])}")
    md.append("  cost: " + "; ".join(f"{c} calls {v['calls']:.1f} tok {v['tokens']/1000:.0f}k usd {v['usd']:.3f} exh {pct(v['exh'])}% noans {pct(v['noans'])}%" for c, v in d["cost"].items()))
    md.append("  reach: " + "; ".join(f"{c} " + " ".join(f"{k}={pct(reach[m][c].get(k, {'rate': float('nan')})['rate'])}" for k in CLASSES + ['all']) for c in ("direct", "routing", "ingress")))
    md.append("  additions effect: " + "; ".join(f"{k}: with n={v['with_add_n']} ing {pct(v['with_add_acc'])} dir {pct(v['with_add_direct'])} / without n={v['without_n']} ing {pct(v['without_acc'])} dir {pct(v['without_direct'])}" for k, v in addeff[m].items()))
md.append(f"\n## scale shared templates ({len(shared_t)}): {sorted(shared_t)}")
for c, g in CELLS:
    v = scale["cells"][c]; md.append(f"  {c} G={g}: all n={v['n_all']} total {fmt_ci(v['d_total_all'])} | shared n={v['n_shared']} " + ", ".join(f"{k} {pct(v['acc_shared'][k])}" for k in C4) + f" total {fmt_ci(v['d_total_shared'])} route {fmt_ci(v['d_route_shared'])} sel {fmt_ci(v['d_sel_shared'])}")
for l, v in scale["by_groups_involved"].items(): md.append(f"  spans {l} n={v['n']}: " + ", ".join(f"{k} {pct(v['acc'][k])}" for k in C4) + f" total {fmt_ci(v['d_total'])} route {fmt_ci(v['d_route'])} sel {fmt_ci(v['d_sel'])}")
md.append(f"  pooled n={scale['pooled_n']}: " + "; ".join(f"{k} n={v['n']} " + " ".join(f"{c} {pct(v['acc'][c])}" for c in C4) + f" route {fmt_ci(v['d_route'])} sel {fmt_ci(v['d_sel'])}" for k, v in scale["pooled_by_class"].items()))
md.append(f"\n## variants n={var['n']}")
for c in ALL7:
    v = var["cond"][c]; md.append(f"  {c}: acc {pct(v['acc'])} A {pct(v['by_class']['A'])} B {pct(v['by_class']['B'])} C {pct(v['by_class']['C'])} D {pct(v['by_class']['D'])} cops {pct(v['c_ops'])} calls {v['calls']:.1f} tok {v['tokens']/1000:.0f}k usd {v['usd']:.3f}"
              + (f" | vs direct {fmt_ci(v['vs_direct'])}" if v["vs_direct"] else "") + (f" | vs ingress {fmt_ci(v['vs_ingress'])} p={v['mcn_vs_ingress']['p']:.2g}" if v["vs_ingress"] else "") + f" | reach {pct(reach7.get(c, float('nan')))}")
md.append("\n## gateway"); md += [f"  {k}: " + ", ".join(f"{a} {b:.3f}" if isinstance(b, float) else f"{a} {b}" for a, b in v.items()) for k, v in gws.items()]
md.append("\n## templates (27B pooled)"); md += [f"  {t} n={v['n']}: " + " ".join(f"{c} {pct(v['acc'][c])}" for c in C4) + f" total {fmt_ci(v['d_total'])}" for t, v in tpl.items()]
md.append(f"\n## ops: {NUM['ops']}")
(OUT / "numbers.md").write_text("\n".join(md), encoding="utf-8")
print("\n".join(md))
