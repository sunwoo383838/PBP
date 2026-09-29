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
from gbg.retrieval.eval_recall import build_cases, evaluate, run_new
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
    return run(evaluate(rets, cases, {"evidence": run_new})), skipped


def test_recall_h0_h1_at_least_90_percent():
    """90% 기준은 정확 조회(색인 + catalog 한 단계)에 적용한다. H2는 보고만."""
    report, skipped = _recall_report()
    idx = report["systems"]["index"]
    assert report["cases"] >= 5 and set(idx["by_disc"]) >= {"H0", "H1", "H2"}
    for disc in ("H0", "H1"):
        assert idx["by_disc"][disc]["recall"] >= 0.9, (disc, idx["by_disc"][disc])
    ev = report["systems"]["evidence"]
    assert ev["by_class"] and ev["holder"]["active"]["n"] and set(ev["at_k"]) == {5, 10, 20, 50}
    assert ev["queries"]["n"] == report["cases"] and ev["queries"]["tokens"]


def _close(s, agent):
    s.history.add(agent, 0, "assistant", "[Result] done", [], "d")                   # 픽스처의 열린 에피소드를 닫는다


def test_h2_value_line_returned_with_its_episode():
    """값 줄에는 엔티티가 없다 (H2). 대상 줄로 걸려도 결과는 에피소드 전체(small-to-big)."""
    s = stores()
    _close(s, "fin-sel.a3")
    for text, ents in [("[Task] Review commitment CMT-00077", ["CMT-00077"]), ("[Memo] Checking the 영업1팀 file.", ["영업1팀"]),
                       ("[Tool result] Recorded — On that item: hold until Friday.", []), ("[Result] Review done", [])]:
        s.history.add("fin-sel.a3", 0, "assistant", text, ents, "d")
    s.history.add("fin-sel.a3", 0, "assistant", "[Memo] unrelated note", [], "d")
    ev = run(build_evidence(retriever(s, "FIN-SEL"), "CMT-00077", ["CMT-00077"], mode="bm25"))
    ep = next(it for it in ev.items if it.title == "[Task] Review commitment CMT-00077")
    assert "On that item: hold until Friday." in ep.text and ep.text.endswith("[Result] Review done")
    assert "unrelated note" not in ep.text, "에피소드 밖 줄은 한 줄짜리 단위"
    assert "tag" in ep.source


def test_deepinfra_reranker_batches_and_caches(tmp_path):
    import httpx
    from gbg.retrieval.rerank import CachedReranker, DeepInfraReranker, RerankCache
    seen = []

    def handler(req):
        body = json.loads(req.content)
        seen.append((req.url.path, len(body["documents"])))
        return httpx.Response(200, json={"scores": [len(d) / 100 for d in body["documents"]]})
    inner = DeepInfraReranker(P.llm, "Qwen/Qwen3-Reranker-8B", batch=2, api_key="k", transport=httpx.MockTransport(handler))
    rr = CachedReranker(inner, RerankCache(tmp_path / "rr.sqlite"))
    assert rr.score("q", ["a", "bbb", "cc"]) == [0.01, 0.03, 0.02]
    assert seen == [("/v1/inference/Qwen/Qwen3-Reranker-8B", 2), ("/v1/inference/Qwen/Qwen3-Reranker-8B", 1)]
    replay = CachedReranker(inner, rr.cache, "REPLAY")
    assert replay.score("q", ["cc", "a"]) == [0.02, 0.01] and len(seen) == 2


def test_episode_chunking_rules():
    from gbg.contracts.schemas import HistoryEntry
    from gbg.retrieval.episodes import episodes
    mk = lambda i, t, task=None: HistoryEntry(seq=i, day=0, role="user", text=t, tokens=5, entities=[], digest="",
                                             task=task)
    es = [mk(1, "[Memo] a"), mk(2, "[Task] one"), mk(3, "x"), mk(4, "[Task] two"), mk(5, "y"), mk(6, "[Result] r"),
          mk(7, "[Task W-1] run", "W-1"), mk(8, "[Handover] note"), mk(9, "[Question from agent-x] q", "W-2"),
          mk(10, "[Answer from agent-y] a", "W-1"), mk(11, "[Answer to agent-x] a", "W-2")]
    got = [ep.seqs for ep in episodes("a", es)]
    assert got == [(1,), (2, 3), (4, 5, 6), (7, 10), (8,), (9, 11)], "[Result] 전 새 [Task]는 그 직전에서 끊고, 과제는 id로 묶는다"
    assert [ep.title for ep in episodes("a", es)][:3] == ["", "[Task] one", "[Task] two"]


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
    for cond in ("routing", "ingress_read", "ingress_sel", "ingress", "i_e", "gateway_rag"):   # 경계 조건 모두 같은 검색
        guard = AccessGuard(access, cond)
        assert authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "FIN-SEL")["allowed"]
        with pytest.raises(RetrievalDenied):
            authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "HR-SEL")
    for cond in conds:
        guard = AccessGuard(access, cond)
        if cond == "full_load":                                            # 정의: 모든 권한 (자기 그룹 이력 포함)
            assert authorize(guard, "agent:fin-sel.a1", "FIN-SEL", "FIN-SEL")["allowed"]
            continue
        with pytest.raises(RetrievalDenied):
            authorize(guard, "agent:fin-sel.a1", "FIN-SEL", "FIN-SEL")             # 에이전트는 그룹 이력 불가


# ─────────────────────────── 조립 규칙 ───────────────────────────
def test_no_version_pruning_and_cap():
    """조회 단계는 버전을 고르지 않는다 (버전 선택은 Ingress 게이트웨이 LLM의 L_state 결정). 상한은 점수 낮은 것부터 뺀다."""
    s = stores()
    _close(s, "fin-sel.a1")
    for i in range(5):
        s.history.add("fin-sel.a1", i + 1, "assistant", f"영업1팀 available budget update {i}.", ["영업1팀"], "d")
    ev = run(build_evidence(retriever(s, "FIN-SEL"), "영업1팀 available budget", ["영업1팀"]))
    updates = [it.text for it in ev.items if "budget update" in it.text]
    assert updates == [f"영업1팀 available budget update {i}." for i in range(5)]
    assert "attr" not in ev.log

    class ByDay:                                                          # 점수 = 가장 오래된 것이 가장 높다
        name = "by-day"

        def score(self, q, docs):
            return [-int(d.rsplit(" ", 1)[-1].rstrip(".")) if "budget update" in d else -99 for d in docs]
    small = RP.model_copy(update={"evidence_cap": 60})
    r = retriever(s, "FIN-SEL", params=small)
    r.reranker = ByDay()
    ev = run(build_evidence(r, "영업1팀 available budget", ["영업1팀"]))
    assert ev.cap_reached and ev.tokens <= 60 and ev.log["cap_reached"]
    kept = [it.text for it in ev.items]
    assert kept and kept[0] == "영업1팀 available budget update 0.", "점수 높은(오래된) 것이 남고 낮은 것부터 빠진다"
    assert [it.day for it in ev.items] == sorted(it.day for it in ev.items), "표시는 시간순"


# ─────────────────────────── 실제 bge-m3 (선택) ───────────────────────────
@pytest.mark.skipif(os.environ.get("GBG_LIVE") != "1", reason="GBG_LIVE=1일 때만 DeepInfra 임베딩을 부른다")
def test_real_bge_m3(tmp_path):
    emb = CachedEmbedder(DeepInfraEmbedder(P.llm, RP.embed_model), EmbeddingCache(tmp_path / "emb.sqlite"), "LIVE")
    report, _ = _recall_report(emb)
    hy = report["systems"]["evidence"]
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
    rep = lambda h0, h1, h2: {"systems": {"index": {"by_disc": {"H0": {"recall": h0}, "H1": {"recall": h1},
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


def test_runner_runs_eval_seed_only_with_frozen_retrieval_config(tmp_path):
    from gbg.contracts.conditions import ConfigError
    from gbg.kernel.runner import Runner
    from gbg.kernel.tools import ToolRegistry
    from gbg.tests.support import load_adapter
    from gbg.tests.test_stage3 import ACCESS, CONDITIONS
    a = load_adapter("worldgen_mini")
    a.manifest = {**a.manifest, "params": {**a.manifest.get("params", {}), "seed": 12}}
    mk = lambda d, rp: Runner(a, condition="direct", seed=0, run_dir=tmp_path / d, conditions=CONDITIONS, access=ACCESS,
                              tools=ToolRegistry(ACCESS), agent_factory=lambda aid, g, role: None, retrieval=rp)
    with pytest.raises(ConfigError, match="평가 시드 12"):
        mk("changed", RP.model_copy(update={"top_k": RP.top_k + 1}))      # 동결 뒤 조회 설정을 바꾸면 거부
    with pytest.raises(ConfigError, match="평가 시드 12"):
        mk("missing", None)
    mk("frozen", RP)                                                       # 동결된 설정 그대로면 실행


def test_long_texts_are_clipped_for_the_embedding_model():
    """과제를 이어 풀면 생기는 긴 에피소드: 임베딩 입력만 앞부분으로 자르고, 한도 초과 거부가 오면 절반씩 줄여 재시도."""
    import asyncio
    import httpx
    from gbg.retrieval.embed import DeepInfraEmbedder
    sent = []

    def handler(req):
        body = __import__("json").loads(req.content)
        sent.append([len(t) for t in body["input"]])
        if max(len(t) for t in body["input"]) > 5000:
            return httpx.Response(400, json={"error": {"message": "the model's context length is only 8192 tokens (parameter=input_tokens)"}})
        return httpx.Response(200, json={"data": [{"index": i, "embedding": [1.0, 0.0]} for i, _ in enumerate(body["input"])]})
    e = DeepInfraEmbedder(P.llm, "m", api_key="k", transport=httpx.MockTransport(handler))
    out = asyncio.run(e.embed(["x" * 40000, "short"]))
    assert out.shape == (2, 2) and sent == [[16000, 5], [8000, 5], [4000, 5]]


def test_long_documents_are_clipped_for_the_reranker():
    import httpx
    from gbg.retrieval.rerank import DeepInfraReranker
    sent = []

    def handler(req):
        body = json.loads(req.content)
        sent.append(max(len(d) for d in body["documents"]))
        if sent[-1] > 5000:
            return httpx.Response(400, json={"detail": "This model's maximum context length is 40960 tokens (parameter=input_tokens)"})
        return httpx.Response(200, json={"scores": [0.5] * len(body["documents"])})
    r = DeepInfraReranker(P.llm, "m", api_key="k", transport=httpx.MockTransport(handler))
    assert r.score("q", ["x" * 50000, "short"]) == [0.5, 0.5] and sent == [16000, 8000, 4000]


def test_retriever_sync_lock_works_across_event_loops():
    """실행기는 묶음마다 asyncio.run(새 루프)을 쓴다. 검색기 동기화 잠금이 앞 루프에 묶여 있으면 경합 때 오류가 난다
    (dry15: "Lock … is bound to a different event loop"로 재시작 113회)."""
    import asyncio
    from gbg.retrieval.hybrid import GroupRetriever

    class R(GroupRetriever):
        def __init__(self):
            pass

        async def _sync(self):
            await asyncio.sleep(0.01)

    r = R()

    async def contended():
        await asyncio.gather(r.sync(), r.sync(), r.sync())
    for _ in range(3):
        asyncio.run(contended())


def test_vector_scores_do_not_depend_on_index_history():
    """같은 문서 집합이면 쌓은 순서·교체 이력과 상관없이 유사도가 같아야 한다 (재개 뒤 색인 = 연속 실행 색인)."""
    import numpy as np
    from gbg.retrieval.embed import VectorIndex
    rng = np.random.default_rng(0)
    vecs = {f"d{i}": rng.standard_normal(1024).astype(np.float32) for i in range(300)}
    q = rng.standard_normal(1024).astype(np.float32)
    a = VectorIndex()
    for k in vecs:                                                         # 하나씩, 중간에 교체도
        a.add([k], np.stack([vecs[k] * 0.5]))
        a.add([k], np.stack([vecs[k]]))
    b = VectorIndex()
    b.add(list(reversed(list(vecs))), np.stack([vecs[k] for k in reversed(list(vecs))]))
    sa, sb = a.scores(q), b.scores(q)
    assert all(round(sa[k], 9) == round(sb[k], 9) for k in vecs)
