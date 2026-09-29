"""과제 단위 타임라인 렌더러 (오프라인 검토 도구, private를 읽는다).

    uv run python -m gbg.cli.trace_view <scenario_dir> --run direct=<run_dir>[,<llm_cache>] --run routing=... \\
        [--tasks W-00001,W-00002] [--max-day 10] --out <dir>

과제마다 HTML 한 장: 위에 과제·요청 범위·정답·need(결정 필수 조각), 아래에 조건별 열을 나란히 둔다. 열 안은 시간순으로
요청자의 LLM 원출력·도구 호출 → 보낸 질문·받은 사람·받은 답 → 응답자 창의 조각 상태(원문/요약/없음) → 경계 모듈의
증거·선택·조립 → 최종 답과 정답의 슬롯별 비교 → need별 전달 판정과 처음 끊긴 게이트. 결정 필수 조각이 나오는 줄은
강조한다. index.html에 과제 × 조건 요약표와 summary.json을 함께 쓴다.
"""
import argparse
import html
import json
import sqlite3
from pathlib import Path

from gbg.benchmarks.worldgen.adapter import WorldgenAdapter
from gbg.contracts.envelope import render_response
from gbg.scoring.delivery import need_delivery
from gbg.scoring.gates import need_gates, present, window_state

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--mut:#6b6b70;--line:#e3e3e8;--card:#f7f7f9;--hl:#fff1a8;--ok:#1f7a3a;--bad:#b3261e;--acc:#2356c7}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececf0;--mut:#9a9aa2;--line:#2c2c31;--card:#1d1d21;--hl:#5a4a00;--ok:#6fd08c;--bad:#ff8a80;--acc:#8fb0ff}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:13px/1.45 ui-sans-serif,system-ui,sans-serif}
h1{font-size:18px;margin:0 0 6px} h2{font-size:14px;margin:14px 0 6px} .mut{color:var(--mut)}
pre{white-space:pre-wrap;word-break:break-word;margin:4px 0;font:12px/1.4 ui-monospace,monospace}
.cols{display:grid;grid-template-columns:repeat(var(--n),minmax(320px,1fr));gap:12px;overflow-x:auto}
.col{border:1px solid var(--line);border-radius:8px;padding:8px;min-width:0}
.ev{background:var(--card);border-radius:6px;padding:6px 8px;margin:6px 0}
.tag{display:inline-block;font-size:11px;padding:1px 6px;border-radius:9px;border:1px solid var(--line);margin-right:4px}
mark{background:var(--hl);color:inherit} .ok{color:var(--ok);font-weight:600} .bad{color:var(--bad);font-weight:600}
table{border-collapse:collapse;width:100%} td,th{border:1px solid var(--line);padding:3px 6px;text-align:left;vertical-align:top}
a{color:var(--acc)}
"""


def esc(t) -> str:
    return html.escape(t if isinstance(t, str) else json.dumps(t, ensure_ascii=False))


def _prompts(cache: Path | None, keys: set[str]) -> dict:
    if cache is None or not cache.exists() or not keys:
        return {}
    db = sqlite3.connect(cache)
    out = {}
    for k in keys:
        row = db.execute("select request from responses where key = ?", (k,)).fetchone()
        if row:
            out[k] = json.loads(row[0]).get("messages", [])
    return out


class Highlighter:
    def __init__(self, frags: list[dict], names: dict):
        self.frags, self.names = frags, names

    def __call__(self, text: str, limit: int = 2500) -> str:
        text = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
        cut = text[:limit] + (f"\n… ({len(text) - limit} chars more)" if len(text) > limit else "")
        lines = []
        for line in cut.splitlines() or [""]:
            hits = [f["fid"] for f in self.frags if present(f, line, self.names)]
            lines.append(f"<mark title='{' '.join(hits)}'>{esc(line)}</mark>" if hits else esc(line))
        return "<pre>" + "\n".join(lines) + "</pre>"


def load(scenario: Path, max_day: int):
    a = WorldgenAdapter()
    a.load(scenario / "harness")
    tasks = {e.task_id: e for e in a.events() if e.kind == "cross" and e.day <= max_day}
    gold = {g["wid"]: g for g in map(json.loads, (scenario / "private" / "gold.jsonl").read_text(encoding="utf-8").splitlines())
            if g["wid"] in tasks}
    frags = {f["fid"]: f for f in map(json.loads, (scenario / "private" / "fragments.jsonl").read_text(encoding="utf-8").splitlines())}
    names = {}
    for items in json.loads((scenario / "harness" / "snapshot_day0" / "catalog.json").read_text(encoding="utf-8")).values():
        for k, v in items.items():
            if isinstance(v, dict):
                names.setdefault(k.split("/", 1)[1], []).extend(x for x in (v.get("name"), v.get("alias")) if x)
    return tasks, gold, frags, names


def _norm_slot(slot, v):
    if v is None:
        return None
    if slot.type == "set":
        return sorted(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in v)
    if slot.type in ("int", "number") and not isinstance(v, bool):
        return float(v)
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def analyze(run_dir: Path, cache: Path | None, tasks, gold, frags, names) -> dict:
    events = [json.loads(x) for x in (run_dir / "wal" / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    by_task: dict[str, list] = {}
    for e in events:
        t = e["payload"].get("task_id")
        if t in gold:
            by_task.setdefault(t, []).append(e)
    keys = {e["payload"]["key"] for es in by_task.values() for e in es if e["type"] == "llm_call" and e["payload"].get("key")}
    prompts = _prompts(cache, keys)
    delivery = need_delivery(events, {w: gold[w] for w in by_task}, frags, names=names)["needs"]
    out = {}
    for wid, es in by_task.items():
        ans = next((e["payload"] for e in es if e["type"] == "answer"), None)
        slots = tasks[wid].output_schema.slots
        a = (ans or {}).get("answer") or {}
        cmp = [(s.name, a.get(s.name), gold[wid]["gold"].get(s.name),
                ans is not None and ans.get("answer") is not None and _norm_slot(s, a.get(s.name)) == _norm_slot(s, gold[wid]["gold"].get(s.name)))
               for s in slots]
        ok = bool(cmp) and all(c[3] for c in cmp)
        rows = [r for r in delivery if r["task_id"] == wid]
        gates = need_gates(es, gold[wid], frags, rows, prompts, ok, names)
        out[wid] = {"events": es, "answer": ans, "compare": cmp, "correct": ok, "delivery": rows, "gates": gates,
                    "prompts": prompts, "budget": (ans or {}).get("budget"), "error": (ans or {}).get("error")}
    return out


def render_column(name: str, r: dict | None, hl: Highlighter, crit: list[dict], names) -> str:
    if r is None:
        return f"<div class='col'><h2>{esc(name)}</h2><p class='mut'>이 조건에서 아직 실행되지 않음</p></div>"
    parts = [f"<h2>{esc(name)} — <span class='{'ok' if r['correct'] else 'bad'}'>{'정답' if r['correct'] else '오답'}</span></h2>"]
    b = r["budget"] or {}
    if b:
        u = b.get("used", {})
        comp = {k: v["calls"] for k, v in b.get("by_component", {}).items()}
        parts.append(f"<p class='mut'>호출 {u.get('calls')} · 토큰 {u.get('tokens')} · {esc(comp)}"
                     f"{' · <b>예산 소진</b>' if b.get('budget_exhausted') else ''}{' · 오류 ' + esc(r['error']) if r['error'] else ''}</p>")
    for e in r["events"]:
        p, t, actor = e["payload"], e["type"], e["actor"]
        if t == "llm_call":
            msg = p.get("message") or {}
            calls = "; ".join(f"{c['name']}({c['arguments'][:300]})" for c in msg.get("tool_calls", []))
            extra = ""
            prm = "\n".join(m.get("content") or "" for m in r["prompts"].get(p.get("key"), []))
            if p.get("component") == "responder" and prm:
                st = {f["fid"]: window_state(f, prm, names) for f in crit}
                extra = f"<div class='mut'>응답자 창의 결정 필수 조각: {esc(st)}</div>"
            if actor.startswith("boundary:") and prm:
                ev = prm.split("Group records found:", 1)[-1] if "Group records found:" in prm else prm.split("Group records:", 1)[-1]
                st = {f["fid"]: present(f, ev, names) for f in crit}
                extra = f"<div class='mut'>증거 블록 안 결정 필수 조각: {esc(st)}</div>"
            parts.append(f"<div class='ev'><span class='tag'>LLM</span><b>{esc(actor)}</b> <span class='mut'>{esc(p.get('component'))}"
                         f" step {p.get('step')} · {esc(p.get('finish_reason'))}</span>{extra}"
                         f"{hl(msg.get('content') or '', 1500)}<pre>{esc(calls)}</pre></div>")
        elif t in ("tool_call", "tool_result") and p.get("serving") is None:
            if t == "tool_result":
                parts.append(f"<div class='ev'><span class='tag'>도구</span>{esc(p.get('tool'))} → {hl(p.get('result') if p.get('ok') else p.get('error'), 1200)}</div>")
        elif t == "message":
            if p["kind"] == "request":
                parts.append(f"<div class='ev'><span class='tag'>질문</span><b>{esc(p.get('from_agent'))}</b> → "
                             f"<b>{esc(p.get('to_agent') or p.get('to_group') or 'egress')}</b>"
                             f"{'' if p.get('delivered', True) else ' <span class=bad>(전달 안 됨)</span>'}{hl(p['request']['question'], 800)}</div>")
            else:
                resp = p["response"]
                parts.append(f"<div class='ev'><span class='tag'>답</span><b>{esc(actor)}</b> → {esc(p.get('from_agent'))}"
                             f" <span class='mut'>({esc(resp['status'])})</span>{hl(render_response(resp), 2500)}</div>")
        elif t == "boundary_decision":
            keep = {k: p.get(k) for k in ("stage", "group", "action", "entities", "selected", "proposed", "referral_to",
                                           "referral_evidence", "referral_rejected", "requery", "targets", "referral_override")
                    if p.get(k) not in (None, [], {})}
            parts.append(f"<div class='ev'><span class='tag'>경계 결정</span><pre>{esc(json.dumps(keep, ensure_ascii=False, indent=1))}</pre>"
                         + (hl(p["answer"], 1500) if p.get("answer") else "") + "</div>")
    rows = "".join(f"<tr><td>{esc(n)}</td><td>{esc(a)}</td><td>{esc(g)}</td><td class='{'ok' if ok else 'bad'}'>{'✓' if ok else '✗'}</td></tr>"
                   for n, a, g, ok in r["compare"])
    parts.append(f"<h2>최종 답 vs 정답</h2><table><tr><th>슬롯</th><th>답</th><th>정답</th><th></th></tr>{rows}</table>")
    grows = "".join(f"<tr><td>{esc(g['need'])}</td><td><b>{esc(g['gate'])}</b></td><td>{esc({k: v for k, v in g.items() if k not in ('need', 'gate', 'group')})}</td></tr>"
                    for g in r["gates"])
    drows = "".join(f"<tr><td>{esc(d['need'])}</td><td>{esc([(x['fid'], x['method'], x['state']) for x in d['frags']])}</td></tr>" for d in r["delivery"])
    parts.append(f"<h2>need별 전달</h2><table>{drows}</table><h2>처음 끊긴 게이트</h2><table>{grows}</table>")
    return f"<div class='col'>{''.join(parts)}</div>"


def render_task(wid, tasks, gold, frags, names, runs: dict[str, dict]) -> str:
    g, te = gold[wid], tasks[wid]
    crit = [frags[fid] for n in g["needs"] if not n.get("local") for fid in (n.get("critical_components") or []) if fid in frags]
    hl = Highlighter(crit, names)
    needs = "".join(f"<tr><td>{esc(n['sem'])}</td><td>{esc(n['group'])}</td><td>{'local' if n.get('local') else ''}</td><td>"
                    + "<br>".join(f"<mark>{esc(frags[f]['fid'])}</mark> [{esc(frags[f]['agent'])}, {esc(frags[f]['disc'])}, day {frags[f]['day']}] {esc(frags[f]['text'])}"
                                  for f in (n.get("critical_components") or []) if f in frags) + "</td></tr>" for n in g["needs"])
    head = (f"<h1>{esc(wid)} · {esc(g['template'])} · 등급 {esc(g['state_class'])}{' · C_ops' if g['c_ops'] else ''} · day {te.day}</h1>"
            f"<p><b>요청자</b> {esc(te.agent)} ({esc(te.group)})</p><pre>{esc(te.text)}</pre>"
            f"<p><b>요청 범위</b></p><pre>{esc(json.dumps(te.request, ensure_ascii=False))}</pre>"
            f"<p><b>정답</b></p><pre>{esc(json.dumps(g['gold'], ensure_ascii=False))}</pre>"
            f"<h2>need와 결정 필수 조각</h2><table><tr><th>need</th><th>그룹</th><th></th><th>조각</th></tr>{needs}</table>")
    cols = "".join(render_column(name, r.get(wid), hl, crit, names) for name, r in runs.items())
    return (f"<!doctype html><html lang='ko'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(wid)} trace</title><style>{CSS}</style><body>{head}<h2>조건별 타임라인</h2>"
            f"<div class='cols' style='--n:{len(runs)}'>{cols}</div></body></html>")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", type=Path)
    ap.add_argument("--run", action="append", required=True, help="이름=실행 디렉터리[,LLM 캐시]")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--max-day", type=int, default=10)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    tasks, gold, frags, names = load(args.scenario, args.max_day)
    runs = {}
    for spec in args.run:
        name, _, rest = spec.partition("=")
        rd, _, cache = rest.partition(",")
        runs[name] = analyze(Path(rd), Path(cache) if cache else None, tasks, gold, frags, names)
    want = [t for t in args.tasks.split(",") if t] or sorted(gold)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for wid in want:
        (args.out / f"{wid}.html").write_text(render_task(wid, tasks, gold, frags, names, runs), encoding="utf-8")
        summary[wid] = {"template": gold[wid]["template"], "class": gold[wid]["state_class"], "c_ops": gold[wid]["c_ops"],
                        **{n: ({"correct": r[wid]["correct"], "gates": [x["gate"] for x in r[wid]["gates"]],
                                "exhausted": (r[wid]["budget"] or {}).get("budget_exhausted"), "error": r[wid]["error"],
                                "calls": ((r[wid]["budget"] or {}).get("used") or {}).get("calls")} if wid in r else None)
                           for n, r in runs.items()}}
    rows = "".join(f"<tr><td><a href='{w}.html'>{w}</a></td><td>{s['template']}</td><td>{s['class']}{' · C_ops' if s['c_ops'] else ''}</td>"
                   + "".join(f"<td class='{'ok' if (s[n] or {}).get('correct') else 'bad'}'>{'—' if s[n] is None else ('✓' if s[n]['correct'] else '✗') + ' ' + esc(','.join(s[n]['gates']))}</td>" for n in runs)
                   + "</tr>" for w, s in summary.items())
    (args.out / "index.html").write_text(
        f"<!doctype html><html lang='ko'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>Trace index</title><style>{CSS}</style><body><h1>과제 × 조건</h1><table><tr><th>과제</th><th>템플릿</th><th>등급</th>"
        + "".join(f"<th>{esc(n)}</th>" for n in runs) + f"</tr>{rows}</table></body></html>", encoding="utf-8")
    (args.out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(want)} tasks → {args.out}")


if __name__ == "__main__":
    main()
