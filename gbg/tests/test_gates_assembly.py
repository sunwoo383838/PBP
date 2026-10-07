"""손실 고리 판정 (§3.4 인과 순서): request → reach → observe(window·search) → respond → select, 옛 버전은 표시(stale),
need는 조각 가운데 가장 이른 고리, 오답은 과제 단위 결과(use).
조립 조건(Ingress·sidecar)은 게이트웨이가 본 것만 잃을 수 있다: 증거·응답(항목/문장)·버전·과거 문답·초안에 있었으면 select."""
from gbg.scoring.gates import evidence_section, need_gates, reply_sections

FR = {"P1": {"fid": "P1", "key": "HR-SEL/profile/E-SEL-2004/grade", "group": "HR-SEL", "agent": "hr-sel.a3",
             "value": {"grade": 7}, "text": "E-SEL-2004 grade is now 7 (promoted day 3)."},
      "P2": {"fid": "P2", "key": "HR-SEL/profile/E-SEL-2004/dept", "group": "HR-SEL", "agent": "hr-sel.a1",
             "value": {"dept": 4417}, "text": "E-SEL-2004 cost centre moved to 4417."}}
NEED = {"sem": "HR-SEL/E-SEL-2004/profile", "group": "HR-SEL", "local": False, "critical_components": ["P1"],
        "sources": [{"type": "frag", "frag": {"fid": "P1", "holders": [{"agent": "hr-sel.a3"}]}},
                    {"type": "frag", "frag": {"fid": "P2", "holders": [{"agent": "hr-sel.a1"}]}}]}
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


def _events(stage="ingress", deliver="assemble", selected=("hr-sel.a3",), reached_prompt=WIN_VERBATIM, assemble_prompt="",
            question=Q, decision=True):
    es = [{"type": "task_delivered", "actor": "k", "payload": {"task_id": "W-1", "agent": "fin-sel.a1"}},
          {"type": "message", "actor": "fin-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "fin-sel.a1",
                                                              "to_group": "HR-SEL", "serving": None, "request": {"question": question}}}]
    if decision:
        es.append({"type": "boundary_decision", "actor": "boundary:HR-SEL",
                   "payload": {"task_id": "W-1", "stage": stage, "group": "HR-SEL", "question": Q, "deliver": deliver, "selected": list(selected)}})
    prompts = {}
    for a in selected:
        es.append({"type": "llm_call", "actor": f"agent:{a}", "payload": {"task_id": "W-1", "agent": a, "component": "responder", "key": f"k-{a}"}})
        prompts[f"k-{a}"] = [{"role": "user", "content": reached_prompt}]
    if assemble_prompt:
        es.append({"type": "llm_call", "actor": "boundary:HR-SEL", "payload": {"task_id": "W-1", "component": "boundary", "key": "k-asm"}})
        prompts["k-asm"] = [{"role": "user", "content": assemble_prompt}]
    return es, prompts


def _gate(rows=ROWS, **kw):
    es, prompts = _events(**kw)
    return need_gates(es, G, FR, rows, prompts, None, NAMES)[0]


def test_reply_sections_split_items_and_text():
    it, tx = reply_sections(_assemble_prompt("grade is 7 per our records", "E-SEL-2004 | grade | 7 | current | D1, day 3: D1"))
    assert it.startswith("- E-SEL-2004 | grade | 7") and "grade is 7 per our records" in tx and "- E-SEL" not in tx
    assert reply_sections("no replies here") == ("", "")
    assert evidence_section("x\n\nGroup records:\n[E1] a\n\nDatabase versions:\n[V1] b").endswith("[V1] b")


def test_select_when_gateway_saw_it_in_evidence_reply_items_text_versions_or_draft():
    frag = FR["P1"]["text"]
    assert _gate(assemble_prompt=_assemble_prompt(evidence=f"[E1] day 3, hr-sel.a3: {frag}"))["gate"] == "L_select"
    g = _gate(assemble_prompt=_assemble_prompt(reply_text=f"Yes, {frag}"))
    assert g["gate"] == "L_select" and g["in_reply_text"] and not g["in_reply_items"] and g["text_only"] and g["eta"] == 1
    g = _gate(assemble_prompt=_assemble_prompt(reply_item=f"E-SEL-2004 | grade | 7 | current | D1, day 3: {frag}"))
    assert g["gate"] == "L_select" and g["in_reply_items"] and g["matcher_suspect"] and not g["text_only"]
    assert _gate(assemble_prompt=_assemble_prompt(evidence="(none)\n\nEarlier exchanges of this desk:\n[S1] " + frag))["gate"] == "L_select"
    draft = "Your first additions, conflicts and proposals for this request (draft):\n- E-SEL-2004 | grade | 7 | current | E1, day 3: " + frag
    assert _gate(assemble_prompt=_assemble_prompt(draft=draft))["gate"] == "L_select"


def test_unseen_fragment_is_respond_window_or_search_in_that_order():
    unseen = _assemble_prompt(reply_text="I do not know.", evidence="[E1] unrelated record")
    g = _gate(assemble_prompt=unseen)
    assert g["gate"] == "L_respond" and g["reached"] == ["hr-sel.a3"] and g["holder_window"] == "verbatim" and not g["in_evidence"]
    assert _gate(assemble_prompt=unseen, reached_prompt=WIN_NONE)["gate"] == "L_observe.window"
    assert _gate(assemble_prompt=unseen, selected=("hr-sel.a1",))["gate"] == "L_observe.search"


def test_sidecar_retrieve_and_routing():
    frag = FR["P1"]["text"]
    g = _gate(stage="sidecar", assemble_prompt=_assemble_prompt(reply_text=frag))
    assert g["gate"] == "L_select" and g["text_only"]
    assert _gate(stage="sidecar", assemble_prompt=_assemble_prompt(reply_text="no"))["gate"] == "L_respond"
    seen = "Candidates\n\nGroup records found:\n[E1] day 3, hr-sel.a3: " + frag
    # Routing (η_φ=0): 닿음·원문·미전달 → respond; 보유자를 안 고르면 증거에 있었어도 reach
    g = _gate(deliver="forward", assemble_prompt="")
    assert g["gate"] == "L_respond" and "in_reply_items" not in g and g["eta"] == 0
    assert _gate(deliver="forward", selected=("hr-sel.a1",))["gate"] == "L_reach"
    assert _gate(deliver="forward", selected=("hr-sel.a1",), assemble_prompt=seen)["gate"] == "L_reach"
    # Retrieve (η_φ=1): 증거에 있었으면 select(전달 묶음에서 빠짐), 증거에도 없고 보유자도 안 고르면 observe.search
    assert _gate(deliver="read", selected=("hr-sel.a1",), assemble_prompt=seen)["gate"] == "L_select"
    assert _gate(deliver="read", selected=("hr-sel.a1",))["gate"] == "L_observe.search"


def test_stale_is_a_flag_and_the_earliest_link_wins():
    stale = [{"need": NEED["sem"], "delivered": False, "frags": [{"fid": "P1", "state": "stale"}]}]
    g = _gate(rows=stale, deliver="forward", selected=("hr-sel.a1",))                 # 비보유자가 DB 옛 값을 줌 → reach + stale
    assert g["gate"] == "L_reach" and g["stale"] and g["stale_any"]
    two = [{"need": NEED["sem"], "delivered": False, "frags": [{"fid": "P1", "state": "missing"}, {"fid": "P2", "state": "missing"}]}]
    g = _gate(rows=two, deliver="forward", selected=("hr-sel.a3",))                   # P1 respond, P2 reach → need는 reach
    assert g["gate"] == "L_reach" and g["fid"] == "P2" and [x["stage"] for x in g["frag_stages"]] == ["L_respond", "L_reach"]


def test_relay_colleague_counts_as_reach_and_dropped_relay_is_select():
    frag = FR["P1"]["text"]
    es, prompts = _events(decision=False, selected=())
    es.append({"type": "message", "actor": "fin-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "fin-sel.a1",
                                                                  "to_agent": "hr-sel.a1", "serving": None, "request": {"question": Q}}})
    es.append({"type": "message", "actor": "agent:hr-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "hr-sel.a1",
                                                                       "to_agent": "hr-sel.a3", "serving": "W-1/1", "request": {"question": Q}}})
    es.append({"type": "llm_call", "actor": "agent:hr-sel.a3", "payload": {"task_id": "W-1", "agent": "hr-sel.a3", "component": "responder", "key": "k-c"}})
    prompts["k-c"] = [{"role": "user", "content": WIN_VERBATIM}]
    g = need_gates(es, G, FR, ROWS, prompts, None, NAMES)[0]
    assert g["gate"] == "L_respond" and g["reached"] == ["hr-sel.a3"]                 # 동료에게 닿음, 동료가 답에 안 실음
    es.append({"type": "message", "actor": "agent:hr-sel.a3", "payload": {"task_id": "W-1", "kind": "response", "from_agent": "hr-sel.a1",
                                                                       "to_agent": "hr-sel.a3", "serving": "W-1/1",
                                                                       "response": {"answer": frag, "items": []}}})
    assert need_gates(es, G, FR, ROWS, prompts, None, NAMES)[0]["gate"] == "L_select"  # 동료는 답했는데 중계에서 빠짐


def test_delivered_need_is_ok_and_echo_is_recorded():
    rows = [{"need": NEED["sem"], "delivered": True, "frags": [{"fid": "P1", "state": "delivered"}]}]
    g = _gate(rows=rows, deliver="forward", question="Is Ok Dain's grade now 7 (promoted day 3)?")
    assert g["gate"] == "ok" and g["echo"] == ["P1"]
    assert _gate(rows=rows, deliver="forward")["echo"] == []


def test_task_outcome_use_only_when_every_need_is_met():
    from gbg.benchmarks.worldgen.scoring import load_private, strata, verify
    from gbg.scoring import ledger
    from gbg.tests.support import FIXTURES
    priv = load_private(FIXTURES / "worldgen_mini")
    ev = []
    for wid, g in priv.gold.items():
        te = priv.tasks[wid]
        ev += [{"type": "task_delivered", "actor": "kernel", "day": te.day, "round": te.round, "payload": {"task_id": wid, "agent": te.agent}},
               {"type": "answer", "actor": f"agent:{te.agent}", "day": te.day, "round": te.round,
                "payload": {"task_id": wid, "agent": te.agent, "answer": {k: "__x__" for k in g["gold"]}}}]
    led = ledger.build(ev, priv, verify, strata)
    for t in led["tasks"]:
        mine = [n for n in led["needs"] if n["task_id"] == t["task_id"]]
        met = all(n["gate"] in ("ok", "unjudged") for n in mine)
        assert t["outcome"] == ("use" if met else "lost")
        assert all(n["gate"] != "L_use" for n in mine)


def test_echo_only_counts_questions_before_the_groups_first_reply():
    rows = [{"need": NEED["sem"], "delivered": True, "frags": [{"fid": "P1", "state": "delivered"}]}]
    es, prompts = _events(deliver="forward")
    es.append({"type": "message", "actor": "boundary:HR-SEL", "payload": {"task_id": "W-1", "kind": "response", "from_agent": "fin-sel.a1",
                                                                       "to_group": "HR-SEL", "serving": None, "response": {"answer": "grade 7"}}})
    es.append({"type": "message", "actor": "fin-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "fin-sel.a1", "to_group": "HR-SEL",
                                                                  "serving": None, "request": {"question": "So Ok Dain's grade is now 7 (promoted day 3)?"}}})
    assert need_gates(es, G, FR, rows, prompts, None, NAMES)[0]["echo"] == []      # 첫 응답 뒤의 확인 질문은 되풀이가 아니다
