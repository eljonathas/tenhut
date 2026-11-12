from __future__ import annotations

from dataclasses import dataclass

import pygame

from tenhut.game.painting import Rgb


@dataclass(frozen=True, slots=True)
class ActionBar:
    """A full-width bar at the bottom of the settings: where it is, what it says and its colour."""

    rect: pygame.Rect
    label: str
    face: Rgb
    fitted: bool
