"""Vision agent — analyses images (PDFs, screenshots, diagrams, handwriting).

Sends base64 image data to a vision-capable Claude model. Falls back to a clear
message when no API key is configured.
"""

from __future__ import annotations

import logging

from ..config import settings

logger = logging.getLogger("orbes.vision")

VISION_SYSTEM = (
    "You are Orbes' vision agent. Describe images accurately, extract text (OCR), "
    "read diagrams and handwriting, and solve math shown in pictures. State clearly "
    "when something is illegible."
)


class VisionAgent:
    def __init__(self) -> None:
        self._client = None
        if settings.anthropic_api_key:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception as exc:  # pragma: no cover
                logger.warning("Vision client unavailable: %s", exc)

    def analyze(self, image_base64: str, media_type: str, prompt: str) -> str:
        if not self._client:
            return (
                "[vision offline] Configure ANTHROPIC_API_KEY to enable image "
                "understanding."
            )
        try:
            resp = self._client.messages.create(
                model=settings.orbes_llm_model,
                max_tokens=settings.orbes_llm_max_tokens,
                system=VISION_SYSTEM,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {"type": "text", "text": prompt or "Describe this image."},
                        ],
                    }
                ],
            )
            return "".join(
                b.text for b in resp.content if getattr(b, "type", "") == "text"
            ).strip()
        except Exception as exc:  # pragma: no cover
            logger.error("Vision call failed: %s", exc)
            return f"Vision analysis failed: {exc}"
