"""가상 시계와 순차 실행.

하루는 라운드 0(날 시작), 작업 라운드 1..rounds_per_day, 하루 끝 정리 라운드(rounds_per_day + 1). 타임라인 사건을
seq 순서로 하나씩 실행하고, 과제 하나가 끝날 때까지 세계를 멈춘다(정답 기준 시점: 과제의 정답은 도착 seq의 세계로
계산돼 있다). cross만 에이전트가 수행하고, 나머지(DB 등록, catalog, 이력 줄, 색인, 로컬 작업 재생, 워커 생성·소멸,
이탈·합류, 공지)는 세계가 정한 대로 적용된다. 로컬 작업은 재생만 한다(결과는 이력 줄로 이미 렌더링돼 있다).
항목 하나가 끝나면 그 사건들에 seq를 매겨 커널 상태와 저장소 투영에 바로 반영하고, 라운드 끝에 WAL로 커밋한다.
병렬은 시드·조건 단위 프로세스로 한다.

순서 키: 항목 하나 안의 사건은 (작업 id, 호출 경로 번호...)로 정렬돼 seq를 받는다. 중첩 문답이 있어도 각 호출 경로가
자기 슬롯을 예약하므로 키가 결정적이다.

커널 상태(구성원, 활동 여부)와 저장소 투영은 번호가 매겨진 사건으로만 바뀐다(apply). 재개는 WAL을 apply로 재생한다.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from gbg.contracts.conditions import Defaults
from gbg.contracts.envelope import Request, Response
from gbg.contracts.events import Event, EventType
from gbg.contracts.schemas import HistoryEntry, TimelineEvent
from gbg.stores import Stores

from .access_guard import AccessGuard
from .budget import UNLIMITED, TaskBudget
from .errors import AgentFailure, FatalError
from .rng import NamedRNG
from .tools import ToolCall, ToolOutput, ToolRegistry

__all__ = ["Agent", "AgentContext", "AgentFactory", "AgentFailure", "Draft", "FatalError", "Kernel", "Span"]


class Agent(Protocol):
    async def work(self, ctx: "AgentContext", task: TimelineEvent) -> dict: ...
    async def respond(self, ctx: "AgentContext", request: Request) -> Response: ...


AgentFactory = Callable[[str, str, str], Agent]            # (agent id, group, role) → Agent


# ─────────────────────────── 사건 버퍼와 순서 키 ───────────────────────────
@dataclass
class Draft:
    key: tuple
    type: EventType
    actor: str
    payload: dict
    obs: list[tuple[str, dict]] = field(default_factory=list)   # (obs 파일 이름, 기록)


class Span:
    """순서 키 공간 하나. emit과 child가 차례로 슬롯을 받는다."""
    def __init__(self, drafts: list[Draft], prefix: tuple):
        self.drafts, self.prefix, self.n = drafts, prefix, 0

    def _slot(self) -> tuple:
        self.n += 1
        return self.prefix + (self.n,)

    def emit(self, type: EventType, actor: str, payload: dict, obs: list[tuple[str, dict]] | None = None):
        self.drafts.append(Draft(self._slot(), type, actor, payload, obs or []))

    def child(self) -> "Span":
        return Span(self.drafts, self._slot())


# ─────────────────────────── 에이전트가 보는 컨텍스트 ───────────────────────────
@dataclass
class AgentContext:
    kernel: "Kernel"
    span: Span
    agent_id: str
    group: str
    role: str
    day: int
    round: int
    task_id: str                                # 이 호출 경로의 원 작업
    hop: int                                    # 0 = 작업 수행, n = n번째 홉의 응답
    lineage: list[str]
    history: tuple[HistoryEntry, ...]           # 과제 시작 시점의 이력 (워밍업 + 반영분)
    serving: str | None = None                  # 응답 중인 요청의 rid (작업 수행이면 None)
    boundary: str | None = None                 # 경계 모듈이 부르는 중이면 그 그룹

    @property
    def rng(self):
        return self.kernel.rng.stream("agent", self.agent_id, self.day, self.round, *self.span.prefix[1:])

    @property
    def component(self) -> str:
        """예산 구성요소: 경계 모듈이면 boundary, 과제 담당자가 작업을 수행하는 중이면 requester, 그 밖은 responder."""
        if self.boundary is not None:
            return "boundary"
        b = self.kernel.budget
        return "requester" if self.serving is None and b is not None and self.agent_id == b.requester else "responder"

    @property
    def actor(self) -> str:
        return f"boundary:{self.boundary}" if self.boundary is not None else f"agent:{self.agent_id}"

    async def call_tool(self, name: str, **args) -> dict:
        return await self.kernel.call_tool(self, name, args)

    async def ask(self, to_agent: str, question: str, purpose: str | None = None, hop: int | None = None) -> Response:
        return await self.kernel.bus.ask(self, to_agent, question, purpose, hop)

    async def ask_group(self, group: str, question: str, purpose: str | None = None) -> Response:
        return await self.kernel.bus.ask_group(self, group, question, purpose)

    async def ask_egress(self, question: str, purpose: str | None) -> Response:
        return await self.kernel.bus.ask_egress(self, question, purpose)

    async def llm(self, messages: list[dict], tools: list[dict], step: int, composition: dict | None = None,
                  final: bool = False, estimate: int = 0, force: str | None = None):
        return await self.kernel.llm_call(self, messages, tools, step, composition, final, estimate, force)


# ─────────────────────────── 커널 ───────────────────────────
@dataclass
class Member:
    group: str
    role: str
    active: bool = True


class Kernel:
    def __init__(self, *, seed: int, condition: str, guard: AccessGuard, tools: ToolRegistry, stores: Stores,
                 agent_factory: AgentFactory, hop_limit: int, defaults: Defaults | None = None, llm=None):
        from .bus import Bus
        self.rng = NamedRNG(seed)
        self.condition, self.guard, self.tools, self.stores = condition, guard, tools, stores
        self.agent_factory = agent_factory
        self.defaults = defaults or UNLIMITED
        self.members: dict[str, Member] = {}
        self.agents: dict[str, Agent] = {}
        self.last_seq = 0
        self.bus = Bus(self, hop_limit)
        self.llm = llm
        self.budget: TaskBudget | None = None      # 실행 중인 과제의 예산 (순차 실행이라 하나뿐)
        self.boundaries: dict = {}                 # 그룹 → 경계 모듈 (경계 조건에서만)
        self.budget_limit = True                   # False면 과제 예산 상한 미적용 (참조 행 full_load)
        self.task_cache: dict = {}                 # 과제 안 도구 캐시 (과제마다 비운다)

    # ── 상태: 번호가 매겨진 사건으로만 바뀐다 ──
    def add_member(self, agent_id: str, group: str, role: str):
        self.members[agent_id] = Member(group, role)
        self.agents[agent_id] = self.agent_factory(agent_id, group, role)

    def apply(self, ev: Event):
        if ev.type == "agent_leave":
            self.members[ev.payload["agent"]].active = False
        elif ev.type == "agent_join" and ev.payload["agent"] not in self.members:
            p = ev.payload
            self.add_member(p["agent"], p["group"], p["role"])
        self.last_seq = ev.seq

    @staticmethod
    def participants(ev: Event) -> list[str]:
        out = []
        if ev.actor.startswith("agent:"):
            out.append(ev.actor.split(":", 1)[1])
        p = ev.payload
        if isinstance(p.get("agent"), str):
            out.append(p["agent"])
        for k in ("from_agent", "to_agent"):
            if isinstance(p.get(k), str):
                out.append(p[k])
        return list(dict.fromkeys(out))

    def groups_of(self, ev: Event) -> list[str]:
        gs = [self.members[a].group for a in self.participants(ev) if a in self.members]
        if ev.actor.startswith("boundary:"):
            gs.append(ev.actor.split(":", 1)[1])
        if isinstance(ev.payload.get("group"), str):
            gs.append(ev.payload["group"])
        return sorted(set(gs))

    def is_active(self, agent_id: str | None) -> bool:
        return agent_id in self.members and self.members[agent_id].active

    # ── 항목 하나 실행 (세계 이벤트 또는 과제) ──
    async def run_item(self, day: int, rnd: int, te: TimelineEvent) -> list[Draft]:
        drafts: list[Draft] = []
        if te.kind != "cross":
            self._world(Span(drafts, (0, te.seq)), te)
            return drafts
        span = Span(drafts, (1, te.task_id))
        span.emit("task_delivered", "kernel", {
            "task_id": te.task_id, "eid": te.eid, "agent": te.agent, "group": te.group, "text": te.text,
            "request": te.request, "entities": te.entities,
            "answer_slots": [s.name for s in te.output_schema.slots]})
        defaults = self.defaults if self.budget_limit else self.defaults.model_copy(   # 참조 행: 상한 없이 소비량만
            update={"budget": self.defaults.budget.model_copy(update={"calls": None, "tokens": None})})
        self.budget = TaskBudget(te.task_id, te.agent, defaults)
        self.task_cache = {}
        head = {"task_id": te.task_id, "agent": te.agent}
        try:
            if not self.is_active(te.agent):
                span.emit("answer", "kernel", {**head, "answer": None, "error": "agent_unavailable",
                                               "budget": self.budget.summary()})
                return drafts
            m = self.members[te.agent]
            ctx = AgentContext(self, span, te.agent, m.group, m.role, day, rnd, te.task_id, 0, [],
                               self.stores.history.entries(te.agent))
            actor = f"agent:{te.agent}"
            try:
                answer = await self.agents[te.agent].work(ctx, te)
                span.emit("answer", actor, {**head, "answer": answer, "budget": self.budget.summary()})
            except FatalError:
                raise
            except AgentFailure as e:
                span.emit("answer", actor, {**head, "answer": None, "error": e.reason, "budget": self.budget.summary()})
            except Exception as e:                                          # 에이전트 오류는 기록하고 런은 계속
                span.emit("answer", actor, {**head, "answer": None, "error": f"agent_exception:{type(e).__name__}",
                                            "budget": self.budget.summary()})
            return drafts
        finally:
            self.budget = None

    def _world(self, span: Span, te: TimelineEvent):
        p = te.payload
        if te.kind in ("agent_leave", "despawn"):
            group = te.group or (self.members[te.agent].group if te.agent in self.members else None)
            span.emit("agent_leave", "kernel", {"agent": te.agent, "group": group, "kind": te.kind,
                                                "handover": p.get("handover")})
        elif te.kind in ("agent_join", "spawn"):
            span.emit("agent_join", "kernel", {"agent": te.agent, "group": te.group, "kind": te.kind,
                                               "role": p.get("role", "worker"), "from": p.get("from"),
                                               "handover": p.get("handover"),
                                               "handover_notes": p.get("handover_notes", []), "entities": te.entities})
        else:                                                               # db_register · catalog · transcript · index · local · world
            span.emit("world_update", "kernel", {"eid": te.eid, "kind": te.kind, "group": te.group,
                                                 "agent": te.agent, "task_id": te.task_id, "data": p})

    # ── 도구 호출 (접근 중재) ──
    async def call_tool(self, ctx: AgentContext, name: str, args: dict) -> dict:
        span = ctx.span
        base = {"task_id": ctx.task_id, "agent": ctx.agent_id, "tool": name, "serving": ctx.serving}
        tool = self.tools.get(name)
        extra_obs: list[tuple[str, dict]] = []
        if tool is None:
            span.emit("tool_call", f"agent:{ctx.agent_id}", {**base, "args": args})
            result = {"ok": False, "error": "unknown_tool"}
        else:
            checks = [self.guard.check(f"agent:{ctx.agent_id}", ctx.group, r, args, name) for r in tool.resources]
            span.emit("tool_call", f"agent:{ctx.agent_id}", {**base, "args": args},
                      obs=[("access", {"day": ctx.day, "round": ctx.round, **c}) for c in checks])
            denied = [c for c in checks if not c["allowed"]]
            if denied:
                result = {"ok": False, "error": "access_denied", "resource": denied[0]["resource"],
                          "scope": denied[0]["scope"]}
            else:
                out = await tool.invoke(ToolCall(ctx.agent_id, ctx.group, ctx.day, ctx.round, dict(args)))
                if isinstance(out, ToolOutput):
                    extra_obs = [(n, {"day": ctx.day, "round": ctx.round, **base, **rec}) for n, rec in out.obs]
                    out = out.result
                result = {"ok": True, "result": out}
        span.emit("tool_result", "kernel", {**base, **result}, obs=extra_obs)
        return result

    # ── LLM 호출 (예산 · 기록) ──
    async def llm_call(self, ctx: AgentContext, messages: list[dict], tools: list[dict], step: int,
                       composition: dict | None, final: bool = False, estimate: int = 0, force: str | None = None):
        if self.llm is None:
            raise FatalError("LLM 백엔드 없이 LLM 에이전트를 실행함")
        component = ctx.component
        if final and component != "requester":
            raise FatalError("최종 답변 호출은 과제 담당자만 할 수 있다")
        self.budget.admit(final, estimate)                                  # 넘으면 BudgetExhausted
        res = await (self.llm.complete(messages, tools, force) if force else self.llm.complete(messages, tools))
        self.budget.charge(component, res.usage, composition, final)
        head = {"task_id": ctx.task_id, "agent": ctx.agent_id, "step": step, "component": component,
                "final": final, "serving": ctx.serving}
        obs = [("llm", {"day": ctx.day, "round": ctx.round, **head, "model": res.model, "key": res.key,
                        "cached": res.cached, "attempts": res.attempts, "latency_ms": res.latency_ms, "usage": res.usage,
                        "tokens": int(res.usage.get("prompt_tokens", 0)) + int(res.usage.get("completion_tokens", 0)),
                        "provider_cached_tokens": int(res.usage.get("provider_cached_tokens", 0) or 0),
                        "service_tier": res.usage.get("service_tier"), "seed": res.seed,
                        "cached_tool_result": bool((composition or {}).get("cached_tool_result"))})]
        if composition is not None:
            obs.append(("context_windows", {"day": ctx.day, "round": ctx.round, **head, **composition}))
        ctx.span.emit("llm_call", ctx.actor, {**head, "model": res.model, "key": res.key,
                                                             "usage": res.usage, "finish_reason": res.finish_reason,
                                                             "message": res.message}, obs=obs)
        return res

    # ── 번호 매기기와 커밋 ──
    def number(self, day: int, rnd: int, drafts: list[Draft]) -> tuple[list[Event], dict[str, list[dict]]]:
        """항목 하나의 사건을 순서 키로 정렬해 seq를 매기고, 그룹·obs 기록을 만든다."""
        events, side = [], {}
        seq = self.last_seq
        for d in sorted(drafts, key=lambda d: d.key):
            seq += 1
            ev = Event(seq=seq, day=day, round=rnd, type=d.type, actor=d.actor, payload=d.payload)
            events.append(ev)
            for name, rec in d.obs:
                side.setdefault(f"obs/{name}.jsonl", []).append({"seq": seq, **rec})
            for g in self.groups_of(ev):
                side.setdefault(f"groups/{g}.jsonl", []).append(ev.model_dump(mode="json"))
        return events, side

    def marker(self, day: int, rnd: int, n_events: int) -> Event:
        return Event(seq=self.last_seq + 1, day=day, round=rnd, type="round_commit", actor="kernel",
                     payload={"day": day, "round": rnd, "events": n_events})
