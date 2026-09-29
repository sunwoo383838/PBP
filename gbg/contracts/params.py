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
    temperature: float
    max_tokens: int = Field(ge=1)
    context_length: int = Field(ge=1)
    tool_choice: Literal["auto", "none"] = "auto"
    extra_body: dict[str, JsonValue] = {}
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
    max_steps: int = Field(ge=1)
    format_retries: int = Field(ge=0)


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
    top_k: int = Field(ge=1)
    versions_per_attr: int = Field(ge=1)
    expand: int = Field(ge=0)
    evidence_cap: int = Field(ge=1)
    alias: AliasParams


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
