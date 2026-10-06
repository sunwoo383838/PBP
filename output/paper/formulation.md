# §3 Problem Formulation — 수식화 설계

결정: 별도의 Preliminaries 절은 두지 않는다. 필요한 것은 배경 이론이 아니라 표기법이므로 §3.1이 그 역할을 한다. §3은 1쪽 안팎, 식은 10개 이내. 기호는 구현과 1:1로 대응한다(§7 표).

- §3.1 Setting — 에이전트·그룹·기록·작업 기억·접근 정책·카드
- §3.2 Tasks and record location — 요구, 결정 필수 기록, 보유 구조, 클래스 A–D
- §3.3 Boundary mechanisms — 두 결정 σ·φ와 관측 집합, 조건 좌표표, 공개 정책
- §3.4 Loss model and metrics — 다섯 관문, 손실 프로파일, Acc·Δ·Π·ρ·cov·υ
- Remark — 모델이 주는 두 예측 (§6의 그림이 검증이 되도록)

§4는 이 틀 위에서 pull by proxy를 (O_σ, O_φ, locus)의 한 점 + 다섯 단계 알고리즘으로 적고, 변형 세 개를 한 성분씩 되돌린 ablation으로 소개한다.

---

## 1. §3.1 Setting

| 기호 | 정의 |
|---|---|
| $\mathcal A$, $\mathcal G$ | 에이전트 집합, 그룹 집합. $\mathcal A=\bigsqcup_{G\in\mathcal G}G$, $g(a)$ = $a$의 그룹 |
| $\mathcal R_G(t)$ | 그룹 $G$의 지속 기록 저장소(DB 행·규정·작업 로그·메시지). 기록 $r=(\mathrm{id},\mathrm{content},t_r,\mathrm{author},v)$, 현재 버전 $r^{(t)}$ |
| $H_a(t)$, $W_a(t)$ | 에이전트 $a$의 전체 이력과 작업 기억(문맥). 용량 $\kappa$ |
| $\pi(a,r)$ | 접근 정책: $a$가 $r$을 직접 조회할 수 있는가 |
| $\mathrm{card}(G)$ | 공개 카드. 역할·담당 기술, 정적. 외부 요청자가 보는 유일한 내부 정보 |

$$W_a(t)=\mathrm{evict}_\kappa\big(H_a(t)\big)\subseteq H_a(t) \tag{1}$$
$$\pi(a,r)=\mathbb 1\big[g(a)=g(r)\big] \tag{2}$$

(2)가 권한 분할이다. 다른 그룹의 정보는 요청 $x=(a_q,G,q)$를 통해서만 얻는다.

## 2. §3.2 Tasks, needs, and where the decision-critical records are

| 기호 | 정의 |
|---|---|
| $\tau=(a_q,q,t,y^*)$ | 과제: 요청자, 질문, 시각, 정답 |
| $N_\tau=\{n_1,\dots,n_k\}$ | 과제의 정보 요구 |
| $R_n(t)$ | 요구 $n$의 결정 필수 기록 집합(현재 버전), 소유 그룹 $G_n$ |
| $\mathrm{hold}(r,t)=\{a: r\in W_a(t)\}$ | 보유 구조: 지금 누구의 작업 기억에 $r$이 있는가. 요청자는 관측 불가 |
| $h(n)$ | 지정 담당자: $\mathrm{card}(G_n)$이 가리키는 구성원 (요청자가 고를 사람) |
| $S$ 피복 $n$ | $R_n(t)\subseteq\bigcup_{a\in S}W_a(t)$ |

$$\mathrm{class}(n)=\begin{cases}
\mathrm A & \{h(n)\}\ \text{가 } n\text{을 피복}\\[2pt]
\mathrm B & \exists\,a'\in G_n\setminus\{h(n)\}:\ \{a'\}\ \text{가 피복}\\[2pt]
\mathrm C & \text{최소 피복 크기}\ \ge 2\\[2pt]
\mathrm D & \text{어떤 } S\subseteq G_n \text{도 피복하지 못함 } (R_n\subseteq\mathcal R_{G_n}\text{에만 존재})
\end{cases} \tag{3}$$

- $C_{ops}$는 클래스가 아니라 겹침 플래그: $R_n$에 운영 판단(예외 승인·대행 결정 등) 기록이 포함됨.
- 클래스 A가 대조군인 이유가 (3)에서 바로 나온다: $h(n)\in\mathrm{hold}(r,t)$이면 정적 카드와 동적 기록이 같은 사람을 가리킨다. B·C·D는 카드와 보유가 어긋나는 세 가지 방식이다.
- 서론의 "첫째·둘째·셋째" 조건 = B, C, D. "더 어려워지는 조건" = $C_{ops}$.

## 3. §3.3 Boundary mechanisms as two decisions under partial observability

요청 $x=(a_q,G,q)$에 대해 경계 메커니즘 $M_G: x\mapsto y$. 두 결정과 각각의 관측 집합:

$$S=\sigma(q;\ O_\sigma)\subseteq G \qquad\text{(request mediation)} \tag{4a}$$
$$y=\phi\big(q,\ \{\mathrm{Resp}(a,q)\}_{a\in S},\ E;\ O_\phi\big),\qquad E=\mathrm{Retr}(\mathcal R_G,q)\ \text{(없을 수 있음)} \qquad\text{(information selection)} \tag{4b}$$

핵심 문장 (본문에 그대로):

> $\sigma$의 이상적 입력은 $\mathrm{hold}(\cdot,t)$이지만 관측할 수 없다. 카드 $\mathrm{card}(G)$는 그것의 정적 근사이고, 그룹 기록 $\mathcal R_G$는 동적 근사이다. 메커니즘은 (i) 두 결정에 어느 근사를 주는가($O_\sigma, O_\phi$), (ii) 결정을 어디서 내리는가(locus)로 구분된다.

### 조건 좌표표 (§4 또는 §5.2에 표로)

| 조건 | $O_\sigma$ (locus) | $O_\phi$ (locus) | $\phi$ 형식 |
|---|---|---|---|
| Direct | card (요청자) | $W_h$ (응답자) | 응답자의 답 |
| Direct+relay | card (요청자) + card (응답자 → 동료 ≤ 3) | $W$ (응답자) | 응답자의 답 |
| Routing | $\mathcal R_G$ (게이트웨이) | $W_a$ (응답자들) | 원문 전달 |
| Retrieve | $\mathcal R_G$ (게이트웨이) | — (요청자에게 이관) | 답 원문 + $E$ 원문 |
| **Ingress (pull by proxy)** | $\mathcal R_G$ (게이트웨이) | $\{\mathrm{Resp}\}\cup E$ (게이트웨이) | 구조화 조립 + 재질의 |
| Sidecar | card (요청자) | $W_a\cup E$ (응답자 부착 모듈) | 구조화 조립 |
| Full-load (참조) | — | $\pi\equiv1$, 단일 에이전트 | — |

한 칸씩만 바뀐다: Direct→Routing은 $O_\sigma$; Routing→Ingress는 $O_\phi$와 locus; Ingress→Sidecar는 locus만; Ingress→Retrieve는 $\phi$만(조립 제거); Direct→Relay는 $O_\sigma$에 한 단계 추가. 사다리와 변형이 같은 좌표계에 놓이므로 "단일 요인 통제"라는 표현 대신 "한 성분씩 바꾼 비교"로 쓴다.

### 공개 정책과 전달

$$\Delta(x)\subseteq\mathcal D_G(x) \tag{5}$$

$\mathcal D_G(x)$ = 경계를 넘어도 되는 내용(허용 정책) — 모든 경계 조건에서 동일. $\Delta(x)$ = 메커니즘이 실제로 넘긴 것. 조건 차이는 $\Delta$에서만 난다. Full-load는 $\pi\equiv 1$이라 이 틀 밖의 참조이며 "분할 없는 단일 에이전트"로만 부른다(상한 아님: 27B에서 Ingress ≥ Full-load).

**불변식 (2)의 실측** (`analysis_package/tables/access_audit.csv`, 81런의 `obs/access.jsonl`): 분할 조건 6개(Direct·Routing·Ingress·relay·retrieve·sidecar, 63런)의 기록 읽기 349,072건은 전부 읽는 주체의 자기 그룹 안이고, 교차 그룹 읽기는 시도 0·허용 0·거부 0. Full-load(18런)는 조직 전체 읽기 34,141건(DB 27,010·이력 7,131) 전부 허용 — 설계대로. §5 공정성 문단에 이 수치를 쓴다.

## 4. §3.4 Loss model and metrics

요구 $n$마다 다섯 관문을 순서 있는 사건으로 둔다.

$$\begin{aligned}
\gamma_{req} &: a_q\text{가 } n\text{을 묻는다}\\
\gamma_{route} &: S\cap\mathrm{hold}(R_n,t)\neq\emptyset\ \ \lor\ \ R_n\cap E\neq\emptyset\\
\gamma_{sel} &: R_n\cap\Delta(x)\neq\emptyset \quad(\text{하위 원인: window / answer / search / assembly})\\
\gamma_{state} &: \text{전달된 버전}=r^{(t)}\\
\gamma_{use} &: y_\tau=y^*
\end{aligned} \tag{6}$$

$$\ell(n)=\min\{k:\gamma_k=0\},\qquad L_k(c)=P\big[\ell(n)=k\mid c\big],\qquad \delta(c)=1-\sum_{k\le\mathrm{state}}L_k(c) \tag{7}$$

- $\gamma_{sel}$의 하위 원인은 $O_\phi$의 어느 성분이 비었는지: window(응답자 문맥에 없음), answer(있었으나 말하지 않음), search(검색이 놓침), assembly(검색됐으나 조립이 버림).
- $\gamma_{route}$에 "$R_n\cap E\neq\emptyset$"를 넣는 것이 Ingress의 route 손실 0을 설명한다(검색이 중개 오류를 흡수). 이 정의를 명시해야 "Routing 11 vs Ingress 0"에 대한 질문이 안 나온다.

과제 지표:

$$\mathrm{Acc}(c)=\frac1{|T|}\sum_{\tau\in T}\mathbb 1\big[y^c_\tau=y^*_\tau\big],\qquad
\Delta_{route}=\mathrm{Acc}(\mathrm{Rout})-\mathrm{Acc}(\mathrm{Dir}),\quad
\Delta_{sel}=\mathrm{Acc}(\mathrm{Ingr})-\mathrm{Acc}(\mathrm{Rout}) \tag{8}$$

$$\Pi(c)=\mathrm{Acc}_A(c)-\mathrm{Acc}_{\bar A}(c),\qquad \rho(c)=1-\frac{\Pi(c)}{\Pi(\mathrm{Dir})} \tag{9}$$

$$\mathrm{cov}(\tau)=\frac{|\Delta(\tau)\cap R_\tau|}{|R_\tau|},\qquad \upsilon(c)=\mathrm{Acc}\big(c\ \big|\ \mathrm{cov}=1\big) \tag{10}$$

- 모든 Δ는 같은 (시나리오, 과제) 쌍에 대한 쌍 비교; CI는 쌍 부트스트랩, 검정은 McNemar. 이 사실은 §5.4에서 한 번만.
- $\rho$는 조건 내 격차 기준("gap closed"의 표준 정의). 서론의 "67pp → 28pp, 58% 회복"과 같은 수. §5.4에서 재정의하지 말고 (9)를 가리킨다.

## 5. Remark — 모델이 주는 예측 (정리가 아니라 remark로)

(3)과 (4)에서 바로 따라온다.

1. 클래스 A에서는 $\sigma_{\mathrm{card}}=\sigma_{\mathcal R_G}=h(n)$이므로 $O_\sigma$만 바꾸는 개입은 효과가 없어야 한다 → $\mathrm{Acc}_A$는 조건 간 수평 (Fig. 2a).
2. B와 D는 $O_\sigma$ 또는 $O_\phi$에 $\mathcal R_G$가 들어가야 피복되고, C는 $|S|\ge2$ 또는 $E$가 필요하다 → 이득은 $\bar A$에 집중되고, 클래스별로 필요한 칸이 다르다(B는 중개 칸에서도, C·D는 선택 칸에서) (Fig. 2a).

"expected under the model"로 쓰고, §6에서 "관측과 일치"로 받는다.

## 6. §4 Pull by Proxy의 수식화

§3 좌표에서 Ingress = $(O_\sigma,O_\phi,\mathrm{locus})=(\mathcal R_G,\ \{\mathrm{Resp}\}\cup E,\ \text{경계})$, $\phi$는 구조화 조립, 폐루프.

```
1. Retrieve   E = Retr_k(R_G, q)                       버전·시각 메타데이터 포함
2. Mediate    S = σ(q, E, act_G), |S| ≤ m              기록상 누가 R을 만졌는가로 선택
3. Fan-out    ρ_a = Resp(a, q), a ∈ S                  병렬, 과제 예산 안
4. Assemble   y = φ(q, {ρ_a}, E) = (ŷ, Add, Conf, Prop, s_G)
                Add  ⊆ E \ facts({ρ_a})                 응답에 없는 기록 사실, 인용 [E#]/[R#]
                Conf                                   ρ_a ↔ E, ρ_a ↔ ρ_a' 불일치 [V#]
                Prop                                   후속 질의 제안 [S#]
                s_G                                    경계 상태: 보유자 이탈·보류·버전 표시
5. Requery    요청자가 되물으면 1–4 반복, s_G 유지
```

형식적으로 새로운 점 두 가지 (본문에 명시):
- (a) $\phi$의 입력에 구성원 응답과 지속 기록을 **동시에** 둔다. Routing($W_a$만)·Retrieve(결합을 요청자에 이관)와의 차이.
- (b) $\sigma$와 $\phi$가 **같은 관측 $\mathcal R_G$를 공유**한다. route 손실을 search가 흡수하는 이유(관문 원장 Ingress route 0).

변형은 한 성분씩 되돌린 ablation으로 소개: Sidecar(locus → 응답자), Retrieve($\phi$ → 항등), Relay($O_\sigma$에 카드 한 단계 추가, $\mathcal R_G$ 없음).

## 7. 기호 ↔ 구현 대응 (일관성 점검)

| 기호 | 구현 위치 |
|---|---|
| $\mathcal R_G$ | 그룹 DB + 규정 + 활동 로그(E#) + 메시지 기록; `analysis_package/tables/retrievals.csv.gz` |
| $W_a(t)$ | raw window + summary (f13b 창 구성, `context__*.json`) |
| $\mathrm{hold}(r,t)$, $h(n)$, class | worldgen gold: holders alive/active/state, card handler, `state_class` |
| $\mathrm{card}(G)$ | `configs/conditions.yaml`의 `directory: agent_cards / group_cards`, `card_mode: static` |
| $\sigma$ | 게이트웨이 선택; `gateway_decisions.csv` |
| $\phi$, Add/Conf/Prop/$s_G$ | assembly의 additions/conflicts/proposals; `boundary_state`, `version_marks` |
| $E=\mathrm{Retr}$ | 임베딩 검색(float64), 게이트웨이·sidecar·Full-load가 같은 검색기 |
| $\Delta(x)$, cov | `gbg/scoring/delivery.py`; coverage 0/partial/1 (`numbers3.json`) |
| $\gamma_k$, $\ell(n)$, $L_k$, $\delta$ | `gbg/scoring/{gates,ledger}.py`; L_req/L_route/L_sel.*/L_state/L_use; Fig. 3·`t11_gates.tex` |
| $\Pi,\rho,\upsilon$ | `numbers5_metrics.json`, `t12_boundary_metrics.tex`, Fig. 2(b) |
| 조건 좌표 | `configs/conditions.yaml`: direct / routing / ingress / full_load / direct_relay / retrieve / sidecar |

## 8. 넣지 말 것

| 항목 | 이유 |
|---|---|
| POMDP 튜플 $(S,A,O,T,R)$ | "정책은 어떻게 계산했나"가 따라옴. 관측 집합 $O_\sigma,O_\phi$만 필요. partial observability는 서술어로만 |
| 최적화 목적함수(피복 최대화 s.t. 예산) | 메커니즘은 최적화기가 아니라 LLM 프롬프트. "근사 보장은?"이 따라옴 |
| 정보이론적 한계·정리·증명 | 결과가 실증. 과한 형식은 신뢰를 깎음 |
| $H$(발견 가능성)·$R$(추론 단계)의 형식 정의 | §5.1 벤치마크 라벨로만 소개 |
| Egress(요청자 측) | I+E 조건은 실행하지 않음 |

## 9. 주의

- Full-load는 "상한"이라 부르지 않는다(27B: Ingress 53.4 ≥ Full-load 52.5).
- $C_{ops}$를 네 번째 클래스처럼 세지 않는다(겹침 플래그). 서론 4문단 표기와 일치시킨다.
- (6)의 $\gamma_{route}$ 정의(검색 포함)를 반드시 명시한다.
- (9)의 $\rho$와 서론 헤드라인 수치는 같은 정의다. 55%(¬A 상승분/Direct 격차)는 쓰지 않는다.
