## CASE 1: qwen3.5-27b · direct · s13 · W-00097 · class A · day 10 · template renewal
### Task as given to the requester
Sol (Assistant Manager)'s contract is about to expire. Can it be renewed, and if not, which assets must be recovered?
[Request scope] renewal cost=662,984 KRW; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"renew": false, "recover_assets": []}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"renew": false, "recover_assets": ["A-SEL-49655", "A-SEL-63722", "A-SEL-90388"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need LEGAL-SEL/E-SEL-2002/contract** (group LEGAL-SEL, class A, local=False)
- DB `LEGAL-SEL/contract/E-SEL-2002/terms` v3 (recorded day -3, registered day -1): {"allowed_tier": "standard", "expiry": 49, "nda": true}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00574 (operational/exception, day -10, by legal-sel.a3; DB shows n/a): Equipment exception of Namgung Sol higher tiers including premium allowed until day 15 for a project, legal check done.
- RECORD FR-01008 (operational/observation, day 1, by legal-sel.a5; DB shows n/a): NDA of Namgung Sol signed copy verified, NDA check step can be skipped until day 15.
- RULE LEGAL-SEL.renewal_policy: {"id": "LEGAL-SEL.renewal_policy", "group": "LEGAL-SEL", "title": "Contract renewal", "params": {"min_grade": 2}, "text": "Renewal conditions: active employment, grade 2 or higher, renewal cost within the department's available budget."}
**need HR-SEL/E-SEL-2002/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2002"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v2 (recorded day -10, registered day -8): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -11, "status": "exited"}
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-01347 (operational/exception, day 7, by fin-sel.n0005; DB shows n/a): Sales Team 2 capex executing office agreed that TYO finance executes it until day 28.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Sales Team 2/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Sales Team 2/remaining` v2 (recorded day 7, registered day 10): 3159648
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00026/status` v2 (recorded day 3, registered day 4): {"status": "settled", "amount": 839113, "expected_settle": 3}
- DB `FIN-TYO/commit/CMT-00028/status` v2 (recorded day 4, registered day 5): {"status": "settled", "amount": 959706, "expected_settle": 4}
- DB `FIN-TYO/commit/CMT-00044/status` v2 (recorded day 4, registered day 7): {"status": "settled", "amount": 386882, "expected_settle": 4}
- RECORD FR-01470 (operational/pending_intent, day 9, by fin-tyo.n0013; DB shows n/a): CMT-00095 Sales Team 2 monitor provisional approval 784,781 KRW under review, settlement expected day 22.
- RECORD FR-01483 (operational/pending_intent, day 10, by fin-tyo.n0013; DB shows n/a): CMT-00096 Sales Team 2 order (incl. shipping) provisional approval (order of W-00083) 617,018 KRW under review, settlement expected day 14.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00095", "CMT-00096"]
**need IT-SEL/E-SEL-2002/assets** (group IT-SEL, class A, local=False)
- QUERY SELECT asset WHERE holder=E-SEL-2002 → []
### Model answer and official verdict
answer: {"recover_assets": [], "renew": false}
official exact match: 1 (2/2 slots)

## CASE 2: qwen3.5-27b · direct · s13 · W-00119 · class A · day 12 · template lookup
### Task as given to the requester
Check Ito-san's current department, grade and assets held.
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
{"dept": "Sales Section 2", "grade": 4, "assets": ["A-TYO-8307"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Support Section", "grade": 4, "assets": ["A-TYO-8307"]}, "partial": null, "neardup": {"dept": "Sales Section 2", "grade": 5, "assets": ["A-TYO-8307"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1005/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1005"}
- DB `HR-TYO/emp/E-TYO-1005/profile` v3 (recorded day 1, registered day 2): {"dept": "Sales Section 2", "grade": 4, "contract": "regular", "hire_day": -110, "status": "active"}
**need IT-TYO/E-TYO-1005/assets** (group IT-TYO, class A, local=False)
- DB `IT-TYO/asset/A-TYO-8307/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1005"}
- QUERY SELECT asset WHERE holder=E-TYO-1005 → ["A-TYO-8307"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-8307"], "dept": "Sales Section 2", "grade": 4}
official exact match: 1 (3/3 slots)

## CASE 3: qwen3.5-27b · direct · s12 · W-00024 · class A · day 3 · template conflict
### Task as given to the requester
Check whether CMT-00041 is still live and what amount to count for it. We are hearing conflicting things.
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
{"status": "settled", "amount": 0}
### Counterfactual answers (generator)
{"stale": {"status": "pending", "amount": 736538}, "partial": null, "neardup": {"status": "pending", "amount": 309331}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00041/effective_status** (group FIN-TYO, class A, local=False)
- CATALOG: {"group": "FIN-TYO", "key": "commits/CMT-00041"}
- DB `FIN-TYO/commit/CMT-00041/status` v2 (recorded day 2, registered day 3): {"status": "settled", "amount": 736538, "expected_settle": 2}
- RULE FIN-TYO.status_authority: {"id": "FIN-TYO.status_authority", "group": "FIN-TYO", "title": "Validity of provisional approval status", "params": {"authoritative": ["db", "owner_record"], "informal_excluded": true}, "text": "Only the registered record and the handling officer's processing record determine a provisional approval's status. Informal remarks or discussions do not change it."}
- RECORD FR-00721 (operational/observation, day -5, by fin-tyo.a1; DB shows n/a): CMT-00041 item someone suggested cancelling it (not decided).
### Model answer and official verdict
answer: {"amount": 0, "status": "settled"}
official exact match: 1 (2/2 slots)

## CASE 4: qwen3.5-27b · direct · s13 · W-00029 · class B · day 3 · template lookup
### Task as given to the requester
Check Hashimoto-san's current department, grade and assets held.
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
{"dept": "Planning Section", "grade": 2, "assets": ["A-TYO-21706"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Sales Section 2", "grade": 2, "assets": ["A-TYO-21706"]}, "partial": {"dept": "Sales Section 2", "grade": 2, "assets": ["A-TYO-21706"]}, "neardup": {"dept": "Dev Section 1", "grade": 3, "assets": ["A-TYO-21706"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2004/profile** (group HR-TYO, class B, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2004"}
- RECORD FR-01015 [decision-critical] (db_pending/observation, day 2, by hr-tyo.a5; DB shows 2): HR record of Hashimoto Moe moved from Sales Section 2 to Planning Section, grade 2, contractor. Stored value: {"contract":"contractor","dept":"Planning Section","grade":2,"hire_day":-8,"status":"active"}
**need IT-TYO/E-TYO-2004/assets** (group IT-TYO, class A, local=False)
- RECORD FR-01122 [decision-critical] (db_pending/observation, day 3, by it-tyo.w00159; DB shows ABSENT): A-TYO-21706 workstation Assigned to Hashimoto Moe. Stored value: {"emp":"E-TYO-2004"}
- QUERY SELECT asset WHERE holder=E-TYO-2004 → ["A-TYO-21706"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-21706"], "dept": "Sales Section 2", "grade": 2}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-01015 (need HR-TYO/E-TYO-2004/profile): matcher says **stale**
record text: HR record of Hashimoto Moe moved from Sales Section 2 to Planning Section, grade 2, contractor. Stored value: {"contract":"contractor","dept":"Planning Section","grade":2,"hire_day":-8,"status":"active"}
What the requester received from HR-TYO during this task:
```
- E-TYO-2004 | department | Sales Section 2 |  | db, day 0: D1
- E-TYO-2004 | grade | 2 |  | db, day 0: D1
```
### MATCHER CHECK FR-01122 (need IT-TYO/E-TYO-2004/assets): matcher says **missing**
record text: A-TYO-21706 workstation Assigned to Hashimoto Moe. Stored value: {"emp":"E-TYO-2004"}
What the requester received from IT-TYO during this task:
```
- E-TYO-2004 | assets held | A-TYO-21706 |  | history, day 3: H274
```

## CASE 5: qwen3.5-27b · direct · s14 · W-00053 · class B · day 6 · template alloc
### Task as given to the requester
Allocate Design Suite seats to Dev Section 2, Sales Section 1, Support Section in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
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
{"alloc": [4, 5, 2], "transfer": 6, "buy": 2, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [5, 5, 2], "transfer": 6, "buy": 3, "unmet": 0}, "partial": {"alloc": [5, 5, 2], "transfer": 6, "buy": 3, "unmet": 0}, "neardup": {"alloc": [3, 5, 2], "transfer": 6, "buy": 1, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/license/Design Suite** (group IT-TYO, class None, local=True)
- DB `IT-TYO/lic/Design Suite/seats` v3 (recorded day -7, registered day -5): {"seats": 21, "used": 18}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need HR-TYO/Dev Section 2/planning_headcount** (group HR-TYO, class B, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-01260 [decision-critical] (db_pending/observation, day 6, by hr-tyo.a5; DB shows 3): HR record of Yamamoto Hina moved from Dev Section 2 to Support Section, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Support Section","grade":3,"hire_day":-351,"status":"active"}
- DB `HR-TYO/emp/E-TYO-1008/profile` v3 (recorded day 2, registered day 4): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -52, "status": "active"}
- RECORD FR-01026 [decision-critical] (operational/pending_intent, day 1, by hr-tyo.a5; DB shows n/a): Transfer of Yoshida Kaede approved from Planning Section to Dev Section 2, effective day 12 (stays in Planning Section until then).
- DB `HR-TYO/emp/E-TYO-1013/profile` v2 (recorded day -2, registered day 1): {"dept": "Dev Section 2", "grade": 2, "contract": "regular", "hire_day": -705, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v3 (recorded day -7, registered day -6): {"dept": "Dev Section 2", "grade": 5, "contract": "contractor", "hire_day": -784, "status": "active"}
- RECORD FR-01051 [decision-critical] (operational/pending_intent, day 2, by hr-tyo.a5; DB shows n/a): Transfer of Maeda An approved from Planning Section to Dev Section 2, effective day 13 (stays in Planning Section until then).
- QUERY COUNT(emp WHERE region=TYO AND dept=Dev Section 2 AND status=active) → 2
**need HR-TYO/Sales Section 1/planning_headcount** (group HR-TYO, class B, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1003/profile` v3 (recorded day 4, registered day 5): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -639, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1004/profile` v4 (recorded day 5, registered day 6): {"dept": "Sales Section 1", "grade": 5, "contract": "contractor", "hire_day": -256, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1008/profile` v3 (recorded day 2, registered day 4): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -52, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1015/profile` v3 (recorded day -5, registered day -4): {"dept": "Sales Section 2", "grade": 3, "contract": "regular", "hire_day": -440, "status": "active"}
- RECORD FR-01090 [decision-critical] (operational/pending_intent, day 2, by hr-tyo.a4; DB shows n/a): Transfer of Kimura Yuito approved from Sales Section 2 to Sales Section 1, effective day 8 (stays in Sales Section 2 until then).
- DB `HR-TYO/emp/E-TYO-1016/profile` v2 (recorded day -7, registered day -4): {"dept": "Sales Section 1", "grade": 2, "contract": "regular", "hire_day": -506, "status": "exited"}
- RECORD FR-01173 [decision-critical] (operational/pending_intent, day 4, by hr-tyo.a4; DB shows n/a): Sales Section 1 confirmed hire OF-00016 starts day 7, regular (not yet in HR records).
- QUERY COUNT(emp WHERE region=TYO AND dept=Sales Section 1 AND status=active) → 3
**need HR-TYO/Support Section/planning_headcount** (group HR-TYO, class B, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-00895 [decision-critical] (operational/pending_intent, day -2, by hr-tyo.a5; DB shows n/a): Transfer of Ono Ken approved from Support Section to Dev Section 1, effective day 7 (stays in Support Section until then).
- DB `HR-TYO/emp/E-TYO-1004/profile` v4 (recorded day 5, registered day 6): {"dept": "Sales Section 1", "grade": 5, "contract": "contractor", "hire_day": -256, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1005/profile` v4 (recorded day 3, registered day 6): {"dept": "Dev Section 1", "grade": 3, "contract": "regular", "hire_day": -396, "status": "active"}
- RECORD FR-01260 [decision-critical] (db_pending/observation, day 6, by hr-tyo.a5; DB shows 3): HR record of Yamamoto Hina moved from Dev Section 2 to Support Section, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Support Section","grade":3,"hire_day":-351,"status":"active"}
- DB `HR-TYO/emp/E-TYO-1011/profile` v2 (recorded day -5, registered day -2): {"dept": "Planning Section", "grade": 1, "contract": "contractor", "hire_day": -356, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1019/profile` v3 (recorded day -4, registered day -1): {"dept": "Dev Section 1", "grade": 2, "contract": "regular", "hire_day": -365, "status": "active"}
- RECORD FR-00920 [decision-critical] (operational/pending_intent, day -1, by hr-tyo.a5; DB shows n/a): Transfer of Hashimoto Moe approved from Planning Section to Support Section, effective day 8 (stays in Planning Section until then).
- DB `HR-TYO/emp/E-TYO-2006/profile` v2 (recorded day -12, registered day -11): {"dept": "Support Section", "grade": 1, "contract": "regular", "hire_day": -12, "status": "exited"}
- DB `HR-TYO/emp/E-TYO-2008/profile` v2 (recorded day -1, registered day 0): {"dept": "Planning Section", "grade": 2, "contract": "regular", "hire_day": -9, "status": "active"}
- DB `HR-TYO/emp/E-TYO-2009/profile` v2 (recorded day -4, registered day -3): {"dept": "Support Section", "grade": 3, "contract": "contractor", "hire_day": -7, "status": "active"}
- RECORD FR-01194 [decision-critical] (operational/pending_intent, day 4, by hr-tyo.a5; DB shows n/a): Transfer of Fujita Riku approved from Support Section to Sales Section 2, effective day 8 (stays in Support Section until then).
- QUERY COUNT(emp WHERE region=TYO AND dept=Support Section AND status=active) → 3
**need IT-SEL/license/Design Suite** (group IT-SEL, class B, local=False)
- DB `IT-SEL/lic/Design Suite/seats` v5 (recorded day -3, registered day -2): {"seats": 27, "used": 12}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01091 [decision-critical] (operational/pending_intent, day 2, by it-sel.n0002; DB shows n/a): Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 12.
**need IT-TYO/rule/seat_transfer_share** (group IT-TYO, class None, local=True)
- RULE IT-TYO.seat_transfer_share: {"id": "IT-TYO.seat_transfer_share", "group": "IT-TYO", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-TYO/rule/seat_purchase_line** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.seat_purchase_line: {"id": "FIN-TYO.seat_purchase_line", "group": "FIN-TYO", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-TYO/Dev Section 2/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Dev Section 2/remaining` v2 (recorded day 1, registered day 2): 1761303
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00017/status` v2 (recorded day -5, registered day -2): {"status": "settled", "amount": 269157, "expected_settle": -5}
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Dev Section 2 AND status IN ['reviewing', 'pending'] → []
**need IT-TYO/rule/seat_price** (group IT-TYO, class None, local=True)
- RULE IT-TYO.seat_price: {"id": "IT-TYO.seat_price", "group": "IT-TYO", "title": "Standard seat price", "params": {"price": 218619}, "text": "When there is no supplier price, one seat costs 218,619 KRW."}
### Model answer and official verdict
answer: {"alloc": [3, 5, 2], "buy": 7, "transfer": 0, "unmet": 0}
official exact match: 0 (1/4 slots)
### MATCHER CHECK FR-01260 (need HR-TYO/Dev Section 2/planning_headcount): matcher says **missing**
record text: HR record of Yamamoto Hina moved from Dev Section 2 to Support Section, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Support Section","grade":3,"hire_day":-351,"status":"active"}
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01026 (need HR-TYO/Dev Section 2/planning_headcount): matcher says **missing**
record text: Transfer of Yoshida Kaede approved from Planning Section to Dev Section 2, effective day 12 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01051 (need HR-TYO/Dev Section 2/planning_headcount): matcher says **missing**
record text: Transfer of Maeda An approved from Planning Section to Dev Section 2, effective day 13 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01090 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Kimura Yuito approved from Sales Section 2 to Sales Section 1, effective day 8 (stays in Sales Section 2 until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01173 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Sales Section 1 confirmed hire OF-00016 starts day 7, regular (not yet in HR records).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00895 (need HR-TYO/Support Section/planning_headcount): matcher says **missing**
record text: Transfer of Ono Ken approved from Support Section to Dev Section 1, effective day 7 (stays in Support Section until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01260 (need HR-TYO/Support Section/planning_headcount): matcher says **missing**
record text: HR record of Yamamoto Hina moved from Dev Section 2 to Support Section, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Support Section","grade":3,"hire_day":-351,"status":"active"}
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00920 (need HR-TYO/Support Section/planning_headcount): matcher says **missing**
record text: Transfer of Hashimoto Moe approved from Planning Section to Support Section, effective day 8 (stays in Planning Section until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01194 (need HR-TYO/Support Section/planning_headcount): matcher says **missing**
record text: Transfer of Fujita Riku approved from Support Section to Sales Section 2, effective day 8 (stays in Support Section until then).
What the requester received from HR-TYO during this task:
```
Found headcount values from department_employees records. Cannot determine planning headcount as no information about confirmed hires or transfers within 7 days is available in my records.
- Dev Section 2 | headcount | 3 |  | db, day unknown: D1
- Sales Section 1 | headcount | 3 |  | db, day unknown: D2
- Support Section | headcount | 2 |  | db, day unknown: D3
missing: planning headcount for Dev Section 2; planning headcount for Sales Section 1; planning headcount for Support Section
---
- Dev Section 2 | current headcount | 3 |  | db, day unknown: D1
- Dev Section 2 | planning headcount | 3 |  | rule, day fixed: planning_headcount
- Sales Section 1 | current headcount | 3 |  | db, day unknown: D2
- Sales Section 1 | confirmed hire within 7 days | 1 |  | history, day 4: H91
- Sales Section 1 | transfer within 7 days | 1 |  | history, day 2: H76
- Sales Section 1 | planning headcount | 5 |  | rule, day fixed: planning_headcount
- Support Section | current headcount | 2 |  | db, day unknown: D3
- Support Section | planning headcount | 2 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01091 (need IT-SEL/license/Design Suite): matcher says **missing**
record text: Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 12.
What the requester received from IT-SEL during this task:
```
(nothing received from this group)
```

## CASE 6: qwen3.5-27b · direct · s14 · W-00039 · class B · day 4 · template vendor
### Task as given to the requester
Marketing Team needs a workstation. Pick a compliant supplier within budget.
[Request scope] item=workstation; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"vendor": "V-SEL-0", "option": "Q-V-SEL-0-WSS", "amount": 1406998, "approver": "division_head", "budget_after": 1219396, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": null, "partial": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-WSS", "amount": 1406998, "approver": "division_head", "budget_after": 1887575, "blocked_by": null}, "neardup": {"vendor": null, "option": null, "amount": null, "approver": null, "budget_after": null, "blocked_by": "budget"}, "wrong_owner": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-WSS", "amount": 1406998, "approver": "division_head", "budget_after": 1887575, "blocked_by": null}}
### World facts behind the gold (by need)
**need FIN-SEL/Marketing Team/budget_schedule** (group FIN-SEL, class B, local=False)
- RECORD FR-00582 [decision-critical] (operational/exception, day -9, by fin-sel.a5; DB shows n/a): Marketing Team capex executing office agreed that TYO finance executes it until day 13.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Marketing Team/budget_schedule** (group FIN-TYO, class B, local=False)
- DB `FIN-TYO/line/Marketing Team/remaining` v1 (recorded day -9, registered day -6): 2900279
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00045/status` v2 (recorded day -1, registered day 2): {"status": "settled", "amount": 499698, "expected_settle": -1}
- RECORD FR-01125 (db_pending/observation, day 3, by fin-tyo.a2; DB shows 1): CMT-00062 Marketing Team provisional approval settled. Stored value: {"amount":870914,"expected_settle":3,"status":"settled"}
- RECORD FR-01182 (db_pending/observation, day 4, by fin-tyo.a3; DB shows 1): CMT-00075 Marketing Team provisional approval settled. Stored value: {"amount":578354,"expected_settle":4,"status":"settled"}
- RECORD FR-01199 [decision-critical] (operational/pending_intent, day 4, by fin-tyo.a2; DB shows n/a): CMT-00096 Marketing Team meeting room equipment provisional approval 273,885 KRW under review, settlement expected day 17.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Marketing Team AND status IN ['reviewing', 'pending'] → ["CMT-00096"]
**need PROC-SEL/quotes/workstation** (group PROC-SEL, class None, local=True)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00570 (operational/handover, day -10, by proc-sel.w00065; DB shows n/a): Supplier V-SEL-3 exclude from comparisons until day 4 due to a quality issue.
- RECORD FR-00713 (operational/handover, day -6, by proc-sel.w00088; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 6 due to a quality issue.
- RECORD FR-00983 (operational/handover, day 0, by proc-sel.w00136; DB shows n/a): Supplier V-SEL-1 exclude from comparisons until day 10 due to a quality issue.
- RECORD FR-01082 (operational/observation, day 2, by proc-sel.w00155; DB shows n/a): Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01168 (operational/observation, day 4, by proc-sel.w00172; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 4 days until day 16.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-WSP/amount` v1 (recorded day -20, registered day -20): 2297147
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-WSS/amount` v1 (recorded day -20, registered day -20): 1406998
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day -5, registered day -4): 12
- DB `PROC-SEL/quote/Q-V-SEL-1-WSP/amount` v1 (recorded day -20, registered day -20): 1695872
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day -5, registered day -4): 12
- DB `PROC-SEL/quote/Q-V-SEL-1-WSS/amount` v2 (recorded day 1, registered day 4): 1360147
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-WSS/amount` v1 (recorded day -20, registered day -20): 1592652
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v4 (recorded day -6, registered day -3): 6
- DB `PROC-SEL/quote/Q-V-SEL-3-WSP/amount` v2 (recorded day -14, registered day -13): 2085014
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v4 (recorded day -6, registered day -3): 6
- DB `PROC-SEL/quote/Q-V-SEL-3-WSS/amount` v2 (recorded day -16, registered day -13): 963358
**need LEGAL-SEL/residency** (group LEGAL-SEL, class A, local=False)
- RULE LEGAL-SEL.residency: {"id": "LEGAL-SEL.residency", "group": "LEGAL-SEL", "title": "Data residency", "params": {"restricted_depts": ["Sales Team 1", "Sales Team 2"]}, "text": "These departments may not use equipment from offshore suppliers: Sales Team 1, Sales Team 2."}
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"amount": null, "approver": null, "blocked_by": "vendor_excluded", "budget_after": null, "option": null, "vendor": null}
official exact match: 0 (0/6 slots)
### MATCHER CHECK FR-00582 (need FIN-SEL/Marketing Team/budget_schedule): matcher says **missing**
record text: Marketing Team capex executing office agreed that TYO finance executes it until day 13.
What the requester received from FIN-SEL during this task:
```
Cannot calculate available budget for Marketing Team due to missing earmark information. Budget line balance is 3,294,573 KRW with no pending provisional approvals, but earmark deductions cannot be determined without their amounts and end days.
- Marketing Team | budget line balance | 3294573 |  | db, day -3: D1
- Marketing Team | sum of items under review or provisionally approved | 0 |  | db, day unknown: D2
- Marketing Team | sum of earmarks in validity period | unknown |  | unknown, day unknown: history
- Marketing Team | available budget | cannot calculate - missing earmark information |  | rule, day fixed: pending_deduction
missing: Marketing Team earmark amounts and end days from history records (H135, H79)
---
Found budget balance and base allocation for Marketing Team, but earmark details (amounts and end days) are not available in records or database.
- Marketing Team | budget line balance | 3294573 |  | db, day -3: D1
- Marketing Team | quarterly base allocation | 2900279 |  | db, day -20: D3
- Marketing Team | department provisional approvals | CMT-00005: 586827 KRW, expected_settle: -8, status: cancelled; CMT-00026: 206503 KRW, expected_settle: -5, status: settled |  | db, day unknown: D2
missing: Marketing Team earmark amounts and end days from H135
---
Cannot determine if Marketing Team has sufficient budget for 963,358 KRW because the end days of earmarks (from H135 and H79) are not specified in records, making it impossible to calculate the sum of earmarks in validity period and thus the actual available budget.
- Marketing Team | budget line balance | 3294573 |  | db, day -3: D1
- Marketing Team | sum of items under review or provisionally approved | 0 |  | db, day unknown: D2
- Marketing Team | sum of earmarks in validity period | unknown - end days not specified in records |  | history, day -6: H135,H79
- Marketing Team | available budget | cannot calculate - missing earmark end days |  | rule, day fixed: pending_deduction
- Marketing Team | sufficient for 963358 KRW | cannot determine - available budget unknown due to missing earmark details |  | rule, day fixed: pending_deduction
missing: end days of Marketing Team earmarks from H135 and H79; sum of earmarks in validity period for Marketing Team on day 4; actual available budget for Marketing Team after all deductions
---
No active earmark details (amounts and end days) for Marketing Team could be confirmed from available records. Database shows no pending provisional approvals, but earmark information from history records (H135) is incomplete with truncated values.
- Marketing Team | budget line balance | 3294573 |  | db, day -3: D1
- Marketing Team | department provisional approvals | CMT-00005: 586827 KRW, cancelled; CMT-00026: 206503 KRW, settled |  | db, day unknown: D2
missing: active earmarks for Marketing Team on day 4 - amounts and end days not found in accessible records
```
### MATCHER CHECK FR-01199 (need FIN-TYO/Marketing Team/budget_schedule): matcher says **missing**
record text: CMT-00096 Marketing Team meeting room equipment provisional approval 273,885 KRW under review, settlement expected day 17.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```

## CASE 7: qwen3.5-27b · direct · s13 · W-00094 · class C · day 10 · template contract_gate
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
answer: {"contract_tier": "standard", "expiry": 258, "it_tier": "premium", "nda_step": true}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-00500 (need LEGAL-TYO/E-TYO-1012/contract): matcher says **missing**
record text: Equipment exception of Yamada Sou higher tiers including premium allowed until day 12 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
Contract terms for E-TYO-1012: allowed tier is standard, expiry day is 258. No legal exceptions found in records.
- E-TYO-1012 | allowed tier | standard |  | db, day 10: D1
- E-TYO-1012 | expiry day | 258 |  | db, day 10: D1
missing: Legal exceptions for E-TYO-1012
---
Contract terms show NDA is required (true). Per contractor_policy, standard equipment for a contractor with NDA clause needs an NDA check unless a verified NDA copy exists and is still valid. Cannot confirm if verified NDA exists.
- E-TYO-1012 | nda required | true |  | db, day 10: D1
- contractor_policy | Standard equipment for contractor with NDA clause requirement | needs an NDA check unless verified NDA copy exists and is still valid |  | rule, day fixed: contractor_policy
missing: Whether E-TYO-1012 has a verified NDA copy on file that is still valid
---
Contract for E-TYO-1012 has NDA clause (nda=true). Standard equipment requires NDA check per contractor_policy unless verified NDA copy exists, but verified NDA copy status is not available in my records.
- E-TYO-1012 | NDA clause in contract | true |  | db, day 10: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 10: D1
- contractor_policy | rule for NDA check | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: contractor_policy
missing: Verified NDA copy status for E-TYO-1012 - whether a signed NDA copy has been verified and is still valid; Whether standard equipment requires an NDA check step for E-TYO-1012 (depends on verified NDA copy status which is not available)
```
### MATCHER CHECK FR-01092 (need LEGAL-TYO/E-TYO-1012/contract): matcher says **missing**
record text: NDA of Yamada Sou signed copy verified, NDA check step can be skipped until day 25.
What the requester received from LEGAL-TYO during this task:
```
Contract terms for E-TYO-1012: allowed tier is standard, expiry day is 258. No legal exceptions found in records.
- E-TYO-1012 | allowed tier | standard |  | db, day 10: D1
- E-TYO-1012 | expiry day | 258 |  | db, day 10: D1
missing: Legal exceptions for E-TYO-1012
---
Contract terms show NDA is required (true). Per contractor_policy, standard equipment for a contractor with NDA clause needs an NDA check unless a verified NDA copy exists and is still valid. Cannot confirm if verified NDA exists.
- E-TYO-1012 | nda required | true |  | db, day 10: D1
- contractor_policy | Standard equipment for contractor with NDA clause requirement | needs an NDA check unless verified NDA copy exists and is still valid |  | rule, day fixed: contractor_policy
missing: Whether E-TYO-1012 has a verified NDA copy on file that is still valid
---
Contract for E-TYO-1012 has NDA clause (nda=true). Standard equipment requires NDA check per contractor_policy unless verified NDA copy exists, but verified NDA copy status is not available in my records.
- E-TYO-1012 | NDA clause in contract | true |  | db, day 10: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 10: D1
- contractor_policy | rule for NDA check | Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: contractor_policy
missing: Verified NDA copy status for E-TYO-1012 - whether a signed NDA copy has been verified and is still valid; Whether standard equipment requires an NDA check step for E-TYO-1012 (depends on verified NDA copy status which is not available)
```

## CASE 8: qwen3.5-27b · direct · s13 · W-00036 · class C · day 4 · template alloc
### Task as given to the requester
Allocate Design Suite seats to Sales Section 1, Dev Section 1, Planning Section in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
[Request scope] procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"alloc": [6, 3, 3], "transfer": 0, "buy": 9, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [5, 3, 3], "transfer": 0, "buy": 8, "unmet": 0}, "partial": {"alloc": [5, 3, 3], "transfer": 0, "buy": 8, "unmet": 0}, "neardup": {"alloc": [5, 3, 3], "transfer": 0, "buy": 8, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/license/Design Suite** (group IT-TYO, class None, local=True)
- DB `IT-TYO/lic/Design Suite/seats` v3 (recorded day -11, registered day -9): {"seats": 20, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need HR-TYO/Sales Section 1/planning_headcount** (group HR-TYO, class C, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1000/profile` v2 (recorded day -4, registered day -3): {"dept": "Sales Section 1", "grade": 5, "contract": "regular", "hire_day": -490, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1002/profile` v5 (recorded day 2, registered day 3): {"dept": "Sales Section 1", "grade": 1, "contract": "regular", "hire_day": -807, "status": "exited"}
- DB `HR-TYO/emp/E-TYO-1007/profile` v4 (recorded day 2, registered day 4): {"dept": "Sales Section 2", "grade": 3, "contract": "regular", "hire_day": -797, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1011/profile` v3 (recorded day 3, registered day 4): {"dept": "Planning Section", "grade": 1, "contract": "regular", "hire_day": -895, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1012/profile` v3 (recorded day -10, registered day -9): {"dept": "Dev Section 1", "grade": 5, "contract": "contractor", "hire_day": -90, "status": "active"}
- RECORD FR-00807 [decision-critical] (operational/pending_intent, day -3, by hr-tyo.a5; DB shows n/a): Transfer of Yamada Sou approved from Dev Section 1 to Sales Section 1, effective day 8 (stays in Dev Section 1 until then).
- DB `HR-TYO/emp/E-TYO-1015/profile` v3 (recorded day -10, registered day -7): {"dept": "Dev Section 2", "grade": 3, "contract": "regular", "hire_day": -47, "status": "active"}
- RECORD FR-00967 [decision-critical] (operational/pending_intent, day 1, by hr-tyo.a5; DB shows n/a): Transfer of Kimura Yuito approved from Dev Section 2 to Sales Section 1, effective day 7 (stays in Dev Section 2 until then).
- RECORD FR-00987 [decision-critical] (operational/pending_intent, day 1, by hr-tyo.a1; DB shows n/a): Transfer of Shimizu Hayate approved from Support Section to Sales Section 1, effective day 10 (stays in Support Section until then).
- DB `HR-TYO/emp/E-TYO-2007/profile` v2 (recorded day 2, registered day 4): {"dept": "Sales Section 1", "grade": 3, "contract": "regular", "hire_day": -7, "status": "exited"}
- RECORD FR-01085 (db_pending/observation, day 3, by hr-tyo.n0008; DB shows 1): HR record of Fujita Riku moved from Sales Section 1 to Dev Section 2, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Dev Section 2","grade":3,"hire_day":-1,"status":"active"}
- RECORD FR-01064 [decision-critical] (operational/pending_intent, day 2, by hr-tyo.a4; DB shows n/a): Sales Section 1 confirmed hire OF-00017 starts day 5, contractor (not yet in HR records).
- QUERY COUNT(emp WHERE region=TYO AND dept=Sales Section 1 AND status=active) → 2
**need HR-TYO/Dev Section 1/planning_headcount** (group HR-TYO, class C, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1000/profile` v2 (recorded day -4, registered day -3): {"dept": "Sales Section 1", "grade": 5, "contract": "regular", "hire_day": -490, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1003/profile` v2 (recorded day -15, registered day -14): {"dept": "Dev Section 1", "grade": 5, "contract": "regular", "hire_day": -608, "status": "exited"}
- DB `HR-TYO/emp/E-TYO-1004/profile` v2 (recorded day -2, registered day 0): {"dept": "Dev Section 2", "grade": 3, "contract": "contractor", "hire_day": -798, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1010/profile` v4 (recorded day 2, registered day 4): {"dept": "Dev Section 1", "grade": 1, "contract": "regular", "hire_day": -592, "status": "exited"}
- DB `HR-TYO/emp/E-TYO-1012/profile` v3 (recorded day -10, registered day -9): {"dept": "Dev Section 1", "grade": 5, "contract": "contractor", "hire_day": -90, "status": "active"}
- RECORD FR-00807 [decision-critical] (operational/pending_intent, day -3, by hr-tyo.a5; DB shows n/a): Transfer of Yamada Sou approved from Dev Section 1 to Sales Section 1, effective day 8 (stays in Dev Section 1 until then).
- RECORD FR-01133 [decision-critical] (db_pending/observation, day 4, by hr-tyo.a4; DB shows 3): HR record of Matsumoto Tsumugi moved from Dev Section 1 to Sales Section 2, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Section 2","grade":1,"hire_day":-427,"status":"active"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v2 (recorded day 1, registered day 4): {"dept": "Support Section", "grade": 3, "contract": "regular", "hire_day": -776, "status": "active"}
- RECORD FR-00679 [decision-critical] (operational/pending_intent, day -7, by hr-tyo.a5; DB shows n/a): Transfer of Yamaguchi Mio approved from Dev Section 1 to Support Section, effective day 5 (stays in Dev Section 1 until then).
- RECORD FR-00940 [decision-critical] (operational/pending_intent, day 0, by hr-tyo.a5; DB shows n/a): Transfer of Ishikawa Sota approved from Dev Section 1 to Dev Section 2, effective day 6 (stays in Dev Section 1 until then).
- RECORD FR-01085 (db_pending/observation, day 3, by hr-tyo.n0008; DB shows 1): HR record of Fujita Riku moved from Sales Section 1 to Dev Section 2, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Dev Section 2","grade":3,"hire_day":-1,"status":"active"}
- RECORD FR-01137 [decision-critical] (operational/pending_intent, day 4, by hr-tyo.a5; DB shows n/a): Transfer of Fujita Riku approved from Dev Section 2 to Dev Section 1, effective day 7 (stays in Dev Section 2 until then).
- RECORD FR-01063 [decision-critical] (operational/pending_intent, day 2, by hr-tyo.a1; DB shows n/a): Dev Section 1 confirmed hire OF-00016 starts day 5, contractor (not yet in HR records).
- QUERY COUNT(emp WHERE region=TYO AND dept=Dev Section 1 AND status=active) → 4
**need HR-TYO/Planning Section/planning_headcount** (group HR-TYO, class A, local=False)
- RULE HR-TYO.headcount_definition: {"id": "HR-TYO.headcount_definition", "group": "HR-TYO", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-TYO.planning_headcount: {"id": "HR-TYO.planning_headcount", "group": "HR-TYO", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-TYO/emp/E-TYO-1008/profile` v3 (recorded day -2, registered day 0): {"dept": "Planning Section", "grade": 5, "contract": "contractor", "hire_day": -783, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1011/profile` v3 (recorded day 3, registered day 4): {"dept": "Planning Section", "grade": 1, "contract": "regular", "hire_day": -895, "status": "active"}
- DB `HR-TYO/emp/E-TYO-1016/profile` v2 (recorded day -7, registered day -5): {"dept": "Sales Section 2", "grade": 5, "contract": "regular", "hire_day": -842, "status": "active"}
- DB `HR-TYO/emp/E-TYO-2004/profile` v3 (recorded day 2, registered day 4): {"dept": "Planning Section", "grade": 2, "contract": "contractor", "hire_day": -8, "status": "active"}
- NEGATIVE: {"query": "HR-TYO Planning Section memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=TYO AND dept=Planning Section AND status=active) → 3
**need IT-SEL/license/Design Suite** (group IT-SEL, class A, local=False)
- RECORD FR-01050 (db_pending/observation, day 2, by it-sel.n0014; DB shows 4): Design Suite seats In use 16/19 seats. Stored value: {"seats":19,"used":16}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00799 (operational/pending_intent, day -4, by it-sel.n0014; DB shows n/a): Design Suite seats 3 seats reserved for Dev Team 2 onboarding until day 4.
- RECORD FR-00834 (operational/pending_intent, day -3, by it-sel.n0014; DB shows n/a): Design Suite seats 3 seats reserved for Dev Team 2 project until day 6.
- RECORD FR-00943 (operational/pending_intent, day 0, by it-sel.a3; DB shows n/a): Design Suite seats 2 seats reserved for Sales Team 1 project until day 13.
**need IT-TYO/rule/seat_transfer_share** (group IT-TYO, class None, local=True)
- RULE IT-TYO.seat_transfer_share: {"id": "IT-TYO.seat_transfer_share", "group": "IT-TYO", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-TYO/rule/seat_purchase_line** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.seat_purchase_line: {"id": "FIN-TYO.seat_purchase_line", "group": "FIN-TYO", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-TYO/Sales Section 1/budget_schedule** (group FIN-TYO, class A, local=False)
- RECORD FR-00342 (operational/exception, day -16, by fin-tyo.a5; DB shows n/a): Sales Section 1 capex executing office agreed that SEL finance executes it until day 8.
- RULE FIN-TYO.owner_exception: {"id": "FIN-TYO.owner_exception", "group": "FIN-TYO", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-SEL/Sales Section 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Sales Section 1/remaining` v1 (recorded day -16, registered day -14): 4271277
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01043 (db_pending/observation, day 2, by fin-sel.a3; DB shows 1): CMT-00036 Sales Section 1 provisional approval settled. Stored value: {"amount":538931,"expected_settle":2,"status":"settled"}
- RECORD FR-01102 (db_pending/observation, day 3, by fin-sel.n0004; DB shows 1): CMT-00038 Sales Section 1 provisional approval settled. Stored value: {"amount":635264,"expected_settle":3,"status":"settled"}
- RECORD FR-01159 (db_pending/observation, day 4, by fin-sel.a4; DB shows ABSENT): CMT-00049 Sales Section 1 provisional approval settled. Stored value: {"amount":536852,"expected_settle":3,"status":"settled"}
- RECORD FR-00886 (operational/pending_intent, day -1, by fin-sel.a3; DB shows n/a): CMT-00051 Sales Section 1 meeting room equipment provisional approval 964,719 KRW under review, settlement expected day 3.
- RECORD FR-01158 (db_pending/observation, day 4, by fin-sel.n0004; DB shows ABSENT): CMT-00057 Sales Section 1 provisional approval settled. Stored value: {"amount":522287,"expected_settle":4,"status":"settled"}
- RECORD FR-00994 (operational/pending_intent, day 1, by fin-sel.n0004; DB shows n/a): CMT-00063 Sales Section 1 monitor provisional approval 988,031 KRW under review, settlement expected day 9.
- RECORD FR-01156 (db_pending/observation, day 4, by fin-sel.n0005; DB shows ABSENT): CMT-00066 Sales Section 1 provisional approval 793,822 KRW confirmed, settlement expected day 7. Stored value: {"amount":793822,"expected_settle":7,"status":"pending"}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Section 1 AND status IN ['reviewing', 'pending'] → ["CMT-00051", "CMT-00063", "CMT-00066"]
**need PROC-TYO/seat_price/Design Suite** (group PROC-TYO, class A, local=False)
- DB `PROC-TYO/seatprice/Design Suite/amount` v1 (recorded day -20, registered day -20): 216416
### Model answer and official verdict
answer: {"alloc": [4, 6, 3], "buy": 10, "transfer": 0, "unmet": 0}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-00807 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Yamada Sou approved from Dev Section 1 to Sales Section 1, effective day 8 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00967 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Kimura Yuito approved from Dev Section 2 to Sales Section 1, effective day 7 (stays in Dev Section 2 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00987 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Shimizu Hayate approved from Support Section to Sales Section 1, effective day 10 (stays in Support Section until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01064 (need HR-TYO/Sales Section 1/planning_headcount): matcher says **missing**
record text: Sales Section 1 confirmed hire OF-00017 starts day 5, contractor (not yet in HR records).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00807 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Yamada Sou approved from Dev Section 1 to Sales Section 1, effective day 8 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01133 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: HR record of Matsumoto Tsumugi moved from Dev Section 1 to Sales Section 2, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Section 2","grade":1,"hire_day":-427,"status":"active"}
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00679 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Yamaguchi Mio approved from Dev Section 1 to Support Section, effective day 5 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-00940 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Ishikawa Sota approved from Dev Section 1 to Dev Section 2, effective day 6 (stays in Dev Section 1 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01137 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: Transfer of Fujita Riku approved from Dev Section 2 to Dev Section 1, effective day 7 (stays in Dev Section 2 until then).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```
### MATCHER CHECK FR-01063 (need HR-TYO/Dev Section 1/planning_headcount): matcher says **missing**
record text: Dev Section 1 confirmed hire OF-00016 starts day 5, contractor (not yet in HR records).
What the requester received from HR-TYO during this task:
```
Planning headcounts: Sales Section 1 = 4, Dev Section 1 = 6, Planning Section = 3
- Sales Section 1 | headcount | 3 |  | db, day unknown: D1
- Shimizu Hayate | transfer to Sales Section 1 | effective day 10 |  | history, day 1: H112
- Sales Section 1 | planning headcount | 4 |  | rule, day fixed: planning_headcount
- Dev Section 1 | headcount | 5 |  | db, day unknown: D2
- Dev Section 1 | confirmed hire | starts day 5 |  | history, day 2: H146
- Dev Section 1 | planning headcount | 6 |  | rule, day fixed: planning_headcount
- Planning Section | headcount | 3 |  | db, day unknown: D3
- Planning Section | planning headcount | 3 |  | rule, day fixed: planning_headcount
```

## CASE 9: qwen3.5-27b · direct · s13 · W-00150 · class C · day 15 · template contract_gate
### Task as given to the requester
For Fujita-san: the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 169}
### Counterfactual answers (generator)
{"stale": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 120}, "partial": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 120}, "neardup": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 169}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2008/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2008"}
- RECORD FR-01718 (db_pending/rationale, day 14, by hr-tyo.n0018; DB shows 3): HR record of Fujita Riku changed to grade 4 (review result), Sales Section 1. Stored value: {"contract":"contractor","dept":"Sales Section 1","grade":4,"hire_day":-1,"status":"active"}
**need IT-TYO/eligibility/E-TYO-2008** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-2008/contract** (group LEGAL-TYO, class C, local=False)
- RECORD FR-01791 [decision-critical] (db_pending/observation, day 15, by legal-tyo.n0017; DB shows 1): Contract of Fujita Riku extended to day 169, allowed tier basic, NDA yes. Stored value: {"allowed_tier":"basic","expiry":169,"nda":true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01033 [decision-critical] (operational/exception, day 2, by legal-tyo.a3; DB shows n/a): Equipment exception of Fujita Riku higher tiers including premium allowed until day 22 for a project, legal check done.
- RECORD FR-01146 (operational/observation, day 4, by legal-tyo.n0017; DB shows n/a): NDA of Fujita Riku signed copy verified, NDA check step can be skipped until day 21.
### Model answer and official verdict
answer: {"contract_tier": "basic", "expiry": 120, "it_tier": "standard", "nda_step": true}
official exact match: 0 (1/4 slots)
### MATCHER CHECK FR-01791 (need LEGAL-TYO/E-TYO-2008/contract): matcher says **stale**
record text: Contract of Fujita Riku extended to day 169, allowed tier basic, NDA yes. Stored value: {"allowed_tier":"basic","expiry":169,"nda":true}
What the requester received from LEGAL-TYO during this task:
```
- E-TYO-2008 | allowed_tier | basic |  | db, day 4: D1
- E-TYO-2008 | expiry | 120 |  | db, day 4: D1
missing: Legal exceptions registered for E-TYO-2008 that would allow equipment above the contract's allowed tier
---
E-TYO-2008 contract requires NDA (nda=true). Per contractor_policy, standard equipment needs NDA check unless verified NDA copy exists and is valid. Cannot confirm if verified NDA copy exists from my records.
- E-TYO-2008 | nda required | true |  | db, day 4: D1
- contractor_policy | Standard equipment for contractor with NDA clause requirement | needs an NDA check unless verified NDA copy exists and is still valid |  | rule, day fixed: rule: contractor_policy
missing: Whether E-TYO-2008 has a verified NDA copy on file that is still valid
```
### MATCHER CHECK FR-01033 (need LEGAL-TYO/E-TYO-2008/contract): matcher says **missing**
record text: Equipment exception of Fujita Riku higher tiers including premium allowed until day 22 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
- E-TYO-2008 | allowed_tier | basic |  | db, day 4: D1
- E-TYO-2008 | expiry | 120 |  | db, day 4: D1
missing: Legal exceptions registered for E-TYO-2008 that would allow equipment above the contract's allowed tier
---
E-TYO-2008 contract requires NDA (nda=true). Per contractor_policy, standard equipment needs NDA check unless verified NDA copy exists and is valid. Cannot confirm if verified NDA copy exists from my records.
- E-TYO-2008 | nda required | true |  | db, day 4: D1
- contractor_policy | Standard equipment for contractor with NDA clause requirement | needs an NDA check unless verified NDA copy exists and is still valid |  | rule, day fixed: rule: contractor_policy
missing: Whether E-TYO-2008 has a verified NDA copy on file that is still valid
```

## CASE 10: qwen3.5-27b · direct · s14 · W-00014 · class D · day 2 · template purchase
### Task as given to the requester
For Ono-san's monitor request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
[Request scope] item=monitor; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=the requesting region and the first other region in the public region list. Evaluate within the optional review scope stated here.
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
{"decision": "order", "option": "Q-V-TYO-1-MNB", "approver": "team_lead", "nda": false, "budget_after": 1500689, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"decision": "order", "option": "Q-V-TYO-1-MNB", "approver": "team_lead", "nda": false, "budget_after": 1154700, "blocked_by": null}, "partial": {"decision": "order", "option": "Q-V-TYO-1-MNB", "approver": "team_lead", "nda": false, "budget_after": 1154700, "blocked_by": null}, "neardup": {"decision": "order", "option": "Q-V-TYO-1-MNB", "approver": "team_lead", "nda": false, "budget_after": 2089718, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1001/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1001"}
- DB `HR-TYO/emp/E-TYO-1001/profile` v1 (recorded day -20, registered day -20): {"dept": "Support Section", "grade": 3, "contract": "regular", "hire_day": -715, "status": "active"}
**need FIN-TYO/Support Section/budget_schedule** (group FIN-TYO, class C, local=False)
- RECORD FR-01029 [decision-critical] (db_pending/rationale, day 1, by fin-tyo.a1; DB shows 6): Support Section capex balance adjusted to 3,172,078 KRW (refund applied). Stored value: 3172078
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00925 [decision-critical] (operational/pending_intent, day -1, by fin-tyo.a1; DB shows n/a): Support Section capex 311,189 KRW earmarked for new-hire equipment until day 5 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00003/status` v2 (recorded day -7, registered day -6): {"status": "settled", "amount": 778994, "expected_settle": -7}
- RECORD FR-00965 (db_pending/observation, day 0, by fin-tyo.a3; DB shows 1): CMT-00021 Support Section provisional approval settled. Stored value: {"amount":725763,"expected_settle":0,"status":"settled"}
- DB `FIN-TYO/commit/CMT-00025/status` v2 (recorded day -1, registered day 0): {"status": "settled", "amount": 879454, "expected_settle": -1}
- DB `FIN-TYO/commit/CMT-00033/status` v2 (recorded day 1, registered day 2): {"status": "settled", "amount": 533734, "expected_settle": 1}
- RECORD FR-01035 [decision-critical] (operational/pending_intent, day 1, by fin-tyo.a3; DB shows n/a): CMT-00085 Support Section meeting room equipment provisional approval 602,109 KRW under review, settlement expected day 11.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Support Section AND status IN ['reviewing', 'pending'] → ["earmark:FR-00925", "CMT-00052", "CMT-00085"]
**need IT-TYO/eligibility/E-TYO-1001** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need PROC-TYO/quotes/monitor** (group PROC-TYO, class D, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00700 [decision-critical] (operational/handover, day -7, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-2 exclude from comparisons until day 6 due to a quality issue.
- RECORD FR-00826 (operational/handover, day -4, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-3 exclude from comparisons until day 4 due to a quality issue.
- RECORD FR-00964 (operational/handover, day 0, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 5 due to a quality issue.
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v2 (recorded day -10, registered day -9): 7
- DB `PROC-TYO/quote/Q-V-TYO-0-MNB/amount` v3 (recorded day -2, registered day 0): 572951
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v2 (recorded day -1, registered day 0): 7
- RECORD FR-00985 [decision-critical] (db_pending/rationale, day 0, by proc-tyo.a1; DB shows 2): V-TYO-1 monitor (basic) quote Q-V-TYO-1-MNB changed to 511,699 KRW (raw material prices). Stored value: 511699
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v2 (recorded day -1, registered day 0): 7
- DB `PROC-TYO/quote/Q-V-TYO-1-MNS/amount` v3 (recorded day -11, registered day -10): 1044581
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
- DB `PROC-TYO/quote/Q-V-TYO-2-MNB/amount` v1 (recorded day -20, registered day -20): 497837
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
- DB `PROC-TYO/quote/Q-V-TYO-2-MNS/amount` v1 (recorded day -20, registered day -20): 1431789
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v4 (recorded day -1, registered day 1): 8
- DB `PROC-TYO/quote/Q-V-TYO-3-MNB/amount` v1 (recorded day -20, registered day -20): 639240
**need PROC-SEL/quotes/monitor** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00570 (operational/handover, day -10, by proc-sel.w00065; DB shows n/a): Supplier V-SEL-3 exclude from comparisons until day 4 due to a quality issue.
- RECORD FR-00713 (operational/handover, day -6, by proc-sel.w00088; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 6 due to a quality issue.
- RECORD FR-00983 (operational/handover, day 0, by proc-sel.w00136; DB shows n/a): Supplier V-SEL-1 exclude from comparisons until day 10 due to a quality issue.
- RECORD FR-00789 (operational/observation, day -5, by proc-sel.w00100; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 5 days until day 3.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-00862 (operational/observation, day -3, by proc-sel.w00114; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 4 days until day 2.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-MNB/amount` v2 (recorded day -4, registered day -3): 831753
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-MNS/amount` v2 (recorded day -15, registered day -14): 1475905
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day -5, registered day -4): 12
- DB `PROC-SEL/quote/Q-V-SEL-1-MNS/amount` v1 (recorded day -20, registered day -20): 961278
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-MNB/amount` v2 (recorded day 0, registered day 1): 776508
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-MNB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v4 (recorded day -6, registered day -3): 6
- DB `PROC-SEL/quote/Q-V-SEL-3-MNB/amount` v1 (recorded day -20, registered day -20): 693284
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-MNS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v4 (recorded day -6, registered day -3): 6
- DB `PROC-SEL/quote/Q-V-SEL-3-MNS/amount` v1 (recorded day -20, registered day -20): 1048550
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 1606153, "decision": "assign", "nda": false, "option": "INV-TYO-MNB"}
official exact match: 0 (3/6 slots)
### MATCHER CHECK FR-01029 (need FIN-TYO/Support Section/budget_schedule): matcher says **missing**
record text: Support Section capex balance adjusted to 3,172,078 KRW (refund applied). Stored value: 3172078
What the requester received from FIN-TYO during this task:
```
Support Section has a budget line balance of 2,826,089 KRW. After deducting the pending provisional approval CMT-00052 (246,392 KRW) and the active earmark (311,189 KRW until day 5), the available budget is 2,268,508 KRW, which is sufficient for the 662,355 KRW monitor.
- Support Section | budget_line_balance | 2826089 |  | db, day 1: D1
- CMT-00052 | provisional approval amount to deduct | 246392 | pending | db, day 0: D2
- Support Section | active earmark | 311189 KRW until day 5 |  | history, day -1: H145
- Support Section | available budget | 2268508 |  | db, day 1: calculated from D1, D2, H145
- Support Section | enough budget for 662355 KRW monitor | yes |  | unknown, day unknown: calculated
---
- 662,355 KRW | required finance approver | team_lead |  | rule, day fixed: approval_tiers
```
### MATCHER CHECK FR-00925 (need FIN-TYO/Support Section/budget_schedule): matcher says **delivered**
record text: Support Section capex 311,189 KRW earmarked for new-hire equipment until day 5 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
Support Section has a budget line balance of 2,826,089 KRW. After deducting the pending provisional approval CMT-00052 (246,392 KRW) and the active earmark (311,189 KRW until day 5), the available budget is 2,268,508 KRW, which is sufficient for the 662,355 KRW monitor.
- Support Section | budget_line_balance | 2826089 |  | db, day 1: D1
- CMT-00052 | provisional approval amount to deduct | 246392 | pending | db, day 0: D2
- Support Section | active earmark | 311189 KRW until day 5 |  | history, day -1: H145
- Support Section | available budget | 2268508 |  | db, day 1: calculated from D1, D2, H145
- Support Section | enough budget for 662355 KRW monitor | yes |  | unknown, day unknown: calculated
---
- 662,355 KRW | required finance approver | team_lead |  | rule, day fixed: approval_tiers
```
### MATCHER CHECK FR-01035 (need FIN-TYO/Support Section/budget_schedule): matcher says **missing**
record text: CMT-00085 Support Section meeting room equipment provisional approval 602,109 KRW under review, settlement expected day 11.
What the requester received from FIN-TYO during this task:
```
Support Section has a budget line balance of 2,826,089 KRW. After deducting the pending provisional approval CMT-00052 (246,392 KRW) and the active earmark (311,189 KRW until day 5), the available budget is 2,268,508 KRW, which is sufficient for the 662,355 KRW monitor.
- Support Section | budget_line_balance | 2826089 |  | db, day 1: D1
- CMT-00052 | provisional approval amount to deduct | 246392 | pending | db, day 0: D2
- Support Section | active earmark | 311189 KRW until day 5 |  | history, day -1: H145
- Support Section | available budget | 2268508 |  | db, day 1: calculated from D1, D2, H145
- Support Section | enough budget for 662355 KRW monitor | yes |  | unknown, day unknown: calculated
---
- 662,355 KRW | required finance approver | team_lead |  | rule, day fixed: approval_tiers
```
### MATCHER CHECK FR-00700 (need PROC-TYO/quotes/monitor): matcher says **missing**
record text: Supplier V-TYO-2 exclude from comparisons until day 6 due to a quality issue.
What the requester received from PROC-TYO during this task:
```
Cannot find employee E-TYO-1001 or monitor quote information in my area's records. All requested monitor pricing data is missing.
- E-TYO-1001 | catalog_entry | NOT_FOUND |  | db, day unknown: D1
- monitor | catalog_entry | NOT_FOUND |  | db, day unknown: D4
missing: Employee E-TYO-1001 details; Monitor quotes from TYO region; Monitor quotes from SEL region; Available monitor options with prices; Cheapest monitor options
```
### MATCHER CHECK FR-00985 (need PROC-TYO/quotes/monitor): matcher says **missing**
record text: V-TYO-1 monitor (basic) quote Q-V-TYO-1-MNB changed to 511,699 KRW (raw material prices). Stored value: 511699
What the requester received from PROC-TYO during this task:
```
Cannot find employee E-TYO-1001 or monitor quote information in my area's records. All requested monitor pricing data is missing.
- E-TYO-1001 | catalog_entry | NOT_FOUND |  | db, day unknown: D1
- monitor | catalog_entry | NOT_FOUND |  | db, day unknown: D4
missing: Employee E-TYO-1001 details; Monitor quotes from TYO region; Monitor quotes from SEL region; Available monitor options with prices; Cheapest monitor options
```

## CASE 11: qwen3.5-27b · direct · s13 · W-00040 · class D · day 4 · template capacity
### Task as given to the requester
How many in-house laptop (premium) units and CAD seats are actually available right now?
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
{"stock": 2, "seats": 0, "seats_other_region": null}
### Counterfactual answers (generator)
{"stale": {"stock": 3, "seats": 0, "seats_other_region": null}, "partial": {"stock": 3, "seats": 0, "seats_other_region": null}, "neardup": {"stock": 2, "seats": 1, "seats_other_region": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/stock/INV-TYO-LTP** (group IT-TYO, class A, local=False)
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-LTP"}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-TYO/inv/INV-TYO-LTP/qty` v3 (recorded day -1, registered day 2): 3
- RECORD FR-00884 [decision-critical] (operational/pending_intent, day -1, by it-tyo.w00124; DB shows n/a): In-house stock laptop (premium) 1 unit held as a Sales Section 1 replacement spare until day 5.
**need IT-TYO/license/CAD** (group IT-TYO, class D, local=False)
- DB `IT-TYO/lic/CAD/seats` v4 (recorded day -7, registered day -6): {"seats": 22, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00770 [decision-critical] (operational/pending_intent, day -5, by it-tyo.w00099; DB shows n/a): CAD seats 2 seats reserved for Support Section project until day 7.
- RECORD FR-00993 [decision-critical] (operational/pending_intent, day 1, by it-tyo.w00138; DB shows n/a): CAD seats 4 seats reserved for Sales Section 2 project until day 15.
### Model answer and official verdict
answer: {"seats": 5, "seats_other_region": null, "stock": 3}
official exact match: 0 (1/3 slots)
### MATCHER CHECK FR-00884 (need IT-TYO/stock/INV-TYO-LTP): matcher says **missing**
record text: In-house stock laptop (premium) 1 unit held as a Sales Section 1 replacement spare until day 5.
What the requester received from IT-TYO during this task:
```
- In-house stock laptop (premium) | quantity | 3 |  | db, day 2: D1
- CAD | total seats | 22 |  | db, day -6: D2
- CAD | used seats | 17 |  | db, day -6: D2
- CAD | available seats | 5 |  | db, day -6: D2
```
### MATCHER CHECK FR-00770 (need IT-TYO/license/CAD): matcher says **missing**
record text: CAD seats 2 seats reserved for Support Section project until day 7.
What the requester received from IT-TYO during this task:
```
- In-house stock laptop (premium) | quantity | 3 |  | db, day 2: D1
- CAD | total seats | 22 |  | db, day -6: D2
- CAD | used seats | 17 |  | db, day -6: D2
- CAD | available seats | 5 |  | db, day -6: D2
```
### MATCHER CHECK FR-00993 (need IT-TYO/license/CAD): matcher says **missing**
record text: CAD seats 4 seats reserved for Sales Section 2 project until day 15.
What the requester received from IT-TYO during this task:
```
- In-house stock laptop (premium) | quantity | 3 |  | db, day 2: D1
- CAD | total seats | 22 |  | db, day -6: D2
- CAD | used seats | 17 |  | db, day -6: D2
- CAD | available seats | 5 |  | db, day -6: D2
```

## CASE 12: qwen3.5-27b · direct · s14 · W-00141 · class D · day 15 · template vendor
### Task as given to the requester
That department from W-00114 needs a laptop. Pick a compliant supplier within budget.
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"vendor": "V-SEL-1", "option": "Q-V-SEL-1-LTS", "amount": 1452400, "approver": "division_head", "budget_after": 849578, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"vendor": null, "option": null, "amount": null, "approver": null, "budget_after": null, "blocked_by": "vendor_excluded"}, "partial": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 458670, "approver": "team_lead", "budget_after": 1843308, "blocked_by": null}, "neardup": {"vendor": "V-SEL-1", "option": "Q-V-SEL-1-LTS", "amount": 1452400, "approver": "division_head", "budget_after": 1262350, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/task/W-00114/result** (group IT-SEL, class None, local=True)
- RECORD FR-01603 (operational/task_result, day 12, by it-sel.n0002; DB shows n/a): W-00114 item result: available=1179292, n_deducted=1
**need FIN-SEL/Dev Team 2/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 2/remaining` v4 (recorded day 12, registered day 15): 2914080
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-SEL/commit/CMT-00001/status` v2 (recorded day -7, registered day -6): {"status": "settled", "amount": 273840, "expected_settle": -7}
- DB `FIN-SEL/commit/CMT-00008/status` v2 (recorded day -13, registered day -10): {"status": "settled", "amount": 669489, "expected_settle": -13}
- DB `FIN-SEL/commit/CMT-00011/status` v2 (recorded day -10, registered day -7): {"status": "settled", "amount": 435969, "expected_settle": -10}
- DB `FIN-SEL/commit/CMT-00015/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 646488, "expected_settle": -2}
- DB `FIN-SEL/commit/CMT-00023/status` v2 (recorded day 1, registered day 4): {"status": "settled", "amount": 259203, "expected_settle": 1}
- DB `FIN-SEL/commit/CMT-00046/status` v2 (recorded day 5, registered day 8): {"status": "settled", "amount": 871578, "expected_settle": 5}
- DB `FIN-SEL/commit/CMT-00053/status` v2 (recorded day 8, registered day 11): {"status": "settled", "amount": 658782, "expected_settle": 8}
- DB `FIN-SEL/commit/CMT-00074/status` v2 (recorded day 11, registered day 12): {"status": "settled", "amount": 258777, "expected_settle": 11}
- DB `FIN-SEL/commit/CMT-00079/status` v2 (recorded day 7, registered day 8): {"status": "settled", "amount": 329890, "expected_settle": 5}
- DB `FIN-SEL/commit/CMT-00088/status` v2 (recorded day 10, registered day 12): {"status": "settled", "amount": 939674, "expected_settle": 10}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00100"]
**need PROC-SEL/quotes/laptop** (group PROC-SEL, class D, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01275 [decision-critical] (operational/handover, day 6, by proc-sel.w00193; DB shows n/a): Supplier V-SEL-0 exclude from comparisons until day 16 due to a quality issue.
- RECORD FR-01420 [decision-critical] (operational/handover, day 8, by proc-sel.w00221; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 21 due to a quality issue.
- RECORD FR-01082 [decision-critical] (operational/observation, day 2, by proc-sel.w00155; DB shows n/a): Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01168 (operational/observation, day 4, by proc-sel.w00172; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 4 days until day 16.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01688 (operational/observation, day 13, by proc-sel.w00267; DB shows n/a): Supplier V-SEL-0 delivery notified: deliveries delayed by 3 days until day 25.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v3 (recorded day 13, registered day 14): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-LTB/amount` v3 (recorded day 12, registered day 15): 458670
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
- RECORD FR-01702 [decision-critical] (db_pending/observation, day 14, by proc-sel.w00271; DB shows 3): Supplier V-SEL-1 lead time change notice applied. Stored value: 4
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
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"amount": 534454, "approver": "team_lead", "blocked_by": null, "budget_after": 1767524, "option": "Q-V-SEL-0-LTB", "vendor": "V-SEL-0"}
official exact match: 0 (1/6 slots)
### MATCHER CHECK FR-01275 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-0 exclude from comparisons until day 16 due to a quality issue.
What the requester received from PROC-SEL during this task:
```
Task W-00114 information is not available in SEL area records. Task IDs only appear in tasks, not in area databases or records.
missing: task W-00114 details - task IDs do not appear in area records per rules; department involved in task W-00114 - not found in SEL area records; item requested in task W-00114 - not found in SEL area records
---
No department order or request information found in SEL area records.
missing: Department orders or requests information - no records found in SEL area database showing which departments have been requesting laptops or other equipment
---
V-SEL-2 is registered (vendor_registration=true) with lead time of 8 days. No exclusion status found in SEL area records.
- V-SEL-2 | vendor_registration | true |  | db, day -20: D1
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D2
missing: V-SEL-2 exclusion status - no exclusion record type available in SEL area database
```
### MATCHER CHECK FR-01420 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-2 exclude from comparisons until day 21 due to a quality issue.
What the requester received from PROC-SEL during this task:
```
Task W-00114 information is not available in SEL area records. Task IDs only appear in tasks, not in area databases or records.
missing: task W-00114 details - task IDs do not appear in area records per rules; department involved in task W-00114 - not found in SEL area records; item requested in task W-00114 - not found in SEL area records
---
No department order or request information found in SEL area records.
missing: Department orders or requests information - no records found in SEL area database showing which departments have been requesting laptops or other equipment
---
V-SEL-2 is registered (vendor_registration=true) with lead time of 8 days. No exclusion status found in SEL area records.
- V-SEL-2 | vendor_registration | true |  | db, day -20: D1
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D2
missing: V-SEL-2 exclusion status - no exclusion record type available in SEL area database
```
### MATCHER CHECK FR-01082 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
What the requester received from PROC-SEL during this task:
```
Task W-00114 information is not available in SEL area records. Task IDs only appear in tasks, not in area databases or records.
missing: task W-00114 details - task IDs do not appear in area records per rules; department involved in task W-00114 - not found in SEL area records; item requested in task W-00114 - not found in SEL area records
---
No department order or request information found in SEL area records.
missing: Department orders or requests information - no records found in SEL area database showing which departments have been requesting laptops or other equipment
---
V-SEL-2 is registered (vendor_registration=true) with lead time of 8 days. No exclusion status found in SEL area records.
- V-SEL-2 | vendor_registration | true |  | db, day -20: D1
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D2
missing: V-SEL-2 exclusion status - no exclusion record type available in SEL area database
```
### MATCHER CHECK FR-01702 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-1 lead time change notice applied. Stored value: 4
What the requester received from PROC-SEL during this task:
```
Task W-00114 information is not available in SEL area records. Task IDs only appear in tasks, not in area databases or records.
missing: task W-00114 details - task IDs do not appear in area records per rules; department involved in task W-00114 - not found in SEL area records; item requested in task W-00114 - not found in SEL area records
---
No department order or request information found in SEL area records.
missing: Department orders or requests information - no records found in SEL area database showing which departments have been requesting laptops or other equipment
---
V-SEL-2 is registered (vendor_registration=true) with lead time of 8 days. No exclusion status found in SEL area records.
- V-SEL-2 | vendor_registration | true |  | db, day -20: D1
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D2
missing: V-SEL-2 exclusion status - no exclusion record type available in SEL area database
```

## CASE 13: qwen3.5-27b · routing · s12 · W-00087 · class A · day 9 · template diag
### Task as given to the requester
Invoice INV-30478 (964,737 KRW, beneficiary Jisung (Assistant Manager), asset A-SEL-80589, provisional approval CMT-00053) does not match. Find the cause.
[Request scope] target supplier=V-SEL-3; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"cause": "RECEIPT_MISSING"}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"cause": "ASSET_NOT_REGISTERED"}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/CMT-00053/status** (group FIN-SEL, class None, local=True)
- CATALOG: {"group": "FIN-SEL", "key": "commits/CMT-00053"}
- RECORD FR-01369 (db_pending/observation, day 9, by fin-sel.a3; DB shows 1): CMT-00053 Sales Team 2 provisional approval settled. Stored value: {"amount":983417,"expected_settle":9,"status":"settled"}
**need HR-SEL/E-SEL-2002/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2002"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v2 (recorded day 2, registered day 3): {"dept": "Sales Team 1", "grade": 2, "contract": "regular", "hire_day": -15, "status": "active"}
**need IT-SEL/E-SEL-2002/assets** (group IT-SEL, class A, local=False)
- DB `IT-SEL/asset/A-SEL-80589/holder` v1 (recorded day 7, registered day 9): {"emp": "E-SEL-2002"}
- QUERY SELECT asset WHERE holder=E-SEL-2002 → ["A-SEL-80589"]
**need PROC-SEL/receipt/CMT-00053** (group PROC-SEL, class A, local=False)
- QUERY {"key": "PROC-SEL/receipt/CMT-00053/received", "asof": 9} → "ABSENT"
**need PROC-SEL/vendor/V-SEL-3/status** (group PROC-SEL, class A, local=False)
- NEGATIVE: {"query": "PROC-SEL exclusion order for supplier V-SEL-3", "result": []}
**need FIN-SEL/rule/invoice_match_precedence** (group FIN-SEL, class None, local=True)
- RULE FIN-SEL.invoice_match_precedence: {"id": "FIN-SEL.invoice_match_precedence", "group": "FIN-SEL", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "RECEIPT_MISSING"}
official exact match: 1 (1/1 slots)