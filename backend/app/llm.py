"""LLM client wrapper around Anthropic's Claude models.

Falls back to a deterministic offline reply when no API key is configured, so the
backend stays runnable for development and tests without external calls.
"""

from __future__ import annotations

import logging

from .config import settings

logger = logging.getLogger("orbes.llm")

SYSTEM_PROMPT = (
    "You are Orbes, a helpful, proactive personal AI assistant. "
    "You can plan multi-step tasks, use tools, and remember user preferences. "
    "Be concise, accurate, and cite sources when you research the web. "
    "When you do not know something, say so rather than inventing facts."
)


class LLMClient:
    def __init__(self) -> None:
        self._client = None
        if settings.anthropic_api_key:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception as exc:  # pragma: no cover - import/availability guard
                logger.warning("Anthropic client unavailable: %s", exc)

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def complete(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Return a text completion for a list of {role, content} messages."""
        if not self._client:
            return self._offline_reply(messages)

        try:
            resp = self._client.messages.create(
                model=settings.orbes_llm_model,
                max_tokens=max_tokens or settings.orbes_llm_max_tokens,
                system=system or SYSTEM_PROMPT,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                    if m["role"] in ("user", "assistant")
                ],
            )
            return "".join(
                block.text for block in resp.content if getattr(block, "type", "") == "text"
            ).strip()
        except Exception as exc:  # pragma: no cover - network guard
            logger.error("LLM call failed: %s", exc)
            return (
                "I hit an error reaching the language model. "
                "Please check the ANTHROPIC_API_KEY configuration."
            )

    @staticmethod
    def _offline_reply(messages: list[dict[str, str]]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        return (
            "[Orbes offline mode] I received: "
            f"\"{last_user}\". Configure ANTHROPIC_API_KEY in your .env to enable "
            "full AI responses."
        )


llm = LLMClient()
