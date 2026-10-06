## CASE 14: qwen3.5-27b · routing · s13 · W-00030 · class A · day 3 · template conflict
### Task as given to the requester
Check whether CMT-00043 is still live and what amount to count for it. We are hearing conflicting things.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"status": "pending", "amount": 892583}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"status": "reviewing", "amount": 536852}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/CMT-00043/effective_status** (group FIN-SEL, class A, local=False)
- CATALOG: {"group": "FIN-SEL", "key": "commits/CMT-00043"}
- DB `FIN-SEL/commit/CMT-00043/status` v1 (recorded day -1, registered day 2): {"status": "pending", "amount": 892583, "expected_settle": 5}
- RULE FIN-SEL.status_authority: {"id": "FIN-SEL.status_authority", "group": "FIN-SEL", "title": "Validity of provisional approval status", "params": {"authoritative": ["db", "owner_record"], "informal_excluded": true}, "text": "Only the registered record and the handling officer's processing record determine a provisional approval's status. Informal remarks or discussions do not change it."}
- RECORD FR-00796 (operational/observation, day -4, by fin-sel.a1; DB shows n/a): CMT-00043 item someone suggested cancelling it (not decided).
### Model answer and official verdict
answer: {"amount": 892583, "status": "pending"}
official exact match: 1 (2/2 slots)

## CASE 15: qwen3.5-27b · routing · s12 · W-00059 · class A · day 6 · template lookup
### Task as given to the requester
Check Ikeda-san's current department, grade and assets held.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- dept: Employee's current department.
- grade: Employee's current grade.
- assets: Asset IDs the employee currently holds (any order; empty list if none).
- Public region list, in order: SEL, TYO.
### Gold answer
{"dept": "Sales Section 2", "grade": 1, "assets": []}
### Counterfactual answers (generator)
{"stale": {"dept": "Sales Section 1", "grade": 1, "assets": []}, "partial": null, "neardup": {"dept": "Sales Section 2", "grade": 3, "assets": []}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2005/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2005"}
- DB `HR-TYO/emp/E-TYO-2005/profile` v2 (recorded day 1, registered day 3): {"dept": "Sales Section 2", "grade": 1, "contract": "contractor", "hire_day": -12, "status": "active"}
**need IT-TYO/E-TYO-2005/assets** (group IT-TYO, class A, local=False)
- QUERY SELECT asset WHERE holder=E-TYO-2005 → []
### Model answer and official verdict
answer: {"assets": [], "dept": "Sales Section 2", "grade": 1}
official exact match: 1 (3/3 slots)

## CASE 16: qwen3.5-27b · routing · s14 · W-00123 · class B · day 13 · template plan
### Task as given to the requester
List, in order, the approvals needed before proceeding with a laptop (standard) at 1,573,584 KRW for Chaewon (Manager).
[Request scope] item=laptop; target supplier=V-SEL-2; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"steps": ["IT_EXCEPTION", "FIN_DIVISION_HEAD"]}
### Counterfactual answers (generator)
{"stale": null, "partial": {"steps": ["IT_EXCEPTION", "LEGAL_NDA", "FIN_DIVISION_HEAD"]}, "neardup": {"steps": ["FIN_DIVISION_HEAD"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1007/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1007"}
- DB `HR-SEL/emp/E-SEL-1007/profile` v3 (recorded day -4, registered day -3): {"dept": "Dev Team 1", "grade": 2, "contract": "contractor", "hire_day": -177, "status": "active"}
**need IT-SEL/eligibility/E-SEL-1007** (group IT-SEL, class None, local=True)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-SEL/E-SEL-1007/contract** (group LEGAL-SEL, class B, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1007/terms` v3 (recorded day -10, registered day -7): {"allowed_tier": "standard", "expiry": 126, "nda": true}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00865 (operational/exception, day -3, by legal-sel.a4; DB shows n/a): Equipment exception of Yoon Chaewon higher tiers including premium allowed until day 17 for a project, legal check done.
- RECORD FR-00956 [decision-critical] (operational/observation, day -1, by legal-sel.n0007; DB shows n/a): NDA of Yoon Chaewon signed copy verified, NDA check step can be skipped until day 27.
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
**need PROC-SEL/vendor/V-SEL-2/registration** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.vendor_onboarding: {"id": "PROC-SEL.vendor_onboarding", "group": "PROC-SEL", "title": "Supplier registration", "params": {"unregistered_step": "PROC_VENDOR_ONBOARD"}, "text": "Trading with an unregistered supplier first requires the supplier registration step."}
- DB `PROC-SEL/vendor/V-SEL-2/registered` v1 (recorded day -20, registered day -20): true
### Model answer and official verdict
answer: {"steps": ["FIN_DIVISION_HEAD"]}
official exact match: 0 (0/1 slots)
### MATCHER CHECK FR-00956 (need LEGAL-SEL/E-SEL-1007/contract): matcher says **delivered**
record text: NDA of Yoon Chaewon signed copy verified, NDA check step can be skipped until day 27.
What the requester received from LEGAL-SEL during this task:
```
[Reply 1] (partial) E-SEL-1007's contract allows standard tier with NDA clause. No legal exception needed for standard tier purchase since it matches allowed_tier. NDA check required as verified NDA expired on day -2.
[Reply 2] (partial) E-SEL-1007 contract allows standard tier with nda=true. Since the requested standard laptop is within the allowed tier, no legal exception is needed per contractor_policy. NDA check may be required since nda=true, but cannot confirm if verified signed NDA copy exists to skip the check.
[Reply 3] (ok) E-SEL-1007 contract allows standard tier (matches requested standard laptop), so no legal exception needed. Contract has NDA clause but verified signed NDA exists valid until day 27, so NDA check step can be skipped. No additional approvals required beyond what's already covered by the contract terms and verified NDA.
- E-SEL-1007 | allowed_tier | standard |  | db, day -7: Reply 1: D1
- E-SEL-1007 | nda | true |  | db, day -7: Reply 1: D1
- E-SEL-1007 | expiry | 126 |  | db, day -7: Reply 1: D1
- contractor_policy | legal exception requirement | Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 1: contractor_policy
- contractor_policy | NDA check requirement | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: Reply 1: contractor_policy
- Yoon Chaewon | verified signed NDA copy | NDA of Yoon Chaewon signed copy verified, NDA check step can be skipped until day -2 | until day -2 | history, day -18: Reply 1: H10
- E-SEL-1007 | allowed_tier | standard |  | db, day -7: Reply 2: D1
- E-SEL-1007 | nda | true |  | db, day -7: Reply 2: D1
- E-SEL-1007 | expiry | 126 |  | db, day -7: Reply 2: D1
- contractor_policy | legal exception requirement | Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 2: contractor_policy
- contractor_policy | NDA check requirement | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: Reply 2: contractor_policy
- E-SEL-1007 | allowed_tier | standard |  | db, day -7: Reply 3: D1
- E-SEL-1007 | nda | true |  | db, day -7: Reply 3: D1
- E-SEL-1007 | expiry | 126 |  | db, day -7: Reply 3: D1
- Yoon Chaewon | verified signed NDA copy | NDA of Yoon Chaewon signed copy verified, NDA check step can be skipped until day 27 | until day 27 | history, day -1: Reply 3: H5
- contractor_policy | legal exception requirement | Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 3: contractor_policy
- contractor_policy | NDA check requirement | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: Reply 3: contractor_policy
missing: Whether E-SEL-1007 currently has any active legal exception recorded; verified signed NDA copy status for E-SEL-1007; whether E-SEL-1007 has any legal exception recorded
```

## CASE 17: qwen3.5-27b · routing · s13 · W-00026 · class B · day 3 · template budget
### Task as given to the requester
How much budget can Sales Section 2 actually spend right now, after all deductions?
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- available: Amount the department can actually spend today.
- n_deducted: Number of items (earmarks and provisional approvals) deducted in that figure.
- Public region list, in order: SEL, TYO.
### Gold answer
{"available": 3749879, "n_deducted": 0}
### Counterfactual answers (generator)
{"stale": null, "partial": {"available": 2406906, "n_deducted": 3}, "neardup": {"available": -1201567, "n_deducted": 4}, "wrong_owner": {"available": 2406906, "n_deducted": 3}}
### World facts behind the gold (by need)
**need FIN-TYO/Sales Section 2/budget_schedule** (group FIN-TYO, class B, local=False)
- RECORD FR-01029 [decision-critical] (operational/exception, day 2, by fin-tyo.a5; DB shows n/a): Sales Section 2 capex executing office agreed that SEL finance executes it until day 13.
- RULE FIN-TYO.owner_exception: {"id": "FIN-TYO.owner_exception", "group": "FIN-TYO", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-SEL/Sales Section 2/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Sales Section 2/remaining` v1 (recorded day 2, registered day 3): 3749879
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Section 2 AND status IN ['reviewing', 'pending'] → []
### Model answer and official verdict
answer: {"available": 3192087, "n_deducted": 1}
official exact match: 0 (0/2 slots)
### MATCHER CHECK FR-01029 (need FIN-TYO/Sales Section 2/budget_schedule): matcher says **missing**
record text: Sales Section 2 capex executing office agreed that SEL finance executes it until day 13.
What the requester received from FIN-TYO during this task:
```
[Reply 1] (partial) Sales Section 2 has budget line balance of 3,749,879 KRW and quarterly base allocation of 4,353,815 KRW. There are 5 provisional approvals (3 settled, 2 pending). On day 3, neither pending approval (CMT-00035 with expected_settle 3, CMT-00040 with expected_settle 1) is being deducted per pending_deduction rule. One earmark of 557,792 KRW until day 4 is active. Available budget is 3,192,087 KRW after deducting the earmark.
[Reply 2] (partial) Sales Section 2 has a budget line balance of 3,749,879 KRW. All provisional approvals (CMT-00007, CMT-00012, CMT-00016, CMT-00035, CMT-00040) are settled, so no items are deducted. No earmarks found. Available budget is 3,749,879 KRW.
- Sales Section 2 | budget_line_balance | 3749879 |  | db, day -1: Reply 1: D1
- Sales Section 2 | budget_line_base | 4353815 |  | db, day -20: Reply 1: D2
- CMT-00007 | provisional_approval status | settled | settled | db, day -5: Reply 1: D3
- CMT-00007 | amount | 800847 | settled | db, day -5: Reply 1: D3
- CMT-00007 | expected_settle | -6 | settled | db, day -5: Reply 1: D3
- CMT-00012 | provisional_approval status | settled | settled | db, day -1: Reply 1: D3
- CMT-00012 | amount | 757012 | settled | db, day -1: Reply 1: D3
- CMT-00012 | expected_settle | -3 | settled | db, day -1: Reply 1: D3
- CMT-00016 | provisional_approval status | settled | settled | db, day -7: Reply 1: D3
- CMT-00016 | amount | 867640 | settled | db, day -7: Reply 1: D3
- CMT-00016 | expected_settle | -10 | settled | db, day -7: Reply 1: D3
- CMT-00035 | provisional_approval status | pending | pending | db, day 1: Reply 1: D3
- CMT-00035 | amount | 497762 | pending | db, day 1: Reply 1: D3
- CMT-00035 | expected_settle | 3 | pending | db, day 1: Reply 1: D3
- CMT-00040 | provisional_approval status | pending | pending | db, day 0: Reply 1: D3
- CMT-00040 | amount | 811813 | pending | db, day 0: Reply 1: D3
- CMT-00040 | expected_settle | 1 | pending | db, day 0: Reply 1: D3
- Sales Section 2 | earmark | 557792 KRW until day 4 |  | history, day -1: Reply 1: H175
- Sales Section 2 | sum of pending provisional approvals being deducted | 0 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 2 | sum of earmarks in validity period | 557792 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 2 | available_budget | 3192087 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 2 | budget_line_balance | 3749879 |  | db, day -1: Reply 2: D1
- Sales Section 2 | budget_line_base | 4353815 |  | db, day -20: Reply 2: D2
- CMT-00007 | status | settled |  | db, day -5: Reply 2: D3
- CMT-00007 | amount | 800847 |  | db, day -5: Reply 2: D3
- CMT-00007 | expected_settle | -6 |  | db, day -5: Reply 2: D3
- CMT-00012 | status | settled |  | db, day -1: Reply 2: D3
- CMT-00012 | amount | 757012 |  | db, day -1: Reply 2: D3
- CMT-00012 | expected_settle | -3 |  | db, day -1: Reply 2: D3
- CMT-00016 | status | settled |  | db, day -7: Reply 2: D3
- CMT-00016 | amount | 867640 |  | db, day -7: Reply 2: D3
- CMT-00016 | expected_settle | -10 |  | db, day -7: Reply 2: D3
- CMT-00035 | status | settled |  | history, day 3: Reply 2: H230
- CMT-00035 | amount | 497762 |  | db, day 1: Reply 2: D3
- CMT-00035 | expected_settle | 3 |  | db, day 1: Reply 2: D3
- CMT-00040 | status | settled |  | history, day 1: Reply 2: H82
- CMT-00040 | amount | 811813 |  | db, day 0: Reply 2: D3
- CMT-00040 | expected_settle | 1 |  | db, day 0: Reply 2: D3
- Sales Section 2 | sum of items being deducted | 0 |  | db, day unknown: Reply 2: calculated from D3,H82,H230
- Sales Section 2 | available budget | 3749879 |  | db, day -1: Reply 2: calculated from D1
missing: Whether Sales Section 2 is in TYO region - no catalog_entry record found to confirm region; Region of Sales Section 2 (catalog_entry returned NO_RECORD); Earmarks for Sales Section 2 (no information found in records)
---
[Reply 1] (ok) Sales Section 2 has an active earmark of 557,792 KRW until day 4 (recorded on day -1). CMT-00035 is pending (497,762 KRW, settle day 3). CMT-00040 is pending (811,813 KRW, settle day 1).
[Reply 2] (partial) No earmark record found for Sales Section 2. CMT-00035 and CMT-00040 show as pending in database but history records indicate they were settled (CMT-00035 on day 3, CMT-00040 on day 1).
[Reply 3] (partial) CMT-00035 and CMT-00040 both have status 'pending' as per database records. No earmark record for Sales Section 2 found in my area's records.
[Reply 4] (partial) CMT-00035 and CMT-00040 both have status 'pending' as per database records. No earmark record found for Sales Section 2.
- Sales Section 2 | earmark amount | 557,792 KRW | active until day 4 | history, day -1: Reply 1: H175
- Sales Section 2 | earmark end day | day 4 | active until day 4 | history, day -1: Reply 1: H175
- CMT-00035 | provisional approval status | pending | pending | db, day 1: Reply 1: D2
- CMT-00035 | amount | 497762 | pending | db, day 1: Reply 1: D2
- CMT-00035 | expected settlement day | 3 | pending | db, day 1: Reply 1: D2
- CMT-00040 | provisional approval status | pending | pending | db, day 0: Reply 1: D3
- CMT-00040 | amount | 811813 | pending | db, day 0: Reply 1: D3
- CMT-00040 | expected settlement day | 1 | pending | db, day 0: Reply 1: D3
- Sales Section 2 | earmark record | NO_RECORD |  | db, day unknown: Reply 2: D1
- CMT-00035 | provisional_approval status | pending | pending | db, day 1: Reply 2: D2
- CMT-00035 | provisional_approval amount | 497762 | pending | db, day 1: Reply 2: D2
- CMT-00035 | expected_settle | 3 | pending | db, day 1: Reply 2: D2
- CMT-00035 | status from history | settled |  | history, day 3: Reply 2: H230
- CMT-00040 | provisional_approval status | pending | pending | db, day 0: Reply 2: D3
- CMT-00040 | provisional_approval amount | 811813 | pending | db, day 0: Reply 2: D3
- CMT-00040 | expected_settle | 1 | pending | db, day 0: Reply 2: D3
- CMT-00040 | status from history | settled |  | history, day 1: Reply 2: H82
- CMT-00035 | status | pending | pending | db, day 1: Reply 3: D2
- CMT-00035 | amount | 497762 | pending | db, day 1: Reply 3: D2
- CMT-00035 | expected_settle | 3 | pending | db, day 1: Reply 3: D2
- CMT-00040 | status | pending | pending | db, day 0: Reply 3: D3
- CMT-00040 | amount | 811813 | pending | db, day 0: Reply 3: D3
- CMT-00040 | expected_settle | 1 | pending | db, day 0: Reply 3: D3
- CMT-00035 | status | pending |  | db, day 1: Reply 4: D2
- CMT-00035 | amount | 497762 |  | db, day 1: Reply 4: D2
- CMT-00035 | expected_settle | 3 |  | db, day 1: Reply 4: D2
- CMT-00040 | status | pending |  | db, day 0: Reply 4: D3
- CMT-00040 | amount | 811813 |  | db, day 0: Reply 4: D3
- CMT-00040 | expected_settle | 1 |  | db, day 0: Reply 4: D3
missing: Active earmark of 557,792 KRW until day 4 for Sales Section 2 - no earmark record found in database; Earmark for Sales Section 2 (557,792 KRW until day 4) - no record found in my area's database or history; Earmark for Sales Section 2 (557,792 KRW until day 4) - not found in records
```

## CASE 18: qwen3.5-27b · routing · s14 · W-00070 · class B · day 7 · template contract_gate
### Task as given to the requester
For Shimizu-san: the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "premium", "contract_tier": "premium", "nda_step": false, "expiry": 187}
### Counterfactual answers (generator)
{"stale": {"it_tier": "premium", "contract_tier": "premium", "nda_step": false, "expiry": 152}, "partial": {"it_tier": "premium", "contract_tier": "standard", "nda_step": false, "expiry": 187}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1017/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1017"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v3 (recorded day -7, registered day -6): {"dept": "Dev Section 2", "grade": 5, "contract": "contractor", "hire_day": -784, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1017** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1017/contract** (group LEGAL-TYO, class B, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1017/terms` v6 (recorded day 1, registered day 4): {"allowed_tier": "standard", "expiry": 187, "nda": false}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00338 [decision-critical] (operational/exception, day -16, by legal-tyo.a3; DB shows n/a): Equipment exception of Shimizu Hayate higher tiers including premium allowed until day 12 for a project, legal check done.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 187, "it_tier": "premium", "nda_step": false}
official exact match: 1 (4/4 slots)
### MATCHER CHECK FR-00338 (need LEGAL-TYO/E-TYO-1017/contract): matcher says **delivered**
record text: Equipment exception of Shimizu Hayate higher tiers including premium allowed until day 12 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
[Reply 1] (ok) Contract terms for E-TYO-1017: allowed_tier=standard, expiry=187, nda=false. Equipment exception allows higher tiers including premium until day 12. No NDA check required since nda=false.
[Reply 2] (ok) For E-TYO-1017 (Shimizu-san): allowed tier is standard, expiry day 187, nda=false. Premium tier would require legal exception per contractor_policy. Standard equipment does not require NDA check since contract nda=false (no NDA clause). Previous NDA skip until day -3 has expired.
[Reply 3] (partial) Contract terms for E-TYO-1017 (Shimizu-san): allowed tier is standard, expires day 187, NDA not required. Since NDA is false, no NDA check is needed for standard equipment per contractor_policy. No legal exceptions found.
- E-TYO-1017 | allowed_tier | standard |  | db, day 4: Reply 1: D1
- E-TYO-1017 | expiry | 187 |  | db, day 4: Reply 1: D1
- E-TYO-1017 | nda | false |  | db, day 4: Reply 1: D1
- Shimizu Hayate | equipment exception | higher tiers including premium allowed until day 12 for a project, legal check done | until day 12 | history, day -16: Reply 1: H11
- E-TYO-1017 | NDA check required for standard equipment | no, nda=false means no NDA clause present |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-1017 | allowed_tier | standard |  | db, day 4: Reply 2: D1
- E-TYO-1017 | expiry | 187 |  | db, day 4: Reply 2: D1
- E-TYO-1017 | nda | false |  | db, day 4: Reply 2: D1
- Shimizu Hayate | NDA check skip status | signed copy verified, NDA check step can be skipped until day -3 | expired (today is day 7) | history, day -13: Reply 2: H19
- contractor_policy | legal exception requirement | Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 2: rule: contractor_policy
- contractor_policy | NDA check requirement for standard equipment | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: Reply 2: rule: contractor_policy
- E-TYO-1017 | highest equipment tier allowed | standard |  | db, day 4: Reply 3: D1
- E-TYO-1017 | contract expiry day | 187 |  | db, day 4: Reply 3: D1
- E-TYO-1017 | NDA required | false |  | db, day 4: Reply 3: D1
- contractor_policy | NDA check requirement for standard equipment | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: Reply 3: contractor_policy
missing: Legal exceptions applying to E-TYO-1017 - no exception records found in database or records
```

## CASE 19: qwen3.5-27b · routing · s14 · W-00125 · class C · day 13 · template alloc
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
answer: {"alloc": [1, 0, 0], "buy": 0, "transfer": 0, "unmet": 10}
official exact match: 0 (1/4 slots)
### MATCHER CHECK FR-01641 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01621 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: HR record of Oh Minjae exit processed (Customer Support Team). Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":2,"hire_day":-111,"status":"exited"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01643 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: HR record of Shin Daeun moved from Dev Team 1 to Customer Support Team, grade 1, regular. Stored value: {"contract":"regular","dept":"Customer Support Team","grade":1,"hire_day":-869,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01248 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01641 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01248 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01642 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: HR record of Bong Seoha moved from Marketing Team to Sales Team 2, grade 2, regular. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":2,"hire_day":-6,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01405 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Tak Jiho approved from Dev Team 2 to Marketing Team, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01645 (need HR-SEL/Sales Team 1/planning_headcount): matcher says **missing**
record text: Transfer of Kim Harin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01626 (need HR-SEL/Sales Team 1/planning_headcount): matcher says **missing**
record text: Transfer of Jung Yerin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Planning headcount: Customer Support Team = 5, Marketing Team = 2, Sales Team 1 = 4
[Reply 2] (partial) Planning headcount based on active employee count: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. Could not confirm absence of confirmed hires or transfers within 7 days.
[Reply 3] (partial) Planning headcount based on active employees from database: Customer Support Team=4, Marketing Team=3, Sales Team 1=2. No information available on confirmed hires or transfers within 7 days.
[Reply 4] (ok)
- Customer Support Team | planning headcount | 5 |  | db, day unknown: Reply 1: D1,H342,H379,H494
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 1: D2,H342,H494,H497
- Sales Team 1 | planning headcount | 4 |  | db, day unknown: Reply 1: D3,H491,H500
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | planning headcount | 4 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D1
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D2
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 | Could not confirm absence of confirmed hires or transfers within 7 days | db, day unknown: Reply 2: D3
- Customer Support Team | planning headcount | 4 |  | db, day unknown: Reply 3: D1
- Marketing Team | planning headcount | 3 |  | db, day unknown: Reply 3: D2
- Sales Team 1 | planning headcount | 2 |  | db, day unknown: Reply 3: D3
- Customer Support Team | headcount | 4 |  | db, day unknown: Reply 4: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: planning_headcount
- Marketing Team | headcount | 3 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 4: planning_headcount
- Sales Team 1 | headcount | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 4: planning_headcount
missing: Confirmed hires starting within 7 days for Customer Support Team; Transfers taking effect within 7 days for Customer Support Team; Confirmed hires starting within 7 days for Marketing Team; Transfers taking effect within 7 days for Marketing Team; Confirmed hires starting within 7 days for Sales Team 1; Transfers taking effect within 7 days for Sales Team 1
```
### MATCHER CHECK FR-01471 (need FIN-SEL/Customer Support Team/budget_schedule): matcher says **missing**
record text: Customer Support Team capex executing office agreed that TYO finance executes it until day 27.
What the requester received from FIN-SEL during this task:
```
(nothing received from this group)
```
### MATCHER CHECK FR-01493 (need FIN-TYO/Customer Support Team/budget_schedule): matcher says **missing**
record text: CMT-00114 Customer Support Team monitor provisional approval 451,072 KRW under review, settlement expected day 18.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```
### MATCHER CHECK FR-01612 (need FIN-TYO/Customer Support Team/budget_schedule): matcher says **missing**
record text: CMT-00120 Customer Support Team travel advance provisional approval 666,274 KRW under review, settlement expected day 19.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```

## CASE 20: qwen3.5-27b · routing · s14 · W-00077 · class C · day 8 · template alloc
### Task as given to the requester
Allocate Analytics seats to Dev Section 1, Planning Section, Sales Section 1 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"alloc": [4, 2, 3], "transfer": 0, "buy": 6, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [3, 2, 3], "transfer": 0, "buy": 5, "unmet": 0}, "partial": {"alloc": [3, 2, 3], "transfer": 0, "buy": 5, "unmet": 0}, "neardup": {"alloc": [1, 2, 3], "transfer": 0, "buy": 3, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/license/Analytics** (group IT-TYO, class None, local=True)
- DB `IT-TYO/lic/Analytics/seats` v3 (recorded day 4, registered day 6): {"seats": 33, "used": 30}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need LEGAL-TYO/sw_contractor/Analytics** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.sw_contractor: {"id": "LEGAL-TYO.sw_contractor", "group": "LEGAL-TYO", "title": "Contractor software restriction", "params": {"blocked": ["Analytics", "Design Suite"]}, "text": "Contractors are not assigned seats of these software products: Analytics, Design Suite."}
**need HR-TYO/Dev Section 1/planning_headcount-regular** (group HR-TYO, class B, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-01318 [decision-critical] (db_pending/observation, day 7, by hr-tyo.a5; DB shows 1): HR record of Ono Ken moved from Support Section to Dev Section 1, grade 3, regular. Stored value: {"contract":"regular","dept":"Dev Section 1","grade":3,"hire_day":-715,"status":"active"}
- DB `HR-TYO/emp/E-TYO-1005/profile` v4 (recorded day 3, registered day 6): {"dept": "Dev Section 1", "grade": 3, "contract": "regular", "hire_day": -396, "status": "active"}
- RECORD FR-01266 [decision-critical] (operational/pending_intent, day 6, by hr-tyo.a5; DB shows n/a): Transfer of Ito Aoi approved from Dev Section 1 to Planning Section, effective day 9 (stays in Dev Section 1 until then).
- DB `HR-TYO/emp/E-TYO-1010/profile` v3 (recorded day 6, registered day 8): {"dept": "Dev Section 1", "grade": 5, "contract": "regular", "hire_day": -896, "status": "active"}
- RECORD FR-01133 [decision-critical] (operational/pending_intent, day 3, by hr-tyo.a5; DB shows n/a): Transfer of Inoue Ritsu approved from Planning Section to Dev Section 1, effective day 9 (stays in Planning Section until then).
- DB `HR-TYO/emp/E-TYO-1018/profile` v3 (recorded day 3, registered day 5): {"dept": "Dev Section 1", "grade": 1, "contract": "regular", "hire_day": -306, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1019/profile` v3 (recorded day -4, registered day -1): {"dept": "Dev Section 1", "grade": 2, "contract": "regular", "hire_day": -365, "status": "active"}
- RECORD FR-01347 [decision-critical] (operational/pending_intent, day 7, by hr-tyo.a5; DB shows n/a): Transfer of Mori Yamato approved from Dev Section 1 to Support Section, effective day 14 (stays in Dev Section 1 until then).
- QUERY COUNT(emp WHERE region=TYO AND dept=Dev Section 1 AND status=active AND contract=regular) → 5
**need HR-TYO/Planning Section/planning_headcount-regular** (group HR-TYO, class B, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1000/profile` v3 (recorded day -4, registered day -2): {"dept": "Planning Section", "grade": 5, "contract": "regular", "hire_day": -106, "status": "exited"}
- DB `HR-TYO/emp/E-TYO-1003/profile` v3 (recorded day 4, registered day 5): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -639, "status": "active"}
- RECORD FR-01266 [decision-critical] (operational/pending_intent, day 6, by hr-tyo.a5; DB shows n/a): Transfer of Ito Aoi approved from Dev Section 1 to Planning Section, effective day 9 (stays in Dev Section 1 until then).
- DB `HR-TYO/emp/E-TYO-1006/profile` v2 (recorded day -1, registered day 1): {"dept": "Planning Section", "grade": 5, "contract": "regular", "hire_day": -162, "status": "active"}
- RECORD FR-01133 [decision-critical] (operational/pending_intent, day 3, by hr-tyo.a5; DB shows n/a): Transfer of Inoue Ritsu approved from Planning Section to Dev Section 1, effective day 9 (stays in Planning Section until then).
- RECORD FR-01378 (db_pending/observation, day 8, by hr-tyo.a5; DB shows 1): HR record of Hashimoto Moe moved from Planning Section to Support Section, grade 2, contractor. Stored value: {"contract":"contractor","dept":"Support Section","grade":2,"hire_day":-14,"status":"active"}
- DB `HR-TYO/emp/E-TYO-2008/profile` v2 (recorded day -1, registered day 0): {"dept": "Planning Section", "grade": 2, "contract": "regular", "hire_day": -9, "status": "active"}
- RECORD FR-01051 [decision-critical] (operational/pending_intent, day 2, by hr-tyo.a5; DB shows n/a): Transfer of Maeda An approved from Planning Section to Dev Section 2, effective day 13 (stays in Planning Section until then).
- QUERY COUNT(emp WHERE region=TYO AND dept=Planning Section AND status=active AND contract=regular) → 3
**need HR-TYO/Sales Section 1/planning_headcount-regular** (group HR-TYO, class C, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1003/profile` v3 (recorded day 4, registered day 5): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -639, "status": "active"}
- RECORD FR-01379 [decision-critical] (db_pending/observation, day 8, by hr-tyo.a5; DB shows 3): HR record of Kimura Yuito moved from Sales Section 2 to Sales Section 1, grade 3, regular. Stored value: {"contract":"regular","dept":"Sales Section 1","grade":3,"hire_day":-440,"status":"active"}
- DB `HR-TYO/emp/E-TYO-1016/profile` v2 (recorded day -7, registered day -4): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -506, "status": "exited"}
- RECORD FR-01320 [decision-critical] (db_pending/observation, day 7, by hr-tyo.a4; DB shows ABSENT): HR record of Hasegawa Fuka joined Sales Section 1, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Section 1","grade":1,"hire_day":7,"status":"active"}
- NEGATIVE: {"query": "HR-TYO Sales Section 1 memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=TYO AND dept=Sales Section 1 AND status=active AND contract=regular) → 3
**need IT-SEL/license/Analytics** (group IT-SEL, class A, local=False)
- DB `IT-SEL/lic/Analytics/seats` v7 (recorded day 6, registered day 7): {"seats": 37, "used": 33}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00995 [decision-critical] (operational/pending_intent, day 1, by it-sel.a4; DB shows n/a): Analytics seats 3 seats reserved for Marketing Team project until day 12.
**need IT-TYO/rule/seat_transfer_share** (group IT-TYO, class None, local=True)
- RULE IT-TYO.seat_transfer_share: {"id": "IT-TYO.seat_transfer_share", "group": "IT-TYO", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-TYO/rule/seat_purchase_line** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.seat_purchase_line: {"id": "FIN-TYO.seat_purchase_line", "group": "FIN-TYO", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-TYO/Dev Section 1/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Dev Section 1/remaining` v2 (recorded day 0, registered day 1): 2682726
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00010/status` v2 (recorded day -9, registered day -6): {"status": "settled", "amount": 955021, "expected_settle": -9}
- DB `FIN-TYO/commit/CMT-00034/status` v2 (recorded day -4, registered day -2): {"status": "settled", "amount": 481193, "expected_settle": -4}
- DB `FIN-TYO/commit/CMT-00041/status` v2 (recorded day 3, registered day 6): {"status": "settled", "amount": 992106, "expected_settle": 3}
- DB `FIN-TYO/commit/CMT-00055/status` v2 (recorded day -1, registered day 0): {"status": "settled", "amount": 361471, "expected_settle": -2}
- DB `FIN-TYO/commit/CMT-00082/status` v2 (recorded day 6, registered day 8): {"status": "settled", "amount": 969263, "expected_settle": 6}
- RECORD FR-01237 (operational/pending_intent, day 5, by fin-tyo.a2; DB shows n/a): CMT-00099 Dev Section 1 monitor provisional approval 225,292 KRW under review, settlement expected day 12.
- RECORD FR-01368 (operational/pending_intent, day 7, by fin-tyo.a3; DB shows n/a): CMT-00107 Dev Section 1 workstation provisional approval 778,929 KRW under review, settlement expected day 15.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Dev Section 1 AND status IN ['reviewing', 'pending'] → ["CMT-00066", "CMT-00099", "CMT-00107"]
**need IT-TYO/rule/seat_price** (group IT-TYO, class None, local=True)
- RULE IT-TYO.seat_price: {"id": "IT-TYO.seat_price", "group": "IT-TYO", "title": "Standard seat price", "params": {"price": 218619}, "text": "When there is no supplier price, one seat costs 218,619 KRW."}
### Model answer and official verdict
answer: {"alloc": [3, 0, 0], "buy": 0, "transfer": 0, "unmet": 10}
official exact match: 0 (1/4 slots)
### MATCHER CHECK FR-01318 (need HR-TYO/Dev Section 1/planning_headcount-regular): matcher says **missing**
record text: HR record of Ono Ken moved from Support Section to Dev Section 1, grade 3, regular. Stored value: {"contract":"regular","dept":"Dev Section 1","grade":3,"hire_day":-715,"status":"active"}
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01266 (need HR-TYO/Dev Section 1/planning_headcount-regular): matcher says **missing**
record text: Transfer of Ito Aoi approved from Dev Section 1 to Planning Section, effective day 9 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01133 (need HR-TYO/Dev Section 1/planning_headcount-regular): matcher says **missing**
record text: Transfer of Inoue Ritsu approved from Planning Section to Dev Section 1, effective day 9 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01347 (need HR-TYO/Dev Section 1/planning_headcount-regular): matcher says **missing**
record text: Transfer of Mori Yamato approved from Dev Section 1 to Support Section, effective day 14 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01266 (need HR-TYO/Planning Section/planning_headcount-regular): matcher says **missing**
record text: Transfer of Ito Aoi approved from Dev Section 1 to Planning Section, effective day 9 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01133 (need HR-TYO/Planning Section/planning_headcount-regular): matcher says **missing**
record text: Transfer of Inoue Ritsu approved from Planning Section to Dev Section 1, effective day 9 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01051 (need HR-TYO/Planning Section/planning_headcount-regular): matcher says **missing**
record text: Transfer of Maeda An approved from Planning Section to Dev Section 2, effective day 13 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01379 (need HR-TYO/Sales Section 1/planning_headcount-regular): matcher says **missing**
record text: HR record of Kimura Yuito moved from Sales Section 2 to Sales Section 1, grade 3, regular. Stored value: {"contract":"regular","dept":"Sales Section 1","grade":3,"hire_day":-440,"status":"active"}
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-01320 (need HR-TYO/Sales Section 1/planning_headcount-regular): matcher says **missing**
record text: HR record of Hasegawa Fuka joined Sales Section 1, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Section 1","grade":1,"hire_day":7,"status":"active"}
What the requester received from HR-TYO during this task:
```
[Reply 1] (partial) Found headcount values from database queries, but cannot determine planning headcount without information about confirmed hires starting within 7 days and transfers taking effect within 7 days.
[Reply 2] (ok)
[Reply 3] (partial) Dev Section 1 planning headcount is 5. Planning Section and Sales Section 1 planning headcounts cannot be determined because the start dates of confirmed hires (OF-00015 and OF-00016) are not specified in records, so I cannot confirm if they fall within 7 days from day 8.
[Reply 4] (partial) Planning headcount as of day 8: Dev Section 1 = 5, Planning Section = 5, Sales Section 1 = 3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 1: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 1: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 1: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D1
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 2: D1
- Planning Section | headcount | 6 |  | db, day unknown: Reply 2: D2
- Planning Section | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D2
- Planning Section | planning headcount | 6 |  | db, day unknown: Reply 2: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | confirmed hires within 7 days | 0 |  | db, day unknown: Reply 2: D3
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 2: D3
- Dev Section 1 | headcount | 5 |  | db, day unknown: Reply 3: D1
- Dev Section 1 | confirmed hires starting within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | transfers taking effect within 7 days | 0 |  | unknown, day unknown: Reply 3: records
- Dev Section 1 | planning headcount | 5 |  | rule, day fixed: Reply 3: planning_headcount
- Planning Section | headcount | 6 |  | db, day unknown: Reply 3: D2
- Sales Section 1 | headcount | 3 |  | db, day unknown: Reply 3: D3
- Dev Section 1 | current headcount | 5 |  | db, day unknown: Reply 4: D1
- Dev Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H421
- Dev Section 1 | transfers in within 7 days | 1 |  | history, day 7: Reply 4: H416
- Dev Section 1 | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D1,H421,H416
- Planning Section | current headcount | 6 |  | db, day unknown: Reply 4: D2
- Planning Section | transfers out within 7 days | 1 |  | history, day 8: Reply 4: H433
- Planning Section | transfers in within 7 days | 0 |  | history, day 8: Reply 4: H457
- Planning Section | planning headcount | 5 |  | db, day unknown: Reply 4: calculated from D2,H433,H457
- Sales Section 1 | current headcount | 3 |  | db, day unknown: Reply 4: D3
- Sales Section 1 | transfers out within 7 days | 1 |  | history, day 7: Reply 4: H424
- Sales Section 1 | transfers in within 7 days | 1 |  | history, day 8: Reply 4: H436
- Sales Section 1 | planning headcount | 3 |  | db, day unknown: Reply 4: calculated from D3,H424,H436
missing: Planning headcount for Dev Section 1 (requires confirmed hires and transfers information); Planning headcount for Planning Section (requires confirmed hires and transfers information); Planning headcount for Sales Section 1 (requires confirmed hires and transfers information); Planning Section confirmed hires starting within 7 days - start date of OF-00015 from H89 not specified; Sales Section 1 confirmed hires starting within 7 days - start date of OF-00016 from H117 not specified; Planning Section planning headcount - cannot calculate without confirmed hires information; Sales Section 1 planning headcount - cannot calculate without confirmed hires information; confirmed hires within 7 days for Dev Section 1; confirmed hires within 7 days for Planning Section; confirmed hires within 7 days for Sales Section 1
```
### MATCHER CHECK FR-00995 (need IT-SEL/license/Analytics): matcher says **stale**
record text: Analytics seats 3 seats reserved for Marketing Team project until day 12.
What the requester received from IT-SEL during this task:
```
(nothing received from this group)
```

## CASE 21: qwen3.5-27b · routing · s12 · W-00094 · class C · day 10 · template capacity
### Task as given to the requester
How many in-house laptop (premium) units and Analytics seats are actually available right now?
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
**need IT-SEL/stock/INV-SEL-LTP** (group IT-SEL, class A, local=False)
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-LTP"}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-SEL/inv/INV-SEL-LTP/qty` v6 (recorded day 7, registered day 8): 0
- NEGATIVE: {"query": "IT-SEL INV-SEL-LTP memos on active holds", "result": []}
**need IT-SEL/license/Analytics** (group IT-SEL, class C, local=False)
- RECORD FR-01382 [decision-critical] (db_pending/observation, day 9, by it-sel.n0012; DB shows 3): Analytics seats In use 16/21 seats. Stored value: {"seats":21,"used":16}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01233 [decision-critical] (operational/pending_intent, day 6, by it-sel.a4; DB shows n/a): Analytics seats 4 seats reserved for Dev Team 2 onboarding until day 20.
- RECORD FR-01234 [decision-critical] (operational/pending_intent, day 6, by it-sel.a5; DB shows n/a): Analytics seats 3 seats reserved for Customer Support Team onboarding until day 19.
### Model answer and official verdict
answer: {"seats": 4, "seats_other_region": null, "stock": 0}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-01382 (need IT-SEL/license/Analytics): matcher says **stale**
record text: Analytics seats In use 16/21 seats. Stored value: {"seats":21,"used":16}
What the requester received from IT-SEL during this task:
```
[Reply 1] (ok) Premium laptop stock: 0 units. Analytics available seats: 8 (21 total - 13 used).
[Reply 2] (ok)
[Reply 3] (ok) Premium laptop (INV-SEL-LTP) available: 0 units; Analytics available seats in SEL: 4 (21 total - 13 used - 4 reserved)
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 1: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 1: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 1: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 1: D2
- INV-SEL-LTP | available quantity | 0 |  | db, day 8: Reply 2: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 2: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 2: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 2: calculated from D2
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 3: D1
- laptop (premium) | available stock | 0 |  | db, day 8: Reply 3: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 3: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 3: D2
- Analytics | reserved seats | 4 seats reserved for Dev Team 2 onboarding until day 20 | until day 20 | history, day 6: Reply 3: H137
- Analytics | available seats (SEL) | 4 |  | db, day 8: Reply 3: calculated from D2 and H137
```
### MATCHER CHECK FR-01233 (need IT-SEL/license/Analytics): matcher says **delivered**
record text: Analytics seats 4 seats reserved for Dev Team 2 onboarding until day 20.
What the requester received from IT-SEL during this task:
```
[Reply 1] (ok) Premium laptop stock: 0 units. Analytics available seats: 8 (21 total - 13 used).
[Reply 2] (ok)
[Reply 3] (ok) Premium laptop (INV-SEL-LTP) available: 0 units; Analytics available seats in SEL: 4 (21 total - 13 used - 4 reserved)
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 1: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 1: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 1: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 1: D2
- INV-SEL-LTP | available quantity | 0 |  | db, day 8: Reply 2: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 2: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 2: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 2: calculated from D2
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 3: D1
- laptop (premium) | available stock | 0 |  | db, day 8: Reply 3: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 3: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 3: D2
- Analytics | reserved seats | 4 seats reserved for Dev Team 2 onboarding until day 20 | until day 20 | history, day 6: Reply 3: H137
- Analytics | available seats (SEL) | 4 |  | db, day 8: Reply 3: calculated from D2 and H137
```
### MATCHER CHECK FR-01234 (need IT-SEL/license/Analytics): matcher says **stale**
record text: Analytics seats 3 seats reserved for Customer Support Team onboarding until day 19.
What the requester received from IT-SEL during this task:
```
[Reply 1] (ok) Premium laptop stock: 0 units. Analytics available seats: 8 (21 total - 13 used).
[Reply 2] (ok)
[Reply 3] (ok) Premium laptop (INV-SEL-LTP) available: 0 units; Analytics available seats in SEL: 4 (21 total - 13 used - 4 reserved)
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 1: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 1: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 1: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 1: D2
- INV-SEL-LTP | available quantity | 0 |  | db, day 8: Reply 2: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 2: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 2: D2
- Analytics | available seats | 8 |  | db, day 8: Reply 2: calculated from D2
- INV-SEL-LTP | inventory_quantity | 0 |  | db, day 8: Reply 3: D1
- laptop (premium) | available stock | 0 |  | db, day 8: Reply 3: D1
- Analytics | total seats | 21 |  | db, day 8: Reply 3: D2
- Analytics | used seats | 13 |  | db, day 8: Reply 3: D2
- Analytics | reserved seats | 4 seats reserved for Dev Team 2 onboarding until day 20 | until day 20 | history, day 6: Reply 3: H137
- Analytics | available seats (SEL) | 4 |  | db, day 8: Reply 3: calculated from D2 and H137
```

## CASE 22: qwen3.5-27b · routing · s13 · W-00121 · class D · day 13 · template vendor
### Task as given to the requester
That department from W-00116 needs a monitor. Pick a compliant supplier within budget.
[Request scope] item=monitor; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- vendor: Supplier ID of the cheapest compliant quote; null if none.
- option: Quote ID of that quote; null if none.
- amount: Quote amount; null if none.
- approver: Finance approver for that amount; null if none.
- budget_after: Available budget of the department minus the amount; null if none.
- blocked_by: null when a quote is chosen. Otherwise the first failing condition of the cheapest quote, checked in this order: budget, vendor_excluded, lead_time, residency; 'no_candidate' if there are no quotes.
- Public region list, in order: SEL, TYO.
### Gold answer
{"vendor": "V-SEL-2", "option": "Q-V-SEL-2-MNB", "amount": 769935, "approver": "team_lead", "budget_after": 206631, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"vendor": "V-SEL-2", "option": "Q-V-SEL-2-MNB", "amount": 769935, "approver": "team_lead", "budget_after": 983546, "blocked_by": null}, "partial": {"vendor": "V-SEL-2", "option": "Q-V-SEL-2-MNB", "amount": 769935, "approver": "team_lead", "budget_after": 1540015, "blocked_by": null}, "neardup": {"vendor": "V-SEL-2", "option": "Q-V-SEL-2-MNB", "amount": 769935, "approver": "team_lead", "budget_after": 122864, "blocked_by": null}, "wrong_owner": {"vendor": "V-SEL-2", "option": "Q-V-SEL-2-MNB", "amount": 769935, "approver": "team_lead", "budget_after": 1540015, "blocked_by": null}}
### World facts behind the gold (by need)
**need IT-SEL/task/W-00116/result** (group IT-SEL, class None, local=True)
- RECORD FR-01627 (operational/task_result, day 12, by it-sel.a2; DB shows n/a): W-00116 item result: available=976566, n_deducted=3
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class B, local=False)
- RECORD FR-01347 [decision-critical] (operational/exception, day 7, by fin-sel.n0005; DB shows n/a): Sales Team 2 capex executing office agreed that TYO finance executes it until day 28.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Sales Team 2/budget_schedule** (group FIN-TYO, class C, local=False)
- DB `FIN-TYO/line/Sales Team 2/remaining` v2 (recorded day 7, registered day 10): 3159648
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00026/status` v2 (recorded day 3, registered day 4): {"status": "settled", "amount": 839113, "expected_settle": 3}
- DB `FIN-TYO/commit/CMT-00028/status` v2 (recorded day 4, registered day 5): {"status": "settled", "amount": 959706, "expected_settle": 4}
- DB `FIN-TYO/commit/CMT-00044/status` v2 (recorded day 4, registered day 7): {"status": "settled", "amount": 386882, "expected_settle": 4}
- RECORD FR-01470 [decision-critical] (operational/pending_intent, day 9, by fin-tyo.n0013; DB shows n/a): CMT-00095 Sales Team 2 monitor provisional approval 784,781 KRW under review, settlement expected day 22.
- RECORD FR-01483 [decision-critical] (operational/pending_intent, day 10, by fin-tyo.n0013; DB shows n/a): CMT-00096 Sales Team 2 order (incl. shipping) provisional approval (order of W-00083) 617,018 KRW under review, settlement expected day 14.
- RECORD FR-01598 [decision-critical] (operational/pending_intent, day 12, by fin-tyo.a4; DB shows n/a): CMT-00107 Sales Team 2 monitor provisional approval 781,283 KRW under review, settlement expected day 25.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00095", "CMT-00096", "CMT-00107"]
**need PROC-SEL/quotes/monitor** (group PROC-SEL, class D, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01055 [decision-critical] (operational/handover, day 2, by proc-sel.w00148; DB shows n/a): Supplier V-SEL-3 exclude from comparisons until day 13 due to a quality issue.
- RECORD FR-01202 (operational/observation, day 5, by proc-sel.w00176; DB shows n/a): Supplier V-SEL-0 delivery notified: deliveries delayed by 5 days until day 17.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01230 (operational/observation, day 5, by proc-sel.w00180; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 5 days until day 19.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01563 (operational/observation, day 11, by proc-sel.w00250; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 2 days until day 19.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v1 (recorded day -20, registered day -20): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-MNS/amount` v2 (recorded day -13, registered day -11): 1417136
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day 8, registered day 9): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-MNB/amount` v3 (recorded day -15, registered day -14): 877793
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day 8, registered day 9): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-MNS/amount` v1 (recorded day -20, registered day -20): 932267
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v3 (recorded day 7, registered day 9): 5
- DB `PROC-SEL/quote/Q-V-SEL-2-MNB/amount` v1 (recorded day -20, registered day -20): 769935
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v3 (recorded day 7, registered day 9): 5
- DB `PROC-SEL/quote/Q-V-SEL-2-MNS/amount` v1 (recorded day -20, registered day -20): 1573087
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v3 (recorded day 4, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-MNB/amount` v1 (recorded day -20, registered day -20): 466326
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v3 (recorded day 4, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-MNS/amount` v1 (recorded day -20, registered day -20): 1292715
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"amount": 769935, "approver": "team_lead", "blocked_by": null, "budget_after": 2351456, "option": "Q-V-SEL-2-MNB", "vendor": "V-SEL-2"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-01347 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **missing**
record text: Sales Team 2 capex executing office agreed that TYO finance executes it until day 28.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) For a purchase of 769,935 KRW, the required finance approver is team_lead. The approval thresholds are: up to 1,000,000 KRW requires team_lead approval, up to 2,500,000 KRW requires division_head approval, and amounts above 2,500,000 KRW require cfo approval.
[Reply 2] (ok) For a purchase of 769,935 KRW, the required approver is FIN_TEAM_LEAD as it falls within the up to 1,000,000 KRW threshold.
[Reply 3] (ok) For a purchase of 769,935 KRW, the required finance approver is team_lead. Approval thresholds: up to 1,000,000 KRW - team_lead; up to 2,500,000 KRW - division_head; above 2,500,000 KRW - cfo.
- approval_tiers | thresholds and approvers | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | rule, day fixed: Reply 1: rule: approval_tiers
- 769,935 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | threshold for team_lead approval | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | threshold for division_head approval | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | threshold for cfo approval | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- 769,935 KRW | required approver | FIN_TEAM_LEAD |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | up to 1,000,000 KRW approver | team_lead |  | rule, day fixed: Reply 3: rule: approval_tiers
- approval_tiers | up to 2,500,000 KRW approver | division_head |  | rule, day fixed: Reply 3: rule: approval_tiers
- approval_tiers | above 2,500,000 KRW approver | cfo |  | rule, day fixed: Reply 3: rule: approval_tiers
- purchase of 769935 KRW | required approver | team_lead |  | rule, day fixed: Reply 3: rule: approval_tiers
```
### MATCHER CHECK FR-01470 (need FIN-TYO/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00095 Sales Team 2 monitor provisional approval 784,781 KRW under review, settlement expected day 22.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```
### MATCHER CHECK FR-01483 (need FIN-TYO/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00096 Sales Team 2 order (incl. shipping) provisional approval (order of W-00083) 617,018 KRW under review, settlement expected day 14.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```
### MATCHER CHECK FR-01598 (need FIN-TYO/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00107 Sales Team 2 monitor provisional approval 781,283 KRW under review, settlement expected day 25.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```
### MATCHER CHECK FR-01055 (need PROC-SEL/quotes/monitor): matcher says **missing**
record text: Supplier V-SEL-3 exclude from comparisons until day 13 due to a quality issue.
What the requester received from PROC-SEL during this task:
```
[Reply 1] (partial) Found 7 monitor quotes in SEL region: 4 standard tier (Q-V-SEL-0-MNS, Q-V-SEL-1-MNS, Q-V-SEL-2-MNS, Q-V-SEL-3-MNS) and 3 basic tier (Q-V-SEL-1-MNB, Q-V-SEL-2-MNB, Q-V-SEL-3-MNB). Vendors V-SEL-0, V-SEL-1, V-SEL-2 are registered; V-SEL-3 is not registered. Lead times: V-SEL-0=6 days, V-SEL-1=4 days, V-SEL-2=5 days, V-SEL-3=9 days. No active exclusion notices found (V-SEL-1 had exclusion until day 7, now expired).
- Q-V-SEL-0-MNS | quote_id | Q-V-SEL-0-MNS |  | db, day fixed: Reply 1: D5
- Q-V-SEL-0-MNS | region | SEL |  | db, day fixed: Reply 1: D5
- Q-V-SEL-0-MNS | tier | standard |  | db, day fixed: Reply 1: D5
- Q-V-SEL-0-MNS | type | monitor |  | db, day fixed: Reply 1: D5
- Q-V-SEL-0-MNS | vendor | V-SEL-0 |  | db, day fixed: Reply 1: D5
- Q-V-SEL-0-MNS | quote_amount | 1417136 |  | db, day -11: Reply 1: D18
- Q-V-SEL-1-MNS | quote_id | Q-V-SEL-1-MNS |  | db, day fixed: Reply 1: D6
- Q-V-SEL-1-MNS | region | SEL |  | db, day fixed: Reply 1: D6
- Q-V-SEL-1-MNS | tier | standard |  | db, day fixed: Reply 1: D6
- Q-V-SEL-1-MNS | type | monitor |  | db, day fixed: Reply 1: D6
- Q-V-SEL-1-MNS | vendor | V-SEL-1 |  | db, day fixed: Reply 1: D6
- Q-V-SEL-1-MNS | quote_amount | 932267 |  | db, day -20: Reply 1: D19
- Q-V-SEL-2-MNS | quote_id | Q-V-SEL-2-MNS |  | db, day fixed: Reply 1: D7
- Q-V-SEL-2-MNS | region | SEL |  | db, day fixed: Reply 1: D7
- Q-V-SEL-2-MNS | tier | standard |  | db, day fixed: Reply 1: D7
- Q-V-SEL-2-MNS | type | monitor |  | db, day fixed: Reply 1: D7
- Q-V-SEL-2-MNS | vendor | V-SEL-2 |  | db, day fixed: Reply 1: D7
- Q-V-SEL-2-MNS | quote_amount | 1573087 |  | db, day -20: Reply 1: D20
- Q-V-SEL-3-MNS | quote_id | Q-V-SEL-3-MNS |  | db, day fixed: Reply 1: D8
- Q-V-SEL-3-MNS | region | SEL |  | db, day fixed: Reply 1: D8
- Q-V-SEL-3-MNS | tier | standard |  | db, day fixed: Reply 1: D8
- Q-V-SEL-3-MNS | type | monitor |  | db, day fixed: Reply 1: D8
- Q-V-SEL-3-MNS | vendor | V-SEL-3 |  | db, day fixed: Reply 1: D8
- Q-V-SEL-3-MNS | quote_amount | 1292715 |  | db, day -20: Reply 1: D21
- Q-V-SEL-1-MNB | quote_id | Q-V-SEL-1-MNB |  | db, day fixed: Reply 1: D10
- Q-V-SEL-1-MNB | region | SEL |  | db, day fixed: Reply 1: D10
- Q-V-SEL-1-MNB | tier | basic |  | db, day fixed: Reply 1: D10
- Q-V-SEL-1-MNB | type | monitor |  | db, day fixed: Reply 1: D10
- Q-V-SEL-1-MNB | vendor | V-SEL-1 |  | db, day fixed: Reply 1: D10
- Q-V-SEL-1-MNB | quote_amount | 877793 |  | db, day -14: Reply 1: D22
- Q-V-SEL-2-MNB | quote_id | Q-V-SEL-2-MNB |  | db, day fixed: Reply 1: D11
- Q-V-SEL-2-MNB | region | SEL |  | db, day fixed: Reply 1: D11
- Q-V-SEL-2-MNB | tier | basic |  | db, day fixed: Reply 1: D11
- Q-V-SEL-2-MNB | type | monitor |  | db, day fixed: Reply 1: D11
- Q-V-SEL-2-MNB | vendor | V-SEL-2 |  | db, day fixed: Reply 1: D11
- Q-V-SEL-2-MNB | quote_amount | 769935 |  | db, day -20: Reply 1: D23
- Q-V-SEL-3-MNB | quote_id | Q-V-SEL-3-MNB |  | db, day fixed: Reply 1: D12
- Q-V-SEL-3-MNB | region | SEL |  | db, day fixed: Reply 1: D12
- Q-V-SEL-3-MNB | tier | basic |  | db, day fixed: Reply 1: D12
- Q-V-SEL-3-MNB | type | monitor |  | db, day fixed: Reply 1: D12
- Q-V-SEL-3-MNB | vendor | V-SEL-3 |  | db, day fixed: Reply 1: D12
- Q-V-SEL-3-MNB | quote_amount | 466326 |  | db, day -20: Reply 1: D24
- V-SEL-0 | vendor_lead_time | 6 |  | db, day -20: Reply 1: D25
- V-SEL-0 | vendor_registration | true |  | db, day -20: Reply 1: D29
- V-SEL-1 | vendor_lead_time | 4 |  | db, day 9: Reply 1: D26
- V-SEL-1 | vendor_registration | true |  | db, day -20: Reply 1: D30
- V-SEL-2 | vendor_lead_time | 5 |  | db, day 9: Reply 1: D27
- V-SEL-2 | vendor_registration | true |  | db, day -20: Reply 1: D31
- V-SEL-3 | vendor_lead_time | 9 |  | db, day 7: Reply 1: D28
- V-SEL-3 | vendor_registration | false |  | db, day -20: Reply 1: D32
missing: Q-V-SEL-0-MNB quote (not found); Exclusion notice status for V-SEL-0 (no exclusion notice found in records); Exclusion notice status for V-SEL-2 (no exclusion notice found in records); Exclusion notice status for V-SEL-3 (no exclusion notice found in records)
```

## CASE 23: qwen3.5-27b · routing · s12 · W-00080 · class D · day 8 · template purchase
### Task as given to the requester
For Takahashi-san's laptop request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
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
{"decision": "order", "option": "Q-V-TYO-1-LTB", "approver": "team_lead", "nda": false, "budget_after": 1508400, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"decision": "order", "option": "Q-V-TYO-1-LTB", "approver": "team_lead", "nda": false, "budget_after": 169952, "blocked_by": null}, "partial": {"decision": "order", "option": "Q-V-TYO-1-LTB", "approver": "team_lead", "nda": false, "budget_after": 2059466, "blocked_by": null}, "neardup": {"decision": "order", "option": "Q-V-TYO-1-LTB", "approver": "team_lead", "nda": false, "budget_after": 2040965, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1003/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1003"}
- DB `HR-TYO/emp/E-TYO-1003/profile` v2 (recorded day 1, registered day 4): {"dept": "Sales Section 1", "grade": 1, "contract": "contractor", "hire_day": -485, "status": "active"}
**need FIN-TYO/Sales Section 1/budget_schedule** (group FIN-TYO, class D, local=False)
- DB `FIN-TYO/line/Sales Section 1/remaining` v6 (recorded day 4, registered day 5): 4113405
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01021 [decision-critical] (operational/pending_intent, day 2, by fin-tyo.a1; DB shows n/a): Sales Section 1 capex 551,066 KRW earmarked for training equipment until day 17 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00019/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 217637, "expected_settle": -2}
- DB `FIN-TYO/commit/CMT-00028/status` v2 (recorded day -3, registered day -1): {"status": "settled", "amount": 927451, "expected_settle": -3}
- RECORD FR-01169 [decision-critical] (operational/pending_intent, day 5, by fin-tyo.a3; DB shows n/a): CMT-00081 Sales Section 1 meeting room equipment provisional approval 609,401 KRW under review, settlement expected day 9.
- RECORD FR-01276 [decision-critical] (db_pending/observation, day 7, by fin-tyo.n0010; DB shows ABSENT): CMT-00082 Sales Section 1 provisional approval 918,151 KRW confirmed, settlement expected day 12. Stored value: {"amount":918151,"expected_settle":12,"status":"pending"}
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Section 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-01021", "CMT-00081", "CMT-00082"]
**need IT-TYO/eligibility/E-TYO-1003** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
- RECORD FR-00927 (operational/exception, day 0, by it-tyo.w00138; DB shows n/a): Equipment tier of Takahashi Misaki up to standard allowed until day 11 for work reasons (IT exception approved).
- RULE IT-TYO.tier_exception: {"id": "IT-TYO.tier_exception", "group": "IT-TYO", "title": "Equipment tier exception", "params": {"exception_raises_tier": true}, "text": "An equipment tier exception approved by IT replaces the grade-based default tier during the exception period."}
**need PROC-TYO/quotes/laptop** (group PROC-TYO, class A, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00981 (operational/handover, day 1, by proc-tyo.n0002; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 8 due to a quality issue.
- RECORD FR-00982 (operational/observation, day 1, by proc-tyo.a4; DB shows n/a): Supplier V-TYO-0 delivery notified: deliveries delayed by 3 days until day 8.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01036 (operational/observation, day 2, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 5 days until day 16.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01341 (operational/observation, day 8, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 19.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 4, registered day 7): 8
- RECORD FR-01239 (db_pending/rationale, day 6, by proc-tyo.a1; DB shows 2): V-TYO-0 laptop (basic) quote Q-V-TYO-0-LTB changed to 752,760 KRW (raw material prices). Stored value: 752760
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 4, registered day 7): 8
- DB `PROC-TYO/quote/Q-V-TYO-0-LTP/amount` v4 (recorded day 5, registered day 8): 2488260
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day -6, registered day -5): 5
- DB `PROC-TYO/quote/Q-V-TYO-1-LTB/amount` v1 (recorded day -20, registered day -20): 526387
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day -6, registered day -5): 5
- DB `PROC-TYO/quote/Q-V-TYO-1-LTP/amount` v2 (recorded day -10, registered day -9): 1663952
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01266 (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTB/amount` v1 (recorded day -20, registered day -20): 704358
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01266 (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTP/amount` v2 (recorded day 1, registered day 2): 2395030
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01266 (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTS/amount` v2 (recorded day -2, registered day 1): 1050981
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v3 (recorded day -1, registered day 1): 9
- DB `PROC-TYO/quote/Q-V-TYO-3-LTB/amount` v1 (recorded day -20, registered day -20): 484258
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v3 (recorded day -1, registered day 1): 9
- DB `PROC-TYO/quote/Q-V-TYO-3-LTP/amount` v3 (recorded day -3, registered day -1): 1931331
**need LEGAL-TYO/residency** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.residency: {"id": "LEGAL-TYO.residency", "group": "LEGAL-TYO", "title": "Data residency", "params": {"restricted_depts": ["Dev Section 1", "Sales Section 1"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Section 1, Sales Section 1."}
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 3587018, "decision": "order", "nda": false, "option": "Q-V-TYO-1-LTB"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-01021 (need FIN-TYO/Sales Section 1/budget_schedule): matcher says **missing**
record text: Sales Section 1 capex 551,066 KRW earmarked for training equipment until day 17 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
[Reply 1] (ok) Sales Section 1 has an available budget of 4,113,405 KRW, which is sufficient for a laptop costing 526,387 KRW.
[Reply 2] (partial) Cannot determine available budget for Sales Section 1 due to missing amount of CMT-00082 which is under review. Budget line balance is 4,113,405 KRW.
[Reply 3] (ok) Available budget for Sales Section 1 is 4,113,405 KRW. They can afford a laptop costing 526,387 KRW.
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 1: D1
- Sales Section 1 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 1: D3
- Sales Section 1 | number of earmarks | 0 |  | unknown, day unknown: Reply 1: records
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 2: D1
- Sales Section 1 | budget_line_base | 4865609 |  | db, day -20: Reply 2: D2
- CMT-00082 | status | under review | under review | history, day 5: Reply 2: H11
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 3: D1
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 3: pending_deduction
missing: Amount of CMT-00082; Earmarks for Sales Section 1
---
[Reply 1] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is up to 1,000,000 KRW.
[Reply 2] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
[Reply 3] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
- approval_tiers | up to 1,000,000 KRW approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- laptop order 526387 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 3: approval_tiers
```
### MATCHER CHECK FR-01169 (need FIN-TYO/Sales Section 1/budget_schedule): matcher says **missing**
record text: CMT-00081 Sales Section 1 meeting room equipment provisional approval 609,401 KRW under review, settlement expected day 9.
What the requester received from FIN-TYO during this task:
```
[Reply 1] (ok) Sales Section 1 has an available budget of 4,113,405 KRW, which is sufficient for a laptop costing 526,387 KRW.
[Reply 2] (partial) Cannot determine available budget for Sales Section 1 due to missing amount of CMT-00082 which is under review. Budget line balance is 4,113,405 KRW.
[Reply 3] (ok) Available budget for Sales Section 1 is 4,113,405 KRW. They can afford a laptop costing 526,387 KRW.
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 1: D1
- Sales Section 1 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 1: D3
- Sales Section 1 | number of earmarks | 0 |  | unknown, day unknown: Reply 1: records
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 2: D1
- Sales Section 1 | budget_line_base | 4865609 |  | db, day -20: Reply 2: D2
- CMT-00082 | status | under review | under review | history, day 5: Reply 2: H11
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 3: D1
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 3: pending_deduction
missing: Amount of CMT-00082; Earmarks for Sales Section 1
---
[Reply 1] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is up to 1,000,000 KRW.
[Reply 2] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
[Reply 3] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
- approval_tiers | up to 1,000,000 KRW approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- laptop order 526387 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 3: approval_tiers
```
### MATCHER CHECK FR-01276 (need FIN-TYO/Sales Section 1/budget_schedule): matcher says **missing**
record text: CMT-00082 Sales Section 1 provisional approval 918,151 KRW confirmed, settlement expected day 12. Stored value: {"amount":918151,"expected_settle":12,"status":"pending"}
What the requester received from FIN-TYO during this task:
```
[Reply 1] (ok) Sales Section 1 has an available budget of 4,113,405 KRW, which is sufficient for a laptop costing 526,387 KRW.
[Reply 2] (partial) Cannot determine available budget for Sales Section 1 due to missing amount of CMT-00082 which is under review. Budget line balance is 4,113,405 KRW.
[Reply 3] (ok) Available budget for Sales Section 1 is 4,113,405 KRW. They can afford a laptop costing 526,387 KRW.
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 1: D1
- Sales Section 1 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 1: D3
- Sales Section 1 | number of earmarks | 0 |  | unknown, day unknown: Reply 1: records
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 2: D1
- Sales Section 1 | budget_line_base | 4865609 |  | db, day -20: Reply 2: D2
- CMT-00082 | status | under review | under review | history, day 5: Reply 2: H11
- Sales Section 1 | budget_line_balance | 4113405 |  | db, day 5: Reply 3: D1
- Sales Section 1 | available budget | 4113405 |  | rule, day fixed: Reply 3: pending_deduction
missing: Amount of CMT-00082; Earmarks for Sales Section 1
---
[Reply 1] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is up to 1,000,000 KRW.
[Reply 2] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
[Reply 3] (ok) A laptop order costing 526,387 KRW requires team_lead approval since it is within the up to 1,000,000 KRW threshold.
- approval_tiers | up to 1,000,000 KRW approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- laptop order 526387 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- laptop order 526,387 KRW | required approver | team_lead |  | rule, day fixed: Reply 3: approval_tiers
```

## CASE 24: qwen3.5-27b · routing · s12 · W-00065 · class D · day 7 · template lookup
### Task as given to the requester
Check Mori-san's current department, grade and assets held.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- dept: Employee's current department.
- grade: Employee's current grade.
- assets: Asset IDs the employee currently holds (any order; empty list if none).
- Public region list, in order: SEL, TYO.
### Gold answer
{"dept": "Sales Section 1", "grade": 4, "assets": ["A-TYO-3893", "A-TYO-46864", "A-TYO-8146"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Dev Section 1", "grade": 4, "assets": ["A-TYO-3893", "A-TYO-46864", "A-TYO-8146"]}, "partial": {"dept": "Sales Section 1", "grade": 4, "assets": ["A-TYO-3893", "A-TYO-8146"]}, "neardup": {"dept": "Sales Section 2", "grade": 1, "assets": ["A-TYO-3893", "A-TYO-46864", "A-TYO-8146"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1019/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1019"}
- DB `HR-TYO/emp/E-TYO-1019/profile` v2 (recorded day 2, registered day 3): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -552, "status": "active"}
**need IT-TYO/E-TYO-1019/assets** (group IT-TYO, class D, local=False)
- DB `IT-TYO/asset/A-TYO-3893/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1019"}
- RECORD FR-01183 [decision-critical] (db_pending/observation, day 5, by it-tyo.w00182; DB shows ABSENT): A-TYO-46864 monitor Assigned to Mori Yamato. Stored value: {"emp":"E-TYO-1019"}
- DB `IT-TYO/asset/A-TYO-8146/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1019"}
- QUERY SELECT asset WHERE holder=E-TYO-1019 → ["A-TYO-3893", "A-TYO-46864", "A-TYO-8146"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-3893", "A-TYO-8146"], "dept": "Sales Section 1", "grade": 4}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-01183 (need IT-TYO/E-TYO-1019/assets): matcher says **missing**
record text: A-TYO-46864 monitor Assigned to Mori Yamato. Stored value: {"emp":"E-TYO-1019"}
What the requester received from IT-TYO during this task:
```
[Reply 1] (ok)
- E-TYO-1019 | current assets | A-TYO-3893, A-TYO-8146 |  | db, day -20: Reply 1: D1
```

## CASE 25: qwen3.5-27b · ingress · s14 · W-00140 · class A · day 14 · template lookup
### Task as given to the requester
Check Jiho (Assistant Manager)'s current department, grade and assets held.
[Request scope] procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- dept: Employee's current department.
- grade: Employee's current grade.
- assets: Asset IDs the employee currently holds (any order; empty list if none).
- Public region list, in order: SEL, TYO.
### Gold answer
{"dept": "Dev Team 2", "grade": 2, "assets": []}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"dept": "Dev Team 1", "grade": 2, "assets": []}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-2012/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2012"}
- DB `HR-SEL/emp/E-SEL-2012/profile` v1 (recorded day -3, registered day -2): {"dept": "Dev Team 2", "grade": 2, "contract": "regular", "hire_day": -3, "status": "active"}
**need IT-SEL/E-SEL-2012/assets** (group IT-SEL, class A, local=False)
- QUERY SELECT asset WHERE holder=E-SEL-2012 → []
### Model answer and official verdict
answer: {"assets": [], "dept": "Dev Team 2", "grade": 2}
official exact match: 1 (3/3 slots)

## CASE 26: qwen3.5-27b · ingress · s13 · W-00059 · class A · day 6 · template diag
### Task as given to the requester
Invoice INV-74377 (671,961 KRW, beneficiary Fujita-san, asset A-TYO-17052, provisional approval CMT-00078) does not match. Find the cause.
[Request scope] target supplier=V-TYO-2; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
**need FIN-TYO/CMT-00078/status** (group FIN-TYO, class A, local=False)
- NEGATIVE: {"query": "FIN-TYO catalog commits/CMT-00078", "result": []}
- RECORD FR-01263 (operational/pending_intent, day 6, by fin-tyo.a1; DB shows n/a): CMT-00078 Support Section meeting room equipment provisional approval 706,412 KRW under review, settlement expected day 10.
**need HR-TYO/E-TYO-2008/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2008"}
- DB `HR-TYO/emp/E-TYO-2008/profile` v2 (recorded day 3, registered day 5): {"dept": "Dev Section 2", "grade": 3, "contract": "contractor", "hire_day": -1, "status": "active"}
**need IT-TYO/E-TYO-2008/assets** (group IT-TYO, class None, local=True)
- QUERY SELECT asset WHERE holder=E-TYO-2008 → []
**need PROC-TYO/receipt/CMT-00078** (group PROC-TYO, class A, local=False)
- QUERY {"key": "PROC-TYO/receipt/CMT-00078/received", "asof": 6} → "ABSENT"
**need PROC-TYO/vendor/V-TYO-2/status** (group PROC-TYO, class A, local=False)
- NEGATIVE: {"query": "PROC-TYO exclusion order for supplier V-TYO-2", "result": []}
**need LEGAL-TYO/E-TYO-2008/contract** (group LEGAL-TYO, class A, local=False)
- DB `LEGAL-TYO/contract/E-TYO-2008/terms` v1 (recorded day 1, registered day 4): {"allowed_tier": "basic", "expiry": 120, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01033 (operational/exception, day 2, by legal-tyo.a3; DB shows n/a): Equipment exception of Fujita Riku higher tiers including premium allowed until day 22 for a project, legal check done.
- RECORD FR-01146 (operational/observation, day 4, by legal-tyo.n0017; DB shows n/a): NDA of Fujita Riku signed copy verified, NDA check step can be skipped until day 21.
**need FIN-TYO/rule/invoice_match_precedence** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.invoice_match_precedence: {"id": "FIN-TYO.invoice_match_precedence", "group": "FIN-TYO", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "AMOUNT_MISMATCH"}
official exact match: 0 (0/1 slots)