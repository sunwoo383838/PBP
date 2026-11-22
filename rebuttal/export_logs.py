"""추가 실험 런의 원본 로그를 rebuttal/logs/ 아래로 압축해 옮긴다 (본 실험의 analysis_package/logs와 같은 형식).

    python rebuttal/export_logs.py RB_DIR [OUT_DIR]
RB_DIR: runs/와 runs_d/가 있는 폴더. 런마다 events.jsonl.gz(실행 기록), obs_*.jsonl.gz(관측 기록), timing_llm.jsonl.gz,
manifest.json, manifest_history.jsonl, run.json, supervise.jsonl, run_meta.json(시나리오 경로는 폴더 이름만 남김).
폴더 이름은 원장과 같다: A__<조건>__<시드>, C__<모델>__sidecar__<시드>, D__<셀>__<조건>__s12.
"""
import gzip, json, shutil, sys, os
from pathlib import Path
RB = Path(sys.argv[1]); OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "logs"
OBS = ("gateway", "messages", "retrievals", "batches", "llm", "access", "db_lookups", "context_windows")

def runs():
    for p in sorted(RB.glob("runs/*/*/s*")):
        model, cond, seed = p.parts[-3:]
        yield p, (f"C__{model}__{cond}__{seed}" if cond == "sidecar" else f"A__{cond}__{seed}")
    for p in sorted(RB.glob("runs_d/*/*/s*")):
        cell, cond, seed = p.parts[-3:]
        yield p, f"D__{cell}__{cond}__{seed}"

for run, name in runs():
    L = OUT / name; L.mkdir(parents=True, exist_ok=True)
    pairs = [(run / "wal/events.jsonl", "events.jsonl.gz"), (run / "timing/llm.jsonl", "timing_llm.jsonl.gz")]
    pairs += [(run / "obs" / f"{n}.jsonl", f"obs_{n}.jsonl.gz") for n in OBS]
    for src, dst in pairs:
        if src.exists():
            with open(src, "rb") as fi, gzip.GzipFile(L / dst, "wb", compresslevel=9, mtime=0) as fo: shutil.copyfileobj(fi, fo)
    for n in ("manifest.json", "manifest_history.jsonl", "run.json", "supervise.jsonl"):
        if (run / n).exists(): shutil.copy(run / n, L / n)
    if (run / "run_meta.json").exists():
        m = json.load(open(run / "run_meta.json")); m["scenario"] = os.path.basename(str(m.get("scenario", "")).rstrip("/"))
        json.dump(m, open(L / "run_meta.json", "w"), indent=1)
    print("done", name, sum(f.stat().st_size for f in L.iterdir()) // 1024, "KB", flush=True)
