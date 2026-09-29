"""Qwen3 토크나이저 (리비전 고정). tokenizer.json을 고정 리비전에서 한 번 받아 sha256을 확인한 뒤 캐시에서 쓴다."""
import hashlib
import os
import urllib.request
from functools import lru_cache
from pathlib import Path

from tokenizers import Tokenizer

from gbg.contracts.params import TokenizerParams

CACHE = Path(os.environ.get("GBG_CACHE", Path.home() / ".cache" / "gbg")) / "tokenizers"


class TokenizerError(RuntimeError):
    pass


def tokenizer_path(p: TokenizerParams) -> Path:
    path = CACHE / f"{p.repo.replace('/', '--')}@{p.revision}" / "tokenizer.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://huggingface.co/{p.repo}/resolve/{p.revision}/tokenizer.json"
        tmp = path.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != p.sha256:
        raise TokenizerError(f"{path}: sha256 {digest} ≠ 고정값 {p.sha256}")
    return path


class QwenTokenizer:
    def __init__(self, p: TokenizerParams):
        self.params = p
        self._tok = Tokenizer.from_file(str(tokenizer_path(p)))

    def count(self, text: str) -> int:
        return len(self._tok.encode(text, add_special_tokens=False).ids)


def load_tokenizer(p: TokenizerParams) -> QwenTokenizer:
    return _load(p.repo, p.revision, p.sha256)


@lru_cache(maxsize=4)
def _load(repo: str, revision: str, sha256: str) -> QwenTokenizer:
    return QwenTokenizer(TokenizerParams(repo=repo, revision=revision, sha256=sha256))
