"""참조 행 full_load: 권한 분할이 없는 단일 에이전트. 조직의 모든 기록을 자기 기억처럼 쓴다 (2026-09-29 재정의).

어느 그룹에 무엇이 있는지 고르는 일(라우팅)을 에이전트에게 넘기지 않는다: 도구에 group 인자가 없다.

    - DB·목록 조회(org_tool): 같은 도구를 모든 그룹에 대해 실행하고 합친다. 엔티티 이름·별칭·ID를 받으면 모든 그룹의
      해당 기록을 돌려주고, 결과마다 출처 그룹만 표시한다.
    - 규정: 전 그룹 규정을 system에 넣는다 (agent_loop).
    - 이력(search_memory(query)): 조직 전체 이력(떠난 구성원, 요청자 자기 그룹 포함)을 게이트웨이와 같은 방식으로 검색한다
      (에피소드 단위, BM25 + bge-m3 RRF, 리랭커, 같은 증거 상한 하나). 엔티티는 게이트웨이의 결정적 단계와 같다(별칭표
      태깅 + 그룹 색인의 엔티티 키). 표시는 에피소드마다 "[E#] 그룹 · 에이전트 · day · [Task] 제목 · entities: 키".
      같은 과제 안에서 같은 질의를 다시 부르면 캐시(도구 실행만 생략, 결과 토큰은 그대로 센다).
    - 예산: 다른 조건과 같은 과제 예산을 적용한다(조건 설정 budget_limit 기본값).
"""
import copy
import re

from gbg.contracts.card import public_id
from gbg.contracts.schemas import ToolSpec
from gbg.retrieval.evidence import org_evidence
from gbg.retrieval.normalize import normalize

from .tools import Resource, Tool, ToolCall, ToolOutput

ORG_HINTS = {
    "NOT_FOUND": "No entity with this name or ID has a record of this type anywhere in the organization's database. "
                 "Try entity.search, or search_memory for records that are only in the history.",
    "NO_RECORD": "The entity exists, but no record of this type is registered for it as of today (for example, no "
                 "goods receipt has been registered). Report that no record is registered.",
    "INVALID_TYPE": "Use one of the record types listed in the tool definition.",
}
_ORDER = ("NO_RECORD", "NOT_FOUND", "INVALID_TYPE")                     # 모든 그룹이 빗나갔을 때 보일 상태의 우선순위


def org_tool(tool: Tool, groups: list[str]) -> Tool:
    """같은 도구를 모든 그룹에 대해 실행해 합친다. 자원 확인은 조직 전체(자기 그룹 + 다른 그룹)를 대상으로 한다."""
    resources = tuple(Resource(r.name, r.action, target="*") for r in tool.resources)

    async def fn(call: ToolCall):
        hits, misses, obs = [], [], []
        for g in groups:
            out = await tool.invoke(ToolCall(call.agent, g, call.day, call.round, dict(call.args)))
            vis = out.result if isinstance(out, ToolOutput) else out
            obs += [(n, {**rec, "org": True}) for n, rec in (out.obs if isinstance(out, ToolOutput) else [])]
            status = vis.get("status") if isinstance(vis, dict) else None
            if status in ("HIT", "AMBIGUOUS"):
                hits.append((g, vis))
            else:
                misses.append(status)
        if tool.name == "entity.search" and hits:                        # 엔티티 목록은 엔티티마다 한 번, 그룹 표시
            seen: dict[str, dict] = {}
            for g, vis in hits:
                for e in vis.get("entities", []):
                    seen.setdefault(e["entity"], {**e, "groups": []})["groups"].append(g)
            return ToolOutput({"status": "HIT", "entities": list(seen.values()),
                               "truncated": any(v.get("truncated") for _, v in hits)}, obs)
        if hits:
            return ToolOutput({"status": "HIT", "results": [{"group": g, **{k: v for k, v in vis.items()
                                                                            if k not in ("hint",)}}
                                                            for g, vis in hits]}, obs)
        status = next((s for s in _ORDER if s in misses), "NOT_FOUND")
        return ToolOutput({"status": status, "hint": ORG_HINTS[status]}, obs)
    return Tool(tool.name, tool.description, resources, fn)


def merge_specs(specs_by_group: dict[str, list[ToolSpec]]) -> list[ToolSpec]:
    """그룹마다 다른 도구 명세(도메인별 record_type)를 하나로: enum은 합집합, 설명은 조직 전체로. group 인자는 없다."""
    merged: dict[str, ToolSpec] = {}
    for g in sorted(specs_by_group):
        for s in specs_by_group[g]:
            if s.name not in merged:
                merged[s.name] = s.model_copy(update={"parameters": copy.deepcopy(s.parameters)})
                continue
            props = merged[s.name].parameters["properties"]
            for k, v in s.parameters.get("properties", {}).items():
                if k in props and "enum" in v and "enum" in props[k]:
                    props[k]["enum"] = list(dict.fromkeys([*props[k]["enum"], *v["enum"]]))
                    if v.get("description") and v["description"] not in props[k].get("description", ""):
                        head, _, lines = v["description"].partition("\n")
                        props[k]["description"] = props[k].get("description", "") + "".join(
                            "\n" + x for x in lines.splitlines() if x not in props[k].get("description", ""))
    out = []
    for s in merged.values():
        desc = s.description
        if s.name == "db.query":
            desc = ("Look up one record type for an entity across the whole organization's database. Returns, for every "
                    "group that holds such a record, the latest version registered as of today, labelled with its group. "
                    "The entity can be given directly as an ID or a name; use entity.search only if db.query returns "
                    "NOT_FOUND.")
        elif s.name == "entity.search":
            desc = "Find entities anywhere in the organization by ID or name. Returns entity IDs you can use with db.query."
        out.append(s.model_copy(update={"description": desc}))
    return out


def search_memory_tool(stores, retrievers: dict, resolvers: dict, cache) -> Tool:
    """조직 전체 이력 검색. retrievers·resolvers = 그룹 → 게이트웨이와 같은 GroupRetriever·AliasResolver."""

    def entities_of(g: str, query: str) -> list[str]:
        found = dict.fromkeys(resolvers[g].tag(query))
        said = normalize(query)
        for key in stores.index.entities(g):                            # 게이트웨이 2단계와 같은 색인 키 대조
            nk = normalize(key)
            if len(nk) > 2 and re.search(rf"(?<!\w){re.escape(nk)}(?!\w)", said):
                found[key] = None
        return list(found)

    def episode_entities(g: str, agent: str, seq) -> list[str]:
        if seq is None:
            return []
        ep = retrievers[g].episodes.get((agent, seq))
        seqs = set(ep.seqs) if ep is not None else {seq}
        return sorted({x for e in stores.history.entries(agent) if e.seq in seqs for x in e.entities})

    async def fn(call: ToolCall):
        q = call.args.get("query")
        base = {"agent": call.agent}
        if not isinstance(q, str) or not q.strip():
            return ToolOutput({"records": "", "error": "empty_query"}, [("full_load", {**base, "error": "empty_query"})])
        memo = cache()
        if ("search_memory", q) in memo:
            return ToolOutput({**memo[("search_memory", q)], "cached": True},
                              [("full_load", {**base, "query": q, "cached": True})])
        text, log, _ = await org_evidence(retrievers, q, lambda g: entities_of(g, q), public_id, episode_entities)
        out = {"records": text or "(nothing found)", "cap_reached": log["cap_reached"]}
        memo[("search_memory", q)] = out
        return ToolOutput(out, [("full_load", {**base, "query": q, "cached": False, "tokens": log["tokens"],
                                               "cap_reached": log["cap_reached"]}),
                                ("retrievals", {"org": True, **log})])
    return Tool("search_memory", "organization-wide history search", (Resource("group_history", "r", target="*"),), fn)
