"""판정 파일(.tsv) 모으기와 검사: 누락·중복·잘못된 값·인용이 실제 메시지에 있는지. 출력 verdicts.json, 문제 목록 problems.json.
    python collect.py [--strict]"""
import json, re, sys, collections
from pathlib import Path
B = Path(__file__).resolve().parent
index = json.load(open(B / "index.json"))
cases = {}
for l in open(B / "out/cases.jsonl"):
    c = json.loads(l); cases[c["case"]] = c
def blocks(text):
    out = {}
    for b in re.split(r"\n(?=\[[MI]\d+\] )", text):
        m = re.match(r"\[([MI]\d+)\] ", b)
        if m: out[m.group(1)] = b.split("\n", 1)[1] if "\n" in b else ""        # 머리줄(질문)은 뺀다
    return out
sq = lambda s: re.sub(r"\s+", " ", s).strip().lower()
REC, INS, COMP = {"current", "stale", "partial", "no"}, {"current", "stale", "partial", "no", "na"}, {"yes", "no"}
V = collections.defaultdict(lambda: collections.defaultdict(lambda: {"F": {}, "C": {}}))      # 본 판정
D = collections.defaultdict(lambda: {"F": {}, "C": {}})                                          # 중복 판정 (case별)
fixed = []; problems = []; done = collections.Counter(); qbad = collections.Counter(); qtot = collections.Counter()
by_part = collections.defaultdict(list)
for x in index: by_part[(x["batch"], x["part"])].append(x)
for (b, p), xs in sorted(by_part.items()):
    f = B / "batches" / b / (p + ".tsv")
    if not f.exists():
        done["missing_file"] += 1; continue
    done["files"] += 1
    want = {("F", x["case"], fid) for x in xs for fid in x["frags"]} | {("C", x["case"], n) for x in xs for n in x["computed"]}
    got = {}
    for ln, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        t = ["" if s.strip() == "-" else s.strip() for s in line.split("\t")]
        t[2] = t[2].strip("`")
        if t[0] == "C" and ("C", t[1], t[2]) not in want:              # need 대신 항목 이름을 적은 줄: 같은 과제의 need 가운데 이름이 든 것 하나로
            lab = t[2].split(" / ")[0].strip()
            m = [n for (kk, cc, n) in want if kk == "C" and cc == t[1] and lab and lab in n.split("/")]
            if len(m) == 1: t[2] = m[0]; fixed.append((b, p, ln, lab, m[0]))
        k = tuple(t[:3])
        if k not in want: problems.append((b, p, ln, "unknown key", line[:120])); continue
        if k in got:
            if t[0] == "C":                                                 # 계산값이 여럿인 need: 모두 yes여야 yes
                if t[3].lower() == "no": got[k]["computed"] = "no"
            elif t[3].lower() != got[k]["received"]: problems.append((b, p, ln, "duplicate, different", line[:120]))
            continue
        cb = blocks(cases[t[1]]["text"])
        def quote_ok(label, q):
            qtot[t[0]] += 1
            ok = label in cb and sq(q) and sq(q) in sq(cb[label])
            if not ok: qbad[t[0]] += 1
            return ok
        if t[0] == "F":
            t += [""] * (10 - len(t))
            if t[6].lower() not in INS and t[6] and not any(t[7:]):            # 빈 칸이 빠져 메모가 앞으로 당겨진 줄
                t[9], t[6] = t[6], ""
            rec, ins = t[3].lower(), t[6].lower() or "na"
            if rec not in REC or ins not in INS: problems.append((b, p, ln, "bad label", line[:120])); continue
            r = {"received": rec, "inside": ins, "note": t[9], "m": t[4], "i": t[7]}
            if rec != "no": r["quote_ok"] = quote_ok(t[4], t[5]); r["quote"] = t[5]
            if ins not in ("no", "na"): r["iquote_ok"] = quote_ok(t[7], t[8]); r["iquote"] = t[8]
            if rec != "no" and not r["quote_ok"]: problems.append((b, p, ln, "quote not found", line[:200]))
            if ins not in ("no", "na") and not r["iquote_ok"]: problems.append((b, p, ln, "inside quote not found", line[:200]))
            got[k] = r
        else:
            t += [""] * (7 - len(t))
            if t[3].lower() == "no" and t[4] and not t[4].startswith("M"): t[6], t[4] = t[4], ""
            c = t[3].lower()
            if c not in COMP: problems.append((b, p, ln, "bad label", line[:120])); continue
            r = {"computed": c, "m": t[4], "note": t[6]}
            if c == "yes":
                r["quote_ok"] = quote_ok(t[4], t[5]); r["quote"] = t[5]
                if not r["quote_ok"]: problems.append((b, p, ln, "quote not found", line[:200]))
            got[k] = r
    for k in want - set(got): problems.append((b, p, 0, "missing decision", "\t".join(k)))
    cmeta = {x["case"]: x for x in xs}
    for (kind, case, key), r in got.items():
        x = cmeta[case]
        tgt = D[case] if x["dup"] else V[x["run_id"]][x["task_id"]]
        tgt[kind][key] = r if kind == "F" else r["computed"]
        if kind == "C" and not x["dup"]: V[x["run_id"]][x["task_id"]].setdefault("Cq", {})[key] = r
    done["decisions"] += len(got); done["wanted"] += len(want)
json.dump(V, open(B / "verdicts.json", "w"), ensure_ascii=False)
json.dump(D, open(B / "verdicts_dup.json", "w"), ensure_ascii=False)
json.dump(problems, open(B / "problems.json", "w"), ensure_ascii=False, indent=0)
json.dump(fixed, open(B / "fixed_keys.json", "w"), ensure_ascii=False, indent=0)
print(dict(done), "quotes", dict(qtot), "not found", dict(qbad), "problems", collections.Counter(p[3] for p in problems), "relabelled C keys", len(fixed))
