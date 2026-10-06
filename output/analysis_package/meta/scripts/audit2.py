import json, sys
from collections import defaultdict, Counter
from pathlib import Path
sys.path.insert(0, "/root/project/g2g_main/code")
from gbg.benchmarks.worldgen.scoring import load_private, verify
from gbg.scoring.reachability import unreachable
M = Path("/root/project/g2g_main"); pv = {}
runs = [(p, 15) for p in M.glob("runs/*/*/s*")] + [(p, 10) for p in M.glob("runs_g/*/*/s*")] + [(p, 10) for p in M.glob("runs_appx/*/s*")]
votes = defaultdict(list); fails = []
for run, cap in sorted(runs):
    rel = run.relative_to(M); seed = run.name
    sc = next((M / "scenarios_g" / rel.parts[1]).glob(f"D*_{seed}_T45")) if rel.parts[0] == "runs_g" else M / "scenarios" / f"D5_{seed}_T45"
    if sc not in pv:
        p = load_private(sc); pv[sc] = (p, set(unreachable(list(p.gold.values()))))
    p, un = pv[sc]
    last_submit = {}
    for l in open(run / "wal/events.jsonl"):
        if '"type":"llm_call"' in l and '"submit"' in l:
            e = json.loads(l)["payload"]
            for tc in e["message"].get("tool_calls") or []:
                if tc.get("name") == "submit": last_submit[e["task_id"]] = tc.get("arguments")
        if '"type":"answer"' in l:
            x = json.loads(l)["payload"]; w = x.get("task_id")
            if w not in p.gold or p.gold[w]["day"] > cap or w in un: continue
            if x.get("answer") is None:
                fails.append((str(rel), w, x.get("error"), str(last_submit.get(w))[:300], json.dumps(p.gold[w]["gold"], ensure_ascii=False)[:200]))
            else:
                votes[(str(sc.relative_to(M)), w)].append((str(rel.parent), json.dumps(x["answer"], sort_keys=True, ensure_ascii=False),
                                                         verify(p.tasks[w], x["answer"], p.gold[w])["exact"]))
print("== 제출 실패 (format_error/budget_exhausted): 마지막 submit 인자 vs 정답")
for f in fails: print("  ", f[0], f[1], f[2], "| submit:", f[3], "| gold:", f[4])
print("\n== 정답 의심: 6개 이상 런이 같은 답을 냈고, 정답을 맞힌 런이 하나도 없는 과제")
sus = []
for (sc, w), vs in votes.items():
    if any(ok for _, _, ok in vs): continue
    c = Counter(a for _, a, _ in vs); top, n = c.most_common(1)[0]
    if n >= 6: sus.append((n, len(vs), sc, w, top))
sus.sort(reverse=True)
print("건수", len(sus), "/ 전체 과제", len(votes))
for s in sus[:30]: print("  ", s[0], "/", s[1], s[2], s[3], s[4][:180])
json.dump(sus, open(M / "audit_suspects.json", "w"), ensure_ascii=False)
