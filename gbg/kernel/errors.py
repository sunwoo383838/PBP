"""커널 오류 구분: 런을 멈추는 오류와 작업 하나의 실패."""


class FatalError(Exception):
    """런 전체를 멈춰야 하는 오류 (REPLAY 캐시 미스, API 영구 실패). 커널이 삼키지 않는다."""


class AgentFailure(Exception):
    """에이전트가 작업을 끝내지 못함 (format_error, step_limit, budget_exhausted). 답 사건에 사유로 남고 런은 계속된다."""
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
