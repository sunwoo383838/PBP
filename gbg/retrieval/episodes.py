"""에이전트 이력의 에피소드 청킹 (검색 단위). 공개 이력의 [Task]/[Result] 표시와 실행 중 과제 id만 쓴다.

    실행 중 과제 사건(task 필드가 있는 항목)  같은 과제 id의 항목 전부가 한 에피소드 (교차 과제 문답 포함)
    그 밖의 줄(워밍업·시나리오 transcript)     [Task 줄부터 다음 [Result 줄까지. [Result 전에 새 [Task가 나오면 그 직전에서
                                               끊는다. 에피소드 밖 줄(메모, 인수인계 노트 등)은 한 줄짜리 단위
어느 줄로 걸리든 검색 결과는 에피소드 전체다(small-to-big). 에피소드 id = (에이전트, 첫 줄 seq).
"""
from dataclasses import dataclass

from gbg.contracts.schemas import HistoryEntry


@dataclass(frozen=True)
class Episode:
    agent: str
    seqs: tuple[int, ...]
    day: int
    title: str                                  # 첫 줄이 과제 줄이면 그 줄, 아니면 ""
    lines: tuple[str, ...]
    tokens: int

    @property
    def id(self) -> tuple[str, int]:
        return (self.agent, self.seqs[0])

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


def _is_task(text: str) -> bool:
    return text.startswith("[Task")


def _is_result(text: str) -> bool:
    return text.startswith("[Result")


def episodes(agent: str, entries: tuple[HistoryEntry, ...] | list[HistoryEntry]) -> list[Episode]:
    """이력 순서대로 에피소드를 만든다. 실행 중 과제 에피소드는 그 과제의 첫 항목 위치에 놓인다."""
    groups: list[list[HistoryEntry]] = []
    by_task: dict[str, list[HistoryEntry]] = {}
    open_ep: list[HistoryEntry] | None = None
    for e in entries:
        if e.task is not None:
            if e.task not in by_task:
                by_task[e.task] = []
                groups.append(by_task[e.task])
            by_task[e.task].append(e)
            continue
        if _is_task(e.text):
            open_ep = [e]
            groups.append(open_ep)
        elif open_ep is not None:
            open_ep.append(e)
        else:
            groups.append([e])
        if _is_result(e.text):
            open_ep = None
    out = []
    for g in groups:
        title = g[0].text.split("\n", 1)[0] if _is_task(g[0].text) else ""
        out.append(Episode(agent, tuple(e.seq for e in g), g[0].day, title, tuple(e.text for e in g),
                           sum(e.tokens for e in g)))
    return out
