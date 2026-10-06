import csv, gzip, json, statistics as st
from collections import defaultdict, Counter
from pathlib import Path
PKG = Path("/root/project/g2g/output/analysis_package"); T = PKG / "tables"; G = Path("/root/project/g2g_main/gates")
C4 = ["direct", "routing", "ingress", "full_load"]; SEEDS = ["s12", "s13", "s14"]; MODELS = ["qwen3.5-27b", "deepseek-v4-flash"]
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1" and r["cell"] == "base" and r["experiment"] == "main"]
by = defaultdict(dict)
for r in rows: by[(r["model"], r["seed"], r["condition"])][r["task_id"]] = r
GOLD = {s: {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / f"meta/scenarios/scenarios__D5_{s}_T45/gold.jsonl.gz", "rt"))} for s in SEEDS}
gw = defaultdict(list)
for r in csv.DictReader(open(T / "gateway_decisions.csv", encoding="utf-8")):
    p = r["run_id"].split("/")
    if p[0] == "main": gw[(p[2], p[3], p[4], r["task_id"])].append(r)
def items(m):
    out = []
    for s in SEEDS:
        ts = set.intersection(*[set(by[(m, s, c)]) for c in C4])
        out += [{c: by[(m, s, c)][t] for c in C4} | {"seed": s, "tid": t, "g": GOLD[s][t]} for t in sorted(ts)]
    return out
def acc(xs, c): return (sum(int(x[c]["exact"]) for x in xs) / len(xs) * 100) if xs else float("nan")
def line(k, xs): print(f"  {k:40} n={len(xs):4} | " + " ".join(f"{c} {acc(xs, c):5.1f}" for c in C4) + f" | Δ {acc(xs,'ingress')-acc(xs,'direct'):+.1f}")
for m in MODELS:
    IT = items(m); print(f"\n==================== {m}")
    print("## Revisit × whether the fact changed since (repeat_changed)")
    for lab, f in (("revisit & changed", lambda x: x["g"].get("revisit") and x["g"].get("repeat_changed")), ("revisit & unchanged", lambda x: x["g"].get("revisit") and not x["g"].get("repeat_changed")), ("first", lambda x: not x["g"].get("revisit"))):
        line(lab, [x for x in IT if f(x)])
    print("## Revisit: did the requester ask anyone? (requester_asks == 0) — share and accuracy")
    for c in C4[:3]:
        rv = [x for x in IT if x["g"].get("revisit")]; z = [x for x in rv if int(x[c]["requester_asks"] or 0) == 0]; nz = [x for x in rv if int(x[c]["requester_asks"] or 0) > 0]
        fr = [x for x in IT if not x["g"].get("revisit")]; z2 = [x for x in fr if int(x[c]["requester_asks"] or 0) == 0]
        print(f"  {c:10} revisit: no-ask {len(z)}/{len(rv)} ({len(z)/len(rv)*100:.0f}%) acc no-ask {acc(z,c):.0f} / ask {acc(nz,c):.0f} | first: no-ask {len(z2)}/{len(fr)} ({len(z2)/len(fr)*100:.0f}%)")
    print("## Ownership-exception tasks: gateway referral behaviour (ingress)")
    oe = [x for x in IT if any(o[1] == "owner_exception" for o in x["g"].get("ops") or [])]
    ref = [x for x in oe if any(d["action"] == "referral" for d in gw[(m, "ingress", x["seed"], x["tid"])])]
    nref = [x for x in oe if x not in ref]
    print(f"  owner_exception tasks {len(oe)}: referred {len(ref)} (acc ingress {acc(ref,'ingress'):.0f}), not referred {len(nref)} (acc ingress {acc(nref,'ingress'):.0f}); overall referral decisions on these tasks: {sum(d['action']=='referral' for x in oe for d in gw[(m,'ingress',x['seed'],x['tid'])])}/{sum(len(gw[(m,'ingress',x['seed'],x['tid'])]) for x in oe)}")
    print("## Ingress L_sel.search / in_evidence by discoverability tier (ledger, needs)")
    tier = Counter(); search = Counter(); inev = Counter()
    for s in SEEDS:
        d = json.load(open(G / f"main__base__{m}__ingress__{s}.json"))
        for n in d["needs"]:
            if n["gate"] == "unjudged": continue
            g = GOLD[s][n["task_id"]]; dd = g.get("critical_disc") or {}; h = max(dd, key=lambda k: int(k[1])) if dd else "none"
            tier[h] += 1; search[h] += n["gate"] == "L_sel.search"; inev[h] += bool(n.get("gate_detail", {}).get("in_evidence"))
    for h in ("H0", "H1", "H2"): print(f"  {h}: needs {tier[h]} search-loss {search[h]/max(1,tier[h])*100:.0f}% in_evidence {inev[h]/max(1,tier[h])*100:.0f}%")
