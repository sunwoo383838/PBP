"""목표 일수 변경: 1차(runs/) 15일, 2차 G 셀(runs_g/) 10일. 목표를 이미 끝낸 런은 멈추기만, 아직인 런은 멈춘 뒤
같은 인자에 --max-day만 바꿔 supervise로 다시 띄운다 (WAL 체크포인트에서 재개). --apply 없으면 계획만 출력."""
import json, os, signal, subprocess, sys, time
from pathlib import Path
M = Path("/root/project/g2g_main"); APPLY = "--apply" in sys.argv
TARGET = {"runs": 15, "runs_g": 10}
me = os.getpid()

def procs():
    out = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit() or int(p.name) == me:
            continue
        try:
            cmd = (p / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        cmd = [c.decode(errors="replace") for c in cmd if c]
        if len(cmd) > 2 and cmd[1:3] in (["-m", "gbg.cli.supervise"], ["-m", "gbg.cli.run_one"]):
            out.append((int(p.name), cmd))
    return out

def done_day(run: Path) -> int:
    d = 0
    for l in open(run / "wal/events.jsonl"):
        if '"round_commit"' in l:
            e = json.loads(l)
            if e["round"] == 3:
                d = max(d, e["day"])
    return d

ps = procs()
plan = []
for top, target in TARGET.items():
    for sup in sorted(M.glob(f"{top}/*/*/s*/supervise.jsonl")):
        run = sup.parent
        if '"done"' in sup.read_text().splitlines()[-1]:
            continue
        mine = [(pid, c) for pid, c in ps if str(run) in c]
        sv = [c for pid, c in mine if c[2] == "gbg.cli.supervise"]
        d = done_day(run)
        plan.append((run, target, d, mine, sv[0] if sv else None))
for run, target, d, mine, sv in plan:
    act = "멈춤" if d >= target else f"멈춘 뒤 --max-day {target}로 재개"
    print(f"{str(run).split('g2g_main/')[1]}: 완료 {d}일 → {act} (프로세스 {len(mine)})")
if not APPLY:
    sys.exit()
for run, target, d, mine, sv in plan:
    for pid, _ in mine:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
time.sleep(5)
for run, target, d, mine, sv in plan:
    for pid, _ in mine:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    with open(run / "retarget.jsonl", "a") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "done_day": d, "target": target,
                            "action": "stop" if d >= target else "resume"}) + "\n")
    if d >= target or sv is None:
        continue
    args = sv[sv.index("--") + 1:]
    args[args.index("--max-day") + 1] = str(target)
    code = Path(sv[0]).parent  # 파이썬 경로 (venv)
    cwd = next((p for p in ("code", "code_appx") if (M / p).exists() and str(M / p) in " ".join(sv)), "code")
    env = {**os.environ, "PYTHONPATH": str(M / "code")}
    subprocess.Popen([sv[0], "-m", "gbg.cli.supervise", str(run), "--", *args], cwd=M / "code", env=env,
                     stdout=open(run / "supervise.out", "a"), stderr=subprocess.STDOUT, start_new_session=True)
print("적용 완료")
