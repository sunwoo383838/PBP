from gbg.benchmarks.common import PublicScenarioAdapter
from gbg.contracts.schemas import ToolSpec

from . import env_tools


class WorldgenAdapter(PublicScenarioAdapter):
    name = "worldgen"

    def env_tools(self) -> list[ToolSpec]:
        return env_tools.all_specs()

    def role_tools(self, role: str) -> list[ToolSpec]:
        return env_tools.role_specs(role)

    def make_tools(self, stores):
        return env_tools.make_tools(stores, {g: s.aliases for g, s in self._snap.items()})
