"""need 단위 전달률 (채점기, 오프라인): 결정 필수 조각이 최신 버전으로 요청자 쪽에 도착했는가.

정답률과 달리 추론 난이도와 무관하게 조건 차이를 보는 지표다.

    도착      과제 수행 중 요청자가 받은 것: 자기 질의에 온 응답(에이전트·경계 모듈), 자기 도구 호출 결과
              (full_load의 기억 검색 결과는 에피소드 하나가 한 메시지). 과제 시작 전부터 요청자 이력에 있던 것은 prior로 따로 센다.
    판정      카나리 조각: 원문의 카나리 형태 값(쉼표를 뺀 4자리 이상 정수, 1000의 배수 제외)이 모두 도착했으면 delivered.
              버전(같은 키·같은 카나리, 예: 가승인 상태)이 있으면 카나리가 든 메시지에 버전을 가르는 값(상태 등)도
              있어야 delivered, 옛 버전 값만 있으면 stale. 같은 키라도 카나리가 다르면 다른 항목(예치 건 여럿)이다.
              카나리가 없는 조각: 서명 매칭. 조각의 엔티티(DB 키의 엔티티 id 또는 catalog·실행 중 catalog·조각 target의
              이름·별칭) 하나 이상과 핵심 값이 요청자가 받은 **같은 메시지** 안에 함께 나타나면 delivered. 핵심 값은 같은
              키의 옛 버전과 다른 필드의 값만(옛 버전이 없거나 모두 같으면 값 필드 전부). 옛 버전 값만 왔으면 stale.
              둘 다 할 수 없는 조각(값 필드 없음)은 unjudged. 판정 방식(canary | signature)을 조각마다 기록한다.
    메시지    구조화 응답은 같은 엔티티의 항목을 합친 것이 한 메시지, 답 문장(answer)이 또 한 메시지. 도구 결과 하나가
              한 메시지 (full_load 기억 검색은 에피소드 하나). "함께 나타남"의 기준은 Matcher: 항목은 엔티티가 맞는
              항목의 값 필드, 문장은 같은 문장의 엔티티 언급 뒤(20 토큰). 수치는 숫자가 든 이름을 지우고 찾는다. 다른 지역 표시는 제외.
    need      결정 필수 조각이 모두 delivered면 need 전달. 계산형 need(집행 가능액·가용 좌석·가용 재고·배분 인원)는
              정답 중간값(벤치마크가 넘김)이 엔티티와 같은 응답 메시지에 도착해도 전달 (computed). 도구 결과는 보지 않는다.
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


def signature(f: dict, names: dict[str, list[str]], keys: list[str] | None = None) -> tuple[list[str], list] | None:
    """(엔티티 표면형들, 핵심 값들). 값 필드가 dict가 아니면 스칼라 하나가 핵심 값. keys가 있으면 그 필드만."""
    key = f.get("key") or ""
    parts = key.split("/")
    ent = parts[2] if len(parts) > 2 else None
    if ent is None or f.get("value") is None:
        return None
    ents = [ent, *names.get(ent, [])]
    val = f["value"]
    core = ([v for k, v in val.items() if (keys is None or k in keys) and not (isinstance(v, str) and v == ent)]
            if isinstance(val, dict) else [val])
    return ents, core


def _changed_keys(f: dict, older: list[dict]) -> list[str] | None:
    """같은 키의 옛 버전과 값이 다른 필드. 옛 버전이 없거나 다른 필드가 없으면 None (값 필드 전부)."""
    cur = f.get("value")
    if not isinstance(cur, dict):
        return None
    olds = [o["value"] for o in older if isinstance(o.get("value"), dict)]
    keys = [k for k in cur if any(o.get(k) != cur[k] for o in olds)]
    return keys or None


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


class Msg:
    """요청자가 받은 메시지 하나. 구조화 응답의 같은 엔티티 항목 묶음이면 items(정규화된 entity·value·status),
    답 문장·도구 결과·항목 도입 전 기록이면 text만."""
    def __init__(self, raw: str, items: list[dict] | None = None, reply: bool = False):
        self.raw, self.norm, self.reply = raw, _norm(raw), reply             # reply: 응답(항목·답 문장), 아니면 도구 결과
        self.items = None if items is None else [
            {"entity": _norm(x.get("entity", "")), "value": _norm(str(x.get("value", ""))),
             "status": _norm(str(x.get("status", x.get("status_or_as_of", ""))))} for x in items]


def _received(events: list[dict], task: str, requester: str) -> list[Msg]:
    """과제 중 요청자가 받은 메시지들: 구조화 응답은 같은 엔티티의 항목 묶음 하나와 답 문장 하나가 각각 한 메시지,
    도구 결과 하나가 한 메시지 (full_load 기억 검색은 에피소드 하나)."""
    parts = []
    for e in events:
        p = e["payload"]
        if p.get("task_id") != task:
            continue
        if e["type"] == "message" and p.get("kind") == "response" and p.get("from_agent") == requester:
            r = p["response"]
            if "items" in r:
                by_ent: dict[str, list] = {}
                for x in r["items"]:
                    by_ent.setdefault(_norm(x.get("entity", "")), []).append(x)
                parts += [Msg(json.dumps(xs, ensure_ascii=False), xs, reply=True) for xs in by_ent.values()]
                if r.get("answer"):
                    parts.append(Msg(r["answer"], reply=True))
            else:                                                          # 항목 도입 전 기록
                parts.append(Msg(json.dumps(r, ensure_ascii=False), reply=True))
        elif e["type"] == "tool_result" and p.get("agent") == requester and p.get("serving") is None:
            res = p.get("result")
            if p.get("tool") == "search_memory" and isinstance(res, dict) and isinstance(res.get("records"), str):
                parts += [Msg(x) for x in re.split(r"\n(?=\[E\d+\] )", res["records"])]
            else:
                parts.append(Msg(json.dumps(res, ensure_ascii=False)))
    return parts


_IDTOK = re.compile(r"[a-z]{1,6}(?:-[a-z0-9]{1,8})*-\d{2,}|[a-z]{1,4}-[a-z]{2,4}-[a-z]{2,4}")   # CMT-00055, E-SEL-2004, INV-TYO-WSS


class Matcher:
    """엔티티와 값이 한 메시지에 '함께' 있는가.
    항목 묶음: 엔티티가 맞는 항목들의 value 필드(문자열 값은 status 필드도)에 값이 있어야 한다 (attribute·ref·기준일은 보지 않는다).
    문장: 같은 문장 안, 엔티티 언급 뒤 20 토큰 안에 값이 있어야 한다 (수치는 그 안에서 다음 id 앞까지).
    수치는 숫자가 든 이름(부서 'Dev Team 2', id 'E-SEL-2004')을 지운 뒤 찾는다 (이름 속 숫자와 값을 섞지 않는다).
    region이 있으면 다른 지역 코드가 적힌 항목·문장 구간은 보지 않는다 (지역마다 같은 이름인 소프트웨어·품목)."""
    AFTER = 20

    def __init__(self, names: dict[str, list[str]], extra: list[str] = (), regions: set[str] = frozenset()):
        self.regions = {r.lower() for r in regions}
        ph = {_norm(x) for k, vs in names.items() for x in (k, *vs)} | {_norm(x) for x in extra}
        ph = sorted((x for x in ph if re.search(r"\d", x) and len(x) > 2), key=len, reverse=True)
        self.names = names
        self.rx = re.compile("|".join(rf"(?<![\w-]){re.escape(x)}(?![\w-])" for x in ph)) if ph else None

    def strip(self, t: str) -> str:
        return self.rx.sub(" _ ", t) if self.rx else t

    def has(self, t: str, v) -> bool:
        return _has_value(self.strip(t) if isinstance(v, (int, float)) and not isinstance(v, bool) else t, v)

    def surfaces(self, ents) -> list[str]:
        return [x for x in dict.fromkeys(_norm(e) for x in ents for e in (x, *self.names.get(x, []))) if x]

    def _other_region(self, t: str, region: str | None) -> bool:
        return bool(region) and bool((self.regions - {region.lower()}) & set(t.split()))

    def hit(self, ents, vals, m: Msg, region: str | None = None) -> bool:
        es = self.surfaces(ents)
        if m.items is not None:
            its = [it for it in m.items if any(e in it["entity"] for e in es)
                   and not self._other_region(" ".join(it.values()), region)]
            return bool(its) and all(any(self.has(it["value"] if isinstance(v, (int, float)) else
                                                  it["value"] + " " + it["status"], v) for it in its) for v in vals)
        for sent in re.split(r"(?<!\d)[.;\n]|[.;](?!\d)", m.raw):            # 문장 단위 (소수점·금액은 자르지 않음)
            if self._text_hit(es, vals, _norm(sent).split(), region):
                return True
        return False

    def _text_hit(self, es, vals, toks, region) -> bool:
        for e in es:
            et = e.split()
            for i in range(len(toks) - len(et) + 1):
                if toks[i:i + len(et)] == et:
                    win = " ".join(toks[i + len(et):i + len(et) + self.AFTER])
                    cut = next((k for k, t in enumerate(win.split()) if _IDTOK.fullmatch(t)), None)
                    num = self.strip(" ".join(win.split()[:cut]))          # 수치는 다음 id 앞까지만 (다른 항목의 값)
                    if not self._other_region(win, region) and all(
                            _has_value(num, v) if isinstance(v, (int, float)) and not isinstance(v, bool) else _has_value(win, v)
                            for v in vals):
                        return True
        return False


def _computed_hit(entries, mt: Matcher, msgs: list[Msg], region: str | None) -> bool:
    """계산형 need: 항목마다(엔티티들, 허용 값들) 엔티티와 값 하나가 한 응답 메시지에 함께 있으면 도착. 계산값은
    기록 원문에 없으므로 도구 결과(자기 영역 조회, full_load 기억 검색)는 보지 않는다."""
    return all(any(mt.hit(ents, [v], m, region) for v in vals for m in msgs if m.reply) for ents, vals in entries)


def need_delivery(events: list[dict], gold: dict[str, dict], fragments: dict[str, dict],
                  prior: dict[str, str] | None = None, names: dict[str, list[str]] | None = None,
                  computed: dict | None = None) -> dict:
    """events: WAL 사건, gold: wid → 정답 원장 행, fragments: fid → 조각, names: 엔티티 id → 이름·별칭(catalog).
    prior: wid → 과제 시작 시 요청자 이력 텍스트. computed: wid → sem → [(엔티티들, 허용 값들)] (계산형 need 중간값)."""
    names = names or {}
    computed = computed or {}
    ids = [p_[2] for f in fragments.values() if len(p_ := (f.get("key") or "").split("/")) > 2]
    mt = Matcher(names, ids, {(f.get("group") or "-").split("-", 1)[-1] for f in fragments.values() if f.get("group")})
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
        got_c = canaries("\n".join(m.raw for m in msgs))
        prior_t = (prior or {}).get(wid, "")
        prior_m = Msg(prior_t)
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
                    carrying = [m.norm for m in msgs if c <= canaries(m.raw)]
                    if not diff:
                        state = ("delivered" if c <= got_c else "prior" if c <= canaries(prior_t) else "missing")
                    elif any(all(mt.has(m, v) for v in diff[0]) for m in carrying):
                        state = "delivered"
                    elif any(all(mt.has(m, v) for v in old) for old in diff[1] for m in carrying):
                        state = "stale"
                    else:
                        state = "prior" if c <= canaries(prior_t) else "missing"
                    frags.append({**base, "method": "canary", "state": state})
                    continue
                keys = _changed_keys(f, older)                            # 옛 버전과 다른 값만 요구
                sig = signature(f, names, keys)
                if sig is None:
                    frags.append({**base, "method": "none", "state": "unjudged"})
                    continue
                olds = [s_ for s_ in (signature(o, names, keys) for o in older) if s_ and s_[1] != sig[1]]
                reg = (f.get("group") or "-").split("-", 1)[-1]
                hit = any(mt.hit(*sig, m, reg) for m in msgs)
                state = ("delivered" if hit else "stale" if any(mt.hit(*o, m, reg) for o in olds for m in msgs) else
                         "prior" if mt.hit(*sig, prior_m, reg) else "missing")
                frags.append({**base, "method": "signature", "state": state})
            judged = [x for x in frags if x["method"] != "none"]
            comp = computed.get(wid, {}).get(n["sem"])
            hit = bool(comp) and _computed_hit(comp, mt, msgs, (n.get("group") or "-").split("-", 1)[-1])
            rows.append({"task_id": wid, "need": n["sem"], "class": g.get("state_class"), "c_ops": g.get("c_ops"),
                         "domain": n["sem"].split("/")[0].split("-")[0], "frags": frags, "scored": bool(judged),
                         "computed": None if not comp else hit,
                         "delivered": bool(judged) and (hit or all(x["state"] == "delivered" for x in judged))})
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
