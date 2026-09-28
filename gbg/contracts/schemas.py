"""핵심 스키마: 이력, 그룹 명세와 초기 상태, 타임라인, 도구, need, 채점, 시나리오 파일.

시나리오 디렉터리 (벤치마크 공통 형식)
    public/manifest.json            Manifest
    public/world_init.json          WorldInit
    public/rulebook.json            [RuleText]  (본문만)
    public/snapshot_day0/<g>.json   GroupSnapshot
    public/timeline.jsonl           TimelineEvent (local | world)
    public/work.jsonl               TimelineEvent (cross, 도착 시 담당자에게만)
    private/gold.jsonl              GoldRecord   (실행 코드는 읽지 않음)
    private/rulebook_params.json    {rule id: 파라미터}
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


class ActivityRecord(Contract):
    """엔티티 → 최근 처리자 (H1 흔적). 그룹 내부 전용."""
    entity: str
    agent: str
    seq: int = Field(ge=1)                      # 그 에이전트 이력의 항목
    day: int
    role: str


class JournalRecord(Contract):
    """엔티티 → H0 원문 항목."""
    entity: str
    agent: str
    seq: int = Field(ge=1)


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
    key: str
    versions: list[DbVersion] = Field(min_length=1)

    @model_validator(mode="after")
    def _ordered(self):
        if [x.v for x in self.versions] != list(range(1, len(self.versions) + 1)):
            raise ValueError(f"{self.key}: 버전 번호는 1부터 연속이어야 한다")
        if any(a.day > b.day for a, b in zip(self.versions, self.versions[1:])):
            raise ValueError(f"{self.key}: 버전의 day가 역전됨")
        return self


class RuleText(Contract):
    """규정 본문 (공개). 파라미터는 private/rulebook_params.json."""
    id: str
    group: str
    body: str


# ─────────────────────────── 그룹 명세와 초기 상태 ───────────────────────────
class MemberSpec(Contract):
    agent_id: str
    role: str
    card: AgentCard


class GroupSpec(Contract):
    id: str
    members: list[MemberSpec] = Field(min_length=1)
    card: GroupCard

    @model_validator(mode="after")
    def _cards(self):
        if self.card.group != self.id:
            raise ValueError(f"{self.id}: 그룹 card의 group 불일치")
        for m in self.members:
            if m.card.group != self.id or m.card.occupant != m.agent_id:
                raise ValueError(f"{m.agent_id}: 에이전트 card의 group·occupant 불일치")
        if len({m.agent_id for m in self.members}) != len(self.members):
            raise ValueError(f"{self.id}: 구성원 id 중복")
        return self


class GroupSnapshot(Contract):
    """snapshot_day0/<group>.json: 1일차 시작 시점의 그룹 상태."""
    group: str
    histories: dict[str, list[HistoryEntry]]    # agent id → 이력
    activity: list[ActivityRecord]
    journal: list[JournalRecord]
    egress_log: list[EgressRecord]
    db: list[DbRecord] = []
    aliases: dict[str, list[str]] = {}          # 엔티티 id → 별칭 (태깅용)
    env: dict[str, JsonValue] = {}              # 벤치마크 고유 환경 상태 (환경 도구가 읽음)

    @model_validator(mode="after")
    def _refs(self):
        for aid, hist in self.histories.items():
            seqs = [e.seq for e in hist]
            if any(a >= b for a, b in zip(seqs, seqs[1:])):
                raise ValueError(f"{aid}: 이력 seq가 증가하지 않음")
        have = {(aid, e.seq) for aid, hist in self.histories.items() for e in hist}
        for r in [*self.activity, *self.journal]:
            if (r.agent, r.seq) not in have:
                raise ValueError(f"{self.group}: 색인이 없는 이력 항목을 가리킴 ({r.agent}, {r.seq})")
        keys = [r.key for r in self.db]
        if len(keys) != len(set(keys)):
            raise ValueError(f"{self.group}: DB 키 중복")
        return self


class GroupInit(GroupSnapshot):
    """어댑터 initial_state()의 반환: 스냅샷 + 그 그룹의 규정 본문."""
    rules: list[RuleText]


# ─────────────────────────── 타임라인 ───────────────────────────
class Slot(Contract):
    name: str
    type: Literal["enum", "number", "id", "bool", "set", "list"]
    options: list[str] | None = None            # enum만
    nullable: bool = False

    @model_validator(mode="after")
    def _options(self):
        if (self.type == "enum") != (self.options is not None):
            raise ValueError(f"{self.name}: options는 enum 슬롯에만, 그리고 반드시 있어야 한다")
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
    """action=db_write 세계 이벤트의 payload: 시나리오가 정한 DB 버전 하나."""
    key: str
    version: DbVersion


class RenderedToolResult(Contract):
    tool: str
    text: str


class TimelineEvent(Contract):
    eid: str
    seq: int = Field(ge=1)                      # 완전 정렬 순서 = (day, round, seq)
    day: int = Field(ge=1)
    round: int = Field(ge=0)                    # 0 = 날 시작(세계 이벤트), 1.. = 작업 라운드
    kind: Literal["local", "cross", "world"]
    group: str
    agent: str | None = None                    # 작업 담당자 또는 세계 이벤트 대상
    task_id: str | None = None
    text: str = ""                              # 렌더링 원문 (과제 문장)
    tool_results: list[RenderedToolResult] = [] # 로컬 작업의 도구 결과 원문
    entities: list[str] = []
    output_schema: OutputSchema | None = None
    action: Literal["agent_leave", "agent_join", "db_write", "env"] | None = None
    payload: dict[str, JsonValue] = {}

    @model_validator(mode="after")
    def _by_kind(self):
        if self.kind in ("local", "cross"):
            if not (self.task_id and self.agent and self.text and self.output_schema):
                raise ValueError(f"{self.eid}: 작업에는 task_id, agent, text, output_schema가 필요하다")
            if self.action is not None:
                raise ValueError(f"{self.eid}: 작업에는 action이 없다")
        else:
            if self.action is None or self.task_id is not None or self.output_schema is not None:
                raise ValueError(f"{self.eid}: 세계 이벤트는 action만 갖는다")
            if self.action in ("agent_leave", "agent_join") and not self.agent:
                raise ValueError(f"{self.eid}: {self.action}에는 agent가 필요하다")
            if self.action == "db_write":
                DbWrite.model_validate(self.payload)
        return self


class ToolSpec(Contract):
    """벤치마크 고유 환경 도구. resources는 호출자 그룹 기준 자원 이름 (접근 표로 검사)."""
    name: str
    description: str
    parameters: dict[str, JsonValue]            # JSON Schema
    resources: list[str]


# ─────────────────────────── need와 채점 ───────────────────────────
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


# ─────────────────────────── 시나리오 파일 ───────────────────────────
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

