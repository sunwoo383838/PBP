## CASE 79: deepseek-v4-flash · ingress · s12 · W-00142 · class C · day 15 · template contract_gate
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
answer: {"contract_tier": "premium", "expiry": 182, "it_tier": "standard", "nda_step": false}
official exact match: 1 (4/4 slots)
### MATCHER CHECK FR-01530 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **delivered**
record text: Equipment exception of Mori Yamato higher tiers including premium allowed until day 32 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
Using database v4 (LEGAL-TYO/contract/E-TYO-1019/terms v4, registered day -9). The contract terms are allowed_tier=standard, expiry=182, nda=true. An equipment exception [E19] (day 12) allows premium until day 32, so the highest tier allowed right now is premium. The signed NDA was verified on day 9 [E14] with skip until day 32, so standard equipment does NOT currently require an NDA check step. Contract expiry is day 182.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda | true |  | db, day -9: Reply 1: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 2: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 2: contractor_policy
- E-TYO-1019 | allowed_tier (contract terms) | standard |  | db, day -9: Reply 3: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 3: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 3: D1
- E-TYO-1019 (Mori Yamato) | equipment exception - higher tiers including premium allowed | Equipment exception of Mori Yamato higher tiers including premium allowed until … for a project, le… |  | history, day 12: Reply 3: H228
- E-TYO-1019 | highest equipment tier allowed (with exception) | premium |  | history, day 12: Reply 3: H228
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 3: contractor_policy
- E-TYO-1019 | allowed_tier (contract terms) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 | expiry (contract terms) | 182 |  | db, day -9: Reply 4: D1
- E-TYO-1019 | nda (contract terms) | true |  | db, day -9: Reply 4: D1
- E-TYO-1019 | highest equipment tier allowed under contract (including legal exceptions) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 | rule: contractor_policy - standard equipment with NDA clause requires NDA check | NDA check required unless NDA verified and still valid |  | rule, day fixed: Reply 4: rule: contractor_policy
- E-TYO-1019 | does standard equipment currently require an NDA check step? | yes |  | db, day -9: Reply 4: D1, rule: contractor_policy
- E-TYO-1019 | allowed equipment tier (contract) | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | legal exceptions | none recorded |  | db, day -9: Reply 5: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 5: D1
- E-TYO-1019 | NDA clause present | true |  | db, day -9: Reply 5: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 5: rule: contractor_policy
- E-TYO-1019 | verified NDA copy on file | no record found |  | db, day -9: Reply 5: D1
- E-TYO-1019 | equipment exception - higher tiers including premium allowed | Equipment exception of Mori Yamato higher tiers including premium allowed until day 32 for a project, legal check done. | until day 32 | history, day 12: [E19]
- E-TYO-1019 | signed NDA verification | NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32. | skipped until day 32 | history, day 9: [E14]
conflict: highest equipment tier allowed (including legal exceptions): R1, R2, R4, R5 say 'standard' but R3 says 'premium'. Group record [E19] (day 12) shows an equipment exception allowing premium until day 32, which is in effect today (day 15). ([R1] [R2] [R3] [R4] [R5] [E19])
conflict: standard equipment requires NDA check step: R1, R2, R4, R5 say 'yes' (NDA check required) but R3 says 'no' (skipped until day 32). Group record [E14] (day 9) shows NDA verified with skip until day 32, which is still in effect today (day 15). ([R1] [R2] [R3] [R4] [R5] [E14])
proposed: highest equipment tier allowed (including legal exceptions) = premium ([E19] [V4]) — The contract terms (v4) allow standard tier, but equipment exception [E19] (day 12) allows premium until day 32, and today is day 15 so the exception is in effect.
proposed: standard equipment requires NDA check step = no — NDA check step skipped until day 32 ([E14] [V4]) — The contract has nda=true, but the signed NDA was verified on day 9 ([E14]) with skip until day 32, and per contractor_policy a verified and still-valid NDA skips the NDA check step.
proposed: contract expiry day = 182 ([V4] [E4]) — Database v4 (registered day -9) and all replies agree on expiry=182.
```
### MATCHER CHECK FR-01364 (need LEGAL-TYO/E-TYO-1019/contract): matcher says **delivered**
record text: NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32.
What the requester received from LEGAL-TYO during this task:
```
Using database v4 (LEGAL-TYO/contract/E-TYO-1019/terms v4, registered day -9). The contract terms are allowed_tier=standard, expiry=182, nda=true. An equipment exception [E19] (day 12) allows premium until day 32, so the highest tier allowed right now is premium. The signed NDA was verified on day 9 [E14] with skip until day 32, so standard equipment does NOT currently require an NDA check step. Contract expiry is day 182.
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | expiry | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | nda | true |  | db, day -9: Reply 1: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 1: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 1: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 1: contractor_policy
- E-TYO-1019 | allowed_tier | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 2: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 2: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 2: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 2: contractor_policy
- E-TYO-1019 | allowed_tier (contract terms) | standard |  | db, day -9: Reply 3: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 3: D1
- E-TYO-1019 | nda required | true |  | db, day -9: Reply 3: D1
- E-TYO-1019 (Mori Yamato) | equipment exception - higher tiers including premium allowed | Equipment exception of Mori Yamato higher tiers including premium allowed until … for a project, le… |  | history, day 12: Reply 3: H228
- E-TYO-1019 | highest equipment tier allowed (with exception) | premium |  | history, day 12: Reply 3: H228
- E-TYO-1019 | standard equipment NDA check required | yes |  | rule, day fixed: Reply 3: contractor_policy
- E-TYO-1019 | allowed_tier (contract terms) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 | expiry (contract terms) | 182 |  | db, day -9: Reply 4: D1
- E-TYO-1019 | nda (contract terms) | true |  | db, day -9: Reply 4: D1
- E-TYO-1019 | highest equipment tier allowed under contract (including legal exceptions) | standard |  | db, day -9: Reply 4: D1
- E-TYO-1019 | rule: contractor_policy - standard equipment with NDA clause requires NDA check | NDA check required unless NDA verified and still valid |  | rule, day fixed: Reply 4: rule: contractor_policy
- E-TYO-1019 | does standard equipment currently require an NDA check step? | yes |  | db, day -9: Reply 4: D1, rule: contractor_policy
- E-TYO-1019 | allowed equipment tier (contract) | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | highest equipment tier allowed (including legal exceptions) | standard |  | db, day -9: Reply 5: D1
- E-TYO-1019 | legal exceptions | none recorded |  | db, day -9: Reply 5: D1
- E-TYO-1019 | contract expiry day | 182 |  | db, day -9: Reply 5: D1
- E-TYO-1019 | NDA clause present | true |  | db, day -9: Reply 5: D1
- E-TYO-1019 | standard equipment requires NDA check step | yes |  | rule, day fixed: Reply 5: rule: contractor_policy
- E-TYO-1019 | verified NDA copy on file | no record found |  | db, day -9: Reply 5: D1
- E-TYO-1019 | equipment exception - higher tiers including premium allowed | Equipment exception of Mori Yamato higher tiers including premium allowed until day 32 for a project, legal check done. | until day 32 | history, day 12: [E19]
- E-TYO-1019 | signed NDA verification | NDA of Mori Yamato signed copy verified, NDA check step can be skipped until day 32. | skipped until day 32 | history, day 9: [E14]
conflict: highest equipment tier allowed (including legal exceptions): R1, R2, R4, R5 say 'standard' but R3 says 'premium'. Group record [E19] (day 12) shows an equipment exception allowing premium until day 32, which is in effect today (day 15). ([R1] [R2] [R3] [R4] [R5] [E19])
conflict: standard equipment requires NDA check step: R1, R2, R4, R5 say 'yes' (NDA check required) but R3 says 'no' (skipped until day 32). Group record [E14] (day 9) shows NDA verified with skip until day 32, which is still in effect today (day 15). ([R1] [R2] [R3] [R4] [R5] [E14])
proposed: highest equipment tier allowed (including legal exceptions) = premium ([E19] [V4]) — The contract terms (v4) allow standard tier, but equipment exception [E19] (day 12) allows premium until day 32, and today is day 15 so the exception is in effect.
proposed: standard equipment requires NDA check step = no — NDA check step skipped until day 32 ([E14] [V4]) — The contract has nda=true, but the signed NDA was verified on day 9 ([E14]) with skip until day 32, and per contractor_policy a verified and still-valid NDA skips the NDA check step.
proposed: contract expiry day = 182 ([V4] [E4]) — Database v4 (registered day -9) and all replies agree on expiry=182.
```

## CASE 80: deepseek-v4-flash · ingress · s13 · W-00021 · class C · day 3 · template vendor
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
answer: {"amount": 480948, "approver": "team_lead", "blocked_by": null, "budget_after": 1116424, "option": "Q-V-SEL-0-LTB", "vendor": "V-SEL-0"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-00683 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: Sales Team 2 capex 467,805 KRW earmarked for training equipment until day 7 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
Database version used: FIN-SEL/line/Sales Team 2/remaining v5 (registered day -3). Available budget for Sales Team 2 as of day 3 = 1,597,372 KRW. Deductions: CMT-00059 (632,153 KRW, pending, deducted until day 4), training equipment earmark (467,805 KRW, active until day 7), quarter-end consumables earmark (462,318 KRW, active until day 14). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and not deducted. No quarterly spending control applies. Approval thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above that.
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D2
- Sales Team 2 | earmark - quarter-end consumables | 462318 | active until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | provisional approval / under review - CMT-00059 | 632153 | pending, expected settle day 5 | history, day 0: Reply 1: H130
- Sales Team 2 | available budget (calculated) | 2065177 |  | rule, day fixed: Reply 1: pending_deduction
- Sales Team 2 | approval tiers - up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | newcomer waiver - equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead instead |  | rule, day fixed: Reply 1: newcomer_waiver
- Sales Team 2 | quarterly budget reset dates | day 16, day 46, day 76 |  | rule, day fixed: Reply 1: reset_calendar
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- Sales Team 2 | available budget (calculated) | 3159648 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for pending/under-review provisional approvals | 0 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for earmarks in validity period | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | approval tiers (spending amount thresholds) | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above: cfo |  | unknown, day unknown: Reply 2: rule:approval_tiers
- Sales Team 2 | quarterly spending control status | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | training equipment earmark amount | 467805 | active until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | training equipment earmark validity | until day 7 | active until day 7 | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available budget (balance minus deductions) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | approval threshold: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 4: D5
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 4: D6
- CMT-00059 | provisional approval amount (pending) | 632153 | pending | history, day 2: Reply 4: H302
- CMT-00059 | expected settlement day | 5 | pending | history, day 2: Reply 4: H302
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D7
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- Sales Team 2 | available budget calculation | Available budget = line balance (3,159,648) − pending provisional approvals (632,153) = 2,527,495 KRW |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | deduction: CMT-00059 (pending, expected settle day 5, today day 3 ≤ day 4, so deducted) | 632153 | pending | history, day 2: Reply 4: H302
- Sales Team 2 | approval tiers rule | Up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | unknown, day unknown: Reply 4: rule:approval_tiers
- Sales Team 2 | quarterly budget reset schedule | Line balances reset to base allocation on day 16, day 46, day 76 |  | unknown, day unknown: Reply 4: rule:reset_calendar
- Sales Team 2 | newcomer waiver rule | Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead |  | unknown, day unknown: Reply 4: rule:newcomer_waiver
- Sales Team 2 | quarterly spending control rule | For a department under quarterly spending control, items above threshold need division_head approval |  | unknown, day unknown: Reply 4: rule:q_exception_approver
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 5: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 5: D2
- Sales Team 2 | provisional approval CMT-00002 | 349589 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00005 | 584884 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00010 | 254702 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | catalog entry | no record registered |  | db, day unknown: Reply 5: D4
- Sales Team 2 | available budget (line balance minus deductions) | 3159648 |  | rule, day fixed: Reply 5: pending_deduction
- Sales Team 2 | approval tier: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | newcomer waiver: equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead |  | rule, day fixed: Reply 5: newcomer_waiver
- Sales Team 2 | quarterly spending control status | not found in my area's records |  | db, day -3: Reply 5: D1
- CMT-00061 | provisional approval status | not found in database or any records |  | db, day unknown: Reply 6: D4
- CMT-00061 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D6
- CMT-00065 | provisional approval status | not found in database; only informal meeting memo suggesting cancellation (undecided) |  | db, day unknown: Reply 6: D5
- CMT-00065 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D7
- CMT-00065 | meeting memo content | someone suggested cancelling it (not decided) |  | history, day 2: Reply 6: H324
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 6: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 6: D2
- Sales Team 2 | registered provisional approvals | CMT-00002 (settled), CMT-00005 (settled), CMT-00010 (settled) — no others |  | db, day unknown: Reply 6: D3
- Sa
[... truncated]
```
### MATCHER CHECK FR-00904 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: Sales Team 2 capex 462,318 KRW earmarked for quarter-end consumables until day 14 (no voucher yet).
What the requester received from FIN-SEL during this task:
```
Database version used: FIN-SEL/line/Sales Team 2/remaining v5 (registered day -3). Available budget for Sales Team 2 as of day 3 = 1,597,372 KRW. Deductions: CMT-00059 (632,153 KRW, pending, deducted until day 4), training equipment earmark (467,805 KRW, active until day 7), quarter-end consumables earmark (462,318 KRW, active until day 14). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and not deducted. No quarterly spending control applies. Approval thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above that.
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D2
- Sales Team 2 | earmark - quarter-end consumables | 462318 | active until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | provisional approval / under review - CMT-00059 | 632153 | pending, expected settle day 5 | history, day 0: Reply 1: H130
- Sales Team 2 | available budget (calculated) | 2065177 |  | rule, day fixed: Reply 1: pending_deduction
- Sales Team 2 | approval tiers - up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | newcomer waiver - equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead instead |  | rule, day fixed: Reply 1: newcomer_waiver
- Sales Team 2 | quarterly budget reset dates | day 16, day 46, day 76 |  | rule, day fixed: Reply 1: reset_calendar
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- Sales Team 2 | available budget (calculated) | 3159648 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for pending/under-review provisional approvals | 0 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for earmarks in validity period | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | approval tiers (spending amount thresholds) | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above: cfo |  | unknown, day unknown: Reply 2: rule:approval_tiers
- Sales Team 2 | quarterly spending control status | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | training equipment earmark amount | 467805 | active until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | training equipment earmark validity | until day 7 | active until day 7 | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available budget (balance minus deductions) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | approval threshold: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 4: D5
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 4: D6
- CMT-00059 | provisional approval amount (pending) | 632153 | pending | history, day 2: Reply 4: H302
- CMT-00059 | expected settlement day | 5 | pending | history, day 2: Reply 4: H302
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D7
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- Sales Team 2 | available budget calculation | Available budget = line balance (3,159,648) − pending provisional approvals (632,153) = 2,527,495 KRW |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | deduction: CMT-00059 (pending, expected settle day 5, today day 3 ≤ day 4, so deducted) | 632153 | pending | history, day 2: Reply 4: H302
- Sales Team 2 | approval tiers rule | Up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | unknown, day unknown: Reply 4: rule:approval_tiers
- Sales Team 2 | quarterly budget reset schedule | Line balances reset to base allocation on day 16, day 46, day 76 |  | unknown, day unknown: Reply 4: rule:reset_calendar
- Sales Team 2 | newcomer waiver rule | Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead |  | unknown, day unknown: Reply 4: rule:newcomer_waiver
- Sales Team 2 | quarterly spending control rule | For a department under quarterly spending control, items above threshold need division_head approval |  | unknown, day unknown: Reply 4: rule:q_exception_approver
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 5: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 5: D2
- Sales Team 2 | provisional approval CMT-00002 | 349589 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00005 | 584884 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00010 | 254702 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | catalog entry | no record registered |  | db, day unknown: Reply 5: D4
- Sales Team 2 | available budget (line balance minus deductions) | 3159648 |  | rule, day fixed: Reply 5: pending_deduction
- Sales Team 2 | approval tier: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | newcomer waiver: equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead |  | rule, day fixed: Reply 5: newcomer_waiver
- Sales Team 2 | quarterly spending control status | not found in my area's records |  | db, day -3: Reply 5: D1
- CMT-00061 | provisional approval status | not found in database or any records |  | db, day unknown: Reply 6: D4
- CMT-00061 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D6
- CMT-00065 | provisional approval status | not found in database; only informal meeting memo suggesting cancellation (undecided) |  | db, day unknown: Reply 6: D5
- CMT-00065 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D7
- CMT-00065 | meeting memo content | someone suggested cancelling it (not decided) |  | history, day 2: Reply 6: H324
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 6: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 6: D2
- Sales Team 2 | registered provisional approvals | CMT-00002 (settled), CMT-00005 (settled), CMT-00010 (settled) — no others |  | db, day unknown: Reply 6: D3
- Sa
[... truncated]
```
### MATCHER CHECK FR-01046 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **delivered**
record text: CMT-00059 Sales Team 2 provisional approval 632,153 KRW confirmed, settlement expected day 5. Stored value: {"amount":632153,"expected_settle":5,"status":"pending"}
What the requester received from FIN-SEL during this task:
```
Database version used: FIN-SEL/line/Sales Team 2/remaining v5 (registered day -3). Available budget for Sales Team 2 as of day 3 = 1,597,372 KRW. Deductions: CMT-00059 (632,153 KRW, pending, deducted until day 4), training equipment earmark (467,805 KRW, active until day 7), quarter-end consumables earmark (462,318 KRW, active until day 14). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and not deducted. No quarterly spending control applies. Approval thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above that.
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D2
- Sales Team 2 | earmark - quarter-end consumables | 462318 | active until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | provisional approval / under review - CMT-00059 | 632153 | pending, expected settle day 5 | history, day 0: Reply 1: H130
- Sales Team 2 | available budget (calculated) | 2065177 |  | rule, day fixed: Reply 1: pending_deduction
- Sales Team 2 | approval tiers - up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | newcomer waiver - equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead instead |  | rule, day fixed: Reply 1: newcomer_waiver
- Sales Team 2 | quarterly budget reset dates | day 16, day 46, day 76 |  | rule, day fixed: Reply 1: reset_calendar
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- Sales Team 2 | available budget (calculated) | 3159648 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for pending/under-review provisional approvals | 0 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for earmarks in validity period | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | approval tiers (spending amount thresholds) | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above: cfo |  | unknown, day unknown: Reply 2: rule:approval_tiers
- Sales Team 2 | quarterly spending control status | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | training equipment earmark amount | 467805 | active until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | training equipment earmark validity | until day 7 | active until day 7 | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available budget (balance minus deductions) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | approval threshold: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 4: D5
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 4: D6
- CMT-00059 | provisional approval amount (pending) | 632153 | pending | history, day 2: Reply 4: H302
- CMT-00059 | expected settlement day | 5 | pending | history, day 2: Reply 4: H302
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D7
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- Sales Team 2 | available budget calculation | Available budget = line balance (3,159,648) − pending provisional approvals (632,153) = 2,527,495 KRW |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | deduction: CMT-00059 (pending, expected settle day 5, today day 3 ≤ day 4, so deducted) | 632153 | pending | history, day 2: Reply 4: H302
- Sales Team 2 | approval tiers rule | Up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | unknown, day unknown: Reply 4: rule:approval_tiers
- Sales Team 2 | quarterly budget reset schedule | Line balances reset to base allocation on day 16, day 46, day 76 |  | unknown, day unknown: Reply 4: rule:reset_calendar
- Sales Team 2 | newcomer waiver rule | Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead |  | unknown, day unknown: Reply 4: rule:newcomer_waiver
- Sales Team 2 | quarterly spending control rule | For a department under quarterly spending control, items above threshold need division_head approval |  | unknown, day unknown: Reply 4: rule:q_exception_approver
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 5: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 5: D2
- Sales Team 2 | provisional approval CMT-00002 | 349589 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00005 | 584884 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00010 | 254702 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | catalog entry | no record registered |  | db, day unknown: Reply 5: D4
- Sales Team 2 | available budget (line balance minus deductions) | 3159648 |  | rule, day fixed: Reply 5: pending_deduction
- Sales Team 2 | approval tier: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | newcomer waiver: equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead |  | rule, day fixed: Reply 5: newcomer_waiver
- Sales Team 2 | quarterly spending control status | not found in my area's records |  | db, day -3: Reply 5: D1
- CMT-00061 | provisional approval status | not found in database or any records |  | db, day unknown: Reply 6: D4
- CMT-00061 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D6
- CMT-00065 | provisional approval status | not found in database; only informal meeting memo suggesting cancellation (undecided) |  | db, day unknown: Reply 6: D5
- CMT-00065 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D7
- CMT-00065 | meeting memo content | someone suggested cancelling it (not decided) |  | history, day 2: Reply 6: H324
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 6: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 6: D2
- Sales Team 2 | registered provisional approvals | CMT-00002 (settled), CMT-00005 (settled), CMT-00010 (settled) — no others |  | db, day unknown: Reply 6: D3
- Sa
[... truncated]
```
### MATCHER CHECK FR-00957 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00061 Sales Team 2 meeting room equipment provisional approval 448,322 KRW under review, settlement expected day 8.
What the requester received from FIN-SEL during this task:
```
Database version used: FIN-SEL/line/Sales Team 2/remaining v5 (registered day -3). Available budget for Sales Team 2 as of day 3 = 1,597,372 KRW. Deductions: CMT-00059 (632,153 KRW, pending, deducted until day 4), training equipment earmark (467,805 KRW, active until day 7), quarter-end consumables earmark (462,318 KRW, active until day 14). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and not deducted. No quarterly spending control applies. Approval thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above that.
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D2
- Sales Team 2 | earmark - quarter-end consumables | 462318 | active until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | provisional approval / under review - CMT-00059 | 632153 | pending, expected settle day 5 | history, day 0: Reply 1: H130
- Sales Team 2 | available budget (calculated) | 2065177 |  | rule, day fixed: Reply 1: pending_deduction
- Sales Team 2 | approval tiers - up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | newcomer waiver - equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead instead |  | rule, day fixed: Reply 1: newcomer_waiver
- Sales Team 2 | quarterly budget reset dates | day 16, day 46, day 76 |  | rule, day fixed: Reply 1: reset_calendar
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- Sales Team 2 | available budget (calculated) | 3159648 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for pending/under-review provisional approvals | 0 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for earmarks in validity period | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | approval tiers (spending amount thresholds) | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above: cfo |  | unknown, day unknown: Reply 2: rule:approval_tiers
- Sales Team 2 | quarterly spending control status | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | training equipment earmark amount | 467805 | active until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | training equipment earmark validity | until day 7 | active until day 7 | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available budget (balance minus deductions) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | approval threshold: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 4: D5
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 4: D6
- CMT-00059 | provisional approval amount (pending) | 632153 | pending | history, day 2: Reply 4: H302
- CMT-00059 | expected settlement day | 5 | pending | history, day 2: Reply 4: H302
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D7
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- Sales Team 2 | available budget calculation | Available budget = line balance (3,159,648) − pending provisional approvals (632,153) = 2,527,495 KRW |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | deduction: CMT-00059 (pending, expected settle day 5, today day 3 ≤ day 4, so deducted) | 632153 | pending | history, day 2: Reply 4: H302
- Sales Team 2 | approval tiers rule | Up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | unknown, day unknown: Reply 4: rule:approval_tiers
- Sales Team 2 | quarterly budget reset schedule | Line balances reset to base allocation on day 16, day 46, day 76 |  | unknown, day unknown: Reply 4: rule:reset_calendar
- Sales Team 2 | newcomer waiver rule | Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead |  | unknown, day unknown: Reply 4: rule:newcomer_waiver
- Sales Team 2 | quarterly spending control rule | For a department under quarterly spending control, items above threshold need division_head approval |  | unknown, day unknown: Reply 4: rule:q_exception_approver
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 5: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 5: D2
- Sales Team 2 | provisional approval CMT-00002 | 349589 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00005 | 584884 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00010 | 254702 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | catalog entry | no record registered |  | db, day unknown: Reply 5: D4
- Sales Team 2 | available budget (line balance minus deductions) | 3159648 |  | rule, day fixed: Reply 5: pending_deduction
- Sales Team 2 | approval tier: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | newcomer waiver: equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead |  | rule, day fixed: Reply 5: newcomer_waiver
- Sales Team 2 | quarterly spending control status | not found in my area's records |  | db, day -3: Reply 5: D1
- CMT-00061 | provisional approval status | not found in database or any records |  | db, day unknown: Reply 6: D4
- CMT-00061 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D6
- CMT-00065 | provisional approval status | not found in database; only informal meeting memo suggesting cancellation (undecided) |  | db, day unknown: Reply 6: D5
- CMT-00065 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D7
- CMT-00065 | meeting memo content | someone suggested cancelling it (not decided) |  | history, day 2: Reply 6: H324
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 6: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 6: D2
- Sales Team 2 | registered provisional approvals | CMT-00002 (settled), CMT-00005 (settled), CMT-00010 (settled) — no others |  | db, day unknown: Reply 6: D3
- Sa
[... truncated]
```
### MATCHER CHECK FR-01018 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **missing**
record text: CMT-00065 Sales Team 2 order (incl. shipping) provisional approval (order of W-00001) 487,593 KRW under review, settlement expected day 6.
What the requester received from FIN-SEL during this task:
```
Database version used: FIN-SEL/line/Sales Team 2/remaining v5 (registered day -3). Available budget for Sales Team 2 as of day 3 = 1,597,372 KRW. Deductions: CMT-00059 (632,153 KRW, pending, deducted until day 4), training equipment earmark (467,805 KRW, active until day 7), quarter-end consumables earmark (462,318 KRW, active until day 14). All three registered provisional approvals (CMT-00002, CMT-00005, CMT-00010) are settled and not deducted. No quarterly spending control applies. Approval thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above that.
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 1: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 1: D2
- Sales Team 2 | earmark - quarter-end consumables | 462318 | active until day 14 | history, day -1: Reply 1: H127
- Sales Team 2 | provisional approval / under review - CMT-00059 | 632153 | pending, expected settle day 5 | history, day 0: Reply 1: H130
- Sales Team 2 | available budget (calculated) | 2065177 |  | rule, day fixed: Reply 1: pending_deduction
- Sales Team 2 | approval tiers - up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | approval tiers - above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 1: approval_tiers
- Sales Team 2 | newcomer waiver - equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead instead |  | rule, day fixed: Reply 1: newcomer_waiver
- Sales Team 2 | quarterly budget reset dates | day 16, day 46, day 76 |  | rule, day fixed: Reply 1: reset_calendar
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 2: D1
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 2: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 2: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 2: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 2: D3
- Sales Team 2 | available budget (calculated) | 3159648 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for pending/under-review provisional approvals | 0 |  | unknown, day unknown: Reply 2: rule:pending_deduction
- Sales Team 2 | deduction for earmarks in validity period | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | approval tiers (spending amount thresholds) | up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above: cfo |  | unknown, day unknown: Reply 2: rule:approval_tiers
- Sales Team 2 | quarterly spending control status | not in my area's records |  | unknown, day unknown: Reply 2: 
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 3: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 3: D2
- Sales Team 2 | training equipment earmark amount | 467805 | active until day 7 | history, day -7: Reply 3: H30
- Sales Team 2 | training equipment earmark validity | until day 7 | active until day 7 | history, day -7: Reply 3: H30
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 3: D3
- CMT-00002 | provisional approval amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected settlement day | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00005 | provisional approval amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 3: D3
- CMT-00010 | provisional approval amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected settlement day | -10 | settled | db, day -8: Reply 3: D3
- Sales Team 2 | available budget (balance minus deductions) | 2691843 |  | rule, day fixed: Reply 3: pending_deduction
- Sales Team 2 | approval threshold: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | approval threshold: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 3: approval_tiers
- Sales Team 2 | budget line balance (remaining capex) | 3159648 |  | db, day -3: Reply 4: D5
- Sales Team 2 | budget line base (quarterly base allocation) | 2683779 |  | db, day -20: Reply 4: D6
- CMT-00059 | provisional approval amount (pending) | 632153 | pending | history, day 2: Reply 4: H302
- CMT-00059 | expected settlement day | 5 | pending | history, day 2: Reply 4: H302
- CMT-00002 | provisional approval status | settled | settled | db, day -7: Reply 4: D7
- CMT-00005 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- CMT-00010 | provisional approval status | settled | settled | db, day -8: Reply 4: D7
- Sales Team 2 | available budget calculation | Available budget = line balance (3,159,648) − pending provisional approvals (632,153) = 2,527,495 KRW |  | unknown, day unknown: Reply 4: rule:pending_deduction
- Sales Team 2 | deduction: CMT-00059 (pending, expected settle day 5, today day 3 ≤ day 4, so deducted) | 632153 | pending | history, day 2: Reply 4: H302
- Sales Team 2 | approval tiers rule | Up to 1,000,000 KRW: team_lead; up to 2,500,000 KRW: division_head; above that: cfo |  | unknown, day unknown: Reply 4: rule:approval_tiers
- Sales Team 2 | quarterly budget reset schedule | Line balances reset to base allocation on day 16, day 46, day 76 |  | unknown, day unknown: Reply 4: rule:reset_calendar
- Sales Team 2 | newcomer waiver rule | Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead |  | unknown, day unknown: Reply 4: rule:newcomer_waiver
- Sales Team 2 | quarterly spending control rule | For a department under quarterly spending control, items above threshold need division_head approval |  | unknown, day unknown: Reply 4: rule:q_exception_approver
- Sales Team 2 | budget line balance | 3159648 |  | db, day -3: Reply 5: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 5: D2
- Sales Team 2 | provisional approval CMT-00002 | 349589 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00005 | 584884 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | provisional approval CMT-00010 | 254702 | settled | db, day unknown: Reply 5: D3
- Sales Team 2 | catalog entry | no record registered |  | db, day unknown: Reply 5: D4
- Sales Team 2 | available budget (line balance minus deductions) | 3159648 |  | rule, day fixed: Reply 5: pending_deduction
- Sales Team 2 | approval tier: up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | approval tier: above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 5: approval_tiers
- Sales Team 2 | newcomer waiver: equipment <= 1,500,000 KRW within 30 days of joining | approved by team_lead |  | rule, day fixed: Reply 5: newcomer_waiver
- Sales Team 2 | quarterly spending control status | not found in my area's records |  | db, day -3: Reply 5: D1
- CMT-00061 | provisional approval status | not found in database or any records |  | db, day unknown: Reply 6: D4
- CMT-00061 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D6
- CMT-00065 | provisional approval status | not found in database; only informal meeting memo suggesting cancellation (undecided) |  | db, day unknown: Reply 6: D5
- CMT-00065 | catalog entry | not found in database or any records |  | db, day unknown: Reply 6: D7
- CMT-00065 | meeting memo content | someone suggested cancelling it (not decided) |  | history, day 2: Reply 6: H324
- Sales Team 2 | current capex balance (database) | 3159648 |  | db, day -3: Reply 6: D1
- Sales Team 2 | quarterly base allocation | 2683779 |  | db, day -20: Reply 6: D2
- Sales Team 2 | registered provisional approvals | CMT-00002 (settled), CMT-00005 (settled), CMT-00010 (settled) — no others |  | db, day unknown: Reply 6: D3
- Sa
[... truncated]
```

## CASE 81: deepseek-v4-flash · ingress · s12 · W-00112 · class C · day 12 · template alloc
### Task as given to the requester
Allocate Design Suite seats to Dev Team 2, Marketing Team, Sales Team 2 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
[Request scope] procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"alloc": [6, 2, 1], "transfer": 0, "buy": 9, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [7, 2, 1], "transfer": 0, "buy": 10, "unmet": 0}, "partial": {"alloc": [7, 2, 1], "transfer": 0, "buy": 10, "unmet": 0}, "neardup": {"alloc": [2, 2, 1], "transfer": 0, "buy": 5, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/license/Design Suite** (group IT-SEL, class None, local=True)
- DB `IT-SEL/lic/Design Suite/seats` v8 (recorded day 8, registered day 10): {"seats": 29, "used": 27}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01294 (operational/pending_intent, day 7, by it-sel.a4; DB shows n/a): Design Suite seats 3 seats reserved for Dev Team 1 project until day 14.
- RECORD FR-01360 (operational/pending_intent, day 9, by it-sel.a5; DB shows n/a): Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 22.
- RECORD FR-01437 (operational/pending_intent, day 10, by it-sel.a2; DB shows n/a): Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 23.
**need LEGAL-SEL/sw_contractor/Design Suite** (group LEGAL-SEL, class A, local=False)
- RULE LEGAL-SEL.sw_contractor: {"id": "LEGAL-SEL.sw_contractor", "group": "LEGAL-SEL", "title": "Contractor software restriction", "params": {"blocked": ["CAD", "Design Suite"]}, "text": "Contractors are not assigned seats of these software products: CAD, Design Suite."}
**need HR-SEL/Dev Team 2/planning_headcount-regular** (group HR-SEL, class C, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-01456 (db_pending/rationale, day 10, by hr-sel.a5; DB shows 4): HR record of Lee Seojun changed to grade 5 (review result), Dev Team 2. Stored value: {"contract":"regular","dept":"Dev Team 2","grade":5,"hire_day":-454,"status":"active"}
- DB `HR-SEL/emp/E-SEL-1003/profile` v2 (recorded day -18, registered day -17): {"dept": "Dev Team 2", "grade": 4, "contract": "regular", "hire_day": -856, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1004/profile` v3 (recorded day 6, registered day 8): {"dept": "Marketing Team", "grade": 1, "contract": "regular", "hire_day": -644, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1005/profile` v4 (recorded day 0, registered day 2): {"dept": "Dev Team 2", "grade": 1, "contract": "regular", "hire_day": -582, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1010/profile` v4 (recorded day 7, registered day 8): {"dept": "Dev Team 2", "grade": 3, "contract": "regular", "hire_day": -648, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1012/profile` v4 (recorded day 5, registered day 6): {"dept": "Dev Team 2", "grade": 1, "contract": "regular", "hire_day": -486, "status": "active"}
- RECORD FR-01278 [decision-critical] (operational/pending_intent, day 7, by hr-sel.a5; DB shows n/a): Transfer of Cho Eunho approved from Dev Team 2 to Sales Team 1, effective day 18 (stays in Dev Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1013/profile` v3 (recorded day 7, registered day 9): {"dept": "Customer Support Team", "grade": 1, "contract": "regular", "hire_day": -372, "status": "active"}
- RECORD FR-01200 [decision-critical] (operational/pending_intent, day 6, by hr-sel.a1; DB shows n/a): Transfer of Pyo Jisung approved from Sales Team 1 to Dev Team 2, effective day 17 (stays in Sales Team 1 until then).
- DB `HR-SEL/emp/E-SEL-2003/profile` v4 (recorded day 8, registered day 10): {"dept": "Dev Team 2", "grade": 2, "contract": "regular", "hire_day": -14, "status": "active"}
- RECORD FR-01011 [decision-critical] (operational/pending_intent, day 2, by hr-sel.a5; DB shows n/a): Transfer of Jegal Yoon approved from Dev Team 2 to Dev Team 1, effective day 14 (stays in Dev Team 2 until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Dev Team 2 AND status=active AND contract=regular) → 7
**need HR-SEL/Marketing Team/planning_headcount-regular** (group HR-SEL, class A, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1004/profile` v3 (recorded day 6, registered day 8): {"dept": "Marketing Team", "grade": 1, "contract": "regular", "hire_day": -644, "status": "active"}
- DB `HR-SEL/emp/E-SEL-2003/profile` v4 (recorded day 8, registered day 10): {"dept": "Dev Team 2", "grade": 2, "contract": "regular", "hire_day": -14, "status": "active"}
- NEGATIVE: {"query": "HR-SEL Marketing Team memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=SEL AND dept=Marketing Team AND status=active AND contract=regular) → 2
**need HR-SEL/Sales Team 2/planning_headcount-regular** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1010/profile` v4 (recorded day 7, registered day 8): {"dept": "Dev Team 2", "grade": 3, "contract": "regular", "hire_day": -648, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1012/profile` v4 (recorded day 5, registered day 6): {"dept": "Dev Team 2", "grade": 1, "contract": "regular", "hire_day": -486, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1018/profile` v2 (recorded day -16, registered day -15): {"dept": "Sales Team 2", "grade": 5, "contract": "regular", "hire_day": -640, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v2 (recorded day 2, registered day 3): {"dept": "Sales Team 1", "grade": 2, "contract": "regular", "hire_day": -15, "status": "active"}
- RECORD FR-01472 [decision-critical] (db_pending/observation, day 11, by hr-sel.a5; DB shows 2): HR record of Mo Seoyun moved from Sales Team 1 to Sales Team 2, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":1,"hire_day":3,"status":"active"}
- NEGATIVE: {"query": "HR-SEL Sales Team 2 memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=SEL AND dept=Sales Team 2 AND status=active AND contract=regular) → 1
**need IT-TYO/license/Design Suite** (group IT-TYO, class A, local=False)
- DB `IT-TYO/lic/Design Suite/seats` v5 (recorded day 8, registered day 10): {"seats": 38, "used": 37}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need IT-SEL/rule/seat_transfer_share** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_transfer_share: {"id": "IT-SEL.seat_transfer_share", "group": "IT-SEL", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-SEL/rule/seat_purchase_line** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.seat_purchase_line: {"id": "FIN-SEL.seat_purchase_line", "group": "FIN-SEL", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-SEL/Dev Team 2/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 2/remaining` v1 (recorded day -20, registered day -20): 2515374
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00945 (operational/pending_intent, day 1, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 152,194 KRW earmarked for meeting room replacement until day 12 (no voucher yet).
- RECORD FR-01185 (operational/pending_intent, day 5, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 327,724 KRW earmarked for meeting room replacement until day 14 (no voucher yet).
- RECORD FR-01354 (operational/pending_intent, day 8, by fin-sel.a1; DB shows n/a): Dev Team 2 capex 150,145 KRW earmarked for training equipment until day 16 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00044/status` v2 (recorded day 1, registered day 2): {"status": "settled", "amount": 541440, "expected_settle": 1}
- RECORD FR-01432 (db_pending/observation, day 10, by fin-sel.a3; DB shows 1): CMT-00045 Dev Team 2 provisional approval settled. Stored value: {"amount":572995,"expected_settle":10,"status":"settled"}
- DB `FIN-SEL/commit/CMT-00064/status` v2 (recorded day 11, registered day 12): {"status": "settled", "amount": 777887, "expected_settle": 11}
- RECORD FR-01422 (operational/pending_intent, day 10, by fin-sel.a3; DB shows n/a): CMT-00097 Dev Team 2 travel advance provisional approval 462,354 KRW under review, settlement expected day 24.
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 2 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00945", "earmark:FR-01185", "earmark:FR-01354", "CMT-00083", "CMT-00097"]
**need PROC-SEL/seat_price/Design Suite** (group PROC-SEL, class A, local=False)
- DB `PROC-SEL/seatprice/Design Suite/amount` v1 (recorded day -20, registered day -20): 118222
### Model answer and official verdict
answer: {"alloc": [10, 1, 3], "buy": 12, "transfer": 0, "unmet": 0}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-01278 (need HR-SEL/Dev Team 2/planning_headcount-regular): matcher says **missing**
record text: Transfer of Cho Eunho approved from Dev Team 2 to Sales Team 1, effective day 18 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
The replies all give planning headcounts of Dev Team 2=8, Marketing Team=2, Sales Team 2=2, but group records show discrepancies: E-SEL-1004 (Jung Yerin) was transferred to Dev Team 2 on day -3 per [E3] (replies still count her in Marketing Team), E-SEL-1013 (Kang Seoa) is active in Dev Team 2 per [E7], and Mo Seoyun was transferred to Sales Team 2 on day 11 per [E5]. Proposed corrected planning headcounts: Dev Team 2=10, Marketing Team=1, Sales Team 2=3. Design Suite seat allocation info is not held in any HR-SEL record.
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 1: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 1: planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 1: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 1: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 1: D3
- Dev Team 2 | planning headcount | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | history, day 10: Reply 2: H487-H490
- Dev Team 2 | Design Suite seats planned | 8 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Sales Team 2 | planning headcount | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 2: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 2: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 2: D3
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 3: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 4: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 4: D1
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 4: D2
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 4: D3
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 5: D8
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 5: D1
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 5: D9
- Mo Seoyun (E-SEL-2013) | current department (database) | Sales Team 1 |  | db, day 7: Reply 5: D3
- Mo Seoyun (E-SEL-2013) | employment status | active |  | db, day 7: Reply 5: D3
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: Reply 6: D1
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: Reply 6: D2
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: Reply 6: D3
- Pi Jaewon | name | Pi Jaewon |  | db, day fixed: Reply 6: D1
- Pi Jaewon | alias | Jaewon (Manager) |  | db, day fixed: Reply 6: D1
- Pi Jaewon | current department | Marketing Team | active | db, day 12: Reply 6: D4
- Pi Jaewon | hire day | 7 |  | db, day 12: Reply 6: D4
- Cho Eunho19 | name | Cho Eunho19 |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | alias | Eunho19 (Senior) |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | current department | Dev Team 2 | active | db, day 12: Reply 6: D5
- Cho Eunho19 | hire day | 11 |  | db, day 12: Reply 6: D5
- Mo Seoyun | name | Mo Seoyun |  | db, day fixed: Reply 6: D3
- Mo Seoyun | alias | Seoyun (Manager) |  | db, day fixed: Reply 6: D3
- Mo Seoyun | current department (database) | Sales Team 1 | active | db, day 7: Reply 6: D6
- Mo Seoyun | hire day | 3 |  | db, day 7: Reply 6: D6
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 7: D1
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 7: D2
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 7: D3
- E-SEL-1004 | department | Dev Team 2 | active | history, day -3: [E3]
- E-SEL-1004 | transfer | moved from Marketing Team to Dev Team 2 | applied day -3 | history, day -3: [E3]
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: [R5]
- Pi Jaewon | onboarding | joined Marketing Team, grade 2, regular | active | history, day 7: [E4]
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: [R5]
- Cho Eunho19 | onboarding | joined Dev Team 2, grade 2, contractor | active | history, day 11: [E6]
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: [R5]
- Mo Seoyun | transfer | moved from Sales Team 1 to Sales Team 2, grade 1, regular | applied day 11 | history, day 11: [E5]
missing: Design Suite seat allocation or assignment information — not held in any HR-SEL record (all seven replies confirm this is outside their area)
conflict: E-SEL-1004 (Jung Yerin) department: All four main replies (R1, R2, R3, R4) list E-SEL-1004 as an active employee of Marketing Team, but group record [E3] (day -3) shows she was transferred from Marketing Team to Dev Team 2 on day -3 and her stored department is Dev Team 2. ([R1] [R2] [R3] [R4] [E3])
conflict: Dev Team 2 active employee count: Replies R1/R2/R3/R4 list 8 active employees for Dev Team 2, omitting E-SEL-1004 (Jung Yerin) who was transferred to Dev Team 2 per [E3], and also omitting E-SEL-1013 (Kang Seoa) who was shown as active in Dev Team 2 in the day-2 database query in [E7]. ([R1] [R2] [R3] [R4] [E3] [E7])
conflict: Marketing Team active employee count: Replies R1/R2/R3/R4 count 2 active employees for Marketing Team including E-SEL-1004, but [E3] shows E-SEL-1004 was transferred to Dev Team 2 on day -3, leaving only E-SEL-2016 (Pi Jaewon) as a confirmed active employee in Marketing Team. ([R1] [R2] [R3] [R4] [E3])
conflict: Sales Team 2 active employee count: Replies R1/R2/R3/R4 list 2 active employees for Sales Team 2 (E-SEL-1006, E-SEL-2010), but [E5] (day 11) shows Mo Seoyun (E-SEL-2013) was transferred from Sales Team 1 to Sales Team 2 effective 
[... truncated]
```
### MATCHER CHECK FR-01200 (need HR-SEL/Dev Team 2/planning_headcount-regular): matcher says **missing**
record text: Transfer of Pyo Jisung approved from Sales Team 1 to Dev Team 2, effective day 17 (stays in Sales Team 1 until then).
What the requester received from HR-SEL during this task:
```
The replies all give planning headcounts of Dev Team 2=8, Marketing Team=2, Sales Team 2=2, but group records show discrepancies: E-SEL-1004 (Jung Yerin) was transferred to Dev Team 2 on day -3 per [E3] (replies still count her in Marketing Team), E-SEL-1013 (Kang Seoa) is active in Dev Team 2 per [E7], and Mo Seoyun was transferred to Sales Team 2 on day 11 per [E5]. Proposed corrected planning headcounts: Dev Team 2=10, Marketing Team=1, Sales Team 2=3. Design Suite seat allocation info is not held in any HR-SEL record.
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 1: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 1: planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 1: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 1: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 1: D3
- Dev Team 2 | planning headcount | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | history, day 10: Reply 2: H487-H490
- Dev Team 2 | Design Suite seats planned | 8 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Sales Team 2 | planning headcount | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 2: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 2: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 2: D3
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 3: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 4: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 4: D1
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 4: D2
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 4: D3
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 5: D8
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 5: D1
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 5: D9
- Mo Seoyun (E-SEL-2013) | current department (database) | Sales Team 1 |  | db, day 7: Reply 5: D3
- Mo Seoyun (E-SEL-2013) | employment status | active |  | db, day 7: Reply 5: D3
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: Reply 6: D1
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: Reply 6: D2
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: Reply 6: D3
- Pi Jaewon | name | Pi Jaewon |  | db, day fixed: Reply 6: D1
- Pi Jaewon | alias | Jaewon (Manager) |  | db, day fixed: Reply 6: D1
- Pi Jaewon | current department | Marketing Team | active | db, day 12: Reply 6: D4
- Pi Jaewon | hire day | 7 |  | db, day 12: Reply 6: D4
- Cho Eunho19 | name | Cho Eunho19 |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | alias | Eunho19 (Senior) |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | current department | Dev Team 2 | active | db, day 12: Reply 6: D5
- Cho Eunho19 | hire day | 11 |  | db, day 12: Reply 6: D5
- Mo Seoyun | name | Mo Seoyun |  | db, day fixed: Reply 6: D3
- Mo Seoyun | alias | Seoyun (Manager) |  | db, day fixed: Reply 6: D3
- Mo Seoyun | current department (database) | Sales Team 1 | active | db, day 7: Reply 6: D6
- Mo Seoyun | hire day | 3 |  | db, day 7: Reply 6: D6
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 7: D1
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 7: D2
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 7: D3
- E-SEL-1004 | department | Dev Team 2 | active | history, day -3: [E3]
- E-SEL-1004 | transfer | moved from Marketing Team to Dev Team 2 | applied day -3 | history, day -3: [E3]
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: [R5]
- Pi Jaewon | onboarding | joined Marketing Team, grade 2, regular | active | history, day 7: [E4]
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: [R5]
- Cho Eunho19 | onboarding | joined Dev Team 2, grade 2, contractor | active | history, day 11: [E6]
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: [R5]
- Mo Seoyun | transfer | moved from Sales Team 1 to Sales Team 2, grade 1, regular | applied day 11 | history, day 11: [E5]
missing: Design Suite seat allocation or assignment information — not held in any HR-SEL record (all seven replies confirm this is outside their area)
conflict: E-SEL-1004 (Jung Yerin) department: All four main replies (R1, R2, R3, R4) list E-SEL-1004 as an active employee of Marketing Team, but group record [E3] (day -3) shows she was transferred from Marketing Team to Dev Team 2 on day -3 and her stored department is Dev Team 2. ([R1] [R2] [R3] [R4] [E3])
conflict: Dev Team 2 active employee count: Replies R1/R2/R3/R4 list 8 active employees for Dev Team 2, omitting E-SEL-1004 (Jung Yerin) who was transferred to Dev Team 2 per [E3], and also omitting E-SEL-1013 (Kang Seoa) who was shown as active in Dev Team 2 in the day-2 database query in [E7]. ([R1] [R2] [R3] [R4] [E3] [E7])
conflict: Marketing Team active employee count: Replies R1/R2/R3/R4 count 2 active employees for Marketing Team including E-SEL-1004, but [E3] shows E-SEL-1004 was transferred to Dev Team 2 on day -3, leaving only E-SEL-2016 (Pi Jaewon) as a confirmed active employee in Marketing Team. ([R1] [R2] [R3] [R4] [E3])
conflict: Sales Team 2 active employee count: Replies R1/R2/R3/R4 list 2 active employees for Sales Team 2 (E-SEL-1006, E-SEL-2010), but [E5] (day 11) shows Mo Seoyun (E-SEL-2013) was transferred from Sales Team 1 to Sales Team 2 effective 
[... truncated]
```
### MATCHER CHECK FR-01011 (need HR-SEL/Dev Team 2/planning_headcount-regular): matcher says **missing**
record text: Transfer of Jegal Yoon approved from Dev Team 2 to Dev Team 1, effective day 14 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
The replies all give planning headcounts of Dev Team 2=8, Marketing Team=2, Sales Team 2=2, but group records show discrepancies: E-SEL-1004 (Jung Yerin) was transferred to Dev Team 2 on day -3 per [E3] (replies still count her in Marketing Team), E-SEL-1013 (Kang Seoa) is active in Dev Team 2 per [E7], and Mo Seoyun was transferred to Sales Team 2 on day 11 per [E5]. Proposed corrected planning headcounts: Dev Team 2=10, Marketing Team=1, Sales Team 2=3. Design Suite seat allocation info is not held in any HR-SEL record.
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 1: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 1: planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 1: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 1: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 1: D3
- Dev Team 2 | planning headcount | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | history, day 10: Reply 2: H487-H490
- Dev Team 2 | Design Suite seats planned | 8 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Sales Team 2 | planning headcount | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 2: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 2: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 2: D3
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 3: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 4: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 4: D1
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 4: D2
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 4: D3
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 5: D8
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 5: D1
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 5: D9
- Mo Seoyun (E-SEL-2013) | current department (database) | Sales Team 1 |  | db, day 7: Reply 5: D3
- Mo Seoyun (E-SEL-2013) | employment status | active |  | db, day 7: Reply 5: D3
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: Reply 6: D1
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: Reply 6: D2
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: Reply 6: D3
- Pi Jaewon | name | Pi Jaewon |  | db, day fixed: Reply 6: D1
- Pi Jaewon | alias | Jaewon (Manager) |  | db, day fixed: Reply 6: D1
- Pi Jaewon | current department | Marketing Team | active | db, day 12: Reply 6: D4
- Pi Jaewon | hire day | 7 |  | db, day 12: Reply 6: D4
- Cho Eunho19 | name | Cho Eunho19 |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | alias | Eunho19 (Senior) |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | current department | Dev Team 2 | active | db, day 12: Reply 6: D5
- Cho Eunho19 | hire day | 11 |  | db, day 12: Reply 6: D5
- Mo Seoyun | name | Mo Seoyun |  | db, day fixed: Reply 6: D3
- Mo Seoyun | alias | Seoyun (Manager) |  | db, day fixed: Reply 6: D3
- Mo Seoyun | current department (database) | Sales Team 1 | active | db, day 7: Reply 6: D6
- Mo Seoyun | hire day | 3 |  | db, day 7: Reply 6: D6
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 7: D1
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 7: D2
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 7: D3
- E-SEL-1004 | department | Dev Team 2 | active | history, day -3: [E3]
- E-SEL-1004 | transfer | moved from Marketing Team to Dev Team 2 | applied day -3 | history, day -3: [E3]
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: [R5]
- Pi Jaewon | onboarding | joined Marketing Team, grade 2, regular | active | history, day 7: [E4]
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: [R5]
- Cho Eunho19 | onboarding | joined Dev Team 2, grade 2, contractor | active | history, day 11: [E6]
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: [R5]
- Mo Seoyun | transfer | moved from Sales Team 1 to Sales Team 2, grade 1, regular | applied day 11 | history, day 11: [E5]
missing: Design Suite seat allocation or assignment information — not held in any HR-SEL record (all seven replies confirm this is outside their area)
conflict: E-SEL-1004 (Jung Yerin) department: All four main replies (R1, R2, R3, R4) list E-SEL-1004 as an active employee of Marketing Team, but group record [E3] (day -3) shows she was transferred from Marketing Team to Dev Team 2 on day -3 and her stored department is Dev Team 2. ([R1] [R2] [R3] [R4] [E3])
conflict: Dev Team 2 active employee count: Replies R1/R2/R3/R4 list 8 active employees for Dev Team 2, omitting E-SEL-1004 (Jung Yerin) who was transferred to Dev Team 2 per [E3], and also omitting E-SEL-1013 (Kang Seoa) who was shown as active in Dev Team 2 in the day-2 database query in [E7]. ([R1] [R2] [R3] [R4] [E3] [E7])
conflict: Marketing Team active employee count: Replies R1/R2/R3/R4 count 2 active employees for Marketing Team including E-SEL-1004, but [E3] shows E-SEL-1004 was transferred to Dev Team 2 on day -3, leaving only E-SEL-2016 (Pi Jaewon) as a confirmed active employee in Marketing Team. ([R1] [R2] [R3] [R4] [E3])
conflict: Sales Team 2 active employee count: Replies R1/R2/R3/R4 list 2 active employees for Sales Team 2 (E-SEL-1006, E-SEL-2010), but [E5] (day 11) shows Mo Seoyun (E-SEL-2013) was transferred from Sales Team 1 to Sales Team 2 effective 
[... truncated]
```
### MATCHER CHECK FR-01472 (need HR-SEL/Sales Team 2/planning_headcount-regular): matcher says **delivered**
record text: HR record of Mo Seoyun moved from Sales Team 1 to Sales Team 2, grade 1, regular. Stored value: {"contract":"regular","dept":"Sales Team 2","grade":1,"hire_day":3,"status":"active"}
What the requester received from HR-SEL during this task:
```
The replies all give planning headcounts of Dev Team 2=8, Marketing Team=2, Sales Team 2=2, but group records show discrepancies: E-SEL-1004 (Jung Yerin) was transferred to Dev Team 2 on day -3 per [E3] (replies still count her in Marketing Team), E-SEL-1013 (Kang Seoa) is active in Dev Team 2 per [E7], and Mo Seoyun was transferred to Sales Team 2 on day 11 per [E5]. Proposed corrected planning headcounts: Dev Team 2=10, Marketing Team=1, Sales Team 2=3. Design Suite seat allocation info is not held in any HR-SEL record.
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 1: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 1: planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 1: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 1: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 1: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 1: D3
- Dev Team 2 | planning headcount | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 2: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | history, day 10: Reply 2: H487-H490
- Dev Team 2 | Design Suite seats planned | 8 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | planning headcount | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Marketing Team | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Sales Team 2 | planning headcount | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 2: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | history, day 11: Reply 2: H526-H531
- Sales Team 2 | Design Suite seats planned | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 2: D1
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 2: D2
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 2: D3
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 3: D1
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D2
- Marketing Team | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 3: D3
- Sales Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 3: rule planning_headcount
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: rule planning_headcount
- Dev Team 2 | headcount (active employees) | 8 |  | db, day unknown: Reply 4: D1
- Dev Team 2 | planning headcount | 8 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Dev Team 2 | active employees | E-SEL-1002, E-SEL-1010, E-SEL-1012, E-SEL-1014, E-SEL-2003, E-SEL-2004, E-SEL-2017, E-SEL-2018 | active | db, day unknown: Reply 4: D1
- Marketing Team | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D2
- Marketing Team | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Marketing Team | active employees | E-SEL-1004, E-SEL-2016 | active | db, day unknown: Reply 4: D2
- Sales Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 4: D3
- Sales Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 4: rule: planning_headcount
- Sales Team 2 | active employees | E-SEL-1006, E-SEL-2010 | active | db, day unknown: Reply 4: D3
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 5: D8
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 5: D1
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 5: D9
- Mo Seoyun (E-SEL-2013) | current department (database) | Sales Team 1 |  | db, day 7: Reply 5: D3
- Mo Seoyun (E-SEL-2013) | employment status | active |  | db, day 7: Reply 5: D3
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: Reply 6: D1
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: Reply 6: D2
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: Reply 6: D3
- Pi Jaewon | name | Pi Jaewon |  | db, day fixed: Reply 6: D1
- Pi Jaewon | alias | Jaewon (Manager) |  | db, day fixed: Reply 6: D1
- Pi Jaewon | current department | Marketing Team | active | db, day 12: Reply 6: D4
- Pi Jaewon | hire day | 7 |  | db, day 12: Reply 6: D4
- Cho Eunho19 | name | Cho Eunho19 |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | alias | Eunho19 (Senior) |  | db, day fixed: Reply 6: D2
- Cho Eunho19 | current department | Dev Team 2 | active | db, day 12: Reply 6: D5
- Cho Eunho19 | hire day | 11 |  | db, day 12: Reply 6: D5
- Mo Seoyun | name | Mo Seoyun |  | db, day fixed: Reply 6: D3
- Mo Seoyun | alias | Seoyun (Manager) |  | db, day fixed: Reply 6: D3
- Mo Seoyun | current department (database) | Sales Team 1 | active | db, day 7: Reply 6: D6
- Mo Seoyun | hire day | 3 |  | db, day 7: Reply 6: D6
- Pi Jaewon | Employee ID | E-SEL-2016 |  | db, day fixed: Reply 7: D1
- Cho Eunho19 | Employee ID | E-SEL-2018 |  | db, day fixed: Reply 7: D2
- Mo Seoyun | Employee ID | E-SEL-2013 |  | db, day fixed: Reply 7: D3
- E-SEL-1004 | department | Dev Team 2 | active | history, day -3: [E3]
- E-SEL-1004 | transfer | moved from Marketing Team to Dev Team 2 | applied day -3 | history, day -3: [E3]
- Pi Jaewon | employee ID | E-SEL-2016 |  | db, day fixed: [R5]
- Pi Jaewon | onboarding | joined Marketing Team, grade 2, regular | active | history, day 7: [E4]
- Cho Eunho19 | employee ID | E-SEL-2018 |  | db, day fixed: [R5]
- Cho Eunho19 | onboarding | joined Dev Team 2, grade 2, contractor | active | history, day 11: [E6]
- Mo Seoyun | employee ID | E-SEL-2013 |  | db, day fixed: [R5]
- Mo Seoyun | transfer | moved from Sales Team 1 to Sales Team 2, grade 1, regular | applied day 11 | history, day 11: [E5]
missing: Design Suite seat allocation or assignment information — not held in any HR-SEL record (all seven replies confirm this is outside their area)
conflict: E-SEL-1004 (Jung Yerin) department: All four main replies (R1, R2, R3, R4) list E-SEL-1004 as an active employee of Marketing Team, but group record [E3] (day -3) shows she was transferred from Marketing Team to Dev Team 2 on day -3 and her stored department is Dev Team 2. ([R1] [R2] [R3] [R4] [E3])
conflict: Dev Team 2 active employee count: Replies R1/R2/R3/R4 list 8 active employees for Dev Team 2, omitting E-SEL-1004 (Jung Yerin) who was transferred to Dev Team 2 per [E3], and also omitting E-SEL-1013 (Kang Seoa) who was shown as active in Dev Team 2 in the day-2 database query in [E7]. ([R1] [R2] [R3] [R4] [E3] [E7])
conflict: Marketing Team active employee count: Replies R1/R2/R3/R4 count 2 active employees for Marketing Team including E-SEL-1004, but [E3] shows E-SEL-1004 was transferred to Dev Team 2 on day -3, leaving only E-SEL-2016 (Pi Jaewon) as a confirmed active employee in Marketing Team. ([R1] [R2] [R3] [R4] [E3])
conflict: Sales Team 2 active employee count: Replies R1/R2/R3/R4 list 2 active employees for Sales Team 2 (E-SEL-1006, E-SEL-2010), but [E5] (day 11) shows Mo Seoyun (E-SEL-2013) was transferred from Sales Team 1 to Sales Team 2 effective 
[... truncated]
```

## CASE 82: deepseek-v4-flash · ingress · s13 · W-00027 · class D · day 3 · template capacity
### Task as given to the requester
How many in-house laptop (basic) units and Analytics seats are actually available right now?
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
{"stock": 0, "seats": 1, "seats_other_region": null}
### Counterfactual answers (generator)
{"stale": {"stock": 0, "seats": 0, "seats_other_region": null}, "partial": {"stock": 1, "seats": 1, "seats_other_region": null}, "neardup": {"stock": 0, "seats": 3, "seats_other_region": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/stock/INV-TYO-LTB** (group IT-TYO, class D, local=False)
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-LTB"}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-TYO/inv/INV-TYO-LTB/qty` v3 (recorded day -6, registered day -3): 2
- RECORD FR-00810 [decision-critical] (operational/pending_intent, day -3, by it-tyo.w00109; DB shows n/a): In-house stock laptop (basic) 1 unit held for an incoming Dev Section 2 hire until day 7.
- RECORD FR-01051 [decision-critical] (operational/pending_intent, day 2, by it-tyo.w00146; DB shows n/a): In-house stock laptop (basic) 1 unit held for an incoming Sales Section 1 hire until day 13.
**need IT-TYO/license/Analytics** (group IT-TYO, class A, local=False)
- RECORD FR-01052 [decision-critical] (db_pending/observation, day 2, by it-tyo.w00147; DB shows 3): Analytics seats In use 36/40 seats. Stored value: {"seats":40,"used":36}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00554 [decision-critical] (operational/pending_intent, day -10, by it-tyo.w00061; DB shows n/a): Analytics seats 3 seats reserved for Dev Section 2 project until day 4.
### Model answer and official verdict
answer: {"seats": 1, "seats_other_region": null, "stock": 1}
official exact match: 0 (2/3 slots)
### MATCHER CHECK FR-00810 (need IT-TYO/stock/INV-TYO-LTB): matcher says **delivered**
record text: In-house stock laptop (basic) 1 unit held for an incoming Dev Section 2 hire until day 7.
What the requester received from IT-TYO during this task:
```
As of day 3: In-house laptop (basic) available = 1 unit (2 in stock minus 1 held for Dev Section 2 hire until day 7). Analytics available free seats = 1 (40 total − 36 used − 3 reserved for Dev Section 2 project until day 4).
- INV-TYO-LTB | inventory quantity (database) | 2 |  | db, day -3: Reply 1: D1
- In-house stock laptop (basic) | hold status | held for an incoming Dev Section 2 hire | recorded day -3 | history, day -3: Reply 1: H183
- In-house stock laptop (basic) | worker report | item done | day 2 | history, day 2: Reply 1: H267
- Analytics | total license seats | 40 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (database, day -2) | 37 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: Reply 1: H268
- Analytics | reserved seats (Dev Section 2 project) | 3 | until day 4 | history, day -10: Reply 1: H164
- Analytics | available free seats (calculated: 40 - 36 - 3) | 1 |  | history, day 2: Reply 1: H268,H164,D2
- In-house stock laptop (basic) | hold end date | day 7 |  | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold active after day 2 item done | yes | active until day 7 | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold reason | incoming Dev Section 2 hire |  | history, day -3: Reply 2: H183
- in-house laptop (basic) | hold end date | day 7 |  | unknown, day unknown: Reply 3: H183
- in-house laptop (basic) | hold active status after day 2 item done | still active | active until day 7 | unknown, day unknown: Reply 3: H183
- In-house stock laptop (basic) | inventory quantity (stocktake, day -20) | 1 |  | history, day -20: [E1]
- In-house stock laptop (basic) | units issued | 1 |  | history, day -10: [E11]
- In-house stock laptop (basic) | assigned to | Ikeda Hikaru (E-TYO-2000) |  | history, day -10: [E12]
- In-house stock laptop (basic) | worker report | item done |  | history, day -6: [E15]
- Analytics | used license seats (audit, day -20) | 36 |  | history, day -20: [E3]
- Analytics | used license seats (worker report, day -14) | 35 |  | history, day -14: [E8]
- Analytics | used license seats (task, day -14) | 35 |  | history, day -14: [E9]
- Analytics | used license seats (task, day -3) | 37 |  | history, day -3: [E18]
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: [E21]
- Analytics | used license seats (task, day 2) | 36 |  | history, day 2: [E23]
conflict: In-house laptop (basic) hold status: R1 suggests the hold placed day -3 for an incoming Dev Section 2 hire may have been resolved by the 'item done' on day 2. However, group records [E16] and [E17] explicitly state the hold lasts 'until day 7', and per the Periods rule a hold recorded as lasting until day N is still in effect on day N. Today is day 3, so the hold remains active. R2 and R3 confirm the hold is still active. ([R1] [E16] [E17] [R2] [R3])
proposed: In-house laptop (basic) available quantity = 1 ([R1] [E16] [E17] [R2] [R3]) — The database on day -3 showed 2 units; one unit is held for an incoming Dev Section 2 hire until day 7 (still active on day 3 per Periods rule), leaving 1 available.
proposed: Analytics available free seats = 1 ([R1] [E10] [E21] [E23]) — 40 total seats minus 36 used (per day 2 records, newer than database v3) minus 3 reserved for Dev Section 2 project until day 4 (still active on day 3) equals 1 available free seat per hold_policy rule.
```
### MATCHER CHECK FR-01051 (need IT-TYO/stock/INV-TYO-LTB): matcher says **stale**
record text: In-house stock laptop (basic) 1 unit held for an incoming Sales Section 1 hire until day 13.
What the requester received from IT-TYO during this task:
```
As of day 3: In-house laptop (basic) available = 1 unit (2 in stock minus 1 held for Dev Section 2 hire until day 7). Analytics available free seats = 1 (40 total − 36 used − 3 reserved for Dev Section 2 project until day 4).
- INV-TYO-LTB | inventory quantity (database) | 2 |  | db, day -3: Reply 1: D1
- In-house stock laptop (basic) | hold status | held for an incoming Dev Section 2 hire | recorded day -3 | history, day -3: Reply 1: H183
- In-house stock laptop (basic) | worker report | item done | day 2 | history, day 2: Reply 1: H267
- Analytics | total license seats | 40 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (database, day -2) | 37 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: Reply 1: H268
- Analytics | reserved seats (Dev Section 2 project) | 3 | until day 4 | history, day -10: Reply 1: H164
- Analytics | available free seats (calculated: 40 - 36 - 3) | 1 |  | history, day 2: Reply 1: H268,H164,D2
- In-house stock laptop (basic) | hold end date | day 7 |  | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold active after day 2 item done | yes | active until day 7 | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold reason | incoming Dev Section 2 hire |  | history, day -3: Reply 2: H183
- in-house laptop (basic) | hold end date | day 7 |  | unknown, day unknown: Reply 3: H183
- in-house laptop (basic) | hold active status after day 2 item done | still active | active until day 7 | unknown, day unknown: Reply 3: H183
- In-house stock laptop (basic) | inventory quantity (stocktake, day -20) | 1 |  | history, day -20: [E1]
- In-house stock laptop (basic) | units issued | 1 |  | history, day -10: [E11]
- In-house stock laptop (basic) | assigned to | Ikeda Hikaru (E-TYO-2000) |  | history, day -10: [E12]
- In-house stock laptop (basic) | worker report | item done |  | history, day -6: [E15]
- Analytics | used license seats (audit, day -20) | 36 |  | history, day -20: [E3]
- Analytics | used license seats (worker report, day -14) | 35 |  | history, day -14: [E8]
- Analytics | used license seats (task, day -14) | 35 |  | history, day -14: [E9]
- Analytics | used license seats (task, day -3) | 37 |  | history, day -3: [E18]
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: [E21]
- Analytics | used license seats (task, day 2) | 36 |  | history, day 2: [E23]
conflict: In-house laptop (basic) hold status: R1 suggests the hold placed day -3 for an incoming Dev Section 2 hire may have been resolved by the 'item done' on day 2. However, group records [E16] and [E17] explicitly state the hold lasts 'until day 7', and per the Periods rule a hold recorded as lasting until day N is still in effect on day N. Today is day 3, so the hold remains active. R2 and R3 confirm the hold is still active. ([R1] [E16] [E17] [R2] [R3])
proposed: In-house laptop (basic) available quantity = 1 ([R1] [E16] [E17] [R2] [R3]) — The database on day -3 showed 2 units; one unit is held for an incoming Dev Section 2 hire until day 7 (still active on day 3 per Periods rule), leaving 1 available.
proposed: Analytics available free seats = 1 ([R1] [E10] [E21] [E23]) — 40 total seats minus 36 used (per day 2 records, newer than database v3) minus 3 reserved for Dev Section 2 project until day 4 (still active on day 3) equals 1 available free seat per hold_policy rule.
```
### MATCHER CHECK FR-01052 (need IT-TYO/license/Analytics): matcher says **delivered**
record text: Analytics seats In use 36/40 seats. Stored value: {"seats":40,"used":36}
What the requester received from IT-TYO during this task:
```
As of day 3: In-house laptop (basic) available = 1 unit (2 in stock minus 1 held for Dev Section 2 hire until day 7). Analytics available free seats = 1 (40 total − 36 used − 3 reserved for Dev Section 2 project until day 4).
- INV-TYO-LTB | inventory quantity (database) | 2 |  | db, day -3: Reply 1: D1
- In-house stock laptop (basic) | hold status | held for an incoming Dev Section 2 hire | recorded day -3 | history, day -3: Reply 1: H183
- In-house stock laptop (basic) | worker report | item done | day 2 | history, day 2: Reply 1: H267
- Analytics | total license seats | 40 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (database, day -2) | 37 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: Reply 1: H268
- Analytics | reserved seats (Dev Section 2 project) | 3 | until day 4 | history, day -10: Reply 1: H164
- Analytics | available free seats (calculated: 40 - 36 - 3) | 1 |  | history, day 2: Reply 1: H268,H164,D2
- In-house stock laptop (basic) | hold end date | day 7 |  | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold active after day 2 item done | yes | active until day 7 | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold reason | incoming Dev Section 2 hire |  | history, day -3: Reply 2: H183
- in-house laptop (basic) | hold end date | day 7 |  | unknown, day unknown: Reply 3: H183
- in-house laptop (basic) | hold active status after day 2 item done | still active | active until day 7 | unknown, day unknown: Reply 3: H183
- In-house stock laptop (basic) | inventory quantity (stocktake, day -20) | 1 |  | history, day -20: [E1]
- In-house stock laptop (basic) | units issued | 1 |  | history, day -10: [E11]
- In-house stock laptop (basic) | assigned to | Ikeda Hikaru (E-TYO-2000) |  | history, day -10: [E12]
- In-house stock laptop (basic) | worker report | item done |  | history, day -6: [E15]
- Analytics | used license seats (audit, day -20) | 36 |  | history, day -20: [E3]
- Analytics | used license seats (worker report, day -14) | 35 |  | history, day -14: [E8]
- Analytics | used license seats (task, day -14) | 35 |  | history, day -14: [E9]
- Analytics | used license seats (task, day -3) | 37 |  | history, day -3: [E18]
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: [E21]
- Analytics | used license seats (task, day 2) | 36 |  | history, day 2: [E23]
conflict: In-house laptop (basic) hold status: R1 suggests the hold placed day -3 for an incoming Dev Section 2 hire may have been resolved by the 'item done' on day 2. However, group records [E16] and [E17] explicitly state the hold lasts 'until day 7', and per the Periods rule a hold recorded as lasting until day N is still in effect on day N. Today is day 3, so the hold remains active. R2 and R3 confirm the hold is still active. ([R1] [E16] [E17] [R2] [R3])
proposed: In-house laptop (basic) available quantity = 1 ([R1] [E16] [E17] [R2] [R3]) — The database on day -3 showed 2 units; one unit is held for an incoming Dev Section 2 hire until day 7 (still active on day 3 per Periods rule), leaving 1 available.
proposed: Analytics available free seats = 1 ([R1] [E10] [E21] [E23]) — 40 total seats minus 36 used (per day 2 records, newer than database v3) minus 3 reserved for Dev Section 2 project until day 4 (still active on day 3) equals 1 available free seat per hold_policy rule.
```
### MATCHER CHECK FR-00554 (need IT-TYO/license/Analytics): matcher says **delivered**
record text: Analytics seats 3 seats reserved for Dev Section 2 project until day 4.
What the requester received from IT-TYO during this task:
```
As of day 3: In-house laptop (basic) available = 1 unit (2 in stock minus 1 held for Dev Section 2 hire until day 7). Analytics available free seats = 1 (40 total − 36 used − 3 reserved for Dev Section 2 project until day 4).
- INV-TYO-LTB | inventory quantity (database) | 2 |  | db, day -3: Reply 1: D1
- In-house stock laptop (basic) | hold status | held for an incoming Dev Section 2 hire | recorded day -3 | history, day -3: Reply 1: H183
- In-house stock laptop (basic) | worker report | item done | day 2 | history, day 2: Reply 1: H267
- Analytics | total license seats | 40 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (database, day -2) | 37 |  | db, day -2: Reply 1: D2
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: Reply 1: H268
- Analytics | reserved seats (Dev Section 2 project) | 3 | until day 4 | history, day -10: Reply 1: H164
- Analytics | available free seats (calculated: 40 - 36 - 3) | 1 |  | history, day 2: Reply 1: H268,H164,D2
- In-house stock laptop (basic) | hold end date | day 7 |  | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold active after day 2 item done | yes | active until day 7 | history, day -3: Reply 2: H183
- In-house stock laptop (basic) | hold reason | incoming Dev Section 2 hire |  | history, day -3: Reply 2: H183
- in-house laptop (basic) | hold end date | day 7 |  | unknown, day unknown: Reply 3: H183
- in-house laptop (basic) | hold active status after day 2 item done | still active | active until day 7 | unknown, day unknown: Reply 3: H183
- In-house stock laptop (basic) | inventory quantity (stocktake, day -20) | 1 |  | history, day -20: [E1]
- In-house stock laptop (basic) | units issued | 1 |  | history, day -10: [E11]
- In-house stock laptop (basic) | assigned to | Ikeda Hikaru (E-TYO-2000) |  | history, day -10: [E12]
- In-house stock laptop (basic) | worker report | item done |  | history, day -6: [E15]
- Analytics | used license seats (audit, day -20) | 36 |  | history, day -20: [E3]
- Analytics | used license seats (worker report, day -14) | 35 |  | history, day -14: [E8]
- Analytics | used license seats (task, day -14) | 35 |  | history, day -14: [E9]
- Analytics | used license seats (task, day -3) | 37 |  | history, day -3: [E18]
- Analytics | used license seats (worker report, day 2) | 36 |  | history, day 2: [E21]
- Analytics | used license seats (task, day 2) | 36 |  | history, day 2: [E23]
conflict: In-house laptop (basic) hold status: R1 suggests the hold placed day -3 for an incoming Dev Section 2 hire may have been resolved by the 'item done' on day 2. However, group records [E16] and [E17] explicitly state the hold lasts 'until day 7', and per the Periods rule a hold recorded as lasting until day N is still in effect on day N. Today is day 3, so the hold remains active. R2 and R3 confirm the hold is still active. ([R1] [E16] [E17] [R2] [R3])
proposed: In-house laptop (basic) available quantity = 1 ([R1] [E16] [E17] [R2] [R3]) — The database on day -3 showed 2 units; one unit is held for an incoming Dev Section 2 hire until day 7 (still active on day 3 per Periods rule), leaving 1 available.
proposed: Analytics available free seats = 1 ([R1] [E10] [E21] [E23]) — 40 total seats minus 36 used (per day 2 records, newer than database v3) minus 3 reserved for Dev Section 2 project until day 4 (still active on day 3) equals 1 available free seat per hold_policy rule.
```

## CASE 83: deepseek-v4-flash · ingress · s13 · W-00009 · class D · day 1 · template alloc
### Task as given to the requester
Allocate IDE Pro seats to Dev Team 1, Marketing Team, Dev Team 2 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
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
{"alloc": [1, 6, 5], "transfer": 0, "buy": 5, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [0, 6, 5], "transfer": 0, "buy": 4, "unmet": 0}, "partial": {"alloc": [0, 6, 5], "transfer": 0, "buy": 4, "unmet": 0}, "neardup": {"alloc": [5, 6, 5], "transfer": 0, "buy": 9, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/license/IDE Pro** (group IT-SEL, class None, local=True)
- DB `IT-SEL/lic/IDE Pro/seats` v2 (recorded day -6, registered day -5): {"seats": 40, "used": 33}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
**need HR-SEL/Dev Team 1/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-00924 [decision-critical] (db_pending/observation, day 0, by hr-sel.a5; DB shows 2): HR record of Choi Jiwoo moved from Sales Team 2 to Dev Team 1, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Dev Team 1","grade":3,"hire_day":-69,"status":"active"}
- NEGATIVE: {"query": "HR-SEL Dev Team 1 memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=SEL AND dept=Dev Team 1 AND status=active) → 1
**need HR-SEL/Marketing Team/planning_headcount** (group HR-SEL, class C, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1002/profile` v6 (recorded day -2, registered day -1): {"dept": "Marketing Team", "grade": 2, "contract": "regular", "hire_day": -473, "status": "active"}
- RECORD FR-00757 [decision-critical] (operational/pending_intent, day -5, by hr-sel.a5; DB shows n/a): Transfer of Han Siwoo approved from Dev Team 2 to Marketing Team, effective day 5 (stays in Dev Team 2 until then).
- DB `HR-SEL/emp/E-SEL-1008/profile` v2 (recorded day -12, registered day -11): {"dept": "Sales Team 2", "grade": 4, "contract": "contractor", "hire_day": -222, "status": "active"}
- RECORD FR-00766 [decision-critical] (operational/pending_intent, day -5, by hr-sel.a5; DB shows n/a): Transfer of Kang Seoa approved from Marketing Team to Sales Team 1, effective day 3 (stays in Marketing Team until then).
- RECORD FR-00677 [decision-critical] (operational/pending_intent, day -7, by hr-sel.a5; DB shows n/a): Transfer of Bae Jihoon approved from Sales Team 2 to Marketing Team, effective day 3 (stays in Sales Team 2 until then).
- RECORD FR-00978 [decision-critical] (operational/pending_intent, day 1, by hr-sel.a4; DB shows n/a): Marketing Team confirmed hire OF-00014 starts day 6, regular (not yet in HR records).
- QUERY COUNT(emp WHERE region=SEL AND dept=Marketing Team AND status=active) → 4
**need HR-SEL/Dev Team 2/planning_headcount** (group HR-SEL, class D, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- RECORD FR-00757 [decision-critical] (operational/pending_intent, day -5, by hr-sel.a5; DB shows n/a): Transfer of Han Siwoo approved from Dev Team 2 to Marketing Team, effective day 5 (stays in Dev Team 2 until then).
- RECORD FR-00605 [decision-critical] (operational/pending_intent, day -9, by hr-sel.a5; DB shows n/a): Transfer of Shin Daeun approved from Sales Team 2 to Dev Team 2, effective day 3 (stays in Sales Team 2 until then).
- RECORD FR-00778 [decision-critical] (operational/pending_intent, day -4, by hr-sel.n0009; DB shows n/a): Transfer of Seo Jian approved from Sales Team 1 to Dev Team 2, effective day 5 (stays in Sales Team 1 until then).
- DB `HR-SEL/emp/E-SEL-1019/profile` v2 (recorded day -1, registered day 1): {"dept": "Dev Team 2", "grade": 3, "contract": "regular", "hire_day": -609, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-2003/profile` v2 (recorded day -7, registered day -4): {"dept": "Sales Team 2", "grade": 3, "contract": "regular", "hire_day": -10, "status": "active"}
- RECORD FR-00881 [decision-critical] (operational/pending_intent, day -1, by hr-sel.a5; DB shows n/a): Transfer of Pyo Jisung approved from Sales Team 2 to Dev Team 2, effective day 7 (stays in Sales Team 2 until then).
- RECORD FR-00747 [decision-critical] (operational/pending_intent, day -5, by hr-sel.a5; DB shows n/a): Transfer of Ok Dain approved from Customer Support Team to Dev Team 2, effective day 6 (stays in Customer Support Team until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Dev Team 2 AND status=active) → 2
**need IT-TYO/license/IDE Pro** (group IT-TYO, class A, local=False)
- DB `IT-TYO/lic/IDE Pro/seats` v2 (recorded day -19, registered day -17): {"seats": 33, "used": 32}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-00772 (operational/pending_intent, day -5, by it-tyo.w00100; DB shows n/a): IDE Pro seats 2 seats reserved for Sales Section 1 onboarding until day 2.
**need IT-SEL/rule/seat_transfer_share** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_transfer_share: {"id": "IT-SEL.seat_transfer_share", "group": "IT-SEL", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-SEL/rule/seat_purchase_line** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.seat_purchase_line: {"id": "FIN-SEL.seat_purchase_line", "group": "FIN-SEL", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-SEL/Dev Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 1/remaining` v4 (recorded day -7, registered day -4): 3215666
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00607 (operational/pending_intent, day -9, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 150,590 KRW earmarked for quarter-end consumables until day 4 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00004/status` v2 (recorded day -10, registered day -9): {"status": "settled", "amount": 843331, "expected_settle": -10}
- DB `FIN-SEL/commit/CMT-00019/status` v2 (recorded day -2, registered day -1): {"status": "settled", "amount": 613302, "expected_settle": -2}
- DB `FIN-SEL/commit/CMT-00034/status` v2 (recorded day -2, registered day -1): {"status": "settled", "amount": 815110, "expected_settle": -2}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00607", "CMT-00041"]
**need IT-SEL/rule/seat_price** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_price: {"id": "IT-SEL.seat_price", "group": "IT-SEL", "title": "Standard seat price", "params": {"price": 135487}, "text": "When there is no supplier price, one seat costs 135,487 KRW."}
### Model answer and official verdict
answer: {"alloc": [1, 6, 0], "buy": 2, "transfer": 0, "unmet": 0}
official exact match: 0 (2/4 slots)
### MATCHER CHECK FR-00924 (need HR-SEL/Dev Team 1/planning_headcount): matcher says **delivered**
record text: HR record of Choi Jiwoo moved from Sales Team 2 to Dev Team 1, grade 3, contractor. Stored value: {"contract":"contractor","dept":"Dev Team 1","grade":3,"hire_day":-69,"status":"active"}
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00757 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Han Siwoo approved from Dev Team 2 to Marketing Team, effective day 5 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00766 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Kang Seoa approved from Marketing Team to Sales Team 1, effective day 3 (stays in Marketing Team until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00677 (need HR-SEL/Marketing Team/planning_headcount): matcher says **missing**
record text: Transfer of Bae Jihoon approved from Sales Team 2 to Marketing Team, effective day 3 (stays in Sales Team 2 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00978 (need HR-SEL/Marketing Team/planning_headcount): matcher says **delivered**
record text: Marketing Team confirmed hire OF-00014 starts day 6, regular (not yet in HR records).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00757 (need HR-SEL/Dev Team 2/planning_headcount): matcher says **missing**
record text: Transfer of Han Siwoo approved from Dev Team 2 to Marketing Team, effective day 5 (stays in Dev Team 2 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00605 (need HR-SEL/Dev Team 2/planning_headcount): matcher says **missing**
record text: Transfer of Shin Daeun approved from Sales Team 2 to Dev Team 2, effective day 3 (stays in Sales Team 2 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00778 (need HR-SEL/Dev Team 2/planning_headcount): matcher says **missing**
record text: Transfer of Seo Jian approved from Sales Team 1 to Dev Team 2, effective day 5 (stays in Sales Team 1 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00881 (need HR-SEL/Dev Team 2/planning_headcount): matcher says **missing**
record text: Transfer of Pyo Jisung approved from Sales Team 2 to Dev Team 2, effective day 7 (stays in Sales Team 2 until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```
### MATCHER CHECK FR-00747 (need HR-SEL/Dev Team 2/planning_headcount): matcher says **missing**
record text: Transfer of Ok Dain approved from Customer Support Team to Dev Team 2, effective day 6 (stays in Customer Support Team until then).
What the requester received from HR-SEL during this task:
```
- Dev Team 1 | planning headcount | 0 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 1 | department_employees record | no record registered |  | db, day unknown: Reply 1: D1
- Dev Team 1 | headcount (active employees) | 0 |  | db, day unknown: Reply 1: D1
- Dev Team 1 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Lee Seojun (E-SEL-1002) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Jung Yerin (E-SEL-1004) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Kang Seoa (E-SEL-1013) | active | db, day unknown: Reply 1: D2
- Marketing Team | active employee | Hwang Taeo (E-SEL-1017) | active | db, day unknown: Reply 1: D2
- Marketing Team | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Marketing Team | transfers taking effect within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 2 | planning headcount | 3 |  | rule, day fixed: Reply 1: rule: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Han Siwoo (E-SEL-1005) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | active employee | Kwon Soyul (E-SEL-1011) | active | db, day unknown: Reply 1: D3
- Dev Team 2 | exited employee (not counted) | Noh Haeun (E-SEL-1019) | exited | db, day unknown: Reply 1: D3
- Dev Team 2 | incoming transfer within 7 days | Seo Jian (E-SEL-1018) from Sales Team 1, effective day 5 | approved | history, day 1: Reply 1: H179
- Dev Team 2 | confirmed hires starting within 7 days | none |  | history, day 1: Reply 1: H179
- Dev Team 1 | planning headcount | 1 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | headcount (active employees) | 1 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1003 | name | Choi Jiwoo |  | db, day fixed: Reply 2: D19
- E-SEL-1003 | department (database) | Sales Team 2 |  | db, day -1: Reply 2: D4
- E-SEL-1003 | department (transfer record) | Dev Team 1 | effective day 0 | history, day -2: Reply 2: H45
- E-SEL-1003 | employment status | active |  | db, day -1: Reply 2: D4
- Dev Team 1 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | transfers taking effect within 7 days | 1 | Choi Jiwoo effective day 0 | history, day -2: Reply 2: H45
- Marketing Team | planning headcount | 5 |  | rule, day fixed: Reply 2: planning_headcount
- Marketing Team | headcount (active employees) | 4 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 2: D12
- E-SEL-1002 | employment status | active |  | db, day -1: Reply 2: D5
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 2: D13
- E-SEL-1004 | employment status | active |  | db, day -8: Reply 2: D6
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 2: D14
- E-SEL-1013 | employment status | active |  | db, day 0: Reply 2: D7
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 2: D15
- E-SEL-1017 | employment status | active |  | db, day -20: Reply 2: D8
- Marketing Team | confirmed hires starting within 7 days | 1 |  | history, day 1: Reply 2: H68
- OF-00014 | start day | 6 |  | history, day 1: Reply 2: H68
- OF-00014 | contract type | regular |  | history, day 1: Reply 2: H68
- OF-00014 | department | Marketing Team |  | history, day 1: Reply 2: H68
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | headcount (active employees) | 2 |  | rule, day fixed: Reply 2: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 2: D16
- E-SEL-1005 | employment status | active |  | db, day 0: Reply 2: D9
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 2: D17
- E-SEL-1011 | employment status | active |  | db, day -7: Reply 2: D10
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 2: D18
- E-SEL-1019 | employment status | exited |  | db, day 1: Reply 2: D11
- Dev Team 2 | confirmed hires starting within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 2 | transfers taking effect within 7 days | 0 |  | rule, day fixed: Reply 2: planning_headcount
- Dev Team 1 | planning headcount | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | active employees (headcount) | 0 |  | db, day unknown: Reply 3: D1
- Dev Team 1 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 1 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | planning headcount | 4 |  | rule, day fixed: Reply 3: planning_headcount
- Marketing Team | active employees (headcount) | 4 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1002 | name | Lee Seojun |  | db, day fixed: Reply 3: D27
- E-SEL-1002 | department | Marketing Team |  | db, day -1: Reply 3: D10
- E-SEL-1002 | status | active |  | db, day -1: Reply 3: D10
- E-SEL-1004 | name | Jung Yerin |  | db, day fixed: Reply 3: D28
- E-SEL-1004 | department | Marketing Team |  | db, day -8: Reply 3: D11
- E-SEL-1004 | status | active |  | db, day -8: Reply 3: D11
- E-SEL-1013 | name | Kang Seoa |  | db, day fixed: Reply 3: D34
- E-SEL-1013 | department | Marketing Team |  | db, day 0: Reply 3: D12
- E-SEL-1013 | status | active |  | db, day 0: Reply 3: D12
- E-SEL-1017 | name | Hwang Taeo |  | db, day fixed: Reply 3: D38
- E-SEL-1017 | department | Marketing Team |  | db, day -20: Reply 3: D13
- E-SEL-1017 | status | active |  | db, day -20: Reply 3: D13
- Marketing Team | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | planning headcount | 2 |  | rule, day fixed: Reply 3: planning_headcount
- Dev Team 2 | active employees (headcount) | 2 |  | rule, day fixed: Reply 3: headcount_definition
- E-SEL-1005 | name | Han Siwoo |  | db, day fixed: Reply 3: D21
- E-SEL-1005 | department | Dev Team 2 |  | db, day 0: Reply 3: D7
- E-SEL-1005 | status | active |  | db, day 0: Reply 3: D7
- E-SEL-1011 | name | Kwon Soyul |  | db, day fixed: Reply 3: D23
- E-SEL-1011 | department | Dev Team 2 |  | db, day -7: Reply 3: D8
- E-SEL-1011 | status | active |  | db, day -7: Reply 3: D8
- E-SEL-1019 | name | Noh Haeun |  | db, day fixed: Reply 3: D39
- E-SEL-1019 | department | Dev Team 2 |  | db, day 1: Reply 3: D9
- E-SEL-1019 | status | exited |  | db, day 1: Reply 3: D9
- E-SEL-1019 | not counted in headcount (exited) | excluded |  | rule, day fixed: Reply 3: headcount_definition
- Dev Team 2 | confirmed hires starting within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Dev Team 2 | transfers taking effect within 7 days | none recorded |  | unknown, day unknown: Reply 3: history, day 1
- Marketing Team | incoming transfer within 7 days | Han Siwoo (E-SEL-1005) from Dev Team 2, effective day 5 | approved | history, day -5: [E2]
- Dev Team 2 | outgoing transfer within 7 days | Han Siwoo (E-SEL-1005) to Marketing Team, effective day 5 | approved | history, day -5: [E2]
conflict: Dev Team 1 planning headcount: [R1] says 0 and [R3] says 0, but [R2] says 1. Group records show Choi Jiwoo was transferred to Dev Team 1 effective day 0 (day 0 task record in [E4]), making 1 active employee. ([R1] [R2] [R3] [E4])
conflict: Marketing Team planning headcount: [R1] says 4, [R2] says 5, [R3] says 4. None include Han Siwoo's transfer in from Dev Team 2 effective day 5 (per [E2]), which is within 7 days. ([R1] [R2] [R3] [E2])
conflict: Dev Team 2 planning headcount: [R1] says 3 (includes Seo Jian but not Han Siwoo's departure), [R2] says 2 (misses Seo Jian's arrival), [R3] says 2 (misses Seo Jian's arrival). ([R1] [R2] [R3] [E2] [S1])
proposed: Dev Team 1 planning headcount = 1 ([R2] [E4]) — Choi Jiwoo was transferred to Dev Team 1 effective day 0 (per day 0 task record in [E4]), making 1 active employee, with no confirmed hires or other transfers within 7 days.
proposed: Marketing Team planning headcount = 6 ([R2] [E2] [E3]) — 4 active employees (Lee Seojun, Jung Yerin, Kang Seoa, Hwang Taeo) plus confirmed hire OF-00014 starting day 6 ([E3]) plus Han Siwoo transferring in from Dev Team 2 effective day 5 ([E2]), all within 7 days.
proposed: Dev Team 2 planning headcount = 2 ([E2] [S1] [R1]) — 2 active employees (Han Siwoo, Kwon Soyul) minus Han Siwoo transferring out to Marketing Team effective day 5 ([E2]) plus Seo Jian transferring in fro
[... truncated]
```

## CASE 84: deepseek-v4-flash · ingress · s12 · W-00041 · class D · day 5 · template diag
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
answer: {"cause": "COMMIT_NOT_CONFIRMED"}
official exact match: 0 (0/1 slots)
### MATCHER CHECK FR-01095 (need IT-SEL/E-SEL-1006/assets): matcher says **delivered**
record text: A-SEL-4259 monitor recovered, back in storage. Stored value: {"emp":null}
What the requester received from IT-SEL during this task:
```
Asset A-SEL-4259 is registered as a basic-tier monitor. However, the reply [R1] reports it as assigned to E-SEL-1006 based on an older database version, while a more recent task record [E10] (day 4) shows the asset was recovered and is now back in storage with no assignee. The type (monitor) and tier (basic) are confirmed by both the reply and the group records.
- A-SEL-4259 | registration status | registered |  | db, day fixed: Reply 1: D1
- A-SEL-4259 | type of asset | monitor |  | db, day fixed: Reply 1: D1
- A-SEL-4259 | tier | basic |  | db, day fixed: Reply 1: D1
- A-SEL-4259 | assigned to employee | E-SEL-1006 |  | db, day -20: Reply 1: D2
- A-SEL-4259 | current assignment | null (recovered, back in storage) |  | history, day 4: [E10]
- A-SEL-4259 | recovery event | recovered, back in storage | recovered | history, day 4: [E10]
conflict: A-SEL-4259 assignment: [R1] states A-SEL-4259 is assigned to employee E-SEL-1006 based on database v1 (day -20). However, [E10] (day 4) records that the asset was recovered and its holder set to null. Since [E10] is dated later than the database version, it supersedes it per the rule that a record made while processing work counts within its period. ([R1] [E10])
proposed: A-SEL-4259 current assignment = unassigned (recovered, back in storage) ([E10]) — The recovery task on day 4 [E10] sets emp to null, which is more recent than the database v1 (day -20) that [R1] relied on, so the current state is that the asset is no longer assigned to anyone.
```

## CASE 85: deepseek-v4-flash · full_load · s14 · W-00090 · class A · day 9 · template contract_gate
### Task as given to the requester
For Minjae (Senior): the highest equipment tier allowed right now under IT rules (grade and tier exceptions) and under the contract (allowed tier and legal exceptions) separately, whether standard equipment needs an NDA check step, and the contract expiry day.
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
{"it_tier": "basic", "contract_tier": "premium", "nda_step": true, "expiry": 84}
### Counterfactual answers (generator)
{"stale": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 84}, "partial": {"it_tier": "basic", "contract_tier": "standard", "nda_step": true, "expiry": 84}, "neardup": {"it_tier": "basic", "contract_tier": "premium", "nda_step": false, "expiry": 126}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-1006/profile** (group HR-SEL, class A, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-1006"}
- DB `HR-SEL/emp/E-SEL-1006/profile` v4 (recorded day 3, registered day 4): {"dept": "Customer Support Team", "grade": 2, "contract": "contractor", "hire_day": -111, "status": "active"}
**need IT-SEL/eligibility/E-SEL-1006** (group IT-SEL, class A, local=False)
- RULE IT-SEL.eligibility: {"id": "IT-SEL.eligibility", "group": "IT-SEL", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-SEL/E-SEL-1006/contract** (group LEGAL-SEL, class A, local=False)
- DB `LEGAL-SEL/contract/E-SEL-1006/terms` v2 (recorded day -13, registered day -11): {"allowed_tier": "standard", "expiry": 84, "nda": true}
- RULE LEGAL-SEL.contractor_policy: {"id": "LEGAL-SEL.contractor_policy", "group": "LEGAL-SEL", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-01042 [decision-critical] (operational/exception, day 1, by legal-sel.a1; DB shows n/a): Equipment exception of Oh Minjae higher tiers including premium allowed until day 27 for a project, legal check done.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 84, "it_tier": "basic", "nda_step": true}
official exact match: 1 (4/4 slots)

## CASE 86: deepseek-v4-flash · full_load · s14 · W-00120 · class A · day 12 · template diag
### Task as given to the requester
Invoice INV-61459 (280,204 KRW, beneficiary Hasegawa-san, asset A-TYO-76066, provisional approval CMT-00020) does not match. Find the cause.
[Request scope] target supplier=V-TYO-2; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"stale": null, "partial": null, "neardup": {"cause": "EMP_EXITED"}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-TYO/CMT-00020/status** (group FIN-TYO, class None, local=True)
- CATALOG: {"group": "FIN-TYO", "key": "commits/CMT-00020"}
- DB `FIN-TYO/commit/CMT-00020/status` v1 (recorded day -9, registered day -7): {"status": "cancelled", "amount": 280204, "expected_settle": -1}
**need HR-TYO/E-TYO-2015/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2015"}
- DB `HR-TYO/emp/E-TYO-2015/profile` v1 (recorded day 7, registered day 10): {"dept": "Sales Section 1", "grade": 1, "contract": "regular", "hire_day": 7, "status": "active"}
**need IT-TYO/E-TYO-2015/assets** (group IT-TYO, class A, local=False)
- QUERY SELECT asset WHERE holder=E-TYO-2015 → []
**need PROC-TYO/receipt/CMT-00020** (group PROC-TYO, class A, local=False)
- DB `PROC-TYO/receipt/CMT-00020/received` v1 (recorded day -3, registered day 0): true
**need PROC-TYO/vendor/V-TYO-2/status** (group PROC-TYO, class A, local=False)
- RECORD FR-01488 (operational/handover, day 9, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-2 exclude from comparisons until day 17 due to a quality issue.
**need FIN-TYO/rule/invoice_match_precedence** (group FIN-TYO, class None, local=True)
- RULE FIN-TYO.invoice_match_precedence: {"id": "FIN-TYO.invoice_match_precedence", "group": "FIN-TYO", "title": "Reporting invoice mismatch causes", "params": {"order": ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]}, "text": "If an invoice fails to match for several reasons, report only the first one in this order: EMP_EXITED > ASSET_NOT_REGISTERED > RECEIPT_MISSING > VENDOR_EXCLUDED > CONTRACT_EXPIRED > COMMIT_CANCELLED > COMMIT_NOT_CONFIRMED > AMOUNT_MISMATCH."}
### Model answer and official verdict
answer: {"cause": "COMMIT_CANCELLED"}
official exact match: 0 (0/1 slots)

## CASE 87: deepseek-v4-flash · full_load · s13 · W-00016 · class A · day 2 · template budget
### Task as given to the requester
How much budget can Dev Team 1 actually spend right now, after all deductions?
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
{"available": 2290215, "n_deducted": 2}
### Counterfactual answers (generator)
{"stale": {"available": 3569368, "n_deducted": 2}, "partial": {"available": 2440805, "n_deducted": 1}, "neardup": {"available": 2603231, "n_deducted": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/Dev Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- DB `FIN-SEL/line/Dev Team 1/remaining` v4 (recorded day -7, registered day -4): 3215666
- RULE FIN-SEL.pending_deduction: {"id": "FIN-SEL.pending_deduction", "group": "FIN-SEL", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00607 [decision-critical] (operational/pending_intent, day -9, by fin-sel.a1; DB shows n/a): Dev Team 1 capex 150,590 KRW earmarked for quarter-end consumables until day 4 (no voucher yet).
- DB `FIN-SEL/commit/CMT-00004/status` v2 (recorded day -10, registered day -9): {"status": "settled", "amount": 843331, "expected_settle": -10}
- DB `FIN-SEL/commit/CMT-00019/status` v2 (recorded day -2, registered day -1): {"status": "settled", "amount": 613302, "expected_settle": -2}
- DB `FIN-SEL/commit/CMT-00034/status` v2 (recorded day -2, registered day -1): {"status": "settled", "amount": 815110, "expected_settle": -2}
- QUERY SELECT commit WHERE group=FIN-SEL AND dept=Dev Team 1 AND status IN ['reviewing', 'pending'] → ["earmark:FR-00607", "CMT-00041"]
### Model answer and official verdict
answer: {"available": 2290215, "n_deducted": 2}
official exact match: 1 (2/2 slots)

## CASE 88: deepseek-v4-flash · full_load · s14 · W-00028 · class B · day 3 · template purchase
### Task as given to the requester
For Hashimoto-san's laptop request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
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
{"stale": {"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "budget"}, "partial": {"decision": "none", "option": null, "approver": null, "nda": null, "budget_after": null, "blocked_by": "budget"}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-2003/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-2003"}
- DB `HR-TYO/emp/E-TYO-2003/profile` v1 (recorded day -14, registered day -11): {"dept": "Planning Section", "grade": 2, "contract": "contractor", "hire_day": -14, "status": "active"}
**need FIN-TYO/Planning Section/budget_schedule** (group FIN-TYO, class A, local=False)
- RECORD FR-01116 [decision-critical] (db_pending/rationale, day 3, by fin-tyo.a1; DB shows 6): Planning Section capex balance adjusted to 4,458,134 KRW (division reallocation). Stored value: 4458134
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-00742 (operational/pending_intent, day -6, by fin-tyo.n0005; DB shows n/a): Planning Section capex 150,031 KRW earmarked for training equipment until day 7 (no voucher yet).
- RECORD FR-00954 (operational/pending_intent, day -1, by fin-tyo.a1; DB shows n/a): Planning Section capex 436,396 KRW earmarked for quarter-end consumables until day 8 (no voucher yet).
- RECORD FR-01064 (db_pending/observation, day 2, by fin-tyo.a2; DB shows ABSENT): CMT-00061 Planning Section provisional approval 890,302 KRW confirmed, settlement expected day 7. Stored value: {"amount":890302,"expected_settle":7,"status":"pending"}
- RECORD FR-00961 (operational/pending_intent, day 0, by fin-tyo.a3; DB shows n/a): CMT-00073 Planning Section meeting room equipment provisional approval 661,700 KRW under review, settlement expected day 13.
- RECORD FR-01008 (operational/pending_intent, day 1, by fin-tyo.a3; DB shows n/a): CMT-00083 Planning Section laptop provisional approval 987,862 KRW under review, settlement expected day 11.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Planning Section AND status IN ['reviewing', 'pending'] → ["earmark:FR-00742", "earmark:FR-00954", "CMT-00059", "CMT-00061", "CMT-00073", "CMT-00083"]
**need IT-TYO/eligibility/E-TYO-2003** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need PROC-TYO/quotes/laptop** (group PROC-TYO, class B, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00700 [decision-critical] (operational/handover, day -7, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-2 exclude from comparisons until day 6 due to a quality issue.
- RECORD FR-00826 (operational/handover, day -4, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-3 exclude from comparisons until day 4 due to a quality issue.
- RECORD FR-00964 (operational/handover, day 0, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 5 due to a quality issue.
- RECORD FR-01152 (operational/observation, day 3, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v2 (recorded day -1, registered day 0): 7
- DB `PROC-TYO/quote/Q-V-TYO-1-LTS/amount` v1 (recorded day -20, registered day -20): 1077364
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
- DB `PROC-TYO/quote/Q-V-TYO-2-LTB/amount` v2 (recorded day -16, registered day -13): 491606
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- DB `PROC-TYO/vendor/V-TYO-2/lead` v2 (recorded day -7, registered day -5): 3
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
**need LEGAL-TYO/residency** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.residency: {"id": "LEGAL-TYO.residency", "group": "LEGAL-TYO", "title": "Data residency", "params": {"restricted_depts": ["Dev Section 1", "Support Section"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Section 1, Support Section."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 53083, "decision": "order", "nda": false, "option": "Q-V-TYO-2-LTB"}
official exact match: 0 (0/6 slots)

## CASE 89: deepseek-v4-flash · full_load · s12 · W-00045 · class B · day 5 · template lookup
### Task as given to the requester
Check Seoyun (Manager)'s current department, grade and assets held.
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
{"dept": "Sales Team 1", "grade": 1, "assets": []}
### Counterfactual answers (generator)
{"stale": {"dept": "Sales Team 1", "grade": 2, "assets": []}, "partial": {"dept": "Sales Team 1", "grade": 2, "assets": []}, "neardup": {"dept": "Dev Team 1", "grade": 2, "assets": []}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-SEL/E-SEL-2013/profile** (group HR-SEL, class B, local=False)
- CATALOG: {"group": "HR-SEL", "key": "employees/E-SEL-2013"}
- RECORD FR-01149 [decision-critical] (db_pending/rationale, day 5, by hr-sel.a3; DB shows 1): HR record of Mo Seoyun changed to grade 1 (review result), Sales Team 1. Stored value: {"contract":"regular","dept":"Sales Team 1","grade":1,"hire_day":3,"status":"active"}
**need IT-SEL/E-SEL-2013/assets** (group IT-SEL, class A, local=False)
- QUERY SELECT asset WHERE holder=E-SEL-2013 → []
### Model answer and official verdict
answer: {"assets": [], "dept": "Sales Team 1", "grade": 2}
official exact match: 0 (2/3 slots)

## CASE 90: deepseek-v4-flash · full_load · s12 · W-00058 · class B · day 6 · template whatif
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
answer: {"available_then": 4314543, "later": false, "now": false}
official exact match: 1 (3/3 slots)

## CASE 91: deepseek-v4-flash · full_load · s14 · W-00115 · class C · day 12 · template alloc
### Task as given to the requester
Allocate IDE Pro seats to Sales Team 1, Customer Support Team, Sales Team 2 in that order, up to each team's planning headcount. If short, pull seats from another region; if still short, buy within budget.
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
{"alloc": [2, 4, 3], "transfer": 0, "buy": 9, "unmet": 0}
### Counterfactual answers (generator)
{"stale": {"alloc": [3, 4, 3], "transfer": 0, "buy": 10, "unmet": 0}, "partial": {"alloc": [3, 4, 3], "transfer": 0, "buy": 10, "unmet": 0}, "neardup": {"alloc": [3, 4, 3], "transfer": 0, "buy": 10, "unmet": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/license/IDE Pro** (group IT-SEL, class None, local=True)
- DB `IT-SEL/lic/IDE Pro/seats` v6 (recorded day 9, registered day 12): {"seats": 27, "used": 26}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01052 (operational/pending_intent, day 2, by it-sel.a2; DB shows n/a): IDE Pro seats 3 seats reserved for Customer Support Team onboarding until day 16.
- RECORD FR-01593 (operational/pending_intent, day 12, by it-sel.n0002; DB shows n/a): IDE Pro seats 3 seats reserved for Dev Team 1 onboarding until day 17.
**need HR-SEL/Sales Team 1/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1001/profile` v2 (recorded day -17, registered day -15): {"dept": "Sales Team 1", "grade": 4, "contract": "regular", "hire_day": -60, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1005/profile` v2 (recorded day -3, registered day -1): {"dept": "Marketing Team", "grade": 1, "contract": "contractor", "hire_day": -567, "status": "active"}
- RECORD FR-01620 [decision-critical] (db_pending/observation, day 12, by hr-sel.a3; DB shows 2): HR record of Seo Jian exit processed (Sales Team 1). Stored value: {"contract":"regular","dept":"Sales Team 1","grade":1,"hire_day":-560,"status":"exited"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v3 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -15, "status": "active"}
- NEGATIVE: {"query": "HR-SEL Sales Team 1 memos on confirmed hires / transfers within the horizon", "result": []}
- QUERY COUNT(emp WHERE region=SEL AND dept=Sales Team 1 AND status=active) → 2
**need HR-SEL/Customer Support Team/planning_headcount** (group HR-SEL, class C, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1003/profile` v2 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -675, "status": "active"}
- RECORD FR-01132 [decision-critical] (operational/pending_intent, day 3, by hr-sel.a5; DB shows n/a): Transfer of Han Siwoo approved from Marketing Team to Customer Support Team, effective day 13 (stays in Marketing Team until then).
- RECORD FR-01621 [decision-critical] (db_pending/observation, day 12, by hr-sel.a2; DB shows 4): HR record of Oh Minjae exit processed (Customer Support Team). Stored value: {"contract":"contractor","dept":"Customer Support Team","grade":2,"hire_day":-111,"status":"exited"}
- RECORD FR-01468 [decision-critical] (operational/pending_intent, day 9, by hr-sel.a5; DB shows n/a): Transfer of Shin Daeun approved from Dev Team 1 to Customer Support Team, effective day 13 (stays in Dev Team 1 until then).
- DB `HR-SEL/emp/E-SEL-1010/profile` v4 (recorded day 9, registered day 12): {"dept": "Customer Support Team", "grade": 5, "contract": "contractor", "hire_day": -385, "status": "active"}
- RECORD FR-01248 [decision-critical] (operational/pending_intent, day 5, by hr-sel.a5; DB shows n/a): Transfer of Song Yuna approved from Customer Support Team to Marketing Team, effective day 15 (stays in Customer Support Team until then).
- DB `HR-SEL/emp/E-SEL-1017/profile` v3 (recorded day -5, registered day -3): {"dept": "Customer Support Team", "grade": 5, "contract": "regular", "hire_day": -501, "status": "exited"}
- QUERY COUNT(emp WHERE region=SEL AND dept=Customer Support Team AND status=active) → 3
**need HR-SEL/Sales Team 2/planning_headcount** (group HR-SEL, class B, local=False)
- RULE HR-SEL.headcount_definition: {"id": "HR-SEL.headcount_definition", "group": "HR-SEL", "title": "Headcount definition", "params": {"count_status": "active"}, "text": "Headcount counts only employees in active status. Employees whose transfer is not yet effective count in their current department."}
- RULE HR-SEL.planning_headcount: {"id": "HR-SEL.planning_headcount", "group": "HR-SEL", "title": "Planning headcount for allocation", "params": {"horizon": 7, "include_confirmed_hires": true, "apply_transfers": true}, "text": "The planning headcount used for seat and equipment allocation is the headcount plus confirmed hires starting within 7 days from today, with transfers taking effect within 7 days counted in their new department."}
- DB `HR-SEL/emp/E-SEL-1002/profile` v3 (recorded day -2, registered day -1): {"dept": "Dev Team 1", "grade": 5, "contract": "contractor", "hire_day": -382, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1003/profile` v2 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -675, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1009/profile` v4 (recorded day 9, registered day 11): {"dept": "Dev Team 1", "grade": 1, "contract": "regular", "hire_day": -869, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1010/profile` v4 (recorded day 9, registered day 12): {"dept": "Customer Support Team", "grade": 5, "contract": "contractor", "hire_day": -385, "status": "active"}
- DB `HR-SEL/emp/E-SEL-1012/profile` v2 (recorded day -17, registered day -14): {"dept": "Sales Team 2", "grade": 1, "contract": "regular", "hire_day": -894, "status": "exited"}
- DB `HR-SEL/emp/E-SEL-1014/profile` v2 (recorded day -10, registered day -9): {"dept": "Dev Team 1", "grade": 4, "contract": "regular", "hire_day": -531, "status": "active"}
- DB `HR-SEL/emp/E-SEL-2002/profile` v3 (recorded day 8, registered day 10): {"dept": "Sales Team 2", "grade": 2, "contract": "contractor", "hire_day": -15, "status": "active"}
- RECORD FR-01305 [decision-critical] (operational/pending_intent, day 6, by hr-sel.a5; DB shows n/a): Transfer of Bong Seoha approved from Marketing Team to Sales Team 2, effective day 13 (stays in Marketing Team until then).
- QUERY COUNT(emp WHERE region=SEL AND dept=Sales Team 2 AND status=active) → 2
**need IT-TYO/license/IDE Pro** (group IT-TYO, class A, local=False)
- DB `IT-TYO/lic/IDE Pro/seats` v4 (recorded day 5, registered day 6): {"seats": 20, "used": 17}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01290 (operational/pending_intent, day 6, by it-tyo.w00194; DB shows n/a): IDE Pro seats 2 seats reserved for Dev Section 1 project until day 19.
- RECORD FR-01470 (operational/pending_intent, day 9, by it-tyo.w00233; DB shows n/a): IDE Pro seats 3 seats reserved for Sales Section 2 onboarding until day 19.
**need IT-SEL/rule/seat_transfer_share** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_transfer_share: {"id": "IT-SEL.seat_transfer_share", "group": "IT-SEL", "title": "Inter-region seat transfer", "params": {"share_num": 1, "share_den": 2}, "text": "Up to 1/2 (rounded down) of another region's free seats may be transferred."}
**need FIN-SEL/rule/seat_purchase_line** (group FIN-SEL, class A, local=False)
- RULE FIN-SEL.seat_purchase_line: {"id": "FIN-SEL.seat_purchase_line", "group": "FIN-SEL", "title": "Seat purchase budget", "params": {"charge_to": "first_team"}, "text": "Seat purchases are charged to the budget of the first team in the request list."}
**need FIN-SEL/Sales Team 1/budget_schedule** (group FIN-SEL, class A, local=False)
- RECORD FR-00725 (operational/exception, day -6, by fin-sel.n0004; DB shows n/a): Sales Team 1 capex executing office agreed that TYO finance executes it until day 13.
- RULE FIN-SEL.owner_exception: {"id": "FIN-SEL.owner_exception", "group": "FIN-SEL", "title": "Executing office arrangement", "params": {"exception_overrides_owner": true}, "text": "If it has been agreed that another region's finance office executes a department budget, that office executes it for the agreed period."}
**need FIN-TYO/Sales Team 1/budget_schedule** (group FIN-TYO, class A, local=False)
- DB `FIN-TYO/line/Sales Team 1/remaining` v1 (recorded day -6, registered day -4): 3755843
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- DB `FIN-TYO/commit/CMT-00060/status` v2 (recorded day 6, registered day 8): {"status": "settled", "amount": 892669, "expected_settle": 6}
- DB `FIN-TYO/commit/CMT-00065/status` v2 (recorded day 7, registered day 8): {"status": "settled", "amount": 987550, "expected_settle": 7}
- DB `FIN-TYO/commit/CMT-00067/status` v2 (recorded day 8, registered day 9): {"status": "settled", "amount": 956444, "expected_settle": 8}
- DB `FIN-TYO/commit/CMT-00081/status` v2 (recorded day 5, registered day 8): {"status": "settled", "amount": 431371, "expected_settle": 5}
- DB `FIN-TYO/commit/CMT-00091/status` v2 (recorded day 7, registered day 9): {"status": "settled", "amount": 437918, "expected_settle": 7}
- RECORD FR-01503 (db_pending/observation, day 10, by fin-tyo.a3; DB shows 1): CMT-00102 Sales Team 1 provisional approval settled. Stored value: {"amount":826711,"expected_settle":10,"status":"settled"}
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Sales Team 1 AND status IN ['reviewing', 'pending'] → ["CMT-00089"]
**need IT-SEL/rule/seat_price** (group IT-SEL, class None, local=True)
- RULE IT-SEL.seat_price: {"id": "IT-SEL.seat_price", "group": "IT-SEL", "title": "Standard seat price", "params": {"price": 256164}, "text": "When there is no supplier price, one seat costs 256,164 KRW."}
### Model answer and official verdict
answer: {"alloc": [0, 0, 0], "buy": 4, "transfer": 0, "unmet": 0}
official exact match: 0 (2/4 slots)