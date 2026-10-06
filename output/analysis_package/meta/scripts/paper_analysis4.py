"""논문 그림 4부 (기준 셀, 1~15일, 4조건 공통 과제): revisit 효과, 발견 가능성·추론 등급 상한, 운영 지표(부하 집중·지연·referral), 이탈 보유자.
출력 f15_revisit, f16_bounds, f17_operational, numbers4.json/md"""
import csv, gzip, json, statistics as st
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
PKG = Path("/root/project/g2g/output/analysis_package"); T = PKG / "tables"; G = Path("/root/project/g2g_main/gates"); M = Path("/root/project/g2g_main"); OUT = Path("/root/project/g2g/output/paper")
C4 = ["direct", "routing", "ingress", "full_load"]; SEEDS = ["s12", "s13", "s14"]; MODELS = ["qwen3.5-27b", "deepseek-v4-flash", "qwen3.5-9b"]
MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load"}
COL = {"direct": "#8c8c8c", "routing": "#e69f00", "ingress": "#0072b2", "full_load": "#009e73"}
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "pdf.fonttype": 42, "figure.dpi": 150})
def save(fig, name):
    fig.savefig(OUT / "figures" / f"{name}.pdf", bbox_inches="tight"); fig.savefig(OUT / "figures" / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig)
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1" and r["cell"] == "base" and r["experiment"] == "main"]
by = defaultdict(dict)
for r in rows: by[(r["model"], r["seed"], r["condition"])][r["task_id"]] = r
GOLD = {s: {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / f"meta/scenarios/scenarios__D5_{s}_T45/gold.jsonl.gz", "rt"))} for s in SEEDS}
LEAVE = {}
for s in SEEDS:
    for l in open(M / f"scenarios/D5_{s}_T45/harness/timeline.jsonl"):
        if '"agent_leave"' in l: e = json.loads(l); LEAVE[(s, e["agent"])] = e["day"]
def items(m):
    out = []
    for s in SEEDS:
        ts = set.intersection(*[set(by[(m, s, c)]) for c in C4])
        out += [{c: by[(m, s, c)][t] for c in C4} | {"seed": s, "tid": t, "g": GOLD[s][t]} for t in sorted(ts)]
    return out
RNG = np.random.default_rng(0)
def boot(xs, a, b, B=2000):
    d = np.array([int(x[a]["exact"]) - int(x[b]["exact"]) for x in xs], float)
    if not len(d): return None
    idx = RNG.integers(0, len(d), (B, len(d))); m = np.sort(d[idx].mean(1)); return {"mean": float(d.mean()), "lo": float(m[int(.025*B)]), "hi": float(m[int(.975*B)]), "n": int(len(d))}
def acc(xs, c): return sum(int(x[c]["exact"]) for x in xs) / len(xs) if xs else float("nan")
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
def is_stale(r, g):
    if int(r["exact"]): return False
    cf = (g.get("counterfactual") or {}).get("stale", {})
    if cf.get("example_answer") is None: return False
    try: return canon(json.loads(r["answer_json"])) == canon(cf["example_answer"])
    except Exception: return False
NUM = {}
# ─────────────────────────── 1. revisit ───────────────────────────
REV = [("first", lambda x: not x["g"].get("revisit")), ("revisit,\nunchanged", lambda x: x["g"].get("revisit") and not x["g"].get("repeat_changed")), ("revisit,\nchanged", lambda x: x["g"].get("revisit") and x["g"].get("repeat_changed"))]
rev = {}
for m in MODELS:
    IT = items(m); rev[m] = {}
    for lab, f in REV:
        xs = [x for x in IT if f(x)]
        rev[m][lab.replace("\n", " ")] = {"n": len(xs), "acc": {c: acc(xs, c) for c in C4}, "d_total": boot(xs, "ingress", "direct"),
                                           "stale": {c: sum(is_stale(x[c], x["g"]) for x in xs) / len(xs) for c in C4} if xs else {}}
    # 시간에 따른 revisit 비율
    rev[m]["revisit_share_by_window"] = {w: sum(1 for x in IT if x["g"].get("revisit") and lo <= x["g"]["day"] <= hi) / max(1, sum(1 for x in IT if lo <= x["g"]["day"] <= hi)) for w, (lo, hi) in (("1-5", (1, 5)), ("6-10", (6, 10)), ("11-15", (11, 15)))}
NUM["revisit"] = rev
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.3), sharey=True)
for ax, m in zip(axes, MODELS[:2]):
    labs = [l for l, _ in REV]; x = np.arange(3); w = 0.2
    for i, c in enumerate(C4):
        ax.bar(x + (i - 1.5) * w, [rev[m][l.replace("\n", " ")]["acc"][c] * 100 for l in labs], w, color=COL[c], label=CN[c])
        if c != "full_load":
            for j, l in enumerate(labs):
                sr = rev[m][l.replace("\n", " ")]["stale"][c] * 100
                if sr >= 3: ax.text(x[j] + (i - 1.5) * w, rev[m][l.replace("\n", " ")]["acc"][c] * 100 + 1.5, f"{sr:.0f}%", ha="center", fontsize=5.5, color="#b30000")
    ax.set_xticks(x); ax.set_xticklabels([f"{l}\n(n={rev[m][l.replace(chr(10), ' ')]['n']})" for l in labs]); ax.set_title(MN[m]); ax.grid(axis="y", lw=.3, alpha=.5); ax.set_ylim(0, 85)
axes[0].set_ylabel("Accuracy (%)"); axes[0].legend(frameon=False, ncol=2)
save(fig, "f15_revisit")
# ─────────────────────────── 2. 상한: 발견 가능성 H, 추론 등급 R ───────────────────────────
def hmax(g):
    d = g.get("critical_disc") or {}; return max(d, key=lambda k: int(k[1])) if d else "none"
bounds = {}
for m in MODELS:
    IT = items(m); bounds[m] = {"H": {}, "R": {}}
    for h in ("H0", "H1", "H2", "none"):
        xs = [x for x in IT if hmax(x["g"]) == h]; bounds[m]["H"][h] = {"n": len(xs), "acc": {c: acc(xs, c) for c in C4}, "d_total": boot(xs, "ingress", "direct")}
    for r in ("R0", "R1", "R2", "R3"):
        xs = [x for x in IT if x["g"].get("R") == r]; bounds[m]["R"][r] = {"n": len(xs), "acc": {c: acc(xs, c) for c in C4}, "d_total": boot(xs, "ingress", "direct")}
    # ingress 증거 포함률 (원장)
    tier = Counter(); inev = Counter(); srch = Counter()
    for s in SEEDS:
        d = json.load(open(G / f"main__base__{m}__ingress__{s}.json"))
        for n in d["needs"]:
            if n["gate"] == "unjudged": continue
            h = hmax(GOLD[s][n["task_id"]]); tier[h] += 1; inev[h] += bool(n.get("gate_detail", {}).get("in_evidence")); srch[h] += n["gate"] == "L_sel.search"
    bounds[m]["H_in_evidence"] = {h: {"needs": tier[h], "in_evidence": inev[h] / max(1, tier[h]), "search_loss": srch[h] / max(1, tier[h])} for h in ("H0", "H1", "H2")}
NUM["bounds"] = bounds
HL = {"H0": "H0\nlog text", "H1": "H1\nactivity trace", "H2": "H2\nreferring\nutterance", "none": "none\n(DB/rules)"}
RL = {"R0": "R0\nlookup", "R1": "R1\none rule", "R2": "R2\nconditional", "R3": "R3\nmulti-hop"}
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.5))
for ax, key, labs, LM, title in ((axes[0], "H", ["H0", "H1", "H2", "none"], HL, "(a) Discoverability of the hardest critical record"), (axes[1], "R", ["R0", "R1", "R2", "R3"], RL, "(b) Reasoning tier of the task")):
    x = np.arange(len(labs)); w = 0.2
    for i, c in enumerate(C4):
        for mi, m in enumerate(MODELS[:2]):
            v = [bounds[m][key][l]["acc"][c] * 100 for l in labs]
            ax.bar(x + (i - 1.5) * w, v, w, color=COL[c], alpha=1 if mi == 0 else 0.45, edgecolor="none", label=f"{CN[c]}" if mi == 0 else None, zorder=3 - mi)
    ax.set_xticks(x); ax.set_xticklabels([f"{LM[l]}\n(n={bounds['qwen3.5-27b'][key][l]['n']})" for l in labs], fontsize=6.5); ax.set_title(title); ax.grid(axis="y", lw=.3, alpha=.5); ax.set_ylim(0, 100)
axes[0].set_ylabel("Accuracy (%)"); axes[0].legend(frameon=False, ncol=2, fontsize=6.5)
save(fig, "f16_bounds")
# ─────────────────────────── 3. 운영: 부하 집중, 지연, referral, 이탈 보유자 ───────────────────────────
inbound = defaultdict(lambda: defaultdict(Counter))
with gzip.open(T / "messages.csv.gz", "rt") as f:
    for r in csv.DictReader(f):
        p = r["run_id"].split("/")
        if p[0] == "main" and r["kind"] == "request" and r["via"] == "agent" and r["to_agent"]: inbound[p[2]][(p[3], p[4], r["to_group"])][r["to_agent"]] += 1
ops = {}
for m in MODELS:
    ops[m] = {"load": {}, "latency": {}}
    for c in C4[:3]:
        top1 = []; hhi = []
        for (cc, s, grp), cnt in inbound[m].items():
            if cc != c or sum(cnt.values()) < 10: continue
            tot = sum(cnt.values()); p = sorted(v / tot for v in cnt.values()); top1.append(p[-1]); hhi.append(sum(q * q for q in p))
        ops[m]["load"][c] = {"groups": len(top1), "top1_share": st.mean(top1), "hhi": st.mean(hhi)}
    IT = items(m)
    for c in C4:
        w = sorted(float(x[c]["wall_seconds"]) / 60 for x in IT if x[c]["wall_seconds"] not in ("", "None"))
        ops[m]["latency"][c] = {"median_min": st.median(w), "p90_min": w[int(.9 * len(w))]}
    # 이탈 보유자 과제
    def departed(x):
        for n in x["g"]["needs"]:
            crit = set(n.get("critical_components") or [])
            for sv in n["sources"]:
                if sv["type"] == "frag" and sv["frag"]["fid"] in crit:
                    hs = sv["frag"].get("holders", [])
                    if hs and not any(h.get("active") for h in hs): return True
        return False
    xs = [x for x in IT if departed(x)]; ops[m]["departed_holder_tasks"] = {"n": len(xs), "acc": {c: acc(xs, c) for c in C4}}
    # 소유권 예외 referral
    gw = defaultdict(list)
    for r in csv.DictReader(open(T / "gateway_decisions.csv", encoding="utf-8")):
        p = r["run_id"].split("/")
        if p[0] == "main" and p[2] == m and p[3] == "ingress": gw[(p[4], r["task_id"])].append(r)
    oe = [x for x in IT if any(o[1] == "owner_exception" for o in x["g"].get("ops") or [])]
    ref = [x for x in oe if any(d["action"] == "referral" for d in gw[(x["seed"], x["tid"])])]
    ops[m]["owner_exception"] = {"n": len(oe), "referred": len(ref), "acc_referred": acc(ref, "ingress"), "acc_not_referred": acc([x for x in oe if x not in ref], "ingress"), "acc_direct": acc(oe, "direct")}
NUM["ops"] = ops
fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.1))
ax = axes[0]; x = np.arange(3); w = 0.35
for mi, m in enumerate(MODELS[:2]):
    ax.bar(x + (mi - .5) * w, [ops[m]["load"][c]["top1_share"] * 100 for c in C4[:3]], w, color=[COL[c] for c in C4[:3]], alpha=1 if mi == 0 else 0.45, label=MN[m])
ax.set_xticks(x); ax.set_xticklabels([CN[c] for c in C4[:3]]); ax.set_ylabel("Share of a group's inbound requests\nreceived by its most-asked member (%)"); ax.set_title("(a) Who gets asked"); ax.grid(axis="y", lw=.3, alpha=.5); ax.legend(frameon=False)
ax = axes[1]; x = np.arange(4)
for mi, m in enumerate(MODELS[:2]):
    ax.bar(x + (mi - .5) * w, [ops[m]["latency"][c]["median_min"] for c in C4], w, color=[COL[c] for c in C4], alpha=1 if mi == 0 else 0.45)
    for j, c in enumerate(C4): ax.plot([x[j] + (mi - .5) * w] * 2, [ops[m]["latency"][c]["median_min"], ops[m]["latency"][c]["p90_min"]], color="k", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels([CN[c] for c in C4]); ax.set_ylabel("Wall-clock minutes per task\n(bar: median, whisker to p90)"); ax.set_title("(b) Latency (solid: 27B, faded: DeepSeek)"); ax.grid(axis="y", lw=.3, alpha=.5)
save(fig, "f17_operational")
json.dump(NUM, open(OUT / "numbers4.json", "w"), ensure_ascii=False, indent=1, default=float)
md = ["# numbers4"]
for m in MODELS:
    md.append(f"## {MN[m]}")
    for k, v in rev[m].items():
        if k == "revisit_share_by_window": md.append(f"  revisit share by window: {v}"); continue
        md.append(f"  {k}: n={v['n']} " + " ".join(f"{c} {v['acc'][c]*100:.1f}" for c in C4) + f" | Δ {v['d_total']['mean']*100:+.1f} [{v['d_total']['lo']*100:+.1f}, {v['d_total']['hi']*100:+.1f}] | stale " + " ".join(f"{c} {v['stale'][c]*100:.0f}" for c in C4))
    for key in ("H", "R"):
        for l, v in bounds[m][key].items(): md.append(f"  {key} {l}: n={v['n']} " + " ".join(f"{c} {v['acc'][c]*100:.1f}" for c in C4) + (f" | Δ {v['d_total']['mean']*100:+.1f} [{v['d_total']['lo']*100:+.1f}, {v['d_total']['hi']*100:+.1f}]" if v["d_total"] else ""))
    md.append("  in_evidence: " + "; ".join(f"{h} needs {v['needs']} in_evidence {v['in_evidence']*100:.0f}% search-loss {v['search_loss']*100:.0f}%" for h, v in bounds[m]["H_in_evidence"].items()))
    md.append("  load: " + "; ".join(f"{c} top1 {v['top1_share']*100:.0f}% hhi {v['hhi']:.2f}" for c, v in ops[m]["load"].items()) + " | latency: " + "; ".join(f"{c} {v['median_min']:.1f}/{v['p90_min']:.1f}" for c, v in ops[m]["latency"].items()))
    md.append(f"  departed-holder tasks: {ops[m]['departed_holder_tasks']} | owner_exception: {ops[m]['owner_exception']}")
(OUT / "numbers4.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md))
