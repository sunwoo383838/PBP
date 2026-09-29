"""Routing은 검색 결과를 담당자 선택에만 쓴다: 요청 원문 전달, 응답 원문 반환, 검색 결과의 카나리 값 비노출."""
from gbg.boundary.router_guard import canary_values, check_router_output

REQ = "How much can Sales Team 1 spend right now after deductions?"
HITS = ["CMT-00039 Sales Section 1 provisional approval 663,841 KRW confirmed, settlement expected day 9.",
        "Sales Team 1 capex 587227 earmarked until day 8 (no voucher yet).", "A-SEL-4334 workstation assigned."]


def test_canary_values_normalize_commas_and_skip_small_numbers():
    assert canary_values(HITS) == {"00039", "663841", "587227", "4334"}
    assert canary_values(["day 9, grade 3, 1,000"]) == {"1000"}


def test_verbatim_routing_passes():
    resp = ["Available is 2,508,100 KRW with 1 deduction."]
    c = check_router_output(REQ, {"fin-sel.a1": REQ, "fin-sel.a3": REQ}, resp, resp, HITS)
    assert c.ok


def test_modified_forward_or_return_is_flagged():
    resp = ["ok"]
    c = check_router_output(REQ, {"fin-sel.a1": REQ + " (see CMT-00039)"}, ["summary: ok"], resp, HITS)
    kinds = {v["kind"] for v in c.violations}
    assert kinds == {"forward_modified", "return_modified", "search_value_leak"}


def test_search_value_in_output_is_leak_unless_request_or_responder_said_it():
    c = check_router_output(REQ, {"a": REQ}, ["663,841"], ["663,841"], HITS)
    assert c.ok, "담당자가 직접 답한 값은 라우터 누출이 아니다"
    c = check_router_output(REQ, {"a": REQ}, ["ok"], ["ok"], HITS, revealed="ask fin-sel.a3 about 587,227")
    assert [v for v in c.violations if v["kind"] == "search_value_leak"][0]["values"] == ["587227"]
