"""need 단위 전달률: 결정 필수 조각이 최신 버전으로 요청자 쪽에 도착했는가 (카나리 기준)."""
from gbg.scoring.delivery import canaries, need_delivery

FR = {"F1": {"fid": "F1", "key": "FIN-SEL/commit/CMT-00055/status", "seq": 10, "disc": "H1", "group": "FIN-SEL",
             "value": {"status": "pending", "amount": 727113}, "text": "CMT-00055 approval 727,113 KRW confirmed (pending)"},
      "F0": {"fid": "F0", "key": "FIN-SEL/commit/CMT-00055/status", "seq": 5, "disc": "H1", "group": "FIN-SEL",
             "value": {"status": "reviewing", "amount": 727113}, "text": "CMT-00055 approval 727,113 KRW under review"},
      "E1": {"fid": "E1", "key": "FIN-SEL/line/Dev Team 2/earmark", "seq": 4, "group": "FIN-SEL",
             "value": {"dept": "Dev Team 2", "amount": 111111, "end": 1}, "text": "Dev Team 2 capex 111,111 KRW earmarked"},
      "E2": {"fid": "E2", "key": "FIN-SEL/line/Dev Team 2/earmark", "seq": 9, "group": "FIN-SEL",
             "value": {"dept": "Dev Team 2", "amount": 222222, "end": 5}, "text": "Dev Team 2 capex 222,222 KRW earmarked"},
      "F2": {"fid": "F2", "key": "HR-SEL/emp/E-SEL-2004/transfer", "seq": 11, "disc": "H0", "group": "HR-SEL",
             "value": {"to": "Dev Team 2", "effective": 7}, "text": "Transfer of Kim approved to Dev Team 2, effective day 7"},
      "F3": {"fid": "F3", "key": "HR-SEL/emp/E-SEL-2004/transfer", "seq": 3, "disc": "H0", "group": "HR-SEL",
             "value": {"to": "Sales Team 1", "effective": 4}, "text": "old transfer"}}
NAMES = {"E-SEL-2004": ["Kim Harin"]}
GOLD = {"W-1": {"state_class": "C", "c_ops": True, "needs": [
    {"sem": "FIN/x", "local": False, "critical_components": ["F1", "F2"]}]}}


def ev(task, answer, requester="a1"):
    return [{"type": "task_delivered", "payload": {"task_id": task, "agent": requester}},
            {"type": "message", "payload": {"task_id": task, "kind": "response", "from_agent": requester,
                                            "response": {"answer": answer}}}]


def test_canaries_skip_ids_round_numbers_and_small_values():
    assert canaries("CMT-00055 727,113 KRW day 7, 2,000,000 and 3171862") == {"727113", "3171862"}


def test_canary_and_signature_judgments():
    d = need_delivery(ev("W-1", "It is 727113 KRW, pending."), GOLD, FR, names=NAMES)
    frags = {x["fid"]: (x["method"], x["state"]) for x in d["needs"][0]["frags"]}
    assert frags == {"F1": ("canary", "delivered"), "F2": ("signature", "missing")} and not d["needs"][0]["delivered"]
    ok = ev("W-1", "727,113 KRW, status pending") + [{"type": "message", "payload": {"task_id": "W-1", "kind": "response", "from_agent": "a1",
                                     "response": {"answer": "Kim Harin moves to Dev Team 2 on day 7."}}}]
    d = need_delivery(ok, GOLD, FR, names=NAMES)
    assert all(x["state"] == "delivered" for x in d["needs"][0]["frags"]) and d["needs"][0]["delivered"]
    assert d["summary"]["all"]["coverage"] == {"canary": 0.5, "signature": 0.5}
    assert "domain_FIN" in d["summary"]


def test_signature_needs_entity_and_values_in_the_same_message():
    split = ev("W-1", "Kim Harin transfer approved.") + [{"type": "message", "payload": {"task_id": "W-1", "kind": "response",
                                     "from_agent": "a1", "response": {"answer": "Dev Team 2, day 7"}}}]
    d = need_delivery(split, GOLD, FR, names=NAMES)
    assert {x["fid"]: x["state"] for x in d["needs"][0]["frags"]}["F2"] == "missing", "엔티티와 값이 다른 메시지"
    stale = ev("W-1", "E-SEL-2004 goes to Sales Team 1 on day 4.")
    assert {x["fid"]: x["state"] for x in need_delivery(stale, GOLD, FR, names=NAMES)["needs"][0]["frags"]}["F2"] == "stale"


def test_stale_prior_and_other_agents():
    d = need_delivery(ev("W-1", "CMT-00055 is 727,113 KRW and under review."), GOLD, FR)
    assert d["needs"][0]["frags"][0]["state"] == "stale", "같은 금액의 옛 버전(상태)만 왔다"
    d = need_delivery(ev("W-1", "727,113 KRW"), GOLD, FR)
    assert d["needs"][0]["frags"][0]["state"] == "missing", "버전이 있으면 상태도 같은 메시지에 있어야 한다"
    g2 = {"W-1": {"state_class": "C", "c_ops": False, "needs": [{"sem": "FIN/y", "local": False, "critical_components": ["E2"]}]}}
    d = need_delivery(ev("W-1", "earmark of 111,111 KRW"), g2, FR)
    assert d["needs"][0]["frags"][0]["state"] == "missing", "같은 키의 다른 예치 건은 옛 버전이 아니다"
    d = need_delivery(ev("W-1", "unknown"), {"W-1": {"state_class": "C", "c_ops": False, "needs": [
        {"sem": "FIN/y", "local": False, "critical_components": ["E2"]}]}}, FR, prior={"W-1": "earlier note: 222,222"})
    assert d["needs"][0]["frags"][0]["state"] == "prior", "과제 전부터 요청자 이력에 있던 것은 따로 센다"
    d = need_delivery(ev("W-1", "727113 pending", requester="a2") + [{"type": "task_delivered", "payload": {"task_id": "W-1", "agent": "a1"}}], GOLD, FR)
    assert d["needs"][0]["frags"][0]["state"] == "missing", "다른 에이전트가 받은 것은 도착이 아니다"


def items_ev(task, items, answer="", requester="a1"):
    return [{"type": "task_delivered", "payload": {"task_id": task, "agent": requester}},
            {"type": "message", "payload": {"task_id": task, "kind": "response", "from_agent": requester,
                                            "response": {"answer": answer, "items": items, "missing": []}}}]


def _it(entity, attribute, value):
    return {"entity": entity, "attribute": attribute, "value": value, "status_or_as_of": "", "source": "db", "ref": ""}


# S1: 같은 엔티티의 항목은 합쳐서, 옛 버전과 다른 값만 요구, 답 문장도 한 메시지
PROF = {"P0": {"fid": "P0", "key": "HR-SEL/emp/E-SEL-2004/profile", "seq": 1, "group": "HR-SEL",
               "value": {"dept": "Dev Team 2", "grade": 1, "status": "active"}, "text": "old"},
        "P1": {"fid": "P1", "key": "HR-SEL/emp/E-SEL-2004/profile", "seq": 2, "group": "HR-SEL",
               "value": {"dept": "Dev Team 2", "grade": 2, "status": "active"}, "text": "changed to grade 2"}}
G_PROF = {"W-1": {"state_class": "B", "c_ops": False, "needs": [
    {"sem": "HR-SEL/E-SEL-2004/profile", "local": False, "critical_components": ["P1"]}]}}


def test_items_of_one_entity_are_merged_and_only_changed_fields_are_required():
    split = items_ev("W-1", [_it("E-SEL-2004", "department", "Dev Team 2"), _it("E-SEL-2004", "grade", "2")])
    assert need_delivery(split, G_PROF, PROF)["needs"][0]["delivered"], "항목이 나뉘어도 같은 엔티티면 한 메시지"
    only_grade = items_ev("W-1", [_it("E-SEL-2004", "grade", "2")])
    assert need_delivery(only_grade, G_PROF, PROF)["needs"][0]["delivered"], "옛 버전과 같은 필드(부서·상태)는 요구하지 않는다"
    old = items_ev("W-1", [_it("E-SEL-2004", "grade", "1")])
    assert need_delivery(old, G_PROF, PROF)["needs"][0]["frags"][0]["state"] == "stale"
    other = items_ev("W-1", [_it("E-SEL-2004", "department", "Sales"), _it("E-SEL-9999", "grade", "2")])
    assert not need_delivery(other, G_PROF, PROF)["needs"][0]["delivered"], "다른 엔티티의 값은 합치지 않는다"
    text = items_ev("W-1", [_it("E-SEL-2004", "department", "Dev Team 2")], answer="E-SEL-2004 is now grade 2.")
    assert need_delivery(text, G_PROF, PROF)["needs"][0]["delivered"], "답 문장도 읽는다"


# S2: 이름 (실행 중 catalog·조각 target)은 load_private가 names에 넣는다
def test_target_name():
    from gbg.benchmarks.worldgen.scoring import target_name
    assert target_name("HR record of Ok Dain") == "Ok Dain"
    assert target_name("In-house stock laptop (basic)") == "laptop (basic)"
    assert target_name("Sales Team 1 capex balance") == "Sales Team 1"
    assert target_name("CAD seats") == "CAD"
    assert target_name("CMT-00041 Support Section workstation provisional approval") is None


# S3: 계산형 need는 중간값이 엔티티와 같은 메시지에 오면 전달
def test_computed_need_is_delivered_by_its_intermediate_value():
    frags = {"E1": FR["E1"], "E2": FR["E2"]}
    g = {"W-1": {"state_class": "C", "c_ops": True, "needs": [
        {"sem": "FIN-SEL/Dev Team 2/budget_schedule", "local": False, "critical_components": ["E1", "E2"]}]}}
    comp = {"W-1": {"FIN-SEL/Dev Team 2/budget_schedule": [(["Dev Team 2"], [1234567])]}}
    msg = items_ev("W-1", [_it("Dev Team 2", "available budget", "1,234,567 KRW")])
    row = need_delivery(msg, g, frags, computed=comp)["needs"][0]
    assert row["delivered"] and row["computed"] and {x["state"] for x in row["frags"]} == {"missing"}
    wrong = items_ev("W-1", [_it("Dev Team 2", "available budget", "1,500,000 KRW")])
    row = need_delivery(wrong, g, frags, computed=comp)["needs"][0]
    assert not row["delivered"] and row["computed"] is False


# S4: 다른 일로 한 접촉은 보유자 도달이 아니다
def test_gate_counts_reach_only_for_questions_about_the_need():
    from gbg.scoring.gates import need_gates
    f = {**PROF["P1"], "agent": "hr-sel.a3"}
    frags = {"P0": PROF["P0"], "P1": f}
    need = {"sem": "HR-SEL/E-SEL-2004/profile", "group": "HR-SEL", "local": False, "critical_components": ["P1"],
            "sources": [{"type": "frag", "frag": {"fid": "P1", "holders": [{"agent": "hr-sel.a3"}]}}]}
    g = {"wid": "W-1", "needs": [need]}
    rows = [{"need": need["sem"], "delivered": False, "frags": [{"fid": "P1", "state": "missing"}]}]

    def run(question):
        es = [{"type": "task_delivered", "actor": "k", "payload": {"task_id": "W-1", "agent": "fin-sel.a1"}},
              {"type": "message", "actor": "fin-sel.a1", "payload": {"task_id": "W-1", "kind": "request", "from_agent": "fin-sel.a1",
                                                                  "to_agent": "hr-sel.a3", "serving": None,
                                                                  "request": {"question": question}}}]
        return need_gates(es, g, frags, rows, {}, False, {"E-SEL-2004": ["Ok Dain"]})[0]
    assert run("What is the grade of Ok Dain?")["reached"] == ["hr-sel.a3"]
    unrelated = run("How many people are in Dev Team 1?")
    assert unrelated["reached"] == [] and unrelated["gate"] == "L_route"


def test_matcher_does_not_take_numbers_from_names_other_items_or_regions():
    """이름 속 숫자('Dev Team 2')·다른 항목의 값·다른 지역 항목·도구 결과는 값 도착으로 세지 않는다."""
    old_grade = items_ev("W-1", [_it("E-SEL-2004", "department", "Dev Team 2"), _it("E-SEL-2004", "grade", "1")])
    dept = {"Dev Team 2": []}                                              # 부서명은 이름 목록(키 엔티티)에 있다
    assert need_delivery(old_grade, G_PROF, PROF, names=dept)["needs"][0]["frags"][0]["state"] == "stale", "'Dev Team 2'의 2는 등급이 아니다"
    text = items_ev("W-1", [], answer="Reply 2 ok: E-SEL-2004 is in Dev Team 2 with grade 1.")
    assert need_delivery(text, G_PROF, PROF, names=dept)["needs"][0]["frags"][0]["state"] == "stale", "엔티티 앞의 숫자는 보지 않는다"
    g = {"W-1": {"state_class": "B", "c_ops": False, "needs": [
        {"sem": "IT-TYO/inventory/workstation", "group": "IT-TYO", "local": False, "critical_components": ["P1"]}]}}
    comp = {"W-1": {"IT-TYO/inventory/workstation": [(["INV-TYO-WSP"], [0])]}}
    nxt = items_ev("W-1", [], answer="INV-TYO-WSP 1 unit left, INV-TYO-WSS 0 units.")
    assert need_delivery(nxt, g, PROF, computed=comp)["needs"][0]["computed"] is False, "다음 id의 값"
    fr = {**PROF, "X": {"fid": "X", "key": "IT-SEL/lic/CAD/seats", "group": "IT-SEL", "value": {"seats": 3}, "text": ""}}
    comp = {"W-1": {"IT-TYO/inventory/workstation": [(["CAD"], [0])]}}
    other = items_ev("W-1", [_it("CAD seats SEL region", "available", "0")])
    assert need_delivery(other, g, fr, computed=comp)["needs"][0]["computed"] is False, "다른 지역 항목"
    same = items_ev("W-1", [_it("CAD seats", "available", "0")])
    assert need_delivery(same, g, fr, computed=comp)["needs"][0]["computed"] is True
    tool = [{"type": "task_delivered", "payload": {"task_id": "W-1", "agent": "a1"}},
            {"type": "tool_result", "payload": {"task_id": "W-1", "agent": "a1", "serving": None, "tool": "db.query",
                                                "result": {"entity": "CAD", "seats": 0}}}]
    assert need_delivery(tool, g, fr, computed=comp)["needs"][0]["computed"] is False, "계산값은 응답에서만"


def test_redirect_metrics_target_follow_delivery_and_day_unknown():
    from gbg.scoring.redirects import redirect_metrics, summarize
    g = {"wid": "W-1", "needs": [{"sem": "HR-SEL/E-SEL-2004/profile", "group": "HR-SEL", "local": False,
                                  "critical_components": ["P1"]}]}
    ev = [{"type": "boundary_decision", "actor": "boundary:IT-SEL", "payload": {
              "task_id": "W-1", "stage": "ingress", "redirects": [{"entity": "E-SEL-2004", "attribute": "grade",
                                                                   "referral_to": "HR-SEL", "reason": "out_of_scope"}],
              "redirects_rejected": [{"why": "evidence"}]}},
          {"type": "message", "actor": "agent:a1", "payload": {"task_id": "W-1", "kind": "request", "to_group": "HR-SEL"}},
          {"type": "message", "actor": "boundary:HR-SEL", "payload": {"task_id": "W-1", "kind": "response", "response": {
              "items": [{"day": "3"}, {"day": "unknown"}]}}}]
    m = redirect_metrics(ev, g, PROF, {}, [{"task_id": "W-1", "need": "HR-SEL/E-SEL-2004/profile", "delivered": True}])
    assert (m["guided"], m["target_correct"], m["followed"], m["delivered_after"], m["rejected"]) == (1, 1, 1, 1, {"evidence": 1})
    s = summarize([m])
    assert s["target_accuracy"] == 1.0 and s["day_unknown_rate"] == 0.5
