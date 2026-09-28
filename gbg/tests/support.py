"""테스트 도우미: 픽스처를 실제 벤치마크 어댑터로 읽는다."""
from pathlib import Path

from gbg.benchmarks.silo.adapter import SiloAdapter
from gbg.benchmarks.worldgen.adapter import WorldgenAdapter

FIXTURES = Path(__file__).parent / "fixtures"
ADAPTERS = {"worldgen_mini": WorldgenAdapter, "silo_mini": SiloAdapter}


def load_adapter(name: str):
    a = ADAPTERS[name]()
    a.load(FIXTURES / name / "public")
    return a
