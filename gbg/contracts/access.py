"""접근 표 (configs/access.yaml). 선언되지 않은 접근은 전부 거부한다.

주체 종류: agent(agent:<id>), boundary(boundary:<group>), kernel.
scope: own = 주체와 같은 그룹 (own_history는 주체 자신), other = 다른 그룹, any = 그룹 없는 전역 자원.
perm: r, w, rw, context (context = ContextBuilder를 통해서만 컨텍스트에 들어옴, 직접 읽기 아님).
"""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import ValidationError

from ._base import Contract
from .conditions import Condition, ConfigError

Perm = Literal["r", "w", "rw", "context"]
Action = Literal["r", "w", "context"]
Scope = Literal["own", "other", "any"]


class AccessRule(Contract):
    subject: str
    resource: str
    scope: Scope
    perm: Perm


class AccessFile(Contract):
    subjects: list[str]
    resources: dict[str, Literal["agent", "group", "global"]]   # 자원 이름 → 소유 단위
    rules: list[AccessRule]
    overrides: dict[str, list[AccessRule]] = {}                  # 조건 이름 → 추가로 허용하는 규칙


class AccessTable:
    def __init__(self, spec: AccessFile, conditions: dict[str, Condition]):
        self.spec, self.conditions = spec, conditions
        self._check()

    def _check(self):
        s = self.spec
        for cond, rules in s.overrides.items():
            if cond not in self.conditions:
                raise ConfigError(f"접근 표 overrides: 존재하지 않는 조건 '{cond}'")
        for rule in s.rules + [r for rs in s.overrides.values() for r in rs]:
            if rule.subject not in s.subjects:
                raise ConfigError(f"접근 표: 존재하지 않는 주체 '{rule.subject}'")
            if rule.resource not in s.resources:
                raise ConfigError(f"접근 표: 존재하지 않는 자원 '{rule.resource}'")
            is_global = s.resources[rule.resource] == "global"
            if is_global != (rule.scope == "any"):
                raise ConfigError(f"접근 표: {rule.resource}에 scope '{rule.scope}'는 맞지 않음")
            if rule.resource == "private":
                raise ConfigError("접근 표: private은 누구에게도 허용할 수 없다")

    def allows(self, subject: str, action: Action, resource: str, scope: Scope, condition: str) -> bool:
        s = self.spec
        if subject not in s.subjects:
            raise ConfigError(f"존재하지 않는 주체 '{subject}'")
        if resource not in s.resources:
            raise ConfigError(f"존재하지 않는 자원 '{resource}'")
        if condition not in self.conditions:
            raise ConfigError(f"존재하지 않는 조건 '{condition}'")
        for rule in s.rules + s.overrides.get(condition, []):
            if (rule.subject, rule.resource, rule.scope) == (subject, resource, scope) and action in _grants(rule.perm):
                return True
        return False


def _grants(perm: Perm) -> set[str]:
    return {"r": {"r"}, "w": {"w"}, "rw": {"r", "w"}, "context": {"context"}}[perm]


def load_access(path: Path, conditions: dict[str, Condition]) -> AccessTable:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    try:
        spec = AccessFile.model_validate(raw)
    except ValidationError as e:
        raise ConfigError(f"{path}: 접근 표 형식 오류\n{e}") from e
    return AccessTable(spec, conditions)
