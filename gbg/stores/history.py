"""에이전트별 이력: 워밍업 스냅샷 + 실행 중 커밋. 항목마다 토큰 수, 엔티티 태그, digest, 누적 토큰.

WAL 사건을 이력 항목으로 렌더링하는 규칙이 여기 있다. 커밋된 사건만 들어오므로 이력은 WAL로 재생성된다.
시나리오가 렌더링한 이력 줄(transcript: 로컬 작업의 과제·도구 결과 등)은 그 원문·토큰·요약을 그대로 쌓는다.
하네스가 렌더링한 항목(과제, 인수인계)은 시나리오 엔티티 id를 그대로 붙이고,
에이전트가 만든 항목은 그룹 별칭표로 태깅한다(tag). digest는 항목 종류별 템플릿으로 커밋 때 한 번 만든다:
결정·대상·범주형 값만 남기고 수치는 버린다 (예: "Day 12: received local task L-021 (CMT-00021)").

responder_session: ephemeral이면 외부 요청에 답한 세션(질문, 그 사이의 도구 호출·중첩 질문, 답)은 응답자 이력에
요약 한 줄만 남는다. persistent이면 전부 남는다.
"""
import json
from collections.abc import Callable

from gbg.contracts.card import public_id
from gbg.contracts.envelope import render_response
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


def _label(agent: str | None, msg: dict, to_side: bool = False) -> str:
    """이력 문구의 상대 표기: 에이전트는 불투명 id, 경계 모듈은 접수 창구, 그룹에 물었으면 그룹 id."""
    if agent and agent.startswith("boundary:"):
        return "your group's intake desk"
    if agent:
        return public_id(agent)
    if to_side and msg.get("to_group"):
        return msg["to_group"]
    return "your group's boundary"


class HistoryStore:
    def __init__(self, snapshots: dict[str, list[HistoryEntry]], tag: Tagger,
                 tokens: Callable[[str], int] = approx_tokens, responder_session: str = "persistent"):
        self._h = {a: list(es) for a, es in snapshots.items()}
        self.tag, self.tokens = tag, tokens
        self.ephemeral = responder_session == "ephemeral"
        self.tasks: dict[str, dict] = {}               # task_id → 과제 정보 (엔티티, 종류, 발견성, 그룹)
        self._at: tuple[int | None, int | None, str | None] = (None, None, None)   # apply 중인 사건의 (라운드, WAL seq, 과제)

    def entries(self, agent: str) -> tuple[HistoryEntry, ...]:
        return tuple(self._h.get(agent, []))

    def cumulative(self, agent: str) -> list[int]:
        out, total = [], 0
        for e in self._h.get(agent, []):
            total += e.tokens
            out.append(total)
        return out

    def add(self, agent: str, day: int, role: str, text: str, entities: list[str], digest: str,
            tokens: int | None = None) -> int:
        hist = self._h.setdefault(agent, [])
        seq = hist[-1].seq + 1 if hist else 1
        rnd, order, task = self._at                                        # 반영 중인 사건의 (라운드, WAL seq, 과제)
        hist.append(HistoryEntry(seq=seq, day=day, role=role, text=text,
                                 tokens=self.tokens(text) if tokens is None else tokens,
                                 entities=sorted(set(entities)), digest=digest, round=rnd, order=order,
                                 task=task))
        return seq

    def apply(self, ev: Event, group_of: dict[str, str]) -> dict[str, int]:
        """사건 하나를 이력에 반영하고, 답 항목이 생기면 {agent: seq}를 돌려준다(색인 갱신용).
        새 항목에는 그 사건의 (라운드, WAL seq)를 적는다 (full_load의 시간순 정렬용). 과제 사건에는 원 과제 id도 적는다
        (검색의 에피소드 묶음용). 시나리오가 렌더링한 transcript 줄은 과제 id 없이 [Task]/[Result] 표시로 묶인다."""
        task = ev.payload.get("task_id") if ev.type != "world_update" else None
        self._at = (ev.round, ev.seq, task if isinstance(task, str) else None)
        try:
            return self._apply(ev, group_of)
        finally:
            self._at = (None, None, None)

    def _apply(self, ev: Event, group_of: dict[str, str]) -> dict[str, int]:
        p, d = ev.payload, ev.day
        tag = lambda agent, text: self.tag(group_of[agent], text)
        in_session = self.ephemeral and p.get("serving") is not None       # 외부 요청에 답하는 세션 안의 사건
        known = lambda a: isinstance(a, str) and a in group_of
        out: dict[str, int] = {}
        if in_session and ev.type in ("tool_call", "tool_result"):
            return out

        if ev.type == "world_update" and p["kind"] == "transcript" and known(p["agent"]):
            x, a = p["data"], p["agent"]
            self.add(a, d, x["role"], x["text"], tag(a, x["text"]), x["summary"], tokens=x["tokens"])
        elif ev.type == "task_delivered" and known(p["agent"]):
            a = p["agent"]
            ents = sorted(set(p.get("entities", [])) | set(tag(a, p["text"])))
            self.tasks[p["task_id"]] = {"entities": ents, "group": p["group"]}
            text = f"[Task {p['task_id']}] {p['text']}"
            if p.get("request"):
                text += f"\nRequest: {_j(p['request'])}"
            self.add(a, d, "user", text, ents, f"Day {d}: received task {p['task_id']}{_targets(ents)}")
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
            pa, pto = _label(a, p), _label(to, p, to_side=True)            # 이력 문구에는 불투명 id·그룹만
            if known(a) and not in_session:
                self.add(a, d, "assistant", f"[Question to {pto}] {q}", tag(a, q), f"Day {d}: asked {pto}{_targets(tag(a, q))}")
            if p.get("delivered") and known(to) and not self.ephemeral:
                self.add(to, d, "user", f"[Question from {pa}] {q}", tag(to, q), f"Day {d}: question from {pa}{_targets(tag(to, q))}")
        elif ev.type == "message" and p["kind"] == "response":
            a, to, r = p["from_agent"], p["to_agent"], p["response"]
            pa, pto = _label(a, p), _label(to, p, to_side=True)
            if ev.actor == f"agent:{to}" and known(to):
                if self.ephemeral:                                          # 세션 전체를 요약 한 줄로
                    ents = tag(to, p.get("question", ""))
                    self.add(to, d, "assistant", f"[Handled a request from {pa}] ({r['status']})", ents,
                             f"Day {d}: handled a request from {pa} ({r['status']}){_targets(ents)}")
                else:
                    body = render_response(r)
                    self.add(to, d, "assistant", f"[Answer to {pa}] {body}", tag(to, body),
                             f"Day {d}: answered {pa} ({r['status']}){_targets(tag(to, body))}")
            if known(a) and not in_session:
                body = render_response(r)
                self.add(a, d, "tool", f"[Answer from {pto}] ({r['status']}) {body}", tag(a, body),
                         f"Day {d}: answer from {pto} ({r['status']}){_targets(tag(a, body))}")
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
