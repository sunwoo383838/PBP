"""핵심 스키마: 이력, 그룹 명세와 초기 상태, 타임라인, 도구, need, 채점.

어댑터는 벤치마크 산출물을 읽어 이 계약으로 넘긴다(groups, initial_state, events). worldgen 4.2는 harness/
폴더를 읽고, SILO 등 자체 형식 벤치마크는 아래 공개 형식을 쓴다.

공개 형식 (SILO 픽스처)
    public/manifest.json            Manifest
    public/world_init.json          WorldInit
    public/rulebook.json            [RuleText]
    public/snapshot_day0/<g>.json   GroupSnapshot
    public/timeline.jsonl           TimelineEvent (cross 이외)
    public/work.jsonl               TimelineEvent (cross)
    private/gold.jsonl              GoldRecord   (실행 코드는 읽지 않음)
"""
from typing import Annotated, Literal

from pydantic import Field, JsonValue, model_validator

from ._base import Contract
from .card import AgentCard, GroupCard

StateClass = Literal["A", "B", "C", "D"]


# ─────────────────────────── 이력과 그룹 색인 ───────────────────────────
class HistoryEntry(Contract):
    seq: int = Field(ge=1)
    day: int                                    # 워밍업은 0 이하
    role: Literal["user", "assistant", "tool"]
    text: str
    tokens: int = Field(ge=0)
    entities: list[str]
    digest: str                                 # 결정·대상·범주형 값만, 수치 없음
    round: int | None = None                    # 하루 안 라운드 (워밍업은 worldgen transcripts의 round)
    order: int | None = None                    # 그룹 공통 순번 = WAL seq (실행 중 사건만. 워밍업은 공개 순번이 없어 None)


class IndexEntry(Contract):
    """그룹 색인 항목 (경계 모듈 전용). journal은 원문(H0), activity는 "누가 무엇을 처리" 흔적(H1)."""
    day: int
    agent: str
    text: str
    entities: list[str] = []                    # 색인 키: 조각이 언급하는 엔티티 전부 (worldgen 4.4)


class EgressRecord(Contract):
    """(엔티티, 속성) → 나간 요청과 결과."""
    day: int
    entity: str
    attr: str
    to_group: str
    question: str
    status: Literal["ok", "partial", "referral", "need_more", "error"]
    referral_to: str | None


# ─────────────────────────── 세계 상태 (DB · 규정) ───────────────────────────
class DbVersion(Contract):
    v: int = Field(ge=1)
    day: int                                    # 사건이 일어난 날
    db_day: int                                 # DB에 등록되는 날 (등록 지연)
    value: JsonValue

    @model_validator(mode="after")
    def _lag(self):
        if self.db_day < self.day:
            raise ValueError("db_day는 day보다 앞설 수 없다")
        return self


class DbRecord(Contract):
    """키 하나의 버전들. 등록 순서는 버전 순서와 무관하고 빈틈이 있을 수 있다. 현재값 = 등록된 최대 버전."""
    key: str
    versions: list[DbVersion] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique(self):
        vs = [x.v for x in self.versions]
        if len(vs) != len(set(vs)):
            raise ValueError(f"{self.key}: 같은 버전 번호가 두 번 등록됨")
        return self


class RuleText(Contract):
    """규정 본문 (공개). 파라미터는 private에만 있다."""
    id: str
    group: str
    body: str
    title: str | None = None


# ─────────────────────────── 그룹 명세와 초기 상태 ───────────────────────────
class MemberSpec(Contract):
    agent_id: str
    role: str
    card: AgentCard | None                      # swarm 워커 등 card가 없는 구성원은 None
    active: bool = True                         # 1일차 시작 시점에 활동 중인가 (떠난 사람의 이력도 그룹에 남는다)


class GroupSpec(Contract):
    id: str
    topology: str = "specialist"                # specialist | swarm
    members: list[MemberSpec] = Field(min_length=1)
    card: GroupCard
    card_targets: dict[str, str] = {}           # 역할 → card가 가리키는 에이전트 (Direct 디렉터리)

    @model_validator(mode="after")
    def _cards(self):
        if self.card.group != self.id:
            raise ValueError(f"{self.id}: 그룹 card의 group 불일치")
        ids = [m.agent_id for m in self.members]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.id}: 구성원 id 중복")
        for m in self.members:
            if m.card is not None and (m.card.group != self.id or m.card.occupant != m.agent_id):
                raise ValueError(f"{m.agent_id}: 에이전트 card의 group·occupant 불일치")
        if unknown := set(self.card_targets.values()) - set(ids):
            raise ValueError(f"{self.id}: card 대상이 구성원이 아님 {sorted(unknown)}")
        return self


class GroupSnapshot(Contract):
    """1일차 시작 시점의 그룹 상태."""
    group: str
    histories: dict[str, list[HistoryEntry]]    # agent id → 이력
    journal: list[IndexEntry] = []
    activity: list[IndexEntry] = []
    entity_index: dict[str, list[str]] = {}     # 엔티티 → 처리한 에이전트
    egress_log: list[EgressRecord] = []
    db: list[DbRecord] = []
    catalog: dict[str, JsonValue] = {}          # 그룹 마스터 데이터 (키 → 값)
    aliases: dict[str, list[str]] = {}          # 엔티티 id → 이름·별칭 (태깅·해소용)
    env: dict[str, JsonValue] = {}              # 벤치마크 고유 환경 상태

    @model_validator(mode="after")
    def _refs(self):
        for aid, hist in self.histories.items():
            seqs = [e.seq for e in hist]
            if any(a >= b for a, b in zip(seqs, seqs[1:])):
                raise ValueError(f"{aid}: 이력 seq가 증가하지 않음")
        keys = [r.key for r in self.db]
        if len(keys) != len(set(keys)):
            raise ValueError(f"{self.group}: DB 키 중복")
        return self


class GroupInit(GroupSnapshot):
    """어댑터 initial_state()의 반환: 스냅샷 + 그 그룹의 규정 본문."""
    rules: list[RuleText]


# ─────────────────────────── 타임라인 ───────────────────────────
class Slot(Contract):
    """닫힌 슬롯 하나. list는 순서 있는 배열, set은 순서 없는 배열(정규화 때 정렬). items는 원소 형식 명세
    (worldgen answer_types의 원소 형식 그대로: integer / boolean / enum(values) / string(format) / tuple(items))."""
    name: str
    type: Literal["int", "number", "enum", "id", "bool", "set", "list"]
    options: list[JsonValue] | None = None      # enum만
    nullable: bool = False
    items: dict[str, JsonValue] | None = None   # set·list의 원소 형식 (없으면 set은 문자열, list는 제한 없음)
    format: str | None = None                   # id 슬롯의 뜻 (id, department)
    note: str | None = None                     # 에이전트에게 보여 줄 설명

    @model_validator(mode="after")
    def _options(self):
        if (self.type == "enum") != (self.options is not None):
            raise ValueError(f"{self.name}: options는 enum 슬롯에만, 그리고 반드시 있어야 한다")
        if self.items is not None and self.type not in ("set", "list"):
            raise ValueError(f"{self.name}: items는 set·list 슬롯에만")
        return self


class OutputSchema(Contract):
    """과제의 닫힌 슬롯. 에이전트 출력은 이 형식으로 강제된다."""
    slots: list[Slot] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique(self):
        names = [s.name for s in self.slots]
        if len(names) != len(set(names)):
            raise ValueError("슬롯 이름 중복")
        return self


class DbWrite(Contract):
    """db_register 이벤트의 payload: 등록되는 DB 버전 하나."""
    key: str
    version: DbVersion


EventKind = Literal["db_register", "catalog", "transcript", "index", "spawn", "despawn",
                    "agent_leave", "agent_join", "local", "cross", "world"]

# 종류별로 반드시 있어야 하는 필드와 payload 키
_REQUIRED = {
    "db_register": ("group",), "catalog": ("group",), "transcript": ("agent",), "index": (),
    "spawn": ("agent", "group"), "despawn": ("agent",), "agent_leave": ("agent", "group"),
    "agent_join": ("agent", "group"), "local": ("agent", "group", "task_id"),
    "cross": ("agent", "group", "task_id", "text", "request", "output_schema"), "world": (),
}
_PAYLOAD = {
    "catalog": ("key", "value"), "transcript": ("role", "text", "tokens", "summary"), "index": ("entries",),
    "agent_join": ("role",),
}


class TimelineEvent(Contract):
    """seq 순서로 하나씩 실행되는 사건. cross만 에이전트가 수행하고, 나머지는 세계가 정한 대로 적용된다."""
    eid: str
    seq: int = Field(ge=1)
    day: int = Field(ge=1)
    round: int = Field(ge=0)                    # 0 = 날 시작, 1..3 = 작업 라운드, 4 = 하루 끝 정리
    kind: EventKind
    group: str | None = None
    agent: str | None = None
    task_id: str | None = None                  # cross: 과제 id, local: 로컬 작업 id
    text: str = ""                              # cross: 과제 문장 (surface)
    request: dict[str, JsonValue] | None = None # cross: 명시적 요청 파라미터 (검토 범위 등)
    entities: list[str] = []
    output_schema: OutputSchema | None = None
    payload: dict[str, JsonValue] = {}

    @model_validator(mode="after")
    def _by_kind(self):
        missing = [f for f in _REQUIRED[self.kind] if getattr(self, f) in (None, "")]
        if missing:
            raise ValueError(f"{self.eid}: {self.kind}에는 {missing}가 필요하다")
        if self.kind != "cross" and (self.output_schema is not None or self.request is not None):
            raise ValueError(f"{self.eid}: output_schema·request는 cross에만")
        if missing := [k for k in _PAYLOAD.get(self.kind, ()) if k not in self.payload]:
            raise ValueError(f"{self.eid}: {self.kind} payload에 {missing}가 필요하다")
        if self.kind == "db_register":
            DbWrite.model_validate(self.payload)
        return self


class ToolSpec(Contract):
    """벤치마크 고유 환경 도구. resources는 호출자 그룹 기준 자원 이름 (접근 표로 검사)."""
    name: str
    description: str
    parameters: dict[str, JsonValue]            # JSON Schema
    resources: list[str]


# ─────────────────────────── need와 채점 (공개 형식) ───────────────────────────
class DbSource(Contract):
    type: Literal["db"] = "db"
    key: str
    v: int = Field(ge=1)
    canary: str | None = None                   # 전달 버전 판정용 문자열


class DbQuerySource(Contract):
    type: Literal["db_query"] = "db_query"
    query: str
    result: JsonValue                           # 없음을 확인한 경우 "ABSENT"
    asof: int


class FragHolder(Contract):
    agent: str
    raw_window: bool
    digest: bool
    active: bool


class FragSource(Contract):
    type: Literal["frag"] = "frag"
    fid: str
    origin: Literal["operational", "db_pending"]
    holders: list[FragHolder] = Field(min_length=1)
    canary: str | None = None


class RuleSource(Contract):
    type: Literal["rule"] = "rule"
    id: str


NeedSource = Annotated[DbSource | DbQuerySource | FragSource | RuleSource, Field(discriminator="type")]


class Need(Contract):
    need_id: str
    semantic_key: str
    group: str
    role: str
    order: int = Field(ge=1)
    card_agent: str | None                      # card만 보고 고를 대상
    sources: list[NeedSource] = Field(min_length=1)
    state_class: StateClass | None = None       # 원격 need의 설계 등급 (로컬 need는 None)


class Verdict(Contract):
    task_id: str
    correct: bool                               # 닫힌 슬롯 전부 일치 (Acc_exact)
    slots: dict[str, bool]


class Manifest(Contract):
    benchmark: str
    world_hash: str
    seed: int
    days: int = Field(ge=1)
    generator: str                              # 생성기 이름·커밋
    tokenizer: str | None = None
    params: dict[str, JsonValue]


class WorldInit(Contract):
    benchmark: str
    groups: list[GroupSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique(self):
        ids = [g.id for g in self.groups]
        agents = [m.agent_id for g in self.groups for m in g.members]
        if len(ids) != len(set(ids)) or len(agents) != len(set(agents)):
            raise ValueError("그룹 또는 에이전트 id 중복")
        return self


class GoldRecord(Contract):
    task_id: str
    answer: dict[str, JsonValue]
    needs: list[Need] = []
    state_class: StateClass | None = None       # 작업 등급 = 가장 어려운 원격 need
    meta: dict[str, JsonValue] = {}             # 벤치마크 고유 (경로, 반사실, R 등급 등)
