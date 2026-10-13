"""Capture service tests using a stub adapter."""

from __future__ import annotations

import numpy as np

from live_avatar_studio.models.frame import Frame
from live_avatar_studio.platform.capture_adapter import CaptureAdapter
from live_avatar_studio.services.capture_service import CaptureService


class _StubAdapter(CaptureAdapter):
    def __init__(self, frames: int = 3):
        self._remaining = frames

    def open(self, width, height, fps): pass
    def close(self): pass

    def read(self) -> np.ndarray:
        if self._remaining <= 0:
            raise RuntimeError("out of stub frames")
        self._remaining -= 1
        return np.zeros((720, 1280, 3), dtype=np.uint8)


def test_capture_stream_yields_frames():
    svc = CaptureService(_StubAdapter(frames=3), width=1280, height=720, fps=120)
    svc.start()
    out = []
    for frame in svc.stream():
        assert isinstance(frame, Frame)
        out.append(frame)
        if len(out) == 3:
            svc.stop()
    assert len(out) == 3


def test_stream_before_start_raises():
    svc = CaptureService(_StubAdapter(), width=640, height=480, fps=30)
    try:
        next(svc.stream())
    except RuntimeError as e:
        assert "not started" in str(e)
    else:
        raise AssertionError("expected RuntimeError")