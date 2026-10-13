"""Capture service — wraps the platform adapter, exposes a pull API."""

from __future__ import annotations

import logging
import time
from typing import Iterator

from live_avatar_studio.models.frame import Frame
from live_avatar_studio.platform.capture_adapter import CaptureAdapter

log = logging.getLogger(__name__)


class CaptureService:
    def __init__(self, adapter: CaptureAdapter, width: int, height: int, fps: int):
        self._adapter = adapter
        self._width = width
        self._height = height
        self._fps = fps
        self._running = False

    def start(self) -> None:
        self._adapter.open(self._width, self._height, self._fps)
        self._running = True
        log.info("capture started: %dx%d @ %dfps", self._width, self._height, self._fps)

    def stop(self) -> None:
        self._running = False
        self._adapter.close()

    def stream(self) -> Iterator[Frame]:
        if not self._running:
            raise RuntimeError("capture service not started")
        interval_ns = int(1e9 / self._fps)
        while self._running:
            t0 = time.perf_counter_ns()
            img = self._adapter.read()
            yield Frame(image=img, timestamp_ns=t0)
            elapsed = time.perf_counter_ns() - t0
            if elapsed < interval_ns:
                time.sleep((interval_ns - elapsed) / 1e9)