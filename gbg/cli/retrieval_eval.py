"""오프라인 회수율 평가 (LLM 없음). 채점기처럼 오프라인 도구라 private/(gold.jsonl, fragments.jsonl)을 읽는다.

    uv run python -m gbg.cli.retrieval_eval <scenario_dir>... [--embedder hash|api] [--reranker api|none] [--out report.json]

worldgen 4.2 시나리오(<dir>/harness, <dir>/private)에서, 각 과제가 도착하기 직전의 그룹 이력(워밍업 + 그때까지 재생된
이력 줄·색인)에 대해 원격 need의 결정 필수 조각이 증거 블록에 들어오는지 본다. 세계 재생은 스크립트 에이전트 실행의
WAL로 한다 (LLM 없음).
"""
import argparse
import asyncio
import json
from pathlib import Path

from gbg.benchmarks.worldgen.adapter import WorldgenAdapter
from gbg.contracts.freeze import DEFAULT_FREEZE, load_freeze, mark_frozen, retrieval_hash
from gbg.contracts.params import load_params
from gbg.retrieval.embed import CachedEmbedder, DeepInfraEmbedder, EmbeddingCache, HashEmbedder
from gbg.retrieval.eval_recall import build_cases, evaluate, run_new
from gbg.retrieval.rerank import CachedReranker, DeepInfraReranker, NullReranker, RerankCache
from gbg.retrieval.hybrid import GroupRetriever
from gbg.stores import Stores

ROOT = Path(__file__).resolve().parents[2]


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _world_events(adapter, params):
    """스크립트 에이전트로 한 번 실행해 WAL 사건을 얻는다 (세계 사건은 조건·에이전트와 무관하게 같다)."""
    import tempfile

    from gbg.agents.scripted import ScriptedAgent
    from gbg.contracts.access import load_access
    from gbg.contracts.conditions import load_conditions
    from gbg.contracts.events import Event
    from gbg.kernel.runner import Runner
    from gbg.kernel.tools import ToolRegistry
    conds = load_conditions(ROOT / "configs" / "conditions.yaml")
    access = load_access(ROOT / "configs" / "access.yaml", conds)
    with tempfile.TemporaryDirectory() as d:
        Runner(adapter, condition="direct", seed=0, run_dir=Path(d), conditions=conds, access=access,
               tools=ToolRegistry(access), agent_factory=lambda aid, g, role: ScriptedAgent(aid),
               params=params.kernel).run()
        return [Event.model_validate_json(x) for x in (Path(d) / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()
                if '"answer"' not in x and '"task_delivered"' not in x]


def _known_entities(stores, events, link_fields) -> dict[str, list[str]]:
    """평가 질의의 엔티티 표면형. 시나리오 전체(스냅샷 + 재생 사건)에서 모은다:
    catalog ID(이름·별칭 포함)와 연결 필드 값(품목·부서·공급사), DB 키의 엔티티, 색인 키(entities)."""
    names: dict[str, list[str]] = {}

    def catalog(key, value):
        eid = key.split("/", 1)[-1]
        names.setdefault(eid, [])
        if isinstance(value, dict):
            names[eid] += [v for k in ("name", "alias") if isinstance(v := value.get(k), str) and v not in names[eid]]
            for f in link_fields:
                if isinstance(value.get(f), str):
                    names.setdefault(value[f], [])

    def db_key(key):
        parts = key.split("/")
        if len(parts) == 4:
            names.setdefault(parts[2], [])

    for g in stores.catalog.dump():
        for key, value in stores.catalog.items(g):
            catalog(key, value)
    for g in stores.db.groups():
        for key in stores.db.keys(g):
            db_key(key)
    for g in stores.index.dump()["entity"]:
        for e in stores.index.entities(g):
            names.setdefault(e, [])
    for ev in events:
        if ev.type != "world_update":
            continue
        kind, data = ev.payload["kind"], ev.payload["data"]
        if kind == "catalog":
            catalog(data["key"], data["value"])
        elif kind == "db_register":
            db_key(data["key"])
        elif kind == "index":
            for x in data["entries"]:
                for e in x.get("entities", []):
                    names.setdefault(e, [])
    return names


THRESHOLD = 0.9                                                          # H0·H1 정확 조회 회수율, 개발 시드 평균


def _lines_of(scenario: Path):
    """조각 → 보유자 이력의 조각 줄 원문 (private/transcripts_full의 entries 위치)."""
    cache: dict[str, list[str]] = {}

    def lines(f: dict) -> list[str]:
        a = f["agent"]
        if a not in cache:
            p = scenario / "private" / "transcripts_full" / f"{a}.jsonl"
            cache[a] = [x["text"] for x in _jsonl(p)] if p.exists() else []
        return [cache[a][i] for i in f.get("entries", []) if i < len(cache[a])]
    return lines


def evaluate_scenario(scenario: Path, params, embedder, reranker=None, systems=None) -> dict:
    adapter = WorldgenAdapter()
    adapter.load(scenario / "harness")
    stores = Stores.from_adapter(adapter, card_mode="static", rounds_per_day=params.kernel.rounds_per_day)
    gold = _jsonl(scenario / "private" / "gold.jsonl")
    frags = {f["fid"]: f for f in _jsonl(scenario / "private" / "fragments.jsonl")}
    events = _world_events(adapter, params)
    cases, skipped = build_cases(gold, frags, _known_entities(stores, events, params.retrieval.catalog_link_fields),
                                 _lines_of(scenario))
    retrievers = {g: GroupRetriever(stores, g, embedder, params.retrieval, reranker) for g in {c.group for c in cases}}
    pos = {"i": 0}

    def advance(case):                                                   # 과제 도착 라운드 전까지의 사건 반영
        while pos["i"] < len(events) and (events[pos["i"]].day, events[pos["i"]].round) < (case.day, case.round):
            stores.apply(events[pos["i"]])
            pos["i"] += 1

    report = asyncio.run(evaluate(retrievers, cases, systems or {"evidence": run_new}, advance=advance))
    report.update(scenario=str(scenario), seed=adapter.manifest.get("params", {}).get("seed"), skipped=skipped)
    return report


def criterion(reports: list[dict]) -> dict:
    """H0·H1 정확 조회 회수율의 개발 시드 평균으로 판정한다 (시드별 회수율의 단순 평균). H2는 보고만."""
    per = {d: [(r["systems"]["index"]["by_disc"].get(d) or {}).get("recall") for r in reports] for d in ("H0", "H1", "H2")}
    mean = {d: round(sum(v) / len(v), 4) if v and None not in v else None for d, v in per.items()}
    return {"per_seed": per, "mean": mean, "threshold": THRESHOLD,
            "pass": all(mean[d] is not None and mean[d] >= THRESHOLD for d in ("H0", "H1"))}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("scenarios", type=Path, nargs="+", help="개발 시드 시나리오 디렉터리들")
    ap.add_argument("--embedder", choices=["hash", "api"], default="api")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "gbg" / "embeddings.sqlite")
    ap.add_argument("--reranker", choices=["api", "none"], default="api")
    ap.add_argument("--rerank-cache", type=Path, default=Path.home() / ".cache" / "gbg" / "rerank.sqlite")
    ap.add_argument("--params", type=Path, default=ROOT / "configs" / "params.yaml")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--freeze", action="store_true",
                    help="개발 시드 전부에서 기준을 통과하면 조회 설정 해시를 configs/retrieval_freeze.yaml에 적는다")
    ap.add_argument("--freeze-file", type=Path, default=DEFAULT_FREEZE)
    args = ap.parse_args(argv)

    params = load_params(args.params)
    inner = HashEmbedder() if args.embedder == "hash" else DeepInfraEmbedder(params.llm, params.retrieval.embed_model)
    embedder = CachedEmbedder(inner, EmbeddingCache(args.cache), "LIVE", params.retrieval.embed_batch)
    rr = params.retrieval
    reranker = (CachedReranker(DeepInfraReranker(params.llm, rr.rerank_model), RerankCache(args.rerank_cache))
                if args.reranker == "api" and rr.rerank_model else NullReranker())
    reports = [evaluate_scenario(sc, params, embedder, reranker) for sc in args.scenarios]
    # 조회 설정은 개발 시드에서 동결한다: 판정에 쓴 설정의 해시를 남겨 평가 시드 실행과 대조한다
    frozen = retrieval_hash(params.retrieval)
    out = {"embedder": embedder.name, "retrieval_params_sha256": frozen, "criterion": criterion(reports),
           "scenarios": reports}
    summary = [{"scenario": r["scenario"], "cases": r["cases"], "skipped": r["skipped"],
                **{m: {k: v for k, v in s.items() if k != "rows"} for m, s in r["systems"].items()}} for r in reports]
    print(json.dumps({"embedder": embedder.name, "retrieval_params_sha256": frozen, "scenarios": summary,
                      "criterion": out["criterion"]}, ensure_ascii=False, indent=1))
    if args.out:
        args.out.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.freeze:
        freeze = load_freeze(args.freeze_file)
        seeds = [r["seed"] for r in reports]
        if not out["criterion"]["pass"]:
            raise SystemExit("동결 거부: 개발 시드 평균이 기준에 못 미친다")
        if sorted(set(seeds)) != sorted(freeze.dev_seeds) or any(s in freeze.eval_seeds for s in seeds):
            raise SystemExit(f"동결 거부: 개발 시드 전부({freeze.dev_seeds})로만 판정해야 한다 (받은 시드 {sorted(set(seeds))})")
        print(f"조회 설정 동결: {mark_frozen(args.freeze_file, params.retrieval)}")


if __name__ == "__main__":
    main()
