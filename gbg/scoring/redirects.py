"""소관 밖 안내(out_of_scope)와 항목 시점(day) 측정 (채점기, 오프라인).

    안내          경계 모듈이 받아들인 out_of_scope 안내 수, 코드가 거부한 수(사유별)
    대상 정답     안내 항목의 엔티티가 가리키는 need의 그룹(정답 원장)과 안내 대상 그룹이 같은가. 걸리는 need가 없으면 unmatched
    따름          안내 뒤 같은 과제에서 대상 그룹으로 요청이 나갔는가 (요청자가 다시 물었거나 Egress가 재발신)
    안내 후 전달  대상이 맞은 안내의 need가 요청자에게 전달됐는가 (delivery 행)
    day unknown   과제 중 오간 응답 항목 가운데 코드가 ref를 풀지 못해 day=unknown인 비율
"""
from .delivery import _norm
from .gates import need_surfaces


def redirect_metrics(events: list[dict], g: dict, fragments: dict, names: dict, delivery_rows: list[dict]) -> dict:
    wid = g["wid"]
    es = [e for e in events if e["payload"].get("task_id") == wid]
    delivered = {r["need"]: r["delivered"] for r in delivery_rows if r["task_id"] == wid}
    out = {"guided": 0, "rejected": {}, "target_correct": 0, "target_wrong": 0, "unmatched": 0, "followed": 0,
           "delivered_after": 0, "delivered_after_n": 0}
    for i, e in enumerate(es):
        p = e["payload"]
        if e["type"] != "boundary_decision" or p.get("stage") != "ingress":
            continue
        for x in p.get("redirects_rejected") or []:
            out["rejected"][x["why"]] = out["rejected"].get(x["why"], 0) + 1
        for x in p.get("redirects") or []:
            out["guided"] += 1
            ent = _norm(x["entity"])
            hit = [n for n in g["needs"] if not n.get("local") and ent and
                   any(s in ent or ent in s for s in need_surfaces(n, fragments, names))]
            if not hit:
                out["unmatched"] += 1
            elif any(n["group"] == x["referral_to"] for n in hit):
                out["target_correct"] += 1
                for n in hit:
                    if n["group"] == x["referral_to"] and n["sem"] in delivered:
                        out["delivered_after_n"] += 1
                        out["delivered_after"] += bool(delivered[n["sem"]])
            else:
                out["target_wrong"] += 1
            later = es[i + 1:]
            out["followed"] += any(q["type"] == "message" and q["payload"].get("kind") == "request"
                                   and q["payload"].get("to_group") == x["referral_to"] for q in later)
    items = [x for e in es if e["type"] == "message" and e["payload"].get("kind") == "response"
             for x in (e["payload"].get("response") or {}).get("items") or []]
    out["items"] = len(items)
    out["day_unknown"] = sum(x.get("day", "unknown") == "unknown" for x in items)
    return out


def summarize(rows: list[dict]) -> dict:
    tot = {k: sum(r[k] for r in rows) for k in ("guided", "target_correct", "target_wrong", "unmatched", "followed",
                                                 "delivered_after", "delivered_after_n", "items", "day_unknown")}
    rej: dict[str, int] = {}
    for r in rows:
        for k, v in r["rejected"].items():
            rej[k] = rej.get(k, 0) + v
    judged = tot["target_correct"] + tot["target_wrong"]
    return {**tot, "rejected": rej,
            "target_accuracy": round(tot["target_correct"] / judged, 4) if judged else None,
            "follow_rate": round(tot["followed"] / tot["guided"], 4) if tot["guided"] else None,
            "delivered_after_rate": round(tot["delivered_after"] / tot["delivered_after_n"], 4) if tot["delivered_after_n"] else None,
            "day_unknown_rate": round(tot["day_unknown"] / tot["items"], 4) if tot["items"] else None}
