"""테스트 픽스처 생성기 (결정적, 난수 없음).

    uv run python -m gbg.tests.fixtures.build_fixtures

worldgen_mini  도메인 2(HR, FIN) × 지역 2(SEL, TYO) = 그룹 4, 그룹당 3명, 5일, 교차 작업 10개.
               상태 등급 A·B·C·D, db_pending/operational 조각, 이탈·인수인계, 등록 지연, db_query를 한 번씩 이상 담는다.
silo_mini      에이전트 8명을 그룹 4개로, 전역 질문 2개. 조각은 소유자만 shard.read로 읽는다.

모든 레코드는 계약 모델을 거쳐 쓰므로, 생성 자체가 스키마 검증이다.
"""
import hashlib
import json
from pathlib import Path

from gbg.contracts.card import AgentCard, AgentSkill, GroupCard
from gbg.contracts.schemas import (
    ActivityRecord, DbQuerySource, DbRecord, DbSource, DbVersion, DbWrite, EgressRecord, FragHolder, FragSource,
    GoldRecord, GroupSnapshot, GroupSpec, HistoryEntry, JournalRecord, Manifest, MemberSpec, Need, OutputSchema,
    RenderedToolResult, RuleSource, RuleText, Slot, TimelineEvent, WorldInit,
)

CLASS_ORDER = "ABCD"


def tokens(text):
    return max(12, int(len(text) * 1.1))                # 근사치. 토크나이저 고정은 Stage 3


def dump(model_or_list):
    if isinstance(model_or_list, list):
        return [x.model_dump(mode="json") for x in model_or_list]
    return model_or_list.model_dump(mode="json")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def world_hash(public: Path):
    h = hashlib.sha256()
    for p in sorted(public.rglob("*")):
        if p.is_file() and p.name != "manifest.json":
            h.update(p.relative_to(public).as_posix().encode()); h.update(p.read_bytes())
    return h.hexdigest()[:16]


class Histories:
    """에이전트별 이력 누적기."""
    def __init__(self):
        self.h = {}

    def add(self, agent, day, role, text, entities, digest):
        hist = self.h.setdefault(agent, [])
        e = HistoryEntry(seq=len(hist) + 1, day=day, role=role, text=text, tokens=tokens(text), entities=entities, digest=digest)
        hist.append(e)
        return e.seq

    def work(self, agent, day, task, result, entities, digest):
        """워밍업 작업 하나 = 과제(user) + 처리 결과(assistant). 색인은 결과 항목을 가리킨다."""
        self.add(agent, day, "user", "[작업] " + task, entities, digest)
        return self.add(agent, day, "assistant", result, entities, digest)


# ═════════════════════════════ worldgen_mini ═════════════════════════════
REGIONS = ["SEL", "TYO"]
ROLES = {"HR": ["records", "records", "payroll"], "FIN": ["budgeting", "budgeting", "payables"]}
ROLE_DESC = {"records": ("인사기록", "직원 소속·직급·계약 유형 기록 조회와 갱신"),
             "payroll": ("급여", "급여 등급, 장비 지원 판단"),
             "budgeting": ("예산", "예산 라인 편성·조정·잔액 조회"),
             "payables": ("지급", "가승인 검토·등록, 정산")}
GROUP_DESC = {"HR": "인사: 직원 소속·직급·계약 기록과 급여", "FIN": "재무: 예산 라인, 가승인, 정산"}
DEPTS = {"SEL": ["영업1팀", "개발1팀"], "TYO": ["営業1課", "開発1課"]}
EMPS = {  # id: (이름, 별칭, 부서 index, 직급, 계약)
    "E-SEL-1000": ("김하린", "하린 과장", 0, 3, "regular"),
    "E-SEL-1001": ("박도윤", "도윤 대리", 1, 2, "contractor"),
    "E-SEL-1002": ("이서준", "서준 선임", 0, 4, "regular"),
    "E-SEL-1003": ("최지우", "지우 과장", 1, 1, "regular"),
    "E-TYO-1000": ("佐藤結衣", "佐藤さん", 0, 3, "regular"),
    "E-TYO-1001": ("小野健", "小野さん", 1, 2, "regular"),
    "E-TYO-1002": ("田中翔", "田中さん", 0, 5, "contractor"),
    "E-TYO-1003": ("高橋美咲", "高橋さん", 1, 2, "regular"),
}
LINES = {("SEL", 0): 3_120_400, ("SEL", 1): 2_874_300, ("TYO", 0): 4_051_700, ("TYO", 1): 3_366_200}
LOOKUP = OutputSchema(slots=[Slot(name="dept", type="id"), Slot(name="grade", type="number")])
BUDGET = OutputSchema(slots=[Slot(name="decision", type="enum", options=["approve", "insufficient"]),
                             Slot(name="available", type="number")])


def agent_id(group, i):
    return f"{group.lower()}.a{i + 1}"


def region_of(e):
    return e.split("-")[1]


def profile(e, dept=None, grade=None):
    name, _, d, g, contract = EMPS[e]
    return {"dept": dept or DEPTS[region_of(e)][d], "grade": grade or g, "contract": contract, "status": "active"}


def records_agent(e):
    """specialist 고정 담당: 엔티티 번호로 같은 역할 두 명 중 하나."""
    return agent_id(f"HR-{region_of(e)}", int(e[-1]) % 2)


def budgeting_agent(region, d):
    return agent_id(f"FIN-{region}", d)


def build_worldgen(out: Path):
    groups = [f"{d}-{r}" for d in ("HR", "FIN") for r in REGIONS]

    # ── 그룹 명세와 card ──
    specs = []
    for g in groups:
        dom, reg = g.split("-")
        members = []
        for i, role in enumerate(ROLES[dom]):
            label, desc = ROLE_DESC[role]
            skill = AgentSkill(id=role, name=label, description=desc, tags=[dom.lower(), role], examples=[])
            scope = f"{reg} {label}" if ROLES[dom].count(role) == 1 else f"{reg} {DEPTS[reg][i]} {label}"
            members.append(MemberSpec(agent_id=agent_id(g, i), role=role, card=AgentCard(
                name=f"{g} {label}", description=desc, version=1, skills=[skill], group=g, scope=scope,
                occupant=agent_id(g, i))))
        skills = list({m.role: m.card.skills[0] for m in members}.values())
        specs.append(GroupSpec(id=g, members=members, card=GroupCard(
            name=g, description=GROUP_DESC[dom], version=1, skills=skills, group=g,
            service_scope=f"{reg} 지역 {', '.join(DEPTS[reg])}", endpoint=f"boundary:{g}")))

    # ── 규정 (본문 공개, 파라미터 비공개) ──
    rules, params = [], {}
    for r in REGIONS:
        rules.append(RuleText(id=f"HR-{r}.transfer_effective", group=f"HR-{r}",
                              body="부서 이동은 발효일부터 소속에 반영한다. 발효 전에는 이전 부서 소속이다."))
        params[f"HR-{r}.transfer_effective"] = {"effective_inclusive": True}
        rules.append(RuleText(id=f"FIN-{r}.pending_deducted", group=f"FIN-{r}",
                              body="집행 가능액은 예산 라인 잔액에서 검토 중이거나 확정 대기인 가승인 합계를 뺀 값이다."))
        params[f"FIN-{r}.pending_deducted"] = {"deduct_status": ["reviewing", "pending"]}

    # ── 워밍업 (0일 이하): DB, 이력, 색인 ──
    H = {g: Histories() for g in groups}
    db = {g: {} for g in groups}
    journal = {g: [] for g in groups}
    activity = {g: [] for g in groups}

    def put(g, key, day, db_day, value):
        vs = db[g].setdefault(key, [])
        vs.append(DbVersion(v=len(vs) + 1, day=day, db_day=db_day, value=value))
        return len(vs)

    for e, (name, alias, d, grade, contract) in EMPS.items():
        g, a = f"HR-{region_of(e)}", records_agent(e)
        p = profile(e)
        put(g, f"{g}/emp/{e}/profile", -5, -5, p)
        seq = H[g].work(a, -5, f"{name} 인사 기록 확인", f"{name} 인사 기록 확정: {p['dept']}, {grade}급, {contract}.",
                        [e], f"-5일차 {e} 인사 기록 확정 (인사기록 담당)")
        journal[g].append(JournalRecord(entity=e, agent=a, seq=seq))

    for (r, d), v in LINES.items():
        g, a, dept = f"FIN-{r}", budgeting_agent(r, d), DEPTS[r][d]
        put(g, f"{g}/line/{dept}/remaining", -5, -5, v)
        seq = H[g].work(a, -5, f"{dept} 예산 라인 확인", f"{dept} capex 잔액 {v:,}원 확정.", [dept],
                        f"-5일차 {dept} 예산 잔액 확정 (예산 담당)")
        journal[g].append(JournalRecord(entity=dept, agent=a, seq=seq))

    # db_pending 조각: 0일차 개발1팀 잔액 조정, DB 등록은 2일차
    put("FIN-SEL", "FIN-SEL/line/개발1팀/remaining", 0, 2, 2_417_900)
    seq = H["FIN-SEL"].work("fin-sel.a2", 0, "개발1팀 예산 조정", "개발1팀 capex 잔액 2,417,900원으로 조정 (본부 재배정). DB 반영은 2일차.",
                            ["개발1팀"], "0일차 개발1팀 예산 조정 (예산 담당)")
    journal["FIN-SEL"].append(JournalRecord(entity="개발1팀", agent="fin-sel.a2", seq=seq))

    # 부서 이동 승인 (db_pending): 0일차 승인, 2일차 등록, 3일차 발효
    put("HR-SEL", "HR-SEL/emp/E-SEL-1001/transfer", 0, 2, {"to": "영업1팀", "effective": 3, "status": "approved"})
    seq = H["HR-SEL"].work("hr-sel.a2", 0, "박도윤 부서 이동 요청 검토", "박도윤 영업1팀 이동 승인, 3일 발효.", ["E-SEL-1001", "영업1팀"],
                           "0일차 E-SEL-1001 부서 이동 승인 (인사기록 담당)")
    activity["HR-SEL"].append(ActivityRecord(entity="E-SEL-1001", agent="hr-sel.a2", seq=seq, day=0, role="records"))

    # operational 조각: 가승인 검토 (DB에 없음, 지급 담당 이력에만)
    commits = {  # cid: (지역, 부서 index, 금액, 검토일, 담당, 발견성)
        "CMT-00001": ("SEL", 0, 612_300, -1, "fin-sel.a3", "H1"),
        "CMT-00002": ("SEL", 1, 455_800, 0, "fin-sel.a3", "H0"),
        "CMT-00003": ("TYO", 1, 389_100, -2, "fin-tyo.a3", "H1"),
    }
    commit_seq = {}
    for cid, (r, d, amt, day, a, disc) in commits.items():
        g, dept = f"FIN-{r}", DEPTS[r][d]
        seq = H[g].work(a, day, f"{dept} 장비 가승인 검토", f"{cid} {dept} 장비 {amt:,}원 가승인 검토 시작, 8일 정산 예정.",
                        [cid, dept], f"{day}일차 {cid} 가승인 검토 시작 (지급 담당)")
        commit_seq[cid] = seq
        if disc == "H0":
            journal[g].append(JournalRecord(entity=cid, agent=a, seq=seq))
        else:
            activity[g].append(ActivityRecord(entity=cid, agent=a, seq=seq, day=day, role="payables"))

    # 워밍업의 정형 그룹 간 교류
    egress = {g: [] for g in groups}
    egress["FIN-SEL"].append(EgressRecord(day=-1, entity="E-SEL-1001", attr="profile", to_group="HR-SEL",
                                          question="도윤 대리 소속 확인 부탁드립니다.", status="ok", referral_to=None))
    egress["HR-SEL"].append(EgressRecord(day=0, entity="개발1팀", attr="available_budget", to_group="FIN-SEL",
                                         question="개발1팀 장비 예산 여유 있는지 확인 부탁드립니다.", status="ok", referral_to=None))

    aliases = {}
    for r in REGIONS:
        al = {e: [EMPS[e][0], EMPS[e][1]] for e in EMPS if region_of(e) == r}
        aliases[r] = al

    # ── 1일차 이후 타임라인 ──
    timeline, work, gold = [], [], []
    seq_counter = iter(range(1, 10_000))
    later_db = []                                            # (day, round, g, key, db_day, value)

    def world(day, rnd, g, action, agent=None, payload=None, entities=()):
        timeline.append(TimelineEvent(eid=f"EV-{len(timeline) + len(work) + 1:04d}", seq=1, day=day, round=rnd, kind="world",
                                      group=g, agent=agent, action=action, payload=payload or {}, entities=list(entities)))

    def db_write(day, rnd, g, key, db_day, value):
        v = put(g, key, day, db_day, value)
        world(day, rnd, g, "db_write", payload=dump(DbWrite(key=key, version=db[g][key][v - 1])))

    def local(day, rnd, g, agent, tid, text, results, entities, schema, answer, disc=None):
        timeline.append(TimelineEvent(eid=f"EV-{len(timeline) + len(work) + 1:04d}", seq=1, day=day, round=rnd, kind="local",
                                      group=g, agent=agent, task_id=tid, text=text,
                                      tool_results=[RenderedToolResult(tool=t, text=x) for t, x in results],
                                      entities=entities, output_schema=schema, payload={"disc": disc} if disc else {}))
        gold.append(GoldRecord(task_id=tid, answer=answer))

    grade_schema = OutputSchema(slots=[Slot(name="grade", type="number")])
    done_schema = OutputSchema(slots=[Slot(name="done", type="bool")])
    status_schema = OutputSchema(slots=[Slot(name="status", type="enum", options=["reviewing", "pending", "settled", "cancelled"])])
    amount_schema = OutputSchema(slots=[Slot(name="remaining", type="number")])

    local(1, 1, "HR-SEL", "hr-sel.a2", "L-001", "지우 과장 직급 조정 요청 반영하고 반영된 직급 알려줘.",
          [("db.query", "E-SEL-1003 profile: 개발1팀, 1급, regular, active"), ("hr.grade_request", "승인된 조정: +1")],
          ["E-SEL-1003"], grade_schema, {"grade": 2})
    db_write(1, 1, "HR-SEL", "HR-SEL/emp/E-SEL-1003/profile", 2, profile("E-SEL-1003", grade=2))
    local(1, 2, "FIN-TYO", "fin-tyo.a1", "L-002", "営業1課 예산 라인 잔액 점검해 줘.",
          [("db.query", "FIN-TYO 営業1課 remaining: 4,051,700")], ["営業1課"], amount_schema, {"remaining": 4_051_700})
    local(2, 1, "FIN-SEL", "fin-sel.a3", "L-003", "CMT-00001 가승인 확정 처리하고 상태 알려줘.",
          [("payables.confirm", "CMT-00001 영업1팀 612,300원 확정 대기 등록")], ["CMT-00001", "영업1팀"], status_schema,
          {"status": "pending"}, disc="H1")
    db_write(2, 1, "FIN-SEL", "FIN-SEL/commit/CMT-00001/status", 3, {"status": "pending", "amount": 612_300, "dept": "영업1팀"})
    world(3, 0, "FIN-SEL", "agent_leave", agent="fin-sel.a3")
    local(3, 1, "HR-SEL", "hr-sel.a2", "L-004", "도윤 대리 부서 이동 발효 처리해 줘.",
          [("db.query", "E-SEL-1001 transfer: 영업1팀, 3일 발효, approved")], ["E-SEL-1001", "영업1팀"], done_schema, {"done": True})
    db_write(3, 1, "HR-SEL", "HR-SEL/emp/E-SEL-1001/profile", 4, profile("E-SEL-1001", dept="영업1팀"))
    world(4, 0, "FIN-SEL", "agent_join", agent="fin-sel.n0001", payload={
        "from": "fin-sel.a3", "role": "payables",
        "handover_notes": ["[인수인계] CMT-00001 영업1팀 가승인 확정 대기, 8일 정산 예정."]},
          entities=["CMT-00001", "영업1팀"])
    local(4, 2, "HR-TYO", "hr-tyo.a3", "L-005", "小野さん 급여 등급 확인해 줘.",
          [("db.query", "E-TYO-1001 profile: 開発1課, 2급, regular, active")], ["E-TYO-1001"], grade_schema, {"grade": 2})
    local(5, 1, "FIN-TYO", "fin-tyo.a2", "L-006", "開発1課 예산 조정 반영하고 조정 후 잔액 알려줘.",
          [("fin.adjust_request", "開発1課 capex 잔액 2,988,600원으로 조정 (분기 이월 반영)")], ["開発1課"], amount_schema,
          {"remaining": 2_988_600}, disc="H0")
    db_write(5, 1, "FIN-TYO", "FIN-TYO/line/開発1課/remaining", 7, 2_988_600)

    # ── 교차 작업 ──
    def holder(agent, raw_window=True, active=True):
        return FragHolder(agent=agent, raw_window=raw_window, digest=True, active=active)

    def hr_need(tid, n, e, day, root):
        """HR 소속 need. 발효됐지만 아직 등록 전인 이동은 db_pending 조각."""
        g = f"HR-{region_of(e)}"; key = f"{g}/emp/{e}/profile"
        vs = db[g][key]
        latest = [x for x in vs if x.day <= day][-1]
        card = agent_id(g, 0)
        if latest.db_day <= day:
            src, cls = DbSource(key=key, v=latest.v, canary=None), "A"
        else:
            src = FragSource(fid=f"FR-{key}#{latest.v}", origin="db_pending", holders=[holder(records_agent(e))])
            cls = "A" if records_agent(e) == card else "B"
        local_need = g == root
        return Need(need_id=f"{tid}.N{n}", semantic_key=f"{g}/{e}/profile", group=g, role="records", order=n,
                    card_agent=card, sources=[src], state_class=None if local_need else cls), latest.value

    def fin_need(tid, n, r, d, day, pending, holders_by_frag):
        """FIN 집행 가능액 need. pending = [(cid, 금액, 출처)], 출처는 'frag' 또는 'db'."""
        g, dept = f"FIN-{r}", DEPTS[r][d]; key = f"{g}/line/{dept}/remaining"
        vs = db[g][key]; latest = [x for x in vs if x.day <= day][-1]
        srcs, frag_holders = [], []
        if latest.db_day <= day:
            srcs.append(DbSource(key=key, v=latest.v, canary=str(latest.value)))
        else:
            h = holders_by_frag[key]
            srcs.append(FragSource(fid=f"FR-{key}#{latest.v}", origin="db_pending", holders=h, canary=str(latest.value)))
            frag_holders.append(h)
        db_pending_cids = [c for c, _, how in pending if how == "db"]
        srcs.append(DbQuerySource(query=f"commit WHERE dept={dept} AND status IN (reviewing, pending)",
                                  result=db_pending_cids or "ABSENT", asof=day))
        for cid, amt, how in pending:
            if how == "db":
                srcs.append(DbSource(key=f"{g}/commit/{cid}/status", v=1, canary=str(amt)))
            else:
                h = holders_by_frag[cid]
                srcs.append(FragSource(fid=f"FR-{cid}", origin="operational", holders=h, canary=str(amt)))
                frag_holders.append(h)
        srcs.append(RuleSource(id=f"{g}.pending_deducted"))
        card = budgeting_agent(r, d)
        live = [{x.agent for x in h if x.active and (x.raw_window or x.digest)} for h in frag_holders]
        if not frag_holders: cls = "A"
        elif any(not L for L in live): cls = "D"
        else:
            inter = set.intersection(*live); cls = "A" if card in inter else ("B" if inter else "C")
        avail = latest.value - sum(a for _, a, _ in pending)
        return Need(need_id=f"{tid}.N{n}", semantic_key=f"{g}/{dept}/available_budget", group=g, role="budgeting", order=n,
                    card_agent=card, sources=srcs, state_class=cls), avail

    frag_h = {
        "CMT-00001": [holder("fin-sel.a3")],
        "CMT-00002": [holder("fin-sel.a3")],
        "CMT-00003": [holder("fin-tyo.a3")],
        "FIN-SEL/line/개발1팀/remaining": [holder("fin-sel.a2")],
    }
    frag_h_after_leave = {**frag_h, "CMT-00002": [FragHolder(agent="fin-sel.a3", raw_window=False, digest=False, active=False)]}

    def cross(tid, day, rnd, root, agent, text, entities, schema, answer, needs):
        work.append(TimelineEvent(eid=f"EV-{len(timeline) + len(work) + 1:04d}", seq=1, day=day, round=rnd, kind="cross",
                                  group=root, agent=agent, task_id=tid, text=text, entities=entities, output_schema=schema))
        remote = [n.state_class for n in needs if n.state_class]
        gold.append(GoldRecord(task_id=tid, answer=answer, needs=needs,
                               state_class=max(remote, key=CLASS_ORDER.index) if remote else None,
                               meta={"template": "lookup" if schema is LOOKUP else "budget"}))

    def lookup(tid, day, rnd, e):
        r = region_of(e); root = f"FIN-{r}"
        n, prof = hr_need(tid, 1, e, day, root)
        cross(tid, day, rnd, root, agent_id(root, 0), f"{EMPS[e][1]} 현재 소속이랑 직급 확인해 줘.", [e], LOOKUP, {"dept": prof["dept"], "grade": prof["grade"]}, [n])

    def budget(tid, day, rnd, e, amount, pending, fh=frag_h):
        r = region_of(e); root = f"HR-{r}"
        n1, prof = hr_need(tid, 1, e, day, root)
        d = DEPTS[r].index(prof["dept"])
        n2, avail = fin_need(tid, 2, r, d, day, pending, fh)
        cross(tid, day, rnd, root, agent_id(root, 2), f"{EMPS[e][1]} 장비 {amount:,}원, 소속 부서 예산으로 지금 집행 가능한지 봐줘. 가능액도 알려줘.",
              [e], BUDGET, {"decision": "approve" if amount <= avail else "insufficient", "available": avail}, [n1, n2])

    lookup("W-001", 1, 2, "E-SEL-1000")                                                          # A
    budget("W-002", 1, 3, "E-SEL-1000", 1_850_000, [("CMT-00001", 612_300, "frag")])              # B: 지급 담당만 앎
    budget("W-003", 1, 3, "E-SEL-1001", 1_500_000, [("CMT-00002", 455_800, "frag")])              # C: 잔액(예산 a2) + 가승인(지급 a3)
    budget("W-004", 2, 2, "E-SEL-1003", 2_300_000, [("CMT-00002", 455_800, "frag")])              # B: 잔액은 DB 등록됨
    lookup("W-005", 2, 3, "E-SEL-1001")                                                          # A: 이동 발효 전
    budget("W-006", 2, 2, "E-TYO-1001", 3_100_000, [("CMT-00003", 389_100, "frag")])              # B
    lookup("W-007", 3, 2, "E-SEL-1001")                                                          # B: 발효, DB 등록 전
    budget("W-008", 4, 2, "E-SEL-1002", 2_700_000, [("CMT-00001", 612_300, "db")])                # A: 확정 대기가 DB에
    budget("W-009", 4, 3, "E-SEL-1003", 1_700_000, [("CMT-00002", 455_800, "frag")], frag_h_after_leave)  # D: 이탈자 이력에만
    lookup("W-010", 5, 2, "E-TYO-1002")                                                          # A

    _write_scenario(out / "worldgen_mini", "worldgen", 5, specs, rules, params, groups,
                    lambda g: GroupSnapshot(group=g, histories={k: v for k, v in H[g].h.items()}, activity=activity[g],
                                            journal=journal[g], egress_log=egress[g],
                                            db=[DbRecord(key=k, versions=[x for x in vs if x.day <= 0])
                                                for k, vs in db[g].items() if any(x.day <= 0 for x in vs)],
                                            aliases={**aliases[g.split("-")[1]], **{d: [d] for d in DEPTS[g.split("-")[1]]}},
                                            env={"scope_categories": DEPTS[g.split("-")[1]]}),
                    timeline, work, gold,
                    {"domains": ["HR", "FIN"], "regions": REGIONS, "rounds_per_day": 3, "db_lag": [1, 2]})


# ═════════════════════════════ silo_mini ═════════════════════════════
SHARDS = {
    "g1.a1": ["apple", "river", "stone", "cloud"], "g1.a2": ["apple", "river", "maple", "tiger"],
    "g2.a1": ["apple", "river", "candle", "ocean"], "g2.a2": ["apple", "river", "stone", "lemon"],
    "g3.a1": ["apple", "river", "piano", "tiger"], "g3.a2": ["apple", "river", "ocean", "cedar"],
    "g4.a1": ["apple", "river", "lemon", "falcon"], "g4.a2": ["apple", "river", "maple", "violet"],
}
QUESTIONS = {
    "Q1": ("모든 에이전트의 조각에 공통으로 들어 있는 단어를 전부 찾아라.",
           OutputSchema(slots=[Slot(name="words", type="set")]),
           {"words": sorted(set.intersection(*map(set, SHARDS.values())))}),
    "Q2": ("모든 조각을 합쳤을 때 서로 다른 단어는 몇 개인가?",
           OutputSchema(slots=[Slot(name="count", type="number")]),
           {"count": len(set().union(*SHARDS.values()))}),
}


def build_silo(out: Path):
    groups = [f"G{i}" for i in range(1, 5)]
    skill = AgentSkill(id="shard", name="조각 보유", description="자기 조각의 원소를 읽고 답한다", tags=["silo"], examples=[])
    specs = [GroupSpec(id=g, members=[MemberSpec(agent_id=a, role="holder", card=AgentCard(
                name=f"{g} 조각 보유자", description="조각 하나를 가진 에이전트", version=1, skills=[skill], group=g,
                scope=None, occupant=a)) for a in SHARDS if a.startswith(g.lower() + ".")],
                       card=GroupCard(name=g, description="조각 보유자 두 명의 그룹", version=1, skills=[skill], group=g,
                                      service_scope=None, endpoint=f"boundary:{g}"))
             for g in groups]
    group_of = {a: a.split(".")[0].upper() for a in SHARDS}

    def snapshot(g):
        H = Histories()
        for a in SHARDS:
            if group_of[a] == g:
                H.add(a, 0, "user", "[안내] 당신은 조각 하나를 가지고 있다. shard.read로 확인할 수 있다.", [f"SH-{a}"],
                      "0일차 조각 안내")
        return GroupSnapshot(group=g, histories=H.h, activity=[], journal=[], egress_log=[],
                             env={"shards": {a: w for a, w in SHARDS.items() if group_of[a] == g}})

    work, gold = [], []
    for rnd, (q, (text, schema, answer)) in enumerate(QUESTIONS.items(), start=1):
        for asker in SHARDS:
            tid = f"{q}.{asker}"; root = group_of[asker]
            work.append(TimelineEvent(eid=f"EV-{len(work) + 1:04d}", seq=1, day=1, round=rnd, kind="cross", group=root,
                                      agent=asker, task_id=tid, text=text, entities=[], output_schema=schema))
            needs = []
            for n, (owner, words) in enumerate(SHARDS.items(), start=1):
                g = group_of[owner]; card = sorted(a for a in SHARDS if group_of[a] == g)[0]
                needs.append(Need(need_id=f"{tid}.N{n}", semantic_key=f"silo/shard/{owner}", group=g, role="holder", order=n,
                                  card_agent=card, sources=[FragSource(fid=f"SH-{owner}", origin="operational",
                                                                       holders=[FragHolder(agent=owner, raw_window=True, digest=False, active=True)])],
                                  state_class=None if g == root else ("A" if owner == card else "B")))
            remote = [x.state_class for x in needs if x.state_class]
            gold.append(GoldRecord(task_id=tid, answer=answer, needs=needs, state_class=max(remote, key=CLASS_ORDER.index)))

    _write_scenario(out / "silo_mini", "silo", 1, specs, [], {}, groups, snapshot, [], work, gold, {"max_rounds": 3})


# ═════════════════════════════ 공통 쓰기 ═════════════════════════════
def _write_scenario(root: Path, benchmark, days, specs, rules, rule_params, groups, snapshot, timeline, work, gold, params):
    pub, priv = root / "public", root / "private"
    events = sorted(timeline + work, key=lambda e: (e.day, e.round, e.kind != "world", e.eid))
    events = [e.model_copy(update={"seq": i}) for i, e in enumerate(events, start=1)]
    timeline = [e for e in events if e.kind != "cross"]
    work = [e for e in events if e.kind == "cross"]
    write_json(pub / "world_init.json", dump(WorldInit(benchmark=benchmark, groups=specs)))
    write_json(pub / "rulebook.json", dump(rules))
    for g in groups:
        write_json(pub / "snapshot_day0" / f"{g}.json", dump(snapshot(g)))
    write_jsonl(pub / "timeline.jsonl", dump(timeline))
    write_jsonl(pub / "work.jsonl", dump(work))
    write_jsonl(priv / "gold.jsonl", dump(gold))
    write_json(priv / "rulebook_params.json", rule_params)
    write_json(pub / "manifest.json", dump(Manifest(benchmark=benchmark, world_hash=world_hash(pub), seed=0, days=days,
                                                    generator="gbg.tests.fixtures.build_fixtures", tokenizer=None,
                                                    params=params)))


def build(out: Path):
    build_worldgen(Path(out))
    build_silo(Path(out))


if __name__ == "__main__":
    build(Path(__file__).parent)
