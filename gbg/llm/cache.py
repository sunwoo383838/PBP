"""SQLite(WAL 모드) 응답 캐시. 키 = hash(모델, 파라미터, 메시지, 도구).

캐시는 프롬프트 보관소이기도 하다: 요청 원문을 함께 저장하므로 채점기가 WAL의 키로 프롬프트를 되찾는다.
"""
import hashlib
import json
from pathlib import Path

from .sqlite_store import SqliteStore


def canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def request_key(request: dict) -> str:
    return hashlib.sha256(canonical(request).encode()).hexdigest()


class ResponseCache:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = SqliteStore(self.path)                                  # WAL·busy_timeout·잠금 재시도
        self.db.execute("CREATE TABLE IF NOT EXISTS responses (key TEXT PRIMARY KEY, model TEXT NOT NULL, "
                        "request TEXT NOT NULL, response TEXT NOT NULL)")

    def get(self, key: str) -> dict | None:
        rows = self.db.execute("SELECT response FROM responses WHERE key = ?", (key,))
        return json.loads(rows[0][0]) if rows else None

    def request(self, key: str) -> dict | None:
        rows = self.db.execute("SELECT request FROM responses WHERE key = ?", (key,))
        return json.loads(rows[0][0]) if rows else None

    def put(self, key: str, request: dict, response: dict) -> dict:
        """이미 있으면 기존 응답을 유지하고 그것을 돌려준다 (먼저 저장된 응답이 정본)."""
        self.db.execute("INSERT OR IGNORE INTO responses (key, model, request, response) VALUES (?, ?, ?, ?)",
                        (key, request["model"], canonical(request), canonical(response)))
        return self.get(key)

    def __len__(self):
        return self.db.execute("SELECT COUNT(*) FROM responses")[0][0]

    def close(self):
        self.db.close()
