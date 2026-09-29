"""DeepInfra OpenAI 호환 백엔드. temperature 0, thinking 끔, 429·5xx 지수 백오프, 모델별 전역 동시 요청 상한.

모드
    LIVE      캐시에 없으면 API를 부르고 저장한다. 같은 키가 동시에 들어오면 한 번만 부른다.
    REPLAY    캐시에만 의존한다. 없으면 즉시 실패(ReplayMiss)해 런을 멈춘다.
    SCRIPTED  API도 캐시도 쓰지 않고 스크립트 함수가 응답한다 (테스트).
응답은 정규형 {"content", "tool_calls": [{"name", "arguments"}], "finish_reason", "usage"}으로 저장·반환한다.
제공자가 붙인 도구 호출 id는 버리고, 에이전트 루프가 결정적 id를 붙인다.
"""
import asyncio
import os
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

import httpx

from gbg.contracts.params import LLMParams
from gbg.kernel.scheduler import FatalError

from .cache import ResponseCache, request_key

Mode = Literal["LIVE", "REPLAY", "SCRIPTED"]
Script = Callable[[dict], dict]
_THINK = re.compile(r"<think>.*?</think>\s*", re.S)


def _local_key() -> str | None:
    try:
        from . import secrets
    except ImportError:
        return None
    return getattr(secrets, "DEEPINFRA_API_KEY", None)


class LLMError(FatalError):
    """API가 재시도 후에도 실패하거나 요청이 잘못됨. 런을 멈추고, WAL 체크포인트에서 재개한다."""


class ReplayMiss(FatalError):
    """REPLAY 모드에서 캐시에 없는 요청."""


@dataclass(frozen=True)
class LLMResult:
    key: str
    model: str
    message: dict                               # {"content", "tool_calls"}
    usage: dict
    finish_reason: str | None
    cached: bool
    attempts: int
    latency_ms: int


def normalize(raw: dict) -> dict:
    """OpenAI chat.completions 응답 → 정규형. DeepInfra는 thinking 내용을 message.reasoning_content로 따로 준다."""
    choice = raw["choices"][0]
    msg = choice["message"]
    content = msg.get("content")
    stripped = False
    if content and "<think>" in content:
        content, stripped = _THINK.sub("", content), True
    calls = [{"name": c["function"]["name"], "arguments": c["function"].get("arguments") or "{}"}   # 제공자 id는 버린다
             for c in msg.get("tool_calls") or []]
    usage = raw.get("usage") or {}
    out = {"content": content or None, "tool_calls": calls, "finish_reason": choice.get("finish_reason"),
           "usage": {"prompt_tokens": usage.get("prompt_tokens", 0), "completion_tokens": usage.get("completion_tokens", 0),
                     "estimated_cost": usage.get("estimated_cost", 0.0)}}
    if stripped:
        out["thinking_stripped"] = True
    if msg.get("reasoning_content"):                                    # thinking이 켜져 있었다는 신호 (내용은 버린다)
        out["reasoning_leaked"] = True
    return out


class LLMBackend:
    def __init__(self, params: LLMParams, *, mode: Mode, model: str, cache: ResponseCache | None = None,
                 script: Script | None = None, transport: httpx.AsyncBaseTransport | None = None,
                 api_key: str | None = None, sleep: Callable[[float], Awaitable] = asyncio.sleep):
        if model not in params.models:
            raise ValueError(f"알 수 없는 모델 별칭 '{model}' ({', '.join(params.models)})")
        if mode in ("LIVE", "REPLAY") and cache is None:
            raise ValueError(f"{mode} 모드에는 캐시가 필요하다")
        if mode == "SCRIPTED" and script is None:
            raise ValueError("SCRIPTED 모드에는 스크립트가 필요하다")
        self.params, self.mode, self.model = params, mode, model
        self.cache, self.script, self.transport, self.sleep = cache, script, transport, sleep
        self.api_key = api_key or os.environ.get(params.api_key_env) or _local_key()
        self.api_calls = 0
        self._inflight: dict[str, asyncio.Future] = {}
        self._sem: tuple[asyncio.AbstractEventLoop, asyncio.Semaphore] | None = None

    def build_request(self, messages: list[dict], tools: list[dict]) -> dict:
        req = {"model": self.params.models[self.model], "messages": messages,
               "temperature": self.params.temperature, "max_tokens": self.params.max_tokens, **self.params.extra_body}
        if tools:
            req["tools"] = tools
            req["tool_choice"] = self.params.tool_choice
        return req

    async def complete(self, messages: list[dict], tools: list[dict]) -> LLMResult:
        req = self.build_request(messages, tools)
        key = request_key(req)
        t0 = time.perf_counter()
        if self.mode == "SCRIPTED":
            return self._result(key, req, self.script(req), False, 0, t0)
        hit = self.cache.get(key)
        if hit is not None:
            return self._result(key, req, hit, True, 0, t0)
        if self.mode == "REPLAY":
            raise ReplayMiss(f"REPLAY 캐시에 없는 요청 {key}")
        if key in self._inflight:                                     # 같은 요청이 이미 날아가는 중
            resp, attempts = await asyncio.shield(self._inflight[key])
            return self._result(key, req, resp, True, 0, t0)
        fut = asyncio.get_running_loop().create_future()
        self._inflight[key] = fut
        try:
            resp, attempts = await self._call_api(req)
            resp = self.cache.put(key, req, resp)                      # 먼저 저장된 응답이 정본
            fut.set_result((resp, attempts))
        except BaseException as e:
            fut.set_exception(e)
            raise
        finally:
            del self._inflight[key]
        return self._result(key, req, resp, False, attempts, t0)

    def _result(self, key, req, resp, cached, attempts, t0) -> LLMResult:
        return LLMResult(key=key, model=req["model"], message={"content": resp["content"], "tool_calls": resp["tool_calls"]},
                         usage=resp["usage"], finish_reason=resp.get("finish_reason"), cached=cached, attempts=attempts,
                         latency_ms=int((time.perf_counter() - t0) * 1000))

    def _semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        if self._sem is None or self._sem[0] is not loop:
            self._sem = (loop, asyncio.Semaphore(self.params.concurrency))
        return self._sem[1]

    async def _call_api(self, req: dict) -> tuple[dict, int]:
        if not self.api_key and self.transport is None:
            raise LLMError(f"API 키가 없다 (환경 변수 {self.params.api_key_env})")
        r = self.params.retry
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        last = ""
        async with self._semaphore():
            async with httpx.AsyncClient(base_url=self.params.base_url, transport=self.transport,
                                         timeout=self.params.timeout_s, headers=headers) as client:
                for attempt in range(1, r.max_attempts + 1):
                    self.api_calls += 1
                    try:
                        resp = await client.post("/chat/completions", json=req)
                    except httpx.TransportError as e:
                        last = f"{type(e).__name__}: {e}"
                    else:
                        if resp.status_code == 200:
                            return normalize(resp.json()), attempt
                        last = f"HTTP {resp.status_code}: {resp.text[:300]}"
                        if resp.status_code != 429 and resp.status_code < 500:
                            raise LLMError(f"요청 거부 {last}")
                    if attempt < r.max_attempts:
                        await self.sleep(min(r.max_delay_s, r.base_delay_s * 2 ** (attempt - 1)))
        raise LLMError(f"{r.max_attempts}회 시도 후 실패: {last}")
