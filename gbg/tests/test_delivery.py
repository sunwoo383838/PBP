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
