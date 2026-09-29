"""그룹 기록 검색과 증거 블록 조립. 모든 경계 조건이 담당자 선택에 같은 검색을 쓴다 (그룹 이력 전체를 읽는다).
Routing은 결과를 담당자 선택에만 쓰고(밖으로 내보내지 않는다), ingress_read는 원문을 첨부하고, 게이트웨이(ingress_sel ·
Ingress · I+E)는 조립에 쓴다.

    후보   = 정확 조회 ∪ 태그 검색 ∪ hybrid(질의, 그룹 이력)
             정확 조회(lookup.py, 라우터와 공통): 색인 + catalog 한 단계 연결 → 일지 원문 항목 + 처리자
             처리자 이력 중 확장 엔티티 항목, 태그 검색: 그룹 이력 전체에서 확장 엔티티 태그·언급 항목
    재순위 = 정확 일치 > 하이브리드, 같은 점수면 최신. 버전은 고르지 않는다: 같은 사실의 버전 선택은 L_state 결정이라
             Ingress(경계 상태)의 게이트웨이 LLM이 맡는다. 조회 단계는 후보를 가지치기하지 않는다
    확장   = 적중한 이력 항목마다 같은 에이전트 이력의 앞뒤 expand개 (H2 선행 발화 확보)
    상한   = evidence_cap 토큰, 넘으면 오래된 것부터 제외. 상한 도달 여부를 기록
    출력   = [E1] fin-tyo.a3 · day 12 · 원문 … (항목마다 인용 id, 시간순). 일지 항목은 "journal"로 표시

모든 검색 호출과 결과(항목 목록, 점수, 상한 도달)는 로그로 돌려준다(obs/retrievals.jsonl). 채점기는 이것으로
L_sel을 검색 실패와 조립 실패로 나눈다.
"""
from dataclasses import dataclass, field

from gbg.contracts.params import RetrievalParams
from gbg.contracts.schemas import HistoryEntry

from .hybrid import Doc, GroupRetriever, Mode
from .lookup import index_lookup, tag_search


@dataclass(frozen=True)
class EvidenceItem:
    cite: str
    agent: str
    seq: int | None                             # 이력 항목이면 seq, 일지 항목이면 None
    day: int
    text: str
    tokens: int
    source: str                                 # exact | journal | hybrid | context


@dataclass
class Evidence:
    items: list[EvidenceItem]
    text: str
    tokens: int
    cap_reached: bool
    log: dict = field(default_factory=dict)


async def build_evidence(retriever: GroupRetriever, query: str, entities: list[str], mode: Mode = "hybrid") -> Evidence:
    p: RetrievalParams = retriever.p
    stores, group = retriever.stores, retriever.group
    await retriever.sync()
    by_seq: dict[str, dict[int, HistoryEntry]] = {}

    def entry(d: Doc) -> HistoryEntry:
        if d[0] not in by_seq:
            by_seq[d[0]] = {e.seq: e for e in stores.history.entries(d[0])}
        return by_seq[d[0]][d[1]]

    agents = set(retriever.agents())

    # 후보: 정확 조회(색인 + catalog 한 단계) + 태그 검색(그룹 이력 전체)
    lk = index_lookup(stores, group, list(entities), p.catalog_link_fields)
    ents, journal = list(lk.entities), list(lk.journal)
    exact: set[Doc] = set(tag_search(stores, sorted(agents), ents)) if ents else set()
    hits = await retriever.search(query, mode)
    score = {h.doc: h.score for h in hits}

    ordered = sorted(exact, key=retriever._recency) + [h.doc for h in hits if h.doc not in exact]
    source = {d: ("exact" if d in exact else "hybrid") for d in ordered}

    # 확장: 같은 에이전트 이력의 앞뒤
    chosen = dict.fromkeys(ordered)
    for d in list(ordered):
        seqs = [e.seq for e in stores.history.entries(d[0])]
        i = seqs.index(d[1])
        for j in range(max(0, i - p.expand), min(len(seqs), i + p.expand + 1)):
            if (d[0], seqs[j]) not in chosen:
                chosen[(d[0], seqs[j])] = None
                source[(d[0], seqs[j])] = "context"

    # 이력 항목 + 일지 항목 (같은 원문이 이력에 이미 있으면 일지 항목은 뺀다)
    texts = {entry(d).text for d in chosen}
    pool = [(entry(d).day, d[0], d[1], entry(d).text, entry(d).tokens, source[d]) for d in chosen]
    seen_j = set()
    for x in journal:
        if x.text in texts or (x.agent, x.text) in seen_j:
            continue
        seen_j.add((x.agent, x.text))
        pool.append((x.day, x.agent, None, x.text, stores.history.tokens(x.text), "journal"))
    pool.sort(key=lambda t: (t[0], t[1], t[2] is None, t[2] or 0, t[3]))

    # 상한: 오래된 것부터 제외
    total = sum(t[4] for t in pool)
    capped = False
    while pool and total > p.evidence_cap:
        total -= pool.pop(0)[4]
        capped = True

    items = [EvidenceItem(f"E{i}", a, s, day, text, tok, src) for i, (day, a, s, text, tok, src) in enumerate(pool, 1)]
    rendered = "\n".join(f"[{it.cite}] {it.agent} · day {it.day}{' · journal' if it.seq is None else ''} · {it.text}"
                         for it in items)
    log = {"group": group, "query": query, "entities": list(entities), "expanded": ents, "holders": list(lk.holders),
           "mode": mode,
           "candidates": [{"agent": d[0], "seq": d[1], "source": source[d], "score": score.get(d)} for d in ordered]
                         + [{"agent": x.agent, "seq": None, "source": "journal", "score": None} for x in journal],
           "selected": [{"cite": it.cite, "agent": it.agent, "seq": it.seq, "source": it.source} for it in items],
           "tokens": total, "cap_reached": capped}
    return Evidence(items, rendered, total, capped, log)
