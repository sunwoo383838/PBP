"""card 레지스트리와 발행 전 누출 검사.

card는 그룹 밖에 공개되는 역량 광고다. 발행(기본 card, 후임 card, 동적 범위 갱신) 전에 검사하고, 걸리면 발행하지
않고 obs/cards.jsonl에 차단 기록을 남긴다. 실행 중 검사는 카나리 목록 없이 한다: 금액처럼 보이는 표현은 전부 차단
(쉼표 없는 숫자, 만·억 단위, 근사·반올림 표현 포함), 건 id 패턴, 직원 이름·별칭, 길이 상한. 카나리 정규화 매칭과
근사값 경고는 채점기(Stage 7)가 오프라인으로 한다.

구조 갱신(이탈·합류)은 모든 조건에 적용된다. card_mode: dynamic이면 매일 마지막 라운드 커밋 때 활동 색인에서
담당 범위(부서 수준 범주)를 다시 계산해, 바뀌었으면 갱신하고 version을 올린다. 다음 날 첫 라운드부터 보인다.
"""
import json
import re
import unicodedata

from gbg.contracts.card import AgentCard, GroupCard
from gbg.contracts.schemas import GroupSpec

from .activity import ActivityIndex

# ─────────────────────────── 금액 탐지 ───────────────────────────
_NUM = r"\d[\d,.]*"
_CUR = r"(?:[₩¥$€£]|S\$|US\$|KRW|JPY|USD|SGD|EUR|CNY)"
_CUR_WORD = r"(?:원|円|엔|달러|불|위안|元|won|yen|dollars?|KRW|JPY|USD|SGD|EUR|CNY)"
_KO_UNIT = r"(?:천|만|억|조)(?=원|[^가-힣]|$)"                             # 조각·만큼 같은 낱말은 제외
_MAG = rf"(?:{_KO_UNIT}|千|万|億|兆|[kKmMbB](?![a-zA-Z])|mn|bn|million|billion|thousand|mil(?![a-z]))"
_APPROX_PRE = r"(?:약|대략|대충|거의|얼추|최대|최소|約|およそ|ほぼ|approx\.?|approximately|about|around|roughly|nearly|~|〜|≈|±)"
_APPROX_POST = r"(?:정도|가량|내외|안팎|남짓|이상|이하|미만|초과|ほど|前後|程度|くらい|ぐらい|余り|以上|以下|未満|(?:여|강)(?![가-힣]))"
_KO_NUM = r"[일이삼사오육칠팔구십백천수몇]"
_JA_NUM = r"[一二三四五六七八九十百千数]"

AMOUNT_PATTERNS = {
    "currency": re.compile(rf"{_CUR}\s*{_NUM}|{_NUM}\s*{_CUR_WORD}"),
    "grouped_number": re.compile(r"\d{1,3}(?:[,.]\d{3})+"),
    "long_number": re.compile(r"\d{4,}"),
    "magnitude": re.compile(rf"{_NUM}\s*{_MAG}"),
    "numeral_amount": re.compile(rf"{_KO_NUM}+\s*(?:{_KO_UNIT})|{_JA_NUM}+\s*(?:万|億|兆)|(?:hundreds|thousands|millions|billions) of"),
    "approx": re.compile(rf"{_APPROX_PRE}\s*{_NUM}|{_NUM}\s*{_APPROX_POST}"),
}


def amount_reasons(text: str) -> list[str]:
    t = unicodedata.normalize("NFKC", text)
    return [k for k, p in AMOUNT_PATTERNS.items() if p.search(t)]


def looks_like_amount(text: str) -> bool:
    return bool(amount_reasons(text))


_ID = re.compile(r"\b[A-Za-z]{1,6}(?:-[A-Za-z]{1,6})*-\d{2,}\b")          # CMT-00001, E-SEL-1001, W-003
_AGENT_ID = re.compile(r"\b[a-z]+(?:-[a-z]+)+\.[a-z]+\d+\b")               # fin-sel.a3
MAX_FIELD, MAX_CARD = 300, 1500


class CardLeakChecker:
    def __init__(self, names: set[str], allowed: set[str]):
        """names: 직원 이름·별칭·엔티티 id (금지), allowed: 부서 수준 범주 (허용)."""
        self.names = sorted((n for n in names - allowed if n), key=lambda n: (-len(n), n))

    @staticmethod
    def texts(card: AgentCard | GroupCard) -> list[str]:
        scope = card.scope if isinstance(card, AgentCard) else card.service_scope
        out = [card.name, card.description, scope or ""]
        for s in card.skills:
            out += [s.name, s.description, *s.tags, *s.examples]
        return out

    def check(self, card: AgentCard | GroupCard) -> list[str]:
        texts = self.texts(card)
        joined = "\n".join(texts)
        reasons = []
        if any(amount_reasons(t) for t in texts):
            reasons.append("amount")
        if _ID.search(joined) or _AGENT_ID.search(joined):
            reasons.append("id")
        if any(n in joined for n in self.names):
            reasons.append("name")
        if any(len(t) > MAX_FIELD for t in texts) or len(joined) > MAX_CARD:
            reasons.append("length")
        return reasons


class CardLeakError(ValueError):
    """시나리오의 기본 card가 누출 검사를 통과하지 못함."""


# ─────────────────────────── 레지스트리 ───────────────────────────
def _dump(card) -> dict:
    return card.model_dump(mode="json")


class CardRegistry:
    def __init__(self, groups: list[GroupSpec], categories: dict[str, list[str]], names: set[str], card_mode: str):
        self.card_mode = card_mode
        self.categories = {g: list(c) for g, c in categories.items()}
        self.checker = CardLeakChecker(names, {c for cs in categories.values() for c in cs})
        self.agent_cards: dict[str, AgentCard] = {}
        self.group_of: dict[str, str] = {}
        self.active: set[str] = set()
        self.group_cards: dict[str, GroupCard] = {}
        for g in groups:
            for card in [g.card, *(m.card for m in g.members)]:
                if reasons := self.checker.check(card):
                    raise CardLeakError(f"{g.id} 기본 card '{card.name}' 누출 검사 실패: {reasons}")
            self.group_cards[g.id] = g.card
            for m in g.members:
                self.agent_cards[m.agent_id], self.group_of[m.agent_id] = m.card, g.id
                self.active.add(m.agent_id)

    # ── 조회 ──
    def directory(self, kind: str) -> list[AgentCard] | list[GroupCard]:
        if kind == "agent_cards":
            return [self.agent_cards[a] for a in sorted(self.active, key=lambda a: (self.group_of[a], a))
                    if a in self.agent_cards]
        if kind == "group_cards":
            return [self.group_cards[g] for g in sorted(self.group_cards)]
        raise ValueError(f"알 수 없는 디렉터리 '{kind}'")

    def render(self, kind: str) -> str:
        return "\n".join(json.dumps(_dump(c), ensure_ascii=False, sort_keys=True) for c in self.directory(kind))

    # ── 발행 ──
    def _publish(self, card, target: str, day: int, seq: int) -> tuple[bool, list]:
        reasons = self.checker.check(card)
        if not reasons:
            return True, []
        return False, [("cards", {"seq": seq, "day": day, "target": target, "kind": card.kind, "status": "blocked",
                                  "reasons": reasons, "attempt": _dump(card)})]

    def leave(self, agent: str):
        self.active.discard(agent)

    def join(self, agent: str, group: str, from_agent: str | None, day: int, seq: int) -> list:
        """후임은 전임 역할의 card를 그대로 이어받는다(점유자 교체, version 증가)."""
        self.group_of[agent] = group
        prev = self.agent_cards.get(from_agent) if from_agent else None
        if prev is None:
            return []
        card = prev.model_copy(update={"occupant": agent, "version": prev.version + 1})
        ok, obs = self._publish(card, agent, day, seq)
        if ok:
            self.agent_cards[agent] = card
            self.active.add(agent)
        return obs

    def update_scope(self, agent: str, scope: str, day: int, seq: int) -> list:
        cur = self.agent_cards[agent]
        if cur.scope == scope:
            return []
        card = cur.model_copy(update={"scope": scope, "version": cur.version + 1})
        ok, obs = self._publish(card, agent, day, seq)
        if ok:
            self.agent_cards[agent] = card
        return obs

    # ── 동적 card (범위 갱신) ──
    def summarize(self, agent: str, cats: list[str]) -> str | None:
        if not cats:
            return None
        return f"담당 범위: {'·'.join(cats)} {self.agent_cards[agent].skills[0].name}"

    def day_end(self, day: int, activity: ActivityIndex, seq: int) -> list:
        if self.card_mode != "dynamic":
            return []
        obs = []
        for agent in sorted(self.active):
            g = self.group_of[agent]
            recs = activity.by_agent(g).get(agent, [])
            cats = sorted({r.entity for r in recs} & set(self.categories.get(g, [])))
            scope = self.summarize(agent, cats)
            if scope is not None:
                obs += self.update_scope(agent, scope, day, seq)
        return obs

    def dump(self):
        return {"agent_cards": {a: _dump(c) for a, c in sorted(self.agent_cards.items())},
                "group_cards": {g: _dump(c) for g, c in sorted(self.group_cards.items())},
                "active": sorted(self.active)}
