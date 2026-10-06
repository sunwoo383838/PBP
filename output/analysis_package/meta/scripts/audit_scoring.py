"""채점 총검토: 모든 런(일수 상한 안)의 답을 정답과 대조.
A 우리 채점 vs worldgen 공식 채점(score_answers.canonical) 불일치
B 엄격 오답인데 느슨한 비교(대소문자·공백·숫자 표기·목록 순서)로는 정답 → 형식 차이 오판 후보
C 같은 과제 답 중복(재시작 재생), D 일수 상한 안 무답 과제, E 답 없음(제출 실패)"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, "/root/project/g2g_main/code")
from gbg.benchmarks.worldgen.scoring import load_private, verify
from gbg.scoring.reachability import unreachable
M = Path("/root/project/g2g_main")
def canonical(a):                                                          # worldgen 공식 채점기와 같은 규칙
    if not isinstance(a, dict): return None
    a = dict(a)
    for f in ("assets", "recover_assets"):
        if f in a and isinstance(a[f], list):
            if not all(isinstance(x, str) for x in a[f]): return None
            a[f] = sorted(a[f])
    return json.dumps(a, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
def loose(v):
    if isinstance(v, bool) or v is None: return v
    if isinstance(v, (int, float)): return round(float(v), 6)
    if isinstance(v, str):
        s = re.sub(r"\s+", " ", v.strip()).casefold().rstrip(".")
        try: return round(float(s.replace(",", "")), 6)
        except ValueError: return s
    if isinstance(v, list): return [loose(x) for x in v]
    if isinstance(v, dict): return {k: loose(x) for k, x in v.items()}
    return v
def loose_eq(a, g):
    la, lg = loose(a), loose(g)
    if la == lg: return True
    if isinstance(la, list) and isinstance(lg, list):
        return sorted(map(json.dumps, la)) == sorted(map(json.dumps, lg))
    return False
pv = {}; out = defaultdict(Counter); B = []; A = []; dupdiff = []
runs = [(p, 15) for p in M.glob("runs/*/*/s*")] + [(p, 10) for p in M.glob("runs_g/*/*/s*")] + [(p, 10) for p in M.glob("runs_appx/*/s*")]
for run, cap in sorted(runs):
    rel = run.relative_to(M); seed = run.name
    if rel.parts[0] == "runs_g": sc = next((M / "scenarios_g" / rel.parts[1]).glob(f"D*_{seed}_T45"))
    else: sc = M / "scenarios" / f"D5_{seed}_T45"
    if sc not in pv:
        p = load_private(sc); pv[sc] = (p, set(unreachable(list(p.gold.values()))))
    p, un = pv[sc]
    ans = defaultdict(list)
    for l in open(run / "wal/events.jsonl"):
        if '"type":"answer"' in l:
            x = json.loads(l)["payload"]
            if x.get("task_id") in p.gold: ans[x["task_id"]].append(x)
    key = str(rel.parent)
    for w, g in p.gold.items():
        if g["day"] > cap or w in un: continue
        if w not in ans:
            out[key]["D_무답(답 사건 없음)"] += 1; continue
        xs = ans[w]
        if len(xs) > 1:
            out[key]["C_중복"] += 1
            if len({json.dumps(x.get("answer"), sort_keys=True) for x in xs}) > 1: dupdiff.append((str(rel), w))
        x = xs[-1]; a = x.get("answer")
        out[key]["채점 대상"] += 1
        if a is None:
            out[key]["E_답 없음(" + str(x.get("error")) + ")"] += 1; continue
        ours = verify(p.tasks[w], a, g)["exact"]
        off = isinstance(a, dict) and set(a) == set(g["gold"]) and canonical(a) == canonical(g["gold"])
        out[key]["정답"] += ours
        if ours != off:
            A.append((str(rel), w, ours, off, a, g["gold"]))
        if not ours:
            bad = [k for k in g["gold"] if json.dumps(a.get(k), sort_keys=True) != json.dumps(g["gold"][k], sort_keys=True)]
            if bad and all(loose_eq(a.get(k), g["gold"][k]) for k in bad):
                B.append((str(rel), w, g["template"], {k: (a.get(k), g["gold"][k]) for k in bad}))
tot = Counter()
for k, c in out.items(): tot.update(c)
print("== 전체 집계", dict(tot))
print(f"== A 우리 채점 vs 공식 채점 불일치: {len(A)}")
for r in A[:10]: print("  ", r[0], r[1], "우리", r[2], "공식", r[3], json.dumps(r[4], ensure_ascii=False)[:150], "| gold", json.dumps(r[5], ensure_ascii=False)[:150])
print(f"== B 형식 차이 오판 후보: {len(B)}")
for r in B[:40]: print("  ", r[0], r[1], r[2], json.dumps(r[3], ensure_ascii=False)[:200])
print(f"== C 답이 다른 중복: {len(dupdiff)}", dupdiff[:5])
print("== 런 묶음별 무답·답 없음")
for k, c in sorted(out.items()):
    extra = {kk: v for kk, v in c.items() if kk.startswith(("D_", "E_", "C_"))}
    if extra: print("  ", k, dict(extra))
json.dump({"A": A, "B": B}, open(M / "audit_scoring.json", "w"), ensure_ascii=False, default=str)
