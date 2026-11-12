import xml.etree.ElementTree as ET

import pytest

from fakes import FakeClock
from tenhut.core import CalibrationRecorder, CameraCalibration, CameraSettings, HeadPose, MonitorSide
from tenhut.services.platform import OperatingSystem
from tenhut.services.vision import (
    CaptureApi,
    FallbackMonitorProvider,
    GazeState,
    GnomeMonitorsXmlProvider,
    HeadPoseClassifier,
    HeadReading,
    HeadReadingBuffer,
    MacMonitorProvider,
    Monitor,
    MonitorLayout,
    MonitorProvider,
    WindowsMonitorProvider,
    XrandrProvider,
)
from tenhut.services.vision.screen_rect import ScreenRect

CALIBRATION = CameraCalibration(HeadPose(2, 3), HeadPose(1, -22), {MonitorSide.LEFT: HeadPose(34, -4)})
CLASSIFIER = HeadPoseClassifier(CALIBRATION, CameraSettings(down_threshold_degrees=14, side_threshold_degrees=18))


@pytest.mark.parametrize(
    ("yaw", "pitch", "expected"),
    [
        (4, 1, GazeState.OK),
        (12, -5, GazeState.OK),
        (2, -14, GazeState.DOWN),
        (33, -6, GazeState.SIDE_ALLOWED),
        (32, -24, GazeState.DOWN),
        (-30, 2, GazeState.SIDE),
    ],
)
def test_classify(yaw, pitch, expected):
    assert CLASSIFIER.classify(HeadPose(yaw, pitch)) is expected


def test_face_lost_right_after_head_dropped_counts_as_down():
    assert CLASSIFIER.classify_missing(HeadReading(HeadPose(0, -9), 100.0), 105.0) is GazeState.DOWN


def test_face_lost_without_dropping_is_absence():
    assert CLASSIFIER.classify_missing(HeadReading(HeadPose(0, 3), 100.0), 105.0) is None
    assert CLASSIFIER.classify_missing(None, 105.0) is None


def test_old_sightings_are_ignored():
    assert CLASSIFIER.classify_missing(HeadReading(HeadPose(0, -15), 100.0), 130.0) is None


def test_infraction_states():
    assert GazeState.DOWN.is_infraction and GazeState.SIDE.is_infraction
    assert not GazeState.OK.is_infraction and not GazeState.SIDE_ALLOWED.is_infraction


def test_recorder_builds_a_calibration_only_when_complete():
    recorder = CalibrationRecorder()
    recorder.record_base(HeadPose(1, 2))
    assert not recorder.is_complete()
    with pytest.raises(ValueError):
        recorder.build()
    recorder.record_down(HeadPose(1, -20), face_vanishes=True)
    recorder.record_side(MonitorSide.RIGHT, HeadPose(-30, 0))
    built = recorder.build()
    assert built.down_face_vanishes and built.sides == {MonitorSide.RIGHT: HeadPose(-30, 0)}


class FixedProvider(MonitorProvider):
    def __init__(self, monitors):
        self.monitors = monitors

    def list_monitors(self):
        return self.monitors


def test_sides_with_no_monitors():
    assert MonitorLayout(FixedProvider([])).sides() == {MonitorSide.LEFT: [], MonitorSide.RIGHT: []}


def test_sides_relative_to_the_primary():
    monitors = [Monitor("DP-2", 1920, 0, 2560, 1440, True), Monitor("DP-1", 0, 210, 1920, 1080, False)]
    sides = MonitorLayout(FixedProvider(monitors)).sides()
    assert sides == {MonitorSide.LEFT: ["DP-1"], MonitorSide.RIGHT: []}
    named = MonitorLayout(FixedProvider(monitors)).sides("DP-1")
    assert named == {MonitorSide.LEFT: [], MonitorSide.RIGHT: ["DP-2"]}


def test_xrandr_output_is_parsed():
    text = "Monitors: 2\n 0: +*DP-2 2560/597x1440/336+1920+0  DP-2\n 1: +DP-1 1920/527x1080/296+0+210  DP-1\n"
    assert XrandrProvider.parse(text) == [
        Monitor("DP-2", 1920, 0, 2560, 1440, True),
        Monitor("DP-1", 0, 210, 1920, 1080, False),
    ]


def test_gnome_monitors_xml_is_parsed_with_scale():
    xml = """<monitors><configuration>
      <logicalmonitor><x>0</x><y>0</y><scale>2</scale><primary>yes</primary>
        <monitor><monitorspec><connector>eDP-1</connector></monitorspec><mode><width>3840</width><height>2160</height></mode></monitor>
      </logicalmonitor></configuration></monitors>"""
    assert GnomeMonitorsXmlProvider.parse(ET.fromstring(xml)) == [Monitor("eDP-1", 0, 0, 1920, 1080, True)]


def test_gnome_provider_with_a_missing_file(tmp_path):
    assert GnomeMonitorsXmlProvider(tmp_path / "none.xml").list_monitors() == []


def test_mac_monitors_flip_the_y_axis_and_ignore_noise():
    text = 'warning\n[{"name":"Main","x":0,"y":0,"w":1440,"h":900},{"name":"","x":1440,"y":100,"w":1920,"h":1080}]'
    assert MacMonitorProvider.parse(text) == [
        Monitor("Main", 0, 0, 1440, 900, True),
        Monitor("Display 2", 1440, -280, 1920, 1080, False),
    ]
    assert MacMonitorProvider.parse("garbage") == []


def test_windows_monitor_info():
    assert WindowsMonitorProvider.monitor_from_info("DISPLAY1", ScreenRect(0, 0, 1920, 1080), 1) == Monitor(
        "DISPLAY1", 0, 0, 1920, 1080, True
    )
    assert WindowsMonitorProvider.monitor_from_info("", ScreenRect(1920, 0, 3840, 1080), 0).name == "?"


def test_fallback_provider_uses_the_first_that_finds_monitors():
    found = [Monitor("A", 0, 0, 1, 1, True)]
    assert FallbackMonitorProvider((FixedProvider([]), FixedProvider(found))).list_monitors() == found
    assert FallbackMonitorProvider(()).list_monitors() == []


def test_capture_api_per_os():
    assert CaptureApi.for_system(OperatingSystem.WINDOWS).opencv_name == "CAP_DSHOW"
    assert CaptureApi.for_system(OperatingSystem.MACOS).opencv_name == "CAP_AVFOUNDATION"
    assert CaptureApi.for_system(OperatingSystem.LINUX).opencv_name == "CAP_V4L2"


def test_reading_buffer_smooths_and_expires():
    clock = FakeClock(100.0)
    buffer = HeadReadingBuffer(clock)
    assert buffer.current() is None
    buffer.store(HeadPose(10, 0))
    clock.current = 100.5
    buffer.store(HeadPose(20, 10))
    assert buffer.current() == HeadPose(15, 5)
    assert len(buffer.seen_since(100.2)) == 1 and buffer.last_seen().timestamp == 100.5
    clock.current = 103.0
    assert buffer.current() is None and buffer.last_seen() is not None
