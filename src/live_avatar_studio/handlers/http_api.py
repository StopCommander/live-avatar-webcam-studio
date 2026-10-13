"""Thin HTTP handler. JSON in, JSON out. All logic in services."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import json

from live_avatar_studio.services.avatar_studio_service import AvatarStudioService


class StudioHTTPHandler(BaseHTTPRequestHandler):
    service: AvatarStudioService  # injected by the server

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200, {"ok": True})
        elif self.path == "/avatar":
            self._json(200, {"rig": self.service._settings.avatar_rig})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/shutdown":
            self.service.shutdown()
            self._json(200, {"ok": True})
        else:
            self._json(404, {"error": "not found"})

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:  # silence default stderr spam
        return