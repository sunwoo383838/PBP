"""Table 12 경계 지표: Π·ρ (정확 일치, numbers.json) + δ·λ·υ (손실 원장, numbers3.json, 진단용).
δ = 모든 손실 고리를 통과해 현재 버전으로 전달된 need 비율(= 원장 ok), λ = 1 − δ, υ = 결정 필수 기록이 모두 전달된 과제의 정확도.
Full-load(π≡1)는 원장 지표를 보고하지 않는다(§3 틀 밖). 출력: tables/t12_boundary_metrics.tex, numbers5_metrics.json"""
import json
from pathlib import Path
OUT = Path("/root/project/g2g/output/paper")
N = json.load(open(OUT / "numbers.json")); N3 = json.load(open(OUT / "numbers3.json"))
C4 = ["direct", "routing", "ingress", "full_load"]; CN = {"direct": "Direct", "routing": "Routing", "ingress": "Ingress", "full_load": "Full-load"}
MN = {"qwen3.5-27b": "Qwen3.5-27B", "deepseek-v4-flash": "DeepSeek-V4-Flash", "qwen3.5-9b": "Qwen3.5-9B"}
rows, M = [], {}
for m in MN:
    bc = N["main"][m]["by_class"]; nN = sum(bc[k]["n"] for k in "BCD"); psp_d = None; M[m] = {}
    for c in C4:
        accA = bc["A"]["acc"][c]; accN = sum(bc[k]["n"] * bc[k]["acc"][c] for k in "BCD") / nN
        psp = accA - accN; psp_d = psp if c == "direct" else psp_d; rho = 1 - psp / psp_d
        led = N3["ledger"][m][c]; cov = N3["coverage"].get(m, {}).get(c, {}).get("1", {}).get("acc")
        diag = c != "full_load"
        bdr = led["loss"]["ok"] if diag else None
        M[m][c] = {"acc": N["main"][m]["acc"][c], "accA": accA, "acc_notA": accN, "psp": psp, "pr": rho,
                   "bdr": bdr, "transit": (1 - bdr) if diag else None, "use": cov if diag else None}
        f = lambda v: f"{v*100:.0f}" if v is not None else "--"
        rows.append(f"{MN[m] if c == 'direct' else ''} & {CN[c]} & {N['main'][m]['acc'][c]*100:.1f} & {accA*100:.1f} & {accN*100:.1f} & {psp*100:.1f} & {rho*100:+.0f}\\% & "
                    f"{f(M[m][c]['bdr'])} & {f(M[m][c]['transit'])} & {f(M[m][c]['use'])} \\\\")
    rows.append(r"\midrule")
rows[-1] = r"\bottomrule"
tex = "\n".join(["% Pi, rho: exact-match over gold labels (headline). delta, lambda, upsilon: heuristic loss ledger, diagnostic only (Sec. 5.4, 6.9); not reported for Full-load (no partition).",
                 r"\begin{tabular}{ll r rr r r r r r}", r"\toprule",
                 r"Backbone & Condition & Acc & $\mathrm{Acc}_A$ & $\mathrm{Acc}_{\bar A}$ & $\Pi$ (pp) & $\rho$ & $\delta$ (\%) & $\lambda$ (\%) & $\upsilon$ (\%) \\", r"\midrule", *rows, r"\end{tabular}"])
(OUT / "tables" / "t12_boundary_metrics.tex").write_text(tex, encoding="utf-8")
json.dump(M, open(OUT / "numbers5_metrics.json", "w"), indent=1)
for m in MN: print(m, {c: (round(v["psp"]*100, 1), round(v["pr"]*100), v["bdr"] and round(v["bdr"]*100), v["use"] and round(v["use"]*100)) for c, v in M[m].items()})
