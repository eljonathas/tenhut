from __future__ import annotations

from typing import ClassVar

from tenhut.controllers.active_settings import ActiveSettings
from tenhut.controllers.feedback import Feedback
from tenhut.controllers.gestures import Gestures
from tenhut.controllers.navigation import Navigation
from tenhut.controllers.reaction import Reaction
from tenhut.controllers.speech import Speech
from tenhut.controllers.speech_hold import SpeechHold
from tenhut.controllers.tickable import Tickable
from tenhut.controllers.utterance import Utterance
from tenhut.core import Clock, Phase, Session
from tenhut.game.audio import SoundEffect
from tenhut.game.character import Character
from tenhut.game.painting import Rgb
from tenhut.game.random_source import RandomSource
from tenhut.i18n import t, t_choice
from tenhut.services.vision import GazeState, HeadPoseClassifier

from .absence_monitor import AbsenceMonitor
from .camera_holder import CameraHolder
from .camera_stop_listener import CameraStopListener
from .gaze_status import GazeStatus
from .infraction_monitor import InfractionMonitor


class CameraController(Tickable, CameraStopListener):
    """While working, watches the soldier through the camera: warns, scolds and penalises bad posture."""

    WARNINGS: ClassVar[dict[GazeState, str]] = {
        GazeState.DOWN: "speech.camera.warn_looking_down",
        GazeState.SIDE: "speech.camera.warn_looking_away",
    }
    SCOLDS: ClassVar[dict[GazeState, str]] = {
        GazeState.DOWN: "speech.camera.scold_looking_down",
        GazeState.SIDE: "speech.camera.scold_looking_away",
    }
    PENALTY_COLOR = Rgb(255, 130, 110)
    ENCOURAGE_CHANCE = 0.5
    SHAKE_SECONDS = 1.0
    SCOLD_FLASH = 0.6

    def __init__(
        self,
        holder: CameraHolder,
        session: Session,
        settings: ActiveSettings,
        *,
        clock: Clock,
        navigation: Navigation,
        speech: Speech,
        feedback: Feedback,
        gestures: Gestures,
        general: Character,
        randomness: RandomSource,
    ) -> None:
        self._holder = holder
        self._session = session
        self._settings = settings
        self._clock = clock
        self._navigation = navigation
        self._speech = speech
        self._feedback = feedback
        self._gestures = gestures
        self._general = general
        self._randomness = randomness
        self._infractions = InfractionMonitor()
        self._absence = AbsenceMonitor()

    @property
    def active(self) -> bool:
        return self._holder.watcher is not None

    @property
    def status(self) -> GazeStatus:
        return self._holder.status

    def camera_stopped(self) -> None:
        self._infractions.clear()
        self._absence.reset()

    def tick(self, dt: float) -> None:
        if self._navigation.current_id.is_calibration:
            return
        settings = self._settings.current.camera
        wanted = settings.is_ready() and self._session.phase is Phase.WORK
        self._holder.ensure(wanted)
        watcher = self._holder.watcher
        if not wanted or watcher is None:
            return
        if watcher.error:
            self._holder.status = GazeStatus.error(watcher.error)
            return
        if watcher.ready:
            self._observe(HeadPoseClassifier(settings.calibration, settings), self._clock.now())

    def _observe(self, classifier: HeadPoseClassifier, now: float) -> None:
        watcher = self._holder.watcher
        angles = watcher.angles()
        state = classifier.classify_missing(watcher.last_seen(), now) if angles is None else None
        if angles is None and state is None:
            self._on_absent(now)
            return
        if self._absence.warned:
            self._speech.say(Utterance(t("speech.camera.back_at_post"), Reaction.STERN_CROSSED, SpeechHold.MEDIUM))
        self._absence.reset()
        state = state or classifier.classify(angles)
        self._holder.status = GazeStatus.of(state)
        if state.is_infraction:
            self._on_infraction(state, now)
        else:
            self._on_good_posture()

    def _on_absent(self, now: float) -> None:
        self._holder.status = GazeStatus.no_face()
        self._infractions.clear()
        if self._absence.observe_absent(now):
            self._feedback.play(SoundEffect.ALARM)
            self._speech.say(Utterance(t("speech.camera.absent"), Reaction.ANGRY_POINT))
            self._feedback.notify(t("notify.camera_absent.title"), t("notify.camera_absent.body"), urgent=True)

    def _on_good_posture(self) -> None:
        if self._infractions.warned and self._randomness.random() < self.ENCOURAGE_CHANCE:
            self._speech.say(Utterance(t("speech.camera.better"), Reaction.STERN_CROSSED, SpeechHold.BRIEF))
        self._infractions.clear()

    def _on_infraction(self, state: GazeState, now: float) -> None:
        if not self._infractions.keeps_going(now):
            return
        tolerance = float(self._settings.current.camera.tolerance_seconds)
        if self._infractions.warning_due(now, tolerance):
            self._warn(state)
        if self._infractions.punishment_due(now, tolerance):
            self._punish(state)

    def _warn(self, state: GazeState) -> None:
        self._general.snap()
        self._general.raise_alert()
        self._feedback.play(SoundEffect.THINK)
        self._speech.say(Utterance(t_choice(self.WARNINGS[state]), Reaction.STERN_POINT, SpeechHold.MEDIUM))
        self._gestures.poke(1)

    def _punish(self, state: GazeState) -> None:
        session = self._session
        session.record_infraction()
        penalty = float(self._settings.current.camera.penalty_minutes)
        session.penalize(penalty)
        session.save()
        suffix = t("speech.camera.penalty_suffix", pen=penalty) if penalty > 0 else ""
        self._feedback.play(SoundEffect.ALARM)
        self._feedback.flash(self.SCOLD_FLASH)
        self._general.shake(self.SHAKE_SECONDS)
        if penalty > 0:
            self._feedback.popup(f"+{penalty:g} min", self.PENALTY_COLOR)
        self._speech.say(Utterance(t_choice(self.SCOLDS[state]) + suffix, Reaction.ANGRY_POINT))
        self._gestures.poke(2)
        self._feedback.notify(
            t("notify.infraction.title"), t("notify.infraction.body", n=session.infractions, extra=suffix), urgent=True
        )
