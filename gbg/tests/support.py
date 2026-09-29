"""테스트 도우미: 픽스처를 실제 벤치마크 어댑터로 읽는다."""
from pathlib import Path

from gbg.benchmarks.silo.adapter import SiloAdapter
from gbg.benchmarks.worldgen.adapter import WorldgenAdapter

FIXTURES = Path(__file__).parent / "fixtures"
ADAPTERS = {"worldgen_mini": (WorldgenAdapter, "harness"), "silo_mini": (SiloAdapter, "public")}


def load_adapter(name: str):
    cls, sub = ADAPTERS[name]
    a = cls()
    a.load(FIXTURES / name / sub)
    return a
