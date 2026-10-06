"""층화 100건 감사 자료 만들기 (기준 셀 1~15일, 도달 가능 과제).
표본: 27B·DeepSeek × 4조건 × 4등급 = 32층 × 3건 = 96 + 9B 4건(조건마다 1) = 100. 층 안에서 (seed, task) 무작위(seed 0).
과제마다 dossier: 질문·답 형식·날짜, 정답, 반사실 답, need별 출처(DB 값·조각 원문·규정 원문·질의 결과), 모델 답과 판정,
그리고 매처 감사용으로 판정 대상 조각마다 매처 판정과 요청자가 그 그룹에서 받은 것(응답 원문·항목). Full-load는 매처 감사에서 뺌.
출력: audit100/dossiers/batch_{1..4}.md, audit100/index.json"""
import csv, json, random, sqlite3, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "/root/project/g2g")
from gbg.benchmarks.worldgen.scoring import load_private
from gbg.contracts.envelope import render_response

M = Path("/root/project/g2g_main"); A = M / "audit100"; (A / "dossiers").mkdir(parents=True, exist_ok=True)
PRIV = {s: load_private(M / "scenarios" / f"D5_{s}_T45") for s in ("s12", "s13", "s14")}
RULES = {s: json.load(open(M / "scenarios" / f"D5_{s}_T45" / "private" / "rulebook_full.json")) for s in PRIV}
DBV = {}
for s in PRIV:
    d = defaultdict(list)
    for line in open(M / "scenarios" / f"D5_{s}_T45" / "private" / "db_versions.jsonl"):
        r = json.loads(line); d[r["key"]].append(r)
    DBV[s] = d
rows = [r for r in csv.DictReader(open("/root/project/g2g/output/analysis_package/tables/tasks.csv"))
        if r["experiment"] == "main" and r["cell"] == "base" and r["reachable"] == "1" and r["within_target_days"] == "1"]
by = defaultdict(list)
for r in rows: by[(r["model"], r["condition"], r["state_class"])].append(r)
rng = random.Random(0); sample = []
for m in ("qwen3.5-27b", "deepseek-v4-flash"):
    for c in ("direct", "routing", "ingress", "full_load"):
        for k in "ABCD":
            pool = sorted(by[(m, c, k)], key=lambda r: (r["seed"], r["task_id"])); sample += rng.sample(pool, 3)
for c in ("direct", "routing", "ingress", "full_load"):
    pool = sorted([r for r in rows if r["model"] == "qwen3.5-9b" and r["condition"] == c], key=lambda r: (r["seed"], r["task_id"])); sample.append(rng.choice(pool))
LED = {}
def ledger(r):
    rid = f"main__base__{r['model']}__{r['condition']}__{r['seed']}"
    if rid not in LED: LED[rid] = json.load(open(M / "gates" / f"{rid}.json"))
    return LED[rid]
WAL = {}
def wal(r):
    p = M / "runs" / r["model"] / r["condition"] / r["seed"] / "wal" / "events.jsonl"
    if p not in WAL: WAL[p] = [json.loads(x) for x in p.read_text().splitlines() if x]
    return WAL[p]

def value_at(s, key, v):
    return next((x for x in DBV[s].get(key, []) if x["v"] == v), None)

def sources(s, g, n):
    out = []
    for src in n["sources"]:
        t = src["type"]
        if t == "db":
            x = value_at(s, src["key"], src["v"]); out.append(f"- DB `{src['key']}` v{src['v']} (recorded day {x and x['day']}, registered day {x and x['db_day']}): {json.dumps(x and x['value'], ensure_ascii=False)}")
        elif t == "frag":
            f = PRIV[s].fragments[src["frag"]["fid"]]; crit = src["frag"]["fid"] in (n.get("critical_components") or [])
            out.append(f"- RECORD {src['frag']['fid']}{' [decision-critical]' if crit else ''} ({f['origin']}/{f['kind']}, day {f['day']}, by {f['agent']}; DB shows {src.get('db_visible_v', 'n/a')}): {f['text']}")
        elif t == "rule":
            out.append(f"- RULE {src['ref']}: {json.dumps(RULES[s].get(src['ref']), ensure_ascii=False)[:600]}")
        elif t == "db_query":
            out.append(f"- QUERY {src.get('query') or json.dumps({k: v for k, v in src.items() if k not in ('type', 'result')}, ensure_ascii=False)[:300]} → {json.dumps(src.get('result'), ensure_ascii=False)[:600]}")
        else:
            out.append(f"- {t.upper()}: {json.dumps({k: v for k, v in src.items() if k != 'type'}, ensure_ascii=False)[:400]}")
    return out

def received(r, grp):
    """요청자가 그 그룹에서 받은 응답(경계 모듈 또는 그 그룹 에이전트), 과제 중."""
    req = None; out = []
    for e in wal(r):
        p = e["payload"]
        if p.get("task_id") != r["task_id"]: continue
        if e["type"] == "task_delivered": req = p["agent"]
        if e["type"] == "message" and p.get("kind") == "response" and p.get("from_agent") == req and p.get("serving") is None:
            src = e["actor"].split(":")[-1]; sg = src.upper() if src.isupper() or ":" not in e["actor"] else src.split(".")[0].upper()
            if e["actor"].startswith("boundary:"): sg = e["actor"].split(":")[1]
            if sg == grp: out.append(render_response(p.get("response") or {}))
    txt = "\n---\n".join(out)
    return (txt[:9000] + "\n[... truncated]") if len(txt) > 9000 else (txt or "(nothing received from this group)")

index = []; parts = defaultdict(list)
for i, r in enumerate(sample, 1):
    s = r["seed"]; P = PRIV[s]; g = P.gold[r["task_id"]]; t = P.tasks[r["task_id"]]
    led = ledger(r); needs = [n for n in led["needs"] if n["task_id"] == r["task_id"] and n["scored"]]
    L = [f"## CASE {i}: {r['model']} · {r['condition']} · {s} · {r['task_id']} · class {r['state_class']} · day {g['day']} · template {g['template']}",
         "### Task as given to the requester", t.text, "### Answer conventions", t.output_schema.conventions,
         "### Gold answer", json.dumps(g["gold"], ensure_ascii=False),
         "### Counterfactual answers (generator)", json.dumps({k: v.get("example_answer") for k, v in (g.get("counterfactual") or {}).items()}, ensure_ascii=False),
         "### World facts behind the gold (by need)"]
    for n in g["needs"]:
        L.append(f"**need {n['sem']}** (group {n['group']}, class {n['class']}, local={n['local']})"); L += sources(s, g, n)
    L += ["### Model answer and official verdict", f"answer: {r['answer_json'] or '(none)'}", f"official exact match: {r['exact']} ({r['slots_correct']}/{r['slots_total']} slots)"]
    mat = []
    if r["condition"] != "full_load":
        for n in needs:
            for fr in n["frags"]:
                if fr["state"] not in ("delivered", "stale", "missing"): continue
                f = P.fragments[fr["fid"]]
                mat.append({"fid": fr["fid"], "need": n["need"], "state": fr["state"]})
                L += [f"### MATCHER CHECK {fr['fid']} (need {n['need']}): matcher says **{fr['state']}**", f"record text: {f['text']}",
                      f"What the requester received from {n['need'].split('/')[0]} during this task:", "```", received(r, n["need"].split("/")[0]), "```"]
    index.append({"case": i, "model": r["model"], "condition": r["condition"], "seed": s, "task_id": r["task_id"], "class": r["state_class"],
                  "exact": r["exact"], "matcher": mat})
    parts[(i - 1) // 13 + 1].append("\n".join(L))
for b, cs in parts.items():
    (A / "dossiers" / f"batch_{b}.md").write_text("\n\n".join(cs), encoding="utf-8")
json.dump(index, open(A / "index.json", "w"), ensure_ascii=False, indent=1)
print(len(sample), "cases;", sum(len(x["matcher"]) for x in index), "matcher checks;", {b: len(cs) for b, cs in parts.items()},
      {b: round(len("\n\n".join(cs)) / 1000) for b, cs in parts.items()}, "k chars")
