"""need별 손실 고리 (채점기, 오프라인. 휴리스틱). §3.4의 인과 순서를 따른다.

전달되지 않은 결정 필수 조각마다 처음 끊긴 고리를 정하고, need는 그 조각들 가운데 가장 이른 고리를 갖는다.

    L_request         요청자가 그 need의 그룹에 묻지 않음 (full_load는 조직 기억 검색을 한 번도 하지 않음)
    L_reach           선택 경로의 기록 범위 Ω에 조각이 없음: 그 need에 관해 닿은 구성원(요청자가 고른 응답자·게이트웨이가
                      고른 구성원·relay로 응답자가 다시 물은 동료) 가운데 조각의 이력 보유자가 없고, 그룹 기록을 정보 선택에
                      넘기는 경로(η_φ=1)도 없음. Routing에서 "선택 증거에는 있었는데 보유자를 고르지 않음"도 여기(η_φ=0)
    L_observe.window  닿은 이력 보유자의 작업 맥락(원문 창)에 조각이 없음
    L_observe.search  η_φ=1 경로(Ingress·Sidecar·Retrieve)에서 보유자에게 닿지 않았고 검색 증거에도 없음. full_load의 검색 누락
    L_respond         닿은 보유자의 원문 창에 있었는데 지역 응답에 싣지 않음
    L_select          정보 선택의 입력에 있었는데 최종 메시지에 없음: 조립 입력(증거 [E#]·DB 버전 [V#]·과거 문답 [S#]·2차 조립
                      초안·응답 [R#]의 항목 줄과 문장 줄), Retrieve의 검색 증거(전달 묶음에서 상한 탈락 등), relay에서 동료가
                      답한 것을 중계한 응답자가 뺀 경우

옛 버전만 전달된 조각은 고리가 아니라 표시(stale)다: 위 순서대로 끊긴 고리를 정하고 stale=True를 붙인다(옛 값 전달은 증상).
need가 전달됐으면(모든 조각 delivered, 또는 계산형 중간값 전달) ok. 답이 틀렸는지는 need가 아니라 과제 단위 결과로
본다(ledger.py: outcome use = 모든 원격 need가 ok인데 오답). 전달된 조각 가운데 그 값이 그 그룹의 첫 응답 전에 요청자가 보낸 질문에
이미 있던 것은 echo로 적는다(응답자가 질문을 되풀이했을 수 있음; 판정은 바꾸지 않음).

gate_detail: 고른 조각의 fid·state·stale·holders·reached·in_evidence·holder_window(조립 조건은 in_reply_items·in_reply_text·
matcher_suspect·text_only), 조각별 고리 frag_stages, echo, eta(η_φ). "창"과 "증거"는 LLM 호출의 입력(캐시된 요청)에서
확인하고, 조각의 존재는 delivery.py와 같은 카나리/서명 기준. "닿음"은 그 need에 관한 질문(need·조각의 엔티티 id나 이름이
질문에 있음)으로 닿은 경우만 센다.
"""
import json
import re

from gbg.contracts.envelope import render_response

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


RANK = {"L_request": 0, "L_reach": 1, "L_observe.window": 2, "L_observe.search": 2, "L_respond": 3, "L_select": 4}


def need_gates(events: list[dict], g: dict, fragments: dict, delivery_rows: list[dict], prompts: dict,
               answer_ok: bool | None = None, names: dict | None = None) -> list[dict]:
    """과제 하나의 need별 손실 고리. prompts: llm_call key → 요청 messages (캐시). answer_ok는 쓰지 않는다(과제 단위 use는 ledger)."""
    names = names or {}
    wid = g["wid"]
    req = next((e["payload"]["agent"] for e in events if e["type"] == "task_delivered"), None)
    mine = [e for e in events if e["payload"].get("task_id") == wid]
    asks = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
            and e["payload"].get("from_agent") == req and e["payload"].get("serving") is None]
    decisions = [e["payload"] for e in mine if e["type"] == "boundary_decision"]
    ingress = [d for d in decisions if d.get("stage") in ("ingress", "sidecar")]     # sidecar: 에이전트에 붙은 같은 모듈
    egress_targets = {t["group"] for d in decisions if d.get("stage") == "egress" for t in d.get("targets", [])}
    inner = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"
             and e["actor"].startswith("boundary:")]
    relay_asks = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "request"   # relay: 응답자 → 동료
                  and e["payload"].get("serving") is not None and e["actor"].startswith("agent:")]
    relay_replies = [e["payload"] for e in mine if e["type"] == "message" and e["payload"]["kind"] == "response"
                     and e["payload"].get("serving") is not None and e["actor"].startswith("agent:")]
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
        modes = {d.get("deliver") for d in ingress if d.get("group") == grp} or {d.get("deliver") for d in ingress}
        mode = "assemble" if "assemble" in modes else "read" if "read" in modes else "forward" if "forward" in modes else None
        eta = int(mode in ("assemble", "read") or searched)                # η_φ: 그룹 기록이 정보 선택에 넘어가는가
        # 질문 되풀이(echo): 그 그룹의 첫 응답이 오기 전에 요청자가 그 그룹에 보낸 질문에 이미 값이 있던 조각
        first = next((i for i, e in enumerate(mine) if e["type"] == "message" and e["payload"].get("kind") == "response"
                      and e["payload"].get("from_agent") == req and e["payload"].get("serving") is None
                      and (e["actor"] == f"boundary:{grp}" or _group_of(e["actor"].split(":")[-1]) == grp)), len(mine))
        questions = "\n".join(_question(e["payload"]) for e in mine[:first] if e["type"] == "message" and e["payload"].get("kind") == "request"
                              and e["payload"].get("from_agent") == req and e["payload"].get("serving") is None
                              and (e["payload"].get("to_group") == grp or _group_of(e["payload"].get("to_agent") or "") == grp))
        echo = [x["fid"] for x in row["frags"] if x["state"] == "delivered" and questions
                and present(fragments[x["fid"]], questions, names)]
        if row.get("delivered"):                                            # 계산형 need는 중간값 전달로 충분
            out.append({"need": row["need"], "group": grp, "gate": "ok", "echo": echo, "eta": eta})
            continue
        cand = []
        for x in row["frags"]:
            if x["state"] == "delivered":
                continue
            f = fragments[x["fid"]]
            holders = {f["agent"], *[h["agent"] for s in need["sources"] if s["type"] == "frag"
                                     and s["frag"]["fid"] == x["fid"] for h in s["frag"].get("holders", [])]}
            # need에 관한 질문으로 닿은 경우만 (다른 일로 한 접촉은 도달이 아니다)
            direct_to = {a.get("to_agent") for a in asks if a.get("to_agent") and about(_question(a), surf)}
            selected = {a for d in ingress if d.get("group") == grp and about(d.get("question"), surf)
                        for a in d.get("selected", [])}
            colleagues = {m.get("to_agent") for m in relay_asks if _group_of(m.get("to_agent") or "") == grp
                          and about(_question(m), surf)}
            reached = (direct_to | selected | colleagues | {m.get("to_agent") for m in inner if about(_question(m), surf)}) & holders
            ev_prompts = [prompt_text(e) for e in llm if e["actor"] == f"boundary:{grp}"]
            in_evidence = any(present(f, evidence_section(p), names) for p in ev_prompts if "records" in p)
            resp_prompts = [prompt_text(e) for e in llm if e["payload"].get("agent") in reached
                            and e["payload"].get("component") == "responder"]
            win = max((window_state(f, p, names) for p in resp_prompts), key=["none", "summary", "verbatim"].index,
                      default="none")
            detail = {"fid": x["fid"], "state": x["state"], "stale": x["state"] == "stale", "holders": sorted(holders),
                      "reached": sorted(reached), "in_evidence": in_evidence, "holder_window": win}
            in_items = in_text = relay_seen = False
            if mode == "assemble":                                          # 조립 입력의 응답 [R#]: 항목 줄 / 문장 줄
                secs = [reply_sections(p) for p in ev_prompts]
                in_items = any(it and present(f, it, names) for it, _ in secs)
                in_text = any(tx and present(f, tx, names) for _, tx in secs)
                detail.update(in_reply_items=in_items, in_reply_text=in_text,
                              matcher_suspect=in_items,                     # 항목은 그대로 전달되므로 미전달이면 매처 의심
                              text_only=in_text and not in_items and not in_evidence)
            if colleagues:                                                  # relay: 동료가 답한 것을 응답자가 중계에서 뺐는가
                relay_seen = any(present(f, render_response(m.get("response") or {}), names) for m in relay_replies
                                 if _group_of(m.get("to_agent") or "") == grp)
                detail["relay_seen"] = relay_seen
            if not asked_group:
                st = "L_request"
            elif searched and not ingress:                                  # full_load: 단일 에이전트의 조직 기억 검색
                st = "L_observe.search"
            elif mode in ("assemble", "read"):                              # η_φ=1: 그룹 기록 전체가 Ω — 도달 손실 없음
                if in_evidence or in_items or in_text:
                    st = "L_select"                                         # 게이트웨이(또는 전달 묶음)는 본 것만 잃는다
                elif reached and win == "verbatim":
                    st = "L_respond"
                elif reached:
                    st = "L_observe.window"
                else:
                    st = "L_observe.search"
            elif not reached:                                               # η_φ=0 (Direct·relay·Routing)
                st = "L_reach"                                              # Routing: 선택 증거에 있어도 보유자를 안 고르면 여기
            elif relay_seen:
                st = "L_select"
            elif win != "verbatim":
                st = "L_observe.window"
            else:
                st = "L_respond"
            cand.append((RANK[st], len(cand), st, detail))
        if not cand:                                                        # 미전달인데 판정할 조각이 없음 (방어)
            out.append({"need": row["need"], "group": grp, "gate": "ok", "echo": echo, "eta": eta})
            continue
        _, _, st, detail = min(cand)
        out.append({"need": row["need"], "group": grp, "gate": st, **detail, "eta": eta, "echo": echo,
                    "stale_any": any(d["stale"] for *_, d in cand),
                    "frag_stages": [{"fid": d["fid"], "stage": s_, "stale": d["stale"]} for _, _, s_, d in cand]})
    return out
