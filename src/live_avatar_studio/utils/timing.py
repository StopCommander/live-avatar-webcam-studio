"""Frame timing helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager
from collections import deque
from typing import Iterator


class FPSMeter:
    def __init__(self, window: int = 120):
        self._samples: deque[float] = deque(maxlen=window)

    def tick(self) -> None:
        self._samples.append(time.perf_counter())

    @property
    def fps(self) -> float:
        if len(self._samples) < 2:
            return 0.0
        span = self._samples[-1] - self._samples[0]
        return (len(self._samples) - 1) / span if span > 0 else 0.0


@contextmanager
def timed(label: str, sink: list[tuple[str, float]]) -> Iterator[None]:
    t0 = time.perf_counter()
    try:
        yield
    finally:
        sink.append((label, (time.perf_counter() - t0) * 1000.0))