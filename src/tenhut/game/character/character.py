from __future__ import annotations

from typing import Final

import pygame

from ..geometry import Point
from ..global_random import GlobalRandom
from ..random_source import RandomSource
from .blink_controller import BlinkController
from .character_painter import CharacterPainter
from .character_state import CharacterState
from .distraction_controller import DistractionController
from .expression_catalog import ExpressionCatalog
from .gaze_controller import GazeController
from .mood import Mood
from .mouth_controller import MouthController
from .pose_name import PoseName
from .sip_cycle import SipCycle


class Character:
    """The general: his mood, pose and attention, animated over time, and able to draw himself."""

    ALERT_DURATION: Final = 0.8
    DEFAULT_SHAKE: Final = 0.6
    SHAKE_JITTER_X: Final = (-1, 0, 1)
    SHAKE_JITTER_Y: Final = (-1, 0, 0, 1)

    def __init__(self, randomness: RandomSource | None = None) -> None:
        self._randomness = randomness or GlobalRandom()
        self._expressions = ExpressionCatalog.standard()
        self._painter = CharacterPainter(expressions=self._expressions)
        self._blink = BlinkController(self._randomness)
        self._gaze = GazeController(self._randomness)
        self._distraction = DistractionController()
        self._mouth = MouthController(self._randomness)
        self._sip = SipCycle()
        self._mood = Mood.NEUTRAL
        self._pose = PoseName.BEHIND
        self._talking = False
        self._elapsed = 0.0
        self._pointer: Point | None = None
        self._shake_until = -1.0
        self._alert_until = -1.0

    @property
    def mood(self) -> Mood:
        return self._mood

    @property
    def pose(self) -> PoseName:
        return self._pose

    @property
    def elapsed(self) -> float:
        return self._elapsed

    @property
    def talking(self) -> bool:
        return self._talking

    @talking.setter
    def talking(self, talking: bool) -> None:
        self._talking = talking

    @property
    def facing(self) -> float:
        """How far he has turned: -1 fully left, 0 toward the soldier, 1 fully right."""
        return self._distraction.facing

    @property
    def facing_direction(self) -> int:
        """Where he is turning to (-1, 0 or 1)."""
        return self._distraction.direction

    @property
    def distracted(self) -> bool:
        return self._distraction.active

    @property
    def alerting(self) -> bool:
        return self._elapsed < self._alert_until

    @property
    def squinting(self) -> bool:
        return self._gaze.squinting

    @property
    def state(self) -> CharacterState:
        return CharacterState(
            self._mood,
            self._pose,
            self._elapsed,
            self._distraction.shift,
            self._gaze.look,
            self._blink.is_blinking(self._elapsed),
            self._gaze.squinting,
            self._talking,
            self._mouth.is_open,
            self._sip.phase,
        )

    def show(self, mood: Mood | None = None, pose: PoseName | None = None) -> None:
        if mood is not None:
            self._mood = mood
        if pose is not None:
            self._pose = pose

    def follow_pointer(self, target: Point | None) -> None:
        """Look toward ``target`` (each axis from -1 to 1), or go back to looking around when ``None``."""
        self._pointer = target

    def distract(self, direction: int, seconds: float) -> None:
        self._distraction.distract(direction, self._elapsed + seconds)

    def snap(self, alert: bool = True) -> None:
        """Turn back to face the soldier, with an exclamation mark when caught looking away."""
        was_distracted = self._distraction.active
        self._distraction.stop()
        self._gaze.look_at_viewer(self._elapsed)
        if alert and was_distracted:
            self.raise_alert()

    def raise_alert(self) -> None:
        self._alert_until = self._elapsed + self.ALERT_DURATION

    def shake(self, seconds: float = DEFAULT_SHAKE) -> None:
        self._shake_until = self._elapsed + seconds

    def freeze(self, elapsed: float, look: Point) -> None:
        """Parks him at a given moment of his breathing, staring at ``look`` and never blinking (for portraits)."""
        self._elapsed = elapsed
        self._blink.suppress()
        self._gaze.fix(look)

    def update(self, dt: float) -> None:
        self._elapsed += dt
        self._blink.update(self._elapsed)
        if self._distraction.is_over(self._elapsed):
            self.snap(alert=False)
        self._distraction.turn(dt)
        self._follow_attention(dt)
        self._mouth.update(self._talking, self._elapsed)
        if self._pose is PoseName.COFFEE:
            self._sip.advance(dt)

    def render(self) -> pygame.Surface:
        return self._painter.render(self.state)

    def jitter(self) -> Point:
        """How far the sprite is knocked about this frame while he shakes."""
        if self._elapsed < self._shake_until:
            return Point(self._randomness.choice(self.SHAKE_JITTER_X), self._randomness.choice(self.SHAKE_JITTER_Y))
        return Point(0, 0)

    def _follow_attention(self, dt: float) -> None:
        if self._distraction.active:
            self._gaze.look_aside(self._distraction.direction)
        elif self._pointer is not None:
            self._gaze.look_at(self._pointer)
        elif self._gaze.scan_is_due(self._elapsed):
            self._gaze.scan(self._elapsed, self._expressions.for_mood(self._mood))
        self._gaze.ease(dt)
