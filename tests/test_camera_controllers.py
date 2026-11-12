from tenhut.controllers import (
    AbsenceMonitor,
    BaseStep,
    CalibrationPlan,
    CalibrationPlanner,
    CaptureWindow,
    DownStep,
    GazeStatus,
    GazeStatusKind,
    InfractionMonitor,
    SideStep,
)
from tenhut.core import CalibrationRecorder, HeadPose, MonitorSide
from tenhut.services.vision import GazeState, HeadReading


class TestInfractionMonitor:
    def test_the_first_bad_moment_only_starts_the_clock(self):
        monitor = InfractionMonitor()
        assert not monitor.keeps_going(100)
        assert monitor.keeps_going(101)

    def test_a_warning_comes_before_the_punishment(self):
        monitor = InfractionMonitor()
        monitor.keeps_going(100)
        assert not monitor.warning_due(101, tolerance=6)
        assert monitor.warning_due(102, tolerance=6)
        assert not monitor.warning_due(103, tolerance=6) and monitor.warned
        assert not monitor.punishment_due(105, tolerance=6)
        assert monitor.punishment_due(106, tolerance=6)

    def test_a_short_tolerance_warns_earlier(self):
        monitor = InfractionMonitor()
        monitor.keeps_going(100)
        assert monitor.warning_due(100.5, tolerance=1)

    def test_a_punishment_starts_over_and_waits_before_the_next(self):
        monitor = InfractionMonitor()
        monitor.keeps_going(100)
        assert monitor.punishment_due(110, tolerance=6)
        assert not monitor.warned and not monitor.keeps_going(111)
        assert not monitor.punishment_due(117, tolerance=6)
        assert monitor.punishment_due(126, tolerance=6)

    def test_good_posture_clears_the_warning(self):
        monitor = InfractionMonitor()
        monitor.keeps_going(100)
        monitor.warning_due(102, tolerance=6)
        monitor.clear()
        assert not monitor.warned and not monitor.keeps_going(103)


def test_absence_is_reported_once_after_a_minute():
    monitor = AbsenceMonitor()
    assert not monitor.observe_absent(0)
    assert not monitor.observe_absent(60)
    assert monitor.observe_absent(61) and monitor.warned
    assert not monitor.observe_absent(120)
    monitor.reset()
    assert not monitor.warned


class TestGazeStatus:
    def test_every_gaze_state_has_a_status(self):
        for state in GazeState:
            assert GazeStatus.of(state).present

    def test_only_infractions_are_alerts(self):
        assert GazeStatus.of(GazeState.DOWN).is_alert and GazeStatus.of(GazeState.SIDE).is_alert
        assert not GazeStatus.of(GazeState.OK).is_alert and not GazeStatus.no_face().is_alert

    def test_nothing_is_not_present(self):
        assert not GazeStatus.none().present

    def test_an_error_shows_its_own_message(self):
        status = GazeStatus.error("camera 3 busy")
        assert status.text == "camera 3 busy" and status.kind is GazeStatusKind.ERROR

    def test_known_statuses_are_translated(self):
        assert GazeStatus.of(GazeState.OK).text and GazeStatus.no_face().text


class TestCalibrationSteps:
    def test_the_plan_asks_for_the_main_screen_each_side_monitor_and_looking_down(self):
        plan = CalibrationPlanner().plan({MonitorSide.LEFT: ["HDMI-1"], MonitorSide.RIGHT: []})
        kinds = [type(step) for step in plan.steps]
        assert kinds == [BaseStep, SideStep, DownStep]

    def test_the_plan_advances_until_it_is_finished(self):
        plan = CalibrationPlan([BaseStep("a"), DownStep("b")])
        assert plan.current.prompt == "a" and not plan.finished
        plan.advance()
        plan.advance()
        assert plan.finished

    def test_a_side_pose_must_differ_from_the_base_in_yaw(self):
        step = SideStep("left", MonitorSide.LEFT)
        base = HeadPose(0, 0)
        assert step.rejection_key(HeadPose(5, 0), base) == "calibration.speech.yaw_too_small"
        assert step.rejection_key(HeadPose(25, 0), base) is None

    def test_a_down_pose_must_differ_from_the_base_in_pitch(self):
        step = DownStep("down")
        assert step.rejection_key(HeadPose(0, 3), HeadPose(0, 0)) == "calibration.speech.pitch_too_small"
        assert step.rejection_key(HeadPose(0, 20), HeadPose(0, 0)) is None

    def test_steps_record_into_the_recorder(self):
        recorder = CalibrationRecorder()
        BaseStep("base").record(recorder, HeadPose(1, 2))
        SideStep("side", MonitorSide.RIGHT).record(recorder, HeadPose(30, 2))
        DownStep("down").record(recorder, HeadPose(1, 25))
        assert recorder.is_complete()
        assert recorder.build().sides[MonitorSide.RIGHT] == HeadPose(30, 2)

    def test_when_the_face_vanishes_the_farthest_pose_seen_is_used(self):
        recorder = CalibrationRecorder()
        recorder.record_base(HeadPose(0, 0))
        seen = [HeadReading(HeadPose(0, 5), 1.0), HeadReading(HeadPose(0, 12), 1.1)]
        DownStep("down").record_vanished(recorder, seen)
        calibration = recorder.build()
        assert calibration.down.pitch == 12 and calibration.down_face_vanishes

    def test_when_nothing_was_seen_the_usual_direction_is_assumed(self):
        recorder = CalibrationRecorder()
        recorder.record_base(HeadPose(3, 1))
        DownStep("down").record_vanished(recorder, [])
        assert recorder.build().down == HeadPose(3, 1 + DownStep.ASSUMED_DROP_DEGREES)

    def test_only_the_down_step_tolerates_a_missing_face(self):
        assert DownStep.tolerates_missing_face
        assert not BaseStep.tolerates_missing_face and not SideStep.tolerates_missing_face


class TestCaptureWindow:
    def test_a_countdown_beeps_once_per_second_then_starts_sampling(self):
        capture = CaptureWindow()
        capture.start(100)
        assert capture.counting_down and capture.busy
        beeps = []
        for tick in range(0, 31):
            now = 100 + tick / 10
            if capture.beep_due(now):
                beeps.append(round(now, 1))
        assert beeps == [100.0, 101.0, 102.0]
        assert capture.countdown_over(103)
        capture.begin_sampling(103)
        assert capture.sampling and not capture.counting_down

    def test_samples_are_collected_until_the_window_closes(self):
        capture = CaptureWindow()
        capture.start(0)
        capture.begin_sampling(3)
        capture.add(HeadPose(1, 1))
        capture.add(None)
        assert not capture.sampling_over(4) and capture.sampling_over(5)
        assert capture.take_samples() == [HeadPose(1, 1)]
        assert not capture.busy

    def test_cancelling_drops_everything(self):
        capture = CaptureWindow()
        capture.start(0)
        capture.cancel()
        assert not capture.busy
