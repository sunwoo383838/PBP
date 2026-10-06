"""f18_need_flow: need가 다섯 관문을 지나며 떨어져 나가는 흐름 (alluvial), 조건별 (27B 기준 셀, numbers3.json의 게이트 원장)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
OUT = Path("/root/project/g2g/output/paper"); N3 = json.load(open(OUT / "numbers3.json"))
STAGES = ["request", "route", "select", "state", "use"]
GATE2STAGE = {"L_req": "request", "L_route": "route", "L_sel.window": "select", "L_sel.answer": "select", "L_sel.search": "select", "L_sel.assembly": "select", "L_state": "state", "L_use": "use", "error": "use"}
SUB = {"select": ["L_sel.window", "L_sel.answer", "L_sel.search", "L_sel.assembly"]}
SUBL = {"L_sel.window": "window", "L_sel.answer": "answer", "L_sel.search": "search", "L_sel.assembly": "assembly"}
LOSSCOL = {"request": "#4e79a7", "route": "#e15759", "select": "#f28e2b", "state": "#59a14f", "use": "#9c9c9c"}
ALIVE = "#1f77b4"
plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42})
def band(ax, x0, x1, y0a, y0b, y1a, y1b, color, alpha=0.9, z=2):
    """x0에서 [y0a,y0b] 폭, x1에서 [y1a,y1b] 폭으로 흐르는 띠 (베지어)."""
    c = (x0 + x1) / 2
    verts = [(x0, y0a), (c, y0a), (c, y1a), (x1, y1a), (x1, y1b), (c, y1b), (c, y0b), (x0, y0b), (x0, y0a)]
    codes = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.LINETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4, MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts, codes), facecolor=color, edgecolor="none", alpha=alpha, zorder=z))
def draw(ax, loss, title, show_labels=True):
    """loss: gate → fraction. 살아남는 띠는 위쪽에 붙고, 손실 띠는 각 관문에서 아래로 빠진다."""
    alive = 1.0; x = 0.0; W = 1.0; gap = 0.12; top = 1.0
    ax.set_xlim(-0.05, len(STAGES) * (W + gap) + 0.9); ax.set_ylim(-0.16, 1.08); ax.axis("off"); ax.set_title(title, fontsize=8.5, loc="left")
    for i, stg in enumerate(STAGES):
        lost = sum(v for g, v in loss.items() if GATE2STAGE.get(g) == stg)
        x1 = x + W
        # 살아남는 띠: 관문 통과 후 폭이 alive-lost로 줄며 위쪽 정렬
        band(ax, x, x1, top, top - alive, top, top - (alive - lost), ALIVE, 0.85)
        # 손실 띠: 아래로 빠짐
        if lost > 0:
            y_drop_top = top - (alive - lost); y_drop_bot = top - alive
            band(ax, x, x1, y_drop_top, y_drop_bot, 0.08 + lost, 0.08, LOSSCOL[stg], 0.9, z=3)
            ax.text(x1 - 0.02, 0.08 + lost / 2, f"{lost*100:.0f}", ha="right", va="center", fontsize=7, color="white" if lost > 0.08 else "black", zorder=4)
            if stg in SUB and show_labels:
                sub = [(SUBL[g], loss.get(g, 0)) for g in SUB[stg] if loss.get(g, 0) >= 0.03]
                ax.text(x1 - W / 2 + 0.1, -0.01, " / ".join(f"{n} {v*100:.0f}" for n, v in sub), fontsize=5.3, color=LOSSCOL[stg], ha="center", va="top")
        ax.text(x + W / 2, 1.04, stg, ha="center", va="bottom", fontsize=7.5, color="#333")
        alive -= lost; x = x1 + gap
    ok = loss.get("ok", 0)
    band(ax, x - gap, x + 0.7, top, top - alive, top, top - alive, ALIVE, 0.85)
    ax.text(x + 0.72, top - alive / 2, f"delivered &\nused: {ok*100:.0f}", ha="left", va="center", fontsize=7.5, color=ALIVE, fontweight="bold")
    ax.text(-0.03, 0.5, "100 judged\nneeds", ha="right", va="center", fontsize=7, color="#333")
fig, axes = plt.subplots(3, 1, figsize=(6.9, 4.6))
for ax, cond, title in zip(axes, ["direct", "routing", "ingress"], ["Direct", "Routing (request mediation only)", "Ingress (pull by proxy)"]):
    draw(ax, N3["ledger"]["qwen3.5-27b"][cond]["loss"], f"{title}  —  Qwen3.5-27B, {N3['ledger']['qwen3.5-27b'][cond]['n_needs']} judged needs")
from matplotlib.patches import Patch
fig.legend([Patch(color=ALIVE)] + [Patch(color=LOSSCOL[s]) for s in STAGES], ["still alive"] + [f"lost at {s}" for s in STAGES], loc="lower center", ncol=6, frameon=False, bbox_to_anchor=(0.5, -0.02), fontsize=7)
fig.savefig(OUT / "figures" / "f18_need_flow.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / "f18_need_flow.png", bbox_inches="tight", dpi=200)
print("ok")
