"""Avatar render service. Blends pose -> rig, then rasterizes."""

from __future__ import annotations

import logging

import numpy as np

from live_avatar_studio.models.avatar import AvatarState
from live_avatar_studio.models.frame import FacePose

log = logging.getLogger(__name__)


class RenderService:
    """Turns a FacePose into an avatar frame.

    Backends: 'gl' (moderngl, GPU) and 'cpu' (numpy reference for tests).
    """

    def __init__(self, backend: str = "gl", resolution: tuple[int, int] = (1280, 720)):
        self._backend = backend
        self._resolution = resolution
        self._state: AvatarState | None = None

    def bind(self, state: AvatarState) -> None:
        self._state = state

    def render(self, pose: FacePose) -> np.ndarray:
        if self._state is None:
            raise RuntimeError("no avatar bound to render service")
        # 1) map blendshapes -> rig weights
        weights = self._map_blendshapes(pose.blendshapes)
        # 2) apply head pose to root bone
        self._state.head_rotation = self._quat_to_euler(pose.quaternion)
        # 3) rasterize
        if self._backend == "cpu":
            return self._rasterize_cpu(weights)
        return self._rasterize_gl(weights)

    def _map_blendshapes(self, bs: np.ndarray | None) -> dict[str, float]:
        if bs is None:
            return {}
        names = self._state.rig.blendshape_names  # type: ignore[union-attr]
        return {n: float(bs[i]) for i, n in enumerate(names) if i < len(bs)}

    @staticmethod
    def _quat_to_euler(q: np.ndarray) -> tuple[float, float, float]:
        w, x, y, z = q
        import math
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return roll, pitch, yaw

    def _rasterize_cpu(self, weights: dict[str, float]) -> np.ndarray:
        # Reference rasterizer — solid fill driven by jawOpen. Test-only.
        h, w = self._resolution[1], self._resolution[0]
        intensity = int(255 * min(1.0, weights.get("jawOpen", 0.0)))
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        canvas[..., 2] = intensity
        return canvas

    def _rasterize_gl(self, weights: dict[str, float]) -> np.ndarray:
        raise NotImplementedError("GL backend wired at runtime by platform adapter")