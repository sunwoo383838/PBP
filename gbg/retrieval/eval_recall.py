"""오프라인 회수율 평가 (LLM 없음). worldgen private 원장(gold.jsonl, fragments.jsonl, transcripts_full/)을 읽는 오프라인
도구다.

원격 need의 결정 필수 성분 중 이력에만 있는 조각(frag 출처)에 대해 잰다.
    index      정확 조회(색인 + catalog 한 단계, 라우터와 공통)가 조각에 닿는가: 조각 원문이 일지 결과에 있거나(H0),
               조각 보유자가 처리자 목록에 있다(H1). H0·H1 90% 기준은 이 수치에 적용한다.
    evidence   게이트웨이 증거 블록(상한 안)에 조각이 들어가는가. 조각이 든다 = 조각의 이력 줄(H2는 대상 줄과 값 줄 둘)이
               모두 증거에 있다. recall@k는 재정렬 순위 상위 k개 후보 안에 드는가
    holder     증거 블록에 조각 보유자(활동 중인 보유자)가 쓴 항목이 있는가 (Routing 담당자 선택의 입력)
발견성(H0/H1/H2)별, need 등급(A–D)별로 보고한다. 질의당 증거 토큰과 검색 시간도 모은다.

- 질의: 과제 원문([Request scope] 앞) + need의 속성 키워드 + 엔티티 표면형. 엔티티는 semantic key(그룹/…/…)에서
  알려진 엔티티(catalog·DB에 있는 ID나 부서)인 칸, 나머지 칸이 속성이다.
- need 하나가 질의 하나다. 같은 need의 조각은 같은 증거로 판정한다.
"""
import statistics
from collections import defaultdict
from dataclasses import dataclass

from .evidence import build_evidence
from .hybrid import GroupRetriever
from .lookup import index_lookup
from .normalize import normalize

KS = (5, 10, 20, 50)


@dataclass(frozen=True)
class Frag:
    fid: str
    disc: str
    text: str
    lines: tuple[str, ...]                      # 보유자 이력의 조각 줄 (H2는 대상 줄·값 줄)
    holders: tuple[str, ...]
    active_holders: tuple[str, ...]


@dataclass(frozen=True)
class Case:
    task_id: str
    need: str
    group: str
    day: int
    round: int
    cls: str                                    # need 등급 A–D
    query: str
    entities: tuple[str, ...]
    attr: str
    frags: tuple[Frag, ...]


def _critical(need: dict) -> set[str] | None:
    crit = need.get("critical_components")
    if crit is None:
        return None
    return {c if isinstance(c, str) else c.get("fid") for c in crit}


def parse_sem(sem: str, names: dict[str, list[str]]) -> tuple[tuple[str, ...], str]:
    """semantic key → (엔티티들, 속성). names에 있는 칸이 모두 엔티티다 (예: PROC-SEL/quotes/laptop → laptop)."""
    parts = sem.split("/")[1:]
    ents = tuple(dict.fromkeys(p for p in parts if p in names))
    attr = " ".join(p for p in parts if p not in ents)
    return ents, attr


def build_cases(gold: list[dict], fragments: dict[str, dict], names: dict[str, list[str]] | None = None,
                lines_of=lambda f: ()) -> tuple[list[Case], dict[str, int]]:
    """names: 알려진 엔티티 → 표면형(이름·별칭). 없으면 semantic key의 두 번째 칸을 엔티티로 본다.
    lines_of(fragment) → 보유자 이력의 조각 줄 원문."""
    cases, skipped = [], defaultdict(int)
    for g in gold:
        surface = g.get("surface", "").split("\n[Request scope]", 1)[0]
        for n in g["needs"]:
            if n.get("local"):
                continue
            if names is None:
                parts = n["sem"].split("/")
                ents, attr = ((parts[1],) if len(parts) > 2 else ()), parts[-1]
            else:
                ents, attr = parse_sem(n["sem"], names)
            words = " ".join(dict.fromkeys(x for e in ents for x in [*(names or {}).get(e, []), e]))
            crit = _critical(n)
            frags = []
            for s in n["sources"]:
                if s["type"] != "frag":
                    continue
                fid = s["frag"]["fid"]
                if crit is not None and fid not in crit:
                    skipped["not_critical"] += 1
                    continue
                f = fragments.get(fid)
                if f is None or not f.get("text"):
                    skipped["no_fragment_text"] += 1
                    continue
                hs = s["frag"].get("holders", [])
                frags.append(Frag(fid, s["frag"].get("disc") or f.get("disc", "?"), f["text"], tuple(lines_of(f)),
                                  tuple(sorted({h["agent"] for h in hs} | {f["agent"]})),
                                  tuple(sorted(h["agent"] for h in hs if h.get("active")))))
            if frags:
                cases.append(Case(g["wid"], n["sem"], n["group"], g["day"], g.get("round", 0), n.get("class") or "?",
                                  f"{surface} {attr.replace('_', ' ')} {words}".strip(), ents, attr, tuple(frags)))
    cases.sort(key=lambda c: (c.day, c.round, c.task_id, c.need))
    return cases, dict(skipped)


def contains(text_norm: str, f: Frag) -> bool:
    """정규화한 증거 원문에 조각이 드는가: 조각 원문 전체, 또는 조각 줄(H2는 대상 줄과 값 줄) 전부."""
    if normalize(f.text) in text_norm:
        return True
    return bool(f.lines) and all(normalize(x) in text_norm for x in f.lines)


def index_hit(retriever: GroupRetriever, case: Case, f: Frag) -> bool:
    lk = index_lookup(retriever.stores, case.group, list(case.entities), retriever.p.catalog_link_fields)
    want = normalize(f.text)
    return any(want in normalize(x.text) for x in lk.journal) or bool(set(f.holders) & set(lk.holders))


async def run_new(retriever: GroupRetriever, case: Case) -> dict:
    ev = await build_evidence(retriever, case.query, list(case.entities))
    ranked = [normalize(t) for t in ev.ranked]
    return {"items": ev.items, "ranked": ranked, "tokens": ev.tokens, "seconds": ev.seconds.get("total"),
            "rerank_seconds": ev.seconds.get("rerank"), "n_candidates": len(ev.log["candidates"]),
            "cap_reached": ev.cap_reached}


async def evaluate(retrievers: dict[str, GroupRetriever], cases: list[Case], systems: dict, advance=None) -> dict:
    """systems: 이름 → async fn(retriever, case) → {"items", "ranked"(없으면 None), "tokens", "seconds", …}.
    advance(case)가 있으면 사례마다 그 과제 도착 직전까지의 세계를 반영한 뒤 평가한다 (사례는 시간순)."""
    rows = {name: [] for name in ("index", *systems)}
    queries = {name: [] for name in systems}
    for c in cases:
        if advance:
            advance(c)
        r = retrievers[c.group]
        for f in c.frags:
            rows["index"].append({"task_id": c.task_id, "need": c.need, "cls": c.cls, "disc": f.disc, "fid": f.fid,
                                  "day": c.day, "hit": index_hit(r, c, f)})
        for name, fn in systems.items():
            out = await fn(r, c)
            ev_norm = "\n".join(normalize(it.text) for it in out["items"])
            by_agent = defaultdict(list)
            for it in out["items"]:
                by_agent[it.agent].append(it)
            queries[name].append({k: out.get(k) for k in ("tokens", "seconds", "rerank_seconds", "n_candidates",
                                                          "cap_reached")})
            for f in c.frags:
                row = {"task_id": c.task_id, "need": c.need, "cls": c.cls, "disc": f.disc, "fid": f.fid, "day": c.day,
                       "hit": contains(ev_norm, f), "holder": bool(set(f.holders) & set(by_agent)),
                       "active_holder": bool(set(f.active_holders) & set(by_agent))}
                if out.get("ranked") is not None:
                    first = next((i for i, t in enumerate(out["ranked"], 1) if t is not None and contains(t, f)), None)
                    row["rank"] = first
                    row.update({f"at{k}": first is not None and first <= k for k in KS})
                rows[name].append(row)
    return {"cases": len(cases), "frags": len(rows["index"]),
            "systems": {name: summarize(rows[name], queries.get(name)) for name in rows}}


def _rate(rows: list[dict], key: str = "hit") -> dict:
    n = len(rows)
    k = sum(bool(r.get(key)) for r in rows)
    return {"n": n, "hit": k, "recall": round(k / n, 4) if n else None}


def _dist(xs: list[float]) -> dict | None:
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return {"mean": round(statistics.fmean(xs), 3), "p50": xs[len(xs) // 2], "p95": xs[min(len(xs) - 1, int(len(xs) * 0.95))],
            "max": xs[-1]}


def summarize(rows: list[dict], queries: list[dict] | None) -> dict:
    by = lambda key, metric="hit": {k: _rate([r for r in rows if r[key] == k], metric)
                                    for k in sorted({r[key] for r in rows})}
    out = {"recall": _rate(rows), "by_disc": by("disc"), "by_class": by("cls"), "rows": rows}
    if rows and "holder" in rows[0]:
        out["holder"] = {"any": _rate(rows, "holder"), "active": _rate(rows, "active_holder"),
                         "active_by_class": by("cls", "active_holder")}
    if rows and "rank" in rows[0]:
        out["at_k"] = {k: {"all": _rate(rows, f"at{k}")["recall"],
                           **{d: _rate([r for r in rows if r["disc"] == d], f"at{k}")["recall"]
                              for d in sorted({r["disc"] for r in rows})}} for k in KS}
    if queries:
        out["queries"] = {"n": len(queries), "tokens": _dist([q["tokens"] for q in queries]),
                          "seconds": _dist([q["seconds"] for q in queries]),
                          "rerank_seconds": _dist([q.get("rerank_seconds") for q in queries]),
                          "candidates": _dist([q.get("n_candidates") for q in queries]),
                          "cap_reached": sum(bool(q.get("cap_reached")) for q in queries)}
    return out
