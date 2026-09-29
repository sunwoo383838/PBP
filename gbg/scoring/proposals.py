"""접수부 제안 값(proposals)의 채택 측정 (채점기, 오프라인).

요청자가 받은 제안마다, 같은 응답 안에서 제안 대상과 걸리는 담당자 항목(ref가 "Reply …")의 값을 찾고, 제출 답이
제안 값을 따랐는지(proposal), 제안과 다른 담당자 값을 따랐는지(member), 둘 다 아닌지(neither), 둘 다 들어 있는지
(both)로 나눈다. 값 비교는 수치면 수치(쉼표·단위 무시), 아니면 정규화한 문자열 일치.
조건 간 비교(예: Routing 정답·Ingress 오답 과제)는 보고 단계에서 이 행을 과제별로 붙여 고른다.
"""
import json
import re

from .delivery import _norm

_N = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def _nums(v) -> set[str]:
    return {m.replace(",", "").rstrip("0").rstrip(".") if "." in m else m.replace(",", "") for m in _N.findall(str(v))}


def _flat(x) -> list:
    if isinstance(x, dict):
        return [y for v in x.values() for y in _flat(v)]
    if isinstance(x, list):
        return [y for v in x for y in _flat(v)]
    return [x]


def _matches(value: str, answer_vals: list) -> bool:
    nv = _nums(value)
    if nv:
        return bool(nv & {n for a in answer_vals for n in _nums(a)})
    return _norm(value) in {_norm(str(a)) for a in answer_vals if a is not None}


def _related(prop_item: str, it: dict) -> bool:
    p = set(_norm(prop_item).split())
    ent, att = _norm(it.get("entity", "")), set(_norm(it.get("attribute", "")).split())
    return (ent and ent in _norm(prop_item)) or len(p & att) >= 2


def proposal_uptake(events: list[dict], wid: str, answer: dict | None) -> dict:
    req = next((e["payload"]["agent"] for e in events if e["type"] == "task_delivered" and e["payload"]["task_id"] == wid), None)
    vals = _flat(answer or {})
    rows = []
    for e in events:
        p = e["payload"]
        if not (e["type"] == "message" and p.get("task_id") == wid and p.get("kind") == "response"
                and p.get("from_agent") == req):
            continue
        r = p.get("response") or {}
        members = [x for x in r.get("items") or [] if str(x.get("ref", "")).startswith("Reply ")]
        for x in r.get("proposals") or []:
            mv = [m["value"] for m in members if _related(x["item"], m) and not _matches(m["value"], [x["value"]])]
            fp, fm = _matches(x["value"], vals), any(_matches(v, vals) for v in mv)
            rows.append({"item": x["item"], "proposed": x["value"], "member_values": mv, "refs": x["refs"],
                         "followed": "both" if fp and fm else "proposal" if fp else "member" if fm else "neither"})
    counts = {k: sum(r["followed"] == k for r in rows) for k in ("proposal", "member", "both", "neither")}
    return {"n": len(rows), **counts, "rows": rows}
