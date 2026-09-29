"""실행 하나: 조건 하나 × 시나리오 하나를 1일부터 max_day까지 (교차 과제는 타임라인 순서, 같은 라운드에서 이어지는 과제는
kernel.parallel_tasks에 따라 동시에). 같은 출력 폴더로 다시 부르면 WAL 체크포인트(라운드 단위)에서 재개하고, 진행 중이던
라운드는 LLM 응답 캐시로 재생한다. 자동 재개는 supervise.py가 맡는다.

캐시: LLM 응답 캐시는 실행 폴더 안(llm_cache.sqlite). 임베딩·재정렬 캐시는 모든 실행이 같은 파일을 공유한다
(2026-09-30: 실행별 복사본은 같은 질의·문서의 점수를 실행마다 따로 계산해 조건 간에 소수점 차이가 생겨 되돌림.
먼저 저장된 값이 정본이고, 잠금은 SqliteStore의 재시도로 처리).

    uv run python -m gbg.cli.run_one CONDITION SCENARIO_DIR OUT_DIR --max-day 15 \
        --embed-cache EMB.sqlite --rerank-cache RERANK.sqlite [--tasks W-00001,W-00002] [--scripted]

--scripted: LLM을 부르지 않는 점검 모드. 모든 역할이 형식에 맞는 최소 응답을 결정적으로 낸다(질문 한 번 → 제출,
응답자는 missing, 게이트웨이는 첫 구성원 선택·빈 조립). 임베딩·재정렬은 실제로 부른다(캐시 사용).
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _default(schema: dict):
    if "anyOf" in schema:
        return None
    if "enum" in schema:
        return schema["enum"][0]
    return {"integer": 0, "number": 0, "string": "", "boolean": False, "array": []}[schema["type"]]


def _call(name: str, args: dict) -> dict:
    return {"content": "", "finish_reason": "tool_calls", "tool_calls": [{"name": name, "arguments": json.dumps(args)}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1}}


def scripted(req: dict) -> dict:
    """점검용 결정적 응답: 모든 역할의 도구 형식을 한 번씩 거친다."""
    tools = {t["function"]["name"]: t["function"] for t in req.get("tools", [])}
    msgs = req["messages"]
    system, user = msgs[0]["content"], msgs[1]["content"] if len(msgs) > 1 else ""
    first = len(msgs) == 2
    if "interpret" in tools:
        return _call("interpret", {"entities": [], "attribute": "requested information"})
    if "route" in tools:
        members = re.findall(r"^- (\S+) \|", user.split("Members:\n", 1)[1].split("\n\n", 1)[0], re.M) if "Members:\n" in user else []
        return _call("route", {"action": "select", "agents": members[:1], "items": []})
    if "answer" in tools:
        return _call("answer", {"additions": [], "conflicts": [], "proposals": [], "missing": ["not confirmed"]})
    if "dispatch" in tools:
        groups = re.findall(r"^- (\S+) \|", system.split("Groups you can ask:\n", 1)[-1], re.M)
        q = user.split("Question: ", 1)[-1].split("\n", 1)[0]
        return _call("dispatch", {"targets": [{"group": groups[0], "question": q}], "entity": "x", "attr": "x"})
    if "reply" in tools:
        return _call("reply", {"items": [], "missing": ["not found in my records"]})
    if "submit" in tools:
        if first:
            q = "What do your records show about this?"
            directory = system.split("<<DIRECTORY>>\n", 1)[-1]
            ids = re.findall(r"^- (\S+) \|", directory, re.M)
            if "ask_group" in tools and ids:
                return _call("ask_group", {"group": ids[0], "question": q})
            if "ask" in tools:
                return _call("ask", {"question": q, "purpose": "check"})
            if "ask_agent" in tools and ids:
                return _call("ask_agent", {"agent_id": ids[0], "question": q})
            if "search_memory" in tools:
                return _call("search_memory", {"query": "budget balance"})
        props = tools["submit"]["parameters"]["properties"]
        return _call("submit", {k: _default(v) for k, v in props.items()})
    return {"content": "", "finish_reason": "stop", "tool_calls": [], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("condition")
    ap.add_argument("scenario", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--max-day", type=int, required=True)
    ap.add_argument("--tasks", default=None, help="이 과제만 (그 앞의 세계 사건은 모두). 없으면 전부")
    ap.add_argument("--embed-cache", type=Path, required=True, help="공유 임베딩 캐시 (모든 실행이 같은 파일)")
    ap.add_argument("--rerank-cache", type=Path, required=True, help="공유 재정렬 캐시 (모든 실행이 같은 파일)")
    ap.add_argument("--run-seed", type=int, default=1)
    ap.add_argument("--model", default=None, help="params.yaml llm.models의 별칭 (없으면 llm.model)")
    ap.add_argument("--scripted", action="store_true")
    ap.add_argument("--configs", type=Path, default=ROOT / "configs")
    a = ap.parse_args(argv)

    from gbg.benchmarks.worldgen.adapter import WorldgenAdapter
    from gbg.contracts.access import load_access
    from gbg.contracts.conditions import load_conditions
    from gbg.contracts.params import load_params
    from gbg.kernel.runner import Runner
    from gbg.kernel.tools import ToolRegistry
    from gbg.llm.agent_loop import AgentRuntime, LLMAgent
    from gbg.llm.backend import LLMBackend
    from gbg.llm.cache import ResponseCache
    from gbg.llm.context_builder import ContextBuilder
    from gbg.llm.tokenizer import load_tokenizer
    from gbg.retrieval.embed import CachedEmbedder, DeepInfraEmbedder, EmbeddingCache
    from gbg.retrieval.rerank import CachedReranker, DeepInfraReranker, RerankCache

    P = load_params(a.configs / "params.yaml")
    conds = load_conditions(a.configs / "conditions.yaml")
    access = load_access(a.configs / "access.yaml", conds)
    tok = load_tokenizer(P.tokenizer)
    ad = WorldgenAdapter()
    ad.load(a.scenario / "harness")
    if a.tasks:
        keep = set(a.tasks.split(","))
        evs = list(ad.events())
        last = max(e.seq for e in evs if e.kind == "cross" and e.task_id in keep)
        ad._events = [e for e in evs if e.seq <= last and (e.kind != "cross" or e.task_id in keep)]

    a.out.mkdir(parents=True, exist_ok=True)
    caches = {"embed_cache.sqlite": a.embed_cache, "rerank_cache.sqlite": a.rerank_cache}   # 공유 캐시

    rt = AgentRuntime(conds[a.condition], ad.group_tools, ContextBuilder(tok.count, P.context.raw_window, P.context.summary),
                      P.agent.max_steps, P.agent.format_retries, P.agent.safety_steps, P.agent.responder_max_steps,
                      tuple(P.agent.responder_exclude_tools))
    llm = (LLMBackend(P.llm, mode="SCRIPTED", script=scripted) if a.scripted
           else LLMBackend(P.llm, mode="LIVE", model=a.model, cache=ResponseCache(a.out / "llm_cache.sqlite")))
    embedder = CachedEmbedder(DeepInfraEmbedder(P.llm, P.retrieval.embed_model), EmbeddingCache(caches["embed_cache.sqlite"]),
                              "LIVE", P.retrieval.embed_batch)
    reranker = CachedReranker(DeepInfraReranker(P.llm, P.retrieval.rerank_model), RerankCache(caches["rerank_cache.sqlite"]))
    t0 = time.monotonic()
    r = Runner(ad, condition=a.condition, seed=a.run_seed, run_dir=a.out, conditions=conds, access=access,
               tools=ToolRegistry(access), env_tools=ad.make_tools, agent_factory=lambda aid, g, role: LLMAgent(aid, rt),
               params=P.kernel, llm=llm, tokens=tok.count, max_day=a.max_day, retrieval=P.retrieval, embedder=embedder,
               reranker=reranker, format_retries=P.agent.format_retries)
    h = r.run()
    meta = a.out / "run_meta.json"
    prev = json.loads(meta.read_text()) if meta.exists() else {}
    meta.write_text(json.dumps({"condition": a.condition, "scenario": str(a.scenario), "max_day": a.max_day,
                                "wal_hash": h, "seconds_last_segment": round(time.monotonic() - t0, 1),
                                "segments": prev.get("segments", 0) + 1, "scripted": a.scripted,
                                "api_calls_last_segment": getattr(llm, "api_calls", None),
                                "embed_computed_last_segment": embedder.computed,
                                "rerank_computed_last_segment": reranker.computed}, indent=1))
    print("done", a.condition, h)


if __name__ == "__main__":
    sys.exit(main())
