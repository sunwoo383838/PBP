"""오프라인 회수율 평가 (LLM 없음). 채점기처럼 오프라인 도구라 private/gold.jsonl을 읽는다.

    uv run python -m gbg.cli.retrieval_eval <scenario_dir> [--embedder hash|api] [--cache PATH] [--out report.json]

시나리오 공개분의 워밍업 스냅샷(1일차 시작 시점) 이력에 대해, 원격 need의 조각이 증거 블록에 들어오는지 본다.
"""
import argparse
import asyncio
import json
from pathlib import Path

from gbg.benchmarks.silo.adapter import SiloAdapter
from gbg.benchmarks.worldgen.adapter import WorldgenAdapter
from gbg.contracts.params import load_params
from gbg.contracts.schemas import GoldRecord, Manifest
from gbg.retrieval.embed import CachedEmbedder, DeepInfraEmbedder, EmbeddingCache, HashEmbedder
from gbg.retrieval.eval_recall import build_cases, evaluate
from gbg.retrieval.hybrid import GroupRetriever
from gbg.stores import Stores

ADAPTERS = {"worldgen": WorldgenAdapter, "silo": SiloAdapter}
ROOT = Path(__file__).resolve().parents[2]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", type=Path)
    ap.add_argument("--embedder", choices=["hash", "api"], default="api")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "gbg" / "embeddings.sqlite")
    ap.add_argument("--params", type=Path, default=ROOT / "configs" / "params.yaml")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    params = load_params(args.params)
    manifest = Manifest.model_validate_json((args.scenario / "public" / "manifest.json").read_text(encoding="utf-8"))
    adapter = ADAPTERS[manifest.benchmark]()
    adapter.load(args.scenario / "public")
    gold = [GoldRecord.model_validate_json(x)
            for x in (args.scenario / "private" / "gold.jsonl").read_text(encoding="utf-8").splitlines() if x]
    stores = Stores.from_adapter(adapter, card_mode="static", rounds_per_day=params.kernel.rounds_per_day)
    inner = HashEmbedder() if args.embedder == "hash" else DeepInfraEmbedder(params.llm, params.retrieval.embed_model)
    embedder = CachedEmbedder(inner, EmbeddingCache(args.cache), "LIVE", params.retrieval.embed_batch)
    tasks = {e.task_id: e for e in adapter.events() if e.kind != "world"}
    cases, skipped = build_cases(stores, tasks, gold, {g: adapter.initial_state(g).aliases for g in stores.env})
    retrievers = {g: GroupRetriever(stores, g, embedder, params.retrieval) for g in {c.group for c in cases}}
    report = asyncio.run(evaluate(retrievers, cases))
    report.update(skipped=skipped, embedder=embedder.name, world_hash=manifest.world_hash)
    summary = {m: {"recall": v["recall"], "by_disc": v["by_disc"], "by_day": v["by_day"]} for m, v in report["modes"].items()}
    print(json.dumps({"cases": report["cases"], "skipped": skipped, **summary}, ensure_ascii=False, indent=1))
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
