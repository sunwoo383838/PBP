"""경계 모듈 LLM 프롬프트와 도구 (영어). 경계 모듈은 에이전트와 같은 모델을 쓰고, 라우팅과 조립까지만 한다."""
from gbg.contracts.envelope import answer_parameters


INTERPRET_SYSTEM = """You are the intake desk of a business group in a company. Requests from other groups arrive here.
Read the request and extract, without answering it:
- entities: every person, department, ID, item or product the request is about, copied exactly as written
- attribute: the information that is requested, in a few words
- purpose: why it is requested, in a few words (empty if not stated)
First think it through step by step in your reply text, then call the interpret tool once.

This group: {group_desc}"""

INTERPRET_TOOL = {
    "name": "interpret", "description": "Record how the request is understood.",
    "parameters": {"type": "object", "properties": {
        "entities": {"type": "array", "items": {"type": "string"}},
        "attribute": {"type": "string"}, "purpose": {"type": "string"}},
        "required": ["entities", "attribute"], "additionalProperties": False}}

ROUTE_SYSTEM = """You are the intake desk of a business group. Decide who in this group should answer a request from another group.
You see the request, the members of this group, and the group records found for it (each record shows which member wrote or handled it).
- Choose every member who is likely to hold the requested information. There is no limit on the number of members. Prefer members that the records show handling this subject; departed members cannot be asked.
- Refer the request to another group only if a record states that another group has been agreed to execute or own this subject for the relevant period. Cite that record in evidence (for example ["E3"]). A group's usual area of work is not a reason to refer; in that case choose members of this group.
- In items, list the requested items. Mark an item "elsewhere" only if this group keeps no records or rules of that kind (see this group's record types and rules), and name the group from the group list that does; otherwise mark it "here".
Do not answer the request yourself. First review the request, the members and the records step by step in your reply text (which records concern the request, and which members wrote or handled them), then call the route tool once.

This group: {group_desc}"""

ROUTE_TOOL = {
    "name": "route", "description": "Choose members to ask, or refer the request to another group.",
    "parameters": {"type": "object", "properties": {
        "action": {"enum": ["select", "referral"]},
        "agents": {"type": "array", "items": {"type": "string"}, "description": "Member ids from the member list."},
        "referral_to": {"type": "string", "description": "Group id from the group list, only for a referral."},
        "evidence": {"type": "array", "items": {"type": "string"},
                     "description": "For a referral: the record ids (E1, E2, ...) stating the agreement."},
        "items": {"type": "array", "description": "The requested items and whether this group handles each.",
                  "items": {"type": "object", "properties": {
                      "entity": {"type": "string", "description": "The person, department, ID or item, as written."},
                      "attribute": {"type": "string", "description": "The requested information, in a few words."},
                      "scope": {"enum": ["here", "elsewhere"]},
                      "target_group": {"type": "string", "description": "Only for elsewhere: a group id from the group list."}},
                      "required": ["entity", "attribute", "scope"]}}},
        "required": ["action", "agents"], "additionalProperties": False}}

ASSEMBLE_SYSTEM = """You are the intake desk of a business group. The replies of the members you asked go to the requesting group as they are; you cannot change or remove them. Using only those replies and the group records given below, add what they need:
- additions: facts from the group records that the replies did not mention, one item per value, with entity and value copied exactly as they appear in the record. In ref, cite the record as [E1] or a database version as [D1]{state_cite}.
- conflicts: where replies disagree with each other or with the group records, name the item, say what disagrees, and cite the refs.
- proposals: where the replies and records support a different value than a reply gives, name the item, give the value you propose, cite the refs it rests on ([R1], [E1], [D1]{state_cite}), and give a one-sentence rationale.
- missing: requested items that neither the replies nor the records confirm. Do not guess.
- When sources disagree, the most recent record counts. Raise such cases as conflicts or proposals.{version_rule}
- Cross-check the replies against the group records: for each requested item, look through the records for entries of the same kind about the same subject that the replies did not mention. A reply covers only what its sender's records hold and can be incomplete.
First work through the request, the replies and the records step by step in your reply text, then call the answer tool once.

This group: {group_desc}"""

VERSION_RULE = """
- Database versions of the same key are the same fact: the latest registered version replaces earlier ones. State the version you use (for example "v3, registered day 12")."""
STATE_CITE = ", an earlier exchange of this desk as [S1]"

_CITES = {"type": "array", "items": {"type": "string"}, "description": "Citations such as \"[R1]\", \"[E3]\", \"[D2]\"."}
ANSWER_TOOL = {
    "name": "answer", "description": "Send the group's additions, conflict notes, proposed values and what could not be "
                                     "confirmed. The members' replies are sent as they are.",
    "parameters": {"type": "object", "properties": {
        "additions": answer_parameters("The citation of the record the value is taken from, for example \"[E3]\" or "
                                       "\"[D2]\".")["properties"]["items"],
        "conflicts": {"type": "array", "items": {"type": "object", "properties": {
            "item": {"type": "string"}, "note": {"type": "string", "description": "What disagrees."}, "refs": _CITES},
            "required": ["item", "note", "refs"], "additionalProperties": False}},
        "proposals": {"type": "array", "items": {"type": "object", "properties": {
            "item": {"type": "string"}, "value": {"type": "string", "description": "The proposed value, copied as written."},
            "refs": _CITES, "rationale": {"type": "string", "description": "One sentence."}},
            "required": ["item", "value", "refs", "rationale"], "additionalProperties": False}},
        "missing": {"type": "array", "items": {"type": "string"}, "description": "Requested items not confirmed."},
        "answer": {"type": "string", "description": "Optional short summary."}},
        "required": ["additions", "conflicts", "proposals", "missing"], "additionalProperties": False}}
REQUERY_TEXT = """Follow-up from your group's intake desk on a request from another group.
For context, the original request was: {question}
Answer only these items, which are still open (do not answer the rest of the request again): {missing}{excerpt}"""

DRAFT_TEXT = """Your first additions, conflicts and proposals for this request (draft):
{items}{missing}
New replies have arrived since then. Keep every draft entry unless a new reply or record contradicts it, add what the new replies confirm, and remove from missing what is now confirmed."""

EXCERPT_TEXT = """
Records of your group on these items (they may be yours or a former member's):
{records}"""

DISPATCH_SYSTEM = """You are the outgoing desk of a business group. A member of your group needs information from other groups.
Decide which group(s) to ask and rewrite the question so the receiving group can act on it: keep every name, ID and amount of the subject as written, so that each rewritten question names what it is about, and add what the related records below make clear (for example the group that handled this before). Do not add task IDs to the question. Task IDs (such as W-00070) appear only in tasks, not in other areas' records.
First think it through step by step in your reply text, then call the dispatch tool once.

This group: {group_desc}

Groups you can ask:
{directory}"""

DISPATCH_TOOL = {
    "name": "dispatch", "description": "Send the request to one or more groups.",
    "parameters": {"type": "object", "properties": {
        "targets": {"type": "array", "items": {"type": "object", "properties": {
            "group": {"type": "string"}, "question": {"type": "string"}}, "required": ["group", "question"]}},
        "entity": {"type": "string", "description": "The main subject (ID or name) of the request."},
        "attr": {"type": "string", "description": "The requested information, in a few words."}},
        "required": ["targets", "entity", "attr"], "additionalProperties": False}}

FORMAT_NUDGE = "Format error: finish by calling the {tool} tool once with valid arguments."

NOT_HERE_TEXT = "Not handled by this group: {items}."
RESEND_TEXT = """{question}
From your group, only this part is needed: {item}"""
