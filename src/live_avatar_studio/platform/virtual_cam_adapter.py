"""Virtual camera publisher adapter.

Windows: writes into a DirectShow source filter registered by the user
(typically OBS Virtual Camera, or our own `lavcam` filter shipped in
native/vcam_filter/).
"""

from __future__ import annotations

import platform

import numpy as np


class VirtualCamAdapter:
    def publish(self, frame: np.ndarray) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class OBSVirtualCamAdapter(VirtualCamAdapter):
    def __init__(self, device_name: str = "OBS Virtual Camera"):
        self._device_name = device_name
        self._pipe = None

    def publish(self, frame: np.ndarray) -> None:
        # Frame is BGR HxWx3 uint8. Handed off via shared memory to the
        # DirectShow filter's worker thread.
        if self._pipe is None:
            raise RuntimeError("virtual cam not opened")
        self._pipe.send(frame.tobytes())

    def close(self) -> None:
        if self._pipe is not None:
            self._pipe.close()
            self._pipe = None


def open_virtual_cam(device_name: str) -> VirtualCamAdapter:
    if platform.system() != "Windows":
        raise RuntimeError("virtual cam publish is Windows-only in this build")
    return OBSVirtualCamAdapter(device_name)