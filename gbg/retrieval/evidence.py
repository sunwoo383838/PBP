"""그룹 기록 검색과 증거 블록 조립. 모든 경계 조건이 담당자 선택에 같은 검색을 쓴다 (그룹 이력 전체를 읽는다).
Routing은 결과를 담당자 선택에만 쓰고(밖으로 내보내지 않는다), ingress_read는 원문을 첨부하고, 게이트웨이(ingress_sel ·
Ingress · I+E)는 조립에 쓴다.

    단위   = 에피소드(episodes.py): [Task]~[Result] 구간, 실행 중에는 과제 하나. 어느 줄로 걸리든 에피소드 전체
    후보   = 하이브리드(BM25 + bge-m3, RRF) 상위 top_k
             ∪ 태그 일치: 확장 엔티티(catalog 한 단계 연결 포함) 태그·언급 줄이 든 에피소드
             ∪ 색인 조회(lookup.py, 라우터와 공통): 일지 항목(H0)이 든 에피소드(이력에 없으면 일지 항목 하나),
               처리 흔적(H1)의 처리자가 그날 그 엔티티를 다룬 에피소드
             질의 = 요청 원문 + 해석 단계의 속성 + 엔티티
    재정렬 = 교차 인코더(bge-reranker-v2-m3) 점수. 버전은 고르지 않는다: 같은 사실의 버전 선택은 L_state 결정이라
             Ingress(경계 상태)의 게이트웨이 LLM이 맡는다
    상한   = 점수 순으로 evidence_cap 토큰까지 채운다. 넘치는 것은 점수 낮은 것부터 빠진다(나이순 삭제는 오래된 기록인
             D 정보를 체계적으로 지운다). 상한 도달 여부를 기록
    출력   = 시간순. [E1] fin-tyo.a3 · day 12 · [Task] 제목 다음 줄마다 원문. 일지 항목은 "journal"로 표시

모든 검색 호출과 결과(후보, 출처, 하이브리드·재정렬 점수, 상한 도달)는 로그로 돌려준다(obs/retrievals.jsonl). 채점기는
이것으로 L_sel을 검색 실패와 조립 실패로 나눈다.
"""
import asyncio
import time
from dataclasses import dataclass, field

from gbg.contracts.params import RetrievalParams

from .hybrid import Doc, GroupRetriever, Mode
from .lookup import index_lookup
from .normalize import normalize


@dataclass(frozen=True)
class EvidenceItem:
    cite: str
    agent: str
    seq: int | None                             # 에피소드 첫 줄 seq, 일지 항목이면 None
    day: int
    text: str                                   # 에피소드 원문(줄바꿈으로 이은 줄들)
    tokens: int
    source: str                                 # hybrid | tag | index | journal (여럿이면 +로 잇는다)
    title: str = ""
    score: float | None = None                  # 재정렬 점수


@dataclass
class Evidence:
    items: list[EvidenceItem]
    text: str
    tokens: int
    cap_reached: bool
    log: dict = field(default_factory=dict)
    ranked: list[str] = field(default_factory=list)  # 후보 원문, 재정렬 순위 순 (오프라인 recall@k용, 로그에 넣지 않음)
    seconds: dict = field(default_factory=dict)  # 후보·재정렬·전체 시간 (로그와 분리: 로그는 재실행에서 바이트 동일)


def render_item(it: EvidenceItem) -> str:
    if it.seq is None:
        return f"[{it.cite}] {it.agent} · day {it.day} · journal · {it.text}"
    lines = it.text.split("\n")
    if it.title and len(lines) > 1:
        rest = "\n".join(f"  {x}" for x in "\n".join(lines[1:]).split("\n"))
        return f"[{it.cite}] {it.agent} · day {it.day} · {lines[0]}\n{rest}"
    return f"[{it.cite}] {it.agent} · day {it.day} · " + "\n  ".join(lines)


async def build_evidence(retriever: GroupRetriever, query: str, entities: list[str], mode: Mode = "hybrid") -> Evidence:
    p: RetrievalParams = retriever.p
    stores, group = retriever.stores, retriever.group
    t0 = time.perf_counter()
    await retriever.sync()
    agents = retriever.agents()
    eps = retriever.episodes

    lk = index_lookup(stores, group, list(entities), p.catalog_link_fields)
    ents = list(lk.entities)
    q = " ".join(dict.fromkeys(x for x in [query, *entities] if x)).strip()
    source: dict[Doc, set[str]] = {}

    def add(d: Doc, s: str):
        source.setdefault(d, set()).add(s)

    # 후보 1: 하이브리드
    hits = await retriever.search(q, mode)
    fused = {h.doc: h.score for h in hits}
    for h in hits:
        add(h.doc, "hybrid")
    # 후보 2: 태그 일치 (확장 엔티티)
    norm = retriever.norm
    if ents:
        keys = [(x, normalize(x)) for x in ents]
        for a in agents:
            for e in stores.history.entries(a):
                if any(x in e.entities or nx in norm[(a, e.seq)] for x, nx in keys):
                    add(retriever.of_line[(a, e.seq)], "tag")
    # 후보 3: 색인 조회. 일지 원문이 이력에 있으면 그 에피소드, 없으면 일지 항목 하나
    journal_units = []
    for x in lk.journal:
        want = normalize(x.text)
        ep = next((retriever.of_line[(x.agent, e.seq)] for e in stores.history.entries(x.agent)
                   if (x.agent, e.seq) in norm and want in norm[(x.agent, e.seq)]), None)
        if ep is not None:
            add(ep, "index")
        elif all(u.text != x.text or u.agent != x.agent for u in journal_units):
            journal_units.append(x)
    for x in lk.activity:
        keys = set(x.entities)
        for e in stores.history.entries(x.agent):
            if e.day == x.day and (keys & set(e.entities) or any(normalize(k) in norm[(x.agent, e.seq)] for k in keys)):
                add(retriever.of_line[(x.agent, e.seq)], "index")
    t_cand = time.perf_counter()

    # 재정렬: 에피소드 원문(일지 항목은 그 원문)
    docs = list(source)
    texts = [eps[d].text for d in docs] + [x.text for x in journal_units]
    scores = await asyncio.to_thread(retriever.reranker.score, q, texts)
    t_rr = time.perf_counter()
    pool = [(scores[i], eps[d].day, d[0], d[1], eps[d].text, eps[d].tokens, "+".join(sorted(source[d])), eps[d].title)
            for i, d in enumerate(docs)]
    pool += [(scores[len(docs) + i], x.day, x.agent, None, x.text, stores.history.tokens(x.text), "journal", "")
             for i, x in enumerate(journal_units)]
    # 같은 점수면 하이브리드 점수, 그다음 최신
    pool.sort(key=lambda t: (-t[0], -fused.get((t[2], t[3]), 0.0), -t[1], -(t[3] or 0), t[2]))

    # 상한: 점수 순으로 채우고 넘치는 것은 뺀다
    chosen, total, capped = [], 0, False
    for t in pool:
        if total + t[5] > p.evidence_cap:
            capped = True
            continue
        chosen.append(t)
        total += t[5]
    chosen.sort(key=lambda t: (t[1], t[2], t[3] is None, t[3] or 0))                 # 표시는 시간순

    items = [EvidenceItem(f"E{i}", a, s, day, text, tok, src, title, round(sc, 4))
             for i, (sc, day, a, s, text, tok, src, title) in enumerate(chosen, 1)]
    rendered = "\n".join(render_item(it) for it in items)
    log = {"group": group, "query": q, "entities": list(entities), "expanded": ents, "holders": list(lk.holders),
           "mode": mode, "reranker": retriever.reranker.name,
           "candidates": [{"agent": t[2], "seq": t[3], "day": t[1], "source": t[6], "rerank": round(t[0], 4),
                           "hybrid": fused.get((t[2], t[3])), "tokens": t[5]} for t in pool],
           "selected": [{"cite": it.cite, "agent": it.agent, "seq": it.seq, "source": it.source, "rerank": it.score}
                        for it in items],
           "tokens": total, "cap_reached": capped}
    secs = {"candidates": round(t_cand - t0, 3), "rerank": round(t_rr - t_cand, 3),
            "total": round(time.perf_counter() - t0, 3)}
    return Evidence(items, rendered, total, capped, log, [t[4] for t in pool], secs)
