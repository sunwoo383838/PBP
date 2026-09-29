"""worldgen 구조화 조회: 역할 정책, 엔티티 해소, 레코드 조회, 엔티티 검색.

에이전트는 (entity, record_type)으로만 묻는다. entity는 ID나 알려진 별칭이고, 여기서 canonical ID와 physical key로
해소한다. 에이전트에게 보이는 상태는 HIT / NOT_FOUND / AMBIGUOUS / INVALID_TYPE 넷뿐이고, 원래 라벨
(NOT_YET_AVAILABLE, PERMISSION_DENIED 등)은 obs에만 남는다. NOT_FOUND와 AMBIGUOUS에는 후보를 싣지 않는다.
"""
import re
import unicodedata
from pathlib import Path

import yaml
from pydantic import Field, ValidationError, model_validator

from gbg.contracts._base import Contract
from gbg.contracts.conditions import ConfigError
from gbg.stores.db import VersionedDB

POLICY_PATH = Path(__file__).with_name("role_policy.yaml")

# 로그 라벨 → 에이전트에게 보이는 상태
VISIBLE = {
    "HIT": "HIT",
    "NOT_FOUND": "NOT_FOUND",                   # 이름·ID가 어떤 엔티티와도 맞지 않음
    "NO_RECORD": "NOT_FOUND",                   # 엔티티는 있으나 그 record type 레코드가 없음
    "NOT_YET_AVAILABLE": "NOT_FOUND",           # 레코드가 있으나 아직 DB에 등록되지 않음 (등록 지연)
    "PERMISSION_DENIED": "NOT_FOUND",           # 다른 그룹 소속 엔티티
    "AMBIGUOUS": "AMBIGUOUS",
    "UNKNOWN_TYPE": "INVALID_TYPE",
    "TYPE_NOT_PERMITTED": "INVALID_TYPE",       # 역할 정책 밖의 record type (백엔드 재검사)
    "KIND_MISMATCH": "INVALID_TYPE",            # 엔티티 종류와 record type이 맞지 않음
    "EMPTY_QUERY": "NOT_FOUND",
}
HINTS = {
    "NOT_FOUND": "No matching record. Retry with the entity ID, or use entity.search to find the entity.",
    "AMBIGUOUS": "The name matches more than one entity. Retry with the entity ID, or use entity.search.",
    "INVALID_TYPE": "Use one of the record types listed in the tool definition.",
}


# ─────────────────────────── 역할 정책 ───────────────────────────
class RecordType(Contract):
    entity_kind: str
    key: str                                    # physical key 템플릿: {group}, {entity} 또는 {member}
    description: str
    match_field: str | None = None
    limit: int | None = Field(None, ge=1)

    @property
    def multi(self) -> bool:
        return "{member}" in self.key

    @model_validator(mode="after")
    def _shape(self):
        if "{group}" not in self.key or (("{entity}" in self.key) == ("{member}" in self.key)):
            raise ValueError(f"key 템플릿은 {{group}}과 {{entity}} 또는 {{member}} 중 하나를 가져야 한다: {self.key}")
        if self.multi and (self.match_field is None or self.limit is None):
            raise ValueError("여러 레코드 유형에는 match_field와 limit이 필요하다")
        return self


class RolePolicy(Contract):
    record_types: dict[str, RecordType]
    entity_names: dict[str, str]
    roles: dict[str, list[str]]
    search_limit: int = Field(ge=1)

    @model_validator(mode="after")
    def _refs(self):
        for role, types in self.roles.items():
            if unknown := set(types) - set(self.record_types):
                raise ValueError(f"역할 {role}: 정의되지 않은 record type {sorted(unknown)}")
        if unknown := {t.entity_kind for t in self.record_types.values()} - set(self.entity_names):
            raise ValueError(f"entity_names에 없는 엔티티 종류 {sorted(unknown)}")
        return self

    def types_for(self, role: str) -> list[str]:
        return list(self.roles.get(role, []))


def load_policy(path: Path = POLICY_PATH) -> RolePolicy:
    try:
        return RolePolicy.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
    except ValidationError as e:
        raise ConfigError(f"{path}: 역할 정책 오류\n{e}") from e


def norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _template_regex(template: str, group: str) -> re.Pattern:
    parts = re.split(r"(\{group\}|\{entity\}|\{member\})", template)
    out = []
    for p in parts:
        if p == "{group}":
            out.append(re.escape(group))
        elif p in ("{entity}", "{member}"):
            out.append(r"(?P<entity>[^/]+)")
        else:
            out.append(re.escape(p))
    return re.compile("^" + "".join(out) + "$")


# ─────────────────────────── 엔티티와 조회 ───────────────────────────
class RecordService:
    def __init__(self, policy: RolePolicy, aliases: dict[str, dict[str, list[str]]], db: VersionedDB):
        """aliases: 그룹 → {엔티티 id: 별칭}. 모든 그룹의 별칭표로 해소하고, 그룹 범위로 권한을 가른다."""
        self.policy, self.aliases, self.db = policy, aliases, db
        # 엔티티 종류를 알려 주는 단일 레코드 유형들 (여러 레코드 유형의 member도 이것으로 분류된다)
        self._kind_templates = [(t.entity_kind, t.key.replace("{member}", "{entity}"))
                                for t in policy.record_types.values()]

    # ── 엔티티 ──
    def _key_entities(self, group: str) -> dict[str, set[str]]:
        """그룹 DB 키에서 뽑은 엔티티 → 종류 (등록 여부와 무관, 존재하는 키 전부)."""
        out: dict[str, set[str]] = {}
        for key in self.db.keys(group):
            for kind, tmpl in self._kind_templates:
                if m := _template_regex(tmpl, group).match(key):
                    out.setdefault(m["entity"], set()).add(kind)
        return out

    def _all_groups(self) -> list[str]:
        return sorted(set(self.aliases) | set(self.db.groups()))

    def resolve(self, text: str) -> list[str]:
        q = norm(text)
        found = set()
        for g in self._all_groups():
            for e in self._key_entities(g):
                if norm(e) == q:
                    found.add(e)
            for e, al in self.aliases.get(g, {}).items():
                if norm(e) == q or any(norm(a) == q for a in al):
                    found.add(e)
        return sorted(found)

    def kinds(self, entity: str) -> set[str]:
        return {k for g in self._all_groups() for k in self._key_entities(g).get(entity, set())}

    def in_scope(self, group: str, entity: str) -> bool:
        return entity in self.aliases.get(group, {}) or entity in self._key_entities(group)

    # ── 조회 ──
    def lookup(self, group: str, role: str, entity_text: str, record_type: str, day: int) -> tuple[dict, dict]:
        """(에이전트에게 보일 결과, obs 기록)."""
        log = {"group": group, "role": role, "entity_input": entity_text, "record_type": record_type,
               "entity": None, "candidates": 0, "keys": []}
        rt = self.policy.record_types.get(record_type)
        if rt is None:
            return self._miss("UNKNOWN_TYPE", log)
        if record_type not in self.policy.types_for(role):                  # 백엔드 권한 재검사
            return self._miss("TYPE_NOT_PERMITTED", log)
        cands = self.resolve(entity_text)
        log["candidates"] = len(cands)
        if not cands:
            return self._miss("NOT_FOUND", log)
        if len(cands) > 1:
            return self._miss("AMBIGUOUS", log)
        e = log["entity"] = cands[0]
        kinds = self.kinds(e)
        if kinds and rt.entity_kind not in kinds:
            return self._miss("KIND_MISMATCH", log)
        if not self.in_scope(group, e):
            return self._miss("PERMISSION_DENIED", log)
        return self._multi(group, e, record_type, rt, day, log) if rt.multi else \
            self._single(group, e, record_type, rt, day, log)

    def _single(self, group, e, name, rt, day, log):
        key = rt.key.format(group=group, entity=e)
        log["keys"] = [key]
        v = self.db.query(group, key, day)
        exists = [x for x in self.db.versions(group, key) if x.day <= day]
        if v is None:
            return self._miss("NOT_YET_AVAILABLE" if exists else "NO_RECORD", log)
        log.update(version=v.v, newer_pending=exists[-1].v > v.v)
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name, "registered_day": v.db_day,
                               "record": v.value})

    def _multi(self, group, e, name, rt, day, log):
        pattern = _template_regex(rt.key, group)
        hits, pending = [], False
        for key in self.db.keys(group):
            if not (m := pattern.match(key)):
                continue
            v = self.db.query(group, key, day)
            if v is not None and isinstance(v.value, dict) and v.value.get(rt.match_field) == e:
                hits.append((m["entity"], key, v))
            elif any(isinstance(x.value, dict) and x.value.get(rt.match_field) == e
                     for x in self.db.versions(group, key) if x.day <= day):
                pending = True
        if not hits:
            return self._miss("NOT_YET_AVAILABLE" if pending else "NO_RECORD", log)
        hits.sort(key=lambda h: h[0])
        shown = hits[: rt.limit]
        log.update(keys=[k for _, k, _ in shown], total=len(hits))
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name,
                               "records": [{"id": m, "registered_day": v.db_day, **v.value} for m, _, v in shown],
                               "truncated": len(hits) > rt.limit})

    def search(self, group: str, role: str, query: str, day: int) -> tuple[dict, dict]:
        """자기 그룹 DB에 오늘까지 등록된 레코드가 있는 엔티티 중, 자기 역할이 조회할 수 있는 종류만 찾는다."""
        log = {"group": group, "role": role, "query": query}
        q = norm(query)
        if not q:
            return self._miss("EMPTY_QUERY", log)
        allowed = {self.policy.record_types[t].entity_kind for t in self.policy.types_for(role)}
        visible: dict[str, str] = {}
        for key in self.db.keys(group):
            if self.db.query(group, key, day) is None:                          # 등록 전 레코드는 발견되지 않는다
                continue
            for kind, tmpl in self._kind_templates:
                if kind in allowed and (m := _template_regex(tmpl, group).match(key)):
                    visible.setdefault(m["entity"], kind)
        names = self.aliases.get(group, {})
        found = sorted(e for e in visible if q in norm(e) or any(q in norm(a) for a in names.get(e, [])))
        log.update(matches=len(found))
        if not found:
            return self._miss("NOT_FOUND", log)
        lim = self.policy.search_limit
        entities = [{"entity": e, "kind": self.policy.entity_names[visible[e]], "name": (names.get(e) or [e])[0]}
                    for e in found[:lim]]
        return self._hit(log, {"status": "HIT", "entities": entities, "truncated": len(found) > lim})

    @staticmethod
    def _hit(log: dict, visible: dict) -> tuple[dict, dict]:
        return visible, {**log, "label": "HIT", "visible": "HIT"}

    @staticmethod
    def _miss(label: str, log: dict) -> tuple[dict, dict]:
        status = VISIBLE[label]
        return {"status": status, "hint": HINTS[status]}, {**log, "label": label, "visible": status}
