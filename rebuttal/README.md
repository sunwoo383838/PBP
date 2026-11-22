# 리버탈 추가 실험

기준 셀(D5·R2, 그룹 10개), 1~10일. 기존 조건은 다시 돌리지 않았고 기존 요청자·응답자 프롬프트는 그대로다.
새 조건의 정의와 문구는 `configs/conditions.yaml`, `PROMPT_MANIFEST.md`, 바꾼 이유와 불변 확인은 `HARNESS_CHANGES.md`에 있다.

## 실행한 것

| 묶음 | 조건 | 모델 | 시드 | 코드 커밋 |
|---|---|---|---|---|
| A1 | ingress_plain_sym | qwen3.5-27b | 12~14 | 7b934ac |
| A2 | ingress_no_requery | qwen3.5-27b | 12~14 | 7685d59 |
| B | rag_only (v2) | qwen3.5-27b | 12~14 | 125179d |
| C | sidecar | deepseek-v4-flash | 12~14 | b0a3cb0 |
| C | sidecar | qwen3.5-9b | 12~14 | 7685d59 |
| D | direct, sidecar × K16k·lag1·warm10 | qwen3.5-27b | 12 | 7685d59 |

비교 기준으로 쓴 기존 런: direct·routing·ingress·full_load(세 모델)는 4b813f5, direct_relay·retrieve·sidecar(27B)는 d5851f4.

- 기존 조건은 위 커밋들 사이에서 대본 실행의 실행 기록 해시와 모델 호출 키 목록이 같다(`HARNESS_CHANGES.md`).
- 4b813f5와 그 뒤 커밋의 동작 차이는 예산 예약분 경합 수정(95ed065) 하나다. 호출 상한(300회)에 닿은 과제에만 영향이 있다.
  1~10일에서 27B는 0개(전 조건 최대 243회), DeepSeek ingress 2개가 옛 코드에서 답 없이 끝났다(`RESULTS.md` 5절).
- DeepSeek sidecar는 제공자가 점이 든 도구 이름을 거부해, 보내는 본문에서만 `db.query` → `db_query`, `entity.search` →
  `entity_search`로 바꾸고 응답은 되돌렸다. 10월의 DeepSeek 네 조건은 점이 든 이름으로 돌았다.
- rag_only v1(7b934ac)은 규정을 근거로 든 답이 인용 형식 검사에서 거절되어 조립 실패가 33.6%였다. 결과를 본 뒤 규정 id 인용을
  허용한 v2로 다시 돌렸다(`HARNESS_CHANGES.md`). v1 결과는 분석에 쓰지 않는다.

## 민감도 셀 (`sensitivity/`)

- K16k: 생성기 `--K 16000 --S 4000`, 하네스 `context.raw_window 16000`·`summary 4000` (`configs_K16k.patch`).
- lag1: 생성기 `--db_lag 1 1` (기준 1~3일). `generator.patch`가 이 인자를 추가한다. 0은 생성기 구조상 만들 수 없다.
- warm10: 생성기 `--warmup 10` (기준 20).
- 세 셀 모두 시드 12, 검사 26종 통과·공개 입력 감사 오류 0 (`validation/`). 고친 생성기를 기본값으로 돌린 출력은 기준 시나리오와
  manifest 외 모든 파일이 바이트 단위로 같다.
- `natural_class.json`: 셀별 자연 후보 등급 분포(가중 이득의 가중치).

## 분석 (`analysis/`)

| 파일 | 내용 |
|---|---|
| `ledgers/*.json.gz` | 런별 과제·need 원장 (새 런 18개 + 비교 기준 45개). master의 `gbg/scoring/ledger.py`로 만들었다 |
| `contrasts.py` → `contrasts.json` | 모델별 공통 과제의 정확도·고리 분포·대비, 민감도 이득(관측·자연 등급 가중) |
| `extract_requests.py` → `requests.json.gz` | 과제별 필요한 그룹과 실제로 요청한 그룹 |
| `request_delivery.py` → `request_delivery.json` | direct·sidecar의 전달률, need 전부 전달된 과제, 요청 범위, 부분집합 이득 |
| `decomposition.py` | ingress_no_requery − ingress_plain_sym 원인 분해 (실행 기록 필요) |
| `common_tasks_27b.json` | 27B 아홉 조건의 공통 과제 285개 |

결과 표는 `RESULTS.md`.

## 한계

- 민감도는 시드 1개(탐색적). 세계와 과제가 기준과 달라 "같은 과제에서 변수만 바꾼 효과"가 아니다.
- DeepSeek의 sidecar 대 다른 조건 비교에는 도구 이름 표기 차이와 실행 시점 차이(제공자 쪽 서빙)가 섞여 있다.
- rag_only v2는 결과를 본 뒤 고친 조건이다.
- 기존 조립 조건도 규정을 근거로 든 보충 항목은 인용 형식 검사에서 거절한다(27B ingress 조립 최종 실패 2.7%).
