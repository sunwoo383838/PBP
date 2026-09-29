"""테스트 픽스처 생성기 (결정적, 난수 없음).

    uv run python -m gbg.tests.fixtures.build_fixtures

worldgen_mini  worldgen 4.2 산출물 형식(harness/ + private/)의 축소판. 도메인 2(HR, FIN) × 지역 2(SEL, TYO) = 그룹 4.
               specialist 3개(5명: 서로 다른 역할 4 + 중복 1), swarm 1개(FIN-TYO: coordinator + 작업별 워커).
               5일, 교차 과제 8개. 담는 상황: card 대상이 아닌 중복 담당, card 대상의 이탈과 후임 합류, 순서가
               뒤섞인 DB 버전 등록, catalog 추가, 로컬 작업 재생 tx 줄, 하루 끝 색인, 발견성 H0/H1/H2 조각.
silo_mini      공개 형식(public/ + private/). 에이전트 8명을 그룹 4개로, 전역 질문 2개.
"""
import hashlib
import json
from pathlib import Path

from gbg.contracts.card import AgentCard, AgentSkill, GroupCard
from gbg.contracts.schemas import (
    FragHolder, FragSource, GoldRecord, GroupSnapshot, GroupSpec, HistoryEntry, Manifest, MemberSpec, Need,
    OutputSchema, Slot, TimelineEvent, WorldInit,
)


def tokens(text):
    return max(12, int(len(text) * 1.1))                # 근사치 (실제 worldgen은 Qwen3 토크나이저)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


# ═════════════════════════════ worldgen_mini (4.2 형식) ═════════════════════════════
GROUPS = {"HR-SEL": ("HR", "SEL", "specialist"), "HR-TYO": ("HR", "TYO", "specialist"),
          "FIN-SEL": ("FIN", "SEL", "specialist"), "FIN-TYO": ("FIN", "TYO", "swarm")}
ROLES = {"HR": ["records", "records", "payroll", "recruiting", "mobility"],
         "FIN": ["budgeting", "payables", "payables", "closing", "control"]}
ROLE_DESC = {"records": "Look up and update employee department, grade, and contract type",
             "payroll": "Pay grades and grade adjustments", "recruiting": "Hiring, joining, and leaving",
             "mobility": "Personnel orders and department transfers",
             "budgeting": "Budget lines, allocations, and balances", "payables": "Review and register provisional approvals",
             "closing": "Month-end closing and cancellations", "control": "Spending controls and execution owner changes",
             "coordinator": "Takes requests and assigns workers"}
EMPS = {"SEL": [("E-SEL-1000", "김하린", "하린 과장"), ("E-SEL-1001", "박도윤", "도윤 대리"),
                ("E-SEL-1002", "이서준", "서준 선임"), ("E-SEL-1003", "최지우", "지우 과장")],
        "TYO": [("E-TYO-1000", "佐藤結衣", "佐藤さん"), ("E-TYO-1001", "小野健", "小野さん")]}
DEPTS = {"SEL": ["영업1팀", "개발1팀"], "TYO": ["営業1課", "開発1課"]}
ANSWER_TYPES = {                                        # worldgen 4.3 answer_types 형식 (템플릿마다 고정)
    "lookup": {"dept": {"type": "string", "format": "department"}, "grade": {"type": "integer"}},
    "budget": {"available": {"type": "integer"}, "n_deducted": {"type": "integer"}},
    "conflict": {"status": {"type": "enum", "values": ["reviewing", "pending", "settled", "cancelled", "none"],
                            "nullable": False}, "amount": {"type": "integer", "nullable": True}},
}
BUDGET_SCOPE = {"procurement": False, "contract_policy": False, "residency_policy": False, "other_regions": False,
                "other_region_seats": False}
FRAG_META: dict[str, tuple[str, str]] = {}              # fid → (발견성, 보유자)


class World:
    def __init__(self):
        self.tx: dict[str, list[dict]] = {}
        self.db: list[dict] = []
        self.journal = {g: [] for g in GROUPS}
        self.activity = {g: [] for g in GROUPS}
        self.entity = {g: {} for g in GROUPS}
        self.catalog = {g: {} for g in GROUPS}
        self.timeline: list[dict] = []
        self.work: list[dict] = []
        self.gold: list[dict] = []
        self.fragments: list[dict] = []
        self.seq = 0

    # ── 워밍업 ──
    def line(self, agent, day, role, text):
        rows = self.tx.setdefault(agent, [])
        rows.append({"i": len(rows), "day": day, "round": 1, "role": role, "text": text, "tok": tokens(text),
                     "summary": text[:60]})

    def frag(self, fid, group, agent, day, text, disc, origin="operational", entity=None, also=()):
        """entity와 also: 조각이 언급하는 엔티티 전부 (4.4 규칙: 색인 키에 모두 넣는다)."""
        self.line(agent, day, "tool", text)
        self.fragments.append({"fid": fid, "group": group, "agent": agent, "day": day, "origin": origin,
                               "disc": disc, "text": text})
        FRAG_META[fid] = (disc, agent)
        ents = [e for e in (entity, *also) if e]
        if disc == "H0":
            self.journal[group].append({"day": day, "agent": agent, "text": text, "entities": ents})
        elif disc == "H1":
            self.activity[group].append({"day": day, "agent": agent, "trace": f"{agent} handled: {' '.join(ents)}",
                                         "entities": ents})
        for e in ents:
            holders = self.entity[group].setdefault(e, [])
            if agent not in holders:
                holders.append(agent)

    # ── 평가 기간 ──
    def ev(self, day, rnd, type_, **kw):
        self.seq += 1
        self.timeline.append({"day": day, "round": rnd, "seq": self.seq, "type": type_, "phase": "eval", **kw})
        return self.seq

    def evtx(self, day, rnd, agent, role, text, eid=None):
        self.ev(day, rnd, "tx", agent=agent, i=0, role=role, text=text, tokens=tokens(text), summary=text[:60], eid=eid)

    def cross(self, day, rnd, wid, group, agent, surface, request, slots, schema, gold, needs, state_class):
        s = self.ev(day, rnd, "cross", work=wid, group=group, assignee=agent, follows=None)
        self.work.append({"wid": wid, "day": day, "round": rnd, "seq": s, "root": group, "assignee": agent,
                          "surface": surface, "request": request, "follows": None, "answer_slots": slots,
                          "answer_types": {k: ANSWER_TYPES[schema][k] for k in slots}})
        self.gold.append({"wid": wid, "day": day, "round": rnd, "gold": gold, "needs": needs,
                          "state_class": state_class, "c_ops": state_class == "C"})


def agent_ids(g):
    dom, _, top = GROUPS[g]
    if top == "swarm":
        return [(f"{g.lower()}.c0", "coordinator")]
    return [(f"{g.lower()}.a{i + 1}", r) for i, r in enumerate(ROLES[dom])]


def need(sem, group, fids, cls, sources=()):
    frags = [{"type": "frag", "frag": {"fid": f, "disc": FRAG_META[f][0], "holders": [{"agent": FRAG_META[f][1]}]}}
             for f in fids]
    return {"sem": sem, "group": group, "role": "", "order": 1, "local": False, "class": cls,
            "n_holders": len({FRAG_META[f][1] for f in fids}),
            "min_cover": 1 if cls in ("A", "B") else (None if cls == "D" else 2),
            "critical_components": list(fids), "sources": [*sources, *frags]}


def build_worldgen(out: Path):
    w = World()
    root = out / "worldgen_mini"

    # ── 그룹, 명부, card ──
    roster, agent_cards, targets = {}, {}, {}
    for g, (dom, reg, top) in GROUPS.items():
        targets[g] = {}
        for aid, role in agent_ids(g):
            roster[aid] = {"group": g, "role": role, "joined": -20, "left": None, "active": True}
            agent_cards[aid] = {"group": g, "name": f"{g} {role}", "description": ROLE_DESC[role]}
            if role not in targets[g]:
                targets[g][role] = aid
        if top == "swarm":
            targets[g] = {r: f"{g.lower()}.c0" for r in sorted(set(ROLES[dom]))}
    targets["HR-SEL"]["records"] = "hr-sel.a2"               # card 대상은 a2, a1은 중복 담당 (디렉터리에 없음)
    roster["fin-sel.a6"] = {"group": "FIN-SEL", "role": "payables", "joined": -20, "left": -8, "active": False}
    roster["fin-tyo.w00001"] = {"group": "FIN-TYO", "role": "worker", "joined": -3, "left": -3, "active": False}

    # ── catalog, DB, 워밍업 이력, 색인 ──
    for reg in ("SEL", "TYO"):
        for eid, name, alias in EMPS[reg]:
            w.catalog[f"HR-{reg}"][f"employees/{eid}"] = {"employee_id": eid, "name": name, "alias": alias, "region": reg}
    grade = {"E-SEL-1000": 3, "E-SEL-1001": 2, "E-SEL-1002": 4, "E-SEL-1003": 1, "E-TYO-1000": 3, "E-TYO-1001": 2}
    dept = {"E-SEL-1000": "영업1팀", "E-SEL-1001": "개발1팀", "E-SEL-1002": "영업1팀", "E-SEL-1003": "개발1팀",
            "E-TYO-1000": "営業1課", "E-TYO-1001": "開発1課"}
    for eid, g in grade.items():
        reg = eid.split("-")[1]; grp = f"HR-{reg}"; rec = f"{grp.lower()}.a{1 + int(eid[-1]) % 2}"
        prof = {"dept": dept[eid], "grade": g, "contract": "regular", "hire_day": -300, "status": "active"}
        w.db.append({"key": f"{grp}/emp/{eid}/profile", "v": 1, "day": -20, "db_day": -20, "value": prof})
        w.line(rec, -20, "user", f"[Task] Check the HR record of {eid}")
        w.frag(f"FR-P{eid[2:5]}{eid[-1]}", grp, rec, -20,
               f"{eid} HR record confirmed: {dept[eid]}, grade {g}, regular.", "H0", "db_pending", eid)
    lines = {("SEL", 0): 3_120_400, ("SEL", 1): 2_874_300, ("TYO", 0): 4_051_700, ("TYO", 1): 3_366_200}
    for (reg, d), v in lines.items():
        g = f"FIN-{reg}"; dn = DEPTS[reg][d]
        for attr in ("remaining", "base"):
            w.db.append({"key": f"{g}/line/{dn}/{attr}", "v": 1, "day": -20, "db_day": -20, "value": v})
        agent = "fin-sel.a1" if reg == "SEL" else "fin-tyo.c0"
        w.line(agent, -20, "user", f"[Task] Check the {dn} budget line")
        w.frag(f"FR-L{reg}{d}", g, agent, -20, f"{dn} capex balance confirmed at KRW {v:,}.", "H0", "db_pending", dn)
    # 가승인: CMT-00001은 등록됨(catalog·DB), CMT-00002·00003은 이력에만 (operational)
    w.catalog["FIN-SEL"]["commits/CMT-00001"] = {"commit_id": "CMT-00001", "department": "영업1팀", "item": "laptop", "work": None}
    w.db.append({"key": "FIN-SEL/commit/CMT-00001/status", "v": 1, "day": -3, "db_day": -2,
                 "value": {"status": "pending", "amount": 612_300, "expected_settle": 8}})
    w.line("fin-sel.a2", -3, "user", "[Task] Review a provisional approval for 영업1팀 equipment")
    w.frag("FR-C1", "FIN-SEL", "fin-sel.a2", -3,
           "CMT-00001 영업1팀 laptop provisional approval KRW 612,300 confirmed, settlement due day 8.", "H1", entity="CMT-00001",
           also=("영업1팀", "laptop"))
    w.line("fin-sel.a3", -1, "user", "[Task] Review a provisional approval for 개발1팀 equipment")
    w.frag("FR-C2", "FIN-SEL", "fin-sel.a3", -1,
           "CMT-00002 개발1팀 monitor provisional approval KRW 455,800 review started, settlement due day 9.", "H1",
           entity="CMT-00002", also=("개발1팀", "monitor"))
    # H2: 선행 발화(대상) + 지시어 발화(값), 색인 없음
    w.line("fin-sel.a3", -1, "assistant", "Opened a review for CMT-00003 개발1팀 workstation.")
    w.line("fin-sel.a3", -1, "assistant", "That one is on hold until Friday; hold KRW 389,100 against the line.")
    w.fragments.append({"fid": "FR-C3", "group": "FIN-SEL", "agent": "fin-sel.a3", "day": -1, "origin": "operational",
                        "disc": "H2", "text": "That one is on hold until Friday; hold KRW 389,100 against the line."})
    FRAG_META["FR-C3"] = ("H2", "fin-sel.a3")
    # 0일차 개발1팀 잔액 조정 (2일차 등록) — 이력(H0 일지)에만
    w.line("fin-sel.a1", 0, "user", "[Task] Adjust the 개발1팀 budget")
    w.frag("FR-LADJ", "FIN-SEL", "fin-sel.a1", 0,
           "개발1팀 capex balance adjusted to KRW 2,417,900 (division reallocation).", "H0", "db_pending", "개발1팀")
    w.line("fin-tyo.w00001", -3, "user", "[Task] Check 開発1課 closing items")
    w.line("fin-tyo.c0", -3, "tool", "[Worker report] 開発1課 closing items processed (details omitted)")

    # ── 평가 기간 타임라인 ──
    S_LOOKUP, S_BUDGET, S_STATUS = "lookup", "budget", "conflict"
    lookup_req = lambda reg, eid, alias: {"region": reg, "subject": {"employee_id": eid, "alias": alias}, "scope": dict(BUDGET_SCOPE)}
    budget_req = lambda reg, dn: {"region": reg, "department": dn, "scope": dict(BUDGET_SCOPE)}
    db_src = lambda key: [{"type": "db", "key": key, "v": 1}]
    # 1일차
    w.ev(1, 0, "db_register", key="HR-SEL/emp/E-SEL-1003/profile", v=3,          # 버전 3이 2보다 먼저 등록된다
         value={"dept": "개발1팀", "grade": 3, "contract": "regular", "hire_day": -300, "status": "active"})
    w.ev(1, 0, "catalog_upsert", group="FIN-SEL", key="commits/CMT-00004",
         value={"commit_id": "CMT-00004", "department": "개발1팀", "item": "laptop", "work": None})
    w.ev(1, 0, "db_register", key="FIN-SEL/commit/CMT-00004/status", v=1,
         value={"status": "pending", "amount": 301_200, "expected_settle": 6})
    w.ev(1, 1, "local", eid="L-001", group="HR-SEL", assignee="hr-sel.a3")
    w.evtx(1, 1, "hr-sel.a3", "user", "[Task] Apply the grade adjustment for 지우 과장", "L-001")
    w.evtx(1, 1, "hr-sel.a3", "tool", "[Tool result] Recorded: E-SEL-1003 grade 2.", "L-001")
    w.cross(1, 1, "W-001", "FIN-SEL", "fin-sel.a1", "Check the current department and grade of 하린 과장.",
            lookup_req("SEL", "E-SEL-1000", "하린 과장"), ["dept", "grade"], S_LOOKUP, {"dept": "영업1팀", "grade": 3},
            [need("HR-SEL/E-SEL-1000/profile", "HR-SEL", [], "A", db_src("HR-SEL/emp/E-SEL-1000/profile"))], "A")
    w.ev(1, 1, "spawn", group="FIN-TYO", agent="fin-tyo.w00002")
    w.ev(1, 1, "local", eid="L-002", group="FIN-TYO", assignee="fin-tyo.w00002")
    w.evtx(1, 1, "fin-tyo.w00002", "user", "[Task] Check the 営業1課 budget line", "L-002")
    w.evtx(1, 1, "fin-tyo.c0", "tool", "[Worker report] 営業1課 budget line checked (details omitted)", "L-002")
    w.cross(1, 2, "W-002", "HR-SEL", "hr-sel.a3",
            "하린 과장 needs equipment for KRW 1,850,000. How much can their department spend right now, after deductions?",
            budget_req("SEL", "영업1팀"), ["available", "n_deducted"], S_BUDGET, {"available": 2_508_100, "n_deducted": 1},
            [need("FIN-SEL/영업1팀/budget_schedule", "FIN-SEL", ["FR-C1"], "B")], "B")
    w.ev(1, 4, "index_batch", entries=[{"group": "FIN-SEL", "index": "activity", "agent": "fin-sel.a3",
                                        "trace": "fin-sel.a3 handled: CMT-00004 개발1팀 provisional approval",
                                        "entities": ["CMT-00004", "개발1팀"]}])
    w.ev(1, 4, "despawn", agent="fin-tyo.w00002")
    # 2일차
    w.ev(2, 0, "db_register", key="HR-SEL/emp/E-SEL-1003/profile", v=2,          # 늦게 온 버전 2: 현재값은 여전히 3
         value={"dept": "개발1팀", "grade": 2, "contract": "regular", "hire_day": -300, "status": "active"})
    w.ev(2, 0, "db_register", key="FIN-SEL/line/개발1팀/remaining", v=2, value=2_417_900)
    w.cross(2, 1, "W-003", "HR-SEL", "hr-sel.a3",
            "지우 과장 needs a monitor for KRW 2,300,000. How much can their department spend right now, after deductions?",
            budget_req("SEL", "개발1팀"), ["available", "n_deducted"], S_BUDGET, {"available": 1_660_700, "n_deducted": 2},
            [need("FIN-SEL/개발1팀/budget_schedule", "FIN-SEL", ["FR-C2", "FR-C3"], "C")], "C")
    w.ev(2, 4, "index_batch", entries=[{"group": "FIN-SEL", "index": "journal", "agent": "fin-sel.a1",
                                        "text": "개발1팀 capex balance registered at KRW 2,417,900.",
                                        "entities": ["개발1팀"]}])
    # 3일차: payables card 대상(fin-sel.a2)이 떠난다
    w.ev(3, 0, "agent_leave", group="FIN-SEL", agent="fin-sel.a2", handover=True)
    w.cross(3, 1, "W-004", "FIN-SEL", "fin-sel.a1", "Check the current department and grade of 도윤 대리.",
            lookup_req("SEL", "E-SEL-1001", "도윤 대리"), ["dept", "grade"], S_LOOKUP, {"dept": "개발1팀", "grade": 2},
            [need("HR-SEL/E-SEL-1001/profile", "HR-SEL", [], "A", db_src("HR-SEL/emp/E-SEL-1001/profile"))], "A")
    w.ev(3, 2, "world", event="budget_reset", regions=["SEL"])
    w.cross(3, 2, "W-005", "HR-SEL", "hr-sel.a3", "Is CMT-00001 still alive, and what is its status?",
            {"region": "SEL", "commit_id": "CMT-00001", "scope": dict(BUDGET_SCOPE)}, ["status", "amount"], S_STATUS,
            {"status": "pending", "amount": 612_300},
            [need("FIN-SEL/CMT-00001/effective_status", "FIN-SEL", ["FR-C1"], "D")], "D")
    w.ev(3, 4, "index_batch", entries=[])
    # 4일차: 후임 합류, 인수인계 줄
    w.ev(4, 0, "agent_join", group="FIN-SEL", agent="fin-sel.n0001", role="payables", handover=True,
         **{"from": "fin-sel.a2"})
    w.evtx(4, 0, "fin-sel.n0001", "user", "[Handover] CMT-00001 영업1팀 provisional approval pending, settlement due day 8.")
    w.cross(4, 1, "W-006", "HR-TYO", "hr-tyo.a3",
            "小野さん needs equipment for KRW 3,100,000. How much can their department spend right now, after deductions?",
            budget_req("TYO", "開発1課"), ["available", "n_deducted"], S_BUDGET, {"available": 3_366_200, "n_deducted": 0},
            [need("FIN-TYO/開発1課/budget_schedule", "FIN-TYO", ["FR-LTYO1"], "A")], "A")
    w.ev(4, 4, "index_batch", entries=[])
    # 5일차
    w.cross(5, 1, "W-007", "FIN-TYO", "fin-tyo.c0", "Check the current department and grade of 佐藤さん.",
            lookup_req("TYO", "E-TYO-1000", "佐藤さん"), ["dept", "grade"], S_LOOKUP, {"dept": "営業1課", "grade": 3},
            [need("HR-TYO/E-TYO-1000/profile", "HR-TYO", [], "A", db_src("HR-TYO/emp/E-TYO-1000/profile"))], "A")
    w.cross(5, 2, "W-008", "HR-SEL", "hr-sel.a1",
            "서준 선임 needs equipment for KRW 2,700,000. How much can their department spend right now, after deductions?",
            budget_req("SEL", "영업1팀"), ["available", "n_deducted"], S_BUDGET, {"available": 2_508_100, "n_deducted": 1},
            [need("FIN-SEL/영업1팀/budget_schedule", "FIN-SEL", ["FR-C1"], "B")], "B")
    w.ev(5, 4, "index_batch", entries=[])

    rule = lambda g, rid, title, text: {"id": f"{g}.{rid}", "title": title, "text": text}
    rulebook = {g: [rule(g, "transfer_effective_day", "Transfer effective day",
                         "A department transfer takes effect on its effective day.")] if g.startswith("HR") else
                   [rule(g, "pending_deduction", "Pending deduction",
                         "The available amount is the line balance minus provisional approvals under review or pending.")]
                for g in GROUPS}

    h, snap = root / "harness", root / "harness" / "snapshot_day0"
    write_json(h / "world_init.json", {"domains": ["HR", "FIN"], "regions": ["SEL", "TYO"],
                                       "groups": {g: {"domain": d, "region": r, "topology": t} for g, (d, r, t) in GROUPS.items()},
                                       "agent_cards": agent_cards})
    write_json(h / "rulebook.json", rulebook)
    write_jsonl(h / "work.jsonl", w.work)
    write_jsonl(h / "timeline.jsonl", w.timeline)
    write_json(snap / "roster.json", roster)
    write_json(snap / "cards.json", targets)
    write_json(snap / "catalog.json", w.catalog)
    write_jsonl(snap / "db_registered.jsonl", w.db)
    for agent, rows in sorted(w.tx.items()):
        write_jsonl(snap / "transcripts" / f"{agent}.jsonl", rows)
    write_json(snap / "index" / "journal.json", w.journal)
    write_json(snap / "index" / "activity.json", w.activity)
    write_json(snap / "index" / "entity.json", w.entity)
    write_jsonl(root / "private" / "gold.jsonl", w.gold)
    write_jsonl(root / "private" / "fragments.jsonl", w.fragments)
    digest = hashlib.sha256(b"".join(p.read_bytes() for p in sorted(h.rglob("*")) if p.is_file())).hexdigest()[:20]
    write_json(root / "manifest.json", {"world_hash": digest, "generator": "worldgen_v4.4", "schema_version": "4.4-mini",
                                        "params": {"seed": 0, "D": 2, "R": 2, "T": 5}})


# ═════════════════════════════ silo_mini (공개 형식) ═════════════════════════════
SHARDS = {
    "g1.a1": ["apple", "river", "stone", "cloud"], "g1.a2": ["apple", "river", "maple", "tiger"],
    "g2.a1": ["apple", "river", "candle", "ocean"], "g2.a2": ["apple", "river", "stone", "lemon"],
    "g3.a1": ["apple", "river", "piano", "tiger"], "g3.a2": ["apple", "river", "ocean", "cedar"],
    "g4.a1": ["apple", "river", "lemon", "falcon"], "g4.a2": ["apple", "river", "maple", "violet"],
}
QUESTIONS = {
    "Q1": ("Find every word that appears in the shards of all agents.",
           OutputSchema(slots=[Slot(name="words", type="set")]),
           {"words": sorted(set.intersection(*map(set, SHARDS.values())))}),
    "Q2": ("How many distinct words are there across all shards combined?",
           OutputSchema(slots=[Slot(name="count", type="int")]),
           {"count": len(set().union(*SHARDS.values()))}),
}
NOTICE = "[Notice] You hold one shard. You can read it with shard.read."


def build_silo(out: Path):
    root = out / "silo_mini"
    groups = [f"G{i}" for i in range(1, 5)]
    skill = AgentSkill(id="shard", name="Shard holder", description="Reads the elements of its own shard and answers",
                       tags=["silo"], examples=[])
    group_of = {a: a.split(".")[0].upper() for a in SHARDS}
    specs = [GroupSpec(id=g, members=[MemberSpec(agent_id=a, role="holder", card=AgentCard(
                name=f"{g} shard holder", description="An agent that holds one shard", version=1, skills=[skill],
                group=g, scope=None, occupant=a)) for a in SHARDS if group_of[a] == g],
                       card=GroupCard(name=g, description="A group of two shard holders", version=1, skills=[skill],
                                      group=g, service_scope=None, endpoint=f"boundary:{g}"))
             for g in groups]
    pub, priv = root / "public", root / "private"
    for g in groups:
        hist = {a: [HistoryEntry(seq=1, day=0, role="user", text=NOTICE, tokens=tokens(NOTICE), entities=[f"SH-{a}"],
                                 digest="Day 0: shard notice")] for a in SHARDS if group_of[a] == g}
        snap = GroupSnapshot(group=g, histories=hist, env={"shards": {a: v for a, v in SHARDS.items() if group_of[a] == g}})
        write_json(pub / "snapshot_day0" / f"{g}.json", snap.model_dump(mode="json"))
    work, gold, seq = [], [], 0
    for rnd, (q, (text, schema, answer)) in enumerate(QUESTIONS.items(), start=1):
        for asker in SHARDS:
            seq += 1
            tid, root_g = f"{q}.{asker}", group_of[asker]
            work.append(TimelineEvent(eid=f"EV-{seq:04d}", seq=seq, day=1, round=rnd, kind="cross", group=root_g,
                                      agent=asker, task_id=tid, text=text, request={}, output_schema=schema))
            needs = []
            for n, owner in enumerate(SHARDS, start=1):
                g = group_of[owner]; card = sorted(a for a in SHARDS if group_of[a] == g)[0]
                needs.append(Need(need_id=f"{tid}.N{n}", semantic_key=f"silo/shard/{owner}", group=g, role="holder",
                                  order=n, card_agent=card,
                                  sources=[FragSource(fid=f"SH-{owner}", origin="operational",
                                                      holders=[FragHolder(agent=owner, raw_window=True, digest=False, active=True)])],
                                  state_class=None if g == root_g else ("A" if owner == card else "B")))
            remote = [x.state_class for x in needs if x.state_class]
            gold.append(GoldRecord(task_id=tid, answer=answer, needs=needs, state_class=max(remote, key="ABCD".index)))
    write_json(pub / "world_init.json", WorldInit(benchmark="silo", groups=specs).model_dump(mode="json"))
    write_json(pub / "rulebook.json", [])
    write_jsonl(pub / "timeline.jsonl", [])
    write_jsonl(pub / "work.jsonl", [e.model_dump(mode="json") for e in work])
    write_jsonl(priv / "gold.jsonl", [x.model_dump(mode="json") for x in gold])
    write_json(pub / "manifest.json", Manifest(benchmark="silo", world_hash="silo-mini", seed=0, days=1,
                                               generator="gbg.tests.fixtures.build_fixtures", params={"max_rounds": 3}
                                               ).model_dump(mode="json"))


def build(out: Path):
    build_worldgen(Path(out))
    build_silo(Path(out))


if __name__ == "__main__":
    build(Path(__file__).parent)
