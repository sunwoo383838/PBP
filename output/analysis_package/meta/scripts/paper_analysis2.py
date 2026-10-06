"""논문 그림 2부: 메커니즘·실패 귀속·동역학·과제 유형. 입력: analysis_package + numbers.json(1부) + gates/(게이트 원장·컨텍스트 집계).
출력: output/paper/figures/f8~f14, tables/t1x_main_extended.tex, t9_failure_modes.tex, t10_claim_map.md, numbers2.json"""
import csv, gzip, json, math
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PKG = Path("/root/project/g2g/output/analysis_package"); T = PKG / "tables"; OUT = Path("/root/project/g2g/output/paper"); G = Path("/root/project/g2g_main/gates")
NUM1 = json.load(open(OUT / "numbers.json"))
MODELS = ["qwen3.5-27b", "deepseek-v4-flash", "qwen3.5-9b"]; MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
C4 = ["direct", "routing", "ingress", "full_load"]; APX = ["direct_relay", "retrieve", "sidecar"]; ALL7 = C4 + APX
CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load", "direct_relay": "Direct+relay", "retrieve": "Retrieve", "sidecar": "Sidecar"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73", "direct_relay": "#bbbbbb", "retrieve": "#d55e00", "sidecar": "#56b4e9"}
CLASSES = ["A", "B", "C", "D"]; SEEDS = ["s12", "s13", "s14"]
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
NUM = {}
def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig)
def pct(x): return f"{x*100:.1f}"

# ─────────────────────────── 데이터 ───────────────────────────
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1"]
for r in rows:
    r["exact"] = int(r["exact"]); r["day"] = int(r["day"]); r["c_ops"] = int(r["c_ops"]); r["n_groups"] = int(r["n_groups"])
    r["tokens"] = int(r["tokens_requester"]) + int(r["tokens_responder"]) + int(r["tokens_boundary"]); r["calls"] = int(r["llm_calls"])
    r["cost"] = float(r["cost_usd_est"]); r["exh"] = int(r["budget_exhausted"]); r["noans"] = int(r["error"] not in ("", "None"))
by = defaultdict(lambda: defaultdict(dict))
for r in rows: by[(r["cell"], r["model"], r["seed"])][r["condition"]][r["task_id"]] = r
def common(cell, model, conds, maxday=None):
    out = []
    for s in SEEDS:
        d = defaultdict(dict)
        for (c2, m2, s2), dd in by.items():
            if (c2, m2, s2) == (cell, model, s):
                for c, ts in dd.items(): d[c].update(ts)
        if not all(c in d for c in conds): continue
        for t in sorted(set.intersection(*[set(d[c]) for c in conds])):
            if maxday and d[conds[0]][t]["day"] > maxday: continue
            out.append({c: d[c][t] for c in conds})
    return out
RNG = np.random.default_rng(0)
def boot(items, a, b, B=2000):
    d = np.array([x[a]["exact"] - x[b]["exact"] for x in items], float)
    if len(d) == 0: return None
    idx = RNG.integers(0, len(d), (B, len(d))); m = np.sort(d[idx].mean(1))
    return {"mean": float(d.mean()), "lo": float(m[int(.025 * B)]), "hi": float(m[int(.975 * B)]), "n": int(len(d))}
def gold_of(cell, seed):
    name = f"scenarios__D5_{seed}_T45" if cell == "base" else next(p.name for p in (PKG / "meta/scenarios").glob(f"scenarios_g__{cell}__D*_{seed}_T45"))
    return {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / "meta/scenarios" / name / "gold.jsonl.gz", "rt", encoding="utf-8"))}
GOLD = {(c, s): gold_of(c, s) for c in ("base", "R1", "D3", "R3") for s in SEEDS}
WORK = {}
for s in SEEDS:
    WORK[("base", s)] = {w["wid"]: w for w in (json.loads(l) for l in gzip.open(PKG / "meta/scenarios" / f"scenarios__D5_{s}_T45/work.jsonl.gz", "rt", encoding="utf-8"))}

# ─────────────────────────── F8 사다리 증분 forest plot ───────────────────────────
main = NUM1["main"]; scale = NUM1["scale"]; var = NUM1["variants"]
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.9), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.75})
ax = axes[0]
rungs = [("d_route", "Direct → Routing\n(request mediation)", COL["routing"]), ("d_sel", "Routing → Ingress\n(information selection)", COL["ingress"])]
groups = [("Qwen3.5-27B", main["qwen3.5-27b"], "o"), ("DeepSeek-V4-Flash", main["deepseek-v4-flash"], "s"), ("Qwen3.5-9B", main["qwen3.5-9b"], "^"),
          ("G=5 (R1)", scale["cells"]["R1"], "v"), ("G=6 (D3)", scale["cells"]["D3"], "<"), ("G=15 (R3)", scale["cells"]["R3"], ">")]
ypos = []; ylab = []; y = 0
for rk, rlab, col in rungs:
    ax.axhspan(y - 0.5, y + len(groups) - 0.5, color=col, alpha=0.06)
    for gl, gd, mk in groups:
        key = rk if rk in gd else rk + "_shared"; b = gd[key]
        ax.errorbar(b["mean"] * 100, y, xerr=[[(b["mean"] - b["lo"]) * 100], [(b["hi"] - b["mean"]) * 100]], fmt=mk, color=col, ms=4, capsize=2, lw=0.8)
        ypos.append(y); ylab.append(gl); y += 1
    y += 0.6
ax.axvline(0, color="k", lw=0.6); ax.set_yticks(ypos); ax.set_yticklabels(ylab); ax.invert_yaxis(); ax.set_xlabel("Paired accuracy difference (pp), 95% CI")
ax.text(0.98, 0.93, "request mediation", transform=ax.transAxes, ha="right", va="top", color=COL["routing"], fontsize=8, fontweight="bold")
ax.text(0.98, 0.44, "information selection", transform=ax.transAxes, ha="right", va="top", color=COL["ingress"], fontsize=8, fontweight="bold")
ax.set_title("(a) Each rung of the ladder, by backbone and organization size"); ax.grid(axis="x", lw=0.3, alpha=0.5)
ax = axes[1]
y = 0; ypos = []; ylab = []
for m in MODELS[:2]:
    for k, lab in (("A", "class A"), ("c_ops", "$C_{ops}$")):
        for rk, _, col in rungs:
            b = main[m]["by_class"][k][rk]
            ax.errorbar(b["mean"] * 100, y, xerr=[[(b["mean"] - b["lo"]) * 100], [(b["hi"] - b["mean"]) * 100]], fmt="o" if m == MODELS[0] else "s", color=col, ms=4, capsize=2, lw=0.8)
            ypos.append(y); ylab.append(f"{'27B' if m == MODELS[0] else 'DS'} · {lab} · {'med.' if rk == 'd_route' else 'sel.'}"); y += 1
        y += 0.4
ax.axvline(0, color="k", lw=0.6); ax.set_yticks(ypos); ax.set_yticklabels(ylab); ax.invert_yaxis(); ax.set_xlabel("pp, 95% CI")
ax.set_title("(b) Class A (control) vs. $C_{ops}$"); ax.grid(axis="x", lw=0.3, alpha=0.5)
save(fig, "f8_rung_forest")

# ─────────────────────────── F9 반사실 실패 귀속 ───────────────────────────
def canon(a):
    if not isinstance(a, dict): return None
    a = dict(a)
    for f in ("assets", "recover_assets"):
        if isinstance(a.get(f), list) and all(isinstance(x, str) for x in a[f]): a[f] = sorted(a[f])
    def nz(v):
        if isinstance(v, bool) or v is None: return v
        if isinstance(v, (int, float)): return float(v)
        if isinstance(v, list): return [nz(x) for x in v]
        if isinstance(v, dict): return {k: nz(x) for k, x in v.items()}
        return v
    return json.dumps(nz(a), sort_keys=True, ensure_ascii=False)
CF = ["stale", "partial", "neardup", "wrong_owner"]
def failure_mode(r, g):
    if r["exact"]: return "correct"
    if r["noans"]: return "no answer"
    try: a = json.loads(r["answer_json"])
    except Exception: return "no answer"
    ca = canon(a); cf = g.get("counterfactual") or {}
    hits = [k for k in CF if cf.get(k, {}).get("example_answer") is not None and canon(cf[k]["example_answer"]) == ca]
    if not hits: return "other wrong"
    return "stale/partial" if set(hits) >= {"stale", "partial"} else {"stale": "stale", "partial": "partial", "neardup": "near-dup", "wrong_owner": "wrong-owner"}[hits[0]]
MODES = ["correct", "stale", "partial", "stale/partial", "near-dup", "wrong-owner", "other wrong", "no answer"]
MCOL = {"correct": "#2ca25f", "stale": "#e6550d", "partial": "#fdae6b", "stale/partial": "#fee6ce", "near-dup": "#756bb1", "wrong-owner": "#bcbddc", "other wrong": "#bdbdbd", "no answer": "#636363"}
fm = {}
for m in MODELS:
    it = common("base", m, C4, 15); fm[m] = {"all": {}, "by_class": {}}
    for c in C4:
        cnt = Counter(failure_mode(x[c], GOLD[("base", x[c]["seed"])][x[c]["task_id"]]) for x in it); n = len(it)
        fm[m]["all"][c] = {k: cnt[k] / n for k in MODES}
        for k in CLASSES:
            sub = [x for x in it if x[c]["state_class"] == k]
            cnt = Counter(failure_mode(x[c], GOLD[("base", x[c]["seed"])][x[c]["task_id"]]) for x in sub)
            fm[m]["by_class"].setdefault(c, {})[k] = {kk: cnt[kk] / max(1, len(sub)) for kk in MODES}
    # 민감 과제만: 반사실 답이 정답과 다른 과제에서의 stale 비율
    for c in C4:
        sens = [x for x in it if GOLD[("base", x[c]["seed"])][x[c]["task_id"]].get("sensitive", {}).get("stale")]
        fm[m]["all"][c]["stale_rate_on_stale_sensitive"] = sum(failure_mode(x[c], GOLD[("base", x[c]["seed"])][x[c]["task_id"]]) in ("stale", "stale/partial") for x in sens) / max(1, len(sens))
        fm[m]["all"][c]["n_stale_sensitive"] = len(sens)
it7 = common("base", "qwen3.5-27b", ALL7, 10); fm["variants"] = {}
for c in ALL7:
    cnt = Counter(failure_mode(x[c], GOLD[("base", x[c]["seed"])][x[c]["task_id"]]) for x in it7); fm["variants"][c] = {k: cnt[k] / len(it7) for k in MODES}
NUM["failure_modes"] = fm
fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.4), gridspec_kw={"width_ratios": [1, 1, 1.6]})
for ax, m in zip(axes[:2], MODELS[:2]):
    x = np.arange(len(C4)); bottom = np.zeros(len(C4))
    for k in MODES:
        v = np.array([fm[m]["all"][c][k] for c in C4]) * 100
        ax.bar(x, v, 0.65, bottom=bottom, color=MCOL[k], label=k, edgecolor="white", lw=0.4); bottom += v
    ax.set_xticks(x); ax.set_xticklabels([CN[c] for c in C4], rotation=20); ax.set_title(MN[m]); ax.set_ylim(0, 100)
axes[0].set_ylabel("Share of tasks (%)")
ax = axes[2]; x = np.arange(len(ALL7)); bottom = np.zeros(len(ALL7))
for k in MODES:
    v = np.array([fm["variants"][c][k] for c in ALL7]) * 100
    ax.bar(x, v, 0.65, bottom=bottom, color=MCOL[k], edgecolor="white", lw=0.4); bottom += v
ax.set_xticks(x); ax.set_xticklabels([CN[c] for c in ALL7], rotation=30, ha="right"); ax.set_title("Variants (27B, days 1–10)"); ax.set_ylim(0, 100)
fig.legend([Patch(color=MCOL[k]) for k in MODES], MODES, loc="lower center", ncol=8, frameon=False, bbox_to_anchor=(0.5, -0.2))
save(fig, "f9_failure_modes")
# 27B 등급별 실패 양상 (부록용)
fig, axes = plt.subplots(1, 4, figsize=(6.9, 2.1), sharey=True)
for ax, k in zip(axes, CLASSES):
    x = np.arange(len(C4)); bottom = np.zeros(len(C4))
    for mode in MODES:
        v = np.array([fm["qwen3.5-27b"]["by_class"][c][k][mode] for c in C4]) * 100
        ax.bar(x, v, 0.65, bottom=bottom, color=MCOL[mode], edgecolor="white", lw=0.4); bottom += v
    ax.set_xticks(x); ax.set_xticklabels([CN[c][:4] for c in C4], rotation=0); ax.set_title(f"class {k} (n={main['qwen3.5-27b']['by_class'][k]['n']})"); ax.set_ylim(0, 100)
axes[0].set_ylabel("Share of tasks (%)")
fig.legend([Patch(color=MCOL[k]) for k in MODES], MODES, loc="lower center", ncol=8, frameon=False, bbox_to_anchor=(0.5, -0.12))
save(fig, "f9b_failure_modes_by_class_27b")

# ─────────────────────────── F10 사실 나이 (days since the needed fact last changed) ───────────────────────────
DBDAY = {}
for s in SEEDS:
    for l in open(f"/root/project/g2g_main/scenarios/D5_{s}_T45/private/db_versions.jsonl"):
        x = json.loads(l); DBDAY[(s, x["key"], x["v"])] = x["day"]
def fact_age(seed, g):
    days = []
    for n in g["needs"]:
        for sv in n["sources"]:
            if sv["type"] == "frag": days.append(sv["frag"]["day"])
            elif sv["type"] == "db" and (seed, sv["key"], sv["v"]) in DBDAY: days.append(DBDAY[(seed, sv["key"], sv["v"])])
    return g["day"] - max(days) if days else None
BINS = [(0, 0, "0"), (1, 1, "1"), (2, 3, "2–3"), (4, 7, "4–7"), (8, 99, "8+")]
age = {}
for m in MODELS:
    it = common("base", m, C4, 15); age[m] = {}
    for lo, hi, lab in BINS:
        sub = [x for x in it if (a := fact_age(x["direct"]["seed"], GOLD[("base", x["direct"]["seed"])][x["direct"]["task_id"]])) is not None and lo <= a <= hi]
        age[m][lab] = {"n": len(sub), "acc": {c: (sum(x[c]["exact"] for x in sub) / len(sub) if sub else float("nan")) for c in C4},
                       "stale": {c: (sum(failure_mode(x[c], GOLD[("base", x[c]["seed"])][x[c]["task_id"]]) in ("stale", "stale/partial") for x in sub) / len(sub) if sub else float("nan")) for c in C4},
                       "d_total": boot(sub, "ingress", "direct")}
NUM["fact_age"] = age
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2))
for ax, m in zip(axes, MODELS[:2]):
    labs = [b[2] for b in BINS]
    for c in C4:
        ax.plot(range(len(labs)), [age[m][l]["acc"][c] * 100 for l in labs], "-o", ms=3, color=COL[c], label=CN[c])
    ax.set_xticks(range(len(labs))); ax.set_xticklabels([f"{l}\n(n={age[m][l]['n']})" for l in labs]); ax.set_title(MN[m]); ax.grid(lw=.3, alpha=.5); ax.set_ylim(0, 100)
    ax.set_xlabel("Days since the needed fact last changed")
axes[0].set_ylabel("Accuracy (%)"); axes[0].legend(frameon=False, ncol=2)
save(fig, "f10_fact_age")

# ─────────────────────────── F11 규모·시간 곡선 (조건별 선) ───────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2))
ax = axes[0]; cells = [("R1", 5), ("D3", 6), ("base", 10), ("R3", 15)]
for c in C4:
    ax.plot([g for _, g in cells], [scale["cells"][cl]["acc_shared"][c] * 100 for cl, _ in cells], "-o", ms=3.5, color=COL[c], label=CN[c])
ax.set_xticks([5, 6, 10, 15]); ax.set_xlabel("Number of groups $G$"); ax.set_ylabel("Accuracy (%)"); ax.set_ylim(0, 80); ax.grid(lw=.3, alpha=.5)
ax.set_title("(a) Organization size (27B, days 1–10)"); ax.legend(frameon=False, ncol=2)
ax = axes[1]
for m, ls in (("qwen3.5-27b", "-"), ("deepseek-v4-flash", "--")):
    for c in C4:
        ax.plot(range(3), [main[m]["by_window"][w]["acc"][c] * 100 for w in ("1-5", "6-10", "11-15")], ls, marker="o", ms=3, color=COL[c], label=f"{CN[c]} ({MN[m].split('-')[0]})" if c == "ingress" else None)
ax.set_xticks(range(3)); ax.set_xticklabels(["days 1–5", "6–10", "11–15"]); ax.set_title("(b) Horizon"); ax.set_ylim(0, 80); ax.grid(lw=.3, alpha=.5)
from matplotlib.lines import Line2D
ax.legend([Line2D([], [], color="k", ls="-"), Line2D([], [], color="k", ls="--")], ["Qwen3.5-27B", "DeepSeek-V4-Flash"], frameon=False, loc="lower left")
save(fig, "f11_scaling_lines")

# ─────────────────────────── F13a 응답자 부하 vs 자기 과제 정확도 ───────────────────────────
inbound = defaultdict(int)
with gzip.open(T / "messages.csv.gz", "rt", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["kind"] == "request" and r["via"] == "agent" and r["to_agent"]: inbound[(r["run_id"], r["to_agent"])] += 1
load = {}
for m in MODELS[:2]:
    load[m] = {}
    for c in C4:
        per = defaultdict(lambda: [0, 0])
        for s in SEEDS:
            for t, r in by[("base", m, s)].get(c, {}).items():
                ag = WORK[("base", s)][t]["assignee"]; per[(r["run_id"], ag)][0] += r["exact"]; per[(r["run_id"], ag)][1] += 1
        bins = defaultdict(lambda: [0, 0, 0])
        for (run, ag), (k, n) in per.items():
            q = inbound.get((run, ag), 0); b = "0" if q == 0 else "1–5" if q <= 5 else "6–15" if q <= 15 else "16+"
            bins[b][0] += k; bins[b][1] += n; bins[b][2] += 1
        load[m][c] = {b: {"acc": v[0] / v[1], "n_tasks": v[1], "n_agents": v[2]} for b, v in bins.items()}
NUM["responder_load"] = load
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1), sharey=True); LB = ["0", "1–5", "6–15", "16+"]
for ax, m in zip(axes, MODELS[:2]):
    x = np.arange(len(LB)); w = 0.2
    for i, c in enumerate(C4):
        ax.bar(x + (i - 1.5) * w, [load[m][c].get(b, {"acc": 0})["acc"] * 100 for b in LB], w, color=COL[c], label=CN[c])
    ax.set_xticks(x); ax.set_xticklabels([f"{b}\n(n={sum(load[m][c].get(b, {'n_tasks': 0})['n_tasks'] for c in C4)})" for b in LB]); ax.set_title(MN[m]); ax.grid(axis="y", lw=.3, alpha=.5)
    ax.set_xlabel("Inbound cross-group requests served by the agent (15 days)")
axes[0].set_ylabel("Accuracy on the agent's\nown tasks (%)"); axes[0].legend(frameon=False, ncol=2)
save(fig, "f13a_responder_load")
# F13b 요청자 컨텍스트 창 구성 (첫 호출, 일자별): 원문 창 항목 중 다른 과제 유래 비율, 토큰
ctx = {}
for m in MODELS[:2]:
    ctx[m] = {}
    for c in C4:
        agg = defaultdict(lambda: Counter())
        for s in SEEDS:
            f = G / f"context__{m}__{c}__{s}.json"
            if not f.exists(): continue
            d = json.load(open(f))["requester"]
            for day, v in d.items():
                if int(day) > 15: continue
                agg[int(day)]["n"] += v["n"]; agg[int(day)]["raw_tokens"] += v["raw_tokens"]; agg[int(day)]["summary_tokens"] += v["summary_tokens"]
                for k, cnt in v["items"].items(): agg[int(day)][k] += cnt
        ctx[m][c] = {day: {"raw_tokens_per_call": a["raw_tokens"] / max(1, a["n"]), "summary_tokens_per_call": a["summary_tokens"] / max(1, a["n"]),
                           "other_task_share_raw": a["other_task|raw"] / max(1, a["other_task|raw"] + a["history|raw"] + a["own_task|raw"]),
                           "n": a["n"]} for day, a in sorted(agg.items())}
NUM["context"] = ctx
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1))
for ax, key, lab in zip(axes, ("other_task_share_raw", "raw_tokens_per_call"), ("Share of raw-window entries that belong\nto other tasks (served or own earlier)", "Raw-window tokens at first call")):
    for m, ls in (("qwen3.5-27b", "-"), ("deepseek-v4-flash", "--")):
        for c in C4:
            days = sorted(ctx[m][c]); ax.plot(days, [ctx[m][c][d][key] * (100 if key.endswith("share_raw") else 1) for d in days], ls, color=COL[c], lw=1, label=CN[c] if m == MODELS[0] else None)
    ax.set_xlabel("Day"); ax.set_ylabel(lab + (" (%)" if key.endswith("share_raw") else "")); ax.grid(lw=.3, alpha=.5)
axes[0].legend(frameon=False, ncol=2, fontsize=6.5); axes[0].set_title("(a) Task residue in the requester window"); axes[1].set_title("(b) Window fill (solid 27B, dashed DeepSeek)")
save(fig, "f13b_context_residue")

# ─────────────────────────── F14 과제 유형 × 조건 히트맵 + 등급 구성 ───────────────────────────
pool = common("base", "qwen3.5-27b", C4, 15) + sum((common(c, "qwen3.5-27b", C4, 10) for c in ("R1", "D3", "R3")), [])
tpls = sorted({x["direct"]["template"] for x in pool}, key=lambda t: -(NUM1["templates"][t]["d_total"]["mean"]))
acc = np.array([[sum(x[c]["exact"] for x in pool if x["direct"]["template"] == t) / sum(1 for x in pool if x["direct"]["template"] == t) for c in C4] for t in tpls]) * 100
mix = np.array([[sum(1 for x in pool if x["direct"]["template"] == t and x["direct"]["state_class"] == k) for k in CLASSES] for t in tpls], float); mix = mix / mix.sum(1, keepdims=True) * 100
fig, axes = plt.subplots(1, 2, figsize=(6.9, 4.0), gridspec_kw={"width_ratios": [1.3, 1]}, sharey=True)
ax = axes[0]; im = ax.imshow(acc, cmap="Blues", vmin=0, vmax=100, aspect="auto")
for i in range(len(tpls)):
    for j in range(len(C4)): ax.text(j, i, f"{acc[i, j]:.0f}", ha="center", va="center", fontsize=7, color="white" if acc[i, j] > 55 else "black")
ax.set_xticks(range(len(C4))); ax.set_xticklabels([CN[c] for c in C4]); ax.set_yticks(range(len(tpls)))
ax.set_yticklabels([f"{t.replace('_', ' ')} (n={sum(1 for x in pool if x['direct']['template'] == t)}, Δ={NUM1['templates'][t]['d_total']['mean']*100:+.0f})" for t in tpls], fontsize=7)
ax.set_title("(a) Accuracy (%) by task type, 27B, all cells"); plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
ax = axes[1]; left = np.zeros(len(tpls)); KC = {"A": "#c7e9c0", "B": "#fdd0a2", "C": "#9ecae1", "D": "#3182bd"}
for j, k in enumerate(CLASSES):
    ax.barh(range(len(tpls)), mix[:, j], left=left, color=KC[k], label=f"class {k}", edgecolor="white", lw=0.4); left += mix[:, j]
ax.set_xlim(0, 100); ax.set_xlabel("State-class mix (%)"); ax.set_title("(b) What each task type reads"); ax.legend(frameon=False, ncol=4, fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, -0.2)); ax.invert_yaxis()
save(fig, "f14_template_heatmap")
NUM["template_mix"] = {t: {"acc": dict(zip(C4, acc[i].tolist())), "class_mix": dict(zip(CLASSES, mix[i].tolist()))} for i, t in enumerate(tpls)}

# ─────────────────────────── T1 확장: 교차 메시지, 성공당 토큰 ───────────────────────────
cross = defaultdict(int); reqs = defaultdict(int)
with gzip.open(T / "messages.csv.gz", "rt", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["kind"] == "request":
            reqs[(r["run_id"], r["task_id"])] += 1
            if r["crossing"] == "1": cross[(r["run_id"], r["task_id"])] += 1
ext = {}
for m in MODELS:
    it = common("base", m, C4, 15); ext[m] = {}
    for c in C4:
        n = len(it); a = sum(x[c]["exact"] for x in it) / n
        needs = sum(sum(1 for nd in GOLD[("base", x[c]["seed"])][x[c]["task_id"]]["needs"] if nd["group"] != GOLD[("base", x[c]["seed"])][x[c]["task_id"]]["root"]) for x in it)
        ext[m][c] = {"acc": a, "crossings_per_task": sum(cross[(x[c]["run_id"], x[c]["task_id"])] for x in it) / n,
                     "crossings_per_need": sum(cross[(x[c]["run_id"], x[c]["task_id"])] for x in it) / max(1, needs),
                     "tokens_per_task": sum(x[c]["tokens"] for x in it) / n, "tokens_per_success": sum(x[c]["tokens"] for x in it) / max(1, sum(x[c]["exact"] for x in it)),
                     "exh": sum(x[c]["exh"] for x in it) / n, "noans": sum(x[c]["noans"] for x in it) / n,
                     "stale": fm[m]["all"][c]["stale"] + fm[m]["all"][c]["stale/partial"], "reach": NUM1["reach"][m].get(c, {}).get("all", {}).get("rate")}
NUM["main_extended"] = ext
L = [r"\begin{tabular}{ll r r r r r r r}", r"\toprule",
     r"Backbone & Condition & Acc. (\%) & Reach (\%) & Stale ans. (\%) & No ans. (\%) & Crossings/need & Tokens/task (k) & Tokens/correct (k) \\", r"\midrule"]
for m in MODELS:
    for c in C4:
        v = ext[m][c]
        L.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & {pct(v['acc'])} & {pct(v['reach']) if v['reach'] is not None else '--'} & {pct(v['stale'])} & {pct(v['noans'])} & "
                 f"{v['crossings_per_need']:.2f} & {v['tokens_per_task']/1000:.0f} & {v['tokens_per_success']/1000:.0f} \\\\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
(OUT / "tables" / "t1x_main_extended.tex").write_text("\n".join(L), encoding="utf-8")
# T9 실패 양상 표
L = [r"\begin{tabular}{ll " + "r" * len(MODES) + "}", r"\toprule", "Backbone & Condition & " + " & ".join(MODES) + r" \\", r"\midrule"]
for m in MODELS:
    for c in C4:
        L.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & " + " & ".join(pct(fm[m]['all'][c][k]) for k in MODES) + r" \\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
(OUT / "tables" / "t9_failure_modes.tex").write_text("\n".join(L), encoding="utf-8")
json.dump(NUM, open(OUT / "numbers2.json", "w"), ensure_ascii=False, indent=1, default=float)

md = ["# numbers2 (auto)"]
for m in MODELS:
    md.append(f"## {MN[m]} failure modes (base, 1-15)")
    for c in C4: md.append(f"  {c}: " + ", ".join(f"{k} {pct(fm[m]['all'][c][k])}" for k in MODES) + f" | stale on stale-sensitive {pct(fm[m]['all'][c]['stale_rate_on_stale_sensitive'])} (n={fm[m]['all'][c]['n_stale_sensitive']})")
    md.append(f"  extended: " + "; ".join(f"{c} cross/need {ext[m][c]['crossings_per_need']:.2f} tok/correct {ext[m][c]['tokens_per_success']/1000:.0f}k" for c in C4))
    md.append(f"  fact age: " + "; ".join(f"{l} n={age[m][l]['n']} " + " ".join(f"{c} {pct(age[m][l]['acc'][c])}" for c in C4) + (f" total {age[m][l]['d_total']['mean']*100:+.1f}" if age[m][l]['d_total'] else "") for l in age[m]))
    if m in load: md.append(f"  responder load: " + "; ".join(f"{c} " + " ".join(f"{b}={pct(load[m][c][b]['acc'])}({load[m][c][b]['n_tasks']})" for b in LB if b in load[m][c]) for c in C4))
md.append("## variants failure modes: " + "; ".join(f"{c} " + " ".join(f"{k} {pct(fm['variants'][c][k])}" for k in MODES) for c in ALL7))
(OUT / "numbers2.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md))
