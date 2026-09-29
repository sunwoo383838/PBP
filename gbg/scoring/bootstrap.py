"""짝지은 부트스트랩 (채점기, 오프라인). 같은 세계(world_hash = 시나리오)에서 돈 두 조건의 과제별 결과를 짝지어 차이의 95% CI.

재표집: 바깥 단위 = 독립 시드(시나리오), 세계 안에서는 연속 날짜 블록(기본 5일)을 복원 추출한다. 난수는 NamedRNG의
이름 붙은 흐름으로 결정적이다 (전역 random 금지).
동등성(차이 CI가 ±margin 안)과 비열등(차이 CI 하한이 −margin 이상) 판정 함수 포함.
"""
from collections import defaultdict

from gbg.kernel.rng import NamedRNG


def paired(rows: list[dict], a: str, b: str, metric: str = "exact", block_days: int = 5, n_boot: int = 2000,
           seed_name: str = "bootstrap") -> dict:
    """rows: {"world", "task_id", "day", "condition", metric}. 두 조건 모두에 있는 과제만 짝짓는다.
    차이 = b − a (과제 평균)."""
    by = defaultdict(dict)
    for r in rows:
        by[(r["world"], r["task_id"])][r["condition"]] = r
    pairs = [(w, t, float(x[b][metric]) - float(x[a][metric]), x[a]["day"]) for (w, t), x in by.items() if a in x and b in x]
    if not pairs:
        return {"n": 0}
    worlds: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for w, _, d, day in pairs:
        worlds[w][(day - 1) // block_days].append(d)
    wl = sorted(worlds)
    rng = NamedRNG(0).stream(seed_name, a, b, metric)
    est = sum(d for *_, d, _ in pairs) / len(pairs)
    boots = []
    for _ in range(n_boot):
        vals = []
        for _w in range(len(wl)):
            blocks = worlds[wl[rng.randrange(len(wl))]]
            keys = sorted(blocks)
            for _k in range(len(keys)):
                vals += blocks[keys[rng.randrange(len(keys))]]
        boots.append(sum(vals) / len(vals))
    boots.sort()
    lo, hi = boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1]
    return {"n": len(pairs), "worlds": len(wl), "diff": round(est, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "a": a, "b": b, "metric": metric}


def equivalent(res: dict, margin: float) -> bool:
    return bool(res.get("n")) and -margin <= res["ci95"][0] and res["ci95"][1] <= margin


def noninferior(res: dict, margin: float) -> bool:
    """b가 a보다 margin 이상 나쁘지 않다."""
    return bool(res.get("n")) and res["ci95"][0] >= -margin
