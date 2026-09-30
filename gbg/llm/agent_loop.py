"""LLM 에이전트: 도구 호출 루프. 단계 상한은 없고(과제 예산이 상한), 예산 상한이 없는 조건만 safety_steps에서
제출 전용 호출 1회로 끝낸다.

과제는 submit(슬롯...)으로, 받은 질문은 reply(answer, missing)로 끝난다. submit 인자는 과제의 닫힌 슬롯 스키마로
검사하고, 형식 오류(도구 없이 글로만 답함, 인자 JSON 오류, 슬롯 불일치)는 format_retries번까지 되돌려 보낸 뒤
format_error로 기록한다. 도구 호출 id는 결정적(call_<단계>_<순번>)으로 바꿔 다음 요청의 캐시 키를 안정시킨다.

과제 예산을 넘기면 커널이 BudgetExhausted를 던진다. 과제 담당자는 예약된 최종 호출 1회로 submit 도구만 받아
그때까지의 정보로 답한다. 받은 질문에 답하던 응답자는 그대로 실패하고, 요청자에게 budget_exhausted 오류가 간다.
"""
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gbg.agents.prompts import COMM_TOOLS, record_kinds, render_directory, render_members, render_rules, render_system
from gbg.contracts.card import AgentCard, AgentSkill, public_id
from gbg.contracts.answer_types import check_value, json_schema
from gbg.contracts.conditions import Condition
from gbg.contracts.envelope import Request, Response, answer_parameters, check_items
from gbg.contracts.schemas import OutputSchema, Slot, TimelineEvent, ToolSpec
from gbg.kernel.budget import BudgetExhausted
from gbg.kernel.scheduler import AgentContext, AgentFailure

from .context_builder import ContextBuilder

FORMAT_NUDGE = "Format error: answer only by calling a tool. Use submit for a task and reply for a question."
REPLY_NUDGE = ("You have used your steps for this question. Do not call other tools. Reply now with the reply tool, "
               "based on what you have found; list what you could not confirm in missing.")
BUDGET_NUDGE = ("The budget for this task is used up. You cannot call other tools or ask anyone. "
                "Submit your final answer now with the submit tool, based on what you have.")
_SLOT_SCHEMA = {"int": "integer", "number": "number", "id": "string", "bool": "boolean"}


@dataclass(frozen=True)
class AgentRuntime:
    condition: Condition
    env_specs: Callable[[str], list[ToolSpec]]      # 그룹 → 환경 도구 명세 (역할·조건과 무관)
    builder: ContextBuilder
    max_steps: int | None
    format_retries: int
    safety_steps: int = 200
    responder_max_steps: int = 10
    responder_exclude_tools: tuple = ()


# ─────────────────────────── 종료 도구 ───────────────────────────
def slot_schema(s: Slot) -> dict:
    if s.type in ("set", "list"):
        sch = {"type": "array"}
        if s.items is not None:
            sch["items"] = json_schema(s.items)
        elif s.type == "set":
            sch["items"] = {"type": "string"}
    elif s.type == "enum":
        sch = {"enum": list(s.options)}
    else:
        sch = {"type": _SLOT_SCHEMA[s.type]}
    if s.note:
        sch["description"] = s.note
    if s.nullable:
        sch = {"anyOf": [sch, {"type": "null"}]}
    return sch


_FORMAT_TEXT = {"id": "an ID, copied exactly", "department": "a department name, copied exactly"}


def _item_text(spec: dict | None, plural: bool = True) -> str:
    """배열 원소 형식을 말로 (worldgen 원소 형식 명세)."""
    if not spec:
        return "values" if plural else "value"
    t = spec.get("type")
    if t == "integer":
        return "integers" if plural else "integer"
    if t == "boolean":
        return "true/false values" if plural else "true/false"
    if t == "string":
        if plural:
            return {"id": "IDs (each copied exactly)", "department": "department names (each copied exactly)"}.get(
                spec.get("format"), "strings")
        return f"string ({_FORMAT_TEXT.get(spec.get('format'), 'text')})"
    if t == "enum":
        return "values from: " + " | ".join(map(str, spec.get("values", [])))
    if t == "tuple":
        inner = ", ".join(n or _item_text(x, False) for n, x in zip(spec.get("names") or [None] * len(spec["items"]),
                                                                    spec["items"]))
        return f"lists [{inner}]"
    return "values"


def render_slot(s: Slot) -> str:
    """과제 프롬프트의 슬롯 한 줄: 이름과 값의 형식을 말로 (예: "dept: string (a department name, copied exactly)").
    타입 이름과 형식 설명을 괄호에 나란히 찍으면 필드 여러 개로 읽힌다(pilot18 dept(id, department) → 객체 제출)."""
    if s.type == "enum":
        body = "one of: " + " | ".join(map(str, s.options))
    elif s.type in ("set", "list"):
        body = f"list of {_item_text(s.items)}, " + ("any order" if s.type == "set" else "in order")
    elif s.type == "id":
        body = f"string ({_FORMAT_TEXT.get(s.format, 'text')})"
    else:
        body = {"int": "integer", "number": "number", "bool": "true/false"}[s.type]
    return f"{s.name}: {body}" + (", or null" if s.nullable else "")


def submit_tool(schema: OutputSchema) -> dict:
    return {"name": "submit", "description": "Submit the final answer to the task.",
            "parameters": {"type": "object", "properties": {s.name: slot_schema(s) for s in schema.slots},
                           "required": [s.name for s in schema.slots], "additionalProperties": False}}


REPLY_TOOL = {"name": "reply", "description": "Answer the question you received: one item per value you found, and "
                                            "anything you could not confirm in missing.",
              "parameters": answer_parameters()}


def check_answer(schema: OutputSchema, args: dict) -> tuple[bool, Any]:
    """닫힌 슬롯 검사. (True, 정규화된 답) 또는 (False, 오류 설명)."""
    names = {s.name for s in schema.slots}
    if set(args) != names:
        return False, f"slots must be exactly {sorted(names)} (got {sorted(args)})"
    out = {}
    for s in schema.slots:
        v = args[s.name]
        if v is None:
            if not s.nullable:
                return False, f"{s.name}: null is not allowed"
            out[s.name] = None
            continue
        ok = {"enum": lambda: any(type(o) is type(v) and o == v for o in s.options),      # True와 1은 다르다
              "int": lambda: isinstance(v, int) and not isinstance(v, bool),
              "number": lambda: isinstance(v, (int, float)) and not isinstance(v, bool),
              "id": lambda: isinstance(v, str),
              "bool": lambda: isinstance(v, bool),
              "set": lambda: isinstance(v, list) and (all(check_value(s.items, x) for x in v) if s.items
                                                     else all(isinstance(x, str) for x in v)),
              "list": lambda: isinstance(v, list) and (s.items is None or all(check_value(s.items, x) for x in v))}[s.type]()
        if not ok:
            return False, f"{s.name}: not a valid {s.type}" + (f" (options: {s.options})" if s.options else "")
        out[s.name] = sorted(v, key=_dumps) if s.type == "set" else v   # 순서 없는 배열은 정규화
    return True, out


def check_reply(args: dict, refs: "RefTable | None" = None) -> tuple[bool, Any]:
    return check_items(args, resolve=refs.resolve if refs else None)


_ID = re.compile(r"\b([DH])(\d+)\b")


def _norm_id(x) -> str:
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def _days(obj, found: list):
    """도구 결과 안의 (엔티티·id, 등록일) 쌍 (full_load의 그룹별 결과 포함)."""
    if isinstance(obj, dict):
        if "registered_day" in obj:
            found.append((_norm_id(obj.get("id") or obj.get("entity")), obj["registered_day"]))
        for v in obj.values():
            _days(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _days(v, found)


class RefTable:
    """응답자 항목의 근거 ID → (source, day). D# = 이 세션의 도구 결과(등록일, 없으면 catalog 같은 고정 자료 "fixed"),
    H# = 자기 이력 줄(그 줄의 날짜), 규정 id = ("rule", "fixed"). 첫 번째로 풀리는 ID를 쓴다."""
    def __init__(self, history, rule_ids):
        self.history = {e.seq: e for e in history}
        self.rules = {_norm_id(r) for r in rule_ids}
        self.results: dict[str, Any] = {}

    def add(self, rid: str, result):
        self.results[rid] = result

    def resolve(self, item: dict) -> tuple[str, str]:
        ref = item.get("ref", "")
        for kind, n in _ID.findall(ref):
            if kind == "H" and int(n) in self.history:
                return "history", str(self.history[int(n)].day)
            if kind == "D" and f"D{n}" in self.results:
                res = self.results[f"D{n}"]
                found: list = []
                _days(res, found)
                ent = _norm_id(item.get("entity"))
                days = {d for _, d in found}
                hit = [d for e, d in found if e and e == ent]
                if hit:
                    return "db", str(hit[0])
                if len(days) == 1:
                    return "db", str(days.pop())
                if not found and isinstance(res, dict) and (res.get("result") or {}).get("status") == "HIT":
                    return "db", "fixed"                                   # 등록일 없는 고정 자료 (catalog)
                return "db", "unknown"
        words = {_norm_id(w) for w in re.split(r"[\s,;()\[\]]+", ref) if w}
        if words & self.rules or _norm_id(ref) in self.rules:
            return "rule", "fixed"
        return "unknown", "unknown"


def _fn(name: str, description: str, parameters: dict) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}


def _dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


# ─────────────────────────── 에이전트 ───────────────────────────
class LLMAgent:
    def __init__(self, agent_id: str, rt: AgentRuntime):
        self.agent_id, self.rt = agent_id, rt
        self._last_rid: dict[int, str | None] = {}                         # 분석 기록: 컨텍스트별 마지막 통신 응답 rid

    ELIDED_MARK = "earlier tool result removed to fit the context window"

    def _manifest(self, ctx: AgentContext, context, messages: list[dict], loop_meta: dict) -> dict:
        """분석 기록 (obs/context_windows 전용, 프롬프트·캐시 키·WAL과 무관): 이번 호출 입력에 든 것의 출처.
        context_items: 창·요약 이력 항목에 출처 태그 (own_task = 이 과제의 앞선 사건, other_task = 다른 과제의 잔여,
        history = 워밍업·로컬 업무). loop_items: 이번 루프에서 쌓인 메시지 (own_output, tool_result, protocol)."""
        def tag(task):
            return "own_task" if task is not None and task == ctx.task_id else "other_task" if task is not None else "history"
        comp = context.composition
        items = [{"where": w, "seq": x[0], "day": x[1], "role": x[2], "task": x[3], "order": x[4], "source": tag(x[3])}
                 for w, key in (("summary", "summary_items"), ("raw", "raw_items")) for x in comp.get(key, [])]
        loop = []
        for m in messages[len(context.messages):]:
            if m["role"] == "assistant":
                loop.append({"kind": "own_output", "tool_calls": len(m.get("tool_calls") or [])})
            elif m["role"] == "tool":
                meta = loop_meta.get(m.get("tool_call_id"), {})
                loop.append({"kind": "tool_result", **meta, "elided": self.ELIDED_MARK in (m.get("content") or ""),
                             "chars": len(m.get("content") or "")})
            else:
                loop.append({"kind": "protocol", "chars": len(m.get("content") or "")})
        return {"context_items": items, "loop_items": loop,
                "input_sources": {"current_task": "serving" if ctx.serving is not None else "task"}}

    def env(self, ctx_or_group) -> list[ToolSpec]:
        """환경 도구 명세. full_load는 모든 그룹의 도구를 조직 전체 도구 하나로 합친다(group 인자 없음). 응답 중에는
        responder_exclude_tools를 뺀다."""
        if self.rt.condition.agent_tool == "search_memory" and isinstance(ctx_or_group, AgentContext):
            from gbg.kernel.full_load import merge_specs
            return merge_specs({g: self.rt.env_specs(g) for g in ctx_or_group.kernel.stores.cards.group_cards})
        specs = self.rt.env_specs(ctx_or_group.group if isinstance(ctx_or_group, AgentContext) else ctx_or_group)
        if isinstance(ctx_or_group, AgentContext) and ctx_or_group.serving is not None:
            specs = [s for s in specs if s.name not in self.rt.responder_exclude_tools]
        return specs

    def records_scope(self, ctx) -> str:
        """응답자 system 전용: 자기 그룹 기록의 범위(종류만). 도구 명세의 기록 종류 설명에서 자동으로 만든다."""
        kinds = [f"{n} ({m})" for n, m in record_kinds(self.env(ctx))]
        if not kinds:
            return ""
        return ("[Your area's records]\nYour area's records contain only: " + "; ".join(kinds)
                + ". Anything else in the question is not in your records: list it under missing without looking it up.")

    def system(self, ctx: AgentContext) -> tuple[str, int]:
        cards = ctx.kernel.stores.cards
        cond = self.rt.condition
        own = cards.agent_cards.get(self.agent_id) or AgentCard(                 # card 없는 구성원: 역할만
            name=ctx.role, description=ctx.role, version=1, group=ctx.group, scope=None, occupant=self.agent_id,
            skills=[AgentSkill(id=ctx.role, name=ctx.role, description=ctx.role)])
        entries = [c for c in cards.directory(cond.directory)
                   if (c.occupant != self.agent_id if cond.directory == "agent_cards" else c.group != ctx.group)]
        if cond.directory == "agent_cards" and ctx.serving is None:         # Direct: 디렉터리에 없는 자기 그룹 동료도 (그룹 표시 없음)
            listed = {c.occupant for c in entries}
            entries += [c for c in self.members(ctx) if c.occupant not in listed]
        directory = render_directory(entries) if self._can_ask(ctx) else "(none)"   # 응답 중·full_load는 아무에게도 묻지 않는다
        if self._relays(ctx):                                               # [direct_relay] 응답자: 자기 그룹 동료만
            directory = render_members(self.members(ctx), ctx.group, tool="ask_colleague")
        if self._member_only(ctx):                                          # 그룹 추상화 조건: 자기 그룹 구성원 (그룹 표시만)
            directory += "\n\n" + render_members(self.members(ctx), ctx.group)
        tools = [(s.name, s.description) for s in self.env(ctx)] + [self._comm_spec(t)[:2] for t in self.comm(ctx)]
        rb = ctx.kernel.stores.rulebook                                     # 자기 그룹 규정 고정 (full_load는 전 그룹)
        if self.rt.condition.agent_tool == "search_memory":
            gs = sorted(cards.group_cards)
            rules = "\n\n".join(render_rules(rb.read_all(g), g, notes=g == gs[-1]) for g in gs)
        else:
            rules = render_rules(rb.read_all(ctx.group))
        if ctx.serving is not None and (scope := self.records_scope(ctx)):   # 응답자 자신의 system에만 (card에는 없음)
            rules = rules + "\n\n" + scope
        return (render_system(own, tools, directory, rules, full_load=cond.agent_tool == "search_memory"),
                self.rt.builder.count(directory))

    def comm(self, ctx=None) -> list[str]:
        """통신 도구. 응답 중(serving)에는 없다: 응답자의 중첩 질의는 모든 조건에서 끈다(자기 이력과 자기 그룹
        DB·catalog·규정만으로 답한다). 그룹 안 질문은 모든 조건에서 허용한다(worldgen 규격 message.send: 그룹 내부):
        Direct는 ask_agent가 이미 모든 에이전트를 받고, 그 밖의 조건은 자기 그룹 구성원 한정 ask_agent(ask_member)를
        더한다. reveal_holders(조건에서 뺌, 코드만 둠)는 제한 없는 ask_agent를 더한다."""
        if isinstance(ctx, AgentContext) and ctx.serving is not None:
            return ["ask_colleague"] if self._relays(ctx) else []
        c = self.rt.condition
        if c.agent_tool == "ask_agent":
            return ["ask_agent"]
        if c.agent_tool == "search_memory":                               # full_load: 묻지 않는다. 조직 전체 기억 검색만
            return ["search_memory"]
        tool = ({"forward": "ask_group_forward", "read": "ask_group_read"}.get(c.ingress.deliver, c.agent_tool)
                if c.agent_tool == "ask_group" and c.ingress is not None else c.agent_tool)   # Routing: 응답 원문만 / retrieve: + 근거 원문
        return [tool] + (["ask_agent"] if c.ingress is not None and c.ingress.reveal_holders else ["ask_member"])

    def _relays(self, ctx) -> bool:
        """[direct_relay] 요청자에게 직접 받은 질문에 답하는 응답자(홉 1)만 자기 그룹 동료에게 되물을 수 있다."""
        return (self.rt.condition.relay is not None and isinstance(ctx, AgentContext) and ctx.serving is not None
                and ctx.boundary is None and ctx.hop == 1)

    def _comm_spec(self, t: str) -> tuple:
        name, desc, params = COMM_TOOLS[t]
        if t == "ask_colleague":
            desc = desc.format(max_asks=self.rt.condition.relay.max_asks)
        return name, desc, params

    def _member_only(self, ctx) -> bool:
        """ask_agent가 자기 그룹 구성원 한정인가 (Direct가 아닌 조건)."""
        return "ask_member" in self.comm(ctx)

    def _can_ask(self, ctx) -> bool:
        return any(t != "search_memory" for t in self.comm(ctx))

    def members(self, ctx: AgentContext) -> list[AgentCard]:
        """자기 그룹의 활동 중인 다른 구성원 전원의 card (디렉터리에 오르지 않는 구성원은 역할 card). 구성원은
        자기 그룹 동료를 안다: 디렉터리 card 대상만이 아니라 명부 전체."""
        k = ctx.kernel
        cards = k.stores.cards.agent_cards
        return [cards[a] for a, (g, _) in sorted(k.stores.members.items())
                if g == ctx.group and a != self.agent_id and k.is_active(a) and a in cards]

    def tool_schemas(self, group, finish: dict) -> list[dict]:
        return ([_fn(s.name, s.description, s.parameters) for s in self.env(group)]
                + [_fn(*self._comm_spec(t)) for t in self.comm(group)]
                + [_fn(finish["name"], finish["description"], finish["parameters"])])

    async def work(self, ctx: AgentContext, task: TimelineEvent) -> dict:
        lines = [f"Today is day {ctx.day}.", f"[Task {task.task_id}] {task.text}"]
        if task.request:
            lines.append(f"Request: {_dumps(task.request)}")
        lines.append("Output format: submit with these slots:\n" + "\n".join(f"- {render_slot(s)}"
                                                                           for s in task.output_schema.slots))
        if task.output_schema.conventions:                                 # 답 작성 규칙 (모든 조건 동일)
            conv = task.output_schema.conventions
            lines.append("Answer conventions:\n" + (conv if isinstance(conv, str) else _dumps(conv)))
        return await self._loop(ctx, "\n".join(lines), submit_tool(task.output_schema),
                                lambda args: check_answer(task.output_schema, args))

    async def respond(self, ctx: AgentContext, request: Request) -> Response:
        who = ("your group's intake desk (a request from another group)" if request.from_agent.startswith("boundary:")
               else public_id(request.from_agent))
        text = f"Today is day {ctx.day}.\n[Question from {who}] {request.question}"
        if request.purpose:
            text += f"\nPurpose: {request.purpose}"
        head = ("\nAnswer from your own records and your area's database, catalog and rules. If a part of the question "
                "is not in your records and a colleague in your group (listed under 'Members of your group') is likely to "
                "hold it, you may ask that colleague with ask_colleague; you remain responsible for the reply."
                if self._relays(ctx) else                                  # [direct_relay] 동료 되묻기 허용
                "\nAnswer only from your own records and your area's database, catalog and rules; you cannot ask "
                "anyone else.")
        text += (head + " Check your records once; list any part you cannot find there in missing and do not keep "
                 "searching. Your area's rules are in the system section above; do not search for them. "
                 "Answer with the reply tool: one item per value, with IDs, names and amounts copied exactly as they "
                 "appear in the record, and in ref the ID of the lookup result (D1, D2, ...), the line of your records "
                 "(H...) or the rule id it comes from. If a record in your history on the same item is newer than the "
                 "database's registered day, give both values as separate items. When you give a calculated value, also "
                 "give each input value as its own item.")
        rules = [r.id.split(".", 1)[1] if r.id.startswith(f"{r.group}.") else r.id
                 for r in ctx.kernel.stores.rulebook.read_all(ctx.group)]
        refs = RefTable(ctx.history, rules)
        answer, items, missing = await self._loop(ctx, text, REPLY_TOOL, lambda a: check_reply(a, refs), refs)
        return Response(rid=request.rid, status="partial" if missing else "ok", answer=answer, items=items,
                        missing=missing, referral_to=None, need=[], as_of=ctx.day)

    async def _loop(self, ctx: AgentContext, task_text: str, finish: dict, check, refs: RefTable | None = None) -> Any:
        system, dir_tokens = self.system(ctx)
        context = self.rt.builder.build(system, ctx.history, task_text, dir_tokens)
        messages = list(context.messages)
        tools = self.tool_schemas(ctx, finish)
        env = {s.name for s in self.env(ctx)}
        tool_def_tokens = self.rt.builder.count(_dumps(tools))                # 도구 정의 = 호출마다 드는 고정비
        comm = {COMM_TOOLS[t][0] for t in self.comm(ctx)}              # 도구 이름 (ask_member → ask_agent)
        errors = 0
        n_results = {"D": 0, "R": 0}                                       # 도구 결과 ID (D# 조회, R# 받은 답)
        loop_meta: dict[str, dict] = {}                                    # 분석 기록: tool_call_id → 도구 결과 출처
        cached_in_context = False                                          # 캐시된 도구 결과가 입력에 들어갔는가

        def fail_format(call_id: str | None, why: str):
            nonlocal errors
            errors += 1
            if errors > self.rt.format_retries:
                raise AgentFailure("format_error")
            if call_id is None:
                messages.append({"role": "user", "content": FORMAT_NUDGE})
            else:
                messages.append({"role": "tool", "tool_call_id": call_id, "content": _dumps({"ok": False, "error": why})})

        responding = ctx.serving is not None
        capped = ctx.kernel.budget is not None and ctx.kernel.budget.defaults.budget.calls is not None
        # 요청자: 단계 상한 없음(과제 예산이 상한). 예산 상한이 없는 조건(full_load)만 안전 한도
        limit = self.rt.responder_max_steps if responding else (self.rt.max_steps or
                                                                 (10 ** 9 if capped else self.rt.safety_steps))
        for step in range(1, limit + 1):
            self._fit(ctx, messages, len(context.messages), tool_def_tokens)
            comp = {**context.composition, "tool_def_tokens": tool_def_tokens,
                    "loop_messages": len(messages) - len(context.messages), "cached_tool_result": cached_in_context,
                    **self._manifest(ctx, context, messages, loop_meta)}
            estimate = self.rt.builder.count(_dumps(messages)) + tool_def_tokens    # 호출 전 프롬프트 추정
            try:
                res = await ctx.llm(messages, tools, step, comp, estimate=estimate)
            except BudgetExhausted:
                if finish["name"] != "submit":
                    raise
                return await self._final(ctx, messages, finish, check, step, context.composition, (context, loop_meta))
            calls = [{"id": f"call_{step}_{i}", **c} for i, c in enumerate(res.message["tool_calls"], 1)]
            messages.append({"role": "assistant", "content": res.message["content"],
                             **({"tool_calls": [{"id": c["id"], "type": "function",
                                                 "function": {"name": c["name"], "arguments": c["arguments"]}}
                                                for c in calls]} if calls else {})})
            if not calls:
                fail_format(None, "no_tool_call")
                continue
            for c in calls:
                try:
                    args = json.loads(c["arguments"])
                    if not isinstance(args, dict):
                        raise ValueError
                except ValueError:
                    if c["name"] == finish["name"]:
                        fail_format(c["id"], "arguments are not a JSON object")
                    else:
                        messages.append({"role": "tool", "tool_call_id": c["id"],
                                         "content": _dumps({"ok": False, "error": "bad_arguments"})})
                    continue
                if c["name"] == finish["name"]:
                    ok, val = check(args)
                    if ok:
                        return val
                    fail_format(c["id"], val)
                    continue
                if c["name"] in env:
                    out = await ctx.call_tool(c["name"], **args)
                    kind = "D"
                elif c["name"] in comm:
                    out = await self._communicate(ctx, c["name"], args)
                    kind = "R"
                else:
                    out = {"ok": False, "error": "unknown_tool"}
                    kind = None
                if kind and isinstance(out, dict):                         # 모든 도구 결과에 ID (항목 ref에 쓴다)
                    n_results[kind] += 1
                    out = {"id": f"{kind}{n_results[kind]}", **out}
                    if refs is not None:
                        refs.add(out["id"], out)
                loop_meta[c["id"]] = {"ref": out.get("id") if isinstance(out, dict) else None, "tool": c["name"],
                                      "args": args, "ok": out.get("ok") if isinstance(out, dict) else None,
                                      "status": (out.get("status") or (out.get("result") or {}).get("status")
                                                 if isinstance(out, dict) and isinstance(out.get("result", {}), dict)
                                                 else None) if isinstance(out, dict) else None,
                                      "rid": self._last_rid.pop(id(ctx), None) if kind == "R" else None,
                                      "cached": bool(isinstance(out, dict) and out.get("cached"))}
                cached_in_context = cached_in_context or bool(isinstance(out, dict) and out.get("cached"))
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": _dumps(out)})
        if finish["name"] == "submit":                                     # 단계 한도: 제출 전용 호출 1회로 끝낸다
            return await self._final(ctx, messages, finish, check, limit + 1, context.composition, (context, loop_meta))
        return await self._last_reply(ctx, messages, finish, check, limit + 1, context.composition, (context, loop_meta))

    ELIDED = _dumps({"elided": "earlier tool result removed to fit the context window"})

    def _fit(self, ctx: AgentContext, messages: list[dict], base: int, extra: int):
        """입력이 모델 컨텍스트(컨텍스트 − 출력 상한, 토크나이저 차이 여유 10%)를 넘으면 이번 루프의 가장 오래된 도구
        결과부터 생략 표시로 바꾼다 (모든 조건 동일). 도구 결과가 계속 쌓이는 긴 루프에서 요청이 거부되는 것을 막는다."""
        p = getattr(getattr(ctx.kernel, "llm", None), "params", None)
        if p is None or not getattr(p, "context_length", None):
            return
        limit = int((p.context_length - p.max_tokens) * 0.9)
        i = base
        while self.rt.builder.count(_dumps(messages)) + extra > limit:
            while i < len(messages) and not (messages[i]["role"] == "tool" and messages[i]["content"] != self.ELIDED):
                i += 1
            if i >= len(messages) - 1:                                     # 마지막 결과는 남긴다
                return
            messages[i] = {**messages[i], "content": self.ELIDED}

    async def _last_reply(self, ctx: AgentContext, messages: list[dict], finish: dict, check, step: int, composition: dict,
                          manifest: tuple | None = None):
        """응답자 단계 한도: reply 도구만 주는 호출 1회 (최종 예약분이 아니라 과제 예산에서 쓴다). responder_step_cap으로 센다."""
        if ctx.kernel.budget is not None:
            ctx.kernel.budget.responder_step_caps += 1
        messages = messages + [{"role": "user", "content": REPLY_NUDGE}]
        tools = [_fn(finish["name"], finish["description"], finish["parameters"])]
        comp = {**composition, "tool_def_tokens": self.rt.builder.count(_dumps(tools)), "loop_messages": -1,
                "responder_step_cap": True, **(self._manifest(ctx, manifest[0], messages, manifest[1]) if manifest else {})}
        res = await ctx.llm(messages, tools, step, comp, estimate=self.rt.builder.count(_dumps(messages)), force=finish["name"])
        for c in res.message["tool_calls"]:
            if c["name"] != finish["name"]:
                continue
            try:
                args = json.loads(c["arguments"])
            except ValueError:
                break
            ok, val = check(args) if isinstance(args, dict) else (False, None)
            if ok:
                return val
            break
        raise AgentFailure("step_limit")

    async def _final(self, ctx: AgentContext, messages: list[dict], finish: dict, check, step: int, composition: dict,
                     manifest: tuple | None = None):
        """예산 소진: 예약된 최종 호출 1회, submit 도구만."""
        messages = messages + [{"role": "user", "content": BUDGET_NUDGE}]
        tools = [_fn(finish["name"], finish["description"], finish["parameters"])]
        self._fit(ctx, messages, 2, self.rt.builder.count(_dumps(tools)))
        comp = {**composition, "tool_def_tokens": self.rt.builder.count(_dumps(tools)), "loop_messages": -1,
                **(self._manifest(ctx, manifest[0], messages, manifest[1]) if manifest else {})}
        res = await ctx.llm(messages, tools, step, comp, final=True, force=finish["name"])   # 제출 도구 강제
        for c in res.message["tool_calls"]:
            if c["name"] != finish["name"]:
                continue
            try:
                args = json.loads(c["arguments"])
            except ValueError:
                break
            ok, val = check(args) if isinstance(args, dict) else (False, None)
            if ok:
                return val
            break
        raise AgentFailure("format_error")

    async def _communicate(self, ctx: AgentContext, tool: str, args: dict) -> dict:
        if tool == "ask_agent":
            if not isinstance(args.get("agent_id"), str) or not isinstance(args.get("question"), str):
                return {"ok": False, "error": "bad_arguments"}
            to = ctx.kernel.stores.cards.resolve(args["agent_id"]) or args["agent_id"]    # 불투명 id → 실제 id
            m = ctx.kernel.members.get(to)
            if self._member_only(ctx) and (m is None or m.group != ctx.group):          # 경계 조건: 자기 그룹만
                return {"ok": False, "error": "not_a_member_of_your_group: ask other groups with the other communication tool"}
            r = await ctx.ask(to, args["question"])
        elif tool == "ask_colleague":                                     # [direct_relay] 자기 그룹 동료에게 (한 단계)
            if not isinstance(args.get("agent_id"), str) or not isinstance(args.get("question"), str):
                return {"ok": False, "error": "bad_arguments"}
            to = ctx.kernel.stores.cards.resolve(args["agent_id"]) or args["agent_id"]
            m = ctx.kernel.members.get(to)
            if m is None or m.group != ctx.group or to == self.agent_id:
                return {"ok": False, "error": "not_a_colleague: ask only members listed under 'Members of your group'"}
            r = await ctx.ask(to, args["question"])
        elif tool == "ask_group":
            if not isinstance(args.get("group"), str) or not isinstance(args.get("question"), str):
                return {"ok": False, "error": "bad_arguments"}
            r = await ctx.ask_group(args["group"], args["question"])
        elif tool == "search_memory":                                      # full_load: 조직 전체 이력 검색
            out = await ctx.call_tool("search_memory", **args)
            return {"ok": out["ok"], **(out.get("result") or {"error": out.get("error")})}
        elif tool == "ask":
            if not isinstance(args.get("question"), str) or not isinstance(args.get("purpose"), str):
                return {"ok": False, "error": "bad_arguments"}
            r = await ctx.ask_egress(args["question"], args["purpose"])
        else:
            return {"ok": False, "error": "not_available"}
        self._last_rid[id(ctx)] = getattr(r, "rid", None)                  # 분석 기록 (결과 문자열에는 넣지 않는다)
        out = {"ok": r.status != "error", "status": r.status, "answer": r.answer,
               "items": [x.model_dump(mode="json") for x in r.items], "missing": r.missing}
        if r.referral_to:
            out["referral_to"] = r.referral_to
        if r.conflicts:                                                    # 접수부 조립: 충돌 표시·제안 값 (담당자 답은 items에 그대로)
            out["conflicts"] = [x.model_dump(mode="json") for x in r.conflicts]
        if r.proposals:
            out["proposals"] = [x.model_dump(mode="json") for x in r.proposals]
        if r.redirects:                                                    # 소관 밖 항목: 어느 그룹에 물을지 (그룹 이름만)
            out["not_handled_here"] = [{"item": f"{x.entity} {x.attribute}".strip(), "ask": x.referral_to}
                                       for x in r.redirects]
        if r.need:
            out["need"] = r.need
        return out
