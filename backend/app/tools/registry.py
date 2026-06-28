"""Tool registry: registers tools and dispatches calls by name."""

from __future__ import annotations

from .alarm import AlarmTool
from .base import Tool, ToolResult
from .code_runner import CodeRunnerTool
from .search import WebSearchTool
from .spotify import OpenAppTool
from .weather import WeatherTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict]:
        return [t.schema() for t in self._tools.values()]

    def call(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(output=f"Unknown tool: {name}")
        return tool.run(**kwargs)


def _build_default() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in (
        OpenAppTool(),
        AlarmTool(),
        WebSearchTool(),
        WeatherTool(),
        CodeRunnerTool(),
    ):
        registry.register(tool)
    return registry


default_registry = _build_default()
