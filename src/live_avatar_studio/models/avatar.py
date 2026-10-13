"""Avatar rig definition + runtime state."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AvatarRig:
    name: str
    rig_path: Path
    bone_count: int
    blendshape_names: tuple[str, ...]
    texture_resolution: tuple[int, int] = (2048, 2048)

    @classmethod
    def default_v3(cls) -> "AvatarRig":
        return cls(
            name="default_rig_v3",
            rig_path=Path("assets/rigs/default_rig_v3.glb"),
            bone_count=173,
            blendshape_names=(
                "browDownLeft", "browDownRight", "browInnerUp",
                "eyeBlinkLeft", "eyeBlinkRight", "jawOpen",
                "mouthSmileLeft", "mouthSmileRight",
            ),
        )


@dataclass(slots=True)
class AvatarState:
    rig: AvatarRig
    active_expression: str = "neutral"
    head_rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    dirty: bool = field(default=True)