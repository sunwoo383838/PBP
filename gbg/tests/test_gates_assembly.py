"""조립 조건(Ingress·sidecar)의 선택 관문 귀속: 게이트웨이는 본 것만 잃을 수 있다.
증거·응답(항목/문장)·버전·과거 문답·초안에 있었으면 assembly, 없었으면 닿음·원문 → answer, 닿음·창에 없음 → window, 못 닿음 → search.
조립이 아닌 조건(Routing)의 규칙은 그대로."""
from gbg.scoring.gates import evidence_section, need_gates, reply_sections

FR = {"P1": {"fid": "P1", "key": "HR-SEL/profile/E-SEL-2004/grade", "group": "HR-SEL", "agent": "hr-sel.a3",
             "value": {"grade": 7}, "text": "E-SEL-2004 grade is now 7 (promoted day 3)."}}
NEED = {"sem": "HR-SEL/E-SEL-2004/profile", "group": "HR-SEL", "local": False, "critical_components": ["P1"],
        "sources": [{"type": "frag", "frag": {"fid": "P1", "holders": [{"agent": "hr-sel.a3"}]}}]}
G = {"wid": "W-1", "needs": [NEED]}
ROWS = [{"need": NEED["sem"], "delivered": False, "frags": [{"fid": "P1", "state": "missing"}]}]
NAMES = {"E-SEL-2004": ["Ok Dain"]}
Q = "What is the grade of Ok Dain?"
WIN_VERBATIM = "[Recent records, verbatim]\nday 3: E-SEL-2004 grade is now 7 (promoted day 3).\n[Current task]\n" + Q
WIN_NONE = "[Recent records, verbatim]\nnothing here\n[Current task]\n" + Q


def _assemble_prompt(reply_text="", reply_item="", evidence="(none)", draft=""):
    parts = [f"Today is day 4.\nRequest from FIN-SEL:\n{Q}",
             "Replies:\n[R1] (ok) " + reply_text + (("\n- " + reply_item) if reply_item else ""),
             "Group records:\n" + evidence]
    return "\n\n".join(parts) + (("\n\n" + draft) if draft else "")


def _events(stage="ingress", deliver="assemble", selected=("hr-sel.a3",), reached_prompt=WIN_VERBATIM, assemble_prompt=""):
    es = [{"type": "task_delivered", "actor": "k", "payload": {"task_id": "W-1", "agent": "fin-sel.a1"}},
          {"type": "message", "actor": "fin-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "fin-sel.a1",
                                                              "to_group": "HR-SEL", "serving": None, "request": {"question": Q}}},
          {"type": "boundary_decision", "actor": "boundary:HR-SEL",
           "payload": {"task_id": "W-1", "stage": stage, "group": "HR-SEL", "question": Q, "deliver": deliver, "selected": list(selected)}}]
    prompts = {}
    for a in selected:
        es.append({"type": "llm_call", "actor": f"agent:{a}", "payload": {"task_id": "W-1", "agent": a, "component": "responder", "key": f"k-{a}"}})
        prompts[f"k-{a}"] = [{"role": "user", "content": reached_prompt}]
    if assemble_prompt:
        es.append({"type": "llm_call", "actor": "boundary:HR-SEL", "payload": {"task_id": "W-1", "component": "boundary", "key": "k-asm"}})
        prompts["k-asm"] = [{"role": "user", "content": assemble_prompt}]
    return es, prompts


def _gate(**kw):
    es, prompts = _events(**kw)
    return need_gates(es, G, FR, ROWS, prompts, False, NAMES)[0]


def test_reply_sections_split_items_and_text():
    it, tx = reply_sections(_assemble_prompt("grade is 7 per our records", "E-SEL-2004 | grade | 7 | current | D1, day 3: D1"))
    assert it.startswith("- E-SEL-2004 | grade | 7") and "grade is 7 per our records" in tx and "- E-SEL" not in tx
    assert reply_sections("no replies here") == ("", "")
    assert evidence_section("x\n\nGroup records:\n[E1] a\n\nDatabase versions:\n[V1] b").endswith("[V1] b")


def test_assembly_when_gateway_saw_it_in_evidence_reply_items_text_versions_or_draft():
    frag = FR["P1"]["text"]
    assert _gate(assemble_prompt=_assemble_prompt(evidence=f"[E1] day 3, hr-sel.a3: {frag}"))["gate"] == "L_sel.assembly"
    g = _gate(assemble_prompt=_assemble_prompt(reply_text=f"Yes, {frag}"))
    assert g["gate"] == "L_sel.assembly" and g["in_reply_text"] and not g["in_reply_items"] and g["text_only"]
    g = _gate(assemble_prompt=_assemble_prompt(reply_item=f"E-SEL-2004 | grade | 7 | current | D1, day 3: {frag}"))
    assert g["gate"] == "L_sel.assembly" and g["in_reply_items"] and g["matcher_suspect"] and not g["text_only"]
    assert _gate(assemble_prompt=_assemble_prompt(evidence="(none)\n\nEarlier exchanges of this desk:\n[S1] " + frag))["gate"] == "L_sel.assembly"
    draft = "Your first additions, conflicts and proposals for this request (draft):\n- E-SEL-2004 | grade | 7 | current | E1, day 3: " + frag
    assert _gate(assemble_prompt=_assemble_prompt(draft=draft))["gate"] == "L_sel.assembly"


def test_unseen_fragment_is_answer_window_or_search_in_that_order():
    unseen = _assemble_prompt(reply_text="I do not know.", evidence="[E1] unrelated record")
    g = _gate(assemble_prompt=unseen)
    assert g["gate"] == "L_sel.answer" and g["reached"] == ["hr-sel.a3"] and g["holder_window"] == "verbatim" and not g["in_evidence"]
    assert _gate(assemble_prompt=unseen, reached_prompt=WIN_NONE)["gate"] == "L_sel.window"
    assert _gate(assemble_prompt=unseen, selected=("hr-sel.a1",))["gate"] == "L_sel.search"


def test_sidecar_stage_uses_the_same_rule_and_routing_is_unchanged():
    frag = FR["P1"]["text"]
    g = _gate(stage="sidecar", assemble_prompt=_assemble_prompt(reply_text=frag))
    assert g["gate"] == "L_sel.assembly" and g["text_only"]
    assert _gate(stage="sidecar", assemble_prompt=_assemble_prompt(reply_text="no"))["gate"] == "L_sel.answer"
    g = _gate(deliver="forward", assemble_prompt="")                       # Routing: 닿음·원문·미전달 → answer (규칙 불변)
    assert g["gate"] == "L_sel.answer" and "in_reply_items" not in g
    assert _gate(deliver="forward", selected=("hr-sel.a1",))["gate"] == "L_route"
    # 선택 증거에는 있었는데 보유자를 안 고름: Routing은 중개 손실(route), retrieve는 증거 원문이 요청자에게 가므로 선택 관문
    seen = "Candidates\n\nGroup records found:\n[E1] day 3, hr-sel.a3: " + frag
    assert _gate(deliver="forward", selected=("hr-sel.a1",), assemble_prompt=seen)["gate"] == "L_route"
    assert _gate(deliver="read", selected=("hr-sel.a1",), assemble_prompt=seen)["gate"] == "L_sel.assembly"
