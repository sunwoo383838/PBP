"""접근 감사: 모든 런의 obs/access.jsonl → 조건별 기록 읽기 건수(자기 그룹 / 교차 그룹 허용 / 거부). 출력 analysis_package/tables/access_audit.csv"""
import csv, glob, json, collections
from pathlib import Path
runs = sorted(glob.glob("/root/project/g2g_main/runs/*/*/s1[234]") + glob.glob("/root/project/g2g_main/runs_g/*/*/s1[234]") + glob.glob("/root/project/g2g_main/runs_appx/*/s1[234]"))
rows = []
for r in runs:
    c = collections.Counter(); cond = None
    for line in open(f"{r}/obs/access.jsonl"):
        e = json.loads(line); cond = e["condition"]
        c[("own" if e["scope"] == "own" else "cross", "allowed" if e["allowed"] else "denied", e["resource"])] += 1
    rid = "/".join(r.split("/")[-3:])
    rows.append({"run": rid, "condition": cond, "reads_total": sum(c.values()), "own_allowed": sum(v for (s, a, _), v in c.items() if s == "own" and a == "allowed"),
                 "own_denied": sum(v for (s, a, _), v in c.items() if s == "own" and a == "denied"), "cross_allowed": sum(v for (s, a, _), v in c.items() if s == "cross" and a == "allowed"),
                 "cross_denied": sum(v for (s, a, _), v in c.items() if s == "cross" and a == "denied"),
                 "cross_db": c[("cross", "allowed", "db")], "cross_group_history": c[("cross", "allowed", "group_history")]})
out = Path("/root/project/g2g/output/analysis_package/tables/access_audit.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
tot = collections.defaultdict(collections.Counter)
for x in rows:
    for k in ("reads_total", "own_allowed", "own_denied", "cross_allowed", "cross_denied"): tot[x["condition"]][k] += x[k]
    tot[x["condition"]]["runs"] += 1
for cond, t in sorted(tot.items()): print(cond, dict(t))
print("wrote", out, len(rows), "runs")
