"""하이브리드 검색: 그룹 하나의 이력(떠난 에이전트, 에이전트 창 밖으로 밀린 원문 포함)을 에피소드 단위(episodes.py)로
색인하고, BM25 순위와 임베딩 순위를 RRF(k=60)로 결합한다.

말뭉치는 저장소에서 증분 동기화한다. 문서 id = (에이전트, 에피소드 첫 줄 seq). 아직 닫히지 않은 에피소드(과제 진행 중)는
줄이 늘면 다시 색인한다. 같은 점수면 최신(날짜, seq가 큰 것) 먼저.
그룹 경계: 이 그룹 소속 에이전트의 이력만 색인한다. 저장소에는 커밋된 사건만 있으므로 요청 시점 이후 기록은 없다.
"""
from dataclasses import dataclass
from typing import Literal

from gbg.contracts.params import RetrievalParams
from gbg.kernel.access_guard import AccessGuard
from gbg.kernel.tools import Resource

from .bm25 import BM25Index
from .embed import Embedder, VectorIndex
from .episodes import Episode, episodes
from .normalize import normalize
from .rerank import NullReranker, Reranker

Mode = Literal["hybrid", "bm25", "embed"]
Doc = tuple[str, int]                           # (agent, 에피소드 첫 seq)


@dataclass(frozen=True)
class Hit:
    doc: Doc
    score: float
    bm25_rank: int | None
    embed_rank: int | None
    bm25_score: float | None = None             # 분석 기록용 (검색 결과·순서에는 쓰지 않는다)
    embed_score: float | None = None


class RetrievalDenied(PermissionError):
    pass


def authorize(guard: AccessGuard, subject: str, subject_group: str, group: str) -> dict:
    """그룹 이력 검색 권한 (접근 표의 group_history). 경계 모듈은 자기 그룹만. 판정 기록을 돌려주고 거부면 예외."""
    rec = guard.check(subject, subject_group, Resource("group_history", "r", target="group"), {"group": group},
                      "retrieval")
    if not rec["allowed"]:
        raise RetrievalDenied(f"{subject}는 {group} 이력을 검색할 수 없다")
    return rec


class GroupRetriever:
    def __init__(self, stores, group: str, embedder: Embedder, params: RetrievalParams,
                 reranker: Reranker | None = None):
        self.stores, self.group, self.embedder, self.p = stores, group, embedder, params
        self.reranker = reranker or NullReranker()
        self.bm25 = BM25Index(params.bm25.k1, params.bm25.b)
        self.vectors = VectorIndex()
        self.episodes: dict[Doc, Episode] = {}
        self.of_line: dict[tuple[str, int], Doc] = {}      # (agent, 줄 seq) → 에피소드
        self.norm: dict[tuple[str, int], str] = {}         # (agent, 줄 seq) → 정규화한 원문 (태그·일지 대조용)
        self._synced: dict[str, int] = {}
        self.last_search: dict = {}                           # 분석 기록용 (evidence 로그)

    def agents(self) -> list[str]:
        return sorted(a for a, (g, _) in self.stores.members.items() if g == self.group)

    async def sync(self):
        """저장소의 새 이력을 색인에 반영한다. 동시에 도는 과제들이 같은 검색기를 쓰므로 한 번에 하나만 동기화한다
        (먼저 온 호출이 벡터까지 넣기 전에 다른 호출이 검색하면 결과가 실행마다 달라진다)."""
        import asyncio
        loop = asyncio.get_running_loop()                                  # 실행기는 묶음마다 새 이벤트 루프를 쓴다:
        if getattr(self, "_lock_loop", None) is not loop:                  # 잠금은 루프마다 새로 (다른 루프에 묶인 잠금은 오류)
            self._lock, self._lock_loop = asyncio.Lock(), loop
        async with self._lock:
            await self._sync()

    async def _sync(self):
        changed: list[Episode] = []
        for a in self.agents():
            entries = self.stores.history.entries(a)
            if self._synced.get(a) == len(entries):
                continue
            for e in entries[self._synced.get(a, 0):]:
                self.norm[(a, e.seq)] = normalize(e.text)
            for ep in episodes(a, entries):
                old = self.episodes.get(ep.id)
                if old is not None and old.seqs == ep.seqs:
                    continue
                if old is not None:
                    self.bm25.remove(ep.id)
                self.bm25.add(ep.id, ep.text)
                self.episodes[ep.id] = ep
                self.of_line.update({(a, s): ep.id for s in ep.seqs})
                changed.append(ep)
            self._synced[a] = len(entries)
        if changed:
            self.vectors.add([ep.id for ep in changed], await self.embedder.embed([ep.text for ep in changed]))

    def _recency(self, doc: Doc):
        ep = self.episodes[doc]
        return (-ep.day, -ep.seqs[0], doc[0])

    def _ranked(self, scores: dict[Doc, float]) -> list[Doc]:
        return sorted(scores, key=lambda d: (-round(scores[d], 9), *self._recency(d)))

    async def search(self, query: str, mode: Mode = "hybrid", top: int | None = None) -> list[Hit]:
        await self.sync()
        top = top or self.p.top_k
        bs = self.bm25.scores(query) if mode in ("hybrid", "bm25") else {}
        bm = self._ranked(bs)
        em: list[Doc] = []
        es: dict = {}
        if mode in ("hybrid", "embed") and self.vectors.ids:
            q = (await self.embedder.embed([query]))[0]
            es = self.vectors.scores(q)
            em = self._ranked(es)[: self.p.embed_candidates]
        br = {d: i for i, d in enumerate(bm, 1)}
        er = {d: i for i, d in enumerate(em, 1)}
        k = self.p.rrf_k
        fused = {d: (1 / (k + br[d]) if d in br else 0.0) + (1 / (k + er[d]) if d in er else 0.0) for d in {*br, *er}}
        ranked = self._ranked(fused)
        hit = lambda d: Hit(d, round(fused[d], 9), br.get(d), er.get(d),
                            round(float(bs[d]), 6) if d in bs else None, round(float(es[d]), 6) if d in es else None)
        # 분석 기록: top_k 밖으로 밀린 후보 (바로 다음 top_k개까지). 결과에는 영향 없음
        self.last_search = {"fused_candidates": len(fused), "bm25_hits": len(bm), "embed_hits": len(em),
                            "outside_top_k": [hit(d) for d in ranked[top:2 * top]]}
        return [hit(d) for d in ranked[:top]]
