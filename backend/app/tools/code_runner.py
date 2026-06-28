"""Code runner tool.

Executes short Python snippets in a restricted subprocess with a timeout. This is
a *development* sandbox only — for production, run untrusted code inside a
container with no network, dropped privileges, and strict resource limits.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult

MAX_OUTPUT = 4000


class CodeRunnerTool(Tool):
    name = "run_python"
    description = "Run a short Python snippet and return stdout/stderr (sandboxed)."
    parameters = {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python source to execute."},
            "timeout": {"type": "integer", "default": 8},
        },
        "required": ["code"],
    }

    def run(self, **kwargs: Any) -> ToolResult:
        code = str(kwargs.get("code", ""))
        timeout = min(int(kwargs.get("timeout", 8)), 30)
        if not code.strip():
            return ToolResult(output="No code provided.")

        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "snippet.py"
            script.write_text(code)
            try:
                proc = subprocess.run(
                    [sys.executable, "-I", str(script)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                return ToolResult(output=f"Execution timed out after {timeout}s.")

        out = (proc.stdout + proc.stderr)[:MAX_OUTPUT]
        return ToolResult(output=out or "(no output)")
