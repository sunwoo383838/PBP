# EntCollabBench(ECB) 통합 계획 — 경계 게이트웨이 실험

> 이 문서는 Claude Code가 단계별로 수행할 구현 계획이다. 각 Phase가 끝나면 **완료 기준 확인 결과를 보고하고 멈춘다.** 문서와 기존 코드가 충돌하거나 문서에 없는 결정이 필요하면 임의로 판단하지 말고 보고한다.

---

## 0. 목적과 원칙

**목적.** 우리 경계 게이트웨이(worldgen 실험에서 쓰는 것과 동일한 모듈)가 외부 벤치마크 ECB의 원본 과제에서도 a2a Direct보다 성능이 좋아지는지 측정한다.

**원칙 (모든 Phase에 적용).**

1. **원본 유지.** ECB의 과제 데이터, 과제 프롬프트, 에이전트 시스템 프롬프트, 도구 이름, `scripts/benchmark.py`, `scripts/judge/` 는 수정하지 않는다. 바뀌는 것은 **통신 기반구조(부서 간 위임 경로)** 뿐이다. 불가피한 실행 설정 변경은 §7 목록에 있는 것만 허용한다.
2. **게이트웨이 코어는 한 벌.** worldgen과 ECB는 같은 게이트웨이 코어를 import 한다. ECB 전용 게이트웨이 로직을 만들지 않는다. ECB 때문에 코어 규칙을 바꿔야 하면 일반 규칙으로 바꾸고 worldgen에도 동일 적용한다.
3. **Direct 행 = ECB 원본 그 자체.** Direct 조건은 원본 peers 설정 그대로 돌린다.
4. **권한 가정 유지.** 그룹 g의 게이트웨이는 g 구성원의 transcript와 g가 참여한 경계 트래픽만 읽는다. 다른 그룹 데이터는 반드시 그 그룹 게이트웨이에 대한 질의로만 얻는다.

---

## 1. ECB 사실 정리 (구현에 필요한 것)

- 저장소: `https://github.com/yutao1024/EntCollabBench` — 커밋 `9d085fc` 에 고정해서 fork.
- 데이터셋: Hugging Face `Kirito-Lab/EntCollabBench` — `mcp_tasks_160.json`, `mcp_multi_tasks_40.json`, `approval_tasks_80.json`, `approval_multi_task_20.json`, `local_data.zip`, `seed.zip`. README 기준 `scripts/dataset/` 아래에 둔다.
- 에이전트 11개, 각각 별도 컨테이너(`agent/docker-compose.yml`), LangChain `create_agent` + `ChatOpenAI`(temperature 0) + `SummarizationMiddleware`. 에이전트 간 위임은 도구 `ask_<agent>_by_http` 로 하는 **동기 중첩 HTTP 호출**. `agent_specs.json` 에 `delegate_to` 가 없으므로 모든 에이전트가 나머지 10명 전원에게 위임 가능.
- 위임 도구는 `peers[target]` URL(환경변수 `AGENT_PEERS_FILE` → `/app/config/agent_peers.json`)에 `POST {base}/v1/agent/tasks` 를 보낸다.
- 요청 payload (`api_schema.py`):
  ```json
  {"request_id": "...", "source_agent": "...", "target_agent": "...", "task": "...",
   "recursion": {"depth": 1, "max_depth": 3, "trace": ["a->b"]},
   "metadata": {"via": "http_client_tool", "session_id": "...", "parent_agent": "...",
                "deadline_at": "...", "benchmark_server_allowlist": [...]}}
  ```
  응답: `{request_id, api_version, status, handled_by, result, recursion, error}`. 에이전트 최종 응답 형식은 `DONE:..., UNDONE:..., ERROR:...` (approval 에이전트는 `DECISION/RATIONALE/ERROR`).
- **`request_id` 는 한 서브태스크의 위임 체인 전체에서 동일하다.** 벤치마크는 `(session_id, request_id)` 로 모든 에이전트 trace를 모아 채점한다.
- trace 조회: `POST {agent}/v1/agent/sessions/trace` `{"session_id": ..., "request_id": ...}` → `{"events": [...]}`. 이벤트 종류: `request_parsed, invoke_start(task 텍스트 포함), llm_invoke_start, llm_invoke_done, llm_response_meta, agent_message, tool_call, tool_result, delegate_start, delegate_done, delegate_error, delegate_non_ok, delegate_blocked_cycle, request_cancelled`.
- 에이전트 세션 메모리: checkpointer thread = `session_id`. 한 과제(batch) 안의 서브태스크끼리는 메모리가 이어지고, 과제가 끝나면 `benchmark.py` 가 `/v1/agent/sessions/clear` 로 지운다.
- `benchmark.py` 흐름: MCP DB seed → 서브태스크마다 시작 에이전트에 요청 → **서브태스크 직후 inline judge**(실패 시 남은 서브태스크 skip) → cleanup → 메모리 clear. judge 환경변수(`JUDGE_MODELS`)가 없으면 종료한다.
- judge는 GT 에이전트마다 "참조 궤적 vs 실제 trace" 를 LLM으로 판정한다. 참조 궤적에 `ask_<agent>_by_http` 호출이 단계로 들어 있으므로 **도구 이름을 바꾸면 안 된다.**
- 채점 무관 인프라: Arena MCP 서버 7개(csm, teams, calendar, email, itsm, drive, hr; `Arena/docker-compose-mcp.yml`)는 SQL seed 기반 결정적 환경. gitea는 실행마다 별도 컨테이너(`tool/gitea_isolation.py`).

### 부서(그룹) 매핑 — 논문 공식 6부서, 변경 금지

| 그룹 | 구성원 |
|---|---|
| IT | it_service_desk_l1, it_change_engineer |
| HR | hr_service_specialist |
| CS | customer_support_specialist |
| SS (Shared Services) | knowledge_base_specialist, collaboration_ops_specialist |
| ENG | developer_engineer, qa_test_engineer |
| AC (Approval Center) | finance_approval_specialist, legal_approval_specialist, procurement_approval_specialist |

---

## 2. 아키텍처

```
[g2g-core]  게이트웨이 코어 + 그룹 메모리(WAL·하이브리드 인덱스) + LLM 실행층·로깅
     ▲                                  ▲
     │ BoundaryPolicy 훅                 │ import
[worldgen 하네스]                   [ecb-adapter]  HTTP 경계 서비스 + trace 동기화
                                            │ peers URL
                                    [ECB fork @9d085fc]
                                     에이전트 11개 · Arena MCP · benchmark.py · judge
```

**의존 규칙.**
- `g2g-core` 는 worldgen 커널, ECB, HTTP 어느 것도 import 하지 않는다. 전송 방식을 모르는 순수 함수 + 메모리 인터페이스.
- `ecb-adapter` 는 `g2g-core` 와 ECB 계약(`api_schema.py` 형식)에만 의존한다.
- ECB fork 수정은 §7 목록뿐.

---

## 3. 실험 조건

| 조건 | 부서 간 위임 경로 | 게이트웨이 동작 |
|---|---|---|
| **Direct** | 원본 그대로 (peers = 에이전트 URL) | 없음 |
| **Passthrough** (검증용, 논문 미보고) | 경계 서비스 경유 | 아무것도 안 하고 그대로 전달. LLM 호출 0 |
| **Routing** | 경계 서비스 경유 | 받는 그룹 게이트웨이가 그룹 메모리로 수신 구성원 결정 (지목된 에이전트는 힌트). payload는 원문 그대로 |
| **Ingress** | 경계 서비스 경유 | Routing + ① 수신 요청의 누락 탐지 → 보낸 그룹 게이트웨이에 pull 질의(pull-by-proxy) → 찾은 원문 조각 덧붙임 ② 응답 커버리지/형식 검사 → 지목 구성원에게 1회 재질의 |
| **I+E** | 경계 서비스 경유 | Ingress + ③ 보내는 그룹 Egress가 나가는 위임문을 **그룹 전체가 받은 지시**와 대조해 누락 원문 조각을 사전에 덧붙임 |
| *(선택)* **Self-check** | 경계 서비스 경유 | I+E와 동일 코드, 단 Egress 입력으로 검색 결과 대신 보내는 구성원의 전체 transcript를 사용 (격리 컨텍스트 효과 대조군) |

- **같은 부서 내 위임은 모든 조건에서 그대로 통과**(게이트웨이 미관여, LLM 호출 없음).
- 벤치마크 → 시작 에이전트 요청은 경계가 아니므로 경계 서비스를 거치지 않는다(원본대로 host 포트로 직접).
- pull 질의에 답하는 기능(`answer_pull`)은 **정보를 가진 그룹의 Ingress 기능**이다. 따라서 Ingress 조건에서도 모든 그룹이 pull에 답한다. Egress(③)는 I+E에서만 켠다.

---

## 4. 게이트웨이 코어

### 4.1 인터페이스 (전송 방식 무관)

```python
route(request, group_memory, member_cards) -> RouteDecision          # Routing
ingress_check(request, member_card, group_memory) -> list[Gap]        # Ingress ①
answer_pull(query, group_memory) -> list[VerbatimFragment] | NotFound # Ingress (보유 그룹 측)
assess_response(request, response, group_memory) -> Coverage          # Ingress ②
egress_complete(outbound, group_memory, target_card) -> list[VerbatimFragment]  # Egress ③
```

그룹 간 pull은 코어의 메시지 인터페이스(`GatewayBus.query(from_group, to_group, query)`)로만 한다. 같은 프로세스에 있어도 직접 다른 그룹 메모리를 읽지 않는다. 모든 질의·응답은 경계 트래픽으로 WAL에 기록한다.

### 4.2 불변 규칙

1. **원문 전달, 덧붙이기만.** 위임문과 응답을 요약·재작성하지 않는다. 보완은 원문 뒤에 고정 헤더 `\n\n[Boundary note — verbatim excerpts from the originating request]\n...` 아래 **원문 조각 그대로** 덧붙인다.
2. **대상 관련 조각만.** Egress/pull로 덧붙이는 조각은 수신 대상과 그 하류 역할에 해당하는 것만. 원 지시 전체를 붙이지 않는다(논문: 과잉 컨텍스트가 하류를 오도함).
3. **재질의는 지목된 구성원에게만, 최대 1회.** 누락 항목을 다른 구성원에게 직접 보내지 않는다(GT 궤적의 위임 호출이 사라져 judge 실패).
4. **판단 대행 금지.** 게이트웨이는 결정·계산·도구 실행을 하지 않는다. 라우팅, 원문 조각 조회, 전달, 재질의만.
5. **recursion 메타를 건드리지 않는다.** 게이트웨이 hop은 depth에 포함하지 않는다. 원본 `recursion` 을 그대로 전달.
6. **`request_id`, `session_id` 보존.** 재질의·전달 모두 원 `request_id` 를 유지해야 judge가 trace를 수집한다.
7. **fail-open.** 게이트웨이 내부 오류 시 원 요청을 그대로 전달하고 `gateway_error` 를 기록한다(조건별 건수 보고).

### 4.3 각 기능의 입력과 판정 기준

- **ingress_check**: 입력 = 수신 요청 원문 + 수신 구성원 카드(역할 설명 + 도구 목록). 출력 = "이 구성원이 행동하려면 필요한데 요청에 없는 식별자·값" 목록. 받는 쪽이 **알아챌 수 있는** 누락만 대상(예: 레코드 ID, 기사 번호, 본문, 파일 경로).
- **answer_pull**: 입력 = Gap 질의. 보유 그룹 메모리에서 하이브리드 검색 → 원문 조각 반환. 없으면 NotFound(추측 금지).
- **assess_response**: ① 형식 위반(DONE/UNDONE/ERROR 또는 DECISION 부재) ② 요청 항목 중 응답·그룹 transcript 어디에도 수행 흔적이 없는 항목 ③ 그룹 transcript에 실패한 도구 호출이 있는데 응답이 DONE인 경우 → 재질의 사유. 인자 정확성까지 검증하지 않는다.
- **egress_complete**: 입력 = 나가는 위임문 + 보내는 그룹이 받은 지시 전체(시작 에이전트의 원 프롬프트, 그룹으로 들어온 작업 지시)에서 검색한 조각 + 대상 카드. 출력 = 위임문에 없는데 대상/하류에 해당하는 원문 조각(조건, 정확한 문구 포함 — 받는 쪽이 **알아챌 수 없는** 누락).
- **연쇄 pull**: 기본은 직전 보낸 그룹에만 질의. NotFound면 `recursion.trace` 를 따라 한 단계 더 앞 그룹에 질의(최대 depth까지). *(열린 결정 — §11)*

---

## 5. 그룹 메모리 (worldgen과 동일 메커니즘)

- 저장: append-only WAL(단일 진실 원천) + 그룹별 projection. 검색: BM25 + 로컬 임베딩 + 활동 인덱스(누가 최근 무엇을 했나). **가중치, top-k, 임베딩 모델, 컨텍스트 예산은 worldgen 설정과 동일.**
- 인덱싱 대상: 그룹 구성원 transcript 이벤트(`invoke_start` task, `agent_message`, `tool_call`, `tool_result`, `delegate_*`) + 그룹이 참여한 경계 트래픽.
- **일반 규칙(코어에 넣고 worldgen에도 적용):**
  - 임계 길이를 넘는 메시지는 문장 단위로 쪼개 인덱싱(원 메시지 ID와 오프셋 유지 → 원문 조각 복원 가능).
  - 최신성 정렬은 wall-clock이 아니라 WAL 순번.
- **ECB 어댑터 몫:**
  - trace 동기화: 게이트웨이 함수 호출 **직전에** 해당 그룹 구성원 전원의 `/v1/agent/sessions/trace` 를 `session_id` 로 조회해 새 이벤트만 WAL에 적재(신선도 보장).
  - 메모리 범위 = `session_id` (과제 단위). 세션 간 공유 금지.
  - 구성원 카드 = `agent_specs.json` 역할 부분 + `tool/toolsets.py` 의 도구 그룹.

---

## 6. ecb-adapter 명세

- **경계 서비스(HTTP).** `POST /agents/<target>/v1/agent/tasks` 수신. 요청 payload의 `source_agent`, `target_agent` 로 부서 판별.
  - 같은 부서 → 원 에이전트 URL로 그대로 전달.
  - 다른 부서 → 조건별 파이프라인: [I+E: egress_complete(보내는 그룹)] → [route(받는 그룹)] → [Ingress: ingress_check → GatewayBus pull → 조각 덧붙임] → 구성원에게 전달 → [Ingress: assess_response → 필요 시 1회 재질의] → 응답 원문 반환.
  - 응답 스키마는 원본과 동일(`handled_by` = 실제 처리 구성원).
- 동시성: `benchmark.py --batch-concurrency` 로 세션이 병렬 실행되므로 상태는 `session_id` 로 분리, thread-safe.
- 타임아웃: 경계 서비스의 구성원 호출은 `metadata.deadline_at` 잔여 시간 내로 제한.
- 배포: 원 compose 파일을 수정하지 않고 override 파일(`docker-compose.boundary.yml`)로 경계 서비스를 같은 네트워크에 추가. 에이전트 `NO_PROXY` 에 경계 서비스 호스트 추가.
- 조건 전환: `config/agent_peers.<condition>.json` 을 생성하고 `AGENT_PEERS_FILE` 로 선택(Direct는 원본 파일). 경계 서비스는 조건값을 환경변수로 받는다.
- 산출물: 게이트웨이 이벤트/토큰 로그(jsonl, `session_id`·`task_id`·`sub_task_id` 키) — 사후 처리로 ECB 결과 jsonl과 병합.

---

## 7. ECB fork 수정 허용 목록 (이외 수정 금지, 논문 부록에 명시)

1. `config/agent_peers.<condition>.json` 추가(원본 파일 유지).
2. `agent/.env` — 40,960 토큰 컨텍스트 대응(전 조건 동일):
   `AGENT_WORKSPACE_READ_MAX_CHARS=20000`, `AGENT_SUMMARY_TRIGGER_TOKENS=24000`, `AGENT_SUMMARY_TRIGGER_MESSAGES=99`, `AGENT_SUMMARY_KEEP_MESSAGES=6`, `MCP_SCHEMA_CONTEXT_MODE=compact`. (Phase 2 smoke test로 컨텍스트 초과 오류가 없는지 확인 후 확정)
3. Qwen3 thinking off 패치: `agent.py` 의 `_build_llm_extra_body` 에 Qwen 분기 추가 + 요약 미들웨어에도 같은 인자 전달. 방식은 Phase 2에서 확정.
4. `docker-compose.boundary.yml` override 추가.

---

## 8. 실행 설정

```bash
export OPENAI_BASE_URL=https://api.deepinfra.com/v1/openai
export OPENAI_API_KEY=<DeepInfra 키>
export AGENT_LLM_MODEL=Qwen/Qwen3-32B          # 14B 실험 시 Qwen/Qwen3-14B
export AGENT_SUMMARY_MODEL=Qwen/Qwen3-32B
export JUDGE_MODELS=Qwen/Qwen3-235B-A22B-Instruct-2507   # 1개 고정, 전 조건 동일
export TASK_TIMEOUT_SECONDS=2000                # 전 조건 동일. Direct 타임아웃이 거의 0이 되는 값으로 조정
export AGENT_HTTP_TIMEOUT_SECONDS=800
```
- 게이트웨이 LLM도 같은 모델(Qwen3-32B), temperature 0, thinking off, 우리 실행층 경유(토큰·프롬프트 WAL 기록).
- `--session-id` 접두어는 `ecb-<condition>-<model>-<runid>` 로 매 실행 고유하게.

---

## 9. 로깅·분석 산출물

- 조건별: ECB 원 지표 R_agent / R_subtask / R_task (ECB judge 그대로) — 헤드라인.
- approval 보조 지표: 결정 라벨(approve/require_preapproval/require_docs 등) 코드 대조 정확도.
- 게이트웨이 개입: 탐지된 gap 수, pull 질의·성공 수, egress 덧붙임 수, 재질의 수(사유별), route 변경 비율, gateway_error 수.
- 토큰: 에이전트 / 게이트웨이 분리.
- 타임아웃률(조건별).
- **hop 유형 라벨(데이터셋 GT로 사전 계산):** 서브태스크마다 `has_cross`(부서 간 위임 포함) / `intra_after_entry`(부서 내 위임만, 단 그 그룹이 경계로 진입됨) / `zero_boundary`(경계 통과 없음) — 조건별 효과를 유형별로 분리 보고. `zero_boundary` 는 음성 대조군.
- 누락 GT 인자 유형 분류(사후): 필수 식별자 vs 조건·정확한 문구 → Ingress vs Egress 기여 분리.

---

## 10. 단계별 작업과 완료 기준

각 Phase 끝에 보고하고 멈춘다.

**Phase 0 — 조사(코드 변경 없음)**
- 기존 저장소에서 게이트웨이/BoundaryPolicy/그룹 메모리(WAL·하이브리드 검색) 관련 모듈 위치와 현재 구현 상태, 커널과의 결합 정도를 보고. §4.1 인터페이스로 분리하는 데 필요한 변경 범위 제안.
- ECB를 `9d085fc` 로 fork·clone, HF 데이터셋 4개 다운로드.
- 데이터셋 전수 스캔 스크립트 작성(분석용, 저장소에 커밋): 과제 수(300), hop 수와 부서 간/내 분류, hop 유형 라벨 생성.
- **완료 기준:** 스캔 결과가 다음 값과 일치하거나 차이를 보고 — workflow single hop 480개 중 부서 간 346 / 부서 내 134, multi hop 149개 중 122 / 27, KB로 들어오는 single 위임 78개 중 61개가 collab→KB, multi 서브태스크 120개 중 `zero_boundary` 15개, approval 100개 전부 부서 간 1개 그룹(AC).

**Phase 1 — 코어 분리**
- 게이트웨이 코어를 §4.1 인터페이스의 순수 모듈로 분리(또는 신규 작성). worldgen 커널은 BoundaryPolicy 훅에서 이를 호출하도록 연결.
- §5 일반 규칙(문장 단위 분할, WAL 순번 최신성) 반영.
- **완료 기준:** 코어 단위 테스트(가짜 메모리) 통과, 기존 worldgen 테스트/결정성 테스트 통과, 코어에 worldgen·ECB·HTTP import 없음.

**Phase 2 — ECB Direct 재현**
- DeepInfra 설정으로 Arena + 에이전트 기동. Qwen3 thinking off 방식 smoke test: ① `reasoning_effort: "none"` ② `chat_template_kwargs: {"enable_thinking": false}` ③ 시스템 프롬프트 끝 `/no_think` 순으로 시도, 응답에 사고 텍스트가 없는 첫 방식을 채택. 도구 호출 형식 오류율도 기록.
- §7-2 컨텍스트 설정 적용 후 approval 10개 + workflow(비-ENG) 5개 Direct 실행.
- **완료 기준:** end-to-end 완료, judge 결과 생성, 컨텍스트 초과 오류 0, thinking 텍스트 누출 0. 결과 수치 보고.

**Phase 3 — 경계 서비스 Passthrough**
- ecb-adapter 경계 서비스 구현(Passthrough 모드), override compose, peers 파일 생성.
- **완료 기준:** Phase 2와 같은 과제에서 게이트웨이 LLM 호출 0, recursion depth/trace 원본과 동일, 부서 간 위임이 전부 경계 서비스를 경유(로그 확인), 결과가 Direct와 노이즈 범위 내.

**Phase 4 — 그룹 메모리 동기화 + Routing**
- trace 동기화, 세션 범위 메모리, 구성원 카드, `route()` 연결.
- **완료 기준:** 각 게이트웨이 호출 시점에 해당 그룹 구성원의 최신 이벤트가 인덱스에 있음(로그로 검증), 다른 그룹 데이터 접근 0, Routing 조건 소규모 실행 완료, route 변경 비율 보고.

**Phase 5 — Ingress**
- `ingress_check`, GatewayBus 기반 `answer_pull`, `assess_response` + 1회 재질의.
- **완료 기준:** 불변 규칙 §4.2 전 항목 테스트(원문 보존, 덧붙임 헤더, 재질의 대상·횟수, request_id 보존, fail-open), 소규모 실행에서 개입 로그 생성.

**Phase 6 — I+E (+ 선택: Self-check)**
- `egress_complete` 연결. Self-check는 입력 소스만 바꾸는 플래그로.
- **완료 기준:** Phase 5와 동일한 불변 규칙 테스트, 소규모 실행 완료.

**Phase 7 — 본 실행**
- 순서: Approval 100개 × {Direct, I+E, Ingress, Routing} × 32B → Workflow 비-ENG 143개 × 같은 조건 × 32B → Approval × 14B → (여유 시) ENG 57개, Self-check(approval).
- **완료 기준:** 조건별 §9 지표 표, 과제 단위 짝 비교(같은 과제의 Direct vs 각 조건) 결과.

---

## 11. 열린 결정 (진행 중 해당 지점에서 보고하고 확인받을 것)

1. **"full" 조건 정의** — 추가 여부와 정의 미정.
2. **연쇄 pull** — 기본값(직전 그룹 → NotFound 시 recursion.trace 따라 한 단계씩)을 유지할지.
3. **judge 모델 최종 확정** — 기본값 Qwen3-235B-A22B-Instruct-2507, 1개.
4. **ENG(gitea) 과제 포함 여부** — 인프라 부담 확인 후.

## 12. 하지 말 것

- ECB 과제·프롬프트·도구 이름·judge·benchmark.py 수정.
- ECB 전용 게이트웨이 로직, 벤치마크별 검색 가중치 튜닝.
- 게이트웨이가 위임문·응답을 요약/재작성하거나, 결정·도구 실행을 대신하는 것.
- 다른 그룹 메모리 직접 읽기, 세션 간 메모리 공유.
- 게이트웨이 hop을 recursion depth에 포함.
