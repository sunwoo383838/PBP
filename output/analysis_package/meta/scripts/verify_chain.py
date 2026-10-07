"""손실 고리 체계 전환 검증 (gates_prev2 = 이전 라벨, gates = 새 고리).
 (1) 불변: 판정 need의 '전달됨' 여부가 같다 — 이전 ok·L_use ⇔ 새 ok (오류 코드는 그대로 오류)
 (2) 전이표: 이전 라벨 → 새 고리, 조건별 (기준 셀 1~15일, 부록 1~10일)
 (3) 옛 버전 표시(stale)·질문 되풀이(echo)·과제 단위 결과(use) 건수"""
import json, glob
from collections import Counter
from pathlib import Path
G = Path("/root/project/g2g_main/gates"); P = Path("/root/project/g2g_main/gates_prev2")
def judged(rows): return [n for n in rows if n["gate"] != "unjudged" and n["scored"]]
bad = 0
for f in sorted(G.glob("*.json")):
    if f.name.startswith(("context", "test_")): continue
    a, b = judged(json.load(open(P / f.name))["needs"]), judged(json.load(open(f))["needs"])
    assert len(a) == len(b), f.name
    for x, y in zip(a, b):
        ox = "err" if x["gate"].startswith("E_") else "ok" if x["gate"] in ("ok", "L_use") else "lost"
        oy = "err" if y["gate"].startswith("E_") else "ok" if y["gate"] == "ok" else "lost"
        bad += ox != oy
print("(1) needs whose delivered/lost/error status changed:", bad)
groups = [("27B", "main__base__qwen3.5-27b__{c}__s*.json"), ("DS", "main__base__deepseek-v4-flash__{c}__s*.json"), ("9B", "main__base__qwen3.5-9b__{c}__s*.json")]
for tag, pat in groups:
    for c in ("direct", "routing", "ingress", "full_load"):
        tr = Counter(); new = Counter(); n = 0; stale = 0; lost = 0; echo = 0; dfr = 0; out = Counter()
        for f in sorted(G.glob(pat.format(c=c))):
            d = json.load(open(f)); a = judged(json.load(open(P / f.name))["needs"]); b = judged(d["needs"])
            for x, y in zip(a, b):
                if y["gate"].startswith("E_"): continue
                n += 1; new[y["gate"]] += 1
                if x["gate"] != y["gate"]: tr[(x["gate"], y["gate"])] += 1
                det = y.get("gate_detail") or {}
                if y["gate"] != "ok": lost += 1; stale += bool(det.get("stale"))
                echo += len(det.get("echo") or []); dfr += sum(fr["state"] == "delivered" for fr in y.get("frags", []))
            out += Counter(t.get("outcome") for t in d["tasks"] if t["day"] <= 15 and not t["unreachable"])
        if not n: continue
        print(f"\n== {tag} {c}: judged needs {n} | links /100: " + ", ".join(f"{k.replace('L_', '')} {v/n*100:.1f}" for k, v in sorted(new.items(), key=lambda kv: -kv[1])))
        print(f"   lost {lost}, of which older value arrived (stale flag) {stale}; delivered fragments {dfr}, echoed from the question {echo}; task outcomes {dict(out)}")
        print("   old → new (top):", ", ".join(f"{o.replace('L_', '')}→{w.replace('L_', '')} {k}" for (o, w), k in tr.most_common(8)))
for c in ("direct_relay", "retrieve", "sidecar"):
    tr = Counter(); n = 0
    for f in sorted(G.glob(f"appendix__base__qwen3.5-27b__{c}__s*.json")):
        a = judged(json.load(open(P / f.name))["needs"]); b = judged(json.load(open(f))["needs"])
        for x, y in zip(a, b):
            n += 1
            if x["gate"] != y["gate"]: tr[(x["gate"], y["gate"])] += 1
    print(f"\n== 27B {c} (1-10d): judged {n}; old → new:", ", ".join(f"{o.replace('L_', '')}→{w.replace('L_', '')} {k}" for (o, w), k in tr.most_common(8)))
