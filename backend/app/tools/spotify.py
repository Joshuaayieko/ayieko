"""App-launch / Spotify tool.

Returns a ``client_action`` instructing the mobile app to launch an installed
app via an Android intent (or URL scheme on iOS).
"""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolResult

# Friendly name -> Android package name.
KNOWN_APPS = {
    "spotify": "com.spotify.music",
    "whatsapp": "com.whatsapp",
    "chrome": "com.android.chrome",
    "camera": "android.media.action.IMAGE_CAPTURE",
    "youtube": "com.google.android.youtube",
    "maps": "com.google.android.apps.maps",
    "gmail": "com.google.android.gm",
}


class OpenAppTool(Tool):
    name = "open_app"
    description = "Open an installed app on the user's phone (e.g. Spotify, WhatsApp)."
    parameters = {
        "type": "object",
        "properties": {
            "app": {
                "type": "string",
                "description": "App name, e.g. 'spotify', 'whatsapp', 'camera'.",
            }
        },
        "required": ["app"],
    }

    def run(self, **kwargs: Any) -> ToolResult:
        app = str(kwargs.get("app", "")).lower().strip()
        package = KNOWN_APPS.get(app)
        return ToolResult(
            output=f"Opening {app.title()}." if package else f"I don't know how to open '{app}'.",
            client_action={"type": "open_app", "app": app, "package": package}
            if package
            else None,
        )
