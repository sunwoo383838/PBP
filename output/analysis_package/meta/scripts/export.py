"""중간 결과 내보내기: output/에 CSV(표별 + 과제 단위 원자료)와 Markdown 보고서."""
import csv, json, sys, random, time
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "/root/project/g2g_main")
import summary as S                                                       # rows/table/acc/boot 재사용
M = S.M; OUT = Path("/root/project/g2g/output"); OUT.mkdir(exist_ok=True)
C4, SEEDS = S.C4, S.SEEDS
asof = time.strftime("%Y-%m-%d %H:%M")
def w(name, header, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)
def r2(x): return f"{x:.3f}"
md = [f"# g2g 본 실험 최종 결과", "", f"기준 시각: {asof} (모든 런 완료: 1차 15일, G 셀·부록 10일)", "",
      "- 지표: 답 전체 정확 일치(exact). 원리상 풀 수 없는 과제(unreachable_local) 제외.",
      "- 비교: 같은 셀·모델·시드에서 비교하는 조건이 모두 답한 공통 과제만.",
      "- 일수 상한: 1차 기준 셀 1~15일, G 셀·부록 1~10일.",
      "- 구간: ingress−direct, 과제 단위 짝 부트스트랩 95% (2000회).", ""]
# 1 모델
rows = []
md += ["## 1. 1차 기준 셀 D5·R2 (1~15일)", "", "| 모델 | 과제 수 | direct | routing | ingress | full_load | ingress−direct [95%] |", "|---|---|---|---|---|---|---|"]
for model in ("qwen3.5-27b", "qwen3.5-9b", "deepseek-v4-flash"):
    R, com = S.table("base", model, C4, 15); g = S.boot(R, com, "ingress", "direct"); a = [S.acc(R, com, c)[0] for c in C4]
    rows.append([model, len(com), *map(r2, a), r2(g[0]), r2(g[1]), r2(g[2])])
    md.append(f"| {model} | {len(com)} | " + " | ".join(f"{x:.2f}" for x in a) + f" | {g[0]:+.2f} [{g[1]:+.2f}, {g[2]:+.2f}] |")
w("1_main_by_model.csv", ["model", "n_tasks", *C4, "gap_ingress_direct", "ci_low", "ci_high"], rows)
md += ["", "DeepSeek-V4-Flash 런은 다른 세션이 실행.", ""]
# 2 G 셀
G = {"R1": 5, "D3": 6, "base": 10, "R3": 15}; rows = []
md += ["## 2. G 셀 (27B, 1~10일)", "", "| 셀 | 그룹 수 | 과제 수 | direct | routing | ingress | full_load | ingress−direct [95%] |", "|---|---|---|---|---|---|---|---|"]
for cell in ("R1", "D3", "base", "R3"):
    R, com = S.table(cell, "qwen3.5-27b", C4, 10); g = S.boot(R, com, "ingress", "direct"); a = [S.acc(R, com, c)[0] for c in C4]
    rows.append([cell, G[cell], len(com), *map(r2, a), r2(g[0]), r2(g[1]), r2(g[2])])
    md.append(f"| {cell} | {G[cell]} | {len(com)} | " + " | ".join(f"{x:.2f}" for x in a) + f" | {g[0]:+.2f} [{g[1]:+.2f}, {g[2]:+.2f}] |")
w("2_gcell_27b.csv", ["cell", "n_groups", "n_tasks", *C4, "gap_ingress_direct", "ci_low", "ci_high"], rows)
# 3 부록
A = C4 + ["direct_relay", "retrieve", "sidecar"]
R, com = S.table("base", "qwen3.5-27b", A, 10); rows = []
md += ["", f"## 3. 부록 (27B 기준 셀, 1~10일, 7조건 공통 {len(com)}과제)", "",
       "| 조건 | 전체 | A | B | C | D | C_ops |", "|---|---|---|---|---|---|---|"]
for c in A:
    v = [S.acc(R, com, c)[0]] + [S.acc(R, com, c, lambda r, k=k: r["cls"] == k)[0] for k in "ABCD"] + [S.acc(R, com, c, lambda r: r["cops"])[0]]
    rows.append([c, *map(r2, v)])
    md.append(f"| {c} | " + " | ".join(f"{x:.2f}" for x in v) + " |")
w("3_appendix_27b.csv", ["condition", "all", "A", "B", "C", "D", "c_ops"], rows)
md += ["", "모든 부록 런 완료(1~10일).", ""]
# 4 층화
pool = []
for cell, mdays in (("base", 15), ("R1", 10), ("D3", 10), ("R3", 10)):
    R4, com4 = S.table(cell, "qwen3.5-27b", C4, mdays); pool.append((cell, R4, com4))
rows = []; md += ["## 4. 27B 과제 유형별 (기준 셀 15일 + G 셀 10일 합산)", ""]
for name, keyf, vals in (("상태 등급", "cls", list("ABCD")), ("C_ops", "cops", [False, True]), ("걸린 그룹 수", "ng", [2, 3, 4, 5])):
    md += [f"**{name}**", "", "| 값 | n | direct | routing | ingress | full_load | ingress−direct |", "|---|---|---|---|---|---|---|"]
    for v in vals:
        r = {}
        for c in C4:
            xs = [R4[(c, s)][wid]["ok"] for _, R4, com4 in pool for s, wid in com4 if R4[(c, s)][wid][keyf] == v]
            r[c] = (sum(xs) / len(xs) if xs else float("nan"), len(xs))
        rows.append([name, v, r["direct"][1], *(r2(r[c][0]) for c in C4), r2(r["ingress"][0] - r["direct"][0])])
        md.append(f"| {v} | {r['direct'][1]} | " + " | ".join(f"{r[c][0]:.2f}" for c in C4) + f" | {r['ingress'][0]-r['direct'][0]:+.2f} |")
    md.append("")
w("4_strata_27b.csv", ["stratum", "value", "n_tasks", *C4, "gap_ingress_direct"], rows)
# 5 과제 단위 원자료 (모든 런, 일수 상한 적용)
long = []
specs = [("base", m, C4, 15) for m in ("qwen3.5-27b", "qwen3.5-9b", "deepseek-v4-flash")] + \
        [(c, "qwen3.5-27b", C4, 10) for c in ("R1", "D3", "R3")] + [("base", "qwen3.5-27b", ["direct_relay", "retrieve", "sidecar"], 10)]
for cell, model, conds, mdays in specs:
    for c in conds:
        for s in SEEDS:
            for wid, x in S.rows(S.run_of(cell, model, c, s), S.sc_of(cell, s), mdays).items():
                long.append([cell, model, c, s, wid, int(x["ok"]), x["cls"], int(x["cops"]), x["ng"], x["tpl"]])
w("5_task_level.csv", ["cell", "model", "condition", "seed", "task_id", "exact", "state_class", "c_ops", "n_groups", "template"], long)
md += ["## 파일", "", "- 1_main_by_model.csv, 2_gcell_27b.csv, 3_appendix_27b.csv, 4_strata_27b.csv: 위 표",
       f"- 5_task_level.csv: 과제 단위 원자료 {len(long)}행 (셀·모델·조건·시드·과제·정답 여부·등급·C_ops·걸린 그룹 수·템플릿, 공통 과제로 거르기 전)"]
(OUT / "results_final.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(sorted(p.name for p in OUT.iterdir())), len(long))
