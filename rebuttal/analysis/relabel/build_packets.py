"""LLM 재판정용 자료(case) 만들기. 과제 하나 = case 하나 (조건·모델 이름은 넣지 않는다).
case: 과제 문장, 판정할 조각(원문·값·옛 버전·엔티티 이름), 계산형 need의 중간값, 요청자가 받은 메시지(M#),
그룹 안에서만 오간 구성원 응답(I#, 조립 조건과 relay). full_load는 뺀다(검색 결과가 기록 원문 그대로라 문자열 대조 대상).
출력: cases.jsonl (case마다 메타 + 본문 text), 표준출력에 크기 통계."""
import json, os, re, sys, random, collections
from pathlib import Path
sys.path.insert(0, os.environ["G2G_CODE"]); sys.path.insert(0, str(Path(__file__).resolve().parent))
from gbg.benchmarks.worldgen.scoring import load_private
from gbg.contracts.envelope import render_response
from gbg.scoring.gates import need_surfaces, _group_of
from gbg.scoring.delivery import canaries, _norm
from runs import runs, load_json

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
PRIV = {}
def priv(sc):
    if sc not in PRIV: PRIV[sc] = load_private(Path(sc))
    return PRIV[sc]

def actor_group(actor):
    if actor.startswith("boundary:"): return actor.split(":", 1)[1]
    if actor.startswith("agent:"): return actor.split(":", 1)[1].split(".")[0].upper()
    return ""

def mentions(text, surfs, cans):
    t = _norm(text)
    return bool(cans & canaries(text)) or any(re.search(rf"(?<!\w){re.escape(x)}(?!\w)", t) for x in surfs)

def trim_records(answer, surfs, cans):
    """Retrieve 응답에 붙은 [Group records]의 [E#] 항목 가운데 판정 대상 엔티티·값이 나오지 않는 항목은 뺀다."""
    if "[Group records]" not in answer: return answer
    head, rec = answer.split("[Group records]", 1)
    ents = re.split(r"\n(?=\[E\d+\] )", rec.strip("\n"))
    keep = [e for e in ents if mentions(e, surfs, cans)]
    return head + "[Group records]\n" + "\n".join(keep) + (f"\n[{len(ents) - len(keep)} other records omitted: they do not mention the entities or values under review]" if len(ents) > len(keep) else "")

def render(r, surfs, cans):
    r = dict(r); r["answer"] = trim_records(r.get("answer") or "", surfs, cans)
    seen, items = {}, []
    for x in r.get("items") or []:                                      # 같은 항목(출처 표기만 다름)은 한 줄로
        k = (x.get("entity"), x.get("attribute"), str(x.get("value")), x.get("status", x.get("status_or_as_of", "")), str(x.get("day")))
        if k in seen: seen[k]["_n"] += 1
        else:
            seen[k] = dict(x, _n=1); items.append(seen[k])
    r["items"] = [dict({k: v for k, v in x.items() if k != "_n"}, ref=x.get("ref", "") + (f" (+{x['_n'] - 1} identical items from other replies)" if x["_n"] > 1 else "")) for x in items]
    t = render_response(r)
    if r.get("status") and r["status"] != "ok": t = f"(status: {r['status']})\n" + t
    return t or "(empty reply)"

cases = []; stat = collections.Counter()
for R in runs():
    if R["cond"] == "full_load": continue
    P = priv(R["scen"]); led = load_json(R["ledger"])
    by_task = collections.defaultdict(list)
    for n in led["needs"]:
        if n["scored"] and not n.get("unreachable"): by_task[n["task_id"]].append(n)
    ev_by = collections.defaultdict(list)
    for line in open(R["run_dir"] + "/wal/events.jsonl"):
        e = json.loads(line); t = e["payload"].get("task_id")
        if t in by_task: ev_by[t].append(e)
    by_key = collections.defaultdict(list)
    for f in P.fragments.values():
        if f.get("key"): by_key[f["key"]].append(f)
    for wid, needs in sorted(by_task.items()):
        g = P.gold[wid]; evs = ev_by[wid]
        req = next((e["payload"]["agent"] for e in evs if e["type"] == "task_delivered"), None)
        if req is None: continue
        gneeds = {n["sem"]: n for n in g["needs"]}
        surfs, cans, groups = [], set(), set()
        L = [f"Simulation day of the task: {g['day']}", "Task given to the requester: " + P.tasks[wid].text.split("\n")[0], "", "## Records under review"]
        frag_ids, comp_needs = [], []
        for n in needs:
            gn = gneeds[n["need"]]; groups.add(gn["group"])
            surfs += need_surfaces(gn, P.fragments, P.names)
            L.append(f"### Need `{n['need']}` (owned by group {gn['group']})")
            comp = (P.computed or {}).get(wid, {}).get(n["need"])
            if comp:
                comp_needs.append(n["need"])
                for ents, vals in comp:
                    nm = [x for e in ents for x in (e, *P.names.get(e, []))]
                    L.append(f"- COMPUTED QUANTITY for {' / '.join(nm)}: the correct value is {' or '.join(str(v) for v in vals)} (derived from the records below plus database values; it appears in no record verbatim)")
            for fr in n["frags"]:
                if fr["method"] == "none": continue
                f = P.fragments[fr["fid"]]; frag_ids.append(fr["fid"]); cans |= canaries(f.get("text", ""))
                ent = (f.get("key") or "").split("/")
                nm = [ent[2], *P.names.get(ent[2], [])] if len(ent) > 2 else []
                L.append(f"- RECORD {fr['fid']} (day {f['day']}; entity: {' / '.join(nm) or 'n/a'}; field `{f.get('key')}`)\n  text: {f['text']}\n  stored value: {json.dumps(f.get('value'), ensure_ascii=False)}")
                older = sorted((o for o in by_key.get(f.get("key"), []) if o["fid"] != f["fid"] and o.get("seq", 0) < f.get("seq", 0)), key=lambda o: o.get("seq", 0))
                same = [o for o in older if not canaries(f.get("text", "")) or canaries(o.get("text", "")) == canaries(f.get("text", ""))]
                for o in same[-3:]:
                    L.append(f"  older version (superseded, day {o['day']}): {o['text']} | value: {json.dumps(o.get('value'), ensure_ascii=False)}")
        if not frag_ids: continue
        surfs = [x for x in dict.fromkeys(surfs)]
        M, I = [], []
        # 그룹 안 응답(I#)은 조립 조건·relay에서만, 그리고 그 판정이 고리를 바꿀 수 있는 과제에서만 싣는다
        settled = lambda n: n["gate"] == "L_request" or (n["gate"] == "ok" and all(x["state"] == "delivered" for x in n["frags"] if x["method"] != "none")) \
            or (n["gate"] == "L_select" and n["gate_detail"].get("in_evidence") and len(n["gate_detail"].get("frag_stages") or []) <= 1)
        want_inside = R["cond"] in ("ingress", "ingress_no_requery", "ingress_plain_sym", "direct_relay") and not all(settled(n) for n in needs)
        for e in evs:
            p = e["payload"]
            if e["type"] == "message" and p.get("kind") == "response" and not e["actor"].startswith("kernel"):
                r = p.get("response") or {}; grp = actor_group(e["actor"]); txt = render(r, surfs, cans)
                q = (p.get("question") or "").strip(); qfull = q
                if len(q) > 400: q = q[:400] + " [...]"
                if p.get("from_agent") == req and p.get("serving") is None:
                    if grp in groups or mentions(txt, surfs, cans):
                        M.append(f"[M{len(M) + 1}] reply from group {grp} to the requester's question: \"{q}\"\n{txt}")
                elif want_inside and p.get("serving") is not None and e["actor"].startswith("agent:") and grp in groups \
                        and mentions(qfull.split("Records of your group on these items", 1)[0] + "\n" + txt, surfs, cans):
                    I.append(f"[I{len(I) + 1}] reply written by a member of {grp}, seen only inside {grp} (question: \"{q}\")\n{txt}")
            elif e["type"] == "tool_result" and p.get("agent") == req and p.get("serving") is None:
                txt = json.dumps(p.get("result"), ensure_ascii=False)
                if mentions(txt, surfs, cans):
                    M.append(f"[M{len(M) + 1}] result of the requester's own tool call `{p.get('tool')}`\n" + (txt[:2500] + " [...truncated]" if len(txt) > 2500 else txt))
        L += ["", "## Messages the requester received during the task"] + (M or ["(none from these groups, and nothing else mentioning these entities)"])
        if I: L += ["", "## Replies that stayed inside the group (the requester did NOT see these)"] + I
        gate = collections.Counter(n["gate"] if n["gate"] != "ok" else ("ok_frag" if all(x["state"] == "delivered" for x in n["frags"] if x["method"] != "none") else "ok_comp") for n in needs)
        text = "\n".join(L)
        cases.append({"run_id": R["run_id"], "task_id": wid, "frags": frag_ids, "computed": comp_needs, "gates": dict(gate),
                      "nM": len(M), "nI": len(I), "chars": len(text), "text": text})
        stat["cases"] += 1; stat["frags"] += len(frag_ids); stat["chars"] += len(text)
    print(R["run_id"], stat["cases"], stat["chars"], flush=True)
random.Random(0).shuffle(cases)
for i, c in enumerate(cases, 1): c["case"] = f"K{i:05d}"
with open(OUT / "cases.jsonl", "w") as f:
    for c in cases: f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(dict(stat))
