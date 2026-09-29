"""커널 오류 구분: 런을 멈추는 오류와 작업 하나의 실패."""


class FatalError(Exception):
    """런 전체를 멈춰야 하는 오류 (REPLAY 캐시 미스, API 영구 실패). 커널이 삼키지 않는다."""


class AgentFailure(Exception):
    """에이전트가 작업을 끝내지 못함 (format_error, step_limit, budget_exhausted). 답 사건에 사유로 남고 런은 계속된다."""
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class HarnessError(FatalError):
    """과제 수행 중 난 예상 밖 예외 (모델 행동이 아닌 하네스·인프라 오류). 과제를 오답으로 기록하지 않고 실행을
    멈춘다. 자동 재개가 WAL 체크포인트에서 그 라운드를 다시 실행하고(LLM 캐시 재생), 재시작 횟수만 기록한다.
    결정적 버그면 같은 지점에서 되풀이되어 감시 스크립트가 멈추고 알린다."""

