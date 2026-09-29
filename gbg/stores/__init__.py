"""그룹별 저장소 투영. 시나리오 초기 상태에서 시작해 번호가 매겨진 WAL 사건으로만 바뀐다.

저장소는 벤치마크를 모른다. 초기 상태와 태깅은 어댑터가 넘긴다.
"""
import json

from gbg.contracts.adapter import BenchmarkAdapter
from gbg.contracts.events import Event
from gbg.contracts.schemas import DbWrite, EgressRecord, GroupInit, GroupSpec, IndexEntry

from .boundary_log import BoundaryLog
from .cards import CardRegistry
from .catalog import Catalog
from .db import VersionedDB
from .egress_log import EgressLog
from .history import HistoryStore, Tagger, approx_tokens
from .index import GroupIndex
from .rulebook import Rulebook

Obs = list[tuple[str, dict]]


class Stores:
    def __init__(self, groups: list[GroupSpec], inits: dict[str, GroupInit], tag: Tagger, *,
                 card_mode: str, rounds_per_day: int, tokens=approx_tokens, responder_session: str = "persistent"):
        self.day_end_round = rounds_per_day + 1
        self.members = {m.agent_id: (g.id, m.role) for g in groups for m in g.members}
        self.db = VersionedDB({g: i.db for g, i in inits.items()})
        self.rulebook = Rulebook({g: i.rules for g, i in inits.items()})
        self.history = HistoryStore({a: es for i in inits.values() for a, es in i.histories.items()}, tag, tokens,
                                    responder_session)
        self.index = GroupIndex({g: i.journal for g, i in inits.items()}, {g: i.activity for g, i in inits.items()},
                                {g: i.entity_index for g, i in inits.items()})
        self.catalog = Catalog({g: i.catalog for g, i in inits.items()})
        self.egress_log = EgressLog({g: i.egress_log for g, i in inits.items()})
        self.boundary_log = BoundaryLog()
        self.env = {g: dict(i.env) for g, i in inits.items()}
        names = {s for i in inits.values() for e, al in i.aliases.items() for s in (e, *al)}
        categories = {g: list(i.env.get("scope_categories", [])) for g, i in inits.items()}
        self.cards = CardRegistry(groups, categories, names, card_mode)

    @classmethod
    def from_adapter(cls, adapter: BenchmarkAdapter, *, card_mode: str, rounds_per_day: int, tokens=approx_tokens,
                     responder_session: str = "persistent"):
        groups = adapter.groups()
        return cls(groups, {g.id: adapter.initial_state(g.id) for g in groups}, adapter.tag,
                   card_mode=card_mode, rounds_per_day=rounds_per_day, tokens=tokens,
                   responder_session=responder_session)

    def apply(self, ev: Event) -> Obs:
        """번호가 매겨진 사건 하나를 모든 투영에 반영한다. 돌려주는 obs 기록은 실행 중에만 파일에 쓴다."""
        p, obs = ev.payload, []
        if ev.type == "world_update":
            kind, data = p["kind"], p["data"]
            if kind == "db_register":
                w = DbWrite.model_validate(data)
                self.db.add(p["group"], w.key, w.version)
            elif kind == "catalog":
                self.catalog.upsert(p["group"], data["key"], data["value"])
            elif kind == "index":
                for x in data["entries"]:
                    self.index.add(x["group"], x["index"], IndexEntry(day=ev.day, agent=x["agent"],
                                                                      text=x.get("text") or x.get("trace") or "",
                                                                      entities=x.get("entities", [])))
        elif ev.type == "boundary_decision":
            if p.get("stage") == "egress":                                  # Egress 결과 → egress_log
                for x in p.get("log", []):
                    self.egress_log.add(p["group"], EgressRecord.model_validate(x))
            elif p.get("stage") == "ingress" and p.get("answer") is not None:   # 조립한 교차 문답 → 경계 상태
                self.boundary_log.add(p["group"], {"day": ev.day, "from_group": p["from_group"], "question": p["question"],
                                                   "entities": p.get("entities", []), "answer": p["answer"],
                                                   "versions": p.get("versions_given", [])})
        elif ev.type == "agent_join":
            self.members[p["agent"]] = (p["group"], p["role"])
            obs += self.cards.join(p["agent"], p["group"], p["role"], p.get("from"), ev.day, ev.seq)
        elif ev.type == "agent_leave":
            self.cards.leave(p["agent"])
        elif ev.type == "round_commit" and p["round"] == self.day_end_round:
            obs += self.cards.day_end(ev.day, self.index, ev.seq)

        self.history.apply(ev, {a: g for a, (g, _) in self.members.items()})
        return obs

    def dump(self) -> dict:
        """모든 투영의 정규 형태 (재생성 비교용)."""
        out = {"db": self.db.dump(), "rulebook": self.rulebook.dump(), "history": self.history.dump(),
               "index": self.index.dump(), "catalog": self.catalog.dump(), "egress_log": self.egress_log.dump(), "boundary_log": self.boundary_log.dump(),
               "env": self.env, "cards": self.cards.dump(), "members": {a: list(v) for a, v in sorted(self.members.items())}}
        return json.loads(json.dumps(out, ensure_ascii=False, sort_keys=True))
