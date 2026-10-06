import json, sys
from pathlib import Path
sc = Path("/root/project/g2g_main") / sys.argv[1]; W = sys.argv[2]
g = next(json.loads(l) for l in open(sc / "private/gold.jsonl") if f'"{W}"' in l)
w = next(json.loads(l) for l in open(sc / "harness/work.jsonl") if f'"{W}"' in l)
print("TASK", W, "day", g["day"], "round", g["round"], "seq", g["seq"], g["template"], "class", g["state_class"], "ops", g.get("ops"))
print("Q:", g["surface"].split("\n")[0]); print("REQ:", json.dumps({k: v for k, v in g["request"].items() if k != "scope"}, ensure_ascii=False))
print("GOLD:", json.dumps(g["gold"], ensure_ascii=False))
db = {}
for l in open(sc / "private/db_versions.jsonl"):
    x = json.loads(l); db.setdefault(x["key"], []).append(x)
fr = {json.loads(l)["fid"]: json.loads(l) for l in open(sc / "private/fragments.jsonl")}
keys = set()
for n in g["needs"]:
    print(" need", n["sem"], "class", n.get("class"))
    for s in n["sources"]:
        if s["type"] == "db": keys.add(s["key"]); print("   db", s["key"], "v", s["v"])
        elif s["type"] == "frag":
            f = fr[s["frag"]["fid"]]; print("   frag", f["fid"], "day", f["day"], "seq", f["seq"], f["kind"], f.get("origin"), "|", f["text"][:160])
        elif s["type"] == "rule": print("   rule", s["ref"])
        else: print("  ", json.dumps(s, ensure_ascii=False)[:220])
for k in sorted(keys):
    for v in db.get(k, []):
        print("  DBVER", k, "v", v["v"], "day", v["day"], "seq", v["seq"], "db_day", v["db_day"], json.dumps(v["value"], ensure_ascii=False)[:120])
