"""재정렬: DeepInfra의 Qwen3-Reranker (params.retrieval.rerank_model). 점수는 (모델, 질의, 문서) 해시로 SQLite에 캐시한다.
bge-reranker-v2-m3는 DeepInfra에 없고 이 서버 CPU(AVX2 없음)에서는 질의당 약 16초라 쓰지 않는다 (2026-09-29).

    DeepInfraReranker     실행용
    NullReranker          재정렬 없음(점수 0): 테스트·오프라인 비교용. 후보는 하이브리드 순위를 그대로 따른다
    CachedReranker        캐시 + 모드(LIVE: 없으면 계산해 저장 / REPLAY: 없으면 즉시 실패)
"""
import hashlib
import os
import sqlite3
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

import httpx

from gbg.contracts.params import LLMParams
from gbg.kernel.scheduler import FatalError


class RerankMiss(FatalError):
    """REPLAY 모드에서 캐시에 없는 (질의, 문서)."""


class Reranker(Protocol):
    name: str

    def score(self, query: str, docs: Sequence[str]) -> list[float]: ...


class NullReranker:
    name = "none"

    def score(self, query: str, docs: Sequence[str]) -> list[float]:
        return [0.0] * len(docs)


class DeepInfraReranker:
    """DeepInfra 추론 API (/v1/inference/<model>, 질의 하나 + 문서 목록 → 점수). 재시도는 LLM 설정을 따른다."""
    def __init__(self, llm: LLMParams, model: str, batch: int = 64, api_key: str | None = None,
                 transport: httpx.BaseTransport | None = None):
        from gbg.llm.backend import _local_key
        self.llm, self.name, self.batch, self.transport = llm, model, batch, transport
        self.api_key = api_key or os.environ.get(llm.api_key_env) or _local_key()
        self.api_calls = 0

    MAX_CHARS = 16000                          # 문서 하나의 앞부분만 (Qwen3-Reranker-8B 입력 한도 40,960토큰)
    MAX_QUERY = 2000

    def _post(self, client: httpx.Client, query: str, docs: list[str]) -> list[float]:
        """긴 에피소드(과제를 이어 풀 때 생기는 긴 문답)는 앞부분으로 재정렬한다. 한도 초과로 거부되면 절반씩 줄여 재시도."""
        from gbg.llm.backend import LLMError
        cap = self.MAX_CHARS
        for _ in range(4):
            try:
                return self._post_once(client, query[:self.MAX_QUERY], [d[:cap] for d in docs])
            except LLMError as e:
                if "context length" not in str(e) and "input_tokens" not in str(e):
                    raise
                cap //= 2
        return self._post_once(client, query[:self.MAX_QUERY], [d[:cap] for d in docs])

    def _post_once(self, client: httpx.Client, query: str, docs: list[str]) -> list[float]:
        from gbg.llm.backend import Backoff, LLMError
        r, last = self.llm.retry, ""
        bo, attempt = Backoff(r), 0
        while True:
            attempt += 1
            self.api_calls += 1
            status = None
            try:
                resp = client.post(f"/v1/inference/{self.name}", json={"queries": [query], "documents": docs})
            except httpx.TransportError as e:
                last = f"{type(e).__name__}: {e}"
            else:
                if resp.status_code == 200:
                    scores = resp.json()["scores"]
                    if len(scores) != len(docs):
                        raise LLMError(f"재정렬 점수 수가 다르다 ({len(scores)} != {len(docs)})")
                    return [float(x) for x in scores]
                status, last = resp.status_code, f"HTTP {resp.status_code}: {resp.text[:300]}"
                if resp.status_code != 429 and resp.status_code < 500:
                    raise LLMError(f"재정렬 요청 거부 {last}")
            if (wait := bo.next(status)) is None:
                break
            time.sleep(wait)
        raise LLMError(f"재정렬 {attempt}회 시도 후 실패: {last}")

    def score(self, query: str, docs: Sequence[str]) -> list[float]:
        if not docs:
            return []
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        base = self.llm.base_url.split("/v1/")[0].rstrip("/") if "/v1/" in self.llm.base_url else "https://api.deepinfra.com"
        with httpx.Client(base_url=base, transport=self.transport, timeout=self.llm.timeout_s, headers=headers) as client:
            out = []
            for i in range(0, len(docs), self.batch):
                out += self._post(client, query, list(docs[i:i + self.batch]))
        return out


class RerankCache:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False, timeout=60)   # 재정렬은 작업 스레드에서 돈다
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS rerank (model TEXT NOT NULL, key TEXT NOT NULL, "
                        "score REAL NOT NULL, PRIMARY KEY (model, key))")

    @staticmethod
    def key(query: str, doc: str) -> str:
        return hashlib.sha256(f"{query}\x00{doc}".encode()).hexdigest()

    def get(self, model: str, query: str, doc: str) -> float | None:
        row = self.db.execute("SELECT score FROM rerank WHERE model = ? AND key = ?",
                              (model, self.key(query, doc))).fetchone()
        return row[0] if row else None

    def put(self, model: str, query: str, doc: str, score: float):
        self.db.execute("INSERT OR IGNORE INTO rerank (model, key, score) VALUES (?, ?, ?)",
                        (model, self.key(query, doc), score))


class CachedReranker:
    def __init__(self, inner: Reranker, cache: RerankCache, mode: Literal["LIVE", "REPLAY"] = "LIVE"):
        self.inner, self.cache, self.mode, self.name = inner, cache, mode, inner.name
        self.computed = 0

    def score(self, query: str, docs: Sequence[str]) -> list[float]:
        got = [self.cache.get(self.name, query, d) for d in docs]
        missing = sorted({d for d, s in zip(docs, got) if s is None})
        if missing and self.mode == "REPLAY":
            raise RerankMiss(f"REPLAY 재정렬 캐시에 없는 문서 {len(missing)}개")
        if missing:
            for d, s in zip(missing, self.inner.score(query, missing)):
                self.cache.put(self.name, query, d, s)
            self.computed += len(missing)
        return [s if s is not None else self.cache.get(self.name, query, d) for d, s in zip(docs, got)]
