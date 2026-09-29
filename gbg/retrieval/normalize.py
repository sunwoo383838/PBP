"""정규화: NFKC(전각·반각 통일), 대소문자, 숫자의 천 단위 쉼표 제거, 공백 정리, 경칭 제거."""
import re
import unicodedata

HONORIFIC_SUFFIXES = (
    # 한국어 호칭·직함
    "님", "씨", "과장", "대리", "선임", "부장", "차장", "팀장", "사원", "주임", "책임", "수석", "이사", "실장", "본부장",
    # 일본어 경칭·직함
    "さん", "様", "さま", "くん", "君", "ちゃん", "殿", "氏", "課長", "部長", "係長", "主任",
    # 영어
    "(mgr)", "mgr",
)
HONORIFIC_PREFIXES = ("mr.", "ms.", "mrs.", "dr.", "mr", "ms", "mrs")
_SUFFIXES = sorted(HONORIFIC_SUFFIXES, key=len, reverse=True)
_THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}(?!\d))")


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).casefold()
    t = _THOUSANDS.sub("", t)
    return " ".join(t.split())


def strip_honorifics(name: str) -> str:
    """이름 끝의 경칭·직함(붙어 있든 띄어 있든)과 영어 호칭 접두를 떼어 낸다. 전부 떼면 원래 이름을 돌려준다."""
    t = normalize(name)
    changed = True
    while changed:
        changed = False
        for p in HONORIFIC_PREFIXES:
            if t.startswith(p + " "):
                t, changed = t[len(p) + 1:].strip(), True
        for s in _SUFFIXES:
            if t.endswith(s) and len(t) > len(s):
                t, changed = t[: -len(s)].strip(), True
                break
    return t or normalize(name)
