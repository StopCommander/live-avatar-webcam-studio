"""Top-level orchestrator. Wires capture -> tracking -> render -> publish."""

from __future__ import annotations

import logging
import signal

from live_avatar_studio.config.settings import StudioSettings
from live_avatar_studio.models.avatar import AvatarRig, AvatarState
from live_avatar_studio.platform.capture_adapter import open_default_capture
from live_avatar_studio.platform.virtual_cam_adapter import open_virtual_cam
from live_avatar_studio.services.capture_service import CaptureService
from live_avatar_studio.services.render_service import RenderService
from live_avatar_studio.services.tracking_service import TrackingService

log = logging.getLogger(__name__)


class AvatarStudioService:
    def __init__(self, settings: StudioSettings):
        self._settings = settings
        self._capture = CaptureService(
            open_default_capture(),
            settings.capture_width,
            settings.capture_height,
            settings.capture_fps,
        )
        self._tracking = TrackingService(
            model_path=__import__("pathlib").Path(settings.face_landmark_model),
            device=settings.inference_device,
        )
        self._render = RenderService(
            backend="cpu" if settings.headless else "gl",
            resolution=(settings.capture_width, settings.capture_height),
        )
        self._publisher = (
            open_virtual_cam(settings.virtual_cam_device)
            if settings.publish_virtual_cam
            else None
        )
        self._running = False

    def run_until_interrupt(self) -> None:
        self._running = True
        signal.signal(signal.SIGINT, lambda *_: self.shutdown())
        self._capture.start()
        self._tracking.load()
        self._render.bind(AvatarState(rig=AvatarRig.default_v3()))
        log.info("studio online, rig=%s", self._settings.avatar_rig)

        for frame in self._capture.stream():
            if not self._running:
                break
            pose = self._tracking.infer(frame)
            if pose is None:
                continue
            avatar_frame = self._render.render(pose)
            if self._publisher is not None:
                self._publisher.publish(avatar_frame)

    def shutdown(self) -> None:
        if not self._running:
            return
        self._running = False
        self._capture.stop()
        if self._publisher is not None:
            self._publisher.close()
        log.info("studio offline")