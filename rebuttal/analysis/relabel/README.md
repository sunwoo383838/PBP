# 손실 고리 LLM 재판정

기존 채점기(`gbg/scoring/delivery.py`)의 전달 매처가 바꿔 말한 전달을 놓치는지 확인하려고, 102개 런(본 실험·부록·G 셀·리버탈)의
need 전달 여부를 LLM이 원문을 읽고 다시 판정했다. 결과 표는 `SUMMARY.md`.

## 무엇을 LLM이 정했나

LLM은 세 가지만 판정한다. 손실 고리(request → reach → observe → respond → select)를 정하는 규칙은 `gbg/scoring/gates.py`를
`regate.py`에 그대로 옮겨 썼고, 판정 결과만 끼워 넣었다.

- (A) 기록 조각이 요청자가 받은 메시지에 도착했는가: current / stale / partial / no
- (B) 그룹 안 구성원 응답에는 있었는가 (창구 조건에서 need가 미전달일 때만)
- (C) 계산이 필요한 need의 중간값이 도착했는가

손실 계산에서는 current만 전달, stale은 옛 값 전달, partial과 no는 미전달로 센다.

## 범위와 판정자

- **대상**: `full_load`를 뺀 102런에서, 기존 원장이 respond·select·observe(window)이거나 계산값 규칙으로 전달된 과제 전부,
  검색 손실 과제 전부, 나머지 중 무작위 300개(대조). 모두 2,759과제, 판정 14,045건이다.
- **사례**: 조건·모델 이름을 지운 사례 묶음으로 판정했다(`build_packets.py` → `out/cases.jsonl`, `make_batches.py` → `batches/`).
- **판정 규칙**: `INSTRUCTIONS.md`. 판정자에게 준 지시는 `JUDGE_PROMPT.md`.
- **판정자**: 판정 파일 938개 중 337개(`judged_by_fable52.txt`)는 Claude Fable 5.2, 나머지는 Claude Opus 5.5가 판정했다.

## 검증

- 판정마다 받은 인용 5,003건이 모두 지목한 메시지 원문에 그대로 있었다.
- 120과제를 다시 판정한 결과, 조각 전달 여부가 99.8%(401건), 계산값이 142/142 일치했다.
- 이전 사람 감사(층화 100건)와 겹치는 조각 130건 중 93.1%가 일치했다.
- 대조 표본 360 need 중 고리가 바뀐 것은 8개다.

## 기존 매처와 다른 정의

- 옛 버전이 여러 개인 기록은 바로 직전 버전과 달라진 값만 요구했다(매처는 어느 옛 버전과든 비교).
- 부분 전달은 미전달로 셌다.
- 메시지 안에 들어간 `[Group records]` 목록도 받은 것으로 셌다. 담당자를 알려 주기만 한 응답은 partial이다.
- 한 기록의 옛 버전이면서 다른 기록의 현재 내용인 경우, 판정자에 따라 stale과 no가 섞여 있다. 둘 다 미전달이라
  고리 분포에는 영향이 없고, 옛 값 전달 비율에만 영향이 있다.

## 파일

| 파일 | 내용 |
|---|---|
| `runs.py` | 런 목록. 리버탈 원장은 `../ledgers/`를 쓴다 |
| `build_packets.py`, `make_batches.py` | 사례 묶음과 판정 배치 생성 (실행 기록·시나리오 필요) |
| `judgments.tar.gz` | 판정 원본 `batches/bNNN/part_NNN.tsv` 938개와 다시 판정한 `redo/` |
| `collect.py` → `verdicts.json.gz`, `verdicts_dup.json.gz` | 판정 검사(형식·인용 대조)와 모음. 사례 묶음 필요 |
| `index.json.gz` | 배치·파일 → 사례, 런, 과제, 중복 판정 여부 |
| `regate.py`, `regate_all.sh` → `regate_out.tar.gz` | 런별 need의 기존 고리와 새 고리, 과제별 결과 |
| `summarize.py` → `SUMMARY.md` | 조각 혼동표, 고리 전이, 조건별 손실 분포(기존 대 LLM), 검증 수치 |
| `progress.sh` | 판정 진행 확인 |

## 다시 돌리기

환경변수 `G2G_CODE`(하네스 코드), `G2G_RUNS`(실행 폴더: `runs/`, `runs_appx/`, `runs_g/`, `scenarios/`,
`scenarios_g/`, `rebuttal/`), `GATE_LEDGER`(본 실험 관문 원장 폴더), `AUDIT_DIR`(사람 감사 폴더)를 정하고,
하네스 의존성이 있는 파이썬을 `PY`로 준다.

```
PY=python bash regate_all.sh     # 사례 묶음이 없으면 verdicts.json.gz를 쓴다
python summarize.py              # SUMMARY.md
```

이 폴더 사본만으로 돌려 `regate_out` 102개와 `SUMMARY.md`가 판정 때 결과와 같음을 확인했다.
