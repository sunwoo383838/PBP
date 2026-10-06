"""효과가 가장 선명한 결과만 모은 본문용 합본 figure 2종.
 f23_headline     : (위) 클래스별 사다리 slope, (아래) 부분 상태 패널티 덤벨 — 27B·DeepSeek만
 f25_bounds_clear : Δ_total(Ingress−Direct)와 95% CI가 단조롭게 움직이는 세 축 — 발견 가능성 H, 과제 폭(그룹 수), 첫 접촉/재방문"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
OUT = Path("/root/project/g2g/output/paper"); FIG = OUT / "figures"
N = json.load(open(OUT / "numbers.json")); N4 = json.load(open(OUT / "numbers4.json"))
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
C4 = ["direct", "routing", "ingress", "full_load"]; CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73"}
MODELS = ["qwen3.5-27b", "deepseek-v4-flash"]; MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash"}
CC = {"A": "#444444", "B": "#d55e00", "C": "#cc79a7", "D": "#56b4e9"}
def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig); print("saved", name)

# ═════════════ F23 headline ═════════════
fig, axes = plt.subplots(2, 2, figsize=(7.1, 4.6), gridspec_kw={"hspace": 0.5, "wspace": 0.12, "height_ratios": [1.15, 1], "top": 0.9})
for j, m in enumerate(MODELS):
    bc = N["main"][m]["by_class"]
    # (위) 사다리 slope
    ax = axes[0, j]
    ly = {k: bc[k]["acc"]["ingress"] * 100 + 2.5 for k in "ABCD"}
    for k in sorted(ly, key=ly.get):                        # 아래에서 위로 7pp 간격 보장
        for k2 in sorted(ly, key=ly.get):
            if k2 != k and 0 <= ly[k2] - ly[k] < 7: ly[k2] = ly[k] + 7
    for k in "ABCD":
        ys = [bc[k]["acc"][c] * 100 for c in C4[:3]]; fl = bc[k]["acc"]["full_load"] * 100
        ax.plot([0, 1, 2], ys, "-o", color=CC[k], lw=1.7, ms=4.2, zorder=3); ax.plot([2, 3], [ys[-1], fl], ":", color=CC[k], lw=0.8, zorder=2); ax.plot(3, fl, "D", color=CC[k], ms=4, mec="white", mew=0.6, zorder=3)
        ax.text(2.1, ly[k], f"{k} (n={bc[k]['n']})", fontsize=6.3, color=CC[k], va="bottom", ha="left")
    ys = [N["main"][m]["acc"][c] * 100 for c in C4]; ax.plot([0, 1, 2], ys[:3], "-", color="black", lw=0.8, alpha=0.45, zorder=1); ax.plot(3, ys[3], "D", color="black", ms=3.5, alpha=0.5)
    ax.text(0.03, ys[0] + 2.5, "all", fontsize=6.3, color="black", alpha=0.6)
    ax.set_xticks(range(4)); ax.set_xticklabels(["Direct", "Routing", "Ingress", "Full-load\n(ref.)"]); ax.set_xlim(-0.3, 3.4); ax.set_ylim(0, 85)
    ax.axvspan(2.5, 3.4, color="#f2f2f2", zorder=0); ax.grid(axis="y", lw=0.3, alpha=0.5); ax.set_title(MN[m], pad=4)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    # (아래) 덤벨
    ax = axes[1, j]; n_notA = sum(bc[k]["n"] for k in "BCD"); psp_d = None
    for i, c in enumerate(C4):
        y = 3 - i; accA = bc["A"]["acc"][c] * 100; accN = sum(bc[k]["n"] * bc[k]["acc"][c] for k in "BCD") / n_notA * 100
        psp = accA - accN; psp_d = psp if c == "direct" else psp_d; rho = 1 - psp / psp_d
        ax.plot([accN, accA], [y, y], color=COL[c], lw=3.4, solid_capstyle="round", alpha=0.9, zorder=2)
        ax.plot(accA, y, "o", color=COL[c], ms=6.5, mec="white", mew=0.8, zorder=4); ax.plot(accN, y, "o", color="white", mec=COL[c], mew=1.6, ms=6.5, zorder=4)
        for k in "BCD": ax.plot(bc[k]["acc"][c] * 100, y - 0.27, marker="|", color=CC[k], ms=5, mew=1.1, zorder=3)
        ax.text(max((accA + accN) / 2, 27), y + 0.2, f"Π = {psp:.0f} pp" + ("" if c == "direct" else f",  ρ = {rho*100:+.0f}%"), ha="center", va="bottom", fontsize=6.3, color=COL[c] if c != "direct" else "#555")
    ax.set_yticks(range(4)); ax.set_yticklabels([CN[c] for c in C4][::-1]); ax.set_ylim(-0.7, 3.75); ax.set_xlim(0, 100); ax.grid(axis="x", lw=0.3, alpha=0.5)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0, 0].set_ylabel("Exact-match accuracy (%)"); axes[0, 1].tick_params(labelleft=False); axes[1, 1].tick_params(labelleft=False)
axes[1, 0].set_xlabel("Exact-match accuracy (%)"); axes[1, 1].set_xlabel("Exact-match accuracy (%)")
axes[0, 0].text(-0.02, 1.22, "(a) Accuracy by state class along the ladder", transform=axes[0, 0].transAxes, fontsize=8, fontweight="bold", va="bottom")
axes[1, 0].text(-0.02, 1.08, "(b) Partial-state penalty Π = Acc$_A$ − Acc$_{B∪C∪D}$ and recovery ρ", transform=axes[1, 0].transAxes, fontsize=8, fontweight="bold", va="bottom")
h = [Line2D([], [], marker="o", color="#444", ls="", ms=6), Line2D([], [], marker="o", color="white", mec="#444", mew=1.6, ls="", ms=6)] + [Line2D([], [], marker="|", color=CC[k], ls="", ms=6, mew=1.2) for k in "BCD"]
fig.legend(h, ["Acc$_A$ (record in the handler's context)", "Acc$_{B∪C∪D}$ (record elsewhere)", "class B", "class C", "class D"], loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.04), fontsize=6.8, handletextpad=0.4, columnspacing=1.2)
save(fig, "f23_headline")

# ═════════════ F25 bounds (clear axes only) ═════════════
B = N4["bounds"]; S = N["scale"]["by_groups_involved"]; R = N4["revisit"]
panels = [
    ("(a) Discoverability of the hardest\ncritical record", [("H0  log text", "H0"), ("H1  activity trace", "H1"), ("H2  referring utterance", "H2"), ("none  (DB / rules)", "none")],
     lambda m, k: B[m]["H"][k]["d_total"], lambda m, k: B[m]["H"][k]["n"], MODELS),
    ("(b) Groups a task spans\n(27B, all four cells pooled)", [("2 groups", "2"), ("3 groups", "3"), ("4 groups", "4"), ("5+ groups", "5+")],
     lambda m, k: S[k]["d_total"], lambda m, k: S[k]["n"], MODELS[:1]),
    ("(c) First contact vs. revisit\nof the same fact", [("first contact", "first"), ("revisit, unchanged", "revisit, unchanged"), ("revisit, changed", "revisit, changed")],
     lambda m, k: R[m][k]["d_total"], lambda m, k: R[m][k]["n"], MODELS),
]
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.3), gridspec_kw={"wspace": 0.75, "width_ratios": [1.1, 1, 1]})
for ax, (title, rows, get, getn, models) in zip(axes, panels):
    for i, (lab, key) in enumerate(rows):
        y = len(rows) - 1 - i
        for mi, m in enumerate(models):
            d = get(m, key); off = 0.17 if len(models) > 1 and mi == 0 else -0.17 if len(models) > 1 else 0
            ax.errorbar(d["mean"] * 100, y + off, xerr=[[(d["mean"] - d["lo"]) * 100], [(d["hi"] - d["mean"]) * 100]], fmt="o" if mi == 0 else "s", color=COL["ingress"] if mi == 0 else "#555", mfc=COL["ingress"] if mi == 0 else "white", ms=4.5, capsize=2, lw=1, zorder=3)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{lab}\n(n={getn(models[0], key)})" for lab, key in rows][::-1], fontsize=6.8)
    ax.axvline(0, color="black", lw=0.7); ax.set_xlim(-15, 70); ax.grid(axis="x", lw=0.3, alpha=0.5); ax.set_title(title, fontsize=8, loc="left")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.supxlabel("Ingress − Direct, paired accuracy difference (pp) with 95% CI", fontsize=8, y=-0.02)
fig.legend([Line2D([], [], marker="o", color=COL["ingress"], ls="", ms=5), Line2D([], [], marker="s", color="#555", mfc="white", ls="", ms=5)], ["Qwen3.5-27B", "DeepSeek-V4-Flash"], loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.17), fontsize=7)
save(fig, "f25_bounds_clear")
