# Experiments (draft for AAMAS 2027 submission)

Companion files: `tables/t1..t11.tex` (LaTeX tabulars), `figures/f1..f19.{pdf,png}`, `numbers*.json` / `numbers*.md` (every number below, with 95% CIs). Regenerate with `meta/scripts/paper_analysis{,2,3,4}.py` over `output/analysis_package/` (the gate ledger in `tables/gate_ledger/` comes from `meta/scripts/gates/run_all.sh`).

---

## 5 Experimental Setup

### 5.1 Benchmark: worldgen

We evaluate on **worldgen** (v4.4), a deterministic generator of authorization-partitioned organizations. An organization has $D \in \{3,5\}$ business domains (HR, IT, Finance, Procurement, Legal) replicated over $R \in \{1,2,3\}$ regions; each domain–region pair is a **group** of 1–5 agents with its own records: a versioned database, a catalog, a rulebook, and per-agent work logs. Agents may read only their own group's records; other groups are reachable only through requests. The world evolves over simulated days (3 rounds per day): employees join, transfer and leave; database versions are registered with lag; agents cover for each other, hand work over, and worker agents are spawned and retired. Every task is **cross-group** by construction: answering it requires records held by at least one group other than the requester's.

Tasks are closed-form (15 templates, e.g. available budget after pending deductions, approval route, invoice-mismatch cause, seat allocation) and are scored by exact match of all answer slots against a gold ledger that the generator derives from the ground-truth state at the time the task is issued. The generator also records, for every task, which records are decision-critical and *where they are at task time*, which yields the **state classes** we use to stratify results:

| Class | Definition (at task issue time) | Share |
|---|---|---|
| A | the designated handler (as listed on agent cards) holds the critical record in its current context window | 40% |
| B | a single agent holds it, but not the designated handler (cover, hand-over, duplicated roles, stale directory) | 20% |
| C | the answer requires records dispersed across several agents; who holds what is recorded only in the group's logs | 25% |
| D | no agent holds it in its current context: it was displaced from the window (summarized or evicted) or its holder left | 15% |
| $C_{ops}$ | (cross-cutting, 23%) the deciding fact exists only in an operational note not yet registered in the database |

Class A is the case where direct messaging *should* suffice; B isolates responder selection; C and D are the cases where *no single responder's context contains the answer*.

We generate the **base cell** $D{=}5, R{=}2$ (10 groups, ~42 agents) with three held-out evaluation seeds (12, 13, 14), 10 tasks per day; we analyze days 1–15 (150 tasks per seed). For the organization-size study we generate $R{=}1$ (5 groups), $D{=}3$ (6 groups) and $R{=}3$ (15 groups) with the same seeds, holding tasks per group per day fixed at 1 (so agent load is constant) and analyze days 1–10. All scenarios pass the generator's 17 integrity invariants, and we re-derived a sample of gold answers by hand. Tasks that are unreachable in principle (every holder of a critical record in the requester's own group is gone) are excluded (23 of 450 per cell).

### 5.2 Conditions

All conditions run on the same scenarios, the same event sequence, the same prompts, the same per-task budget (300 LLM calls / 4M tokens, counted over requester, responders and gateway together), and the same agent memory model (8k-token raw window + 2k-token summary). They differ only in how a cross-boundary request is handled:

- **Direct.** The requester picks responders from static agent cards (name, scope, skills) and messages them; each responder answers from its own context and its group's database/rules; the requester combines replies. It may ask several agents, several times, within budget.
- **Routing** (request mediation only). Requests go to a gateway in the responding group, which interprets the request, searches the group's records (hybrid BM25 + embedding retrieval with reranking over the group's work logs, plus the entity index and catalog), **selects the responders**, and forwards the question and the replies verbatim.
- **Ingress / pull by proxy** (mediation + information selection). As Routing, but the gateway additionally **assembles** the answer from the replies and the retrieved group records: it adds facts the replies omitted, resolves database versions, flags conflicts between replies and records, proposes corrected values (each proposal must cite a record or it is dropped), lists what remains unconfirmed, and re-queries members once for unconfirmed items. Replies and additions are returned with citations; the requester still decides.
- **Full-load** (reference, no partition). A single agent with read access to every group's database, rules and work logs (the same retriever, organization-wide), with the same budget. It bounds what is recoverable when authorization is removed.

To separate *who selects* from *what is selected over*, we add three variants on the base cell (Qwen3.5-27B, days 1–10):

- **Direct+relay.** Direct, but a responder may ask up to three colleagues in its own group before replying (responder-side nested asking, no record access).
- **Retrieve.** Routing plus the gateway's retrieved records, forwarded raw (within the same 12k-token evidence cap) for the requester to select over. Same mediation and same record access as Ingress; selection happens *outside* the group.
- **Sidecar.** Direct (requester picks the agent from cards), but the chosen agent carries a module that retrieves group records and assembles exactly as the Ingress gateway does, for its own reply only. Selection with record access happens *inside* the group, without mediation.

### 5.3 Backbones and protocol

Qwen3.5-27B and DeepSeek-V4-Flash are the two main backbones; Qwen3.5-9B is included to probe backbone dependence. All run with thinking disabled and temperature 0 (DeepInfra). The gateway uses the same backbone as the agents. Execution is deterministic (virtual clock, named RNG streams, event log with checkpoint/replay); retrieval settings are frozen before evaluation seeds are generated. Eight-one runs in total (36 base-cell runs, 36 organization-size runs, 9 variant runs), ≈408k LLM calls.

### 5.4 Metrics

- **Accuracy**: exact match over all answer slots. We report accuracy on the **common task set** of each (cell, backbone, seed): tasks answered by every compared condition (all conditions completed, so this equals the reachable task set; $n{=}427$ per backbone on the base cell).
- **Gap decomposition**: $\Delta_{route} = \text{Acc(Routing)} - \text{Acc(Direct)}$ (request mediation), $\Delta_{sel} = \text{Acc(Ingress)} - \text{Acc(Routing)}$ (information selection over group records), $\Delta_{total}$ their sum. Because conditions share tasks, we compute **paired** bootstrap 95% CIs (2,000 task-level resamples) and exact McNemar tests on discordant pairs.
- **Responder reach**: for every cross-group information need of a task, whether at least one agent that actually holds a decision-critical record for it (or the group's designated handler when the need is database-only) was among the agents contacted (Direct) or selected by the gateway (Routing, Ingress). This measures mediation directly.
**Boundary metrics.** Because the generator records where every decision-critical record is at task time, we can separate what the backbone cannot reason out from what the boundary withholds. Class A is the within-condition control: the handler the requester would pick already holds the record, so no boundary loss can occur (and none is observed, §6.2). We therefore define, per condition $c$:

- **Partial-state penalty** $\Pi(c) = \mathrm{Acc}_A(c) - \mathrm{Acc}_{\bar A}(c)$: the accuracy lost when the record is *not* in the designated handler's context ($\bar A$ = classes B, C, D). It is the cost of deciding on partial state, measured against the same backbone's own ceiling.
- **Penalty recovery** $\rho(c) = 1 - \Pi(c)/\Pi(\text{Direct})$: the share of Direct's penalty that condition $c$ removes.
- **Boundary delivery rate** $\delta(c)$: the share of judged cross-group needs that reach the requester in their current version (survival through the *state* gate), and its complement, the **transit loss** $\lambda(c) = L_{\text{request}}+L_{\text{route}}+L_{\text{select}}+L_{\text{state}}$, with the loss profile in Fig. 12.
- **Utilization** $\upsilon(c)$: accuracy on tasks whose decision-critical records were all delivered—what remains once the boundary is no longer the bottleneck.

$\Pi$ and $\rho$ need only the task labels; $\delta$, $\lambda$ and $\upsilon$ need the event log. None involves a weighting choice.

- **Gateway behaviour**: members selected per request, referral rate, additions/conflicts/proposals per assembly, dropped (uncited) proposals, re-query rate.
- **Cost**: LLM calls and tokens per task (all components), estimated USD per task and per correct answer at provider list prices.

Scoring was cross-checked against the benchmark's official scorer on all 8,919 scored answers (identical verdicts).

---

## 6 Results

### 6.1 Pull by proxy recovers 18–20 points over direct messaging (Table 1)

**Table 1.** Exact-match accuracy (%) on the base cell, days 1–15, $n{=}427$ common tasks per backbone. Gaps in percentage points with paired bootstrap 95% CIs. *(file: `t1_main.tex`)*

| Backbone | Direct | Routing | **Ingress** | Full-load | $\Delta_{route}$ | $\Delta_{sel}$ | $\Delta_{total}$ |
|---|---|---|---|---|---|---|---|
| Qwen3.5-27B | 33.0 | 38.4 | **53.4** | 52.5 | +5.4 [+1.6, +9.1] | +15.0 [+10.3, +19.9] | +20.4 [+15.0, +25.3] |
| DeepSeek-V4-Flash | 34.7 | 45.0 | **52.7** | 62.5 | +10.3 [+6.6, +13.8] | +7.7 [+3.3, +11.9] | +18.0 [+13.3, +23.0] |
| Qwen3.5-9B | 18.7 | 22.7 | 25.1 | 38.4 | +4.0 [+0.5, +7.5] | +2.3 [−1.6, +6.3] | +6.3 [+2.3, +10.1] |

With both main backbones, Ingress raises accuracy by 18–20 points over Direct (McNemar $p < 10^{-12}$; 27B: 112 tasks solved only by Ingress vs. 25 only by Direct). Mediation alone (Routing) recovers 5 points on 27B and 10 on DeepSeek; selection over group records recovers the remaining 15 and 8 points. On 27B, Ingress reaches the accuracy of the unpartitioned reference (52.5, difference +0.9 [−4.4, +6.3]) while respecting the partition; on DeepSeek a 10-point gap to Full-load remains.

### 6.2 Where the gains come from: state classes (Figures 1–2, Table 3)

**Figure 1** (`f1_accuracy_by_class`): accuracy by state class and condition, two panels (27B, DeepSeek), Full-load as a reference marker.
**Figure 2** (`f2_gap_decomposition`): $\Delta_{route}$ and $\Delta_{sel}$ per class with 95% CIs.

| 27B, class ($n$) | Direct | Routing | Ingress | Full-load | $\Delta_{route}$ | $\Delta_{sel}$ |
|---|---|---|---|---|---|---|
| A (180) | 71.7 | 68.3 | 69.4 | 78.3 | −3.3 [−9.4, +2.8] | +1.1 [−5.0, +6.7] |
| B (85) | 11.8 | 32.9 | 55.3 | 40.0 | +21.2 [+10.6, +31.8] | +22.4 [+9.4, +35.3] |
| C (96) | 1.0 | 11.5 | 32.3 | 28.1 | +10.4 [+4.2, +17.7] | +20.8 [+12.5, +30.2] |
| D (66) | 1.5 | 3.0 | 37.9 | 33.3 | +1.5 [−3.0, +7.6] | +34.8 [+22.7, +47.0] |
| $C_{ops}$ (96) | 1.0 | 10.4 | 31.2 | 24.0 | +9.4 [+4.2, +15.6] | +20.8 [+12.5, +30.2] |

| DeepSeek, class ($n$) | Direct | Routing | Ingress | Full-load | $\Delta_{route}$ | $\Delta_{sel}$ |
|---|---|---|---|---|---|---|
| A (180) | 72.8 | 75.6 | 72.8 | 73.3 | +2.8 [−2.2, +7.8] | −2.8 [−8.9, +2.8] |
| B (85) | 14.1 | 44.7 | 50.6 | 60.0 | +30.6 [+20.0, +41.2] | +5.9 [−4.7, +16.5] |
| C (96) | 4.2 | 17.7 | 35.4 | 56.2 | +13.5 [+6.2, +21.9] | +17.7 [+7.3, +28.1] |
| D (66) | 1.5 | 1.5 | 25.8 | 45.5 | 0.0 | +24.2 [+15.2, +34.8] |
| $C_{ops}$ (96) | 4.2 | 17.7 | 31.2 | 53.1 | +13.5 [+5.2, +21.9] | +13.5 [+4.2, +22.9] |

Three regularities hold for both backbones. (i) **Class A shows no gap**: when the designated handler holds the record in context, direct messaging already works (≈70%), and neither mediation nor selection changes it. (ii) **Mediation acts on B**: when the holder is not the card-designated agent, Routing lifts accuracy by 21–31 points, and the responder-reach metric (Fig. 6) shows why: the holder is contacted for 47% (27B) / 61% (DeepSeek) of B-class needs under Direct but 76% / 85% under Routing. (iii) **Selection acts on C and D**: Direct and Routing are at 1–18% on C and 1.5–3% on D; Ingress reaches 26–38%, with $\Delta_{sel}$ of +18 to +35 points. In class D the holder is contacted just as often under Direct as under Routing (72–78%; Fig. 6), yet accuracy stays near zero because the record has left every agent's context—only selection over the group's logs recovers it. The same holds for $C_{ops}$ facts that exist only in operational notes. The backbones differ on B: DeepSeek responders, once reached, include what they hold ($\Delta_{sel}$ ≈ 0), whereas 27B responders omit it and the gateway's record-grounded assembly supplies it ($\Delta_{sel}$ = +22). This is the abstract's claim made concrete: the gains from selection concentrate in the classes where no single responder's context contains the answer.

**Gateway behaviour (Table 4, `t4_gateway.tex`).** Per request the gateway selects 2.3 (27B) / 2.6 (DeepSeek) members and refers 2–4% of requests to another group on recorded ownership exceptions. Per assembly it adds 1.6 / 3.3 facts from records that no reply mentioned, flags 0.6 / 0.7 conflicts, makes 0.6 / 0.5 proposals (6–10% of proposals are dropped by the harness for lacking a citation), and re-queries members on 37% / 63% of requests.

### 6.3 Who selects, over what, and where (Table 2, Figure 4)

**Table 2.** Variants on the base cell, Qwen3.5-27B, days 1–10, $n{=}285$ common tasks. "Med." = request mediation by a gateway; "Sel." = selection over group records. *(file: `t2_variants.tex`)*

| Condition | Med. | Sel. | Where selection happens | Acc. | A | B | C | D | $C_{ops}$ | Calls | Tokens (k) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Direct | – | – | requester, from replies | 33.7 | 71.1 | 15.5 | 1.6 | 0.0 | 1.5 | 21 | 229 |
| Direct+relay | – | – | responder asks peers (no records) | 33.7 | 71.1 | 13.8 | 3.2 | 0.0 | 3.1 | 38 | 420 |
| Routing | ✓ | – | requester, from replies | 40.4 | 68.6 | 34.5 | 17.5 | 2.3 | 15.4 | 35 | 380 |
| Retrieve | ✓ | raw | requester, from replies + raw records | 47.0 | 66.9 | 48.3 | 25.4 | 20.9 | 21.5 | 28 | 328 |
| Sidecar | – | ✓ | inside the group, per agent | 55.8 | 76.0 | 39.7 | 42.9 | 39.5 | 40.0 | 26 | 284 |
| **Ingress** | ✓ | ✓ | inside the group, group gateway | **56.1** | 69.4 | 51.7 | 39.7 | 48.8 | 36.9 | 49 | 576 |
| Full-load (ref.) | n/a | n/a | no partition | 53.7 | 77.7 | 43.1 | 28.6 | 37.2 | 24.6 | 7 | 200 |

- **Asking more agents does not help without records.** Direct+relay, where responders can consult three colleagues, is identical to Direct (+0.0 [−3.5, +3.5]) at 1.8× the cost: the information is not in colleagues' contexts either (C, D).
- **Record access alone is not enough; selection must happen inside the group.** Retrieve gives the requester the same retrieved records the Ingress gateway sees, under the same mediation, and gains 13 points over Direct—but remains 9 points below Ingress (−9.1 [−15.4, −3.5], $p{=}0.004$). Selecting from raw records outside the group, in the requester's context, loses what the gateway's record-grounded assembly recovers.
- **Selection with record access is the dominant factor; mediation adds on top.** Sidecar—no mediation, but assembly over group records inside the group—matches Ingress overall (55.8 vs 56.1, −0.4 [−6.3, +5.3]) at half the calls and tokens, and leads on C and $C_{ops}$. Ingress leads on B (+12) and D (+9), the classes where reaching the right responders matters (the Sidecar's requester still picks agents from static cards: reach 65% vs 77% for Ingress).
- Figure 4 (`f4_accuracy_vs_cost`) places the seven conditions on an accuracy–tokens plane: Sidecar and Ingress form the accuracy frontier; Full-load is cheapest because a single agent makes 7 calls, but it requires removing the partition.

### 6.4 Organization size and task breadth (Figure 3, Table 5)

**Figure 3a** (`f3_scale`): $\Delta_{total}$ with CIs for organizations of 5, 6, 10 and 15 groups (27B, days 1–10, restricted to the 11 task templates present in all cells; $n$ = 118 / 167 / 235 / 350): +12.7 [+5.1, +21.2], +26.9 [+18.6, +35.3], +16.6 [+9.4, +23.8], +16.9 [+11.4, +22.0]. The gain is significant in every cell and shows no monotone trend in $G$; with agent load held constant, the number of groups in the organization does not by itself change what the gateway recovers.

**Figure 3b**: pooling all 27B cells ($n{=}1162$) and splitting by the number of groups a task spans, both components shrink with breadth: $\Delta_{total}$ = +27.0 (2 groups), +26.4 (3), +15.5 (4), +8.0 [+2.3, +14.3] (5+). Direct accuracy itself drops to 17% on 5+-group tasks; the requester must still combine several gateways' assembled answers, and that outer combination is not mediated. This is the main open limitation of placing the proxy at each group boundary.

### 6.5 Over time (Figure 5)

**Figure 5** (`f5_by_day_window`): accuracy per 5-day window. Records accumulate and more facts leave agents' windows as days pass; Direct declines from 36% (days 1–5) to 32% (11–15) on 27B. Ingress stays ahead in every window—$\Delta_{total}$ = +23.8, +21.1, +16.2 on 27B and +20.3, +15.5, +18.3 on DeepSeek—with a modest narrowing on 27B as the evidence available per request grows against a fixed 12k-token evidence cap.

### 6.6 Cost (Table 6)

| 27B, base cell | Acc. | Calls/task | Tokens/task (k) | USD/task | USD/correct |
|---|---|---|---|---|---|
| Direct | 33.0 | 21 | 250 | 0.082 | 0.25 |
| Routing | 38.4 | 36 | 410 | 0.147 | 0.38 |
| Ingress | 53.4 | 50 | 605 | 0.224 | 0.42 |
| Full-load | 52.5 | 7 | 192 | 0.061 | 0.12 |

Mediation and selection cost 1.7× and 2.4× the tokens of Direct (gateway interpret/route/assemble calls plus fan-out to ~2.3 members per request); per correct answer, Ingress costs 1.7× Direct. Sidecar reaches the same accuracy at 1.2× Direct's tokens (Table 2). DeepSeek makes about twice as many calls per task in every condition (42 → 83) but at a lower price per token. No condition hit the per-task budget on 27B; Direct on 9B exhausted it on 10% of tasks.

### 6.7 Backbone dependence (Figure 7)

On Qwen3.5-9B the total gain is +6.3 [+2.3, +10.1] and $\Delta_{sel}$ is not significant (+2.3 [−1.6, +6.3]); Ingress stays at 4% on C and D even though its gateway adds the most records per assembly of any backbone (4.5 facts, re-query on 50%). The assembled evidence is delivered but not used, and the gateway's own interpretation/selection steps also run on the weaker model. Full-load (38.4) is the best 9B condition. The benefit of pull by proxy therefore presupposes a backbone that can both operate the gateway and exploit cited evidence; we report the two main backbones as the supported regime.

### 6.8 Failure analysis and limitations

- **Where Ingress loses to Direct.** By template (Table 8), gains are largest on tasks that read dispersed or displaced state—contract gate +68, in-house capacity +41, lookup +37, available budget +32, conflicting commitments +28—and absent or slightly negative on rule-application tasks: approval plan −3.2 [−12.7, +5.6] and approval precedence −5.2 [−17.2, +6.9] (both n.s.). Tracing the 14 base-cell tasks that only Direct solved (all class A/B) shows two gateway-side causes: the assembly forwards responders' structured items and the gateway's own additions but not responders' free-text explanations, so hints such as "we hold employee contracts, not supplier contracts" are flattened to *not found*; and when the requested entity is absent the gateway answers *cannot determine* instead of returning the applicable rule. Both are fixable in the assembly step and did not affect the between-condition comparison (they lower Ingress).
- **Known harness effects.** A race in budget accounting under parallel responders left 5 Ingress tasks (0.06% of answers) without a final submission; 9B produced 7 format errors by emitting the string "None" for null. Three tasks (0.3%) have a gold answer that depends on an ambiguity between the rule text and the generator's contract-denial logic; all conditions scored 0 on them.
- **Scope.** Scenarios are synthetic; the state-class mix (40/20/25/15) is set by the generator, not observed in the wild, so absolute accuracies should not be read as deployment estimates. The analysis horizon is 15 days; the 30-day horizon is available only for Direct and Full-load on 27B.

### 6.9 Where needs are lost: a gate ledger (Figure 12, Table 11)

To locate the loss rather than only measure it, we trace every cross-group information need that depends on a decision-critical record through the gates it must pass: the requester must ask the holding group (**request**), the question must reach an agent that holds the record (**route**), the record must be included in what comes back (**select**: present in the responder's window, included in its answer, found by the gateway's search, kept in the assembly), the delivered record must be the current version (**state**), and the requester must use it correctly (**use**). An offline scorer assigns each need its first failing gate from the event log and the cached prompts, matching records by canary values and entity–value signatures; it is a heuristic (needs grounded only in database or rule lookups are not judged), so we read it for contrasts between conditions, not absolute levels. On the base cell this judges 453 needs per backbone per condition, almost all in classes B–D.

**Figure 12** (`f12_gate_ledger`): (a) survival of needs across gates for Qwen3.5-27B; (b) first failing gate per 100 judged needs for both main backbones. Under Direct, half of all needs die at **route** (51 per 100 on 27B, 44 on DeepSeek): the requester asks an agent that does not hold the record. Routing removes most of that loss (to 11 / 9) but the needs then die at **select**—the reached responder has the record outside its window (9 / 25) or leaves it out of its answer (12 / 5)—and at **use**. Ingress removes route loss entirely (0) and halves state loss (9 → 3 on 27B), leaving three terminal losses: records the gateway's search did not surface (9 / 6), records that were retrieved or replied but dropped in assembly (17 / 6), and records delivered but misused (24 / 31). Needs that survive to the end rise from 2 (Direct) to 10 (Routing) to 27 (Ingress) per 100 on 27B. The assembly loss is the actionable residual: it is where the omitted-explanation limitation of §6.8 lives.

**Figure 12c** (`f12c_gate_composition`) splits the ledger by state class and by task breadth. Route loss is the dominant failure in B, C and D under Direct and is absent under Ingress in every class; for tasks spanning 5+ groups, however, Ingress needs die at **use** (45 per 100, vs. 13 for 2-group tasks): the records arrive, from several gateways, and the requester fails to combine them—consistent with the breadth limitation in §6.4.

### 6.10 Placement matters through visible state (Figure 4b)

**Figure 4b** (`f4b_coverage_vs_accuracy`): task accuracy against the share of a task's decision-critical records that were actually delivered to the requester (none / some / all), by condition. In every condition accuracy is near zero when nothing is delivered (5–18%) and high when everything is (50–83%); the conditions differ mainly in how often they reach "all" (Direct 18 of 282 judged tasks on 27B, Routing 61, Ingress 103). At full delivery Ingress still exceeds Direct (83 vs 50%), which we attribute to the cited, de-duplicated form in which the gateway delivers records; we do not separate this from selection in the present design.

### 6.11 What the wrong answers are (Figure 9, Table 9)

The generator stores, for each task, the answer that would result from four specific failures: using a superseded version (*stale*), omitting a component (*partial*), confusing a near-duplicate entity (*near-dup*) and asking the wrong owner (*wrong-owner*). **Figure 9** (`f9_failure_modes`) classifies every submitted answer as correct, one of these, another wrong answer, or no answer. Named failures account for 15% of Direct answers on 27B (partial 8.7, stale/partial 5.6) and 5% of Ingress answers (3.5, 1.6); the component-omission failures that assembly targets fall by more than half, while near-dup confusions rise slightly (0 → 2.3%) as the gateway brings more candidate records into view. Most wrong answers (38–52%) match none of the named counterfactuals: they are reasoning or combination errors over partially delivered state, consistent with the large *use* loss in the ledger.

### 6.12 Time-varying records (Figure 10)

**Figure 10** (`f10_fact_age`): accuracy against the age of the task's most recently changed decision-critical fact (days since it was recorded). Facts that changed the same day or the day before (292 of 427 tasks) are the hard case—Direct 21% on 27B—because the change is not yet in the database and lives only in a responder's log; this is where the gap is largest (+19 and +34 points). Facts older than a week are mostly registered and all conditions score 67–94%. The proxy's value is concentrated on fresh changes.

### 6.13 Task types (Figure 14)

**Figure 14** (`f14_template_heatmap`): accuracy of every condition on each of the 15 task types (27B, all cells) alongside each type's state-class mix. Types that read in-house capacity, contract terms or available budget are 65–80% class C/D and gain 31–68 points; lookup and conflict-resolution types are 40% class B with no C/D and gain 28–37 points, mostly through Routing; the two rule-application types (plan, precedence) are 66–81% class A and show no gain. Seat allocation (93% C/D) stays near zero in every condition, including Full-load: a reasoning limit, not a boundary loss. The ordering of gains follows the class mix, not the task template, which is the prediction of the state-class model.

### 6.14 Context hygiene (Figure 13, appendix)

Serving requests leaves residue in agents' windows. **Figure 13b** shows that after the first week 53–72% (Direct) and 65–90% (Routing/Ingress) of a requester's raw window consists of entries from other tasks—served requests and the agent's own earlier tasks—and that the gateway's fan-out (2.3–2.6 members per request) raises this residue relative to Direct; Full-load agents, who serve no one, stay below 20%. **Figure 13a** relates an agent's own-task accuracy to the number of cross-group requests it served and shows no monotone penalty in any condition, though the heavily-loaded bins are small.

### 6.15 First contact versus revisit (Figure 15)

Tasks that return to a subject the requester has already handled (38% of tasks) behave differently from first contacts. **Figure 15** (`f15_revisit`) splits tasks into first contact, revisit with the fact unchanged, and revisit after the fact changed. On first contacts the gain is largest: +30.9 [+24.0, +38.2] on 27B and +26.3 [+20.2, +33.2] on DeepSeek. When the subject was seen before and nothing changed, the requester's own log already holds the earlier answer and Direct reaches 50% without any proxy; the gain shrinks to +2.4 [−3.9, +9.4] / +3.1. When the fact changed in between (38 tasks), every condition fails (10–21%), and the wrong answers are mostly *not* the superseded value (≤8% stale): the requester neither reuses its old answer nor reliably obtains the new one. Pull by proxy therefore pays mainly on first contact; keeping cross-group answers current across revisits is an open problem that a request-side state (an egress-side cache with revalidation) would have to address.

### 6.16 What bounds the gain: discoverability and reasoning (Figure 16)

**Figure 16a** (`f16_bounds`) stratifies tasks by how discoverable their hardest decision-critical record is, using the generator's tiers: H0, the record's text is in a member's log; H1, only an activity trace of who handled it; H2, the value appears in a later utterance that refers back to the subject and carries no index key. Ingress reaches 68% / 55% on H0 / H1 (gains of +45 / +47 on 27B) but 26% on H2 (+23 [+15, +32]); the gateway's search surfaces H2 records for only 11–17% of needs. **Figure 16b** stratifies by the generator's reasoning tier: on pure lookups (R0) Ingress reaches 89–95%, on one-rule and conditional tasks 56–57%, and on multi-hop tasks (R3) 9–14% (+10 [+3, +18] on 27B; n.s. on DeepSeek). Among needs that were delivered and still answered wrongly, 61% belong to a single multi-step template (seat allocation). The proxy turns lookups into near-solved problems; its gain is bounded on one side by what retrieval over logs can discover and on the other by reasoning that remains with the requester.

### 6.17 Operational effects (Figure 17)

**Load.** Under Direct, the single most-asked member of a group receives 61% (27B) / 53% (DeepSeek) of the group's inbound requests—the card-listed handler—whereas the gateway spreads requests over the members that hold the records (35% / 31%; Herfindahl index 0.50 → 0.27). **Latency.** Serialized gateway steps make Ingress slower: median 15.9 min per task versus 3.3 for Direct on 27B (p90 44.9 vs 9.7), a cost to weigh alongside tokens (Table 6). **Departed holders.** In the 51 tasks whose decision-critical record was held only by members who had since left, Direct and Routing score 2%; Ingress 43% (27B) / 27% (DeepSeek); Full-load 35% / 49%. **Recorded ownership exceptions.** 65 tasks involve a recorded agreement that another group executes a budget; the gateway referred the request in only 15 of them on 27B, scoring 53% when it did versus 28% when it did not (Direct 25%). The referral rule works but is under-triggered—an actionable refinement of the route step.

### 6.18 Boundary metrics (Table 12)

**Table 12** (`t12_boundary_metrics.tex`) reports the metrics of §5.4. Direct pays a partial-state penalty of 67 pp on both main backbones: it answers 72–73% of class-A tasks and 5–7% of the rest. Routing removes about a fifth of that penalty ($\rho$ = 23% / 20%); Ingress removes 58% on Qwen3.5-27B and 47% on DeepSeek ($\Pi$ = 28 / 35 pp), delivering 51% / 56% of judged needs in their current version against 16% / 23% for Direct, with transit loss falling from 84 / 77 to 49 / 44 per 100 needs. Utilization on fully delivered tasks rises from 50% / 45% (Direct) to 83% / 78% (Ingress). The unpartitioned reference removes 33% (27B) and 72% (DeepSeek) of the penalty: on DeepSeek the remaining gap between Ingress and Full-load is mostly a delivery gap (56% vs 62%) with similar utilization. On Qwen3.5-9B no condition recovers the penalty ($\rho \le 0$); its delivery rate rises (7 → 25%) but utilization does not follow, which is the backbone limitation of §6.7 stated in boundary terms.

---

## Figure and table plan (what to show, why)

| Item | Content | Claim it supports | Placement |
|---|---|---|---|
| Table 1 (+T1x) | Accuracy by condition × backbone; $\Delta_{route}$, $\Delta_{sel}$, $\Delta_{total}$ with CIs; T1x adds reach, stale-answer rate, crossings/need, tokens/correct | headline: +18–20 pp; mediation 5–10 pp; selection the rest | main |
| Fig. 1 + Fig. 2 | Accuracy by state class; $\Delta_{route}$ vs $\Delta_{sel}$ per class with CIs | gains concentrate where no single context has the answer; A unchanged | main (merge as one 2-row figure) |
| Fig. 8 | Forest plot of each rung across backbones and organization sizes; class A vs $C_{ops}$ | the decomposition replicates; A is a negative control | main |
| Fig. 19 | Worked examples: communication graph of one class-D and one class-C task under Direct vs Ingress, from the logs | makes the two decisions and the group-record access concrete | main (as Fig. 1 companion or in §6.2) |
| Fig. 12 (+Table 11) or Fig. 18 | Gate ledger: survival curve + first-failing-gate heatmap (Fig. 12), or the same ledger as a need-flow (alluvial) diagram (Fig. 18) | *where* each condition loses needs; Routing fixes route, Ingress fixes route+state, residual is assembly/use | main (choose one) |
| Fig. 6 (+T7) | Responder reach by class | mediation mechanism; reaching the holder is necessary (B) but not sufficient (D) | main or appendix |
| Table 2 + Fig. 4 | 7 conditions with factor columns (mediation, selection, location); accuracy vs tokens | relay ≠ help; raw records < in-group selection; sidecar ≈ ingress at half cost | main |
| Fig. 4b | Accuracy vs share of decision-critical records delivered | placement acts through visible state | main or appendix |
| Fig. 3 + Fig. 11 + Table 5 | gain vs organization size; gain vs task breadth; accuracy curves vs $G$ and horizon | no size effect; breadth is the open limitation; gain persists over the horizon | main (Fig. 3), appendix (Fig. 11) |
| Fig. 9 (+Table 9) | Counterfactual failure modes per condition | assembly removes omission failures; residual errors are reasoning errors | appendix |
| Fig. 10 | Accuracy vs age of the needed fact | value concentrates on fresh, unregistered changes | main (small) or appendix |
| Fig. 14 | Task-type × condition heatmap with class mix | gains follow class mix, not template | appendix |
| Fig. 12c | Gate composition by class and by breadth | which gate each class dies at; use-loss at 5+ groups | appendix |
| Table 4 | Gateway behaviour statistics | what the proxy actually does | appendix |
| Table 6 | calls, tokens, USD per task and per correct | cost of the proxy | main (compact) |
| Table 12 | boundary metrics: partial-state penalty $\Pi$, recovery $\rho$, delivery $\delta$, transit loss $\lambda$, utilization $\upsilon$ | one row per condition that separates boundary loss from reasoning | main |
| Fig. 7, Fig. 5, Fig. 13 | 9B by class; 5-day windows; context residue and responder load | backbone dependence; persistence; hygiene | appendix |
| Fig. 15 | first contact vs revisit (unchanged / changed) | gain is on first contact; revisits after a change fail everywhere | main (small) or appendix |
| Fig. 16 | accuracy by discoverability tier and reasoning tier | retrieval and reasoning bound the gain | appendix |
| Fig. 17 | load concentration; latency; departed holders; referrals (text) | operational effects of the proxy | appendix |
| Table 3, 8 | per-class and per-template numbers | reproducibility | appendix |

Suggested main-text set for 8 pages: Table 1, Fig. 1+2 (merged), Fig. 8, Fig. 12, Table 2 + Fig. 4, Fig. 3, Table 6; everything else in the appendix.

## Claim-to-evidence map (Table 10)

| RQ | Claim | Contrast | Measure | Shown in |
|---|---|---|---|---|
| RQ1 main effect | C1 pull by proxy recovers 18–20 pp over direct messaging across two backbones | Direct vs Ingress, paired | exact-match accuracy, paired bootstrap, McNemar | T1, F8 |
| RQ2 decomposition | C2 mediation alone recovers 5–10 pp; selection over group records recovers the rest | Direct→Routing→Ingress rungs | $\Delta_{route}$, $\Delta_{sel}$ | T1, F2, F8 |
| | C3 selection gains concentrate where no single responder's context holds the answer; class A is unaffected | same, stratified by state class | per-class $\Delta$; reach; gate ledger | F1, F2, F6, F12, T3 |
| | C4 mediation acts by reaching the holder; selection acts by delivering records the holder cannot or does not supply | gates request/route/select/state | first failing gate per need | F12, F12c, T11 |
| | C5 accuracy follows visible state | all conditions, binned by delivered records | coverage vs accuracy | F4b |
| RQ3 design space | C6 record access alone is insufficient; selection must occur inside the group (Retrieve < Ingress); nested asking without records does nothing (Direct+relay = Direct); a per-agent module matches the gateway at half the cost (Sidecar ≈ Ingress), with the gateway ahead on B/D | 7 conditions, factor columns | accuracy by class, tokens | T2, F4, F9 |
| RQ4 boundary conditions | C7 the gain does not depend on organization size and persists over the horizon; it shrinks with the number of groups a task spans | $G \in \{5,6,10,15\}$; day windows; groups spanned | $\Delta_{total}$ with CIs | F3, F11, T5 |
| | C8 the gain requires a capable backbone (9B: +6 pp, $\Delta_{sel}$ n.s.) | three backbones | T1, F7 | T1, F7 |
| | C9 value concentrates on fresh, unregistered changes | fact age bins | accuracy vs fact age | F10 |
| | C10 assembly removes omission failures; residual errors are reasoning over delivered state | counterfactual answers | failure-mode shares | F9, T9 |
| | C11 the gain is on first-contact subjects; revisits after a change fail in every condition | first / revisit-unchanged / revisit-changed | accuracy, stale share | F15 |
| | C12 the gain is bounded by record discoverability (H2) and multi-hop reasoning (R3) | tiers H0–H2, R0–R3 | accuracy, in-evidence rate | F16 |
| | C13 the proxy spreads load from the card handler to holders, at a latency cost; it recovers records of departed members | messages, wall-clock, departed-holder tasks | top-1 share, minutes/task | F17 |

## Figure captions (draft)

- **Fig. 1.** Exact-match accuracy by state class on the base cell (days 1–15, $n$ per class shown). Bars: Direct, Routing, Ingress (pull by proxy); diamonds: Full-load reference without partition. Class A (handler holds the record in context) is unaffected; B is recovered by responder selection; C, D and $C_{ops}$ are recovered only when the gateway selects over the group's records.
- **Fig. 2.** Decomposition of the gain into request mediation ($\Delta_{route}$ = Routing − Direct) and information selection ($\Delta_{sel}$ = Ingress − Routing) per state class; error bars are paired bootstrap 95% CIs.
- **Fig. 3.** (a) Total gain of pull by proxy for organizations of 5–15 groups with agent load held constant (27B, days 1–10, shared task templates). (b) Gain components by the number of groups a task spans, pooled over all 27B cells.
- **Fig. 4.** Accuracy against tokens per task for all seven conditions (27B, base cell, days 1–10, $n{=}285$).
- **Fig. 4b.** Task accuracy by the share of decision-critical records delivered to the requester (none / some / all), per condition; numbers above bars are task counts. Accuracy tracks delivered state in every condition; conditions differ mainly in how often they deliver everything.
- **Fig. 5.** Accuracy per 5-day window as records accumulate.
- **Fig. 6.** Responder reach: fraction of cross-group information needs for which an agent holding a decision-critical record was contacted (Direct) or selected by the gateway (Routing, Ingress), by state class.
- **Fig. 7.** Accuracy by state class for Qwen3.5-9B.
- **Fig. 8.** Paired accuracy differences for each rung of the ladder—request mediation (Routing − Direct) and information selection (Ingress − Routing)—across three backbones and three organization sizes (a), and for class A (negative control) versus $C_{ops}$ tasks (b). Error bars: paired bootstrap 95% CIs.
- **Fig. 9.** Share of tasks whose submitted answer is correct, matches one of the generator's counterfactual answers (stale version, missing component, near-duplicate entity, wrong owner), is another wrong answer, or is missing; base cell, two backbones, and the seven variants.
- **Fig. 10.** Accuracy against the number of days since the task's most recently changed decision-critical fact was recorded.
- **Fig. 11.** Accuracy of each condition against organization size (a) and over three 5-day windows for two backbones (b).
- **Fig. 12.** Gate ledger. (a) Share of judged cross-group needs still alive after each gate (request → route → select → state → use) for Qwen3.5-27B. (b) First failing gate per 100 judged needs for both backbones; "sel" splits selection loss into record outside the responder's window, omitted from its answer, not surfaced by the gateway's search, and dropped in assembly. Heuristic offline scorer; needs resolvable from database or rule lookups alone are not judged.
- **Fig. 12c.** First-failing-gate composition for Direct (plain) and Ingress (hatched) by state class (a) and by the number of groups a task spans (b).
- **Fig. 13.** Context hygiene (appendix). (a) Agents' accuracy on their own tasks against the number of cross-group requests they served. (b) Share of a requester's raw window occupied by entries from other tasks, and raw-window tokens at the first call, by day.
- **Fig. 14.** (a) Accuracy of each condition on each task type (27B, all cells; row labels give $n$ and $\Delta_{total}$). (b) State-class mix of each task type.
- **Fig. 15.** Accuracy on first-contact tasks, revisits of an unchanged subject, and revisits after the fact changed; red labels give the share of answers equal to the superseded value.
- **Fig. 16.** Accuracy by (a) the discoverability tier of the task's hardest decision-critical record (H0: text in a log; H1: activity trace only; H2: value in a later referring utterance without an index key) and (b) the generator's reasoning tier. Solid bars: Qwen3.5-27B; faded: DeepSeek-V4-Flash.
- **Fig. 17.** (a) Share of a group's inbound cross-group requests received by its most-asked member. (b) Wall-clock minutes per task (median; whisker to the 90th percentile).
- **Fig. 18.** Flow of judged cross-group needs through the five gates for Direct, Routing and Ingress (Qwen3.5-27B, base cell, 453 needs each). Band width is the share of needs still alive; bands peeling off are needs lost at that gate, with the selection loss split into window / answer / search / assembly. Heuristic offline scorer.
- **Fig. 19.** Two tasks from the logs (Qwen3.5-27B, seed 12). Top: W-00065 (class D)—the asset assignment exists only in a note written by a worker who has since left; Direct asks the card-listed handler, who answers from the database view; the gateway searches the group log and adds the note with its citation. Bottom: W-00016 (class C)—the available budget depends on deductions held by several members; Direct asks the handler twice; the gateway fans out to four members, adds a cancelled commitment from the records, flags one conflict and proposes a corrected value. ★ card-listed handler; ● member holding a decision-critical record; dashed red: departed member; yellow: group records readable only inside the group.
