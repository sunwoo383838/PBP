## CASE 40: qwen3.5-27b · full_load · s14 · W-00081 · class B · day 9 · template plan
### Task as given to the requester
We want to go ahead with W-00074 as is. List the approvals needed, in order.
[Request scope] item=workstation; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- steps: Ordered list of required approval steps, from: IT_EXCEPTION, LEGAL_NDA, LEGAL_OVERRIDE, BLOCKED_CONTRACT, FIN_TEAM_LEAD, FIN_DIVISION_HEAD, FIN_CFO, PROC_VENDOR_ONBOARD. Order: IT step, then legal step, then finance step, then procurement step. If the contract forbids the item, the list is exactly ["BLOCKED_CONTRACT"].
- Public region list, in order: SEL, TYO.
### Gold answer
{"steps": ["IT_EXCEPTION", "LEGAL_OVERRIDE", "FIN_DIVISION_HEAD"]}
### Counterfactual answers (generator)
{"stale": null, "partial": {"steps": ["BLOCKED_CONTRACT"]}, "neardup": {"steps": ["IT_EXCEPTION", "FIN_DIVISION_HEAD"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/task/W-00074/result** (group FIN-SEL, class None, local=True)
- RECORD FR-01422 (operational/task_result, day 8, by fin-sel.a2; DB shows n/a): W-00074 item result: approver=legal_and_division_head, governing_rule=legal_override, it_exception=True
**need HR-SEL/E-SEL-2007/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2007"}
- DB `HR-SEL/emp/E-SEL-2007/profile` v3 (recorded day 4, registered day 5): {"dept": "Sales Team 1", "grade": 1, "contract": "contractor", "hire_day": -12, "status": "active"}
**need IT-SEL/eligibility/E-SEL-2007** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-SEL/E-SEL-2007/contract** (group LEGAL-SEL, class B, local=False)
- DB `LEGAL-SEL/contract/E-SEL-2007/terms` v5 (recorded day 5, registered day 7): {"allowed_tier": "standard", "expiry": 108, "nda": true}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01389 [decision-critical] (operational/exception, day 8, by legal-sel.a4; DB shows n/a): Equipment exception of Jegal Yoon higher tiers including premium allowed until day 27 for a project, legal check done.
- RECORD FR-00587 (operational/observation, day -9, by legal-sel.a5; DB shows n/a): NDA of Jegal Yoon signed copy verified, NDA check step can be skipped until day 19.
**need FIN-SEL/approval** (group FIN-SEL, class None, local=True)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"steps": ["FIN_TEAM_LEAD"]}
official exact match: 0 (0/1 slots)

## CASE 41: qwen3.5-27b · full_load · s12 · W-00009 · class B · day 1 · template conflict
### Task as given to the requester
Check whether CMT-00055 is still live and what amount to count for it. We are hearing conflicting things.
[Request scope] procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- status: Effective status of the provisional approval: 'reviewing', 'pending', 'settled', 'cancelled', or 'none' if no authoritative record exists.
- amount: Amount to count for it: the approval amount while it is 'reviewing' or 'pending', otherwise 0.
- Public region list, in order: SEL, TYO.
### Gold answer
{"status": "cancelled", "amount": 0}
### Counterfactual answers (generator)
{"stale": null, "partial": {"status": "none", "amount": 0}, "neardup": {"status": "reviewing", "amount": 547336}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00055/effective_status** (group FIN-TYO, class B, local=False)
- NEGATIVE: {"query": "FIN-TYO catalog commits/CMT-00055", "result": []}
- RECORD FR-00967 [decision-critical] (db_pending/observation, day 1, by fin-tyo.a5; DB shows ABSENT): CMT-00055 Planning Section provisional approval cancellation confirmed. Stored value: {"amount":237272,"expected_settle":10,"status":"cancelled"}
- RULE FIN-TYO.status_authority: {"id": "FIN-TYO.status_authority", "group": "FIN-TYO", "title": "Validity of provisional approval status", "params": {"authoritative": ["db", "owner_record"], "informal_excluded": true}, "text": "Only the registered record and the handling officer's processing record determine a provisional approval's status. Informal remarks or discussions do not change it."}
- RECORD FR-00852 (operational/observation, day -2, by fin-tyo.a1; DB shows n/a): CMT-00055 item someone suggested cancelling it (not decided).
**need PROC-TYO/receipt/CMT-00055** (group PROC-TYO, class None, local=True)
- QUERY {"key": "PROC-TYO/receipt/CMT-00055/received", "asof": 1} → "ABSENT"
### Model answer and official verdict
answer: {"amount": 0, "status": "cancelled"}
official exact match: 1 (2/2 slots)

## CASE 42: qwen3.5-27b · full_load · s12 · W-00058 · class B · day 6 · template whatif
### Task as given to the requester
Can a workstation for Ishikawa-san at 4,233,016 KRW go ahead right now, and if not, will it work after the next budget reset?
[Request scope] item=workstation; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"now": false, "later": false, "available_then": 4314543}
### Counterfactual answers (generator)
{"stale": {"now": false, "later": false, "available_then": 4507369}, "partial": {"now": false, "later": true, "available_then": 4865609}, "neardup": {"now": true, "later": false, "available_then": 4275418}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2007/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2007"}
- DB `HR-TYO/emp/E-TYO-2007/profile` v2 (recorded day 2, registered day 4): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -12, "status": "active"}
**need FIN-TYO/Sales Section 1/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Sales Section 1/remaining` v6 (recorded day 4, registered day 5): 4113405
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00856 (operational/pending_intent, day -2, by fin-tyo.a4; DB shows n/a): Sales Section 1 capex 366,200 KRW earmarked for new-hire equipment until day 6 (no voucher yet).
- RECORD FR-01021 [decision-critical] (operational/pending_intent, day 2, by fin-tyo.a1; DB shows n/a): Sales Section 1 capex 551,066 KRW earmarked for training equipment until day 17 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00019/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 217637, "expected_settle": -2}
- DB `FIN-TYO/commit/CMT-00028/status` v2 (recorded day -3, registered day -1): {"status": "settled", "amount": 927451, "expected_settle": -3}
- RECORD FR-01169 (operational/pending_intent, day 5, by fin-tyo.a3; DB shows n/a): CMT-00081 Sales Section 1 meeting room equipment provisional approval 609,401 KRW under review, settlement expected day 9.
- RECORD FR-01177 (operational/pending_intent, day 5, by fin-tyo.n0009; DB shows n/a): CMT-00082 Sales Section 1 order (incl. shipping) provisional approval (order of W-00031) 918,151 KRW under review, settlement expected day 12.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Section 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00856", "earmark:FR-01021", "CMT-00081", "CMT-00082"]
**need FIN-TYO/Sales Section 1/next_reset** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.reset_calendar: {"id": "FIN-TYO.reset_calendar", "group": "FIN-TYO", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-TYO/line/Sales Section 1/base` v1 (recorded day -20, registered day -20): 4865609
**need PROC-TYO/price_notice/workstation** (group PROC-TYO, class B, local=False)
- RULE PROC-TYO.price_notice_policy: {"id": "PROC-TYO.price_notice_policy", "group": "PROC-TYO", "title": "Price increase notice", "params": {"apply_from_effective_day": true}, "text": "A notified price increase applies to all new items from the effective day stated in the notice."}
- RECORD FR-01103 [decision-critical] (operational/observation, day 4, by proc-tyo.a2; DB shows n/a): workstation unit price notified: 10% increase from day 16.
### Model answer and official verdict
answer: {"available_then": 4314543, "later": true, "now": false}
official exact match: 0 (2/3 slots)

## CASE 43: qwen3.5-27b · full_load · s14 · W-00134 · class C · day 14 · template purchase
### Task as given to the requester
For Kimura-san's monitor request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
[Request scope] item=monitor; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 811326, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 2557437, "blocked_by": null}, "partial": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 1097301, "blocked_by": null}, "neardup": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 2359184, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1015/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1015"}
- DB `HR-TYO/emp/E-TYO-1015/profile` v4 (recorded day 8, registered day 10): {"dept": "Sales Section 1", "grade": 3, "contract": "regular", "hire_day": -440, "status": "active"}
**need FIN-TYO/Sales Section 1/budget_schedule** (group FIN-TYO, class C, local=False)
- DB `FIN-TYO/line/Sales Section 1/remaining` v3 (recorded day 7, registered day 9): 2988155
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01537 [decision-critical] (operational/pending_intent, day 11, by fin-tyo.a1; DB shows n/a): Sales Section 1 capex 285,975 KRW earmarked for new-hire equipment until day 23 (no voucher yet).
- RECORD FR-01647 [decision-critical] (operational/pending_intent, day 13, by fin-tyo.a1; DB shows n/a): Sales Section 1 capex 269,273 KRW earmarked for new-hire equipment until day 22 (no voucher yet).
- RECORD FR-01701 [decision-critical] (operational/pending_intent, day 14, by fin-tyo.a1; DB shows n/a): Sales Section 1 capex 453,229 KRW earmarked for training equipment until day 25 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00027/status` v2 (recorded day -2, registered day 1): {"status": "settled", "amount": 814288, "expected_settle": -2}
- DB `FIN-TYO/commit/CMT-00030/status` v2 (recorded day -7, registered day -5): {"status": "settled", "amount": 788118, "expected_settle": -7}
- DB `FIN-TYO/commit/CMT-00035/status` v2 (recorded day -7, registered day -5): {"status": "settled", "amount": 331979, "expected_settle": -7}
- RECORD FR-01646 [decision-critical] (operational/pending_intent, day 13, by fin-tyo.a2; DB shows n/a): CMT-00123 Sales Section 1 monitor provisional approval 505,997 KRW under review, settlement expected day 24.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Section 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-01537", "earmark:FR-01647", "earmark:FR-01701", "CMT-00123"]
**need IT-TYO/eligibility/E-TYO-1015** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need IT-TYO/inventory/monitor** (group IT-TYO, class A, local=False)
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-MNB"}
- RECORD FR-01694 (db_pending/observation, day 14, by it-tyo.w00268; DB shows 13): In-house stock monitor (basic) 1 unit issued. Stored value: 3
- RECORD FR-01610 (operational/pending_intent, day 12, by it-tyo.w00253; DB shows n/a): In-house stock monitor (basic) 1 unit held for an incoming Planning Section hire until day 19.
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-MNS"}
- DB `IT-TYO/inv/INV-TYO-MNS/qty` v2 (recorded day -15, registered day -12): 0
**need LEGAL-TYO/residency** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.residency: {"id": "LEGAL-TYO.residency", "group": "LEGAL-TYO", "title": "Data residency", "params": {"restricted_depts": ["Dev Section 1", "Support Section"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Section 1, Support Section."}
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 1317323, "decision": "assign", "nda": false, "option": "INV-TYO-MNB"}
official exact match: 0 (5/6 slots)

## CASE 44: qwen3.5-27b · full_load · s13 · W-00094 · class C · day 10 · template contract_gate
### Task as given to the requester
For Yamada-san: the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "premium", "contract_tier": "premium", "nda_step": false, "expiry": 258}
### Counterfactual answers (generator)
{"stale": {"it_tier": "premium", "contract_tier": "premium", "nda_step": false, "expiry": 222}, "partial": {"it_tier": "premium", "contract_tier": "standard", "nda_step": false, "expiry": 258}, "neardup": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 258}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1012/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1012"}
- DB `HR-TYO/emp/E-TYO-1012/profile` v4 (recorded day 8, registered day 10): {"dept": "Sales Section 1", "grade": 5, "contract": "contractor", "hire_day": -90, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1012** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1012/contract** (group LEGAL-TYO, class C, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1012/terms` v9 (recorded day 9, registered day 10): {"allowed_tier": "standard", "expiry": 258, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00500 [decision-critical] (operational/exception, day -12, by legal-tyo.a3; DB shows n/a): Equipment exception of Yamada Sou higher tiers including premium allowed until day 12 for a project, legal check done.
- RECORD FR-01092 [decision-critical] (operational/observation, day 3, by legal-tyo.n0017; DB shows n/a): NDA of Yamada Sou signed copy verified, NDA check step can be skipped until day 25.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 258, "it_tier": "premium", "nda_step": false}
official exact match: 1 (4/4 slots)

## CASE 45: qwen3.5-27b · full_load · s14 · W-00125 · class C · day 13 · template alloc
### Task as given to the requester
Allocate IDE Pro seats to Customer Support Team, Marketing Team, Sales Team 1 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- alloc: List of integers: seats given to each team, in the team order of the request.
- transfer: Seats pulled from the other region.
- buy: Seats purchased.
- unmet: Total seats still missing after allocation.
- Public region list, in order: SEL, TYO.
### Gold answer
{"alloc": [4, 2, 1], "transfer": 0, "buy": 7, "unmet": 3}
### Counterfactual answers (generator)
{"stale": {"alloc": [5, 2, 0], "transfer": 0, "buy": 7, "unmet": 4}, "partial": {"alloc": [3, 2, 2], "transfer": 0, "buy": 7, "unmet": 2}, "neardup": {"alloc": [4, 3, 0], "transfer": 0, "buy": 7, "unmet": 5}, "wrong_owner": {"alloc": [4, 2, 4], "transfer": 0, "buy": 10, "unmet": 0}}
### World facts behind the gold (by need)
**need IT-SEL/license/IDE Pro** (group IT-SEL, class None, local=True)
- RECORD FR-01663 (db_pending/observation, day 13, by it-sel.a3; DB shows 6): IDE Pro seats In use 27/27 seats. Stored value: {"seats":27,"used":27}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01052 (operational/pending_intent, day 2, by it-sel.a2; DB shows n/a): IDE Pro seats 3 seats reserved for Customer Support Team onboarding until day 16.
- RECORD FR-01593 (operational/pending_intent, day 12, by it-sel.n0002; DB shows n/a): IDE Pro seats 3 seats reserved for Dev Team 1 onboarding until day 17.
**need HR-SEL/Customer Support Team/planning_headcount** (group HR-SEL, class C, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1003/profile` v2 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -675, "status": "active"}
- RECORD FR-01641 [decision-critical] (db_pending/observation, day 13, by hr-sel.a5; DB shows 2): HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
- RECORD FR-01621 [decision-critical] (db_pending/observation, day 12, by hr-sel.a2; DB shows 4): HR record of Oh Minjae exit processed (Customer Support Team). Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":2,"hire_day":-111,"status":"exited"}
- RECORD FR-01643 [decision-critical] (db_pending/observation, day 13, by hr-sel.n0013; DB shows 4): HR record of Shin Daeun moved from Dev Team 1 to Customer Support Team, grade 1, regular. Stored value: {"contract":"regular","dept":"Customer Support Team","grade":1,"hire_day":-869,"status":"active"}
- DB `HR-SEL/emp/E-SEL-1010/profile` v4 (recorded day 9, registered day 12): {"dept": "Customer Support Team", "grade": 5, "contract": "contractor", "hire_day": -385, "status": "active"}
- RECORD FR-01248 [decision-critical] (operational/pending_intent, day 5, by hr-sel.a5; DB shows n/a): Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
- DB `HR-SEL/emp/E-SEL-1017/profile` v3 (recorded day -5, registered day -3): {"dept": "Customer Support Team", "grade": 5, "contract": "regular", "hire_day": -501, "status": "exited"}
- QUERY COUNT(emp WHERE region=SEL AND dept=Customer Support Team AND status=active) → 5
**need HR-SEL/Marketing Team/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-01587 (db_pending/observation, day 12, by hr-sel.a2; DB shows 3): HR record of Kim Harin moved from Marketing Team to Dev Team 2, grade 2, regular. Stored value: {"contract":"regular","dept":"Dev Team 2","grade":2,"hire_day":-510,"status":"active"}
- RECORD FR-01641 [decision-critical] (db_pending/observation, day 13, by hr-sel.a5; DB shows 2): HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
- RECORD FR-01248 [decision-critical] (operational/pending_intent, day 5, by hr-sel.a5; DB shows n/a): Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
- RECORD FR-01642 [decision-critical] (db_pending/observation, day 13, by hr-sel.a5; DB shows 2): HR record of Bong Seoha moved from Marketing Team to Sales Team 2, grade 2, regular. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":2,"hire_day":-6,"status":"active"}
- RECORD FR-01405 [decision-critical] (operational/pending_intent, day 8, by hr-sel.a5; DB shows n/a): Transfer of Tak Jiho approved from Dev Team 2 to Marketing Team, effective day 16 (stays in Dev Team 2 until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Marketing Team AND status=active) → 0
**need HR-SEL/Sales Team 1/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-01587 (db_pending/observation, day 12, by hr-sel.a2; DB shows 3): HR record of Kim Harin moved from Marketing Team to Dev Team 2, grade 2, regular. Stored value: {"contract":"regular","dept":"Dev Team 2","grade":2,"hire_day":-510,"status":"active"}
- RECORD FR-01645 [decision-critical] (operational/pending_intent, day 13, by hr-sel.a5; DB shows n/a): Transfer of Kim Harin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1001/profile` v2 (recorded day -17, registered day -15): {"dept": "Sales Team 1", "grade": 4, "contract": "regular", "hire_day": -60, "status": "exited"}
- RECORD FR-01534 (db_pending/rationale, day 11, by hr-sel.a3; DB shows 3): HR record of Jung Yerin changed to grade 5 (review result), Dev Team 2. Stored value: {"contract":"regular","dept":"Dev Team 2","grade":5,"hire_day":-505,"status":"active"}
- RECORD FR-01626 [decision-critical] (operational/pending_intent, day 12, by hr-sel.a5; DB shows n/a): Transfer of Jung Yerin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1018/profile` v3 (recorded day 12, registered day 13): {"dept": "Sales Team 1", "grade": 1, "contract": "regular", "hire_day": -560, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v3 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -15, "status": "active"}
- QUERY COUNT(emp WHERE region=SEL AND dept=Sales Team 1 AND status=active) → 2
**need IT-TYO/license/IDE Pro** (group IT-TYO, class A, local=False)
- DB `IT-TYO/lic/IDE Pro/seats` v4 (recorded day 5, registered day 6): {"seats": 20, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01290 (operational/pending_intent, day 6, by it-tyo.w00194; DB shows n/a): IDE Pro seats 2 seats reserved for Dev Section 1 project until day 19.
- RECORD FR-01470 (operational/pending_intent, day 9, by it-tyo.w00233; DB shows n/a): IDE Pro seats 3 seats reserved for Sales Section 2 onboarding until day 19.
**need IT-SEL/rule/seat_transfer_share** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_transfer_share: {"id": "IT-SEL.seat_transfer_share", "group": "IT-SEL", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-SEL/rule/seat_purchase_line** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.seat_purchase_line: {"id": "FIN-SEL.seat_purchase_line", "group": "FIN-SEL", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-SEL/Customer Support Team/budget_schedule** (group FIN-SEL, class B, local=False)
- RECORD FR-01471 [decision-critical] (operational/exception, day 9, by fin-sel.a3; DB shows n/a): Customer Support Team capex executing office agreed that TYO finance executes it until day 27.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Customer Support Team/budget_schedule** (group FIN-TYO, class C, local=False)
- DB `FIN-TYO/line/Customer Support Team/remaining` v1 (recorded day 9, registered day 10): 2983974
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01493 [decision-critical] (operational/pending_intent, day 10, by fin-tyo.a4; DB shows n/a): CMT-00114 Customer Support Team monitor provisional approval 451,072 KRW under review, settlement expected day 18.
- RECORD FR-01612 [decision-critical] (operational/pending_intent, day 12, by fin-tyo.a2; DB shows n/a): CMT-00120 Customer Support Team travel advance provisional approval 666,274 KRW under review, settlement expected day 19.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Customer Support Team AND status IN ['reviewing', 'pending'] → ["CMT-00114", "CMT-00120"]
**need IT-SEL/rule/seat_price** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_price: {"id": "IT-SEL.seat_price", "group": "IT-SEL", "title": "Standard seat price", "params": {"price": 256164}, "text": "When there is no supplier price, one seat costs 256,164 KRW."}
### Model answer and official verdict
answer: {"alloc": [5, 1, 4], "buy": 10, "transfer": 0, "unmet": 0}
official exact match: 0 (1/4 slots)

## CASE 46: qwen3.5-27b · full_load · s12 · W-00005 · class D · day 1 · template alloc
### Task as given to the requester
Allocate CAD seats to Dev Team 1, Customer Support Team, Sales Team 2 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- alloc: List of integers: seats given to each team, in the team order of the request.
- transfer: Seats pulled from the other region.
- buy: Seats purchased.
- unmet: Total seats still missing after allocation.
- Public region list, in order: SEL, TYO.
### Gold answer
{"alloc": [2, 1, 2], "transfer": 1, "buy": 4, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [3, 1, 2], "transfer": 1, "buy": 5, "unmet": 0}, "partial": {"alloc": [3, 1, 2], "transfer": 1, "buy": 5, "unmet": 0}, "neardup": {"alloc": [7, 1, 2], "transfer": 1, "buy": 9, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/license/CAD** (group IT-SEL, class None, local=True)
- RECORD FR-00874 (db_pending/observation, day -1, by it-sel.a4; DB shows 5): CAD seats In use 27/27 seats. Stored value: {"seats":27,"used":27}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00618 (operational/pending_intent, day -8, by it-sel.a4; DB shows n/a): CAD seats 3 seats reserved for Sales Team 2 project until day 2.
- RECORD FR-00819 (operational/pending_intent, day -3, by it-sel.a5; DB shows n/a): CAD seats 2 seats reserved for Customer Support Team onboarding until day 5.
- RECORD FR-00844 (operational/pending_intent, day -2, by it-sel.a4; DB shows n/a): CAD seats 3 seats reserved for Sales Team 2 project until day 4.
**need HR-SEL/Dev Team 1/planning_headcount** (group HR-SEL, class A, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1000/profile` v2 (recorded day -19, registered day -18): {"dept": "Dev Team 1", "grade": 2, "contract": "regular", "hire_day": -196, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1006/profile` v2 (recorded day -10, registered day -7): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -531, "status": "active"}
- RECORD FR-00616 [decision-critical] (operational/pending_intent, day -8, by hr-sel.a1; DB shows n/a): Transfer of Bong Seoha approved from Dev Team 1 to Sales Team 2, effective day 3 (stays in Dev Team 1 until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Dev Team 1 AND status=active) → 3
**need HR-SEL/Customer Support Team/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1002/profile` v2 (recorded day -9, registered day -7): {"dept": "Customer Support Team", "grade": 4, "contract": "regular", "hire_day": -454, "status": "active"}
- RECORD FR-00893 [decision-critical] (operational/pending_intent, day 0, by hr-sel.a5; DB shows n/a): Transfer of Lee Seojun approved from Customer Support Team to Dev Team 2, effective day 6 (stays in Customer Support Team until then).
- DB `HR-SEL/emp/E-SEL-1007/profile` v3 (recorded day -6, registered day -3): {"dept": "Customer Support Team", "grade": 5, "contract": "contractor", "hire_day": -550, "status": "exited"}
- RECORD FR-00935 [decision-critical] (db_pending/observation, day 1, by hr-sel.a5; DB shows 2): HR record of Jang Woojin moved from Customer Support Team to Sales Team 1, grade 5, regular. Stored value: {"contract":"regular","dept":"Sales Team 1","grade":5,"hire_day":-861,"status":"active"}
- DB `HR-SEL/emp/E-SEL-1011/profile` v2 (recorded day -13, registered day -10): {"dept": "Customer Support Team", "grade": 4, "contract": "regular", "hire_day": -511, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1012/profile` v3 (recorded day -5, registered day -3): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -486, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1013/profile` v2 (recorded day -3, registered day 0): {"dept": "Dev Team 2", "grade": 1, "contract": "regular", "hire_day": -372, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1016/profile` v3 (recorded day -3, registered day -2): {"dept": "Customer Support Team", "grade": 1, "contract": "contractor", "hire_day": -702, "status": "active"}
- QUERY COUNT(emp WHERE region=SEL AND dept=Customer Support Team AND status=active) → 2
**need HR-SEL/Sales Team 2/planning_headcount** (group HR-SEL, class C, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1006/profile` v2 (recorded day -10, registered day -7): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -531, "status": "active"}
- RECORD FR-00894 (db_pending/rationale, day 0, by hr-sel.a3; DB shows 2): HR record of Lim Hajun changed to grade 3 (review result), Sales Team 2. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":3,"hire_day":-648,"status":"active"}
- RECORD FR-00762 [decision-critical] (operational/pending_intent, day -4, by hr-sel.a5; DB shows n/a): Transfer of Lim Hajun approved from Sales Team 2 to Dev Team 2, effective day 7 (stays in Sales Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1012/profile` v3 (recorded day -5, registered day -3): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -486, "status": "active"}
- RECORD FR-00748 [decision-critical] (operational/pending_intent, day -4, by hr-sel.a4; DB shows n/a): Transfer of Cho Eunho approved from Sales Team 2 to Dev Team 2, effective day 5 (stays in Sales Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1014/profile` v2 (recorded day -9, registered day -6): {"dept": "Sales Team 1", "grade": 3, "contract": "regular", "hire_day": -385, "status": "active"}
- RECORD FR-00596 [decision-critical] (operational/pending_intent, day -9, by hr-sel.a5; DB shows n/a): Transfer of Hwang Taeo approved from Sales Team 2 to Sales Team 1, effective day 2 (stays in Sales Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1018/profile` v2 (recorded day -16, registered day -15): {"dept": "Sales Team 2", "grade": 5, "contract": "regular", "hire_day": -640, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-2001/profile` v2 (recorded day -12, registered day -9): {"dept": "Marketing Team", "grade": 3, "contract": "contractor", "hire_day": -18, "status": "active"}
- RECORD FR-00691 [decision-critical] (operational/pending_intent, day -6, by hr-sel.a5; DB shows n/a): Transfer of Pyo Jisung approved from Sales Team 2 to Sales Team 1, effective day 2 (stays in Sales Team 2 until then).
- RECORD FR-00616 [decision-critical] (operational/pending_intent, day -8, by hr-sel.a1; DB shows n/a): Transfer of Bong Seoha approved from Dev Team 1 to Sales Team 2, effective day 3 (stays in Dev Team 1 until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Sales Team 2 AND status=active) → 5
**need IT-TYO/license/CAD** (group IT-TYO, class D, local=False)
- DB `IT-TYO/lic/CAD/seats` v2 (recorded day -18, registered day -16): {"seats": 31, "used": 25}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00621 [decision-critical] (operational/pending_intent, day -8, by it-tyo.w00079; DB shows n/a): CAD seats 2 seats reserved for Sales Section 1 onboarding until day 6.
- RECORD FR-00845 [decision-critical] (operational/pending_intent, day -2, by it-tyo.w00122; DB shows n/a): CAD seats 2 seats reserved for Planning Section project until day 10.
**need IT-SEL/rule/seat_transfer_share** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_transfer_share: {"id": "IT-SEL.seat_transfer_share", "group": "IT-SEL", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-SEL/rule/seat_purchase_line** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.seat_purchase_line: {"id": "FIN-SEL.seat_purchase_line", "group": "FIN-SEL", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-SEL/Dev Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 1/remaining` v2 (recorded day -4, registered day -1): 4492968
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00543 (operational/pending_intent, day -11, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 292,165 KRW earmarked for new-hire equipment until day 3 (no voucher yet).
- RECORD FR-00634 (operational/pending_intent, day -8, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 486,491 KRW earmarked for meeting room replacement until day 4 (no voucher yet).
- RECORD FR-00855 (operational/pending_intent, day -2, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 170,723 KRW earmarked for training equipment until day 7 (no voucher yet).
- RECORD FR-00877 (operational/pending_intent, day -1, by fin-sel.a4; DB shows n/a): Dev Team 1 capex 512,677 KRW earmarked for new-hire equipment until day 13 (no voucher yet).
- RECORD FR-00900 (db_pending/observation, day 0, by fin-sel.a3; DB shows 1): CMT-00017 Dev Team 1 provisional approval settled. Stored value: {"amount":401082,"expected_settle":0,"status":"settled"}
- RECORD FR-00901 (db_pending/observation, day 0, by fin-sel.a5; DB shows 1): CMT-00021 Dev Team 1 provisional approval settled. Stored value: {"amount":385564,"expected_settle":0,"status":"settled"}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00543", "earmark:FR-00634", "earmark:FR-00855", "earmark:FR-00877"]
**need IT-SEL/rule/seat_price** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_price: {"id": "IT-SEL.seat_price", "group": "IT-SEL", "title": "Standard seat price", "params": {"price": 166914}, "text": "When there is no supplier price, one seat costs 166,914 KRW."}
### Model answer and official verdict
answer: {"alloc": [2, 1, 3], "buy": 6, "transfer": 0, "unmet": 0}
official exact match: 0 (1/4 slots)

## CASE 47: qwen3.5-27b · full_load · s14 · W-00137 · class D · day 14 · template purchase
### Task as given to the requester
For Seojun (Assistant Manager)'s laptop request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "vendor_excluded"}
### Counterfactual answers (generator)
{"stale": {"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "budget"}, "partial": {"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "lead_time"}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1002/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1002"}
- DB `HR-SEL/emp/E-SEL-1002/profile` v3 (recorded day -2, registered day -1): {"dept": "Dev Team 1", "grade": 5, "contract": "contractor", "hire_day": -382, "status": "active"}
**need FIN-SEL/Dev Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 1/remaining` v3 (recorded day 11, registered day 13): 3974551
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-SEL/commit/CMT-00014/status` v2 (recorded day -5, registered day -4): {"status": "settled", "amount": 817861, "expected_settle": -5}
- DB `FIN-SEL/commit/CMT-00029/status` v2 (recorded day -7, registered day -5): {"status": "settled", "amount": 236917, "expected_settle": -7}
- RECORD FR-01655 (db_pending/observation, day 13, by fin-sel.a3; DB shows 1): CMT-00086 Dev Team 1 provisional approval settled. Stored value: {"amount":1093577,"expected_settle":13,"status":"settled"}
- RECORD FR-01604 (db_pending/observation, day 12, by fin-sel.a2; DB shows ABSENT): CMT-00106 Dev Team 1 provisional approval 608,564 KRW confirmed, settlement expected day 17. Stored value: {"amount":608564,"expected_settle":17,"status":"pending"}
- RECORD FR-01521 (operational/pending_intent, day 10, by fin-sel.a2; DB shows n/a): CMT-00116 Dev Team 1 monitor provisional approval 779,720 KRW under review, settlement expected day 18.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 1 AND status IN ['reviewing', 'pending'] → ["CMT-00105", "CMT-00106", "CMT-00109", "CMT-00116"]
**need IT-SEL/eligibility/E-SEL-1002** (group IT-SEL, class None, local=True)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need PROC-SEL/quotes/laptop** (group PROC-SEL, class D, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01275 [decision-critical] (operational/handover, day 6, by proc-sel.w00193; DB shows n/a): Supplier V-SEL-0 exclude from comparisons until day 16 due to a quality issue.
- RECORD FR-01420 (operational/handover, day 8, by proc-sel.w00221; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 21 due to a quality issue.
- RECORD FR-01082 (operational/observation, day 2, by proc-sel.w00155; DB shows n/a): Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01168 (operational/observation, day 4, by proc-sel.w00172; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 4 days until day 16.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01688 (operational/observation, day 13, by proc-sel.w00267; DB shows n/a): Supplier V-SEL-0 delivery notified: deliveries delayed by 3 days until day 25.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v3 (recorded day 13, registered day 14): 6
- RECORD FR-01632 (db_pending/rationale, day 12, by proc-sel.w00257; DB shows 2): V-SEL-0 laptop (basic) quote Q-V-SEL-0-LTB changed to 458,670 KRW (raw material prices). Stored value: 458670
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v3 (recorded day 13, registered day 14): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTP/amount` v1 (recorded day -20, registered day -20): 2113187
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v3 (recorded day 13, registered day 14): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTS/amount` v3 (recorded day 11, registered day 12): 1478160
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- RECORD FR-01702 (db_pending/observation, day 14, by proc-sel.w00271; DB shows 3): Supplier V-SEL-1 lead time change notice applied. Stored value: 4
- DB `PROC-SEL/quote/Q-V-SEL-1-LTS/amount` v1 (recorded day -20, registered day -20): 1452400
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-LTB/amount` v1 (recorded day -20, registered day -20): 489150
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-LTP/amount` v2 (recorded day 6, registered day 8): 1908409
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-LTS/amount` v1 (recorded day -20, registered day -20): 1259460
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v5 (recorded day 6, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTB/amount` v4 (recorded day 12, registered day 13): 844801
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v5 (recorded day 6, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTP/amount` v1 (recorded day -20, registered day -20): 2367972
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v5 (recorded day 6, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTS/amount` v2 (recorded day -1, registered day 2): 1379255
**need LEGAL-SEL/residency** (group LEGAL-SEL, class A, local=False)
- RULE LEGAL-SEL.residency: {"id": "LEGAL-SEL.residency", "group": "LEGAL-SEL", "title": "Data residency", "params": {"restricted_depts": ["Sales Team 1", "Sales Team 2"]}, "text": "These departments may not use equipment from offshore suppliers: Sales Team 1, Sales Team 2."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 1415531, "decision": "assign", "nda": false, "option": "INV-SEL-LTB"}
official exact match: 0 (0/6 slots)

## CASE 48: qwen3.5-27b · full_load · s13 · W-00137 · class D · day 14 · template temporal
### Task as given to the requester
Equipment for Haram (Manager) at 1,951,921 KRW: taking personnel changes into account, which department's budget can pay for it and from which day?
[Request scope] item=laptop; search window=today through 20 days later (inclusive); procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- budget_dept: Department whose budget pays on the earliest feasible day (the department the employee belongs to on that day); null if no day in the search window works.
- earliest_day: First day in the stated search window on which the expense can be made; null if none.
- Public region list, in order: SEL, TYO.
### Gold answer
{"budget_dept": "Sales Team 1", "earliest_day": 17}
### Counterfactual answers (generator)
{"stale": {"budget_dept": "Sales Team 1", "earliest_day": 14}, "partial": {"budget_dept": "Sales Team 1", "earliest_day": 14}, "neardup": {"budget_dept": "Customer Support Team", "earliest_day": 22}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-2017/assignment_timeline** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2017"}
- DB `HR-SEL/emp/E-SEL-2017/profile` v1 (recorded day 10, registered day 13): {"dept": "Sales Team 1", "grade": 2, "contract": "contractor", "hire_day": 10, "status": "active"}
- RULE HR-SEL.transfer_effective_day: {"id": "HR-SEL.transfer_effective_day", "group": "HR-SEL", "title": "Transfer effective day", "params": {"inclusive": true}, "text": "An employee belongs to the new department from the transfer's effective day itself."}
- RECORD FR-01539 (operational/pending_intent, day 11, by hr-sel.a5; DB shows n/a): Transfer of Byun Haram approved from Sales Team 1 to Sales Team 2, effective day 18 (stays in Sales Team 1 until then).
**need FIN-SEL/Sales Team 1/budget_schedule** (group FIN-SEL, class D, local=False)
- RECORD FR-01737 [decision-critical] (db_pending/rationale, day 14, by fin-sel.a1; DB shows 6): Sales Team 1 capex balance adjusted to 1,993,140 KRW (quarter carry-over). Stored value: 1993140
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01224 [decision-critical] (operational/pending_intent, day 5, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 369,909 KRW earmarked for training equipment until day 16 (no voucher yet).
- RECORD FR-01260 [decision-critical] (operational/pending_intent, day 6, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 162,433 KRW earmarked for meeting room replacement until day 19 (no voucher yet).
- RECORD FR-01615 [decision-critical] (operational/pending_intent, day 12, by fin-sel.a1; DB shows n/a): Sales Team 1 capex 432,093 KRW earmarked for new-hire equipment until day 20 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00006/status` v2 (recorded day -12, registered day -9): {"status": "settled", "amount": 795461, "expected_settle": -12}
- DB `FIN-SEL/commit/CMT-00015/status` v2 (recorded day -8, registered day -6): {"status": "settled", "amount": 599076, "expected_settle": -8}
- DB `FIN-SEL/commit/CMT-00020/status` v2 (recorded day -1, registered day 0): {"status": "settled", "amount": 967831, "expected_settle": -1}
- DB `FIN-SEL/commit/CMT-00022/status` v2 (recorded day -7, registered day -6): {"status": "settled", "amount": 274002, "expected_settle": -7}
- DB `FIN-SEL/commit/CMT-00031/status` v2 (recorded day -1, registered day 2): {"status": "settled", "amount": 771458, "expected_settle": -1}
- DB `FIN-SEL/commit/CMT-00033/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 202746, "expected_settle": -4}
- DB `FIN-SEL/commit/CMT-00039/status` v2 (recorded day 5, registered day 7): {"status": "settled", "amount": 548951, "expected_settle": 5}
- DB `FIN-SEL/commit/CMT-00042/status` v2 (recorded day 8, registered day 10): {"status": "settled", "amount": 785966, "expected_settle": 8}
- RECORD FR-01573 [decision-critical] (operational/pending_intent, day 12, by fin-sel.a3; DB shows n/a): CMT-00104 Sales Team 1 travel advance provisional approval 691,367 KRW under review, settlement expected day 26.
- RECORD FR-01616 [decision-critical] (operational/pending_intent, day 12, by fin-sel.a3; DB shows n/a): CMT-00108 Sales Team 1 laptop provisional approval 268,660 KRW under review, settlement expected day 26.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-01224", "earmark:FR-01260", "earmark:FR-01615", "CMT-00104", "CMT-00108"]
**need FIN-SEL/Sales Team 1/next_reset** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.reset_calendar: {"id": "FIN-SEL.reset_calendar", "group": "FIN-SEL", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-SEL/line/Sales Team 1/base` v1 (recorded day -20, registered day -20): 3806034
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-01347 (operational/exception, day 7, by fin-sel.n0005; DB shows n/a): Sales Team 2 capex executing office agreed that TYO finance executes it until day 28.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Sales Team 2/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Sales Team 2/remaining` v2 (recorded day 7, registered day 10): 3159648
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00026/status` v2 (recorded day 3, registered day 4): {"status": "settled", "amount": 839113, "expected_settle": 3}
- DB `FIN-TYO/commit/CMT-00028/status` v2 (recorded day 4, registered day 5): {"status": "settled", "amount": 959706, "expected_settle": 4}
- DB `FIN-TYO/commit/CMT-00044/status` v2 (recorded day 4, registered day 7): {"status": "settled", "amount": 386882, "expected_settle": 4}
- RECORD FR-01713 (db_pending/observation, day 14, by fin-tyo.n0013; DB shows ABSENT): CMT-00095 Sales Team 2 provisional approval 784,781 KRW confirmed, settlement expected day 22. Stored value: {"amount":784781,"expected_settle":22,"status":"pending"}
- RECORD FR-01483 (operational/pending_intent, day 10, by fin-tyo.n0013; DB shows n/a): CMT-00096 Sales Team 2 order (incl. shipping) provisional approval (order of W-00083) 617,018 KRW under review, settlement expected day 14.
- RECORD FR-01717 (db_pending/observation, day 14, by fin-tyo.n0013; DB shows ABSENT): CMT-00107 Sales Team 2 provisional approval 781,283 KRW confirmed, settlement expected day 25. Stored value: {"amount":781283,"expected_settle":25,"status":"pending"}
- RECORD FR-01732 (operational/pending_intent, day 14, by fin-tyo.a4; DB shows n/a): CMT-00116 Sales Team 2 order (incl. shipping) provisional approval (order of W-00121) 775,260 KRW under review, settlement expected day 26.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00095", "CMT-00096", "CMT-00107", "CMT-00116"]
**need FIN-TYO/Sales Team 2/next_reset** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.reset_calendar: {"id": "FIN-TYO.reset_calendar", "group": "FIN-TYO", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-TYO/line/Sales Team 2/base` v2 (recorded day 7, registered day 9): 2683779
**need PROC-SEL/quotes/laptop** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01202 (operational/observation, day 5, by proc-sel.w00176; DB shows n/a): Supplier V-SEL-0 delivery notified: deliveries delayed by 5 days until day 17.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01230 (operational/observation, day 5, by proc-sel.w00180; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 5 days until day 19.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01563 (operational/observation, day 11, by proc-sel.w00250; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 2 days until day 19.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v1 (recorded day -20, registered day -20): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTB/amount` v1 (recorded day -20, registered day -20): 480948
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v1 (recorded day -20, registered day -20): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTP/amount` v2 (recorded day -11, registered day -8): 1873105
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v1 (recorded day -20, registered day -20): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTS/amount` v2 (recorded day -4, registered day -3): 1544257
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day 8, registered day 9): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-LTB/amount` v3 (recorded day -16, registered day -15): 589357
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day 8, registered day 9): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-LTP/amount` v3 (recorded day 3, registered day 5): 2388059
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day 8, registered day 9): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-LTS/amount` v4 (recorded day 7, registered day 9): 1199879
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v3 (recorded day 7, registered day 9): 5
- DB `PROC-SEL/quote/Q-V-SEL-2-LTP/amount` v1 (recorded day -20, registered day -20): 2252407
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v3 (recorded day 7, registered day 9): 5
- DB `PROC-SEL/quote/Q-V-SEL-2-LTS/amount` v1 (recorded day -20, registered day -20): 1191288
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v3 (recorded day 4, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTB/amount` v1 (recorded day -20, registered day -20): 814884
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v3 (recorded day 4, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTP/amount` v1 (recorded day -20, registered day -20): 1872838
### Model answer and official verdict
answer: {"budget_dept": "Sales Team 1", "earliest_day": 16}
official exact match: 0 (1/2 slots)

## CASE 49: deepseek-v4-flash · direct · s13 · W-00008 · class A · day 1 · template diag
### Task as given to the requester
Invoice INV-50118 (497,762 KRW, beneficiary Fujita-san, asset A-TYO-50248, provisional approval CMT-00035) does not match. Find the cause.
[Request scope] target supplier=V-TYO-0; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"stale": null, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00035/status** (group FIN-TYO, class A, local=False)
- CATALOG: {"group": "FIN-TYO", "key": "commits/CMT-00035"}
- DB `FIN-TYO/commit/CMT-00035/status` v1 (recorded day -1, registered day 1): {"status": "pending", "amount": 497762, "expected_settle": 3}
**need HR-TYO/E-TYO-2008/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2008"}
- DB `HR-TYO/emp/E-TYO-2008/profile` v1 (recorded day -1, registered day 1): {"dept": "Sales Section 1", "grade": 3, "contract": "contractor", "hire_day": -1, "status": "active"}
**need IT-TYO/E-TYO-2008/assets** (group IT-TYO, class None, local=True)
- QUERY SELECT asset WHERE holder=E-TYO-2008 → []
**need PROC-TYO/receipt/CMT-00035** (group PROC-TYO, class A, local=False)
- RECORD FR-00972 (db_pending/observation, day 1, by proc-tyo.n0012; DB shows ABSENT): Goods of CMT-00035 receipt confirmed. Stored value: true
**need PROC-TYO/vendor/V-TYO-0/status** (group PROC-TYO, class A, local=False)
- NEGATIVE: {"query": "PROC-TYO exclusion order for supplier V-TYO-0", "result": []}
**need LEGAL-TYO/E-TYO-2008/contract** (group LEGAL-TYO, class A, local=False)
- RECORD FR-00966 (db_pending/observation, day 1, by legal-tyo.a1; DB shows ABSENT): Contract of Fujita Riku allowed tier basic, expires day 120, NDA yes. Stored value: {"allowed_tier":"basic","expiry":120,"nda":true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
**need FIN-TYO/rule/invoice_match_precedence** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.invoice_match_precedence: {"id": "FIN-TYO.invoice_match_precedence", "group": "FIN-TYO", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "AMOUNT_MISMATCH"}
official exact match: 0 (0/1 slots)

## CASE 50: deepseek-v4-flash · direct · s13 · W-00057 · class A · day 6 · template plan
### Task as given to the requester
List, in order, the approvals needed before proceeding with a monitor (standard) at 1,142,377 KRW for Eunho (Manager).
[Request scope] item=monitor; target supplier=V-SEL-1; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- steps: Ordered list of required approval steps, from: IT_EXCEPTION, LEGAL_NDA, LEGAL_OVERRIDE, BLOCKED_CONTRACT, FIN_TEAM_LEAD, FIN_DIVISION_HEAD, FIN_CFO, PROC_VENDOR_ONBOARD. Order: IT step, then legal step, then finance step, then procurement step. If the contract forbids the item, the list is exactly ["BLOCKED_CONTRACT"].
- Public region list, in order: SEL, TYO.
### Gold answer
{"steps": ["FIN_DIVISION_HEAD"]}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1012/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1012"}
- RECORD FR-01259 (db_pending/rationale, day 6, by hr-sel.n0006; DB shows 3): HR record of Cho Eunho changed to grade 5 (review result), Customer Support Team. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":5,"hire_day":-64,"status":"active"}
**need IT-SEL/eligibility/E-SEL-1012** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
- RECORD FR-01199 (operational/exception, day 5, by fin-sel.n0005; DB shows n/a): Customer Support Team new equipment spending control items above 800,000 KRW need division head approval until day 24.
- RULE FIN-SEL.q_exception_approver: {"id": "FIN-SEL.q_exception_approver", "group": "FIN-SEL", "title": "Quarterly spending control", "params": {"approver": "division_head"}, "text": "For a department under a quarterly spending control, items above the threshold need division_head approval."}
**need PROC-SEL/vendor/V-SEL-1/registration** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.vendor_onboarding: {"id": "PROC-SEL.vendor_onboarding", "group": "PROC-SEL", "title": "Supplier registration", "params": {"unregistered_step": "PROC_VENDOR_ONBOARD"}, "text": "Trading with an unregistered supplier first requires the supplier registration step."}
- DB `PROC-SEL/vendor/V-SEL-1/registered` v1 (recorded day -20, registered day -20): true
### Model answer and official verdict
answer: {"steps": ["FIN_DIVISION_HEAD"]}
official exact match: 1 (1/1 slots)

## CASE 51: deepseek-v4-flash · direct · s12 · W-00039 · class A · day 4 · template diag
### Task as given to the requester
Invoice INV-27850 (1,219,342 KRW, beneficiary Ikeda-san, asset A-TYO-7883, provisional approval CMT-00076) does not match. Find the cause.
[Request scope] target supplier=V-TYO-3; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"stale": null, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00076/status** (group FIN-TYO, class A, local=False)
- NEGATIVE: {"query": "FIN-TYO catalog commits/CMT-00076", "result": []}
- RECORD FR-01116 (operational/pending_intent, day 4, by fin-tyo.a3; DB shows n/a): CMT-00076 Sales Team 1 workstation (incl. shipping) provisional approval (order of W-00028) 1,219,342 KRW under review, settlement expected day 17.
**need HR-TYO/E-TYO-2005/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2005"}
- DB `HR-TYO/emp/E-TYO-2005/profile` v2 (recorded day 1, registered day 3): {"dept": "Sales Section 2", "grade": 1, "contract": "contractor", "hire_day": -12, "status": "active"}
**need IT-TYO/E-TYO-2005/assets** (group IT-TYO, class None, local=True)
- QUERY SELECT asset WHERE holder=E-TYO-2005 → []
**need PROC-TYO/receipt/CMT-00076** (group PROC-TYO, class A, local=False)
- QUERY {"key": "PROC-TYO/receipt/CMT-00076/received", "asof": 4} → "ABSENT"
**need PROC-TYO/vendor/V-TYO-3/status** (group PROC-TYO, class A, local=False)
- NEGATIVE: {"query": "PROC-TYO exclusion order for supplier V-TYO-3", "result": []}
**need LEGAL-TYO/E-TYO-2005/contract** (group LEGAL-TYO, class A, local=False)
- DB `LEGAL-TYO/contract/E-TYO-2005/terms` v2 (recorded day -4, registered day -1): {"allowed_tier": "basic", "expiry": 74, "nda": false}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01040 (operational/exception, day 2, by legal-tyo.a3; DB shows n/a): Equipment exception of Ikeda Hikaru higher tiers including premium allowed until day 18 for a project, legal check done.
**need FIN-TYO/rule/invoice_match_precedence** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.invoice_match_precedence: {"id": "FIN-TYO.invoice_match_precedence", "group": "FIN-TYO", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "COMMIT_NOT_CONFIRMED"}
official exact match: 0 (0/1 slots)

## CASE 52: deepseek-v4-flash · direct · s12 · W-00121 · class B · day 13 · template conflict
### Task as given to the requester
Check whether the provisional approval raised for W-00080 is still live and what amount to count for it.
[Request scope] procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- status: Effective status of the provisional approval: 'reviewing', 'pending', 'settled', 'cancelled', or 'none' if no authoritative record exists.
- amount: Amount to count for it: the approval amount while it is 'reviewing' or 'pending', otherwise 0.
- Public region list, in order: SEL, TYO.
### Gold answer
{"status": "reviewing", "amount": 545037}
### Counterfactual answers (generator)
{"stale": null, "partial": {"status": "none", "amount": 0}, "neardup": {"status": "reviewing", "amount": 403642}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/task/W-00080/result** (group HR-TYO, class None, local=True)
- RECORD FR-01358 (operational/task_result, day 8, by hr-tyo.a1; DB shows n/a): W-00080 item result: decision=order, option=Q-V-TYO-1-LTB, approver=team_lead, nda=False, budget_after=1508400
**need FIN-TYO/CMT-00093/effective_status** (group FIN-TYO, class B, local=False)
- NEGATIVE: {"query": "FIN-TYO catalog commits/CMT-00093", "result": []}
- RECORD FR-01391 [decision-critical] (operational/pending_intent, day 9, by fin-tyo.a1; DB shows n/a): CMT-00093 Sales Section 1 laptop (incl. shipping) provisional approval (order of W-00080) 545,037 KRW under review, settlement expected day 13.
- RULE FIN-TYO.status_authority: {"id": "FIN-TYO.status_authority", "group": "FIN-TYO", "title": "Validity of provisional approval status", "params": {"authoritative": ["db", "owner_record"], "informal_excluded": true}, "text": "Only the registered record and the handling officer's processing record determine a provisional approval's status. Informal remarks or discussions do not change it."}
- RECORD FR-01392 (operational/observation, day 9, by fin-tyo.a4; DB shows n/a): CMT-00093 item someone suggested cancelling it (not decided).
### Model answer and official verdict
answer: {"amount": 545037, "status": "reviewing"}
official exact match: 1 (2/2 slots)
### MATCHER CHECK FR-01391 (need FIN-TYO/CMT-00093/effective_status): matcher says **delivered**
record text: CMT-00093 Sales Section 1 laptop (incl. shipping) provisional approval (order of W-00080) 545,037 KRW under review, settlement expected day 13.
What the requester received from FIN-TYO during this task:
```
W-00080 is not found in my area's records or database. Task IDs are not stored in my area; they appear only in tasks themselves. I cannot find any provisional approval related to W-00080.
missing: W-00080 — no record of this task ID exists in my area's records or database; no provisional approval (CMT-...) related to W-00080 can be found in my area
---
Neither Q-V-TYO-1-LTB nor E-TYO-1003 exist in my area's database or records. I have no provisional approvals or any other records related to either entity.
- Q-V-TYO-1-LTB | catalog_entry | NOT_FOUND |  | db, day unknown: D1
- E-TYO-1003 | catalog_entry | NOT_FOUND |  | db, day unknown: D2
missing: Q-V-TYO-1-LTB — no catalog_entry, no provisional_approval, or any other record found in my area's database or records; E-TYO-1003 — no catalog_entry, no provisional_approval, or any other record found in my area's database or records; Any provisional approval (CMT-...) related to quote Q-V-TYO-1-LTB — none found in my area; Any provisional approval (CMT-...) related to employee E-TYO-1003 (Takahashi Misaki) — none found in my area
---
Employee E-TYO-1003 (Takahashi Misaki) does not exist in my area's database or records. Sales Section 1 has 6 provisional approvals (CMT-00019, CMT-00023, CMT-00028, CMT-00034, CMT-00081, CMT-00082). Only CMT-00023 was for a laptop, but it was cancelled (registered day -8). None of these are linked to E-TYO-1003 in my records.
- E-TYO-1003 | catalog_entry | NOT_FOUND |  | db, day unknown: D1
- Sales Section 1 | department_provisional_approvals | CMT-00019, CMT-00023, CMT-00028, CMT-00034, CMT-00081, CMT-00082 |  | db, day unknown: D2
- CMT-00023 | item | laptop | cancelled | db, day fixed: D6
- CMT-00023 | amount | 677407 | cancelled | db, day -8: D2
- CMT-00023 | expected settlement day | -5 | cancelled | db, day -8: D2
- CMT-00023 | registered day | -8 | cancelled | db, day -8: D2
- CMT-00023 | department | Sales Section 1 | cancelled | db, day fixed: D6
- CMT-00019 | item | meeting room equipment | settled | db, day fixed: D5
- CMT-00028 | item | workstation | settled | db, day fixed: D7
- CMT-00034 | item | travel advance | cancelled | db, day fixed: D8
- CMT-00081 | item | meeting room equipment | settled | db, day fixed: D3
- CMT-00082 | item | order (incl. shipping) | pending | db, day fixed: D4
- CMT-00082 | status (my record day 12) | settled |  | history, day 12: H373
missing: E-TYO-1003 (Takahashi Misaki) — no record of this employee exists in my area's database or records; no provisional approval linked to this employee; Any provisional approval related to a laptop purchase for E-TYO-1003 — none found
---
As of today (day 13), the database shows CMT-00082 as pending (registered day 9), but my own settlement record from day 12 shows it was settled. The later record (day 12) takes precedence, so its current status is settled. Amount is 918,151 KRW. It belongs to Sales Section 1 for an order including shipping, linked to work W-00031. No quote or employee link exists in my area's records, and it was not raised for W-00080.
- CMT-00082 | status (database) | pending |  | db, day 9: D1
- CMT-00082 | status (my settlement record, day 12) | settled |  | history, day 12: H373
- CMT-00082 | amount | 918151 |  | db, day 9: D1
- CMT-00082 | expected settlement day | 12 |  | db, day 9: D1
- CMT-00082 | department | Sales Section 1 |  | db, day fixed: D2
- CMT-00082 | item | order (incl. shipping) |  | db, day fixed: D2
- CMT-00082 | work reference | W-00031 |  | db, day fixed: D2
missing: CMT-00082 — linked to any quote: no quote field in my area's records; CMT-00082 — linked to any employee: no employee field in my area's records; CMT-00082 — raised for W-00080: the catalog entry references W-00031, not W-00080
---
My records show CMT-00093 as a provisional approval for Sales Section 1 laptop (incl. shipping) linked to W-00080, amount 545,037 KRW, status under review (from my day 9 processing record). However, the database does not have a registered provisional approval for CMT-00093. Quote Q-V-TYO-1-LTB is not found in my area's catalog.
- CMT-00093 | provisional approval for Sales Section 1 laptop (incl. shipping) | 545037 | under review | history, day 9: H596
- CMT-00093 | related task/order | W-00080 |  | history, day 9: H596
- CMT-00093 | department | Sales Section 1 |  | history, day 9: H596
- Q-V-TYO-1-LTB | catalog entry | NOT_FOUND |  | db, day unknown: D2
missing: Whether CMT-00093 is the same as 'a provisional approval raised for W-00080' — my records show CMT-00093 is described as '(order of W-00080)' but the database has no registered provisional approval with ID CMT-00093; the record in my history (H596) shows it as under review.; Quote Q-V-TYO-1-LTB — no catalog entry exists in my area's records for this quote.
---
CMT-00093 does not exist in any of my area's records (provisional_approval, catalog_entry, or department_provisional_approvals for Sales Section 1). I have no information about its status, amount, or any relation to W-00080.
- CMT-00093 | provisional_approval | NOT_FOUND |  | db, day unknown: D1
- CMT-00093 | catalog_entry | NOT_FOUND |  | db, day unknown: D2
- Sales Section 1 | department_provisional_approvals | CMT-00093 not listed |  | db, day unknown: D3
missing: CMT-00093 — provisional_approval: not found in my area's database or records; CMT-00093 — catalog_entry: not found in my area's database or records; CMT-00093 — status: not found; CMT-00093 — amount: not found
---
As of today (day 13), my most recent record on CMT-00093 is from day 9, when it was noted as 'under review' with amount 545,037 KRW and expected settlement day 13. The database has no registered provisional approval or catalog entry for CMT-00093, and it does not appear in Sales Section 1's list of registered provisional approvals. I have no newer records indicating it has been settled, cancelled, or otherwise changed since day 9.
- CMT-00093 | status (from processing record, day 9) | under review | under review | history, day 9: H596
- CMT-00093 | amount | 545037 |  | history, day 9: H596
- CMT-00093 | department | Sales Section 1 |  | history, day 9: H596
- CMT-00093 | item | laptop (incl. shipping) |  | history, day 9: H596
- CMT-00093 | linked order | W-00080 |  | history, day 9: H596
- CMT-00093 | expected settlement day | 13 |  | history, day 9: H596
- CMT-00093 | database provisional_approval record | NOT_FOUND |  | db, day unknown: D1
- CMT-00093 | database catalog_entry record | NOT_FOUND |  | db, day unknown: D2
- CMT-00093 | Sales Section 1 department_provisional_approvals | not listed |  | db, day unknown: D3
missing: Any more recent record of CMT-00093 after day 9 — none found in my history or database
---
- CMT-00093 | provisional approval status in database | not found |  | db, day unknown: D1
- CMT-00093 | catalog entry in database | not found |  | db, day unknown: D2
- CMT-00093 | Sales Section 1 department provisional approvals | not listed |  | db, day unknown: D3
- CMT-00093 | mention in personal task history | someone suggested cancelling it (not decided) |  | history, day 9: H116
missing: CMT-00093 settlement record; CMT-00093 cancellation record; CMT-00093 amount (545,037 KRW) not confirmed in my records; CMT-00093 department (Sales Section 1) not confirmed in my records; CMT-00093 item (laptop) not confirmed in my records; CMT-00093 relation to W-00080 not in my records
---
I have no records of provisional approval CMT-00093 in my area's database or history. It is not found as a standalone provisional approval, nor is it listed among Sales Section 1's registered provisional approvals.
- CMT-00093 | provisional approval record | NOT_FOUND |  | db, day unknown: D1
- Sales Section 1 | department provisional approvals | List does not include CMT-00093 |  | db, day unknown: D2
missing: CMT-00093 — no record of this provisional approval exists in my area's database or history; it is not listed among Sales Section 1's registered provisional approvals
---
As of day 13, CMT-00093 does not exist in my area's database or records. It has not been registered, settled, or cancelled — there is no record of it at all.
- CMT-00093 | provisional_approval | NOT_FOUND |  | db, day unknown: D1
- CMT-00093 | catalog_entry | NOT_FOUND |  | db, day unknown: D2
missing: CMT-00093 — no record exists in my area's database or records (no provisional_approval, no catalog_entry, no department_provisional_approvals listing)
```