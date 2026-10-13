"""Unit tests for the CPU reference renderer and blendshape mapping."""

from __future__ import annotations

import numpy as np
import pytest

from live_avatar_studio.models.avatar import AvatarRig, AvatarState
from live_avatar_studio.models.frame import FacePose
from live_avatar_studio.services.render_service import RenderService


def _pose(blendshapes: np.ndarray | None = None) -> FacePose:
    return FacePose(
        landmarks=np.zeros((478, 3), dtype=np.float32),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        translation=np.zeros(3, dtype=np.float32),
        blendshapes=blendshapes,
    )


def test_cpu_renderer_returns_correct_shape():
    svc = RenderService(backend="cpu", resolution=(320, 240))
    svc.bind(AvatarState(rig=AvatarRig.default_v3()))
    out = svc.render(_pose())
    assert out.shape == (240, 320, 3)
    assert out.dtype == np.uint8


def test_jaw_open_drives_intensity():
    rig = AvatarRig.default_v3()
    bs = np.zeros(len(rig.blendshape_names), dtype=np.float32)
    bs[rig.blendshape_names.index("jawOpen")] = 1.0
    svc = RenderService(backend="cpu", resolution=(64, 64))
    svc.bind(AvatarState(rig=rig))
    out = svc.render(_pose(bs))
    assert out[..., 2].max() == 255


def test_render_without_bind_raises():
    svc = RenderService(backend="cpu")
    with pytest.raises(RuntimeError, match="no avatar bound"):
        svc.render(_pose())