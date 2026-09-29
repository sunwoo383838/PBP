"""채점 CLI (오프라인): 한 시나리오에서 돈 조건별 실행을 채점해 원장·지표·검사·짝지은 부트스트랩을 쓴다.

    uv run python -m gbg.cli.score <scenario_dir> direct=<run_dir> routing=<run_dir> ... [--max-day 10]
        [--cache cond=<llm_cache.sqlite>] [--out <dir>]

캐시를 주지 않으면 <run_dir>/../llm_cache_<cond>.sqlite를 찾는다 (게이트의 창·증거 판정과 누출 검사가 프롬프트를 읽는다).
출력: <out>/ledger_<cond>.json, report.json, report.md. 원리상 풀 수 없는 과제는 Acc_exact 분모에서 빼고 따로 센다.
"""
import argparse
import json
from pathlib import Path

from gbg.benchmarks.worldgen.scoring import load_private, strata, verify
from gbg.contracts.conditions import load_conditions
from gbg.scoring import bootstrap, checks, ledger, metrics

ROOT = Path(__file__).resolve().parents[2]


def _pairs(xs: list[str]) -> dict[str, Path]:
    return {k: Path(v) for k, v in (x.split("=", 1) for x in xs)}


def score_run(cond: str, run_dir: Path, cache: Path | None, priv, conds) -> dict:
    events = ledger.load_events(run_dir)
    keys = {e["payload"]["key"] for e in events if e["type"] == "llm_call" and e["payload"].get("key")}
    prompts = ledger.load_prompts(cache, keys)
    led = ledger.build(events, priv, verify, strata, prompts)
    c = conds[cond]
    cap = None if not c.budget_limit else {"calls": conds.defaults.budget.calls, "tokens": conds.defaults.budget.tokens}
    return {"ledger": led, "summary": metrics.summarize(led),
            "checks": checks.run_checks(run_dir, events, prompts, led["tasks"], cap, direct=c.agent_tool == "ask_agent"),
            "prompts_found": len(prompts), "llm_calls": len(keys)}


def render_md(report: dict) -> str:
    lines = ["| 조건 | Acc_exact (풀 수 있는 과제) | 전체 | 슬롯 | need 전달 | 과제당 토큰 | tok/success | 호출 p50·p95 | 소진 | 응답자 상한 과제 | 제출 실패 | 검사 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for cond, r in report["conditions"].items():
        s, h = r["summary"], r["summary"]["headline"]
        lines.append(f"| {cond} | {h['acc_exact']['exact']}/{h['acc_exact']['n']} ({h['acc_exact']['acc']}) | "
                     f"{h['acc_exact_all']['acc']} | {s['slot_acc']} | {s['need_delivery']} | {h['tokens_per_task']} | "
                     f"{h['tok_per_success']} | {s['calls']['p50']}·{s['calls']['p95']} | {s['budget']['exhausted']} | "
                     f"{s['budget']['tasks_with_responder_step_cap']} | {s['budget']['submit_failures']} | "
                     f"{'ok' if r['checks']['ok'] else 'FAIL'} |")
    lines += ["", "게이트 (need 단위, 풀 수 있는 과제): 실패 / 도달 (조건부 실패율)", "",
              "| 조건 | L_req | L_route | L_sel | L_state | L_use | ok | 오류 |", "|---|---|---|---|---|---|---|---|"]
    for cond, r in report["conditions"].items():
        g = r["summary"]["gates"]["stages"]
        cells = [f"{g[k]['failed']}/{g[k]['reached']} ({g[k]['conditional_failure']})" for k in ("L_req", "L_route", "L_sel", "L_state", "L_use")]
        lines.append(f"| {cond} | " + " | ".join(cells) + f" | {g['ok']['reached']} | {r['summary']['gates']['errors']} |")
    lines += ["", "등급별 Acc_exact", "", "| 조건 | " + " | ".join("ABCD") + " | C_ops |", "|---|---|---|---|---|---|"]
    for cond, r in report["conditions"].items():
        st = r["summary"]["strata"]
        cell = lambda d: f"{d['exact']}/{d['n']}" if d else "-"
        lines.append(f"| {cond} | " + " | ".join(cell(st["class"].get(k)) for k in "ABCD") + f" | {cell(st['c_ops'].get('True'))} |")
    if report["paired"]:
        lines += ["", "짝지은 차이 (b − a, Acc_exact, 95% CI)", ""]
        for p in report["paired"]:
            lines.append(f"- {p['b']} − {p['a']}: {p.get('diff')} {p.get('ci95')} (n={p['n']})")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", type=Path)
    ap.add_argument("runs", nargs="+", help="cond=run_dir")
    ap.add_argument("--max-day", type=int)
    ap.add_argument("--cache", action="append", default=[], help="cond=llm_cache.sqlite")
    ap.add_argument("--conditions", type=Path, default=ROOT / "configs" / "conditions.yaml")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    priv = load_private(a.scenario, a.max_day)
    conds = load_conditions(a.conditions)
    runs, caches = _pairs(a.runs), _pairs(a.cache)
    report = {"scenario": str(a.scenario), "seed": priv.seed, "conditions": {}, "paired": []}
    rows = []
    for cond, run_dir in runs.items():
        name = cond.split("@", 1)[0]                                     # "ingress@2" 같은 별칭 허용
        cache = caches.get(cond) or next(iter(run_dir.parent.glob(f"llm_cache_{name}*.sqlite")), None)
        r = score_run(name, run_dir, cache, priv, conds)
        report["conditions"][cond] = r
        rows += [{"world": str(a.scenario), "task_id": t["task_id"], "day": t["day"], "condition": cond,
                  "exact": t["exact"]} for t in r["ledger"]["tasks"] if not t["unreachable"]]
    names = list(runs)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            report["paired"].append(bootstrap.paired(rows, x, y))
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        for cond, r in report["conditions"].items():
            (a.out / f"ledger_{cond}.json").write_text(json.dumps(r["ledger"], ensure_ascii=False, indent=1), encoding="utf-8")
        slim = {**report, "conditions": {c: {k: v for k, v in r.items() if k != "ledger"} for c, r in report["conditions"].items()}}
        (a.out / "report.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
        (a.out / "report.md").write_text(render_md(report), encoding="utf-8")
    print(render_md(report))
    for cond, r in report["conditions"].items():
        bad = {k: v for k, v in r["checks"].items() if isinstance(v, dict) and not v["ok"]}
        if bad:
            print(f"[검사 실패] {cond}: " + json.dumps(bad, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
