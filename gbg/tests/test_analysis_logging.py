"""분석 기록 (obs 전용): 새 기록이 채워지고, WAL·프롬프트에는 새지 않는다.
실험 불변은 별도로 master 코드와 같은 대본 실행의 WAL 해시·LLM 요청 키가 같음을 확인했다(HARNESS_CHANGES.md)."""
import json

import pytest

from gbg.tests.test_stage5 import run

NEW_KEYS = ("context_items", "loop_items", "evidence_cites", "reply_cites", "version_cites", "state_cites",
            "select_basis", "record_counts", "outside_top_k", "bm25_rank", "crossing")


def _jl(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


@pytest.fixture(scope="module")
def ingress_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("ing") / "ingress"
    run(d, "ingress")
    return d


def test_agent_calls_record_context_and_loop_items(ingress_run):
    cw = _jl(ingress_run / "obs" / "context_windows.jsonl")
    agent = [c for c in cw if c.get("component") in ("requester", "responder")]
    assert agent and all("context_items" in c and "loop_items" in c for c in agent)
    items = [x for c in agent for x in c["context_items"]]
    assert items and {x["source"] for x in items} <= {"own_task", "other_task", "history"}
    tools = [x for c in agent for x in c["loop_items"] if x["kind"] == "tool_result"]
    asked = [x for x in tools if x.get("tool") == "ask_group"]
    assert asked and all(x["rid"] and x["ref"].startswith("R") for x in asked), "통신 결과는 응답 rid와 R# id"


def test_gateway_calls_record_citation_maps(ingress_run):
    cw = _jl(ingress_run / "obs" / "context_windows.jsonl")
    asm = [c for c in cw if c.get("boundary_step") == "assemble"]
    assert asm and all({"evidence_cites", "reply_cites", "version_cites", "state_cites"} <= set(c) for c in asm)
    assert any(c["reply_cites"] for c in asm) and all(v["rid"] for c in asm for v in c["reply_cites"].values())
    assert all("seqs" in v for c in asm for v in c["evidence_cites"].values())
    gw = _jl(ingress_run / "obs" / "gateway.jsonl")
    assert gw and all(g["select_basis"] in ("llm", "index_holders", "card_targets", "none") and "record_counts" in g
                      for g in gw if "selected" in g)


def test_retrieval_candidates_have_channel_scores_and_reasons(ingress_run):
    for r in _jl(ingress_run / "obs" / "retrievals.jsonl"):
        assert "outside_top_k" in r and "search_stats" in r and "selected_seqs" in r
        assert all(c["reason"] in ("selected", "cap_cut") and "bm25_rank" in c for c in r["candidates"])
        assert sum(c["reason"] == "selected" for c in r["candidates"]) == len(r["selected"])


def test_messages_batches_manifest(ingress_run):
    msgs = _jl(ingress_run / "obs" / "messages.jsonl")
    assert msgs and any(m["crossing"] for m in msgs) and all("seq" in m for m in msgs)
    assert _jl(ingress_run / "obs" / "batches.jsonl")
    m = json.loads((ingress_run / "manifest.json").read_text())
    assert m["condition_resolved"]["ingress"] and m["harness"]["commit"] is not None and "retrieval" in m


def test_analysis_fields_never_reach_the_wal(ingress_run):
    wal = (ingress_run / "wal" / "events.jsonl").read_text(encoding="utf-8")
    assert not [k for k in NEW_KEYS if f'"{k}"' in wal], "분석 기록은 obs 전용 (WAL 해시 불변)"
    run_json = json.loads((ingress_run / "run.json").read_text())
    assert "harness" not in run_json, "run.json(재개 설정 비교)에는 넣지 않는다"
