"""자동 재개 감시: 실행(run_one)이 비정상 종료하면 같은 폴더로 다시 시작한다(WAL 체크포인트에서 재개, 진행 중
라운드는 LLM 캐시로 재생). 재시작은 과제 실패로 세지 않고 횟수만 기록한다.

같은 지점(마지막으로 커밋된 day·round)에서 연속으로 3번 재시작해도 넘어가지 못하면 멈추고 알린다(ALERT 파일 + 종료
코드 2). 결정적 버그(같은 곳에서 되풀이되는 하네스 예외)나 영구적인 API 장애가 여기에 걸린다.

    uv run python -m gbg.cli.supervise OUT_DIR -- <run_one 인자 전부>
기록: OUT_DIR/supervise.jsonl (시작·종료·재시작마다 한 줄), OUT_DIR/ALERT (멈췄을 때)
"""
import json
import subprocess
import sys
from pathlib import Path

MAX_SAME_POINT = 3
BACKOFF_S = (30, 120, 300)


def last_commit(out: Path) -> tuple[int, int] | None:
    """WAL의 마지막 round_commit (day, round). 없으면 None."""
    p = out / "wal" / "events.jsonl"
    if not p.exists():
        return None
    last = None
    with p.open("rb") as f:
        for line in f:
            if b'"round_commit"' in line:
                try:
                    ev = json.loads(line)
                except ValueError:
                    break
                last = (ev["day"], ev["round"])
    return last


def log(out: Path, rec: dict):
    import datetime
    rec = {"at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"), **rec}   # 기록용 (실행 결과와 무관)
    with (out / "supervise.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None):
    import time
    argv = list(sys.argv[1:] if argv is None else argv)
    out = Path(argv[0])
    cmd = [sys.executable, "-m", "gbg.cli.run_one", *argv[argv.index("--") + 1:]]
    out.mkdir(parents=True, exist_ok=True)
    (out / "ALERT").unlink(missing_ok=True)
    restarts, same, point = 0, 0, last_commit(out)
    while True:
        log(out, {"event": "start", "restarts": restarts, "from": point})
        with (out / "run.log").open("a", encoding="utf-8") as lf:
            rc = subprocess.call(cmd, stdout=lf, stderr=subprocess.STDOUT)
        if rc == 0:
            log(out, {"event": "done", "restarts": restarts})
            return 0
        now = last_commit(out)
        same = same + 1 if now == point else 1
        restarts += 1
        log(out, {"event": "restart", "exit": rc, "restarts": restarts, "at_point": now, "same_point_count": same})
        if same >= MAX_SAME_POINT:
            (out / "ALERT").write_text(json.dumps({"reason": f"{MAX_SAME_POINT}회 연속 같은 지점에서 실패",
                                                    "point": now, "exit": rc, "restarts": restarts},
                                                   ensure_ascii=False), encoding="utf-8")
            log(out, {"event": "stop", "point": now})
            return 2
        point = now
        time.sleep(BACKOFF_S[min(same, len(BACKOFF_S)) - 1])


if __name__ == "__main__":
    sys.exit(main())
