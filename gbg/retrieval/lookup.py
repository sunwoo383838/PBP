"""정확 조회: 그룹 색인 + catalog 한 단계 연결. 모든 경계 조건의 그룹 기록 검색(evidence.py)의 첫 단계다.

    확장   = 조회 엔티티 ∪ 그 엔티티의 catalog 항목이 가리키는 값(연결 필드) ∪ 그 엔티티를 연결 필드로 가리키는
             catalog 항목의 id와 그 항목의 연결 필드 값  (예: 품목 laptop → 견적 Q-… → 공급사 V-…)
    일지   = 확장된 엔티티를 색인 키(entities)로 갖는 일지 항목 (H0 원문)
    처리자 = 확장된 엔티티의 활동 흔적·엔티티 색인이 가리키는 에이전트 (H1)

검색은 여기에 그룹 이력 전체의 엔티티 태그 검색(tag_search)과 하이브리드 검색을 더한다.
"""
from dataclasses import dataclass

from gbg.contracts.schemas import IndexEntry

from .normalize import normalize


@dataclass(frozen=True)
class IndexLookup:
    entities: tuple[str, ...]                   # 확장된 엔티티
    journal: tuple[IndexEntry, ...]
    activity: tuple[IndexEntry, ...]
    holders: tuple[str, ...]


def _mentions(entity: str, text: str) -> bool:
    return normalize(entity) in normalize(text)


def expand(stores, group: str, entities: list[str], link_fields: list[str]) -> list[str]:
    """catalog 한 단계 연결로 엔티티를 넓힌다 (자기 그룹 catalog만)."""
    out = dict.fromkeys(entities)
    items = stores.catalog.items(group)
    for e in entities:
        for key, value in items:
            if not isinstance(value, dict):
                continue
            eid = key.split("/", 1)[-1]
            links = [value[f] for f in link_fields if isinstance(value.get(f), str)]
            if eid == e:                                                 # 자기 항목이 가리키는 값
                out.update(dict.fromkeys(links))
            elif e in links:                                             # 그 엔티티를 가리키는 항목
                out[eid] = None
                out.update(dict.fromkeys(links))
    return list(out)


def index_lookup(stores, group: str, entities: list[str], link_fields: list[str]) -> IndexLookup:
    ents = expand(stores, group, entities, link_fields)
    keys = set(ents)
    hit = lambda x: not keys.isdisjoint(x.entities)
    journal = tuple(x for x in stores.index.journal(group) if hit(x))
    activity = tuple(x for x in stores.index.activity(group) if hit(x))
    holders = dict.fromkeys(x.agent for x in activity)
    for e in ents:
        holders.update(dict.fromkeys(stores.index.holders(group, e)))
    return IndexLookup(tuple(ents), journal, activity, tuple(holders))


def tag_search(stores, agents: list[str], entities: list[str]) -> list[tuple[str, int]]:
    """그룹 이력 전체에서 엔티티 태그가 붙었거나 엔티티를 언급하는 항목 (경계 모듈 전용)."""
    return [(a, e.seq) for a in agents for e in stores.history.entries(a)
            if any(x in e.entities or _mentions(x, e.text) for x in entities)]
