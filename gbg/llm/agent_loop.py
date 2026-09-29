"""LLM 에이전트: 도구 호출 루프, 최대 max_steps 단계.

과제는 submit(슬롯...)으로, 받은 질문은 reply(answer, missing)로 끝난다. submit 인자는 과제의 닫힌 슬롯 스키마로
검사하고, 형식 오류(도구 없이 글로만 답함, 인자 JSON 오류, 슬롯 불일치)는 format_retries번까지 되돌려 보낸 뒤
format_error로 기록한다. 도구 호출 id는 결정적(call_<단계>_<순번>)으로 바꿔 다음 요청의 캐시 키를 안정시킨다.
"""
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gbg.agents.prompts import COMM_TOOLS, render_directory, render_system
from gbg.contracts.conditions import Condition
from gbg.contracts.envelope import Request, Response, SourcedValue
from gbg.contracts.schemas import OutputSchema, Slot, TimelineEvent, ToolSpec
from gbg.kernel.scheduler import AgentContext, AgentFailure

from .context_builder import ContextBuilder

FORMAT_NUDGE = "Format error: answer only by calling a tool. Use submit for a task and reply for a question."
_SLOT_SCHEMA = {"enum": "string", "number": "number", "id": "string", "bool": "boolean"}


@dataclass(frozen=True)
class AgentRuntime:
    condition: Condition
    env_specs: Callable[[str], list[ToolSpec]]      # 역할 → 환경 도구 명세 (조건과 무관)
    builder: ContextBuilder
    max_steps: int
    format_retries: int


# ─────────────────────────── 종료 도구 ───────────────────────────
def slot_schema(s: Slot) -> dict:
    if s.type in ("set", "list"):
        sch = {"type": "array", "items": {"type": "string"}}
    else:
        sch = {"type": _SLOT_SCHEMA[s.type]}
        if s.type == "enum":
            sch["enum"] = list(s.options)
    if s.nullable:
        sch = {"anyOf": [sch, {"type": "null"}]}
    return sch


def submit_tool(schema: OutputSchema) -> dict:
    return {"name": "submit", "description": "Submit the final answer to the task.",
            "parameters": {"type": "object", "properties": {s.name: slot_schema(s) for s in schema.slots},
                           "required": [s.name for s in schema.slots], "additionalProperties": False}}


REPLY_TOOL = {"name": "reply", "description": "Answer the question you received. List anything you could not confirm in missing.",
              "parameters": {"type": "object", "properties": {
                  "answer": {"type": "string"},
                  "values": {"type": "array", "items": {"type": "object", "properties": {
                      "value": {"type": "string"}, "source": {"type": "string"}}, "required": ["value", "source"]}},
                  "missing": {"type": "array", "items": {"type": "string"}}},
                  "required": ["answer"], "additionalProperties": False}}


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
        ok = {"enum": lambda: isinstance(v, str) and v in s.options,
              "number": lambda: isinstance(v, (int, float)) and not isinstance(v, bool),
              "id": lambda: isinstance(v, str),
              "bool": lambda: isinstance(v, bool),
              "set": lambda: isinstance(v, list) and all(isinstance(x, str) for x in v),
              "list": lambda: isinstance(v, list) and all(isinstance(x, str) for x in v)}[s.type]()
        if not ok:
            return False, f"{s.name}: not a valid {s.type}" + (f" (options: {s.options})" if s.options else "")
        out[s.name] = sorted(set(v)) if s.type == "set" else v
    return True, out


def check_reply(args: dict) -> tuple[bool, Any]:
    if not isinstance(args.get("answer"), str):
        return False, "answer must be a string"
    try:
        values = [SourcedValue(value=x["value"], source=x["source"]) for x in args.get("values", [])]
    except (KeyError, TypeError):
        return False, "each values item needs value and source"
    missing = args.get("missing", [])
    if not (isinstance(missing, list) and all(isinstance(x, str) for x in missing)):
        return False, "missing must be a list of strings"
    return True, (args["answer"], values, missing)


def _fn(name: str, description: str, parameters: dict) -> dict:
    return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}


def _dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


# ─────────────────────────── 에이전트 ───────────────────────────
class LLMAgent:
    def __init__(self, agent_id: str, rt: AgentRuntime):
        self.agent_id, self.rt = agent_id, rt

    def system(self, ctx: AgentContext) -> tuple[str, int]:
        cards = ctx.kernel.stores.cards
        cond = self.rt.condition
        own = cards.agent_cards[self.agent_id]
        entries = [c for c in cards.directory(cond.directory)
                   if (c.occupant != self.agent_id if cond.directory == "agent_cards" else c.group != ctx.group)]
        directory = render_directory(entries)
        comm = COMM_TOOLS[cond.agent_tool]
        tools = [(s.name, s.description) for s in self.rt.env_specs(ctx.role)] + [(comm[0], comm[1])]
        return render_system(own, tools, directory), self.rt.builder.count(directory)

    def tool_schemas(self, role: str, finish: dict) -> list[dict]:
        comm = COMM_TOOLS[self.rt.condition.agent_tool]
        return ([_fn(s.name, s.description, s.parameters) for s in self.rt.env_specs(role)]
                + [_fn(*comm), _fn(finish["name"], finish["description"], finish["parameters"])])

    async def work(self, ctx: AgentContext, task: TimelineEvent) -> dict:
        lines = [f"[Task {task.task_id}] {task.text}"]
        lines += [f"[{r.tool}] {r.text}" for r in task.tool_results]
        slots = ", ".join(f"{s.name}({s.type}{': ' + '|'.join(s.options) if s.options else ''})"
                          for s in task.output_schema.slots)
        lines.append(f"Output format: submit({slots})")
        return await self._loop(ctx, "\n".join(lines), submit_tool(task.output_schema),
                                lambda args: check_answer(task.output_schema, args))

    async def respond(self, ctx: AgentContext, request: Request) -> Response:
        text = f"[Question from {request.from_agent} ({request.from_group})] {request.question}"
        if request.purpose:
            text += f"\nPurpose: {request.purpose}"
        text += "\nAnswer with the reply tool."
        answer, values, missing = await self._loop(ctx, text, REPLY_TOOL, check_reply)
        return Response(rid=request.rid, status="partial" if missing else "ok", answer=answer, values=values,
                        missing=missing, referral_to=None, need=[], as_of=ctx.day)

    async def _loop(self, ctx: AgentContext, task_text: str, finish: dict, check) -> Any:
        system, dir_tokens = self.system(ctx)
        context = self.rt.builder.build(system, ctx.history, task_text, dir_tokens)
        messages = list(context.messages)
        tools = self.tool_schemas(ctx.role, finish)
        env = {s.name for s in self.rt.env_specs(ctx.role)}
        tool_def_tokens = self.rt.builder.count(_dumps(tools))                # 도구 정의 = 호출마다 드는 고정비
        comm = COMM_TOOLS[self.rt.condition.agent_tool][0]
        errors = 0

        def fail_format(call_id: str | None, why: str):
            nonlocal errors
            errors += 1
            if errors > self.rt.format_retries:
                raise AgentFailure("format_error")
            if call_id is None:
                messages.append({"role": "user", "content": FORMAT_NUDGE})
            else:
                messages.append({"role": "tool", "tool_call_id": call_id, "content": _dumps({"ok": False, "error": why})})

        for step in range(1, self.rt.max_steps + 1):
            comp = {**context.composition, "tool_def_tokens": tool_def_tokens,
                    "loop_messages": len(messages) - len(context.messages)}
            res = await ctx.llm(messages, tools, step, comp)
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
                elif c["name"] == comm:
                    out = await self._communicate(ctx, comm, args)
                else:
                    out = {"ok": False, "error": "unknown_tool"}
                messages.append({"role": "tool", "tool_call_id": c["id"], "content": _dumps(out)})
        raise AgentFailure("step_limit")

    async def _communicate(self, ctx: AgentContext, tool: str, args: dict) -> dict:
        if tool == "ask_agent":
            if not isinstance(args.get("agent_id"), str) or not isinstance(args.get("question"), str):
                return {"ok": False, "error": "bad_arguments"}
            r = await ctx.ask(args["agent_id"], args["question"])
            return {"ok": r.status != "error", "status": r.status, "answer": r.answer,
                    "values": [v.model_dump(mode="json") for v in r.values], "missing": r.missing}
        return {"ok": False, "error": "not_available"}                     # ask_group · ask: 경계 모듈(Stage 5)
