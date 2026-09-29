"""need 단위 전달률 (채점기, 오프라인): 결정 필수 조각이 최신 버전으로 요청자 쪽에 도착했는가.

정답률과 달리 추론 난이도와 무관하게 조건 차이를 보는 지표다.

    도착      과제 수행 중 요청자가 받은 것: 자기 질의에 온 응답(에이전트·경계 모듈), 자기 도구 호출 결과
              (full_load의 그룹 이력 포함). 과제 시작 전부터 요청자 이력에 있던 것은 prior로 따로 센다.
    판정      카나리 조각: 원문의 카나리 형태 값(쉼표를 뺀 4자리 이상 정수, 1000의 배수 제외)이 모두 도착했으면 delivered.
              버전(같은 키·같은 카나리, 예: 가승인 상태)이 있으면 카나리가 든 메시지에 버전을 가르는 값(상태 등)도
              있어야 delivered, 옛 버전 값만 있으면 stale. 같은 키라도 카나리가 다르면 다른 항목(예치 건 여럿)이다.
              카나리가 없는 조각: 서명 매칭. 조각의 엔티티(DB 키의 엔티티 id 또는 catalog 이름·별칭) 하나 이상과
              핵심 값(값 필드의 일차·등급·수량·공급사 id·상태 등)이 요청자가 받은 **같은 메시지** 안에 함께 나타나면
              delivered. 같은 키의 옛 버전만 왔으면 stale. 둘 다 할 수 없는 조각(값 필드 없음)은 unjudged.
              판정 방식(canary | signature)을 조각마다 기록한다.
    need      결정 필수 조각이 모두 delivered면 need 전달.
"""
import json
import re
from collections import defaultdict

_NUM = re.compile(r"(?<![\w.-])\d{1,3}(?:,\d{3})+(?![\d,])|(?<![\w.,-])\d{4,}(?![\w-])")


def canaries(text: str) -> set[str]:
    out = set()
    for m in _NUM.findall(text or ""):
        v = m.replace(",", "")
        if len(v) >= 4 and int(v) % 1000:
            out.add(v)
    return out


_STATUS = {"reviewing": ("reviewing", "under review", "in review"), "pending": ("pending", "provisionally approved"),
           "settled": ("settled",), "cancelled": ("cancelled", "canceled"), "active": ("active",), "exited": ("exited", "left")}


def _norm(t: str) -> str:
    return " ".join(re.sub(r"[^\w\s-]", " ", (t or "").lower().replace(",", "")).split())


def _has_value(msg: str, v) -> bool:
    if isinstance(v, bool) or v is None:
        return True                                                    # 참·거짓·없음은 서명에 넣지 않는다
    if isinstance(v, (int, float)):
        return re.search(rf"(?<![\w.-]){int(v)}(?![\w-])", msg) is not None
    if isinstance(v, str):
        return any(_norm(x) in msg for x in _STATUS.get(v, (v,)))
    return True


def signature(f: dict, names: dict[str, list[str]]) -> tuple[list[str], list] | None:
    """(엔티티 표면형들, 핵심 값들). 값 필드가 dict가 아니면 스칼라 하나가 핵심 값."""
    key = f.get("key") or ""
    parts = key.split("/")
    ent = parts[2] if len(parts) > 2 else None
    if ent is None or f.get("value") is None:
        return None
    ents = [ent, *names.get(ent, [])]
    val = f["value"]
    core = [v for k, v in val.items() if not (isinstance(v, str) and v == ent)] if isinstance(val, dict) else [val]
    return ents, core


def _sig_hit(sig, msg: str) -> bool:
    ents, core = sig
    return any(_norm(e) in msg for e in ents) and all(_has_value(msg, v) for v in core)


def _distinguishing(f: dict, versions: list[dict]) -> tuple[list, list[list]] | None:
    """현재 조각과 옛 버전을 가르는 값들: (현재 값들, [옛 버전마다 값들]). 버전이 없거나 값 필드가 없으면 None."""
    cur = f.get("value")
    if not versions or not isinstance(cur, dict):
        return None
    olds = [o["value"] for o in versions if isinstance(o.get("value"), dict)]
    keys = [k for k in cur if any(o.get(k) != cur[k] for o in olds)]
    if not keys:
        return None
    return [cur[k] for k in keys], [[o.get(k) for k in keys] for o in olds]


def _received(events: list[dict], task: str, requester: str) -> list[str]:
    """과제 중 요청자가 받은 메시지들(응답 하나, 도구 결과 하나가 각각 한 메시지)."""
    parts = []
    for e in events:
        p = e["payload"]
        if p.get("task_id") != task:
            continue
        if e["type"] == "message" and p.get("kind") == "response" and p.get("from_agent") == requester:
            r = p["response"]
            if "items" in r:                                              # 구조화 응답: 항목 하나가 한 메시지
                parts += [json.dumps(x, ensure_ascii=False) for x in r["items"]]
            else:                                                          # 항목 도입 전 기록
                parts.append(json.dumps(r, ensure_ascii=False))
        elif e["type"] == "tool_result" and p.get("agent") == requester and p.get("serving") is None:
            parts.append(json.dumps(p.get("result"), ensure_ascii=False))
    return parts


def need_delivery(events: list[dict], gold: dict[str, dict], fragments: dict[str, dict],
                  prior: dict[str, str] | None = None, names: dict[str, list[str]] | None = None) -> dict:
    """events: WAL 사건, gold: wid → 정답 원장 행, fragments: fid → 조각, names: 엔티티 id → 이름·별칭(catalog).
    prior: wid → 과제 시작 시 요청자 이력 텍스트."""
    names = names or {}
    requester = {e["payload"]["task_id"]: e["payload"]["agent"] for e in events if e["type"] == "task_delivered"}
    by_key = defaultdict(list)
    for f in fragments.values():
        if f.get("key"):
            by_key[f["key"]].append(f)
    rows = []
    for wid, g in gold.items():
        if wid not in requester:
            continue
        msgs = _received(events, wid, requester[wid])
        got_c = canaries("\n".join(msgs))
        nmsgs = [_norm(m) for m in msgs]
        prior_t = (prior or {}).get(wid, "")
        for n in g["needs"]:
            if n.get("local"):
                continue
            frags = []
            for fid in n.get("critical_components") or []:
                f = fragments.get(fid)
                if f is None:
                    continue
                older = [o for o in by_key.get(f.get("key"), []) if o["fid"] != fid and o.get("seq", 0) < f.get("seq", 0)]
                c = canaries(f.get("text", ""))
                base = {"fid": fid, "disc": f.get("disc"), "domain": (f.get("group") or "").split("-")[0]}
                if c:
                    # 버전 = 같은 키, 같은 카나리 (예: 가승인 상태 reviewing → pending → settled). 카나리가 다르면
                    # 같은 키의 다른 항목(예: 부서의 여러 예치 건)이라 옛 버전이 아니다.
                    versions = [o for o in older if canaries(o.get("text", "")) == c]
                    diff = _distinguishing(f, versions)
                    carrying = [m for m, raw in zip(nmsgs, msgs) if c <= canaries(raw)]
                    if not diff:
                        state = ("delivered" if c <= got_c else "prior" if c <= canaries(prior_t) else "missing")
                    elif any(all(_has_value(m, v) for v in diff[0]) for m in carrying):
                        state = "delivered"
                    elif any(all(_has_value(m, v) for v in old) for old in diff[1] for m in carrying):
                        state = "stale"
                    else:
                        state = "prior" if c <= canaries(prior_t) else "missing"
                    frags.append({**base, "method": "canary", "state": state})
                    continue
                sig = signature(f, names)
                if sig is None:
                    frags.append({**base, "method": "none", "state": "unjudged"})
                    continue
                olds = [s_ for s_ in (signature(o, names) for o in older) if s_ and s_[1] != sig[1]]
                hit = any(_sig_hit(sig, m) for m in nmsgs)
                state = ("delivered" if hit else "stale" if any(_sig_hit(o, m) for o in olds for m in nmsgs) else
                         "prior" if _sig_hit(sig, _norm(prior_t)) else "missing")
                frags.append({**base, "method": "signature", "state": state})
            judged = [x for x in frags if x["method"] != "none"]
            rows.append({"task_id": wid, "need": n["sem"], "class": g.get("state_class"), "c_ops": g.get("c_ops"),
                         "domain": n["sem"].split("/")[0].split("-")[0], "frags": frags, "scored": bool(judged),
                         "delivered": bool(judged) and all(x["state"] == "delivered" for x in judged)})
    return {"needs": rows, "summary": summarize(rows)}


def summarize(rows: list[dict]) -> dict:
    """전달률과 판정 방식별 커버리지를 전체·등급·C_ops·도메인별로."""
    out = {}
    groups = {"all": rows}
    for r in rows:
        groups.setdefault(f"class_{r['class']}", []).append(r)
        groups.setdefault("C_ops" if r["c_ops"] else "non_C_ops", []).append(r)
        groups.setdefault(f"domain_{r['domain']}", []).append(r)
    for k, rs in groups.items():
        scored = [r for r in rs if r["scored"]]
        frags = [x for r in rs for x in r["frags"]]
        by_method = defaultdict(lambda: defaultdict(int))
        for x in frags:
            by_method[x["method"]][x["state"]] += 1
        judged = [x for x in frags if x["method"] != "none"]
        out[k] = {"needs": len(rs), "needs_scored": len(scored),
                  "need_delivery": round(sum(r["delivered"] for r in scored) / len(scored), 4) if scored else None,
                  "fragments": len(frags),
                  "coverage": {m: round(sum(v.values()) / len(frags), 4) for m, v in by_method.items()} if frags else {},
                  "fragment_delivery": round(sum(x["state"] == "delivered" for x in judged) / len(judged), 4) if judged else None,
                  "delivery_by_method": {m: round(v["delivered"] / sum(v.values()), 4) for m, v in by_method.items() if m != "none"},
                  "states": {m: dict(v) for m, v in by_method.items()}}
    return out
