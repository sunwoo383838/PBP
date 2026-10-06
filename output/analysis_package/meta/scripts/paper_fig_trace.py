"""f19_trace_examples: 실제 로그에서 뽑은 과제 두 개의 통신 그래프 (Direct vs Ingress). 값은 WAL(27B, 시드 12) 그대로.
 row 1: W-00065 (class D) — 떠난 작업자의 메모에만 있는 자산. row 2: W-00016 (class C) — 여러 담당자에 흩어진 예산 차감."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse
OUT = Path("/root/project/g2g/output/paper")
plt.rcParams.update({"font.size": 7, "pdf.fonttype": 42})
GREEN, GRAY, RED, BLUE, YEL, YEDGE = "#c7e9c0", "#e0e0e0", "#d62728", "#0072b2", "#fff3c4", "#b58900"

def box(ax, x, y, w, h, text, fc="white", ec="#333", ls="-", fs=6.3, bold=False, z=3):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, ls=ls, lw=0.9, zorder=z))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else "normal", zorder=z + 1)
def arrow(ax, p, q, color="#333", ls="-", lw=0.9, rad=0.0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, shrinkA=2, shrinkB=2, connectionstyle=f"arc3,rad={rad}"), zorder=4)
def label(ax, x, y, text, color="#333", fs=5.8, ha="center", va="center"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, zorder=6, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.9))
def cyl(ax, x, y, w, h, text, fs=5.6):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01,rounding_size=0.05", fc=YEL, ec=YEDGE, lw=0.9, zorder=3))
    ax.add_patch(Ellipse((x, y + h / 2), w, 0.16, fc=YEL, ec=YEDGE, lw=0.9, zorder=3.5)); ax.text(x, y - 0.03, text, ha="center", va="center", fontsize=fs, zorder=4)
def group(ax, x0, x1, y0, y1, name):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.02,rounding_size=0.15", fc="#f7f9fb", ec="#8aa", lw=0.8, ls="--", zorder=1))
    ax.text(x0 + 0.12, y1 - 0.08, name, ha="left", va="top", fontsize=6.5, color="#467", fontweight="bold", zorder=2)
def panel(ax, title): ax.set_xlim(0, 10); ax.set_ylim(0.3, 7.0); ax.axis("off"); ax.set_title(title, fontsize=7.5, loc="left", pad=3)

fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.6))
# ───────── (a) W-00065 Direct ─────────
ax = axes[0, 0]; panel(ax, "(a) Direct — W-00065, class D:\nthe record is a departed worker's note")
box(ax, 1.4, 4.2, 2.2, 1.0, "fin-tyo.a1\n(requester)")
group(ax, 3.6, 9.7, 0.5, 6.4, "IT-TYO group")
box(ax, 6.0, 5.3, 2.4, 0.8, "it-tyo.c0  ★\ncard handler", fc=GRAY)
box(ax, 6.0, 3.5, 2.4, 0.8, "it-tyo.w00182\n(left day 6)", ec=RED, ls="--")
cyl(ax, 8.2, 1.6, 2.4, 1.2, "group log\n[E10] day 5, by w00182:\nA-TYO-46864 → Mori")
ax.annotate("", xy=(7.6, 2.25), xytext=(7.0, 3.1), arrowprops=dict(arrowstyle="-", color=RED, lw=0.7, ls=":"), zorder=2)
label(ax, 5.1, 2.65, "wrote the note on day 5;\nnot yet in the DB", color=RED, fs=5.0)
arrow(ax, (2.5, 4.55), (4.8, 5.3)); label(ax, 3.4, 5.45, "Q: Mori's assets?")
arrow(ax, (4.8, 5.05), (2.5, 4.2), ls="--"); label(ax, 4.4, 4.25, "2 assets (DB view)")
box(ax, 1.4, 2.0, 2.2, 0.85, "answer: 2 assets  ✗\ngold: 3", fc="#fde0dd", ec=RED, bold=True)
# ───────── (b) W-00065 Ingress ─────────
ax = axes[0, 1]; panel(ax, "(b) Ingress — W-00065:\nrecovered from the group log")
box(ax, 1.2, 4.2, 2.0, 1.0, "fin-tyo.a1\n(requester)")
group(ax, 3.2, 9.7, 0.5, 6.4, "IT-TYO group")
box(ax, 4.7, 4.2, 1.7, 1.0, "gateway\n(intake desk)", fc="#dbe9f6", ec=BLUE, bold=True)
box(ax, 7.9, 5.5, 2.2, 0.75, "it-tyo.c0  ★", fc=GRAY)
box(ax, 7.9, 3.95, 2.2, 0.75, "it-tyo.w00182\n(left day 6)", ec=RED, ls="--")
cyl(ax, 7.9, 1.7, 2.6, 1.1, "group log\n[E10] day 5: A-TYO-46864 → Mori")
arrow(ax, (2.2, 4.4), (3.85, 4.4)); label(ax, 3.0, 4.65, "Q")
arrow(ax, (5.55, 4.6), (6.8, 5.4), lw=0.8); label(ax, 5.9, 5.3, "select c0", fs=5.5)
arrow(ax, (6.8, 5.15), (5.55, 4.35), ls="--", lw=0.8); label(ax, 6.55, 4.55, "2 assets", fs=5.5)
arrow(ax, (4.9, 3.7), (6.6, 2.0), color=YEDGE, lw=0.8); label(ax, 5.15, 2.55, "search\nrecords", color=YEDGE, fs=5.5)
arrow(ax, (6.6, 1.55), (4.4, 3.65), color=YEDGE, ls="--", lw=0.8); label(ax, 7.9, 0.85, "found: [E10] A-TYO-46864", color=YEDGE, fs=5.5)
arrow(ax, (3.85, 4.0), (2.2, 4.0), color=BLUE, lw=1.5); label(ax, 3.25, 3.3, "1 reply + 1 addition,\ncited [E10]", color=BLUE)
box(ax, 1.2, 2.0, 2.0, 0.85, "answer: 3 assets  ✓", fc=GREEN, ec="#2a7", bold=True)
# ───────── (c) W-00016 Direct ─────────
ax = axes[1, 0]; panel(ax, "(c) Direct — W-00016, class C:\ndeductions spread over members")
box(ax, 1.4, 4.2, 2.2, 1.0, "legal-tyo.a5\n(requester)")
group(ax, 3.6, 9.7, 0.5, 6.4, "FIN-TYO group")
box(ax, 6.0, 5.5, 2.2, 0.72, "fin-tyo.a1  ★", fc=GRAY)
box(ax, 6.0, 4.4, 2.2, 0.72, "fin-tyo.a2  ●", fc=GREEN)
box(ax, 6.0, 3.3, 2.2, 0.72, "fin-tyo.a3  ●", fc=GREEN)
box(ax, 6.0, 2.2, 2.2, 0.72, "fin-tyo.a4")
cyl(ax, 8.4, 1.5, 2.1, 1.1, "group log\n[E21] CMT-00049\ncancelled")
arrow(ax, (2.5, 4.55), (4.9, 5.45)); label(ax, 3.3, 5.5, "Q ×2: available\nbudget?")
arrow(ax, (4.9, 5.2), (2.5, 4.2), ls="--"); label(ax, 4.25, 3.85, "balance 4,108,776;\nearmark expired")
box(ax, 1.4, 2.0, 2.2, 0.9, "answer: 4,108,776 / 0  ✗\ngold: 2,889,428 / 2", fc="#fde0dd", ec=RED, bold=True, fs=5.9)
# ───────── (d) W-00016 Ingress ─────────
ax = axes[1, 1]; panel(ax, "(d) Ingress — W-00016:\nfan-out, search, conflict, proposal")
box(ax, 1.2, 4.2, 2.0, 1.0, "legal-tyo.a5\n(requester)")
group(ax, 3.2, 9.7, 0.5, 6.4, "FIN-TYO group")
box(ax, 4.7, 4.2, 1.7, 1.0, "gateway\n(intake desk)", fc="#dbe9f6", ec=BLUE, bold=True)
for y, name, fc in ((5.6, "fin-tyo.a1  ★", GRAY), (4.6, "fin-tyo.a2  ●", GREEN), (3.6, "fin-tyo.a3  ●", GREEN), (2.6, "fin-tyo.a4", "white")):
    box(ax, 7.9, y, 2.1, 0.68, name, fc=fc)
    arrow(ax, (5.55, 4.35), (6.85, y + 0.05), lw=0.6, color="#555"); arrow(ax, (6.85, y - 0.1), (5.55, 4.05), lw=0.6, color="#555", ls="--")
cyl(ax, 7.9, 1.25, 2.6, 0.8, "group log  [E21] CMT-00049 cancelled", fs=5.3)
arrow(ax, (2.2, 4.4), (3.85, 4.4)); label(ax, 3.0, 4.65, "Q")
arrow(ax, (4.9, 3.7), (6.6, 1.5), color=YEDGE, lw=0.8); label(ax, 5.0, 2.4, "search\nrecords", color=YEDGE, fs=5.5)
arrow(ax, (3.85, 4.0), (2.2, 4.0), color=BLUE, lw=1.5); label(ax, 3.25, 3.2, "4 replies + [E21]\n+ 1 conflict\n+ 1 proposal", color=BLUE)
box(ax, 1.2, 2.0, 2.0, 0.85, "answer: 2,889,428 / 2  ✓", fc=GREEN, ec="#2a7", bold=True, fs=5.9)
fig.text(0.5, 0.01, "★ card-listed handler    ● member whose context holds a decision-critical record    dashed red: member who has left    yellow: group records, readable only inside the group",
         ha="center", fontsize=6.0)
fig.subplots_adjust(hspace=0.3, wspace=0.08, bottom=0.05, top=0.92)
fig.savefig(OUT / "figures" / "f19_trace_examples.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / "f19_trace_examples.png", bbox_inches="tight", dpi=200)
print("ok")
