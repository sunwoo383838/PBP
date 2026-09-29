"""런 하나: 시나리오(어댑터) + 조건 + 시드. WAL 커밋이 체크포인트이고, 같은 run_dir로 다시 부르면 재개한다."""
import asyncio
import json
from collections.abc import Callable
from pathlib import Path

from gbg.contracts.access import AccessTable
from gbg.contracts.adapter import BenchmarkAdapter
from gbg.contracts.conditions import Condition, ConfigError, resolve_condition
from gbg.contracts.freeze import DEFAULT_FREEZE, FreezeError, RetrievalFreeze, check_frozen, load_freeze
from gbg.contracts.params import KernelParams, RetrievalParams
from gbg.stores import Stores

from .access_guard import AccessGuard
from .full_load import all_groups_tool, load_history_tool
from .scheduler import AgentFactory, Kernel
from .tools import Tool, ToolRegistry
from .wal import WAL, Fault


class RunConfigError(RuntimeError):
    """이미 있는 런 디렉터리를 다른 설정으로 재개하려 함."""


class Runner:
    def __init__(self, adapter: BenchmarkAdapter, *, condition: str, seed: int, run_dir: Path,
                 conditions: dict[str, Condition], access: AccessTable, tools: ToolRegistry,
                 agent_factory: AgentFactory, env_tools: Callable[[Stores], list[Tool]] | None = None,
                 params: KernelParams = KernelParams(), fault: Fault | None = None, llm=None,
                 tokens: Callable[[str], int] | None = None, max_day: int | None = None,
                 retrieval: RetrievalParams | None = None, freeze: RetrievalFreeze | None = None,
                 embedder=None, format_retries: int = 1, full_load_tokens: int = 40000):
        freeze = freeze or load_freeze(DEFAULT_FREEZE)                     # 평가 시드는 동결된 조회 설정으로만
        seed_of = (getattr(adapter, "manifest", None) or {}).get("params", {}).get("seed")
        try:
            check_frozen(freeze, seed_of, retrieval)
        except FreezeError as e:
            raise ConfigError(str(e)) from e
        cond = resolve_condition(conditions, condition)
        if cond.blocked:
            raise ConfigError(f"조건 '{condition}'은 실행할 수 없다: {cond.blocked}")
        defaults = getattr(conditions, "defaults", None)
        if defaults is None:
            raise ConfigError("조건 설정에 defaults(과제 예산)가 없다: load_conditions로 읽은 ConditionSet을 넘긴다")
        self.adapter, self.condition, self.seed, self.params = adapter, condition, seed, params
        self.run_dir = Path(run_dir)
        self.wal = WAL(self.run_dir, fault)
        extra = {"tokens": tokens} if tokens else {}
        self.stores = Stores.from_adapter(adapter, card_mode=cond.card_mode, rounds_per_day=params.rounds_per_day,
                                          responder_session=cond.responder_session, **extra)
        self.max_day = max_day
        full_load = cond.agent_tool == "load_group_history"
        for tool in env_tools(self.stores) if env_tools else []:
            tools.register(all_groups_tool(tool) if full_load else tool)   # full_load: 모든 그룹에 같은 도구
        self.kernel = Kernel(seed=seed, condition=condition, guard=AccessGuard(access, condition), tools=tools,
                             stores=self.stores, agent_factory=agent_factory, hop_limit=params.hop_limit,
                             defaults=defaults, llm=llm)
        self.card_mode = cond.card_mode
        self.kernel.budget_limit = cond.budget_limit
        if full_load:
            from gbg.stores.history import approx_tokens
            tools.register(load_history_tool(self.stores, tokens or approx_tokens, full_load_tokens,
                                             lambda: self.kernel.task_cache))
        if cond.ingress is not None:                                       # 경계 조건: 그룹마다 경계 모듈 하나
            if embedder is None or retrieval is None:
                raise ConfigError(f"조건 '{condition}'의 경계 모듈에는 임베더와 조회 설정(retrieval)이 필요하다")
            from gbg.boundary.module import BoundaryModule
            from gbg.retrieval.alias import AliasResolver
            from gbg.retrieval.hybrid import GroupRetriever
            from gbg.stores.history import approx_tokens
            for g in adapter.groups():
                resolver = AliasResolver(adapter.initial_state(g.id).aliases, embedder=embedder,
                                         embed_threshold=retrieval.alias.embed_threshold)
                self.kernel.boundaries[g.id] = BoundaryModule(
                    g.id, cond, retriever=GroupRetriever(self.stores, g.id, embedder, retrieval), resolver=resolver,
                    count=tokens or approx_tokens, format_retries=format_retries)

    def _check_config(self):
        cfg = {"benchmark": self.adapter.name, "condition": self.condition, "card_mode": self.card_mode,
               "seed": self.seed, "params": self.params.model_dump(), "defaults": self.kernel.defaults.model_dump()}
        path = self.run_dir / "run.json"
        if path.exists():
            old = json.loads(path.read_text(encoding="utf-8"))
            if old != cfg:
                raise RunConfigError(f"{self.run_dir}: 기존 런 설정 {old}와 다름 {cfg}")
        else:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(cfg, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    def run(self) -> str:
        """끝까지 실행하고 WAL 해시를 돌려준다."""
        self._check_config()
        k = self.kernel
        for g in self.adapter.groups():
            for m in g.members:
                k.add_member(m.agent_id, g.id, m.role)
                k.members[m.agent_id].active = m.active
        committed = self.wal.recover()
        for ev in committed:
            self._apply(ev)
        done = (committed[-1].day, committed[-1].round) if committed else (0, self.params.rounds_per_day)

        last_round = self.params.rounds_per_day + 1                       # 하루 끝 정리 라운드
        by_slot: dict[tuple[int, int], list] = {}
        prev = None
        for te in self.adapter.events():                                  # seq 순서
            if not 0 <= te.round <= last_round:
                raise ValueError(f"{te.eid}: round {te.round}는 0..{last_round} 밖")
            if prev is not None and (te.seq <= prev.seq or (te.day, te.round) < (prev.day, prev.round)):
                raise ValueError(f"{te.eid}: seq 순서와 (day, round) 순서가 어긋남")
            by_slot.setdefault((te.day, te.round), []).append(te)
            prev = te
        last_day = max(d for d, _ in by_slot) if by_slot else 0
        if self.max_day is not None:
            last_day = min(last_day, self.max_day)

        for day in range(1, last_day + 1):
            for rnd in range(last_round + 1):
                if (day, rnd) <= done:
                    continue
                events: list = []
                side: dict[str, list[dict]] = {}
                for te in sorted(by_slot.get((day, rnd), []), key=lambda e: e.seq):   # seq 순서로 하나씩
                    drafts = asyncio.run(k.run_item(day, rnd, te))
                    evs, s = k.number(day, rnd, drafts)
                    self._absorb(evs, s, events, side)                    # 다음 항목은 반영된 세계를 본다
                self._absorb([k.marker(day, rnd, len(events))], {}, events, side)
                self.wal.commit(events, side)
        return self.wal.hash()

    def _absorb(self, evs, s, events, side):
        for name, recs in s.items():
            side.setdefault(name, []).extend(recs)
        for ev in evs:
            for name, rec in self._apply(ev):                             # 투영 갱신의 obs 기록도 같은 커밋에
                side.setdefault(f"obs/{name}.jsonl", []).append(rec)
            events.append(ev)

    def _apply(self, ev):
        self.kernel.apply(ev)
        return self.stores.apply(ev)
