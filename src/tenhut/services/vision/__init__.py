"""Camera surveillance (optional, off by default): head pose, monitors and the camera thread."""

from .camera_dependencies import CameraDependencies
from .camera_watcher import CameraWatcher
from .capture_api import CaptureApi
from .face_landmark_model import FaceLandmarkModel
from .fallback_monitor_provider import FallbackMonitorProvider
from .gaze_state import GazeState
from .gnome_monitors_xml_provider import GnomeMonitorsXmlProvider
from .head_pose_classifier import HeadPoseClassifier
from .head_reading import HeadReading
from .head_reading_buffer import HeadReadingBuffer
from .mac_monitor_provider import MacMonitorProvider
from .monitor import Monitor
from .monitor_layout import MonitorLayout
from .monitor_provider import MonitorProvider
from .monitor_provider_factory import MonitorProviderFactory
from .screen_rect import ScreenRect
from .windows_monitor_provider import WindowsMonitorProvider
from .xrandr_provider import XrandrProvider

__all__ = [
    "CameraDependencies",
    "CameraWatcher",
    "CaptureApi",
    "FaceLandmarkModel",
    "FallbackMonitorProvider",
    "GazeState",
    "GnomeMonitorsXmlProvider",
    "HeadPoseClassifier",
    "HeadReading",
    "HeadReadingBuffer",
    "MacMonitorProvider",
    "Monitor",
    "MonitorLayout",
    "MonitorProvider",
    "MonitorProviderFactory",
    "ScreenRect",
    "WindowsMonitorProvider",
    "XrandrProvider",
]
