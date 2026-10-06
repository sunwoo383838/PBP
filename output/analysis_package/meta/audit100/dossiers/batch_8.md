## CASE 92: deepseek-v4-flash · full_load · s12 · W-00088 · class C · day 9 · template capacity
### Task as given to the requester
How many in-house workstation (standard) units and IDE Pro seats are actually available right now?
[Request scope] item=workstation; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only; seat lookup regions=the requesting region and the first other region in the public region list (report each separately). Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- stock: Units of the named in-house stock item actually available now (never below 0).
- seats: Seats of the named software actually available now in the requesting region (never below 0).
- seats_other_region: Same for the other region when requested; null when not requested.
- Public region list, in order: SEL, TYO.
### Gold answer
{"stock": 5, "seats": 0, "seats_other_region": 8}
### Counterfactual answers (generator)
{"stale": {"stock": 4, "seats": 0, "seats_other_region": 8}, "partial": {"stock": 4, "seats": 0, "seats_other_region": 8}, "neardup": {"stock": 5, "seats": 0, "seats_other_region": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/stock/INV-SEL-WSS** (group IT-SEL, class C, local=False)
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-WSS"}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01351 [decision-critical] (db_pending/observation, day 8, by it-sel.n0011; DB shows 7): In-house stock workstation (standard) Receipt added. Stored value: 7
- RECORD FR-01179 [decision-critical] (operational/pending_intent, day 5, by it-sel.a5; DB shows n/a): In-house stock workstation (standard) 1 unit held for an incoming Sales Team 2 hire until day 10.
- RECORD FR-01396 [decision-critical] (operational/pending_intent, day 9, by it-sel.n0011; DB shows n/a): In-house stock workstation (standard) 1 unit held as a Customer Support Team replacement spare until day 14.
**need IT-SEL/license/IDE Pro** (group IT-SEL, class A, local=False)
- DB `IT-SEL/lic/IDE Pro/seats` v10 (recorded day 7, registered day 8): {"seats": 37, "used": 37}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00896 (operational/pending_intent, day 0, by it-sel.a4; DB shows n/a): IDE Pro seats 3 seats reserved for Dev Team 1 project until day 9.
- RECORD FR-00971 (operational/pending_intent, day 1, by it-sel.a5; DB shows n/a): IDE Pro seats 3 seats reserved for Marketing Team onboarding until day 9.
- RECORD FR-01079 (operational/pending_intent, day 3, by it-sel.a3; DB shows n/a): IDE Pro seats 2 seats reserved for Sales Team 1 project until day 13.
**need IT-TYO/license/IDE Pro** (group IT-TYO, class B, local=False)
- RECORD FR-01362 [decision-critical] (db_pending/observation, day 9, by it-tyo.w00215; DB shows 5): IDE Pro seats In use 16/24 seats. Stored value: {"seats":24,"used":16}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
### Model answer and official verdict
answer: {"seats": 0, "seats_other_region": 8, "stock": 5}
official exact match: 1 (3/3 slots)

## CASE 93: deepseek-v4-flash · full_load · s12 · W-00098 · class C · day 10 · template whatif
### Task as given to the requester
Can a workstation for Eunho (Manager) at 1,627,718 KRW go ahead right now, and if not, will it work after the next budget reset?
[Request scope] item=workstation; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- now: true if the amount can be spent today.
- later: true if it can be spent on the next budget reset day (taking any notified price change into account when procurement review is included).
- available_then: Available budget of the department on the next reset day.
- Public region list, in order: SEL, TYO.
### Gold answer
{"now": false, "later": true, "available_then": 1902875}
### Counterfactual answers (generator)
{"stale": null, "partial": {"now": false, "later": true, "available_then": 2053020}, "neardup": {"now": false, "later": true, "available_then": 3650183}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1012/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1012"}
- DB `HR-SEL/emp/E-SEL-1012/profile` v4 (recorded day 5, registered day 6): {"dept": "Dev Team 2", "grade": 1, "contract": "regular", "hire_day": -486, "status": "active"}
**need FIN-SEL/Dev Team 2/budget_schedule** (group FIN-SEL, class C, local=False)
- DB `FIN-SEL/line/Dev Team 2/remaining` v1 (recorded day -20, registered day -20): 2515374
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00945 (operational/pending_intent, day 1, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 152,194 KRW earmarked for meeting room replacement until day 12 (no voucher yet).
- RECORD FR-01185 (operational/pending_intent, day 5, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 327,724 KRW earmarked for meeting room replacement until day 14 (no voucher yet).
- RECORD FR-01354 [decision-critical] (operational/pending_intent, day 8, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 150,145 KRW earmarked for training equipment until day 16 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00044/status` v2 (recorded day 1, registered day 2): {"status": "settled", "amount": 541440, "expected_settle": 1}
- RECORD FR-01432 (db_pending/observation, day 10, by fin-sel.a3; DB shows 1): CMT-00045 Dev Team 2 provisional approval settled. Stored value: {"amount":572995,"expected_settle":10,"status":"settled"}
- RECORD FR-01422 [decision-critical] (operational/pending_intent, day 10, by fin-sel.a3; DB shows n/a): CMT-00097 Dev Team 2 travel advance provisional approval 462,354 KRW under review, settlement expected day 24.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 2 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00945", "earmark:FR-01185", "earmark:FR-01354", "CMT-00064", "CMT-00083", "CMT-00097"]
**need FIN-SEL/Dev Team 2/next_reset** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.reset_calendar: {"id": "FIN-SEL.reset_calendar", "group": "FIN-SEL", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-SEL/line/Dev Team 2/base` v1 (recorded day -20, registered day -20): 2515374
### Model answer and official verdict
answer: {"available_then": 1902875, "later": true, "now": false}
official exact match: 1 (3/3 slots)

## CASE 94: deepseek-v4-flash · full_load · s12 · W-00041 · class D · day 5 · template diag
### Task as given to the requester
Invoice INV-96729 (524,745 KRW, beneficiary Minjae (Lead), asset A-SEL-4259, provisional approval CMT-00040) does not match. Find the cause.
[Request scope] target supplier=V-SEL-1; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- cause: Single reported cause code (per the finance reporting precedence), or 'OK' if nothing is wrong.
- Public region list, in order: SEL, TYO.
### Gold answer
{"cause": "ASSET_NOT_REGISTERED"}
### Counterfactual answers (generator)
{"stale": {"cause": "OK"}, "partial": {"cause": "OK"}, "neardup": {"cause": "EMP_EXITED"}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/CMT-00040/status** (group FIN-SEL, class None, local=True)
- CATALOG: {"group": "FIN-SEL", "key": "commits/CMT-00040"}
- DB `FIN-SEL/commit/CMT-00040/status` v1 (recorded day -2, registered day -1): {"status": "pending", "amount": 524745, "expected_settle": 8}
**need HR-SEL/E-SEL-1006/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1006"}
- DB `HR-SEL/emp/E-SEL-1006/profile` v2 (recorded day -10, registered day -7): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -531, "status": "active"}
**need IT-SEL/E-SEL-1006/assets** (group IT-SEL, class D, local=False)
- RECORD FR-01095 [decision-critical] (db_pending/observation, day 4, by it-sel.n0003; DB shows 1): A-SEL-4259 monitor recovered, back in storage. Stored value: {"emp":null}
- QUERY SELECT asset WHERE holder=E-SEL-1006 → []
**need PROC-SEL/receipt/CMT-00040** (group PROC-SEL, class A, local=False)
- DB `PROC-SEL/receipt/CMT-00040/received` v1 (recorded day -1, registered day 0): true
**need PROC-SEL/vendor/V-SEL-1/status** (group PROC-SEL, class A, local=False)
- NEGATIVE: {"query": "PROC-SEL exclusion order for supplier V-SEL-1", "result": []}
**need LEGAL-SEL/E-SEL-1006/contract** (group LEGAL-SEL, class A, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1006/terms` v4 (recorded day 2, registered day 5): {"allowed_tier": "standard", "expiry": 12, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00547 (operational/exception, day -11, by legal-sel.a3; DB shows n/a): Equipment exception of Oh Minjae higher tiers including premium allowed until day 19 for a project, legal check done.
**need FIN-SEL/rule/invoice_match_precedence** (group FIN-SEL, class None, local=True)
- RULE FIN-SEL.invoice_match_precedence: {"id": "FIN-SEL.invoice_match_precedence", "group": "FIN-SEL", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "OK"}
official exact match: 0 (0/1 slots)

## CASE 95: deepseek-v4-flash · full_load · s12 · W-00070 · class D · day 7 · template contract_gate
### Task as given to the requester
For Minjae (Lead): the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- it_tier: Highest tier IT allows this employee right now.
- contract_tier: Highest tier the contract allows right now (including any legal exception).
- nda_step: true if standard equipment would currently require an NDA check step, else false.
- expiry: Contract expiry day.
- Public region list, in order: SEL, TYO.
### Gold answer
{"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 12}
### Counterfactual answers (generator)
{"stale": null, "partial": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 12}, "neardup": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 53}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1006/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1006"}
- DB `HR-SEL/emp/E-SEL-1006/profile` v2 (recorded day -10, registered day -7): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -531, "status": "active"}
**need IT-SEL/eligibility/E-SEL-1006** (group IT-SEL, class D, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
- RECORD FR-00884 [decision-critical] (operational/exception, day -1, by it-sel.a3; DB shows n/a): Equipment tier of Oh Minjae up to standard allowed until day 15 for work reasons (IT exception approved).
- RULE IT-SEL.tier_exception: {"id": "IT-SEL.tier_exception", "group": "IT-SEL", "title": "Equipment tier exception", "params": {"exception_raises_tier": true}, "text": "An equipment tier exception approved by IT replaces the grade-based default tier during the exception period."}
**need LEGAL-SEL/E-SEL-1006/contract** (group LEGAL-SEL, class B, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1006/terms` v4 (recorded day 2, registered day 5): {"allowed_tier": "standard", "expiry": 12, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00547 [decision-critical] (operational/exception, day -11, by legal-sel.a3; DB shows n/a): Equipment exception of Oh Minjae higher tiers including premium allowed until day 19 for a project, legal check done.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 12, "it_tier": "standard", "nda_step": false}
official exact match: 1 (4/4 slots)

## CASE 96: deepseek-v4-flash · full_load · s14 · W-00057 · class D · day 6 · template capacity
### Task as given to the requester
How many in-house laptop (standard) units and IDE Pro seats are actually available right now?
[Request scope] item=laptop; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- stock: Units of the named in-house stock item actually available now (never below 0).
- seats: Seats of the named software actually available now in the requesting region (never below 0).
- seats_other_region: Same for the other region when requested; null when not requested.
- Public region list, in order: SEL, TYO.
### Gold answer
{"stock": 0, "seats": 0, "seats_other_region": null}
### Counterfactual answers (generator)
{"stale": {"stock": 1, "seats": 0, "seats_other_region": null}, "partial": {"stock": 0, "seats": 1, "seats_other_region": null}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/stock/INV-TYO-LTS** (group IT-TYO, class A, local=False)
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-LTS"}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-TYO/inv/INV-TYO-LTS/qty` v3 (recorded day -10, registered day -9): 0
- NEGATIVE: {"query": "IT-TYO INV-TYO-LTS memos on active holds", "result": []}
**need IT-TYO/license/IDE Pro** (group IT-TYO, class D, local=False)
- DB `IT-TYO/lic/IDE Pro/seats` v4 (recorded day 5, registered day 6): {"seats": 20, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00858 [decision-critical] (operational/pending_intent, day -3, by it-tyo.w00111; DB shows n/a): IDE Pro seats 4 seats reserved for Dev Section 2 project until day 10.
- RECORD FR-01290 (operational/pending_intent, day 6, by it-tyo.w00194; DB shows n/a): IDE Pro seats 2 seats reserved for Dev Section 1 project until day 19.
### Model answer and official verdict
answer: {"seats": 0, "seats_other_region": null, "stock": 0}
official exact match: 1 (3/3 slots)

## CASE 97: qwen3.5-9b · direct · s14 · W-00084 · class A · day 9 · template purchase
### Task as given to the requester
For Siwoo (Manager)'s workstation request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
[Request scope] item=workstation; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- decision: 'assign' (in-house stock) or 'order' (supplier quote) for the cheapest candidate that satisfies every applicable condition; 'none' if no candidate qualifies. Use 'order' only when procurement review is included, otherwise 'assign'.
- option: ID of the chosen candidate; null when decision is 'none'.
- approver: Finance approver required for the chosen candidate's cost; null when decision is 'none'.
- nda: true if the chosen item needs an NDA check under contract review, otherwise false; null when decision is 'none'.
- budget_after: Available budget of the employee's department minus the chosen cost; null when decision is 'none'.
- blocked_by: null when a candidate is chosen. When decision is 'none': the first failing condition of the cheapest candidate, checked in this order: budget, eligibility, vendor_excluded, lead_time, residency, contract; 'no_candidate' if there is no candidate at all.
- Public region list, in order: SEL, TYO.
### Gold answer
{"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "no_candidate"}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1005/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1005"}
- DB `HR-SEL/emp/E-SEL-1005/profile` v2 (recorded day -3, registered day -1): {"dept": "Marketing Team", "grade": 1, "contract": "contractor", "hire_day": -567, "status": "active"}
**need FIN-SEL/Marketing Team/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-00582 (operational/exception, day -9, by fin-sel.a5; DB shows n/a): Marketing Team capex executing office agreed that TYO finance executes it until day 13.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Marketing Team/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Marketing Team/remaining` v1 (recorded day -9, registered day -6): 2900279
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00045/status` v2 (recorded day -1, registered day 2): {"status": "settled", "amount": 499698, "expected_settle": -1}
- DB `FIN-TYO/commit/CMT-00062/status` v2 (recorded day 3, registered day 6): {"status": "settled", "amount": 870914, "expected_settle": 3}
- DB `FIN-TYO/commit/CMT-00075/status` v2 (recorded day 4, registered day 7): {"status": "settled", "amount": 578354, "expected_settle": 4}
- RECORD FR-01199 (operational/pending_intent, day 4, by fin-tyo.a2; DB shows n/a): CMT-00096 Marketing Team meeting room equipment provisional approval 273,885 KRW under review, settlement expected day 17.
- RECORD FR-01344 (db_pending/observation, day 7, by fin-tyo.a4; DB shows ABSENT): CMT-00097 Marketing Team provisional approval 1,424,226 KRW confirmed, settlement expected day 18. Stored value: {"amount":1424226,"expected_settle":18,"status":"pending"}
- RECORD FR-01307 (operational/pending_intent, day 6, by fin-tyo.a2; DB shows n/a): CMT-00103 Marketing Team travel advance provisional approval 511,220 KRW under review, settlement expected day 18.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Marketing Team AND status IN ['reviewing', 'pending'] → ["CMT-00096", "CMT-00097", "CMT-00103"]
**need IT-SEL/eligibility/E-SEL-1005** (group IT-SEL, class None, local=True)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
- RECORD FR-01325 (operational/exception, day 7, by it-sel.n0002; DB shows n/a): Equipment tier of Han Siwoo up to standard allowed until day 18 for work reasons (IT exception approved).
- RULE IT-SEL.tier_exception: {"id": "IT-SEL.tier_exception", "group": "IT-SEL", "title": "Equipment tier exception", "params": {"exception_raises_tier": true}, "text": "An equipment tier exception approved by IT replaces the grade-based default tier during the exception period."}
**need IT-SEL/inventory/workstation** (group IT-SEL, class None, local=True)
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-WSP"}
- DB `IT-SEL/inv/INV-SEL-WSP/qty` v4 (recorded day 6, registered day 7): 1
- RECORD FR-01366 (operational/pending_intent, day 7, by it-sel.a1; DB shows n/a): In-house stock workstation (premium) 1 unit held as a Sales Team 1 replacement spare until day 15.
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-WSS"}
- DB `IT-SEL/inv/INV-SEL-WSS/qty` v6 (recorded day 2, registered day 4): 0
**need LEGAL-SEL/residency** (group LEGAL-SEL, class A, local=False)
- RULE LEGAL-SEL.residency: {"id": "LEGAL-SEL.residency", "group": "LEGAL-SEL", "title": "Data residency", "params": {"restricted_depts": ["Sales Team 1", "Sales Team 2"]}, "text": "These departments may not use equipment from offshore suppliers: Sales Team 1, Sales Team 2."}
### Model answer and official verdict
answer: {"approver": null, "blocked_by": "eligibility", "budget_after": null, "decision": "none", "nda": null, "option": null}
official exact match: 0 (5/6 slots)

## CASE 98: qwen3.5-9b · routing · s13 · W-00139 · class B · day 14 · template renewal
### Task as given to the requester
Seoyun (Lead)'s contract is about to expire. Can it be renewed, and if not, which assets must be recovered?
[Request scope] renewal cost=233,438 KRW; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- renew: true if the contract can be renewed.
- recover_assets: If renew is false: asset IDs the employee currently holds (any order). If renew is true: empty list.
- Public region list, in order: SEL, TYO.
### Gold answer
{"renew": false, "recover_assets": ["A-SEL-43620"]}
### Counterfactual answers (generator)
{"stale": null, "partial": {"renew": false, "recover_assets": []}, "neardup": {"renew": false, "recover_assets": ["A-SEL-41609"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need LEGAL-SEL/E-SEL-2015/contract** (group LEGAL-SEL, class A, local=False)
- DB `LEGAL-SEL/contract/E-SEL-2015/terms` v1 (recorded day 7, registered day 8): {"allowed_tier": "standard", "expiry": 39, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RULE LEGAL-SEL.renewal_policy: {"id": "LEGAL-SEL.renewal_policy", "group": "LEGAL-SEL", "title": "Contract renewal", "params": {"min_grade": 2}, "text": "Renewal conditions: active employment, grade 2 or higher, renewal cost within the department's available budget."}
**need HR-SEL/E-SEL-2015/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2015"}
- RECORD FR-01690 (db_pending/observation, day 13, by hr-sel.a1; DB shows 1): HR record of Mo Seoyun exit processed (Sales Team 1). Stored value: {"contract":"contractor","dept":"Sales Team 1","grade":2,"hire_day":6,"status":"exited"}
**need FIN-SEL/Sales Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-01737 (db_pending/rationale, day 14, by fin-sel.a1; DB shows 6): Sales Team 1 capex balance adjusted to 1,993,140 KRW (quarter carry-over). Stored value: 1993140
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01224 (operational/pending_intent, day 5, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 369,909 KRW earmarked for training equipment until day 16 (no voucher yet).
- RECORD FR-01260 (operational/pending_intent, day 6, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 162,433 KRW earmarked for meeting room replacement until day 19 (no voucher yet).
- RECORD FR-01615 (operational/pending_intent, day 12, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 432,093 KRW earmarked for new-hire equipment until day 20 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00006/status` v2 (recorded day -12, registered day -9): {"status": "settled", "amount": 795461, "expected_settle": -12}
- DB `FIN-SEL/commit/CMT-00015/status` v2 (recorded day -8, registered day -6): {"status": "settled", "amount": 599076, "expected_settle": -8}
- DB `FIN-SEL/commit/CMT-00020/status` v2 (recorded day -1, registered day 0): {"status": "settled", "amount": 967831, "expected_settle": -1}
- DB `FIN-SEL/commit/CMT-00022/status` v2 (recorded day -7, registered day -6): {"status": "settled", "amount": 274002, "expected_settle": -7}
- DB `FIN-SEL/commit/CMT-00031/status` v2 (recorded day -1, registered day 2): {"status": "settled", "amount": 771458, "expected_settle": -1}
- DB `FIN-SEL/commit/CMT-00033/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 202746, "expected_settle": -4}
- DB `FIN-SEL/commit/CMT-00039/status` v2 (recorded day 5, registered day 7): {"status": "settled", "amount": 548951, "expected_settle": 5}
- DB `FIN-SEL/commit/CMT-00042/status` v2 (recorded day 8, registered day 10): {"status": "settled", "amount": 785966, "expected_settle": 8}
- RECORD FR-01573 (operational/pending_intent, day 12, by fin-sel.a3; DB shows n/a): CMT-00104 Sales Team 1 travel advance provisional approval 691,367 KRW under review, settlement expected day 26.
- RECORD FR-01616 (operational/pending_intent, day 12, by fin-sel.a3; DB shows n/a): CMT-00108 Sales Team 1 laptop provisional approval 268,660 KRW under review, settlement expected day 26.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-01224", "earmark:FR-01260", "earmark:FR-01615", "CMT-00104", "CMT-00108"]
**need IT-SEL/E-SEL-2015/assets** (group IT-SEL, class B, local=False)
- RECORD FR-01641 [decision-critical] (db_pending/observation, day 13, by it-sel.a2; DB shows ABSENT): A-SEL-43620 workstation Assigned to Mo Seoyun. Stored value: {"emp":"E-SEL-2015"}
- QUERY SELECT asset WHERE holder=E-SEL-2015 → ["A-SEL-43620"]
### Model answer and official verdict
answer: {"recover_assets": [], "renew": true}
official exact match: 0 (0/2 slots)
### MATCHER CHECK FR-01641 (need IT-SEL/E-SEL-2015/assets): matcher says **missing**
record text: A-SEL-43620 workstation Assigned to Mo Seoyun. Stored value: {"emp":"E-SEL-2015"}
What the requester received from IT-SEL during this task:
```
[Reply 1] (partial)
[Reply 2] (partial) Employee E-SEL-2015 (Seoyun, Lead) has no assets registered in the database. No catalog entry exists for this employee in my area's records. Active IT exceptions or holds affecting contract renewal are not available in my area's records.
[Reply 3] (partial)
- E-SEL-2015 | assets held | none |  | db, day unknown: Reply 1: D1
- E-SEL-2015 | grade | missing |  | db, day unknown: Reply 1: D2
- E-SEL-2015 | department | missing |  | db, day unknown: Reply 1: D2
- E-SEL-2015 | active IT exception | unknown |  | db, day unknown: Reply 1: D2
- E-SEL-2015 | holds affecting contract renewal | unknown |  | db, day unknown: Reply 1: D2
- E-SEL-2015 | assets held | none found in database |  | db, day unknown: Reply 2: D1
- E-SEL-2015 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
- E-SEL-2015 | assets held | none found in records |  | db, day unknown: Reply 3: D1
- E-SEL-2015 | active IT exceptions | none found in records |  | db, day unknown: Reply 3: D2
- E-SEL-2015 | holds affecting contract renewal | none found in records |  | db, day unknown: Reply 3: D2
missing: E-SEL-2015 grade; E-SEL-2015 department; active IT exception for E-SEL-2015; holds affecting contract renewal for E-SEL-2015; active IT exceptions for E-SEL-2015; grade of employee E-SEL-2015 (Seoyun)
```

## CASE 99: qwen3.5-9b · ingress · s12 · W-00150 · class D · day 15 · template whatif
### Task as given to the requester
Can a monitor for Doyun (Senior) at 1,488,968 KRW go ahead right now, and if not, will it work after the next budget reset?
[Request scope] item=monitor; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- now: true if the amount can be spent today.
- later: true if it can be spent on the next budget reset day (taking any notified price change into account when procurement review is included).
- available_then: Available budget of the department on the next reset day.
- Public region list, in order: SEL, TYO.
### Gold answer
{"now": true, "later": true, "available_then": 1891740}
### Counterfactual answers (generator)
{"stale": null, "partial": {"now": true, "later": true, "available_then": 2447876}, "neardup": {"now": false, "later": false, "available_then": 1175246}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1001/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1001"}
- DB `HR-SEL/emp/E-SEL-1001/profile` v4 (recorded day -1, registered day 1): {"dept": "Dev Team 1", "grade": 3, "contract": "regular", "hire_day": -606, "status": "active"}
**need FIN-SEL/Dev Team 1/budget_schedule** (group FIN-SEL, class D, local=False)
- DB `FIN-SEL/line/Dev Team 1/remaining` v3 (recorded day 6, registered day 7): 3124022
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01082 [decision-critical] (operational/pending_intent, day 3, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 556,136 KRW earmarked for quarter-end consumables until day 16 (no voucher yet).
- RECORD FR-01421 [decision-critical] (operational/pending_intent, day 10, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 316,687 KRW earmarked for new-hire equipment until day 22 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00017/status` v2 (recorded day 0, registered day 3): {"status": "settled", "amount": 401082, "expected_settle": 0}
- DB `FIN-SEL/commit/CMT-00021/status` v2 (recorded day 0, registered day 3): {"status": "settled", "amount": 385564, "expected_settle": 0}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-01082", "earmark:FR-01421"]
**need FIN-SEL/Dev Team 1/next_reset** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.reset_calendar: {"id": "FIN-SEL.reset_calendar", "group": "FIN-SEL", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-SEL/line/Dev Team 1/base` v1 (recorded day -20, registered day -20): 2764563
**need PROC-SEL/price_notice/monitor** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.price_notice_policy: {"id": "PROC-SEL.price_notice_policy", "group": "PROC-SEL", "title": "Price increase notice", "params": {"apply_from_effective_day": true}, "text": "A notified price increase applies to all new items from the effective day stated in the notice."}
- RECORD FR-00364 (operational/observation, day -15, by proc-sel.w00029; DB shows n/a): monitor unit price notified: 10% increase from day 16.
- RECORD FR-01299 (operational/observation, day 7, by proc-sel.w00206; DB shows n/a): monitor unit price notified: 8% increase from day 16.
### Model answer and official verdict
answer: {"available_then": 3124022, "later": true, "now": false}
official exact match: 0 (1/3 slots)
### MATCHER CHECK FR-01082 (need FIN-SEL/Dev Team 1/budget_schedule): matcher says **missing**
record text: Dev Team 1 capex 556,136 KRW earmarked for quarter-end consumables until day 16 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 1: D1
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 2: D1
- Dev Team 1 | available budget | 3124022 |  | db, day 7: Reply 2: calculation from D1 and D2
- CMT-00017 | amount | 401082 | settled | db, day 3: Reply 2: D2
- CMT-00021 | amount | 385564 | settled | db, day 3: Reply 2: D2
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 3: D1
- Dev Team 1 | holds on budget | none found in records |  | history, day 3: Reply 4: H232
- Dev Team 1 | reservations on budget | none found in records |  | history, day 3: Reply 4: H233
- Dev Team 1 | exclusions for Dev Team 1 | none found in records |  | history, day 3: Reply 4: H234
- Dev Team 1 | quarterly spending control | unknown |  | history, day 3: Reply 4: H234
- Dev Team 1 | holds on budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | reservations on budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | exclusions for budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | quarterly spending control | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | holds on budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | reservations on budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | exclusions for budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | quarterly spending control | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | holds on budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | reservations on budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | exclusions for budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | quarterly spending control | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | budget line balance | 3124022 |  | history, day 6: [E12]
- Dev Team 1 | budget line base | 2764563 |  | history, day -20: [E1]
- CMT-00017 | amount | 401082 | settled | history, day 3: [E7]
- CMT-00017 | expected_settle | 0 | settled | history, day 3: [E7]
- CMT-00021 | amount | 385564 | settled | history, day 3: [E7]
- CMT-00021 | expected_settle | 0 | settled | history, day 3: [E7]
- Earmark Dev Team 1 budget (new-hire equipment) | amount | 512677 | until day 13 | history, day -1: [E5]
missing: holds on Dev Team 1 budget; reservations on Dev Team 1 budget; exclusions for Dev Team 1; quarterly spending control for Dev Team 1
---
- Dev Team 1 | next budget reset day | day 28 |  | rule, day fixed: Reply 1: reset_calendar
- Dev Team 1 | next budget reset day | day 28 |  | rule, day fixed: [R1]
```
### MATCHER CHECK FR-01421 (need FIN-SEL/Dev Team 1/budget_schedule): matcher says **missing**
record text: Dev Team 1 capex 316,687 KRW earmarked for new-hire equipment until day 22 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 1: D1
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 2: D1
- Dev Team 1 | available budget | 3124022 |  | db, day 7: Reply 2: calculation from D1 and D2
- CMT-00017 | amount | 401082 | settled | db, day 3: Reply 2: D2
- CMT-00021 | amount | 385564 | settled | db, day 3: Reply 2: D2
- Dev Team 1 | budget line balance | 3124022 |  | db, day 7: Reply 3: D1
- Dev Team 1 | holds on budget | none found in records |  | history, day 3: Reply 4: H232
- Dev Team 1 | reservations on budget | none found in records |  | history, day 3: Reply 4: H233
- Dev Team 1 | exclusions for Dev Team 1 | none found in records |  | history, day 3: Reply 4: H234
- Dev Team 1 | quarterly spending control | unknown |  | history, day 3: Reply 4: H234
- Dev Team 1 | holds on budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | reservations on budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | exclusions for budget | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | quarterly spending control | none found in records |  | unknown, day unknown: Reply 5: 
- Dev Team 1 | holds on budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | reservations on budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | exclusions for budget | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | quarterly spending control | none found |  | history, day 12: Reply 6: H288
- Dev Team 1 | holds on budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | reservations on budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | exclusions for budget | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | quarterly spending control | NOT FOUND |  | history, day 10: Reply 7: H285
- Dev Team 1 | budget line balance | 3124022 |  | history, day 6: [E12]
- Dev Team 1 | budget line base | 2764563 |  | history, day -20: [E1]
- CMT-00017 | amount | 401082 | settled | history, day 3: [E7]
- CMT-00017 | expected_settle | 0 | settled | history, day 3: [E7]
- CMT-00021 | amount | 385564 | settled | history, day 3: [E7]
- CMT-00021 | expected_settle | 0 | settled | history, day 3: [E7]
- Earmark Dev Team 1 budget (new-hire equipment) | amount | 512677 | until day 13 | history, day -1: [E5]
missing: holds on Dev Team 1 budget; reservations on Dev Team 1 budget; exclusions for Dev Team 1; quarterly spending control for Dev Team 1
---
- Dev Team 1 | next budget reset day | day 28 |  | rule, day fixed: Reply 1: reset_calendar
- Dev Team 1 | next budget reset day | day 28 |  | rule, day fixed: [R1]
```

## CASE 100: qwen3.5-9b · full_load · s13 · W-00138 · class C · day 14 · template sourcing
### Task as given to the requester
Planning Section will place a department order for a monitor. List the usable quotes right now from cheapest, with quote amount and actual lead time.
[Request scope] item=monitor; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- options: List of [quote_id, amount, lead_days] for every quote usable right now for a department order, cheapest first (ties by quote ID); lead_days is the lead time actually in effect today. Empty list if none. Registration status does not remove a quote from this list (list quotes of unregistered suppliers too).
- Public region list, in order: SEL, TYO.
### Gold answer
{"options": [["Q-V-TYO-2-MNB", 640262, 10], ["Q-V-TYO-1-MNB", 827020, 6], ["Q-V-TYO-1-MNS", 1039588, 6], ["Q-V-TYO-2-MNS", 1148249, 10]]}
### Counterfactual answers (generator)
{"stale": {"options": [["Q-V-TYO-2-MNB", 640262, 10], ["Q-V-TYO-1-MNB", 827020, 8], ["Q-V-TYO-1-MNS", 1039588, 6], ["Q-V-TYO-2-MNS", 1148249, 10]]}, "partial": {"options": [["Q-V-TYO-2-MNB", 640262, 10], ["Q-V-TYO-3-MNB", 730231, 6], ["Q-V-TYO-1-MNB", 827020, 6], ["Q-V-TYO-1-MNS", 1039588, 6], ["Q-V-TYO-2-MNS", 1148249, 10], ["Q-V-TYO-3-MNS", 1540273, 6]]}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need PROC-TYO/quotes/monitor** (group PROC-TYO, class C, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01723 [decision-critical] (operational/handover, day 14, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-3 exclude from comparisons until day 26 due to a quality issue.
- RECORD FR-01076 (operational/observation, day 2, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 2 days until day 14.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01233 [decision-critical] (operational/observation, day 5, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 4 days until day 16.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01264 [decision-critical] (operational/observation, day 6, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-1 delivery notified: deliveries delayed by 2 days until day 14.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01337 (operational/observation, day 7, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-0 delivery notified: deliveries delayed by 5 days until day 20.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 5, registered day 6): 11
- DB `PROC-TYO/quote/Q-V-TYO-0-MNB/amount` v2 (recorded day 13, registered day 14): 858560
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 5, registered day 6): 11
- DB `PROC-TYO/quote/Q-V-TYO-0-MNS/amount` v1 (recorded day -20, registered day -20): 1439646
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v4 (recorded day 4, registered day 7): 4
- DB `PROC-TYO/quote/Q-V-TYO-1-MNB/amount` v1 (recorded day -20, registered day -20): 827020
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v4 (recorded day 4, registered day 7): 4
- DB `PROC-TYO/quote/Q-V-TYO-1-MNS/amount` v2 (recorded day -15, registered day -12): 1039588
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v3 (recorded day 5, registered day 7): 6
- DB `PROC-TYO/quote/Q-V-TYO-2-MNB/amount` v3 (recorded day 3, registered day 4): 640262
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v3 (recorded day 5, registered day 7): 6
- DB `PROC-TYO/quote/Q-V-TYO-2-MNS/amount` v1 (recorded day -20, registered day -20): 1148249
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v5 (recorded day 10, registered day 12): 4
- DB `PROC-TYO/quote/Q-V-TYO-3-MNB/amount` v2 (recorded day 1, registered day 3): 730231
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v5 (recorded day 10, registered day 12): 4
- DB `PROC-TYO/quote/Q-V-TYO-3-MNS/amount` v1 (recorded day -20, registered day -20): 1540273
### Model answer and official verdict
answer: {"options": [["Q-V-TYO-2-MNB", 640262, 10], ["Q-V-TYO-1-MNB", 827020, 6], ["Q-V-TYO-1-MNS", 1039588, 6], ["Q-V-TYO-2-MNS", 1148249, 10]]}
official exact match: 1 (1/1 slots)