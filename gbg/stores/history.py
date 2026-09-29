"""에이전트별 이력: 워밍업 스냅샷 + 실행 중 커밋. 항목마다 토큰 수, 엔티티 태그, digest, 누적 토큰.

WAL 사건을 이력 항목으로 렌더링하는 규칙이 여기 있다. 커밋된 사건만 들어오므로 이력은 WAL로 재생성된다.
하네스가 렌더링한 항목(과제, 도구 결과 원문, 인수인계)은 시나리오 엔티티 id를 그대로 붙이고,
에이전트가 만든 항목은 그룹 별칭표로 태깅한다(tag). digest는 항목 종류별 템플릿으로 커밋 때 한 번 만든다:
결정·대상·범주형 값만 남기고 수치는 버린다 (예: "Day 12: received local task L-021 (CMT-00021)").
"""
import json
from collections.abc import Callable

from gbg.contracts.events import Event
from gbg.contracts.schemas import HistoryEntry

from .cards import looks_like_amount

Tagger = Callable[[str, str], list[str]]


def approx_tokens(text: str) -> int:
    """근사 토큰 수. Qwen3 토크나이저 고정은 Stage 3 (tokenizer.py)."""
    return max(12, int(len(text) * 1.1))


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def _targets(entities) -> str:
    return f" ({'·'.join(sorted(set(entities)))})" if entities else ""


def _categorical(answer) -> str:
    """답에서 범주형 값(선택지, 참/거짓, 짧은 id)만 남긴다. 수치와 금액처럼 보이는 문자열은 버린다."""
    if not isinstance(answer, dict):
        return ""
    keep = [f"{k}={str(v).lower() if isinstance(v, bool) else v}" for k, v in sorted(answer.items())
            if isinstance(v, bool) or (isinstance(v, str) and v and len(v) <= 40 and not looks_like_amount(v))]
    return f": {', '.join(keep)}" if keep else ""


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
            self.add(a, d, "user", f"[Task {p['task_id']}] {p['text']}", ents,
                     f"Day {d}: received {p['kind']} task {p['task_id']}{_targets(ents)}")
            for r in p.get("tool_results", []):
                self.add(a, d, "tool", f"[{r['tool']}] {r['text']}", ents + tag(a, r["text"]),
                         f"Day {d}: checked {r['tool']} result{_targets(ents)}")
        elif ev.type == "tool_call" and known(p["agent"]):
            a = p["agent"]; text = f"[Tool call] {p['tool']} {_j(p['args'])}"
            self.add(a, d, "assistant", text, tag(a, text), f"Day {d}: called {p['tool']}{_targets(tag(a, text))}")
        elif ev.type == "tool_result" and known(p["agent"]):
            a = p["agent"]
            body = p.get("result") if p["ok"] else {"error": p["error"]}
            text = f"[Tool result] {p['tool']} {_j(body)}"
            self.add(a, d, "tool", text, tag(a, text), f"Day {d}: {p['tool']} {'succeeded' if p['ok'] else 'failed'}")
        elif ev.type == "message" and p["kind"] == "request":
            a, to, q = p["from_agent"], p["to_agent"], p["request"]["question"]
            if known(a):
                self.add(a, d, "assistant", f"[Question to {to}] {q}", tag(a, q), f"Day {d}: asked {to}{_targets(tag(a, q))}")
            if p.get("delivered") and known(to):
                self.add(to, d, "user", f"[Question from {a}] {q}", tag(to, q), f"Day {d}: question from {a}{_targets(tag(to, q))}")
        elif ev.type == "message" and p["kind"] == "response":
            a, to, r = p["from_agent"], p["to_agent"], p["response"]
            if ev.actor == f"agent:{to}" and known(to):
                self.add(to, d, "assistant", f"[Answer to {a}] {r['answer']}", tag(to, r["answer"]),
                         f"Day {d}: answered {a} ({r['status']}){_targets(tag(to, r['answer']))}")
            if known(a):
                self.add(a, d, "tool", f"[Answer from {to}] ({r['status']}) {r['answer']}", tag(a, r["answer"]),
                         f"Day {d}: answer from {to} ({r['status']}){_targets(tag(a, r['answer']))}")
        elif ev.type == "answer" and ev.actor.startswith("agent:") and known(p["agent"]):
            a = p["agent"]; body = p["answer"] if p.get("error") is None else {"error": p["error"]}
            text = f"[Submitted {p['task_id']}] {_j(body)}"
            digest = (f"Day {d}: submitted {p['task_id']}{_categorical(body)}" if p.get("error") is None
                      else f"Day {d}: failed {p['task_id']} ({p['error']})")
            out[a] = self.add(a, d, "assistant", text, tag(a, text), digest)
        elif ev.type == "agent_join" and known(p["agent"]):
            a = p["agent"]
            for note in p.get("handover_notes", []):
                text = note if note.startswith("[Handover]") else f"[Handover] {note}"
                ents = list(p.get("entities", [])) + tag(a, note)
                self.add(a, d, "user", text, ents, f"Day {d}: received handover{_targets(ents)}")
        return out

    def dump(self):
        return {"entries": {a: [e.model_dump(mode="json") for e in es] for a, es in sorted(self._h.items())},
                "tasks": {t: v for t, v in sorted(self.tasks.items())}}
