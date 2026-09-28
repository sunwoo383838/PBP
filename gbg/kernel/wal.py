"""라운드 커밋 WAL.

커밋 순서: 사건을 wal/events.jsonl에 쓰고 → 그룹·obs 파일로 나눠 쓰고(flush + fsync) → round_commit 표시를 쓰고
flush + fsync. 재개 시에는 마지막 round_commit까지만 인정하고, 그룹·obs 파일은 그 seq 이후를 잘라낸다.
"""
import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from gbg.contracts.events import Event

Fault = Callable[[str, dict], None]


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sync(f):
    f.flush()
    os.fsync(f.fileno())


class WAL:
    def __init__(self, run_dir: Path, fault: Fault | None = None):
        self.dir = Path(run_dir)
        self.path = self.dir / "wal" / "events.jsonl"
        self.fault = fault or (lambda point, info: None)

    def side_files(self) -> list[Path]:
        return sorted(p for sub in ("groups", "obs") for p in (self.dir / sub).glob("*.jsonl"))

    def recover(self) -> list[Event]:
        """커밋된 사건(round_commit 포함)을 돌려주고, 그 뒤의 흔적을 모든 파일에서 지운다."""
        if not self.path.exists():
            return []
        data = self.path.read_bytes()
        committed, pending, pos, cut = [], [], 0, 0
        while (nl := data.find(b"\n", pos)) >= 0:
            try:
                ev = Event.model_validate_json(data[pos:nl])
            except ValidationError:
                break
            pending.append(ev)
            pos = nl + 1
            if ev.type == "round_commit":
                committed += pending
                pending, cut = [], pos
        if cut != len(data):
            with open(self.path, "r+b") as f:
                f.truncate(cut)
                _sync(f)
        last = committed[-1].seq if committed else 0
        for p in self.side_files():
            self._truncate_side(p, last)
        return committed

    @staticmethod
    def _truncate_side(path: Path, last_seq: int):
        raw = path.read_bytes()
        keep, pos = 0, 0
        while (nl := raw.find(b"\n", pos)) >= 0:
            try:
                seq = json.loads(raw[pos:nl])["seq"]
            except (ValueError, KeyError, TypeError):
                break
            if seq > last_seq:
                break
            pos = keep = nl + 1
        if keep != len(raw):
            with open(path, "r+b") as f:
                f.truncate(keep)
                _sync(f)

    def commit(self, events: list[Event], side: dict[str, list[dict]]):
        """events의 마지막은 round_commit. side는 {"groups/<g>.jsonl" | "obs/<name>.jsonl": [seq를 가진 기록]}."""
        *body, marker = events
        assert marker.type == "round_commit"
        info = {"day": marker.day, "round": marker.round}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            for ev in body:
                f.write(dumps(ev.model_dump(mode="json")) + "\n")
                f.flush()
                self.fault("wal_event", {**info, "seq": ev.seq})
            _sync(f)
        for rel in sorted(side):
            p = self.dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.writelines(dumps(r) + "\n" for r in side[rel])
                _sync(f)
            self.fault("side_file", {**info, "file": rel})
        self.fault("before_marker", info)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(dumps(marker.model_dump(mode="json")) + "\n")
            _sync(f)

    def hash(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest() if self.path.exists() else ""
