# Delivery audit: instructions for the judge

You are auditing logged conversations between software agents in a simulated company. Agents in one group ask other groups for facts. For each case you decide, by reading, whether specific **records** (facts owned by another group) actually reached the agent who asked (the **requester**). An automatic string matcher made these decisions before; it misses paraphrases and inverted phrasings. Your judgments replace it, so decide from the meaning of the text, not from surface overlap. Do not write code or use search tools to make the decisions. You may not know which system produced a case, and it does not matter.

## What a case contains

- `# CASE K01234`: the case id.
- The simulation day and the task the requester was working on (context only).
- `## Records under review`: grouped by need. Each `RECORD FR-xxxxx` has the entity it is about (ID / name / alias), the record `text`, its `stored value`, and sometimes `older version` lines (superseded states of the same record). Some needs also have a `COMPUTED QUANTITY` line: a number derived from the records and database values that appears in no record.
- `## Messages the requester received during the task`: messages `[M1]`, `[M2]`, ... Each is a reply from a group (or the result of the requester's own tool call). The line `[M#] reply from group G to the requester's question: "..."` is a header. The quoted question was written by the requester. It is context for reading the reply and is **not** part of what the requester received.
- Sometimes `## Replies that stayed inside the group`: messages `[I1]`, `[I2]`, ... written by members of the group to the group's own desk. The requester did not see them.
- Item lines look like `- entity | attribute | value | status | source, day: reference`.

## Decision 1, for every RECORD: `received`

Look only at the M messages (not their header questions, not the I messages).

- `current`: at least one M message conveys this record's fact about the right entity.
  - The entity must be identifiable: by ID, name or alias, or unambiguously from the question that the message answers.
  - The message must state the record's **required content**: the fact in `text` with every value that appears in both `text` and `stored value`. That covers numbers, days, IDs and statuses, and also non-numeric values such as a destination department, a contract type or a tier. Ignore fields that only name the entity itself.
  - If `older version` lines are listed (oldest first), the required content is only what differs from the **last** older version listed, which is the state just before the current record. Fields unchanged since that version are not required.
  - The content counts whichever group sent it. If a group other than the record's owner states the same content for the same entity, that is `current` (add `other-group` in the note).
  - Any wording counts: paraphrase, inverted phrasing ("asset A-1 is assigned to E-5" for "E-5 holds A-1"), an item line, a quoted raw record, a tool result. A hedged statement ("records suggest ...") that still states the content counts; add `hedged` in the note.
  - The same day expressed differently counts ("through day 14", "ends day 14", "until day 14").
- `stale`: no M message conveys the current content, but one conveys the content of an `older version` as the state of this record. Only possible when older versions are listed.
- `partial`: an M message conveys the fact for the right entity with some, but not all, of the required content (for example the amount of a hold but not its end day, or that an exception exists but not until when).
- `no`: none of the above. This includes: the entity is mentioned without the content; the content is given for a different entity; the content is given for a same-named item of another region (stock items and software exist once per region; check the region code or the replying group); the message says nothing is recorded or the item is missing; the content appears only in a header question; only an aggregate (a count or a total) reflects the record and the entity itself is not named.

Two boundary cases:
- A list or roster that names the entity under its new state without the rest (for example a person listed under the destination department of a transfer, with no effective day) is `partial`.
- `stale` needs the older version's distinguishing values stated in full. If the older state is only partly conveyed, write `no` and put `partial-stale` in the note.

Precedence when several messages differ: `current` > `partial` > `stale` > `no`. (If one message gives the current content, later contradicting messages do not undo it.)

## Decision 2, for every RECORD: `inside`

- If the case has no I section, or `received` is `current`: write `na`.
- Otherwise apply exactly the same test to the I messages and write `current`, `stale`, `partial` or `no`.

## Decision 3, for every COMPUTED QUANTITY: `computed`

- `yes`: an M message that is a reply from a group (not the requester's own tool result) gives this number for this entity as the quantity in question or as a figure a reader would take for it (for example the entity's available, remaining, free or current amount or count).
- `no`: otherwise, including when the same digits appear only in another role (part of an ID, another entity's value, a price, a different attribute such as total seats when the quantity is free seats).
- If the message gives the correct number and also a different number for the same quantity: write `yes` only if the correct number is itself labelled as the quantity (add `conflicting` in the note). If the correct number appears only under another label (for example the raw balance) while a different number is given as the quantity, write `no`.

## Evidence quote

For every decision other than `no` / `na`, give the message label and a quote copied **exactly** from that message (one line, at most 150 characters, no tab characters, the shortest span that shows the content). The quote is checked by a program against the message text, so do not reword it. For `no`, leave the label and quote empty.

## Output format

For each input file `<dir>/part_NNN.md`, write `<dir>/part_NNN.tsv` with the Write tool as soon as you finish that file (before reading the next one). One line per decision, fields separated by a single tab character, no header line:

    F<TAB>case<TAB>record id<TAB>received<TAB>M label<TAB>quote for received<TAB>inside<TAB>I label<TAB>quote for inside<TAB>note
    C<TAB>case<TAB>need<TAB>computed<TAB>M label<TAB>quote<TAB>note

Write a single hyphen `-` in every field that has no content (empty fields at the end of a line get lost otherwise). Every F line has exactly 10 fields and every C line exactly 7.

Example lines (tabs shown as `→`):

    F→K00012→FR-00949→current→M2→NDA check step can be skipped until day 16→na→-→-→-
    F→K00012→FR-00424→no→-→-→partial→I3→exception for premium tier is on file→end day not stated
    C→K00012→IT-TYO/license/SW-9/seats→yes→M1→SW-9 | free seats | 3→-
    C→K00012→FIN-TYO/Dev Team 2/budget_schedule→no→-→-→-

Rules:
- Every record id and every COMPUTED QUANTITY of every case in the file gets exactly one line. If the same record id is printed twice in one case (under two needs), write one line for it. Use the case id, record id and need string exactly as printed.
- If a part file already has a `.tsv` next to it, skip that part.
- `note` is optional and short (a few words). Use it for `hedged`, for doubt, or to say what is missing in a `partial`.
- A file can be large. If the Read tool returns only part of it, keep reading with `offset` until the end before judging the last case.
- Work through the files in order. Judge each case independently of the others.
- When all files are done, reply with one line per file: the file name and the number of F and C lines written. Nothing else is needed.
