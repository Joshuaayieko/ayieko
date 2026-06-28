"""Web search / research tool.

Uses the Tavily API when ``TAVILY_API_KEY`` is configured; otherwise returns a
graceful placeholder so the assistant degrades nicely offline.
"""

from __future__ import annotations

from typing import Any

import httpx

from ..config import settings
from .base import Tool, ToolResult


class WebSearchTool(Tool):
    name = "web_search"
    description = (
        "Search the web for up-to-date information and return summarised results "
        "with source URLs."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."},
            "max_results": {"type": "integer", "default": 5},
        },
        "required": ["query"],
    }

    def run(self, **kwargs: Any) -> ToolResult:
        query = str(kwargs.get("query", "")).strip()
        max_results = int(kwargs.get("max_results", 5))
        if not query:
            return ToolResult(output="No search query provided.")

        if not settings.tavily_api_key:
            return ToolResult(
                output=(
                    f"[search unavailable] Set TAVILY_API_KEY to enable live web "
                    f"research for: '{query}'."
                )
            )

        try:
            resp = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                },
                timeout=20.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # pragma: no cover - network guard
            return ToolResult(output=f"Search failed: {exc}")

        lines = []
        if data.get("answer"):
            lines.append(f"Answer: {data['answer']}")
        for item in data.get("results", [])[:max_results]:
            lines.append(f"- {item.get('title')} — {item.get('url')}")
        return ToolResult(output="\n".join(lines) or "No results found.")
