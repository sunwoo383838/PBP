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
from .full_load import org_tool, search_memory_tool
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
                 embedder=None, reranker=None, format_retries: int = 1,
                 oracle_evidence: Path | None = None):
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
        full_load = cond.agent_tool == "search_memory"
        groups = [g.id for g in adapter.groups()]
        for tool in env_tools(self.stores) if env_tools else []:
            tools.register(org_tool(tool, groups) if full_load else tool)  # full_load: 조직 전체에 한 번에
        if cond.budget_bonus_calls and defaults.budget.calls is not None:   # [부록 retrieve] 요청자 호출 추가분
            defaults = defaults.model_copy(update={"budget": defaults.budget.model_copy(
                update={"calls": defaults.budget.calls + cond.budget_bonus_calls})})
        self.kernel = Kernel(seed=seed, condition=condition, guard=AccessGuard(access, condition), tools=tools,
                             stores=self.stores, agent_factory=agent_factory, hop_limit=params.hop_limit,
                             defaults=defaults, llm=llm)
        self.kernel.relay_max = cond.relay.max_asks if cond.relay else 0     # [부록 direct_relay]
        self.card_mode = cond.card_mode
        self._manifest = self._manifest_info(cond, retrieval, freeze, llm, embedder, reranker)
        self.kernel.budget_limit = cond.budget_limit
        self.kernel.timing_dir = Path(run_dir) / "timing"                  # 벽시계 기록 (결정성 계약 밖)
        if full_load:                                                      # 조직 전체 이력 검색: 게이트웨이와 같은 검색기
            if embedder is None or retrieval is None:
                raise ConfigError("full_load의 search_memory에는 임베더와 조회 설정(retrieval)이 필요하다")
            from gbg.retrieval.alias import AliasResolver
            from gbg.retrieval.hybrid import GroupRetriever
            retrievers = {g: GroupRetriever(self.stores, g, embedder, retrieval, reranker) for g in groups}
            resolvers = {g: AliasResolver(adapter.initial_state(g).aliases, embedder=embedder,
                                          embed_threshold=retrieval.alias.embed_threshold) for g in groups}
            tools.register(search_memory_tool(self.stores, retrievers, resolvers, lambda: self.kernel.task_cache))
        oracle_cond = cond.ingress is not None and cond.ingress.evidence == "oracle"
        if oracle_evidence is not None and not oracle_cond:                # 정답 조각은 retrieval_oracle에서만
            raise ConfigError(f"조건 '{condition}'에 oracle_evidence가 마운트돼 있다 (retrieval_oracle에서만 허용)")
        if oracle_cond and oracle_evidence is None:
            raise ConfigError("retrieval_oracle에는 oracle_evidence/ 마운트가 필요하다 (gbg.cli.export_oracle)")
        oracle = ({p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(oracle_evidence).glob("*.json"))}
                  if oracle_evidence is not None else None)
        if cond.ingress is not None or cond.sidecar is not None:            # 경계 조건: 그룹마다 경계 모듈 하나 (sidecar: 받은 에이전트에 붙는 모듈)
            if embedder is None or retrieval is None:
                raise ConfigError(f"조건 '{condition}'의 경계 모듈에는 임베더와 조회 설정(retrieval)이 필요하다")
            from gbg.agents.prompts import record_kinds
            from gbg.boundary.module import BoundaryModule
            from gbg.retrieval.alias import AliasResolver
            from gbg.retrieval.hybrid import GroupRetriever
            from gbg.stores.history import approx_tokens
            for g in adapter.groups():
                resolver = AliasResolver(adapter.initial_state(g.id).aliases, embedder=embedder,
                                         embed_threshold=retrieval.alias.embed_threshold)
                target = self.kernel.sidecars if cond.sidecar is not None else self.kernel.boundaries
                target[g.id] = BoundaryModule(
                    g.id, cond if cond.sidecar is None else cond.model_copy(update={"ingress": cond.sidecar}), retriever=GroupRetriever(self.stores, g.id, embedder, retrieval, reranker), resolver=resolver,
                    count=tokens or approx_tokens, format_retries=format_retries, oracle=oracle,
                    record_kinds=record_kinds(adapter.group_tools(g.id)) if hasattr(adapter, "group_tools") else ())

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

    def _manifest_info(self, cond, retrieval, freeze, llm, embedder, reranker) -> dict:
        """분석용 런 매니페스트 (manifest.json). run.json(재개 설정 비교용)과 분리하고 실행에는 쓰지 않는다."""
        import subprocess
        from gbg.contracts.freeze import retrieval_hash
        root = Path(__file__).resolve().parents[2]

        def git(*args):
            try:
                return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=10).stdout.strip()
            except Exception:
                return None
        scen = getattr(self.adapter, "manifest", None) or {}
        lp = getattr(llm, "params", None)
        return {"benchmark": self.adapter.name, "condition": self.condition,
                "condition_resolved": cond.model_dump(mode="json"), "seed": self.seed, "max_day": self.max_day,
                "kernel_params": self.params.model_dump(mode="json"),
                "task_budget": self.kernel.defaults.model_dump(mode="json"),
                "scenario": {k: scen.get(k) for k in ("world_hash", "generator", "seed", "params", "days")},
                "harness": {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", "gbg", "configs"))},
                "llm": {"mode": getattr(llm, "mode", None), "model_alias": getattr(llm, "model", None),
                        "params": lp.model_dump(mode="json") if lp is not None else None},
                "retrieval": {"params": retrieval.model_dump(mode="json") if retrieval is not None else None,
                              "params_sha256": retrieval_hash(retrieval) if retrieval is not None else None,
                              "freeze_sha256": getattr(freeze, "retrieval_params_sha256", None),
                              "embedder": getattr(embedder, "name", None) or type(embedder).__name__ if embedder else None,
                              "reranker": getattr(reranker, "name", None) or type(reranker).__name__ if reranker else None}}

    def _write_manifest(self):
        path = self.run_dir / "manifest.json"
        text = json.dumps(self._manifest, ensure_ascii=False, sort_keys=True, default=str)
        if not path.exists():
            path.write_text(text + "\n", encoding="utf-8")
        elif path.read_text(encoding="utf-8").strip() != text:            # 재개 때 달라졌으면 이력으로 남긴다
            with open(self.run_dir / "manifest_history.jsonl", "a", encoding="utf-8") as f:
                f.write(text + "\n")

    def run(self) -> str:
        """끝까지 실행하고 WAL 해시를 돌려준다."""
        self._check_config()
        self._write_manifest()
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
                for batch in self._batches(sorted(by_slot.get((day, rnd), []), key=lambda e: e.seq)):
                    before = len(events)
                    for drafts in asyncio.run(self._run_batch(day, rnd, batch)):    # 결과는 seq 순서로 반영
                        evs, s = k.number(day, rnd, drafts)
                        self._absorb(evs, s, events, side)                # 다음 묶음은 반영된 세계를 본다
                    if any(te.kind == "cross" for te in batch) and len(events) > before:
                        side.setdefault("obs/batches.jsonl", []).append(  # 분석 기록: 같은 세계를 본 동시 과제 묶음
                            {"seq": events[before].seq, "day": day, "round": rnd, "size": len(batch),
                             "tasks": [te.task_id for te in batch if te.kind == "cross"]})
                self._absorb([k.marker(day, rnd, len(events))], {}, events, side)
                self.wal.commit(events, side)
        return self.wal.hash()

    def _batches(self, items: list) -> list[list]:
        """seq 순서의 항목을 실행 묶음으로. parallel_tasks면 세계 사건 없이 이어지는 교차 과제를 한 묶음으로 동시에
        실행한다(앞 과제에 이어지는 과제는 그 앞 과제와 같은 묶음에 넣지 않는다). 세계 사건은 하나씩."""
        out: list[list] = []
        for te in items:
            prev = out[-1] if out else None
            if (self.params.parallel_tasks and te.kind == "cross" and prev and prev[-1].kind == "cross"
                    and (te.payload or {}).get("follows") not in {x.task_id for x in prev}):
                prev.append(te)
            else:
                out.append([te])
        return out

    async def _run_batch(self, day: int, rnd: int, batch: list) -> list:
        """묶음의 항목을 동시에 실행한다. 과제마다 실행 문맥(예산·도구 캐시)이 따로 복사되고, 묶음 안 과제는 묶음 시작
        시점의 세계를 본다(서로의 문답은 반영 전이라 보이지 않는다)."""
        if len(batch) == 1:
            return [await self.kernel.run_item(day, rnd, batch[0])]
        return list(await asyncio.gather(*(self.kernel.run_item(day, rnd, te) for te in batch)))

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
