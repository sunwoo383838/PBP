# g2g 그룹 경계 통신 실험 — 외부 분석 패키지

기준: 2026-10-02, 모든 런 완료. 런 81개(1차 36, G 셀 36, 부록 9).

## 1. 폴더 구성

| 경로 | 내용 |
|---|---|
| `tables/` | 런·과제·LLM 호출·경계 결정·메시지·검색·묶음 단위 원자료 표 (CSV, 큰 것은 .csv.gz) |
| `agg/` | 원자료에서 계산한 요약 표 (조건별 정확도·비용, 부록 7조건, 층화, 일자 창, 게이트웨이 요약, 런 묶음 비용) |
| `logs/<run_id>/` | 런마다 원 로그: `events.jsonl.gz`(WAL, 모든 사건과 LLM 메시지 원문), `obs_*.jsonl.gz`(분석용 관측 기록), `timing_llm.jsonl.gz`(벽시계 지연), `manifest.json`, `run.json`, `supervise.jsonl`(재시작 이력), `retarget.jsonl`(목표 일수 변경 이력) |
| `meta/` | 실행 설정(`configs_main`, `configs_appendix`), 동결 커밋, 변경 이력(`HARNESS_CHANGES.md`), 시나리오(정답 원장 `gold.jsonl.gz`, 과제 `work.jsonl.gz`, 세계 구성, 검수 결과), 보고서(`reports/`), 실행·분석 스크립트(`scripts/`) |

`run_id` 형식: `<experiment>/<cell>/<model>/<condition>/<seed>` (로그 폴더 이름은 `/`를 `__`로 바꿈).

## 2. 실험 구성

| 실험 | 셀 (그룹 수) | 모델 | 조건 | 시드 | 분석 일수 |
|---|---|---|---|---|---|
| main (1차) | base = D5·R2 (10) | qwen3.5-27b, qwen3.5-9b, deepseek-v4-flash | direct, routing, ingress, full_load | s12, s13, s14 | 1~15일 |
| gcell (2차) | R1 = D5·R1 (5), D3 = D3·R2 (6), R3 = D5·R3 (15) | qwen3.5-27b | 같은 4조건 | 같음 | 1~10일 |
| appendix (부록) | base (10) | qwen3.5-27b | direct_relay, retrieve, sidecar | 같음 | 1~10일 |

- G 셀은 그룹당 하루 1과제(하루 과제 수 = 그룹 수)로 에이전트당 과제 수를 기준 셀과 같게 맞춤.
- 1차는 원래 30일 목표였으나 15일로 단축. 27B direct·full_load와 일부 런은 15일 넘게 진행된 기록이 남아 있음 → `within_target_days`로 거름.
- 모든 모델 thinking 끔, 온도 0, 과제 예산 호출 300회·토큰 400만(retrieve만 요청자 호출 +1).
- DeepSeek-V4-Flash 런은 같은 코드·설정으로 다른 세션이 실행함.

조건 정의: `meta/configs_main/conditions.yaml`, `meta/configs_appendix/conditions.yaml` 참고.

| 조건 | 요약 |
|---|---|
| direct | 요청자가 에이전트 카드로 상대 그룹 에이전트에게 직접 질의 |
| routing | 상대 그룹 게이트웨이가 그룹 기록으로 담당자를 골라 원문 중계 |
| ingress | 게이트웨이가 여러 담당자에게 묻고 그룹 기록으로 답을 조립(버전 판정·충돌·제안·출처), 부족하면 재질의 (pull-by-proxy) |
| full_load | 권한 분할 없는 단일 에이전트, 조직 전체 DB 조회·이력 검색(참조점) |
| direct_relay | direct + 응답자가 자기 그룹 동료에게 요청당 최대 3번 되물음 |
| retrieve | 게이트웨이가 검색·담당자 질의까지 하고 조립 없이 답 원문 + 근거 기록 원문 전달 |
| sidecar | direct + 받은 에이전트마다 붙은 검색·조립 모듈(그 에이전트 혼자 답함) |

## 3. 주요 표 스키마

### tables/runs.csv (런 1행)
`n_scored`·`n_correct`·`accuracy`는 일수 상한 안·풀 수 있는 과제 기준(공통 과제로 거르기 전). `cost_usd_est`는 DeepInfra 단가(100만 토큰당 27B 0.26/2.60, 9B 0.10/0.15, DeepSeek 0.09/0.18 달러)로 계산한 추정치. `restarts`는 자동 재개 횟수(잔액 부족 등 외부 장애 포함).

### tables/tasks.csv (런 × 과제 1행)
| 열 | 뜻 |
|---|---|
| day, round, template, family | 과제 시점과 종류(15종) |
| state_class | 담당자 기억 상태 등급 A(카드 담당자의 최근 기억에 원문)~D(누구의 현재 기억에도 없음) |
| c_ops | 운영 기록 조각(DB 미반영 처리 기록 등)이 답을 가르는 과제 |
| n_groups, reasoning_tier, max_holders, path_len | 걸린 그룹 수, 추론 등급, 보유자 수, 경로 길이 |
| within_target_days | 분석 일수 상한 안이면 1 |
| reachable | 원리상 풀 수 있으면 1 (요청자 그룹 안 결정 필수 조각의 보유자가 모두 없는 과제는 0) |
| exact | 답 전체 정확 일치 (공식 채점기와 8,919건 모두 같은 판정) |
| slots_correct / slots_total | 슬롯별 일치 수 |
| answer_json, gold_json | 제출 답과 정답 |
| error | 답이 없을 때 사유(format_error, budget_exhausted) |
| calls_*, tokens_* | 과제 예산 기준 구성요소별(요청자·응답자·게이트웨이) 호출·토큰 |
| budget_exhausted, final_call_used, requester_asks, responder_step_caps | 예산·질의 관련 |
| llm_calls, cost_usd_est, wall_seconds | 그 과제의 LLM 호출 수, 추정 비용, 첫 호출~마지막 호출 벽시계 시간 |

### tables/llm_calls.csv.gz (LLM 호출 1행)
component(requester/responder/boundary), boundary_step(interpret/route/assemble), cached(재개 때 캐시 재생), attempts, latency_ms, prompt/completion tokens, finish_reason(length = 출력 상한 도달).

### tables/gateway_decisions.csv (경계 결정 1행)
stage(ingress/sidecar 등), action(select/referral/out_of_scope), selected·proposed 담당자, 조립 결과의 보탬·충돌·제안·버린 제안 수, 재질의 대상.

### tables/messages.csv.gz (메시지 1행)
via(agent/group), crossing(그룹 경계 통과), hop, chars.

### tables/retrievals.csv.gz (검색 1행)
source(gateway = 게이트웨이 그룹 기록 검색, search_memory = full_load 조직 전체 검색), cap_reached(증거 상한 12k 도달), 후보·선택·상한 탈락 수.

## 4. 결과 재현 방법

비교는 (셀·모델·시드)마다 **비교하는 조건이 모두 답한 공통 과제**만 쓴다. `within_target_days == 1`, `reachable == 1`로 거른 뒤 `task_id`로 조건을 맞춘다. 신뢰구간은 과제 단위 짝 부트스트랩(2,000회). 계산 코드는 `meta/scripts/summary.py`, `meta/scripts/export_agg.py`.

대표 결과(`meta/reports/results_final.md`):
- 기준 셀 27B: direct 0.33 → ingress 0.53 (+0.20, 95% CI [+0.16, +0.25]), full_load 0.52.
- 과제 유형별(27B 합산): A 등급 −0.01, B +0.47, C +0.29, D +0.31, C_ops +0.28.
- 그룹 수 5·6·10·15에서 격차 +0.18 / +0.27 / +0.22 / +0.20 (규모 효과 없음).
- 부록(1~10일): direct 0.34, direct_relay 0.34, routing 0.40, retrieve 0.47, full_load 0.54, sidecar 0.56, ingress 0.56.

## 5. 알려진 사항

- 채점 검토: `meta/reports/scoring_audit.md`. 공식 채점기와 전부 일치. 정답 원장 모호성 1개 유형(계약직 premium 장비의 계약 거부, 3과제), 예산 예약분 경합으로 인한 ingress 무답 5건(동결 코드 결함, master에서 수정), 9B의 null 표기 형식 오류 7건.
- ingress 조립은 담당자 답의 설명 글(`answer`)을 요청자에게 전달하지 않음(항목과 게이트웨이 보탬만). 규칙 적용형 과제에서 일부 손해로 분석됨.
- 패키지에서 뺀 것(용량): LLM 호출별 입력 구성 기록 `obs/context_windows.jsonl`(약 6GB), 응답 캐시 `llm_cache.sqlite`, 접근 기록·DB 조회 기록. 원본은 실행 폴더(`/root/project/g2g_main/runs*`)에 있음.
- 외부 장애: DeepInfra 잔액 소진(10-01 03시·05시·06~11시·12시)으로 런이 멈췄다가 체크포인트에서 재개됨. 재개는 응답 캐시로 진행 중 라운드를 재생하므로 결과에 영향 없음(접두 동일성 검증).

## 6. 비용 표 해석 주의

- `agg/by_condition.csv`·`appendix_7conditions.csv`의 `llm_calls_per_task`는 재개 때 캐시로 재생된 호출도 포함한다(비용 `cost_usd_*`에는 포함하지 않음). 재시작이 있었던 런에서 호출 수가 조금 많게 잡힐 수 있다.
- `cost_usd_per_success` = 과제당 비용 ÷ 정확도.

## 7. 추가분 (2026-10-03)

- `tables/gate_ledger/<run_id>.json`: 런마다 need 단위 원장(전달 판정·처음 끊긴 게이트, `meta/scripts/run_ledger.py`로 생성, 휴리스틱 채점기). 2026-10-06 재계산: 조립 조건(ingress·sidecar)의 선택 관문은 "게이트웨이는 본 것만 잃을 수 있다" 규칙 — 조립 LLM 입력(증거 E#·버전 V#·과거 문답 S#·초안·응답 R#)에 조각이 있었으면 assembly, 아니면 닿음·원문 → answer, 닿음·창에 없음 → window, 못 닿음 → search. gate_detail에 in_evidence, in_reply_items, in_reply_text, matcher_suspect(항목에 있었는데 미전달: 전달 매처 오판 의심), text_only(문장에만 있다가 빠짐). 비조립 조건은 불변. retrieve는 route/select/use 3갈래로만 보고. 검증 `meta/scripts/verify_rule.py`, 채점기 사본 `meta/scripts/gates.py`. 같은 날 Routing의 "선택 증거에 있었는데 보유자를 안 고름"을 L_sel.assembly → L_route로(조립이 없으므로 중개 손실).
- `tables/run_checks.csv`: 81런 실행 검사(`meta/scripts/run_checks_all.py`) — leak(조각 id·내부 DB 키), card_leak(카드 조건의 실제 에이전트 id), budget(과제당 호출·토큰 상한 초과 수), determinism(WAL 해시 재계산 = 기록값, 기록 없는 16런은 해시만), access(거부·교차 읽기), retrieval(게이트웨이 검색 후보·상한 탈락·top-k 밖·보유자 색인의 작성자 그룹이 다른 그룹인 수 = 0).
- `tables/access_audit.csv`: 런별 기록 읽기 건수(자기 그룹/교차 그룹 허용/거부, `meta/scripts/access_audit.py`). 분할 조건은 교차 읽기 0, Full-load만 조직 전체 읽기.
- `meta/scripts/paper_analysis{,2,3}.py`: 논문 그림·표 생성 (`/root/project/g2g/output/paper/`).
