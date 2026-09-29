"""원리상 풀 수 없는 과제 표시 (채점기, 오프라인). 2026-09-29 결정 (b): 정확도 분모에서 빼고 따로 보고한다.

    unreachable_local  요청자 자기 그룹 need의 결정 필수 조각을, 과제 시점에 활동 중인 보유자가 하나도 없이
                       떠난 구성원만 들고 있다. 자기 그룹 기록을 검색하는 경로가 어떤 조건에도 없다(경계 모듈은
                       다른 그룹의 요청만 받고, full_load는 다른 그룹 이력만 불러온다).
정답 원장의 보유자 active 표시(과제 시점)만 쓴다.
"""


def unreachable(gold_rows: list[dict]) -> dict[str, list[dict]]:
    """wid → 원인 목록. 풀 수 있는 과제는 넣지 않는다."""
    out: dict[str, list[dict]] = {}
    for g in gold_rows:
        for n in g["needs"]:
            if not n.get("local"):
                continue
            crit = n.get("critical_components")
            for s in n["sources"]:
                if s["type"] != "frag" or s.get("role") == "distractor":
                    continue
                f = s["frag"]
                if crit is not None and f["fid"] not in crit:
                    continue
                hs = f.get("holders", [])
                if hs and not any(h.get("active") for h in hs):
                    out.setdefault(g["wid"], []).append({"reason": "unreachable_local", "need": n["sem"], "fid": f["fid"],
                                                         "disc": f.get("disc"), "holders": [h["agent"] for h in hs]})
    return out
