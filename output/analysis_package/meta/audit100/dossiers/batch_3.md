## CASE 27: qwen3.5-27b · ingress · s14 · W-00003 · class A · day 1 · template precedence
### Task as given to the requester
We got a request from Shimizu-san for a laptop (standard) at 1,523,099 KRW. Work out the approval route and which rule governs it.
[Request scope] item=laptop; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"approver": "division_head", "governing_rule": "tiers", "it_exception": false}
### Counterfactual answers (generator)
{"stale": {"approver": "division_head", "governing_rule": "q_exception", "it_exception": false}, "partial": null, "neardup": {"approver": "division_head", "governing_rule": "q_exception", "it_exception": true}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1017/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1017"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v3 (recorded day -7, registered day -6): {"dept": "Dev Section 2", "grade": 5, "contract": "contractor", "hire_day": -784, "status": "active"}
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
**need IT-TYO/eligibility/E-TYO-1017** (group IT-TYO, class None, local=True)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1017/contract** (group LEGAL-TYO, class A, local=False)
- RECORD FR-01012 (db_pending/observation, day 1, by legal-tyo.a3; DB shows 5): Contract of Shimizu Hayate extended to day 187, allowed tier standard, NDA no. Stored value: {"allowed_tier":"standard","expiry":187,"nda":false}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00338 (operational/exception, day -16, by legal-tyo.a3; DB shows n/a): Equipment exception of Shimizu Hayate higher tiers including premium allowed until day 12 for a project, legal check done.
### Model answer and official verdict
answer: {"approver": "division_head", "governing_rule": "tiers", "it_exception": false}
official exact match: 1 (3/3 slots)

## CASE 28: qwen3.5-27b · ingress · s14 · W-00086 · class B · day 9 · template lookup
### Task as given to the requester
Check Shimizu-san's current department, grade and assets held.
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
{"dept": "Dev Section 2", "grade": 5, "assets": ["A-TYO-6652", "A-TYO-7665", "A-TYO-78646"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Sales Section 2", "grade": 5, "assets": ["A-TYO-6652", "A-TYO-7665", "A-TYO-78646"]}, "partial": {"dept": "Dev Section 2", "grade": 5, "assets": ["A-TYO-6652", "A-TYO-7665"]}, "neardup": {"dept": "Dev Section 1", "grade": 1, "assets": ["A-TYO-6652", "A-TYO-7665", "A-TYO-78646"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1017/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1017"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v3 (recorded day -7, registered day -6): {"dept": "Dev Section 2", "grade": 5, "contract": "contractor", "hire_day": -784, "status": "active"}
**need IT-TYO/E-TYO-1017/assets** (group IT-TYO, class B, local=False)
- DB `IT-TYO/asset/A-TYO-6652/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1017"}
- DB `IT-TYO/asset/A-TYO-7665/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1017"}
- RECORD FR-01445 [decision-critical] (db_pending/observation, day 9, by it-tyo.w00227; DB shows ABSENT): A-TYO-78646 workstation Assigned to Shimizu Hayate. Stored value: {"emp":"E-TYO-1017"}
- QUERY SELECT asset WHERE holder=E-TYO-1017 → ["A-TYO-6652", "A-TYO-7665", "A-TYO-78646"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-6652", "A-TYO-7665", "A-TYO-78646"], "dept": "Dev Section 2", "grade": 5}
official exact match: 1 (3/3 slots)
### MATCHER CHECK FR-01445 (need IT-TYO/E-TYO-1017/assets): matcher says **missing**
record text: A-TYO-78646 workstation Assigned to Shimizu Hayate. Stored value: {"emp":"E-TYO-1017"}
What the requester received from IT-TYO during this task:
```
Employee E-TYO-1017 currently holds assets A-TYO-6652, A-TYO-7665, and A-TYO-78646. The first two were assigned on day -20 ([E4], [E5]), and the third was assigned today (day 9) via task W-00227 ([E13]). Reply R2 correctly lists all three, while R1 only reflects the older database state.
- E-TYO-1017 | asset IDs held | A-TYO-6652 |  | db, day -20: Reply 1: D1
- E-TYO-1017 | asset IDs held | A-TYO-7665 |  | db, day -20: Reply 1: D1
- E-TYO-1017 | asset_id | A-TYO-6652 |  | db, day -20: Reply 2: D1
- E-TYO-1017 | asset_id | A-TYO-7665 |  | db, day -20: Reply 2: D1
- E-TYO-1017 | asset_id | A-TYO-78646 |  | history, day 9: Reply 2: H6
- E-TYO-1017 | asset IDs held | A-TYO-6652 |  | history, day -20: [E4]
- E-TYO-1017 | asset IDs held | A-TYO-7665 |  | history, day -20: [E5]
- E-TYO-1017 | asset IDs held | A-TYO-78646 |  | history, day 9: [E13]
```

## CASE 29: qwen3.5-27b · ingress · s12 · W-00063 · class B · day 7 · template sourcing
### Task as given to the requester
Dev Section 1 will place a department order for a laptop. List the usable quotes right now from cheapest, with quote amount and actual lead time.
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"options": [["Q-V-TYO-1-LTB", 526387, 5], ["Q-V-TYO-1-LTP", 1663952, 5]]}
### Counterfactual answers (generator)
{"stale": {"options": [["Q-V-TYO-1-LTB", 526387, 7], ["Q-V-TYO-1-LTP", 1663952, 5]]}, "partial": {"options": [["Q-V-TYO-3-LTB", 484258, 9], ["Q-V-TYO-1-LTB", 526387, 5], ["Q-V-TYO-1-LTP", 1663952, 5], ["Q-V-TYO-3-LTP", 1931331, 9]]}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need PROC-TYO/quotes/laptop** (group PROC-TYO, class B, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-00981 (operational/handover, day 1, by proc-tyo.n0002; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 8 due to a quality issue.
- RECORD FR-00891 [decision-critical] (operational/observation, day -1, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 2 days until day 7.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-00982 (operational/observation, day 1, by proc-tyo.a4; DB shows n/a): Supplier V-TYO-0 delivery notified: deliveries delayed by 3 days until day 8.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01036 (operational/observation, day 2, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 5 days until day 16.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 4, registered day 7): 8
- RECORD FR-01239 (db_pending/rationale, day 6, by proc-tyo.a1; DB shows 2): V-TYO-0 laptop (basic) quote Q-V-TYO-0-LTB changed to 752,760 KRW (raw material prices). Stored value: 752760
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-0-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-0"}
- DB `PROC-TYO/vendor/V-TYO-0/lead` v3 (recorded day 4, registered day 7): 8
- RECORD FR-01154 (db_pending/rationale, day 5, by proc-tyo.a1; DB shows 3): V-TYO-0 laptop (premium) quote Q-V-TYO-0-LTP changed to 2,488,260 KRW (raw material prices). Stored value: 2488260
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
- RECORD FR-01266 [decision-critical] (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTB/amount` v1 (recorded day -20, registered day -20): 704358
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01266 [decision-critical] (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTP/amount` v2 (recorded day 1, registered day 2): 2395030
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01266 [decision-critical] (db_pending/observation, day 7, by proc-tyo.a3; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 11
- DB `PROC-TYO/quote/Q-V-TYO-2-LTS/amount` v2 (recorded day -2, registered day 1): 1050981
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v3 (recorded day -1, registered day 1): 9
- DB `PROC-TYO/quote/Q-V-TYO-3-LTB/amount` v1 (recorded day -20, registered day -20): 484258
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-3-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-3"}
- DB `PROC-TYO/vendor/V-TYO-3/lead` v3 (recorded day -1, registered day 1): 9
- DB `PROC-TYO/quote/Q-V-TYO-3-LTP/amount` v3 (recorded day -3, registered day -1): 1931331
### Model answer and official verdict
answer: {"options": [["Q-V-TYO-1-LTB", 526387, 5], ["Q-V-TYO-2-LTB", 704358, 7], ["Q-V-TYO-2-LTS", 1050981, 7], ["Q-V-TYO-1-LTP", 1663952, 5], ["Q-V-TYO-2-LTP", 2395030, 7]]}
official exact match: 0 (0/1 slots)
### MATCHER CHECK FR-00891 (need PROC-TYO/quotes/laptop): matcher says **missing**
record text: Supplier V-TYO-3 delivery notified: deliveries delayed by 2 days until day 7.
What the requester received from PROC-TYO during this task:
```
Confirmed 5 usable quotes from V-TYO-1 and V-TYO-2. V-TYO-0 is excluded until day 8, V-TYO-3 is unregistered. Corrected lead times for V-TYO-0 (4) and V-TYO-2 (7). Added missing quote Q-V-TYO-2-LTS. Item records for INV-TYO-* and Dev Section 1 info remain unconfirmed.
- Q-V-TYO-0-LTB | quote_id | Q-V-TYO-0-LTB |  | db, day fixed: Reply 1: D4
- Q-V-TYO-0-LTB | amount | 840454 |  | db, day 2: Reply 1: D12
- Q-V-TYO-0-LTB | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-0-LTP | quote_id | Q-V-TYO-0-LTP |  | db, day fixed: Reply 1: D5
- Q-V-TYO-0-LTP | amount | 1703927 |  | db, day -1: Reply 1: D13
- Q-V-TYO-0-LTP | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-1-LTB | quote_id | Q-V-TYO-1-LTB |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTB | amount | 526387 |  | db, day -20: Reply 1: D14
- Q-V-TYO-1-LTB | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-1-LTP | quote_id | Q-V-TYO-1-LTP |  | db, day fixed: Reply 1: D7
- Q-V-TYO-1-LTP | amount | 1663952 |  | db, day -9: Reply 1: D15
- Q-V-TYO-1-LTP | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D8
- Q-V-TYO-2-LTB | amount | 704358 |  | db, day -20: Reply 1: D16
- Q-V-TYO-2-LTB | lead_time | 5 |  | db, day 6: Reply 1: D22
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D9
- Q-V-TYO-2-LTP | amount | 2395030 |  | db, day 2: Reply 1: D17
- Q-V-TYO-2-LTP | lead_time | 5 |  | db, day 6: Reply 1: D22
- V-TYO-0 | vendor_registration | true |  | db, day -20: Reply 1: D24
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D25
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D26
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D27
- department order | lead time limit | 10 days |  | rule, day fixed: Reply 1: lead_time_limit
- Q-V-TYO-2-LTS | amount | 1050981 |  | history, day 2: [E2]
- V-TYO-0 | vendor_lead_time | 4 |  | history, day 5: [E4]
- V-TYO-2 | vendor_lead_time | 7 |  | history, day 5: [E4]
- V-TYO-0 | exclusion status | exclude from comparisons until day 8 | until day 8 | history, day 2: [E3]
missing: INV-TYO-LTB item record; INV-TYO-LTP item record; INV-TYO-LTS item record; Dev Section 1 department information
conflict: V-TYO-0 quotes usability: R1 lists V-TYO-0 quotes as usable, but records show V-TYO-0 is excluded from comparisons until day 8 (active on day 7). ([R1] [E3] [S5])
conflict: V-TYO-0 lead time: R1 states lead time 8, but latest record [E4] (day 4) shows 4. ([R1] [E4])
conflict: V-TYO-2 lead time: R1 states lead time 5, but record [E4] shows 7. ([R1] [E4])
conflict: Q-V-TYO-2-LTS inclusion: R1 omits Q-V-TYO-2-LTS, which exists in records with amount 1050981. ([R1] [E2])
proposed: Usable quotes for department order = Q-V-TYO-1-LTB (526387, 5d), Q-V-TYO-1-LTP (1663952, 5d), Q-V-TYO-2-LTB (704358, 7d), Q-V-TYO-2-LTS (1050981, 7d), Q-V-TYO-2-LTP (2395030, 7d) ([E2] [E4] [S5]) — V-TYO-0 is excluded until day 8 and V-TYO-3 is unregistered; V-TYO-1 and V-TYO-2 meet the ≤10 day lead time limit for department orders.
proposed: V-TYO-0 lead time = 4 ([E4]) — Latest record (day 4) overrides the earlier value of 8.
proposed: V-TYO-2 lead time = 7 ([E4]) — Record shows lead time 7, overriding R1's value of 5.
```
### MATCHER CHECK FR-01266 (need PROC-TYO/quotes/laptop): matcher says **stale**
record text: Supplier V-TYO-2 lead time change notice applied. Stored value: 11
What the requester received from PROC-TYO during this task:
```
Confirmed 5 usable quotes from V-TYO-1 and V-TYO-2. V-TYO-0 is excluded until day 8, V-TYO-3 is unregistered. Corrected lead times for V-TYO-0 (4) and V-TYO-2 (7). Added missing quote Q-V-TYO-2-LTS. Item records for INV-TYO-* and Dev Section 1 info remain unconfirmed.
- Q-V-TYO-0-LTB | quote_id | Q-V-TYO-0-LTB |  | db, day fixed: Reply 1: D4
- Q-V-TYO-0-LTB | amount | 840454 |  | db, day 2: Reply 1: D12
- Q-V-TYO-0-LTB | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-0-LTP | quote_id | Q-V-TYO-0-LTP |  | db, day fixed: Reply 1: D5
- Q-V-TYO-0-LTP | amount | 1703927 |  | db, day -1: Reply 1: D13
- Q-V-TYO-0-LTP | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-1-LTB | quote_id | Q-V-TYO-1-LTB |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTB | amount | 526387 |  | db, day -20: Reply 1: D14
- Q-V-TYO-1-LTB | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-1-LTP | quote_id | Q-V-TYO-1-LTP |  | db, day fixed: Reply 1: D7
- Q-V-TYO-1-LTP | amount | 1663952 |  | db, day -9: Reply 1: D15
- Q-V-TYO-1-LTP | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D8
- Q-V-TYO-2-LTB | amount | 704358 |  | db, day -20: Reply 1: D16
- Q-V-TYO-2-LTB | lead_time | 5 |  | db, day 6: Reply 1: D22
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D9
- Q-V-TYO-2-LTP | amount | 2395030 |  | db, day 2: Reply 1: D17
- Q-V-TYO-2-LTP | lead_time | 5 |  | db, day 6: Reply 1: D22
- V-TYO-0 | vendor_registration | true |  | db, day -20: Reply 1: D24
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D25
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D26
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D27
- department order | lead time limit | 10 days |  | rule, day fixed: Reply 1: lead_time_limit
- Q-V-TYO-2-LTS | amount | 1050981 |  | history, day 2: [E2]
- V-TYO-0 | vendor_lead_time | 4 |  | history, day 5: [E4]
- V-TYO-2 | vendor_lead_time | 7 |  | history, day 5: [E4]
- V-TYO-0 | exclusion status | exclude from comparisons until day 8 | until day 8 | history, day 2: [E3]
missing: INV-TYO-LTB item record; INV-TYO-LTP item record; INV-TYO-LTS item record; Dev Section 1 department information
conflict: V-TYO-0 quotes usability: R1 lists V-TYO-0 quotes as usable, but records show V-TYO-0 is excluded from comparisons until day 8 (active on day 7). ([R1] [E3] [S5])
conflict: V-TYO-0 lead time: R1 states lead time 8, but latest record [E4] (day 4) shows 4. ([R1] [E4])
conflict: V-TYO-2 lead time: R1 states lead time 5, but record [E4] shows 7. ([R1] [E4])
conflict: Q-V-TYO-2-LTS inclusion: R1 omits Q-V-TYO-2-LTS, which exists in records with amount 1050981. ([R1] [E2])
proposed: Usable quotes for department order = Q-V-TYO-1-LTB (526387, 5d), Q-V-TYO-1-LTP (1663952, 5d), Q-V-TYO-2-LTB (704358, 7d), Q-V-TYO-2-LTS (1050981, 7d), Q-V-TYO-2-LTP (2395030, 7d) ([E2] [E4] [S5]) — V-TYO-0 is excluded until day 8 and V-TYO-3 is unregistered; V-TYO-1 and V-TYO-2 meet the ≤10 day lead time limit for department orders.
proposed: V-TYO-0 lead time = 4 ([E4]) — Latest record (day 4) overrides the earlier value of 8.
proposed: V-TYO-2 lead time = 7 ([E4]) — Record shows lead time 7, overriding R1's value of 5.
```
### MATCHER CHECK FR-01266 (need PROC-TYO/quotes/laptop): matcher says **stale**
record text: Supplier V-TYO-2 lead time change notice applied. Stored value: 11
What the requester received from PROC-TYO during this task:
```
Confirmed 5 usable quotes from V-TYO-1 and V-TYO-2. V-TYO-0 is excluded until day 8, V-TYO-3 is unregistered. Corrected lead times for V-TYO-0 (4) and V-TYO-2 (7). Added missing quote Q-V-TYO-2-LTS. Item records for INV-TYO-* and Dev Section 1 info remain unconfirmed.
- Q-V-TYO-0-LTB | quote_id | Q-V-TYO-0-LTB |  | db, day fixed: Reply 1: D4
- Q-V-TYO-0-LTB | amount | 840454 |  | db, day 2: Reply 1: D12
- Q-V-TYO-0-LTB | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-0-LTP | quote_id | Q-V-TYO-0-LTP |  | db, day fixed: Reply 1: D5
- Q-V-TYO-0-LTP | amount | 1703927 |  | db, day -1: Reply 1: D13
- Q-V-TYO-0-LTP | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-1-LTB | quote_id | Q-V-TYO-1-LTB |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTB | amount | 526387 |  | db, day -20: Reply 1: D14
- Q-V-TYO-1-LTB | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-1-LTP | quote_id | Q-V-TYO-1-LTP |  | db, day fixed: Reply 1: D7
- Q-V-TYO-1-LTP | amount | 1663952 |  | db, day -9: Reply 1: D15
- Q-V-TYO-1-LTP | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D8
- Q-V-TYO-2-LTB | amount | 704358 |  | db, day -20: Reply 1: D16
- Q-V-TYO-2-LTB | lead_time | 5 |  | db, day 6: Reply 1: D22
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D9
- Q-V-TYO-2-LTP | amount | 2395030 |  | db, day 2: Reply 1: D17
- Q-V-TYO-2-LTP | lead_time | 5 |  | db, day 6: Reply 1: D22
- V-TYO-0 | vendor_registration | true |  | db, day -20: Reply 1: D24
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D25
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D26
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D27
- department order | lead time limit | 10 days |  | rule, day fixed: Reply 1: lead_time_limit
- Q-V-TYO-2-LTS | amount | 1050981 |  | history, day 2: [E2]
- V-TYO-0 | vendor_lead_time | 4 |  | history, day 5: [E4]
- V-TYO-2 | vendor_lead_time | 7 |  | history, day 5: [E4]
- V-TYO-0 | exclusion status | exclude from comparisons until day 8 | until day 8 | history, day 2: [E3]
missing: INV-TYO-LTB item record; INV-TYO-LTP item record; INV-TYO-LTS item record; Dev Section 1 department information
conflict: V-TYO-0 quotes usability: R1 lists V-TYO-0 quotes as usable, but records show V-TYO-0 is excluded from comparisons until day 8 (active on day 7). ([R1] [E3] [S5])
conflict: V-TYO-0 lead time: R1 states lead time 8, but latest record [E4] (day 4) shows 4. ([R1] [E4])
conflict: V-TYO-2 lead time: R1 states lead time 5, but record [E4] shows 7. ([R1] [E4])
conflict: Q-V-TYO-2-LTS inclusion: R1 omits Q-V-TYO-2-LTS, which exists in records with amount 1050981. ([R1] [E2])
proposed: Usable quotes for department order = Q-V-TYO-1-LTB (526387, 5d), Q-V-TYO-1-LTP (1663952, 5d), Q-V-TYO-2-LTB (704358, 7d), Q-V-TYO-2-LTS (1050981, 7d), Q-V-TYO-2-LTP (2395030, 7d) ([E2] [E4] [S5]) — V-TYO-0 is excluded until day 8 and V-TYO-3 is unregistered; V-TYO-1 and V-TYO-2 meet the ≤10 day lead time limit for department orders.
proposed: V-TYO-0 lead time = 4 ([E4]) — Latest record (day 4) overrides the earlier value of 8.
proposed: V-TYO-2 lead time = 7 ([E4]) — Record shows lead time 7, overriding R1's value of 5.
```
### MATCHER CHECK FR-01266 (need PROC-TYO/quotes/laptop): matcher says **stale**
record text: Supplier V-TYO-2 lead time change notice applied. Stored value: 11
What the requester received from PROC-TYO during this task:
```
Confirmed 5 usable quotes from V-TYO-1 and V-TYO-2. V-TYO-0 is excluded until day 8, V-TYO-3 is unregistered. Corrected lead times for V-TYO-0 (4) and V-TYO-2 (7). Added missing quote Q-V-TYO-2-LTS. Item records for INV-TYO-* and Dev Section 1 info remain unconfirmed.
- Q-V-TYO-0-LTB | quote_id | Q-V-TYO-0-LTB |  | db, day fixed: Reply 1: D4
- Q-V-TYO-0-LTB | amount | 840454 |  | db, day 2: Reply 1: D12
- Q-V-TYO-0-LTB | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-0-LTP | quote_id | Q-V-TYO-0-LTP |  | db, day fixed: Reply 1: D5
- Q-V-TYO-0-LTP | amount | 1703927 |  | db, day -1: Reply 1: D13
- Q-V-TYO-0-LTP | lead_time | 8 |  | db, day 7: Reply 1: D20
- Q-V-TYO-1-LTB | quote_id | Q-V-TYO-1-LTB |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTB | amount | 526387 |  | db, day -20: Reply 1: D14
- Q-V-TYO-1-LTB | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-1-LTP | quote_id | Q-V-TYO-1-LTP |  | db, day fixed: Reply 1: D7
- Q-V-TYO-1-LTP | amount | 1663952 |  | db, day -9: Reply 1: D15
- Q-V-TYO-1-LTP | lead_time | 5 |  | db, day -5: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D8
- Q-V-TYO-2-LTB | amount | 704358 |  | db, day -20: Reply 1: D16
- Q-V-TYO-2-LTB | lead_time | 5 |  | db, day 6: Reply 1: D22
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D9
- Q-V-TYO-2-LTP | amount | 2395030 |  | db, day 2: Reply 1: D17
- Q-V-TYO-2-LTP | lead_time | 5 |  | db, day 6: Reply 1: D22
- V-TYO-0 | vendor_registration | true |  | db, day -20: Reply 1: D24
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D25
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D26
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D27
- department order | lead time limit | 10 days |  | rule, day fixed: Reply 1: lead_time_limit
- Q-V-TYO-2-LTS | amount | 1050981 |  | history, day 2: [E2]
- V-TYO-0 | vendor_lead_time | 4 |  | history, day 5: [E4]
- V-TYO-2 | vendor_lead_time | 7 |  | history, day 5: [E4]
- V-TYO-0 | exclusion status | exclude from comparisons until day 8 | until day 8 | history, day 2: [E3]
missing: INV-TYO-LTB item record; INV-TYO-LTP item record; INV-TYO-LTS item record; Dev Section 1 department information
conflict: V-TYO-0 quotes usability: R1 lists V-TYO-0 quotes as usable, but records show V-TYO-0 is excluded from comparisons until day 8 (active on day 7). ([R1] [E3] [S5])
conflict: V-TYO-0 lead time: R1 states lead time 8, but latest record [E4] (day 4) shows 4. ([R1] [E4])
conflict: V-TYO-2 lead time: R1 states lead time 5, but record [E4] shows 7. ([R1] [E4])
conflict: Q-V-TYO-2-LTS inclusion: R1 omits Q-V-TYO-2-LTS, which exists in records with amount 1050981. ([R1] [E2])
proposed: Usable quotes for department order = Q-V-TYO-1-LTB (526387, 5d), Q-V-TYO-1-LTP (1663952, 5d), Q-V-TYO-2-LTB (704358, 7d), Q-V-TYO-2-LTS (1050981, 7d), Q-V-TYO-2-LTP (2395030, 7d) ([E2] [E4] [S5]) — V-TYO-0 is excluded until day 8 and V-TYO-3 is unregistered; V-TYO-1 and V-TYO-2 meet the ≤10 day lead time limit for department orders.
proposed: V-TYO-0 lead time = 4 ([E4]) — Latest record (day 4) overrides the earlier value of 8.
proposed: V-TYO-2 lead time = 7 ([E4]) — Record shows lead time 7, overriding R1's value of 5.
```

## CASE 30: qwen3.5-27b · ingress · s13 · W-00108 · class B · day 11 · template conflict
### Task as given to the requester
Check whether CMT-00094 is still live and what amount to count for it. We are hearing conflicting things.
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
{"status": "reviewing", "amount": 385129}
### Counterfactual answers (generator)
{"stale": null, "partial": {"status": "none", "amount": 0}, "neardup": {"status": "reviewing", "amount": 844791}, "wrong_owner": null}
### World facts behind the gold (by need)
**need FIN-SEL/CMT-00094/effective_status** (group FIN-SEL, class B, local=False)
- NEGATIVE: {"query": "FIN-SEL catalog commits/CMT-00094", "result": []}
- RECORD FR-01452 [decision-critical] (operational/pending_intent, day 9, by fin-sel.n0004; DB shows n/a): CMT-00094 Marketing Team workstation provisional approval 385,129 KRW under review, settlement expected day 17.
- RULE FIN-SEL.status_authority: {"id": "FIN-SEL.status_authority", "group": "FIN-SEL", "title": "Validity of provisional approval status", "params": {"authoritative": ["db", "owner_record"], "informal_excluded": true}, "text": "Only the registered record and the handling officer's processing record determine a provisional approval's status. Informal remarks or discussions do not change it."}
### Model answer and official verdict
answer: {"amount": 385129, "status": "reviewing"}
official exact match: 1 (2/2 slots)
### MATCHER CHECK FR-01452 (need FIN-SEL/CMT-00094/effective_status): matcher says **delivered**
record text: CMT-00094 Marketing Team workstation provisional approval 385,129 KRW under review, settlement expected day 17.
What the requester received from FIN-SEL during this task:
```
Confirmed CMT-00094 status (under review) and amount (385,129 KRW) from record [E23]; added department, item, and expected settlement day not included in the reply.
- CMT-00094 | status | under review |  | history, day 9: Reply 1: H346
- CMT-00094 | amount | 385,129 KRW |  | history, day 9: Reply 1: H346
- CMT-00094 | department | Marketing Team |  | history, day 9: [E23]
- CMT-00094 | item | workstation |  | history, day 9: [E23]
- CMT-00094 | expected_settle | day 17 |  | history, day 9: [E23]
---
CMT-00094 is confirmed to be under review as of day 11 with no status change since day 9. The amount is 385,129 KRW and expected settlement day is 17, based on record [E28] from day 9.
- CMT-00094 | status | under review |  | history, day 9: Reply 1: H346
- CMT-00094 | amount | 385,129 KRW |  | history, day 9: Reply 1: H346
- CMT-00094 | expected settlement day | 17 |  | history, day 9: Reply 1: H346
- CMT-00094 | database status | NOT_FOUND |  | db, day unknown: Reply 1: D1
- CMT-00094 | status | under review | under review | history, day 9: [E28]
- CMT-00094 | amount | 385,129 KRW |  | history, day 9: [E28]
- CMT-00094 | expected settlement day | 17 |  | history, day 9: [E28]
```

## CASE 31: qwen3.5-27b · ingress · s13 · W-00116 · class C · day 12 · template budget
### Task as given to the requester
How much budget can Sales Team 2 actually spend right now, after all deductions?
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
{"available": 976566, "n_deducted": 3}
### Counterfactual answers (generator)
{"stale": {"available": 1753481, "n_deducted": 3}, "partial": {"available": 2309950, "n_deducted": 4}, "neardup": {"available": 1612792, "n_deducted": 1}, "wrong_owner": {"available": 2309950, "n_deducted": 4}}
### World facts behind the gold (by need)
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
### Model answer and official verdict
answer: {"available": 3121391, "n_deducted": 2}
official exact match: 0 (0/2 slots)
### MATCHER CHECK FR-01347 (need FIN-SEL/Sales Team 2/budget_schedule): matcher says **missing**
record text: Sales Team 2 capex executing office agreed that TYO finance executes it until day 28.
What the requester received from FIN-SEL during this task:
```
Sales Team 2 has a budget line balance of 3,690,872 KRW. After deducting two active earmarks (totaling 569,481 KRW), the available budget is 3,121,391 KRW. No provisional approvals are currently deducted as all are settled or cancelled.
- Sales Team 2 | remaining capex budget | 3690872 |  | db, day 11: Reply 1: D1
- Sales Team 2 | department provisional approvals | CMT-00002 (settled, 349589 KRW, expected_settle -9), CMT-00005 (settled, 584884 KRW, expected_settle -10), CMT-00010 (settled, 254702 KRW, expected_settle -10), CMT-00059 (settled, 632153 KRW, expected_settle 5), CMT-00061 (settled, 448322 KRW, expected_settle 8), CMT-00065 (settled, 487593 KRW, expected_settle 6), CMT-00072 (cancelled, 498905 KRW, expected_settle 13) | all settled or cancelled | db, day unknown: Reply 1: D2
- Sales Team 2 | earmark for meeting room replacement | 285019 KRW until day 16 |  | history, day 9: Reply 1: H356
- Sales Team 2 | earmark for new-hire equipment | 284462 KRW until day 24 |  | history, day 10: Reply 1: H369
- Sales Team 2 | count of deducted provisional approvals | 0 |  | db, day unknown: Reply 1: calculated from D2 and rule pending_deduction
- Sales Team 2 | count of active earmarks | 2 |  | history, day 9: Reply 1: H356, H369
- Sales Team 2 | sum of earmarks in validity period | 569481 KRW |  | history, day 9: Reply 1: calculated from H356, H369
- Sales Team 2 | available budget | 3121391 KRW |  | db, day 11: Reply 1: calculated from D1, H356, H369 using rule pending_deduction
- Sales Team 2 | budget_line_balance | 3690872 |  | db, day 11: Reply 2: D1
- Sales Team 2 | budget_line_base | 2683779 |  | db, day -20: Reply 2: D2
- CMT-00002 | provisional_approval status | settled | settled | db, day -7: Reply 2: D3
- CMT-00005 | provisional_approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00010 | provisional_approval status | settled | settled | db, day -8: Reply 2: D3
- CMT-00059 | provisional_approval status | settled | settled | db, day 7: Reply 2: D3
- CMT-00061 | provisional_approval status | settled | settled | db, day 9: Reply 2: D3
- CMT-00065 | provisional_approval status | settled | settled | db, day 10: Reply 2: D3
- CMT-00072 | provisional_approval status | cancelled | cancelled | db, day 10: Reply 2: D3
- Sales Team 2 | budget_line_balance | 3690872 |  | db, day 11: Reply 3: D1
- Sales Team 2 | budget_line_base | 2683779 |  | db, day -20: Reply 3: D2
- CMT-00002 | amount | 349589 | settled | db, day -7: Reply 3: D3
- CMT-00002 | expected_settle | -9 | settled | db, day -7: Reply 3: D3
- CMT-00005 | amount | 584884 | settled | db, day -8: Reply 3: D3
- CMT-00005 | expected_settle | -10 | settled | db, day -8: Reply 3: D3
- CMT-00010 | amount | 254702 | settled | db, day -8: Reply 3: D3
- CMT-00010 | expected_settle | -10 | settled | db, day -8: Reply 3: D3
- CMT-00059 | amount | 632153 | settled | db, day 7: Reply 3: D3
- CMT-00059 | expected_settle | 5 | settled | db, day 7: Reply 3: D3
- CMT-00061 | amount | 448322 | settled | db, day 9: Reply 3: D3
- CMT-00061 | expected_settle | 8 | settled | db, day 9: Reply 3: D3
- CMT-00065 | amount | 487593 | settled | db, day 10: Reply 3: D3
- CMT-00065 | expected_settle | 6 | settled | db, day 10: Reply 3: D3
- CMT-00072 | amount | 498905 | cancelled | db, day 10: Reply 3: D3
- CMT-00072 | expected_settle | 13 | cancelled | db, day 10: Reply 3: D3
- Sales Team 2 | available_budget | 3690872 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Sales Team 2 | budget line balance | 3690872 |  | db, day 11: Reply 4: D1
- Sales Team 2 | active earmarks | none |  | history, day -7: Reply 4: H30
- Sales Team 2 | budget_line_balance | 3690872 |  | db, day 11: Reply 5: D1
- Sales Team 2 | available budget | 3690872 |  | db, day 11: Reply 5: calculated from D1 and D2
- Sales Team 2 | active earmarks | none found |  | unknown, day unknown: Reply 5: missing
- Sales Team 2 | remaining capex budget | 3690872 |  | db, day 11: Reply 6: D1
- Sales Team 2 | available budget | 3690872 |  | db, day 11: Reply 6: D1
- Sales Team 2 | remaining capex budget | 3690872 |  | db, day 11: Reply 7: D1
- Sales Team 2 | earmark (meeting room replacement) | 285019 KRW until day 16 |  | history, day 9: Reply 7: H356
- Sales Team 2 | earmark (new-hire equipment) | 284462 KRW until day 24 |  | history, day 10: Reply 7: H369
- Sales Team 2 | available budget | 3121391 KRW |  | db, day 11: Reply 7: calculated from D1, H356, H369
- Sales Team 2 | budget_line_balance | 3690872 |  | db, day 11: Reply 8: D1
- Sales Team 2 | available budget | 3690872 |  | db, day 11: Reply 8: calculated from D1 using pending_deduction rule
- Sales Team 2 | active earmarks | 0 |  | unknown, day unknown: Reply 8: missing
- Sales Team 2 | remaining capex budget | 3690872 |  | db, day 11: [V7]
- Sales Team 2 | earmark for meeting room replacement | 285019 KRW until day 16 |  | history, day 9: [R1]
- Sales Team 2 | earmark for new-hire equipment | 284462 KRW until day 24 |  | history, day 10: [R1]
- Sales Team 2 | count of deducted provisional approvals | 0 |  | db, day unknown: [R1]
- Sales Team 2 | available budget | 3121391 KRW |  | db, day 11: [R1]
missing: Available budget for Sales Team 2; Active earmarks for Sales Team 2
conflict: Earmarks affecting Sales Team 2 budget: [R2] and [R3] state no earmarks were found, but [R1] and group records confirm two active earmarks (285,019 KRW until day 16 and 284,462 KRW until day 24). ([R1] [R2] [R3])
conflict: Available budget: [R3] states available budget is 3,690,872 KRW (equal to line balance), but correct calculation subtracts earmarks to get 3,121,391 KRW. ([R1] [R3])
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

## CASE 32: qwen3.5-27b · ingress · s13 · W-00045 · class C · day 5 · template contract_gate
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
{"it_tier": "premium", "contract_tier": "premium", "nda_step": false, "expiry": 222}
### Counterfactual answers (generator)
{"stale": null, "partial": {"it_tier": "premium", "contract_tier": "standard", "nda_step": false, "expiry": 222}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1012/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1012"}
- DB `HR-TYO/emp/E-TYO-1012/profile` v3 (recorded day -10, registered day -9): {"dept": "Dev Section 1", "grade": 5, "contract": "contractor", "hire_day": -90, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1012** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1012/contract** (group LEGAL-TYO, class C, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1012/terms` v8 (recorded day 1, registered day 3): {"allowed_tier": "standard", "expiry": 222, "nda": true}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00500 [decision-critical] (operational/exception, day -12, by legal-tyo.a3; DB shows n/a): Equipment exception of Yamada Sou higher tiers including premium allowed until day 12 for a project, legal check done.
- RECORD FR-01092 [decision-critical] (operational/observation, day 3, by legal-tyo.n0017; DB shows n/a): NDA of Yamada Sou signed copy verified, NDA check step can be skipped until day 25.
### Model answer and official verdict
answer: {"contract_tier": "premium", "expiry": 222, "it_tier": "premium", "nda_step": false}
official exact match: 1 (4/4 slots)
### MATCHER CHECK FR-00500 (need LEGAL-TYO/E-TYO-1012/contract): matcher says **delivered**
record text: Equipment exception of Yamada Sou higher tiers including premium allowed until day 12 for a project, legal check done.
What the requester received from LEGAL-TYO during this task:
```
The highest allowed tier is premium due to an active exception until day 12. An NDA check is skipped until day 25. Contract expires day 222.
- E-TYO-1012 | allowed equipment tier | standard |  | db, day 3: Reply 1: D1
- E-TYO-1012 | contract expiry day | 222 |  | db, day 3: Reply 1: D1
- E-TYO-1012 | NDA required in contract | true |  | db, day 3: Reply 1: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 2: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 2: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 2: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 3: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 3: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 3: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 4: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 4: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 4: D1
- E-TYO-1012 | NDA check status | signed copy verified, NDA check step can be skipped until day 25 |  | history, day 3: Reply 4: H23
- E-TYO-1012 | legal exception | higher tiers including premium allowed until day 12 | active until day 12 | history, day -12: [E5]
conflict: Legal exceptions modifying allowed tier: R4 states 'No legal exception record found', but [E5] records an exception allowing premium tiers. ([R4] [E5])
conflict: NDA check status: [E3] states NDA check can be skipped until day 0, while R4 cites a record (day 3) stating it can be skipped until day 25. ([E3] [R4])
proposed: Highest equipment tier allowed = premium ([E5] [V8]) — While the contract base tier is standard, the exception in [E5] allows premium tiers until day 12, which is still in effect on day 5.
proposed: Legal exceptions modifying allowed tier = higher tiers including premium allowed until day 12 ([E5]) — [E5] is a valid record from day -12 stating the exception is active until day 12, contradicting R4's claim of no record.
proposed: NDA check requirement for standard equipment = Skipped until day 25 ([R4] [E3]) — The record cited by R4 (day 3) is later than [E3] (day -14) and thus supersedes the earlier expiration date.
```
### MATCHER CHECK FR-01092 (need LEGAL-TYO/E-TYO-1012/contract): matcher says **delivered**
record text: NDA of Yamada Sou signed copy verified, NDA check step can be skipped until day 25.
What the requester received from LEGAL-TYO during this task:
```
The highest allowed tier is premium due to an active exception until day 12. An NDA check is skipped until day 25. Contract expires day 222.
- E-TYO-1012 | allowed equipment tier | standard |  | db, day 3: Reply 1: D1
- E-TYO-1012 | contract expiry day | 222 |  | db, day 3: Reply 1: D1
- E-TYO-1012 | NDA required in contract | true |  | db, day 3: Reply 1: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 2: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 2: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 2: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 3: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 3: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 3: D1
- E-TYO-1012 | allowed_tier | standard |  | db, day 3: Reply 4: D1
- E-TYO-1012 | expiry | 222 |  | db, day 3: Reply 4: D1
- E-TYO-1012 | nda | true |  | db, day 3: Reply 4: D1
- E-TYO-1012 | NDA check status | signed copy verified, NDA check step can be skipped until day 25 |  | history, day 3: Reply 4: H23
- E-TYO-1012 | legal exception | higher tiers including premium allowed until day 12 | active until day 12 | history, day -12: [E5]
conflict: Legal exceptions modifying allowed tier: R4 states 'No legal exception record found', but [E5] records an exception allowing premium tiers. ([R4] [E5])
conflict: NDA check status: [E3] states NDA check can be skipped until day 0, while R4 cites a record (day 3) stating it can be skipped until day 25. ([E3] [R4])
proposed: Highest equipment tier allowed = premium ([E5] [V8]) — While the contract base tier is standard, the exception in [E5] allows premium tiers until day 12, which is still in effect on day 5.
proposed: Legal exceptions modifying allowed tier = higher tiers including premium allowed until day 12 ([E5]) — [E5] is a valid record from day -12 stating the exception is active until day 12, contradicting R4's claim of no record.
proposed: NDA check requirement for standard equipment = Skipped until day 25 ([R4] [E3]) — The record cited by R4 (day 3) is later than [E3] (day -14) and thus supersedes the earlier expiration date.
```

## CASE 33: qwen3.5-27b · ingress · s14 · W-00082 · class C · day 9 · template sourcing
### Task as given to the requester
Sales Section 2 will place a department order for a laptop. List the usable quotes right now from cheapest, with quote amount and actual lead time.
[Request scope] item=laptop; procurement review=apply procurement quotes, prices, receipts and registration rules; contract review=excluded; data residency review=included; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"options": []}
### Counterfactual answers (generator)
{"stale": {"options": [["Q-V-TYO-2-LTB", 647783, 6]]}, "partial": {"options": [["Q-V-TYO-3-LTB", 543753, 8], ["Q-V-TYO-3-LTS", 1072284, 8], ["Q-V-TYO-3-LTP", 2178635, 8]]}, "neardup": null, "wrong_owner": null}
### World facts behind the gold (by need)
**need PROC-TYO/quotes/laptop** (group PROC-TYO, class C, local=False)
- RULE PROC-TYO.lead_time_limit: {"id": "PROC-TYO.lead_time_limit", "group": "PROC-TYO", "title": "Lead time limits", "params": {"purchase_max_days": 7, "vendor_max_days": 10}, "text": "Personal equipment orders use only suppliers with a lead time of 7 days or less; department orders 10 days or less."}
- RECORD FR-01188 (operational/handover, day 4, by proc-tyo.a5; DB shows n/a): Supplier V-TYO-1 exclude from comparisons until day 12 due to a quality issue.
- RECORD FR-01388 (operational/handover, day 8, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-0 exclude from comparisons until day 22 due to a quality issue.
- RECORD FR-01152 [decision-critical] (operational/observation, day 3, by proc-tyo.a2; DB shows n/a): Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01239 (operational/observation, day 5, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-1 delivery notified: deliveries delayed by 4 days until day 19.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- RECORD FR-01329 [decision-critical] (operational/observation, day 7, by proc-tyo.a3; DB shows n/a): Supplier V-TYO-2 delivery notified: deliveries delayed by 3 days until day 15.
- RULE PROC-TYO.delay_notice: {"id": "PROC-TYO.delay_notice", "group": "PROC-TYO", "title": "Delivery delay notice", "params": {"delay_adds_to_lead": true}, "text": "During a supplier's delay notice period, the notified delay is added to the registered lead time when checking lead time limits."}
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-1-LTS"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-1"}
- DB `PROC-TYO/vendor/V-TYO-1/lead` v3 (recorded day 7, registered day 8): 9
- DB `PROC-TYO/quote/Q-V-TYO-1-LTS/amount` v1 (recorded day -20, registered day -20): 1077364
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTB"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01448 [decision-critical] (db_pending/observation, day 9, by proc-tyo.n0012; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 10
- DB `PROC-TYO/quote/Q-V-TYO-2-LTB/amount` v4 (recorded day 5, registered day 8): 647783
- CATALOG: {"group": "PROC-TYO", "key": "quotes/Q-V-TYO-2-LTP"}
- CATALOG: {"group": "PROC-TYO", "key": "vendors/V-TYO-2"}
- RECORD FR-01448 [decision-critical] (db_pending/observation, day 9, by proc-tyo.n0012; DB shows 2): Supplier V-TYO-2 lead time change notice applied. Stored value: 10
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
answer: {"options": [["Q-V-TYO-2-LTB", 647783, 6], ["Q-V-TYO-2-LTP", 2135766, 6]]}
official exact match: 0 (0/1 slots)
### MATCHER CHECK FR-01152 (need PROC-TYO/quotes/laptop): matcher says **missing**
record text: Supplier V-TYO-3 delivery notified: deliveries delayed by 5 days until day 15.
What the requester received from PROC-TYO during this task:
```
Only two quotes are usable for a department order: Q-V-TYO-2-LTB and Q-V-TYO-2-LTP. V-TYO-1 quotes exceed the 10-day limit (effective 13 days) and V-TYO-3 quotes are from an unregistered vendor.
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | db, day 3: Reply 1: D13
- Q-V-TYO-2-LTP | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTP | quote_id | Q-V-TYO-3-LTP |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | quote_amount | 2178635 |  | db, day -20: Reply 1: D14
- Q-V-TYO-3-LTP | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-1-LTS | quote_id | Q-V-TYO-1-LTS |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | quote_amount | 1077364 |  | db, day -20: Reply 1: D15
- Q-V-TYO-1-LTS | vendor | V-TYO-1 |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | lead_time | 9 |  | db, day 8: Reply 1: D19
- Q-V-TYO-3-LTS | quote_id | Q-V-TYO-3-LTS |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | quote_amount | 1072284 |  | db, day -6: Reply 1: D16
- Q-V-TYO-3-LTS | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | db, day 8: Reply 1: D17
- Q-V-TYO-2-LTB | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTB | quote_id | Q-V-TYO-3-LTB |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | quote_amount | 543753 |  | db, day 3: Reply 1: D18
- Q-V-TYO-3-LTB | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | lead_time | 8 |  | db, day 1: Reply 1: D21
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D22
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D23
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D24
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | history, day 8: Reply 2: H388
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | history, day 8: Reply 2: H408
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | history, day 8: Reply 2: H404
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | history, day 8: Reply 2: H416
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- V-TYO-1 | effective_lead_time | 13 |  | history, day 8: [E6]
- V-TYO-1 | usability_for_department_order | false |  | history, day 8: [E6]
- V-TYO-3 | usability_for_department_order | false |  | history, day 8: [E6]
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: [E6]
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: [E6]
conflict: V-TYO-1 lead time and usability: R1 states V-TYO-1 lead time is 9 days and within the 10-day limit. Records [E6] indicate a delay notice of +4 days, resulting in an effective lead time of 13 days, which exceeds the limit. ([R1] [E6])
proposed: Usable laptop quotes for department order = Q-V-TYO-2-LTB (647783 KRW, 6 days), Q-V-TYO-2-LTP (2135766 KRW, 6 days) ([E6] [R2]) — Only these quotes meet the 10-day lead time limit after applying delay notices and come from registered vendors.
```
### MATCHER CHECK FR-01329 (need PROC-TYO/quotes/laptop): matcher says **missing**
record text: Supplier V-TYO-2 delivery notified: deliveries delayed by 3 days until day 15.
What the requester received from PROC-TYO during this task:
```
Only two quotes are usable for a department order: Q-V-TYO-2-LTB and Q-V-TYO-2-LTP. V-TYO-1 quotes exceed the 10-day limit (effective 13 days) and V-TYO-3 quotes are from an unregistered vendor.
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | db, day 3: Reply 1: D13
- Q-V-TYO-2-LTP | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTP | quote_id | Q-V-TYO-3-LTP |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | quote_amount | 2178635 |  | db, day -20: Reply 1: D14
- Q-V-TYO-3-LTP | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-1-LTS | quote_id | Q-V-TYO-1-LTS |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | quote_amount | 1077364 |  | db, day -20: Reply 1: D15
- Q-V-TYO-1-LTS | vendor | V-TYO-1 |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | lead_time | 9 |  | db, day 8: Reply 1: D19
- Q-V-TYO-3-LTS | quote_id | Q-V-TYO-3-LTS |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | quote_amount | 1072284 |  | db, day -6: Reply 1: D16
- Q-V-TYO-3-LTS | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | db, day 8: Reply 1: D17
- Q-V-TYO-2-LTB | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTB | quote_id | Q-V-TYO-3-LTB |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | quote_amount | 543753 |  | db, day 3: Reply 1: D18
- Q-V-TYO-3-LTB | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | lead_time | 8 |  | db, day 1: Reply 1: D21
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D22
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D23
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D24
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | history, day 8: Reply 2: H388
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | history, day 8: Reply 2: H408
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | history, day 8: Reply 2: H404
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | history, day 8: Reply 2: H416
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- V-TYO-1 | effective_lead_time | 13 |  | history, day 8: [E6]
- V-TYO-1 | usability_for_department_order | false |  | history, day 8: [E6]
- V-TYO-3 | usability_for_department_order | false |  | history, day 8: [E6]
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: [E6]
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: [E6]
conflict: V-TYO-1 lead time and usability: R1 states V-TYO-1 lead time is 9 days and within the 10-day limit. Records [E6] indicate a delay notice of +4 days, resulting in an effective lead time of 13 days, which exceeds the limit. ([R1] [E6])
proposed: Usable laptop quotes for department order = Q-V-TYO-2-LTB (647783 KRW, 6 days), Q-V-TYO-2-LTP (2135766 KRW, 6 days) ([E6] [R2]) — Only these quotes meet the 10-day lead time limit after applying delay notices and come from registered vendors.
```
### MATCHER CHECK FR-01448 (need PROC-TYO/quotes/laptop): matcher says **stale**
record text: Supplier V-TYO-2 lead time change notice applied. Stored value: 10
What the requester received from PROC-TYO during this task:
```
Only two quotes are usable for a department order: Q-V-TYO-2-LTB and Q-V-TYO-2-LTP. V-TYO-1 quotes exceed the 10-day limit (effective 13 days) and V-TYO-3 quotes are from an unregistered vendor.
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | db, day 3: Reply 1: D13
- Q-V-TYO-2-LTP | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTP | quote_id | Q-V-TYO-3-LTP |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | quote_amount | 2178635 |  | db, day -20: Reply 1: D14
- Q-V-TYO-3-LTP | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-1-LTS | quote_id | Q-V-TYO-1-LTS |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | quote_amount | 1077364 |  | db, day -20: Reply 1: D15
- Q-V-TYO-1-LTS | vendor | V-TYO-1 |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | lead_time | 9 |  | db, day 8: Reply 1: D19
- Q-V-TYO-3-LTS | quote_id | Q-V-TYO-3-LTS |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | quote_amount | 1072284 |  | db, day -6: Reply 1: D16
- Q-V-TYO-3-LTS | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | db, day 8: Reply 1: D17
- Q-V-TYO-2-LTB | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTB | quote_id | Q-V-TYO-3-LTB |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | quote_amount | 543753 |  | db, day 3: Reply 1: D18
- Q-V-TYO-3-LTB | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | lead_time | 8 |  | db, day 1: Reply 1: D21
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D22
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D23
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D24
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | history, day 8: Reply 2: H388
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | history, day 8: Reply 2: H408
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | history, day 8: Reply 2: H404
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | history, day 8: Reply 2: H416
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- V-TYO-1 | effective_lead_time | 13 |  | history, day 8: [E6]
- V-TYO-1 | usability_for_department_order | false |  | history, day 8: [E6]
- V-TYO-3 | usability_for_department_order | false |  | history, day 8: [E6]
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: [E6]
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: [E6]
conflict: V-TYO-1 lead time and usability: R1 states V-TYO-1 lead time is 9 days and within the 10-day limit. Records [E6] indicate a delay notice of +4 days, resulting in an effective lead time of 13 days, which exceeds the limit. ([R1] [E6])
proposed: Usable laptop quotes for department order = Q-V-TYO-2-LTB (647783 KRW, 6 days), Q-V-TYO-2-LTP (2135766 KRW, 6 days) ([E6] [R2]) — Only these quotes meet the 10-day lead time limit after applying delay notices and come from registered vendors.
```
### MATCHER CHECK FR-01448 (need PROC-TYO/quotes/laptop): matcher says **stale**
record text: Supplier V-TYO-2 lead time change notice applied. Stored value: 10
What the requester received from PROC-TYO during this task:
```
Only two quotes are usable for a department order: Q-V-TYO-2-LTB and Q-V-TYO-2-LTP. V-TYO-1 quotes exceed the 10-day limit (effective 13 days) and V-TYO-3 quotes are from an unregistered vendor.
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | db, day 3: Reply 1: D13
- Q-V-TYO-2-LTP | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D3
- Q-V-TYO-2-LTP | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTP | quote_id | Q-V-TYO-3-LTP |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | quote_amount | 2178635 |  | db, day -20: Reply 1: D14
- Q-V-TYO-3-LTP | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D4
- Q-V-TYO-3-LTP | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-1-LTS | quote_id | Q-V-TYO-1-LTS |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | quote_amount | 1077364 |  | db, day -20: Reply 1: D15
- Q-V-TYO-1-LTS | vendor | V-TYO-1 |  | db, day fixed: Reply 1: D6
- Q-V-TYO-1-LTS | lead_time | 9 |  | db, day 8: Reply 1: D19
- Q-V-TYO-3-LTS | quote_id | Q-V-TYO-3-LTS |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | quote_amount | 1072284 |  | db, day -6: Reply 1: D16
- Q-V-TYO-3-LTS | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D8
- Q-V-TYO-3-LTS | lead_time | 8 |  | db, day 1: Reply 1: D21
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | db, day 8: Reply 1: D17
- Q-V-TYO-2-LTB | vendor | V-TYO-2 |  | db, day fixed: Reply 1: D11
- Q-V-TYO-2-LTB | lead_time | 3 |  | db, day -5: Reply 1: D20
- Q-V-TYO-3-LTB | quote_id | Q-V-TYO-3-LTB |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | quote_amount | 543753 |  | db, day 3: Reply 1: D18
- Q-V-TYO-3-LTB | vendor | V-TYO-3 |  | db, day fixed: Reply 1: D12
- Q-V-TYO-3-LTB | lead_time | 8 |  | db, day 1: Reply 1: D21
- V-TYO-1 | vendor_registration | true |  | db, day -20: Reply 1: D22
- V-TYO-2 | vendor_registration | true |  | db, day -20: Reply 1: D23
- V-TYO-3 | vendor_registration | false |  | db, day -20: Reply 1: D24
- Q-V-TYO-2-LTB | quote_id | Q-V-TYO-2-LTB |  | history, day 8: Reply 2: H388
- Q-V-TYO-2-LTB | quote_amount | 647783 |  | history, day 8: Reply 2: H408
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- Q-V-TYO-2-LTP | quote_id | Q-V-TYO-2-LTP |  | history, day 8: Reply 2: H404
- Q-V-TYO-2-LTP | quote_amount | 2135766 |  | history, day 8: Reply 2: H416
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: Reply 2: calculated from H426 (base 3) + delay notice +3 until day 15
- V-TYO-1 | effective_lead_time | 13 |  | history, day 8: [E6]
- V-TYO-1 | usability_for_department_order | false |  | history, day 8: [E6]
- V-TYO-3 | usability_for_department_order | false |  | history, day 8: [E6]
- Q-V-TYO-2-LTB | effective_lead_time | 6 |  | history, day 8: [E6]
- Q-V-TYO-2-LTP | effective_lead_time | 6 |  | history, day 8: [E6]
conflict: V-TYO-1 lead time and usability: R1 states V-TYO-1 lead time is 9 days and within the 10-day limit. Records [E6] indicate a delay notice of +4 days, resulting in an effective lead time of 13 days, which exceeds the limit. ([R1] [E6])
proposed: Usable laptop quotes for department order = Q-V-TYO-2-LTB (647783 KRW, 6 days), Q-V-TYO-2-LTP (2135766 KRW, 6 days) ([E6] [R2]) — Only these quotes meet the 10-day lead time limit after applying delay notices and come from registered vendors.
```

## CASE 34: qwen3.5-27b · ingress · s13 · W-00038 · class D · day 4 · template precedence
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
answer: {"approver": "division_head", "governing_rule": "tiers", "it_exception": false}
official exact match: 0 (1/3 slots)
### MATCHER CHECK FR-00525 (need IT-SEL/eligibility/E-SEL-1007): matcher says **delivered**
record text: Equipment tier of Yoon Chaewon up to premium allowed until day 7 for work reasons (IT exception approved).
What the requester received from IT-SEL during this task:
```
Employee E-SEL-1007 (Yoon Chaewon) has an active IT exception allowing premium tier until day 7.
- E-SEL-1007 | catalog entry | NOT_FOUND |  | db, day unknown: Reply 1: D1
- Chaewon Senior | catalog entry | NOT_FOUND |  | db, day unknown: Reply 1: D2
- E-SEL-1007 | name | Yoon Chaewon |  | history, day -20: [E1]
- E-SEL-1007 | IT equipment tier exception | up to premium allowed until day 7 for work reasons (IT exception approved) | held until day 7 | history, day -11: [E6]
conflict: Employee E-SEL-1007 catalog entry: Reply [R1] states 'NOT_FOUND', but records [E1], [E2], [E3], [E6], [E15] contain entries for this employee. ([R1] [E1])
conflict: IT equipment tier exception for E-SEL-1007: Reply [R1] states no exception found, but record [E6] documents an approved exception. ([R1] [E6])
proposed: Current allowed equipment tier for employee E-SEL-1007 = Premium ([E6] [E1]) — The IT exception approved on day -11 allows premium tier until day 7, which is active on day 4.
proposed: Whether premium tier is allowed for employee E-SEL-1007 = Yes ([E6]) — The active IT exception permits premium tier.
```
### MATCHER CHECK FR-00499 (need LEGAL-SEL/E-SEL-1007/contract): matcher says **missing**
record text: Equipment exception of Yoon Chaewon higher tiers including premium allowed until day 17 for a project, legal check done.
What the requester received from LEGAL-SEL during this task:
```
Contract terms for E-SEL-1007 are confirmed as standard tier, expiring day 184, with no NDA required (based on DB v4, day -1). However, determining if the 2,113,553 KRW workstation purchase is denied requires missing information: contractor status, employee department, supplier location, the specific tier classification of the workstation, whether the price exceeds the standard limit, and any existing legal exceptions. No additional facts were found in group records to resolve these gaps.
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 1: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 1: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 1: D1
- E-SEL-1007 | catalog_entry | no record registered | NO_RECORD | db, day unknown: Reply 1: D2
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 2: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 2: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 2: D1
- E-SEL-1007 | catalog_entry | NO_RECORD |  | db, day unknown: Reply 2: D2
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 3: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 3: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 3: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 4: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 4: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 4: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 5: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 5: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 5: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 6: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 6: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 6: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 7: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 7: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 7: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 8: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 8: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 8: D1
- E-SEL-1007 | allowed_tier | standard |  | db, day -1: Reply 9: D1
- E-SEL-1007 | expiry | 184 |  | db, day -1: Reply 9: D1
- E-SEL-1007 | nda | false |  | db, day -1: Reply 9: D1
missing: Contractor status of E-SEL-1007; Department of E-SEL-1007 (for residency rule check); Supplier location of the workstation (offshore or domestic); Workstation tier classification for 2,113,553 KRW; Whether 2,113,553 KRW exceeds the standard tier limit; Any legal exceptions granted for E-SEL-1007
```

## CASE 35: qwen3.5-27b · ingress · s14 · W-00126 · class D · day 13 · template purchase
### Task as given to the requester
For Ito-san's monitor request: can it be fulfilled with the cheapest option that meets all conditions, and whose approval is needed?
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
{"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 2170166, "blocked_by": null}
### Counterfactual answers (generator)
{"stale": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 256962, "blocked_by": null}, "partial": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 256962, "blocked_by": null}, "neardup": {"decision": "assign", "option": "INV-TYO-MNB", "approver": "team_lead", "nda": false, "budget_after": 2759045, "blocked_by": null}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1005/profile** (group HR-TYO, class None, local=True)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1005"}
- DB `HR-TYO/emp/E-TYO-1005/profile` v5 (recorded day 9, registered day 10): {"dept": "Planning Section", "grade": 3, "contract": "regular", "hire_day": -396, "status": "active"}
**need FIN-TYO/Planning Section/budget_schedule** (group FIN-TYO, class D, local=False)
- RECORD FR-01631 [decision-critical] (db_pending/rationale, day 12, by fin-tyo.a1; DB shows 9): Planning Section capex balance adjusted to 4,228,979 KRW (urgent spend deduction). Stored value: 4228979
- RULE FIN-TYO.pending_deduction: {"id": "FIN-TYO.pending_deduction", "group": "FIN-TYO", "title": "Available budget (Art. 4.2)", "params": {"deduct_statuses": ["reviewing", "pending"], "earmarks_deducted": true, "deduct_until": "day_before_settle"}, "text": "Available budget = line balance − (sum of items under review or provisionally approved) − (sum of earmarks in their validity period). An item is deducted only until the day before its expected settlement day (not on the settlement day itself). An earmark is deducted through its end day."}
- RECORD FR-01274 [decision-critical] (operational/pending_intent, day 6, by fin-tyo.a1; DB shows n/a): Planning Section capex 507,211 KRW earmarked for meeting room replacement until day 14 (no voucher yet).
- RECORD FR-01475 [decision-critical] (operational/pending_intent, day 9, by fin-tyo.a1; DB shows n/a): Planning Section capex 194,251 KRW earmarked for training equipment until day 14 (no voucher yet).
- DB `FIN-TYO/commit/CMT-00059/status` v2 (recorded day 6, registered day 8): {"status": "settled", "amount": 787154, "expected_settle": 6}
- DB `FIN-TYO/commit/CMT-00061/status` v2 (recorded day 7, registered day 8): {"status": "settled", "amount": 890302, "expected_settle": 7}
- RECORD FR-01656 (db_pending/observation, day 13, by fin-tyo.a3; DB shows 1): CMT-00073 Planning Section provisional approval settled. Stored value: {"amount":661700,"expected_settle":13,"status":"settled"}
- DB `FIN-TYO/commit/CMT-00083/status` v2 (recorded day 11, registered day 12): {"status": "settled", "amount": 987862, "expected_settle": 11}
- RECORD FR-01659 [decision-critical] (db_pending/observation, day 13, by fin-tyo.n0015; DB shows ABSENT): CMT-00115 Planning Section provisional approval 349,849 KRW confirmed, settlement expected day 14. Stored value: {"amount":349849,"expected_settle":14,"status":"pending"}
- RECORD FR-01648 [decision-critical] (operational/pending_intent, day 13, by fin-tyo.a1; DB shows n/a): CMT-00124 Planning Section meeting room equipment provisional approval 345,147 KRW under review, settlement expected day 22.
- QUERY SELECT commit WHERE group=FIN-TYO AND dept=Planning Section AND status IN ['reviewing', 'pending'] → ["earmark:FR-01274", "earmark:FR-01475", "CMT-00115", "CMT-00124"]
**need IT-TYO/eligibility/E-TYO-1005** (group IT-TYO, class A, local=False)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need IT-TYO/inventory/monitor** (group IT-TYO, class A, local=False)
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-MNB"}
- DB `IT-TYO/inv/INV-TYO-MNB/qty` v13 (recorded day 9, registered day 10): 4
- RECORD FR-01610 (operational/pending_intent, day 12, by it-tyo.w00253; DB shows n/a): In-house stock monitor (basic) 1 unit held for an incoming Planning Section hire until day 19.
- CATALOG: {"group": "IT-TYO", "key": "inventory/INV-TYO-MNS"}
- DB `IT-TYO/inv/INV-TYO-MNS/qty` v2 (recorded day -15, registered day -12): 0
**need LEGAL-TYO/residency** (group LEGAL-TYO, class A, local=False)
- RULE LEGAL-TYO.residency: {"id": "LEGAL-TYO.residency", "group": "LEGAL-TYO", "title": "Data residency", "params": {"restricted_depts": ["Dev Section 1", "Support Section"]}, "text": "These departments may not use equipment from offshore suppliers: Dev Section 1, Support Section."}
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"approver": "team_lead", "blocked_by": null, "budget_after": 3566624, "decision": "assign", "nda": false, "option": "INV-TYO-MNB"}
official exact match: 0 (5/6 slots)
### MATCHER CHECK FR-01631 (need FIN-TYO/Planning Section/budget_schedule): matcher says **delivered**
record text: Planning Section capex balance adjusted to 4,228,979 KRW (urgent spend deduction). Stored value: 4228979
What the requester received from FIN-TYO during this task:
```
The current budget line balance for Planning Section is 4,228,979 KRW (from day 12 history record). There are no active earmarks on day 13, and the pending provisional approval CMT-00073 (661,700 KRW) is not deducted on its settlement day (day 13). Therefore, the available budget is 4,228,979 KRW, which is sufficient to cover the 662,355 KRW monitor expense.
- Planning Section | budget_line_balance (database) | 2315775 |  | db, day 7: Reply 1: D1
- Planning Section | budget_line_balance (history record) | 4228979 |  | history, day 12: Reply 1: H634
- Planning Section | pending provisional approval (CMT-00073) | 661700 | pending | db, day unknown: Reply 1: D2
- Planning Section | expected_settle for CMT-00073 | 13 |  | db, day unknown: Reply 1: D2
- Planning Section | sum of pending provisional approvals being deducted on day 13 | 0 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | available budget | 4228979 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | expense coverage for 662355 KRW | yes |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | budget line balance | 2315775 |  | db, day 7: Reply 2: D1
- Planning Section | budget line base | 4798049 |  | db, day -20: Reply 2: D2
- CMT-00073 | status | pending |  | db, day 8: Reply 2: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 2: D3
- CMT-00073 | expected settlement day | 13 |  | db, day 8: Reply 2: D3
- Planning Section | provisional approvals being deducted | 0 |  | rule, day fixed: Reply 2: rule: pending_deduction
- Planning Section | budget_line_balance | 2315775 |  | db, day 7: Reply 3: D1
- Planning Section | budget_line_base | 4798049 |  | db, day -20: Reply 3: D2
- CMT-00073 | provisional_approval_status | pending | pending | db, day 8: Reply 3: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 3: D3
- CMT-00073 | expected_settlement_day | 13 |  | db, day 8: Reply 3: D3
- Planning Section | available_budget | 2315775 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | expense_coverage | yes |  | unknown, day unknown: Reply 3: calculation
- Planning Section | number_of_pending_approvals_deducted | 0 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | budget_line_balance | 4228979 |  | history, day 12: [R1]
- Planning Section | active earmarks on day 13 | none |  | history, day 1: [E2], [E3], [E6]
- CMT-00073 | deduction status on day 13 | not deducted | pending | history, day 6: [E8]
conflict: Planning Section budget_line_balance: Replies [R2] and [R3] cite 2,315,775 KRW (database day 7), while reply [R1] cites 4,228,979 KRW (history record day 12). The day 12 record is later and takes precedence. ([R1] [R2] [R3])
conflict: Available budget calculation: Reply [R2] states available budget cannot be calculated due to missing earmark info, but records confirm no active earmarks exist on day 13. ([R2] [E2] [E3])
proposed: Planning Section available budget = 4228979 ([R1] [E8] [E2]) — Using the latest balance of 4,228,979 KRW (day 12 history) and deducting 0 for provisional approvals (settlement day 13) and 0 for earmarks (none active), the available budget is 4,228,979 KRW.
proposed: Expense coverage for 662355 KRW = yes ([R1] [E8]) — The available budget of 4,228,979 KRW exceeds the requested expense of 662,355 KRW.
---
The finance approver for 662,355 KRW is team_lead. Thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above 2,500,000 KRW. Reply [R3] contained a conflicting data entry corrected by records and other replies.
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- 662355 KRW expense | required approver | division_head |  | rule, day fixed: Reply 3: approval_tiers
- team_lead | approval threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- division_head | approval threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- cfo | approval threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | approver for up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense of 662355 KRW | required approver based on amount | FIN_TEAM_LEAD |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | history, day 6: [E6]
conflict: expense 662355 KRW required approver: Reply [R3] data line states 'division_head', contradicting its own text and all other replies ([R1], [R2], [R4]) and records ([E6]-[E9]) which state 'team_lead'. ([R3] [R1] [R2] [R4] [E6] [E7] [E8] [E9])
proposed: expense 662355 KRW required approver = team_lead ([E6] [E7] [E8] [E9] [R1] [R2] [R4]) — The amount 662,355 KRW is below the 1,000,000 KRW threshold for team_lead approval per the approval_tiers rule.
```
### MATCHER CHECK FR-01274 (need FIN-TYO/Planning Section/budget_schedule): matcher says **missing**
record text: Planning Section capex 507,211 KRW earmarked for meeting room replacement until day 14 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
The current budget line balance for Planning Section is 4,228,979 KRW (from day 12 history record). There are no active earmarks on day 13, and the pending provisional approval CMT-00073 (661,700 KRW) is not deducted on its settlement day (day 13). Therefore, the available budget is 4,228,979 KRW, which is sufficient to cover the 662,355 KRW monitor expense.
- Planning Section | budget_line_balance (database) | 2315775 |  | db, day 7: Reply 1: D1
- Planning Section | budget_line_balance (history record) | 4228979 |  | history, day 12: Reply 1: H634
- Planning Section | pending provisional approval (CMT-00073) | 661700 | pending | db, day unknown: Reply 1: D2
- Planning Section | expected_settle for CMT-00073 | 13 |  | db, day unknown: Reply 1: D2
- Planning Section | sum of pending provisional approvals being deducted on day 13 | 0 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | available budget | 4228979 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | expense coverage for 662355 KRW | yes |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | budget line balance | 2315775 |  | db, day 7: Reply 2: D1
- Planning Section | budget line base | 4798049 |  | db, day -20: Reply 2: D2
- CMT-00073 | status | pending |  | db, day 8: Reply 2: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 2: D3
- CMT-00073 | expected settlement day | 13 |  | db, day 8: Reply 2: D3
- Planning Section | provisional approvals being deducted | 0 |  | rule, day fixed: Reply 2: rule: pending_deduction
- Planning Section | budget_line_balance | 2315775 |  | db, day 7: Reply 3: D1
- Planning Section | budget_line_base | 4798049 |  | db, day -20: Reply 3: D2
- CMT-00073 | provisional_approval_status | pending | pending | db, day 8: Reply 3: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 3: D3
- CMT-00073 | expected_settlement_day | 13 |  | db, day 8: Reply 3: D3
- Planning Section | available_budget | 2315775 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | expense_coverage | yes |  | unknown, day unknown: Reply 3: calculation
- Planning Section | number_of_pending_approvals_deducted | 0 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | budget_line_balance | 4228979 |  | history, day 12: [R1]
- Planning Section | active earmarks on day 13 | none |  | history, day 1: [E2], [E3], [E6]
- CMT-00073 | deduction status on day 13 | not deducted | pending | history, day 6: [E8]
conflict: Planning Section budget_line_balance: Replies [R2] and [R3] cite 2,315,775 KRW (database day 7), while reply [R1] cites 4,228,979 KRW (history record day 12). The day 12 record is later and takes precedence. ([R1] [R2] [R3])
conflict: Available budget calculation: Reply [R2] states available budget cannot be calculated due to missing earmark info, but records confirm no active earmarks exist on day 13. ([R2] [E2] [E3])
proposed: Planning Section available budget = 4228979 ([R1] [E8] [E2]) — Using the latest balance of 4,228,979 KRW (day 12 history) and deducting 0 for provisional approvals (settlement day 13) and 0 for earmarks (none active), the available budget is 4,228,979 KRW.
proposed: Expense coverage for 662355 KRW = yes ([R1] [E8]) — The available budget of 4,228,979 KRW exceeds the requested expense of 662,355 KRW.
---
The finance approver for 662,355 KRW is team_lead. Thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above 2,500,000 KRW. Reply [R3] contained a conflicting data entry corrected by records and other replies.
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- 662355 KRW expense | required approver | division_head |  | rule, day fixed: Reply 3: approval_tiers
- team_lead | approval threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- division_head | approval threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- cfo | approval threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | approver for up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense of 662355 KRW | required approver based on amount | FIN_TEAM_LEAD |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | history, day 6: [E6]
conflict: expense 662355 KRW required approver: Reply [R3] data line states 'division_head', contradicting its own text and all other replies ([R1], [R2], [R4]) and records ([E6]-[E9]) which state 'team_lead'. ([R3] [R1] [R2] [R4] [E6] [E7] [E8] [E9])
proposed: expense 662355 KRW required approver = team_lead ([E6] [E7] [E8] [E9] [R1] [R2] [R4]) — The amount 662,355 KRW is below the 1,000,000 KRW threshold for team_lead approval per the approval_tiers rule.
```
### MATCHER CHECK FR-01475 (need FIN-TYO/Planning Section/budget_schedule): matcher says **missing**
record text: Planning Section capex 194,251 KRW earmarked for training equipment until day 14 (no voucher yet).
What the requester received from FIN-TYO during this task:
```
The current budget line balance for Planning Section is 4,228,979 KRW (from day 12 history record). There are no active earmarks on day 13, and the pending provisional approval CMT-00073 (661,700 KRW) is not deducted on its settlement day (day 13). Therefore, the available budget is 4,228,979 KRW, which is sufficient to cover the 662,355 KRW monitor expense.
- Planning Section | budget_line_balance (database) | 2315775 |  | db, day 7: Reply 1: D1
- Planning Section | budget_line_balance (history record) | 4228979 |  | history, day 12: Reply 1: H634
- Planning Section | pending provisional approval (CMT-00073) | 661700 | pending | db, day unknown: Reply 1: D2
- Planning Section | expected_settle for CMT-00073 | 13 |  | db, day unknown: Reply 1: D2
- Planning Section | sum of pending provisional approvals being deducted on day 13 | 0 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | available budget | 4228979 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | expense coverage for 662355 KRW | yes |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | budget line balance | 2315775 |  | db, day 7: Reply 2: D1
- Planning Section | budget line base | 4798049 |  | db, day -20: Reply 2: D2
- CMT-00073 | status | pending |  | db, day 8: Reply 2: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 2: D3
- CMT-00073 | expected settlement day | 13 |  | db, day 8: Reply 2: D3
- Planning Section | provisional approvals being deducted | 0 |  | rule, day fixed: Reply 2: rule: pending_deduction
- Planning Section | budget_line_balance | 2315775 |  | db, day 7: Reply 3: D1
- Planning Section | budget_line_base | 4798049 |  | db, day -20: Reply 3: D2
- CMT-00073 | provisional_approval_status | pending | pending | db, day 8: Reply 3: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 3: D3
- CMT-00073 | expected_settlement_day | 13 |  | db, day 8: Reply 3: D3
- Planning Section | available_budget | 2315775 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | expense_coverage | yes |  | unknown, day unknown: Reply 3: calculation
- Planning Section | number_of_pending_approvals_deducted | 0 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | budget_line_balance | 4228979 |  | history, day 12: [R1]
- Planning Section | active earmarks on day 13 | none |  | history, day 1: [E2], [E3], [E6]
- CMT-00073 | deduction status on day 13 | not deducted | pending | history, day 6: [E8]
conflict: Planning Section budget_line_balance: Replies [R2] and [R3] cite 2,315,775 KRW (database day 7), while reply [R1] cites 4,228,979 KRW (history record day 12). The day 12 record is later and takes precedence. ([R1] [R2] [R3])
conflict: Available budget calculation: Reply [R2] states available budget cannot be calculated due to missing earmark info, but records confirm no active earmarks exist on day 13. ([R2] [E2] [E3])
proposed: Planning Section available budget = 4228979 ([R1] [E8] [E2]) — Using the latest balance of 4,228,979 KRW (day 12 history) and deducting 0 for provisional approvals (settlement day 13) and 0 for earmarks (none active), the available budget is 4,228,979 KRW.
proposed: Expense coverage for 662355 KRW = yes ([R1] [E8]) — The available budget of 4,228,979 KRW exceeds the requested expense of 662,355 KRW.
---
The finance approver for 662,355 KRW is team_lead. Thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above 2,500,000 KRW. Reply [R3] contained a conflicting data entry corrected by records and other replies.
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- 662355 KRW expense | required approver | division_head |  | rule, day fixed: Reply 3: approval_tiers
- team_lead | approval threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- division_head | approval threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- cfo | approval threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | approver for up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense of 662355 KRW | required approver based on amount | FIN_TEAM_LEAD |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | history, day 6: [E6]
conflict: expense 662355 KRW required approver: Reply [R3] data line states 'division_head', contradicting its own text and all other replies ([R1], [R2], [R4]) and records ([E6]-[E9]) which state 'team_lead'. ([R3] [R1] [R2] [R4] [E6] [E7] [E8] [E9])
proposed: expense 662355 KRW required approver = team_lead ([E6] [E7] [E8] [E9] [R1] [R2] [R4]) — The amount 662,355 KRW is below the 1,000,000 KRW threshold for team_lead approval per the approval_tiers rule.
```
### MATCHER CHECK FR-01659 (need FIN-TYO/Planning Section/budget_schedule): matcher says **missing**
record text: CMT-00115 Planning Section provisional approval 349,849 KRW confirmed, settlement expected day 14. Stored value: {"amount":349849,"expected_settle":14,"status":"pending"}
What the requester received from FIN-TYO during this task:
```
The current budget line balance for Planning Section is 4,228,979 KRW (from day 12 history record). There are no active earmarks on day 13, and the pending provisional approval CMT-00073 (661,700 KRW) is not deducted on its settlement day (day 13). Therefore, the available budget is 4,228,979 KRW, which is sufficient to cover the 662,355 KRW monitor expense.
- Planning Section | budget_line_balance (database) | 2315775 |  | db, day 7: Reply 1: D1
- Planning Section | budget_line_balance (history record) | 4228979 |  | history, day 12: Reply 1: H634
- Planning Section | pending provisional approval (CMT-00073) | 661700 | pending | db, day unknown: Reply 1: D2
- Planning Section | expected_settle for CMT-00073 | 13 |  | db, day unknown: Reply 1: D2
- Planning Section | sum of pending provisional approvals being deducted on day 13 | 0 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | available budget | 4228979 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | expense coverage for 662355 KRW | yes |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | budget line balance | 2315775 |  | db, day 7: Reply 2: D1
- Planning Section | budget line base | 4798049 |  | db, day -20: Reply 2: D2
- CMT-00073 | status | pending |  | db, day 8: Reply 2: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 2: D3
- CMT-00073 | expected settlement day | 13 |  | db, day 8: Reply 2: D3
- Planning Section | provisional approvals being deducted | 0 |  | rule, day fixed: Reply 2: rule: pending_deduction
- Planning Section | budget_line_balance | 2315775 |  | db, day 7: Reply 3: D1
- Planning Section | budget_line_base | 4798049 |  | db, day -20: Reply 3: D2
- CMT-00073 | provisional_approval_status | pending | pending | db, day 8: Reply 3: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 3: D3
- CMT-00073 | expected_settlement_day | 13 |  | db, day 8: Reply 3: D3
- Planning Section | available_budget | 2315775 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | expense_coverage | yes |  | unknown, day unknown: Reply 3: calculation
- Planning Section | number_of_pending_approvals_deducted | 0 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | budget_line_balance | 4228979 |  | history, day 12: [R1]
- Planning Section | active earmarks on day 13 | none |  | history, day 1: [E2], [E3], [E6]
- CMT-00073 | deduction status on day 13 | not deducted | pending | history, day 6: [E8]
conflict: Planning Section budget_line_balance: Replies [R2] and [R3] cite 2,315,775 KRW (database day 7), while reply [R1] cites 4,228,979 KRW (history record day 12). The day 12 record is later and takes precedence. ([R1] [R2] [R3])
conflict: Available budget calculation: Reply [R2] states available budget cannot be calculated due to missing earmark info, but records confirm no active earmarks exist on day 13. ([R2] [E2] [E3])
proposed: Planning Section available budget = 4228979 ([R1] [E8] [E2]) — Using the latest balance of 4,228,979 KRW (day 12 history) and deducting 0 for provisional approvals (settlement day 13) and 0 for earmarks (none active), the available budget is 4,228,979 KRW.
proposed: Expense coverage for 662355 KRW = yes ([R1] [E8]) — The available budget of 4,228,979 KRW exceeds the requested expense of 662,355 KRW.
---
The finance approver for 662,355 KRW is team_lead. Thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above 2,500,000 KRW. Reply [R3] contained a conflicting data entry corrected by records and other replies.
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- 662355 KRW expense | required approver | division_head |  | rule, day fixed: Reply 3: approval_tiers
- team_lead | approval threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- division_head | approval threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- cfo | approval threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | approver for up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense of 662355 KRW | required approver based on amount | FIN_TEAM_LEAD |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | history, day 6: [E6]
conflict: expense 662355 KRW required approver: Reply [R3] data line states 'division_head', contradicting its own text and all other replies ([R1], [R2], [R4]) and records ([E6]-[E9]) which state 'team_lead'. ([R3] [R1] [R2] [R4] [E6] [E7] [E8] [E9])
proposed: expense 662355 KRW required approver = team_lead ([E6] [E7] [E8] [E9] [R1] [R2] [R4]) — The amount 662,355 KRW is below the 1,000,000 KRW threshold for team_lead approval per the approval_tiers rule.
```
### MATCHER CHECK FR-01648 (need FIN-TYO/Planning Section/budget_schedule): matcher says **missing**
record text: CMT-00124 Planning Section meeting room equipment provisional approval 345,147 KRW under review, settlement expected day 22.
What the requester received from FIN-TYO during this task:
```
The current budget line balance for Planning Section is 4,228,979 KRW (from day 12 history record). There are no active earmarks on day 13, and the pending provisional approval CMT-00073 (661,700 KRW) is not deducted on its settlement day (day 13). Therefore, the available budget is 4,228,979 KRW, which is sufficient to cover the 662,355 KRW monitor expense.
- Planning Section | budget_line_balance (database) | 2315775 |  | db, day 7: Reply 1: D1
- Planning Section | budget_line_balance (history record) | 4228979 |  | history, day 12: Reply 1: H634
- Planning Section | pending provisional approval (CMT-00073) | 661700 | pending | db, day unknown: Reply 1: D2
- Planning Section | expected_settle for CMT-00073 | 13 |  | db, day unknown: Reply 1: D2
- Planning Section | sum of pending provisional approvals being deducted on day 13 | 0 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | available budget | 4228979 |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | expense coverage for 662355 KRW | yes |  | rule, day fixed: Reply 1: pending_deduction
- Planning Section | budget line balance | 2315775 |  | db, day 7: Reply 2: D1
- Planning Section | budget line base | 4798049 |  | db, day -20: Reply 2: D2
- CMT-00073 | status | pending |  | db, day 8: Reply 2: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 2: D3
- CMT-00073 | expected settlement day | 13 |  | db, day 8: Reply 2: D3
- Planning Section | provisional approvals being deducted | 0 |  | rule, day fixed: Reply 2: rule: pending_deduction
- Planning Section | budget_line_balance | 2315775 |  | db, day 7: Reply 3: D1
- Planning Section | budget_line_base | 4798049 |  | db, day -20: Reply 3: D2
- CMT-00073 | provisional_approval_status | pending | pending | db, day 8: Reply 3: D3
- CMT-00073 | amount | 661700 |  | db, day 8: Reply 3: D3
- CMT-00073 | expected_settlement_day | 13 |  | db, day 8: Reply 3: D3
- Planning Section | available_budget | 2315775 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | expense_coverage | yes |  | unknown, day unknown: Reply 3: calculation
- Planning Section | number_of_pending_approvals_deducted | 0 |  | rule, day fixed: Reply 3: rule: pending_deduction
- Planning Section | budget_line_balance | 4228979 |  | history, day 12: [R1]
- Planning Section | active earmarks on day 13 | none |  | history, day 1: [E2], [E3], [E6]
- CMT-00073 | deduction status on day 13 | not deducted | pending | history, day 6: [E8]
conflict: Planning Section budget_line_balance: Replies [R2] and [R3] cite 2,315,775 KRW (database day 7), while reply [R1] cites 4,228,979 KRW (history record day 12). The day 12 record is later and takes precedence. ([R1] [R2] [R3])
conflict: Available budget calculation: Reply [R2] states available budget cannot be calculated due to missing earmark info, but records confirm no active earmarks exist on day 13. ([R2] [E2] [E3])
proposed: Planning Section available budget = 4228979 ([R1] [E8] [E2]) — Using the latest balance of 4,228,979 KRW (day 12 history) and deducting 0 for provisional approvals (settlement day 13) and 0 for earmarks (none active), the available budget is 4,228,979 KRW.
proposed: Expense coverage for 662355 KRW = yes ([R1] [E8]) — The available budget of 4,228,979 KRW exceeds the requested expense of 662,355 KRW.
---
The finance approver for 662,355 KRW is team_lead. Thresholds: team_lead up to 1,000,000 KRW, division_head up to 2,500,000 KRW, cfo above 2,500,000 KRW. Reply [R3] contained a conflicting data entry corrected by records and other replies.
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 1: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 1: rule: approval_tiers
- approval_tiers | team_lead threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | division_head threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- approval_tiers | cfo threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 2: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | rule, day fixed: Reply 2: rule: approval_tiers
- 662355 KRW expense | required approver | division_head |  | rule, day fixed: Reply 3: approval_tiers
- team_lead | approval threshold | up to 1,000,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- division_head | approval threshold | up to 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- cfo | approval threshold | above 2,500,000 KRW |  | rule, day fixed: Reply 3: approval_tiers
- approval_tiers | approver for up to 1,000,000 KRW | team_lead |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for up to 2,500,000 KRW | division_head |  | rule, day fixed: Reply 4: rule: approval_tiers
- approval_tiers | approver for above 2,500,000 KRW | cfo |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense of 662355 KRW | required approver based on amount | FIN_TEAM_LEAD |  | rule, day fixed: Reply 4: rule: approval_tiers
- expense 662355 KRW | required approver | team_lead |  | history, day 6: [E6]
conflict: expense 662355 KRW required approver: Reply [R3] data line states 'division_head', contradicting its own text and all other replies ([R1], [R2], [R4]) and records ([E6]-[E9]) which state 'team_lead'. ([R3] [R1] [R2] [R4] [E6] [E7] [E8] [E9])
proposed: expense 662355 KRW required approver = team_lead ([E6] [E7] [E8] [E9] [R1] [R2] [R4]) — The amount 662,355 KRW is below the 1,000,000 KRW threshold for team_lead approval per the approval_tiers rule.
```

## CASE 36: qwen3.5-27b · ingress · s14 · W-00079 · class D · day 8 · template capacity
### Task as given to the requester
How many in-house workstation (premium) units and Design Suite seats are actually available right now?
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
{"stock": 0, "seats": 7, "seats_other_region": 0}
### Counterfactual answers (generator)
{"stale": {"stock": 0, "seats": 13, "seats_other_region": 0}, "partial": {"stock": 1, "seats": 7, "seats_other_region": 0}, "neardup": {"stock": 0, "seats": 0, "seats_other_region": 0}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-SEL/stock/INV-SEL-WSP** (group IT-SEL, class A, local=False)
- CATALOG: {"group": "IT-SEL", "key": "inventory/INV-SEL-WSP"}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- DB `IT-SEL/inv/INV-SEL-WSP/qty` v4 (recorded day 6, registered day 7): 1
- RECORD FR-01366 [decision-critical] (operational/pending_intent, day 7, by it-sel.a1; DB shows n/a): In-house stock workstation (premium) 1 unit held as a Sales Team 1 replacement spare until day 15.
**need IT-SEL/license/Design Suite** (group IT-SEL, class C, local=False)
- RECORD FR-01359 [decision-critical] (db_pending/observation, day 7, by it-sel.a4; DB shows 5): Design Suite seats after transfer in use 12/21 seats. Stored value: {"seats":21,"used":12}
- RULE IT-SEL.hold_policy: {"id": "IT-SEL.hold_policy", "group": "IT-SEL", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
- RECORD FR-01091 [decision-critical] (operational/pending_intent, day 2, by it-sel.n0002; DB shows n/a): Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 12.
**need IT-TYO/license/Design Suite** (group IT-TYO, class D, local=False)
- RECORD FR-01360 [decision-critical] (db_pending/observation, day 7, by it-tyo.w00211; DB shows 3): Design Suite seats after allocation in use 29/29 seats. Stored value: {"seats":29,"used":29}
- RULE IT-TYO.hold_policy: {"id": "IT-TYO.hold_policy", "group": "IT-TYO", "title": "Stock holds", "params": {"holds_reduce_available": true}, "text": "Stock held for a specific purpose and reserved seats are excluded from the available quantity during the hold."}
### Model answer and official verdict
answer: {"seats": 7, "seats_other_region": 0, "stock": 0}
official exact match: 1 (3/3 slots)
### MATCHER CHECK FR-01366 (need IT-SEL/stock/INV-SEL-WSP): matcher says **delivered**
record text: In-house stock workstation (premium) 1 unit held as a Sales Team 1 replacement spare until day 15.
What the requester received from IT-SEL during this task:
```
The available premium workstation stock is 0 due to a hold on the single unit in inventory.
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 1: D1
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 2: D1
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | hold | 1 unit held as a Sales Team 1 replacement spare until day 15 | held until day 15 | history, day 7: [E8]
conflict: Available inventory quantity for INV-SEL-WSP: Replies [R1] and [R2] state the quantity is 1, but record [E8] indicates 1 unit is held until day 15, meaning the available quantity is 0. ([R1] [R2] [E8])
proposed: Available inventory quantity for INV-SEL-WSP = 0 ([E6] [E8]) — Although the total stock is 1 ([E6]), the single unit is held for Sales Team 1 until day 15 ([E8]), so it is excluded from the available quantity per the hold_policy rule.
---
Design Suite has 21 total seats, 12 used, with 2 seats reserved for Customer Support Team until day 12, leaving 7 available seats.
- Design Suite | total seats | 27 |  | db, day -2: Reply 1: D1
- Design Suite | used seats | 12 |  | db, day -2: Reply 1: D1
- Design Suite | available seats (database) | 15 |  | db, day -2: Reply 1: D1
- Design Suite | total seats (record) | 21 |  | history, day 7: Reply 1: H226
- Design Suite | used seats (record) | 12 |  | history, day 7: Reply 1: H226
- Design Suite | available seats (record) | 9 |  | history, day 7: Reply 1: H226
- Design Suite | total license seats | 27 |  | db, day -2: Reply 2: D1
- Design Suite | used license seats | 12 |  | db, day -2: Reply 2: D1
- Design Suite | free seats available | 15 |  | db, day -2: Reply 2: D1
- Design Suite | reserved seats | 2 seats reserved for Customer Support Team onboarding until day 12 | held until day 12 | history, day 2: [E13]
conflict: holds or reservations affecting Design Suite seat availability: Replies [R1] and [R2] state no holds or reservations were found, but record [E13] confirms an active reservation of 2 seats until day 12. ([R1] [R2] [E13])
conflict: Design Suite available seats: Reply [R1] proposes 9 available based on record H226, and [R2] proposes 15 based on the database; however, the active reservation of 2 seats reduces the available count further. ([R1] [R2] [E13] [E29])
proposed: Design Suite total seats = 21 ([E29]) — Record [E29] from day 7 updates the total seats to 21 after a transfer, superseding the database version [V5] from day -2.
proposed: Design Suite available seats = 7 ([E29] [E13]) — Based on the latest record [E29] showing 21 total and 12 used (9 free), minus the 2 seats actively reserved until day 12 per [E13].
```
### MATCHER CHECK FR-01359 (need IT-SEL/license/Design Suite): matcher says **delivered**
record text: Design Suite seats after transfer in use 12/21 seats. Stored value: {"seats":21,"used":12}
What the requester received from IT-SEL during this task:
```
The available premium workstation stock is 0 due to a hold on the single unit in inventory.
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 1: D1
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 2: D1
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | hold | 1 unit held as a Sales Team 1 replacement spare until day 15 | held until day 15 | history, day 7: [E8]
conflict: Available inventory quantity for INV-SEL-WSP: Replies [R1] and [R2] state the quantity is 1, but record [E8] indicates 1 unit is held until day 15, meaning the available quantity is 0. ([R1] [R2] [E8])
proposed: Available inventory quantity for INV-SEL-WSP = 0 ([E6] [E8]) — Although the total stock is 1 ([E6]), the single unit is held for Sales Team 1 until day 15 ([E8]), so it is excluded from the available quantity per the hold_policy rule.
---
Design Suite has 21 total seats, 12 used, with 2 seats reserved for Customer Support Team until day 12, leaving 7 available seats.
- Design Suite | total seats | 27 |  | db, day -2: Reply 1: D1
- Design Suite | used seats | 12 |  | db, day -2: Reply 1: D1
- Design Suite | available seats (database) | 15 |  | db, day -2: Reply 1: D1
- Design Suite | total seats (record) | 21 |  | history, day 7: Reply 1: H226
- Design Suite | used seats (record) | 12 |  | history, day 7: Reply 1: H226
- Design Suite | available seats (record) | 9 |  | history, day 7: Reply 1: H226
- Design Suite | total license seats | 27 |  | db, day -2: Reply 2: D1
- Design Suite | used license seats | 12 |  | db, day -2: Reply 2: D1
- Design Suite | free seats available | 15 |  | db, day -2: Reply 2: D1
- Design Suite | reserved seats | 2 seats reserved for Customer Support Team onboarding until day 12 | held until day 12 | history, day 2: [E13]
conflict: holds or reservations affecting Design Suite seat availability: Replies [R1] and [R2] state no holds or reservations were found, but record [E13] confirms an active reservation of 2 seats until day 12. ([R1] [R2] [E13])
conflict: Design Suite available seats: Reply [R1] proposes 9 available based on record H226, and [R2] proposes 15 based on the database; however, the active reservation of 2 seats reduces the available count further. ([R1] [R2] [E13] [E29])
proposed: Design Suite total seats = 21 ([E29]) — Record [E29] from day 7 updates the total seats to 21 after a transfer, superseding the database version [V5] from day -2.
proposed: Design Suite available seats = 7 ([E29] [E13]) — Based on the latest record [E29] showing 21 total and 12 used (9 free), minus the 2 seats actively reserved until day 12 per [E13].
```
### MATCHER CHECK FR-01091 (need IT-SEL/license/Design Suite): matcher says **delivered**
record text: Design Suite seats 2 seats reserved for Customer Support Team onboarding until day 12.
What the requester received from IT-SEL during this task:
```
The available premium workstation stock is 0 due to a hold on the single unit in inventory.
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 1: D2
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 1: D1
- INV-SEL-WSP | inventory_quantity | 1 |  | db, day 7: Reply 2: D1
- INV-SEL-WSP | item_id | INV-SEL-WSP |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | tier | premium |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | cost | 2339704 |  | db, day fixed: Reply 2: D2
- INV-SEL-WSP | hold | 1 unit held as a Sales Team 1 replacement spare until day 15 | held until day 15 | history, day 7: [E8]
conflict: Available inventory quantity for INV-SEL-WSP: Replies [R1] and [R2] state the quantity is 1, but record [E8] indicates 1 unit is held until day 15, meaning the available quantity is 0. ([R1] [R2] [E8])
proposed: Available inventory quantity for INV-SEL-WSP = 0 ([E6] [E8]) — Although the total stock is 1 ([E6]), the single unit is held for Sales Team 1 until day 15 ([E8]), so it is excluded from the available quantity per the hold_policy rule.
---
Design Suite has 21 total seats, 12 used, with 2 seats reserved for Customer Support Team until day 12, leaving 7 available seats.
- Design Suite | total seats | 27 |  | db, day -2: Reply 1: D1
- Design Suite | used seats | 12 |  | db, day -2: Reply 1: D1
- Design Suite | available seats (database) | 15 |  | db, day -2: Reply 1: D1
- Design Suite | total seats (record) | 21 |  | history, day 7: Reply 1: H226
- Design Suite | used seats (record) | 12 |  | history, day 7: Reply 1: H226
- Design Suite | available seats (record) | 9 |  | history, day 7: Reply 1: H226
- Design Suite | total license seats | 27 |  | db, day -2: Reply 2: D1
- Design Suite | used license seats | 12 |  | db, day -2: Reply 2: D1
- Design Suite | free seats available | 15 |  | db, day -2: Reply 2: D1
- Design Suite | reserved seats | 2 seats reserved for Customer Support Team onboarding until day 12 | held until day 12 | history, day 2: [E13]
conflict: holds or reservations affecting Design Suite seat availability: Replies [R1] and [R2] state no holds or reservations were found, but record [E13] confirms an active reservation of 2 seats until day 12. ([R1] [R2] [E13])
conflict: Design Suite available seats: Reply [R1] proposes 9 available based on record H226, and [R2] proposes 15 based on the database; however, the active reservation of 2 seats reduces the available count further. ([R1] [R2] [E13] [E29])
proposed: Design Suite total seats = 21 ([E29]) — Record [E29] from day 7 updates the total seats to 21 after a transfer, superseding the database version [V5] from day -2.
proposed: Design Suite available seats = 7 ([E29] [E13]) — Based on the latest record [E29] showing 21 total and 12 used (9 free), minus the 2 seats actively reserved until day 12 per [E13].
```
### MATCHER CHECK FR-01360 (need IT-TYO/license/Design Suite): matcher says **delivered**
record text: Design Suite seats after allocation in use 29/29 seats. Stored value: {"seats":29,"used":29}
What the requester received from IT-TYO during this task:
```
Design Suite has 0 available seats in TYO region. The latest record [E25] (day 7) shows 29 total seats with 29 in use, overriding the older database data (21 total, 18 used) cited in the reply. No active holds or reservations affect availability as previous reservations expired before day 8.
- Design Suite | total seats | 21 |  | db, day -5: Reply 1: D1
- Design Suite | used seats | 18 |  | db, day -5: Reply 1: D1
- Design Suite | available seats (calculated) | 3 |  | db, day -5: Reply 1: D1
- Design Suite | total seats | 29 |  | history, day 7: [E25]
- Design Suite | used seats | 29 |  | history, day 7: [E25]
- Design Suite | available seats | 0 |  | history, day 7: [E25]
conflict: Design Suite seat counts: [R1] reports 21 total and 18 used seats based on database version from day -5, whereas [E25] (day 7) records 29 total and 29 used seats, and [S1] confirms the 29/29 state. ([R1] [E25] [S1])
proposed: Available Design Suite seats = 0 ([E25] [S1]) — The latest record [E25] from day 7 shows 29 total seats with 29 in use, superseding the older database version cited in [R1].
```

## CASE 37: qwen3.5-27b · full_load · s14 · W-00031 · class A · day 4 · template plan
### Task as given to the requester
We want to go ahead with W-00003 as is. List the approvals needed, in order.
[Request scope] item=laptop; procurement review=excluded; equipment candidates are in-house stock, seats use the standard price; contract review=included; data residency review=excluded; equipment quote regions=requesting region only. Evaluate within the optional review scope stated here.
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
{"stale": null, "partial": null, "neardup": {"steps": ["IT_EXCEPTION", "FIN_DIVISION_HEAD"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need IT-TYO/task/W-00003/result** (group IT-TYO, class None, local=True)
- RECORD FR-01016 (operational/task_result, day 1, by it-tyo.w00143; DB shows n/a): W-00003 item result: approver=division_head, governing_rule=tiers, it_exception=False
**need HR-TYO/E-TYO-1017/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1017"}
- DB `HR-TYO/emp/E-TYO-1017/profile` v3 (recorded day -7, registered day -6): {"dept": "Dev Section 2", "grade": 5, "contract": "contractor", "hire_day": -784, "status": "active"}
**need IT-TYO/eligibility/E-TYO-1017** (group IT-TYO, class None, local=True)
- RULE IT-TYO.eligibility: {"id": "IT-TYO.eligibility", "group": "IT-TYO", "title": "Equipment tier by grade", "params": {"grade_tier": {"1": "basic", "2": "basic", "3": "standard", "4": "standard", "5": "premium"}}, "text": "Default equipment tier by grade: grade 1 basic, grade 2 basic, grade 3 standard, grade 4 standard, grade 5 premium. A higher tier needs an IT exception."}
**need LEGAL-TYO/E-TYO-1017/contract** (group LEGAL-TYO, class A, local=False)
- DB `LEGAL-TYO/contract/E-TYO-1017/terms` v6 (recorded day 1, registered day 4): {"allowed_tier": "standard", "expiry": 187, "nda": false}
- RULE LEGAL-TYO.contractor_policy: {"id": "LEGAL-TYO.contractor_policy", "group": "LEGAL-TYO", "title": "Contractor equipment policy", "params": {"premium_requires_override": true, "above_allowed_requires_override": true, "standard_with_nda": "nda", "override_approver": "legal_and_division_head", "nda_confirmation_clears": true}, "text": "Premium equipment for contractors and equipment above the contract's allowed tier need a legal exception (approver legal_and_division_head). Standard equipment for a contractor whose contract has an NDA clause needs an NDA check. However, a contractor whose signed NDA copy has been verified an
- RECORD FR-00338 (operational/exception, day -16, by legal-tyo.a3; DB shows n/a): Equipment exception of Shimizu Hayate higher tiers including premium allowed until day 12 for a project, legal check done.
**need FIN-TYO/approval** (group FIN-TYO, class A, local=False)
- RULE FIN-TYO.approval_tiers: {"id": "FIN-TYO.approval_tiers", "group": "FIN-TYO", "title": "Approval tiers", "params": {"tiers": [[1000000, "team_lead"], [2500000, "division_head"], [null, "cfo"]]}, "text": "Approver by spending amount: up to 1,000,000 KRW: team_lead, up to 2,500,000 KRW: division_head, above that: cfo."}
- RULE FIN-TYO.newcomer_waiver: {"id": "FIN-TYO.newcomer_waiver", "group": "FIN-TYO", "title": "New-hire equipment waiver", "params": {"days": 30, "cap": 1500000, "approver": "team_lead"}, "text": "Equipment items of 1,500,000 KRW or less for employees within 30 days of joining are approved by team_lead instead."}
### Model answer and official verdict
answer: {"steps": ["FIN_TEAM_LEAD"]}
official exact match: 0 (0/1 slots)

## CASE 38: qwen3.5-27b · full_load · s13 · W-00016 · class A · day 2 · template budget
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

## CASE 39: qwen3.5-27b · full_load · s12 · W-00037 · class A · day 4 · template lookup
### Task as given to the requester
Check Nakamura-san's current department, grade and assets held.
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
{"dept": "Support Section", "grade": 1, "assets": ["A-TYO-5436"]}
### Counterfactual answers (generator)
{"stale": {"dept": "Sales Section 1", "grade": 1, "assets": ["A-TYO-5436"]}, "partial": null, "neardup": {"dept": "Sales Section 2", "grade": 3, "assets": ["A-TYO-5436"]}, "wrong_owner": null}
### World facts behind the gold (by need)
**need HR-TYO/E-TYO-1008/profile** (group HR-TYO, class A, local=False)
- CATALOG: {"group": "HR-TYO", "key": "employees/E-TYO-1008"}
- DB `HR-TYO/emp/E-TYO-1008/profile` v3 (recorded day -2, registered day -1): {"dept": "Support Section", "grade": 1, "contract": "regular", "hire_day": -778, "status": "active"}
**need IT-TYO/E-TYO-1008/assets** (group IT-TYO, class None, local=True)
- DB `IT-TYO/asset/A-TYO-5436/holder` v1 (recorded day -20, registered day -20): {"emp": "E-TYO-1008"}
- QUERY SELECT asset WHERE holder=E-TYO-1008 → ["A-TYO-5436"]
### Model answer and official verdict
answer: {"assets": ["A-TYO-5436"], "dept": "Support Section", "grade": 1}
official exact match: 1 (3/3 slots)