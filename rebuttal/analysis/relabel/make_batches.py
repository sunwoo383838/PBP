"""재판정 대상 고르기와 묶음 파일 만들기.
대상: (1) respond·select·observe.window·계산값 전달 need가 있는 과제 전부, (2) observe.search need가 있는 과제 전부,
(3) 나머지 과제 가운데 무작위 300(대조), (4) (1) 가운데 무작위 120은 다른 묶음에 한 번 더(판정 일관성)."""
import json, random, collections
from pathlib import Path
B = Path(__file__).resolve().parent; cs = [json.loads(l) for l in open(B / "out/cases.jsonl")]
HOT = ("L_respond", "L_select", "L_observe.window", "ok_comp")
kind = lambda c: "hot" if any(g in c["gates"] for g in HOT) else "search" if "L_observe.search" in c["gates"] else "cold"
rng = random.Random(1)
hot = [c for c in cs if kind(c) == "hot"]; search = [c for c in cs if kind(c) == "search"]; cold = [c for c in cs if kind(c) == "cold"]
sel = hot + search + rng.sample(cold, 300); rng.shuffle(sel)
dup = rng.sample(hot, 120)
def pack(cases, file_cap=45000, batch_cap=500000):
    files, cur, n = [], [], 0
    for c in cases:
        if cur and n + c["chars"] > file_cap: files.append(cur); cur, n = [], 0
        cur.append(c); n += c["chars"]
    if cur: files.append(cur)
    batches, cur, n = [], [], 0
    for f in files:
        s = sum(c["chars"] for c in f)
        if cur and n + s > batch_cap: batches.append(cur); cur, n = [], 0
        cur.append(f); n += s
    if cur: batches.append(cur)
    return batches
index = []
main_b = pack(sel); dup_b = pack(dup)
for bi, batch in enumerate(main_b + dup_b, 1):
    d = B / "batches" / f"b{bi:03d}"; d.mkdir(parents=True, exist_ok=True)
    for fi, f in enumerate(batch, 1):
        (d / f"part_{fi:03d}.md").write_text("\n\n".join(f"# CASE {c['case']}\n{c['text']}" for c in f) + "\n", encoding="utf-8")
        for c in f:
            index.append({"batch": f"b{bi:03d}", "part": f"part_{fi:03d}", "case": c["case"], "run_id": c["run_id"], "task_id": c["task_id"],
                          "kind": kind(c), "dup": bi > len(main_b), "frags": c["frags"], "computed": c["computed"]})
    print(f"b{bi:03d}", len(batch), "files", sum(len(f) for f in batch), "cases", sum(c["chars"] for f in batch for c in f) // 1000, "k chars", "(dup)" if bi > len(main_b) else "")
json.dump(index, open(B / "index.json", "w"))
print(len(sel), "cases +", len(dup), "dup;", sum(len(c["frags"]) for c in sel), "records;", sum(len(c["computed"]) for c in sel), "computed")
