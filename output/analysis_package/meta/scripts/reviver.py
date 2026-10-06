"""ALERT로 멈춘 런을 자동 재기동 (DeepInfra 잔액 402 등 일시 장애 대비). 코드·설정은 그대로, 같은 인자로 supervise만
다시 띄운다(WAL 체크포인트 재개). 런당 최대 8회, 재기동 전 API가 200을 줄 때까지 기다린다. 기록: reviver.log"""
import json, os, subprocess, time, urllib.request
from pathlib import Path
M = Path("/root/project/g2g_main"); PY = "/root/project/g2g/.venv/bin/python"; HOME = os.environ["HOME"]
LOG = M / "reviver.log"; count = {}

def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%m-%d %H:%M:%S ") + msg + "\n")

def api_ok() -> bool:
    import importlib.util
    spec = importlib.util.spec_from_file_location("s", M / "code/gbg/llm/secrets.py"); s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
    key = [v for k, v in vars(s).items() if "KEY" in k.upper()][0]
    req = urllib.request.Request("https://api.deepinfra.com/v1/openai/chat/completions", method="POST",
                                 data=json.dumps({"model": "Qwen/Qwen3.5-9B", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        return urllib.request.urlopen(req, timeout=60).status == 200
    except Exception:
        return False

def args_for(run: Path):
    p = run.relative_to(M).parts
    seed = p[-1]
    if p[0] == "runs":
        model, cond = p[1], p[2]; sc = M / "scenarios" / f"D5_{seed}_T45"; day = 15; code = M / "code"
    elif p[0] == "runs_g":
        model, cond = "qwen3.5-27b", p[2]; sc = next((M / "scenarios_g" / p[1]).glob(f"D*_{seed}_T45")); day = 10; code = M / "code"
    else:
        model, cond = "qwen3.5-27b", p[1]; sc = M / "scenarios" / f"D5_{seed}_T45"; day = 10; code = M / "code_appx"
    return code, [PY, "-m", "gbg.cli.supervise", str(run), "--", cond, str(sc), str(run), "--max-day", str(day),
                  "--embed-cache", f"{HOME}/.cache/gbg/embeddings.sqlite", "--rerank-cache", f"{HOME}/.cache/gbg/rerank.sqlite",
                  "--model", model]

log("시작")
while True:
    alerts = [a.parent for top in ("runs", "runs_g", "runs_appx") for a in (M / top).glob("**/ALERT")]
    for run in alerts:
        n = count.get(run, 0)
        if n >= 8:
            continue
        while not api_ok():
            log(f"API 대기 (402 등): {run.relative_to(M)}"); time.sleep(120)
        code, cmd = args_for(run)
        subprocess.Popen(cmd, cwd=code, env={**os.environ, "PYTHONPATH": str(code)}, stdout=open(run / "supervise.out", "a"),
                         stderr=subprocess.STDOUT, start_new_session=True)
        count[run] = n + 1
        log(f"재기동 {count[run]}회: {run.relative_to(M)}")
        time.sleep(3)
    def running():
        for p in Path("/proc").iterdir():
            try:
                if p.name.isdigit() and b"gbg.cli.supervise" in (p / "cmdline").read_bytes():
                    return True
            except OSError:
                pass
        return False
    if not alerts and not running():
        log("모든 런 종료"); break
    time.sleep(60)
