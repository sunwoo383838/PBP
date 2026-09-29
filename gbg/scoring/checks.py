"""실행 검사 (채점기, 오프라인). 하나라도 실패하면 그 실행의 지표를 쓰지 않는다.

    leak          LLM 입력(캐시된 요청)에 정답 전용 식별자가 0건: 조각 id(FR-, 모든 입력), 내부 DB 키("<그룹>/<종류>/…",
                  에이전트 입력만. Ingress 게이트웨이는 버전 표시로 DB 키를 본다)
    card_leak     Direct 조건 입력에 실제 에이전트 id(그룹이 붙은 이름, 예: fin-sel.a3)가 0건 (불투명 id만)
    access        접근 감사(obs/access.jsonl)의 거부 0건
    budget        예산 상한이 있는 조건에서 과제당 호출·토큰이 상한 이하 (최종 호출 예약분 포함)
    determinism   WAL 해시 기록 (같은 설정 재실행과 대조는 호출자가)
이탈 에이전트에게 간 요청은 검사 실패가 아니라 L_route로 집계한다.
"""
import hashlib
import json
import re
from pathlib import Path

FRAG_ID = re.compile(r"\bFR-\d{5}\b")
PHYSICAL_KEY = re.compile(r"\b[A-Z]{2,5}-[A-Z]{3}/(?:emp|line|commit|inv|asset|lic|vendor|quote|seatprice|receipt|contract)/")
AGENT_ID = re.compile(r"\b[a-z]{2,5}-[a-z]{3}\.(?:a|c|n|w)\d+\b")


def _texts(messages: list[dict]) -> str:
    return "\n".join((m.get("content") or "") if isinstance(m.get("content"), str) else json.dumps(m.get("content"))
                     for m in messages)


def leak(prompts: dict, agent_keys: set[str] | None = None) -> dict:
    hits = []
    for key, msgs in prompts.items():
        t = _texts(msgs)
        pats = [(FRAG_ID, "fragment_id")] + ([(PHYSICAL_KEY, "physical_key")] if agent_keys is None or key in agent_keys else [])
        for pat, kind in pats:
            for m in pat.findall(t):
                hits.append({"key": key, "kind": kind, "match": m})
    return {"ok": not hits, "hits": hits[:20], "n": len(hits)}


def agent_keys(events: list[dict]) -> set[str]:
    return {e["payload"]["key"] for e in events if e["type"] == "llm_call"
            and e["payload"].get("component") in ("requester", "responder")}


def card_leak(prompts: dict, events: list[dict]) -> dict:
    """요청자·응답자 입력만 본다 (경계 모듈은 자기 그룹 구성원 실제 id를 쓴다)."""
    hits = [{"key": k, "match": m} for k in agent_keys(events) & set(prompts) for m in AGENT_ID.findall(_texts(prompts[k]))]
    return {"ok": not hits, "hits": hits[:20], "n": len(hits)}


def access(run_dir: Path) -> dict:
    p = Path(run_dir) / "obs" / "access.jsonl"
    rows = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x] if p.exists() else []
    denied = [r for r in rows if not r.get("allowed", True)]
    return {"ok": not denied, "checked": len(rows), "denied": denied[:20]}


def budget(ledger_tasks: list[dict], cap: dict | None) -> dict:
    """cap = {"calls": n, "tokens": n} (None이면 상한 없는 조건: 검사 생략)."""
    if not cap:
        return {"ok": True, "skipped": True}
    over = [t["task_id"] for t in ledger_tasks if t["calls"] > cap["calls"] or t["tokens"] > cap["tokens"]]
    return {"ok": not over, "over": over}


def determinism(run_dir: Path) -> dict:
    wal = Path(run_dir) / "wal" / "events.jsonl"
    return {"ok": wal.exists(), "wal_sha256": hashlib.sha256(wal.read_bytes()).hexdigest() if wal.exists() else None}


def run_checks(run_dir: Path, events: list[dict], prompts: dict, ledger_tasks: list[dict], cap: dict | None,
               direct: bool) -> dict:
    out = {"leak": leak(prompts, agent_keys(events)), "access": access(run_dir), "budget": budget(ledger_tasks, cap),
           "determinism": determinism(run_dir)}
    if direct:
        out["card_leak"] = card_leak(prompts, events)
    out["ok"] = all(v["ok"] for v in out.values() if isinstance(v, dict))
    return out
