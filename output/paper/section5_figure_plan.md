# §5 Experiments 구성안 — "결과가 선명한 것만" 기준

증거의 급을 나눈다: 주장은 정확 일치 수치(Acc·Δ·Π·ρ)로만 세우고, 관문 원장(휴리스틱)은 진단용 그림 하나(Fig. 3)로만 쓴다. 그 위에서 선정 기준은 두 가지를 **동시에** 만족하는 것: (1) 효과가 크고 CI가 0을 확실히 벗어나며 두 주력 백본에서 같은 방향, (2) 그림을 보면 가설(경계가 문제이고, 중개+선택이 그걸 푼다)이 바로 읽힘. 보기 좋지만 결과가 흐린 것은 본문에서 뺐고, 왜 뺐는지 §4에 수치로 적었다.

8페이지 AAMAS 기준 §5+§6 ≈ 3.3p. 본문 figure 5개(+선택 1) + 표 2개. 파일은 `output/paper/figures/`.

## 1. 본문 figure (전부 "선명" 등급)

### Fig. 2 — The ladder and the penalty (`f23_headline`, 2×2, 27B·DeepSeek) ★ 헤드라인
- **(a)** 클래스별 사다리 slope: A는 평탄(72→68→69, DS 73→76→73), B/C/D만 오름. B는 Routing 칸에서도(12→33), C/D는 Ingress 칸에서만(C 12→32, D 3→38). Full-load는 회색 영역의 참조 다이아몬드.
- **(b)** 부분 상태 패널티 덤벨: Π 67→52→28pp (ρ +23% / +58%), DS 66→53→35 (+20% / +47%).
- **선명한 이유**: A와 ¬A의 분리가 10pp가 아니라 60pp 단위이고, 두 백본이 같은 모양. 가설이 그림의 "형태"로 보임 — A 수평선, B/C/D 상승선.
- 9B는 넣지 않음(아래 §4). 본문 §6.7에서 수치로만 다루고 `f7`·`f20`(3패널판)은 부록.

### Fig. 3 — Where needs are lost (`f18_need_flow`, alluvial, 27B) ★ — **진단용(diagnostic)으로 표기**
- 고리(§3.4): request → reach → observe(window/search) → respond → select. 옛 버전 전달은 표시(stale), 오답은 과제 단위 use, 오류는 별도.
- Direct는 reach에서 67/100(DS 57), Routing은 reach 24 + observe 11 + respond 13(DS 21 + 25 + 4), Ingress는 reach 0(η_φ=1이라 정의상) + observe 21(window 11·search 10) + respond 6 + select 13. 현재 버전 전달 16 → 41 → 51 (DS 23 → 44 → 56).
- Full-load는 §3 틀 밖이라 원장 그림·표에서 제외(계산만 numbers3에).
- **증거의 급**: 관문 원장은 휴리스틱 채점기(귀속 규칙이 분석 중 여러 번 바뀜, 매처 재현율 0.71)라 **주장의 근거가 아니라 "잃는 모습"을 보여 주는 관측**. 캡션 첫 줄에 "Diagnostic view from a heuristic offline scorer"를 쓰고, 본문 주장은 정확 일치 수치(Acc·Δ·Π·ρ)로만 세운다. reach 감소는 η_φ=0인 Direct·Routing 사이에서만 중개 개선으로 읽는다.

### Fig. 4 — Rescue without loss (`f21_outcome_transition`, 27B·DeepSeek) ★
- (시나리오, 과제) 쌍 전이. A: 구조 8 vs 손실 11 (대칭 = 선택 소음). B 49 vs 6, C 32 vs 1, D 36 vs 0 (DS: B 41 vs 5, C 34 vs 3, D 24 vs 0).
- **선명한 이유**: "평균이 올랐다"가 아니라 "누가 올랐고 아무도 안 떨어졌다"가 막대 색으로 보임. McNemar p<0.001의 시각판.
- 보충 첫 장으로 `f22_task_raster`(427과제×4조건 래스터) — 같은 메시지를 한 장의 무늬로.

### Fig. 5 — What bounds the gain (`f25_bounds_clear`, Δ 포레스트 3패널) ★
- (a) 발견 가능성: H0 +45 [+23,+65], H1 +47 [+36,+57], H2 +23 [+15,+32], none(DB/rules) −4 [−10,+2] — DS도 +40/+34/+23/−1. 'none'은 그림 안의 두 번째 대조군.
- (b) 과제가 걸치는 그룹 수(27B, 4셀 풀): 2그룹 +27 [+21,+33], 3 +26, 4 +16, 5+ +8 [+2,+14] — 단조 감소.
- (c) 첫 접촉 +31 [+24,+38] / 재방문·불변 +2 [−4,+9] / 재방문·변경 +8 [0,+18]; DS +26 / +3 / +11.
- **선명한 이유**: 세 축 모두 CI가 겹치지 않는 단조 패턴이고 둘 다 가설과 일치 — 이득은 "기록이 로그에 있고, 요청자가 아직 안 가진" 상황에 집중된다. (c)의 '재방문·불변 ≈ 0'은 pull by proxy가 필요 없는 곳에서는 아무것도 안 바꾼다는 negative control.
- 기존 `f16`(H·R 막대)·`f15`(재방문 막대)·`f10`(사실 나이)은 부록으로.

### Fig. 6 — Variants: what the effect is made of (`f4_accuracy_vs_cost`, 27B, 10일, n=285) ★
- Direct 33.7 = Direct+relay 33.7 (동료에게 묻게 해도 0), Routing 40.4, Retrieve 47.0 (조립 제거 −9.1, p=0.004), Ingress 56.1 @ 575k tok, Sidecar 55.8 @ 285k tok, Full-load 53.7.
- **선명한 이유**: 한 산점도에서 "조립이 효과의 원천"(retrieve↓)과 "게이트웨이 홉은 필요 없음"(sidecar =, 토큰 절반)이 갈림. 점 7개 모두 CI 밖으로 분리되는 쌍만 본문에서 언급.

### Fig. 7 (선택) — Two tasks as they happened (`f19_trace_examples`) ○
- 실제 WAL의 클래스 D·C 과제 통신 그래프. 정량 figure가 아니라 기제 삽화. 공간이 0.3p 남으면 §4 끝에, 아니면 부록 첫 figure.

## 2. 본문 표

- **Table 1** = `t1_main` + Π·ρ (정확 일치 기반): 백본 3 × 조건 4, Acc, Δ_route/Δ_sel/Δ_total [CI], Π, ρ. 9B는 여기서만 등장(ρ ≤ 0). **δ·λ·υ는 원장(휴리스틱) 지표라 Table 1에 넣지 않고** Table 12(부록)에 "diagnostic" 표기로 둔다.
- **Table 2** = `t2_variants` + `t6_cost` 합본: 7조건, Acc, vs Ingress [CI], McNemar p, 호출·토큰·USD per task.
- G 셀은 표 없이 §6.6에 한 문장 + 부록 Table 5: "격차 +13/+27/+17/+17 (G=5/6/10/15), 크기 추세 없음".

## 3. 절 구성 (페이지)

| 절 | figure/표 | 분량 |
|---|---|---|
| 5.1–5.4 설정·조건·백본·지표 | — | 1.2p |
| 6.1 Main result + 사다리 두 칸 | Table 1, **Fig. 2** | 0.6p |
| 6.2 Where needs are lost | **Fig. 3** | 0.3p |
| 6.3 Rescue without loss | **Fig. 4** | 0.25p |
| 6.4 What bounds the gain | **Fig. 5** | 0.3p |
| 6.5 Variants, cost, scale | **Fig. 6**, Table 2 | 0.35p |
| 6.6 Backbone dependence, operational effects, limits | (수치만) | 0.3p |

## 4. 본문에서 뺀 것과 이유 (결과가 흐림)

| 파일 | 왜 빠지나 | 처리 |
|---|---|---|
| `f13a_responder_load` | 극적인 칸(27B 6–15건: Direct 8% vs Ingress 68%)이 **n=13 vs 22 과제**. DS는 같은 칸에서 Routing 75% > Ingress 50%(n=4, 10)로 방향이 뒤집힘 | 삭제. 부하 집중은 §6.6에 수치(top-1 share 61→40→35%)로만 |
| `f11_scaling_lines` (a) | G=5/6/10/15에서 Ingress 48/62/55/50 — 추세 없음, D3 셀만 튐 | 부록 Table 5 + 한 문장 |
| `f11` (b), `f5_by_day_window` | 기간별 차이가 조건 효과보다 작음 | 부록 |
| `f10_fact_age` | 비단조: 0일 +19, 1일 +34, 2–3일 +5 [−10,+18], 4–7일 +17, 8+ +19. "최근 사실에 집중" 주장이 성립 안 함 | 부록, 주장 삭제 |
| `f16_bounds` (b) 추론 단계 R | R0 +39 > R2 +24 > R1 +17 > R3 +10 — 순서가 안 맞고 DS R3는 n.s.(+1) | (a) H만 Fig. 5로 흡수, R은 부록 |
| `f15_revisit` | 패턴은 선명하나 막대형이라 CI가 안 보임 | Δ 포레스트로 바꿔 Fig. 5(c)에 흡수 |
| `f6_responder_reach` | 접촉률 차이 B 47→76→79 외에는 작고(A/D ±5) DS는 Routing ≈ Ingress | 부록 |
| `f9_failure_modes` | stale/partial 이동이 몇 pp 수준 | 부록 |
| `f14_template_heatmap` | Δ 범위는 넓지만(−5…+68) alloc·sourcing처럼 C/D 비중이 높은데 이득이 없는 행이 있어 설명이 길어짐 | 부록 (유형별 표와 함께) |
| `f8_rung_forest` | 12개 CI 중 2개(9B sel, G=5 route)가 0을 포함 — 정직하지만 흐림 | 부록; 본문은 Table 1의 CI로 |
| `f1`, `f2`, `f3`, `f7`, `f4b`, `f12`, `f13b`, `f17` | 막대형·수치판 | 부록/보관 |
| 9B 전반 | ρ −13/−2/−54%로 사다리를 못 오름. 참이지만 헤드라인 그림에 넣으면 메시지가 흐려짐 | Table 1 한 행 + §6.6 두 문장 + 부록 `f7`, `f20` |

## 5. 오늘 만든 것

- `f23_headline` (slope + 덤벨 합본, 본문 Fig. 2), `f25_bounds_clear` (H·폭·재방문 Δ 포레스트, Fig. 5) — `g2g_main/paper_fig_clear.py`
- `f20`, `f21`, `f22`, `f24` — `paper_fig_new.py` (f21이 Fig. 4; 나머지는 부록/보충)
- 라벨 겹침 수정: `f12`, `f13a`, `f13b`, `f19` — `paper_fig_fix.py`, `paper_fig_trace.py`
- 스크립트는 `analysis_package/meta/scripts/`에도 복사. 입력은 `numbers*.json`과 `5_task_level.csv`뿐이라 로그 없이 재현됨.

## 6. 남은 것

1. Fig. 1 개념도(분할 → 클래스 A–D → 세 조건), §4 파이프라인 그림.
2. `experiments_section.md`의 §6 소제목·figure 번호를 이 구성에 맞게 재배열(현재는 6.1–6.18 탐색 순서).
3. Table 1·2 합본 LaTeX 생성.
