"""worldgen 구조화 조회: 조회 정책(그룹 단위), 엔티티 해소, 레코드 조회, 엔티티 검색.

에이전트는 (entity, record_type)으로만 묻는다. entity는 ID나 알려진 이름(catalog의 이름·별칭)이고, 여기서 canonical
ID와 physical key로 해소한다. 권한은 그룹 단위다: 그 그룹 도메인의 record type을 구성원 전원이 읽는다.
에이전트에게 보이는 상태는 HIT / NOT_FOUND / AMBIGUOUS / INVALID_TYPE 넷뿐이고, 원래 라벨(PERMISSION_DENIED 등)은
obs에만 남는다. NOT_FOUND에는 후보를 싣지 않는다. AMBIGUOUS(같은 이름이 여럿)는 자기 그룹 범위 안의 후보를 ID와 함께
모두 돌려준다 (2026-09-29). 자기 그룹 범위 안 후보가 하나뿐이면 그것으로 조회한다.

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
    "NO_RECORD": "NO_RECORD",                   # 엔티티는 있으나 그 record type 레코드가 (등록된 것으로) 없음
    "PERMISSION_DENIED": "NOT_FOUND",           # 다른 그룹 소속 엔티티
    "AMBIGUOUS": "AMBIGUOUS",
    "UNKNOWN_TYPE": "INVALID_TYPE",
    "TYPE_NOT_PERMITTED": "INVALID_TYPE",       # 그룹 도메인 밖의 record type (백엔드 재검사)
    "KIND_MISMATCH": "INVALID_TYPE",            # 엔티티 종류와 record type이 맞지 않음
    "EMPTY_QUERY": "NOT_FOUND",
}
HINTS = {
    "NOT_FOUND": ("No entity with this name or ID in your area's records. If it belongs to another area, list it under "
                  "missing instead of looking further."),
    "NO_RECORD": ("The entity exists, but no record of this type is registered for it as of today (for example, no "
                  "goods receipt has been registered). Report that no record is registered."),
    "AMBIGUOUS": "The name matches more than one entity. Retry with one of the candidate IDs.",
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
    limit: int | None = Field(None, ge=1)       # None = 상한 없음 (목록 전부)

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
        if self.multi and self.match is None:
            raise ValueError("여러 레코드 유형에는 match가 필요하다")
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


def _names(value, kind: str = "") -> list[str]:
    """catalog 값에서 사람이 부르는 이름들: name, alias, 그리고 이름 필드가 없는 종류의 표기
    (재고 품목 "laptop (basic)", 견적 "V-SEL-0 laptop (basic)"). 이름으로 모든 엔티티 종류를 조회할 수 있게 한다."""
    if not isinstance(value, dict):
        return []
    out = [v for k in ("name", "alias") if isinstance(v := value.get(k), str) and v]
    t, tier = value.get("type"), value.get("tier")
    if kind == "inventory" and t and tier:
        out += [f"{t} ({tier})", f"{t} {tier}", f"in-house stock {t} ({tier})"]
    if kind == "quotes" and t and tier and value.get("vendor"):
        out += [f"{value['vendor']} {t} ({tier})", f"{value['vendor']} {t} {tier}"]
    return out


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
                out[eid] = (self.policy.catalog_kinds[ck], _names(value, ck))
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

    def _held_elsewhere(self, group: str, entity: str, rt) -> bool:
        """이 record type의 레코드를 다른 그룹이 갖고 있거나, 엔티티가 이 type이 다루는 종류가 아니면 True.
        아무 그룹에도 레코드가 없는 이 종류의 엔티티(예: 입고 기록이 아직 없는 가승인)는 '등록된 레코드 없음'이다."""
        if rt.catalog or rt.entity_kind not in self.kinds(entity):
            return True
        return any(self.stores.db.keys(g) and rt.key.format(group=g, entity=entity) in set(self.stores.db.keys(g))
                   for g in self._groups() if g != group)

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
            return self._near(group, entity_text, *self._miss("NOT_FOUND", log))
        if len(cands) > 1:                                                  # 자기 그룹 범위 안 후보로 좁힌다
            own = [c for c in cands if self.in_scope(group, c)]
            if len(own) == 1:
                cands = own
            else:
                vis, lg = self._miss("AMBIGUOUS", log)
                cat = self._catalog_entities(group)
                vis["candidates"] = [{"entity": c, "kind": cat[c][0] if c in cat else sorted(self.kinds(c) or {"entity"})[0],
                                      **({"name": cat[c][1][0]} if c in cat and cat[c][1] else {})} for c in own]
                return vis, {**lg, "candidates_shown": len(own)}
        e = log["entity"] = cands[0]
        kinds = self.kinds(e)
        if rt.entity_kind != "any" and kinds and rt.entity_kind not in kinds:
            return self._miss("KIND_MISMATCH", log)
        if not rt.multi and not self.in_scope(group, e) and self._held_elsewhere(group, e, rt):   # 다른 그룹의 레코드
            return self._near(group, entity_text, *self._miss("PERMISSION_DENIED", log))
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
        shown = hits[: rt.limit] if rt.limit else hits
        log.update(keys=[k for _, k, _ in shown], total=len(hits))
        return self._hit(log, {"status": "HIT", "entity": e, "record_type": name,
                               "records": [{"id": m, "registered_day": v.db_day, "record": v.value} for m, _, v in shown],
                               "truncated": bool(rt.limit) and len(hits) > rt.limit})

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

    def _near(self, group: str, text: str, vis: dict, log: dict, n: int = 3) -> tuple[dict, dict]:
        """NOT_FOUND에 자기 기록 안의 가까운 후보(최대 n)를 붙인다. 다른 그룹의 엔티티는 싣지 않는다."""
        import difflib
        pool = dict(self._catalog_entities(group))
        for e, kinds in self._key_entities(group).items():
            pool.setdefault(e, (sorted(kinds)[0], []))
        surf = {norm(x): e for e, (_, names) in pool.items() for x in (e, *names)}
        close = difflib.get_close_matches(norm(text), list(surf), n=n * 3, cutoff=0.6)
        picked = list(dict.fromkeys(surf[x] for x in close))[:n]
        if picked:
            vis = {**vis, "nearest_in_your_records": [{"entity": e, "kind": pool[e][0],
                                                        **({"name": pool[e][1][0]} if pool[e][1] else {})} for e in picked]}
        return vis, {**log, "near": picked}

    @staticmethod
    def _hit(log: dict, visible: dict) -> tuple[dict, dict]:
        return visible, {**log, "label": "HIT", "visible": "HIT"}

    @staticmethod
    def _miss(label: str, log: dict) -> tuple[dict, dict]:
        status = VISIBLE[label]
        return {"status": status, "hint": HINTS[status]}, {**log, "label": label, "visible": status}
