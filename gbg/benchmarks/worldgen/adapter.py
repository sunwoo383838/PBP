"""worldgen 4.3 어댑터: harness/ 폴더(공개 입력)만 읽는다. private/·manifest는 실행 중 읽지 않는다.

    harness/world_init.json                  그룹(도메인·지역·토폴로지), 에이전트 card
    harness/rulebook.json                    그룹별 규정 본문
    harness/work.jsonl                       교차 과제: surface, request, answer_slots, answer_types(슬롯 형식, 템플릿별 고정)
    harness/timeline.jsonl                   평가 기간 사건 (seq 순서)
    harness/snapshot_day0/roster.json        에이전트 → 그룹·역할·활동 여부
    harness/snapshot_day0/cards.json         그룹별 역할 → card가 가리키는 에이전트
    harness/snapshot_day0/catalog.json       그룹별 업무 마스터 데이터
    harness/snapshot_day0/db_registered.jsonl 0일까지 등록된 DB 버전
    harness/snapshot_day0/transcripts/       에이전트별 워밍업 이력 원문
    harness/snapshot_day0/index/             일지·활동·엔티티 색인 (경계 모듈 전용)

역할·card·명부·답 슬롯은 모두 이 파일들에서 읽고 코드에 고정하지 않는다.
"""
import json
from collections.abc import Iterator
from pathlib import Path

import yaml

from gbg.benchmarks.common import PrivateAccessError
from gbg.contracts.answer_types import slot_from_spec
from gbg.contracts.card import AgentCard, AgentSkill, GroupCard
from gbg.contracts.schemas import (
    DbRecord, DbVersion, GroupInit, GroupSnapshot, GroupSpec, HistoryEntry, IndexEntry, MemberSpec, Need,
    OutputSchema, RuleText, TimelineEvent, ToolSpec, Verdict,
)
from gbg.retrieval.alias import AliasResolver

from . import env_tools

ROLE_CARDS = yaml.safe_load(Path(__file__).with_name("role_cards.yaml").read_text(encoding="utf-8"))

_LINE = {"db_register", "catalog_upsert", "tx", "index_batch", "spawn", "despawn", "agent_leave", "agent_join",
         "local", "cross", "world"}
_KIND = {"catalog_upsert": "catalog", "tx": "transcript", "index_batch": "index"}
_COMMON = {"day", "round", "seq", "type", "phase"}


def _jsonl(text: str) -> list[dict]:
    return [json.loads(x) for x in text.splitlines() if x.strip()]


class AnswerSchemaError(ValueError):
    """과제의 답 슬롯 형식을 찾을 수 없거나 슬롯 이름이 맞지 않음."""


class ScenarioFormatError(ValueError):
    """worldgen 4.4 산출물 형식이 아님 (출력 체크리스트를 대신하는 적재 검사)."""


GENERATOR = "worldgen_v4.4"                     # worldgen은 4.4로 동결


def _check_work(w: dict):
    """과제마다 answer_types와 request.scope(other_region_seats 포함)가 있어야 한다."""
    if not isinstance(w.get("answer_types"), dict) or not w["answer_types"]:
        raise ScenarioFormatError(f"{w.get('wid')}: answer_types 없음")
    scope = (w.get("request") or {}).get("scope")
    if not isinstance(scope, dict) or "other_region_seats" not in scope:
        raise ScenarioFormatError(f"{w.get('wid')}: request.scope(other_region_seats 포함) 없음")


def _check_index_entries(entries: list[dict], where: str):
    """색인 항목마다 entities 목록이 있어야 한다 (4.4 색인 다중 키)."""
    for x in entries:
        if not isinstance(x.get("entities"), list):
            raise ScenarioFormatError(f"{where}: 색인 항목에 entities 없음 ({x.get('agent')})")


class WorldgenAdapter:
    name = "worldgen"

    # ── 읽기 ──
    def load(self, harness_dir: Path) -> None:
        pub = Path(harness_dir).resolve()
        if pub.name != "harness" or "private" in pub.parts:
            raise PrivateAccessError(f"{harness_dir}: 공개 입력(harness/) 디렉터리만 로드한다")
        self._pub = pub
        # 시나리오 루트의 manifest (공개: generator·seed·파라미터). private/는 읽지 않는다
        self.manifest = json.loads((pub.parent / "manifest.json").read_text(encoding="utf-8"))
        if self.manifest.get("generator") != GENERATOR:
            raise ScenarioFormatError(f"generator {self.manifest.get('generator')!r} ≠ {GENERATOR}")
        world = json.loads(self.read("world_init.json"))
        roster = json.loads(self.read("snapshot_day0/roster.json"))
        targets = json.loads(self.read("snapshot_day0/cards.json"))
        self._catalog = json.loads(self.read("snapshot_day0/catalog.json"))
        rulebook = json.loads(self.read("rulebook.json"))
        self._domain = {g: v["domain"] for g, v in world["groups"].items()}
        self._region = {g: v["region"] for g, v in world["groups"].items()}

        self._groups = [self._group_spec(g, v, world["agent_cards"], roster, targets.get(g, {}))
                        for g, v in world["groups"].items()]
        employees = {e["employee_id"]: [e[k] for k in ("name", "alias") if e.get(k)]
                     for cat in self._catalog.values() for k, e in cat.items() if k.startswith("employees/")}
        self._db: dict[str, dict[str, list[DbVersion]]] = {}
        for r in _jsonl(self.read("snapshot_day0/db_registered.jsonl")):
            g = r["key"].split("/", 1)[0]
            self._db.setdefault(g, {}).setdefault(r["key"], []).append(
                DbVersion(v=r["v"], day=r["day"], db_day=r["db_day"], value=r["value"]))
        departments = self._departments()
        self._aliases = {g: {**{d: [] for d in departments.get(self._region[g], [])},
                             **{k.split("/", 1)[1]: [] for k in self._catalog.get(g, {})}, **employees}
                         for g in self._domain}                           # 부서 + catalog id + 직원 이름·별칭
        self._tagger = {g: AliasResolver(a) for g, a in self._aliases.items()}
        index = {k: json.loads(self.read(f"snapshot_day0/index/{k}.json")) for k in ("journal", "activity", "entity")}
        for k in ("journal", "activity"):
            for g, entries in index[k].items():
                _check_index_entries(entries, f"snapshot {k} {g}")
        self._index = index
        self._rules = {g: [RuleText(id=r["id"], group=g, title=r.get("title"), body=r["text"]) for r in rs]
                       for g, rs in rulebook.items()}
        self._transcripts = {p.stem: _jsonl(p.read_text(encoding="utf-8"))
                             for p in sorted((pub / "snapshot_day0" / "transcripts").glob("*.jsonl"))}
        self._scope = {g: departments.get(self._region[g], []) for g in self._domain}

        work = {w["wid"]: w for w in _jsonl(self.read("work.jsonl"))}
        for w in work.values():
            _check_work(w)
        timeline = _jsonl(self.read("timeline.jsonl"))
        for r in timeline:
            if r["type"] == "index_batch":
                _check_index_entries(r["entries"], f"index_batch seq {r['seq']}")
        self._events = [self._event(r, work) for r in timeline]

    def read(self, rel: str) -> str:
        path = (self._pub / rel).resolve()
        if not path.is_relative_to(self._pub) or "private" in path.parts:
            raise PrivateAccessError(f"{rel}: 공개 입력 밖의 경로")
        return path.read_text(encoding="utf-8")

    def _group_spec(self, g, meta, agent_cards, roster, targets) -> GroupSpec:
        members = []
        for aid in sorted(a for a, r in roster.items() if r["group"] == g):
            r = roster[aid]
            c = agent_cards.get(aid)
            card = None if c is None else AgentCard(
                name=c["name"], description=c["description"], version=1, group=g, scope=None, occupant=aid,
                region=meta["region"], skills=self._skills(meta, r["role"], c["description"]))
            members.append(MemberSpec(agent_id=aid, role=r["role"], card=card, active=r["active"]))
        # 그룹 card(게이트웨이 조건 전용)의 skills = 구성원 card skills의 합집합
        skills = list({s.id: s for m in members if m.card for s in m.card.skills}.values())
        gcard = GroupCard(name=g, description=f"{meta['domain']} group, region {meta['region']}", version=1,
                          skills=skills, group=g, service_scope=None, endpoint=f"boundary:{g}")
        return GroupSpec(id=g, topology=meta.get("topology", "specialist"), members=members, card=gcard,
                         card_targets=dict(targets))

    @staticmethod
    def _skills(meta, role: str, description: str) -> list[AgentSkill]:
        """card skills. swarm 접수 담당(coordinator)은 접수 업무 + 그 도메인 역할들의 업무 범위 (role_cards.yaml,
        worldgen 4.4 const의 ROLES·CARD). 문구에 그룹은 넣지 않는다."""
        own = [AgentSkill(id=role, name=role, description=description)]
        if meta.get("topology") != "swarm" or role != "coordinator":
            return own
        roles = dict.fromkeys(ROLE_CARDS["roles"][meta["domain"]])
        return own + [AgentSkill(id=r, name=r, description=ROLE_CARDS["card"][r]) for r in roles]

    def _departments(self) -> dict[str, list[str]]:
        """지역별 부서: 예산 라인 키, 인사 기록의 부서 값, catalog 가승인의 부서. 태깅 엔티티이자 동적 card 범주."""
        depts: dict[str, set[str]] = {}
        for g, keys in self._db.items():
            for k, vs in keys.items():
                parts = k.split("/")
                if len(parts) == 4 and parts[1] == "line":
                    depts.setdefault(self._region[g], set()).add(parts[2])
                for v in vs:
                    if isinstance(v.value, dict) and isinstance(v.value.get("dept"), str):
                        depts.setdefault(self._region[g], set()).add(v.value["dept"])
        for g, cat in self._catalog.items():
            for k, v in cat.items():
                if k.startswith("commits/") and isinstance(v, dict) and isinstance(v.get("department"), str):
                    depts.setdefault(self._region[g], set()).add(v["department"])
        return {r: sorted(d) for r, d in depts.items()}

    # ── 과제와 사건 ──
    @staticmethod
    def _schema_for(w: dict) -> OutputSchema:
        """과제의 answer_types(템플릿마다 고정)를 닫힌 슬롯으로. 슬롯 이름·순서는 answer_slots와 같아야 한다."""
        types = w.get("answer_types")
        if types is None:
            raise AnswerSchemaError(f"{w['wid']}: answer_types가 없다 (worldgen 4.3 이상 필요)")
        if list(types) != list(w["answer_slots"]):
            raise AnswerSchemaError(f"{w['wid']}: answer_types {list(types)} ≠ answer_slots {w['answer_slots']}")
        return OutputSchema(slots=[slot_from_spec(k, v) for k, v in types.items()])

    def _event(self, r: dict, work: dict) -> TimelineEvent:
        t = r["type"]
        if t not in _LINE:
            raise ValueError(f"seq {r['seq']}: 알 수 없는 사건 종류 '{t}'")
        base = {"eid": f"EV-{r['seq']}", "seq": r["seq"], "day": r["day"], "round": r["round"],
                "kind": _KIND.get(t, t)}
        if t == "cross":
            w = work[r["work"]]
            return TimelineEvent(**base, group=r["group"], agent=r["assignee"], task_id=w["wid"], text=w["surface"],
                                 request=w["request"], output_schema=self._schema_for(w),
                                 payload={"follows": w.get("follows")})
        if t == "db_register":
            return TimelineEvent(**base, group=r["key"].split("/", 1)[0], payload={
                "key": r["key"], "version": {"v": r["v"], "day": r["day"], "db_day": r["day"], "value": r["value"]}})
        if t == "local":
            return TimelineEvent(**base, group=r["group"], agent=r["assignee"], task_id=r["eid"])
        if t == "tx":
            return TimelineEvent(**base, agent=r["agent"], task_id=r.get("eid"), payload={
                "role": r["role"], "text": r["text"], "tokens": r["tokens"], "summary": r["summary"]})
        rest = {k: v for k, v in r.items() if k not in _COMMON | {"group", "agent"}}
        return TimelineEvent(**base, group=r.get("group"), agent=r.get("agent"), payload=rest)

    # ── BenchmarkAdapter ──
    def groups(self) -> list[GroupSpec]:
        return list(self._groups)

    def domain_of(self) -> dict[str, str]:
        return dict(self._domain)

    def initial_state(self, group: str) -> GroupInit:
        members = [m.agent_id for g in self._groups if g.id == group for m in g.members]
        tag = self._tagger[group].tag
        histories = {a: [HistoryEntry(seq=i, day=x["day"], role=x["role"], text=x["text"], tokens=x["tok"],
                                      entities=tag(x["text"]), digest=x["summary"])
                         for i, x in enumerate(self._transcripts[a], 1)]
                     for a in members if a in self._transcripts}
        entry = lambda x: IndexEntry(day=x["day"], agent=x["agent"], text=x.get("text") or x.get("trace") or "",
                                     entities=x.get("entities", []))
        snap = GroupSnapshot(
            group=group, histories=histories,
            journal=[entry(x) for x in self._index["journal"].get(group, [])],
            activity=[entry(x) for x in self._index["activity"].get(group, [])],
            entity_index=self._index["entity"].get(group, {}),
            db=[DbRecord(key=k, versions=vs) for k, vs in sorted(self._db.get(group, {}).items())],
            catalog=self._catalog.get(group, {}), aliases=self._aliases[group],
            env={"scope_categories": self._scope[group]})
        return GroupInit(**snap.model_dump(), rules=self._rules.get(group, []))

    def events(self) -> Iterator[TimelineEvent]:
        return iter(self._events)

    def env_tools(self) -> list[ToolSpec]:
        return env_tools.domain_specs(next(iter(self._domain.values())))

    def group_tools(self, group: str) -> list[ToolSpec]:
        return env_tools.domain_specs(self._domain[group])

    def make_tools(self, stores):
        return env_tools.make_tools(stores, self.domain_of())

    def tag(self, group: str, text: str) -> list[str]:
        return self._tagger[group].tag(text) if group in self._tagger else []

    # 오프라인 채점은 Stage 7
    def verify(self, task_id: str, answer: dict, private_dir: Path) -> Verdict:
        raise NotImplementedError("Stage 7")

    def needs(self, task_id: str, private_dir: Path) -> list[Need] | None:
        raise NotImplementedError("Stage 7")
