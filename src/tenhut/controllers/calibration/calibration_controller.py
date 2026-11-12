from __future__ import annotations

import statistics

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.calibration_starter import CalibrationStarter
from tenhut.controllers.camera.camera_holder import CameraHolder
from tenhut.controllers.camera.gaze_status import GazeStatus
from tenhut.controllers.feedback import Feedback
from tenhut.controllers.navigation import Navigation
from tenhut.controllers.page_id import PageId
from tenhut.controllers.reaction import Reaction
from tenhut.controllers.speech import Speech
from tenhut.controllers.speech_hold import SpeechHold
from tenhut.controllers.tickable import Tickable
from tenhut.controllers.utterance import Utterance
from tenhut.core import CalibrationRecorder, Clock, HeadPose, MonitorSide, SettingsStore
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character, Mood, PoseName
from tenhut.i18n import t
from tenhut.services.vision import CameraWatcher, HeadPoseClassifier, MonitorLayout

from .calibration_plan import CalibrationPlan
from .calibration_planner import CalibrationPlanner
from .capture_window import CaptureWindow
from .down_step import DownStep


class CalibrationController(CalibrationStarter, Tickable):
    """Walks the soldier through the camera calibration and then lets him test it."""

    MIN_SAMPLES = 8
    TEST_REACTION_SECONDS = 0.5
    HISTORY_SECONDS = 1.0

    def __init__(
        self,
        holder: CameraHolder,
        monitors: MonitorLayout,
        settings: ActiveSettings,
        *,
        store: SettingsStore,
        clock: Clock,
        navigation: Navigation,
        speech: Speech,
        feedback: Feedback,
        general: Character,
    ) -> None:
        self._holder = holder
        self._monitors = monitors
        self._settings = settings
        self._store = store
        self._clock = clock
        self._navigation = navigation
        self._speech = speech
        self._feedback = feedback
        self._general = general
        self._planner = CalibrationPlanner()
        self._plan = CalibrationPlan([])
        self._recorder = CalibrationRecorder()
        self._capture = CaptureWindow()
        self._sides: dict[MonitorSide, list[str]] = {}

    @property
    def plan(self) -> CalibrationPlan:
        return self._plan

    @property
    def capture_window(self) -> CaptureWindow:
        return self._capture

    @property
    def sides(self) -> dict[MonitorSide, list[str]]:
        return self._sides

    @property
    def base_pose(self) -> HeadPose | None:
        return self._recorder.base

    @property
    def holder(self) -> CameraHolder:
        return self._holder

    def start(self) -> None:
        self._sides = self._monitors.sides(self._settings.current.camera.camera_monitor)
        self._plan = self._planner.plan(self._sides)
        self._recorder = CalibrationRecorder()
        self._capture.cancel()
        self._holder.ensure(True)
        self._navigation.open(PageId.CALIBRATION)
        self._prompt()

    def capture(self) -> None:
        watcher = self._holder.watcher
        if not watcher or not watcher.ready:
            self._speech.say(Utterance(t("calibration.speech.camera_starting"), Reaction.THINKING_CHIN))
            return
        if self._capture.busy:
            return
        self._capture.start(self._clock.now())
        self._speech.murmur(t("calibration.speech.hold_position"), persist=True)

    def finish(self) -> None:
        camera = self._settings.current.camera.calibrated(self._recorder.build())
        self._settings.replace(self._settings.current.with_camera(camera))
        self._store.save(self._settings.current)
        self._holder.ensure(False)
        self._navigation.open(PageId.MAIN)
        self._speech.say(Utterance(t("calibration.speech.camera_on"), Reaction.STERN_POINT, SpeechHold.LONG))

    def cancel(self) -> None:
        self._capture.cancel()
        self._holder.ensure(False)
        self._navigation.open(PageId.MAIN)
        self._speech.murmur(t("calibration.speech.cancelled"))

    def tick(self, dt: float) -> None:
        if self._navigation.current_id is PageId.CALIBRATION_TEST:
            self._test_posture()
        else:
            self._advance_capture(self._clock.now())

    def _advance_capture(self, now: float) -> None:
        capture = self._capture
        if capture.counting_down:
            self._count_down(now)
        elif capture.sampling:
            watcher = self._holder.watcher
            capture.add(watcher.angles() if watcher else None)
            if capture.sampling_over(now):
                self._judge_samples(capture.take_samples())

    def _count_down(self, now: float) -> None:
        if self._capture.beep_due(now):
            self._feedback.play(SoundEffect.TICK)
        if self._capture.countdown_over(now):
            self._capture.begin_sampling(now)
            self._feedback.play(SoundEffect.THINK)

    def _judge_samples(self, samples: list[HeadPose]) -> None:
        step = self._plan.current
        if len(samples) < self.MIN_SAMPLES and step.tolerates_missing_face:
            self._accept_vanished_face(step)
        elif len(samples) < self.MIN_SAMPLES:
            self._reject(t("calibration.speech.face_not_seen"))
        else:
            pose = HeadPose(statistics.median(s.yaw for s in samples), statistics.median(s.pitch for s in samples))
            reason = step.rejection_key(pose, self._recorder.base)
            if reason:
                self._reject(t(reason))
            else:
                step.record(self._recorder, pose)
                self._accept(t("calibration.speech.noted"), t("calibration.speech.calibrated_test"))

    def _accept_vanished_face(self, step: DownStep) -> None:
        watcher = self._holder.watcher
        seen = watcher.seen_since(self._capture.started_at - self.HISTORY_SECONDS) if watcher else []
        step.record_vanished(self._recorder, seen)
        message = t("calibration.speech.face_vanishes_when_down")
        self._accept(message, message + t("calibration.speech.test_now"))

    def _accept(self, prefix: str, finished_message: str) -> None:
        self._feedback.play(SoundEffect.APPROVED)
        self._plan.advance()
        if self._plan.finished:
            self._navigation.open(PageId.CALIBRATION_TEST)
            self._speech.say(Utterance(finished_message, Reaction.STERN_CROSSED, persist=True))
        else:
            self._prompt(prefix)

    def _reject(self, reason: str) -> None:
        self._feedback.play(SoundEffect.DENIED)
        self._prompt(reason)

    def _prompt(self, prefix: str = "") -> None:
        message = t("calibration.prompt.capture_instructions", prefix=prefix, msg=self._plan.current.prompt)
        self._speech.say(Utterance(message, Reaction.NEUTRAL_POINT, persist=True))

    def _test_posture(self) -> None:
        watcher = self._holder.watcher
        angles = watcher.angles() if watcher else None
        classifier = HeadPoseClassifier(self._recorder.build(), self._settings.current.camera)
        if angles is None:
            self._test_missing_face(classifier, watcher)
            return
        state = classifier.classify(angles)
        self._holder.status = GazeStatus.of(state)
        bad = state.is_infraction
        self._general.show(Mood.ANGRY if bad else Mood.HAPPY, PoseName.POINT if bad else PoseName.THUMBS)
        self._speech.react_for(self.TEST_REACTION_SECONDS)

    def _test_missing_face(self, classifier: HeadPoseClassifier, watcher: CameraWatcher | None) -> None:
        missed = classifier.classify_missing(watcher.last_seen() if watcher else None, self._clock.now())
        self._holder.status = GazeStatus.face_vanished() if missed else GazeStatus.no_face()
        if missed:
            self._general.show(Mood.ANGRY, PoseName.POINT)
            self._speech.react_for(self.TEST_REACTION_SECONDS)
