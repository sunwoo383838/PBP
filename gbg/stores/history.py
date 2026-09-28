"""에이전트별 이력: 워밍업 스냅샷 + 실행 중 커밋. 항목마다 토큰 수, 엔티티 태그, digest, 누적 토큰.

WAL 사건을 이력 항목으로 렌더링하는 규칙이 여기 있다. 커밋된 사건만 들어오므로 이력은 WAL로 재생성된다.
하네스가 렌더링한 항목(과제, 도구 결과 원문, 인수인계)은 시나리오 엔티티 id를 그대로 붙이고,
에이전트가 만든 항목은 그룹 별칭표로 태깅한다(tag). digest는 수치 없이 결정·대상·종류만 남긴다(정식 템플릿은 Stage 3).
"""
import json
from collections.abc import Callable

from gbg.contracts.events import Event
from gbg.contracts.schemas import HistoryEntry

Tagger = Callable[[str, str], list[str]]


def approx_tokens(text: str) -> int:
    """근사 토큰 수. Qwen3 토크나이저 고정은 Stage 3 (tokenizer.py)."""
    return max(12, int(len(text) * 1.1))


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


class HistoryStore:
    def __init__(self, snapshots: dict[str, list[HistoryEntry]], tag: Tagger,
                 tokens: Callable[[str], int] = approx_tokens):
        self._h = {a: list(es) for a, es in snapshots.items()}
        self.tag, self.tokens = tag, tokens
        self.tasks: dict[str, dict] = {}               # task_id → 과제 정보 (엔티티, 종류, 발견성, 그룹)

    def entries(self, agent: str) -> tuple[HistoryEntry, ...]:
        return tuple(self._h.get(agent, []))

    def cumulative(self, agent: str) -> list[int]:
        out, total = [], 0
        for e in self._h.get(agent, []):
            total += e.tokens
            out.append(total)
        return out

    def add(self, agent: str, day: int, role: str, text: str, entities: list[str], digest: str) -> int:
        hist = self._h.setdefault(agent, [])
        seq = hist[-1].seq + 1 if hist else 1
        hist.append(HistoryEntry(seq=seq, day=day, role=role, text=text, tokens=self.tokens(text),
                                 entities=sorted(set(entities)), digest=digest))
        return seq

    def apply(self, ev: Event, group_of: dict[str, str]) -> dict[str, int]:
        """사건 하나를 이력에 반영하고, 답 항목이 생기면 {agent: seq}를 돌려준다(색인 갱신용)."""
        p, d = ev.payload, ev.day
        tag = lambda agent, text: self.tag(group_of[agent], text)
        known = lambda a: isinstance(a, str) and a in group_of
        out: dict[str, int] = {}

        if ev.type == "task_delivered" and known(p["agent"]):
            a, ents = p["agent"], list(p.get("entities", []))
            self.tasks[p["task_id"]] = {"entities": ents, "kind": p["kind"], "disc": p.get("disc"), "group": p["group"]}
            label = "로컬" if p["kind"] == "local" else "교차"
            self.add(a, d, "user", f"[과제 {p['task_id']}] {p['text']}", ents, f"{d}일차 {label} 과제 {p['task_id']} 수신")
            for r in p.get("tool_results", []):
                self.add(a, d, "tool", f"[{r['tool']}] {r['text']}", ents + tag(a, r["text"]), f"{d}일차 {r['tool']} 결과 확인")
        elif ev.type == "tool_call" and known(p["agent"]):
            a = p["agent"]; text = f"[도구 호출] {p['tool']} {_j(p['args'])}"
            self.add(a, d, "assistant", text, tag(a, text), f"{d}일차 {p['tool']} 호출")
        elif ev.type == "tool_result" and known(p["agent"]):
            a = p["agent"]
            body = p.get("result") if p["ok"] else {"error": p["error"]}
            text = f"[도구 결과] {p['tool']} {_j(body)}"
            self.add(a, d, "tool", text, tag(a, text), f"{d}일차 {p['tool']} 결과 {'확인' if p['ok'] else '실패'}")
        elif ev.type == "message" and p["kind"] == "request":
            a, to, q = p["from_agent"], p["to_agent"], p["request"]["question"]
            if known(a):
                self.add(a, d, "assistant", f"[질문 → {to}] {q}", tag(a, q), f"{d}일차 {to}에게 질문")
            if p.get("delivered") and known(to):
                self.add(to, d, "user", f"[질문 ← {a}] {q}", tag(to, q), f"{d}일차 {a}의 질문 수신")
        elif ev.type == "message" and p["kind"] == "response":
            a, to, r = p["from_agent"], p["to_agent"], p["response"]
            if ev.actor == f"agent:{to}" and known(to):
                self.add(to, d, "assistant", f"[답변 → {a}] {r['answer']}", tag(to, r["answer"]), f"{d}일차 {a}에게 답변")
            if known(a):
                self.add(a, d, "tool", f"[답변 ← {to}] ({r['status']}) {r['answer']}", tag(a, r["answer"]),
                         f"{d}일차 {to}의 답변 {r['status']}")
        elif ev.type == "answer" and ev.actor.startswith("agent:") and known(p["agent"]):
            a = p["agent"]; body = p["answer"] if p.get("error") is None else {"error": p["error"]}
            text = f"[답 제출 {p['task_id']}] {_j(body)}"
            out[a] = self.add(a, d, "assistant", text, tag(a, text), f"{d}일차 {p['task_id']} 답 제출")
        elif ev.type == "agent_join" and known(p["agent"]):
            a = p["agent"]
            for note in p.get("handover_notes", []):
                text = note if note.startswith("[인수인계]") else f"[인수인계] {note}"
                self.add(a, d, "user", text, list(p.get("entities", [])) + tag(a, note), f"{d}일차 인수인계 수신")
        return out

    def dump(self):
        return {"entries": {a: [e.model_dump(mode="json") for e in es] for a, es in sorted(self._h.items())},
                "tasks": {t: v for t, v in sorted(self.tasks.items())}}
