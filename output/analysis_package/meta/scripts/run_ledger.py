"""런 하나의 need 원장(전달·게이트) 계산 → gates/<run_id>.json. 사용: run_ledger.py <run_dir> <scenario_dir> <max_day> <out.json>"""
import json, sys, time
from collections import Counter
from pathlib import Path
import os
sys.path.insert(0, os.environ.get("GBG_CODE", "/root/project/g2g_main/code"))   # 채점기는 master(GBG_CODE)로 돌릴 수 있음
from gbg.benchmarks.worldgen.scoring import load_private, strata, verify
from gbg.scoring.ledger import build, load_events, load_prompts
run, sc, maxday, out = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4])
t0 = time.time()
priv = load_private(sc)
ev = load_events(run)
keys = {e["payload"]["key"] for e in ev if e["type"] == "llm_call"}
led = build(ev, priv, verify, strata, load_prompts(run / "llm_cache.sqlite", keys))
tasks = {t["task_id"]: t for t in led["tasks"]}
needs = [n for n in led["needs"] if priv.gold[n["task_id"]]["day"] <= maxday]
out.write_text(json.dumps({"run": str(run), "seconds": round(time.time() - t0, 1), "tasks": led["tasks"], "needs": needs,
                           "task_keys": list(led["tasks"][0].keys()) if led["tasks"] else [], "need_keys": list(needs[0].keys()) if needs else []}, ensure_ascii=False, default=str))
print(run.name, "needs", len(needs), "gates", dict(Counter(n.get("gate") for n in needs)), "delivered", sum(bool(n.get("delivered")) for n in needs), f"{time.time()-t0:.0f}s")
