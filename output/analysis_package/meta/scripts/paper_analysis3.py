"""논문 그림 3부: need 단위 게이트 원장(gates/*.json, 휴리스틱 채점기) → 생존 곡선·게이트별 손실 히트맵·등급/폭별 손실 구성·
가시 상태(전달된 결정 필수 조각 비율) vs 정답. 출력 f12_*, f4b_coverage, tables/t11_gates.tex, numbers3.json"""
import json, glob, re
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

G = Path("/root/project/g2g_main/gates"); OUT = Path("/root/project/g2g/output/paper"); PKG = Path("/root/project/g2g/output/analysis_package")
MODELS = ["qwen3.5-27b", "deepseek-v4-flash", "qwen3.5-9b"]; MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
C4 = ["direct", "routing", "ingress", "full_load"]; APX = ["direct_relay", "retrieve", "sidecar"]
CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load", "direct_relay": "Direct+relay", "retrieve": "Retrieve", "sidecar": "Sidecar"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73", "direct_relay": "#bbbbbb", "retrieve": "#d55e00", "sidecar": "#56b4e9"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
GATES = ["L_req", "L_route", "L_sel.window", "L_sel.answer", "L_sel.search", "L_sel.assembly", "L_state", "L_use", "error", "ok"]
GL = {"L_req": "request", "L_route": "route", "L_sel.window": "sel:\nwindow", "L_sel.answer": "sel:\nanswer", "L_sel.search": "sel:\nsearch", "L_sel.assembly": "sel:\nassembly", "L_state": "state", "L_use": "use", "error": "error", "ok": "ok"}
STAGE = {"L_req": "request", "L_route": "route", "L_sel.window": "select", "L_sel.answer": "select", "L_sel.search": "select", "L_sel.assembly": "select", "L_state": "state", "L_use": "use", "error": "use", "ok": "ok"}
STAGES = ["request", "route", "select", "state", "use"]
def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig)

# ─────────────────────────── 적재 ───────────────────────────
runs = {}                                                                  # (exp, cell, model, cond, seed) → {"needs": [...], "tasks": {tid: task}}
for f in sorted(G.glob("*.json")):
    m = re.match(r"(main|gcell|appendix)__(\w+)__([\w.\-]+)__(\w+)__(s\d+)\.json", f.name)
    if not m: continue
    d = json.load(open(f))
    needs = [n for n in d["needs"] if n["gate"] != "unjudged" and n["scored"]]
    for n in needs:
        n["gate"] = "error" if n["gate"].startswith("E_") else n["gate"]
    runs[m.groups()] = {"needs": needs, "tasks": {t["task_id"]: t for t in d["tasks"]}}
NUM = {"n_runs": len(runs)}
GOLD = {}
def gold(cell, seed):
    if (cell, seed) not in GOLD:
        name = f"scenarios__D5_{seed}_T45" if cell == "base" else next(p.name for p in (PKG / "meta/scenarios").glob(f"scenarios_g__{cell}__D*_{seed}_T45"))
        import gzip
        GOLD[(cell, seed)] = {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / "meta/scenarios" / name / "gold.jsonl.gz", "rt", encoding="utf-8"))}
    return GOLD[(cell, seed)]

def pool(exp, cell, model, cond):
    out = []
    for (e, c, m, co, s), v in runs.items():
        if (e, c, m, co) == (exp, cell, model, cond): out += [{**n, "seed": s, "task": v["tasks"].get(n["task_id"], {})} for n in v["needs"]]
    return out
def dist(needs):
    c = Counter(n["gate"] for n in needs); n = max(1, len(needs))
    return {g: c[g] / n for g in GATES}, len(needs)
def survival(d):
    alive = 1.0; out = [1.0]
    for st in STAGES:
        alive -= sum(v for g, v in d.items() if STAGE.get(g) == st and g != "ok"); out.append(alive)
    return out                                                              # [start, after request, after route, after select, after state, after use]

# ─────────────────────────── 집계 ───────────────────────────
ledger = {}
for m in MODELS:
    ledger[m] = {}
    for c in C4:
        needs = pool("main", "base", m, c); d, n = dist(needs)
        ledger[m][c] = {"n_needs": n, "loss": d, "survival": survival(d),
                        "by_class": {k: dist([x for x in needs if x["class"] == k]) for k in "ABCD"}}
ledger["variants"] = {c: dict(zip(("loss", "n_needs"), dist(pool("appendix", "base", "qwen3.5-27b", c)))) for c in APX}
for c in C4: ledger["variants"][c] = dict(zip(("loss", "n_needs"), dist([x for x in pool("main", "base", "qwen3.5-27b", c) if gold("base", x["seed"])[x["task_id"]]["day"] <= 10])))
ledger["by_breadth"] = {}
for c in ("direct", "ingress"):
    needs = pool("main", "base", "qwen3.5-27b", c) + sum((pool("gcell", cell, "qwen3.5-27b", c) for cell in ("R1", "D3", "R3")), [])
    for lo, hi, lab in ((2, 2, "2"), (3, 3, "3"), (4, 4, "4"), (5, 99, "5+")):
        sub = [x for x in needs if lo <= x["task"].get("n_groups", 0) <= hi]
        ledger["by_breadth"].setdefault(c, {})[lab] = dict(zip(("loss", "n_needs"), dist(sub)))
NUM["ledger"] = ledger

# ─────────────────────────── F12 생존 곡선 + 게이트별 손실 히트맵 ───────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1, 1.3], "wspace": 0.5})
ax = axes[0]; xs = ["judged\nneeds", "after\nrequest", "after\nroute", "after\nselect", "after\nstate", "after\nuse\n(= ok)"]
for c in C4:
    sv = ledger["qwen3.5-27b"][c]["survival"]; ax.plot(range(6), [v * 100 for v in sv], "-o", ms=3, color=COL[c], label=f"{CN[c]} (n={ledger['qwen3.5-27b'][c]['n_needs']})")
    ax.text(4.75, sv[-1] * 100 + 2, f"{sv[-1]*100:.0f}", color=COL[c], fontsize=6.5, va="bottom", ha="right")
ax.set_xticks(range(6)); ax.set_xticklabels(xs); ax.set_ylabel("Need events still alive (%)"); ax.set_ylim(0, 100); ax.grid(lw=.3, alpha=.5)
ax.set_title("(a) Survival of needs across gates (Qwen3.5-27B)"); ax.legend(frameon=False, fontsize=6.5)
ax = axes[1]; rows_ = [(m, c) for m in MODELS[:2] for c in C4]; cols = GATES[:-1]
mat = np.array([[ledger[m][c]["loss"][g] * 100 for g in cols] for m, c in rows_])
im = ax.imshow(mat, cmap="OrRd", vmin=0, vmax=max(40, mat.max()), aspect="auto")
for i in range(len(rows_)):
    for j in range(len(cols)): ax.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=6.5, color="white" if mat[i, j] > 25 else "black")
ax.set_xticks(range(len(cols))); ax.set_xticklabels([GL[g] for g in cols], fontsize=6); ax.set_yticks(range(len(rows_))); ax.set_yticklabels([f"{'27B' if m == MODELS[0] else 'DS'} {CN[c]}" for m, c in rows_], fontsize=7)
ax.axhline(3.5, color="k", lw=0.6); ax.set_title("(b) First failing gate, per 100 judged needs"); plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
save(fig, "f12_gate_ledger")

# ─────────────────────────── F12c 등급별·폭별 손실 구성 (Direct vs Ingress, 27B) ───────────────────────────
SC = {"L_req": "#4e79a7", "L_route": "#e15759", "L_sel.window": "#f28e2b", "L_sel.answer": "#ffbe7d", "L_sel.search": "#b07aa1", "L_sel.assembly": "#d4a6c8", "L_state": "#59a14f", "L_use": "#bab0ac", "error": "#333333"}
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.4), sharey=True)
def stacked(ax, groups, getter, title, xlabel):
    x = np.arange(len(groups)); w = 0.36
    for i, c in enumerate(("direct", "ingress")):
        bottom = np.zeros(len(groups))
        for g in GATES[:-1]:
            v = np.array([getter(c, k)[0].get(g, 0) * 100 for k in groups])
            ax.bar(x + (i - .5) * w, v, w, bottom=bottom, color=SC[g], edgecolor="k" if c == "ingress" else "none", lw=0.4, hatch="//" if c == "ingress" else None); bottom += v
    ax.set_xticks(x); ax.set_xticklabels([f"{k} (n={getter('direct', k)[1]})" for k in groups]); ax.set_title(title); ax.set_xlabel(xlabel); ax.grid(axis="y", lw=.3, alpha=.5)
stacked(axes[0], list("ABCD"), lambda c, k: ledger["qwen3.5-27b"][c]["by_class"][k], "(a) By state class (plain: Direct, hatched: Ingress)", "State class")
stacked(axes[1], ["2", "3", "4", "5+"], lambda c, k: (ledger["by_breadth"][c][k]["loss"], ledger["by_breadth"][c][k]["n_needs"]), "(b) By groups a task spans (all 27B cells)", "Groups spanned")
axes[0].set_ylabel("Needs lost per 100 (by first failing gate)")
fig.legend([Patch(color=SC[g]) for g in GATES[:-1]], [GL[g].replace("\n", " ") for g in GATES[:-1]], loc="lower center", ncol=9, frameon=False, bbox_to_anchor=(0.5, -0.2), fontsize=6.5)
save(fig, "f12c_gate_composition")

# ─────────────────────────── F4b 가시 상태(전달된 결정 필수 조각 비율) vs 정답 ───────────────────────────
cov = {}
for m in MODELS[:2]:
    cov[m] = {}
    for c in C4:
        per_task = defaultdict(lambda: [0, 0, None])                        # delivered frags, judged frags, exact
        for n in pool("main", "base", m, c):
            fr = [f for f in n.get("frags", []) if f.get("state") in ("delivered", "stale", "missing")]
            t = per_task[(n["seed"], n["task_id"])]; t[0] += sum(f["state"] == "delivered" for f in fr); t[1] += len(fr); t[2] = n["task"].get("exact")
        bins = defaultdict(lambda: [0, 0])
        for (s, tid), (dl, jd, ex) in per_task.items():
            if jd == 0 or ex is None: continue
            r = dl / jd; b = "0" if r == 0 else "1" if r == 1 else "partial"
            bins[b][0] += int(ex); bins[b][1] += 1
        cov[m][c] = {b: {"acc": v[0] / v[1], "n": v[1]} for b, v in bins.items()}
NUM["coverage"] = cov
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2), sharey=True); B = ["0", "partial", "1"]
for ax, m in zip(axes, MODELS[:2]):
    x = np.arange(3); w = 0.2
    for i, c in enumerate(C4):
        ax.bar(x + (i - 1.5) * w, [cov[m][c].get(b, {"acc": 0})["acc"] * 100 for b in B], w, color=COL[c], label=CN[c])
        for j, b in enumerate(B):
            if b in cov[m][c]: ax.text(x[j] + (i - 1.5) * w, cov[m][c][b]["acc"] * 100 + 1.5, str(cov[m][c][b]["n"]), ha="center", fontsize=5.5, color="#444")
    ax.set_xticks(x); ax.set_xticklabels(["none", "some", "all"]); ax.set_xlabel("Decision-critical records delivered to the requester"); ax.set_title(MN[m]); ax.grid(axis="y", lw=.3, alpha=.5); ax.set_ylim(0, 100)
axes[0].set_ylabel("Task accuracy (%)"); axes[0].legend(frameon=False, ncol=2)
save(fig, "f4b_coverage_vs_accuracy")

# ─────────────────────────── T11 ───────────────────────────
L = [r"\begin{tabular}{ll r " + "r" * len(GATES) + "}", r"\toprule", r"Backbone & Condition & Needs & " + " & ".join(g.replace("_", r"\_") for g in GATES) + r" \\", r"\midrule"]
for m in MODELS:
    for c in C4:
        d = ledger[m][c]; L.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & {d['n_needs']} & " + " & ".join(f"{d['loss'][g]*100:.1f}" for g in GATES) + r" \\")
    L.append(r"\midrule")
L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
(OUT / "tables" / "t11_gates.tex").write_text("\n".join(L), encoding="utf-8")
json.dump(NUM, open(OUT / "numbers3.json", "w"), ensure_ascii=False, indent=1, default=float)
md = ["# numbers3 (gate ledger, heuristic)"]
for m in MODELS:
    for c in C4:
        d = ledger[m][c]; md.append(f"{MN[m]} {c} n={d['n_needs']}: " + " ".join(f"{g}={d['loss'][g]*100:.1f}" for g in GATES) + " | survival " + " ".join(f"{v*100:.0f}" for v in d["survival"]))
        md.append("   by class: " + "; ".join(f"{k} n={d['by_class'][k][1]} ok={d['by_class'][k][0]['ok']*100:.0f} route={d['by_class'][k][0]['L_route']*100:.0f} sel={sum(d['by_class'][k][0][g] for g in GATES if g.startswith('L_sel'))*100:.0f} state={d['by_class'][k][0]['L_state']*100:.0f} use={d['by_class'][k][0]['L_use']*100:.0f}" for k in "ABCD"))
md.append("variants (1-10d): " + "; ".join(f"{c} n={v['n_needs']} ok={v['loss']['ok']*100:.0f} route={v['loss']['L_route']*100:.0f} sel={sum(v['loss'][g] for g in GATES if g.startswith('L_sel'))*100:.0f} use={v['loss']['L_use']*100:.0f}" for c, v in ledger["variants"].items()))
md.append("breadth: " + "; ".join(f"{c} {k} n={v['n_needs']} ok={v['loss']['ok']*100:.0f} route={v['loss']['L_route']*100:.0f} sel={sum(v['loss'][g] for g in GATES if g.startswith('L_sel'))*100:.0f}" for c in ("direct", "ingress") for k, v in ledger["by_breadth"][c].items()))
for m in MODELS[:2]: md.append(f"coverage {MN[m]}: " + "; ".join(f"{c} " + " ".join(f"{b}={v['acc']*100:.0f}({v['n']})" for b, v in cov[m][c].items()) for c in C4))
(OUT / "numbers3.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md))
