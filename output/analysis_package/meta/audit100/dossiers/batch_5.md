## CASE 53: deepseek-v4-flash · direct · s14 · W-00088 · class B · day 9 · template lookup
### Task as given to the requester
Check Inoue-san's current department, grade and assets held.
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
{"dept": "Dev Section 1", "grade": 2, "assets": ["A-TYO-5167", "A-TYO-8867"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Planning Section", "grade": 2, "assets": ["A-TYO-5167", "A-TYO-8867"]}, "partial": {"dept": "Planning Section", "grade": 2, "assets": ["A-TYO-5167", "A-TYO-8867"]}, "neardup": {"dept": "Sales Section 1", "grade": 3, "assets": ["A-TYO-5167", "A-TYO-8867"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1014/profile** (group HR-TYO, class B, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1014"}
- RECORD FR-01439 [decision-critical] (db_pending/observation, day 9, by hr-tyo.a5; DB shows 1): HR record of Inoue Ritsu moved from Planning Section to Dev Section 1, grade 2, regular. Stored value: {"contract":"regular","dept":"Dev Section 1","grade":2,"hire_day":-316,"status":"active"}
**need IT-TYO/E-TYO-1014/assets** (group IT-TYO, class A, local=False)
- DB `IT-TYO/asset/A-TYO-5167/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1014"}
- DB `IT-TYO/asset/A-TYO-8867/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1014"}
- QUERY SELECT asset WHERE holder=E-TYO-1014 → ["A-TYO-5167", "A-TYO-8867"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-5167", "A-TYO-8867"], "dept": "Planning Section", "grade": 2}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-01439 (need HR-TYO/E-TYO-1014/profile): matcher says **stale**
record text: HR record of Inoue Ritsu moved from Planning Section to Dev Section 1, grade 2, regular. Stored value: {"contract":"regular","dept":"Dev Section 1","grade":2,"hire_day":-316,"status":"active"}
What the requester received from HR-TYO during this task:
```
Employee E-TYO-1014 (Inoue Ritsu / Inoue-san) is in Planning Section, grade 2, regular contract, active, hired 316 days ago (hire_day = -316).
- E-TYO-1014 | department | Planning Section |  | db, day -20: D1
- E-TYO-1014 | grade | 2 |  | db, day -20: D1
- E-TYO-1014 | contract type | regular |  | db, day -20: D1
- E-TYO-1014 | hire day | -316 |  | db, day -20: D1
- E-TYO-1014 | status | active |  | db, day -20: D1
- E-TYO-1014 | name | Inoue Ritsu |  | db, day fixed: D2
- E-TYO-1014 | alias | Inoue-san |  | db, day fixed: D2
```

## CASE 54: deepseek-v4-flash · direct · s13 · W-00014 · class B · day 2 · template budget
### Task as given to the requester
How much budget can Marketing Team actually spend right now, after all deductions?
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
{"available": 3850359, "n_deducted": 1}
### Counterfactual answers (generator)
{"stale": null, "partial": {"available": 2126893, "n_deducted": 1}, "neardup": {"available": 997528, "n_deducted": 2}, "wrong_owner": {"available": 2126893, "n_deducted": 1}}
### World facts behind the gold (by need)
**need FIN-SEL/Marketing Team/budget_schedule** (group FIN-SEL, class B, local=False)
- RECORD FR-00582 [decision-critical] (operational/exception, day -10, by fin-sel.n0005; DB shows n/a): Marketing Team capex executing office agreed that TYO finance executes it until day 8.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Marketing Team/budget_schedule** (group FIN-TYO, class B, local=False)
- DB `FIN-TYO/line/Marketing Team/remaining` v1 (recorded day -10, registered day -9): 4234059
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01003 [decision-critical] (operational/pending_intent, day 1, by fin-tyo.a5; DB shows n/a): CMT-00064 Marketing Team meeting room equipment provisional approval 383,700 KRW under review, settlement expected day 7.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Marketing Team AND status IN ['reviewing', 'pending'] → ["CMT-00064"]
### Model answer and official verdict
answer: {"available": 2126893, "n_deducted": 1}
official exact match: 0 (1/2 slots)
### MATCHER CHECK FR-00582 (need FIN-SEL/Marketing Team/budget_schedule): matcher says **missing**
record text: Marketing Team capex executing office agreed that TYO finance executes it until day 8.
What the requester received from FIN-SEL during this task:
```
Marketing Team's current capex balance is 2,457,564 KRW. There is one active earmark: 330,671 KRW for new-hire equipment (valid until day 7). An older earmark of 207,590 KRW (until day -7) has expired. All three registered provisional approvals are settled, so none reduce the spendable amount. The available budget is 2,126,893 KRW.
- Marketing Team | capex balance (budget line balance) | 2457564 |  | db, day 0: D1
- Marketing Team | quarterly base allocation | 4234059 |  | db, day -20: D2
- Marketing Team | earmark – new-hire equipment (until day -7, expired) | 207590 | until day -7 | history, day -18: H34
- Marketing Team | earmark – new-hire equipment (until day 7, active) | 330671 | until day 7 | history, day 2: H225
- Marketing Team | provisional approvals (all settled, none pending) | none pending |  | db, day unknown: D3
- Marketing Team | available budget (balance − active earmarks) | 2126893 |  | rule, day fixed: pending_deduction
---
Marketing Team (SEL) has a remaining capex balance of 2,457,564 KRW with a quarterly base of 4,234,059 KRW. All three registered provisional approvals are settled. The executing office agreement with TYO finance is active until day 8, so TYO executes their budget during that period. No pending provisional approvals, earmarks, holds, or exclusions are recorded. The available budget today (day 2) is 2,457,564 KRW.
- Marketing Team | budget line balance (remaining capex) | 2457564 |  | db, day 0: D1
- Marketing Team | quarterly base allocation | 4234059 |  | db, day -20: D2
- Marketing Team | executing office arrangement | TYO finance executes it until day 8 | active (day 2 is within period until day 8) | history, day -10: H16
- Marketing Team | provisional approval CMT-00001 | 960344 | settled | db, day unknown: D3
- Marketing Team | provisional approval CMT-00011 | 599397 | settled | db, day unknown: D3
- Marketing Team | provisional approval CMT-00024 | 201931 | settled | db, day unknown: D3
- Marketing Team | pending provisional approvals | none |  | db, day unknown: D3
- Marketing Team | available budget (line balance minus pending/earmark deductions) | 2457564 |  | rule, day fixed: rule, day fixed: pending_deduction
- Marketing Team | next quarterly budget reset day | day 16 |  | rule, day fixed: rule, day fixed: reset_calendar
missing: holds on Marketing Team budget — none found in my records; exclusions on Marketing Team budget — none found in my records; earmarks on Marketing Team budget — none found in my records; quarterly spending control applying to Marketing Team — no record of such a control
---
There are no provisional approvals currently under review for Marketing Team (SEL region). All three registered provisional approvals (CMT-00001, CMT-00011, CMT-00024) are settled.
- Marketing Team | department_provisional_approvals | No provisional approvals currently under review |  | db, day unknown: D1
- CMT-00001 | status | settled | settled | db, day -11: D1
- CMT-00011 | status | settled | settled | db, day 1: D1
- CMT-00024 | status | settled | settled | db, day -6: D1
```
### MATCHER CHECK FR-01003 (need FIN-TYO/Marketing Team/budget_schedule): matcher says **missing**
record text: CMT-00064 Marketing Team meeting room equipment provisional approval 383,700 KRW under review, settlement expected day 7.
What the requester received from FIN-TYO during this task:
```
(nothing received from this group)
```

## CASE 55: deepseek-v4-flash · direct · s12 · W-00142 · class C · day 15 · template contract_gate
### Task as given to the requester
For Mori-san: the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 182}
### Counterfactual answers (generator)
{"stale": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 134}, "partial": {"it_tier": "standard", "contract_tier": "standard", "nda_step": false, "expiry": 182}, "neardup": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 182}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1019/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1019"}
- DB `HR-TYO/emp/E-TYO-1019/profile` v2 (recorded day 2, registered day 3): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -552, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1019** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1019/contract** (group LEGAL-TYO, class C, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1019/terms` v4 (recorded day -11, registered day -9): {"allowed_tier": "standard", "expiry": 182, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01530 [decision-critical] (operational/exception, day 12, by legal-tyo.a4; DB shows n/a): Equipment exception of Mori Yamato higher tiers including premium allowed until day 32 for a project, legal check done.
- RECORD FR-01364 [decision-critical] (operational/observation, day 9, by legal-tyo.a5; DB shows n/a): NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32.
### Model answer and official verdict
answer: {"contract_tier": "standard", "expiry": 182, "it_tier": "standard", "nda_step": false}
official exact match: 0 (3/4 slots)
### MATCHER CHECK FR-01530 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **missing**
record text: Equipment exception of Mori Yamato higher tiers including premium allowed until day 32 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
Employee E-TYO-1019 (Mori-san) has a contract with allowed tier 'standard', expiry day 182, and NDA required (true). No legal exceptions affecting the allowed tier are recorded in my area.
- E-TYO-1019 | allowed equipment tier | standard |  | db, day -9: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: D1
- E-TYO-1019 | NDA required | true |  | db, day -9: D1
- E-TYO-1019 | catalog_entry | NO_RECORD |  | db, day unknown: D2
missing: E-TYO-1019 (Mori-san) - legal exceptions affecting the allowed tier — none recorded in my area's records or database; my area does not hold legal exception records
---
E-TYO-1019 (Mori-san) has contract terms: allowed_tier=standard, expiry=182, nda=true. Under contractor_policy, standard equipment with an NDA clause normally requires an NDA check. However, on day 9 the signed NDA copy of Mori Yamato was verified and the NDA check step can be skipped (while that skip remains valid). No catalog_entry is registered, so employment type and department are unknown.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | nda | true |  | db, day -9: D1
- E-TYO-1019 | contract_terms registered_day | -9 |  | db, day -9: D1
- Mori Yamato | NDA signed copy verification | verified | NDA check step can be skipped until … | history, day 9: H243
- E-TYO-1019 | catalog_entry | no record registered |  | db, day unknown: D2
- contractor_policy | rule: standard equipment with NDA clause needs NDA check | NDA check required |  | rule, day fixed: rule: contractor_policy
- contractor_policy | rule: verified signed NDA skips NDA check step | skip while valid |  | rule, day fixed: rule: contractor_policy
- E-TYO-1019 | conclusion: NDA check needed for standard equipment | No — NDA signed copy was verified on day 9 and NDA check step can be skipped (while still valid) |  | history, day 9: H243
missing: E-TYO-1019 (Mori-san) — no catalog_entry record registered; cannot determine department or whether employee is a contractor or regular employee; The exact 'until' date for the NDA check skip for Mori Yamato — the record shows '…' (truncated); the skip is recorded as in effect
---
The NDA signed copy of Mori Yamato (E-TYO-1019) was verified on day 9 (record H243). However, the record does not specify an exact end date for the skip period — it states 'until ...' without a concrete day number. Unlike other NDA verifications (e.g., Ito Aoi until day 24, Maeda An until day 25), no end day was recorded for Mori Yamato.
- Mori Yamato | NDA signed copy verification | verified |  | history, day 9: H243
- Mori Yamato | NDA check step skip end date | not specified (record states 'until ...') |  | history, day 9: H243
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | nda | true |  | db, day -9: D1
missing: Mori Yamato (E-TYO-1019) — the NDA check step skip end date is not specified in the record; the record states 'until ...' without a concrete day number
---
E-TYO-1019 (Mori-san, grade 4 contractor, Sales Section 1) has a contract allowing up to standard tier equipment. No tier exception exists in my records. To obtain premium tier, a legal exception with approver legal_and_division_head would be required per the contractor policy. Additionally, Sales Section 1 is restricted from using equipment from offshore suppliers.
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: D1
- E-TYO-1019 | nda required | true |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | highest equipment tier allowed under contract | standard |  | db, day -9: D1
- E-TYO-1019 | equipment tier exception on record | none found |  | unknown, day unknown: history
- contractor_policy | rule - premium equipment or above-allowed-tier equipment | needs legal exception (approver legal_and_division_head) |  | rule, day fixed: rule: contractor_policy
- E-TYO-1019 | premium tier eligibility via exception | possible only with legal exception approved by legal_and_division_head |  | rule, day fixed: rule: contractor_policy
- Sales Section 1 | data residency restriction | may not use equipment from offshore suppliers |  | rule, day fixed: rule: residency
missing: Whether E-TYO-1019 has a verified signed NDA copy that is still valid (could skip NDA check step) - not in my area's records; Any existing equipment tier exception for E-TYO-1019 - none found in my area's records
```
### MATCHER CHECK FR-01364 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **stale**
record text: NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32.
What the requester received from LEGAL-TYO during this task:
```
Employee E-TYO-1019 (Mori-san) has a contract with allowed tier 'standard', expiry day 182, and NDA required (true). No legal exceptions affecting the allowed tier are recorded in my area.
- E-TYO-1019 | allowed equipment tier | standard |  | db, day -9: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: D1
- E-TYO-1019 | NDA required | true |  | db, day -9: D1
- E-TYO-1019 | catalog_entry | NO_RECORD |  | db, day unknown: D2
missing: E-TYO-1019 (Mori-san) - legal exceptions affecting the allowed tier — none recorded in my area's records or database; my area does not hold legal exception records
---
E-TYO-1019 (Mori-san) has contract terms: allowed_tier=standard, expiry=182, nda=true. Under contractor_policy, standard equipment with an NDA clause normally requires an NDA check. However, on day 9 the signed NDA copy of Mori Yamato was verified and the NDA check step can be skipped (while that skip remains valid). No catalog_entry is registered, so employment type and department are unknown.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | nda | true |  | db, day -9: D1
- E-TYO-1019 | contract_terms registered_day | -9 |  | db, day -9: D1
- Mori Yamato | NDA signed copy verification | verified | NDA check step can be skipped until … | history, day 9: H243
- E-TYO-1019 | catalog_entry | no record registered |  | db, day unknown: D2
- contractor_policy | rule: standard equipment with NDA clause needs NDA check | NDA check required |  | rule, day fixed: rule: contractor_policy
- contractor_policy | rule: verified signed NDA skips NDA check step | skip while valid |  | rule, day fixed: rule: contractor_policy
- E-TYO-1019 | conclusion: NDA check needed for standard equipment | No — NDA signed copy was verified on day 9 and NDA check step can be skipped (while still valid) |  | history, day 9: H243
missing: E-TYO-1019 (Mori-san) — no catalog_entry record registered; cannot determine department or whether employee is a contractor or regular employee; The exact 'until' date for the NDA check skip for Mori Yamato — the record shows '…' (truncated); the skip is recorded as in effect
---
The NDA signed copy of Mori Yamato (E-TYO-1019) was verified on day 9 (record H243). However, the record does not specify an exact end date for the skip period — it states 'until ...' without a concrete day number. Unlike other NDA verifications (e.g., Ito Aoi until day 24, Maeda An until day 25), no end day was recorded for Mori Yamato.
- Mori Yamato | NDA signed copy verification | verified |  | history, day 9: H243
- Mori Yamato | NDA check step skip end date | not specified (record states 'until ...') |  | history, day 9: H243
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | nda | true |  | db, day -9: D1
missing: Mori Yamato (E-TYO-1019) — the NDA check step skip end date is not specified in the record; the record states 'until ...' without a concrete day number
---
E-TYO-1019 (Mori-san, grade 4 contractor, Sales Section 1) has a contract allowing up to standard tier equipment. No tier exception exists in my records. To obtain premium tier, a legal exception with approver legal_and_division_head would be required per the contractor policy. Additionally, Sales Section 1 is restricted from using equipment from offshore suppliers.
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: D1
- E-TYO-1019 | nda required | true |  | db, day -9: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: D1
- E-TYO-1019 | highest equipment tier allowed under contract | standard |  | db, day -9: D1
- E-TYO-1019 | equipment tier exception on record | none found |  | unknown, day unknown: history
- contractor_policy | rule - premium equipment or above-allowed-tier equipment | needs legal exception (approver legal_and_division_head) |  | rule, day fixed: rule: contractor_policy
- E-TYO-1019 | premium tier eligibility via exception | possible only with legal exception approved by legal_and_division_head |  | rule, day fixed: rule: contractor_policy
- Sales Section 1 | data residency restriction | may not use equipment from offshore suppliers |  | rule, day fixed: rule: residency
missing: Whether E-TYO-1019 has a verified signed NDA copy that is still valid (could skip NDA check step) - not in my area's records; Any existing equipment tier exception for E-TYO-1019 - none found in my area's records
```

## CASE 56: deepseek-v4-flash · direct · s12 · W-00094 · class C · day 10 · template capacity
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
As of day 10, INV-SEL-LTP (laptop premium, SEL region) has 0 units available in stock according to the database (registered day 8). No holds or reservations affect this item.
- INV-SEL-LTP | item_id | INV-SEL-LTP |  | db, day fixed: D2
- INV-SEL-LTP | type | laptop |  | db, day fixed: D2
- INV-SEL-LTP | tier | premium |  | db, day fixed: D2
- INV-SEL-LTP | region | SEL |  | db, day fixed: D2
- INV-SEL-LTP | cost | 2348357 |  | db, day fixed: D2
- INV-SEL-LTP | inventory_quantity (database, registered day 8) | 0 |  | db, day 8: D1
- INV-SEL-LTP | available quantity (no holds or reservations recorded) | 0 |  | db, day 8: D1; rule: hold_policy
missing: Any holds or reservations on INV-SEL-LTP — none found in my area's records
---
Analytics has 21 total seats, 13 in use, giving 8 free seats. However, 4 seats are reserved for Dev Team 2 onboarding until day 20, so only 4 seats are actually available.
- Analytics | total seats | 21 |  | db, day 8: D1
- Analytics | used seats (database, registered day 8) | 13 |  | db, day 8: D1
- Analytics | free seats (unused) | 8 |  | db, day 8: D1
- Analytics | free seats calculation | 21 - 13 = 8 |  | db, day 8: D1
- Analytics | reserved seats for Dev Team 2 onboarding | 4 | held until day 20 | history, day 6: H195
- Analytics | available seats (excluding reserved per hold_policy) | 4 |  | rule, day fixed: rule: hold_policy
- Analytics | available seats calculation | 21 - 13 - 4 = 4 |  | rule, day fixed: rule: hold_policy
```
### MATCHER CHECK FR-01233 (need IT-SEL/license/Analytics): matcher says **missing**
record text: Analytics seats 4 seats reserved for Dev Team 2 onboarding until day 20.
What the requester received from IT-SEL during this task:
```
As of day 10, INV-SEL-LTP (laptop premium, SEL region) has 0 units available in stock according to the database (registered day 8). No holds or reservations affect this item.
- INV-SEL-LTP | item_id | INV-SEL-LTP |  | db, day fixed: D2
- INV-SEL-LTP | type | laptop |  | db, day fixed: D2
- INV-SEL-LTP | tier | premium |  | db, day fixed: D2
- INV-SEL-LTP | region | SEL |  | db, day fixed: D2
- INV-SEL-LTP | cost | 2348357 |  | db, day fixed: D2
- INV-SEL-LTP | inventory_quantity (database, registered day 8) | 0 |  | db, day 8: D1
- INV-SEL-LTP | available quantity (no holds or reservations recorded) | 0 |  | db, day 8: D1; rule: hold_policy
missing: Any holds or reservations on INV-SEL-LTP — none found in my area's records
---
Analytics has 21 total seats, 13 in use, giving 8 free seats. However, 4 seats are reserved for Dev Team 2 onboarding until day 20, so only 4 seats are actually available.
- Analytics | total seats | 21 |  | db, day 8: D1
- Analytics | used seats (database, registered day 8) | 13 |  | db, day 8: D1
- Analytics | free seats (unused) | 8 |  | db, day 8: D1
- Analytics | free seats calculation | 21 - 13 = 8 |  | db, day 8: D1
- Analytics | reserved seats for Dev Team 2 onboarding | 4 | held until day 20 | history, day 6: H195
- Analytics | available seats (excluding reserved per hold_policy) | 4 |  | rule, day fixed: rule: hold_policy
- Analytics | available seats calculation | 21 - 13 - 4 = 4 |  | rule, day fixed: rule: hold_policy
```
### MATCHER CHECK FR-01234 (need IT-SEL/license/Analytics): matcher says **missing**
record text: Analytics seats 3 seats reserved for Customer Support Team onboarding until day 19.
What the requester received from IT-SEL during this task:
```
As of day 10, INV-SEL-LTP (laptop premium, SEL region) has 0 units available in stock according to the database (registered day 8). No holds or reservations affect this item.
- INV-SEL-LTP | item_id | INV-SEL-LTP |  | db, day fixed: D2
- INV-SEL-LTP | type | laptop |  | db, day fixed: D2
- INV-SEL-LTP | tier | premium |  | db, day fixed: D2
- INV-SEL-LTP | region | SEL |  | db, day fixed: D2
- INV-SEL-LTP | cost | 2348357 |  | db, day fixed: D2
- INV-SEL-LTP | inventory_quantity (database, registered day 8) | 0 |  | db, day 8: D1
- INV-SEL-LTP | available quantity (no holds or reservations recorded) | 0 |  | db, day 8: D1; rule: hold_policy
missing: Any holds or reservations on INV-SEL-LTP — none found in my area's records
---
Analytics has 21 total seats, 13 in use, giving 8 free seats. However, 4 seats are reserved for Dev Team 2 onboarding until day 20, so only 4 seats are actually available.
- Analytics | total seats | 21 |  | db, day 8: D1
- Analytics | used seats (database, registered day 8) | 13 |  | db, day 8: D1
- Analytics | free seats (unused) | 8 |  | db, day 8: D1
- Analytics | free seats calculation | 21 - 13 = 8 |  | db, day 8: D1
- Analytics | reserved seats for Dev Team 2 onboarding | 4 | held until day 20 | history, day 6: H195
- Analytics | available seats (excluding reserved per hold_policy) | 4 |  | rule, day fixed: rule: hold_policy
- Analytics | available seats calculation | 21 - 13 - 4 = 4 |  | rule, day fixed: rule: hold_policy
```

## CASE 57: deepseek-v4-flash · direct · s14 · W-00036 · class C · day 4 · template capacity
### Task as given to the requester
How many in-house monitor (basic) units and CAD seats are actually available right now?
[Request scope] item=monitor; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only; seat lookup regions=the requesting region and the first other region in the public region list (report each separately). Evaluate within the optional review scope stated here.
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
{"stock": 5, "seats": 4, "seats_other_region": 0}
### Counterfactual answers (generator)
{"stale": {"stock": 3, "seats": 4, "seats_other_region": 0}, "partial": {"stock": 3, "seats": 4, "seats_other_region": 0}, "neardup": {"stock": 5, "seats": 0, "seats_other_region": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/stock/INV-TYO-MNB** (group IT-TYO, class A, local=False)
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-MNB"}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01164 [decision-critical] (db_pending/observation, day 4, by it-tyo.w00171; DB shows 7): In-house stock monitor (basic) Receipt added. Stored value: 6
- RECORD FR-01053 [decision-critical] (operational/pending_intent, day 2, by it-tyo.w00151; DB shows n/a): In-house stock monitor (basic) 1 unit held as a Support Section replacement spare until day 8.
**need IT-TYO/license/CAD** (group IT-TYO, class A, local=False)
- DB `IT-TYO/lic/CAD/seats` v1 (recorded day -20, registered day -20): {"seats": 38, "used": 34}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need IT-SEL/license/CAD** (group IT-SEL, class C, local=False)
- DB `IT-SEL/lic/CAD/seats` v6 (recorded day -2, registered day 0): {"seats": 31, "used": 23}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00870 [decision-critical] (operational/pending_intent, day -3, by it-sel.a4; DB shows n/a): CAD seats 3 seats reserved for Marketing Team project until day 11.
- RECORD FR-00879 [decision-critical] (operational/pending_intent, day -2, by it-sel.n0002; DB shows n/a): CAD seats 3 seats reserved for Sales Team 2 onboarding until day 10.
- RECORD FR-00994 [decision-critical] (operational/pending_intent, day 1, by it-sel.a4; DB shows n/a): CAD seats 4 seats reserved for Dev Team 1 project until day 11.
### Model answer and official verdict
answer: {"seats": 4, "seats_other_region": 1, "stock": 5}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-01164 (need IT-TYO/stock/INV-TYO-MNB): matcher says **stale**
record text: In-house stock monitor (basic) Receipt added. Stored value: 6
What the requester received from IT-TYO during this task:
```
INV-TYO-MNB (basic monitor, TYO) has 5 units in the database (registered day 3). A worker report on day 4 indicates a receipt was added, which is newer than the database value. No hold is recorded in my area's records or database, so I cannot confirm the Support Section replacement spare hold. The only other monitor in TYO is INV-TYO-MNS (standard tier), not basic.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database) | 5 |  | db, day 3: D1
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D1
- INV-TYO-MNB | worker report — receipt added (day 4) | receipt added | newer than database day 3 | history, day 4: H773
- INV-TYO-MNS | item_id | INV-TYO-MNS |  | db, day fixed: D5
- INV-TYO-MNS | type | monitor |  | db, day fixed: D5
- INV-TYO-MNS | tier | standard |  | db, day fixed: D5
- INV-TYO-MNS | region | TYO |  | db, day fixed: D5
missing: INV-TYO-MNB — hold as Support Section replacement spare until day 8: no record of any hold on INV-TYO-MNB found in my area's records or database; cannot confirm this hold exists; Any other basic monitor inventory items in TYO region besides INV-TYO-MNB: none found — INV-TYO-MNS is standard tier, not basic
---
My area manages software license seats. CAD has 38 total seats, 34 used, leaving 4 free. No holds or reservations were found, so all 4 free seats are available. The license_seats record does not include a region field, so I cannot confirm this is TYO-specific.
- CAD | total license seats | 38 |  | db, day -20: D1
- CAD | used license seats | 34 |  | db, day -20: D1
- CAD | free license seats (calculated) | 4 |  | db, day -20: D1
- CAD | available seats after holds/reservations | 4 |  | db, day -20: D1
- TYO region | region of CAD license_seats record | not specified — license_seats record has no region field |  | db, day -20: D1
missing: CAD — any holds or reservations on seats: none found in my area's records or database; CAD — catalog_entry: NO_RECORD (no master data entry registered)
---
The database shows INV-TYO-MNB has 5 units in stock, registered on day 3. A worker report on day 3 (H773) recorded a receipt added for "In-house stock monitor (basic)" which matches INV-TYO-MNB, but the report does not specify how many units were received. Without a quantity in the receipt record, I cannot determine how many units were received or calculate an updated available quantity.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database) | 5 |  | db, day 3: D1
- INV-TYO-MNB | registered_day (database) | 3 |  | db, day 3: D1
- INV-TYO-MNB | worker report receipt | Receipt added (In-house stock monitor basic) |  | history, day 4: H773
missing: INV-TYO-MNB — number of units received in the receipt: the worker report (H773) does not specify a quantity; it only states 'Receipt added'; INV-TYO-MNB — actual available quantity as of day 4 considering the receipt: the database shows 5 units registered on day 3; the receipt (also day 3) does not state how many units were added, so I cannot calculate a post-receipt quantity
---
My area's database and records show INV-TYO-MNB (basic monitor, TYO region) has 5 units in stock registered on day 3, with no holds, reservations, or exclusions of any kind recorded. The record you mention from day 2 about '1 unit held as a Support Section replacement spare, held until day 8' is not present in my area's records or database.
- INV-TYO-MNB | inventory quantity | 5 |  | db, day 3: D1
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D1
missing: INV-TYO-MNB — any hold or reservation: none found in my area's database or records; the inventory_quantity record shows 5 units with no holds, reservations, or exclusions recorded
---
The CAD license_seats record shows 38 total, 34 used, 4 free. The record has no region field. There are no separate records for 'CAD TYO' or 'CAD SEL'. My area is TYO region, so this is the data available in my area's database, but I cannot confirm whether it represents TYO specifically or a global pool.
- CAD | total license seats | 38 |  | db, day -20: D1
- CAD | used license seats | 34 |  | db, day -20: D1
- CAD | free license seats (calculated) | 4 |  | db, day -20: D1
- CAD | region specified in license_seats record | not present — license_seats record has no region field |  | db, day -20: D1
- CAD | catalog_entry | NO_RECORD — no master data entry with region specification |  | db, day unknown: D2
- CAD TYO | license_seats | NOT_FOUND |  | db, day unknown: D3
- CAD SEL | license_seats | NOT_FOUND |  | db, day unknown: D4
missing: CAD — whether the 38/34 count is specific to TYO region: my area's license_seats records do not include a region field, so I cannot confirm this; my area is TYO region, so this is the data available in my area's database; CAD — whether licenses are managed per region or globally: my area's records and database do not contain information about how licensing is structured across regions
---
H773 is a tool result record from day 4 with the full text: "Recorded — In-house stock monitor (basic) [Worker report] Receipt added." It indicates a receipt was added for INV-TYO-MNB (basic monitor). The database shows 5 units in stock registered on day 3.
- H773 | record type | [Tool result] |  | history, day 4: H773
- H773 | day | day 4 |  | history, day 4: H773
- H773 | full text | Recorded — In-house stock monitor (basic) [Worker report] Receipt added. |  | history, day 4: H773
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D1
- INV-TYO-MNB | type | monitor |  | db, day fixed: D1
- INV-TYO-MNB | tier | basic |  | db, day fixed: D1
- INV-TYO-MNB | region | TYO |  | db, day fixed: D1
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D1
- INV-TYO-MNB | inventory quantity (database, day 3) | 5 |  | db, day 3: D2
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D2
---
The database shows INV-TYO-MNB has 5 units in stock as of day 3. A worker report on day 4 confirms a receipt was added, but the record does not specify how many units were received, so I cannot determine the current total stock.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database, registered day 3) | 5 |  | db, day 3: D1
- INV-TYO-MNB | receipt added (day 4 worker report) | Receipt added — quantity not specified in record |  | history, day 4: H773
missing: INV-TYO-MNB — quantity received on day 4: not specified in the worker report record (H773); cannot calculate current total stock
```
### MATCHER CHECK FR-01053 (need IT-TYO/stock/INV-TYO-MNB): matcher says **missing**
record text: In-house stock monitor (basic) 1 unit held as a Support Section replacement spare until day 8.
What the requester received from IT-TYO during this task:
```
INV-TYO-MNB (basic monitor, TYO) has 5 units in the database (registered day 3). A worker report on day 4 indicates a receipt was added, which is newer than the database value. No hold is recorded in my area's records or database, so I cannot confirm the Support Section replacement spare hold. The only other monitor in TYO is INV-TYO-MNS (standard tier), not basic.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database) | 5 |  | db, day 3: D1
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D1
- INV-TYO-MNB | worker report — receipt added (day 4) | receipt added | newer than database day 3 | history, day 4: H773
- INV-TYO-MNS | item_id | INV-TYO-MNS |  | db, day fixed: D5
- INV-TYO-MNS | type | monitor |  | db, day fixed: D5
- INV-TYO-MNS | tier | standard |  | db, day fixed: D5
- INV-TYO-MNS | region | TYO |  | db, day fixed: D5
missing: INV-TYO-MNB — hold as Support Section replacement spare until day 8: no record of any hold on INV-TYO-MNB found in my area's records or database; cannot confirm this hold exists; Any other basic monitor inventory items in TYO region besides INV-TYO-MNB: none found — INV-TYO-MNS is standard tier, not basic
---
My area manages software license seats. CAD has 38 total seats, 34 used, leaving 4 free. No holds or reservations were found, so all 4 free seats are available. The license_seats record does not include a region field, so I cannot confirm this is TYO-specific.
- CAD | total license seats | 38 |  | db, day -20: D1
- CAD | used license seats | 34 |  | db, day -20: D1
- CAD | free license seats (calculated) | 4 |  | db, day -20: D1
- CAD | available seats after holds/reservations | 4 |  | db, day -20: D1
- TYO region | region of CAD license_seats record | not specified — license_seats record has no region field |  | db, day -20: D1
missing: CAD — any holds or reservations on seats: none found in my area's records or database; CAD — catalog_entry: NO_RECORD (no master data entry registered)
---
The database shows INV-TYO-MNB has 5 units in stock, registered on day 3. A worker report on day 3 (H773) recorded a receipt added for "In-house stock monitor (basic)" which matches INV-TYO-MNB, but the report does not specify how many units were received. Without a quantity in the receipt record, I cannot determine how many units were received or calculate an updated available quantity.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database) | 5 |  | db, day 3: D1
- INV-TYO-MNB | registered_day (database) | 3 |  | db, day 3: D1
- INV-TYO-MNB | worker report receipt | Receipt added (In-house stock monitor basic) |  | history, day 4: H773
missing: INV-TYO-MNB — number of units received in the receipt: the worker report (H773) does not specify a quantity; it only states 'Receipt added'; INV-TYO-MNB — actual available quantity as of day 4 considering the receipt: the database shows 5 units registered on day 3; the receipt (also day 3) does not state how many units were added, so I cannot calculate a post-receipt quantity
---
My area's database and records show INV-TYO-MNB (basic monitor, TYO region) has 5 units in stock registered on day 3, with no holds, reservations, or exclusions of any kind recorded. The record you mention from day 2 about '1 unit held as a Support Section replacement spare, held until day 8' is not present in my area's records or database.
- INV-TYO-MNB | inventory quantity | 5 |  | db, day 3: D1
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D1
missing: INV-TYO-MNB — any hold or reservation: none found in my area's database or records; the inventory_quantity record shows 5 units with no holds, reservations, or exclusions recorded
---
The CAD license_seats record shows 38 total, 34 used, 4 free. The record has no region field. There are no separate records for 'CAD TYO' or 'CAD SEL'. My area is TYO region, so this is the data available in my area's database, but I cannot confirm whether it represents TYO specifically or a global pool.
- CAD | total license seats | 38 |  | db, day -20: D1
- CAD | used license seats | 34 |  | db, day -20: D1
- CAD | free license seats (calculated) | 4 |  | db, day -20: D1
- CAD | region specified in license_seats record | not present — license_seats record has no region field |  | db, day -20: D1
- CAD | catalog_entry | NO_RECORD — no master data entry with region specification |  | db, day unknown: D2
- CAD TYO | license_seats | NOT_FOUND |  | db, day unknown: D3
- CAD SEL | license_seats | NOT_FOUND |  | db, day unknown: D4
missing: CAD — whether the 38/34 count is specific to TYO region: my area's license_seats records do not include a region field, so I cannot confirm this; my area is TYO region, so this is the data available in my area's database; CAD — whether licenses are managed per region or globally: my area's records and database do not contain information about how licensing is structured across regions
---
H773 is a tool result record from day 4 with the full text: "Recorded — In-house stock monitor (basic) [Worker report] Receipt added." It indicates a receipt was added for INV-TYO-MNB (basic monitor). The database shows 5 units in stock registered on day 3.
- H773 | record type | [Tool result] |  | history, day 4: H773
- H773 | day | day 4 |  | history, day 4: H773
- H773 | full text | Recorded — In-house stock monitor (basic) [Worker report] Receipt added. |  | history, day 4: H773
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D1
- INV-TYO-MNB | type | monitor |  | db, day fixed: D1
- INV-TYO-MNB | tier | basic |  | db, day fixed: D1
- INV-TYO-MNB | region | TYO |  | db, day fixed: D1
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D1
- INV-TYO-MNB | inventory quantity (database, day 3) | 5 |  | db, day 3: D2
- INV-TYO-MNB | registered_day | 3 |  | db, day 3: D2
---
The database shows INV-TYO-MNB has 5 units in stock as of day 3. A worker report on day 4 confirms a receipt was added, but the record does not specify how many units were received, so I cannot determine the current total stock.
- INV-TYO-MNB | item_id | INV-TYO-MNB |  | db, day fixed: D2
- INV-TYO-MNB | type | monitor |  | db, day fixed: D2
- INV-TYO-MNB | tier | basic |  | db, day fixed: D2
- INV-TYO-MNB | region | TYO |  | db, day fixed: D2
- INV-TYO-MNB | cost | 662355 |  | db, day fixed: D2
- INV-TYO-MNB | inventory quantity (database, registered day 3) | 5 |  | db, day 3: D1
- INV-TYO-MNB | receipt added (day 4 worker report) | Receipt added — quantity not specified in record |  | history, day 4: H773
missing: INV-TYO-MNB — quantity received on day 4: not specified in the worker report record (H773); cannot calculate current total stock
```
### MATCHER CHECK FR-00870 (need IT-SEL/license/CAD): matcher says **delivered**
record text: CAD seats 3 seats reserved for Marketing Team project until day 11.
What the requester received from IT-SEL during this task:
```
CAD has 31 total seats, 23 in use, and 7 actively reserved (3 for Marketing Team until day 11, 4 for Dev Team 1 until day 11). Excluding used and reserved seats, 1 seat is actually available.
- CAD | total seats | 31 |  | db, day 0: D1
- CAD | used seats (database, day 0) | 23 |  | db, day 0: D1
- CAD | used seats (latest record, day -2) | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 | 4 | active | history, day 1: H113
- CAD | available seats (total - used - reserved) | 1 |  | rule, day fixed: rule hold_policy
---
Yes, the CAD seat information I provided is specifically for the SEL region. My area's records and database only cover SEL; I have no data on CAD seats in the TYO region.
- CAD | total seats (SEL) | 31 |  | db, day 0: D1
- CAD | used seats (SEL) - database day 0 | 23 |  | db, day 0: D1
- CAD | used seats (SEL) - latest record day -2 | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 (SEL) | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 (SEL) | 4 | active | history, day 1: H113
- CAD | available seats (SEL) | 1 |  | rule, day fixed: rule hold_policy
missing: CAD total seats in TYO region; CAD used seats in TYO region; CAD holds or reservations in TYO region; CAD available seats in TYO region
```
### MATCHER CHECK FR-00879 (need IT-SEL/license/CAD): matcher says **stale**
record text: CAD seats 3 seats reserved for Sales Team 2 onboarding until day 10.
What the requester received from IT-SEL during this task:
```
CAD has 31 total seats, 23 in use, and 7 actively reserved (3 for Marketing Team until day 11, 4 for Dev Team 1 until day 11). Excluding used and reserved seats, 1 seat is actually available.
- CAD | total seats | 31 |  | db, day 0: D1
- CAD | used seats (database, day 0) | 23 |  | db, day 0: D1
- CAD | used seats (latest record, day -2) | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 | 4 | active | history, day 1: H113
- CAD | available seats (total - used - reserved) | 1 |  | rule, day fixed: rule hold_policy
---
Yes, the CAD seat information I provided is specifically for the SEL region. My area's records and database only cover SEL; I have no data on CAD seats in the TYO region.
- CAD | total seats (SEL) | 31 |  | db, day 0: D1
- CAD | used seats (SEL) - database day 0 | 23 |  | db, day 0: D1
- CAD | used seats (SEL) - latest record day -2 | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 (SEL) | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 (SEL) | 4 | active | history, day 1: H113
- CAD | available seats (SEL) | 1 |  | rule, day fixed: rule hold_policy
missing: CAD total seats in TYO region; CAD used seats in TYO region; CAD holds or reservations in TYO region; CAD available seats in TYO region
```
### MATCHER CHECK FR-00994 (need IT-SEL/license/CAD): matcher says **delivered**
record text: CAD seats 4 seats reserved for Dev Team 1 project until day 11.
What the requester received from IT-SEL during this task:
```
CAD has 31 total seats, 23 in use, and 7 actively reserved (3 for Marketing Team until day 11, 4 for Dev Team 1 until day 11). Excluding used and reserved seats, 1 seat is actually available.
- CAD | total seats | 31 |  | db, day 0: D1
- CAD | used seats (database, day 0) | 23 |  | db, day 0: D1
- CAD | used seats (latest record, day -2) | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 | 4 | active | history, day 1: H113
- CAD | available seats (total - used - reserved) | 1 |  | rule, day fixed: rule hold_policy
---
Yes, the CAD seat information I provided is specifically for the SEL region. My area's records and database only cover SEL; I have no data on CAD seats in the TYO region.
- CAD | total seats (SEL) | 31 |  | db, day 0: D1
- CAD | used seats (SEL) - database day 0 | 23 |  | db, day 0: D1
- CAD | used seats (SEL) - latest record day -2 | 23 |  | history, day -2: H107
- CAD | reserved seats - Marketing Team project until day 11 (SEL) | 3 | active | history, day -3: H104
- CAD | reserved seats - Dev Team 1 project until day 11 (SEL) | 4 | active | history, day 1: H113
- CAD | available seats (SEL) | 1 |  | rule, day fixed: rule hold_policy
missing: CAD total seats in TYO region; CAD used seats in TYO region; CAD holds or reservations in TYO region; CAD available seats in TYO region
```

## CASE 58: deepseek-v4-flash · direct · s14 · W-00092 · class D · day 10 · template vendor
### Task as given to the requester
Support Section needs a laptop. Pick a compliant supplier within budget.
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=the requesting region and the first other region in the public region list. Evaluate within the optional review scope stated here.
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
{"vendor": null, "option": null, "amount": null, "approver": null, "budget_after": null, "blocked_by": "lead_time"}
### Counterfactual answers (generator)
{"stale": {"vendor": "V-SEL-3", "option": "Q-V-SEL-3-LTB", "amount": 461132, "approver": "team_lead", "budget_after": 652383, "blocked_by": null}, "partial": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 534454, "approver": "team_lead", "budget_after": 579061, "blocked_by": null}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/Support Section/budget_schedule** (group FIN-TYO, class None, local=True)
- DB `FIN-TYO/line/Support Section/remaining` v7 (recorded day 1, registered day 3): 3172078
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01414 (operational/pending_intent, day 8, by fin-tyo.a3; DB shows n/a): Support Section capex 364,362 KRW earmarked for training equipment until day 13 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00003/status` v2 (recorded day -7, registered day -6): {"status": "settled", "amount": 778994, "expected_settle": -7}
- DB `FIN-TYO/commit/CMT-00021/status` v2 (recorded day 0, registered day 3): {"status": "settled", "amount": 725763, "expected_settle": 0}
- DB `FIN-TYO/commit/CMT-00025/status` v2 (recorded day -1, registered day 0): {"status": "settled", "amount": 879454, "expected_settle": -1}
- DB `FIN-TYO/commit/CMT-00033/status` v2 (recorded day 1, registered day 2): {"status": "settled", "amount": 533734, "expected_settle": 1}
- DB `FIN-TYO/commit/CMT-00052/status` v2 (recorded day 7, registered day 8): {"status": "settled", "amount": 246392, "expected_settle": 7}
- RECORD FR-01463 (db_pending/observation, day 9, by fin-tyo.a3; DB shows 1): CMT-00095 Support Section provisional approval settled. Stored value: {"amount":201773,"expected_settle":9,"status":"settled"}
- RECORD FR-01415 (operational/pending_intent, day 8, by fin-tyo.a3; DB shows n/a): CMT-00110 Support Section monitor provisional approval 646,298 KRW under review, settlement expected day 13.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Support Section AND status IN ['reviewing', 'pending'] → ["earmark:FR-01414", "CMT-00085", "CMT-00098", "CMT-00110"]
**need PROC-TYO/quotes/laptop** (group PROC-TYO, class A, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01188 (operational/handover, day 4, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-1 exclude from comparisons until day 12 due to a quality issue.
- RECORD FR-01388 (operational/handover, day 8, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 22 due to a quality issue.
- RECORD FR-01488 (operational/handover, day 9, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-2 exclude from comparisons until day 17 due to a quality issue.
- RECORD FR-01495 (operational/handover, day 10, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-3 exclude from comparisons until day 19 due to a quality issue.
- RECORD FR-01152 (operational/observation, day 3, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01239 (operational/observation, day 5, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-1 delivery notified: deliveries delayed by 4 days until day 19.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01329 (operational/observation, day 7, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day 7, registered day 8): 9
- DB `PROC-TYO/quote/Q-V-TYO-1-LTS/amount` v1 (recorded day -20, registered day -20): 1077364
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01494 (db_pending/observation, day 10, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 12
- DB `PROC-TYO/quote/Q-V-TYO-2-LTB/amount` v4 (recorded day 5, registered day 8): 647783
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01494 (db_pending/observation, day 10, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 12
- DB `PROC-TYO/quote/Q-V-TYO-2-LTP/amount` v2 (recorded day 2, registered day 3): 2135766
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v4 (recorded day -1, registered day 1): 8
- DB `PROC-TYO/quote/Q-V-TYO-3-LTB/amount` v2 (recorded day 1, registered day 3): 543753
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v4 (recorded day -1, registered day 1): 8
- DB `PROC-TYO/quote/Q-V-TYO-3-LTP/amount` v1 (recorded day -20, registered day -20): 2178635
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v4 (recorded day -1, registered day 1): 8
- DB `PROC-TYO/quote/Q-V-TYO-3-LTS/amount` v2 (recorded day -7, registered day -6): 1072284
**need PROC-SEL/quotes/laptop** (group PROC-SEL, class D, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00983 (operational/handover, day 0, by proc-sel.w00136; DB shows n/a): Supplier V-SEL-1 exclude from comparisons until day 10 due to a quality issue.
- RECORD FR-01275 [decision-critical] (operational/handover, day 6, by proc-sel.w00193; DB shows n/a): Supplier V-SEL-0 exclude from comparisons until day 16 due to a quality issue.
- RECORD FR-01420 [decision-critical] (operational/handover, day 8, by proc-sel.w00221; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 21 due to a quality issue.
- RECORD FR-01082 [decision-critical] (operational/observation, day 2, by proc-sel.w00155; DB shows n/a): Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01168 (operational/observation, day 4, by proc-sel.w00172; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 4 days until day 16.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01418 (operational/observation, day 8, by proc-sel.w00220; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 2 days until day 13.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-LTB/amount` v2 (recorded day -11, registered day -9): 534454
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-LTP/amount` v1 (recorded day -20, registered day -20): 2113187
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day -18, registered day -17): 9
- DB `PROC-SEL/quote/Q-V-SEL-0-LTS/amount` v1 (recorded day -20, registered day -20): 1154392
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v3 (recorded day -5, registered day -4): 12
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
- RECORD FR-01417 [decision-critical] (db_pending/rationale, day 8, by proc-sel.w00219; DB shows 2): V-SEL-3 laptop (basic) quote Q-V-SEL-3-LTB changed to 461,132 KRW (raw material prices). Stored value: 461132
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v5 (recorded day 6, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTP/amount` v1 (recorded day -20, registered day -20): 2367972
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v5 (recorded day 6, registered day 7): 9
- DB `PROC-SEL/quote/Q-V-SEL-3-LTS/amount` v2 (recorded day -1, registered day 2): 1379255
### Model answer and official verdict
answer: {"amount": 534454, "approver": "team_lead", "blocked_by": null, "budget_after": 579061, "option": "Q-V-SEL-0-LTB", "vendor": "V-SEL-0"}
official exact match: 0 (0/6 slots)
### MATCHER CHECK FR-01275 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-0 exclude from comparisons until day 16 due to a quality issue.
What the requester received from PROC-SEL during this task:
```
Here are all SEL region laptop quotes. Suppliers: V-SEL-0 (registered, lead time 9d) has premium (2,113,187 KRW), standard (1,154,392 KRW), basic (534,454 KRW) quotes. V-SEL-1 (registered, lead time 12d) has only standard (1,452,400 KRW). V-SEL-2 (registered, lead time 8d, but delay notice adds 2d until day 13, and excluded from comparisons until day 21) has premium (1,908,409 KRW), standard (1,259,460 KRW), basic (489,150 KRW). V-SEL-3 (NOT registered, lead time 9d) has premium (2,367,972 KRW), standard (1,379,255 KRW), basic (772,879 KRW). Note: For a department order (Support Section in TYO), lead_time_limit rule allows only suppliers with lead time ≤10 days. V-SEL-1 (12d) exceeds this. V-SEL-2's effective lead time with delay is 10d which meets the limit, but it is excluded from comparisons until day 21. V-SEL-3 is not registered as a vendor.
- Q-V-SEL-0-LTP | type | laptop |  | db, day fixed: D1
- Q-V-SEL-0-LTP | tier | premium |  | db, day fixed: D1
- Q-V-SEL-0-LTP | vendor | V-SEL-0 |  | db, day fixed: D1
- Q-V-SEL-0-LTP | quote_amount | 2113187 |  | db, day -20: D13
- Q-V-SEL-0-LTS | type | laptop |  | db, day fixed: D2
- Q-V-SEL-0-LTS | tier | standard |  | db, day fixed: D2
- Q-V-SEL-0-LTS | vendor | V-SEL-0 |  | db, day fixed: D2
- Q-V-SEL-0-LTS | quote_amount | 1154392 |  | db, day -20: D14
- Q-V-SEL-0-LTB | type | laptop |  | db, day fixed: D10
- Q-V-SEL-0-LTB | tier | basic |  | db, day fixed: D10
- Q-V-SEL-0-LTB | vendor | V-SEL-0 |  | db, day fixed: D10
- Q-V-SEL-0-LTB | quote_amount | 534454 |  | db, day -9: D15
- Q-V-SEL-1-LTS | type | laptop |  | db, day fixed: D3
- Q-V-SEL-1-LTS | tier | standard |  | db, day fixed: D3
- Q-V-SEL-1-LTS | vendor | V-SEL-1 |  | db, day fixed: D3
- Q-V-SEL-1-LTS | quote_amount | 1452400 |  | db, day -20: D16
- Q-V-SEL-2-LTP | type | laptop |  | db, day fixed: D5
- Q-V-SEL-2-LTP | tier | premium |  | db, day fixed: D5
- Q-V-SEL-2-LTP | vendor | V-SEL-2 |  | db, day fixed: D5
- Q-V-SEL-2-LTP | quote_amount | 1908409 |  | db, day 8: D17
- Q-V-SEL-2-LTS | type | laptop |  | db, day fixed: D4
- Q-V-SEL-2-LTS | tier | standard |  | db, day fixed: D4
- Q-V-SEL-2-LTS | vendor | V-SEL-2 |  | db, day fixed: D4
- Q-V-SEL-2-LTS | quote_amount | 1259460 |  | db, day -20: D18
- Q-V-SEL-2-LTB | type | laptop |  | db, day fixed: D12
- Q-V-SEL-2-LTB | tier | basic |  | db, day fixed: D12
- Q-V-SEL-2-LTB | vendor | V-SEL-2 |  | db, day fixed: D12
- Q-V-SEL-2-LTB | quote_amount | 489150 |  | db, day -20: D19
- Q-V-SEL-3-LTP | type | laptop |  | db, day fixed: D7
- Q-V-SEL-3-LTP | tier | premium |  | db, day fixed: D7
- Q-V-SEL-3-LTP | vendor | V-SEL-3 |  | db, day fixed: D7
- Q-V-SEL-3-LTP | quote_amount | 2367972 |  | db, day -20: D20
- Q-V-SEL-3-LTS | type | laptop |  | db, day fixed: D6
- Q-V-SEL-3-LTS | tier | standard |  | db, day fixed: D6
- Q-V-SEL-3-LTS | vendor | V-SEL-3 |  | db, day fixed: D6
- Q-V-SEL-3-LTS | quote_amount | 1379255 |  | db, day 2: D21
- Q-V-SEL-3-LTB | type | laptop |  | db, day fixed: D8
- Q-V-SEL-3-LTB | tier | basic |  | db, day fixed: D8
- Q-V-SEL-3-LTB | vendor | V-SEL-3 |  | db, day fixed: D8
- Q-V-SEL-3-LTB | quote_amount | 772879 |  | db, day -6: D22
- V-SEL-0 | vendor_lead_time | 9 |  | db, day -17: D23
- V-SEL-0 | vendor_registration | true |  | db, day -20: D27
- V-SEL-1 | vendor_lead_time | 12 |  | db, day -4: D24
- V-SEL-1 | vendor_registration | true |  | db, day -20: D28
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D25
- V-SEL-2 | vendor_registration | true |  | db, day -20: D29
- V-SEL-2 | delay_notice | delayed by 2 days until day 13 | in effect on day 10 | history, day 8: H2409
- V-SEL-2 | excluded_from_comparisons | excluded until day 21 | in effect on day 10 | history, day 8: H2410
- V-SEL-3 | vendor_lead_time | 9 |  | db, day 7: D26
- V-SEL-3 | vendor_registration | false |  | db, day -20: D30
missing: Support Section in TYO — employee/department information not found in my area's records
---
The lead_time_limit rule states: personal equipment orders use only suppliers with lead time ≤7 days; department orders use only suppliers with lead time ≤10 days. The rule does not list specific departments — it simply says "department orders." It is part of the SEL area's rules. The rule does not mention TYO or any other region, so I cannot confirm whether it applies to TYO suppliers or TYO departments from my own records.
- lead_time_limit | rule text | Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less. |  | rule, day fixed: lead_time_limit
- lead_time_limit | applies to departments | The rule distinguishes between 'personal equipment orders' and 'department orders' but does not list specific departments by name. |  | rule, day fixed: lead_time_limit
- lead_time_limit | TYO region applicability | The rule is in the SEL area's rules and does not mention TYO or any other region. It does not specify whether it applies across regions. |  | rule, day fixed: lead_time_limit
- lead_time_limit | SEL region applicability | The rule is part of the SEL area's rules, so it governs orders placed in the SEL region. |  | rule, day fixed: lead_time_limit
missing: Whether the lead_time_limit rule applies to all departments or just some — the rule text only says 'department orders' without listing specific departments; no catalog entries define which departments are covered.; Whether the rule applies to TYO suppliers when ordering for a TYO department — the rule is in the SEL area's rules and does not mention TYO; I have no records about TYO region rules or how they interact with SEL rules.
```
### MATCHER CHECK FR-01420 (need PROC-SEL/quotes/laptop): matcher says **delivered**
record text: Supplier V-SEL-2 exclude from comparisons until day 21 due to a quality issue.
What the requester received from PROC-SEL during this task:
```
Here are all SEL region laptop quotes. Suppliers: V-SEL-0 (registered, lead time 9d) has premium (2,113,187 KRW), standard (1,154,392 KRW), basic (534,454 KRW) quotes. V-SEL-1 (registered, lead time 12d) has only standard (1,452,400 KRW). V-SEL-2 (registered, lead time 8d, but delay notice adds 2d until day 13, and excluded from comparisons until day 21) has premium (1,908,409 KRW), standard (1,259,460 KRW), basic (489,150 KRW). V-SEL-3 (NOT registered, lead time 9d) has premium (2,367,972 KRW), standard (1,379,255 KRW), basic (772,879 KRW). Note: For a department order (Support Section in TYO), lead_time_limit rule allows only suppliers with lead time ≤10 days. V-SEL-1 (12d) exceeds this. V-SEL-2's effective lead time with delay is 10d which meets the limit, but it is excluded from comparisons until day 21. V-SEL-3 is not registered as a vendor.
- Q-V-SEL-0-LTP | type | laptop |  | db, day fixed: D1
- Q-V-SEL-0-LTP | tier | premium |  | db, day fixed: D1
- Q-V-SEL-0-LTP | vendor | V-SEL-0 |  | db, day fixed: D1
- Q-V-SEL-0-LTP | quote_amount | 2113187 |  | db, day -20: D13
- Q-V-SEL-0-LTS | type | laptop |  | db, day fixed: D2
- Q-V-SEL-0-LTS | tier | standard |  | db, day fixed: D2
- Q-V-SEL-0-LTS | vendor | V-SEL-0 |  | db, day fixed: D2
- Q-V-SEL-0-LTS | quote_amount | 1154392 |  | db, day -20: D14
- Q-V-SEL-0-LTB | type | laptop |  | db, day fixed: D10
- Q-V-SEL-0-LTB | tier | basic |  | db, day fixed: D10
- Q-V-SEL-0-LTB | vendor | V-SEL-0 |  | db, day fixed: D10
- Q-V-SEL-0-LTB | quote_amount | 534454 |  | db, day -9: D15
- Q-V-SEL-1-LTS | type | laptop |  | db, day fixed: D3
- Q-V-SEL-1-LTS | tier | standard |  | db, day fixed: D3
- Q-V-SEL-1-LTS | vendor | V-SEL-1 |  | db, day fixed: D3
- Q-V-SEL-1-LTS | quote_amount | 1452400 |  | db, day -20: D16
- Q-V-SEL-2-LTP | type | laptop |  | db, day fixed: D5
- Q-V-SEL-2-LTP | tier | premium |  | db, day fixed: D5
- Q-V-SEL-2-LTP | vendor | V-SEL-2 |  | db, day fixed: D5
- Q-V-SEL-2-LTP | quote_amount | 1908409 |  | db, day 8: D17
- Q-V-SEL-2-LTS | type | laptop |  | db, day fixed: D4
- Q-V-SEL-2-LTS | tier | standard |  | db, day fixed: D4
- Q-V-SEL-2-LTS | vendor | V-SEL-2 |  | db, day fixed: D4
- Q-V-SEL-2-LTS | quote_amount | 1259460 |  | db, day -20: D18
- Q-V-SEL-2-LTB | type | laptop |  | db, day fixed: D12
- Q-V-SEL-2-LTB | tier | basic |  | db, day fixed: D12
- Q-V-SEL-2-LTB | vendor | V-SEL-2 |  | db, day fixed: D12
- Q-V-SEL-2-LTB | quote_amount | 489150 |  | db, day -20: D19
- Q-V-SEL-3-LTP | type | laptop |  | db, day fixed: D7
- Q-V-SEL-3-LTP | tier | premium |  | db, day fixed: D7
- Q-V-SEL-3-LTP | vendor | V-SEL-3 |  | db, day fixed: D7
- Q-V-SEL-3-LTP | quote_amount | 2367972 |  | db, day -20: D20
- Q-V-SEL-3-LTS | type | laptop |  | db, day fixed: D6
- Q-V-SEL-3-LTS | tier | standard |  | db, day fixed: D6
- Q-V-SEL-3-LTS | vendor | V-SEL-3 |  | db, day fixed: D6
- Q-V-SEL-3-LTS | quote_amount | 1379255 |  | db, day 2: D21
- Q-V-SEL-3-LTB | type | laptop |  | db, day fixed: D8
- Q-V-SEL-3-LTB | tier | basic |  | db, day fixed: D8
- Q-V-SEL-3-LTB | vendor | V-SEL-3 |  | db, day fixed: D8
- Q-V-SEL-3-LTB | quote_amount | 772879 |  | db, day -6: D22
- V-SEL-0 | vendor_lead_time | 9 |  | db, day -17: D23
- V-SEL-0 | vendor_registration | true |  | db, day -20: D27
- V-SEL-1 | vendor_lead_time | 12 |  | db, day -4: D24
- V-SEL-1 | vendor_registration | true |  | db, day -20: D28
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D25
- V-SEL-2 | vendor_registration | true |  | db, day -20: D29
- V-SEL-2 | delay_notice | delayed by 2 days until day 13 | in effect on day 10 | history, day 8: H2409
- V-SEL-2 | excluded_from_comparisons | excluded until day 21 | in effect on day 10 | history, day 8: H2410
- V-SEL-3 | vendor_lead_time | 9 |  | db, day 7: D26
- V-SEL-3 | vendor_registration | false |  | db, day -20: D30
missing: Support Section in TYO — employee/department information not found in my area's records
---
The lead_time_limit rule states: personal equipment orders use only suppliers with lead time ≤7 days; department orders use only suppliers with lead time ≤10 days. The rule does not list specific departments — it simply says "department orders." It is part of the SEL area's rules. The rule does not mention TYO or any other region, so I cannot confirm whether it applies to TYO suppliers or TYO departments from my own records.
- lead_time_limit | rule text | Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less. |  | rule, day fixed: lead_time_limit
- lead_time_limit | applies to departments | The rule distinguishes between 'personal equipment orders' and 'department orders' but does not list specific departments by name. |  | rule, day fixed: lead_time_limit
- lead_time_limit | TYO region applicability | The rule is in the SEL area's rules and does not mention TYO or any other region. It does not specify whether it applies across regions. |  | rule, day fixed: lead_time_limit
- lead_time_limit | SEL region applicability | The rule is part of the SEL area's rules, so it governs orders placed in the SEL region. |  | rule, day fixed: lead_time_limit
missing: Whether the lead_time_limit rule applies to all departments or just some — the rule text only says 'department orders' without listing specific departments; no catalog entries define which departments are covered.; Whether the rule applies to TYO suppliers when ordering for a TYO department — the rule is in the SEL area's rules and does not mention TYO; I have no records about TYO region rules or how they interact with SEL rules.
```
### MATCHER CHECK FR-01082 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: Supplier V-SEL-3 delivery notified: deliveries delayed by 3 days until day 15.
What the requester received from PROC-SEL during this task:
```
Here are all SEL region laptop quotes. Suppliers: V-SEL-0 (registered, lead time 9d) has premium (2,113,187 KRW), standard (1,154,392 KRW), basic (534,454 KRW) quotes. V-SEL-1 (registered, lead time 12d) has only standard (1,452,400 KRW). V-SEL-2 (registered, lead time 8d, but delay notice adds 2d until day 13, and excluded from comparisons until day 21) has premium (1,908,409 KRW), standard (1,259,460 KRW), basic (489,150 KRW). V-SEL-3 (NOT registered, lead time 9d) has premium (2,367,972 KRW), standard (1,379,255 KRW), basic (772,879 KRW). Note: For a department order (Support Section in TYO), lead_time_limit rule allows only suppliers with lead time ≤10 days. V-SEL-1 (12d) exceeds this. V-SEL-2's effective lead time with delay is 10d which meets the limit, but it is excluded from comparisons until day 21. V-SEL-3 is not registered as a vendor.
- Q-V-SEL-0-LTP | type | laptop |  | db, day fixed: D1
- Q-V-SEL-0-LTP | tier | premium |  | db, day fixed: D1
- Q-V-SEL-0-LTP | vendor | V-SEL-0 |  | db, day fixed: D1
- Q-V-SEL-0-LTP | quote_amount | 2113187 |  | db, day -20: D13
- Q-V-SEL-0-LTS | type | laptop |  | db, day fixed: D2
- Q-V-SEL-0-LTS | tier | standard |  | db, day fixed: D2
- Q-V-SEL-0-LTS | vendor | V-SEL-0 |  | db, day fixed: D2
- Q-V-SEL-0-LTS | quote_amount | 1154392 |  | db, day -20: D14
- Q-V-SEL-0-LTB | type | laptop |  | db, day fixed: D10
- Q-V-SEL-0-LTB | tier | basic |  | db, day fixed: D10
- Q-V-SEL-0-LTB | vendor | V-SEL-0 |  | db, day fixed: D10
- Q-V-SEL-0-LTB | quote_amount | 534454 |  | db, day -9: D15
- Q-V-SEL-1-LTS | type | laptop |  | db, day fixed: D3
- Q-V-SEL-1-LTS | tier | standard |  | db, day fixed: D3
- Q-V-SEL-1-LTS | vendor | V-SEL-1 |  | db, day fixed: D3
- Q-V-SEL-1-LTS | quote_amount | 1452400 |  | db, day -20: D16
- Q-V-SEL-2-LTP | type | laptop |  | db, day fixed: D5
- Q-V-SEL-2-LTP | tier | premium |  | db, day fixed: D5
- Q-V-SEL-2-LTP | vendor | V-SEL-2 |  | db, day fixed: D5
- Q-V-SEL-2-LTP | quote_amount | 1908409 |  | db, day 8: D17
- Q-V-SEL-2-LTS | type | laptop |  | db, day fixed: D4
- Q-V-SEL-2-LTS | tier | standard |  | db, day fixed: D4
- Q-V-SEL-2-LTS | vendor | V-SEL-2 |  | db, day fixed: D4
- Q-V-SEL-2-LTS | quote_amount | 1259460 |  | db, day -20: D18
- Q-V-SEL-2-LTB | type | laptop |  | db, day fixed: D12
- Q-V-SEL-2-LTB | tier | basic |  | db, day fixed: D12
- Q-V-SEL-2-LTB | vendor | V-SEL-2 |  | db, day fixed: D12
- Q-V-SEL-2-LTB | quote_amount | 489150 |  | db, day -20: D19
- Q-V-SEL-3-LTP | type | laptop |  | db, day fixed: D7
- Q-V-SEL-3-LTP | tier | premium |  | db, day fixed: D7
- Q-V-SEL-3-LTP | vendor | V-SEL-3 |  | db, day fixed: D7
- Q-V-SEL-3-LTP | quote_amount | 2367972 |  | db, day -20: D20
- Q-V-SEL-3-LTS | type | laptop |  | db, day fixed: D6
- Q-V-SEL-3-LTS | tier | standard |  | db, day fixed: D6
- Q-V-SEL-3-LTS | vendor | V-SEL-3 |  | db, day fixed: D6
- Q-V-SEL-3-LTS | quote_amount | 1379255 |  | db, day 2: D21
- Q-V-SEL-3-LTB | type | laptop |  | db, day fixed: D8
- Q-V-SEL-3-LTB | tier | basic |  | db, day fixed: D8
- Q-V-SEL-3-LTB | vendor | V-SEL-3 |  | db, day fixed: D8
- Q-V-SEL-3-LTB | quote_amount | 772879 |  | db, day -6: D22
- V-SEL-0 | vendor_lead_time | 9 |  | db, day -17: D23
- V-SEL-0 | vendor_registration | true |  | db, day -20: D27
- V-SEL-1 | vendor_lead_time | 12 |  | db, day -4: D24
- V-SEL-1 | vendor_registration | true |  | db, day -20: D28
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D25
- V-SEL-2 | vendor_registration | true |  | db, day -20: D29
- V-SEL-2 | delay_notice | delayed by 2 days until day 13 | in effect on day 10 | history, day 8: H2409
- V-SEL-2 | excluded_from_comparisons | excluded until day 21 | in effect on day 10 | history, day 8: H2410
- V-SEL-3 | vendor_lead_time | 9 |  | db, day 7: D26
- V-SEL-3 | vendor_registration | false |  | db, day -20: D30
missing: Support Section in TYO — employee/department information not found in my area's records
---
The lead_time_limit rule states: personal equipment orders use only suppliers with lead time ≤7 days; department orders use only suppliers with lead time ≤10 days. The rule does not list specific departments — it simply says "department orders." It is part of the SEL area's rules. The rule does not mention TYO or any other region, so I cannot confirm whether it applies to TYO suppliers or TYO departments from my own records.
- lead_time_limit | rule text | Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less. |  | rule, day fixed: lead_time_limit
- lead_time_limit | applies to departments | The rule distinguishes between 'personal equipment orders' and 'department orders' but does not list specific departments by name. |  | rule, day fixed: lead_time_limit
- lead_time_limit | TYO region applicability | The rule is in the SEL area's rules and does not mention TYO or any other region. It does not specify whether it applies across regions. |  | rule, day fixed: lead_time_limit
- lead_time_limit | SEL region applicability | The rule is part of the SEL area's rules, so it governs orders placed in the SEL region. |  | rule, day fixed: lead_time_limit
missing: Whether the lead_time_limit rule applies to all departments or just some — the rule text only says 'department orders' without listing specific departments; no catalog entries define which departments are covered.; Whether the rule applies to TYO suppliers when ordering for a TYO department — the rule is in the SEL area's rules and does not mention TYO; I have no records about TYO region rules or how they interact with SEL rules.
```
### MATCHER CHECK FR-01417 (need PROC-SEL/quotes/laptop): matcher says **missing**
record text: V-SEL-3 laptop (basic) quote Q-V-SEL-3-LTB changed to 461,132 KRW (raw material prices). Stored value: 461132
What the requester received from PROC-SEL during this task:
```
Here are all SEL region laptop quotes. Suppliers: V-SEL-0 (registered, lead time 9d) has premium (2,113,187 KRW), standard (1,154,392 KRW), basic (534,454 KRW) quotes. V-SEL-1 (registered, lead time 12d) has only standard (1,452,400 KRW). V-SEL-2 (registered, lead time 8d, but delay notice adds 2d until day 13, and excluded from comparisons until day 21) has premium (1,908,409 KRW), standard (1,259,460 KRW), basic (489,150 KRW). V-SEL-3 (NOT registered, lead time 9d) has premium (2,367,972 KRW), standard (1,379,255 KRW), basic (772,879 KRW). Note: For a department order (Support Section in TYO), lead_time_limit rule allows only suppliers with lead time ≤10 days. V-SEL-1 (12d) exceeds this. V-SEL-2's effective lead time with delay is 10d which meets the limit, but it is excluded from comparisons until day 21. V-SEL-3 is not registered as a vendor.
- Q-V-SEL-0-LTP | type | laptop |  | db, day fixed: D1
- Q-V-SEL-0-LTP | tier | premium |  | db, day fixed: D1
- Q-V-SEL-0-LTP | vendor | V-SEL-0 |  | db, day fixed: D1
- Q-V-SEL-0-LTP | quote_amount | 2113187 |  | db, day -20: D13
- Q-V-SEL-0-LTS | type | laptop |  | db, day fixed: D2
- Q-V-SEL-0-LTS | tier | standard |  | db, day fixed: D2
- Q-V-SEL-0-LTS | vendor | V-SEL-0 |  | db, day fixed: D2
- Q-V-SEL-0-LTS | quote_amount | 1154392 |  | db, day -20: D14
- Q-V-SEL-0-LTB | type | laptop |  | db, day fixed: D10
- Q-V-SEL-0-LTB | tier | basic |  | db, day fixed: D10
- Q-V-SEL-0-LTB | vendor | V-SEL-0 |  | db, day fixed: D10
- Q-V-SEL-0-LTB | quote_amount | 534454 |  | db, day -9: D15
- Q-V-SEL-1-LTS | type | laptop |  | db, day fixed: D3
- Q-V-SEL-1-LTS | tier | standard |  | db, day fixed: D3
- Q-V-SEL-1-LTS | vendor | V-SEL-1 |  | db, day fixed: D3
- Q-V-SEL-1-LTS | quote_amount | 1452400 |  | db, day -20: D16
- Q-V-SEL-2-LTP | type | laptop |  | db, day fixed: D5
- Q-V-SEL-2-LTP | tier | premium |  | db, day fixed: D5
- Q-V-SEL-2-LTP | vendor | V-SEL-2 |  | db, day fixed: D5
- Q-V-SEL-2-LTP | quote_amount | 1908409 |  | db, day 8: D17
- Q-V-SEL-2-LTS | type | laptop |  | db, day fixed: D4
- Q-V-SEL-2-LTS | tier | standard |  | db, day fixed: D4
- Q-V-SEL-2-LTS | vendor | V-SEL-2 |  | db, day fixed: D4
- Q-V-SEL-2-LTS | quote_amount | 1259460 |  | db, day -20: D18
- Q-V-SEL-2-LTB | type | laptop |  | db, day fixed: D12
- Q-V-SEL-2-LTB | tier | basic |  | db, day fixed: D12
- Q-V-SEL-2-LTB | vendor | V-SEL-2 |  | db, day fixed: D12
- Q-V-SEL-2-LTB | quote_amount | 489150 |  | db, day -20: D19
- Q-V-SEL-3-LTP | type | laptop |  | db, day fixed: D7
- Q-V-SEL-3-LTP | tier | premium |  | db, day fixed: D7
- Q-V-SEL-3-LTP | vendor | V-SEL-3 |  | db, day fixed: D7
- Q-V-SEL-3-LTP | quote_amount | 2367972 |  | db, day -20: D20
- Q-V-SEL-3-LTS | type | laptop |  | db, day fixed: D6
- Q-V-SEL-3-LTS | tier | standard |  | db, day fixed: D6
- Q-V-SEL-3-LTS | vendor | V-SEL-3 |  | db, day fixed: D6
- Q-V-SEL-3-LTS | quote_amount | 1379255 |  | db, day 2: D21
- Q-V-SEL-3-LTB | type | laptop |  | db, day fixed: D8
- Q-V-SEL-3-LTB | tier | basic |  | db, day fixed: D8
- Q-V-SEL-3-LTB | vendor | V-SEL-3 |  | db, day fixed: D8
- Q-V-SEL-3-LTB | quote_amount | 772879 |  | db, day -6: D22
- V-SEL-0 | vendor_lead_time | 9 |  | db, day -17: D23
- V-SEL-0 | vendor_registration | true |  | db, day -20: D27
- V-SEL-1 | vendor_lead_time | 12 |  | db, day -4: D24
- V-SEL-1 | vendor_registration | true |  | db, day -20: D28
- V-SEL-2 | vendor_lead_time | 8 |  | db, day -20: D25
- V-SEL-2 | vendor_registration | true |  | db, day -20: D29
- V-SEL-2 | delay_notice | delayed by 2 days until day 13 | in effect on day 10 | history, day 8: H2409
- V-SEL-2 | excluded_from_comparisons | excluded until day 21 | in effect on day 10 | history, day 8: H2410
- V-SEL-3 | vendor_lead_time | 9 |  | db, day 7: D26
- V-SEL-3 | vendor_registration | false |  | db, day -20: D30
missing: Support Section in TYO — employee/department information not found in my area's records
---
The lead_time_limit rule states: personal equipment orders use only suppliers with lead time ≤7 days; department orders use only suppliers with lead time ≤10 days. The rule does not list specific departments — it simply says "department orders." It is part of the SEL area's rules. The rule does not mention TYO or any other region, so I cannot confirm whether it applies to TYO suppliers or TYO departments from my own records.
- lead_time_limit | rule text | Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less. |  | rule, day fixed: lead_time_limit
- lead_time_limit | applies to departments | The rule distinguishes between 'personal equipment orders' and 'department orders' but does not list specific departments by name. |  | rule, day fixed: lead_time_limit
- lead_time_limit | TYO region applicability | The rule is in the SEL area's rules and does not mention TYO or any other region. It does not specify whether it applies across regions. |  | rule, day fixed: lead_time_limit
- lead_time_limit | SEL region applicability | The rule is part of the SEL area's rules, so it governs orders placed in the SEL region. |  | rule, day fixed: lead_time_limit
missing: Whether the lead_time_limit rule applies to all departments or just some — the rule text only says 'department orders' without listing specific departments; no catalog entries define which departments are covered.; Whether the rule applies to TYO suppliers when ordering for a TYO department — the rule is in the SEL area's rules and does not mention TYO; I have no records about TYO region rules or how they interact with SEL rules.
```

## CASE 59: deepseek-v4-flash · direct · s12 · W-00072 · class D · day 8 · template budget
### Task as given to the requester
How much budget can Support Section actually spend right now, after all deductions?
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
{"available": 2126694, "n_deducted": 4}
### Counterfactual answers (generator)
{"stale": {"available": 1795878, "n_deducted": 4}, "partial": {"available": 2280623, "n_deducted": 3}, "neardup": {"available": 2034787, "n_deducted": 3}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/Support Section/budget_schedule** (group FIN-TYO, class D, local=False)
- DB `FIN-TYO/line/Support Section/remaining` v2 (recorded day -5, registered day -3): 4108776
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01033 [decision-critical] (operational/pending_intent, day 2, by fin-tyo.a2; DB shows n/a): Support Section capex 153,929 KRW earmarked for meeting room replacement until day 9 (no voucher yet).
- RECORD FR-01057 [decision-critical] (operational/pending_intent, day 3, by fin-tyo.a1; DB shows n/a): Support Section capex 562,797 KRW earmarked for training equipment until day 12 (no voucher yet).
- RECORD FR-01297 [decision-critical] (operational/pending_intent, day 7, by fin-tyo.a1; DB shows n/a): Support Section capex 593,344 KRW earmarked for meeting room replacement until day 12 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00004/status` v2 (recorded day -7, registered day -4): {"status": "settled", "amount": 552559, "expected_settle": -7}
- DB `FIN-TYO/commit/CMT-00057/status` v2 (recorded day 7, registered day 8): {"status": "settled", "amount": 547336, "expected_settle": 7}
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Support Section AND status IN ['reviewing', 'pending'] → ["earmark:FR-01033", "earmark:FR-01057", "earmark:FR-01297", "CMT-00054"]
### Model answer and official verdict
answer: {"available": 2843420, "n_deducted": 2}
official exact match: 0 (0/2 slots)
### MATCHER CHECK FR-01033 (need FIN-TYO/Support Section/budget_schedule): matcher says **missing**
record text: Support Section capex 153,929 KRW earmarked for meeting room replacement until day 9 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
Support Section's capex balance is 4,108,776 KRW. Deductions: one pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) and one active earmark for meeting room replacement (593,344 KRW until day 12). Available budget = 4,108,776 - 672,012 - 593,344 = 2,843,420 KRW.
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation (database registered day -20) | 3777960 |  | db, day -20: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D3
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D3
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D3
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D3
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D3
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | pending provisional approvals total (only CMT-00054 is pending, deducted until day before settle day 9) | 672012 | deducted | rule, day fixed: rule pending_deduction
- Support Section | active earmarks total (meeting room replacement deducted through day 12) | 593344 | deducted | rule, day fixed: rule pending_deduction
- Support Section | available budget (line balance 4,108,776 - pending prov. approval 672,012 - earmark 593,344) | 2843420 |  | rule, day fixed: rule pending_deduction
missing: Support Section - quarterly spending control: no record found in my area's records
---
Support Section has a remaining capex balance of 4,108,776 KRW with one pending provisional approval (CMT-00054, 672,012 KRW, expected settle day 9) which is deducted today (day 8, the day before settlement). Available budget = 4,108,776 − 672,012 = 3,436,764 KRW. No quarterly spending control, executing office arrangement, holds, reservations, or exceptions are recorded in my area's records.
- Support Section | remaining capex balance | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation | 3777960 |  | db, day -20: D2
- Support Section | pending provisional approval (CMT-00054) | 672012 | pending | db, day unknown: D3
- Support Section | expected settlement day of CMT-00054 | 9 |  | db, day unknown: D3
- Support Section | available budget (line balance minus pending deductions per Art. 4.2) | 3436764 |  | db, day -3: D1, D3, rule: pending_deduction
- Support Section | quarterly spending control | No record found |  | db, day unknown: D4
- Support Section | executing office arrangement (another region executes budget) | No record found |  | db, day unknown: D4
- Support Section | budget reset days | day 16, day 46, day 76 |  | rule, day fixed: rule: reset_calendar
- approval_tiers | team_lead approval required up to | 1000000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | division_head approval required up to | 2500000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | cfo approval required above | 2500000 |  | rule, day fixed: rule: approval_tiers
missing: Holds affecting Support Section — no such records exist in my area's database or catalog; Reservations affecting Support Section — no such records exist in my area's database or catalog; Exclusions affecting Support Section — no such records exist in my area's database or catalog; Exceptions affecting Support Section — no such records exist in my area's database or catalog; Earmarks for Support Section — no such records exist in my area's database or catalog
---
The earmark for Support Section meeting room replacement of 593,344 KRW until day 12 was recorded on day 7 from a task I received. It has no voucher yet. Per the pending_deduction rule, an earmark is deducted through its end day (day 12), and since it was recorded while processing work (not an informal suggestion), it counts as a confirmed deduction. There is no database record type for earmarks — they are kept in my area's history records only.
- Support Section | earmark - meeting room replacement until day 12 | 593344 KRW | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | earmark source | Task: Earmark Support Section budget (meeting room replacement) |  | history, day 7: H480
- Support Section | earmark recorded on | day 7 |  | history, day 7: H480
- Support Section | earmark voucher status | no voucher yet |  | history, day 7: H481
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D2
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D2
missing: earmark - no database record type exists for earmarks; they exist only in my area's history records; confirmed deduction status - the earmark is a recorded instruction (not an informal remark), so it counts as a deduction under pending_deduction rule
---
Support Section has one pending provisional approval: CMT-00054 for 672,012 KRW with expected settlement on day 9. The other three approvals (CMT-00004, CMT-00049, CMT-00057) are settled or cancelled.
- Support Section | department_provisional_approvals - all records | CMT-00004 (settled, 552559, expected settle -7), CMT-00049 (cancelled, 537362, expected settle 1), CMT-00054 (pending, 672012, expected settle 9), CMT-00057 (settled, 547336, expected settle 7) |  | db, day unknown: D1
- CMT-00054 | status | pending | pending | db, day 3: D2
- CMT-00054 | amount | 672012 |  | db, day 3: D2
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D2
- CMT-00054 | registered day | 3 |  | db, day 3: D2
---
CMT-00054 (672,012 KRW, pending, expected settle day 9) is deducted from the budget today (day 8) because per rule pending_deduction, an item is deducted until the day before its expected settlement day. Since day 8 is before day 9, it is still deducted today. On day 9 (the settlement day), it would no longer be deducted.
- CMT-00054 | status | pending | pending | db, day 3: D1
- CMT-00054 | amount | 672012 |  | db, day 3: D1
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D1
- CMT-00054 | registered day | 3 |  | db, day 3: D1
- CMT-00054 | deducted from budget today (day 8)? | yes |  | rule, day fixed: rule: pending_deduction
- rule: pending_deduction | deduction rule for provisional approvals | An item is deducted only until the day before its expected settlement day (not on the settlement day itself) |  | rule, day fixed: rule: pending_deduction
---
Yes, the pending_deduction rule applies to earmarks. The meeting room replacement earmark of 593,344 KRW (valid until day 12) is deducted from the available budget today (day 8), because an earmark is deducted through its end day and today is within the validity period. Additionally, the pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) is also deducted since today (day 8) is before its settlement day.
- pending_deduction | rule text | Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An earmark is deducted through its end day. |  | rule, day fixed: rule pending_deduction
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12) | history, day 7: H481
- Periods | rule text | anything recorded as lasting 'until day N' is still in effect on day N |  | unknown, day unknown: rule Periods
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- Support Section | available budget (line balance 4,108,776 - earmark 593,344 - pending provisional approval 672,012) | 2843420 |  | rule, day fixed: rule pending_deduction
```
### MATCHER CHECK FR-01057 (need FIN-TYO/Support Section/budget_schedule): matcher says **missing**
record text: Support Section capex 562,797 KRW earmarked for training equipment until day 12 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
Support Section's capex balance is 4,108,776 KRW. Deductions: one pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) and one active earmark for meeting room replacement (593,344 KRW until day 12). Available budget = 4,108,776 - 672,012 - 593,344 = 2,843,420 KRW.
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation (database registered day -20) | 3777960 |  | db, day -20: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D3
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D3
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D3
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D3
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D3
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | pending provisional approvals total (only CMT-00054 is pending, deducted until day before settle day 9) | 672012 | deducted | rule, day fixed: rule pending_deduction
- Support Section | active earmarks total (meeting room replacement deducted through day 12) | 593344 | deducted | rule, day fixed: rule pending_deduction
- Support Section | available budget (line balance 4,108,776 - pending prov. approval 672,012 - earmark 593,344) | 2843420 |  | rule, day fixed: rule pending_deduction
missing: Support Section - quarterly spending control: no record found in my area's records
---
Support Section has a remaining capex balance of 4,108,776 KRW with one pending provisional approval (CMT-00054, 672,012 KRW, expected settle day 9) which is deducted today (day 8, the day before settlement). Available budget = 4,108,776 − 672,012 = 3,436,764 KRW. No quarterly spending control, executing office arrangement, holds, reservations, or exceptions are recorded in my area's records.
- Support Section | remaining capex balance | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation | 3777960 |  | db, day -20: D2
- Support Section | pending provisional approval (CMT-00054) | 672012 | pending | db, day unknown: D3
- Support Section | expected settlement day of CMT-00054 | 9 |  | db, day unknown: D3
- Support Section | available budget (line balance minus pending deductions per Art. 4.2) | 3436764 |  | db, day -3: D1, D3, rule: pending_deduction
- Support Section | quarterly spending control | No record found |  | db, day unknown: D4
- Support Section | executing office arrangement (another region executes budget) | No record found |  | db, day unknown: D4
- Support Section | budget reset days | day 16, day 46, day 76 |  | rule, day fixed: rule: reset_calendar
- approval_tiers | team_lead approval required up to | 1000000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | division_head approval required up to | 2500000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | cfo approval required above | 2500000 |  | rule, day fixed: rule: approval_tiers
missing: Holds affecting Support Section — no such records exist in my area's database or catalog; Reservations affecting Support Section — no such records exist in my area's database or catalog; Exclusions affecting Support Section — no such records exist in my area's database or catalog; Exceptions affecting Support Section — no such records exist in my area's database or catalog; Earmarks for Support Section — no such records exist in my area's database or catalog
---
The earmark for Support Section meeting room replacement of 593,344 KRW until day 12 was recorded on day 7 from a task I received. It has no voucher yet. Per the pending_deduction rule, an earmark is deducted through its end day (day 12), and since it was recorded while processing work (not an informal suggestion), it counts as a confirmed deduction. There is no database record type for earmarks — they are kept in my area's history records only.
- Support Section | earmark - meeting room replacement until day 12 | 593344 KRW | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | earmark source | Task: Earmark Support Section budget (meeting room replacement) |  | history, day 7: H480
- Support Section | earmark recorded on | day 7 |  | history, day 7: H480
- Support Section | earmark voucher status | no voucher yet |  | history, day 7: H481
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D2
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D2
missing: earmark - no database record type exists for earmarks; they exist only in my area's history records; confirmed deduction status - the earmark is a recorded instruction (not an informal remark), so it counts as a deduction under pending_deduction rule
---
Support Section has one pending provisional approval: CMT-00054 for 672,012 KRW with expected settlement on day 9. The other three approvals (CMT-00004, CMT-00049, CMT-00057) are settled or cancelled.
- Support Section | department_provisional_approvals - all records | CMT-00004 (settled, 552559, expected settle -7), CMT-00049 (cancelled, 537362, expected settle 1), CMT-00054 (pending, 672012, expected settle 9), CMT-00057 (settled, 547336, expected settle 7) |  | db, day unknown: D1
- CMT-00054 | status | pending | pending | db, day 3: D2
- CMT-00054 | amount | 672012 |  | db, day 3: D2
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D2
- CMT-00054 | registered day | 3 |  | db, day 3: D2
---
CMT-00054 (672,012 KRW, pending, expected settle day 9) is deducted from the budget today (day 8) because per rule pending_deduction, an item is deducted until the day before its expected settlement day. Since day 8 is before day 9, it is still deducted today. On day 9 (the settlement day), it would no longer be deducted.
- CMT-00054 | status | pending | pending | db, day 3: D1
- CMT-00054 | amount | 672012 |  | db, day 3: D1
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D1
- CMT-00054 | registered day | 3 |  | db, day 3: D1
- CMT-00054 | deducted from budget today (day 8)? | yes |  | rule, day fixed: rule: pending_deduction
- rule: pending_deduction | deduction rule for provisional approvals | An item is deducted only until the day before its expected settlement day (not on the settlement day itself) |  | rule, day fixed: rule: pending_deduction
---
Yes, the pending_deduction rule applies to earmarks. The meeting room replacement earmark of 593,344 KRW (valid until day 12) is deducted from the available budget today (day 8), because an earmark is deducted through its end day and today is within the validity period. Additionally, the pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) is also deducted since today (day 8) is before its settlement day.
- pending_deduction | rule text | Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An earmark is deducted through its end day. |  | rule, day fixed: rule pending_deduction
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12) | history, day 7: H481
- Periods | rule text | anything recorded as lasting 'until day N' is still in effect on day N |  | unknown, day unknown: rule Periods
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- Support Section | available budget (line balance 4,108,776 - earmark 593,344 - pending provisional approval 672,012) | 2843420 |  | rule, day fixed: rule pending_deduction
```
### MATCHER CHECK FR-01297 (need FIN-TYO/Support Section/budget_schedule): matcher says **delivered**
record text: Support Section capex 593,344 KRW earmarked for meeting room replacement until day 12 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
Support Section's capex balance is 4,108,776 KRW. Deductions: one pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) and one active earmark for meeting room replacement (593,344 KRW until day 12). Available budget = 4,108,776 - 672,012 - 593,344 = 2,843,420 KRW.
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation (database registered day -20) | 3777960 |  | db, day -20: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D3
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D3
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D3
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D3
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D3
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | pending provisional approvals total (only CMT-00054 is pending, deducted until day before settle day 9) | 672012 | deducted | rule, day fixed: rule pending_deduction
- Support Section | active earmarks total (meeting room replacement deducted through day 12) | 593344 | deducted | rule, day fixed: rule pending_deduction
- Support Section | available budget (line balance 4,108,776 - pending prov. approval 672,012 - earmark 593,344) | 2843420 |  | rule, day fixed: rule pending_deduction
missing: Support Section - quarterly spending control: no record found in my area's records
---
Support Section has a remaining capex balance of 4,108,776 KRW with one pending provisional approval (CMT-00054, 672,012 KRW, expected settle day 9) which is deducted today (day 8, the day before settlement). Available budget = 4,108,776 − 672,012 = 3,436,764 KRW. No quarterly spending control, executing office arrangement, holds, reservations, or exceptions are recorded in my area's records.
- Support Section | remaining capex balance | 4108776 |  | db, day -3: D1
- Support Section | quarterly base allocation | 3777960 |  | db, day -20: D2
- Support Section | pending provisional approval (CMT-00054) | 672012 | pending | db, day unknown: D3
- Support Section | expected settlement day of CMT-00054 | 9 |  | db, day unknown: D3
- Support Section | available budget (line balance minus pending deductions per Art. 4.2) | 3436764 |  | db, day -3: D1, D3, rule: pending_deduction
- Support Section | quarterly spending control | No record found |  | db, day unknown: D4
- Support Section | executing office arrangement (another region executes budget) | No record found |  | db, day unknown: D4
- Support Section | budget reset days | day 16, day 46, day 76 |  | rule, day fixed: rule: reset_calendar
- approval_tiers | team_lead approval required up to | 1000000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | division_head approval required up to | 2500000 |  | rule, day fixed: rule: approval_tiers
- approval_tiers | cfo approval required above | 2500000 |  | rule, day fixed: rule: approval_tiers
missing: Holds affecting Support Section — no such records exist in my area's database or catalog; Reservations affecting Support Section — no such records exist in my area's database or catalog; Exclusions affecting Support Section — no such records exist in my area's database or catalog; Exceptions affecting Support Section — no such records exist in my area's database or catalog; Earmarks for Support Section — no such records exist in my area's database or catalog
---
The earmark for Support Section meeting room replacement of 593,344 KRW until day 12 was recorded on day 7 from a task I received. It has no voucher yet. Per the pending_deduction rule, an earmark is deducted through its end day (day 12), and since it was recorded while processing work (not an informal suggestion), it counts as a confirmed deduction. There is no database record type for earmarks — they are kept in my area's history records only.
- Support Section | earmark - meeting room replacement until day 12 | 593344 KRW | active (in effect through day 12 per Periods rule) | history, day 7: H481
- Support Section | earmark source | Task: Earmark Support Section budget (meeting room replacement) |  | history, day 7: H480
- Support Section | earmark recorded on | day 7 |  | history, day 7: H480
- Support Section | earmark voucher status | no voucher yet |  | history, day 7: H481
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- CMT-00057 | provisional approval amount | 547336 | settled | db, day 8: D2
- CMT-00049 | provisional approval amount | 537362 | cancelled | db, day 5: D2
- CMT-00004 | provisional approval amount | 552559 | settled | db, day -4: D2
missing: earmark - no database record type exists for earmarks; they exist only in my area's history records; confirmed deduction status - the earmark is a recorded instruction (not an informal remark), so it counts as a deduction under pending_deduction rule
---
Support Section has one pending provisional approval: CMT-00054 for 672,012 KRW with expected settlement on day 9. The other three approvals (CMT-00004, CMT-00049, CMT-00057) are settled or cancelled.
- Support Section | department_provisional_approvals - all records | CMT-00004 (settled, 552559, expected settle -7), CMT-00049 (cancelled, 537362, expected settle 1), CMT-00054 (pending, 672012, expected settle 9), CMT-00057 (settled, 547336, expected settle 7) |  | db, day unknown: D1
- CMT-00054 | status | pending | pending | db, day 3: D2
- CMT-00054 | amount | 672012 |  | db, day 3: D2
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D2
- CMT-00054 | registered day | 3 |  | db, day 3: D2
---
CMT-00054 (672,012 KRW, pending, expected settle day 9) is deducted from the budget today (day 8) because per rule pending_deduction, an item is deducted until the day before its expected settlement day. Since day 8 is before day 9, it is still deducted today. On day 9 (the settlement day), it would no longer be deducted.
- CMT-00054 | status | pending | pending | db, day 3: D1
- CMT-00054 | amount | 672012 |  | db, day 3: D1
- CMT-00054 | expected settlement day | 9 |  | db, day 3: D1
- CMT-00054 | registered day | 3 |  | db, day 3: D1
- CMT-00054 | deducted from budget today (day 8)? | yes |  | rule, day fixed: rule: pending_deduction
- rule: pending_deduction | deduction rule for provisional approvals | An item is deducted only until the day before its expected settlement day (not on the settlement day itself) |  | rule, day fixed: rule: pending_deduction
---
Yes, the pending_deduction rule applies to earmarks. The meeting room replacement earmark of 593,344 KRW (valid until day 12) is deducted from the available budget today (day 8), because an earmark is deducted through its end day and today is within the validity period. Additionally, the pending provisional approval CMT-00054 (672,012 KRW, expected settle day 9) is also deducted since today (day 8) is before its settlement day.
- pending_deduction | rule text | Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An earmark is deducted through its end day. |  | rule, day fixed: rule pending_deduction
- Support Section | earmark - meeting room replacement until day 12 | 593344 | active (in effect through day 12) | history, day 7: H481
- Periods | rule text | anything recorded as lasting 'until day N' is still in effect on day N |  | unknown, day unknown: rule Periods
- Support Section | capex balance (database registered day -3) | 4108776 |  | db, day -3: D1
- CMT-00054 | provisional approval amount | 672012 | pending | db, day 3: D2
- CMT-00054 | expected settlement day | 9 | pending | db, day 3: D2
- Support Section | available budget (line balance 4,108,776 - earmark 593,344 - pending provisional approval 672,012) | 2843420 |  | rule, day fixed: rule pending_deduction
```

## CASE 60: deepseek-v4-flash · direct · s12 · W-00070 · class D · day 7 · template contract_gate
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
answer: {"contract_tier": "standard", "expiry": 12, "it_tier": "basic", "nda_step": false}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-00884 (need IT-SEL/eligibility/E-SEL-1006): matcher says **missing**
record text: Equipment tier of Oh Minjae up to standard allowed until day 15 for work reasons (IT exception approved).
What the requester received from IT-SEL during this task:
```
For employee E-SEL-1006 (Minjae, grade 2), the default equipment tier by grade is basic. No IT exception was found in my area's records, so the highest tier IT allows right now is basic.
- E-SEL-1006 | grade | 2 |  | unknown, day unknown: question
- E-SEL-1006 | default tier by grade | basic |  | rule, day fixed: rule: eligibility
- E-SEL-1006 | highest allowed tier (no exceptions found) | basic |  | rule, day fixed: rule: eligibility
- E-SEL-1006 | IT exception | none found in records |  | db, day unknown: D1, D2
missing: catalog entry for E-SEL-1006 (grade, department, name) - not in my area's records; any IT exception records for E-SEL-1006 - not found in my area's database
---
In my area's records and database, I found no catalog entry for E-SEL-1006, no assigned assets, and no IT exception records. The default tier for grade 2 is basic per the eligibility rule. Any exception allowing a higher tier would need to be recorded elsewhere.
- E-SEL-1006 | grade | 2 |  | unknown, day unknown: question
- E-SEL-1006 | default tier by grade | basic |  | rule, day fixed: rule: eligibility
- E-SEL-1006 | catalog entry in SEL area | not found |  | db, day unknown: D1
- E-SEL-1006 | assigned assets | none registered |  | db, day unknown: D2
- E-SEL-1006 | IT exception records | none found |  | db, day unknown: D1, D2
missing: Any tier exceptions, special approvals, or department-specific rules for E-SEL-1006 that may be held outside the SEL area's records
```
### MATCHER CHECK FR-00547 (need LEGAL-SEL/E-SEL-1006/contract): matcher says **missing**
record text: Equipment exception of Oh Minjae higher tiers including premium allowed until day 19 for a project, legal check done.
What the requester received from LEGAL-SEL during this task:
```
Employee E-SEL-1006 (Minjae (Lead), Oh Minjae) has contract terms registered as of day 5: allowed tier 'standard', expiry day 12, and NDA not required (nda: false). No catalog_entry is registered for this employee.
- E-SEL-1006 | allowed_tier | standard |  | db, day 5: D1
- E-SEL-1006 | expiry | 12 |  | db, day 5: D1
- E-SEL-1006 | nda | false |  | db, day 5: D1
- Minjae (Lead) | contract_terms (via E-SEL-1006) | allowed_tier: standard, expiry: 12, nda: false |  | db, day 5: D3
- Oh Minjae | contract_terms (via E-SEL-1006) | allowed_tier: standard, expiry: 12, nda: false |  | db, day 5: D4
---
My area's records show E-SEL-1006's contract allows standard tier (nda=false). The requested standard tier matches the contract's allowed tier and is not premium equipment, so per contractor_policy no legal exception is needed. The 'IT only allows basic tier by grade' restriction is not covered by any of my area's four rules.
- E-SEL-1006 | contract_terms - allowed_tier | standard |  | db, day 5: D2
- E-SEL-1006 | contract_terms - expiry | 12 |  | db, day 5: D2
- E-SEL-1006 | contract_terms - nda | false |  | db, day 5: D2
- E-SEL-1006 | catalog_entry | NO_RECORD |  | db, day unknown: D1
- contractor_policy | rule text | Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified and is still valid skips the NDA check step. |  | rule, day fixed: rule: contractor_policy
- E-SEL-1006 | requested item tier vs contract allowed tier | standard (requested) equals standard (allowed) |  | db, day 5: D2
- E-SEL-1006 | legal exception needed per contractor_policy | no - equipment is not premium and not above contract's allowed tier |  | rule, day fixed: rule: contractor_policy
- E-SEL-1006 | NDA check needed per contractor_policy | no - nda is false |  | rule, day fixed: rule: contractor_policy
missing: whether 'IT only allows basic tier by grade' triggers any rule in my area — not covered by my area's rules (contractor_policy, renewal_policy, residency, sw_contractor) or database; whether a legal exception is required due to IT's grade-based tier restriction — not defined in my area's rules; what the outcome would be regarding contract_tier being standard with a legal exception — my area's rules do not address this scenario since no legal exception is triggered by my rules
---
The contract review passes. The contract is active (expiry day 12, today is day 7), has nda=false (no NDA clause, so no NDA check needed), and the allowed tier is standard. The highest tier the contract allows right now is standard.
- E-SEL-1006 | allowed_tier | standard |  | db, day 5: D1
- E-SEL-1006 | expiry | 12 |  | db, day 5: D1
- E-SEL-1006 | nda | false |  | db, day 5: D1
- E-SEL-1006 | highest tier contract allows | standard |  | db, day 5: D1
- E-SEL-1006 | contract expiry status | not expired (expiry day 12, today day 7) |  | db, day 5: D1
- E-SEL-1006 | contract review result | passes - contract is active (expiry day 12), no NDA required (nda=false), allowed tier is standard |  | db, day 5: D1
missing: Catalog entry for E-SEL-1006 (Minjae (Lead), Oh Minjae) — no record registered in area's database
```

## CASE 61: deepseek-v4-flash · routing · s13 · W-00052 · class A · day 6 · template diag
### Task as given to the requester
Invoice INV-76821 (884,389 KRW, beneficiary Takahashi-san, asset A-TYO-4079, provisional approval CMT-00014) does not match. Find the cause.
[Request scope] target supplier=V-TYO-1; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"cause": "EMP_EXITED"}
### Counterfactual answers (generator)
{"stale": {"cause": "ASSET_NOT_REGISTERED"}, "partial": null, "neardup": {"cause": "ASSET_NOT_REGISTERED"}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00014/status** (group FIN-TYO, class A, local=False)
- CATALOG: {"group": "FIN-TYO", "key": "commits/CMT-00014"}
- DB `FIN-TYO/commit/CMT-00014/status` v2 (recorded day -4, registered day -3): {"status": "settled", "amount": 884389, "expected_settle": -4}
**need HR-TYO/E-TYO-1003/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1003"}
- DB `HR-TYO/emp/E-TYO-1003/profile` v2 (recorded day -15, registered day -14): {"dept": "Dev Section 1", "grade": 5, "contract": "regular", "hire_day": -608, "status": "exited"}
**need IT-TYO/E-TYO-1003/assets** (group IT-TYO, class None, local=True)
- DB `IT-TYO/asset/A-TYO-4079/holder` v2 (recorded day -14, registered day -13): {"emp": null}
- QUERY SELECT asset WHERE holder=E-TYO-1003 → []
**need PROC-TYO/receipt/CMT-00014** (group PROC-TYO, class A, local=False)
- DB `PROC-TYO/receipt/CMT-00014/received` v1 (recorded day -5, registered day -4): true
**need PROC-TYO/vendor/V-TYO-1/status** (group PROC-TYO, class A, local=False)
- NEGATIVE: {"query": "PROC-TYO exclusion order for supplier V-TYO-1", "result": []}
**need FIN-TYO/rule/invoice_match_precedence** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.invoice_match_precedence: {"id": "FIN-TYO.invoice_match_precedence", "group": "FIN-TYO", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "EMP_EXITED"}
official exact match: 1 (1/1 slots)

## CASE 62: deepseek-v4-flash · routing · s14 · W-00024 · class A · day 3 · template lookup
### Task as given to the requester
Check Ono-san's current department, grade and assets held.
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
{"dept": "Support Section", "grade": 3, "assets": ["A-TYO-5708"]}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"dept": "Dev Section 1", "grade": 1, "assets": ["A-TYO-5708"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1001/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1001"}
- DB `HR-TYO/emp/E-TYO-1001/profile` v1 (recorded day -20, registered day -20): {"dept": "Support Section", "grade": 3, "contract": "regular", "hire_day": -715, "status": "active"}
**need IT-TYO/E-TYO-1001/assets** (group IT-TYO, class None, local=True)
- DB `IT-TYO/asset/A-TYO-5708/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1001"}
- QUERY SELECT asset WHERE holder=E-TYO-1001 → ["A-TYO-5708"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-5708"], "dept": "Support Section", "grade": 3}
official exact match: 1 (3/3 slots)

## CASE 63: deepseek-v4-flash · routing · s14 · W-00013 · class A · day 2 · template temporal
### Task as given to the requester
Equipment for Hajun (Lead) at 1,767,668 KRW: taking personnel changes into account, which department's budget can pay for it and from which day?
[Request scope] item=workstation; search window=today through 20 days later (inclusive); procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"budget_dept": "Sales Team 2", "earliest_day": 2}
### Counterfactual answers (generator)
{"stale": {"budget_dept": "Sales Team 1", "earliest_day": 6}, "partial": null, "neardup": {"budget_dept": "Dev Team 1", "earliest_day": 13}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1010/assignment_timeline** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1010"}
- DB `HR-SEL/emp/E-SEL-1010/profile` v3 (recorded day 0, registered day 2): {"dept": "Sales Team 2", "grade": 5, "contract": "contractor", "hire_day": -385, "status": "active"}
- RULE HR-SEL.transfer_effective_day: {"id": "HR-SEL.transfer_effective_day", "group": "HR-SEL", "title": "Transfer effective day", "params": {"inclusive": true}, "text": "An employee belongs to the new department from the transfer's effective day itself."}
- RECORD FR-00971 (operational/pending_intent, day 0, by hr-sel.a3; DB shows n/a): Transfer of Lim Hajun approved from Sales Team 2 to Customer Support Team, effective day 9 (stays in Sales Team 2 until then).
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-00841 (operational/exception, day -3, by fin-sel.n0004; DB shows n/a): Sales Team 2 capex executing office agreed that TYO finance executes it until day 20.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Sales Team 2/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Sales Team 2/remaining` v1 (recorded day -3, registered day -2): 2638932
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01003 (operational/pending_intent, day 1, by fin-tyo.a3; DB shows n/a): CMT-00078 Sales Team 2 meeting room equipment provisional approval 474,266 KRW under review, settlement expected day 9.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00078"]
**need FIN-TYO/Sales Team 2/next_reset** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.reset_calendar: {"id": "FIN-TYO.reset_calendar", "group": "FIN-TYO", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-TYO/line/Sales Team 2/base` v1 (recorded day -3, registered day -1): 3915076
**need FIN-SEL/Customer Support Team/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Customer Support Team/remaining` v3 (recorded day -14, registered day -12): 2983974
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00605 (operational/pending_intent, day -9, by fin-sel.a1; DB shows n/a): Customer Support Team capex 185,434 KRW earmarked for training equipment until day 6 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00012/status` v2 (recorded day -5, registered day -2): {"status": "settled", "amount": 783494, "expected_settle": -5}
- DB `FIN-SEL/commit/CMT-00042/status` v2 (recorded day -2, registered day 1): {"status": "settled", "amount": 896464, "expected_settle": -2}
- RECORD FR-00909 (operational/pending_intent, day -2, by fin-sel.a1; DB shows n/a): CMT-00069 Customer Support Team monitor provisional approval 410,966 KRW under review, settlement expected day 11.
- RECORD FR-01023 (db_pending/observation, day 1, by fin-sel.a2; DB shows ABSENT): CMT-00072 Customer Support Team provisional approval 752,098 KRW confirmed, settlement expected day 11. Stored value: {"amount":752098,"expected_settle":11,"status":"pending"}
- RECORD FR-01005 (operational/pending_intent, day 1, by fin-sel.a3; DB shows n/a): CMT-00080 Customer Support Team monitor provisional approval 794,140 KRW under review, settlement expected day 9.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Customer Support Team AND status IN ['reviewing', 'pending'] → ["earmark:FR-00605", "CMT-00044", "CMT-00069", "CMT-00072", "CMT-00080"]
**need FIN-SEL/Customer Support Team/next_reset** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.reset_calendar: {"id": "FIN-SEL.reset_calendar", "group": "FIN-SEL", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-SEL/line/Customer Support Team/base` v1 (recorded day -20, registered day -20): 2606663
**need PROC-SEL/quotes/workstation** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00570 (operational/handover, day -10, by proc-sel.w00065; DB shows n/a): Supplier V-SEL-3 exclude from comparisons until day 4 due to a quality issue.
- RECORD FR-00713 (operational/handover, day -6, by proc-sel.w00088; DB shows n/a): Supplier V-SEL-2 exclude from comparisons until day 6 due to a quality issue.
- RECORD FR-00983 (operational/handover, day 0, by proc-sel.w00136; DB shows n/a): Supplier V-SEL-1 exclude from comparisons until day 10 due to a quality issue.
- RECORD FR-00789 (operational/observation, day -5, by proc-sel.w00100; DB shows n/a): Supplier V-SEL-1 delivery notified: deliveries delayed by 5 days until day 3.
- RULE PROC-SEL.delay_notice: {"id": "PROC-SEL.delay_notice", "group": "PROC-SEL", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-00862 (operational/observation, day -3, by proc-sel.w00114; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 4 days until day 2.
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
- RECORD FR-01036 (db_pending/rationale, day 1, by proc-sel.w00148; DB shows 1): V-SEL-1 workstation (standard) quote Q-V-SEL-1-WSS changed to 1,360,147 KRW (raw material prices). Stored value: 1360147
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
### Model answer and official verdict
answer: {"budget_dept": null, "earliest_day": null}
official exact match: 0 (0/2 slots)

## CASE 64: deepseek-v4-flash · routing · s12 · W-00068 · class B · day 7 · template purchase
### Task as given to the requester
For Minjae (Lead)'s monitor request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
[Request scope] item=monitor; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"decision": "assign", "option": "INV-SEL-MNB", "approver": "team_lead", "nda": false, "budget_after": 865649, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"decision": "assign", "option": "INV-SEL-MNB", "approver": "team_lead", "nda": false, "budget_after": 2103772, "blocked_by": null}, "partial": {"decision": "assign", "option": "INV-SEL-MNB", "approver": "team_lead", "nda": false, "budget_after": 2103772, "blocked_by": null}, "neardup": {"decision": "assign", "option": "INV-SEL-MNB", "approver": "team_lead", "nda": false, "budget_after": 3189779, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1006/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1006"}
- DB `HR-SEL/emp/E-SEL-1006/profile` v2 (recorded day -10, registered day -7): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -531, "status": "active"}
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class B, local=False)
- RECORD FR-01235 [decision-critical] (db_pending/rationale, day 6, by fin-sel.a3; DB shows 7): Sales Team 2 capex balance adjusted to 2,322,305 KRW (refund applied). Stored value: 2322305
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-SEL/commit/CMT-00014/status` v2 (recorded day -2, registered day 0): {"status": "settled", "amount": 556792, "expected_settle": -2}
- DB `FIN-SEL/commit/CMT-00016/status` v2 (recorded day -11, registered day -10): {"status": "settled", "amount": 444248, "expected_settle": -11}
- DB `FIN-SEL/commit/CMT-00020/status` v2 (recorded day -8, registered day -7): {"status": "settled", "amount": 255551, "expected_settle": -8}
- DB `FIN-SEL/commit/CMT-00030/status` v2 (recorded day -5, registered day -2): {"status": "settled", "amount": 963340, "expected_settle": -5}
- DB `FIN-SEL/commit/CMT-00048/status` v2 (recorded day 4, registered day 5): {"status": "settled", "amount": 925976, "expected_settle": 4}
- RECORD FR-01277 (db_pending/observation, day 7, by fin-sel.a3; DB shows ABSENT): CMT-00087 Sales Team 2 provisional approval cancellation confirmed. Stored value: {"amount":896300,"expected_settle":12,"status":"cancelled"}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["CMT-00053"]
**need IT-SEL/eligibility/E-SEL-1006** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
- RECORD FR-00884 (operational/exception, day -1, by it-sel.a3; DB shows n/a): Equipment tier of Oh Minjae up to standard allowed until day 15 for work reasons (IT exception approved).
- RULE IT-SEL.tier_exception: {"id": "IT-SEL.tier_exception", "group": "IT-SEL", "title": "Equipment tier exception", "params": {"exception_raises_tier": true}, "text": "An equipment tier exception approved by IT replaces the grade-based default tier during the exception period."}
**need IT-SEL/inventory/monitor** (group IT-SEL, class A, local=False)
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-MNB"}
- RECORD FR-01281 (db_pending/observation, day 7, by it-sel.a4; DB shows 5): In-house stock monitor (basic) Receipt added. Stored value: 6
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-MNS"}
- RECORD FR-01166 (db_pending/observation, day 5, by it-sel.a5; DB shows 5): In-house stock monitor (standard) Receipt added. Stored value: 7
- RECORD FR-01128 (operational/pending_intent, day 4, by it-sel.a5; DB shows n/a): In-house stock monitor (standard) 1 unit held for an incoming Sales Team 1 hire until day 11.
**need LEGAL-SEL/E-SEL-1006/contract** (group LEGAL-SEL, class A, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1006/terms` v4 (recorded day 2, registered day 5): {"allowed_tier": "standard", "expiry": 12, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00547 (operational/exception, day -11, by legal-sel.a3; DB shows n/a): Equipment exception of Oh Minjae higher tiers including premium allowed until day 19 for a project, legal check done.
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 2103772, "decision": "assign", "nda": false, "option": "INV-SEL-MNB"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-01235 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: Sales Team 2 capex balance adjusted to 2,322,305 KRW (refund applied). Stored value: 2322305
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) As of day 7, Sales Team 2's available budget is 2,577,011 KRW. This is calculated as the line balance of 3,560,428 KRW minus the pending provisional approval CMT-00053 (983,417 KRW, expected settlement day 9). All other provisional approvals are either settled or cancelled. No earmarks were found. A cost of 473,239 KRW can be covered.
[Reply 2] (partial) The current available budget for Sales Team 2 is 2,577,011 KRW (line balance 3,560,428 KRW minus one pending provisional approval CMT-00053 of 983,417 KRW, which is deducted because today day 7 is before its expected settlement day 9). A cost of 473,239 KRW can be covered.
[Reply 3] (partial) The current available budget for Sales Team 2 as of day 7 is 1,338,888 KRW. This is calculated as the line balance of 2,322,305 KRW (per the day 6 refund adjustment, which is newer than the database version) minus the pending provisional approval CMT-00053 (983,417 KRW, expected settlement day 9, deducted until day 8). A cost of 473,239 KRW can be covered.
- Sales Team 2 | capex balance (line balance) | 3560428 |  | db, day 4: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 4826382 |  | db, day -20: Reply 1: D2
- CMT-00014 | provisional approval amount | 556792 | settled | db, day 0: Reply 1: D3
- CMT-00014 | expected settlement day | -2 |  | db, day 0: Reply 1: D3
- CMT-00016 | provisional approval amount | 444248 | settled | db, day -10: Reply 1: D3
- CMT-00016 | expected settlement day | -11 |  | db, day -10: Reply 1: D3
- CMT-00020 | provisional approval amount | 255551 | settled | db, day -7: Reply 1: D3
- CMT-00020 | expected settlement day | -8 |  | db, day -7: Reply 1: D3
- CMT-00030 | provisional approval amount | 963340 | settled | db, day -2: Reply 1: D3
- CMT-00030 | expected settlement day | -5 |  | db, day -2: Reply 1: D3
- CMT-00048 | provisional approval amount | 925976 | settled | db, day 5: Reply 1: D3
- CMT-00048 | expected settlement day | 4 |  | db, day 5: Reply 1: D3
- CMT-00053 | provisional approval amount | 983417 | pending | db, day 3: Reply 1: D3
- CMT-00053 | expected settlement day | 9 |  | db, day 3: Reply 1: D3
- CMT-00068 | provisional approval amount | 836622 | cancelled | db, day 6: Reply 1: D3
- CMT-00068 | expected settlement day | 8 |  | db, day 6: Reply 1: D3
- Sales Team 2 | pending provisional approvals to deduct (Art. 4.2) | 983417 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | earmarks in validity period | none found in records |  | unknown, day unknown: Reply 1: history
- Sales Team 2 | available budget calculation | 3560428 - 983417 - 0 = 2577011 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | available budget as of day 7 | 2577011 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- 473239 KRW cost | can be covered by available budget | yes (2577011 >= 473239) |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | budget line balance (remaining capex) | 3560428 |  | db, day 4: Reply 2: D1
- Sales Team 2 | budget line balance registered day | 4 |  | db, day 4: Reply 2: D1
- Sales Team 2 | quarterly base allocation | 4826382 |  | db, day -20: Reply 2: D2
- CMT-00053 | provisional approval status | pending | pending | db, day 3: Reply 2: D3
- CMT-00053 | provisional approval amount | 983417 | pending | db, day 3: Reply 2: D3
- CMT-00053 | expected settlement day | 9 | pending | db, day 3: Reply 2: D3
- Sales Team 2 | available budget (line balance - pending items) | 2577011 |  | unknown, day unknown: Reply 2: rule_pending_deduction
- Sales Team 2 | line balance (input for calculation) | 3560428 |  | db, day 4: Reply 2: D1
- Sales Team 2 | sum of pending/provisionally approved items deducted (CMT-00053) | 983417 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | can cover cost of 473239 KRW | yes (473239 <= 2577011) |  | unknown, day unknown: Reply 2: rule_pending_deduction
- Sales Team 2 | budget line balance (remaining capex) - adjusted day 6 (refund applied) | 2322305 |  | history, day 6: Reply 3: H708
- Sales Team 2 | budget line balance (remaining capex) - database version | 3560428 |  | db, day 4: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 4826382 |  | db, day -20: Reply 3: D2
- CMT-00053 | provisional approval amount | 983417 | pending | db, day 3: Reply 3: D3
- CMT-00053 | expected settlement day | 9 |  | db, day 3: Reply 3: D3
- CMT-00068 | provisional approval amount | 836622 | cancelled | db, day 6: Reply 3: D3
- CMT-00087 | provisional approval amount | 896300 | cancelled | history, day 7: Reply 3: H742
- Sales Team 2 | available budget as of day 7 (line balance minus pending deductions per Art. 4.2) | 1338888 |  | unknown, day unknown: Reply 3: rule:pending_deduction
- Sales Team 2 | can cost of 473239 KRW be covered | yes (1338888 >= 473239) |  | unknown, day unknown: Reply 3: rule:pending_deduction
missing: earmarks in their validity period for Sales Team 2 — no such records exist in my area's database or records; Earmarks for Sales Team 2 — my area does not hold earmark records; no record type for earmarks exists in my area's database.; Items under review for Sales Team 2 beyond registered provisional approvals — my area only holds registered provisional approvals; 'under review' items that are not yet registered as provisional approvals are not in my area's records.
---
[Reply 1] (partial) As of day 7, the correct available budget for Sales Team 2 is 2,577,011 KRW. This comes from the database line balance of 3,560,428 KRW minus the pending provisional approval CMT-00053 (983,417 KRW, expected settlement day 9, still before its settlement day so deducted per Art. 4.2). All other provisional approvals are settled or cancelled and do not reduce the available budget. No earmarks were found. The figure 1,338,888 KRW (based on a day 6 adjusted line balance of 2,322,305) is not supported by my area's records — I have no record of any adjustment to Sales Team 2's balance.
[Reply 2] (partial) The correct available budget as of day 7 is 1,338,888 KRW. The database shows a line balance of 3,560,428 KRW (registered day 4), but my day 6 processing record (H708) adjusted it to 2,322,305 KRW due to a refund. Per the rule 'Records and the database', a processing record is newer than the database version and counts. Deducting the pending CMT-00053 (983,417 KRW, expected settlement day 9, still before its deduction cutoff) gives 1,338,888 KRW.
[Reply 3] (partial) As of day 7, the correct available budget for Sales Team 2 is 2,577,011 KRW (line balance 3,560,428 minus pending CMT-00053 at 983,417). The figure 1,338,888 KRW relies on a 'day 6 adjusted line balance of 2,322,305' which does not exist in my area's records or database; my database shows only the day-4 registered balance of 3,560,428.
- Sales Team 2 | capex balance (line balance) | 3560428 |  | db, day 4: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 4826382 |  | db, day -20: Reply 1: D2
- CMT-00053 | provisional approval amount | 983417 | pending | db, day 3: Reply 1: D3
- CMT-00053 | expected settlement day | 9 |  | db, day 3: Reply 1: D3
- CMT-00053 | department | Sales Team 2 |  | db, day fixed: Reply 1: D4
- CMT-00014 | provisional approval amount | 556792 | settled | db, day 0: Reply 1: D3
- CMT-00016 | provisional approval amount | 444248 | settled | db, day -10: Reply 1: D3
- CMT-00020 | provisional approval amount | 255551 | settled | db, day -7: Reply 1: D3
- CMT-00030 | provisional approval amount | 963340 | settled | db, day -2: Reply 1: D3
- CMT-00048 | provisional approval amount | 925976 | settled | db, day 5: Reply 1: D3
- CMT-00068 | provisional approval amount | 836622 | cancelled | db, day 6: Reply 1: D3
- Sales Team 2 | pending provisional approvals to deduct (Art. 4.2) | 983417 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | earmarks in validity period | none found in records |  | unknown, day unknown: Reply 1: history
- Sales Team 2 | available budget calculation | 3560428 - 983417 = 2577011 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | correct available budget as of day 7 | 2577011 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Sales Team 2 | adjusted line balance of 2322305 on day 6 | not found in my area's records |  | unknown, day unknown: Reply 1: history
- Sales Team 2 | budget line balance (database, registered day 4) | 3560428 |  | db, day 4: Reply 2: D1
- Sales Team 2 | budget line balance (adjusted day 6, refund applied) | 2322305 |  | history, day 6: Reply 2: H708
- CMT-00053 | provisional approval amount | 983417 | pending | db, day 3: Reply 2: D3
- CMT-00053 | expected settlement day | 9 |  | db, day 3: Reply 2: D3
- Sales Team 2 | available budget as of day 7 (adjusted balance 2,322,305 minus pending CMT-00053 983,417) | 1338888 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | correct current available budget | 1338888 |  | h
[... truncated]
```

## CASE 65: deepseek-v4-flash · routing · s13 · W-00053 · class B · day 6 · template lookup
### Task as given to the requester
Check Eunho (Manager)'s current department, grade and assets held.
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
{"dept": "Customer Support Team", "grade": 5, "assets": ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Customer Support Team", "grade": 4, "assets": ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"]}, "partial": {"dept": "Customer Support Team", "grade": 4, "assets": ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"]}, "neardup": {"dept": "Sales Team 1", "grade": 3, "assets": ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1012/profile** (group HR-SEL, class B, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1012"}
- RECORD FR-01259 [decision-critical] (db_pending/rationale, day 6, by hr-sel.n0006; DB shows 3): HR record of Cho Eunho changed to grade 5 (review result), Customer Support Team. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":5,"hire_day":-64,"status":"active"}
**need IT-SEL/E-SEL-1012/assets** (group IT-SEL, class A, local=False)
- DB `IT-SEL/asset/A-SEL-5419/holder` v1 (recorded day -20, registered day -20): {"emp": "E-SEL-1012"}
- DB `IT-SEL/asset/A-SEL-5873/holder` v1 (recorded day -20, registered day -20): {"emp": "E-SEL-1012"}
- DB `IT-SEL/asset/A-SEL-67665/holder` v1 (recorded day 1, registered day 3): {"emp": "E-SEL-1012"}
- QUERY SELECT asset WHERE holder=E-SEL-1012 → ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"]
### Model answer and official verdict
answer: {"assets": ["A-SEL-5419", "A-SEL-5873", "A-SEL-67665"], "dept": "Customer Support Team", "grade": 5}
official exact match: 1 (3/3 slots)
### MATCHER CHECK FR-01259 (need HR-SEL/E-SEL-1012/profile): matcher says **delivered**
record text: HR record of Cho Eunho changed to grade 5 (review result), Customer Support Team. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":5,"hire_day":-64,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (ok) Employee E-SEL-1012 (Cho Eunho, alias Eunho (Manager)) is currently in Customer Support Team, grade 5, contractor, active.
[Reply 2] (ok) Employee E-SEL-1012 (Cho Eunho / Eunho Manager) is in Customer Support Team, grade 5, contractor, active, hired 64 days ago.
[Reply 3] (ok) Employee E-SEL-1012 (Cho Eunho / Eunho (Manager)) is currently in Customer Support Team, grade 5, contractor, active.
[Reply 4] (ok) Employee E-SEL-1012 (Cho Eunho, alias Manager) is currently in Customer Support Team, grade 5.
- E-SEL-1012 | name | Cho Eunho |  | db, day fixed: Reply 1: D2
- E-SEL-1012 | alias | Eunho (Manager) |  | db, day fixed: Reply 1: D2
- E-SEL-1012 | employee_id | E-SEL-1012 |  | db, day fixed: Reply 1: D2
- E-SEL-1012 | department | Customer Support Team | active | db, day 6: Reply 1: D1
- E-SEL-1012 | grade | 5 | active | db, day 6: Reply 1: D1
- E-SEL-1012 | contract type | contractor | active | db, day 6: Reply 1: D1
- E-SEL-1012 | hire_day | -64 | active | db, day 6: Reply 1: D1
- E-SEL-1012 | employment status | active |  | db, day 6: Reply 1: D1
- E-SEL-1012 | name | Cho Eunho |  | db, day fixed: Reply 2: D2
- E-SEL-1012 | alias | Eunho (Manager) |  | db, day fixed: Reply 2: D2
- E-SEL-1012 | employee ID | E-SEL-1012 |  | db, day fixed: Reply 2: D2
- E-SEL-1012 | region | SEL |  | db, day fixed: Reply 2: D2
- E-SEL-1012 | department | Customer Support Team |  | db, day 6: Reply 2: D1
- E-SEL-1012 | grade | 5 |  | db, day 6: Reply 2: D1
- E-SEL-1012 | contract type | contractor |  | db, day 6: Reply 2: D1
- E-SEL-1012 | hire day | -64 |  | db, day 6: Reply 2: D1
- E-SEL-1012 | employment status | active |  | db, day 6: Reply 2: D1
- E-SEL-1012 | name | Cho Eunho |  | db, day fixed: Reply 3: D2
- E-SEL-1012 | alias | Eunho (Manager) |  | db, day fixed: Reply 3: D2
- E-SEL-1012 | current department | Customer Support Team | active | db, day 6: Reply 3: D1
- E-SEL-1012 | grade | 5 |  | db, day 6: Reply 3: D1
- E-SEL-1012 | contract type | contractor |  | db, day 6: Reply 3: D1
- E-SEL-1012 | employment status | active | active | db, day 6: Reply 3: D1
- E-SEL-1012 | department | Customer Support Team |  | db, day 6: Reply 4: D1
- E-SEL-1012 | grade | 5 |  | db, day 6: Reply 4: D1
- E-SEL-1012 | name | Cho Eunho |  | db, day unknown: Reply 4: D2
```