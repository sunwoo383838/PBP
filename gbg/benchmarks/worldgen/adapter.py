from gbg.benchmarks.common import PublicScenarioAdapter
from gbg.contracts.schemas import ToolSpec

from . import env_tools


class WorldgenAdapter(PublicScenarioAdapter):
    name = "worldgen"

    def env_tools(self) -> list[ToolSpec]:
        return env_tools.SPECS

    def make_tools(self, stores):
        return env_tools.make_tools(stores)
