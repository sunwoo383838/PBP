"""모든 도구 호출 전에 (주체, 행동, 자원, 조건)을 접근 표로 확인한다. 판정은 전부 obs/access.jsonl에 남는다."""
from gbg.contracts.access import AccessTable

from .tools import Resource


class AccessGuard:
    def __init__(self, table: AccessTable, condition: str):
        self.table, self.condition = table, condition

    def check(self, subject: str, subject_group: str, resource: Resource, args: dict, tool: str) -> dict:
        """판정 기록을 돌려준다. record["allowed"]가 결과다."""
        kind, _, sid = subject.partition(":")
        unit = self.table.spec.resources[resource.name]
        target = args.get(resource.target) if resource.target else None
        if unit == "global":
            scope, target = "any", None
        elif unit == "agent":
            target = target or sid
            scope = "own" if target == sid else "other"
        else:
            target = target or subject_group
            scope = "own" if target == subject_group else "other"
        allowed = self.table.allows(kind, resource.action, resource.name, scope, self.condition)
        return {"subject": subject, "tool": tool, "action": resource.action, "resource": resource.name,
                "scope": scope, "target": target, "condition": self.condition, "allowed": allowed}
