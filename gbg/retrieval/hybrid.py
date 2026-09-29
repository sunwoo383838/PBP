"""하이브리드 검색: 그룹 하나의 이력(떠난 에이전트 포함) 말뭉치에서 BM25 순위와 임베딩 순위를 RRF(k=60)로 결합, 상위 20.

말뭉치는 저장소에서 증분 동기화한다. 문서 id = (에이전트, 이력 seq). 같은 점수면 최신(날짜, seq가 큰 것) 먼저.
그룹 경계: 이 그룹 소속 에이전트의 이력만 색인한다.
"""
from dataclasses import dataclass
from typing import Literal

from gbg.contracts.params import RetrievalParams
from gbg.kernel.access_guard import AccessGuard
from gbg.kernel.tools import Resource

from .bm25 import BM25Index
from .embed import Embedder, VectorIndex

Mode = Literal["hybrid", "bm25", "embed"]
Doc = tuple[str, int]                           # (agent, seq)


@dataclass(frozen=True)
class Hit:
    doc: Doc
    score: float
    bm25_rank: int | None
    embed_rank: int | None


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
    def __init__(self, stores, group: str, embedder: Embedder, params: RetrievalParams):
        self.stores, self.group, self.embedder, self.p = stores, group, embedder, params
        self.bm25 = BM25Index(params.bm25.k1, params.bm25.b)
        self.vectors = VectorIndex()
        self.meta: dict[Doc, tuple[int, int]] = {}     # doc → (day, seq) 정렬용
        self._synced: dict[str, int] = {}

    def agents(self) -> list[str]:
        return sorted(a for a, (g, _) in self.stores.members.items() if g == self.group)

    async def sync(self):
        new_ids, new_texts = [], []
        for a in self.agents():
            entries = self.stores.history.entries(a)
            for e in entries[self._synced.get(a, 0):]:
                doc = (a, e.seq)
                self.bm25.add(doc, e.text)
                self.meta[doc] = (e.day, e.seq)
                new_ids.append(doc)
                new_texts.append(e.text)
            self._synced[a] = len(entries)
        if new_ids:
            self.vectors.add(new_ids, await self.embedder.embed(new_texts))

    def _recency(self, doc: Doc):
        day, seq = self.meta[doc]
        return (-day, -seq, doc[0])

    def _ranked(self, scores: dict[Doc, float]) -> list[Doc]:
        return sorted(scores, key=lambda d: (-round(scores[d], 9), *self._recency(d)))

    async def search(self, query: str, mode: Mode = "hybrid", top: int | None = None) -> list[Hit]:
        await self.sync()
        top = top or self.p.top_k
        bm = self._ranked(self.bm25.scores(query)) if mode in ("hybrid", "bm25") else []
        em: list[Doc] = []
        if mode in ("hybrid", "embed") and self.vectors.ids:
            q = (await self.embedder.embed([query]))[0]
            em = self._ranked(self.vectors.scores(q))[: self.p.embed_candidates]
        br = {d: i for i, d in enumerate(bm, 1)}
        er = {d: i for i, d in enumerate(em, 1)}
        k = self.p.rrf_k
        fused = {d: (1 / (k + br[d]) if d in br else 0.0) + (1 / (k + er[d]) if d in er else 0.0) for d in {*br, *er}}
        return [Hit(d, round(fused[d], 9), br.get(d), er.get(d)) for d in self._ranked(fused)[:top]]
