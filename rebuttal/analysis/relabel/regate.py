"""LLM 판정을 넣어 손실 고리를 다시 매긴다. 사슬 규칙은 gbg/scoring/gates.py 그대로이고, 바꾸는 것은 세 가지 입력뿐이다.
  A  조각이 요청자에게 도착했는가        (delivery.py의 카나리·서명 매칭 대신: current→delivered, stale→stale, partial·no→missing)
  B  조각이 그룹 안 구성원 응답에 있었는가 (조립 조건의 in_reply_items·in_reply_text, relay의 relay_seen에 OR)
  C  계산형 need의 중간값이 도착했는가    (delivery.py의 computed 대신)
판정이 없는 조각·need는 휴리스틱 값을 그대로 쓴다.
    python regate.py RUN_ID VERDICTS.json OUT.json      (VERDICTS: run_id → task_id → {"F": {fid: {received, inside}}, "C": {need: yes|no}})
"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.environ["G2G_CODE"]); sys.path.insert(0, str(Path(__file__).resolve().parent))
from gbg.benchmarks.worldgen.scoring import load_private, strata, verify
from gbg.contracts.envelope import render_response
from gbg.scoring.delivery import need_delivery
from gbg.scoring.gates import (RANK, _group_of, _question, about, evidence_section, need_surfaces, present, reply_sections,
                               window_state)
from gbg.scoring.ledger import _error_code, load_events, load_prompts
from gbg.scoring.reachability import unreachable
from runs import runs, load_json


def need_gates_llm(events, g, fragments, delivery_rows, prompts, names, inside):
    """gates.need_gates와 같은 규칙. inside: fid → 그룹 안 응답 판정(B). 조각마다 고리와 근거를 모두 돌려준다."""
    wid = g["wid"]
    req = next((e["payload"]["agent"] for e in events if e["type"] == "task_delivered"), None)
    mine = [e for e in events if e["payload"].get("task_id") == wid]
    asks = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
            and e["payload"].get("from_agent") == req and e["payload"].get("serving") is None]
    decisions = [e["payload"] for e in mine if e["type"] == "boundary_decision"]
    ingress = [d for d in decisions if d.get("stage") in ("ingress", "sidecar")]
    egress_targets = {t["group"] for d in decisions if d.get("stage") == "egress" for t in d.get("targets", [])}
    inner = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request" and e["actor"].startswith("boundary:")]
    relay_asks = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
                  and e["payload"].get("serving") is not None and e["actor"].startswith("agent:")]
    relay_replies = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "response"
                     and e["payload"].get("serving") is not None and e["actor"].startswith("agent:")]
    llm = [e for e in mine if e["type"] == "llm_call"]
    searched = any(e["type"] == "tool_call" and e["payload"].get("tool") == "search_memory" and e["payload"].get("agent") == req for e in mine)

    def prompt_text(e):
        return "\n".join(m.get("content") or "" for m in (prompts.get(e["payload"].get("key")) or []))

    out = []
    for row in delivery_rows:
        need = next(n for n in g["needs"] if n["sem"] == row["need"])
        grp = need["group"]; surf = need_surfaces(need, fragments, names)
        asked_group = any((a.get("to_group") == grp) or _group_of(a.get("to_agent") or "") == grp for a in asks) or grp in egress_targets or searched
        modes = {d.get("deliver") for d in ingress if d.get("group") == grp} or {d.get("deliver") for d in ingress}
        mode = "assemble" if "assemble" in modes else "read" if "read" in modes else "forward" if "forward" in modes else None
        eta = int(mode in ("assemble", "read") or searched)
        if row.get("delivered"):
            out.append({"need": row["need"], "group": grp, "gate": "ok", "eta": eta}); continue
        cand = []
        for x in row["frags"]:
            if x["state"] == "delivered": continue
            f = fragments[x["fid"]]
            holders = {f["agent"], *[h["agent"] for s in need["sources"] if s["type"] == "frag" and s["frag"]["fid"] == x["fid"] for h in s["frag"].get("holders", [])]}
            direct_to = {a.get("to_agent") for a in asks if a.get("to_agent") and about(_question(a), surf)}
            selected = {a for d in ingress if d.get("group") == grp and about(d.get("question"), surf) for a in d.get("selected", [])}
            colleagues = {m.get("to_agent") for m in relay_asks if _group_of(m.get("to_agent") or "") == grp and about(_question(m), surf)}
            reached = (direct_to | selected | colleagues | {m.get("to_agent") for m in inner if about(_question(m), surf)}) & holders
            ev_prompts = [prompt_text(e) for e in llm if e["actor"] == f"boundary:{grp}"]
            in_evidence = any(present(f, evidence_section(p), names) for p in ev_prompts if "records" in p)
            resp_prompts = [prompt_text(e) for e in llm if e["payload"].get("agent") in reached and e["payload"].get("component") == "responder"]
            win = max((window_state(f, p, names) for p in resp_prompts), key=["none", "summary", "verbatim"].index, default="none")
            b = inside.get(x["fid"]) == "current"                                # B: 그룹 안 응답에 있었다 (LLM 판정)
            detail = {"fid": x["fid"], "state": x["state"], "stale": x["state"] == "stale", "reached": sorted(reached),
                      "in_evidence": in_evidence, "holder_window": win, "inside_llm": inside.get(x["fid"])}
            in_items = in_text = relay_seen = False
            if mode == "assemble":
                secs = [reply_sections(p) for p in ev_prompts]
                in_items = any(it and present(f, it, names) for it, _ in secs)
                in_text = any(tx and present(f, tx, names) for _, tx in secs) or b
                detail.update(in_reply_items=in_items, in_reply_text=in_text)
            if colleagues:
                relay_seen = b or any(present(f, render_response(m.get("response") or {}), names) for m in relay_replies if _group_of(m.get("to_agent") or "") == grp)
                detail["relay_seen"] = relay_seen
            if not asked_group: st = "L_request"
            elif searched and not ingress: st = "L_observe.search"
            elif mode in ("assemble", "read"):
                if in_evidence or in_items or in_text: st = "L_select"
                elif reached and win == "verbatim": st = "L_respond"
                elif reached: st = "L_observe.window"
                else: st = "L_observe.search"
            elif not reached: st = "L_reach"
            elif relay_seen: st = "L_select"
            elif win != "verbatim": st = "L_observe.window"
            else: st = "L_respond"
            cand.append((RANK[st], len(cand), st, detail))
        if not cand:
            out.append({"need": row["need"], "group": grp, "gate": "ok", "eta": eta}); continue
        _, _, st, detail = min(cand)
        out.append({"need": row["need"], "group": grp, "gate": st, **detail, "eta": eta, "stale_any": any(d["stale"] for *_, d in cand),
                    "frag_stages": [{"fid": d["fid"], "stage": s_, "stale": d["stale"]} for _, _, s_, d in cand]})
    return out


STATE = {"current": "delivered", "stale": "stale", "partial": "missing", "no": "missing"}


def main(run_id, verdict_file, out_file):
    R = next(r for r in runs() if r["run_id"] == run_id)
    V = load_json(verdict_file).get(run_id, {})
    priv = load_private(Path(R["scen"])); ev = load_events(Path(R["run_dir"]))
    old = load_json(R["ledger"])
    old_need = {(n["task_id"], n["need"]): n for n in old["needs"]}
    wids = sorted({t for t, _ in old_need})
    by_task = {}
    for e in ev:
        t = e["payload"].get("task_id")
        if t in priv.gold: by_task.setdefault(t, []).append(e)
    keys = {e["payload"]["key"] for t in wids for e in by_task.get(t, []) if e["type"] == "llm_call"}
    prompts = load_prompts(Path(R["run_dir"]) / "llm_cache.sqlite", keys)
    delivery = need_delivery(ev, {w: priv.gold[w] for w in wids if w in by_task}, priv.fragments, names=priv.names, computed=priv.computed)["needs"]
    unreach = unreachable([priv.gold[w] for w in by_task])
    needs, tasks = [], []
    for wid in wids:
        es, g = by_task.get(wid, []), priv.gold[wid]
        if not es: continue
        v = V.get(wid, {"F": {}, "C": {}})
        ans = next((e["payload"] for e in es if e["type"] == "answer"), None)
        answer = (ans or {}).get("answer") if ans and ans.get("error") is None else None
        exact = verify(priv.tasks[wid], answer, g)["exact"]; err = _error_code(ans)
        rows = [json.loads(json.dumps(r)) for r in delivery if r["task_id"] == wid]
        for r in rows:                                                      # A·C: LLM 판정으로 전달 상태를 바꾼다
            r["heur"] = {"frags": {x["fid"]: x["state"] for x in r["frags"]}, "computed": r["computed"], "delivered": r["delivered"]}
            for x in r["frags"]:
                j = v["F"].get(x["fid"])
                if j and x["method"] != "none":
                    x["state"] = STATE[j["received"]]; x["llm"] = j["received"]
            judged = [x for x in r["frags"] if x["method"] != "none"]
            if r["need"] in v["C"]: r["computed"] = v["C"][r["need"]] == "yes"
            r["delivered"] = bool(judged) and (bool(r["computed"]) or all(x["state"] == "delivered" for x in judged))
            r["delivered_frag"] = bool(judged) and all(x["state"] == "delivered" for x in judged)
        inside = {fid: j.get("inside") for fid, j in v["F"].items()}
        gates = {x["need"]: x for x in need_gates_llm(es, g, priv.fragments, rows, prompts, priv.names, inside)}
        mine = []
        for r in rows:
            gt = gates.get(r["need"], {}); o = old_need.get((wid, r["need"]), {})
            gate = "unjudged" if not r["scored"] else err if (err and gt.get("gate") != "ok") else gt.get("gate")
            mine.append({"task_id": wid, "need": r["need"], "class": r["class"], "scored": r["scored"], "unreachable": wid in unreach,
                         "gate_old": o.get("gate"), "gate": gate, "delivered_old": o.get("delivered"), "delivered": r["delivered"],
                         "delivered_frag": r["delivered_frag"], "computed": r["computed"], "computed_old": r["heur"]["computed"],
                         "llm_judged": any("llm" in x for x in r["frags"]) or r["need"] in v["C"],
                         "frags": r["frags"], "heur_frags": r["heur"]["frags"],
                         "detail": {k: gt[k] for k in gt if k not in ("need", "group", "gate")}})
        needs += mine
        ot = next((t for t in old["tasks"] if t["task_id"] == wid), {})
        tasks.append({"task_id": wid, "day": g.get("day"), "exact": exact, "error": err, "unreachable": wid in unreach, "class": g.get("state_class"),
                      "template": g.get("template"), "outcome_old": ot.get("outcome"),
                      "outcome": err or ("correct" if exact else "use" if all(n["gate"] in ("ok", "unjudged") for n in mine) else "lost")})
    json.dump({"run_id": run_id, "tasks": tasks, "needs": needs}, open(out_file, "w"), ensure_ascii=False)
    same = sum(n["gate"] == n["gate_old"] for n in needs)
    print(run_id, "needs", len(needs), "same gate", same, "changed", len(needs) - same, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
