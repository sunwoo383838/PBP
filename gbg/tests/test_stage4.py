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
from gbg.contracts.schemas import GoldRecord
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


def gold():
    return [GoldRecord.model_validate_json(x)
            for x in (FIXTURES / "worldgen_mini" / "private" / "gold.jsonl").read_text(encoding="utf-8").splitlines()]


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
    ev1 = run(build_evidence(retriever(stores(), "FIN-SEL", live), "영업1팀 available budget", ["영업1팀"], "available_budget"))
    assert live.computed > 0
    replay = CachedEmbedder(HashEmbedder(), cache, "REPLAY")
    ev2 = run(build_evidence(retriever(stores(), "FIN-SEL", replay), "영업1팀 available budget", ["영업1팀"], "available_budget"))
    assert replay.computed == 0
    assert ev1.text == ev2.text and json.dumps(ev1.log, sort_keys=True) == json.dumps(ev2.log, sort_keys=True)
    assert ev1.items and ev1.text.startswith("[E1] ")


def test_replay_miss_is_fatal(tmp_path):
    replay = CachedEmbedder(HashEmbedder(), EmbeddingCache(tmp_path / "emb.sqlite"), "REPLAY")
    with pytest.raises(EmbeddingMiss):
        run(build_evidence(retriever(stores(), "FIN-SEL", replay), "x", []))


# ─────────────────────────── 2. 회수율 ───────────────────────────
def _recall_report(embedder=None):
    a = load_adapter("worldgen_mini")
    s = stores()
    tasks = {e.task_id: e for e in a.events() if e.kind != "world"}
    aliases = {g: snap.aliases for g, snap in a._snap.items()}
    cases, skipped = build_cases(s, tasks, gold(), aliases)
    rets = {g: retriever(s, g, embedder) for g in {c.group for c in cases}}
    return run(evaluate(rets, cases)), skipped


def test_recall_h0_h1_at_least_90_percent():
    report, skipped = _recall_report()
    hy = report["modes"]["hybrid"]
    assert report["cases"] >= 5
    for disc in ("H0", "H1"):
        assert hy["by_disc"][disc]["recall"] >= 0.9, (disc, hy["by_disc"][disc])
    assert "bm25" in report["modes"] and hy["by_day"]
    assert skipped.get("no_canary", 0) >= 1, "카나리 없는 조각은 측정에서 빠진다"


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


def test_alias_resolution_accuracy_at_least_95_percent():
    a = load_adapter("worldgen_mini")
    total = correct = 0
    wrong = []
    for group, cases in ALIAS_CASES.items():
        r = AliasResolver(a._snap[group].aliases, embedder=HashEmbedder(), embed_threshold=RP.alias.embed_threshold,
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
    for cond in conds:
        guard = AccessGuard(access, cond)
        assert authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "FIN-SEL")["allowed"]
        with pytest.raises(RetrievalDenied):
            authorize(guard, "boundary:FIN-SEL", "FIN-SEL", "HR-SEL")
        with pytest.raises(RetrievalDenied):
            authorize(guard, "agent:fin-sel.a1", "FIN-SEL", "FIN-SEL")             # 에이전트는 그룹 이력 불가


# ─────────────────────────── 조립 규칙 ───────────────────────────
def test_attr_versions_and_cap():
    s = stores()
    for i in range(5):
        s.history.add("fin-sel.a1", i + 1, "assistant", f"영업1팀 available budget update {i}.", ["영업1팀"], "d")
    ev = run(build_evidence(retriever(s, "FIN-SEL"), "영업1팀 available budget", ["영업1팀"], "available_budget"))
    updates = [it.text for it in ev.items if "budget update" in it.text and it.source != "context"]
    assert updates == ["영업1팀 available budget update 3.", "영업1팀 available budget update 4."]
    small = RP.model_copy(update={"evidence_cap": 60})
    ev = run(build_evidence(retriever(s, "FIN-SEL", params=small), "영업1팀 available budget", ["영업1팀"], "available_budget"))
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
    a = load_adapter("worldgen_mini")
    total = correct = 0
    for group, cases in ALIAS_CASES.items():
        r = AliasResolver(a._snap[group].aliases, embedder=emb, embed_threshold=RP.alias.embed_threshold)
        for text, want in cases:
            total += 1
            correct += run(r.resolve(text)).entities == ((want,) if want else ())
    assert correct / total >= 0.95
