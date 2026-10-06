"""f12·f13a 재렌더 (라벨 겹침 수정). 데이터는 numbers3.json / numbers2.json 그대로."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
OUT = Path("/root/project/g2g/output/paper"); FIG = OUT / "figures"
N2 = json.load(open(OUT / "numbers2.json")); N3 = json.load(open(OUT / "numbers3.json"))
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
C4 = ["direct", "routing", "ingress", "full_load"]; CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73"}
MODELS = ["qwen3.5-27b", "deepseek-v4-flash"]; MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash"}
GATES = ["L_req", "L_route", "L_sel.window", "L_sel.answer", "L_sel.search", "L_sel.assembly", "L_state", "L_use", "error"]
GL = {"L_req": "request", "L_route": "route", "L_sel.window": "sel: window", "L_sel.answer": "sel: answer", "L_sel.search": "sel: search", "L_sel.assembly": "sel: assembly", "L_state": "state", "L_use": "use", "error": "error"}
def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig); print("saved", name)
# F12
led = N3["ledger"]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1, 1.3], "wspace": 0.5})
ax = axes[0]; xs = ["judged", "req.", "route", "select", "state", "use"]
for c in C4:
    sv = led["qwen3.5-27b"][c]["survival"]; ax.plot(range(6), [v * 100 for v in sv], "-o", ms=3, color=COL[c], label=f"{CN[c]} (n={led['qwen3.5-27b'][c]['n_needs']})")
    ax.text(5.08, sv[-1] * 100, f"{sv[-1]*100:.0f}", color=COL[c], fontsize=6.5, va="center", ha="left")
ax.set_xticks(range(6)); ax.set_xticklabels(xs, fontsize=6.8); ax.set_xlabel("needs alive after each gate"); ax.set_xlim(-0.2, 5.5); ax.set_ylabel("Need events still alive (%)"); ax.set_ylim(0, 100); ax.grid(lw=.3, alpha=.5)
ax.set_title("(a) Survival of needs across gates (Qwen3.5-27B)"); ax.legend(frameon=False, fontsize=6.5)
ax = axes[1]; rows_ = [(m, c) for m in MODELS for c in C4]
mat = np.array([[led[m][c]["loss"][g] * 100 for g in GATES] for m, c in rows_])
im = ax.imshow(mat, cmap="OrRd", vmin=0, vmax=max(40, mat.max()), aspect="auto")
for i in range(len(rows_)):
    for j in range(len(GATES)): ax.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", fontsize=6.5, color="white" if mat[i, j] > 25 else "black")
ax.set_xticks(range(len(GATES))); ax.set_xticklabels([GL[g] for g in GATES], fontsize=6.3, rotation=35, ha="right", rotation_mode="anchor")
ax.set_yticks(range(len(rows_))); ax.set_yticklabels([f"{'27B' if m == MODELS[0] else 'DS'} {CN[c]}" for m, c in rows_], fontsize=7)
ax.axhline(3.5, color="k", lw=0.6); ax.set_title("(b) First failing gate, per 100 judged needs"); plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
save(fig, "f12_gate_ledger")
# F13a
load = N2["responder_load"]; LB = ["0", "1–5", "6–15", "16+"]
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2), sharey=True)
for ax, m in zip(axes, MODELS):
    x = np.arange(len(LB)); w = 0.2
    for i, c in enumerate(C4):
        ax.bar(x + (i - 1.5) * w, [load[m][c].get(b, {"acc": 0})["acc"] * 100 for b in LB], w, color=COL[c], label=CN[c])
    ax.set_xticks(x); ax.set_xticklabels([f"{b}\n(n={sum(load[m][c].get(b, {'n_tasks': 0})['n_tasks'] for c in C4)})" for b in LB], fontsize=7); ax.set_title(MN[m]); ax.grid(axis="y", lw=.3, alpha=.5)
fig.supxlabel("Inbound cross-group requests served by the agent over 15 days (n = agent-tasks)", fontsize=8, y=-0.12)
axes[0].set_ylabel("Accuracy on the agent's\nown tasks (%)"); axes[0].legend(frameon=False, ncol=2)
save(fig, "f13a_responder_load")
# F13b 요청자 창의 잔류물 (라벨 겹침 수정: 짧은 y라벨, 패널 간격)
ctx = N2["context"]
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.2), gridspec_kw={"wspace": 0.3})
for ax, key, lab, title in zip(axes, ("other_task_share_raw", "raw_tokens_per_call"), ("Raw-window entries from\nother tasks (%)", "Raw-window tokens\nat first call"), ("(a) Task residue in the requester window", "(b) Window fill")):
    for m, ls in zip(MODELS, ("-", "--")):
        for c in C4:
            days = sorted(ctx[m][c], key=int); ax.plot([int(d) for d in days], [ctx[m][c][d][key] * (100 if key.endswith("share_raw") else 1) for d in days], ls, color=COL[c], lw=1, label=CN[c] if m == MODELS[0] else None)
    ax.set_xlabel("Day"); ax.set_ylabel(lab, fontsize=7.5); ax.grid(lw=.3, alpha=.5); ax.set_title(title, fontsize=8)
axes[0].legend(frameon=False, ncol=2, fontsize=6.5, loc="lower right")
axes[1].plot([], [], "-", color="#333", label="Qwen3.5-27B"); axes[1].plot([], [], "--", color="#333", label="DeepSeek-V4-Flash"); axes[1].legend(frameon=False, fontsize=6.5, loc="lower right")
save(fig, "f13b_context_residue")
