"""Coding agent — writes, explains, debugs and runs code."""

from __future__ import annotations

from ..llm import llm
from ..tools.code_runner import CodeRunnerTool

CODING_SYSTEM = (
    "You are Orbes' coding agent. Write clean, correct, well-documented code in "
    "Python, Java, JavaScript, C++, HTML, CSS and SQL. Explain your reasoning, "
    "point out edge cases, and prefer standard idioms. When asked to debug, "
    "identify the root cause before proposing a fix."
)


class CodingAgent:
    def __init__(self) -> None:
        self.runner = CodeRunnerTool()

    def assist(self, prompt: str) -> str:
        return llm.complete([{"role": "user", "content": prompt}], system=CODING_SYSTEM)

    def run_python(self, code: str, timeout: int = 8) -> str:
        return self.runner.run(code=code, timeout=timeout).output
