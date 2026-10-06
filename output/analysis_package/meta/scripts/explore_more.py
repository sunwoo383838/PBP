"""로그에서 추가 분석 후보를 빠르게 훑는다 (기준 셀, 1~15일, 4조건 공통 과제)."""
import csv, gzip, json, re, statistics as st
from collections import defaultdict, Counter
from pathlib import Path
PKG = Path("/root/project/g2g/output/analysis_package"); T = PKG / "tables"; G = Path("/root/project/g2g_main/gates"); M = Path("/root/project/g2g_main")
C4 = ["direct", "routing", "ingress", "full_load"]; SEEDS = ["s12", "s13", "s14"]; MODELS = ["qwen3.5-27b", "deepseek-v4-flash"]
rows = [r for r in csv.DictReader(open(T / "tasks.csv", encoding="utf-8")) if r["within_target_days"] == "1" and r["reachable"] == "1" and r["cell"] == "base" and r["experiment"] == "main"]
by = defaultdict(dict)
for r in rows: by[(r["model"], r["seed"], r["condition"])][r["task_id"]] = r
GOLD = {s: {g["wid"]: g for g in (json.loads(l) for l in gzip.open(PKG / f"meta/scenarios/scenarios__D5_{s}_T45/gold.jsonl.gz", "rt"))} for s in SEEDS}
LEAVE = {}
for s in SEEDS:
    for l in open(M / f"scenarios/D5_{s}_T45/harness/timeline.jsonl"):
        if '"agent_leave"' in l:
            e = json.loads(l); LEAVE[(s, e["agent"])] = e["day"]
def items(m):
    out = []
    for s in SEEDS:
        ts = set.intersection(*[set(by[(m, s, c)]) for c in C4])
        out += [{c: by[(m, s, c)][t] for c in C4} | {"seed": s, "tid": t, "g": GOLD[s][t]} for t in sorted(ts)]
    return out
def acc(xs, c): return (sum(int(x[c]["exact"]) for x in xs) / len(xs) * 100) if xs else float("nan")
def line(name, groups, xs_by):
    print(f"\n## {name}")
    for k, xs in groups:
        print(f"  {k:28} n={len(xs):4} | " + " ".join(f"{c} {acc(xs, c):5.1f}" for c in C4) + f" | Δ {acc(xs,'ingress')-acc(xs,'direct'):+.1f}")
for m in MODELS:
    IT = items(m); print(f"\n==================== {m} (n={len(IT)})")
    # 1 발견 가능성 H 등급 (가장 어려운 결정 필수 조각 기준)
    def hmax(g):
        d = g.get("critical_disc") or {}
        return max(d, key=lambda k: int(k[1])) if d else "none"
    line("Discoverability of hardest critical record", [(h, [x for x in IT if hmax(x["g"]) == h]) for h in ("H0", "H1", "H2", "none")], None)
    # 2 추론 등급
    line("Reasoning tier", [(r, [x for x in IT if x["g"].get("R") == r]) for r in ("R0", "R1", "R2", "R3")], None)
    # 3 소유권 예외
    line("Ownership exception tasks", [("has owner_exception", [x for x in IT if any(o[1] == "owner_exception" for o in x["g"].get("ops") or [])]), ("other", [x for x in IT if not any(o[1] == "owner_exception" for o in x["g"].get("ops") or [])])], None)
    # 8 follow-up / revisit
    line("Follow-up (refers to earlier task)", [("follows", [x for x in IT if x["g"].get("follows")]), ("fresh", [x for x in IT if not x["g"].get("follows")])], None)
    line("Revisit (subject seen before)", [("revisit", [x for x in IT if x["g"].get("revisit")]), ("first", [x for x in IT if not x["g"].get("revisit")])], None)
    line("Critical origin", [("has db_pending (unregistered)", [x for x in IT if (x["g"].get("critical_origin") or {}).get("db_pending")]), ("operational only", [x for x in IT if not (x["g"].get("critical_origin") or {}).get("db_pending") and (x["g"].get("critical_origin") or {}).get("operational")]), ("no critical frags", [x for x in IT if not x["g"].get("critical_origin")])], None)
    # 7 이탈 후 경과일 (D 등급, 결정 필수 조각 보유자 전원 이탈)
    def days_since_leave(x):
        g = x["g"]; ds = []
        for n in g["needs"]:
            crit = set(n.get("critical_components") or [])
            for sv in n["sources"]:
                if sv["type"] == "frag" and sv["frag"]["fid"] in crit:
                    hs = sv["frag"].get("holders", [])
                    if hs and not any(h.get("active") for h in hs):
                        ds += [g["day"] - LEAVE[(x["seed"], h["agent"])] for h in hs if (x["seed"], h["agent"]) in LEAVE]
        return min(ds) if ds else None
    binsL = [(0, 1, "0–1d"), (2, 4, "2–4d"), (5, 9, "5–9d"), (10, 99, "10d+")]
    line("Days since the (last) holder left (tasks with a departed holder)", [(lab, [x for x in IT if (d := days_since_leave(x)) is not None and lo <= d <= hi]) for lo, hi, lab in binsL], None)
    # 6 지연시간
    print("\n## Wall-clock minutes per task (median / p90)")
    for c in C4:
        w = sorted(float(x[c]["wall_seconds"]) / 60 for x in IT if x[c]["wall_seconds"] not in ("", "None"))
        print(f"  {c:10} {st.median(w):5.1f} / {w[int(.9*len(w))]:5.1f}")
    # 4 제안 채택 (원장)
    agg = Counter(); corr = Counter()
    for s in SEEDS:
        f = G / f"main__base__{m}__ingress__{s}.json"
        if not f.exists(): continue
        for t in json.load(open(f))["tasks"]:
            p = t.get("proposals")
            if not p or not p.get("n"): continue
            for k in ("proposal", "member", "both", "neither", "dropped"): agg[k] += p.get(k, 0)
            agg["tasks_with_proposal"] += 1
            if p.get("proposal") and not p.get("member"): corr["followed_proposal_tasks"] += 1; corr["followed_proposal_correct"] += int(t["exact"])
            elif p.get("member") and not p.get("proposal"): corr["followed_member_tasks"] += 1; corr["followed_member_correct"] += int(t["exact"])
    print("\n## Gateway proposals (ingress): what the requester followed", dict(agg), dict(corr))
    # 10 use-failure template (coverage all but wrong) from ledger
    use_tpl = Counter(); use_n = 0
    for s in SEEDS:
        f = G / f"main__base__{m}__ingress__{s}.json"
        d = json.load(open(f)); tasks = {t["task_id"]: t for t in d["tasks"]}
        for n in d["needs"]:
            if n["gate"] == "L_use": use_tpl[GOLD[s][n["task_id"]]["template"]] += 1; use_n += 1
    print("## Ingress L_use needs by template:", use_tpl.most_common(8), "total", use_n)
# 5 부하 집중도 (그룹 안에서 요청이 몇 명에게 몰리나)
inbound = defaultdict(Counter)
with gzip.open(T / "messages.csv.gz", "rt") as f:
    for r in csv.DictReader(f):
        if r["kind"] == "request" and r["via"] == "agent" and r["to_agent"] and r["run_id"].startswith("main/base/qwen3.5-27b/"):
            inbound[(r["run_id"].split("/")[3], r["to_group"])][r["to_agent"]] += 1
print("\n## Inbound request concentration within a group (27B): top-1 member share, mean over groups; HHI")
for c in C4[:3]:
    shares = []; hhi = []
    for (cc, grp), cnt in inbound.items():
        if cc != c or sum(cnt.values()) < 10: continue
        tot = sum(cnt.values()); p = sorted(v / tot for v in cnt.values()); shares.append(p[-1]); hhi.append(sum(x * x for x in p))
    print(f"  {c:10} groups={len(shares)} top1={st.mean(shares)*100:.0f}% HHI={st.mean(hhi):.2f}")
# 9 검색 상한 절단
cap = Counter()
with gzip.open(T / "retrievals.csv.gz", "rt") as f:
    for r in csv.DictReader(f):
        if r["source"] == "gateway" and r["run_id"].startswith("main/base/qwen3.5-27b/ingress/"): cap["n"] += 1; cap["cap_reached"] += r["cap_reached"] == "1"; cap["cut>0"] += int(r["n_cap_cut"] or 0) > 0
print("\n## Gateway retrievals (27B ingress):", dict(cap))
