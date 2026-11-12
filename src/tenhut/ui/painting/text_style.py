from __future__ import annotations

from dataclasses import dataclass

import pygame

from tenhut.game.painting import Rgb

from .text_align import TextAlign


@dataclass(frozen=True, slots=True)
class TextStyle:
    """How a piece of text is drawn."""

    font: pygame.font.Font
    color: Rgb
    align: TextAlign = TextAlign.LEFT
