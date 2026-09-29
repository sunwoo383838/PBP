"""worldgen 구조화 조회: 조회 정책(그룹 단위), 엔티티 해소, 레코드 조회, 엔티티 검색.

에이전트는 (entity, record_type)으로만 묻는다. entity는 ID나 알려진 이름(catalog의 이름·별칭)이고, 여기서 canonical
ID와 physical key로 해소한다. 권한은 그룹 단위다: 그 그룹 도메인의 record type을 구성원 전원이 읽는다.
에이전트에게 보이는 상태는 HIT / NOT_FOUND / AMBIGUOUS / INVALID_TYPE 넷뿐이고, 원래 라벨(PERMISSION_DENIED 등)은
obs에만 남는다. NOT_FOUND와 AMBIGUOUS에는 후보를 싣지 않는다.

DB 현재값은 오늘까지 등록된 버전 중 최대 버전이다. catalog는 현재 상태(catalog 이벤트까지 반영)를 쓴다.
"""
import re
import unicodedata
from pathlib import Path

import yaml
from pydantic import Field, ValidationError, model_validator

from gbg.contracts._base import Contract
from gbg.contracts.conditions import ConfigError

POLICY_PATH = Path(__file__).with_name("record_policy.yaml")

# 로그 라벨 → 에이전트에게 보이는 상태
VISIBLE = {
    "HIT": "HIT",
    "NOT_FOUND": "NOT_FOUND",                   # 이름·ID가 어떤 엔티티와도 맞지 않음
    "NO_RECORD": "NOT_FOUND",                   # 엔티티는 있으나 그 record type 레코드가 (등록된 것으로) 없음
    "PERMISSION_DENIED": "NOT_FOUND",           # 다른 그룹 소속 엔티티
    "AMBIGUOUS": "AMBIGUOUS",
    "UNKNOWN_TYPE": "INVALID_TYPE",
    "TYPE_NOT_PERMITTED": "INVALID_TYPE",       # 그룹 도메인 밖의 record type (백엔드 재검사)
    "KIND_MISMATCH": "INVALID_TYPE",            # 엔티티 종류와 record type이 맞지 않음
    "EMPTY_QUERY": "NOT_FOUND",
}
HINTS = {
    "NOT_FOUND": "No matching record. Retry with the entity ID, or use entity.search to find the entity.",
    "AMBIGUOUS": "The name matches more than one entity. Retry with the entity ID, or use entity.search.",
    "INVALID_TYPE": "Use one of the record types listed in the tool definition.",
}


# ─────────────────────────── 조회 정책 ───────────────────────────
class Match(Contract):
    source: str                                 # catalog | db
    field: str
    catalog_kind: str | None = None


class RecordType(Contract):
    domains: list[str] = Field(min_length=1)
    entity_kind: str
    description: str
    key: str | None = None                      # physical key 템플릿: {group}, {entity} 또는 {member}
    catalog: bool = False                       # catalog 항목 자체를 돌려준다
    match: Match | None = None                  # 여러 레코드 유형: member 중 조회 엔티티와 맞는 것
    limit: int | None = Field(None, ge=1)

    @property
    def multi(self) -> bool:
        return bool(self.key and "{member}" in self.key)

    @model_validator(mode="after")
    def _shape(self):
        if self.catalog:
            if self.key:
                raise ValueError("catalog 유형에는 key가 없다")
            return self
        if not self.key or "{group}" not in self.key or (("{entity}" in self.key) == ("{member}" in self.key)):
            raise ValueError(f"key 템플릿은 {{group}}과 {{entity}} 또는 {{member}} 중 하나를 가져야 한다: {self.key}")
        if self.multi and (self.match is None or self.limit is None):
            raise ValueError("여러 레코드 유형에는 match와 limit이 필요하다")
        return self


class RecordPolicy(Contract):
    record_types: dict[str, RecordType]
    catalog_kinds: dict[str, str]
    entity_names: dict[str, str]
    search_limit: int = Field(ge=1)

    @model_validator(mode="after")
    def _refs(self):
        kinds = {t.entity_kind for t in self.record_types.values()} | set(self.catalog_kinds.values())
        if unknown := kinds - set(self.entity_names):
            raise ValueError(f"entity_names에 없는 엔티티 종류 {sorted(unknown)}")
        return self

    def types_for(self, domain: str) -> list[str]:
        return [n for n, t in self.record_types.items() if domain in t.domains]


def load_policy(path: Path = POLICY_PATH) -> RecordPolicy:
    try:
        return RecordPolicy.model_validate(yaml.safe_load(Path(path).read_text(encoding="utf-8")))
    except ValidationError as e:
        raise ConfigError(f"{path}: 조회 정책 오류\n{e}") from e


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


def _names(value) -> list[str]:
    """catalog 값에서 사람이 부르는 이름들 (name, alias)."""
    if not isinstance(value, dict):
        return []
    return [v for k in ("name", "alias") if isinstance(v := value.get(k), str) and v]


# ─────────────────────────── 엔티티와 조회 ───────────────────────────
class RecordService:
    def __init__(self, policy: RecordPolicy, stores, domain_of: dict[str, str]):
        """domain_of: 그룹 → 도메인. 권한은 호출자 그룹의 도메인으로 정한다."""
        self.policy, self.stores, self.domain_of = policy, stores, domain_of
        # 엔티티 종류는 단일 레코드 유형의 키로만 정한다 (여러 레코드 유형의 member는 조회 엔티티와 종류가 다르다)
        self._kind_templates = [(t.entity_kind, t.key) for t in policy.record_types.values() if t.key and not t.multi]

    # ── 엔티티 ──
    def _key_entities(self, group: str, day: int | None = None) -> dict[str, set[str]]:
        """그룹 DB 키에서 뽑은 엔티티 → 종류. day를 주면 그날까지 등록된 키만."""
        out: dict[str, set[str]] = {}
        db = self.stores.db
        for key in db.keys(group):
            if day is not None and db.query(group, key, day) is None:
                continue
            for kind, tmpl in self._kind_templates:
                if m := _template_regex(tmpl, group).match(key):
                    out.setdefault(m["entity"], set()).add(kind)
        return out

    def _catalog_entities(self, group: str) -> dict[str, tuple[str, list[str]]]:
        """catalog의 엔티티 → (종류, 이름들)."""
        out = {}
        for key, value in self.stores.catalog.items(group):
            ck, _, eid = key.partition("/")
            if eid and ck in self.policy.catalog_kinds:
                out[eid] = (self.policy.catalog_kinds[ck], _names(value))
        return out

    def _groups(self) -> list[str]:
        return sorted(self.domain_of)

    def resolve(self, text: str) -> list[str]:
        q = norm(text)
        found = set()
        for g in self._groups():
            for e in self._key_entities(g):
                if norm(e) == q:
                    found.add(e)
            for e, (_, names) in self._catalog_entities(g).items():
                if norm(e) == q or any(norm(n) == q for n in names):
                    found.add(e)
        return sorted(found)

    def kinds(self, entity: str) -> set[str]:
        out = set()
        for g in self._groups():
            out |= self._key_entities(g).get(entity, set())
            if entity in (cat := self._catalog_entities(g)):
                out.add(cat[entity][0])
        return out

    def in_scope(self, group: str, entity: str) -> bool:
        return entity in self._catalog_entities(group) or entity in self._key_entities(group)

    # ── 조회 ──
    def lookup(self, group: str, entity_text: str, record_type: str, day: int) -> tuple[dict, dict]:
        """(에이전트에게 보일 결과, obs 기록)."""
        domain = self.domain_of[group]
        log = {"group": group, "domain": domain, "entity_input": entity_text, "record_type": record_type,
               "entity": None, "candidates": 0, "keys": []}
        rt = self.policy.record_types.get(record_type)
        if rt is None:
            return self._miss("UNKNOWN_TYPE", log)
        if record_type not in self.policy.types_for(domain):                # 백엔드 권한 재검사
            return self._miss("TYPE_NOT_PERMITTED", log)
        cands = self.resolve(entity_text)
        log["candidates"] = len(cands)
        if not cands:
            return self._miss("NOT_FOUND", log)
        if len(cands) > 1:
            return self._miss("AMBIGUOUS", log)
        e = log["entity"] = cands[0]
        kinds = self.kinds(e)
        if rt.entity_kind != "any" and kinds and rt.entity_kind not in kinds:
            return self._miss("KIND_MISMATCH", log)
        if not self.in_scope(group, e):
            return self._miss("PERMISSION_DENIED", log)
        if rt.catalog:
            return self._catalog(group, e, record_type, log)
        return self._multi(group, e, record_type, rt, day, log) if rt.multi else \
            self._single(group, e, record_type, rt, day, log)

    def _catalog(self, group, e, name, log):
        key = self.stores.catalog.entity_keys(group).get(e)
        if key is None:
            return self._miss("NO_RECORD", log)
        log["keys"] = [f"catalog:{key}"]
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name,
                               "record": self.stores.catalog.get(group, key)})

    def _single(self, group, e, name, rt, day, log):
        key = rt.key.format(group=group, entity=e)
        log["keys"] = [key]
        v = self.stores.db.query(group, key, day)
        if v is None:
            return self._miss("NO_RECORD", log)
        log.update(version=v.v)
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name, "registered_day": v.db_day,
                               "record": v.value})

    def _multi(self, group, e, name, rt, day, log):
        pattern = _template_regex(rt.key, group)
        hits = []
        for key in self.stores.db.keys(group):
            if not (m := pattern.match(key)):
                continue
            v = self.stores.db.query(group, key, day)
            if v is None:
                continue
            if rt.match.source == "catalog":
                entry = self.stores.catalog.get(group, f"{rt.match.catalog_kind}/{m['entity']}")
                field_value = entry.get(rt.match.field) if isinstance(entry, dict) else None
            else:
                field_value = v.value.get(rt.match.field) if isinstance(v.value, dict) else None
            if field_value == e:
                hits.append((m["entity"], key, v))
        if not hits:
            return self._miss("NO_RECORD", log)
        hits.sort(key=lambda h: h[0])
        shown = hits[: rt.limit]
        log.update(keys=[k for _, k, _ in shown], total=len(hits))
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name,
                               "records": [{"id": m, "registered_day": v.db_day, "record": v.value} for m, _, v in shown],
                               "truncated": len(hits) > rt.limit})

    def search(self, group: str, query: str, day: int) -> tuple[dict, dict]:
        """자기 그룹의 catalog(현재 상태)와 오늘까지 등록된 DB 레코드의 엔티티 중 ID·이름이 질의를 포함하는 것."""
        log = {"group": group, "query": query}
        q = norm(query)
        if not q:
            return self._miss("EMPTY_QUERY", log)
        visible: dict[str, tuple[str, list[str]]] = {}
        for e, kinds in self._key_entities(group, day).items():
            visible[e] = (sorted(kinds)[0], [])
        for e, (kind, names) in self._catalog_entities(group).items():
            visible[e] = (kind, names)
        found = sorted(e for e, (_, names) in visible.items() if q in norm(e) or any(q in norm(n) for n in names))
        log.update(matches=len(found))
        if not found:
            return self._miss("NOT_FOUND", log)
        lim = self.policy.search_limit
        entities = [{"entity": e, "kind": self.policy.entity_names[visible[e][0]], "name": (visible[e][1] or [e])[0]}
                    for e in found[:lim]]
        return self._hit(log, {"status": "HIT", "entities": entities, "truncated": len(found) > lim})

    @staticmethod
    def _hit(log: dict, visible: dict) -> tuple[dict, dict]:
        return visible, {**log, "label": "HIT", "visible": "HIT"}

    @staticmethod
    def _miss(label: str, log: dict) -> tuple[dict, dict]:
        status = VISIBLE[label]
        return {"status": status, "hint": HINTS[status]}, {**log, "label": label, "visible": status}
