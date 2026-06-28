"""Weather tool backed by OpenWeather (current conditions)."""

from __future__ import annotations

from typing import Any

import httpx

from ..config import settings
from .base import Tool, ToolResult


class WeatherTool(Tool):
    name = "get_weather"
    description = "Get the current weather for a city."
    parameters = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Nairobi'."},
            "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"},
        },
        "required": ["city"],
    }

    def run(self, **kwargs: Any) -> ToolResult:
        city = str(kwargs.get("city", "")).strip()
        units = kwargs.get("units", "metric")
        if not city:
            return ToolResult(output="No city provided.")

        if not settings.openweather_api_key:
            return ToolResult(
                output=f"[weather unavailable] Set OPENWEATHER_API_KEY to get weather for {city}."
            )

        try:
            resp = httpx.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "units": units,
                    "appid": settings.openweather_api_key,
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # pragma: no cover - network guard
            return ToolResult(output=f"Weather lookup failed: {exc}")

        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        unit = "°C" if units == "metric" else "°F"
        return ToolResult(output=f"Weather in {city}: {desc}, {temp}{unit}.")
