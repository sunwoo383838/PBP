"""card 노출 규칙: Direct에서는 그룹 개념 비노출(불투명 id·지역·skills), swarm 접수 담당 skills, 디렉터리 중복 제거,
그룹 card(게이트웨이 조건 전용) skills = 구성원 card skills의 합집합."""
import asyncio
import json

from gbg.agents.prompts import render_directory
from gbg.benchmarks.worldgen.adapter import ROLE_CARDS
from gbg.contracts.card import public_id
from gbg.kernel.tools import ToolCall
from gbg.stores import Stores
from gbg.tests import test_stage3 as T
from gbg.tests.support import FIXTURES, load_adapter


PUBLISHED = set(json.loads((FIXTURES / "worldgen_mini" / "harness" / "world_init.json").read_text(encoding="utf-8"))["agent_cards"])


def _groups():
    return {g.id: g for g in load_adapter("worldgen_mini").groups()}


def test_public_id_is_opaque_and_deterministic():
    pid = public_id("fin-sel.a1")
    assert pid == public_id("fin-sel.a1") and pid.startswith("agent-") and len(pid) == 16
    assert all(c in "0123456789abcdef" for c in pid[6:]), "그룹을 드러내지 않는 해시"


def test_swarm_coordinator_skills_from_roles_and_card():
    c0 = next(m for m in _groups()["FIN-TYO"].members if m.agent_id == "fin-tyo.c0").card
    roles = list(dict.fromkeys(ROLE_CARDS["roles"]["FIN"]))
    assert [s.id for s in c0.skills] == ["coordinator", *roles]
    assert [s.description for s in c0.skills[1:]] == [ROLE_CARDS["card"][r] for r in roles]
    assert c0.region == "TYO"
    assert not any(g in s.description for s in c0.skills for g in ("FIN", "TYO", "fin-tyo")), "문구에 그룹 없음"


def test_group_card_skills_are_union_of_member_cards():
    """world_init에 공개된 card만 합친다. 역할로 만든 card(워커, card 없이 합류할 구성원)는 프롬프트용이다."""
    for g in _groups().values():
        union = list({s.id: s for m in g.members if m.agent_id in PUBLISHED for s in m.card.skills}.values())
        assert g.card.skills == union
    assert [s.id for s in _groups()["FIN-TYO"].card.skills] == ["coordinator", "budgeting", "payables", "closing", "control"]


def test_directory_lists_each_agent_once_without_groups():
    a = load_adapter("worldgen_mini")
    s = Stores.from_adapter(a, card_mode="static", rounds_per_day=3)
    d = s.cards.directory("agent_cards")
    occ = [c.occupant for c in d]
    assert len(occ) == len(set(occ)) and occ.count("fin-tyo.c0") == 1, "여러 역할의 card 대상이어도 한 번"
    assert [public_id(o) for o in occ] == sorted(public_id(o) for o in occ), "그룹 순이 아니라 불투명 id 순"
    text = render_directory(d)
    for g in a.groups():
        assert g.id not in text and g.id.lower() not in text
        assert all(m.agent_id not in text for m in g.members)
    assert s.cards.resolve(public_id("fin-sel.a2")) == "fin-sel.a2"
    s.cards.leave("fin-sel.a2")
    assert s.cards.resolve(public_id("fin-sel.a2")) == "fin-sel.a2", "떠난 구성원도 풀어 준다 (버스가 끊는다)"
    assert s.cards.resolve("agent-0000000000") is None


def test_ask_agent_by_public_id_reaches_responder_without_group(tmp_path):
    fake = T.FakeDeepInfra()
    llm = T.backend("LIVE", cache=T.ResponseCache(tmp_path / "c.sqlite"), transport=fake.transport())
    T.llm_runner(tmp_path / "run", llm, condition="direct").run()
    msgs = [e for e in T.wal(tmp_path / "run") if e["type"] == "message" and e["payload"]["kind"] == "request"]
    assert msgs and all(m["payload"]["delivered"] for m in msgs)
    members = {m.agent_id for g in _groups().values() for m in g.members}
    assert all(m["payload"]["to_agent"] in members for m in msgs), "WAL에는 실제 id"
    asked = [b for b in fake.bodies if "[Question from " in b["messages"][1]["content"]]
    assert asked
    for b in asked:
        text = b["messages"][0]["content"] + b["messages"][1]["content"]
        q = text.split("[Question from ", 1)[1].split("]", 1)[0]
        assert q.startswith("agent-") and "(" not in q
    for b in fake.bodies:
        system = b["messages"][0]["content"]
        assert not any(g in system for g in _groups()), "system 프롬프트에 그룹 id 없음"


def test_rules_are_fixed_in_system_prompt_own_group_only_without_group_ids(tmp_path):
    """규정은 도구가 아니라 system에 고정: 자기 그룹 규정만, 그룹 접두어 없는 id로. full_load는 전 그룹 규정."""
    from gbg.tests.test_stage5 import run
    a = load_adapter("worldgen_mini")
    assert "rulebook.read" not in {t.name for t in a.make_tools(Stores.from_adapter(a, card_mode="static", rounds_per_day=3))}
    systems = []

    def script(req):
        systems.append((req["messages"][0]["content"], {t["function"]["name"] for t in req.get("tools", [])}))
        return T.mk([("submit", {"dept": "", "grade": 0})]) if any(t["function"]["name"] == "submit" for t in req["tools"]) \
            else T.mk([("reply", {"answer": "x", "items": [], "missing": ["x"]})])
    run(tmp_path / "d", "direct", script=script, max_day=1)
    assert any("[Rules of your area]" in sm for sm, tools in systems if "submit" in tools)
    assert all("rulebook.read" not in tools for _, tools in systems)
    own = [sm for sm, _ in systems if "transfer_effective_day" in sm]
    assert own and all(g.id not in sm for sm in own for g in a.groups()), "Direct: 그룹 id 없이"
    run(tmp_path / "f", "full_load", script=script, max_day=1)
    fl = [sm for sm, tools in systems if "load_group_history" in tools]
    assert fl and all(f"[Rules of {g}]" in fl[0] for g in ("FIN-SEL", "HR-SEL", "HR-TYO", "FIN-TYO"))


def test_every_member_has_a_card_but_workers_stay_out_of_the_directory():
    """swarm 워커도 자기 역할 card를 가진다(시스템 프롬프트용). 디렉터리에는 card 대상만 보인다."""
    from gbg.stores import Stores
    a = load_adapter("worldgen_mini")
    s = Stores.from_adapter(a, card_mode="static", rounds_per_day=3)
    assert all(m.card for g in a.groups() for m in g.members)
    w = s.cards.agent_cards["fin-tyo.w00001"]
    assert w.skills[0].id == "worker" and w.skills[0].description == ROLE_CARDS["card"]["worker"]
    assert "fin-tyo.w00001" not in {c.occupant for c in s.cards.directory("agent_cards")}
    s.cards.join("fin-tyo.w00009", "FIN-TYO", "worker", None, 2, 1)       # 실행 중 생긴 워커도 역할 card를 받는다
    assert s.cards.agent_cards["fin-tyo.w00009"].occupant == "fin-tyo.w00009"
    assert "fin-tyo.w00009" not in {c.occupant for c in s.cards.directory("agent_cards")}
