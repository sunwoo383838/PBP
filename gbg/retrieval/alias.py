"""별칭 해소: 정규화 후 정확 일치 → 편집 거리 1~2 → 별칭 임베딩 최근접. 에이전트 발화의 엔티티 태깅에도 쓴다.

id처럼 생긴 표면형(CMT-00001, E-SEL-1001)은 한 글자 차이가 다른 엔티티이므로 정확 일치만 허용한다.
숫자가 든 이름(영업1팀)도 숫자가 바뀌면 다른 엔티티이므로, 편집 거리는 숫자열이 같은 표면형끼리만 잰다.
"""
import re
from dataclasses import dataclass

import numpy as np

from .bm25 import ID_RE
from .embed import Embedder
from .normalize import normalize, strip_honorifics


def edit_distance(a: str, b: str, limit: int) -> int:
    """레벤슈타인 거리. limit을 넘으면 limit + 1."""
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
        if min(cur) > limit:
            return limit + 1
        prev = cur
    return prev[-1]


_DIGITS = re.compile(r"\d+")


def _is_id(form: str) -> bool:
    return bool(ID_RE.fullmatch(form))


@dataclass(frozen=True)
class Resolution:
    entities: tuple[str, ...]                   # 비었으면 해소 실패, 둘 이상이면 모호
    method: str                                 # exact | edit | embedding | none
    score: float = 0.0


class AliasResolver:
    def __init__(self, table: dict[str, list[str]], *, max_edit: int = 2, embed_threshold: float = 0.85,
                 embedder: Embedder | None = None):
        """table: 엔티티 id → 별칭 (한 그룹의 별칭표)."""
        self.max_edit, self.threshold, self.embedder = max_edit, embed_threshold, embedder
        forms: dict[str, set[str]] = {}
        for e, al in table.items():
            for surface in (e, *al):
                for f in {normalize(surface), strip_honorifics(surface)}:
                    if f:
                        forms.setdefault(f, set()).add(e)
        self.forms = {f: tuple(sorted(es)) for f, es in sorted(forms.items())}
        self._vecs: np.ndarray | None = None

    def _exact(self, q: str) -> tuple[str, ...]:
        return tuple(sorted({e for f in {normalize(q), strip_honorifics(q)} for e in self.forms.get(f, ())}))

    def _edit(self, q: str) -> tuple[str, ...]:
        s = strip_honorifics(q)
        if _is_id(s):
            return ()
        limit = min(self.max_edit, max(1, len(s) // 3))
        best, hits = limit + 1, set()
        digits = _DIGITS.findall(s)
        for f, es in self.forms.items():
            if _is_id(f) or _DIGITS.findall(f) != digits:
                continue
            d = edit_distance(s, f, limit)
            if d < best:
                best, hits = d, set(es)
            elif d == best and d <= limit:
                hits |= set(es)
        return tuple(sorted(hits)) if best <= limit else ()

    def resolve_sync(self, text: str) -> Resolution:
        """정확 일치와 편집 거리까지만 (임베딩 없이)."""
        if ex := self._exact(text):
            return Resolution(ex, "exact", 1.0)
        if ed := self._edit(text):
            return Resolution(ed, "edit", 0.0)
        return Resolution((), "none")

    async def resolve(self, text: str) -> Resolution:
        r = self.resolve_sync(text)
        if r.entities or self.embedder is None or _is_id(strip_honorifics(text)):
            return r
        all_forms = [f for f in self.forms if not _is_id(f)]
        if not all_forms:
            return r
        if self._vecs is None:
            self._vecs = await self.embedder.embed(all_forms)
        digits = _DIGITS.findall(strip_honorifics(text))
        keep = [i for i, f in enumerate(all_forms) if _DIGITS.findall(f) == digits]    # 숫자가 다르면 다른 엔티티
        if not keep:
            return r
        forms = [all_forms[i] for i in keep]
        q = (await self.embedder.embed([strip_honorifics(text)]))[0]
        sims = self._vecs[keep] @ q
        i = int(np.argmax(sims))
        if float(sims[i]) < self.threshold:
            return Resolution((), "none", float(sims[i]))
        top = float(sims[i])
        tied = sorted({e for f, s in zip(forms, sims) if abs(float(s) - top) < 1e-6 for e in self.forms[f]})
        return Resolution(tuple(tied), "embedding", top)

    def tag(self, text: str) -> list[str]:
        """원문에 들어 있는 표면형(정규화·경칭 제거 후, 2글자 이상)의 엔티티. 결정적이다."""
        t = normalize(text)
        found = set()
        for f, es in self.forms.items():
            if len(f) >= 2 and f in t:
                found.update(es)
        return sorted(found)
