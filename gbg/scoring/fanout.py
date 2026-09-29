"""경계 요청의 팬아웃 측정 (채점기, 오프라인). 라우터가 고른 구성원마다 같은 요청이 복제되는 비용과 효과를 본다.

    selected      경계 요청(ingress)당 선택 구성원 수 (재질의 대상 제외)
    duplicates    같은 경계 요청 안에서 다른 응답자 세션이 이미 조회한 (기록 키, 일차)를 다시 조회한 db.query 수
    disagreement  응답이 둘 이상인 경계 요청에서 같은 (엔티티, 속성)에 구성원들이 서로 다른 값을 낸 경우.
                  구성원 값의 정오: 결정 필수 조각의 원문 값·need가 참조한 DB 버전 값에 있는 값이면 correct,
                  다른 어느 쪽 값도 거기 없거나 3자리 이하 수면 unknown (계산값·작은 수). 최종 답: Ingress 게이트웨이 항목이 택한 값,
                  Routing은 전부 그대로 전달(forwarded). 과제 정답 여부를 함께 적는다.
    sessions      경계 요청의 응답자 세션별 LLM 지연 합(순차였다면)과 최댓값(병렬이면 벽시계 하한)
구조화 응답(items)이 있는 실행에만 disagreement를 잰다.
"""
import re
from collections import defaultdict

_WS = re.compile(r"[\s,]+")


def _n(x: str) -> str:
    return _WS.sub(" ", (x or "").lower()).strip()


def _v(x: str) -> str:
    return _WS.sub("", (x or "").lower())


def _truth(g: dict, fragments: dict, db_versions: dict) -> set[str]:
    """과제의 결정 필수 조각 원문에 든 값 토큰 + need가 참조한 DB 버전의 값."""
    out = set()
    for n in g["needs"]:
        for fid in n.get("critical_components") or []:
            f = fragments.get(fid)
            if f:
                out |= {_v(t) for t in re.findall(r"[\w.-]+", f.get("text", ""))}
        for s in n["sources"]:
            if s["type"] == "db" and (k := (s["key"], s.get("v"))) in db_versions:
                val = db_versions[k]
                vals = val.values() if isinstance(val, dict) else [val]
                out |= {_v(str(x)) for x in vals}
    return out


def fanout(events: list[dict], lookups: list[dict], llm: list[dict], gold: dict | None = None,
           fragments: dict | None = None, db_versions: dict | None = None, correct: dict | None = None) -> dict:
    """events: WAL 사건, lookups: obs/db_lookups, llm: obs/llm. gold: wid → 정답 원장 행,
    db_versions: (key, v) → value, correct: wid → 과제 완전 정답 여부."""
    decisions = {e["payload"]["rid"]: e["payload"] for e in events
                 if e["type"] == "boundary_decision" and e["payload"].get("stage") == "ingress"}
    parent: dict[str, str] = {}                                          # 내부 질의 rid → 경계 요청 rid
    replies: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for e in events:
        p = e["payload"]
        if e["type"] != "message" or not str(p.get("from_agent", "")).startswith("boundary:"):
            continue
        if p["kind"] == "request" and p.get("serving") in decisions:
            parent[p["rid"]] = p["serving"]
        elif p["kind"] == "response" and p["rid"] in parent:
            replies[parent[p["rid"]]].append((p["to_agent"], p["response"]))

    seen: dict[str, set] = defaultdict(set)
    dup = total = 0
    dup_by_req: dict[str, int] = defaultdict(int)
    for x in lookups:
        if x.get("tool") != "db.query" or x.get("serving") not in parent:
            continue
        total += 1
        req, key = parent[x["serving"]], (tuple(x.get("keys") or [x.get("entity_input")]), x.get("record_type"), x["day"])
        if key in seen[req]:
            dup += 1
            dup_by_req[req] += 1
        seen[req].add(key)

    lat: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for x in llm:
        if x.get("component") == "responder" and x.get("serving") in parent:
            lat[parent[x["serving"]]][x["serving"]] += x.get("latency_ms", 0) / 1000

    rows, cases = [], []
    for rid, d in decisions.items():
        sel = d.get("selected") or []
        sess = lat.get(rid, {})
        rows.append({"rid": rid, "task_id": d.get("task_id"), "group": d["group"], "deliver": d.get("deliver"),
                     "selected": len(sel), "requery": len(d.get("requery") or []), "duplicate_queries": dup_by_req[rid],
                     "session_seconds_sum": round(sum(sess.values()), 1), "session_seconds_max": round(max(sess.values(), default=0), 1)})
        rs = [(a, r) for a, r in replies.get(rid, []) if "items" in r]
        if len(rs) < 2:
            continue
        vals: dict[tuple, dict[str, str]] = defaultdict(dict)
        for a, r in rs:
            for it in r["items"]:
                vals[(_n(it["entity"]), _n(it["attribute"]))].setdefault(_v(it["value"]), a)
        final = {(_n(it["entity"]), _n(it["attribute"])): _v(it["value"]) for it in d.get("items") or []}
        final_vals = {_v(it["value"]) for it in d.get("items") or []}
        wid = d.get("task_id")
        truth = _truth(gold[wid], fragments or {}, db_versions or {}) if gold and wid in gold else set()
        for key, by_val in vals.items():
            if len(by_val) < 2:
                continue
            # 짧은 수(3자리 이하)는 기록 어디에나 흔해 정오를 가를 수 없다 → unknown
            judged = {v: ("unknown" if re.fullmatch(r"\d{1,3}", v) else "correct" if v in truth else "other") for v in by_val}
            if not any(j == "correct" for j in judged.values()):
                judged = {v: "unknown" for v in by_val}
            took = final.get(key) if key in final else next((v for v in by_val if v in final_vals), None)
            cases.append({"rid": rid, "task_id": wid, "entity": key[0], "attribute": key[1],
                          "values": {v: {"agent": a, "judged": judged[v]} for v, a in by_val.items()},
                          "final": ("forwarded" if d.get("deliver") == "forward" else
                                    ({"value": took, "judged": judged.get(took, "not_a_member_value")} if took else "none")),
                          "task_correct": (correct or {}).get(wid)})
    multi = [r for r in rows if r["selected"] >= 2]
    with_items = sum(1 for rid in decisions if sum("items" in r for _, r in replies.get(rid, [])) >= 2)
    return {"requests": len(rows),
            "selected_mean": round(sum(r["selected"] for r in rows) / len(rows), 2) if rows else None,
            "selected_hist": dict(sorted(defaultdict(int, {k: sum(1 for r in rows if r["selected"] == k)
                                                           for k in {r["selected"] for r in rows}}).items())),
            "db_queries": total, "duplicate_queries": dup, "duplicate_rate": round(dup / total, 3) if total else None,
            "multi_member_requests": len(multi), "requests_with_2plus_item_replies": with_items,
            "disagreement_requests": len({c["rid"] for c in cases}),
            "disagreement_rate": round(len({c["rid"] for c in cases}) / with_items, 3) if with_items else None,
            "session_seconds": {"sum": round(sum(r["session_seconds_sum"] for r in rows), 1),
                                "max_per_request": round(sum(r["session_seconds_max"] for r in rows), 1)},
            "rows": rows, "disagreements": cases}
