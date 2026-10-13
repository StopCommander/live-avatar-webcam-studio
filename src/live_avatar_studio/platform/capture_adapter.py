"""Capture adapter — dispatches to the right native backend per OS.

Windows -> DirectShow via `lav_capture.dll` (C++ shim in native/capture_shim).
Linux   -> V4L2 via OpenCV.
macOS   -> AVFoundation via OpenCV.
"""

from __future__ import annotations

import platform
import ctypes
from pathlib import Path

import numpy as np


class CaptureAdapter:
    def open(self, width: int, height: int, fps: int) -> None:
        raise NotImplementedError

    def read(self) -> np.ndarray:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class OpenCVCaptureAdapter(CaptureAdapter):
    def __init__(self, index: int = 0):
        self._index = index
        self._cap = None

    def open(self, width: int, height: int, fps: int) -> None:
        import cv2
        self._cap = cv2.VideoCapture(self._index, cv2.CAP_V4L2)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._cap.set(cv2.CAP_PROP_FPS, fps)

    def read(self) -> np.ndarray:
        ok, frame = self._cap.read()
        if not ok:
            raise RuntimeError("capture read failed")
        return frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()


class DirectShowCaptureAdapter(CaptureAdapter):
    """Windows path: loads the C++ shim and calls lav_open/lav_read/lav_close."""

    _DLL_NAME = "lav_capture.dll"

    def __init__(self, index: int = 0):
        self._index = index
        self._dll = None
        self._handle = None

    def open(self, width: int, height: int, fps: int) -> None:
        dll_path = Path(__file__).parent / "native" / self._DLL_NAME
        self._dll = ctypes.CDLL(str(dll_path))
        self._dll.lav_open.restype = ctypes.c_void_p
        self._handle = self._dll.lav_open(self._index, width, height, fps)
        if not self._handle:
            raise RuntimeError(f"lav_open failed for camera {self._index}")

    def read(self) -> np.ndarray:
        # Shim returns a BGR buffer; we copy immediately to own the memory.
        buf = (ctypes.c_uint8 * (1280 * 720 * 3))()
        ok = self._dll.lav_read(self._handle, buf)
        if not ok:
            raise RuntimeError("lav_read returned no frame")
        return np.frombuffer(bytes(buf), dtype=np.uint8).reshape(720, 1280, 3).copy()

    def close(self) -> None:
        if self._dll and self._handle:
            self._dll.lav_close(self._handle)
            self._handle = None


def open_default_capture() -> CaptureAdapter:
    sysname = platform.system()
    if sysname == "Windows":
        return DirectShowCaptureAdapter()
    return OpenCVCaptureAdapter()