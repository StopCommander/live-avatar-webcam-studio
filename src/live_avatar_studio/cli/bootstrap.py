"""Thin CLI bootstrap.

Parses args, wires services, hands off. No business logic lives here —
everything routes through AvatarStudioService.
"""

from __future__ import annotations

import argparse
import logging
import sys

from live_avatar_studio.config.settings import StudioSettings
from live_avatar_studio.services.avatar_studio_service import AvatarStudioService

log = logging.getLogger("live_avatar_studio.cli")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="live-avatar-studio",
        description="Realtime webcam -> AI avatar generator.",
    )
    p.add_argument("--config", default="config/studio.toml")
    p.add_argument("--camera", type=int, default=0, help="webcam index")
    p.add_argument("--virtual-cam", action="store_true",
                   help="publish to virtual camera device")
    p.add_argument("--avatar", default="default_rig_v3")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--verbose", "-v", action="count", default=0)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose > 1 else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    settings = StudioSettings.load(args.config)
    settings.camera_index = args.camera
    settings.avatar_rig = args.avatar
    settings.publish_virtual_cam = args.virtual_cam
    settings.headless = args.headless

    service = AvatarStudioService(settings)
    try:
        service.run_until_interrupt()
    except KeyboardInterrupt:
        log.info("interrupt received, shutting down")
        service.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())