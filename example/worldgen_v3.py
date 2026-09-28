#!/usr/bin/env python3
"""worldgen_v3.py — 통합 과제 생성기 (규격 v2 + 추론 템플릿 + 능력 기반 D 가변)

    python3 worldgen_v3.py --seed 7 --D 3 --tasks 300
    python3 worldgen_v3.py --seed 7 --D 5 --tasks 300

LLM 없음, 시드 결정적. 출력: <out>/D<D>_s<seed>/
    world_init.json   그룹·역할·에이전트·card·규정 (시스템 공개)
    timeline.jsonl    세계·로컬·교차 이벤트 전체, 완전 정렬 (정답 없음)
    work.jsonl        교차 작업의 과제 문장과 출력 형식 (시스템 공개)
    gold.jsonl        정답, need(의미 상태 + 출처), 경로, 반사실, 상태 등급, 오라클 (비공개)
    stats.json        실현 혼합 비율, 일차별 등급, 오라클 상한

구조 (규격 v2 대응)
  §2 세계  : 그룹 = 도메인 × 지역, 역할·card, 공유 DB(등록 지연), 규정, 에이전트별 대화 이력
  §3 조각  : 에이전트가 처리한 일에서 생기는 이력 조각(보류 의도, 예외, 인수인계, 근거, 관측),
             발견 가능성 태그 H0 일지 / H1 활동 흔적 / H2 문맥 의존
  §4 시간  : 우선순위 큐 forward pass, 워밍업, 출생-사멸(에이전트·엔티티), 작업 효과가 세계에 반영(상태 매개 결합),
             ShadowContexts(K 토큰 창을 결정적으로 모사)
  §5 작업  : 추론 유형 템플릿 11종, 핵심 능력 + 확장 제약(활성 도메인에 따라), TracingWorld로 정답·need 추적,
             반사실 4종(stale / partial / neardup / wrong_owner)
"""
import argparse, collections, hashlib, heapq, json, os, random

# ═════════════════════════════ 상수 ═════════════════════════════
ALL_DOMAINS = ["HR", "IT", "FIN", "PROC", "LEGAL"]
ALL_REGIONS = ["SEL", "TYO", "SGP"]
ROLES = {"HR": ["records", "records", "payroll", "recruiting"], "IT": ["assets", "assets", "access", "licenses"],
         "FIN": ["budgeting", "budgeting", "payables", "closing"], "PROC": ["buying", "buying", "vendors", "receiving"],
         "LEGAL": ["contracts", "contracts", "compliance", "privacy"]}
CARD = {"records": "직원 소속·직급·계약 유형 기록 조회와 갱신", "payroll": "급여 등급, 입사자 장비 지원 판단", "recruiting": "채용 진행과 입사 처리",
        "assets": "자산 배정·회수, 사내 재고 관리", "access": "계정·접근 권한, 장비 등급 판단", "licenses": "소프트웨어 라이선스 좌석 관리",
        "budgeting": "예산 라인 편성·조정·잔액 조회", "payables": "가승인 검토·등록, 정산", "closing": "월 마감, 취소 확정",
        "buying": "견적 요청·발주", "vendors": "공급사 등급·리드타임 관리", "receiving": "입고·납품 확인",
        "contracts": "계약 조건·기간 관리", "compliance": "승인 규정·예외 판단", "privacy": "데이터 거주 규정",
        "coordinator": "요청 접수와 워커 배정", "worker": "배정된 건 처리"}
DEPTS = {"SEL": ["영업1팀", "영업2팀", "개발1팀", "개발2팀", "마케팅팀", "고객지원팀"],
         "TYO": ["営業1課", "営業2課", "開発1課", "開発2課", "企画課", "サポート課"],
         "SGP": ["Sales-A", "Sales-B", "Dev-A", "Dev-B", "Marketing", "Support"]}
NAMES = {"SEL": ["김하린", "박도윤", "이서준", "최지우", "정예린", "한시우", "오민재", "윤채원", "장우진", "신다은",
                 "임하준", "권소율", "조은호", "강서아", "배지훈", "문가온", "송유나", "황태오", "서지안", "노하은"],
         "TYO": ["佐藤結衣", "小野健", "田中翔", "高橋美咲", "鈴木大輔", "伊藤葵", "渡辺蓮", "山本陽菜", "中村悠", "小林凛",
                 "加藤湊", "吉田楓", "山田蒼", "松本紬", "井上律", "木村結翔", "林芽依", "清水颯", "山口澪", "森大和"],
         "SGP": ["Tan Wei", "Lim Hui", "Ng Jia", "Goh Ren", "Lee Min", "Ong Kai", "Teo Yan", "Chua Li", "Koh Zhi", "Yeo Shan",
                 "Sim Rui", "Low Jun", "Ho Xin", "Seah En", "Tay Qi", "Wong Hao", "Chan Yi", "Toh Ming", "Poh Wen", "Quek Ann"]}
ITEM_TYPES = {"노트북": ["basic", "standard", "premium"], "워크스테이션": ["standard", "premium"], "모니터": ["basic", "standard"]}
TIER_RANK = {"basic": 0, "standard": 1, "premium": 2}
PRICE = {"basic": (450_000, 900_000), "standard": (900_000, 1_600_000), "premium": (1_600_000, 2_500_000)}
SOFTWARE = ["CAD", "IDE Pro", "Analytics", "Design Suite"]
RESET_DAYS = [16, 46, 76]
CLASS_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}


def kstr(key): return "/".join(str(x) for x in key)
def h(x): return int(hashlib.md5(str(x).encode()).hexdigest(), 16)


class RNG:
    """이름 붙은 난수 흐름: 한 구성요소의 변경이 다른 구성요소의 난수를 밀지 않음."""
    def __init__(s, seed): s.seed, s.st = seed, {}
    def __call__(s, name):
        if name not in s.st:
            s.st[name] = random.Random(int(hashlib.sha256(f"{s.seed}|{name}".encode()).hexdigest()[:16], 16))
        return s.st[name]


def poisson(r, lam):
    L, k, p = pow(2.718281828, -lam), 0, 1.0
    while True:
        p *= r.random()
        if p <= L: return k
        k += 1


class Skip(Exception): pass


# ═════════════════════════════ 세계 ═════════════════════════════
class World:
    def __init__(w, P):
        w.P, w.R = P, RNG(P.seed)
        w.domains, w.regions = ALL_DOMAINS[:P.D], ALL_REGIONS[:P.R]
        w.day, w.round, w.seq = -P.warmup, 0, 0
        w.groups, w.agent_group, w.agent_role, w.active = {}, {}, {}, {}
        w.tx, w.tx_total = collections.defaultdict(list), collections.defaultdict(int)
        w.frags, w.db = {}, {}
        w.journal, w.activity = collections.defaultdict(list), collections.defaultdict(list)
        w.timeline, w.pq, w.ids, w.canaries = [], [], collections.Counter(), set()
        w.emps, w.commits, w.assets, w.inv, w.vendors, w.quotes = {}, {}, {}, {}, {}, {}
        w.owner_exc, w.q_exc, w.exclusions, w.overrides, w.price_notices = [], [], [], [], []
        w.rules, w.tasks, w.sig, w.cooldown = {}, [], collections.Counter(), {}
        w.counts = collections.Counter(); w.spawned_today = []

    # ── 기본 도구 ──
    def has(w, d): return d in w.domains
    def newid(w, p): w.ids[p] += 1; return f"{p}-{w.ids[p]:05d}"
    def canary(w, lo, hi):
        r = w.R("canary")
        while True:
            v = r.randrange(lo, hi)
            if v % 1000 and v not in w.canaries: w.canaries.add(v); return v
    def log(w, typ, **kw):
        w.seq += 1
        w.timeline.append({"t": f"{w.day:+03d}.{w.round}.{w.seq:06d}", "day": w.day, "type": typ, "warmup": w.day < 1, **kw})
    def push(w, day, rnd, prio, typ, payload):
        w.seq += 1; heapq.heappush(w.pq, (day, rnd, prio, w.seq, typ, payload))
    def other_regions(w, r): return [x for x in w.regions if x != r]
    def sibling(w, r, dept): d = DEPTS[r]; return d[(d.index(dept) + 1) % len(d)] if dept in d else dept

    # ── 대화 이력 (ShadowContexts의 원자료) ──
    def tok(w, text): return max(12, int(len(text) * 1.1))
    def tx_add(w, aid, text, fid=None, extra=0):
        t = w.tok(text) + extra; w.tx_total[aid] += t
        w.tx[aid].append({"day": w.day, "tok": t, "cum": w.tx_total[aid], "fid": fid})
    def in_window(w, fid):
        """이 조각이 지금 주인의 컨텍스트 창(최근 K 토큰 원문) 안에 있는가."""
        f = w.frags[fid]; a = f["agent"]; e = w.tx[a][f["tx_idx"]]
        return w.active.get(a, False) and (w.tx_total[a] - e["cum"] + e["tok"]) <= w.P.K

    def frag(w, g, aid, kind, key, value, text, disc=None, copy_of=None):
        fid = w.newid("FR")
        if disc is None: disc = w.R("disc").choices(["H0", "H1", "H2"], w.P.disc_mix)[0]
        shown = text if disc != "H2" else "그 건 관련 — " + text.split(" ", 1)[-1]
        f = {"fid": fid, "group": g, "agent": aid, "day": w.day, "kind": kind, "key": kstr(key) if key else None,
             "value": value, "text": shown, "disc": disc, "copies": [], "origin": copy_of}
        w.frags[fid] = f; w.tx_add(aid, shown, fid); f["tx_idx"] = len(w.tx[aid]) - 1
        if disc == "H0": w.journal[g].append(fid)
        elif disc == "H1": w.activity[g].append((aid, fid))
        if copy_of: w.frags[copy_of]["copies"].append(fid)
        if w.agent_role.get(aid) == "worker" and copy_of is None:          # swarm: coordinator에는 요약만
            coord = f"{g.lower()}.c0"
            if w.R("summary").random() < w.P.p_summary_value:
                w.frag(g, coord, "summary", key, value, "[워커 보고] " + shown, disc="H1", copy_of=fid)
            else:
                w.tx_add(coord, "[워커 보고] 처리 완료 (세부 수치 생략)")
        return fid

    def fsrc(w, fid):
        f = w.frags[fid]
        hs = [{"agent": w.frags[x]["agent"], "in_window": w.in_window(x), "active": w.active.get(w.frags[x]["agent"], False)}
              for x in [fid] + f["copies"]]
        return {"fid": fid, "kind": f["kind"], "disc": f["disc"], "day": f["day"], "holders": hs}

    # ── 공유 DB (등록 지연) ──
    def write(w, g, etype, eid, attr, value, holder, text, kind="observation", lag=None, disc=None):
        key = (g, etype, eid, attr)
        if lag is None: lag = w.R("lag").randint(*w.P.db_lag)
        fid = w.frag(g, holder, kind, key, value, text, disc)
        vs = w.db.setdefault(key, [])
        vs.append({"v": len(vs) + 1, "day": w.day, "db_day": w.day + lag, "value": value, "fid": fid})
        return fid
    def cur(w, key):
        vs = [v for v in w.db.get(key, []) if v["day"] <= w.day]
        return vs[-1]["value"] if vs else None

    # ── 그룹·에이전트 ──
    def add_agent(w, g, aid, role):
        w.groups[g]["agents"].append(aid); w.agent_group[aid] = g; w.agent_role[aid] = role; w.active[aid] = True
    def assign(w, g, role, key):
        """배치: specialist는 역할 일치자 중 엔티티 해시 고정 + p_cover 대리, swarm은 새 워커 spawn."""
        G = w.groups[g]
        if G["topology"] == "swarm":
            wid = f"{g.lower()}.w{w.newid('WK')[-5:]}"; w.add_agent(g, wid, "worker"); w.spawned_today.append(wid)
            w.log("spawn", group=g, agent=wid); w.counts["spawn"] += 1; return wid
        c = sorted(a for a in G["agents"] if w.active[a] and w.agent_role[a] == role) or sorted(a for a in G["agents"] if w.active[a])
        a = c[h(key) % len(c)]
        if w.R("cover").random() < w.P.p_cover:
            o = sorted(x for x in G["agents"] if w.active[x] and x != a)
            if o: a = w.R("cover").choice(o)
        return a
    def card(w, g, role):
        """card만 보고 고르는 대상. 복제 담당자는 구분 불가 → 정렬상 첫 번째. swarm은 coordinator."""
        G = w.groups[g]
        if G["topology"] == "swarm": return f"{g.lower()}.c0"
        c = sorted(a for a in G["agents"] if w.active[a] and w.agent_role[a] == role) or sorted(a for a in G["agents"] if w.active[a])
        return c[0]
    def work(w, aid, text):
        w.tx_add(aid, "[작업] " + text, extra=w.P.task_overhead)

    # ═════════ 초기화 ═════════
    def init(w):
        r0 = w.R("init")
        for d in w.domains:
            for r in w.regions:
                g = f"{d}-{r}"; top = "swarm" if g in w.P.swarm else "specialist"
                w.groups[g] = {"domain": d, "region": r, "topology": top, "agents": []}
                if top == "swarm": w.add_agent(g, f"{g.lower()}.c0", "coordinator")
                else:
                    for i, role in enumerate(ROLES[d]): w.add_agent(g, f"{g.lower()}.a{i+1}", role)
        for r in w.regions:
            others = w.other_regions(r)
            w.rules[r] = {"tiers": [(1_000_000, "팀장"), (2_500_000, "본부장"), (10**12, "CFO")], "newcomer_days": 30, "newcomer_cap": 1_500_000,
                          "elig": {1: "basic", 2: "basic", 3: "standard", 4: "standard", 5: "premium"}, "seat_price": w.canary(120_000, 260_000),
                          "restricted": r0.sample(DEPTS[r], 2), "sw_contractor_block": r0.sample(SOFTWARE, 2), "transfer_share": 0.5}
            hr, it, fin = f"HR-{r}", f"IT-{r}", f"FIN-{r}"
            for i, nm in enumerate(NAMES[r]):
                e = f"E-{r}-{1000+i}"
                alias = (nm[1:] + r0.choice([" 과장", " 대리", " 선임"])) if r == "SEL" else (nm[:2] + "さん" if r == "TYO" else nm.split()[0] + " (mgr)")
                w.emps[e] = {"name": nm, "alias": alias, "region": r}
                prof = {"dept": r0.choice(DEPTS[r]), "grade": r0.randint(1, 5), "contract": "contractor" if r0.random() < 0.28 else "regular",
                        "hire_day": -r0.randint(40, 900), "status": "active"}
                w.write(hr, "emp", e, "profile", prof, w.assign(hr, "records", e), f"{nm} 인사 기록 확정: {prof['dept']}, {prof['grade']}급.", lag=0, disc="H0")
                if w.has("LEGAL") and prof["contract"] == "contractor":
                    lg = f"LEGAL-{r}"; terms = {"allowed_tier": r0.choice(["basic", "standard"]), "expiry": r0.randint(5, 120), "nda": r0.random() < 0.6}
                    w.write(lg, "contract", e, "terms", terms, w.assign(lg, "contracts", e), f"{nm} 계약: 허용 {terms['allowed_tier']}, {terms['expiry']}일 만료.", lag=0)
            for dept in DEPTS[r]:
                v = w.canary(2_400_000, 5_200_000)
                w.write(fin, "line", dept, "remaining", v, w.assign(fin, "budgeting", dept), f"{dept} capex 잔액 {v:,}원 확정.", lag=0, disc="H0")
                w.write(fin, "line", dept, "base", v, w.assign(fin, "budgeting", dept), f"{dept} 분기 기준 배정 {v:,}원.", lag=0, disc="H0")
            for itype, tiers in ITEM_TYPES.items():
                for tier in tiers:
                    iid = f"INV-{r}-{itype[:2]}{tier[0].upper()}"
                    w.inv[iid] = {"region": r, "type": itype, "tier": tier, "cost": w.canary(*PRICE[tier])}
                    w.write(it, "inv", iid, "qty", r0.randint(1, 3), w.assign(it, "assets", iid), f"사내 재고 {itype}({tier}) 수량 확인.", lag=0)
            for e, x in list(w.emps.items()):
                if x["region"] != r: continue
                for _ in range(r0.randint(1, 2)):
                    itype = r0.choice(list(ITEM_TYPES)); tier = r0.choice(ITEM_TYPES[itype]); aid = f"A-{r}-{w.canary(3000, 9999)}"
                    w.assets[aid] = {"region": r, "type": itype, "tier": tier, "history": {e}}
                    w.write(it, "asset", aid, "holder", {"emp": e}, w.assign(it, "assets", aid), f"{aid} {itype} {x['name']}에게 배정.", lag=0)
            for sw in SOFTWARE:
                seats = r0.randint(18, 40)
                w.write(it, "lic", sw, "seats", {"seats": seats, "used": seats - r0.randint(1, 8)}, w.assign(it, "licenses", sw), f"{sw} 좌석 현황 갱신.", lag=0)
            if w.has("PROC"):
                pg = f"PROC-{r}"
                for vi in range(4):
                    vid = f"V-{r}-{vi}"; country = r if vi < 2 else ("CN" if vi == 3 else (others[0] if others else r))
                    w.vendors[vid] = {"region": r, "country": country, "registered": vi != 3}
                    w.write(pg, "vendor", vid, "lead", r0.randint(3, 14), w.assign(pg, "vendors", vid), f"공급사 {vid} 리드타임 확인.", lag=0)
                    for itype, tiers in ITEM_TYPES.items():
                        for tier in tiers:
                            if r0.random() < 0.8:
                                qid = f"Q-{vid}-{itype[:2]}{tier[0].upper()}"; w.quotes[qid] = {"region": r, "vendor": vid, "type": itype, "tier": tier}
                                v = w.canary(*PRICE[tier])
                                w.write(pg, "quote", qid, "amount", v, w.assign(pg, "buying", itype), f"{vid} {itype}({tier}) 견적 {v:,}원.", lag=0)
                for sw in SOFTWARE:
                    v = w.canary(110_000, 280_000)
                    w.write(pg, "seatprice", sw, "amount", v, w.assign(pg, "buying", sw), f"{sw} 좌석 단가 {v:,}원.", lag=0)

    # ═════════ 출생-사멸: 에이전트 ═════════
    def lifecycle(w):
        r = w.R("life")
        for g, G in w.groups.items():
            if G["topology"] == "swarm": continue
            for a in sorted(G["agents"]):
                if w.active[a] and r.random() < w.P.mu_agent:
                    w.active[a] = False; ho = r.random() < w.P.p_handover
                    na = f"{g.lower()}.n{w.newid('AG')[-4:]}"
                    w.log("agent_leave", group=g, agent=a, handover=ho); w.counts["agent_leave"] += 1
                    w.push(w.day + 1, 0, 0, "agent_join", {"group": g, "agent": na, "role": w.agent_role[a], "from": a, "handover": ho})
    def on_join(w, p):
        w.add_agent(p["group"], p["agent"], p["role"]); w.log("agent_join", **p); w.counts["agent_join"] += 1
        if p["handover"]:
            recent = [f for f in w.frags.values() if f["agent"] == p["from"] and f["value"] is not None and f["origin"] is None][-3:]
            for f in recent:
                w.frag(p["group"], p["agent"], "handover", None, f["value"], "[인수인계] " + f["text"], disc="H1", copy_of=f["fid"])

    # ═════════ 로컬 작업 (세계를 바꾸는 이벤트) ═════════
    def schedule_day(w):
        r = w.R("slots")
        for g, G in w.groups.items():
            n_act = sum(1 for a in G["agents"] if w.active[a]) if G["topology"] == "specialist" else 3
            for _ in range(poisson(r, w.P.local_per_agent * n_act)):
                w.push(w.day, r.randint(1, 3), 2, "local", {"group": g})
        if w.day >= 1:
            base = w.P.tasks / w.P.T; n = int(base) + (1 if r.random() < base % 1 else 0)
            for _ in range(n): w.push(w.day, r.randint(1, 3), 3, "cross", {})
        if w.day in RESET_DAYS:
            w.push(w.day, 1, 1, "budget_reset", {})

    def active_emps(w, r):
        return sorted(e for e, x in w.emps.items() if x["region"] == r and (w.cur((f"HR-{r}", "emp", e, "profile")) or {}).get("status") == "active")

    def local(w, g):
        G = w.groups[g]; d, r = G["domain"], G["region"]; rr = w.R("local")
        kinds = {"HR": [("transfer", .22), ("hire", .08), ("exit", .05), ("grade", .08), ("routine", .57)],
                 "IT": [("assign", .15), ("restock", .14), ("license", .12), ("recover", .08), ("routine", .57)],
                 "FIN": [("line_adjust", .1), ("commit_review", .25), ("owner_exc", .03 if len(w.regions) > 1 else 0), ("q_exc", .03), ("routine", .59)],
                 "PROC": [("quote_update", .12), ("exclude", .025), ("receipt", .15), ("lead", .05), ("price_notice", .04), ("routine", .59)],
                 "LEGAL": [("amend", .08), ("extend", .08), ("override", .04), ("routine", .8)]}[d]
        k = rr.choices([x for x, _ in kinds], [p for _, p in kinds])[0]
        getattr(w, f"L_{d}_{k}", w.L_routine)(g, r, rr)
        if w.day >= 1: w.counts[f"local:{d}:{k}"] += 1

    def L_routine(w, g, r, rr):
        a = w.assign(g, rr.choice(ROLES[w.groups[g]["domain"]]), rr.random())
        w.work(a, "일상 문의 응대와 기록 정리"); w.log("local", group=g, kind="routine", assignee=a)

    # HR
    def L_HR_transfer(w, g, r, rr):
        es = [e for e in w.active_emps(r) if (w.cur((g, "emp", e, "transfer")) or {}).get("status") != "approved"]
        if not es: return
        e = rr.choice(es); prof = w.cur((g, "emp", e, "profile")); to = rr.choice([x for x in DEPTS[r] if x != prof["dept"]]); eff = w.day + rr.randint(2, 10)
        a = w.assign(g, "records", e); w.work(a, f"{w.emps[e]['name']} 부서 이동 요청 검토")
        w.write(g, "emp", e, "transfer", {"to": to, "effective": eff, "status": "approved"}, a, f"{w.emps[e]['name']} {to} 이동 승인, {eff}일 발효.", kind="pending_intent")
        w.push(eff, 1, 1, "transfer_effect", {"g": g, "e": e}); w.log("local", group=g, kind="transfer", assignee=a, emp=e)
    def transfer_effect(w, p):
        g, e = p["g"], p["e"]; prof = dict(w.cur((g, "emp", e, "profile"))); tr = w.cur((g, "emp", e, "transfer"))
        if prof["status"] != "active": return
        prof["dept"] = tr["to"]; a = w.assign(g, "records", e)
        w.write(g, "emp", e, "profile", prof, a, f"{w.emps[e]['name']} {tr['to']} 소속 반영.")
        w.write(g, "emp", e, "transfer", {**tr, "status": "done"}, a, f"{w.emps[e]['name']} 이동 완료 처리.")
    def L_HR_hire(w, g, r, rr):
        e = f"E-{r}-{2000 + w.ids['hire']}"; w.ids["hire"] += 1; nm = rr.choice(NAMES[r]) + "2"
        w.emps[e] = {"name": nm, "alias": (nm[1:] + " 씨") if r == "SEL" else (nm[:2] + "さん" if r == "TYO" else nm.split()[0]), "region": r}
        prof = {"dept": rr.choice(DEPTS[r]), "grade": rr.randint(1, 3), "contract": "contractor" if rr.random() < 0.4 else "regular", "hire_day": w.day, "status": "active"}
        a = w.assign(g, "recruiting", e); w.work(a, f"{nm} 입사 처리")
        w.write(g, "emp", e, "profile", prof, a, f"{nm} {prof['dept']} 입사, {prof['grade']}급, {prof['contract']}.")
        if w.has("LEGAL") and prof["contract"] == "contractor": w.push(w.day + rr.randint(1, 2), 1, 2, "contract_create", {"e": e})
        w.log("local", group=g, kind="hire", assignee=a, emp=e); w.counts["employee_birth"] += 1
    def L_HR_exit(w, g, r, rr):
        es = w.active_emps(r)
        if len(es) < 12: return
        e = rr.choice(es); prof = dict(w.cur((g, "emp", e, "profile"))); prof["status"] = "exited"
        a = w.assign(g, "records", e); w.work(a, f"{w.emps[e]['name']} 퇴직 처리")
        w.write(g, "emp", e, "profile", prof, a, f"{w.emps[e]['name']} 퇴직 처리 완료."); w.log("local", group=g, kind="exit", assignee=a, emp=e)
        w.counts["employee_death"] += 1
    def L_HR_grade(w, g, r, rr):
        es = w.active_emps(r)
        if not es: return
        e = rr.choice(es); prof = dict(w.cur((g, "emp", e, "profile"))); prof["grade"] = max(1, min(5, prof["grade"] + rr.choice([-1, 1])))
        a = w.assign(g, "payroll", e); w.work(a, "직급 조정 반영")
        w.write(g, "emp", e, "profile", prof, a, f"{w.emps[e]['name']} {prof['grade']}급으로 조정.", kind="rationale"); w.log("local", group=g, kind="grade", assignee=a)
    # IT
    def L_IT_assign(w, g, r, rr, e=None, iid=None, handle=None):
        items = [i for i, x in w.inv.items() if x["region"] == r and (w.cur((g, "inv", i, "qty")) or 0) > 0]
        es = w.active_emps(r)
        if not items or not es: return
        iid = iid if iid in items else rr.choice(sorted(items)); e = e or rr.choice(es); x = w.inv[iid]
        a = w.assign(g, "assets", iid); w.work(a, f"{w.emps[e]['name']} 장비 배정" + (f" ({handle} 후속)" if handle else ""))
        w.write(g, "inv", iid, "qty", w.cur((g, "inv", iid, "qty")) - 1, a, f"재고 {x['type']}({x['tier']}) 1대 출고.")
        aid = f"A-{r}-{w.canary(10000, 99999)}"; w.assets[aid] = {"region": r, "type": x["type"], "tier": x["tier"], "history": {e}}
        w.write(g, "asset", aid, "holder", {"emp": e}, a, f"{aid} {x['type']} {w.emps[e]['name']}에게 배정."); w.log("local", group=g, kind="assign", assignee=a)
    def L_IT_restock(w, g, r, rr):
        iid = rr.choice(sorted(i for i, x in w.inv.items() if x["region"] == r)); a = w.assign(g, "assets", iid)
        w.work(a, "재고 입고 반영"); w.write(g, "inv", iid, "qty", (w.cur((g, "inv", iid, "qty")) or 0) + rr.randint(1, 2), a, f"{w.inv[iid]['type']} 재고 입고.")
        w.log("local", group=g, kind="restock", assignee=a)
    def L_IT_license(w, g, r, rr, sw=None, delta=None):
        sw = sw or rr.choice(SOFTWARE); v = dict(w.cur((g, "lic", sw, "seats"))); a = w.assign(g, "licenses", sw)
        v["used"] = max(0, min(v["seats"], v["used"] + (delta if delta is not None else rr.choice([-2, -1, 1, 2, 3]))))
        w.work(a, f"{sw} 좌석 사용 변경"); w.write(g, "lic", sw, "seats", v, a, f"{sw} 사용 {v['used']}/{v['seats']}석."); w.log("local", group=g, kind="license", assignee=a)
    def L_IT_recover(w, g, r, rr, only=None):
        cands = []
        for aid, x in w.assets.items():
            if x["region"] != r: continue
            hv = w.cur((g, "asset", aid, "holder"))
            if hv and hv.get("emp"):
                st = (w.cur((f"HR-{r}", "emp", hv["emp"], "profile")) or {}).get("status")
                if (only and aid in only) or (not only and st == "exited"): cands.append(aid)
        if not cands: return
        aid = rr.choice(sorted(cands)); a = w.assign(g, "assets", aid); w.work(a, "퇴직자 자산 회수")
        w.write(g, "asset", aid, "holder", {"emp": None}, a, f"{aid} 회수 완료."); w.log("local", group=g, kind="recover", assignee=a)
    # FIN
    def L_FIN_line_adjust(w, g, r, rr):
        dept = rr.choice(DEPTS[r]); v = w.canary(1_600_000, 5_000_000); a = w.assign(g, "budgeting", dept)
        why = rr.choice(["본부 재배정", "분기 이월 반영", "긴급 집행 차감", "환급 반영"])
        w.work(a, f"{dept} 예산 조정"); w.write(g, "line", dept, "remaining", v, a, f"{dept} capex 잔액 {v:,}원으로 조정 ({why}).", kind="rationale")
        w.log("local", group=g, kind="line_adjust", assignee=a)
    def commit_review(w, g, r, dept, amount, item, rr, handle=None):
        cid = w.newid("CMT"); a = w.assign(g, "payables", dept); settle = w.day + rr.randint(4, 14)
        w.work(a, f"{dept} {item} 가승인 검토" + (f" ({handle} 후속)" if handle else ""))
        fid = w.frag(g, a, "pending_intent", (g, "commit", cid, "status"), {"status": "reviewing", "amount": amount, "expected_settle": settle},
                     f"{dept} {item} {amount:,}원 가승인 검토 시작, {settle}일 정산 예정.")
        c = {"cid": cid, "group": g, "dept": dept, "amount": amount, "item": item, "review_day": w.day, "review_fid": fid, "expected_settle": settle, "talk_fid": None}
        w.commits[cid] = c
        if rr.random() < 0.12: w.push(w.day + rr.randint(1, 4), 2, 1, "commit_cancel", {"cid": cid})
        else: w.push(w.day + rr.randint(1, 3), 2, 1, "commit_confirm", {"cid": cid})
        if rr.random() < 0.15:
            b = w.assign(g, "budgeting", dept); c["talk_fid"] = w.frag(g, b, "observation", None, "cancel_talk", f"{cid} 건 취소하자는 얘기 나옴 (미확정).")
        w.log("local", group=g, kind="commit_review", assignee=a, cid=cid); w.counts["commit_birth"] += 1
        return cid
    def L_FIN_commit_review(w, g, r, rr):
        dept = rr.choice(DEPTS[r])
        for x in w.owner_exc:                                   # 소유권 예외 중인 부서는 다른 지역 재무에서 집행
            if x["dept"] == dept and x["from"] == r and x["start"] <= w.day <= x["end"]: g = f"FIN-{x['to']}"
        w.commit_review(g, r, dept, w.canary(150_000, 900_000), rr.choice(list(ITEM_TYPES) + ["회의실 장비", "출장비 선급"]), rr)
    def commit_confirm(w, p):
        c = w.commits[p["cid"]]; a = w.assign(c["group"], "payables", c["dept"])
        w.write(c["group"], "commit", c["cid"], "status", {"status": "pending", "amount": c["amount"], "expected_settle": c["expected_settle"]}, a,
                f"{c['cid']} {c['dept']} {c['amount']:,}원 가승인 확정.")
        w.push(c["expected_settle"], 2, 1, "commit_settle", {"cid": c["cid"]})
    def commit_settle(w, p):
        c = w.commits[p["cid"]]; a = w.assign(c["group"], "payables", c["dept"])
        w.write(c["group"], "commit", c["cid"], "status", {"status": "settled", "amount": c["amount"], "expected_settle": c["expected_settle"]}, a, f"{c['cid']} 정산 완료.")
        w.counts["commit_death"] += 1
    def commit_cancel(w, p):
        c = w.commits[p["cid"]]; a = w.assign(c["group"], "closing", c["dept"])
        w.write(c["group"], "commit", c["cid"], "status", {"status": "cancelled", "amount": c["amount"], "expected_settle": c["expected_settle"]}, a, f"{c['cid']} 취소 확정.")
        w.counts["commit_death"] += 1
    def L_FIN_owner_exc(w, g, r, rr):
        o = rr.choice(w.other_regions(r)); dept = rr.choice(DEPTS[r])
        if any(x["dept"] == dept and x["end"] >= w.day for x in w.owner_exc): return
        a = w.assign(g, "budgeting", dept); end = w.day + rr.randint(10, 25); w.work(a, "부서 예산 집행 주체 조정 회의")
        fid = w.frag(g, a, "exception", None, {"dept": dept, "to": o}, f"{dept} capex는 {end}일까지 {o} 재무에서 집행하기로 함.")
        og = f"FIN-{o}"; b = w.assign(og, "budgeting", dept)
        w.write(og, "line", dept, "remaining", w.cur((g, "line", dept, "remaining")), b, f"{r} {dept} capex 라인 이관 접수.")
        w.owner_exc.append({"dept": dept, "from": r, "to": o, "start": w.day, "end": end, "fid": fid}); w.log("local", group=g, kind="owner_exception", dept=dept)
    def L_FIN_q_exc(w, g, r, rr):
        dept = rr.choice(DEPTS[r]); a = w.assign(g, "budgeting", dept); w.work(a, "분기 집행 통제 지시 반영")
        fid = w.frag(g, a, "exception", None, {"dept": dept}, f"이번 분기 {dept} 신규 장비 100만원 초과 건은 본부장 승인 필요.")
        w.q_exc.append({"region": r, "dept": dept, "threshold": 1_000_000, "start": w.day, "end": w.day + rr.randint(15, 40), "fid": fid})
        w.log("local", group=g, kind="q_exception", dept=dept)
    def budget_reset(w, p):
        for r in w.regions:
            g = f"FIN-{r}"
            for dept in DEPTS[r]:
                a = w.assign(g, "budgeting", dept); base = w.cur((g, "line", dept, "base"))
                w.write(g, "line", dept, "remaining", base, a, f"{dept} 분기 재설정: {base:,}원.")
        w.log("world", kind="budget_reset")
    # PROC
    def L_PROC_quote_update(w, g, r, rr):
        qs = sorted(q for q, x in w.quotes.items() if x["region"] == r)
        if not qs: return
        q = rr.choice(qs); x = w.quotes[q]; v = w.canary(*PRICE[x["tier"]]); a = w.assign(g, "buying", x["type"])
        w.work(a, "견적 갱신"); w.write(g, "quote", q, "amount", v, a, f"{x['vendor']} {x['type']}({x['tier']}) 견적 {v:,}원으로 변경.", kind="rationale")
        w.log("local", group=g, kind="quote_update", assignee=a)
    def L_PROC_exclude(w, g, r, rr):
        v = rr.choice(sorted(x for x, y in w.vendors.items() if y["region"] == r)); a = w.assign(g, "vendors", v)
        w.work(a, "공급사 품질 이슈 검토"); fid = w.frag(g, a, "handover", None, {"vendor": v}, f"{v}는 품질 이슈로 당분간 비교 대상에서 제외할 것.")
        w.exclusions.append({"region": r, "vendor": v, "start": w.day, "end": w.day + rr.randint(5, 14), "fid": fid}); w.log("local", group=g, kind="exclude", assignee=a)
    def L_PROC_receipt(w, g, r, rr):
        cs = sorted(c for c, x in w.commits.items() if x["group"] == f"FIN-{r}" and (w.cur((g, "receipt", c, "received")) is None)
                    and (w.cur((x["group"], "commit", c, "status")) or {}).get("status") in ("pending", "cancelled"))
        if not cs: return
        c = rr.choice(cs); a = w.assign(g, "receiving", c); w.work(a, "입고 확인")
        w.write(g, "receipt", c, "received", True, a, f"{c} 물품 입고 확인."); w.log("local", group=g, kind="receipt", assignee=a)
    def L_PROC_lead(w, g, r, rr):
        v = rr.choice(sorted(x for x, y in w.vendors.items() if y["region"] == r)); a = w.assign(g, "vendors", v)
        w.work(a, "리드타임 재확인"); w.write(g, "vendor", v, "lead", rr.randint(3, 16), a, f"{v} 리드타임 변경 통보."); w.log("local", group=g, kind="lead", assignee=a)
    def L_PROC_price_notice(w, g, r, rr):
        itype = rr.choice(list(ITEM_TYPES)); pct = rr.choice([5, 8, 10, 15]); a = w.assign(g, "buying", itype)
        nxt = next((d for d in RESET_DAYS if d > w.day), RESET_DAYS[-1])
        w.work(a, "단가 인상 통보 검토"); fid = w.frag(g, a, "observation", None, {"type": itype, "pct": pct}, f"{itype} 단가 {nxt}일부터 {pct}% 인상 예정 통보 받음.")
        w.price_notices.append({"region": r, "type": itype, "pct": pct, "from": nxt, "fid": fid}); w.log("local", group=g, kind="price_notice", assignee=a)
    # LEGAL
    def contract_create(w, p):
        e = p["e"]; r = w.emps[e]["region"]; g = f"LEGAL-{r}"; rr = w.R("local")
        terms = {"allowed_tier": rr.choice(["basic", "standard"]), "expiry": w.day + rr.randint(30, 120), "nda": rr.random() < 0.6}
        a = w.assign(g, "contracts", e); w.work(a, "신규 계약 체결")
        w.write(g, "contract", e, "terms", terms, a, f"{w.emps[e]['name']} 계약 체결: 허용 {terms['allowed_tier']}, {terms['expiry']}일 만료.")
    def contractors(w, r):
        return sorted(e for e in w.emps if w.emps[e]["region"] == r and w.cur((f"LEGAL-{r}", "contract", e, "terms")))
    def L_LEGAL_amend(w, g, r, rr):
        cs = w.contractors(r)
        if not cs: return
        e = rr.choice(cs); t = dict(w.cur((g, "contract", e, "terms"))); t["allowed_tier"] = rr.choice(["basic", "standard"]); t["nda"] = rr.random() < 0.6
        a = w.assign(g, "contracts", e); w.work(a, "계약 조건 변경")
        w.write(g, "contract", e, "terms", t, a, f"{w.emps[e]['name']} 계약 조건 변경: 허용 {t['allowed_tier']}.", kind="rationale"); w.log("local", group=g, kind="amend", assignee=a)
    def L_LEGAL_extend(w, g, r, rr, e=None):
        cs = w.contractors(r)
        if not cs: return
        e = e or rr.choice(cs); t = dict(w.cur((g, "contract", e, "terms"))); t["expiry"] = max(t["expiry"], w.day) + rr.randint(30, 60)
        a = w.assign(g, "contracts", e); w.work(a, "계약 연장")
        w.write(g, "contract", e, "terms", t, a, f"{w.emps[e]['name']} 계약 {t['expiry']}일까지 연장."); w.log("local", group=g, kind="extend", assignee=a)
    def L_LEGAL_override(w, g, r, rr):
        cs = w.contractors(r)
        if not cs: return
        e = rr.choice(cs); a = w.assign(g, "compliance", e); w.work(a, "예외 승인 심의")
        fid = w.frag(g, a, "exception", None, {"emp": e}, f"{w.emps[e]['name']} 건은 프로젝트 사유로 premium 장비 예외 허용, 법무 확인 완료.")
        w.overrides.append({"emp": e, "start": w.day, "end": w.day + rr.randint(10, 30), "fid": fid}); w.log("local", group=g, kind="override", assignee=a)

    # ═════════ 디스패치 ═════════
    def dispatch(w, typ, p):
        if typ == "agent_join": w.on_join(p)
        elif typ == "local": w.local(p["group"])
        elif typ == "cross": gen_cross(w)
        elif typ == "followup": gen_cross(w, follow=p)
        elif typ == "effect": apply_effect(w, p)
        else: getattr(w, typ)(p)


# ═════════════════════════════ 추적 월드 (정답 + need 기록) ═════════════════════════════
class TW:
    """정답 함수가 세계를 읽는 유일한 통로. 읽기마다 need와 출처를 기록하고, mode로 반사실 세계를 만든다."""
    def __init__(t, w, root, mode=None):
        t.w, t.root, t.day, t.m, t.needs, t.cur, t.used = w, root, w.day, mode or {}, [], None, set()
        t.cnt = collections.Counter()
    def begin(t, sem, g, role):
        t.cur = {"sem": sem, "group": g, "role": role, "order": len(t.needs) + 1, "local": g == t.root, "sources": [], "card": t.w.card(g, role)}
        t.needs.append(t.cur)
    def _mode(t, name):
        """mode = {name: k}: 원격 need에서 name 반사실이 적용 가능한 k번째 지점만 비튼다."""
        if name in t.m and name not in t.used and not t.cur["local"]:
            t.cnt[name] += 1
            if t.cnt[name] - 1 == t.m[name]: t.used.add(name); return True
        return False
    def rule(t, ref): t.cur["sources"].append({"type": "rule", "ref": ref})
    def frag(t, fid, droppable=True):
        if droppable and t._mode("partial"): return False
        t.cur["sources"].append({"type": "frag", "frag": t.w.fsrc(fid)}); return True
    def db(t, key):
        vs = [v for v in t.w.db.get(key, []) if v["day"] <= t.day]
        if not vs: return None
        latest = vs[-1]
        if latest["db_day"] <= t.day:                                   # DB에 등록된 최신값
            val = vs[-2]["value"] if len(vs) > 1 and t._mode("stale") else latest["value"]
            t.cur["sources"].append({"type": "db", "key": kstr(key), "v": latest["v"]}); return val
        if t._mode("partial"):                                          # 최신값은 아직 이력에만 → 빠뜨리면 DB의 옛값
            vis = [v for v in vs if v["db_day"] <= t.day]; return vis[-1]["value"] if vis else None
        val = vs[-2]["value"] if len(vs) > 1 and t._mode("stale") else latest["value"]
        t.cur["sources"].append({"type": "frag", "key": kstr(key), "v": latest["v"], "frag": t.w.fsrc(latest["fid"])}); return val

    # ── HR ──
    def hr_profile(t, e):
        r = t.w.emps[e]["region"]; g = f"HR-{r}"; t.begin(f"{g}/{e}/profile", g, "records")
        p = t.db((g, "emp", e, "profile"))
        if p is None: raise Skip
        return p
    def hr_transfer(t, e):
        r = t.w.emps[e]["region"]; g = f"HR-{r}"; t.begin(f"{g}/{e}/assignment_timeline", g, "records")
        p = t.db((g, "emp", e, "profile")); tr = t.db((g, "emp", e, "transfer")); t.rule(f"{g}.transfer_effective_day")
        if p is None: raise Skip
        pend = tr if tr and tr["status"] == "approved" else None
        return {"dept": p["dept"], "to": pend["to"] if pend else None, "eff": pend["effective"] if pend else None,
                "contract": p["contract"], "grade": p["grade"], "status": p["status"]}
    def hr_dept_on(t, e, day):
        x = t.hr_transfer(e)
        return x["to"] if x["to"] and day >= x["eff"] else x["dept"]
    def hr_headcount(t, r, dept, excl_contract=False):
        g = f"HR-{r}"; t.begin(f"{g}/{dept}/headcount" + ("-regular" if excl_contract else ""), g, "records")
        t.cur["sources"].append({"type": "db", "key": f"{g}/roster", "v": 0}); n = 0
        for e in sorted(t.w.emps):
            if t.w.emps[e]["region"] != r: continue
            key = (g, "emp", e, "profile"); vs = [v for v in t.w.db.get(key, []) if v["day"] <= t.day]
            if not vs: continue
            vis = [v for v in vs if v["db_day"] <= t.day]
            rel = vs[-1]["value"]["dept"] == dept or (vis and vis[-1]["value"]["dept"] == dept)
            if not rel: continue
            val = vs[-1]["value"] if vs[-1]["db_day"] <= t.day else t.db(key)
            if val and val["status"] == "active" and val["dept"] == dept and not (excl_contract and val["contract"] == "contractor"): n += 1
        return n
    # ── FIN ──
    def fin_region(t, r, dept):
        for x in t.w.owner_exc:
            if x["dept"] == dept and x["from"] == r and x["start"] <= t.day <= x["end"]:
                if t._mode("wrong_owner"): return r
                t.frag(x["fid"], droppable=False); t.rule(f"FIN-{r}.owner_exception"); return x["to"]
        return r
    def commit_state(t, c):
        key = (c["group"], "commit", c["cid"], "status"); vs = [v for v in t.w.db.get(key, []) if v["day"] <= t.day]
        if vs:
            if vs[-1]["value"]["status"] in ("settled", "cancelled") and vs[-1]["db_day"] <= t.day: return vs[-1]["value"]
            return t.db(key)
        if c["review_day"] <= t.day and t.frag(c["review_fid"]):
            return {"status": "reviewing", "amount": c["amount"], "expected_settle": c["expected_settle"]}
        return None
    def fin_schedule(t, r, dept):
        g0 = f"FIN-{r}"; t.begin(f"{g0}/{dept}/budget_schedule", g0, "budgeting")
        rr = t.fin_region(r, dept); g = f"FIN-{rr}"
        if t._mode("neardup"): dept = t.w.sibling(r, dept)
        rem = t.db((g, "line", dept, "remaining")); t.rule(f"{g}.rule4.2_reviewing_deducted")
        if rem is None: raise Skip
        pend = []
        for cid in sorted(t.w.commits):
            c = t.w.commits[cid]
            if c["group"] != g or c["dept"] != dept or c["review_day"] > t.day: continue
            st = t.commit_state(c)
            if st and st["status"] in ("reviewing", "pending"): pend.append((st["amount"], st["expected_settle"]))
        return rem, pend
    def fin_available(t, r, dept):
        rem, pend = t.fin_schedule(r, dept); return rem - sum(a for a, _ in pend)
    def fin_reset(t, r, dept):
        g = f"FIN-{r}"; t.begin(f"{g}/{dept}/next_reset", g, "budgeting"); t.rule(f"{g}.reset_calendar")
        return next((d for d in RESET_DAYS if d > t.day), None), t.db((g, "line", dept, "base"))
    def fin_approval(t, r, amount, prof, dept):
        g = f"FIN-{r}"; t.begin(f"{g}/approval", g, "budgeting"); R = t.w.rules[r]; t.rule(f"{g}.approval_tiers")
        appr, gov = next(n for lim, n in R["tiers"] if amount <= lim), "tiers"
        if t.day - prof["hire_day"] <= R["newcomer_days"] and amount <= R["newcomer_cap"]:
            t.rule(f"{g}.newcomer_waiver"); appr, gov = "팀장", "newcomer_waiver"
        for q in t.w.q_exc:
            if q["region"] == r and q["dept"] == dept and q["start"] <= t.day <= q["end"] and amount > q["threshold"]:
                if t.frag(q["fid"]): appr, gov = "본부장", "q_exception"
        return appr, gov
    # ── IT ──
    def it_tier(t, r, grade):
        g = f"IT-{r}"; t.begin(f"{g}/eligibility", g, "access"); t.rule(f"{g}.eligibility"); return t.w.rules[r]["elig"][grade]
    def it_inventory(t, r, itype):
        g = f"IT-{r}"; t.begin(f"{g}/inventory/{itype}", g, "assets"); out = []
        for iid in sorted(t.w.inv):
            x = t.w.inv[iid]
            if x["region"] != r or x["type"] != itype: continue
            q = t.db((g, "inv", iid, "qty"))
            if q and q > 0: out.append({"id": iid, "tier": x["tier"], "cost": x["cost"], "country": r, "lead": 0, "excluded": False, "vendor": None})
        return out
    def it_assets(t, e):
        r = t.w.emps[e]["region"]; g = f"IT-{r}"; t.begin(f"{g}/{e}/assets", g, "assets"); out = []
        for aid in sorted(t.w.assets):
            if e in t.w.assets[aid]["history"]:
                v = t.db((g, "asset", aid, "holder"))
                if v and v.get("emp") == e: out.append(aid)
        return out
    def it_free(t, r, sw):
        g = f"IT-{r}"; t.begin(f"{g}/license/{sw}", g, "licenses"); v = t.db((g, "lic", sw, "seats")); return v["seats"] - v["used"]
    def it_seat_price(t, r):
        g = f"IT-{r}"; t.begin(f"{g}/seat_price", g, "licenses"); t.rule(f"{g}.seat_price"); return t.w.rules[r]["seat_price"]
    # ── PROC ──
    def proc_quotes(t, regions, itype):
        out = []
        for r in regions:
            g = f"PROC-{r}"; t.begin(f"{g}/quotes/{itype}", g, "buying"); ex = set()
            for x in t.w.exclusions:
                if x["region"] == r and x["start"] <= t.day <= x["end"] and t.frag(x["fid"]): ex.add(x["vendor"])
            for qid in sorted(t.w.quotes):
                q = t.w.quotes[qid]
                if q["region"] != r or q["type"] != itype: continue
                v = t.w.vendors[q["vendor"]]
                out.append({"id": qid, "vendor": q["vendor"], "tier": q["tier"], "cost": t.db((g, "quote", qid, "amount")),
                            "lead": t.db((g, "vendor", q["vendor"], "lead")), "country": v["country"], "excluded": q["vendor"] in ex, "registered": v["registered"]})
        return out
    def proc_seat_price(t, r, sw):
        g = f"PROC-{r}"; t.begin(f"{g}/seat_price/{sw}", g, "buying"); return t.db((g, "seatprice", sw, "amount"))
    def proc_receipt(t, r, cid):
        g = f"PROC-{r}"; t.begin(f"{g}/receipt/{cid}", g, "receiving"); return bool(t.db((g, "receipt", cid, "received")))
    def proc_price_notice(t, r, itype, on_day):
        g = f"PROC-{r}"; t.begin(f"{g}/price_notice/{itype}", g, "buying"); pct = 0
        for n in t.w.price_notices:
            if n["region"] == r and n["type"] == itype and n["from"] <= on_day and t.frag(n["fid"]): pct = n["pct"]
        return pct
    def proc_vendor_registered(t, r, vid):
        g = f"PROC-{r}"; t.begin(f"{g}/vendor/{vid}/registration", g, "vendors"); t.rule(f"{g}.vendor_onboarding"); return t.w.vendors[vid]["registered"]
    # ── LEGAL ──
    def legal_terms(t, e):
        r = t.w.emps[e]["region"]; g = f"LEGAL-{r}"; t.begin(f"{g}/{e}/contract", g, "contracts")
        terms = t.db((g, "contract", e, "terms")); t.rule(f"{g}.contractor_policy"); ov = None
        for o in t.w.overrides:
            if o["emp"] == e and o["start"] <= t.day <= o["end"] and t.frag(o["fid"]): ov = o
        return terms, ov
    def legal_residency(t, r):
        g = f"LEGAL-{r}"; t.begin(f"{g}/residency", g, "privacy"); t.rule(f"{g}.residency"); return t.w.rules[r]["restricted"]
    def legal_sw_block(t, r, sw):
        g = f"LEGAL-{r}"; t.begin(f"{g}/sw_contractor/{sw}", g, "compliance"); t.rule(f"{g}.sw_contractor"); return sw in t.w.rules[r]["sw_contractor_block"]


def legal_gate(terms, ov, tier):
    if terms is None: return "ok"
    if tier == "premium" or TIER_RANK[tier] > TIER_RANK[terms["allowed_tier"]]: return "override" if ov else "deny"
    return "nda" if (tier == "standard" and terms["nda"]) else "ok"


# ═════════════════════════════ 추론 템플릿 ═════════════════════════════
# 각 템플릿: root 도메인, 핵심 도메인(없으면 꺼짐), 확장 제약(도메인이 활성이면 확률로 붙음), 샘플러, 정답 함수, 문장
def pick_emp(w, r, rr, contractor=None, transfer=False):
    es = w.active_emps(r)
    if contractor is not None: es = [e for e in es if (w.cur((f"HR-{r}", "emp", e, "profile"))["contract"] == "contractor") == contractor]
    if transfer:
        tr = [e for e in es if (w.cur((f"HR-{r}", "emp", e, "transfer")) or {}).get("status") == "approved"]
        if tr and rr.random() < 0.75: es = tr
    if not es: raise Skip
    return rr.choice(es)

def s_purchase(w, rr, p):
    p["emp"] = pick_emp(w, p["r"], rr, contractor=True if ("contract" in p["ext"] and rr.random() < 0.6) else None)
    p["itype"] = rr.choice(list(ITEM_TYPES)); p["xregion"] = rr.random() < 0.4
def g_purchase(t, p):
    e, r = p["emp"], p["r"]; prof = t.hr_profile(e); dept = t.hr_dept_on(e, t.day)
    avail = t.fin_available(r, dept); tmax = t.it_tier(r, prof["grade"])
    cands = t.proc_quotes([r] + (t.w.other_regions(r)[:1] if p.get("xregion") else []), p["itype"]) if "proc" in p["ext"] else t.it_inventory(r, p["itype"])
    restricted = t.legal_residency(r) if "residency" in p["ext"] else []
    terms = ov = None
    if "contract" in p["ext"] and prof["contract"] == "contractor": terms, ov = t.legal_terms(e)
    first = None
    for c in sorted(cands, key=lambda c: (c["cost"], c["id"])):
        f = []
        if c["cost"] > avail: f.append("budget")
        if TIER_RANK[c["tier"]] > TIER_RANK[tmax]: f.append("eligibility")
        if c["excluded"]: f.append("vendor_excluded")
        if c["lead"] > 7: f.append("lead_time")
        if dept in restricted and c["country"] != r: f.append("residency")
        if legal_gate(terms, ov, c["tier"]) == "deny": f.append("contract")
        if not f:
            appr, gov = t.fin_approval(r, c["cost"], prof, dept)
            return {"decision": "order" if "proc" in p["ext"] else "assign", "option": c["id"], "approver": appr,
                    "nda": legal_gate(terms, ov, c["tier"]) == "nda", "budget_after": avail - c["cost"]}
        first = first or f[0]
    return {"decision": "none", "blocked_by": first or "no_candidate"}

def s_precedence(w, rr, p):
    p["emp"] = pick_emp(w, p["r"], rr, contractor=True if ("contract" in p["ext"] and rr.random() < 0.6) else None)
    p["itype"] = rr.choice(list(ITEM_TYPES)); p["tier"] = rr.choice(ITEM_TYPES[p["itype"]]); p["amount"] = w.canary(*PRICE[p["tier"]])
def g_precedence(t, p):
    e, r = p["emp"], p["r"]; prof = t.hr_profile(e); dept = t.hr_dept_on(e, t.day)
    appr, gov = t.fin_approval(r, p["amount"], prof, dept); it_exc = TIER_RANK[p["tier"]] > TIER_RANK[t.it_tier(r, prof["grade"])]
    if "contract" in p["ext"] and prof["contract"] == "contractor":
        terms, ov = t.legal_terms(e); gate = legal_gate(terms, ov, p["tier"])
        if gate == "deny": return {"approver": "불가", "governing_rule": "contract_deny", "it_exception": it_exc}
        if gate == "override": return {"approver": "법무+본부장", "governing_rule": "legal_override", "it_exception": it_exc}
    return {"approver": appr, "governing_rule": gov, "it_exception": it_exc}

def s_temporal(w, rr, p):
    p["emp"] = pick_emp(w, p["r"], rr, transfer=True); p["amount"] = w.canary(700_000, 2_400_000); p["itype"] = rr.choice(list(ITEM_TYPES)); p["horizon"] = 20
def g_temporal(t, p):
    e, r = p["emp"], p["r"]; x = t.hr_transfer(e)
    depts = [x["dept"]] + ([x["to"]] if x["to"] else []); sched = {d: t.fin_schedule(r, d) for d in depts}
    lead, expiry = 0, None
    if "proc" in p["ext"]:
        ok = [q for q in t.proc_quotes([r], p["itype"]) if not q["excluded"]]
        if ok: lead = min(ok, key=lambda q: (q["cost"], q["id"]))["lead"]
    if "contract" in p["ext"] and x["contract"] == "contractor":
        terms, _ = t.legal_terms(e); expiry = terms["expiry"] if terms else None
    for d in range(t.day, t.day + p["horizon"] + 1):
        dep = x["to"] if x["to"] and d >= x["eff"] else x["dept"]; rem, pend = sched[dep]
        if p["amount"] <= rem - sum(a for a, s in pend if s > d) and (expiry is None or d + lead <= expiry):
            return {"budget_dept": dep, "earliest_day": d}
    return {"budget_dept": None, "earliest_day": None}

def s_alloc(w, rr, p):
    p["sw"] = rr.choice(SOFTWARE); p["teams"] = rr.sample(DEPTS[p["r"]], 3)
def g_alloc(t, p):
    r = p["r"]; free = t.it_free(r, p["sw"])
    excl = "contract" in p["ext"] and t.legal_sw_block(r, p["sw"])
    need = [t.hr_headcount(r, d, excl_contract=excl) for d in p["teams"]]
    short = max(0, sum(need) - free); transfer = 0
    if short > 0 and t.w.other_regions(r):
        of = t.it_free(t.w.other_regions(r)[0], p["sw"]); transfer = min(short, max(0, of) // 2); short -= transfer
    buy = 0
    if short > 0:
        avail = t.fin_available(r, p["teams"][0]); price = t.proc_seat_price(r, p["sw"]) if "proc" in p["ext"] else t.it_seat_price(r)
        buy = min(short, max(0, avail) // price)
    pool, alloc = free + transfer + buy, []
    for n in need: a = min(n, pool); alloc.append(a); pool -= a
    return {"alloc": alloc, "transfer": transfer, "buy": buy, "unmet": sum(need) - sum(alloc)}

def s_diag(w, rr, p):
    r = p["r"]; cs = sorted(c for c, x in w.commits.items() if x["group"] == f"FIN-{r}" and x["review_day"] <= w.day)
    if not cs: raise Skip
    c = w.commits[rr.choice(cs)]; es = sorted(e for e in w.emps if w.emps[e]["region"] == r); e = rr.choice(es)
    mine = sorted(a for a, x in w.assets.items() if e in x["history"]); allr = sorted(a for a, x in w.assets.items() if x["region"] == r)
    p.update({"cid": c["cid"], "emp": e, "asset": rr.choice(mine) if mine and rr.random() < 0.7 else rr.choice(allr),
              "amount": c["amount"] if rr.random() < 0.75 else c["amount"] + rr.choice([-1, 1]) * rr.randint(10_000, 90_000),
              "vendor": rr.choice(sorted(v for v, x in w.vendors.items() if x["region"] == r)) if w.has("PROC") else None, "inv": w.newid("INV")})
DIAG_ORDER = ["EMP_EXITED", "ASSET_NOT_REGISTERED", "RECEIPT_MISSING", "VENDOR_EXCLUDED", "CONTRACT_EXPIRED", "COMMIT_CANCELLED", "COMMIT_NOT_CONFIRMED", "AMOUNT_MISMATCH"]
def g_diag(t, p):
    r, e, c = p["r"], p["emp"], t.w.commits[p["cid"]]; fail = set()
    t.begin(f"FIN-{r}/{c['cid']}/status", c["group"], "payables"); st = t.commit_state(c)
    if st is None or st["status"] == "reviewing": fail.add("COMMIT_NOT_CONFIRMED")
    elif st["status"] == "cancelled": fail.add("COMMIT_CANCELLED")
    if st and st["amount"] != p["amount"]: fail.add("AMOUNT_MISMATCH")
    prof = t.hr_profile(e)
    if prof["status"] != "active": fail.add("EMP_EXITED")
    if p["asset"] not in t.it_assets(e): fail.add("ASSET_NOT_REGISTERED")
    if "proc" in p["ext"]:
        if not t.proc_receipt(r, c["cid"]): fail.add("RECEIPT_MISSING")
        t.begin(f"PROC-{r}/vendor/{p['vendor']}/status", f"PROC-{r}", "vendors")
        if any(x["vendor"] == p["vendor"] and x["start"] <= t.day <= x["end"] and t.frag(x["fid"]) for x in t.w.exclusions): fail.add("VENDOR_EXCLUDED")
    if "contract" in p["ext"] and prof["contract"] == "contractor":
        terms, _ = t.legal_terms(e)
        if terms and terms["expiry"] < t.day: fail.add("CONTRACT_EXPIRED")
    return {"cause": next((k for k in DIAG_ORDER if k in fail), "OK")}

def s_conflict(w, rr, p):
    r = p["r"]; cs = [c for c, x in w.commits.items() if x["group"] == f"FIN-{r}" and x["review_day"] <= w.day and w.day - x["review_day"] <= 14]
    if not cs: raise Skip
    talk = [c for c in cs if w.commits[c]["talk_fid"]]; p["cid"] = rr.choice(sorted(talk if talk and rr.random() < 0.6 else cs))
def g_conflict(t, p):
    r, c = p["r"], t.w.commits[p["cid"]]; t.begin(f"FIN-{r}/{c['cid']}/effective_status", c["group"], "payables")
    st = t.commit_state(c); t.rule(f"{c['group']}.status_authority")
    if c["talk_fid"]: t.frag(c["talk_fid"], droppable=False)            # 비권위 발언: 읽고 배제해야 함
    if st is None: return {"status": "none", "amount": 0}
    status = st["status"]
    if "proc" in p["ext"] and status == "cancelled" and t.proc_receipt(r, c["cid"]): status = "pending"   # 입고 후 취소 무효
    return {"status": status, "amount": st["amount"] if status in ("reviewing", "pending") else 0}

def s_whatif(w, rr, p):
    p["emp"] = pick_emp(w, p["r"], rr); p["itype"] = rr.choice(list(ITEM_TYPES))
    t = TW(w, "none"); dept = t.hr_dept_on(p["emp"], w.day); now = t.fin_available(p["r"], dept)
    rd, base = t.fin_reset(p["r"], dept)
    if rd is None or base is None: raise Skip
    _, pend = t.fin_schedule(p["r"], dept); then = base - sum(a for a, s in pend if s > rd)
    anchor = rr.choice([now, then, then]); p["amount"] = max(300_000, anchor + rr.choice([-1, 1]) * rr.randint(40_000, 500_000))
def g_whatif(t, p):
    e, r = p["emp"], p["r"]; dept = t.hr_dept_on(e, t.day); now = t.fin_available(r, dept)
    rd, base = t.fin_reset(r, dept)
    if rd is None or base is None: raise Skip
    _, pend = t.fin_schedule(r, dept); then = base - sum(a for a, s in pend if s > rd)
    amt = p["amount"]
    if "proc" in p["ext"]: amt = amt * (100 + t.proc_price_notice(r, p["itype"], rd)) // 100
    return {"now": p["amount"] <= now, "later": amt <= then, "available_then": then}

def s_plan(w, rr, p, follow=None):
    if follow: p.update(follow); return
    p["emp"] = pick_emp(w, p["r"], rr, contractor=True if ("contract" in p["ext"] and rr.random() < 0.6) else None)
    p["itype"] = rr.choice(list(ITEM_TYPES)); p["tier"] = rr.choice(ITEM_TYPES[p["itype"]]); p["amount"] = w.canary(*PRICE[p["tier"]])
    p["vendor"] = rr.choice(sorted(v for v, x in w.vendors.items() if x["region"] == p["r"])) if w.has("PROC") else None
def g_plan(t, p):
    e, r = p["emp"], p["r"]; prof = t.hr_profile(e); dept = t.hr_dept_on(e, t.day); steps = []
    if TIER_RANK[p["tier"]] > TIER_RANK[t.it_tier(r, prof["grade"])]: steps.append("IT_EXCEPTION")
    if "contract" in p["ext"] and prof["contract"] == "contractor":
        terms, ov = t.legal_terms(e); gate = legal_gate(terms, ov, p["tier"])
        if gate == "deny": return {"steps": ["BLOCKED_CONTRACT"]}
        if gate in ("nda", "override"): steps.append("LEGAL_" + gate.upper())
    appr, _ = t.fin_approval(r, p["amount"], prof, dept); steps.append(f"FIN_{appr}")
    if p.get("vendor") and "proc" in p["ext"] and not t.proc_vendor_registered(r, p["vendor"]): steps.append("PROC_VENDOR_ONBOARD")
    return {"steps": steps}

def s_vendor(w, rr, p):
    p["dept"] = rr.choice(DEPTS[p["r"]]); p["itype"] = rr.choice(list(ITEM_TYPES)); p["xregion"] = rr.random() < 0.5
def g_vendor(t, p):
    r = p["r"]; avail = t.fin_available(r, p["dept"]); qs = t.proc_quotes([r] + (t.w.other_regions(r)[:1] if p["xregion"] else []), p["itype"])
    restricted = t.legal_residency(r) if "residency" in p["ext"] else []; first = None
    for q in sorted(qs, key=lambda q: (q["cost"], q["id"])):
        f = [k for k, bad in [("budget", q["cost"] > avail), ("vendor_excluded", q["excluded"]), ("lead_time", q["lead"] > 10),
                              ("residency", p["dept"] in restricted and q["country"] != r)] if bad]
        if not f:
            appr, _ = t.fin_approval(r, q["cost"], {"hire_day": -999}, p["dept"])
            return {"vendor": q["vendor"], "option": q["id"], "amount": q["cost"], "approver": appr, "budget_after": avail - q["cost"]}
        first = first or f[0]
    return {"vendor": None, "blocked_by": first or "no_candidate"}

def s_renewal(w, rr, p):
    r = p["r"]; cs = [e for e in w.contractors(r) if w.day - 10 <= w.cur((f"LEGAL-{r}", "contract", e, "terms"))["expiry"] <= w.day + 40]
    if not cs: raise Skip
    p["emp"] = rr.choice(cs); p["cost"] = w.canary(200_000, 1_400_000)
def g_renewal(t, p):
    e, r = p["emp"], p["r"]; t.legal_terms(e)                              # root LEGAL (로컬)
    prof = t.hr_profile(e); dept = t.hr_dept_on(e, t.day); avail = t.fin_available(r, dept); assets = t.it_assets(e)
    ok = prof["status"] == "active" and prof["grade"] >= 2 and p["cost"] <= avail
    return {"renew": ok, "recover_assets": [] if ok else assets}

def s_lookup(w, rr, p): p["emp"] = pick_emp(w, p["r"], rr)
def g_lookup(t, p):
    prof = t.hr_profile(p["emp"]); return {"dept": prof["dept"], "grade": prof["grade"], "assets": t.it_assets(p["emp"])}

EXT = {"proc": "PROC", "residency": "LEGAL", "contract": "LEGAL"}
TEMPLATES = {
    #  이름: (root 도메인(함수), root 역할, 추론 유형, 핵심 도메인, 확장 제약, 가중치, 샘플러, 정답, 문장)
    "purchase":   (lambda w: "HR", "payroll", "constraint", {"HR", "IT", "FIN"}, ["proc", "residency", "contract"], .16, s_purchase, g_purchase,
                   "{alias} {itype} 건, 조건 맞는 것 중 제일 싼 걸로 처리 가능한지랑 누구 승인까지 필요한지 알려줘."),
    "precedence": (lambda w: "IT", "access", "rule", {"HR", "IT", "FIN"}, ["contract"], .12, s_precedence, g_precedence,
                   "{alias} {itype}({tier}) {amount:,}원 요청 들어왔어. 승인 절차 어떻게 되는지, 어느 규정 때문인지 판단해 줘."),
    "temporal":   (lambda w: "IT", "assets", "temporal", {"HR", "IT", "FIN"}, ["proc", "contract"], .11, s_temporal, g_temporal,
                   "{alias} 장비 {amount:,}원, 인사 변동 감안해서 어느 부서 예산으로 며칠부터 집행 가능한지 봐줘."),
    "alloc":      (lambda w: "IT", "licenses", "allocation", {"HR", "IT", "FIN"}, ["proc", "contract"], .10, s_alloc, g_alloc,
                   "{sw} 좌석 {teams[0]}, {teams[1]}, {teams[2]} 순으로 필요한 만큼 나눠 줘. 모자라면 다른 지역에서 당기고, 그래도 모자라면 예산 내에서 사고."),
    "diag":       (lambda w: "FIN", "payables", "diagnosis", {"HR", "IT", "FIN"}, ["proc", "contract"], .10, s_diag, g_diag,
                   "{inv} 인보이스({amount:,}원, 수혜자 {alias}, 자산 {asset}, 가승인 {cid}) 매칭이 안 돼. 원인 찾아줘."),
    "conflict":   (lambda w: "PROC" if w.has("PROC") else "HR", "buying", "conflict", {"FIN"}, ["proc"], .09, s_conflict, g_conflict,
                   "{cid} 건 지금 살아 있는 건지, 얼마로 봐야 하는지 확인해 줘. 얘기가 엇갈려서."),
    "whatif":     (lambda w: "HR", "payroll", "counterfactual", {"HR", "FIN"}, ["proc"], .08, s_whatif, g_whatif,
                   "{alias} {itype} {amount:,}원 지금 바로 되는지, 안 되면 다음 예산 재설정 뒤엔 되는지 봐줘."),
    "plan":       (lambda w: "PROC" if w.has("PROC") else "IT", "buying", "plan", {"HR", "IT", "FIN"}, ["proc", "contract"], .08, s_plan, g_plan,
                   "{alias} {itype}({tier}) {amount:,}원 진행 전에 받아야 할 승인을 순서대로 정리해 줘."),
    "vendor":     (lambda w: "PROC", "buying", "constraint", {"PROC", "FIN"}, ["residency"], .07, s_vendor, g_vendor,
                   "{dept} {itype} 필요한데 예산 안에서 규정 맞는 공급사 골라 줘."),
    "renewal":    (lambda w: "LEGAL", "contracts", "rule", {"LEGAL", "HR", "FIN", "IT"}, [], .06, s_renewal, g_renewal,
                   "{alias} 계약 만료 다가오는데 연장 가능한지, 안 되면 회수할 자산 정리해 줘."),
    "lookup":     (lambda w: "FIN", "closing", "lookup", {"HR", "IT", "FIN"}, [], .07, s_lookup, g_lookup,
                   "{alias} 현재 소속, 직급, 보유 자산 확인해 줘."),
}


def classify(w, needs):
    """need 상태 등급: A card 대상 한 명(또는 DB)로 충분 / B 한 명이 갖지만 card 대상 아님 / C 둘 이상 합쳐야 함 / D 누구의 창에도 없음."""
    out = []
    for n in needs:
        if n["local"]: n["class"] = None; continue
        comps = [s["frag"] for s in n["sources"] if s["type"] == "frag"]
        live = [set(x["agent"] for x in c["holders"] if x["in_window"] and x["active"]) for c in comps]
        if not comps: cl = "A"
        elif any(not L for L in live): cl = "D"
        else:
            inter = set.intersection(*live); cl = "A" if n["card"] in inter else ("B" if inter else "C")
        n["class"] = cl; out.append(cl)
    return max(out, key=lambda c: CLASS_ORDER[c]) if out else None


def gen_cross(w, follow=None):
    rr = w.R("task")
    enabled = {k: v for k, v in TEMPLATES.items() if v[3] <= set(w.domains) and v[0](w) in w.domains}
    names = sorted(enabled)
    for _ in range(40):
        name = "plan" if follow else rr.choices(names, [enabled[k][5] for k in names])[0]
        root_fn, role, family, core, exts, _, sampler, gold_fn, surface = TEMPLATES[name]
        if role not in ROLES[root_fn(w)]: role = ROLES[root_fn(w)][0]
        p = {"r": rr.choice(w.regions), "ext": [x for x in exts if EXT[x] in w.domains and rr.random() < w.P.p_ext]}
        root = f"{root_fn(w)}-{p['r']}"
        try:
            sampler(w, rr, p, follow["params"]) if follow else sampler(w, rr, p)
            if follow: p["r"] = follow["params"]["r"]; p["ext"] = follow["params"]["ext"]; root = f"{root_fn(w)}-{p['r']}"
            t = TW(w, root); gold = gold_fn(t, p)
        except Skip: continue
        needs = t.needs; groups = [root] + [n["group"] for n in needs]
        if all(n["local"] for n in needs): continue
        seqd = [g for i, g in enumerate(groups) if i == 0 or g != groups[i - 1]]
        cls0 = classify(w, needs); xr = any(g.split("-")[1] != p["r"] for g in groups)
        sig = f"{name}|{','.join(sorted(p['ext']))}|{'>'.join(g.split('-')[0] for g in seqd)}|{cls0}|{'x' if xr else 'l'}"
        if w.sig[sig] >= max(4, int(w.P.tasks * 0.06)) and not follow: continue
        ck = (name, p.get("emp") or p.get("cid") or p.get("dept") or (p.get("sw"), tuple(p.get("teams", []))[:1]))
        if ck in w.cooldown and w.day - w.cooldown[ck] < 5 and not follow: continue
        cfs, cft = {}, {}
        for mode in ("stale", "partial", "neardup", "wrong_owner"):
            cfs[mode] = None
            for k in range(8):
                t2 = TW(w, root, {mode: k})
                try: a = gold_fn(t2, p)
                except Skip: a = "SKIP"
                if mode not in t2.used: break
                if a == "SKIP": continue                      # 비튼 결과 정답 함수가 성립하지 않음 → 이 지점은 제외
                if cfs[mode] is None: cfs[mode], cft[mode] = a, k
                if a != gold: cfs[mode], cft[mode] = a, k; break
        cls = classify(w, needs)
        wid = w.newid("W"); asg = w.assign(root, role, f"{wid}")
        emp = w.emps.get(p.get("emp"), {})
        fmt = {**p, "alias": emp.get("alias", ""), "teams": p.get("teams", ["", "", ""])}
        text = (f"{follow['handle']} 건 후속으로, " if follow else "") + surface.format(**fmt)
        w.work(asg, text); w.sig[sig] += 1; w.cooldown[ck] = w.day
        cross_needs = [n for n in needs if not n["local"]]
        comps = [s for n in cross_needs for s in n["sources"] if s["type"] == "frag"]
        task = {"wid": wid, "day": w.day, "round": w.round, "template": name, "family": family, "root": root, "assignee": asg,
                "assignee_topology": w.groups[root]["topology"], "surface": text, "ext": sorted(p["ext"]), "follows": follow["handle"] if follow else None,
                "gold": gold, "needs": needs, "path": seqd, "n_groups": len(set(groups)), "path_len": len(seqd),
                "revisit": len(seqd) != len(set(seqd)), "domains": sorted({g.split('-')[0] for g in groups}),
                "state_class": cls, "counterfactual": cfs,
                "sensitive": {k: (v is not None and v != gold) for k, v in cfs.items()}, "cf_target_index": cft, "cf_applicable": {k: v is not None for k, v in cfs.items()},
                "n_frag_components": len(comps), "disc_mix": dict(collections.Counter(s["frag"]["disc"] for s in comps)),
                "oracle": {"local_only": False,
                           "db_only": not comps,
                           "card_db": all(n["class"] == "A" for n in cross_needs),
                           "single_holder": all(n["class"] in ("A", "B") for n in cross_needs),
                           "all_history": True},
                "signature": sig}
        w.tasks.append(task); w.log("cross", work=wid, group=root, assignee=asg, template=name, groups=sorted(set(groups)))
        schedule_effects(w, task, p, rr)
        return


def schedule_effects(w, task, p, rr):
    """작업 결과(정답 기준)가 세계에 반영 → 이후 작업은 바뀐 상태에서 샘플링 (상태 매개 결합)."""
    g, n = task["gold"], task["template"]
    if n == "purchase" and g["decision"] in ("assign", "order"):
        w.push(w.day + 1, rr.randint(1, 3), 2, "effect", {"kind": g["decision"], "r": p["r"], "emp": p["emp"], "option": g["option"], "handle": task["wid"]})
        if rr.random() < w.P.p_followup_rate:
            opt = g["option"]; x = w.quotes.get(opt) or w.inv.get(opt)
            w.push(w.day + rr.randint(1, 2), rr.randint(1, 3), 3, "followup", {"handle": task["wid"], "params": {
                "r": p["r"], "emp": p["emp"], "itype": x["type"], "tier": x["tier"], "amount": w.cur((f"PROC-{w.quotes[opt]['region']}", "quote", opt, "amount")) if opt in w.quotes else x["cost"],
                "vendor": w.quotes[opt]["vendor"] if opt in w.quotes else None, "ext": p["ext"]}})
    elif n == "precedence" and g["approver"] != "불가" and rr.random() < w.P.p_followup_rate:
        w.push(w.day + rr.randint(1, 2), rr.randint(1, 3), 3, "followup", {"handle": task["wid"], "params": {
            "r": p["r"], "emp": p["emp"], "itype": p["itype"], "tier": p["tier"], "amount": p["amount"],
            "vendor": sorted(v for v, x in w.vendors.items() if x["region"] == p["r"])[0] if w.has("PROC") else None, "ext": p["ext"]}})
    if n == "vendor" and g.get("vendor"):
        w.push(w.day + 1, rr.randint(1, 3), 2, "effect", {"kind": "order_dept", "r": p["r"], "dept": p["dept"], "amount": g["amount"], "handle": task["wid"]})
    elif n == "alloc" and sum(g["alloc"]) > 0:
        w.push(w.day + 1, rr.randint(1, 3), 2, "effect", {"kind": "seats", "r": p["r"], "sw": p["sw"], "n": sum(g["alloc"]) - g["transfer"] - g["buy"], "handle": task["wid"]})
    elif n == "renewal":
        w.push(w.day + 1, rr.randint(1, 3), 2, "effect", {"kind": "renew" if g["renew"] else "recover", "r": p["r"], "emp": p["emp"], "assets": g["recover_assets"], "handle": task["wid"]})


def apply_effect(w, p):
    rr, r = w.R("effect"), p["r"]
    if p["kind"] == "assign": w.L_IT_assign(f"IT-{r}", r, rr, e=p["emp"], iid=p["option"], handle=p["handle"])
    elif p["kind"] == "order":
        prof = w.cur((f"HR-{r}", "emp", p["emp"], "profile")); q = w.quotes[p["option"]]
        w.commit_review(f"FIN-{r}", r, prof["dept"], w.cur((f"PROC-{q['region']}", "quote", p["option"], "amount")), q["type"], rr, handle=p["handle"])
    elif p["kind"] == "order_dept": w.commit_review(f"FIN-{r}", r, p["dept"], p["amount"], "발주", rr, handle=p["handle"])
    elif p["kind"] == "seats": w.L_IT_license(f"IT-{r}", r, rr, sw=p["sw"], delta=p["n"])
    elif p["kind"] == "renew": w.L_LEGAL_extend(f"LEGAL-{r}", r, rr, e=p["emp"])
    elif p["kind"] == "recover":
        for _ in p["assets"]: w.L_IT_recover(f"IT-{r}", r, rr, only=set(p["assets"]))
    w.counts["effect:" + p["kind"]] += 1


# ═════════════════════════════ 실행 ═════════════════════════════
def run(P):
    w = World(P); w.init()
    for day in range(-P.warmup, P.T + 1):
        w.day = day; w.spawned_today = []
        if day > -P.warmup: w.lifecycle()
        w.schedule_day()
        while w.pq and w.pq[0][0] <= day:
            _, rnd, _, _, typ, payload = heapq.heappop(w.pq); w.round = rnd; w.dispatch(typ, payload)
        for a in w.spawned_today: w.active[a] = False; w.log("despawn", agent=a)
    return w


def stats(w):
    T = w.tasks; N = len(T); C = collections.Counter
    def rate(xs): return round(sum(xs) / max(1, len(xs)), 3)
    win = {"d01-10": (1, 10), "d11-20": (11, 20), "d21-30": (21, 30)}
    comp = [s for t in T for n in t["needs"] if not n["local"] for s in n["sources"] if s["type"] == "frag"]
    return {
        "D": w.P.D, "domains": w.domains, "R": w.P.R, "G": len(w.groups), "seed": w.P.seed, "tasks": N,
        "templates": dict(C(t["template"] for t in T)), "families": dict(C(t["family"] for t in T)),
        "n_groups": dict(sorted(C(t["n_groups"] for t in T).items())), "path_len": dict(sorted(C(t["path_len"] for t in T).items())),
        "revisit_rate": rate([t["revisit"] for t in T]), "ext_count": dict(sorted(C(len(t["ext"]) for t in T).items())),
        "state_class": dict(sorted(C(t["state_class"] for t in T).items())),
        "state_class_by_window": {k: dict(sorted(C(t["state_class"] for t in T if a <= t["day"] <= b).items())) for k, (a, b) in win.items()},
        "oracle_upper_bound": {k: rate([t["oracle"][k] for t in T]) for k in ("db_only", "card_db", "single_holder", "all_history")},
        "card_db_by_window": {k: rate([t["oracle"]["card_db"] for t in T if a <= t["day"] <= b]) for k, (a, b) in win.items()},
        "sensitivity_when_applicable": {m: rate([t["sensitive"][m] for t in T if t["cf_applicable"][m]]) for m in ("stale", "partial", "neardup", "wrong_owner")},
        "cf_applicable_share": {m: rate([t["cf_applicable"][m] for t in T]) for m in ("stale", "partial", "neardup", "wrong_owner")},
        "needs_per_task": round(sum(len(t["needs"]) for t in T) / max(1, N), 2), "frag_components_per_task": round(len(comp) / max(1, N), 2),
        "fragment_kind": dict(C(s["frag"]["kind"] for s in comp)), "fragment_disc": dict(C(s["frag"]["disc"] for s in comp)),
        "assignee_topology": dict(C(t["assignee_topology"] for t in T)), "follow_ups": sum(1 for t in T if t["follows"]),
        "no_ext_subset": {"n": sum(1 for t in T if not t["ext"]), "state_class": dict(sorted(C(t["state_class"] for t in T if not t["ext"]).items())),
                          "card_db": rate([t["oracle"]["card_db"] for t in T if not t["ext"]])},
        "unique_signatures": len(w.sig), "top_signature_share": round(max(w.sig.values()) / max(1, N), 3) if w.sig else 0,
        "timeline_events": len(w.timeline), "timeline_types": dict(C(e["type"] for e in w.timeline)),
        "world_counts": dict(sorted(w.counts.items())),
        "gold_distribution": {k: dict(C(str(t["gold"].get(f))[:14] for t in T if t["template"] == k).most_common(6))
                              for k, f in {"purchase": "decision", "precedence": "governing_rule", "diag": "cause", "whatif": "later", "vendor": "vendor",
                                           "conflict": "status", "renewal": "renew", "plan": "steps", "temporal": "budget_dept"}.items() if any(t["template"] == k for t in T)},
    }


def dump(w, out):
    os.makedirs(out, exist_ok=True)
    init = {"domains": w.domains, "regions": w.regions, "rules": {r: {k: v for k, v in x.items()} for r, x in w.rules.items()},
            "groups": {g: {**{k: v for k, v in G.items() if k != "agents"},
                           "agents": [{"id": a, "role": w.agent_role[a], "card": {"name": f"{g} {w.agent_role[a]}", "description": CARD[w.agent_role[a]]}}
                                      for a in G["agents"] if not a.split(".")[-1].startswith(("w", "n"))]} for g, G in w.groups.items()}}
    json.dump(init, open(f"{out}/world_init.json", "w"), ensure_ascii=False, indent=1, default=str)
    with open(f"{out}/timeline.jsonl", "w") as f:
        for e in w.timeline: f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
    with open(f"{out}/work.jsonl", "w") as f:
        for t in w.tasks: f.write(json.dumps({k: t[k] for k in ("wid", "day", "round", "root", "assignee", "surface", "follows")}, ensure_ascii=False) + "\n")
    with open(f"{out}/gold.jsonl", "w") as f:
        for t in w.tasks: f.write(json.dumps(t, ensure_ascii=False, default=str) + "\n")
    s = stats(w); json.dump(s, open(f"{out}/stats.json", "w"), ensure_ascii=False, indent=1)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7); ap.add_argument("--D", type=int, default=5); ap.add_argument("--R", type=int, default=2)
    ap.add_argument("--T", type=int, default=30); ap.add_argument("--warmup", type=int, default=20); ap.add_argument("--tasks", type=int, default=300)
    ap.add_argument("--K", type=int, default=6000); ap.add_argument("--out", default="out_v3")
    P = ap.parse_args()
    P.db_lag, P.p_cover, P.mu_agent, P.p_handover, P.p_summary_value = (1, 5), 0.2, 0.012, 0.3, 0.5
    P.disc_mix, P.local_per_agent, P.task_overhead, P.p_ext, P.p_followup_rate = [0.4, 0.4, 0.2], 1.2, 260, 0.75, 0.35
    P.swarm = {"IT-TYO", "PROC-SEL"}
    w = run(P); s = dump(w, f"{P.out}/D{P.D}_s{P.seed}")
    print(json.dumps(s, ensure_ascii=False, indent=1))


if __name__ == "__main__": main()
