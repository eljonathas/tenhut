from __future__ import annotations

import math
from typing import Final

import pygame

from .anatomy import Anatomy
from .character_state import CharacterState
from .expression_catalog import ExpressionCatalog
from .head import Head
from .legs import Legs
from .outline_renderer import OutlineRenderer
from .painter import Painter
from .pose_catalog import PoseCatalog
from .torso import Torso


class CharacterPainter:
    """Stacks the body parts back to front, with the pose's arms in between, and outlines the result."""

    BREATH_RATE: Final = 2.4
    BREATH_THRESHOLD: Final = 0.3

    def __init__(self, poses: PoseCatalog | None = None, expressions: ExpressionCatalog | None = None) -> None:
        self._poses = poses or PoseCatalog.standard()
        self._expressions = expressions or ExpressionCatalog.standard()
        self._legs = Legs()
        self._torso = Torso()
        self._head = Head(self._expressions)
        self._outline = OutlineRenderer()

    def render(self, state: CharacterState) -> pygame.Surface:
        """The outlined sprite, ``Anatomy.CANVAS_SIZE`` pixels, transparent around the general."""
        body = pygame.Surface(Anatomy.CANVAS_SIZE, pygame.SRCALPHA)
        painter = Painter(body, bob=self._breathing_bob(state))
        pose = self._poses.for_name(state.pose)
        self._legs.paint(painter, state)
        pose.paint_before_torso(painter, state)
        self._torso.paint(painter, state)
        pose.paint_arms(painter, state)
        self._head.paint(painter, state)
        pose.paint_after_head(painter, state)
        return self._outline.outline(body)

    def _breathing_bob(self, state: CharacterState) -> int:
        """The upper body drops one pixel while he exhales; furious, he does not breathe calmly at all."""
        if not self._expressions.for_mood(state.mood).breathes:
            return 0
        return 1 if math.sin(state.elapsed * self.BREATH_RATE) > self.BREATH_THRESHOLD else 0
