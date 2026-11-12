from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class TitleCardFonts:
    title: pygame.font.Font
    subtitle: pygame.font.Font
