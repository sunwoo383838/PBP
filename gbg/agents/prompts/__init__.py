"""시스템 프롬프트 (영어). 전 조건 동일하고, 조건마다 다른 것은 <<TOOLS>>와 <<DIRECTORY>> 블록뿐이다.
공통 부분에는 그룹 개념을 넣지 않는다 (Direct에서는 그룹 id·그룹 card·구성원 목록이 전혀 보이지 않는다).

디렉터리는 매 호출 시점의 card 레지스트리(구조 갱신, card_mode에 따른 동적 요약 포함)에서 렌더링한다.
"""
from gbg.contracts.card import AgentCard, GroupCard, public_id

TOOL_OPEN, TOOL_CLOSE = "<<TOOLS>>", "<</TOOLS>>"
DIR_OPEN, DIR_CLOSE = "<<DIRECTORY>>", "<</DIRECTORY>>"

COMMON = """You are an agent in a company. You handle the work of your role and answer the tasks and questions you receive.

What you have
- Your own records (shown to you with each task) and the database and rulebook you can access. They cover only your own area of work. The database shows only values registered as of today.
- Other parts of the company hold everything else: their records, their databases and their rules. You cannot look these up yourself; you can only ask for them with the communication tool listed below (if there is one).

How to work on a task
- First decide what information the answer needs and who is likely to hold each piece. Look up what your own area holds, and ask early for the rest. You may ask several times and ask several parties.
- Do not keep searching your own tools for information your area does not hold. If a lookup finds nothing, ask instead.
- Apply the rules that govern each piece (your area's rules are listed below; other areas' rules come from the parties you ask), then work out the answer step by step. Do not guess.
- You can call several tools in one step when you need several lookups or questions.
- When you ask, name the subject in the question: the names, IDs and amounts it is about. Do not use task IDs (such as W-00070); other parts of the company do not have them in their records. If the task refers to an earlier task by its ID, find what that task was about in your own records and ask about its subject.
- Give your final answer to a task with the submit tool, and your answer to another agent's question with the reply tool. Do not answer in any other form.
- Each submit slot must follow the task's output format exactly.
- Write every question, reply, and answer in English. Copy names of people and departments exactly as they are written.

[Your role]
{card}"""

# full_load(참조 행, 정의: 권한 분할이 없는 단일 에이전트): 조직의 모든 기록을 자기 기억처럼 쓴다. 묻는 상대가 없다.
# 격리·질의 문장 넷만 바꾸고 나머지 문장은 COMMON과 같다.
_HAVE = """- Your own records (shown to you with each task) and the database and rulebook you can access. They cover only your own area of work. The database shows only values registered as of today.
- Other parts of the company hold everything else: their records, their databases and their rules. You cannot look these up yourself; you can only ask for them with the communication tool listed below (if there is one)."""
_HAVE_FULL = """- Your own records (shown to you with each task).
- You have direct access to all records of the organization: database, rules and the full history of every group. Look things up yourself; there is no one to ask.
- The database tools cover the whole organization at once and show only values registered as of today. The rules of every group are listed below. search_memory searches the full history of every group, including members who have left."""
_LOOK = """- Do not keep searching your own tools for information your area does not hold. If a lookup finds nothing, ask instead."""
_LOOK_FULL = """- If the database does not show what you need, search the history with search_memory."""
_ASK = """- First decide what information the answer needs and who is likely to hold each piece. Look up what your own area holds, and ask early for the rest. You may ask several times and ask several parties."""
_ASK_FULL = """- First decide what information the answer needs. Then look up each piece yourself."""
_RULES = """- Apply the rules that govern each piece (your area's rules are listed below; other areas' rules come from the parties you ask), then work out the answer step by step. Do not guess."""
_RULES_FULL = """- Apply the rules that govern each piece (the rules of every group are listed below), then work out the answer step by step. Do not guess."""
_NAME = """- When you ask, name the subject in the question: the names, IDs and amounts it is about. Do not use task IDs (such as W-00070); other parts of the company do not have them in their records. If the task refers to an earlier task by its ID, find what that task was about in your own records and ask about its subject.
"""
_NAME_FULL = """- If the task refers to an earlier task by its ID, find what that task was about in your own records and search for its subject (names, IDs and amounts), not the task ID.
"""
COMMON_FULL_LOAD = (COMMON.replace(_HAVE, _HAVE_FULL).replace(_LOOK, _LOOK_FULL).replace(_ASK, _ASK_FULL)
                    .replace(_RULES, _RULES_FULL).replace(_NAME, _NAME_FULL))
assert all(x not in COMMON_FULL_LOAD for x in (_HAVE, _LOOK, _ASK, _RULES, _NAME))

COMM_TOOLS = {
    "ask_agent": ("ask_agent", "Ask one agent in the directory (by its id) a question. The agent answers from its own "
                               "records, database and rules only. Choose the agent whose skills match the information "
                               "you need; ask several agents if the information is spread across areas.",
                  {"type": "object", "properties": {"agent_id": {"type": "string"}, "question": {"type": "string"}},
                   "required": ["agent_id", "question"], "additionalProperties": False}),
    "ask_group": ("ask_group", "Ask a group in the directory (by its id) a question. The group's intake desk finds the "
                               "members who hold the information, has them answer from their records, database and "
                               "rules, and returns the group's answer. Ask each group whose area covers a piece you need.",
                  {"type": "object", "properties": {"group": {"type": "string"}, "question": {"type": "string"}},
                   "required": ["group", "question"], "additionalProperties": False}),
    "ask": ("ask", "State the information you need and why. Your outgoing desk decides which group(s) in the directory "
                   "hold it, sends them the request, and returns their answers. Ask separately for pieces held in "
                   "different areas if that is clearer.",
            {"type": "object", "properties": {"question": {"type": "string"}, "purpose": {"type": "string"}},
             "required": ["question", "purpose"], "additionalProperties": False}),
    "ask_member": ("ask_agent", "Ask a member of your own group (listed under 'Members of your group' in the directory, "
                                "by id) a question. The member answers from their own records, database and rules only. "
                                "Use this for information held by colleagues in your group; other groups are reached "
                                "through the other communication tool.",
                   {"type": "object", "properties": {"agent_id": {"type": "string"}, "question": {"type": "string"}},
                    "required": ["agent_id", "question"], "additionalProperties": False}),
    "search_memory": ("search_memory", "Search the full history of the whole organization (every group, including "
                                       "members who have left) for records relevant to a query. Returns the most relevant "
                                       "work episodes, oldest first, each headed by its group, member, day, task title and "
                                       "entity keys.",
                      {"type": "object", "properties": {"query": {
                          "type": "string", "description": "What to look for: names, IDs, and the fact you need."}},
                       "required": ["query"], "additionalProperties": False}),
}


def _skills(card) -> str:
    return "; ".join(f"{s.name}: {s.description}" for s in card.skills)


def render_card(card: AgentCard) -> str:
    """자기 card: 지역·skills(·범위)만. 그룹과 그룹이 붙은 이름은 넣지 않는다."""
    lines = [f"Region: {card.region}"] if card.region else []
    if card.scope:
        lines.append(f"Scope: {card.scope}")
    lines.append(f"Skills: {_skills(card)}")
    return "\n".join(lines)


def render_directory(cards: list[AgentCard] | list[GroupCard]) -> str:
    lines = []
    for c in cards:
        if isinstance(c, AgentCard):                                       # 불투명 id · 지역 · skills
            region = f" | Region: {c.region}" if c.region else ""
            scope = f" | Scope: {c.scope}" if c.scope else ""
            lines.append(f"- {public_id(c.occupant)}{region}{scope} | Skills: {_skills(c)}")
        else:
            skills = ", ".join(s.name for s in c.skills)
            scope = f" | Service scope: {c.service_scope}" if c.service_scope else ""
            lines.append(f"- {c.group} | {c.description}{scope} | Skills: {skills}")
    return "\n".join(lines) if lines else "(none)"


def render_members(cards: list[AgentCard], group: str) -> str:
    """경계 조건의 자기 그룹 구성원 목록 (불투명 id · 지역 · skills). 그룹 메타데이터만 붙인다."""
    body = render_directory(cards) if cards else "(none)"
    return f"Members of your group ({group}), reachable with ask_agent:\n{body}"


PERIOD_NOTE = "- Periods: anything recorded as lasting \"until day N\" (a hold, reservation, exclusion, delay or exception) is still in effect on day N."
# 기록과 DB의 관계 (worldgen 정답 기준, 모든 조건·모든 역할의 모든 LLM 호출에 같은 문장). Direct에 그룹 개념을
# 드러내지 않도록 "group" 대신 공통 프롬프트와 같은 "area"를 쓴다.
RECORDS_NOTE = ("- Records and the database: database registration can lag by a few days. A record made while processing "
                "work (a hold, reservation, earmark, review, exclusion, exception, delay notice, approved transfer, or a "
                "status change such as a confirmed exit or cancellation) can be newer than the database version and "
                "still counts, within its stated period or from its effective day; informal remarks or undecided "
                "suggestions do not change anything. How a dated record applies is decided by the relevant rule (some rules "
                "count changes that take effect soon). Colleagues in the same area read the same database, so identical "
                "database values from several of them are one source, not independent confirmations.")


def record_kinds(specs) -> list[tuple[str, str]]:
    """도구 명세의 record_type 설명에서 (기록 종류, 뜻). 응답자 기록 범위와 접수부 소관 판정에 쓴다."""
    kinds = []
    for s in specs:
        rt = (s.parameters.get("properties") or {}).get("record_type") or {}
        for line in (rt.get("description") or "").splitlines():
            if line.startswith("- ") and ":" in line:
                name, _, meaning = line[2:].partition(":")
                kinds.append((name.strip(), meaning.strip().rstrip(".")))
    return kinds


def render_rules(rules, label: str | None = None, notes: bool = True) -> str:
    """규정 블록: 그룹 접두어 없는 id, 제목, 본문. label이 있으면(full_load) 그룹마다 제목을 단다."""
    lines = []
    for r in rules:
        rid = r.id.split(".", 1)[1] if r.id.startswith(f"{r.group}.") else r.id
        lines.append(f"- {rid}{f' ({r.title})' if r.title else ''}: {r.body}")
    head = f"[Rules of {label}]" if label else "[Rules of your area]"
    if notes:                                                             # full_load는 마지막 그룹 뒤에 한 번만
        lines += [PERIOD_NOTE, RECORDS_NOTE]                                 # 기간 해석·기록과 DB (worldgen 정답 기준, 모든 호출 동일)
    return head + "\n" + "\n".join(lines)


def render_system(card: AgentCard, tools: list[tuple[str, str]], directory: str, rules: str = "",
                  full_load: bool = False) -> str:
    tool_lines = "\n".join(f"- {name}: {desc}" for name, desc in tools)
    return ((COMMON_FULL_LOAD if full_load else COMMON).format(card=render_card(card)) + (f"\n\n{rules}" if rules else "")
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
