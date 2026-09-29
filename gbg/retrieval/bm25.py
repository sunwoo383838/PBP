"""그룹별 증분 BM25. 토큰 = 공백 단어 + 한국어·일본어 문자 2-gram + id·금액 통토큰. k1=1.5, b=0.75."""
import math
import re
from collections import Counter
from collections.abc import Hashable

from .normalize import normalize

ID_RE = re.compile(r"[a-z]{1,6}(?:-[a-z0-9]{1,8})*-\d{2,}")           # cmt-00001, e-sel-1001, fin-sel.a3 제외
NUM_RE = re.compile(r"\d{3,}")                                      # 금액 등 긴 숫자 (쉼표는 정규화에서 제거)
WORD_RE = re.compile(r"[0-9a-z]+(?:[.\-][0-9a-z]+)*")
_CJK = "\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
CJK_RE = re.compile(f"[0-9{_CJK}]*[{_CJK}][0-9{_CJK}]*")               # 한중일 글자가 든 구간 (숫자 포함: 영업1팀)


def tokenize(text: str) -> list[str]:
    t = normalize(text)
    toks = ID_RE.findall(t) + NUM_RE.findall(t) + WORD_RE.findall(t)
    for run in CJK_RE.findall(t):
        toks += [run] if len(run) == 1 else [run[i:i + 2] for i in range(len(run) - 1)]
    return toks


class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs: dict[Hashable, Counter] = {}
        self.lengths: dict[Hashable, int] = {}
        self.df: Counter = Counter()

    def __len__(self):
        return len(self.docs)

    def add(self, doc_id: Hashable, text: str):
        if doc_id in self.docs:
            raise ValueError(f"문서 {doc_id} 중복 추가")
        tf = Counter(tokenize(text))
        self.docs[doc_id], self.lengths[doc_id] = tf, sum(tf.values())
        self.df.update(tf.keys())

    def scores(self, query: str) -> dict[Hashable, float]:
        n = len(self.docs)
        if not n:
            return {}
        avg = sum(self.lengths.values()) / n
        q = set(tokenize(query))
        out: dict[Hashable, float] = {}
        for doc, tf in self.docs.items():
            s = 0.0
            for tok in q:
                f = tf.get(tok)
                if not f:
                    continue
                idf = math.log((n - self.df[tok] + 0.5) / (self.df[tok] + 0.5) + 1)
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.lengths[doc] / avg))
            if s > 0:
                out[doc] = s
        return out
