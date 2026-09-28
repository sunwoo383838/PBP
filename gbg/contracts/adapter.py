"""벤치마크 어댑터. 러너는 run(adapter, condition, model, seed) 하나이고, 코어는 이 인터페이스만 안다.

벤치마크별 코드는 gbg/benchmarks/<name>/ 어댑터에만 둔다.
"""
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, runtime_checkable

from .schemas import GroupInit, GroupSpec, Need, TimelineEvent, ToolSpec, Verdict


@runtime_checkable
class BenchmarkAdapter(Protocol):
    name: str

    def load(self, public_dir: Path) -> None: ...                           # private 접근 금지
    def groups(self) -> list[GroupSpec]: ...                                # 그룹 id, 구성원(에이전트 id, 역할), card
    def initial_state(self, group: str) -> GroupInit: ...                   # 초기 이력, 활동 색인, 일지, egress_log 시드, 환경 상태
    def events(self) -> Iterator[TimelineEvent]: ...                        # 완전 정렬된 타임라인 (local | cross | world)
    def env_tools(self) -> list[ToolSpec]: ...                              # 벤치마크 고유 환경 도구와 필요한 접근 자원
    def tag(self, group: str, text: str) -> list[str]: ...                  # 에이전트 발화의 엔티티 태깅

    # 오프라인 (채점기에서만 호출)
    def verify(self, task_id: str, answer: dict, private_dir: Path) -> Verdict: ...
    def needs(self, task_id: str, private_dir: Path) -> list[Need] | None: ...  # None이면 게이트 귀속 생략
