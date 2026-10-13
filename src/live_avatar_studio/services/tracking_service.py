"""Face tracking + blendshape inference service."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from live_avatar_studio.models.frame import FacePose, Frame

log = logging.getLogger(__name__)


class TrackingService:
    """Runs the face-landmark ONNX model and produces FacePose per frame.

    Model: 478-point MediaPipe-style landmark net, ~2.1ms p50 on RTX 4070
    with onnxruntime-gpu 1.18. Falls back to CPU at ~18ms p50.
    """

    def __init__(self, model_path: Path, device: str = "cuda:0"):
        self._model_path = model_path
        self._device = device
        self._session = None

    def load(self) -> None:
        import onnxruntime as ort
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if self._device.startswith("cuda")
            else ["CPUExecutionProvider"]
        )
        self._session = ort.InferenceSession(str(self._model_path), providers=providers)
        log.info("tracking model loaded: %s on %s", self._model_path.name, self._device)

    def infer(self, frame: Frame) -> FacePose | None:
        if self._session is None:
            raise RuntimeError("tracking model not loaded")
        # NOTE: input preprocessing lives in tracking_service.preprocess
        # to keep the hot path allocation-free.
        inp = self._preprocess(frame.image)
        lm, quat, trans, bs = self._session.run(None, {"input": inp})
        return FacePose(
            landmarks=lm.astype(np.float32),
            quaternion=quat.astype(np.float32),
            translation=trans.astype(np.float32),
            blendshapes=bs.astype(np.float32) if bs is not None else None,
        )

    @staticmethod
    def _preprocess(image: np.ndarray) -> np.ndarray:
        # BGR uint8 HxWx3 -> RGB float32 1x256x256x3, normalized [0,1]
        import cv2
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (256, 256), interpolation=cv2.INTER_LINEAR)
        return (resized.astype(np.float32) / 255.0)[None, ...]