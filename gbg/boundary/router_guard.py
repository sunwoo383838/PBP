"""Routing 출력 검사: 검색 결과는 담당자 선택에만 쓴다.

Routing에서 요청 원문과 응답 원문은 코드가 그대로 옮기므로 검사하지 않는다. 검사 대상은 **라우터가 만든 출력**,
즉 선택 결과(담당자 id)와 referral(대상 그룹, 사유)이다. 실행 중에는 카나리 목록(private)을 읽을 수 없으므로
검색 결과에 있던 카나리 형태의 값(쉼표를 뺀 4자리 이상 정수, id의 일부는 제외)을 모아 대조한다. 요청 원문에 원래
있던 값은 뺀다. 걸리면 버그로 보고 실행을 멈춘다(호출하는 쪽이 FatalError). 카나리 목록과의 정규화 매칭은
채점기(Stage 7)가 오프라인으로 한다.
"""
import re

_NUM = re.compile(r"(?<![\w.,-])\d{1,3}(?:,\d{3})+(?![\d,])|(?<![\w.,-])\d{4,}(?![\w-])")


def canary_values(texts: list[str]) -> set[str]:
    """카나리 형태의 값: 쉼표를 뺀 4자리 이상 정수. CMT-00039 같은 id의 숫자 부분은 값이 아니다."""
    out = set()
    for t in texts:
        for m in _NUM.findall(t or ""):
            v = m.replace(",", "")
            if len(v) >= 4:
                out.add(v)
    return out


def router_leaks(outputs: list[str], retrieved: list[str], request: str) -> list[str]:
    """라우터가 만든 출력에 들어간, 검색 결과의 카나리 형태 값 (요청 원문에 있던 값 제외)."""
    return sorted((canary_values(retrieved) - canary_values([request])) & canary_values(outputs))
