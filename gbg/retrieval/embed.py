"""임베딩: 다국어 모델 하나(버전 고정)를 텍스트 해시로 SQLite에 캐시하고, 그룹별 numpy 배열로 전수 코사인.

    DeepInfraEmbedder  BAAI/bge-m3 (params.retrieval.embed_model), 실행용
    HashEmbedder       문자 1~3-gram 해시 벡터, API 없는 결정적 대체 (테스트·오프라인)
    CachedEmbedder     캐시 + 모드(LIVE: 없으면 계산해 저장 / REPLAY: 없으면 즉시 실패)
"""
import hashlib
import os
import sqlite3
from collections.abc import Hashable, Sequence
from pathlib import Path
from typing import Literal, Protocol

import httpx
import numpy as np

from gbg.contracts.params import LLMParams
from gbg.kernel.scheduler import FatalError

from .normalize import normalize


class EmbeddingMiss(FatalError):
    """REPLAY 모드에서 캐시에 없는 텍스트."""


class Embedder(Protocol):
    name: str

    async def embed(self, texts: Sequence[str]) -> np.ndarray: ...


def _unit(m: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(m, axis=1, keepdims=True)
    return (m / np.where(n == 0, 1, n)).astype(np.float32)


class HashEmbedder:
    """정규화한 문자열의 문자 1~3-gram을 해시해 dim 차원에 더한 단위 벡터. 결정적이고 API가 없다."""
    def __init__(self, dim: int = 512):
        self.dim, self.name = dim, f"hash-ngram-{dim}"

    async def embed(self, texts: Sequence[str]) -> np.ndarray:
        m = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            s = normalize(t)
            for n in (1, 2, 3):
                for j in range(len(s) - n + 1):
                    h = int.from_bytes(hashlib.blake2b(s[j:j + n].encode(), digest_size=8).digest(), "big")
                    m[i, h % self.dim] += 1.0 if (h >> 63) else -1.0
        return _unit(m)


class DeepInfraEmbedder:
    def __init__(self, llm: LLMParams, model: str, api_key: str | None = None,
                 transport: httpx.AsyncBaseTransport | None = None):
        from gbg.llm.backend import _local_key
        self.llm, self.name, self.transport = llm, model, transport
        self.api_key = api_key or os.environ.get(llm.api_key_env) or _local_key()
        self.api_calls = 0

    MAX_CHARS = 16000                          # bge-m3 입력 한도 8,192토큰 안쪽 (영문 약 4k토큰). 넘으면 앞부분만 임베딩

    async def embed(self, texts: Sequence[str]) -> np.ndarray:
        """긴 텍스트(과제를 이어 풀 때 생기는 긴 문답 에피소드)는 앞부분만 임베딩한다. BM25·증거 표시는 원문 전체.
        그래도 모델 한도를 넘으면(문자당 토큰이 많은 텍스트) 절반씩 줄여 다시 보낸다."""
        from gbg.llm.backend import LLMError
        cap = self.MAX_CHARS
        for _ in range(4):
            try:
                return await self._embed([t[:cap] for t in texts])
            except LLMError as e:
                if "context length" not in str(e) and "input_tokens" not in str(e):
                    raise
                cap //= 2
        return await self._embed([t[:cap] for t in texts])

    async def _embed(self, texts: Sequence[str]) -> np.ndarray:
        from gbg.llm.backend import Backoff, LLMError
        r = self.llm.retry
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        last, bo, attempt = "", Backoff(r), 0
        async with httpx.AsyncClient(base_url=self.llm.base_url, transport=self.transport, timeout=self.llm.timeout_s,
                                     headers=headers) as client:
            while True:
                attempt += 1
                self.api_calls += 1
                status = None
                try:
                    resp = await client.post("/embeddings", json={"model": self.name, "input": list(texts),
                                                                  "encoding_format": "float"})
                except httpx.TransportError as e:
                    last = f"{type(e).__name__}: {e}"
                else:
                    if resp.status_code == 200:
                        data = sorted(resp.json()["data"], key=lambda d: d["index"])
                        return _unit(np.array([d["embedding"] for d in data], dtype=np.float32))
                    status, last = resp.status_code, f"HTTP {resp.status_code}: {resp.text[:300]}"
                    if resp.status_code != 429 and resp.status_code < 500:
                        raise LLMError(f"임베딩 요청 거부 {last}")
                if (wait := bo.next(status)) is None:
                    break
                import asyncio
                await asyncio.sleep(wait)
        raise LLMError(f"임베딩 {attempt}회 시도 후 실패: {last}")


class EmbeddingCache:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=60)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS embeddings (model TEXT NOT NULL, key TEXT NOT NULL, "
                        "vec BLOB NOT NULL, PRIMARY KEY (model, key))")

    @staticmethod
    def key(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, model: str, text: str) -> np.ndarray | None:
        row = self.db.execute("SELECT vec FROM embeddings WHERE model = ? AND key = ?", (model, self.key(text))).fetchone()
        return np.frombuffer(row[0], dtype=np.float32) if row else None

    def put(self, model: str, text: str, vec: np.ndarray):
        self.db.execute("INSERT OR IGNORE INTO embeddings (model, key, vec) VALUES (?, ?, ?)",
                        (model, self.key(text), np.asarray(vec, dtype=np.float32).tobytes()))

    def __len__(self):
        return self.db.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]


class CachedEmbedder:
    def __init__(self, inner: Embedder, cache: EmbeddingCache, mode: Literal["LIVE", "REPLAY"] = "LIVE", batch: int = 64):
        self.inner, self.cache, self.mode, self.batch = inner, cache, mode, batch
        self.name = inner.name
        self.computed = 0

    async def embed(self, texts: Sequence[str]) -> np.ndarray:
        missing = sorted({t for t in texts if self.cache.get(self.name, t) is None})
        if missing and self.mode == "REPLAY":
            raise EmbeddingMiss(f"REPLAY 임베딩 캐시에 없는 텍스트 {len(missing)}개")
        for i in range(0, len(missing), self.batch):
            chunk = missing[i:i + self.batch]
            for t, v in zip(chunk, await self.inner.embed(chunk)):
                self.cache.put(self.name, t, v)
            self.computed += len(chunk)
        return np.stack([self.cache.get(self.name, t) for t in texts]) if texts else np.zeros((0, 0), np.float32)


class VectorIndex:
    """그룹 하나의 문서 벡터. 추가 순서대로 쌓고 전수 코사인으로 찾는다. 같은 id를 다시 넣으면 그 행을 바꾼다."""
    def __init__(self):
        self.ids: list[Hashable] = []
        self.row: dict[Hashable, int] = {}
        self.matrix: np.ndarray | None = None

    def add(self, ids: Sequence[Hashable], vecs: np.ndarray):
        new = []
        for i, v in zip(ids, vecs):
            if i in self.row:
                self.matrix[self.row[i]] = v
            else:
                self.row[i] = len(self.ids) + len(new)
                new.append((i, v))
        if new:
            self.ids += [i for i, _ in new]
            m = np.stack([v for _, v in new])
            self.matrix = m if self.matrix is None else np.vstack([self.matrix, m])

    def scores(self, qvec: np.ndarray) -> dict[Hashable, float]:
        if self.matrix is None:
            return {}
        sims = self.matrix @ qvec
        return {i: float(s) for i, s in zip(self.ids, sims)}
