"""그룹별 규정 본문. 파라미터 파일은 private에만 있고 여기에는 존재하지 않는다."""
from gbg.contracts.schemas import RuleText


class Rulebook:
    def __init__(self, rules: dict[str, list[RuleText]]):
        self._rules = {g: {r.id: r for r in rs} for g, rs in rules.items()}

    def read(self, group: str, rule_id: str) -> RuleText | None:
        return self._rules.get(group, {}).get(rule_id)

    def read_all(self, group: str) -> list[RuleText]:
        return [self._rules[group][k] for k in sorted(self._rules.get(group, {}))]

    def search(self, group: str, text: str) -> list[RuleText]:
        return [r for r in self.read_all(group) if text and (text in r.body or text in r.id)]

    def dump(self):
        return {g: [r.model_dump(mode="json") for r in self.read_all(g)] for g in sorted(self._rules)}
