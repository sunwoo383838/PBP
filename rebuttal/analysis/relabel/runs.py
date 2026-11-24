"""런 목록: run_id → (런 폴더, 시나리오 폴더, 원장 파일, 분석 일수, 표시용 속성)."""
import glob, gzip, json, os
# 경로는 환경변수로 받는다: G2G_RUNS = 실행 폴더(runs/, runs_appx/, runs_g/, scenarios/, scenarios_g/, rebuttal/ 포함),
# GATE_LEDGER = 본 실험 관문 원장 폴더. 리버탈 런 원장은 이 저장소의 ../ledgers/*.json.gz를 쓴다.
M = os.environ["G2G_RUNS"]; RB = M + "/rebuttal"
GL = os.environ["GATE_LEDGER"]
RL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ledgers")
def load_json(f):
    return json.load(gzip.open(f) if f.endswith(".gz") else open(f))
def runs():
    out = []
    for f in sorted(glob.glob(GL + "/*.json")):
        b = os.path.basename(f)[:-5]
        if b.startswith("context"): continue
        exp, cell, model, cond, seed = b.split("__")
        if exp == "main":
            rd, sc, md = f"{M}/runs/{model}/{cond}/{seed}", f"{M}/scenarios/D5_{seed}_T45", 15
        elif exp == "appendix":
            rd, sc, md = f"{M}/runs_appx/{cond}/{seed}", f"{M}/scenarios/D5_{seed}_T45", 10
        else:
            d = "D3" if cell == "D3" else "D5"
            rd, sc, md = f"{M}/runs_g/{cell}/{cond}/{seed}", f"{M}/scenarios_g/{cell}/{d}_{seed}_T45", 10
        out.append(dict(run_id=b, exp=exp, cell=cell, model=model, cond=cond, seed=seed, run_dir=rd, scen=sc, ledger=f, max_day=md))
    for f in sorted(glob.glob(RL + "/[ACD]__*.json.gz")):
        b = os.path.basename(f)[:-8]; p = b.split("__")
        if p[0] == "A":
            cond, seed = p[1], p[2]; model, cell = "qwen3.5-27b", "base"
            rd, sc = f"{RB}/runs/{model}/{cond}/{seed}", f"{M}/scenarios/D5_{seed}_T45"
        elif p[0] == "C":
            model, cond, seed = p[1], p[2], p[3]; cell = "base"
            rd, sc = f"{RB}/runs/{model}/{cond}/{seed}", f"{M}/scenarios/D5_{seed}_T45"
        else:
            cell, cond, seed = p[1], p[2], p[3]; model = "qwen3.5-27b"
            rd, sc = f"{RB}/runs_d/{cell}/{cond}/{seed}", f"{RB}/scenarios_d/{cell}/D5_{seed}_T45"
        out.append(dict(run_id="rebuttal__" + b, exp="rebuttal_" + p[0], cell=cell, model=model, cond=cond, seed=seed, run_dir=rd, scen=sc, ledger=f, max_day=10))
    return out
if __name__ == "__main__":
    rs = runs(); print(len(rs))
    for r in rs:
        ok = os.path.exists(r["run_dir"] + "/wal/events.jsonl") and os.path.exists(r["scen"] + "/private/gold.jsonl")
        if not ok: print("MISSING", r)
