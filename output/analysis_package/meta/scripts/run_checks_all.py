"""81런 실행 검사 (오프라인, LLM 재실행 없음). gbg/scoring/checks.py의 규칙을 그대로 쓴다.
 leak         WAL의 llm_call 키마다 캐시된 요청에서 조각 id(FR-#####, 모든 입력)·내부 DB 키(요청자·응답자 입력만) 0건
 card_leak    요청자·응답자 입력의 실제 에이전트 id 0건 (카드 조건: direct·direct_relay·sidecar). 다른 조건은 참고로 요청자 입력만 집계
 budget       과제당 호출·토큰 ≤ 상한(300회, 4.0M, 최종 예약분 포함) — 원장 tasks의 calls·tokens
 determinism  WAL sha256을 다시 계산해 실행이 기록한 run_meta.json의 wal_hash와 대조 (기록 이후 변조·잘림 없음)
 access       obs/access.jsonl 거부 0건, 교차 그룹 읽기 수 (분할 조건 0이어야)
 retrieval    게이트웨이 검색 기록(obs/retrievals.jsonl)의 모든 후보(selected·cap_cut·outside_top_k·selected 목록)와
              보유자 색인(holders)의 작성자 그룹 = 검색한 게이트웨이 그룹 (full_load는 조직 전체 검색이라 참고만)
사용: run_checks_all.py [-j N]  → g2g_main/checks/<run_id>.json, output/analysis_package/tables/run_checks.csv"""
import csv, glob, hashlib, json, sqlite3, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, "/root/project/g2g")
from gbg.scoring.checks import AGENT_ID, FRAG_ID, PHYSICAL_KEY, _texts

M = Path("/root/project/g2g_main"); OUT = M / "checks"; OUT.mkdir(exist_ok=True)
CAP = {"calls": 300, "tokens": 4_000_000}
CARD = {"direct", "direct_relay", "sidecar"}


def runs():
    for p in sorted(glob.glob(f"{M}/runs/*/*/s1[234]")):
        q = Path(p); yield f"main__base__{q.parent.parent.name}__{q.parent.name}__{q.name}", q
    for p in sorted(glob.glob(f"{M}/runs_g/*/*/s1[234]")):
        q = Path(p); yield f"gcell__{q.parent.parent.name}__qwen3.5-27b__{q.parent.name}__{q.name}", q
    for p in sorted(glob.glob(f"{M}/runs_appx/*/s1[234]")):
        q = Path(p); yield f"appendix__base__qwen3.5-27b__{q.parent.name}__{q.name}", q


def grp(agent: str) -> str:
    return agent.split(":")[-1].split(".")[0].upper()


def check(arg):
    rid, run = arg
    cond = json.loads((run / "run.json").read_text())["condition"]
    ev = [json.loads(x) for x in (run / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines() if x]
    calls = [e["payload"] for e in ev if e["type"] == "llm_call"]
    comp = {c["key"]: c.get("component") for c in calls}
    db = sqlite3.connect(f"file:{run / 'llm_cache.sqlite'}?mode=ro", uri=True)
    leak = Counter(); card = Counter(); card_req = Counter(); missing = 0; ex = []
    for key, cp in comp.items():
        row = db.execute("select request from responses where key = ?", (key,)).fetchone()
        if not row:
            missing += 1; continue
        t = _texts(json.loads(row[0]).get("messages", []))
        agent_in = cp in ("requester", "responder")
        n_fr = len(FRAG_ID.findall(t)); n_pk = len(PHYSICAL_KEY.findall(t)) if agent_in else 0
        leak["fragment_id"] += n_fr; leak["physical_key"] += n_pk
        if (n_fr or n_pk) and len(ex) < 5: ex.append({"key": key, "component": cp, "fr": FRAG_ID.findall(t)[:2], "pk": PHYSICAL_KEY.findall(t)[:2] if agent_in else []})
        if agent_in:
            ids = AGENT_ID.findall(t)
            card[cp] += len(ids)
            if cp == "requester": card_req["hits"] += len(ids)
    led = json.loads((M / "gates" / f"{rid}.json").read_text())["tasks"]
    over = [(t["task_id"], t["calls"], t["tokens"]) for t in led if t["calls"] > CAP["calls"] or t["tokens"] > CAP["tokens"]]
    wal = hashlib.sha256((run / "wal" / "events.jsonl").read_bytes()).hexdigest()
    meta = run / "run_meta.json"                                         # retarget로 멈춘 런은 run_meta가 없음(정상 종료 기록 없음)
    rec = json.loads(meta.read_text()).get("wal_hash") if meta.exists() else None
    last_day = max((e.get("day") or 0) for e in ev)
    acc = Counter()
    for line in (run / "obs" / "access.jsonl").read_text().splitlines():
        a = json.loads(line); acc["checked"] += 1; acc["denied"] += not a["allowed"]; acc["cross"] += a["scope"] != "own"
    ret = Counter(); foreign = []
    rp = run / "obs" / "retrievals.jsonl"
    if rp.exists():
        for line in rp.read_text().splitlines():
            r = json.loads(line); g = r.get("group")
            ret["retrievals"] += 1
            if g is None:                                                    # full_load: 조직 전체 검색
                ret["org_wide"] += 1; continue
            for fld in ("candidates", "outside_top_k", "selected"):
                for c in r.get(fld) or []:
                    ret[f"n_{fld}"] += 1
                    if grp(c["agent"]) != g:
                        ret[f"foreign_{fld}"] += 1
                        if len(foreign) < 5: foreign.append({"rid": r["rid"], "group": g, "field": fld, "agent": c["agent"]})
            for h in r.get("holders") or []:
                ret["n_holders"] += 1; ret["foreign_holders"] += grp(h) != g
    res = {"run": rid, "condition": cond, "llm_calls": len(comp), "prompts_missing": missing,
           "leak_fragment_id": leak["fragment_id"], "leak_physical_key": leak["physical_key"], "leak_examples": ex,
           "card_leak_applies": cond in CARD, "card_leak_requester": card["requester"], "card_leak_responder": card["responder"],
           "budget_tasks": len(led), "budget_over": over,
           "wal_sha256": wal, "wal_hash_recorded": rec, "wal_hash_match": (wal == rec) if rec else None, "wal_last_day": last_day,
           "access_checked": acc["checked"], "access_denied": acc["denied"], "access_cross": acc["cross"],
           **{f"ret_{k}": v for k, v in ret.items()}, "ret_foreign_examples": foreign}
    (OUT / f"{rid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    return res


if __name__ == "__main__":
    j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 8
    todo = list(runs())
    with Pool(j) as p:
        rows = []
        for r in p.imap_unordered(check, todo):
            rows.append(r); print(f"{len(rows)}/{len(todo)} {r['run']} leak {r['leak_fragment_id']}/{r['leak_physical_key']} card {r['card_leak_requester']}/{r['card_leak_responder']} over {len(r['budget_over'])} wal {r['wal_hash_match']} foreign {sum(v for k, v in r.items() if k.startswith('ret_foreign_') and isinstance(v, int))}", flush=True)
    rows.sort(key=lambda r: r["run"])
    cols = [k for k in rows[0] if not k.endswith("_examples") and k != "budget_over"] + ["budget_over_n"]
    allk = sorted({k for r in rows for k in r if k.startswith("ret_") and not k.endswith("_examples")})
    cols = [c for c in cols if not c.startswith("ret_")] + allk
    with open("/root/project/g2g/output/analysis_package/tables/run_checks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in rows: w.writerow({**{k: r.get(k, 0) for k in cols}, "budget_over_n": len(r["budget_over"])})
    print("DONE", len(rows))
