"""Planner agent — the orchestration core of Orbes.

Pipeline:  goal -> intent detection -> (optional tool calls) -> synthesise answer.

Tool selection here uses lightweight rule-based intent detection so the assistant
is useful even without an LLM API key. When the LLM is live it produces the final
natural-language answer, grounded in any tool output and the user's memories.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..llm import llm
from ..memory import MemoryStore
from ..tools import default_registry
from ..tools.base import ToolResult


@dataclass
class PlanResult:
    reply: str
    plan: list[str] = field(default_factory=list)
    tools_used: list[dict] = field(default_factory=list)


# (tool name, regex, argument extractor)
def _alarm_args(m: re.Match) -> dict:
    text = m.string.lower()
    timer = re.search(r"(\d+)\s*(min|minute|hour|hr|sec|second)", text)
    if timer or "timer" in text:
        dur = timer.group(0) if timer else "5 minutes"
        return {"kind": "timer", "time": dur}
    clock = re.search(r"(\d{1,2}(:\d{2})?\s*(am|pm)?)", text)
    return {"kind": "alarm", "time": clock.group(1) if clock else "07:00"}


INTENTS = [
    ("open_app", re.compile(r"\bopen\s+(?P<app>[a-z]+)", re.I),
     lambda m: {"app": m.group("app")}),
    ("set_alarm", re.compile(r"\b(set (an? )?(alarm|timer)|wake me|remind me at)\b", re.I),
     _alarm_args),
    ("get_weather", re.compile(r"\bweather\b.*\bin\s+(?P<city>[a-z\s]+)", re.I),
     lambda m: {"city": m.group("city").strip()}),
    ("web_search", re.compile(r"\b(search|look up|google|research|latest|news about)\b", re.I),
     lambda m: {"query": m.string}),
]


class PlannerAgent:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory
        self.registry = default_registry

    def _detect_tool(self, message: str) -> tuple[str, dict] | None:
        for name, pattern, extractor in INTENTS:
            m = pattern.search(message)
            if m:
                return name, extractor(m)
        return None

    def handle(self, message: str, history: list[dict] | None = None) -> PlanResult:
        history = history or []
        plan: list[str] = ["Understand the request"]
        tools_used: list[dict] = []
        tool_context = ""

        detected = self._detect_tool(message)
        if detected:
            name, args = detected
            plan.append(f"Use tool: {name}")
            result: ToolResult = self.registry.call(name, **args)
            tools_used.append(
                {
                    "name": name,
                    "arguments": args,
                    "result": result.output,
                    "client_action": result.client_action,
                }
            )
            tool_context = f"\n\nTool `{name}` returned:\n{result.output}"

        plan.append("Compose the answer")

        # Build the LLM prompt with memory + tool context.
        system_extra = self.memory.context_block() if self.memory else ""
        messages = list(history)
        user_content = message + tool_context
        messages.append({"role": "user", "content": user_content})

        system = None
        if system_extra:
            from ..llm import SYSTEM_PROMPT

            system = f"{SYSTEM_PROMPT}\n\n{system_extra}"

        reply = llm.complete(messages, system=system)

        # If a client action was produced, make sure it's surfaced even offline.
        if tools_used and tools_used[-1].get("client_action") and not llm.is_live:
            reply = tools_used[-1]["result"]

        return PlanResult(reply=reply, plan=plan, tools_used=tools_used)
