"""컨텍스트 구성: system(역할, 자기 card, 도구, 디렉터리) + 요약(창 이전 항목의 digest, 최신부터 summary 토큰까지)
+ 원문 창(최근 raw_window 토큰) + 현재 과제. 같은 입력이면 출력이 바이트 동일하다.
"""
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from gbg.contracts.schemas import HistoryEntry

ROLE_LABEL = {"user": "received", "assistant": "me", "tool": "tool"}


@dataclass(frozen=True)
class Context:
    messages: list[dict]
    composition: dict                           # obs/context_windows.jsonl에 남는 창 구성


def _span(entries: Sequence[HistoryEntry], tokens: int) -> dict:
    return {"n": len(entries), "tokens": tokens,
            "first_seq": entries[0].seq if entries else None, "last_seq": entries[-1].seq if entries else None}


class ContextBuilder:
    def __init__(self, count: Callable[[str], int], raw_window: int, summary: int):
        self.count, self.raw_window, self.summary = count, raw_window, summary

    def build(self, system: str, history: Sequence[HistoryEntry], task: str, directory_tokens: int) -> Context:
        # 원문 창: 최신부터 거꾸로, 창을 넘는 첫 항목에서 멈춘다 (연속 구간)
        raw_tokens, start = 0, len(history)
        for i in range(len(history) - 1, -1, -1):
            if raw_tokens + history[i].tokens > self.raw_window:
                break
            raw_tokens += history[i].tokens
            start = i
        window = history[start:]

        # 요약: 창 바로 앞부터 거꾸로 digest, 예산을 넘는 첫 항목에서 멈춘다
        lines, sum_tokens, summarized = [], 0, []
        for e in reversed(history[:start]):
            line = f"- [H{e.seq}] day {e.day}: {e.digest}"                  # 줄 ID = 이력 seq (항목 ref에 쓴다)
            t = self.count(line)
            if sum_tokens + t > self.summary:
                break
            lines.append(line)
            sum_tokens += t
            summarized.append(e)

        parts = []
        if lines:
            parts.append("[Earlier records, summarized, newest first]\n" + "\n".join(lines))
        if window:
            parts.append("[Recent records, verbatim]\n" + "\n".join(
                f"[H{e.seq}] (day {e.day} {ROLE_LABEL[e.role]}) {e.text}" for e in window))
        parts.append("[Current task]\n" + task)
        user = "\n\n".join(parts)

        composition = {
            "system_tokens": self.count(system), "directory_tokens": directory_tokens,
            "raw": _span(window, raw_tokens), "summary": _span(list(reversed(summarized)), sum_tokens),
            "dropped": start - len(summarized), "task_tokens": self.count(task), "history_len": len(history),
            # 분석 기록 (obs 전용, 프롬프트와 무관): 창·요약에 든 이력 항목 [seq, day, role, 원 과제 id, WAL 순번]
            "raw_items": [[e.seq, e.day, e.role, e.task, e.order] for e in window],
            "summary_items": [[e.seq, e.day, e.role, e.task, e.order] for e in reversed(summarized)],
        }
        return Context([{"role": "system", "content": system}, {"role": "user", "content": user}], composition)
