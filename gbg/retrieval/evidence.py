"""증거 블록 조립.

    후보   = 정확 조회(activity[엔티티] 관련 항목 + journal[엔티티]) ∪ hybrid(질의, 그룹 이력)
    재순위 = 정확 일치 > 하이브리드, 같은 점수면 최신. (엔티티, 속성) 태그가 있으면 최신 versions_per_attr개만
    확장   = 적중 항목마다 같은 에이전트 이력의 앞뒤 expand개 (H2 선행 발화 확보)
    상한   = evidence_cap 토큰, 넘으면 오래된 것부터 제외. 상한 도달 여부를 기록
    출력   = [E1] fin-tyo.a3 · day 12 · 원문 … (항목마다 인용 id, 시간순)

모든 검색 호출과 결과(항목 목록, 점수, 상한 도달)는 로그로 돌려준다(obs/retrievals.jsonl). 채점기는 이것으로
L_sel을 검색 실패와 조립 실패로 나눈다.
"""
from dataclasses import dataclass, field

from gbg.contracts.params import RetrievalParams
from gbg.contracts.schemas import HistoryEntry

from .hybrid import Doc, GroupRetriever, Mode
from .normalize import normalize


@dataclass(frozen=True)
class EvidenceItem:
    cite: str
    agent: str
    seq: int
    day: int
    text: str
    tokens: int
    source: str                                 # exact | hybrid | context


@dataclass
class Evidence:
    items: list[EvidenceItem]
    text: str
    tokens: int
    cap_reached: bool
    log: dict = field(default_factory=dict)


def _attr_words(attr: str | None) -> list[str]:
    return [w for w in normalize(attr or "").replace("_", " ").split() if len(w) > 2]


async def build_evidence(retriever: GroupRetriever, query: str, entities: list[str], attr: str | None = None,
                         mode: Mode = "hybrid") -> Evidence:
    p: RetrievalParams = retriever.p
    stores, group = retriever.stores, retriever.group
    await retriever.sync()
    by_seq: dict[str, dict[int, HistoryEntry]] = {}

    def entry(d: Doc) -> HistoryEntry:
        if d[0] not in by_seq:
            by_seq[d[0]] = {e.seq: e for e in stores.history.entries(d[0])}
        return by_seq[d[0]][d[1]]

    agents = set(retriever.agents())

    # 후보: 정확 조회
    exact: set[Doc] = set()
    for ent in entities:
        for r in stores.activity.lookup(group, ent) + stores.journal.lookup(group, ent):
            if r.agent not in agents:
                continue
            exact.add((r.agent, r.seq))
            exact.update((r.agent, e.seq) for e in stores.history.entries(r.agent) if ent in e.entities)
    hits = await retriever.search(query, mode)
    score = {h.doc: h.score for h in hits}

    ordered = sorted(exact, key=retriever._recency) + [h.doc for h in hits if h.doc not in exact]
    source = {d: ("exact" if d in exact else "hybrid") for d in ordered}

    # (엔티티, 속성) 버전 제한: 그 엔티티 태그와 속성 낱말을 함께 가진 항목은 최신 N개만
    words = _attr_words(attr)
    if entities and words:
        kept, seen = [], {}
        for d in ordered:
            e = entry(d)
            keys = [ent for ent in entities if ent in e.entities and any(w in normalize(e.text) for w in words)]
            if keys and all(seen.get(k, 0) >= p.versions_per_attr for k in keys):
                continue
            for k in keys:
                seen[k] = seen.get(k, 0) + 1
            kept.append(d)
        ordered = kept

    # 확장: 같은 에이전트 이력의 앞뒤
    chosen = dict.fromkeys(ordered)
    for d in list(ordered):
        seqs = [e.seq for e in stores.history.entries(d[0])]
        i = seqs.index(d[1])
        for j in range(max(0, i - p.expand), min(len(seqs), i + p.expand + 1)):
            if (d[0], seqs[j]) not in chosen:
                chosen[(d[0], seqs[j])] = None
                source[(d[0], seqs[j])] = "context"

    # 상한: 오래된 것부터 제외
    docs = sorted(chosen, key=lambda d: (entry(d).day, d[0], d[1]))
    total = sum(entry(d).tokens for d in docs)
    capped = False
    while docs and total > p.evidence_cap:
        total -= entry(docs.pop(0)).tokens
        capped = True

    items = [EvidenceItem(f"E{i}", d[0], d[1], entry(d).day, entry(d).text, entry(d).tokens, source[d])
             for i, d in enumerate(docs, 1)]
    text = "\n".join(f"[{it.cite}] {it.agent} · day {it.day} · {it.text}" for it in items)
    log = {"group": group, "query": query, "entities": list(entities), "attr": attr, "mode": mode,
           "candidates": [{"agent": d[0], "seq": d[1], "source": source[d], "score": score.get(d)} for d in ordered],
           "selected": [{"cite": it.cite, "agent": it.agent, "seq": it.seq, "source": it.source} for it in items],
           "tokens": total, "cap_reached": capped}
    return Evidence(items, text, total, capped, log)


def contains(items: list[EvidenceItem], entries: list[tuple[str, int]]) -> bool:
    got = {(it.agent, it.seq) for it in items}
    return any(e in got for e in entries)


def entry_matches(e: HistoryEntry, canary: str) -> bool:
    return canary in normalize(e.text).replace(" ", "")
