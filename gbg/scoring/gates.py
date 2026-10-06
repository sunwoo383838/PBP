"""need별 처음 끊긴 게이트 (채점기, 오프라인. v0 휴리스틱).

need마다 결정 필수 조각을 차례로 보며, 전달되지 않은 첫 조각이 어디서 끊겼는지 정한다.

    ok           모두 전달되고 답도 맞음
    L_use        모두 전달됐는데 답이 틀림 (추론·사용 실패)
    L_state      옛 버전만 전달됨
    L_req        요청자가 그 need의 그룹에 묻지 않음 (full_load는 조직 기억 검색을 한 번도 하지 않음)
    L_route      그룹에는 물었지만 보유자에게 닿지 않음 (Direct: 다른 에이전트에게 물음 / 경계: 보유자를 고르지 않음,
                 Ingress는 증거에도 없음)
    L_sel.window 보유자에게 물었지만 보유자의 컨텍스트 창에 그 조각이 없음 (창 밖으로 밀려남)
    L_sel.answer 보유자 창에는 있었는데 답에 싣지 않음
    L_sel.search Ingress: 보유자도 고르지 않았고 증거 블록에도 없음 (검색 실패)
    L_sel.assembly Ingress: 증거 블록 또는 응답에 있었는데 조립 답에 빠짐

조립 조건(deliver=assemble: Ingress·sidecar)의 선택 관문은 "게이트웨이는 본 것만 잃을 수 있다"로 가른다. 조립 LLM의 입력
(증거 [E#]·DB 버전 [V#]·과거 문답 [S#]·재질의 뒤 2차 조립의 초안, 그리고 응답 [R#]의 항목 줄과 문장 줄)에 조각이 있었으면
assembly. 없었으면 닿음·원문 → answer, 닿음·창에 없음 → window, 못 닿음 → search. gate_detail에 in_evidence와
in_reply_items(응답의 항목 줄)·in_reply_text(응답의 문장 줄)를 따로 적는다. 항목 줄에 있었는데 미전달이면 코드가 항목을
그대로 넘기므로 전달 매처 오판이 의심된다(matcher_suspect). 문장 줄에만 있다가 빠진 것(text_only)은 Ingress가 담당자
설명 글을 조립 답에 그대로 싣지 않는 데서 온다(sidecar는 그대로 둠).
조립이 아닌 조건(Direct·Routing·retrieve·direct_relay·full_load)의 규칙은 바꾸지 않았다.

"창"과 "증거"는 LLM 호출의 입력(캐시에 저장된 요청)에서 확인한다. 조각의 존재는 delivery.py와 같은 카나리/서명 기준.
"보유자에 닿음"은 그 need에 관한 질문(need·조각의 엔티티 id나 이름이 질문에 있음)으로 닿은 경우만 센다. 다른 일로
물은 접촉은 닿은 것이 아니다. 계산형 need가 중간값으로 전달됐으면(delivery의 computed) 조각 판정 없이 ok/L_use.
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


_ATTRS = {"profile", "budget_schedule", "next_reset", "approval", "license", "inventory", "stock", "assets", "status",
          "result", "effective_status", "assignment_timeline", "eligibility", "seat_transfer_share", "seat_purchase_line",
          "seat_price", "invoice_match_precedence", "planning_headcount", "planning_headcount-regular"}


def need_surfaces(need: dict, fragments: dict, names: dict) -> list[str]:
    """need에 관한 질문인지 가르는 표면형: sem의 엔티티 부분, 결정 필수 조각의 키 엔티티, 그 이름·별칭."""
    ents = [x for x in need["sem"].split("/")[1:] if x not in _ATTRS]
    for fid in need.get("critical_components") or []:
        parts = (fragments.get(fid, {}).get("key") or "").split("/")
        if len(parts) > 2:
            ents.append(parts[2])
    out = []
    for e in dict.fromkeys(ents):
        out += [e, *names.get(e, [])]
    return [x for x in dict.fromkeys(_norm(x) for x in out) if len(x) > 1]


def about(question: str | None, surfaces: list[str]) -> bool:
    q = _norm(question or "")
    return any(re.search(rf"(?<!\w){re.escape(x)}(?!\w)", q) for x in surfaces)


def _group_of(agent: str) -> str:
    return agent.split(".")[0].upper() if agent and not agent.startswith("boundary:") else ""


def reply_sections(prompt: str) -> tuple[str, str]:
    """조립 프롬프트의 Replies 부분을 항목 줄(render_items의 '- ' 줄)과 문장 줄로 나눈다. 1차·2차(재질의 뒤) 조립 모두 같은 형식.
    조립 프롬프트가 아니면 빈 문자열 둘."""
    if "Replies:\n" not in prompt:
        return "", ""
    sec = prompt.split("Replies:\n", 1)[1].split("\n\nGroup records:", 1)[0]
    lines = sec.splitlines()
    return "\n".join(x for x in lines if x.startswith("- ")), "\n".join(x for x in lines if not x.startswith("- "))


def evidence_section(prompt: str) -> str:
    """경계 LLM 입력에서 그룹 기록 부분. 선택 프롬프트는 'Group records found:' 이후, 조립 프롬프트는 'Group records:' 이후
    (DB 버전 [V#]·과거 문답 [S#]·2차 조립의 초안까지 포함: 모두 게이트웨이가 본 것)."""
    if "Group records found:" in prompt:
        return prompt.split("Group records found:", 1)[-1]
    if "Group records:" in prompt:
        return prompt.split("Group records:", 1)[-1]
    return ""


def _question(msg: dict) -> str:
    r = msg.get("request") or {}
    return msg.get("question") or r.get("question") or ""


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
    ingress = [d for d in decisions if d.get("stage") in ("ingress", "sidecar")]     # sidecar: 에이전트에 붙은 같은 모듈
    assemble = any(d.get("deliver") == "assemble" for d in ingress)
    egress_targets = {t["group"] for d in decisions if d.get("stage") == "egress" for t in d.get("targets", [])}
    inner = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["actor"].startswith("boundary:")]
    llm = [e for e in mine if e["type"] == "llm_call"]
    searched = any(e["type"] == "tool_call" and e["payload"].get("tool") == "search_memory"      # full_load: 조직 기억 검색
                   and e["payload"].get("agent") == req for e in mine)

    def prompt_text(e) -> str:
        msgs = prompts.get(e["payload"].get("key")) or []
        return "\n".join(m.get("content") or "" for m in msgs)

    out = []
    for row in delivery_rows:
        need = next(n for n in g["needs"] if n["sem"] == row["need"])
        grp = need["group"]
        surf = need_surfaces(need, fragments, names)
        asked_group = any((a.get("to_group") == grp) or _group_of(a.get("to_agent") or "") == grp for a in asks) \
            or grp in egress_targets or searched
        verdict, detail = "ok", {}
        for x in ([] if row.get("delivered") else row["frags"]):             # 계산형 need는 중간값 전달로 충분
            if x["state"] == "delivered":
                continue
            f = fragments[x["fid"]]
            holders = {f["agent"], *[h["agent"] for s in need["sources"] if s["type"] == "frag"
                                     and s["frag"]["fid"] == x["fid"] for h in s["frag"].get("holders", [])]}
            # need에 관한 질문으로 닿은 경우만 (다른 일로 한 접촉은 도달이 아니다)
            direct_to = {a.get("to_agent") for a in asks if a.get("to_agent") and about(_question(a), surf)}
            selected = {a for d in ingress if d.get("group") == grp and about(d.get("question"), surf)
                        for a in d.get("selected", [])}
            reached = (direct_to | selected | {m.get("to_agent") for m in inner if about(_question(m), surf)}) & holders
            ev_prompts = [prompt_text(e) for e in llm if e["actor"] == f"boundary:{grp}"]
            in_evidence = any(present(f, evidence_section(p), names) for p in ev_prompts if "records" in p)
            resp_prompts = [prompt_text(e) for e in llm if e["payload"].get("agent") in reached
                            and e["payload"].get("component") == "responder"]
            win = max((window_state(f, p, names) for p in resp_prompts), key=["none", "summary", "verbatim"].index,
                      default="none")
            detail = {"fid": x["fid"], "state": x["state"], "holders": sorted(holders), "reached": sorted(reached),
                      "in_evidence": in_evidence, "holder_window": win}
            if assemble:                                                    # 조립 입력의 응답 [R#]: 항목 줄 / 문장 줄
                secs = [reply_sections(p) for p in ev_prompts]
                in_items = any(it and present(f, it, names) for it, _ in secs)
                in_text = any(tx and present(f, tx, names) for _, tx in secs)
                detail.update(in_reply_items=in_items, in_reply_text=in_text,
                              matcher_suspect=in_items,                     # 항목은 그대로 전달되므로 미전달이면 매처 의심
                              text_only=in_text and not in_items and not in_evidence)
            if x["state"] == "stale":
                verdict = "L_state"
            elif not asked_group:
                verdict = "L_req"
            elif assemble:                                                  # 게이트웨이는 본 것만 잃을 수 있다
                if in_evidence or in_items or in_text:
                    verdict = "L_sel.assembly"
                elif reached and win == "verbatim":
                    verdict = "L_sel.answer"
                elif reached:
                    verdict = "L_sel.window"
                else:
                    verdict = "L_sel.search"
            elif searched and not reached:                                  # full_load: 검색했는데 조각이 오지 않음
                verdict = "L_sel.search"
            elif ingress and in_evidence and not reached:                   # 선택 증거에는 있었는데 보유자를 안 고름
                # Routing(forward): 조립이 없으므로 σ가 본 것을 σ가 잃은 중개 손실 = route. retrieve(read): 증거 원문이 요청자에게
                # 가므로 중개가 아니라 전달 형식(상한 탈락·매처)의 문제 = 선택 관문에 둠(보고는 route/select/use 3갈래)
                verdict = "L_route" if any(d.get("deliver") == "forward" for d in ingress) else "L_sel.assembly"
            elif not reached:
                verdict = "L_route"
            elif win != "verbatim":
                verdict = "L_sel.window"
            else:
                verdict = "L_sel.answer"
            break
        if verdict == "ok" and not answer_ok:
            verdict = "L_use"
        out.append({"need": row["need"], "group": grp, "gate": verdict, **detail})
    return out
