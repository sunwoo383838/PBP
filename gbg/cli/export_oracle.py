"""retrieval_oracle용 정답 조각 내보내기 (오프라인, 채점기처럼 private를 읽는다).

    uv run python -m gbg.cli.export_oracle <scenario_dir> [--out <dir>]

worldgen 4.4는 동결돼 oracle_evidence/를 내보내지 않으므로 하네스가 대신 만든다. 과제마다 원격 need의 결정 필수
조각을 그 need의 그룹별로 모아 <out>/<wid>.json = {group: [{agent, day, text}]}로 쓴다. 기본 출력은
<scenario_dir>/oracle_evidence/ 이고, 실행 프로세스는 retrieval_oracle 조건에서만 이 폴더를 마운트한다.
"""
import argparse
import json
from pathlib import Path


def export(scenario: Path, out: Path) -> int:
    frags = {f["fid"]: f for f in map(json.loads, (scenario / "private" / "fragments.jsonl").read_text(encoding="utf-8").splitlines())}
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for line in (scenario / "private" / "gold.jsonl").read_text(encoding="utf-8").splitlines():
        g = json.loads(line)
        by: dict[str, list[dict]] = {}
        for need in g["needs"]:
            if need.get("local"):
                continue
            for fid in need.get("critical_components") or []:
                f = frags.get(fid)
                if f and f.get("text"):
                    row = {"agent": f["agent"], "day": f["day"], "text": f["text"]}
                    if row not in by.setdefault(need["group"], []):
                        by[need["group"]].append(row)
        (out / f"{g['wid']}.json").write_text(json.dumps(by, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8")
        n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    out = args.out or args.scenario / "oracle_evidence"
    print(f"{export(args.scenario, out)} tasks → {out}")


if __name__ == "__main__":
    main()
