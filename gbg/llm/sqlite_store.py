"""캐시용 SQLite 연결 (LLM 응답·임베딩·재정렬 캐시 공통).

여러 실행이 같은 캐시 파일을 쓰거나, 한 실행 안에서 동시 과제·작업 스레드가 같은 연결을 쓸 때 잠금 오류로 과제가
실패하지 않게 한다: WAL 모드, busy_timeout, 연결 단위 스레드 잠금, "locked"/"busy" 오류의 백오프 재시도(최대 약 10분).
재시도로도 안 되면 CacheLockError(FatalError)로 실행을 멈추고, 자동 재개가 그 라운드부터 다시 돈다.
"""
import sqlite3
import threading
import time
from pathlib import Path

from gbg.kernel.errors import FatalError


class CacheLockError(FatalError):
    """캐시 DB 잠금이 재시도 뒤에도 풀리지 않음 (하네스 인프라 오류, 과제 실패가 아니다)."""


class SqliteStore:
    MAX_WAIT_S = 600.0

    def __init__(self, path: Path, busy_ms: int = 60000):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False, timeout=busy_ms / 1000)
        self.execute(f"PRAGMA busy_timeout={busy_ms}")
        self.execute("PRAGMA journal_mode=WAL")
        self.execute("PRAGMA synchronous=NORMAL")

    def execute(self, sql: str, params=()) -> list:
        """문장 하나를 실행하고 결과 행을 모두 돌려준다. 잠금 오류는 백오프로 재시도한다."""
        waited, delay = 0.0, 0.5
        while True:
            try:
                with self._lock:
                    return self.db.execute(sql, params).fetchall()
            except sqlite3.OperationalError as e:
                msg = str(e).lower()
                if "locked" not in msg and "busy" not in msg:
                    raise
                if waited >= self.MAX_WAIT_S:
                    raise CacheLockError(f"캐시 잠금이 {waited:.0f}초 동안 풀리지 않음: {e}") from e
                d = min(delay, 30.0)                                  # 결정적 백오프 (전역 난수 금지)
                time.sleep(d)
                waited += d
                delay *= 2

    def close(self):
        with self._lock:
            self.db.close()
