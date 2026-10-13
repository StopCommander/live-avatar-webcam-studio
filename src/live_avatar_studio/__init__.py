"""live-avatar-webcam-studio.

Realtime webcam -> AI avatar generator. Service-oriented architecture:
thin CLI/HTTP handlers, business services, domain models, and platform
adapters for capture, inference, and virtual-camera output.

Python 3.11+. See pyproject.toml for the full dependency surface.
"""

from live_avatar_studio.version import __version__, BUILD_CHANNEL

__all__ = ["__version__", "BUILD_CHANNEL"]