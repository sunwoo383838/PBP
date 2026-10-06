"""채점 규칙 변경(조립 조건: 게이트웨이는 본 것만 잃을 수 있다) 검증.
 (1) 조립이 아닌 조건(direct·routing·full_load·direct_relay·retrieve)의 원장이 전후 동일한지 (seconds 제외)
 (2) 조립 조건(ingress·sidecar)의 선택 관문 분포 전후 (판정 need = gate != unjudged and scored; 기본 셀 1~15일)
 (3) 새로 assembly가 된 need 전수와 그중 20건의 근거(어디서 봤나·조각 원문·입력의 일치 줄·전달된 답)
 (4) 문장에만 있다가 빠짐(text_only)·매처 의심(matcher_suspect) 조건별 건수
사용: verify_rule.py [--cases N]"""
import glob, json, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, "/root/project/g2g")
from gbg.scoring.gates import evidence_section, reply_sections
from gbg.scoring.delivery import _norm, _sig_hit, canaries, signature
from gbg.benchmarks.worldgen.scoring import load_private

G = Path("/root/project/g2g_main/gates"); OLD = Path("/root/project/g2g_main/gates_old"); M = Path("/root/project/g2g_main")
NCASES = int(sys.argv[sys.argv.index("--cases") + 1]) if "--cases" in sys.argv else 20
def judged(rows): return [n for n in rows if n["gate"] != "unjudged" and n["scored"]]
def strip(d): return {k: v for k, v in d.items() if k != "seconds"}

# (1) 불변 조건 diff
print("== (1) non-assemble ledgers identical? ==")
same = bad = 0
for f in sorted(G.glob("*.json")):
    if f.name.startswith("context") or "__ingress__" in f.name or "__sidecar__" in f.name: continue
    o = OLD / f.name
    if not o.exists(): print("  no old:", f.name); continue
    if strip(json.load(open(f))) == strip(json.load(open(o))): same += 1
    else:
        bad += 1; a, b = json.load(open(o))["needs"], json.load(open(f))["needs"]
        diff = Counter((x["gate"], y["gate"]) for x, y in zip(a, b) if x["gate"] != y["gate"] or x["gate_detail"] != y["gate_detail"])
        print("  DIFF", f.name, dict(diff))
print(f"  identical {same}, differing {bad}")

# (2) 조립 조건 분포 전후
print("\n== (2) select sub-gates per 100 judged needs, old -> new ==")
SEL = ["L_sel.window", "L_sel.answer", "L_sel.search", "L_sel.assembly"]
groups = {"27B ingress (base 1-15d)": "main__base__qwen3.5-27b__ingress__s*.json", "DS ingress (base 1-15d)": "main__base__deepseek-v4-flash__ingress__s*.json",
          "9B ingress (base 1-15d)": "main__base__qwen3.5-9b__ingress__s*.json", "27B sidecar (base 1-10d)": "appendix__base__qwen3.5-27b__sidecar__s*.json",
          "27B ingress G cells (1-10d)": "gcell__*__qwen3.5-27b__ingress__s*.json"}
transitions = {}
for label, pat in groups.items():
    old = Counter(); new = Counter(); n = 0; tr = Counter()
    for f in sorted(G.glob(pat)):
        a, b = judged(json.load(open(OLD / f.name))["needs"]), judged(json.load(open(f))["needs"])
        assert len(a) == len(b), f.name
        n += len(b)
        for x, y in zip(a, b):
            old[x["gate"]] += 1; new[y["gate"]] += 1
            if x["gate"] != y["gate"]: tr[(x["gate"], y["gate"])] += 1
    transitions[label] = tr
    print(f"  {label}: judged needs {n}")
    for g in SEL: print(f"     {g:16s} {old[g]/n*100:5.1f} -> {new[g]/n*100:5.1f}   ({old[g]} -> {new[g]})")
    print("     sum select     ", f"{sum(old[g] for g in SEL)/n*100:5.1f} -> {sum(new[g] for g in SEL)/n*100:5.1f}")
    print("     transitions:", dict(tr))

# (4) text_only / matcher_suspect 조건별
print("\n== (4) text_only (문장에만 있다가 빠짐) / matcher_suspect (항목에 있었는데 미전달) ==")
for label, pat in groups.items():
    c = Counter(); n = 0
    for f in sorted(G.glob(pat)):
        for r in judged(json.load(open(f))["needs"]):
            n += 1; d = r.get("gate_detail") or {}
            if r["gate"] == "L_sel.assembly":
                c["assembly"] += 1
                c["in_evidence"] += bool(d.get("in_evidence")); c["in_reply_items"] += bool(d.get("in_reply_items")); c["in_reply_text"] += bool(d.get("in_reply_text"))
                c["text_only"] += bool(d.get("text_only")); c["matcher_suspect"] += bool(d.get("matcher_suspect"))
    print(f"  {label}: assembly {c['assembly']} = in_evidence {c['in_evidence']} | in_reply_items {c['in_reply_items']} | in_reply_text {c['in_reply_text']}; text_only {c['text_only']} ({c['text_only']/max(1,n)*100:.1f}/100 needs), matcher_suspect {c['matcher_suspect']}")

# (3) 새로 assembly가 된 사례 20건: 조각 원문, 어디서 봤나, 일치 줄, 전달된 답
print(f"\n== (3) newly-assembly cases (first {NCASES}; 27B base ingress, then DeepSeek) ==")
import sqlite3
def hit_lines(f, text, names):
    c = canaries(f.get("text", ""))
    if c: return [l for l in text.splitlines() if canaries(l) & c][:2]
    sig = signature(f, names)
    if sig is None:
        key = _norm(f.get("text", ""))[:60]; return [l for l in text.splitlines() if key in _norm(l)][:2]
    return [l for l in text.splitlines() if _sig_hit(sig, _norm(l))][:2]
shown = 0
for f in sorted(G.glob("main__base__qwen3.5-27b__ingress__s*.json")) + sorted(G.glob("main__base__deepseek-v4-flash__ingress__s*.json")):
    seed = f.stem.split("__")[-1]; d = json.load(open(f)); run = Path(d["run"]); model = f.stem.split("__")[2]
    priv = load_private(M / "scenarios" / f"D5_{seed}_T45")
    old_rows = {(r["task_id"], r["need"]): r for r in json.load(open(OLD / f.name))["needs"]}
    ev = [json.loads(x) for x in (run / "wal" / "events.jsonl").read_text().splitlines() if x]
    db = sqlite3.connect(run / "llm_cache.sqlite")
    for r in judged(d["needs"]):
        o = old_rows[(r["task_id"], r["need"])]
        if r["gate"] != "L_sel.assembly" or o["gate"] == "L_sel.assembly" or shown >= NCASES: continue
        det = r["gate_detail"]; frag = priv.fragments[det["fid"]]
        mine = [e for e in ev if e["payload"].get("task_id") == r["task_id"]]
        where = [k for k in ("in_evidence", "in_reply_items", "in_reply_text") if det.get(k)]
        lines = []
        for e in mine:
            if e["type"] == "llm_call" and e["actor"] == f"boundary:{r['need'].split('/')[0]}":
                row = db.execute("select request from responses where key = ?", (e["payload"]["key"],)).fetchone()
                if not row: continue
                p = "\n".join(m.get("content") or "" for m in json.loads(row[0]).get("messages", []))
                it, tx = reply_sections(p)
                for tag, sec in (("E", evidence_section(p) if "records" in p else ""), ("R-item", it), ("R-text", tx)):
                    for l in hit_lines(frag, sec, priv.names): lines.append(f"[{tag}] {l[:150]}")
        final = next((e["payload"] for e in mine if e["type"] == "answer"), {})
        resp = [e["payload"] for e in mine if e["type"] == "message" and e["payload"].get("kind") == "response" and e["actor"].startswith("boundary:")]
        gw_ans = (resp[-1].get("response") or resp[-1].get("answer") or {}) if resp else {}
        gw_txt = (gw_ans.get("answer") if isinstance(gw_ans, dict) else str(gw_ans))[:160] if gw_ans else "(no gateway response found)"
        shown += 1
        print(f"\n#{shown} {model} {seed} {r['task_id']} class {r['class']} need {r['need']}  old={o['gate']} -> new=L_sel.assembly  seen in {where}  reached={det['reached']} window={det['holder_window']}")
        print(f"   frag {det['fid']}: {frag.get('text','')[:150]}")
        for l in dict.fromkeys(lines[:4]): print("   seen:", l)
        print(f"   gateway answer: {gw_txt}")
        print(f"   final exact={next((t['exact'] for t in d['tasks'] if t['task_id']==r['task_id']), None)}")
