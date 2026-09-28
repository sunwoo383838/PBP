"""런 하나: 시나리오(어댑터) + 조건 + 시드. WAL 커밋이 체크포인트이고, 같은 run_dir로 다시 부르면 재개한다."""
import asyncio
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from gbg.contracts.access import AccessTable
from gbg.contracts.adapter import BenchmarkAdapter
from gbg.contracts.conditions import Condition, resolve_condition
from gbg.stores import Stores

from .access_guard import AccessGuard
from .scheduler import AgentFactory, Kernel
from .tools import Tool, ToolRegistry
from .wal import WAL, Fault


class RunConfigError(RuntimeError):
    """이미 있는 런 디렉터리를 다른 설정으로 재개하려 함."""


@dataclass(frozen=True)
class KernelParams:
    rounds_per_day: int = 3
    hop_limit: int = 4


class Runner:
    def __init__(self, adapter: BenchmarkAdapter, *, condition: str, seed: int, run_dir: Path,
                 conditions: dict[str, Condition], access: AccessTable, tools: ToolRegistry,
                 agent_factory: AgentFactory, env_tools: Callable[[Stores], list[Tool]] | None = None,
                 params: KernelParams = KernelParams(), fault: Fault | None = None,
                 launch_order: Callable[[list[str]], list[str]] | None = None):
        cond = resolve_condition(conditions, condition)
        self.adapter, self.condition, self.seed, self.params = adapter, condition, seed, params
        self.run_dir = Path(run_dir)
        self.wal = WAL(self.run_dir, fault)
        self.stores = Stores.from_adapter(adapter, card_mode=cond.card_mode, rounds_per_day=params.rounds_per_day)
        for tool in env_tools(self.stores) if env_tools else []:
            tools.register(tool)
        self.kernel = Kernel(seed=seed, condition=condition, guard=AccessGuard(access, condition), tools=tools,
                             stores=self.stores, agent_factory=agent_factory, hop_limit=params.hop_limit,
                             launch_order=launch_order)
        self.card_mode = cond.card_mode

    def _check_config(self):
        cfg = {"benchmark": self.adapter.name, "condition": self.condition, "card_mode": self.card_mode,
               "seed": self.seed, "params": asdict(self.params)}
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
        committed = self.wal.recover()
        for ev in committed:
            self._apply(ev)
        done = (committed[-1].day, committed[-1].round) if committed else (0, self.params.rounds_per_day)

        by_slot: dict[tuple[int, int], list] = {}
        for te in self.adapter.events():
            if not 0 <= te.round <= self.params.rounds_per_day:
                raise ValueError(f"{te.eid}: round {te.round}는 0..{self.params.rounds_per_day} 밖")
            by_slot.setdefault((te.day, te.round), []).append(te)
        last_day = max(d for d, _ in by_slot) if by_slot else 0

        for day in range(1, last_day + 1):
            for rnd in range(self.params.rounds_per_day + 1):
                if (day, rnd) <= done:
                    continue
                arrivals = sorted(by_slot.get((day, rnd), []), key=lambda e: e.seq)
                drafts = asyncio.run(k.run_round(day, rnd, arrivals))
                events, side = k.seal(day, rnd, drafts)
                for ev in events:                                         # 투영 갱신 → 그 obs 기록도 같은 커밋에
                    for name, rec in self._apply(ev):
                        side.setdefault(f"obs/{name}.jsonl", []).append(rec)
                self.wal.commit(events, side)
        return self.wal.hash()

    def _apply(self, ev):
        self.kernel.apply(ev)
        return self.stores.apply(ev)
