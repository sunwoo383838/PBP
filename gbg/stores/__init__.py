"""그룹별 저장소 투영. 시나리오 초기 상태에서 시작해 커밋된 WAL 사건으로만 바뀐다.

저장소는 벤치마크를 모른다. 초기 상태와 태깅은 어댑터가 넘긴다.
"""
import json

from gbg.contracts.adapter import BenchmarkAdapter
from gbg.contracts.events import Event
from gbg.contracts.schemas import ActivityRecord, DbWrite, GroupInit, GroupSpec, JournalRecord

from .activity import ActivityIndex
from .cards import CardRegistry
from .db import VersionedDB
from .egress_log import EgressLog
from .history import HistoryStore, Tagger, approx_tokens
from .journal import Journal
from .rulebook import Rulebook

Obs = list[tuple[str, dict]]


class Stores:
    def __init__(self, groups: list[GroupSpec], inits: dict[str, GroupInit], tag: Tagger, *,
                 card_mode: str, rounds_per_day: int, tokens=approx_tokens):
        self.rounds_per_day = rounds_per_day
        self.members = {m.agent_id: (g.id, m.role) for g in groups for m in g.members}
        self.db = VersionedDB({g: i.db for g, i in inits.items()})
        self.rulebook = Rulebook({g: i.rules for g, i in inits.items()})
        self.history = HistoryStore({a: es for i in inits.values() for a, es in i.histories.items()}, tag, tokens)
        self.activity = ActivityIndex({g: i.activity for g, i in inits.items()})
        self.journal = Journal({g: i.journal for g, i in inits.items()})
        self.egress_log = EgressLog({g: i.egress_log for g, i in inits.items()})
        self.env = {g: dict(i.env) for g, i in inits.items()}
        names = {s for i in inits.values() for e, al in i.aliases.items() for s in (e, *al)}
        categories = {g: list(i.env.get("scope_categories", [])) for g, i in inits.items()}
        self.cards = CardRegistry(groups, categories, names, card_mode)

    @classmethod
    def from_adapter(cls, adapter: BenchmarkAdapter, *, card_mode: str, rounds_per_day: int, tokens=approx_tokens):
        groups = adapter.groups()
        return cls(groups, {g.id: adapter.initial_state(g.id) for g in groups}, adapter.tag,
                   card_mode=card_mode, rounds_per_day=rounds_per_day, tokens=tokens)

    def apply(self, ev: Event) -> Obs:
        """커밋된 사건 하나를 모든 투영에 반영한다. 돌려주는 obs 기록은 실행 중에만 파일에 쓴다."""
        p, obs = ev.payload, []
        if ev.type == "world_update":
            if p["action"] == "db_write":
                w = DbWrite.model_validate(p["data"])
                self.db.add(p["group"], w.key, w.version)
            elif p["action"] == "env":
                self.env.setdefault(p["group"], {}).update(p["data"])
            return obs
        if ev.type == "agent_join":
            self.members[p["agent"]] = (p["group"], p["role"])
            obs += self.cards.join(p["agent"], p["group"], p.get("from"), ev.day, ev.seq)
        elif ev.type == "agent_leave":
            self.cards.leave(p["agent"])
        elif ev.type == "round_commit" and p["round"] == self.rounds_per_day:
            obs += self.cards.day_end(ev.day, self.activity, ev.seq)

        group_of = {a: g for a, (g, _) in self.members.items()}
        answered = self.history.apply(ev, group_of)
        if ev.type == "answer":
            task = self.history.tasks.get(p["task_id"], {})
            for agent, seq in answered.items():
                if task.get("kind") != "local":
                    continue
                g, role = self.members[agent]
                for ent in task["entities"]:
                    self.activity.add(g, ActivityRecord(entity=ent, agent=agent, seq=seq, day=ev.day, role=role))
                    if task.get("disc") == "H0":
                        self.journal.add(g, JournalRecord(entity=ent, agent=agent, seq=seq))
        return obs

    def dump(self) -> dict:
        """모든 투영의 정규 형태 (재생성 비교용)."""
        out = {"db": self.db.dump(), "rulebook": self.rulebook.dump(), "history": self.history.dump(),
               "activity": self.activity.dump(), "journal": self.journal.dump(), "egress_log": self.egress_log.dump(),
               "env": self.env, "cards": self.cards.dump(), "members": {a: list(v) for a, v in sorted(self.members.items())}}
        return json.loads(json.dumps(out, ensure_ascii=False, sort_keys=True))
