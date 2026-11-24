"""LLM 재판정 결과 요약 (Markdown). regate_out/*.json, verdicts*.json, index.json을 읽는다."""
import json, os, sys, collections, random, re, gzip
from pathlib import Path
B = Path(__file__).resolve().parent; sys.path.insert(0, str(B))
from runs import runs
RUNS = {r["run_id"]: r for r in runs()}
L = {}
for rid in RUNS:
    f = B / "regate_out" / f"{rid}.json"
    if f.exists(): L[rid] = json.load(open(f))
ST = ["ok", "L_request", "L_reach", "L_observe.window", "L_observe.search", "L_respond", "L_select"]
NM = {"ok": "전달", "L_request": "request", "L_reach": "reach", "L_observe.window": "observe(window)", "L_observe.search": "observe(search)",
      "L_respond": "respond", "L_select": "select"}
def md(h, rows):
    return "\n".join(["| " + " | ".join(map(str, h)) + " |", "|" + "---|" * len(h)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows]) + "\n"
def needs(rid, tasks=None):
    return [n for n in L[rid]["needs"] if n["scored"] and not n["unreachable"] and (tasks is None or n["task_id"] in tasks)]
def pct(c, keys=ST):
    t = sum(c[k] for k in keys); return [f"{100 * c[k] / t:.1f}" if t else "-" for k in keys], t
out = []
P = out.append

# ── 1. 조각 단위: 휴리스틱 × LLM
P("## 1. 조각 단위: 기존 매처 판정과 LLM 판정\n")
conf = collections.Counter(); confc = collections.defaultdict(collections.Counter)
for rid, d in L.items():
    for n in needs(rid):
        for x in n["frags"]:
            if "llm" in x:
                h = n["heur_frags"][x["fid"]]; conf[(h, x["llm"])] += 1; confc[RUNS[rid]["cond"]][(h, x["llm"])] += 1
LL = ["current", "stale", "partial", "no"]; HH = ["delivered", "stale", "missing", "prior"]
P(md(["기존 매처 \\ LLM"] + LL + ["합"], [[h] + [conf[(h, l)] for l in LL] + [sum(conf[(h, l)] for l in LL)] for h in HH]))
tp = conf[("delivered", "current")]; hd = sum(conf[("delivered", l)] for l in LL); ld = sum(conf[(h, "current")] for h in HH)
P(f"LLM 판정을 기준으로 한 기존 매처: 정밀도 {tp}/{hd} = {100*tp/max(1,hd):.1f}%, 재현율 {tp}/{ld} = {100*tp/max(1,ld):.1f}%.\n")
rows = []
for c, cc in sorted(confc.items()):
    tp = cc[("delivered", "current")]; hd = sum(cc[("delivered", l)] for l in LL); ld = sum(cc[(h, "current")] for h in HH); tot = sum(cc.values())
    rows.append([f"`{c}`", tot, hd, ld, f"{100*tp/max(1,hd):.1f}", f"{100*tp/max(1,ld):.1f}", sum(cc[(h, 'partial')] for h in HH)])
P(md(["조건", "판정 조각", "매처 전달", "LLM 전달", "매처 정밀도 %", "매처 재현율 %", "LLM 부분 전달"], rows))

# ── 2. need 단위 전이
P("## 2. need 단위: 기존 고리 → 새 고리 (LLM이 판정한 need)\n")
def lab(n, old):
    g = n["gate_old"] if old else n["gate"]
    return g
tr = collections.Counter()
for rid in L:
    for n in needs(rid):
        if n["llm_judged"]: tr[(n["gate_old"], n["gate"])] += 1
keys = ST + sorted({k for a, b in tr for k in (a, b)} - set(ST))
P(md(["기존 \\ 새"] + [NM.get(k, k) for k in keys] + ["합", "유지 %"],
     [[NM.get(a, a)] + [tr[(a, b)] for b in keys] + [s := sum(tr[(a, b)] for b in keys), f"{100*tr[(a,a)]/max(1,s):.0f}"] for a in keys if sum(tr[(a, b)] for b in keys)]))

# ── 3. 조건별 분포: 기존과 새
def dist(rids, tasks_by_rid=None):
    o, n_, oc = collections.Counter(), collections.Counter(), collections.Counter()
    for rid in rids:
        for n in needs(rid, tasks_by_rid and tasks_by_rid.get(rid)):
            if n["gate_old"] in ST: o[n["gate_old"]] += 1
            if n["gate"] in ST: n_[n["gate"]] += 1
            if n["gate"] == "ok" and not n["delivered_frag"]: oc["comp_only_new"] += 1
            if n["gate_old"] == "ok" and not all(s == "delivered" for s in n["heur_frags"].values()): oc["comp_only_old"] += 1
    return o, n_, oc
def table(title, groups, note=""):
    P(f"### {title}\n"); 
    if note: P(note + "\n")
    rows = []
    for name, rids, tk in groups:
        rids = [r for r in rids if r in L]
        if not rids: continue
        o, n_, oc = dist(rids, tk)
        po, to = pct(o); pn, tn = pct(n_)
        rows.append([name, "기존", to] + po + [f"{100*oc['comp_only_old']/max(1,to):.1f}"])
        rows.append(["", "LLM", tn] + pn + [f"{100*oc['comp_only_new']/max(1,tn):.1f}"])
    P(md(["조건", "판정", "need"] + [NM[k] for k in ST] + ["그중 계산값만으로 전달"], rows))
def rid_main(m, c): return [f"main__base__{m}__{c}__{s}" for s in ("s12", "s13", "s14")]
def common(rid_lists, max_day=None):
    """시드별로 모든 조건이 채점된 과제의 교집합 (도달 가능, 일수 안)."""
    tk = {}
    for s in ("s12", "s13", "s14"):
        sets = []
        for rl in rid_lists:
            rid = next((r for r in rl if r.endswith(s)), None)
            if rid is None or rid not in L: continue
            sets.append({t["task_id"] for t in L[rid]["tasks"] if not t["unreachable"] and (max_day is None or t["day"] <= max_day)})
        inter = set.intersection(*sets) if sets else set()
        for rl in rid_lists:
            rid = next((r for r in rl if r.endswith(s)), None)
            if rid: tk[rid] = inter
    return tk
MODELS = [("qwen3.5-27b", "27B"), ("deepseek-v4-flash", "DeepSeek"), ("qwen3.5-9b", "9B")]
P("## 3. 조건별 손실 지점: 기존 채점기와 LLM 재판정\n")
P("값은 판정 가능한 need 가운데 비율(%). full_load는 LLM 판정 대상이 아니라 두 줄이 같다.\n")
g = []
for m, mn in MODELS:
    lists = [rid_main(m, c) for c in ("direct", "routing", "ingress", "full_load")]
    tk = common(lists, 15)
    for c, rl in zip(("direct", "routing", "ingress", "full_load"), lists): g.append((f"{mn} `{c}`", rl, tk))
table("3.1 본 실험 (기준 셀, 1~15일, 모델별 4조건 공통 과제)", g)
def rid27(c):
    if c in ("direct", "routing", "ingress", "full_load"): return rid_main("qwen3.5-27b", c)
    if c in ("direct_relay", "retrieve", "sidecar"): return [f"appendix__base__qwen3.5-27b__{c}__{s}" for s in ("s12", "s13", "s14")]
    return [f"rebuttal__A__{c}__{s}" for s in ("s12", "s13", "s14")]
C10 = ["direct", "direct_relay", "routing", "retrieve", "sidecar", "ingress_plain_sym", "ingress_no_requery", "ingress", "rag_only", "full_load"]
lists = [rid27(c) for c in C10]; tk27 = common(lists, 10)
table("3.2 27B 10개 조건 (기준 셀, 1~10일, 공통 과제)", [(f"`{c}`", rl, tk27) for c, rl in zip(C10, lists)],
      f"공통 과제 수: {sum(len(v) for k, v in tk27.items() if '__direct__' in k and 'main' in k)}")
g = []
for m, mn in MODELS[1:]:
    lists = [rid_main(m, c) for c in ("direct", "routing", "ingress", "full_load")] + [[f"rebuttal__C__{m}__sidecar__{s}" for s in ("s12", "s13", "s14")]]
    tk = common(lists, 10)
    for c, rl in zip(("direct", "routing", "sidecar", "ingress", "full_load"), [lists[0], lists[1], lists[4], lists[2], lists[3]]): g.append((f"{mn} `{c}`", rl, tk))
table("3.3 다른 모델 (기준 셀, 1~10일, 5조건 공통 과제)", g)
g = []
for cell in ("R1", "D3", "R3"):
    lists = [[f"gcell__{cell}__qwen3.5-27b__{c}__{s}" for s in ("s12", "s13", "s14")] for c in ("direct", "routing", "ingress", "full_load")]
    tk = common(lists, 10)
    for c, rl in zip(("direct", "routing", "ingress", "full_load"), lists): g.append((f"{cell} `{c}`", rl, tk))
table("3.4 그룹 수 셀 (27B, 1~10일, 셀별 4조건 공통 과제)", g)
g = []
for cell in ("K16k", "lag1", "warm10"):
    lists = [[f"rebuttal__D__{cell}__{c}__s12"] for c in ("direct", "sidecar")]
    tk = common(lists, 10)
    for c, rl in zip(("direct", "sidecar"), lists): g.append((f"{cell} `{c}`", rl, tk))
table("3.5 민감도 셀 (27B, 시드 12, 1~10일)", g)

# ── 4. 과제 결과 (use / lost)
P("## 4. 과제 단위 결과: 전달됐는데 오답(use), 손실 있음(lost)\n")
rows = []
for name, rl in [(f"{mn} `{c}`", rid_main(m, c)) for m, mn in MODELS for c in ("direct", "routing", "ingress")] + \
                [(f"27B `{c}`", rid27(c)) for c in ("direct_relay", "retrieve", "sidecar", "ingress_plain_sym", "ingress_no_requery", "rag_only")] + \
                [(f"{mn} `sidecar`", [f"rebuttal__C__{m}__sidecar__{s}" for s in ("s12", "s13", "s14")]) for m, mn in MODELS[1:]]:
    o, n_ = collections.Counter(), collections.Counter(); jd = [0, 0, 0, 0]
    for rid in rl:
        if rid not in L: continue
        byt = collections.defaultdict(list)
        for n in needs(rid): byt[n["task_id"]].append(n)
        for t in L[rid]["tasks"]:
            if t["unreachable"] or t["task_id"] not in byt: continue          # 판정 가능한 need가 있는 과제만
            ns = byt[t["task_id"]]
            for k, key in ((0, "gate_old"), (2, "gate")):
                if all(n[key] == "ok" for n in ns): jd[k] += 1; jd[k + 1] += t["exact"]
            o[t["outcome_old"]] += 1; n_[t["outcome"]] += 1
    rows.append([name, sum(o.values()), f"{jd[1]}/{jd[0]}", f"{jd[3]}/{jd[2]}", f"{100*jd[1]/max(1,jd[0]):.0f} → {100*jd[3]/max(1,jd[2]):.0f}"])
P("판정 가능한 need가 있는 과제 가운데, 판정된 need가 모두 전달된 과제의 정답 수 / 과제 수.\n")
P(md(["조건", "과제", "기존: 정답/모두 전달", "LLM: 정답/모두 전달", "정답률 % (기존 → LLM)"], rows))

# ── 5. 판정의 믿을 만함
P("## 5. 판정 점검\n")
def _lj(n):
    f = B / n
    return json.load(open(f)) if f.exists() else json.load(gzip.open(str(f) + ".gz"))
idx = _lj("index.json"); V = _lj("verdicts.json"); D = _lj("verdicts_dup.json")
cm = {x["case"]: x for x in idx if not x["dup"]}
agree = collections.Counter(); pairs = collections.Counter()
for case, d in D.items():
    x = cm.get(case)
    if not x: continue
    v = V.get(x["run_id"], {}).get(x["task_id"])
    if not v: continue
    for fid, r in d["F"].items():
        if fid in v["F"]:
            a, b = v["F"][fid]["received"], r["received"]; agree["F_n"] += 1; agree["F_same"] += a == b; agree["F_bin"] += (a == "current") == (b == "current")
            pairs[tuple(sorted((a, b)))] += 1
            if v["F"][fid]["inside"] != "na" and r["inside"] != "na": agree["I_n"] += 1; agree["I_bin"] += (v["F"][fid]["inside"] == "current") == (r["inside"] == "current")
    for nd, r in d["C"].items():
        if nd in v["C"]: agree["C_n"] += 1; agree["C_same"] += v["C"][nd] == r
P(f"- 같은 과제를 다른 판정자가 한 번 더 판정 ({len(D)}과제): 조각 판정 {agree['F_n']}건 중 네 값 일치 {agree['F_same']} ({100*agree['F_same']/max(1,agree['F_n']):.1f}%), "
  f"전달 여부 일치 {agree['F_bin']} ({100*agree['F_bin']/max(1,agree['F_n']):.1f}%); 그룹 안 응답 {agree['I_n']}건 중 일치 {agree['I_bin']}; "
  f"계산값 {agree['C_n']}건 중 일치 {agree['C_same']} ({100*agree['C_same']/max(1,agree['C_n']):.1f}%).")
P("- 어긋난 쌍: " + ", ".join(f"{a}/{b} {n}" for (a, b), n in pairs.most_common() if a != b) + ".")
qa = collections.Counter()
for rid, ts in V.items():
    for t, v in ts.items():
        for fid, r in v["F"].items():
            if "quote_ok" in r: qa["n"] += 1; qa["ok"] += r["quote_ok"]
            if "iquote_ok" in r: qa["n"] += 1; qa["ok"] += r["iquote_ok"]
        for nd, r in v.get("Cq", {}).items():
            if "quote_ok" in r: qa["n"] += 1; qa["ok"] += r["quote_ok"]
P(f"- 인용 대조: 인용 {qa['n']}건 중 {qa['ok']}건이 지목한 메시지 원문에 그대로 있음 ({100*qa['ok']/max(1,qa['n']):.1f}%).")
# 이전 감사(194건)와 비교
A = Path(os.environ["AUDIT_DIR"])
ai = {x["case"]: x for x in json.load(open(A / "index.json"))}; cmp_ = collections.Counter()
for f in sorted((A / "results").glob("*.jsonl")):
    for l in open(f):
        if not l.strip(): continue
        r = json.loads(l); x = ai[r["case"]]; rid = f"main__base__{x['model']}__{x['condition']}__{x['seed']}"
        v = V.get(rid, {}).get(x["task_id"])
        for m in r.get("matcher") or []:
            if v and m["fid"] in v["F"]:
                new = {"current": "delivered", "stale": "stale", "partial": "missing", "no": "missing"}[v["F"][m["fid"]]["received"]]
                cmp_[(m["human"], new)] += 1
tot = sum(cmp_.values()); same = sum(n for (a, b), n in cmp_.items() if a == b)
P(f"- 이전 감사(검토자 판정 194건)와 겹치는 조각 {tot}건 중 같은 판정 {same}건 ({100*same/max(1,tot):.1f}%). 어긋난 것: " +
  ", ".join(f"감사 {a} / 이번 {b} {n}" for (a, b), n in sorted(cmp_.items()) if a != b) + ".")
# 대조 표본
kinds = collections.defaultdict(collections.Counter)
for x in idx:
    if x["dup"]: continue
    v = V.get(x["run_id"], {}).get(x["task_id"])
    if not v or x["run_id"] not in L: continue
    for n in L[x["run_id"]]["needs"]:
        if n["task_id"] == x["task_id"] and n["scored"] and n["llm_judged"]:
            kinds[x["kind"]]["needs"] += 1; kinds[x["kind"]]["changed"] += n["gate"] != n["gate_old"]
P("- 표본 종류별 고리가 바뀐 need: " + "; ".join(f"{k} {c['changed']}/{c['needs']}" for k, c in kinds.items()) + " (cold = 대조 표본: respond·select·observe·계산값 전달 need가 없는 과제).")
(B / "SUMMARY.md").write_text("\n".join(out), encoding="utf-8"); print("\n".join(out))
