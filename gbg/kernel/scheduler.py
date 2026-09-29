"""가상 시계와 라운드 실행.

하루는 라운드 0(세계 이벤트)과 작업 라운드 1..rounds_per_day. 라운드마다 도착한 작업을 에이전트별 큐에 넣고,
서로 다른 에이전트는 asyncio로 동시에, 같은 에이전트는 순차로 실행한다.

결정론: 라운드 안의 사건은 버퍼에 모였다가 커밋 때 순서 키로 정렬돼 seq를 받는다. 순서 키는
(0, 타임라인 seq) 세계 이벤트, (1, 작업 id, n1, n2, ...) 작업과 그 작업에서 파생된 문답이다. 각 호출 경로가
자기 슬롯을 예약하므로 실행이 어떻게 섞여도 키가 같다.

커널 상태(구성원, 활동 여부)와 저장소 투영은 커밋된 사건으로만 바뀐다(apply). 재개는 WAL을 apply로 재생한다.
에이전트는 라운드 시작 시점의 이력을 본다: 라운드 중에는 투영이 바뀌지 않는다.
"""
import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from gbg.contracts.envelope import Request, Response
from gbg.contracts.events import Event, EventType
from gbg.contracts.schemas import HistoryEntry, TimelineEvent
from gbg.stores import Stores

from .access_guard import AccessGuard
from .rng import NamedRNG
from .tools import ToolCall, ToolOutput, ToolRegistry


class FatalError(Exception):
    """런 전체를 멈춰야 하는 오류 (REPLAY 캐시 미스, API 영구 실패). 커널이 삼키지 않는다."""


class AgentFailure(Exception):
    """에이전트가 작업을 끝내지 못함 (format_error, step_limit). 답 사건에 사유로 남고 런은 계속된다."""
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


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
    history: tuple[HistoryEntry, ...]           # 라운드 시작 시점의 이력 (워밍업 + 커밋분)

    @property
    def rng(self):
        return self.kernel.rng.stream("agent", self.agent_id, self.day, self.round, *self.span.prefix[1:])

    async def call_tool(self, name: str, **args) -> dict:
        return await self.kernel.call_tool(self, name, args)

    async def ask(self, to_agent: str, question: str, purpose: str | None = None) -> Response:
        return await self.kernel.bus.ask(self, to_agent, question, purpose)

    async def llm(self, messages: list[dict], tools: list[dict], step: int, composition: dict | None = None):
        return await self.kernel.llm_call(self, messages, tools, step, composition)


# ─────────────────────────── 커널 ───────────────────────────
@dataclass
class Member:
    group: str
    role: str
    active: bool = True


class Kernel:
    def __init__(self, *, seed: int, condition: str, guard: AccessGuard, tools: ToolRegistry, stores: Stores,
                 agent_factory: AgentFactory, hop_limit: int,
                 launch_order: Callable[[list[str]], list[str]] | None = None, llm=None):
        from .bus import Bus
        self.rng = NamedRNG(seed)
        self.condition, self.guard, self.tools, self.stores = condition, guard, tools, stores
        self.agent_factory, self.launch_order = agent_factory, launch_order
        self.members: dict[str, Member] = {}
        self.agents: dict[str, Agent] = {}
        self.last_seq = 0
        self.bus = Bus(self, hop_limit)
        self.llm = llm

    # ── 상태: 커밋된 사건으로만 바뀐다 ──
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

    # ── 라운드 실행 ──
    async def run_round(self, day: int, rnd: int, arrivals: list[TimelineEvent]) -> list[Draft]:
        drafts: list[Draft] = []
        queues: dict[str, list[tuple[TimelineEvent, Span]]] = {}
        for te in arrivals:
            if te.kind == "world":
                self._world(Span(drafts, (0, te.seq)), te)
                continue
            span = Span(drafts, (1, te.task_id))
            span.emit("task_delivered", "kernel", {
                "task_id": te.task_id, "eid": te.eid, "kind": te.kind, "agent": te.agent, "group": te.group,
                "text": te.text, "tool_results": [r.model_dump() for r in te.tool_results], "entities": te.entities,
                "disc": te.payload.get("disc")})
            if not self.is_active(te.agent):
                span.emit("answer", "kernel", {"task_id": te.task_id, "agent": te.agent, "answer": None,
                                               "error": "agent_unavailable"})
                continue
            queues.setdefault(te.agent, []).append((te, span))

        order = sorted(queues)
        if self.launch_order:
            order = self.launch_order(order)
        await asyncio.gather(*(self._drain(a, queues[a], day, rnd) for a in order))
        return drafts

    def _world(self, span: Span, te: TimelineEvent):
        if te.action == "agent_leave":
            span.emit("agent_leave", "kernel", {"agent": te.agent, "group": te.group})
            self.members[te.agent].active = False                          # 같은 라운드의 작업에 바로 반영
        elif te.action == "agent_join":
            p = te.payload
            span.emit("agent_join", "kernel", {"agent": te.agent, "group": te.group, "role": p["role"],
                                               "from": p.get("from"), "handover_notes": p.get("handover_notes", []),
                                               "entities": te.entities})
            self.add_member(te.agent, te.group, p["role"])
        else:                                                               # db_write · env: 저장소 투영은 Stage 2
            span.emit("world_update", "kernel", {"eid": te.eid, "action": te.action, "group": te.group,
                                                 "agent": te.agent, "data": te.payload})

    async def _drain(self, agent_id: str, queue, day: int, rnd: int):
        m = self.members[agent_id]
        for te, span in queue:
            ctx = AgentContext(self, span, agent_id, m.group, m.role, day, rnd, te.task_id, 0, [],
                               self.stores.history.entries(agent_id))
            try:
                answer = await self.agents[agent_id].work(ctx, te)
                span.emit("answer", f"agent:{agent_id}", {"task_id": te.task_id, "agent": agent_id, "answer": answer})
            except FatalError:
                raise
            except AgentFailure as e:
                span.emit("answer", f"agent:{agent_id}", {"task_id": te.task_id, "agent": agent_id, "answer": None,
                                                          "error": e.reason})
            except Exception as e:                                          # 에이전트 오류는 기록하고 런은 계속
                span.emit("answer", f"agent:{agent_id}", {"task_id": te.task_id, "agent": agent_id, "answer": None,
                                                          "error": f"agent_exception:{type(e).__name__}"})

    # ── 도구 호출 (접근 중재) ──
    async def call_tool(self, ctx: AgentContext, name: str, args: dict) -> dict:
        span = ctx.span
        base = {"task_id": ctx.task_id, "agent": ctx.agent_id, "tool": name}
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

    # ── LLM 호출 (기록) ──
    async def llm_call(self, ctx: AgentContext, messages: list[dict], tools: list[dict], step: int,
                       composition: dict | None):
        if self.llm is None:
            raise FatalError("LLM 백엔드 없이 LLM 에이전트를 실행함")
        res = await self.llm.complete(messages, tools)
        head = {"task_id": ctx.task_id, "agent": ctx.agent_id, "step": step}
        obs = [("llm", {"day": ctx.day, "round": ctx.round, **head, "model": res.model, "key": res.key,
                        "cached": res.cached, "attempts": res.attempts, "latency_ms": res.latency_ms, "usage": res.usage})]
        if composition is not None:
            obs.append(("context_windows", {"day": ctx.day, "round": ctx.round, **head, **composition}))
        ctx.span.emit("llm_call", f"agent:{ctx.agent_id}", {**head, "model": res.model, "key": res.key,
                                                             "usage": res.usage, "finish_reason": res.finish_reason,
                                                             "message": res.message}, obs=obs)
        return res

    # ── 커밋 ──
    def seal(self, day: int, rnd: int, drafts: list[Draft]) -> tuple[list[Event], dict[str, list[dict]]]:
        """버퍼를 순서 키로 정렬해 seq를 매기고, round_commit과 그룹·obs 기록을 만든다."""
        events, side = [], {}
        seq = self.last_seq
        for d in sorted(drafts, key=lambda d: d.key):
            seq += 1
            ev = Event(seq=seq, day=day, round=rnd, type=d.type, actor=d.actor, payload=d.payload)
            events.append(ev)
            for name, rec in d.obs:
                side.setdefault(f"obs/{name}.jsonl", []).append({"seq": seq, **rec})
        for ev in events:
            line = ev.model_dump(mode="json")
            for g in self.groups_of(ev):
                side.setdefault(f"groups/{g}.jsonl", []).append(line)
        events.append(Event(seq=seq + 1, day=day, round=rnd, type="round_commit", actor="kernel",
                            payload={"day": day, "round": rnd, "events": len(events)}))
        return events, side

