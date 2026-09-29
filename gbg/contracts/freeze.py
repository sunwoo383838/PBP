"""조회 설정 동결 (configs/retrieval_freeze.yaml).

조회 설정은 개발 시드에서 정하고 동결한다. 평가 시드 시나리오는 동결된 해시와 지금 조회 설정의 해시가 같을 때만
실행한다 (동결 전이거나 다르면 거부).
"""
import hashlib
import json
from pathlib import Path

import yaml
from pydantic import Field

from ._base import Contract
from .params import RetrievalParams


DEFAULT_FREEZE = Path(__file__).resolve().parents[2] / "configs" / "retrieval_freeze.yaml"


class FreezeError(ValueError):
    """평가 시드인데 조회 설정이 동결되지 않았거나 동결된 설정과 다르다."""


class RetrievalFreeze(Contract):
    dev_seeds: list[int] = Field(min_length=1)
    eval_seeds: list[int] = Field(min_length=1)
    retrieval_params_sha256: str | None = None


def retrieval_hash(p: RetrievalParams) -> str:
    return hashlib.sha256(json.dumps(p.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()


def load_freeze(path: Path) -> RetrievalFreeze:
    f = RetrievalFreeze.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
    if set(f.dev_seeds) & set(f.eval_seeds):
        raise ValueError(f"개발·평가 시드가 겹친다: {sorted(set(f.dev_seeds) & set(f.eval_seeds))}")
    return f


def check_frozen(freeze: RetrievalFreeze, scenario_seed: int | None, p: RetrievalParams | None):
    """평가 시드면 동결된 조회 설정과 같은지 확인한다. 개발 시드·시드 없는 시나리오(픽스처)는 통과."""
    if scenario_seed not in freeze.eval_seeds:
        return
    if freeze.retrieval_params_sha256 is None:
        raise FreezeError(f"평가 시드 {scenario_seed}: 조회 설정이 아직 동결되지 않았다 (retrieval_eval --freeze)")
    if p is None:
        raise FreezeError(f"평가 시드 {scenario_seed}: 조회 설정을 넘기지 않아 동결 해시와 대조할 수 없다")
    if retrieval_hash(p) != freeze.retrieval_params_sha256:
        raise FreezeError(f"평가 시드 {scenario_seed}: 조회 설정이 동결된 설정과 다르다")


def mark_frozen(path: Path, p: RetrievalParams) -> str:
    """동결 해시를 파일에 적는다 (주석은 보존하고 해당 줄만 바꾼다)."""
    h = retrieval_hash(p)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    out = [f"retrieval_params_sha256: {h}" if x.startswith("retrieval_params_sha256:") else x for x in lines]
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")
    return h
