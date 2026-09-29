"""PROMPT_MANIFEST.md 생성: 역할 × 조건의 실제 프롬프트 전문, 조건 간 diff, 오류·힌트 문구 목록.

스크립트 LLM(테스트 오라클)으로 worldgen_mini 픽스처를 조건마다 실행하면서 LLM에 실제로 간 요청(system, 첫 user,
도구 정의)을 역할별 첫 호출 하나씩 모은다. 코드에서 렌더링한 것을 그대로 옮기므로 코드와 어긋나지 않는다.

    uv run python -m gbg.cli.prompt_manifest [출력 경로]
"""
import difflib
import json
import sys
import tempfile
from pathlib import Path

CONDITIONS = ("direct", "routing", "ingress", "i_e", "full_load")
ROLES = [("requester", "요청자 (과제 담당)"), ("responder", "응답자 (받은 질문)"), ("interpret", "경계: 해석"),
         ("route", "경계: 담당자 선택"), ("assemble", "경계: 조립 (1차)"), ("reassemble", "경계: 재조립 (2차, 초안 포함)"),
         ("dispatch", "경계: Egress 요청 정리")]


def _role(req) -> str | None:
    tools = {t["function"]["name"] for t in req.get("tools", [])}
    user = req["messages"][1]["content"] if len(req["messages"]) > 1 else ""
    if len(req["messages"]) != 2:
        return None                                                        # 루프 중간 호출은 빼고 첫 호출만
    for name in ("interpret", "route", "dispatch", "reply", "submit"):
        if name in tools:
            return {"reply": "responder", "submit": "requester"}.get(name, name)
    if "answer" in tools:
        return "reassemble" if "for this request (draft):" in user else "assemble"
    return None


def capture() -> dict[str, dict[str, dict]]:
    from gbg.tests import test_stage5 as T5
    out: dict[str, dict[str, dict]] = {}
    for cond in CONDITIONS:
        got: dict[str, dict] = {}
        seen = set()

        def script(req, got=got, seen=seen):
            role = _role(req)
            if role and role not in got:
                got[role] = {"system": req["messages"][0]["content"], "user": req["messages"][1]["content"],
                             "tools": [t["function"] for t in req.get("tools", [])]}
            tools = {t["function"]["name"] for t in req.get("tools", [])}
            user = req["messages"][1]["content"]
            if "answer" in tools and "KRW 1,850,000" in user and "W-002" not in seen:   # 재질의 → 재조립을 한 번 일으킨다
                seen.add("W-002")
                return T5.oracle(req, assemble_missing=[["settlement day of the provisional approval"]])
            return T5.oracle(req)
        with tempfile.TemporaryDirectory() as d:
            T5.run(Path(d), cond, script=script)
        out[cond] = got
    return out


def _tools_md(tools: list[dict]) -> str:
    lines = []
    for t in tools:
        lines.append(f"- **{t['name']}**: {t['description']}")
        for k, v in (t.get("parameters", {}).get("properties") or {}).items():
            if isinstance(v, dict) and v.get("description"):
                lines.append(f"  - `{k}`: {v['description']}")
    return "\n".join(lines)


def _diff(a: str, b: str, na: str, nb: str) -> str:
    d = "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(), na, nb, lineterm="", n=1))
    return d or "(같음)"


def messages() -> list[tuple[str, str, str]]:
    """(위치, 이름, 문구): 에이전트에게 보이는 오류·힌트·재촉 문구."""
    from gbg.benchmarks.worldgen.records import HINTS
    from gbg.boundary import prompts as BP
    from gbg.kernel.full_load import ORG_HINTS
    from gbg.llm import agent_loop as AL
    rows = [("agent_loop", "FORMAT_NUDGE", AL.FORMAT_NUDGE), ("agent_loop", "REPLY_NUDGE", AL.REPLY_NUDGE),
            ("agent_loop", "BUDGET_NUDGE", AL.BUDGET_NUDGE), ("boundary", "FORMAT_NUDGE", BP.FORMAT_NUDGE)]
    rows += [("db.query (조건 공통)", k, v) for k, v in HINTS.items()]
    rows += [("db.query (full_load)", k, v) for k, v in ORG_HINTS.items()]
    rows += [("통신 도구", "bad_arguments", '{"ok": false, "error": "bad_arguments"}'),
             ("통신 도구", "unknown_tool", '{"ok": false, "error": "unknown_tool"}'),
             ("통신 도구", "not_a_member", '{"ok": false, "error": "not_a_member_of_your_group: ask other groups with the other communication tool"}'),
             ("커널", "access_denied", '{"ok": false, "error": "access_denied", "resource": ...}'),
             ("버스", "nested_asks_disabled / max_asks / requery_not_allowed / budget_exhausted / agent_unavailable",
              "응답 status=error, answer=<코드>"),
             ("경계", "dispatch_failed / assembly_failed", "응답 status=error, answer=<코드>"),
             ("경계", "referral (ownership_exception)", "This is handled by <group>."),
             ("경계", "no member", "No member of this group could be identified for this request."),
             ("reply·answer 형식 검사", "check_items", "items must be a list and missing a list of strings / answer must be a "
              "string / give at least one item or one missing entry / items[i] must have exactly the fields [...] / "
              "items[i]: every field must be a string (copy numbers as text) / items[i].source must be one of [...] / "
              "items[i]: entity and value must not be empty / items[i].ref: cite the reply or record, for example [R1] or [E3]")]
    rows += [("경계 템플릿", "REQUERY_TEXT", BP.REQUERY_TEXT), ("경계 템플릿", "EXCERPT_TEXT", BP.EXCERPT_TEXT),
             ("경계 템플릿", "DRAFT_TEXT", BP.DRAFT_TEXT), ("경계 템플릿", "NOT_HERE_TEXT", BP.NOT_HERE_TEXT),
             ("경계 템플릿 (I+E 재발신)", "RESEND_TEXT", BP.RESEND_TEXT),
             ("요청자가 받는 응답", "not_handled_here", '"not_handled_here": [{"item": "<entity> <attribute>", "ask": "<group>"}]'),
             ("응답 표기 (render_response)", "redirect", "not handled there: <entity> <attribute> → ask <group>")]
    return rows


def render(cap: dict) -> str:
    out = ["# PROMPT_MANIFEST", "",
           "`gbg/cli/prompt_manifest.py`가 생성한다. 스크립트 LLM으로 worldgen_mini 픽스처를 조건마다 실행해, LLM에 실제로 간 "
           "요청 중 역할별 첫 호출의 system·user·도구 정의를 그대로 옮겼다. user의 기록·과제 내용은 픽스처 예시다.", ""]
    out += ["## 1. 역할 × 조건 표", "", "| 역할 | " + " | ".join(CONDITIONS) + " |", "|---|" + "---|" * len(CONDITIONS)]
    for r, label in ROLES:
        out.append(f"| {label} | " + " | ".join("●" if r in cap[c] else "–" for c in CONDITIONS) + " |")
    out += ["", "## 2. 조건 간 diff (Direct 기준, system)", ""]
    for r in ("requester", "responder"):
        for c in CONDITIONS[1:]:
            if r in cap["direct"] and r in cap[c]:
                out += [f"### {r}: direct → {c}", "```diff", _diff(cap["direct"][r]["system"], cap[c][r]["system"],
                                                                     "direct", c), "```", ""]
    for r in ("interpret", "route", "assemble"):
        if r in cap["routing"] and r in cap["i_e"]:
            out += [f"### {r}: routing → i_e", "```diff", _diff(cap["routing"][r]["system"], cap["i_e"][r]["system"],
                                                                 "routing", "i_e"), "```", ""]
    out += ["## 3. 전문", ""]
    for c in CONDITIONS:
        out += [f"### 조건: {c}", ""]
        for r, label in ROLES:
            if r not in cap[c]:
                continue
            x = cap[c][r]
            out += [f"#### {c} · {label}", "", "**system**", "```text", x["system"], "```", "", "**user (예시)**", "```text",
                    x["user"], "```", "", "**도구**", "", _tools_md(x["tools"]), ""]
    out += ["## 4. 오류·힌트·재촉 문구", "", "| 위치 | 이름 | 문구 |", "|---|---|---|"]
    for where, name, text in messages():
        cell = json.dumps(text, ensure_ascii=False)[1:-1].replace("|", "\\|")
        out.append(f"| {where} | {name} | {cell} |")
    return "\n".join(out) + "\n"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("PROMPT_MANIFEST.md")
    path.write_text(render(capture()), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
