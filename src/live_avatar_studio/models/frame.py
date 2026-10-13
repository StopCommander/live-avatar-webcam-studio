"""Frame + pose domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(slots=True)
class Frame:
    """A single captured frame. BGR, uint8, HxWx3."""
    image: np.ndarray
    timestamp_ns: int
    source: str = "webcam"

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.image.shape  # type: ignore[return-value]


@dataclass(slots=True)
class FacePose:
    """478-point landmark set + derived head pose."""
    landmarks: np.ndarray          # (478, 3) float32, normalized
    quaternion: np.ndarray         # (4,) float32, wxyz
    translation: np.ndarray        # (3,) float32
    blendshapes: Optional[np.ndarray] = None  # (52,) float32