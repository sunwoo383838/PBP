"""구조화 응답 항목(items): reply·게이트웨이 answer 공통 스키마 검사, Routing 전달, 경계 모듈 내부 질의 병렬 실행."""
import asyncio

from gbg.contracts.envelope import ITEM_FIELDS, Item, Response, answer_parameters, check_items, render_response
from gbg.llm.agent_loop import REPLY_TOOL

ITEM = {"entity": "CMT-00055", "attribute": "status", "value": "1,234,567", "status": "pending", "ref": "D1"}


def test_reply_schema_llm_writes_ref_and_code_fills_source_and_day():
    props = REPLY_TOOL["parameters"]["properties"]
    assert set(REPLY_TOOL["parameters"]["required"]) == {"items", "missing"}
    item = props["items"]["items"]
    assert set(item["required"]) == set(ITEM_FIELDS) == {"entity", "attribute", "value", "status", "ref"}
    assert "source" not in item["properties"] and "day" not in item["properties"], "source·day는 LLM이 쓰지 않는다"
    assert REPLY_TOOL["parameters"] == answer_parameters()


def test_check_items_accepts_and_rejects():
    ok, (answer, items, missing) = check_items({"items": [ITEM], "missing": []}, resolve=lambda x: ("db", "12"))
    assert ok and items == [Item(**ITEM, source="db", day="12")] and items[0].value == "1,234,567", "값은 원문 그대로"
    assert check_items({"items": [ITEM], "missing": []})[1][1][0].day == "unknown", "풀리지 않으면 unknown"
    assert check_items({"items": [], "missing": ["hires"]})[0], "항목이 없으면 missing이 1개 이상"
    for bad in ({"items": [], "missing": []}, {"items": [{**ITEM, "source": "db"}], "missing": []},
                {"items": [{**ITEM, "value": 1234567}], "missing": []}, {"items": [{"entity": "x"}], "missing": []},
                {"items": [{**ITEM, "value": " "}], "missing": []}):
        assert not check_items(bad)[0], bad
    assert not check_items({"items": [ITEM], "missing": []}, lambda r: None if "[R" in r else "cite")[0]


def test_render_response_lists_items():
    r = Response(rid="r", status="partial", answer="summary", items=[Item(**ITEM, source="db", day="12")], missing=["hires"],
                 referral_to=None, need=[], as_of=1).model_dump(mode="json")
    text = render_response(r)
    assert "CMT-00055 | status | 1,234,567 | pending | db, day 12: D1" in text and "missing: hires" in text


def test_internal_queries_run_concurrently():
    from gbg.boundary.module import BoundaryModule
    running, peak = [0], [0]

    class B:
        async def ask(self, a, q, purpose, hop):
            running[0] += 1
            peak[0] = max(peak[0], running[0])
            await asyncio.sleep(0.01)
            running[0] -= 1
            return a

    class Req:
        purpose, hop = None, 1
    out = asyncio.run(BoundaryModule._ask_all(B(), [("a1", "q"), ("a2", "q"), ("a3", "q")], Req()))
    assert out == [("a1", "a1"), ("a2", "a2"), ("a3", "a3")] and peak[0] == 3
