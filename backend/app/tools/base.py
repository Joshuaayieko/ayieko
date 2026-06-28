"""Base tool interface.

Every tool exposes a name, a human description, a JSON-schema-ish parameter spec
(used both for LLM tool-calling and for client-side validation), and a ``run``
method. Some tools execute server-side (search, weather, code runner) while
others return an *intent* the mobile app fulfils locally (open app, set alarm).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    output: str
    # When set, the mobile client should perform a device action (Android intent
    # to open an app, schedule an alarm, etc.) rather than just display output.
    client_action: dict[str, Any] | None = None


class Tool(abc.ABC):
    name: str = "tool"
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)  # type: ignore[assignment]

    @abc.abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with keyword arguments and return a result."""

    def schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
