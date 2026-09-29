"""시스템 프롬프트 (영어). 전 조건 동일하고, 조건마다 다른 것은 <<TOOLS>>와 <<DIRECTORY>> 블록뿐이다.

디렉터리는 매 호출 시점의 card 레지스트리(구조 갱신, card_mode에 따른 동적 요약 포함)에서 렌더링한다.
"""
from gbg.contracts.card import AgentCard, GroupCard

TOOL_OPEN, TOOL_CLOSE = "<<TOOLS>>", "<</TOOLS>>"
DIR_OPEN, DIR_CLOSE = "<<DIRECTORY>>", "<</DIRECTORY>>"

COMMON = """You are an agent in one business group of a company. You handle the work of your role and answer the tasks and questions you receive.

Rules
- Use tools to look up your own group's database and rulebook. The database shows only values registered as of today.
- If the information you need is not in your own records or your group's database, ask elsewhere with the communication tool. Do not guess.
- Give your final answer to a task with the submit tool, and your answer to another agent's question with the reply tool. Do not answer in any other form.
- Each submit slot must follow the task's output format exactly.
- Write every question, reply, and answer in English. Copy names of people and departments exactly as they are written.

[Your role]
{card}"""

COMM_TOOLS = {
    "ask_agent": ("ask_agent", "Ask one agent in the directory directly.",
                  {"type": "object", "properties": {"agent_id": {"type": "string"}, "question": {"type": "string"}},
                   "required": ["agent_id", "question"], "additionalProperties": False}),
    "ask_group": ("ask_group", "Ask a group in the directory. That group's boundary module forwards the question to the "
                               "right member and returns the answer.",
                  {"type": "object", "properties": {"group": {"type": "string"}, "question": {"type": "string"}},
                   "required": ["group", "question"], "additionalProperties": False}),
    "ask": ("ask", "State the information you need and why. Your group's boundary module finds the right group, sends "
                   "the request, and returns the answer.",
            {"type": "object", "properties": {"question": {"type": "string"}, "purpose": {"type": "string"}},
             "required": ["question", "purpose"], "additionalProperties": False}),
}


def render_card(card: AgentCard) -> str:
    skills = "; ".join(f"{s.name}: {s.description}" for s in card.skills)
    lines = [f"Group: {card.group}", f"Name: {card.name}", f"Description: {card.description}"]
    if card.scope:
        lines.append(f"Scope: {card.scope}")
    lines.append(f"Skills: {skills}")
    return "\n".join(lines)


def render_directory(cards: list[AgentCard] | list[GroupCard]) -> str:
    lines = []
    for c in cards:
        skills = ", ".join(s.name for s in c.skills)
        if isinstance(c, AgentCard):
            scope = f" | Scope: {c.scope}" if c.scope else ""
            lines.append(f"- {c.occupant} | {c.name} | {c.description}{scope} | Skills: {skills}")
        else:
            scope = f" | Service scope: {c.service_scope}" if c.service_scope else ""
            lines.append(f"- {c.group} | {c.description}{scope} | Skills: {skills}")
    return "\n".join(lines) if lines else "(none)"


def render_system(card: AgentCard, tools: list[tuple[str, str]], directory: str) -> str:
    tool_lines = "\n".join(f"- {name}: {desc}" for name, desc in tools)
    return (COMMON.format(card=render_card(card))
            + f"\n\n{TOOL_OPEN}\n{tool_lines}\n{TOOL_CLOSE}\n\n{DIR_OPEN}\n{directory}\n{DIR_CLOSE}")


def strip_condition_blocks(system: str) -> str:
    """도구·디렉터리 블록을 지운 나머지 (조건 간 동일해야 하는 부분)."""
    out, skip = [], False
    for line in system.splitlines():
        if line in (TOOL_OPEN, DIR_OPEN):
            skip = True
        elif line in (TOOL_CLOSE, DIR_CLOSE):
            skip = False
        elif not skip:
            out.append(line)
    return "\n".join(out)
