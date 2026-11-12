from __future__ import annotations

from pygame import Rect

from .anatomy import Anatomy
from .body_part import BodyPart
from .cap import Cap
from .character_state import CharacterState
from .ears import Ears
from .expression_catalog import ExpressionCatalog
from .eyes import Eyes
from .mustache import Mustache
from .nose import Nose
from .painter import Painter
from .sideburns import Sideburns
from .skull import Skull


class Head(BodyPart):
    """The head: ears, skull and sideburns, then the face (shifted and clipped when he turns), then the cap."""

    FACE_LEFT = 26
    FACE_WIDTH = 22
    TURN_MARGIN = 3
    TURNED_FROM = 1

    def __init__(self, expressions: ExpressionCatalog) -> None:
        self._expressions = expressions
        self._ears = Ears()
        self._skull = Skull()
        self._sideburns = Sideburns()
        self._nose = Nose()
        self._eyes = Eyes()
        self._mustache = Mustache()
        self._cap = Cap()

    def paint(self, painter: Painter, state: CharacterState) -> None:
        expression = self._expressions.for_mood(state.mood)
        skin = expression.skin
        self._ears.paint(painter, state.turn, skin)
        self._skull.paint(painter, skin)
        self._sideburns.paint(painter, state.turn)
        with painter.shifted(state.turn), painter.clipped(self._face_window(state.turn)):
            self._nose.paint_front(painter, skin)
            expression.paint_cheeks(painter)
            self._eyes.paint(painter, state, expression)
            expression.paint_brows(painter)
            expression.paint_mouth(painter, state)
            self._mustache.paint(painter)
            self._nose.paint_profile(painter, state.turn, skin)
        self._cap.paint(painter, state.turn)
        expression.paint_forehead(painter)

    def _face_window(self, turn: int) -> Rect:
        """The raw columns the features may occupy, so they are cut at the edge of the turned head."""
        left = self.FACE_LEFT - (self.TURN_MARGIN if turn < -self.TURNED_FROM else 0)
        width = self.FACE_WIDTH + (self.TURN_MARGIN if abs(turn) > self.TURNED_FROM else 0)
        return Rect(left, 0, width, Anatomy.HEIGHT + 2 * Anatomy.OUTLINE_MARGIN)
