"""Stage 4 수용 기준 (하이브리드 검색).

1. 같은 입력이면 증거 블록이 바이트 동일 (임베딩은 캐시에서).
2. 회수율: H0·H1 90% 이상 (하이브리드). H2는 문맥 확장으로 닿는 비율을 보고만 함.
3. 한국어·일본어 별칭 변형 테스트 세트에서 별칭 해소 정확도 95% 이상.
4. 그룹 경계 밖 항목이 결과에 절대 섞이지 않음 (접근 가드 통과).

테스트 임베더는 API 없는 결정적 HashEmbedder다. 실제 bge-m3 검증은 GBG_LIVE=1일 때만 돈다.
"""
import asyncio
import json
import os
from pathlib import Path

import pytest

from gbg.contracts.access import load_access
from gbg.contracts.conditions import load_conditions
from gbg.contracts.params import load_params
from gbg.kernel.access_guard import AccessGuard
from gbg.retrieval.alias import AliasResolver, edit_distance
from gbg.retrieval.bm25 import BM25Index, tokenize
from gbg.retrieval.embed import CachedEmbedder, DeepInfraEmbedder, EmbeddingCache, EmbeddingMiss, HashEmbedder
from gbg.retrieval.eval_recall import build_cases, evaluate
from gbg.retrieval.evidence import build_evidence
from gbg.retrieval.hybrid import GroupRetriever, RetrievalDenied, authorize
from gbg.retrieval.normalize import normalize, strip_honorifics
from gbg.stores import Stores
from gbg.tests.support import FIXTURES, load_adapter

ROOT = Path(__file__).resolve().parents[2]
P = load_params(ROOT / "configs" / "params.yaml")
RP = P.retrieval


def stores():
    return Stores.from_adapter(load_adapter("worldgen_mini"), card_mode="static", rounds_per_day=3)


def retriever(s, group, embedder=None, params=RP):
    return GroupRetriever(s, group, embedder or HashEmbedder(), params)


def run(coro):
    return asyncio.run(coro)


# ─────────────────────────── 정규화 · 토큰 ───────────────────────────
def test_normalize():
    assert normalize("ＣＭＴ－００００１  잔액 ２，４１７，９００") == "cmt-00001 잔액 2417900"
    assert strip_honorifics("하린 과장님") == "하린" and strip_honorifics("佐藤様") == "佐藤"
    assert strip_honorifics("Mr. Tan Wei") == "tan wei" and strip_honorifics("Tan (mgr)") == "tan"
    assert strip_honorifics("과장") == "과장", "전부 경칭이면 그대로"


def test_tokenize_has_words_bigrams_and_whole_ids_amounts():
    toks = tokenize("CMT-00001 영업1팀 equipment KRW 612,300 営業課")
    for t in ("cmt-00001", "612300", "equipment", "krw", "영업", "업1", "1팀", "営業", "業課"):
        assert t in toks, t


def test_bm25_prefers_rarer_matching_terms():
    ix = BM25Index()
    for i, t in enumerate(["budget line 영업1팀", "budget line 개발1팀", "CMT-00001 provisional approval 영업1팀"]):
        ix.add(i, t)
    s = ix.scores("CMT-00001")
    assert list(s) == [2]
    s = ix.scores("영업1팀 budget")
    assert s[0] > s[1] and s[0] > s[2]


# ─────────────────────────── 1. 결정론 ───────────────────────────
def test_evidence_is_byte_identical_and_uses_cache(tmp_path):
    cache = EmbeddingCache(tmp_path / "emb.sqlite")
    live = CachedEmbedder(HashEmbedder(), cache, "LIVE")
    ev1 = run(build_evidence(retriever(stores(), "FIN-SEL", live), "영업1팀 available budget", ["영업1팀"]))
    assert live.computed > 0
    replay = CachedEmbedder(HashEmbedder(), cache, "REPLAY")
    ev2 = run(build_evidence(retriever(stores(), "FIN-SEL", replay), "영업1팀 available budget", ["영업1팀"]))
    assert replay.computed == 0
    assert ev1.text == ev2.text and json.dumps(ev1.log, sort_keys=True) == json.dumps(ev2.log, sort_keys=True)
    assert ev1.items and ev1.text.startswith("[E1] ")


def test_replay_miss_is_fatal(tmp_path):
    replay = CachedEmbedder(HashEmbedder(), EmbeddingCache(tmp_path / "emb.sqlite"), "REPLAY")
    with pytest.raises(EmbeddingMiss):
        run(build_evidence(retriever(stores(), "FIN-SEL", replay), "x", []))


# ─────────────────────────── 2. 회수율 ───────────────────────────
def _recall_report(embedder=None):
    s = stores()
    priv = FIXTURES / "worldgen_mini" / "private"
    gold = [json.loads(x) for x in (priv / "gold.jsonl").read_text(encoding="utf-8").splitlines()]
    frags = {f["fid"]: f for f in map(json.loads, (priv / "fragments.jsonl").read_text(encoding="utf-8").splitlines())}
    cases, skipped = build_cases(gold, frags)
    rets = {g: retriever(s, g, embedder) for g in {c.group for c in cases}}
    return run(evaluate(rets, cases)), skipped


def test_recall_h0_h1_at_least_90_percent():
    """90% 기준은 정확 조회(색인 + catalog 한 단계)에 적용한다. H2는 보고만."""
    report, skipped = _recall_report()
    idx = report["modes"]["index"]
    assert report["cases"] >= 5 and set(idx["by_disc"]) >= {"H0", "H1", "H2"}
    for disc in ("H0", "H1"):
        assert idx["by_disc"][disc]["recall"] >= 0.9, (disc, idx["by_disc"][disc])
    assert {"hybrid", "bm25"} <= set(report["modes"]) and report["modes"]["hybrid"]["by_day"]


def test_h2_antecedent_reached_by_context_expansion():
    s = stores()
    s.history.add("fin-sel.a3", 0, "assistant", "CMT-00077 영업1팀 equipment review started.", ["CMT-00077", "영업1팀"], "d")
    s.history.add("fin-sel.a3", 0, "assistant", "Hold that one until Friday.", [], "d")          # 지시어 발화
    ev = run(build_evidence(retriever(s, "FIN-SEL"), "CMT-00077", ["CMT-00077"], mode="bm25"))
    texts = {it.text: it.source for it in ev.items}
    assert texts["Hold that one until Friday."] == "context"


# ─────────────────────────── 3. 별칭 해소 ───────────────────────────
ALIAS_CASES = {
    "HR-SEL": [
        ("김하린", "E-SEL-1000"), ("하린 과장", "E-SEL-1000"), ("하린 과장님", "E-SEL-1000"), ("하린과장", "E-SEL-1000"),
        ("김하린씨", "E-SEL-1000"), ("김 하린", "E-SEL-1000"), ("김하린 과장", "E-SEL-1000"),
        ("박도윤", "E-SEL-1001"), ("도윤대리", "E-SEL-1001"), ("박도윤 대리님", "E-SEL-1001"),
        ("이서준 선임", "E-SEL-1002"), ("서준", "E-SEL-1002"), ("최지우 과장", "E-SEL-1003"), ("최지유", "E-SEL-1003"),
        ("E-SEL-1000", "E-SEL-1000"), ("e-sel-1001", "E-SEL-1001"), ("Ｅ－ＳＥＬ－１００２", "E-SEL-1002"),
        ("영업1팀", "영업1팀"), ("영업 1팀", "영업1팀"), ("영업１팀", "영업1팀"), ("개발1팀", "개발1팀"),
        ("홍길동", None), ("개발2팀", None), ("E-SEL-1009", None),
    ],
    "HR-TYO": [
        ("佐藤さん", "E-TYO-1000"), ("佐藤様", "E-TYO-1000"), ("佐藤 結衣", "E-TYO-1000"), ("佐藤結衣さん", "E-TYO-1000"),
        ("小野さま", "E-TYO-1001"), ("小野健さん", "E-TYO-1001"), ("田中翔様", "E-TYO-1002"), ("高橋美咲", "E-TYO-1003"),
        ("髙橋美咲", "E-TYO-1003"), ("営業１課", "営業1課"), ("開発1課", "開発1課"), ("ｅ－ｔｙｏ－１００３", "E-TYO-1003"),
        ("鈴木さん", None), ("開発2課", None),
    ],
}


ALIAS_TABLES = {
    "HR-SEL": {"E-SEL-1000": ["김하린", "하린 과장"], "E-SEL-1001": ["박도윤", "도윤 대리"], "E-SEL-1002": ["이서준", "서준 선임"],
               "E-SEL-1003": ["최지우", "지우 과장"], "영업1팀": ["영업1팀"], "개발1팀": ["개발1팀"]},
    "HR-TYO": {"E-TYO-1000": ["佐藤結衣", "佐藤さん"], "E-TYO-1001": ["小野健", "小野さん"], "E-TYO-1002": ["田中翔", "田中さん"],
               "E-TYO-1003": ["高橋美咲", "高橋さん"], "営業1課": ["営業1課"], "開発1課": ["開発1課"]},
}


def test_alias_resolution_accuracy_at_least_95_percent():
    total = correct = 0
    wrong = []
    for group, cases in ALIAS_CASES.items():
        r = AliasResolver(ALIAS_TABLES[group], embedder=HashEmbedder(), embed_threshold=RP.alias.embed_threshold,
                          max_edit=RP.alias.max_edit)
        for text, want in cases:
            got = run(r.resolve(text)).entities
            ok = got == ((want,) if want else ())
            total, correct = total + 1, correct + ok
            if not ok:
                wrong.append((text, want, got))
    assert total >= 35 and correct / total >= 0.95, wrong


def test_ids_are_never_fuzzy_matched():
    assert edit_distance("e-sel-1000", "e-sel-1001", 2) == 1
    r = AliasResolver({"E-SEL-1000": ["김하린"]})
    assert r.resolve_sync("E-SEL-1001").entities == ()


def test_tagging_uses_alias_resolution():
    a = load_adapter("worldgen_mini")
    assert a.tag("HR-SEL", "Please check 하린 과장님's grade.") == ["E-SEL-1000"]
    assert a.tag("HR-TYO", "佐藤様の件") == ["E-TYO-1000"]
    assert a.tag("FIN-SEL", "CMT-00001 영업1팀") == ["CMT-00001", "영업1팀"], "catalog id와 부서도 태깅된다"
    assert a.tag("HR-SEL", "nothing here") == []


# ─────────────────────────── 4. 그룹 경계 ───────────────────────────
def test_results_never_cross_group_boundary():
    s = stores()
    hr_agents = {a for a, (g, _) in s.members.items() if g.startswith("HR-")}
    for q, ents in [("김하린 HR record grade", ["E-SEL-1000"]), ("영업1팀 capex balance", ["영업1팀"]), ("transfer 박도윤", [])]:
        ev = run(build_evidence(retriever(s, "FIN-SEL"), q, ents))
        assert all(it.agent.startswith("fin-sel.") for it in ev.items), q
        assert not hr_agents & {c["agent"] for c in ev.log["candidates"]}


def test_retrieval_authorization_follows_access_table():
    conds = load_conditions(ROOT / "configs" / "conditions.yaml")
    access = load_access(ROOT / "configs" / "access.yaml", conds)
    for cond in ("routing", "routing_reveal", "ingress_read", "ingress_sel", "ingress", "i_e"):   # 경계 조건 모두 같은 검색
        guard = AccessGuard(access, cond)
        assert authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "FIN-SEL")["allowed"]
        with pytest.raises(RetrievalDenied):
            authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "HR-SEL")
    for cond in conds:
        guard = AccessGuard(access, cond)
        with pytest.raises(RetrievalDenied):
            authorize(guard, "agent:fin-sel.a1", "FIN-SEL", "FIN-SEL")             # 에이전트는 그룹 이력 불가


# ─────────────────────────── 조립 규칙 ───────────────────────────
def test_no_version_pruning_and_cap():
    """조회 단계는 버전을 고르지 않는다 (버전 선택은 Ingress 게이트웨이 LLM의 L_state 결정). 상한만 적용한다."""
    s = stores()
    for i in range(5):
        s.history.add("fin-sel.a1", i + 1, "assistant", f"영업1팀 available budget update {i}.", ["영업1팀"], "d")
    ev = run(build_evidence(retriever(s, "FIN-SEL"), "영업1팀 available budget", ["영업1팀"]))
    updates = [it.text for it in ev.items if "budget update" in it.text]
    assert updates == [f"영업1팀 available budget update {i}." for i in range(5)]
    assert "attr" not in ev.log
    small = RP.model_copy(update={"evidence_cap": 60})
    ev = run(build_evidence(retriever(s, "FIN-SEL", params=small), "영업1팀 available budget", ["영업1팀"]))
    assert ev.cap_reached and ev.tokens <= 60 and ev.log["cap_reached"]
    assert ev.items and ev.items[-1].day == max(it.day for it in ev.items), "오래된 것부터 뺀다"


# ─────────────────────────── 실제 bge-m3 (선택) ───────────────────────────
@pytest.mark.skipif(os.environ.get("GBG_LIVE") != "1", reason="GBG_LIVE=1일 때만 DeepInfra 임베딩을 부른다")
def test_real_bge_m3(tmp_path):
    emb = CachedEmbedder(DeepInfraEmbedder(P.llm, RP.embed_model), EmbeddingCache(tmp_path / "emb.sqlite"), "LIVE")
    report, _ = _recall_report(emb)
    hy = report["modes"]["hybrid"]
    for disc in ("H0", "H1"):
        assert hy["by_disc"][disc]["recall"] >= 0.9
    total = correct = 0
    for group, cases in ALIAS_CASES.items():
        r = AliasResolver(ALIAS_TABLES[group], embedder=emb, embed_threshold=RP.alias.embed_threshold)
        for text, want in cases:
            total += 1
            correct += run(r.resolve(text)).entities == ((want,) if want else ())
    assert correct / total >= 0.95


def test_exact_lookup_expands_one_catalog_hop():
    """정확 조회 = 색인 + catalog 한 단계 연결 (라우터와 게이트웨이 공통)."""
    from gbg.retrieval.lookup import expand, index_lookup
    s = stores()
    s.catalog.upsert("FIN-SEL", "commits/CMT-00004", {"commit_id": "CMT-00004", "department": "개발1팀", "item": "laptop"})
    links = RP.catalog_link_fields
    assert expand(s, "FIN-SEL", ["개발1팀"], links) == ["개발1팀", "CMT-00004", "laptop"], "부서 → 그 부서의 가승인"
    assert expand(s, "FIN-SEL", ["CMT-00001"], links) == ["CMT-00001", "영업1팀", "laptop"], "가승인 → 부서·품목"
    lk = index_lookup(s, "FIN-SEL", ["개발1팀"], links)
    assert "fin-sel.a3" in lk.holders and any("2,417,900" in x.text for x in lk.journal)
    assert expand(s, "HR-SEL", ["개발1팀"], links) == ["개발1팀"], "다른 그룹 catalog는 쓰지 않는다"


def test_exact_lookup_matches_index_keys_not_text():
    """4.4: 색인 항목은 entities 목록을 키로 갖고, 정확 조회는 이 키로만 맞춘다 (원문 언급은 쓰지 않는다)."""
    from gbg.contracts.schemas import IndexEntry
    from gbg.retrieval.lookup import index_lookup
    s = stores()
    s.index.add("FIN-SEL", "journal", IndexEntry(day=5, agent="fin-sel.a4", text="Transfer approved from Sales Team 1.",
                                                 entities=["E-SEL-1009", "영업1팀"]))
    s.index.add("FIN-SEL", "journal", IndexEntry(day=5, agent="fin-sel.a5", text="영업1팀 mentioned without key."))
    assert "fin-sel.a4" in s.index.holders("FIN-SEL", "E-SEL-1009") and "fin-sel.a4" in s.index.holders("FIN-SEL", "영업1팀")
    lk = index_lookup(s, "FIN-SEL", ["영업1팀"], [])
    texts = [x.text for x in lk.journal]
    assert "Transfer approved from Sales Team 1." in texts and "영업1팀 mentioned without key." not in texts
    assert "fin-sel.a5" not in lk.holders


def test_recall_criterion_is_dev_seed_mean():
    """H0·H1 기준은 개발 시드 평균 0.9 이상. H2는 보고만 한다."""
    from gbg.cli.retrieval_eval import criterion
    rep = lambda h0, h1, h2: {"modes": {"index": {"by_disc": {"H0": {"recall": h0}, "H1": {"recall": h1},
                                                              "H2": {"recall": h2}}}}}
    c = criterion([rep(0.95, 0.88, 0.1), rep(0.87, 0.94, 0.0)])
    assert c["mean"] == {"H0": 0.91, "H1": 0.91, "H2": 0.05} and c["pass"]
    assert not criterion([rep(0.95, 0.88, 1.0)])["pass"]


def test_eval_seed_runs_only_with_frozen_retrieval_config(tmp_path):
    """평가 시드는 동결된 조회 설정 해시와 같을 때만 실행한다. 개발 시드·픽스처는 제한 없음."""
    import shutil
    from gbg.contracts.freeze import FreezeError, RetrievalFreeze, check_frozen, load_freeze, mark_frozen, retrieval_hash
    f = load_freeze(Path(__file__).resolve().parents[2] / "configs" / "retrieval_freeze.yaml")
    assert f.dev_seeds == [1, 2, 3, 4, 5, 7] and f.eval_seeds == [12, 13, 14, 15, 16]
    check_frozen(f, 7, None)                                              # 개발 시드
    check_frozen(f, None, None)                                           # 시드 없는 픽스처
    open_ = RetrievalFreeze(dev_seeds=[7], eval_seeds=[12])
    with pytest.raises(FreezeError, match="동결되지 않았다"):
        check_frozen(open_, 12, RP)
    frozen = open_.model_copy(update={"retrieval_params_sha256": retrieval_hash(RP)})
    check_frozen(frozen, 12, RP)
    with pytest.raises(FreezeError, match="다르다"):
        check_frozen(frozen, 12, RP.model_copy(update={"top_k": RP.top_k + 1}))
    with pytest.raises(FreezeError):
        check_frozen(frozen, 12, None)
    p = tmp_path / "freeze.yaml"
    shutil.copy(Path(__file__).resolve().parents[2] / "configs" / "retrieval_freeze.yaml", p)
    assert mark_frozen(p, RP) == load_freeze(p).retrieval_params_sha256 == retrieval_hash(RP)
    assert "# 조회 설정 동결" in p.read_text(encoding="utf-8"), "주석 보존"


def test_runner_refuses_eval_seed_scenario_before_freeze(tmp_path):
    from gbg.contracts.conditions import ConfigError
    from gbg.kernel.runner import Runner
    from gbg.kernel.tools import ToolRegistry
    from gbg.tests.support import load_adapter
    from gbg.tests.test_stage3 import ACCESS, CONDITIONS
    a = load_adapter("worldgen_mini")
    a.manifest = {**a.manifest, "params": {**a.manifest.get("params", {}), "seed": 12}}
    with pytest.raises(ConfigError, match="평가 시드 12"):
        Runner(a, condition="direct", seed=0, run_dir=tmp_path, conditions=CONDITIONS, access=ACCESS,
               tools=ToolRegistry(ACCESS), agent_factory=lambda aid, g, role: None, retrieval=RP)
