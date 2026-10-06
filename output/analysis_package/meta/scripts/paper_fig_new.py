"""새 figure 4종 (numbers*.json + 5_task_level.csv에서만 계산, 로그 재처리 없음).
 f20_penalty_dumbbell : 조건별 Acc_A ↔ Acc_¬A 덤벨 = 부분 상태 패널티 Π, 회복률 ρ (백본 3개)
 f21_outcome_transition : (seed, task) 쌍 단위 Direct→Ingress 결과 전이, 클래스별 (구조됨/잃음/둘 다 ✓/둘 다 ✗)
 f22_task_raster : 과제 × 조건 정답 래스터 (클래스순 정렬) — 어디가 켜지는지 한눈에
 f24_ladder_slope : 조건 사다리(Direct→Routing→Ingress)를 따라 클래스별 정확도 slope (A 평탄, B/C/D 상승)"""
import csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

OUT = Path("/root/project/g2g/output/paper"); FIG = OUT / "figures"
N = json.load(open(OUT / "numbers.json"))
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
C4 = ["direct", "routing", "ingress", "full_load"]
CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load (ref.)"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73"}
MODELS = ["qwen3.5-27b", "deepseek-v4-flash", "qwen3.5-9b"]
MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
CLASS_COL = {"B": "#d55e00", "C": "#cc79a7", "D": "#56b4e9"}
def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig); print("saved", name)

# ───────────── 과제 수준 데이터 (기준 셀) ─────────────
rows = [r for r in csv.DictReader(open(OUT.parent / "5_task_level.csv")) if r["cell"] == "base"]
score = defaultdict(dict)                                   # (model, cond) → {(seed, task): exact}
meta = {}                                                   # (seed, task) → (class, c_ops)
for r in rows:
    score[(r["model"], r["condition"])][(r["seed"], r["task_id"])] = int(r["exact"]); meta[(r["seed"], r["task_id"])] = (r["state_class"], r["c_ops"] == "1")

# ═════════════ F20 덤벨: 부분 상태 패널티 ═════════════
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.3), sharex=True, gridspec_kw={"wspace": 0.12})
for ax, m in zip(axes, MODELS):
    bc = N["main"][m]["by_class"]; n_notA = sum(bc[k]["n"] for k in "BCD")
    psp_d = None
    for i, c in enumerate(C4):
        y = 3 - i; accA = bc["A"]["acc"][c] * 100; acc_notA = sum(bc[k]["n"] * bc[k]["acc"][c] for k in "BCD") / n_notA * 100
        psp = accA - acc_notA; psp_d = psp if c == "direct" else psp_d; rho = 1 - psp / psp_d
        ax.plot([acc_notA, accA], [y, y], color=COL[c], lw=3.2, solid_capstyle="round", alpha=0.9, zorder=2)
        ax.plot(accA, y, "o", color=COL[c], ms=6.5, mec="white", mew=0.8, zorder=4)
        ax.plot(acc_notA, y, "o", color="white", mec=COL[c], mew=1.6, ms=6.5, zorder=4)
        for k in "BCD":                                    # 클래스별 위치 (작은 눈금)
            ax.plot(bc[k]["acc"][c] * 100, y - 0.27, marker="|", color=CLASS_COL[k], ms=5, mew=1.1, zorder=3)
        txt = f"Π = {psp:.0f} pp" + ("" if c == "direct" else f",  ρ = {rho*100:+.0f}%")
        ax.text(max((accA + acc_notA) / 2, 27), y + 0.2, txt, ha="center", va="bottom", fontsize=6.3, color=COL[c] if c != "direct" else "#555")
    ax.set_yticks(range(4)); ax.set_yticklabels([CN[c].replace(" (ref.)", "") for c in C4][::-1]); ax.set_ylim(-0.7, 3.75)
    ax.set_xlim(0, 100); ax.grid(axis="x", lw=0.3, alpha=0.5); ax.set_title(MN[m])
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[1].set_xlabel("Exact-match accuracy (%)"); axes[1].tick_params(labelleft=False); axes[2].tick_params(labelleft=False)
h = [Line2D([], [], marker="o", color="#444", ls="", ms=6), Line2D([], [], marker="o", color="white", mec="#444", mew=1.6, ls="", ms=6)] + [Line2D([], [], marker="|", color=CLASS_COL[k], ls="", ms=6, mew=1.2) for k in "BCD"]
fig.legend(h, ["class A (record in handler's context)", "classes B∪C∪D (record elsewhere)", "class B", "class C", "class D"], loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.2), fontsize=6.8, handletextpad=0.4, columnspacing=1.2)
save(fig, "f20_penalty_dumbbell")

# ═════════════ F21 결과 전이 (Direct → Ingress, Routing → Ingress), 클래스별 ═════════════
def transition(m, a, b, keys):
    sa, sb = score[(m, a)], score[(m, b)]; out = {"both": 0, "rescued": 0, "lost": 0, "neither": 0}
    for k in keys:
        x, y = sa[k], sb[k]; out["both" if x and y else "rescued" if y else "lost" if x else "neither"] += 1
    return out
OUTC = [("both", "#1b7837", "correct in both"), ("rescued", "#0072b2", "rescued (✗ → ✓)"), ("lost", "#d62728", "lost (✓ → ✗)"), ("neither", "#dddddd", "wrong in both")]
groups = [("A", lambda k: meta[k][0] == "A"), ("B", lambda k: meta[k][0] == "B"), ("C", lambda k: meta[k][0] == "C"), ("D", lambda k: meta[k][0] == "D"), ("$C_{ops}$", lambda k: meta[k][1])]
fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.2), sharey=True, gridspec_kw={"wspace": 0.08})
for ax, m in zip(axes, MODELS[:2]):
    keys_all = list(score[(m, "direct")].keys())
    for gi, (lab, pred) in enumerate(groups):
        keys = [k for k in keys_all if pred(k)]
        for pi, (a, b) in enumerate((("direct", "ingress"), ("routing", "ingress"))):
            t = transition(m, a, b, keys); n = len(keys); y = (len(groups) - 1 - gi) * 2.2 + (0.55 if pi == 0 else -0.55)
            left = 0
            for key, col, _ in OUTC:
                w = t[key] / n * 100; ax.barh(y, w, left=left, height=0.95, color=col, edgecolor="white", lw=0.4)
                if key in ("rescued", "lost") and w >= 3: ax.text(left + w / 2, y, f"{w:.0f}", ha="center", va="center", fontsize=6, color="white", fontweight="bold")
                left += w
            ax.text(101, y, "D→I" if pi == 0 else "R→I", va="center", fontsize=5.8, color="#555")
    ax.set_yticks([(len(groups) - 1 - gi) * 2.2 for gi in range(len(groups))]); ax.set_yticklabels([f"{lab}\n(n={sum(1 for k in keys_all if pred(k))})" for lab, pred in groups], fontsize=7)
    ax.set_xlim(0, 100); ax.set_title(MN[m]); ax.grid(axis="x", lw=0.3, alpha=0.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.supxlabel("Share of (scenario, task) pairs (%)", fontsize=8, y=-0.02)
fig.legend([Patch(color=c) for _, c, _ in OUTC], [l for _, _, l in OUTC], loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.17), fontsize=7)
save(fig, "f21_outcome_transition")

# ═════════════ F22 과제 래스터 ═════════════
# 행: (seed, task) 쌍을 클래스(A,B,C,D) → C_ops → Direct 정답 → Ingress 정답 순으로 정렬. 열: 4조건. 색: 정답/오답.
fig, axes = plt.subplots(1, 3, figsize=(7.1, 3.6), gridspec_kw={"wspace": 0.42})
cmap = ListedColormap(["#f2f2f2", "#0072b2"])
for ax, m in zip(axes, MODELS):
    keys = list(score[(m, "direct")].keys())
    order = sorted(keys, key=lambda k: ("ABCD".index(meta[k][0]), -score[(m, "direct")][k], -score[(m, "routing")][k], -score[(m, "ingress")][k], -score[(m, "full_load")][k]))
    mat = np.array([[score[(m, c)][k] for c in C4] for k in order])
    ax.imshow(mat, cmap=cmap, aspect="auto", interpolation="nearest", vmin=0, vmax=1)
    ax.set_xticks(range(4)); ax.set_xticklabels(["Direct", "Routing", "Ingress", "Full"], fontsize=7); ax.set_yticks([])
    pos = 0
    for k in "ABCD":
        n = sum(1 for key in order if meta[key][0] == k)
        if pos: ax.axhline(pos - 0.5, color="black", lw=0.7)
        ax.text(-0.62, pos + n / 2, f"{k}\n{n}", ha="right", va="center", fontsize=6.8); pos += n
    for j, c in enumerate(C4): ax.text(j, -0.5 - len(order) * 0.012, f"{mat[:, j].mean()*100:.0f}%", ha="center", va="bottom", fontsize=6.5, color=COL[c], fontweight="bold")
    ax.set_title(MN[m], pad=14)
    for s in ("top", "right", "left", "bottom"): ax.spines[s].set_visible(False)
fig.text(0.5, 0.0, "Rows: 427 (scenario, task) pairs per backbone, grouped by state class and sorted by outcome; blue = exact match. Column heads: accuracy.", ha="center", va="top", fontsize=6.8)
save(fig, "f22_task_raster")

# ═════════════ F24 사다리 slope: 클래스별 정확도가 조건 사다리를 따라 어떻게 움직이나 ═════════════
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.3), sharey=True, gridspec_kw={"wspace": 0.1})
CL = [("A", "#444444", "A"), ("B", CLASS_COL["B"], "B"), ("C", CLASS_COL["C"], "C"), ("D", CLASS_COL["D"], "D")]
for ax, m in zip(axes, MODELS):
    bc = N["main"][m]["by_class"]; xs = [0, 1, 2]
    for k, col, lab in CL:
        ys = [bc[k]["acc"][c] * 100 for c in C4[:3]]; ax.plot(xs, ys, "-o", color=col, lw=1.6, ms=4, label=f"class {lab} (n={bc[k]['n']})", zorder=3)
        ax.plot(3, bc[k]["acc"]["full_load"] * 100, "D", color=col, ms=4, mec="white", mew=0.6, zorder=3)
        ax.plot([2, 3], [ys[-1], bc[k]["acc"]["full_load"] * 100], ":", color=col, lw=0.8, zorder=2)
    ys = [N["main"][m]["acc"][c] * 100 for c in C4]; ax.plot([0, 1, 2], ys[:3], "-", color="black", lw=0.8, alpha=0.5); ax.plot(3, ys[3], "D", color="black", ms=3.5, alpha=0.6)
    ax.text(2.08, ys[2] + 1.5, "all", fontsize=6.3, color="black", alpha=0.7)
    ax.set_xticks(range(4)); ax.set_xticklabels(["Direct", "Routing", "Ingress", "Full-load\n(ref.)"]); ax.set_xlim(-0.3, 3.4); ax.set_ylim(0, 85)
    ax.axvspan(2.5, 3.4, color="#f2f2f2", zorder=0); ax.set_title(MN[m]); ax.grid(axis="y", lw=0.3, alpha=0.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].set_ylabel("Exact-match accuracy (%)"); fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.22), fontsize=7)
save(fig, "f24_ladder_slope")
