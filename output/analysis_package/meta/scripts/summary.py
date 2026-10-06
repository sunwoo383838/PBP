"""중간 정리: 일수 상한(1차 기준 셀 15일, G 셀 비교 10일, 부록 10일) 안의 공통 과제로 조건 비교. 원리상 불가 과제 제외.
ingress−direct 격차는 과제 단위 짝 부트스트랩 95% 구간(2000회)."""
import json, sys, random
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "/root/project/g2g_main/code")
from gbg.benchmarks.worldgen.scoring import load_private, verify
from gbg.scoring.reachability import unreachable
M = Path("/root/project/g2g_main"); C4 = ["direct", "routing", "ingress", "full_load"]; SEEDS = ("s12", "s13", "s14")
pv = {}
def rows(run, sc, maxday):
    if sc not in pv:
        p = load_private(sc); pv[sc] = (p, set(unreachable(list(p.gold.values()))))
    p, un = pv[sc]; out = {}
    for l in open(run / "wal/events.jsonl"):
        if '"type":"answer"' in l:
            x = json.loads(l)["payload"]; w = x.get("task_id")
            if w in p.gold and w not in un and p.gold[w]["day"] <= maxday:
                g = p.gold[w]
                out[w] = {"ok": verify(p.tasks[w], x.get("answer"), g)["exact"], "cls": g["state_class"], "cops": bool(g.get("c_ops")),
                          "ng": min(g["n_groups"], 5), "tpl": g["template"]}
    return out
def sc_of(cell, seed):
    return M / "scenarios" / f"D5_{seed}_T45" if cell == "base" else next((M / "scenarios_g" / cell).glob(f"D*_{seed}_T45"))
def run_of(cell, model, cond, seed):
    if cond in ("direct_relay", "retrieve", "sidecar"): return M / "runs_appx" / cond / seed
    return M / "runs" / model / cond / seed if cell == "base" else M / "runs_g" / cell / cond / seed
def table(cell, model, conds, maxday):
    R = {(c, s): rows(run_of(cell, model, c, s), sc_of(cell, s), maxday) for c in conds for s in SEEDS}
    com = [(s, w) for s in SEEDS for w in set.intersection(*[set(R[(c, s)]) for c in conds])]
    return R, com
def acc(R, com, c, f=lambda r: True):
    xs = [R[(c, s)][w]["ok"] for s, w in com if f(R[(c, s)][w])]
    return (sum(xs) / len(xs), len(xs)) if xs else (float("nan"), 0)
def boot(R, com, a, b):
    d = [R[(a, s)][w]["ok"] - R[(b, s)][w]["ok"] for s, w in com]
    rnd = random.Random(0); m = []
    for _ in range(2000):
        smp = [d[rnd.randrange(len(d))] for _ in d]; m.append(sum(smp) / len(smp))
    m.sort(); return sum(d) / len(d), m[50], m[1949]
print("## 1) 1차 기준 셀 D5·R2 (1~15일)")
print("모델 | n | direct | routing | ingress | full_load | ingress−direct [95% 구간]")
for model in ("qwen3.5-27b", "qwen3.5-9b", "deepseek-v4-flash"):
    R, com = table("base", model, C4, 15)
    g = boot(R, com, "ingress", "direct")
    print(f"{model} | {len(com)} | " + " | ".join(f"{acc(R, com, c)[0]:.2f}" for c in C4) + f" | {g[0]:+.2f} [{g[1]:+.2f}, {g[2]:+.2f}]")
print("\n## 2) G 셀 (27B, 1~10일, 셀마다 4조건 공통)")
print("셀 | G | n | direct | routing | ingress | full_load | ingress−direct [95% 구간]")
G = {"R1": 5, "D3": 6, "base": 10, "R3": 15}
for cell in ("R1", "D3", "base", "R3"):
    R, com = table(cell, "qwen3.5-27b", C4, 10)
    g = boot(R, com, "ingress", "direct")
    print(f"{cell} | {G[cell]} | {len(com)} | " + " | ".join(f"{acc(R, com, c)[0]:.2f}" for c in C4) + f" | {g[0]:+.2f} [{g[1]:+.2f}, {g[2]:+.2f}]")
print("\n## 3) 부록 (27B 기준 셀, 1~10일, 7조건 공통)")
A = C4 + ["direct_relay", "retrieve", "sidecar"]
R, com = table("base", "qwen3.5-27b", A, 10)
print(f"n={len(com)}")
print("조건 | 전체 | A | B | C | D | C_ops")
for c in A:
    print(f"{c} | {acc(R, com, c)[0]:.2f} | " + " | ".join(f"{acc(R, com, c, lambda r, k=k: r['cls'] == k)[0]:.2f}" for k in "ABCD")
          + f" | {acc(R, com, c, lambda r: r['cops'])[0]:.2f}")
print("\n## 4) 27B 층화 (기준 셀 1~15일 + G 셀 1~10일 합산, 셀마다 4조건 공통)")
pool = []
for cell, md in (("base", 15), ("R1", 10), ("D3", 10), ("R3", 10)):
    R, com = table(cell, "qwen3.5-27b", C4, md); pool.append((R, com))
def pooled(f, c):
    xs = [R[(c, s)][w]["ok"] for R, com in pool for s, w in com if f(R[(c, s)][w])]
    return sum(xs) / len(xs) if xs else float("nan"), len(xs)
for name, keyf, vals in (("상태 등급", "cls", "ABCD"), ("C_ops", "cops", (False, True)), ("걸린 그룹 수", "ng", (2, 3, 4, 5))):
    print(f"[{name}] 값 | n | " + " | ".join(C4) + " | ingress−direct")
    for v in vals:
        r = {c: pooled(lambda x: x[keyf] == v, c) for c in C4}
        print(f"  {v} | {r['direct'][1]} | " + " | ".join(f"{r[c][0]:.2f}" for c in C4) + f" | {r['ingress'][0] - r['direct'][0]:+.2f}")
