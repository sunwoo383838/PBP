"""참조 행 full_load: 권한을 풀어 준 참조(상한 아님). 통신 대신 컨텍스트로 풀면 어떤가.

    - 요청자에게 모든 그룹의 조회 도구(DB·catalog·규정)를 자기 그룹과 똑같이 열어 준다: 같은 도구에 group 인자를 더한다.
    - load_group_history(group): 그 그룹 에이전트 전원(이탈자 포함)의 이력 원문을 시간순((일차, 라운드, WAL 순번))으로
      이어 붙여 돌려준다.
      검색·필터는 없다. 상한(기본 40k 토큰)을 넘으면 오래된 줄부터 버리고, 잘림 여부와 버린 토큰 수를 기록한다.
    - 같은 과제 안에서 같은 그룹을 다시 불러오면 캐시로 처리한다(도구 실행만 생략. 결과가 다음 호출의 입력에 들어가면
      그 토큰은 그대로 센다).
    - 과제 예산 상한을 적용하지 않는다(조건 설정 budget_limit: false). 과제당 토큰과 성공당 토큰은 채점기가 보고한다.
"""
import copy
from collections.abc import Callable

from gbg.contracts.card import public_id
from gbg.contracts.schemas import ToolSpec

from .tools import Resource, Tool, ToolCall, ToolOutput

GROUP_ARG = {"type": "string", "description": "Group id from the directory. Omit for your own group."}


def all_groups_tool(tool: Tool) -> Tool:
    """같은 도구를 group 인자로 다른 그룹에도 쓰게 한다. 자원 확인은 그 그룹을 대상으로 한다."""
    resources = tuple(Resource(r.name, r.action, target="group") for r in tool.resources)

    async def fn(call: ToolCall):
        args = dict(call.args)
        group = args.pop("group", None) or call.group
        return await tool.invoke(ToolCall(call.agent, group, call.day, call.round, args))
    return Tool(tool.name, tool.description, resources, fn)


def merge_specs(specs_by_group: dict[str, list[ToolSpec]]) -> list[ToolSpec]:
    """그룹마다 다른 도구 명세(도메인별 record_type)를 하나로: enum은 합집합, group 인자 추가."""
    merged: dict[str, ToolSpec] = {}
    for g in sorted(specs_by_group):
        for s in specs_by_group[g]:
            if s.name not in merged:
                params = copy.deepcopy(s.parameters)
                params.setdefault("properties", {})["group"] = GROUP_ARG
                merged[s.name] = s.model_copy(update={"parameters": params})
                continue
            props = merged[s.name].parameters["properties"]
            for k, v in s.parameters.get("properties", {}).items():
                if k in props and "enum" in v and "enum" in props[k]:
                    props[k]["enum"] = list(dict.fromkeys([*props[k]["enum"], *v["enum"]]))
                    if v.get("description") and v["description"] not in props[k].get("description", ""):
                        head, _, lines = v["description"].partition("\n")
                        props[k]["description"] = props[k].get("description", "") + "".join(
                            "\n" + x for x in lines.splitlines() if x not in props[k].get("description", ""))
    return list(merged.values())


def load_history_tool(stores, count: Callable[[str], int], limit: int, cache: Callable[[], dict]) -> Tool:
    def fn(call: ToolCall):
        group = call.args.get("group")
        agents = sorted(a for a, (g, _) in stores.members.items() if g == group)     # 이탈자 포함
        memo = cache()
        base = {"group": group, "agent": call.agent}
        if not agents:
            return ToolOutput({"group": group, "records": "", "error": "unknown_group"},
                              [("full_load", {**base, "error": "unknown_group"})])
        if ("load_group_history", group) in memo:
            out = memo[("load_group_history", group)]
            return ToolOutput({**out, "cached": True}, [("full_load", {**base, "cached": True})])
        # 시간순: (일차, 라운드, 그룹 공통 순번). 워밍업은 공개 순번이 없어 같은 라운드 안에서는 에이전트 순
        rows = sorted(((e.day, e.round if e.round is not None else -1, e.order if e.order is not None else -1, a, e.seq),
                       f"(day {e.day} · {public_id(a)}) {e.text}") for a in agents for e in stores.history.entries(a))
        lines = [r[1] for r in rows]
        sizes = [count(x) for x in lines]
        total, dropped, start = sum(sizes), 0, 0
        while start < len(lines) and total - dropped > limit:              # 오래된 줄부터 버린다
            dropped += sizes[start]
            start += 1
        out = {"group": group, "records": "\n".join(lines[start:]), "truncated": start > 0}
        memo[("load_group_history", group)] = out
        return ToolOutput(out, [("full_load", {**base, "cached": False, "lines": len(lines), "kept_lines": len(lines) - start,
                                               "tokens": total - dropped, "truncated": start > 0,
                                               "dropped_tokens": dropped})])
    return Tool("load_group_history", "Load the records of a group", (Resource("group_history", "r", target="group"),), fn)
