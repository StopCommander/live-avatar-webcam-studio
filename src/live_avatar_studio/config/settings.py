"""Studio settings model. Loaded from TOML, overridable by CLI."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass(slots=True)
class StudioSettings:
    camera_index: int = 0
    capture_width: int = 1280
    capture_height: int = 720
    capture_fps: int = 30
    avatar_rig: str = "default_rig_v3"
    inference_backend: str = "onnxruntime"
    inference_device: str = "cuda:0"
    publish_virtual_cam: bool = False
    virtual_cam_device: str = "OBS Virtual Camera"
    headless: bool = False
    face_landmark_model: str = "models/face_landmark_478.onnx"
    avatar_blend_model: str = "models/avatar_blend_v3.onnx"
    extra: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "StudioSettings":
        p = Path(path)
        if not p.exists():
            return cls()
        raw = tomllib.loads(p.read_text(encoding="utf-8"))
        known = {f for f in cls.__dataclass_fields__ if f != "extra"}
        kwargs = {k: v for k, v in raw.items() if k in known}
        extra = {k: v for k, v in raw.items() if k not in known}
        inst = cls(**kwargs)
        inst.extra = extra
        return inst

    def as_dict(self) -> dict:
        return asdict(self)