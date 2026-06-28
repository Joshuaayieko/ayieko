"""Research agent — searches the web, then summarises and cites sources."""

from __future__ import annotations

from ..llm import llm
from ..tools.search import WebSearchTool

RESEARCH_SYSTEM = (
    "You are Orbes' research agent. You search the web, read the results, then "
    "summarise concisely and always cite source URLs. Distinguish facts from "
    "speculation and flag uncertainty."
)


class ResearchAgent:
    def __init__(self) -> None:
        self.search = WebSearchTool()

    def research(self, query: str, max_results: int = 5) -> str:
        findings = self.search.run(query=query, max_results=max_results).output
        prompt = (
            f"Question: {query}\n\nSearch results:\n{findings}\n\n"
            "Write a concise, well-structured answer and cite the sources."
        )
        return llm.complete([{"role": "user", "content": prompt}], system=RESEARCH_SYSTEM)
