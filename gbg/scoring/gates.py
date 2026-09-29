"""need별 처음 끊긴 게이트 (채점기, 오프라인. v0 휴리스틱).

need마다 결정 필수 조각을 차례로 보며, 전달되지 않은 첫 조각이 어디서 끊겼는지 정한다.

    ok           모두 전달되고 답도 맞음
    L_use        모두 전달됐는데 답이 틀림 (추론·사용 실패)
    L_state      옛 버전만 전달됨
    L_req        요청자가 그 need의 그룹에 묻지 않음
    L_route      그룹에는 물었지만 보유자에게 닿지 않음 (Direct: 다른 에이전트에게 물음 / 경계: 보유자를 고르지 않음,
                 Ingress는 증거에도 없음)
    L_sel.window 보유자에게 물었지만 보유자의 컨텍스트 창에 그 조각이 없음 (창 밖으로 밀려남)
    L_sel.answer 보유자 창에는 있었는데 답에 싣지 않음
    L_sel.search Ingress: 보유자도 고르지 않았고 증거 블록에도 없음 (검색 실패)
    L_sel.assembly Ingress: 증거 블록 또는 응답에 있었는데 조립 답에 빠짐

"창"과 "증거"는 LLM 호출의 입력(캐시에 저장된 요청)에서 확인한다. 조각의 존재는 delivery.py와 같은 카나리/서명 기준.
"""
import json
import re

from .delivery import _norm, _sig_hit, canaries, signature


def present(f: dict, text: str, names: dict) -> bool:
    c = canaries(f.get("text", ""))
    if c:
        return c <= canaries(text)
    sig = signature(f, names)
    if sig is None:
        return _norm(f.get("text", ""))[:60] in _norm(text)
    return any(_sig_hit(sig, _norm(line)) for line in text.splitlines())


def window_state(f: dict, prompt: str, names: dict) -> str:
    """응답자 창에서 조각의 상태: 원문(verbatim) / 요약(summary) / 없음(none)."""
    verb = prompt.split("[Recent records, verbatim]", 1)[1].split("[Current task]", 1)[0] if "[Recent records, verbatim]" in prompt else ""
    summ = prompt.split("[Earlier records, summarized, newest first]", 1)[1].split("[Recent records, verbatim]", 1)[0] \
        if "[Earlier records, summarized" in prompt else ""
    if verb and present(f, verb, names):
        return "verbatim"
    ent = (f.get("key") or "").split("/")
    if summ and len(ent) > 2 and _norm(ent[2]) in _norm(summ):
        return "summary"
    return "none"


def _group_of(agent: str) -> str:
    return agent.split(".")[0].upper() if agent and not agent.startswith("boundary:") else ""


def need_gates(events: list[dict], g: dict, fragments: dict, delivery_rows: list[dict], prompts: dict,
               answer_ok: bool, names: dict | None = None) -> list[dict]:
    """과제 하나의 need별 판정. prompts: llm_call key → 요청 messages (캐시)."""
    names = names or {}
    wid = g["wid"]
    req = next((e["payload"]["agent"] for e in events if e["type"] == "task_delivered"), None)
    mine = [e for e in events if e["payload"].get("task_id") == wid]
    asks = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
            and e["payload"].get("from_agent") == req and e["payload"].get("serving") is None]
    decisions = [e["payload"] for e in mine if e["type"] == "boundary_decision"]
    ingress = [d for d in decisions if d.get("stage") == "ingress"]
    egress_targets = {t["group"] for d in decisions if d.get("stage") == "egress" for t in d.get("targets", [])}
    inner = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["actor"].startswith("boundary:")]
    llm = [e for e in mine if e["type"] == "llm_call"]

    def prompt_text(e) -> str:
        msgs = prompts.get(e["payload"].get("key")) or []
        return "\n".join(m.get("content") or "" for m in msgs)

    out = []
    for row in delivery_rows:
        need = next(n for n in g["needs"] if n["sem"] == row["need"])
        grp = need["group"]
        asked_group = any((a.get("to_group") == grp) or _group_of(a.get("to_agent") or "") == grp for a in asks) \
            or grp in egress_targets
        verdict, detail = "ok", {}
        for x in row["frags"]:
            if x["state"] == "delivered":
                continue
            f = fragments[x["fid"]]
            holders = {f["agent"], *[h["agent"] for s in need["sources"] if s["type"] == "frag"
                                     and s["frag"]["fid"] == x["fid"] for h in s["frag"].get("holders", [])]}
            direct_to = {a.get("to_agent") for a in asks if a.get("to_agent")}
            selected = {a for d in ingress if d.get("group") == grp for a in d.get("selected", [])}
            reached = (direct_to | selected | {m.get("to_agent") for m in inner}) & holders
            ev_prompts = [prompt_text(e) for e in llm if e["actor"] == f"boundary:{grp}"]
            in_evidence = any(present(f, p.split("Group records found:", 1)[-1] if "Group records found:" in p
                                      else p.split("Group records:", 1)[-1], names) for p in ev_prompts if "records" in p)
            resp_prompts = [prompt_text(e) for e in llm if e["payload"].get("agent") in reached
                            and e["payload"].get("component") == "responder"]
            win = max((window_state(f, p, names) for p in resp_prompts), key=["none", "summary", "verbatim"].index,
                      default="none")
            detail = {"fid": x["fid"], "state": x["state"], "holders": sorted(holders), "reached": sorted(reached),
                      "in_evidence": in_evidence, "holder_window": win}
            if x["state"] == "stale":
                verdict = "L_state"
            elif not asked_group:
                verdict = "L_req"
            elif ingress and in_evidence and not reached:
                verdict = "L_sel.assembly"
            elif not reached:
                verdict = "L_sel.search" if ingress and any(d.get("deliver") == "assemble" for d in ingress) else "L_route"
            elif win != "verbatim":
                verdict = "L_sel.window"
            elif any(d.get("deliver") == "assemble" for d in ingress):
                verdict = "L_sel.assembly"
            else:
                verdict = "L_sel.answer"
            break
        if verdict == "ok" and not answer_ok:
            verdict = "L_use"
        out.append({"need": row["need"], "group": grp, "gate": verdict, **detail})
    return out
