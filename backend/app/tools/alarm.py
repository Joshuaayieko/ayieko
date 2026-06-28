"""Alarm / timer tool.

The backend can't ring the user's phone, so this tool returns a structured
``client_action`` that the Flutter app maps to Android's AlarmManager / iOS
local notifications.
"""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolResult


class AlarmTool(Tool):
    name = "set_alarm"
    description = "Set an alarm or countdown timer on the user's device."
    parameters = {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["alarm", "timer"]},
            "time": {
                "type": "string",
                "description": "For alarms: HH:MM (24h). For timers: duration like '20m'.",
            },
            "label": {"type": "string", "description": "Optional label for the alarm."},
        },
        "required": ["kind", "time"],
    }

    def run(self, **kwargs: Any) -> ToolResult:
        kind = kwargs.get("kind", "alarm")
        time = kwargs.get("time", "")
        label = kwargs.get("label", "")
        verb = "Alarm" if kind == "alarm" else "Timer"
        return ToolResult(
            output=f"{verb} request prepared for {time}"
            + (f" ({label})" if label else "")
            + ".",
            client_action={
                "type": "set_alarm",
                "kind": kind,
                "time": time,
                "label": label,
            },
        )
