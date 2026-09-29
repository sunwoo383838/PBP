"""과제 예산: 과제 하나의 LLM 호출 수·토큰을 요청자·응답자(중첩 포함)·경계 모듈 합산으로 센다.

상한(B_CALLS, B_TOKENS)은 모든 조건에 같고, 최종 답변용 호출과 토큰은 따로 남겨 둔다. 최종 답변이 아닌 호출은
예약분을 침범하면 거부되고(budget_exhausted), 요청자는 예약된 호출로 그때까지의 정보로 답한다.
상한이 없으면(null) 거부 없이 소비량만 기록한다.
"""
from dataclasses import asdict, dataclass, field

from gbg.contracts.conditions import Budget, Defaults, FinalReserve, RequesterPolicy

from .errors import AgentFailure

COMPONENTS = ("requester", "responder", "boundary")


class BudgetExhausted(AgentFailure):
    def __init__(self):
        super().__init__("budget_exhausted")


UNLIMITED = Defaults(budget=Budget(calls=None, tokens=None), final_reserve=FinalReserve(calls=1, tokens=0),
                     requester=RequesterPolicy(max_asks=None, requery=True))


@dataclass
class Usage:
    calls: int = 0
    tokens: int = 0
    directory_tokens: int = 0
    tool_def_tokens: int = 0


@dataclass
class TaskBudget:
    task_id: str
    requester: str
    defaults: Defaults
    by: dict[str, Usage] = field(default_factory=lambda: {c: Usage() for c in COMPONENTS})
    exhausted: bool = False
    final_used: bool = False
    asks: int = 0
    asked: set = field(default_factory=set)

    @property
    def calls(self) -> int:
        return sum(u.calls for u in self.by.values())

    @property
    def tokens(self) -> int:
        return sum(u.tokens for u in self.by.values())

    def admit(self, final: bool, estimate: int = 0):
        """이 호출을 해도 되는가. 안 되면 BudgetExhausted.

        estimate는 호출 전에 센 프롬프트 토큰 추정치다. 비최종 호출은 (사용량 + 추정치 + 예약 토큰) ≤ 상한일 때만
        허용하므로, 토큰 상한은 출력 토큰만큼만 넘을 수 있다. 최종 호출은 예약분이라 토큰으로는 막지 않는다.
        """
        lim, res = self.defaults.budget, self.defaults.final_reserve
        if final:
            ok = lim.calls is None or self.calls < lim.calls
        else:
            ok = (lim.calls is None or self.calls + 1 + res.calls <= lim.calls) and \
                 (lim.tokens is None or self.tokens + estimate + res.tokens <= lim.tokens)
        if not ok:
            self.exhausted = True
            raise BudgetExhausted()

    def charge(self, component: str, usage: dict, composition: dict | None, final: bool):
        u = self.by[component]
        u.calls += 1
        u.tokens += int(usage.get("prompt_tokens", 0)) + int(usage.get("completion_tokens", 0))
        if composition:
            u.directory_tokens += int(composition.get("directory_tokens", 0))
            u.tool_def_tokens += int(composition.get("tool_def_tokens", 0))
        self.final_used = self.final_used or final

    def summary(self) -> dict:
        return {"limit": self.defaults.budget.model_dump(), "reserve": self.defaults.final_reserve.model_dump(),
                "used": {"calls": self.calls, "tokens": self.tokens},
                "by_component": {c: asdict(u) for c, u in self.by.items()},
                "budget_exhausted": self.exhausted, "final_call_used": self.final_used, "requester_asks": self.asks}
