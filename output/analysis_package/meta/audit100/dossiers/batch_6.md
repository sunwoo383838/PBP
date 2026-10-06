## CASE 66: deepseek-v4-flash · routing · s14 · W-00081 · class B · day 9 · template plan
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
answer: {"steps": ["IT_EXCEPTION", "LEGAL_OVERRIDE", "FIN_DIVISION_HEAD"]}
official exact match: 1 (1/1 slots)
### MATCHER CHECK FR-01389 (need LEGAL-SEL/E-SEL-2007/contract): matcher says **delivered**
record text: Equipment exception of Jegal Yoon higher tiers including premium allowed until day 27 for a project, legal check done.
What the requester received from LEGAL-SEL during this task:
```
[Reply 1] (partial) Contract terms for E-SEL-2007: allowed tier 'standard' (database day 7), expiry day 108, NDA yes. LEGAL_NDA is needed because the contract has an NDA clause and no verified signed NDA copy is on file. LEGAL_OVERRIDE is needed because a workstation (premium) is above the standard allowed tier. BLOCKED_CONTRACT applies because the purchase exceeds the allowed tier without a legal exception. No equipment exceptions are recorded in my area.
[Reply 2] (partial) From my area's records: E-SEL-2007 (Jegal Yoon, grade 1 contractor, Sales Team 1) has contract terms of standard tier (registered day 7, superseding previous basic tier from day 3), expiry day 108, NDA required true. An equipment exception (H26, day -7) allows higher tiers including premium but its end date is cut off in my records. For LEGAL_NDA: the NDA check step applies to standard equipment, not premium, so not needed. For LEGAL_OVERRIDE/BLOCKED_CONTRACT: the contract blocks premium (above standard tier), but the exception may override it if still active - however the end date is unknown. Data residency policy restricts Sales Team 1 from offshore suppliers.
[Reply 3] (partial) Contract terms for E-SEL-2007: allowed_tier=standard, nda=true, expiry=108. An equipment exception (day 8) allows premium until day 27. LEGAL_NDA step is not needed because the purchase is for premium equipment (the NDA check rule applies to standard equipment). LEGAL_OVERRIDE is not needed because the existing exception covers the legal exception requirement. BLOCKED_CONTRACT cannot be determined because the vendor is unknown — the residency rule restricts Sales Team 1 from offshore suppliers.
[Reply 4] (partial) Contract terms for E-SEL-2007: allowed tier standard, NDA yes, expires day 108. Signed NDA copy verified (skip until day 19). The workstation is premium (above standard tier), so LEGAL_NDA does not apply (NDA check is for standard equipment); LEGAL_OVERRIDE is needed (legal exception with approver legal_and_division_head). No existing equipment exceptions found. BLOCKED_CONTRACT cannot be determined from my records (no supplier info). Also note Sales Team 1 may not use offshore supplier equipment per residency rule.
- E-SEL-2007 | allowed_tier | standard |  | db, day 7: Reply 1: D1
- E-SEL-2007 | contract expiry day | 108 |  | db, day 7: Reply 1: D1
- E-SEL-2007 | NDA required | true |  | db, day 7: Reply 1: D1
- E-SEL-2007 | allowed_tier (earlier database version, day 3) | basic |  | history, day 3: Reply 1: H109
- E-SEL-2007 | LEGAL_NDA needed | yes — contract has NDA clause; no verified signed NDA copy on file to skip the check |  | unknown, day unknown: Reply 1: rule:contractor_policy
- E-SEL-2007 | LEGAL_OVERRIDE needed | yes — workstation (premium) is above the contract's allowed tier (standard); premium equipment needs a legal exception per contractor_policy (approver legal_and_division_head) |  | unknown, day unknown: Reply 1: rule:contractor_policy
- E-SEL-2007 | BLOCKED_CONTRACT | yes — contract allows standard tier; workstation (premium) is above standard tier and no legal exception is recorded |  | db, day 7: Reply 1: D1
- E-SEL-2007 | existing equipment exceptions | none found in my area's records |  | db, day 7: Reply 1: D1
- E-SEL-2007 | catalog_entry | NO_RECORD |  | db, day unknown: Reply 1: D2
- E-SEL-2007 | allowed_tier (contract) | standard |  | db, day 7: Reply 2: D1
- E-SEL-2007 | contract expiry day | 108 |  | db, day 7: Reply 2: D1
- E-SEL-2007 | nda required | true |  | db, day 7: Reply 2: D1
- E-SEL-2007 | contract terms registered day | 7 |  | db, day 7: Reply 2: D1
- E-SEL-2007 | previous allowed_tier (superseded, registered day 3) | basic |  | history, day 6: Reply 2: H174
- E-SEL-2007 | item requested | workstation (premium) at 2,333,868 KRW |  | unknown, day unknown: Reply 2: question
- E-SEL-2007 | employee type | grade 1 contractor |  | history, day 6: Reply 2: H172
- E-SEL-2007 | department | Sales Team 1 |  | history, day 6: Reply 2: H172
- E-SEL-2007 | LEGAL_NDA step needed | no - NDA check step applies to standard equipment; this is premium equipment which falls under the legal exception rule instead |  | rule, day fixed: Reply 2: contractor_policy
- E-SEL-2007 | LEGAL_OVERRIDE needed | equipment exception exists (H26) allowing higher tiers including premium, but its end date is incomplete in records - cannot determine if still active | unknown end date | history, day -7: Reply 2: H26
- E-SEL-2007 | BLOCKED_CONTRACT issue | contract allows standard tier; premium workstation is above standard tier so contract would block it, but equipment exception (H26) allows higher tiers including premium - end date unknown | cannot determine if exception is active | db, day 7: Reply 2: D1, H26, contractor_policy
- E-SEL-2007 | existing equipment exception | higher tiers including premium allowed until ... for a project, legal check done | end date incomplete in records | history, day -7: Reply 2: H26
- E-SEL-2007 | data residency policy | Sales Team 1 may not use equipment from offshore suppliers | rule applies | rule, day fixed: Reply 2: residency
- E-SEL-2007 | contractor software restriction | workstation is not CAD or IDE Pro, so no restriction |  | rule, day fixed: Reply 2: sw_contractor
- E-SEL-2007 | allowed_tier (contract) | standard |  | db, day 7: Reply 3: D1
- E-SEL-2007 | nda required | true |  | db, day 7: Reply 3: D1
- E-SEL-2007 | contract expiry day | 108 |  | db, day 7: Reply 3: D1
- E-SEL-2007 | employee type | contractor |  | history, day 6: Reply 3: H164
- E-SEL-2007 | department | Sales Team 1 |  | history, day 6: Reply 3: H164
- E-SEL-2007 | equipment exception - higher tiers including premium allowed until day 27 | higher tiers including premium allowed until day 27 for a project, legal check done | in effect until day 27 | history, day 8: Reply 3: H183
- E-SEL-2007 | LEGAL_NDA step needed | no — the purchase is for premium equipment, not standard equipment; the NDA check rule applies only to standard equipment for contractors |  | rule, day fixed: Reply 3: rule: contractor_policy
- E-SEL-2007 | LEGAL_OVERRIDE needed | no — the existing equipment exception (recorded day 8) provides the required legal exception for premium equipment for a contractor, approved by legal_and_division_head |  | history, day 8: Reply 3: H183
- E-SEL-2007 | BLOCKED_CONTRACT issue | cannot determine — the residency rule restricts Sales Team 1 from using equipment from offshore suppliers, but the vendor/supplier of the workstation is not specified in my records |  | rule, day fixed: Reply 3: rule: residency
- workstation (premium) | purchase amount | 2,333,868 KRW |  | unknown, day unknown: Reply 3: question
- E-SEL-2007 | allowed tier (contract terms) | standard |  | db, day 7: Reply 4: D1
- E-SEL-2007 | contract expiry day | 108 |  | db, day 7: Reply 4: D1
- E-SEL-2007 | NDA required by contract | true |  | db, day 7: Reply 4: D1
- E-SEL-2007 | signed NDA copy verified | verified | skipped until day 19 | history, day -1: Reply 4: H2
- E-SEL-2007 | workstation type | premium |  | unknown, day unknown: Reply 4: task description
- E-SEL-2007 | workstation price | 2,333,868 KRW |  | unknown, day unknown: Reply 4: task description
- E-SEL-2007 | department | Sales Team 1 |  | unknown, day unknown: Reply 4: task description
- E-SEL-2007 | LEGAL_NDA step needed | no — NDA check applies only to standard equipment; this is premium equipment above the allowed tier |  | rule, day fixed: Reply 4: contractor_policy
- E-SEL-2007 | LEGAL_OVERRIDE needed | yes — premium equipment for contractors and equipment above the allowed tier (standard) need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 4: contractor_policy
- E-SEL-2007 | existing equipment exceptions | none found in my area's records |  | history, day -1: Reply 4: H1-H183
- E-SEL-2007 | residency restriction | Sales Team 1 may not use equipment from offshore suppliers |  | rule, day fixed: Reply 4: residency
missing: Whether E-SEL-2007 is a contractor or employee — not stored in my area's records (contract_terms and catalog_entry do not contain contract type); Supplier V-SEL-3 details (offshore/local) — not found in my area's records; Department of E-SEL-2007 — not stored in my area's records; catalog_entry for E-SEL-2007 (no record registered); full end date of equipment exception for Jegal Yoon (E-SEL-2007) - the summary record H26 cuts off the 'until' day; supplier information for the workstation purchase (not provided in question); tier-to-cost mapping for workstation (premium) at 2,333,868 KRW (no such mapping in my area's records); verified signed NDA copy for E-SEL-2007 (none in my records); Vendor/supplier of the workstation — not specified in the question and not found in my area's records; therefore cannot determine whether the residency rule (Sales Team 1 may not use equipment from offshore suppliers) creates a BLOCKED_CONTRACT issue; BLOCKED_CONTRACT issue — su
[... truncated]
```

## CASE 67: deepseek-v4-flash · routing · s13 · W-00021 · class C · day 3 · template vendor
### Task as given to the requester
That department from W-00005 needs a laptop. Pick a compliant supplier within budget.
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 480948, "approver": "team_lead", "budget_after": 180509, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 480948, "approver": "team_lead", "budget_after": 389652, "blocked_by": null}, "partial": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 480948, "approver": "team_lead", "budget_after": 648314, "blocked_by": null}, "neardup": {"vendor": "V-SEL-0", "option": "Q-V-SEL-0-LTB", "amount": 480948, "approver": "team_lead", "budget_after": 1809267, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/task/W-00005/result** (group HR-SEL, class None, local=True)
- RECORD FR-01000 (operational/task_result, day 1, by hr-sel.n0015; DB shows n/a): W-00005 item result: available=1149050, n_deducted=4
**need FIN-SEL/Sales Team 2/budget_schedule** (group FIN-SEL, class C, local=False)
- DB `FIN-SEL/line/Sales Team 2/remaining` v5 (recorded day -6, registered day -3): 3159648
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00683 [decision-critical] (operational/pending_intent, day -7, by fin-sel.a4; DB shows n/a): Sales Team 2 capex 467,805 KRW earmarked for training equipment until day 7 (no voucher yet).
- RECORD FR-00904 [decision-critical] (operational/pending_intent, day -1, by fin-sel.a1; DB shows n/a): Sales Team 2 capex 462,318 KRW earmarked for quarter-end consumables until day 14 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00002/status` v2 (recorded day -9, registered day -7): {"status": "settled", "amount": 349589, "expected_settle": -9}
- DB `FIN-SEL/commit/CMT-00005/status` v2 (recorded day -10, registered day -8): {"status": "settled", "amount": 584884, "expected_settle": -10}
- DB `FIN-SEL/commit/CMT-00010/status` v2 (recorded day -10, registered day -8): {"status": "settled", "amount": 254702, "expected_settle": -10}
- RECORD FR-01046 [decision-critical] (db_pending/observation, day 2, by fin-sel.n0004; DB shows ABSENT): CMT-00059 Sales Team 2 provisional approval 632,153 KRW confirmed, settlement expected day 5. Stored value: {"amount":632153,"expected_settle":5,"status":"pending"}
- RECORD FR-00957 [decision-critical] (operational/pending_intent, day 0, by fin-sel.a3; DB shows n/a): CMT-00061 Sales Team 2 meeting room equipment provisional approval 448,322 KRW under review, settlement expected day 8.
- RECORD FR-01018 [decision-critical] (operational/pending_intent, day 2, by fin-sel.n0005; DB shows n/a): CMT-00065 Sales Team 2 order (incl. shipping) provisional approval (order of W-00001) 487,593 KRW under review, settlement expected day 6.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Team 2 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00683", "earmark:FR-00904", "CMT-00059", "CMT-00061", "CMT-00065"]
**need PROC-SEL/quotes/laptop** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01055 (operational/handover, day 2, by proc-sel.w00148; DB shows n/a): Supplier V-SEL-3 exclude from comparisons until day 13 due to a quality issue.
- RECORD FR-01074 (operational/handover, day 2, by proc-sel.w00152; DB shows n/a): Supplier V-SEL-1 exclude from comparisons until day 7 due to a quality issue.
- RECORD FR-00610 (operational/observation, day -9, by proc-sel.w00070; DB shows n/a): Supplier V-SEL-2 delivery notified: deliveries delayed by 4 days until day 3.
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
- DB `PROC-SEL/vendor/V-SEL-1/lead` v2 (recorded day -7, registered day -6): 5
- DB `PROC-SEL/quote/Q-V-SEL-1-LTB/amount` v3 (recorded day -16, registered day -15): 589357
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v2 (recorded day -7, registered day -6): 5
- DB `PROC-SEL/quote/Q-V-SEL-1-LTP/amount` v2 (recorded day -16, registered day -13): 2084743
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v2 (recorded day -7, registered day -6): 5
- DB `PROC-SEL/quote/Q-V-SEL-1-LTS/amount` v3 (recorded day -2, registered day -1): 1082462
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v2 (recorded day -1, registered day 2): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-LTP/amount` v1 (recorded day -20, registered day -20): 2252407
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-LTS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v2 (recorded day -1, registered day 2): 8
- DB `PROC-SEL/quote/Q-V-SEL-2-LTS/amount` v1 (recorded day -20, registered day -20): 1191288
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTB"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v2 (recorded day -6, registered day -3): 12
- DB `PROC-SEL/quote/Q-V-SEL-3-LTB/amount` v1 (recorded day -20, registered day -20): 814884
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-LTP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v2 (recorded day -6, registered day -3): 12
- DB `PROC-SEL/quote/Q-V-SEL-3-LTP/amount` v1 (recorded day -20, registered day -20): 1872838
**need LEGAL-SEL/residency** (group LEGAL-SEL, class A, local=False)
- RULE LEGAL-SEL.residency: {"id": "LEGAL-SEL.residency", "group": "LEGAL-SEL", "title": "Data residency", "params": {"restricted_depts": ["Dev Team 1", "Sales Team 2"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Team 1, Sales Team 2."}
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"amount": 480948, "approver": "team_lead", "blocked_by": null, "budget_after": 1109779, "option": "Q-V-SEL-0-LTB", "vendor": "V-SEL-0"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-00683 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: Sales Team 2 capex 467,805 KRW earmarked for training equipment until day 7 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) Sales Team 2's current database capex balance is 3,159,648 KRW (registered day -3). Active deductions: CMT-00059 (under review, 632,153 KRW, expected settlement day 5, recorded day 0) and an earmark for quarter-end consumables (462,318 KRW, until day 14, recorded day -1). All three database provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. After deducting the under-review item and the active earmark per Art. 4.2, the remaining available budget on day 3 is 2,065,177 KRW.
[Reply 2] (partial) Sales Team 2's current capex budget balance is 3,159,648 KRW. There are no active deductions: all three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled, and no items under review or earmarks were found in my area's records. Therefore the available budget equals the balance: 3,159,648 KRW.
[Reply 3] (ok) Sales Team 2's current capex budget balance is 3,159,648 KRW. There is 1 active deduction: the training equipment earmark of 467,805 KRW (recorded day -7, valid through day 7). All three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and do not reduce the budget. Available budget = 3,159,648 − 467,805 = 2,691,843 KRW.
[Reply 4] (ok) Sales Team 2's current capex balance is 3,159,648 KRW (registered day -3). The only active deduction is CMT-00065 (487,593 KRW under review, expected settle day 6, recorded day 2). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. No earmarks are recorded for Sales Team 2 in my area's records. The available budget after deducting the under-review item is 2,672,055 KRW.
- Sales Team 2 | capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | balance registered day | -3 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D3
- Sales Team 2 | base allocation registered day | -20 |  | db, day -20: Reply 1: D3
- CMT-00059 | provisional approval amount | 632153 | under review | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462318 | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 1: D2
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 1: D2
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 1: D2
- Sales Team 2 | available budget calculation (Art. 4.2): balance − under review items − active earmarks | 3159648 − 632153 − 462318 = 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | remaining available capex budget (day 3) | 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base | 2683779 |  | db, day -20: Reply 2: D2
- Sales Team 2 | current capex budget balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | number of items under review | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | earmarks in validity period | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | available budget (calculated) | 3159648 |  | rule, day fixed: Reply 2: pending_deduction
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D5
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D5
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D6
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D6
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D7
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D7
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | active earmark (training equipment) | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | earmark record date | day -7 |  | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available capex budget (calculated) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | line balance input for calculation | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | active earmark input for calculation | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | provisional approvals deducted | 0 | none pending or under review | db, day unknown: Reply 3: D3
- Sales Team 2 | capex balance | 3159648 |  | db, day -3: Reply 4: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 4: D3
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D2
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00065 | provisional approval amount (under review) | 487593 | under review | history, day 2: Reply 4: H133
- CMT-00065 | expected settlement day | 6 |  | history, day 2: Reply 4: H133
- Sales Team 2 | available budget (line balance minus under-review items) | 2672055 |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | earmarks | none registered in my area's records |  | history, day 2: Reply 4: H133
missing: Any earmarks for Sales Team 2 — not found in my area's records or database; Any items under review for Sales Team 2 — not found in my area's records or database
---
[Reply 1] (partial) Here are the findings from my area's records:
[Reply 2] (partial) From SEL area's records and database: The only active deduction I can confirm for Sales Team 2 is the training equipment earmark of 467,805 KRW (recorded day -7, valid until day 7). CMT-00059, CMT-00065, and the quarter-end consumables earmark of 462,318 KRW are not found in any SEL area records or database.
- CMT-00059 | status | under review | under review | history, day 0: Reply 1: H130
- CMT-00059 | amount | 632,153 KRW |  | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | most recent record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462,318 KRW | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00065 | status | no status recorded (suggestion to cancel, not decided) |  | history, day 2: Reply 1: H324
- CMT-00065 | most recent record date | day 2 |  | history, day 2: Reply 1: H324
- CMT-00059 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D3
- CMT-00059 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D5
- CMT-00065 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D4
- CMT-00065 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D6
- Sales Team 2 | training equipment earmark amount | 467805 | earmarked until day 7 | history, day -7: Reply 2: H30
- Sales Team 2 | training equipment earmark record date | day -7 |  | history, day -7: Reply 2: H30
- Sales Team 2 | quarter-end consumables earmark 462318 KRW | NOT_FOUND in SEL records |  | history, day -7: Reply 2: H30-H31
missing: Sales Team 2 – training equipment earmark of 467,805 KRW until day 7 — no such record found in my area's records or database; Whether CMT-00059 is under review — not in SEL area's records or database; Most recent record date for CMT-00059 — not in SEL area's records or database; Whether a quarter-end consumables earmark of 462,318 KRW until day 14 exists — not in SEL area's records or database; Record date for quarter-end consumables earmark — not in SEL area's records or database; Whether CMT-00065 is under review — not in SEL area's records or database; Most recent record date for CMT-00065 — not in SEL area's records or database
---
[Reply 1] (ok) Sales Team 2's final available capex budget on day 3 is 2,065,177 KRW, after deducting two active items: CMT-00059 (under review, 632,153 KRW, record day 0) and the quarter-end consumables earmark (462,318 KRW, until day 14, record day -1).
[Reply 2] (ok) Sales Team 2's available capex budget today (day 3) is 2,672,055 KRW. The only active deduction is CMT-
[... truncated]
```
### MATCHER CHECK FR-00904 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: Sales Team 2 capex 462,318 KRW earmarked for quarter-end consumables until day 14 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) Sales Team 2's current database capex balance is 3,159,648 KRW (registered day -3). Active deductions: CMT-00059 (under review, 632,153 KRW, expected settlement day 5, recorded day 0) and an earmark for quarter-end consumables (462,318 KRW, until day 14, recorded day -1). All three database provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. After deducting the under-review item and the active earmark per Art. 4.2, the remaining available budget on day 3 is 2,065,177 KRW.
[Reply 2] (partial) Sales Team 2's current capex budget balance is 3,159,648 KRW. There are no active deductions: all three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled, and no items under review or earmarks were found in my area's records. Therefore the available budget equals the balance: 3,159,648 KRW.
[Reply 3] (ok) Sales Team 2's current capex budget balance is 3,159,648 KRW. There is 1 active deduction: the training equipment earmark of 467,805 KRW (recorded day -7, valid through day 7). All three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and do not reduce the budget. Available budget = 3,159,648 − 467,805 = 2,691,843 KRW.
[Reply 4] (ok) Sales Team 2's current capex balance is 3,159,648 KRW (registered day -3). The only active deduction is CMT-00065 (487,593 KRW under review, expected settle day 6, recorded day 2). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. No earmarks are recorded for Sales Team 2 in my area's records. The available budget after deducting the under-review item is 2,672,055 KRW.
- Sales Team 2 | capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | balance registered day | -3 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D3
- Sales Team 2 | base allocation registered day | -20 |  | db, day -20: Reply 1: D3
- CMT-00059 | provisional approval amount | 632153 | under review | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462318 | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 1: D2
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 1: D2
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 1: D2
- Sales Team 2 | available budget calculation (Art. 4.2): balance − under review items − active earmarks | 3159648 − 632153 − 462318 = 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | remaining available capex budget (day 3) | 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base | 2683779 |  | db, day -20: Reply 2: D2
- Sales Team 2 | current capex budget balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | number of items under review | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | earmarks in validity period | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | available budget (calculated) | 3159648 |  | rule, day fixed: Reply 2: pending_deduction
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D5
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D5
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D6
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D6
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D7
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D7
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | active earmark (training equipment) | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | earmark record date | day -7 |  | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available capex budget (calculated) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | line balance input for calculation | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | active earmark input for calculation | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | provisional approvals deducted | 0 | none pending or under review | db, day unknown: Reply 3: D3
- Sales Team 2 | capex balance | 3159648 |  | db, day -3: Reply 4: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 4: D3
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D2
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00065 | provisional approval amount (under review) | 487593 | under review | history, day 2: Reply 4: H133
- CMT-00065 | expected settlement day | 6 |  | history, day 2: Reply 4: H133
- Sales Team 2 | available budget (line balance minus under-review items) | 2672055 |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | earmarks | none registered in my area's records |  | history, day 2: Reply 4: H133
missing: Any earmarks for Sales Team 2 — not found in my area's records or database; Any items under review for Sales Team 2 — not found in my area's records or database
---
[Reply 1] (partial) Here are the findings from my area's records:
[Reply 2] (partial) From SEL area's records and database: The only active deduction I can confirm for Sales Team 2 is the training equipment earmark of 467,805 KRW (recorded day -7, valid until day 7). CMT-00059, CMT-00065, and the quarter-end consumables earmark of 462,318 KRW are not found in any SEL area records or database.
- CMT-00059 | status | under review | under review | history, day 0: Reply 1: H130
- CMT-00059 | amount | 632,153 KRW |  | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | most recent record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462,318 KRW | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00065 | status | no status recorded (suggestion to cancel, not decided) |  | history, day 2: Reply 1: H324
- CMT-00065 | most recent record date | day 2 |  | history, day 2: Reply 1: H324
- CMT-00059 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D3
- CMT-00059 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D5
- CMT-00065 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D4
- CMT-00065 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D6
- Sales Team 2 | training equipment earmark amount | 467805 | earmarked until day 7 | history, day -7: Reply 2: H30
- Sales Team 2 | training equipment earmark record date | day -7 |  | history, day -7: Reply 2: H30
- Sales Team 2 | quarter-end consumables earmark 462318 KRW | NOT_FOUND in SEL records |  | history, day -7: Reply 2: H30-H31
missing: Sales Team 2 – training equipment earmark of 467,805 KRW until day 7 — no such record found in my area's records or database; Whether CMT-00059 is under review — not in SEL area's records or database; Most recent record date for CMT-00059 — not in SEL area's records or database; Whether a quarter-end consumables earmark of 462,318 KRW until day 14 exists — not in SEL area's records or database; Record date for quarter-end consumables earmark — not in SEL area's records or database; Whether CMT-00065 is under review — not in SEL area's records or database; Most recent record date for CMT-00065 — not in SEL area's records or database
---
[Reply 1] (ok) Sales Team 2's final available capex budget on day 3 is 2,065,177 KRW, after deducting two active items: CMT-00059 (under review, 632,153 KRW, record day 0) and the quarter-end consumables earmark (462,318 KRW, until day 14, record day -1).
[Reply 2] (ok) Sales Team 2's available capex budget today (day 3) is 2,672,055 KRW. The only active deduction is CMT-
[... truncated]
```
### MATCHER CHECK FR-01046 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: CMT-00059 Sales Team 2 provisional approval 632,153 KRW confirmed, settlement expected day 5. Stored value: {"amount":632153,"expected_settle":5,"status":"pending"}
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) Sales Team 2's current database capex balance is 3,159,648 KRW (registered day -3). Active deductions: CMT-00059 (under review, 632,153 KRW, expected settlement day 5, recorded day 0) and an earmark for quarter-end consumables (462,318 KRW, until day 14, recorded day -1). All three database provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. After deducting the under-review item and the active earmark per Art. 4.2, the remaining available budget on day 3 is 2,065,177 KRW.
[Reply 2] (partial) Sales Team 2's current capex budget balance is 3,159,648 KRW. There are no active deductions: all three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled, and no items under review or earmarks were found in my area's records. Therefore the available budget equals the balance: 3,159,648 KRW.
[Reply 3] (ok) Sales Team 2's current capex budget balance is 3,159,648 KRW. There is 1 active deduction: the training equipment earmark of 467,805 KRW (recorded day -7, valid through day 7). All three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and do not reduce the budget. Available budget = 3,159,648 − 467,805 = 2,691,843 KRW.
[Reply 4] (ok) Sales Team 2's current capex balance is 3,159,648 KRW (registered day -3). The only active deduction is CMT-00065 (487,593 KRW under review, expected settle day 6, recorded day 2). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. No earmarks are recorded for Sales Team 2 in my area's records. The available budget after deducting the under-review item is 2,672,055 KRW.
- Sales Team 2 | capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | balance registered day | -3 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D3
- Sales Team 2 | base allocation registered day | -20 |  | db, day -20: Reply 1: D3
- CMT-00059 | provisional approval amount | 632153 | under review | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462318 | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 1: D2
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 1: D2
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 1: D2
- Sales Team 2 | available budget calculation (Art. 4.2): balance − under review items − active earmarks | 3159648 − 632153 − 462318 = 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | remaining available capex budget (day 3) | 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base | 2683779 |  | db, day -20: Reply 2: D2
- Sales Team 2 | current capex budget balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | number of items under review | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | earmarks in validity period | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | available budget (calculated) | 3159648 |  | rule, day fixed: Reply 2: pending_deduction
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D5
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D5
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D6
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D6
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D7
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D7
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | active earmark (training equipment) | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | earmark record date | day -7 |  | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available capex budget (calculated) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | line balance input for calculation | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | active earmark input for calculation | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | provisional approvals deducted | 0 | none pending or under review | db, day unknown: Reply 3: D3
- Sales Team 2 | capex balance | 3159648 |  | db, day -3: Reply 4: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 4: D3
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D2
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00065 | provisional approval amount (under review) | 487593 | under review | history, day 2: Reply 4: H133
- CMT-00065 | expected settlement day | 6 |  | history, day 2: Reply 4: H133
- Sales Team 2 | available budget (line balance minus under-review items) | 2672055 |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | earmarks | none registered in my area's records |  | history, day 2: Reply 4: H133
missing: Any earmarks for Sales Team 2 — not found in my area's records or database; Any items under review for Sales Team 2 — not found in my area's records or database
---
[Reply 1] (partial) Here are the findings from my area's records:
[Reply 2] (partial) From SEL area's records and database: The only active deduction I can confirm for Sales Team 2 is the training equipment earmark of 467,805 KRW (recorded day -7, valid until day 7). CMT-00059, CMT-00065, and the quarter-end consumables earmark of 462,318 KRW are not found in any SEL area records or database.
- CMT-00059 | status | under review | under review | history, day 0: Reply 1: H130
- CMT-00059 | amount | 632,153 KRW |  | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | most recent record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462,318 KRW | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00065 | status | no status recorded (suggestion to cancel, not decided) |  | history, day 2: Reply 1: H324
- CMT-00065 | most recent record date | day 2 |  | history, day 2: Reply 1: H324
- CMT-00059 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D3
- CMT-00059 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D5
- CMT-00065 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D4
- CMT-00065 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D6
- Sales Team 2 | training equipment earmark amount | 467805 | earmarked until day 7 | history, day -7: Reply 2: H30
- Sales Team 2 | training equipment earmark record date | day -7 |  | history, day -7: Reply 2: H30
- Sales Team 2 | quarter-end consumables earmark 462318 KRW | NOT_FOUND in SEL records |  | history, day -7: Reply 2: H30-H31
missing: Sales Team 2 – training equipment earmark of 467,805 KRW until day 7 — no such record found in my area's records or database; Whether CMT-00059 is under review — not in SEL area's records or database; Most recent record date for CMT-00059 — not in SEL area's records or database; Whether a quarter-end consumables earmark of 462,318 KRW until day 14 exists — not in SEL area's records or database; Record date for quarter-end consumables earmark — not in SEL area's records or database; Whether CMT-00065 is under review — not in SEL area's records or database; Most recent record date for CMT-00065 — not in SEL area's records or database
---
[Reply 1] (ok) Sales Team 2's final available capex budget on day 3 is 2,065,177 KRW, after deducting two active items: CMT-00059 (under review, 632,153 KRW, record day 0) and the quarter-end consumables earmark (462,318 KRW, until day 14, record day -1).
[Reply 2] (ok) Sales Team 2's available capex budget today (day 3) is 2,672,055 KRW. The only active deduction is CMT-
[... truncated]
```
### MATCHER CHECK FR-00957 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00061 Sales Team 2 meeting room equipment provisional approval 448,322 KRW under review, settlement expected day 8.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) Sales Team 2's current database capex balance is 3,159,648 KRW (registered day -3). Active deductions: CMT-00059 (under review, 632,153 KRW, expected settlement day 5, recorded day 0) and an earmark for quarter-end consumables (462,318 KRW, until day 14, recorded day -1). All three database provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. After deducting the under-review item and the active earmark per Art. 4.2, the remaining available budget on day 3 is 2,065,177 KRW.
[Reply 2] (partial) Sales Team 2's current capex budget balance is 3,159,648 KRW. There are no active deductions: all three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled, and no items under review or earmarks were found in my area's records. Therefore the available budget equals the balance: 3,159,648 KRW.
[Reply 3] (ok) Sales Team 2's current capex budget balance is 3,159,648 KRW. There is 1 active deduction: the training equipment earmark of 467,805 KRW (recorded day -7, valid through day 7). All three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and do not reduce the budget. Available budget = 3,159,648 − 467,805 = 2,691,843 KRW.
[Reply 4] (ok) Sales Team 2's current capex balance is 3,159,648 KRW (registered day -3). The only active deduction is CMT-00065 (487,593 KRW under review, expected settle day 6, recorded day 2). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. No earmarks are recorded for Sales Team 2 in my area's records. The available budget after deducting the under-review item is 2,672,055 KRW.
- Sales Team 2 | capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | balance registered day | -3 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D3
- Sales Team 2 | base allocation registered day | -20 |  | db, day -20: Reply 1: D3
- CMT-00059 | provisional approval amount | 632153 | under review | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462318 | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 1: D2
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 1: D2
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 1: D2
- Sales Team 2 | available budget calculation (Art. 4.2): balance − under review items − active earmarks | 3159648 − 632153 − 462318 = 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | remaining available capex budget (day 3) | 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base | 2683779 |  | db, day -20: Reply 2: D2
- Sales Team 2 | current capex budget balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | number of items under review | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | earmarks in validity period | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | available budget (calculated) | 3159648 |  | rule, day fixed: Reply 2: pending_deduction
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D5
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D5
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D6
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D6
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D7
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D7
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | active earmark (training equipment) | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | earmark record date | day -7 |  | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available capex budget (calculated) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | line balance input for calculation | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | active earmark input for calculation | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | provisional approvals deducted | 0 | none pending or under review | db, day unknown: Reply 3: D3
- Sales Team 2 | capex balance | 3159648 |  | db, day -3: Reply 4: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 4: D3
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D2
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00065 | provisional approval amount (under review) | 487593 | under review | history, day 2: Reply 4: H133
- CMT-00065 | expected settlement day | 6 |  | history, day 2: Reply 4: H133
- Sales Team 2 | available budget (line balance minus under-review items) | 2672055 |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | earmarks | none registered in my area's records |  | history, day 2: Reply 4: H133
missing: Any earmarks for Sales Team 2 — not found in my area's records or database; Any items under review for Sales Team 2 — not found in my area's records or database
---
[Reply 1] (partial) Here are the findings from my area's records:
[Reply 2] (partial) From SEL area's records and database: The only active deduction I can confirm for Sales Team 2 is the training equipment earmark of 467,805 KRW (recorded day -7, valid until day 7). CMT-00059, CMT-00065, and the quarter-end consumables earmark of 462,318 KRW are not found in any SEL area records or database.
- CMT-00059 | status | under review | under review | history, day 0: Reply 1: H130
- CMT-00059 | amount | 632,153 KRW |  | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | most recent record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462,318 KRW | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00065 | status | no status recorded (suggestion to cancel, not decided) |  | history, day 2: Reply 1: H324
- CMT-00065 | most recent record date | day 2 |  | history, day 2: Reply 1: H324
- CMT-00059 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D3
- CMT-00059 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D5
- CMT-00065 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D4
- CMT-00065 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D6
- Sales Team 2 | training equipment earmark amount | 467805 | earmarked until day 7 | history, day -7: Reply 2: H30
- Sales Team 2 | training equipment earmark record date | day -7 |  | history, day -7: Reply 2: H30
- Sales Team 2 | quarter-end consumables earmark 462318 KRW | NOT_FOUND in SEL records |  | history, day -7: Reply 2: H30-H31
missing: Sales Team 2 – training equipment earmark of 467,805 KRW until day 7 — no such record found in my area's records or database; Whether CMT-00059 is under review — not in SEL area's records or database; Most recent record date for CMT-00059 — not in SEL area's records or database; Whether a quarter-end consumables earmark of 462,318 KRW until day 14 exists — not in SEL area's records or database; Record date for quarter-end consumables earmark — not in SEL area's records or database; Whether CMT-00065 is under review — not in SEL area's records or database; Most recent record date for CMT-00065 — not in SEL area's records or database
---
[Reply 1] (ok) Sales Team 2's final available capex budget on day 3 is 2,065,177 KRW, after deducting two active items: CMT-00059 (under review, 632,153 KRW, record day 0) and the quarter-end consumables earmark (462,318 KRW, until day 14, record day -1).
[Reply 2] (ok) Sales Team 2's available capex budget today (day 3) is 2,672,055 KRW. The only active deduction is CMT-
[... truncated]
```
### MATCHER CHECK FR-01018 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: CMT-00065 Sales Team 2 order (incl. shipping) provisional approval (order of W-00001) 487,593 KRW under review, settlement expected day 6.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (ok) Sales Team 2's current database capex balance is 3,159,648 KRW (registered day -3). Active deductions: CMT-00059 (under review, 632,153 KRW, expected settlement day 5, recorded day 0) and an earmark for quarter-end consumables (462,318 KRW, until day 14, recorded day -1). All three database provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. After deducting the under-review item and the active earmark per Art. 4.2, the remaining available budget on day 3 is 2,065,177 KRW.
[Reply 2] (partial) Sales Team 2's current capex budget balance is 3,159,648 KRW. There are no active deductions: all three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled, and no items under review or earmarks were found in my area's records. Therefore the available budget equals the balance: 3,159,648 KRW.
[Reply 3] (ok) Sales Team 2's current capex budget balance is 3,159,648 KRW. There is 1 active deduction: the training equipment earmark of 467,805 KRW (recorded day -7, valid through day 7). All three provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and do not reduce the budget. Available budget = 3,159,648 − 467,805 = 2,691,843 KRW.
[Reply 4] (ok) Sales Team 2's current capex balance is 3,159,648 KRW (registered day -3). The only active deduction is CMT-00065 (487,593 KRW under review, expected settle day 6, recorded day 2). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled. No earmarks are recorded for Sales Team 2 in my area's records. The available budget after deducting the under-review item is 2,672,055 KRW.
- Sales Team 2 | capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | balance registered day | -3 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D3
- Sales Team 2 | base allocation registered day | -20 |  | db, day -20: Reply 1: D3
- CMT-00059 | provisional approval amount | 632153 | under review | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462318 | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 1: D2
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 1: D2
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 1: D2
- Sales Team 2 | available budget calculation (Art. 4.2): balance − under review items − active earmarks | 3159648 − 632153 − 462318 = 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | remaining available capex budget (day 3) | 2065177 |  | rule, day fixed: Reply 1: rule: pending_deduction
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base | 2683779 |  | db, day -20: Reply 2: D2
- Sales Team 2 | current capex budget balance | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | number of pending provisional approvals | 0 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | number of items under review | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | earmarks in validity period | 0 |  | unknown, day unknown: Reply 2: history
- Sales Team 2 | available budget (calculated) | 3159648 |  | rule, day fixed: Reply 2: pending_deduction
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D5
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D5
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D6
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D6
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D7
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D7
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | active earmark (training equipment) | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | earmark record date | day -7 |  | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available capex budget (calculated) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | line balance input for calculation | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | active earmark input for calculation | 467805 | earmarked until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | provisional approvals deducted | 0 | none pending or under review | db, day unknown: Reply 3: D3
- Sales Team 2 | capex balance | 3159648 |  | db, day -3: Reply 4: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 4: D3
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D2
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D2
- CMT-00065 | provisional approval amount (under review) | 487593 | under review | history, day 2: Reply 4: H133
- CMT-00065 | expected settlement day | 6 |  | history, day 2: Reply 4: H133
- Sales Team 2 | available budget (line balance minus under-review items) | 2672055 |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | earmarks | none registered in my area's records |  | history, day 2: Reply 4: H133
missing: Any earmarks for Sales Team 2 — not found in my area's records or database; Any items under review for Sales Team 2 — not found in my area's records or database
---
[Reply 1] (partial) Here are the findings from my area's records:
[Reply 2] (partial) From SEL area's records and database: The only active deduction I can confirm for Sales Team 2 is the training equipment earmark of 467,805 KRW (recorded day -7, valid until day 7). CMT-00059, CMT-00065, and the quarter-end consumables earmark of 462,318 KRW are not found in any SEL area records or database.
- CMT-00059 | status | under review | under review | history, day 0: Reply 1: H130
- CMT-00059 | amount | 632,153 KRW |  | history, day 0: Reply 1: H130
- CMT-00059 | expected settlement day | 5 |  | history, day 0: Reply 1: H130
- CMT-00059 | most recent record date | day 0 |  | history, day 0: Reply 1: H130
- Sales Team 2 | active earmark – quarter-end consumables | 462,318 KRW | until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | earmark record date | day -1 |  | history, day -1: Reply 1: H127
- CMT-00065 | status | no status recorded (suggestion to cancel, not decided) |  | history, day 2: Reply 1: H324
- CMT-00065 | most recent record date | day 2 |  | history, day 2: Reply 1: H324
- CMT-00059 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D3
- CMT-00059 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D5
- CMT-00065 | existence in SEL area records | NOT_FOUND |  | db, day unknown: Reply 2: D4
- CMT-00065 | provisional_approval record | NOT_FOUND |  | db, day unknown: Reply 2: D6
- Sales Team 2 | training equipment earmark amount | 467805 | earmarked until day 7 | history, day -7: Reply 2: H30
- Sales Team 2 | training equipment earmark record date | day -7 |  | history, day -7: Reply 2: H30
- Sales Team 2 | quarter-end consumables earmark 462318 KRW | NOT_FOUND in SEL records |  | history, day -7: Reply 2: H30-H31
missing: Sales Team 2 – training equipment earmark of 467,805 KRW until day 7 — no such record found in my area's records or database; Whether CMT-00059 is under review — not in SEL area's records or database; Most recent record date for CMT-00059 — not in SEL area's records or database; Whether a quarter-end consumables earmark of 462,318 KRW until day 14 exists — not in SEL area's records or database; Record date for quarter-end consumables earmark — not in SEL area's records or database; Whether CMT-00065 is under review — not in SEL area's records or database; Most recent record date for CMT-00065 — not in SEL area's records or database
---
[Reply 1] (ok) Sales Team 2's final available capex budget on day 3 is 2,065,177 KRW, after deducting two active items: CMT-00059 (under review, 632,153 KRW, record day 0) and the quarter-end consumables earmark (462,318 KRW, until day 14, record day -1).
[Reply 2] (ok) Sales Team 2's available capex budget today (day 3) is 2,672,055 KRW. The only active deduction is CMT-
[... truncated]
```

## CASE 68: deepseek-v4-flash · routing · s14 · W-00125 · class C · day 13 · template alloc
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
answer: {"alloc": [4, 1, 3], "buy": 7, "transfer": 0, "unmet": 0}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-01641 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **delivered**
record text: HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01621 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: HR record of Oh Minjae exit processed (Customer Support Team). Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":2,"hire_day":-111,"status":"exited"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01643 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **delivered**
record text: HR record of Shin Daeun moved from Dev Team 1 to Customer Support Team, grade 1, regular. Stored value: {"contract":"regular","dept":"Customer Support Team","grade":1,"hire_day":-869,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01248 (need HR-SEL/Customer Support Team/planning_headcount): matcher says **missing**
record text: Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01641 (need HR-SEL/Marketing Team/planning_headcount): matcher says **delivered**
record text: HR record of Han Siwoo moved from Marketing Team to Customer Support Team, grade 1, contractor. Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":1,"hire_day":-567,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01248 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01642 (need HR-SEL/Marketing Team/planning_headcount): matcher says **stale**
record text: HR record of Bong Seoha moved from Marketing Team to Sales Team 2, grade 2, regular. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":2,"hire_day":-6,"status":"active"}
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01405 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Tak Jiho approved from Dev Team 2 to Marketing Team, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01645 (need HR-SEL/Sales Team 1/planning_headcount): matcher says **missing**
record text: Transfer of Kim Harin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01626 (need HR-SEL/Sales Team 1/planning_headcount): matcher says **missing**
record text: Transfer of Jung Yerin approved from Dev Team 2 to Sales Team 1, effective day 16 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
[Reply 1] (partial) Planning headcounts: Customer Support Team = 3, Marketing Team = 2, Sales Team 1 = 2.
[Reply 2] (ok) Planning headcounts as of day 13: Customer Support Team = 5 (4 active + 1 transfer of E-SEL-1009 taking effect day 13 within 7 days); Marketing Team = 3; Sales Team 1 = 2.
[Reply 3] (partial) Planning headcounts: Customer Support Team = 4, Marketing Team = 3, Sales Team 1 = 2. No confirmed hires or transfers within the next 7 days were found in my records.
[Reply 4] (partial) Planning headcounts as of day 13: Customer Support Team = 4, Marketing Team = 1, Sales Team 1 = 3.
- Customer Support Team | headcount (active employees per database) | 4 |  | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1006 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1010 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1016 | active | db, day unknown: Reply 1: D1
- Customer Support Team | active employee (database) | E-SEL-1019 | active | db, day unknown: Reply 1: D1
- E-SEL-1006 | employment status (per exit record day 12) | exited |  | history, day 12: Reply 1: H672
- Customer Support Team | headcount (active after day-12 exit) | 3 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Customer Support Team | planning headcount | 3 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Marketing Team | headcount (active employees per database) | 3 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1000 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-1005 | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee (database) | E-SEL-2010 | active | db, day unknown: Reply 1: D2
- E-SEL-1000 | department (per transfer record day 12) | Dev Team 2 |  | history, day 12: Reply 1: H635
- Marketing Team | headcount (active after day-12 transfer of E-SEL-1000) | 2 |  | unknown, day unknown: Reply 1: rule:headcount_definition
- Marketing Team | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Sales Team 1 | headcount (active employees per database) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-1013 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | active employee (database) | E-SEL-2007 | active | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1001 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | exited employee (database) | E-SEL-1018 | exited | db, day unknown: Reply 1: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 1: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1006 (contractor, grade 2, hire_day -111, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1010 (contractor, grade 5, hire_day -385, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1016 (regular, grade 1, hire_day -328, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | active employee | E-SEL-1019 (regular, grade 1, hire_day -123, active) | active | db, day unknown: Reply 2: D1
- Customer Support Team | transfer taking effect within 7 days | E-SEL-1009 (Shin Daeun) transferred from Dev Team 1 to Customer Support Team, grade 1, regular, effective day 13 |  | history, day 13: Reply 2: H222
- Customer Support Team | planning headcount | 5 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1000 (regular, grade 2, hire_day -510, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-1005 (contractor, grade 1, hire_day -567, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | active employee | E-SEL-2010 (regular, grade 2, hire_day -6, active) | active | db, day unknown: Reply 2: D2
- Marketing Team | planning headcount | 3 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-1013 (regular, grade 2, hire_day -733, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | active employee | E-SEL-2007 (contractor, grade 1, hire_day -12, active) | active | db, day unknown: Reply 2: D3
- Sales Team 1 | planning headcount | 2 |  | unknown, day unknown: Reply 2: rule:planning_headcount
- Customer Support Team | headcount (active employees) | 4 |  | db, day unknown: Reply 3: D1
- E-SEL-1006 | status | active |  | db, day 4: Reply 3: D1
- E-SEL-1010 | status | active |  | db, day 12: Reply 3: D1
- E-SEL-1016 | status | active |  | db, day -20: Reply 3: D1
- E-SEL-1019 | status | active |  | db, day 11: Reply 3: D1
- E-SEL-1017 | status | exited |  | db, day -3: Reply 3: D1
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | headcount (active employees) | 3 |  | db, day unknown: Reply 3: D2
- E-SEL-1000 | status | active |  | db, day -5: Reply 3: D2
- E-SEL-1005 | status | active |  | db, day -1: Reply 3: D2
- E-SEL-2010 | status | active |  | db, day 5: Reply 3: D2
- Marketing Team | planning headcount | 3 |  | rule, day fixed: Reply 3: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- E-SEL-1013 | status | active |  | db, day 9: Reply 3: D3
- E-SEL-2007 | status | active |  | db, day 5: Reply 3: D3
- E-SEL-1001 | status | exited |  | db, day -15: Reply 3: D3
- E-SEL-1018 | status | exited |  | db, day 13: Reply 3: D3
- Sales Team 1 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Customer Support Team | planning headcount | 4 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Customer Support Team | headcount (active employees) | 4 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1006 | name | Oh Minjae |  | db, day fixed: Reply 4: D13
- E-SEL-1006 | department | Customer Support Team | active | db, day 4: Reply 4: D4
- E-SEL-1010 | name | Lim Hajun |  | db, day fixed: Reply 4: D14
- E-SEL-1010 | department | Customer Support Team | active | db, day 12: Reply 4: D5
- E-SEL-1016 | name | Song Yuna |  | db, day fixed: Reply 4: D15
- E-SEL-1016 | department | Customer Support Team | active | db, day -20: Reply 4: D6
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 4: D16
- E-SEL-1019 | department | Customer Support Team | active | db, day 11: Reply 4: D7
- E-SEL-1016 | transfer out — Song Yuna to new dept effective day 15 | not counted in Customer Support Team for planning | approved | history, day 5: Reply 4: H365
- E-SEL-1006 | transfer out — Oh Minjae to Marketing Team effective day 16 | not counted in Customer Support Team for planning | approved | history, day 8: Reply 4: H422
- E-SEL-1005 | transfer in — Han Siwoo from Marketing Team effective day 13 | counted in Customer Support Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-1009 | transfer in — Shin Daeun from Dev Team 1 effective day 13 | counted in Customer Support Team for planning | approved | history, day 9: Reply 4: H477
- Marketing Team | planning headcount | 1 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | headcount (active employees) | 3 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1000 | name | Kim Harin |  | db, day fixed: Reply 4: D17
- E-SEL-1000 | department | Marketing Team | active | db, day -5: Reply 4: D8
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 4: D18
- E-SEL-1005 | department | Marketing Team | active | db, day -1: Reply 4: D9
- E-SEL-2010 | name | Bong Seoha |  | db, day fixed: Reply 4: D19
- E-SEL-2010 | department | Marketing Team | active | db, day 5: Reply 4: D10
- E-SEL-1005 | transfer out — Han Siwoo to Customer Support Team effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H722
- E-SEL-2010 | transfer out — Bong Seoha to Sales Team 2 effective day 13 | not counted in Marketing Team for planning | applied | history, day 13: Reply 4: H725
- Sales Team 1 | planning headcount | 3 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 1 | headcount (active employees) | 2 | active | rule, day fixed: Reply 4: rule: headcount_definition
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 4: D20
- E-SEL-1013 | department | Sales Team 1 | active | db, day 9: Reply 4: D11
- E-SEL-2007 | name | Jegal Yoon |  | db, day fixed: Reply 4: D21
- E-SEL-2007 | department | Sales Team 1 | active | db, day 5: R
[... truncated]
```
### MATCHER CHECK FR-01471 (need FIN-SEL/Customer Support Team/budget_schedule): matcher says **missing**
record text: Customer Support Team capex executing office agreed that TYO finance executes it until day 27.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records do not contain any information about IDE Pro software seats or a general SEL region budget. I only track capex budgets for specific named departments. Without knowing which department would purchase the software, I cannot determine the available budget or number of seats.
[Reply 2] (partial) My area's records do not contain a catalog entry for IDE Pro software seats (no price per seat), and there is no region-level 'SEL' budget line. The seat_purchase_line rule states that seat purchases are charged to the budget of the first team in the request list, but no request list or team was specified. Without the price per seat and the applicable team, I cannot determine how many seats can be purchased.
[Reply 3] (partial) My area's records do not contain a catalog entry for IDE Pro software seats (so the price per seat is unknown), nor a budget line for 'SEL region' as a whole. Budgets exist per department. Per the seat_purchase_line rule, seat purchases are charged to the budget of the first team in the request list, but I do not have that request list. Without the price per seat and the applicable department, I cannot determine how many seats can be purchased.
[Reply 4] (partial) I cannot determine the available budget for purchasing IDE Pro software seats because: (1) no department is specified in the question, so I do not know which budget line to check; (2) no catalog entry for IDE Pro software seats exists in my area's records, so I have no price per seat; (3) without a department and a unit price, I cannot calculate how many seats can be purchased.
- IDE Pro software seats | catalog entry in my area's records | NOT_FOUND |  | db, day unknown: Reply 1: D1
- SEL region | general budget line for SEL region | no such record exists in my area |  | unknown, day unknown: Reply 1: my area's records
- IDE Pro | catalog entry (price per seat) | NOT_FOUND |  | db, day unknown: Reply 2: D1
- software seat | catalog entry | NOT_FOUND |  | db, day unknown: Reply 2: D5
- IDE Pro software seat | catalog entry | NOT_FOUND |  | db, day unknown: Reply 2: D6
- SEL | budget line balance (region-level) | NOT_FOUND |  | db, day unknown: Reply 2: D9
- SEL | catalog entry | NOT_FOUND |  | db, day unknown: Reply 2: D10
- Sales Team 1 | budget_line_balance | 4667771 |  | db, day 12: Reply 2: D2
- Sales Team 1 | pending provisional approvals count | 0 |  | db, day unknown: Reply 2: D4
- Sales Team 1 | earmarks | NO_RECORD |  | history, day 12: Reply 2: H706
- seat_purchase_line | rule | Seat purchases are charged to the budget of the first team in the request list |  | unknown, day unknown: Reply 2: rule:seat_purchase_line
- IDE Pro software seats | price per seat | NOT_FOUND in catalog |  | db, day unknown: Reply 3: D1
- SEL region | budget line balance | NOT_FOUND — budgets are per department, not per region |  | db, day unknown: Reply 3: D6
- seat_purchase_line rule | rule text | Seat purchases are charged to the budget of the first team in the request list |  | unknown, day unknown: Reply 3: rule:seat_purchase_line
- Sales Team 1 | budget line balance | 4667771 |  | db, day 12: Reply 3: D7
- Sales Team 1 | quarterly base allocation | 4780991 |  | db, day -20: Reply 3: D8
- Sales Team 1 | pending provisional approvals | none |  | db, day unknown: Reply 3: D9
- Dev Team 1 | budget line balance | 3974551 |  | history, day 13: Reply 3: H915
- Dev Team 2 | budget line balance | 1791394 |  | history, day 12: Reply 3: H899
- Customer Support Team | budget line balance | 2983974 |  | history, day 12: Reply 3: H905
- IDE Pro software seats | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 4: D1
- IDE Pro software seats | price per seat | NOT_FOUND |  | db, day unknown: Reply 4: D1
missing: IDE Pro software — no catalog entry found in my area's database; Budget available for purchasing IDE Pro software seats in SEL region — no general 'SEL region' budget exists in my area; my area only tracks individual department budgets (Dev Team 1, Dev Team 2, Customer Support Team, Marketing Team, Sales Team 1, Sales Team 2); Number of seats that can be purchased — unknown, as neither the price per seat nor the responsible department is specified; IDE Pro software seat — price per seat / unit cost: no catalog entry exists in my area's database or records; cannot determine how many seats can be purchased; SEL region — available budget for IDE Pro software seats: 'SEL' as a region is not an entity in my area's database; my area holds budget lines only for individual teams/departments, not a regional aggregate; Which team/department the purchase would be charged to: the question does not specify which team is first in the request list; per rule seat_purchase_line, seat purchases are charged to the budget of the first team in the request list; IDE Pro software seats — price per seat: no catalog entry exists in my area's records or database; Which department's budget would be used for the purchase: the question does not specify a department, and 'SEL region' is not a budget entity in my records; per rule seat_purchase_line, seat purchases are charged to the budget of the first team in the request list, but the request list is not in my records; How many seats can be purchased: cannot calculate without knowing the price per seat and which department's budget applies; Department whose budget would be used — not specified in the question; cannot determine without knowing which department is requesting or which team is first in the request list (rule:seat_purchase_line); Price per seat for IDE Pro software — no catalog entry found in my area's database or records; Available budget for an unspecified department — cannot calculate without knowing which department's budget applies
---
[Reply 1] (partial) Customer Support Team's capex balance as of day 13 is 2,983,974 KRW (database, registered day -12). There are two pending provisional approvals (CMT-00072 for 752,098 KRW with expected settle day 11, and CMT-00092 for 545,885 KRW with expected settle day 13), but neither is deducted on day 13 because their deduction ended on day 10 and day 12 respectively (day before settlement). No earmarks are recorded. Therefore the available budget under Art. 4.2 is 2,983,974 KRW.
[Reply 2] (partial) Customer Support Team's budget line balance as of day 13 is 2,983,974 KRW. There are no pending provisional approvals that reduce the available budget today: CMT-00072 was settled on day 11 (per my processing record), and CMT-00092 has settlement day 13 (today), so per Art. 4.2 it is not deducted. Earmarks and items under review are not recorded in my area. Therefore the available budget equals the line balance: 2,983,974 KRW.
[Reply 3] (partial) Customer Support Team's budget line balance as of day 13 is 2,983,974 KRW. The only pending provisional approval in the database is CMT-00072 (752,098 KRW, expected settle day 11) which is past its settlement day so not deducted on day 13. CMT-00092 was pending in the database but I settled it today (day 13); it also had expected settle day 13 so it would not be deducted today regardless. Therefore, available budget equals the balance: 2,983,974 KRW. No earmarks are recorded in my area's records.
[Reply 4] (ok) As of day 13, Customer Support Team's budget line balance is 2,983,974 KRW. There are two pending provisional approvals (CMT-00072: 752,098 KRW expected settle day 11; CMT-00092: 545,885 KRW expected settle day 13), but neither is deducted from available budget on day 13: CMT-00072's settlement day (11) has passed, and CMT-00092 settles today (day 13) so it is not deducted per Art. 4.2. No earmarks are registered. Therefore the full balance of 2,983,974 KRW is available.
- Customer Support Team | capex balance (database, registered day -12) | 2983974 |  | db, day -12: Reply 1: D1
- Customer Support Team | quarterly base allocation | 2606663 |  | db, day -20: Reply 1: D2
- CMT-00072 | provisional approval status | pending | pending | db, day 4: Reply 1: D3
- CMT-00072 | provisional approval amount | 752098 |  | db, day 4: Reply 1: D3
- CMT-00072 | expected settlement day | 11 |  | db, day 4: Reply 1: D3
- CMT-00072 | deducted on day 13 (expected settle day 11, day before = 10, day 13 > 10) | no |  | unknown, day unknown: Reply 1: rule:pending_deduction
- CMT-00092 | provisional approval status | pending | pending | db, day 10: Reply 1: D3
- CMT-00092 | provisional approval amount | 545885 |  | db, day 10: Reply 1: D3
- CMT-00092 | expected settlement day | 13 |  | db, day 10: Reply 1: D3
- CMT-00092 | deducted on day 13 (expected settle day 13, day before = 12, day 13 > 12) | no |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Customer Support Team | earmarks | none in my records |  | history, day 12: Reply 1: H905
- Customer Support Team | available budget as of day 13 (Art. 4.2) | 2983974 |  | unknown, day unknown: Reply 1: rule:pending_deduction
- Customer Support Team | budget line balance (capex
[... truncated]
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

## CASE 69: deepseek-v4-flash · routing · s12 · W-00085 · class C · day 9 · template contract_gate
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
{"stale": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 134}, "partial": {"it_tier": "standard", "contract_tier": "standard", "nda_step": false, "expiry": 182}, "neardup": {"it_tier": "standard", "contract_tier": "premium", "nda_step": false, "expiry": 74}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1019/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1019"}
- DB `HR-TYO/emp/E-TYO-1019/profile` v2 (recorded day 2, registered day 3): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -552, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1019** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1019/contract** (group LEGAL-TYO, class C, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1019/terms` v4 (recorded day -11, registered day -9): {"allowed_tier": "standard", "expiry": 182, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00826 [decision-critical] (operational/exception, day -3, by legal-tyo.a3; DB shows n/a): Equipment exception of Mori Yamato higher tiers including premium allowed until day 11 for a project, legal check done.
- RECORD FR-01364 [decision-critical] (operational/observation, day 9, by legal-tyo.a5; DB shows n/a): NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 182, "it_tier": "standard", "nda_step": false}
official exact match: 1 (4/4 slots)
### MATCHER CHECK FR-00826 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **delivered**
record text: Equipment exception of Mori Yamato higher tiers including premium allowed until day 11 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
[Reply 1] (partial) From my area's database (contract_terms for E-TYO-1019, registered day -9): allowed tier = standard, expiry = 182, nda = true. No legal exception is recorded. Standard equipment requires an NDA check because nda=true and no signed NDA verification is found in my records.
[Reply 2] (ok) For E-TYO-1019 (Mori-san / Mori Yamato): Contract allows standard tier, but an equipment exception (recorded day -3) allows premium until day 11, so premium is the highest tier right now. Contract expiry day is 182. Standard equipment requires an NDA check because the contract has an NDA clause and no verified NDA copy is on record for this employee.
[Reply 3] (partial) E-TYO-1019 (Mori-san/Mori Yamato) has contract terms: allowed_tier=standard, expiry=182, nda=true. The highest tier allowed is standard. No legal exception is recorded. The NDA signed copy verification allowed skipping the NDA check until day 3, but that has expired (today is day 9), so standard equipment now requires an NDA check step.
[Reply 4] (partial) For Mori Yamato (E-TYO-1019): highest allowed tier is 'standard' (no legal exceptions found), contract expires day 182, NDA clause is present. However, the signed NDA copy was verified today (day 9) and allows skipping the NDA check step until day 32, so standard equipment does not require an NDA check step.
[Reply 5] (partial) Employee E-TYO-1019 (Mori Yamato) has a contract with allowed tier 'standard', expiry day 182, NDA required. No legal exceptions are recorded. Standard equipment requires an NDA check because the contract has an NDA clause and there is no record of a verified NDA copy to skip that step.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | highest tier allowed (including legal exception) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda | true |  | db, day -9: Reply 1: D1
- E-TYO-1019 | NDA check required for standard equipment | yes (nda=true, no signed NDA verification found in my records) |  | unknown, day unknown: Reply 1: rule:contractor_policy
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 2: D1
- Mori Yamato | equipment exception - higher tiers including premium allowed | higher tiers including premium allowed until day 11 for a project, legal check done | in effect until day 11 | history, day -3: Reply 2: H61
- E-TYO-1019 | highest tier currently allowed | premium (via exception until day 11) |  | history, day -3: Reply 2: H61
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 2: contractor_policy
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 3: D2
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 3: D2
- E-TYO-1019 | nda | true |  | db, day -9: Reply 3: D2
- E-TYO-1019 | highest tier contract allows | standard |  | db, day -9: Reply 3: D2
- E-TYO-1019 | legal exception affecting allowed tier | none recorded |  | db, day -9: Reply 3: D2
- Mori Yamato | NDA signed copy verified skip | skip until day 3 | expired (today day 9) | history, day -14: Reply 3: H14
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 3: rule: contractor_policy
- E-TYO-1019 (Mori Yamato) | highest allowed tier (contract terms) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | legal exceptions affecting allowed tier | none found in my area's records |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | contract expiry day | 182 |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | NDA required by contract | true |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | signed NDA verification — skip NDA check step until | day 32 | still in effect on day 9 | history, day 9: Reply 4: H229
- E-TYO-1019 (Mori Yamato) | standard equipment NDA check step needed | no — signed NDA verification allows skipping until day 32 (still in effect today, day 9) |  | history, day 9: Reply 4: rule: contractor_policy, H229
- E-TYO-1019 | allowed tier | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | highest tier the contract allows right now | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | legal exceptions affecting allowed tier | none recorded |  | db, day -9: Reply 5: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 5: D1
- E-TYO-1019 | NDA required by contract | true |  | db, day -9: Reply 5: D1
- E-TYO-1019 | standard equipment NDA check requirement | NDA check needed because contract has NDA clause and no verified NDA copy is recorded to skip the check |  | rule, day fixed: Reply 5: contractor_policy
missing: Any legal exception for E-TYO-1019 — not found in my area's records or database; Any signed NDA verification for E-TYO-1019 — not found in my area's records or database; catalog_entry for E-TYO-1019 - no record registered; Any legal exceptions affecting E-TYO-1019's allowed tier — none found in my area's records or database; grade (not in my area's records); employment type 'contractor' (not in my area's records); department Sales Section 1 (not in my area's records); any verified NDA copy for E-TYO-1019 (no record in my area)
---
[Reply 1] (partial) My records show: (1) Equipment exception for Mori Yamato allowing premium until day 11 was recorded on day -3 and is still in effect (day 9 ≤ day 11). There is no conflicting record showing no exception — that information does not exist in my area. (2) No signed NDA verification exists for Mori Yamato/E-TYO-1019 in my records or database. The only NDA verification in my history is for Kimura Yuito. Since the contract requires an NDA (true) and no verified copy is on record, the NDA check step is required for standard equipment.
[Reply 2] (partial) My records show: (1) Equipment exception — No exception allowing premium exists in my area. The database (registered day -9) and the contract change record (day -11) both show allowed tier 'standard'. The claim of an exception allowing premium until day 11 recorded on day -3 is not found anywhere in my area's records. (2) NDA verification — A signed NDA verification was done today (day 9) allowing the NDA check step to be skipped until day 32 (per H229). This is a newer record than the database contract terms (which show nda=true but don't track verification skips). So the correct current status: allowed tier = standard (no premium exception), NDA check step can be skipped until day 32.
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 1: D1
- Mori Yamato | equipment exception - higher tiers including premium allowed | higher tiers including premium allowed until day 11 for a project, legal check done | in effect until day 11 | history, day -3: Reply 1: H61
- E-TYO-1019 | highest tier currently allowed | premium (via exception until day 11) |  | history, day -3: Reply 1: H61
- E-TYO-1019 | standard equipment NDA check required | yes, contract has NDA clause and no verified NDA copy on record |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-1019 | signed NDA verification on record | none found |  | history, day -19: Reply 1: H1-H3
- E-TYO-1019 (Mori Yamato) | allowed tier (contract terms - database) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract terms registered day | -9 |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | NDA required by contract | true |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract change recorded - allowed tier | standard |  | history, day -11: Reply 2: H39
- E-TYO-1019 (Mori Yamato) | contract change recorded - day | -11 |  | history, day -11: Reply 2: H39
- E-TYO-1019 (Mori Yamato) | equipment exception allowing premium until day 11 | no such record exists in my area |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | signed NDA verification - skip NDA check step until | day 32 | still in effect until day 32 | history, day 9: Reply 2: H229
- E-TYO-1019 (Mori Yamato) | signed NDA verification recorded day | 9 |  | history, day 9: Reply 2: H229
missing: E-TYO-1019: any signed NDA verification done today (day 9) allowing skip until day 32 — not found in TYO area records; Equipment exception allowing premium until day 11 for E-TYO-1019 (Mori Yamato) — no such record exists in my area's database or history; the only contract change recorded for Mori Yamato (day -11) set allowed tier to 'standard', not 'premium'
---
[Reply 1] (partial) I have H61 in my records: received day -3, equipment exception of Mori Yamato allowing higher tiers including premium until day 11, legal check done. There is no H229 record in my hist
[... truncated]
```
### MATCHER CHECK FR-01364 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **delivered**
record text: NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32.
What the requester received from LEGAL-TYO during this task:
```
[Reply 1] (partial) From my area's database (contract_terms for E-TYO-1019, registered day -9): allowed tier = standard, expiry = 182, nda = true. No legal exception is recorded. Standard equipment requires an NDA check because nda=true and no signed NDA verification is found in my records.
[Reply 2] (ok) For E-TYO-1019 (Mori-san / Mori Yamato): Contract allows standard tier, but an equipment exception (recorded day -3) allows premium until day 11, so premium is the highest tier right now. Contract expiry day is 182. Standard equipment requires an NDA check because the contract has an NDA clause and no verified NDA copy is on record for this employee.
[Reply 3] (partial) E-TYO-1019 (Mori-san/Mori Yamato) has contract terms: allowed_tier=standard, expiry=182, nda=true. The highest tier allowed is standard. No legal exception is recorded. The NDA signed copy verification allowed skipping the NDA check until day 3, but that has expired (today is day 9), so standard equipment now requires an NDA check step.
[Reply 4] (partial) For Mori Yamato (E-TYO-1019): highest allowed tier is 'standard' (no legal exceptions found), contract expires day 182, NDA clause is present. However, the signed NDA copy was verified today (day 9) and allows skipping the NDA check step until day 32, so standard equipment does not require an NDA check step.
[Reply 5] (partial) Employee E-TYO-1019 (Mori Yamato) has a contract with allowed tier 'standard', expiry day 182, NDA required. No legal exceptions are recorded. Standard equipment requires an NDA check because the contract has an NDA clause and there is no record of a verified NDA copy to skip that step.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | highest tier allowed (including legal exception) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda | true |  | db, day -9: Reply 1: D1
- E-TYO-1019 | NDA check required for standard equipment | yes (nda=true, no signed NDA verification found in my records) |  | unknown, day unknown: Reply 1: rule:contractor_policy
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 2: D1
- Mori Yamato | equipment exception - higher tiers including premium allowed | higher tiers including premium allowed until day 11 for a project, legal check done | in effect until day 11 | history, day -3: Reply 2: H61
- E-TYO-1019 | highest tier currently allowed | premium (via exception until day 11) |  | history, day -3: Reply 2: H61
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 2: contractor_policy
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 3: D2
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 3: D2
- E-TYO-1019 | nda | true |  | db, day -9: Reply 3: D2
- E-TYO-1019 | highest tier contract allows | standard |  | db, day -9: Reply 3: D2
- E-TYO-1019 | legal exception affecting allowed tier | none recorded |  | db, day -9: Reply 3: D2
- Mori Yamato | NDA signed copy verified skip | skip until day 3 | expired (today day 9) | history, day -14: Reply 3: H14
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 3: rule: contractor_policy
- E-TYO-1019 (Mori Yamato) | highest allowed tier (contract terms) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | legal exceptions affecting allowed tier | none found in my area's records |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | contract expiry day | 182 |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | NDA required by contract | true |  | db, day -9: Reply 4: D1
- E-TYO-1019 (Mori Yamato) | signed NDA verification — skip NDA check step until | day 32 | still in effect on day 9 | history, day 9: Reply 4: H229
- E-TYO-1019 (Mori Yamato) | standard equipment NDA check step needed | no — signed NDA verification allows skipping until day 32 (still in effect today, day 9) |  | history, day 9: Reply 4: rule: contractor_policy, H229
- E-TYO-1019 | allowed tier | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | highest tier the contract allows right now | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | legal exceptions affecting allowed tier | none recorded |  | db, day -9: Reply 5: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 5: D1
- E-TYO-1019 | NDA required by contract | true |  | db, day -9: Reply 5: D1
- E-TYO-1019 | standard equipment NDA check requirement | NDA check needed because contract has NDA clause and no verified NDA copy is recorded to skip the check |  | rule, day fixed: Reply 5: contractor_policy
missing: Any legal exception for E-TYO-1019 — not found in my area's records or database; Any signed NDA verification for E-TYO-1019 — not found in my area's records or database; catalog_entry for E-TYO-1019 - no record registered; Any legal exceptions affecting E-TYO-1019's allowed tier — none found in my area's records or database; grade (not in my area's records); employment type 'contractor' (not in my area's records); department Sales Section 1 (not in my area's records); any verified NDA copy for E-TYO-1019 (no record in my area)
---
[Reply 1] (partial) My records show: (1) Equipment exception for Mori Yamato allowing premium until day 11 was recorded on day -3 and is still in effect (day 9 ≤ day 11). There is no conflicting record showing no exception — that information does not exist in my area. (2) No signed NDA verification exists for Mori Yamato/E-TYO-1019 in my records or database. The only NDA verification in my history is for Kimura Yuito. Since the contract requires an NDA (true) and no verified copy is on record, the NDA check step is required for standard equipment.
[Reply 2] (partial) My records show: (1) Equipment exception — No exception allowing premium exists in my area. The database (registered day -9) and the contract change record (day -11) both show allowed tier 'standard'. The claim of an exception allowing premium until day 11 recorded on day -3 is not found anywhere in my area's records. (2) NDA verification — A signed NDA verification was done today (day 9) allowing the NDA check step to be skipped until day 32 (per H229). This is a newer record than the database contract terms (which show nda=true but don't track verification skips). So the correct current status: allowed tier = standard (no premium exception), NDA check step can be skipped until day 32.
- E-TYO-1019 | allowed_tier (contract) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 1: D1
- Mori Yamato | equipment exception - higher tiers including premium allowed | higher tiers including premium allowed until day 11 for a project, legal check done | in effect until day 11 | history, day -3: Reply 1: H61
- E-TYO-1019 | highest tier currently allowed | premium (via exception until day 11) |  | history, day -3: Reply 1: H61
- E-TYO-1019 | standard equipment NDA check required | yes, contract has NDA clause and no verified NDA copy on record |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-1019 | signed NDA verification on record | none found |  | history, day -19: Reply 1: H1-H3
- E-TYO-1019 (Mori Yamato) | allowed tier (contract terms - database) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract terms registered day | -9 |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | NDA required by contract | true |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | contract change recorded - allowed tier | standard |  | history, day -11: Reply 2: H39
- E-TYO-1019 (Mori Yamato) | contract change recorded - day | -11 |  | history, day -11: Reply 2: H39
- E-TYO-1019 (Mori Yamato) | equipment exception allowing premium until day 11 | no such record exists in my area |  | db, day -9: Reply 2: D1
- E-TYO-1019 (Mori Yamato) | signed NDA verification - skip NDA check step until | day 32 | still in effect until day 32 | history, day 9: Reply 2: H229
- E-TYO-1019 (Mori Yamato) | signed NDA verification recorded day | 9 |  | history, day 9: Reply 2: H229
missing: E-TYO-1019: any signed NDA verification done today (day 9) allowing skip until day 32 — not found in TYO area records; Equipment exception allowing premium until day 11 for E-TYO-1019 (Mori Yamato) — no such record exists in my area's database or history; the only contract change recorded for Mori Yamato (day -11) set allowed tier to 'standard', not 'premium'
---
[Reply 1] (partial) I have H61 in my records: received day -3, equipment exception of Mori Yamato allowing higher tiers including premium until day 11, legal check done. There is no H229 record in my hist
[... truncated]
```

## CASE 70: deepseek-v4-flash · routing · s13 · W-00137 · class D · day 14 · template temporal
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
answer: {"budget_dept": "Sales Team 1", "earliest_day": 14}
official exact match: 0 (1/2 slots)
### MATCHER CHECK FR-01737 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **delivered**
record text: Sales Team 1 capex balance adjusted to 1,993,140 KRW (quarter carry-over). Stored value: 1993140
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```
### MATCHER CHECK FR-01224 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **missing**
record text: Sales Team 1 capex 369,909 KRW earmarked for training equipment until day 16 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```
### MATCHER CHECK FR-01260 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **missing**
record text: Sales Team 1 capex 162,433 KRW earmarked for meeting room replacement until day 19 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```
### MATCHER CHECK FR-01615 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **missing**
record text: Sales Team 1 capex 432,093 KRW earmarked for new-hire equipment until day 20 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```
### MATCHER CHECK FR-01573 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **missing**
record text: CMT-00104 Sales Team 1 travel advance provisional approval 691,367 KRW under review, settlement expected day 26.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```
### MATCHER CHECK FR-01616 (need FIN-SEL/Sales Team 1/budget_schedule): matcher says **missing**
record text: CMT-00108 Sales Team 1 laptop provisional approval 268,660 KRW under review, settlement expected day 26.
What the requester received from FIN-SEL during this task:
```
[Reply 1] (partial) My area's records have no information about employee E-SEL-2017 (Haram, Manager). The employee ID is not found in my catalog, and my catalog entries do not link commitments to specific employees. Additionally, no provisional approval with amount 1,951,921 KRW exists in any department in my database.
[Reply 2] (partial) My area's records contain no information about employee E-SEL-2017 (Haram, Manager). The catalog_entry database has no entry for this employee ID or name. My area's provisional approval records are linked to departments, not individual employees, so I cannot identify any CMT ID as being "for" a specific employee.
- E-SEL-2017 | catalog entry | NOT_FOUND in my area's records |  | db, day unknown: Reply 1: D1
- 1,951,921 KRW | provisional approval with this amount | no provisional approval with amount 1,951,921 KRW found in any department in my area's database |  | db, day unknown: Reply 1: D6,D7,D8,D9,D10,D11
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- Haram | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D2
missing: Any provisional approval (CMT-...) for employee E-SEL-2017 (Haram, Manager) — not found: my area's catalog entries do not contain employee/person fields, and E-SEL-2017 is not found in my catalog; no provisional approval with amount 1,951,921 KRW exists in my database; Status of such a provisional approval — cannot determine as none found; Expected settlement day of such a provisional approval — cannot determine as none found; E-SEL-2017 (Haram, Manager) — no record of this employee exists in my area's catalog_entry database; Any provisional approval (CMT-...) for employee E-SEL-2017 — my area's records do not link provisional approvals to individual employees; catalog_entry for provisional approvals only shows department and item type, not the employee; A provisional approval with amount 1,951,921 KRW for a laptop for E-SEL-2017 — cannot be determined from my area's records; Status of any such provisional approval — not found in my area's records; Expected settlement day of any such provisional approval — not found in my area's records
---
[Reply 1] (partial) Employee E-SEL-2017 (Haram, Manager) is not found in my area's records. My area has no rule that determines which department's budget pays for equipment when an employee transfers between departments. Therefore I cannot answer which department's budget would pay in either scenario based solely on my own records and rules.
[Reply 2] (partial)
- E-SEL-2017 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Sales Team 1 | capex balance (database, day 6) | 4636449 |  | db, day 6: Reply 1: D2
- Sales Team 1 | capex balance (adjusted day 14, quarter carry-over) | 1993140 |  | history, day 14: Reply 1: H1197
- Sales Team 2 | capex balance (database, day 11) | 3690872 |  | db, day 11: Reply 1: D3
- E-SEL-2017 | catalog entry | not found in my area's records |  | db, day unknown: Reply 2: D1
- Sales Team 1 | capex balance (budget_line_balance) | 4636449 |  | db, day 6: Reply 2: D2
- Sales Team 2 | capex balance (budget_line_balance) | 3690872 |  | db, day 11: Reply 2: D3
missing: E-SEL-2017 (Haram, Manager) — no record found in my area's database or catalog; Which department's budget pays for equipment provided on day 14 — no rule in my area covers transfers or which department pays for an employee moving between teams; I cannot determine this from my records alone; Which department's budget pays for equipment provided on day 18 or later — same as above; no applicable rule in my area; E-SEL-2017 (Haram, Manager) — no catalog entry exists in my area's records; therefore no information about this employee's department, role, or transfer is available in my area; Approved transfer of E-SEL-2017 from Sales Team 1 to Sales Team 2 effective day 18 — no record of any transfer exists in my area's database or history; Rule determining which department's budget pays for equipment when an employee transfers between departments — my area's rules do not contain such a rule; the seat_purchase_line rule covers seat purchases only, not general equipment
```

## CASE 71: deepseek-v4-flash · routing · s13 · W-00038 · class D · day 4 · template precedence
### Task as given to the requester
We got a request from Chaewon (Senior) for a workstation (premium) at 2,113,553 KRW. Work out the approval route and which rule governs it.
[Request scope] item=workstation; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
### Answer conventions
- Return exactly the listed slots as JSON.
- Amounts, quantities and days are plain integers (no currency, no thousands separators). A day is the simulation day number (e.g. 14).
- IDs (INV-..., Q-..., V-..., A-..., CMT-...) must be copied exactly. Department names must be copied exactly.
- Enum slots must use one of the listed values exactly.
- Use null only where the slot description says so; use false (not null) for a boolean that is simply not triggered.
- A hold, reservation, exclusion, delay or exception recorded as lasting "until day N" is still in effect on day N (inclusive).
- approver: Who must approve the request (finance approver, or 'legal_and_division_head' when a legal exception governs, or 'not_allowed' when the contract forbids it).
- governing_rule: Which rule determined the approver: 'tiers', 'newcomer_waiver', 'q_exception', 'legal_override' or 'contract_deny'.
- it_exception: true if the requested tier is above the tier IT currently allows for this employee, else false.
- Public region list, in order: SEL, TYO.
### Gold answer
{"approver": "legal_and_division_head", "governing_rule": "legal_override", "it_exception": false}
### Counterfactual answers (generator)
{"stale": null, "partial": {"approver": "legal_and_division_head", "governing_rule": "legal_override", "it_exception": true}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1007/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1007"}
- DB `HR-SEL/emp/E-SEL-1007/profile` v1 (recorded day -20, registered day -20): {"dept": "Sales Team 2", "grade": 4, "contract": "contractor", "hire_day": -844, "status": "active"}
**need FIN-SEL/approval** (group FIN-SEL, class None, local=True)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
**need IT-SEL/eligibility/E-SEL-1007** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
- RECORD FR-00525 [decision-critical] (operational/exception, day -11, by it-sel.a3; DB shows n/a): Equipment tier of Yoon Chaewon up to premium allowed until day 7 for work reasons (IT exception approved).
- RULE IT-SEL.tier_exception: {"id": "IT-SEL.tier_exception", "group": "IT-SEL", "title": "Equipment tier exception", "params": {"exception_raises_tier": true}, "text": "An equipment tier exception approved by IT replaces the grade-based default tier during the exception period."}
**need LEGAL-SEL/E-SEL-1007/contract** (group LEGAL-SEL, class D, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1007/terms` v4 (recorded day -4, registered day -1): {"allowed_tier": "standard", "expiry": 184, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00499 [decision-critical] (operational/exception, day -12, by legal-sel.n0002; DB shows n/a): Equipment exception of Yoon Chaewon higher tiers including premium allowed until day 17 for a project, legal check done.
### Model answer and official verdict
answer: {"approver": "legal_and_division_head", "governing_rule": "legal_override", "it_exception": true}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-00525 (need IT-SEL/eligibility/E-SEL-1007): matcher says **missing**
record text: Equipment tier of Yoon Chaewon up to premium allowed until day 7 for work reasons (IT exception approved).
What the requester received from IT-SEL during this task:
```
[Reply 1] (partial) My records show that Yoon Chaewon (E-SEL-1007) has an IT exception on record for premium tier. However, I cannot find the employee's grade in my database, so I cannot confirm their default tier. Since they already have a premium-tier IT exception, the IT-allowed tier would be premium (the exception replaces the grade-based default). A premium workstation (INV-SEL-WSP, cost 2,495,948 KRW) is tier premium, which matches the exception. Inventory quantity is 0.
[Reply 2] (partial) My area's records do not contain E-SEL-1007's grade, so I cannot determine their default tier per the eligibility rule. I also have no record of an IT exception for E-SEL-1007. However, E-SEL-1007 already holds three premium workstations (A-SEL-3456, A-SEL-8659, A-SEL-94234), suggesting a premium-tier entitlement may exist, but that information is not in my area's records.
- E-SEL-1007 | employee ID | E-SEL-1007 |  | db, day unknown: Reply 1: D1
- E-SEL-1007 | catalog entry (grade/name) | not found in my area's database |  | db, day unknown: Reply 1: D1
- Yoon Chaewon (E-SEL-1007) | IT exception on record | premium tier |  | history, day 4: Reply 1: H206
- INV-SEL-WSP | item type | workstation |  | db, day fixed: Reply 1: D5
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 1: D5
- INV-SEL-WSP | cost | 2495948 |  | db, day fixed: Reply 1: D5
- INV-SEL-WSP | region | SEL |  | db, day fixed: Reply 1: D5
- INV-SEL-WSP | inventory quantity | 0 |  | db, day -6: Reply 1: D6
- E-SEL-1007 | assigned assets | A-SEL-3456, A-SEL-8659, A-SEL-94234 |  | db, day unknown: Reply 1: D3
- E-SEL-1007 | catalog_entry | NOT_FOUND |  | db, day unknown: Reply 2: D1
- E-SEL-1007 | assigned assets | A-SEL-3456 (premium workstation), A-SEL-8659 (premium workstation), A-SEL-94234 (premium workstation) |  | db, day unknown: Reply 2: D2
- A-SEL-3456 | tier | premium |  | db, day fixed: Reply 2: D3
- A-SEL-3456 | type | workstation |  | db, day fixed: Reply 2: D3
- A-SEL-8659 | tier | premium |  | db, day fixed: Reply 2: D4
- A-SEL-8659 | type | workstation |  | db, day fixed: Reply 2: D4
- A-SEL-94234 | tier | premium |  | db, day fixed: Reply 2: D5
- A-SEL-94234 | type | workstation |  | db, day fixed: Reply 2: D5
- INV-SEL-WSP | cost (premium workstation) | 2495948 |  | db, day fixed: Reply 2: D7
- INV-SEL-WSP | inventory quantity | 0 |  | db, day -6: Reply 2: D6
- eligibility rule | default tier by grade | grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium; higher tier needs IT exception |  | rule, day fixed: Reply 2: rule: eligibility
- tier_exception rule | IT exception replaces grade-based default | an approved IT exception replaces the grade-based default tier during the exception period |  | rule, day fixed: Reply 2: rule: tier_exception
missing: E-SEL-1007 (Chaewon) - grade (not found in my area's catalog entry database); E-SEL-1007 (Chaewon) - name confirmation (not found in my area's catalog entry database); E-SEL-1007 (Chaewon) - default equipment tier by grade (cannot determine without grade); E-SEL-1007 (Chaewon) grade — not found in my area's records or database; E-SEL-1007 (Chaewon) department — not found in my area's records or database; E-SEL-1007 (Chaewon) current IT-allowed tier — not found in my area's records or database; E-SEL-1007 (Chaewon) IT equipment tier exception — no record found in my area's records or database
---
[Reply 1] (partial) My area's records and database contain no concrete record of an IT exception for E-SEL-1007 (Chaewon). The only mention is in my own answer (H206) where I listed 'Yoon Chaewon' among three premium-tier IT exceptions, but I cannot find the underlying record that would support that statement. No catalog entry exists for E-SEL-1007 or Chaewon in my database.
- E-SEL-1007 | catalog entry | not found in my area's database |  | db, day unknown: Reply 1: D1
- Chaewon | catalog entry | not found in my area's database |  | db, day unknown: Reply 1: D2
- E-SEL-1007 | assigned assets | A-SEL-3456, A-SEL-8659, A-SEL-94234 |  | db, day unknown: Reply 1: D3
- E-SEL-1007 (Chaewon) | premium-tier IT exception on record | no concrete record found in my history or database |  | history, day 4: Reply 1: H206
missing: Any active IT exception for premium tier for E-SEL-1007 (Chaewon) — no concrete record of such an exception exists in my area's records or database
```
### MATCHER CHECK FR-00499 (need LEGAL-SEL/E-SEL-1007/contract): matcher says **missing**
record text: Equipment exception of Yoon Chaewon higher tiers including premium allowed until day 17 for a project, legal check done.
What the requester received from LEGAL-SEL during this task:
```
[Reply 1] (partial) The contract for E-SEL-1007 (Chaewon) allows standard tier equipment with no NDA clause, expiring day 184. The requested premium workstation is above the allowed tier and is premium equipment, so a legal exception (approver legal_and_division_head) is required per contractor_policy. No NDA check is needed. Additionally, since the employee is in Sales Team 2, the data residency rule prohibits using equipment from offshore suppliers — but I cannot determine the supplier's origin from my records.
[Reply 2] (partial) The contract for E-SEL-1007 (Chaewon) allows standard tier only. The requested premium workstation is above the allowed tier, so a legal exception (approver legal_and_division_head) is required per contractor_policy. No NDA check is needed (nda=false). Additionally, Sales Team 2 is restricted from using equipment from offshore suppliers per the residency rule. I have no records of any existing legal exception for this employee.
[Reply 3] (partial) Based on my area's records: E-SEL-1007 (Chaewon) has a contract allowing tier 'standard' (expiry day 184, NDA not required). The requested premium workstation is above the allowed tier, so per contractor_policy a legal exception (approver legal_and_division_head) is needed. Since NDA is false, no NDA check step applies for standard equipment. Additionally, the residency rule states Sales Team 2 may not use equipment from offshore suppliers, but I cannot determine the vendor or whether it is offshore from my records. No contract denial or other legal override was found in my area.
[Reply 4] (partial) The employee E-SEL-1007 (Chaewon) has contract terms: allowed tier standard, expiry day 184, NDA false. The requested premium workstation exceeds the allowed tier, so a legal exception (approver legal_and_division_head) is required per contractor_policy. Additionally, Sales Team 2 is subject to the residency rule restricting offshore suppliers. No catalog entry is registered for this employee. There is no concept of 'contract denial' in my area's rules.
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 1: D2
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 1: D2
- E-SEL-1007 | nda | false |  | db, day -1: Reply 1: D2
- E-SEL-1007 | requested equipment tier | premium |  | unknown, day unknown: Reply 1: question
- E-SEL-1007 | legal override needed | Yes – premium equipment and equipment above the contract's allowed tier (standard) need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 1: contractor_policy
- E-SEL-1007 | NDA check needed | No – contract has no NDA clause (nda=false) and requested equipment is premium, not standard |  | rule, day fixed: Reply 1: contractor_policy
- E-SEL-1007 | department | Sales Team 2 |  | unknown, day unknown: Reply 1: question
- E-SEL-1007 | data residency restriction | Sales Team 2 may not use equipment from offshore suppliers per data residency rule |  | rule, day fixed: Reply 1: residency
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 2: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 2: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 2: D1
- premium workstation | requested tier vs allowed tier | premium (above standard) |  | rule, day fixed: Reply 2: contractor_policy
- premium workstation | legal override needed | yes - premium equipment and equipment above allowed tier need a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 2: contractor_policy
- premium workstation | NDA check needed | no - contract has nda=false |  | rule, day fixed: Reply 2: contractor_policy
- Sales Team 2 | data residency restriction | may not use equipment from offshore suppliers |  | rule, day fixed: Reply 2: residency
- E-SEL-1007 | catalog_entry | no record registered |  | db, day unknown: Reply 2: D2
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 3: D2
- E-SEL-1007 | contract expiry day | 184 |  | db, day -1: Reply 3: D2
- E-SEL-1007 | NDA required | false |  | db, day -1: Reply 3: D2
- E-SEL-1007 | requested item | premium workstation |  | unknown, day unknown: Reply 3: task description
- E-SEL-1007 | item tier vs allowed tier | premium > standard (above allowed tier) |  | db, day -1: Reply 3: D2, task description
- contractor_policy | legal exception needed for premium/above-tier equipment | yes, approver legal_and_division_head |  | rule, day fixed: Reply 3: rule: contractor_policy
- Sales Team 2 | data residency restriction | may not use equipment from offshore suppliers |  | rule, day fixed: Reply 3: rule: residency
- E-SEL-1007 | catalog_entry | NO_RECORD registered |  | db, day unknown: Reply 3: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 4: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 4: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 4: D1
- E-SEL-1007 | requested item | premium workstation |  | unknown, day unknown: Reply 4: task description
- E-SEL-1007 | department | Sales Team 2 |  | unknown, day unknown: Reply 4: task description
- E-SEL-1007 | region | SEL |  | unknown, day unknown: Reply 4: task description
- E-SEL-1007 | legal exception needed | yes, premium equipment and equipment above allowed tier require a legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 4: contractor_policy
- E-SEL-1007 | catalog_entry | NO_RECORD |  | db, day unknown: Reply 4: D2
- Sales Team 2 | offshore supplier restriction | Sales Team 2 may not use equipment from offshore suppliers per residency rule |  | rule, day fixed: Reply 4: residency
missing: Supplier information for the workstation (not in my area's scope); Whether the supplier is offshore (needed to apply data residency rule for Sales Team 2); Catalog entry for E-SEL-1007 (NO_RECORD in database); vendor/supplier for this purchase (to assess data residency and vendor exclusions); any existing legal exception for E-SEL-1007/Chaewon; Vendor/supplier information for the workstation - not in my area's records; Whether the supplier is considered 'offshore' - not in my area's records; E-SEL-1007 department confirmation (catalog_entry not registered) - stated as Sales Team 2 in the request; Whether E-SEL-1007 is a contractor or employee - not determinable from my records; Any contract denial or legal override beyond what is noted above - none found in my records; Any contract denial (no such concept in my area's records or rules); Supplier information (not provided in request; if supplier is offshore, Sales Team 2 is restricted by residency rule); Legal override beyond the legal exception requirement
```

## CASE 72: deepseek-v4-flash · routing · s13 · W-00113 · class D · day 12 · template capacity
### Task as given to the requester
How many in-house laptop (standard) units and CAD seats are actually available right now?
[Request scope] item=laptop; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only; seat lookup regions=the requesting region and the first other region in the public region list (report each separately). Evaluate within the optional review scope stated here.
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
{"stock": 4, "seats": 0, "seats_other_region": 1}
### Counterfactual answers (generator)
{"stale": {"stock": 5, "seats": 0, "seats_other_region": 1}, "partial": {"stock": 5, "seats": 0, "seats_other_region": 1}, "neardup": {"stock": 4, "seats": 0, "seats_other_region": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/stock/INV-TYO-LTS** (group IT-TYO, class A, local=False)
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-LTS"}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-TYO/inv/INV-TYO-LTS/qty` v5 (recorded day 0, registered day 2): 5
- RECORD FR-01345 [decision-critical] (operational/pending_intent, day 7, by it-tyo.w00203; DB shows n/a): In-house stock laptop (standard) 1 unit held as a Dev Section 2 replacement spare until day 15.
**need IT-TYO/license/CAD** (group IT-TYO, class D, local=False)
- DB `IT-TYO/lic/CAD/seats` v4 (recorded day -7, registered day -6): {"seats": 22, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00993 [decision-critical] (operational/pending_intent, day 1, by it-tyo.w00138; DB shows n/a): CAD seats 4 seats reserved for Sales Section 2 project until day 15.
- RECORD FR-01517 [decision-critical] (operational/pending_intent, day 10, by it-tyo.w00238; DB shows n/a): CAD seats 3 seats reserved for Planning Section project until day 24.
**need IT-SEL/license/CAD** (group IT-SEL, class A, local=False)
- DB `IT-SEL/lic/CAD/seats` v9 (recorded day 10, registered day 11): {"seats": 35, "used": 34}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
### Model answer and official verdict
answer: {"seats": 5, "seats_other_region": 1, "stock": 5}
official exact match: 0 (1/3 slots)
### MATCHER CHECK FR-01345 (need IT-TYO/stock/INV-TYO-LTS): matcher says **missing**
record text: In-house stock laptop (standard) 1 unit held as a Dev Section 2 replacement spare until day 15.
What the requester received from IT-TYO during this task:
```
[Reply 1] (ok) Standard laptops (INV-TYO-LTS): 5 units in stock, none held, so 5 available. CAD seats: 22 total, 17 used, so 5 available.
[Reply 2] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). CAD seats available in TYO: 5 (22 total minus 17 used).
[Reply 3] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
[Reply 4] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
- INV-TYO-LTS | inventory_quantity (standard laptop) | 5 |  | db, day 2: Reply 1: D1
- INV-TYO-LTS | available quantity (no holds recorded) | 5 |  | rule, day fixed: Reply 1: rule: hold_policy
- CAD | total license seats | 22 |  | db, day -6: Reply 1: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 1: D2
- CAD | available license seats | 5 |  | db, day -6: Reply 1: D2
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 2: D4
- CAD | total seats | 22 |  | db, day -6: Reply 2: D2
- CAD | used seats | 17 |  | db, day -6: Reply 2: D2
- CAD | available seats (calculated) | 5 |  | rule, day fixed: Reply 2: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 3: D4
- CAD | total license seats | 22 |  | db, day -6: Reply 3: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 3: D2
- CAD | available license seats | 5 |  | rule, day fixed: Reply 3: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | inventory quantity | 5 |  | db, day 2: Reply 4: D4
- CAD | total seats | 22 |  | db, day -6: Reply 4: D2
- CAD | used seats | 17 |  | db, day -6: Reply 4: D2
- CAD | available seats | 5 |  | db, day -6: Reply 4: D2
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 4: D5
```
### MATCHER CHECK FR-00993 (need IT-TYO/license/CAD): matcher says **missing**
record text: CAD seats 4 seats reserved for Sales Section 2 project until day 15.
What the requester received from IT-TYO during this task:
```
[Reply 1] (ok) Standard laptops (INV-TYO-LTS): 5 units in stock, none held, so 5 available. CAD seats: 22 total, 17 used, so 5 available.
[Reply 2] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). CAD seats available in TYO: 5 (22 total minus 17 used).
[Reply 3] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
[Reply 4] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
- INV-TYO-LTS | inventory_quantity (standard laptop) | 5 |  | db, day 2: Reply 1: D1
- INV-TYO-LTS | available quantity (no holds recorded) | 5 |  | rule, day fixed: Reply 1: rule: hold_policy
- CAD | total license seats | 22 |  | db, day -6: Reply 1: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 1: D2
- CAD | available license seats | 5 |  | db, day -6: Reply 1: D2
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 2: D4
- CAD | total seats | 22 |  | db, day -6: Reply 2: D2
- CAD | used seats | 17 |  | db, day -6: Reply 2: D2
- CAD | available seats (calculated) | 5 |  | rule, day fixed: Reply 2: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 3: D4
- CAD | total license seats | 22 |  | db, day -6: Reply 3: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 3: D2
- CAD | available license seats | 5 |  | rule, day fixed: Reply 3: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | inventory quantity | 5 |  | db, day 2: Reply 4: D4
- CAD | total seats | 22 |  | db, day -6: Reply 4: D2
- CAD | used seats | 17 |  | db, day -6: Reply 4: D2
- CAD | available seats | 5 |  | db, day -6: Reply 4: D2
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 4: D5
```
### MATCHER CHECK FR-01517 (need IT-TYO/license/CAD): matcher says **missing**
record text: CAD seats 3 seats reserved for Planning Section project until day 24.
What the requester received from IT-TYO during this task:
```
[Reply 1] (ok) Standard laptops (INV-TYO-LTS): 5 units in stock, none held, so 5 available. CAD seats: 22 total, 17 used, so 5 available.
[Reply 2] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). CAD seats available in TYO: 5 (22 total minus 17 used).
[Reply 3] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
[Reply 4] (ok) Current in-house stock of standard laptops in TYO: 5 units (item INV-TYO-LTS). Available CAD seats in TYO: 5 (22 total minus 17 used).
- INV-TYO-LTS | inventory_quantity (standard laptop) | 5 |  | db, day 2: Reply 1: D1
- INV-TYO-LTS | available quantity (no holds recorded) | 5 |  | rule, day fixed: Reply 1: rule: hold_policy
- CAD | total license seats | 22 |  | db, day -6: Reply 1: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 1: D2
- CAD | available license seats | 5 |  | db, day -6: Reply 1: D2
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 2: D4
- CAD | total seats | 22 |  | db, day -6: Reply 2: D2
- CAD | used seats | 17 |  | db, day -6: Reply 2: D2
- CAD | available seats (calculated) | 5 |  | rule, day fixed: Reply 2: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 2: D5
- INV-TYO-LTS | inventory quantity (standard laptop) | 5 |  | db, day 2: Reply 3: D4
- CAD | total license seats | 22 |  | db, day -6: Reply 3: D2
- CAD | used license seats | 17 |  | db, day -6: Reply 3: D2
- CAD | available license seats | 5 |  | rule, day fixed: Reply 3: rule seat_price
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 3: D6
- INV-TYO-LTS | inventory quantity | 5 |  | db, day 2: Reply 4: D4
- CAD | total seats | 22 |  | db, day -6: Reply 4: D2
- CAD | used seats | 17 |  | db, day -6: Reply 4: D2
- CAD | available seats | 5 |  | db, day -6: Reply 4: D2
- INV-TYO-LTS | item type | laptop |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | tier | standard |  | db, day fixed: Reply 4: D5
- INV-TYO-LTS | region | TYO |  | db, day fixed: Reply 4: D5
```

## CASE 73: deepseek-v4-flash · ingress · s13 · W-00135 · class A · day 14 · template lookup
### Task as given to the requester
Check Haram (Manager)'s current department, grade and assets held.
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
{"dept": "Sales Team 1", "grade": 2, "assets": []}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": {"dept": "Customer Support Team", "grade": 4, "assets": []}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-2017/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2017"}
- DB `HR-SEL/emp/E-SEL-2017/profile` v1 (recorded day 10, registered day 13): {"dept": "Sales Team 1", "grade": 2, "contract": "contractor", "hire_day": 10, "status": "active"}
**need IT-SEL/E-SEL-2017/assets** (group IT-SEL, class A, local=False)
- QUERY SELECT asset WHERE holder=E-SEL-2017 → []
### Model answer and official verdict
answer: {"assets": [], "dept": "Sales Team 1", "grade": 2}
official exact match: 1 (3/3 slots)

## CASE 74: deepseek-v4-flash · ingress · s12 · W-00057 · class A · day 6 · template vendor
### Task as given to the requester
Sales Section 2 needs a workstation. Pick a compliant supplier within budget.
[Request scope] item=workstation; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=included; equipment quote regions=the requesting region and the first other region in the public region list. Evaluate within the optional review scope stated here.
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
{"vendor": "V-TYO-1", "option": "Q-V-TYO-1-WSS", "amount": 911214, "approver": "team_lead", "budget_after": 3364204, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"vendor": "V-SEL-3", "option": "Q-V-SEL-3-WSS", "amount": 1206832, "approver": "division_head", "budget_after": 3068586, "blocked_by": null}, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/Sales Section 2/budget_schedule** (group FIN-TYO, class None, local=True)
- RECORD FR-00374 (operational/exception, day -15, by fin-tyo.a4; DB shows n/a): Sales Section 2 capex executing office agreed that SEL finance executes it until day 9.
- RULE FIN-TYO.owner_exception: {"id": "FIN-TYO.owner_exception", "group": "FIN-TYO", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-SEL/Sales Section 2/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Sales Section 2/remaining` v1 (recorded day -15, registered day -12): 4275418
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-SEL/commit/CMT-00026/status` v2 (recorded day 0, registered day 1): {"status": "settled", "amount": 372012, "expected_settle": 0}
- DB `FIN-SEL/commit/CMT-00037/status` v2 (recorded day -2, registered day 1): {"status": "settled", "amount": 342170, "expected_settle": -2}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Section 2 AND status IN ['reviewing', 'pending'] → []
**need PROC-TYO/quotes/workstation** (group PROC-TYO, class A, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00981 (operational/handover, day 1, by proc-tyo.n0002; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 8 due to a quality issue.
- RECORD FR-00681 (operational/observation, day -6, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-1 delivery notified: deliveries delayed by 5 days until day 6.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-00891 (operational/observation, day -1, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 2 days until day 7.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-00982 (operational/observation, day 1, by proc-tyo.a4; DB shows n/a): Supplier V-TYO-0 delivery notified: deliveries delayed by 3 days until day 8.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01036 (operational/observation, day 2, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 5 days until day 16.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-WSP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- RECORD FR-01104 (db_pending/observation, day 4, by proc-tyo.a2; DB shows 2): Supplier V-TYO-0 lead time change notice applied. Stored value: 8
- DB `PROC-TYO/quote/Q-V-TYO-0-WSP/amount` v1 (recorded day -20, registered day -20): 2092413
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-WSS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day -6, registered day -5): 5
- DB `PROC-TYO/quote/Q-V-TYO-1-WSS/amount` v2 (recorded day -13, registered day -11): 911214
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-WSP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day 3, registered day 6): 5
- DB `PROC-TYO/quote/Q-V-TYO-2-WSP/amount` v1 (recorded day -20, registered day -20): 2436288
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-WSS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day 3, registered day 6): 5
- DB `PROC-TYO/quote/Q-V-TYO-2-WSS/amount` v3 (recorded day -5, registered day -3): 1294985
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-WSP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v3 (recorded day -1, registered day 1): 9
- DB `PROC-TYO/quote/Q-V-TYO-3-WSP/amount` v1 (recorded day -20, registered day -20): 1997101
**need PROC-SEL/quotes/workstation** (group PROC-SEL, class A, local=False)
- RULE PROC-SEL.lead_time_limit: {"id": "PROC-SEL.lead_time_limit", "group": "PROC-SEL", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day 0, registered day 1): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-WSP/amount` v1 (recorded day -20, registered day -20): 2256722
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-0-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-0"}
- DB `PROC-SEL/vendor/V-SEL-0/lead` v2 (recorded day 0, registered day 1): 6
- DB `PROC-SEL/quote/Q-V-SEL-0-WSS/amount` v1 (recorded day -20, registered day -20): 1276284
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v2 (recorded day 4, registered day 5): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-WSP/amount` v1 (recorded day -20, registered day -20): 1761247
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-1-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-1"}
- DB `PROC-SEL/vendor/V-SEL-1/lead` v2 (recorded day 4, registered day 5): 4
- DB `PROC-SEL/quote/Q-V-SEL-1-WSS/amount` v1 (recorded day -20, registered day -20): 1320854
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 11
- DB `PROC-SEL/quote/Q-V-SEL-2-WSP/amount` v1 (recorded day -20, registered day -20): 1965462
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-2-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-2"}
- DB `PROC-SEL/vendor/V-SEL-2/lead` v1 (recorded day -20, registered day -20): 11
- DB `PROC-SEL/quote/Q-V-SEL-2-WSS/amount` v2 (recorded day -12, registered day -10): 1324214
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-WSP"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v2 (recorded day -3, registered day -2): 3
- DB `PROC-SEL/quote/Q-V-SEL-3-WSP/amount` v3 (recorded day -5, registered day -2): 2003070
- CATALOG: {"group": "PROC-SEL", "key": "quotes/Q-V-SEL-3-WSS"}
- CATALOG: {"group": "PROC-SEL", "key": "vendors/V-SEL-3"}
- DB `PROC-SEL/vendor/V-SEL-3/lead` v2 (recorded day -3, registered day -2): 3
- DB `PROC-SEL/quote/Q-V-SEL-3-WSS/amount` v2 (recorded day 3, registered day 6): 1206832
**need LEGAL-TYO/residency** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.residency: {"id": "LEGAL-TYO.residency", "group": "LEGAL-TYO", "title": "Data residency", "params": {"restricted_depts": ["Dev Section 1", "Sales Section 1"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Section 1, Sales Section 1."}
**need FIN-TYO/approval** (group FIN-TYO, class None, local=True)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"amount": 911214, "approver": "team_lead", "blocked_by": null, "budget_after": 741314, "option": "Q-V-TYO-1-WSS", "vendor": "V-TYO-1"}
official exact match: 0 (5/6 slots)

## CASE 75: deepseek-v4-flash · ingress · s14 · W-00080 · class A · day 8 · template temporal
### Task as given to the requester
Equipment for Nakamura-san at 1,475,033 KRW: taking personnel changes into account, which department's budget can pay for it and from which day?
[Request scope] item=monitor; search window=today through 20 days later (inclusive); procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"budget_dept": "Sales Section 1", "earliest_day": 8}
### Counterfactual answers (generator)
{"stale": null, "partial": null, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1008/assignment_timeline** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1008"}
- DB `HR-TYO/emp/E-TYO-1008/profile` v3 (recorded day 2, registered day 4): {"dept": "Sales Section 1", "grade": 4, "contract": "contractor", "hire_day": -52, "status": "active"}
- RULE HR-TYO.transfer_effective_day: {"id": "HR-TYO.transfer_effective_day", "group": "HR-TYO", "title": "Transfer effective day", "params": {"inclusive": true}, "text": "An employee belongs to the new department from the transfer's effective day itself."}
- NEGATIVE: {"query": "HR-TYO memo on an approved, not yet effective transfer: E-TYO-1008", "result": []}
**need FIN-TYO/Sales Section 1/budget_schedule** (group FIN-TYO, class A, local=False)
- RECORD FR-00529 (operational/exception, day -11, by fin-tyo.a5; DB shows n/a): Sales Section 1 capex executing office agreed that SEL finance executes it until day 10.
- RULE FIN-TYO.owner_exception: {"id": "FIN-TYO.owner_exception", "group": "FIN-TYO", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-SEL/Sales Section 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Sales Section 1/remaining` v1 (recorded day -11, registered day -10): 3314201
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-SEL/commit/CMT-00047/status` v2 (recorded day -2, registered day 1): {"status": "settled", "amount": 415424, "expected_settle": -4}
- DB `FIN-SEL/commit/CMT-00048/status` v2 (recorded day 3, registered day 4): {"status": "settled", "amount": 712784, "expected_settle": 3}
- DB `FIN-SEL/commit/CMT-00049/status` v2 (recorded day 2, registered day 3): {"status": "settled", "amount": 469553, "expected_settle": 2}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Sales Section 1 AND status IN ['reviewing', 'pending'] → []
**need FIN-SEL/Sales Section 1/next_reset** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.reset_calendar: {"id": "FIN-SEL.reset_calendar", "group": "FIN-SEL", "title": "Quarterly budget reset", "params": {"days": [16, 46, 76]}, "text": "Line balances are reset to the base allocation on day 16, day 46, day 76."}
- DB `FIN-SEL/line/Sales Section 1/base` v1 (recorded day -11, registered day -10): 3314201
**need PROC-TYO/quotes/monitor** (group PROC-TYO, class A, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01188 (operational/handover, day 4, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-1 exclude from comparisons until day 12 due to a quality issue.
- RECORD FR-01388 (operational/handover, day 8, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 22 due to a quality issue.
- RECORD FR-01152 (operational/observation, day 3, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01239 (operational/observation, day 5, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-1 delivery notified: deliveries delayed by 4 days until day 19.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01241 (operational/observation, day 5, by proc-tyo.a4; DB shows n/a): Supplier V-TYO-0 delivery notified: deliveries delayed by 3 days until day 12.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01329 (operational/observation, day 7, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v2 (recorded day -10, registered day -9): 7
- DB `PROC-TYO/quote/Q-V-TYO-0-MNB/amount` v3 (recorded day -2, registered day 0): 572951
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day 7, registered day 8): 9
- DB `PROC-TYO/quote/Q-V-TYO-1-MNB/amount` v4 (recorded day 6, registered day 8): 706041
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day 7, registered day 8): 9
- DB `PROC-TYO/quote/Q-V-TYO-1-MNS/amount` v3 (recorded day -11, registered day -10): 1044581
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
- DB `PROC-TYO/quote/Q-V-TYO-2-MNB/amount` v2 (recorded day 2, registered day 4): 548426
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-MNS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
- DB `PROC-TYO/quote/Q-V-TYO-2-MNS/amount` v1 (recorded day -20, registered day -20): 1431789
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-MNB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v4 (recorded day -1, registered day 1): 8
- DB `PROC-TYO/quote/Q-V-TYO-3-MNB/amount` v2 (recorded day 3, registered day 4): 828975
### Model answer and official verdict
answer: {"budget_dept": "Sales Section 1", "earliest_day": 8}
official exact match: 1 (2/2 slots)

## CASE 76: deepseek-v4-flash · ingress · s13 · W-00128 · class B · day 13 · template lookup
### Task as given to the requester
Check Yerin (Lead)'s current department, grade and assets held.
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
{"dept": "Marketing Team", "grade": 1, "assets": ["A-SEL-39893", "A-SEL-6133", "A-SEL-89171", "A-SEL-9234", "A-SEL-99055"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Marketing Team", "grade": 2, "assets": ["A-SEL-39893", "A-SEL-6133", "A-SEL-89171", "A-SEL-9234", "A-SEL-99055"]}, "partial": {"dept": "Marketing Team", "grade": 1, "assets": ["A-SEL-39893", "A-SEL-6133", "A-SEL-9234", "A-SEL-99055"]}, "neardup": {"dept": "Sales Team 1", "grade": 1, "assets": ["A-SEL-39893", "A-SEL-6133", "A-SEL-89171", "A-SEL-9234", "A-SEL-99055"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1004/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1004"}
- DB `HR-SEL/emp/E-SEL-1004/profile` v2 (recorded day -10, registered day -8): {"dept": "Marketing Team", "grade": 1, "contract": "regular", "hire_day": -575, "status": "active"}
**need IT-SEL/E-SEL-1004/assets** (group IT-SEL, class B, local=False)
- DB `IT-SEL/asset/A-SEL-39893/holder` v1 (recorded day 5, registered day 8): {"emp": "E-SEL-1004"}
- DB `IT-SEL/asset/A-SEL-6133/holder` v1 (recorded day -20, registered day -20): {"emp": "E-SEL-1004"}
- RECORD FR-01665 [decision-critical] (db_pending/observation, day 13, by it-sel.a2; DB shows ABSENT): A-SEL-89171 laptop Assigned to Jung Yerin. Stored value: {"emp":"E-SEL-1004"}
- DB `IT-SEL/asset/A-SEL-9234/holder` v1 (recorded day -20, registered day -20): {"emp": "E-SEL-1004"}
- DB `IT-SEL/asset/A-SEL-99055/holder` v1 (recorded day -9, registered day -7): {"emp": "E-SEL-1004"}
- QUERY SELECT asset WHERE holder=E-SEL-1004 → ["A-SEL-39893", "A-SEL-6133", "A-SEL-89171", "A-SEL-9234", "A-SEL-99055"]
### Model answer and official verdict
answer: {"assets": ["A-SEL-39893", "A-SEL-6133", "A-SEL-89171", "A-SEL-9234", "A-SEL-99055"], "dept": "Marketing Team", "grade": 1}
official exact match: 1 (3/3 slots)
### MATCHER CHECK FR-01665 (need IT-SEL/E-SEL-1004/assets): matcher says **missing**
record text: A-SEL-89171 laptop Assigned to Jung Yerin. Stored value: {"emp":"E-SEL-1004"}
What the requester received from IT-SEL during this task:
```
Employee E-SEL-1004 (Yerin, Lead) currently holds 5 assets: A-SEL-39893, A-SEL-6133, A-SEL-9234, A-SEL-99055, and A-SEL-89171. [R1] omitted A-SEL-89171 which was assigned on day 13 per [E10].
- E-SEL-1004 | holder of asset | A-SEL-39893 |  | db, day unknown: Reply 1: D1
- E-SEL-1004 | holder of asset | A-SEL-6133 |  | db, day unknown: Reply 1: D1
- E-SEL-1004 | holder of asset | A-SEL-9234 |  | db, day unknown: Reply 1: D1
- E-SEL-1004 | holder of asset | A-SEL-99055 |  | db, day unknown: Reply 1: D1
- E-SEL-1004 | asset ID | A-SEL-39893 |  | db, day unknown: Reply 2: D1
- A-SEL-39893 | type | monitor |  | db, day fixed: Reply 2: D3
- A-SEL-39893 | tier | basic |  | db, day fixed: Reply 2: D3
- E-SEL-1004 | asset ID | A-SEL-6133 |  | db, day unknown: Reply 2: D1
- A-SEL-6133 | type | workstation |  | db, day fixed: Reply 2: D4
- A-SEL-6133 | tier | standard |  | db, day fixed: Reply 2: D4
- E-SEL-1004 | asset ID | A-SEL-9234 |  | db, day unknown: Reply 2: D1
- A-SEL-9234 | type | monitor |  | db, day fixed: Reply 2: D5
- A-SEL-9234 | tier | standard |  | db, day fixed: Reply 2: D5
- E-SEL-1004 | asset ID | A-SEL-99055 |  | db, day unknown: Reply 2: D1
- A-SEL-99055 | type | laptop |  | db, day fixed: Reply 2: D6
- A-SEL-99055 | tier | premium |  | db, day fixed: Reply 2: D6
- E-SEL-1004 | asset ID | A-SEL-89171 |  | history, day 13: Reply 2: H954
- A-SEL-89171 | type | laptop |  | db, day fixed: Reply 2: D7
- A-SEL-89171 | tier | premium |  | db, day fixed: Reply 2: D7
- A-SEL-89171 | type | laptop |  | history, day 13: [E10]
- A-SEL-89171 | tier | premium |  | db, day fixed: [R2]
conflict: Number of assets held by E-SEL-1004: [R1] states 4 assets (A-SEL-39893, A-SEL-6133, A-SEL-9234, A-SEL-99055) while [R2] states 5 assets (those 4 plus A-SEL-89171). Group record [E10] confirms A-SEL-89171 was assigned to Jung Yerin on day 13. (R1 R2 E10)
proposed: Assets held by E-SEL-1004 (Yerin, Lead) = A-SEL-39893, A-SEL-6133, A-SEL-9234, A-SEL-99055, A-SEL-89171 (R2 E1 E2 E3 E5 E10) — [R2] includes A-SEL-89171 from a history record dated day 13, and [E10] confirms the assignment of A-SEL-89171 to Jung Yerin on day 13, making 5 total assets.
```

## CASE 77: deepseek-v4-flash · ingress · s13 · W-00070 · class B · day 7 · template contract_gate
### Task as given to the requester
For Hasegawa-san: the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "basic", "contract_tier": "standard", "nda_step": false, "expiry": 75}
### Counterfactual answers (generator)
{"stale": null, "partial": {"it_tier": "basic", "contract_tier": "standard", "nda_step": true, "expiry": 75}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2014/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2014"}
- DB `HR-TYO/emp/E-TYO-2014/profile` v1 (recorded day 5, registered day 7): {"dept": "Sales Section 1", "grade": 1, "contract": "contractor", "hire_day": 5, "status": "active"}
**need IT-TYO/eligibility/E-TYO-2014** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-2014/contract** (group LEGAL-TYO, class B, local=False)
- DB `LEGAL-TYO/contract/E-TYO-2014/terms` v3 (recorded day 6, registered day 7): {"allowed_tier": "standard", "expiry": 75, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01339 [decision-critical] (operational/observation, day 7, by legal-tyo.a4; DB shows n/a): NDA of Hasegawa Fuka signed copy verified, NDA check step can be skipped until day 34.
### Model answer and official verdict
answer: {"contract_tier": "standard", "expiry": 75, "it_tier": "basic", "nda_step": true}
official exact match: 0 (3/4 slots)
### MATCHER CHECK FR-01339 (need LEGAL-TYO/E-TYO-2014/contract): matcher says **missing**
record text: NDA of Hasegawa Fuka signed copy verified, NDA check step can be skipped until day 34.
What the requester received from LEGAL-TYO during this task:
```
All seven replies consistently report: allowed_tier=standard, expiry=day 75, nda=true, no legal exceptions for higher tiers, and standard equipment requires an NDA check because the contract has an NDA clause (per contractor_policy). The group records [E5] show the contract was initially recorded with allowed_tier=basic on day 6, then changed to standard on the same day [E6][E7]; the database (day 7, D1) reflects the current value of standard. Whether a signed NDA copy has been verified and is still valid is not in TYO area's records.
- E-TYO-2014 | allowed equipment tier | standard |  | db, day 7: Reply 1: D1
- E-TYO-2014 | contract expiry day | 75 |  | db, day 7: Reply 1: D1
- E-TYO-2014 | NDA required | true |  | db, day 7: Reply 1: D1
- E-TYO-2014 | legal exception for higher tier | no record found |  | db, day 7: Reply 1: D1
- E-TYO-2014 | standard equipment NDA check needed | yes, because NDA clause exists per contractor_policy rule |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-2014 | allowed_tier | standard |  | db, day 7: Reply 2: D1
- E-TYO-2014 | expiry | 75 |  | db, day 7: Reply 2: D1
- E-TYO-2014 | nda | true |  | db, day 7: Reply 2: D1
- E-TYO-2014 | catalog_entry | no record registered |  | db, day unknown: Reply 2: D2
- E-TYO-2014 | contract allows equipment tier | standard |  | db, day 7: Reply 2: D1
- E-TYO-2014 | legal exceptions allowing higher tiers | none found in TYO area's records or database |  | db, day unknown: Reply 2: D2
- E-TYO-2014 | contract expiry day | 75 |  | db, day 7: Reply 2: D1
- E-TYO-2014 | standard equipment NDA check needed | yes — contract has NDA clause (nda=true) and no record of verified NDA copy exists in TYO area |  | rule, day fixed: Reply 2: contractor_policy
- E-TYO-2014 | allowed_tier | standard |  | db, day 7: Reply 3: D1
- E-TYO-2014 | expiry | 75 |  | db, day 7: Reply 3: D1
- E-TYO-2014 | nda | true |  | db, day 7: Reply 3: D1
- E-TYO-2014 | highest allowed equipment tier under contract | standard |  | db, day 7: Reply 3: D1
- E-TYO-2014 | legal exceptions allowing higher tiers | none found in my area's records |  | db, day 7: Reply 3: D1
- E-TYO-2014 | contract expiry day | 75 |  | db, day 7: Reply 3: D1
- E-TYO-2014 | standard equipment NDA check required | yes — contract has NDA clause, so standard equipment requires an NDA check step per contractor_policy rule |  | rule, day fixed: Reply 3: rule: contractor_policy
- E-TYO-2014 | previous record - allowed_tier (day 6) | basic |  | history, day 6: Reply 3: H213
- E-TYO-2014 | allowed_tier | standard |  | db, day 7: Reply 4: D1
- E-TYO-2014 | expiry | 75 |  | db, day 7: Reply 4: D1
- E-TYO-2014 | nda | true |  | db, day 7: Reply 4: D1
- E-TYO-2014 | catalog_entry | no record registered |  | db, day unknown: Reply 4: D2
- E-TYO-2014 | contract allows equipment tier | standard |  | db, day 7: Reply 4: D1
- E-TYO-2014 | legal exceptions allowing higher tiers | none found in TYO area records |  | rule, day fixed: Reply 4: rule: contractor_policy
- E-TYO-2014 | standard equipment NDA check needed | yes — contract has NDA clause and no verified signed NDA copy on record |  | rule, day fixed: Reply 4: rule: contractor_policy
- E-TYO-2014 | employment type | contractor |  | unknown, day unknown: Reply 4: task description
- E-TYO-2014 | department | Sales Section 1 |  | unknown, day unknown: Reply 4: task description
- E-TYO-2014 | grade | 1 |  | unknown, day unknown: Reply 4: task description
- E-TYO-2014 | allowed_tier | standard |  | db, day 7: Reply 5: D1
- E-TYO-2014 | expiry | 75 |  | db, day 7: Reply 5: D1
- E-TYO-2014 | nda | true |  | db, day 7: Reply 5: D1
- E-TYO-2014 | standard equipment NDA check required per contractor_policy | NDA check needed because contract has NDA clause (nda=true) |  | rule, day fixed: Reply 5: contractor_policy
- E-TYO-2014 | contract_terms - allowed_tier | standard |  | db, day 7: Reply 6: D1
- E-TYO-2014 | contract_terms - expiry | 75 |  | db, day 7: Reply 6: D1
- E-TYO-2014 | contract_terms - nda | true |  | db, day 7: Reply 6: D1
- E-TYO-2014 | catalog_entry | no record registered |  | db, day unknown: Reply 6: D2
- E-TYO-2014 | contract terms - allowed_tier | standard |  | db, day 7: Reply 7: D1
- E-TYO-2014 | contract terms - expiry | 75 |  | db, day 7: Reply 7: D1
- E-TYO-2014 | contract terms - nda | true |  | db, day 7: Reply 7: D1
- E-TYO-2014 | allowed_tier (initial record, day 6) | basic |  | history, day 6: [E5]
- E-TYO-2014 | allowed_tier (changed to, day 6) | standard |  | history, day 6: [E6]
missing: E-TYO-2014 — whether a signed NDA copy has been verified and is still valid (not in TYO area's records or database)
```

## CASE 78: deepseek-v4-flash · ingress · s14 · W-00096 · class B · day 10 · template plan
### Task as given to the requester
List, in order, the approvals needed before proceeding with a workstation (standard) at 930,993 KRW for Seojun (Assistant Manager).
[Request scope] item=workstation; target supplier=V-SEL-0; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"steps": ["LEGAL_OVERRIDE", "FIN_TEAM_LEAD"]}
### Counterfactual answers (generator)
{"stale": {"steps": ["FIN_TEAM_LEAD"]}, "partial": {"steps": ["BLOCKED_CONTRACT"]}, "neardup": {"steps": ["FIN_TEAM_LEAD"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1002/profile** (group HR-SEL, class None, local=True)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1002"}
- DB `HR-SEL/emp/E-SEL-1002/profile` v3 (recorded day -2, registered day -1): {"dept": "Dev Team 1", "grade": 5, "contract": "contractor", "hire_day": -382, "status": "active"}
**need IT-SEL/eligibility/E-SEL-1002** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-SEL/E-SEL-1002/contract** (group LEGAL-SEL, class B, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1002/terms` v6 (recorded day 7, registered day 8): {"allowed_tier": "basic", "expiry": 86, "nda": false}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00520 [decision-critical] (operational/exception, day -11, by legal-sel.a3; DB shows n/a): Equipment exception of Lee Seojun higher tiers including premium allowed until day 13 for a project, legal check done.
**need FIN-SEL/approval** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.approval_tiers: {"id": "FIN-SEL.approval_tiers", "group": "FIN-SEL", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-SEL.newcomer_waiver: {"id": "FIN-SEL.newcomer_waiver", "group": "FIN-SEL", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"steps": ["FIN_TEAM_LEAD"]}
official exact match: 0 (0/1 slots)
### MATCHER CHECK FR-00520 (need LEGAL-SEL/E-SEL-1002/contract): matcher says **delivered**
record text: Equipment exception of Lee Seojun higher tiers including premium allowed until day 13 for a project, legal check done.
What the requester received from LEGAL-SEL during this task:
```
Contract status: active, expires day 86. The contract (v6, registered day 8) allows basic tier only. A standard workstation exceeds the allowed tier, but an equipment exception [E2] (day -11) already allows higher tiers including premium until day 13 with legal check done, so no additional legal exception is needed. No NDA check is needed because the contract has nda=false. Information about V-SEL-0's supplier agreement is not available in any LEGAL-SEL record.
- E-SEL-1002 | allowed_tier (contract) | basic |  | db, day 8: Reply 1: D1
- E-SEL-1002 | expiry | 86 |  | db, day 8: Reply 1: D1
- E-SEL-1002 | nda | false |  | db, day 8: Reply 1: D1
- E-SEL-1002 | item type requested | workstation |  | unknown, day unknown: Reply 1: question
- E-SEL-1002 | item tier requested | standard |  | unknown, day unknown: Reply 1: question
- E-SEL-1002 | supplier | V-SEL-0 |  | unknown, day unknown: Reply 1: question
- E-SEL-1002 | amount | 930,993 KRW |  | unknown, day unknown: Reply 1: question
- E-SEL-1002 | requested tier exceeds allowed tier | yes (standard > basic) |  | rule, day fixed: Reply 1: rule: contractor_policy
- E-SEL-1002 | legal exception required | equipment above contract's allowed tier needs legal exception (approver legal_and_division_head) |  | rule, day fixed: Reply 1: rule: contractor_policy
- E-SEL-1002 | NDA check needed for standard equipment | no (contract has nda=false) |  | rule, day fixed: Reply 1: rule: contractor_policy
- E-SEL-1002 | contract status | active (expires day 86, today is day 10) |  | db, day 8: Reply 1: D1
- E-SEL-1002 | contract_terms - allowed_tier | basic |  | db, day 8: Reply 2: D1
- E-SEL-1002 | contract_terms - expiry | 86 |  | db, day 8: Reply 2: D1
- E-SEL-1002 | contract_terms - nda required | false |  | db, day 8: Reply 2: D1
- E-SEL-1002 | catalog_entry | no record registered |  | db, day unknown: Reply 2: D2
- E-SEL-1002 | purchase item tier requested | standard |  | unknown, day unknown: Reply 2: task description
- E-SEL-1002 | allowed tier under contract | basic |  | db, day 8: Reply 2: D1
- E-SEL-1002 | standard workstation above allowed tier - legal exception needed | yes (approver: legal_and_division_head) |  | rule, day fixed: Reply 2: contractor_policy
- E-SEL-1002 | NDA check needed | no (contract does not have NDA clause) |  | rule, day fixed: Reply 2: contractor_policy
- E-SEL-1002 | contract status | active (expiry day 86) |  | db, day 8: Reply 2: D1
- E-SEL-1002 | allowed_tier (contract) | basic |  | db, day 8: Reply 3: D1
- E-SEL-1002 | contract expiry day | 86 |  | db, day 8: Reply 3: D1
- E-SEL-1002 | nda required (contract) | false |  | db, day 8: Reply 3: D1
- E-SEL-1002 | purchase item | workstation (standard) |  | unknown, day unknown: Reply 3: task description
- E-SEL-1002 | purchase amount | 930,993 KRW |  | unknown, day unknown: Reply 3: task description
- E-SEL-1002 | supplier | V-SEL-0 |  | unknown, day unknown: Reply 3: task description
- E-SEL-1002 | department | Dev Team 1 |  | unknown, day unknown: Reply 3: task description
- E-SEL-1002 | contract allows standard workstation | no — contract allows basic tier; standard is above basic |  | db, day 8: Reply 3: D1
- E-SEL-1002 | override needed for standard equipment | yes — equipment above contract's allowed tier needs legal exception (approver legal_and_division_head) per contractor_policy |  | rule, day fixed: Reply 3: rule: contractor_policy
- E-SEL-1002 | NDA check needed | no — contract has no NDA clause (nda: false) |  | db, day 8: Reply 3: D1
- E-SEL-1002 | contract status | active (expiry day 86, today is day 10) |  | db, day 8: Reply 3: D1
- E-SEL-1002 | contract allowed tier | basic |  | db, day 8: Reply 4: D1
- E-SEL-1002 | contract expiry day | 86 |  | db, day 8: Reply 4: D1
- E-SEL-1002 | NDA required | false |  | db, day 8: Reply 4: D1
- E-SEL-1002 | standard workstation purchase allowed by contract | no (contract allows basic; standard is above basic) |  | db, day 8: Reply 4: D1, contractor_policy
- E-SEL-1002 | legal exception needed for standard equipment (above allowed tier) | yes |  | rule, day fixed: Reply 4: contractor_policy
- E-SEL-1002 | NDA check step needed | no (nda: false) |  | db, day 8: Reply 4: D1, contractor_policy
- E-SEL-1002 | contract status | active (expiry day 86, today is day 10) |  | db, day 8: Reply 4: D1
- V-SEL-0 | catalog entry | NOT_FOUND |  | db, day unknown: Reply 5: D1
- E-SEL-1002 | contract allowed tier | basic |  | db, day 8: Reply 5: D2
- E-SEL-1002 | contract expiry day | 86 |  | db, day 8: Reply 5: D2
- E-SEL-1002 | contract NDA required | false |  | db, day 8: Reply 5: D2
- E-SEL-1002 | catalog entry | NO_RECORD |  | db, day unknown: Reply 5: D3
- E-SEL-1002 | contract_terms - allowed_tier | basic |  | db, day 8: Reply 6: D1
- E-SEL-1002 | contract_terms - expiry | 86 |  | db, day 8: Reply 6: D1
- E-SEL-1002 | contract_terms - nda required | false |  | db, day 8: Reply 6: D1
- E-SEL-1002 | purchase item tier requested | standard |  | unknown, day unknown: Reply 6: task description
- E-SEL-1002 | allowed tier under contract | basic |  | db, day 8: Reply 6: D1
- E-SEL-1002 | purchase allowed under contract | No - standard tier exceeds allowed_tier (basic) |  | rule, day fixed: Reply 6: contractor_policy
- E-SEL-1002 | required action for equipment above allowed tier | legal exception needed (approver: legal_and_division_head) |  | rule, day fixed: Reply 6: contractor_policy
- V-SEL-0 | catalog_entry | not found in my area's records |  | db, day unknown: Reply 6: D2
- E-SEL-1002 | contract_terms - allowed_tier (earlier version, extension record day 3) | standard |  | history, day 3: Reply 6: H93
- V-SEL-0 | supplier agreement / contract details | not found in my area's records |  | db, day unknown: Reply 7: D3
- V-SEL-0 | whether supplier agreement allows purchasing a standard workstation | not found in my area's records |  | db, day unknown: Reply 7: D3
- E-SEL-1002 | contract allowed tier (database, day 8) | basic |  | db, day 8: Reply 7: D1
- E-SEL-1002 | contract NDA required (database, day 8) | false |  | db, day 8: Reply 7: D1
- E-SEL-1002 | contract expiry | 86 |  | db, day 8: Reply 7: D1
- E-SEL-1002 | allowed_tier (contract) | basic |  | db, day 8: Reply 8: D1
- E-SEL-1002 | expiry | 86 |  | db, day 8: Reply 8: D1
- E-SEL-1002 | nda | false |  | db, day 8: Reply 8: D1
- E-SEL-1002 | equipment exception | higher tiers including premium allowed until day 13 for a project, legal check done | in effect (day 10 ≤ day 13) | history, day -11: [E2]
- E-SEL-1002 | signed NDA verified | verified, NDA check step can be skipped until day 28 | skip until day 28 | history, day 4: [E6]
missing: V-SEL-0 contract details — whether the supplier agreement allows purchasing a standard workstation; no reply or group record contains information about supplier V-SEL-0
conflict: E-SEL-1002 legal exception existence: All replies (R1–R8) state that no legal exception is recorded for E-SEL-1002, but group record [E2] (day -11) records an equipment exception allowing higher tiers including premium until day 13 with legal check done, which is still in effect (day 10 ≤ day 13). ([R1] [R2] [R3] [R4] [R5] [R6] [R7] [R8] [E2])
proposed: E-SEL-1002 legal exception needed for standard workstation = No additional legal exception needed — the equipment exception [E2] (higher tiers including premium allowed until day 13, legal check done) already covers the requested standard workstation (which is below premium) and is still in effect (today day 10 ≤ day 13). ([E2]) — The equipment exception recorded on day -11 allows higher tiers including premium until day 13 with legal check done, so a standard workstation (below premium) is covered and no new legal exception is required.
proposed: E-SEL-1002 NDA check needed = No NDA check needed ([V6] [R1] [R2] [R3] [R4] [R5] [R6] [R7] [R8]) — The latest database version v6 (registered day 8) shows nda=false, and per contractor_policy, standard equipment only requires an NDA check if the contract has an NDA clause.
```