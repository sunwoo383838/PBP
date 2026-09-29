"""Routing 카나리 검사: 라우터가 만든 출력(선택 결과, referral 사유)에만 적용한다."""
from gbg.boundary.router_guard import canary_values, router_leaks

REQ = "How much can Sales Team 1 spend right now after deductions?"
HITS = ["CMT-00039 Sales Section 1 provisional approval 663,841 KRW confirmed, settlement expected day 9.",
        "Sales Team 1 capex 587227 earmarked until day 8 (no voucher yet).", "A-SEL-4334 workstation assigned."]


def test_canary_values_normalize_commas_and_skip_ids_and_small_numbers():
    assert canary_values(HITS) == {"663841", "587227"}
    assert canary_values(["day 9, grade 3, 1,000"]) == {"1000"}


def test_selection_and_referral_without_values_pass():
    assert router_leaks(["fin-sel.a1", "fin-sel.a3", "", "E3"], HITS, REQ) == []


def test_value_in_router_output_is_a_leak_unless_in_request():
    assert router_leaks(["FIN-TYO", "663,841"], HITS, REQ) == ["663841"]
    assert router_leaks(["FIN-TYO", "663,841"], HITS, REQ + " (item of 663,841 KRW)") == []
