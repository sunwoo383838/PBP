"""기준 셀 런의 obs/context_windows.jsonl → 요청자 첫 호출의 컨텍스트 구성 (출처별 항목 수, 토큰) 일자별 집계.
출력: gates/context__<model>__<cond>__<seed>.json"""
import json, sys
from collections import defaultdict, Counter
from pathlib import Path
M = Path("/root/project/g2g_main")
runs = [p for p in M.glob("runs/*/*/s1[234]")] + [p for p in M.glob("runs_appx/*/s1[234]")]
for run in runs:
    parts = run.parts
    name = f"context__{parts[-3]}__{parts[-2]}__{parts[-1]}.json" if parts[-4] == "runs" else f"context__appx__{parts[-2]}__{parts[-1]}.json"
    out = M / "gates" / name
    if out.exists(): continue
    f = run / "obs/context_windows.jsonl"
    if not f.exists(): continue
    agg = defaultdict(lambda: {"n": 0, "raw_tokens": 0, "summary_tokens": 0, "history_len": 0, "items": Counter(), "system_tokens": 0, "task_tokens": 0})
    resp = defaultdict(lambda: {"n": 0, "raw_tokens": 0, "summary_tokens": 0, "items": Counter()})
    with open(f, encoding="utf-8") as fh:
        for line in fh:
            if '"step": 1,' not in line and '"step":1,' not in line: continue
            x = json.loads(line)
            if x.get("step") != 1 or x.get("final"): continue
            if x.get("component") == "requester" and x.get("serving") is None:
                a = agg[x["day"]]
            elif x.get("component") == "responder":
                a = resp[x["day"]]
            else: continue
            a["n"] += 1; a["raw_tokens"] += x.get("raw", {}).get("tokens", 0); a["summary_tokens"] += x.get("summary", {}).get("tokens", 0)
            if "history_len" in a: a["history_len"] += x.get("history_len", 0); a["system_tokens"] += x.get("system_tokens", 0); a["task_tokens"] += x.get("task_tokens", 0)
            for it in x.get("context_items", []):
                a["items"][f"{it.get('source')}|{it.get('where')}"] += 1
    json.dump({"requester": {d: {**v, "items": dict(v["items"])} for d, v in agg.items()}, "responder": {d: {**v, "items": dict(v["items"])} for d, v in resp.items()}},
              open(out, "w"), ensure_ascii=False)
    print("done", name, flush=True)
print("ALL_DONE")
