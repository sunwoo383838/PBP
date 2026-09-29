"""실행 파라미터 (configs/params.yaml). 선언 밖 키는 로드 시 오류."""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field, JsonValue, ValidationError

from ._base import Contract
from .conditions import ConfigError


class KernelParams(Contract):
    rounds_per_day: int = Field(3, ge=1)
    hop_limit: int = Field(4, ge=1)


class RetryParams(Contract):
    max_attempts: int = Field(ge=1)
    base_delay_s: float = Field(ge=0)
    max_delay_s: float = Field(ge=0)


class LLMParams(Contract):
    base_url: str
    api_key_env: str
    models: dict[str, str]
    model: str | None = None                    # 모든 LLM 호출이 쓰는 별칭 (models의 키)
    temperature: float
    max_tokens: int = Field(ge=1)
    context_length: int = Field(ge=1)
    tool_choice: Literal["auto", "none"] = "auto"
    extra_body: dict[str, JsonValue] = {}
    service_tier: Literal["priority", "default"] | None = None   # 처리 순서만 바꾼다: 캐시 키에 넣지 않는다
    seed_per_call: bool = False                 # 호출마다 요청 내용에서 정한 seed를 싣고 기록한다
    concurrency: int = Field(ge=1)
    timeout_s: float = Field(gt=0)
    retry: RetryParams


class TokenizerParams(Contract):
    repo: str
    revision: str
    sha256: str


class ContextParams(Contract):
    raw_window: int = Field(ge=1)
    summary: int = Field(ge=0)


class AgentParams(Contract):
    max_steps: int | None = Field(default=None, ge=1)   # None = 단계 상한 없음 (과제 예산이 상한)
    safety_steps: int = Field(default=200, ge=1)        # 예산 상한이 없는 조건(full_load)의 무한 루프 방지
    responder_max_steps: int = Field(default=10, ge=1)  # 응답자 루프 상한 (모든 조건 동일). 닿으면 reply 전용 호출 1회
    responder_exclude_tools: list[str] = []            # 응답자에게 주지 않는 환경 도구 (모든 조건 동일)
    format_retries: int = Field(ge=0)
    full_load_tokens: int = Field(default=40000, ge=1)  # full_load의 load_group_history 상한 (넘으면 오래된 줄부터)


class BM25Params(Contract):
    k1: float = Field(gt=0)
    b: float = Field(ge=0, le=1)


class AliasParams(Contract):
    max_edit: int = Field(ge=0)
    embed_threshold: float = Field(gt=0, le=1)


class RetrievalParams(Contract):
    embed_model: str
    embed_batch: int = Field(ge=1)
    bm25: BM25Params
    rrf_k: int = Field(ge=1)
    embed_candidates: int = Field(ge=1)
    top_k: int = Field(ge=1)                            # 하이브리드(RRF) 상위 후보 수 (에피소드)
    rerank_model: str | None = None                     # DeepInfra 재정렬 모델. None이면 재정렬 없음(하이브리드 순)
    evidence_cap: int = Field(ge=1)
    alias: AliasParams
    catalog_link_fields: list[str] = []


class Params(Contract):
    kernel: KernelParams
    llm: LLMParams
    tokenizer: TokenizerParams
    context: ContextParams
    agent: AgentParams
    retrieval: RetrievalParams


def load_params(path: Path) -> Params:
    try:
        return Params.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
    except ValidationError as e:
        raise ConfigError(f"{path}: 파라미터 오류\n{e}") from e
