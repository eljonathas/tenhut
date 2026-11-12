from __future__ import annotations

import math

import pygame

from tenhut.game.geometry import Point
from tenhut.game.painting import Canvas, Palette

from .animation import Animation
from .animation_palette import AnimationPalette
from .slam_placement import SlamPlacement


class SlamAnimation(Animation):
    """The general raises both fists and pounds the desk: the desk shakes, loose objects hop, BAM."""

    IMPACT_TIME = 0.32
    DURATION = 1.15
    SETTLE_SECONDS = 0.55
    SHAKE_AMPLITUDE = 2
    SHAKE_FREQUENCY_X = 70
    SHAKE_FREQUENCY_Y = 50
    HOP_HEIGHT = 7
    HOP_FREQUENCY = 11
    DUST_SECONDS = 0.35
    CAPTION_SECONDS = 0.7
    CAPTION_TILT = -8
    FIST_SIZE = (12, 9)
    FIST_OFFSETS = (-17, 5)

    def __init__(self, placement: SlamPlacement, caption: str, font: pygame.font.Font) -> None:
        self._placement = placement
        self._caption = caption
        self._font = font
        self._fist = self._build_fist()
        self._elapsed = 0.0
        self._impact_landed = False

    @property
    def finished(self) -> bool:
        return self._elapsed >= self.DURATION

    @property
    def fists_raised(self) -> bool:
        return self._elapsed < self.IMPACT_TIME

    @property
    def impact_landed(self) -> bool:
        """True only during the update in which the fists hit the desk."""
        return self._impact_landed

    @property
    def since_impact(self) -> float:
        """Seconds since the fists hit the desk, or -1 while they are still raised."""
        return -1.0 if self.fists_raised else self._elapsed - self.IMPACT_TIME

    @property
    def shake(self) -> Point:
        """Displacement of the desk in world pixels."""
        if self.fists_raised:
            return Point(0, 0)
        since = self.since_impact
        decay = self._decay(since)
        return Point(
            round(math.sin(since * self.SHAKE_FREQUENCY_X) * self.SHAKE_AMPLITUDE * decay),
            round(abs(math.sin(since * self.SHAKE_FREQUENCY_Y)) * self.SHAKE_AMPLITUDE * decay),
        )

    @property
    def hop(self) -> int:
        """How high loose objects jump off the desk, in world pixels."""
        if self.fists_raised:
            return 0
        since = self.since_impact
        return int(self.HOP_HEIGHT * self._decay(since) * abs(math.sin(since * self.HOP_FREQUENCY)))

    def place(self, placement: SlamPlacement) -> None:
        self._placement = placement

    def update(self, dt: float) -> None:
        before = self._elapsed
        self._elapsed += dt
        self._impact_landed = before < self.IMPACT_TIME <= self._elapsed

    def draw(self, surface: pygame.Surface) -> None:
        """Fists over the desk edge, impact dust and the caption; nothing before the fists land."""
        if self.fists_raised:
            return
        placement = self._placement
        shake = self.shake
        desk_top = placement.desk_top + shake.y * placement.world_scale
        center_x = placement.center_x + shake.x * placement.world_scale
        self._draw_fists(surface, center_x, desk_top)
        if self.since_impact < self.DUST_SECONDS:
            self._draw_dust(surface, center_x, desk_top)
        if self.since_impact < self.CAPTION_SECONDS:
            self._draw_caption(surface, center_x, desk_top)

    def _decay(self, since_impact: float) -> float:
        return max(0.0, 1 - since_impact / self.SETTLE_SECONDS)

    def _build_fist(self) -> pygame.Surface:
        width, height = self.FIST_SIZE
        fist = pygame.Surface(self.FIST_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(fist, Palette.OUTLINE, (0, 0, width, height), border_radius=2)
        pygame.draw.rect(fist, Palette.GLOVE, (1, 1, width - 2, height - 2), border_radius=2)
        canvas = Canvas(fist)
        for column in (4, 7):
            canvas.line(AnimationPalette.FIST_FOLD, (column, 2), (column, 5))
        canvas.line(AnimationPalette.FIST_FOLD, (1, 6), (10, 6))
        return fist

    def _draw_fists(self, surface: pygame.Surface, center_x: float, desk_top: float) -> None:
        scale = self._placement.character_scale
        fist = pygame.transform.scale_by(self._fist, scale)
        for offset in self.FIST_OFFSETS:
            surface.blit(fist, (center_x + offset * scale, desk_top - 6 * scale))

    def _draw_dust(self, surface: pygame.Surface, center_x: float, desk_top: float) -> None:
        scale = self._placement.character_scale
        since = self.since_impact
        canvas = Canvas(surface)
        for side in (-1, 1):
            for streak in range(3):
                x = center_x + side * (20 + streak * 4) * scale
                y = desk_top - (2 + streak * 3) * scale
                canvas.line(AnimationPalette.DUST, (x, y), (x + side * (6 + since * 40), y - 3 - since * 20), width=2)

    def _draw_caption(self, surface: pygame.Surface, center_x: float, desk_top: float) -> None:
        scale = self._placement.character_scale
        since = self.since_impact
        for color, shadow in ((Palette.OUTLINE, 2), (AnimationPalette.SLAM_TEXT, 0)):
            image = pygame.transform.scale_by(self._font.render(self._caption, False, color), 2)
            image = pygame.transform.rotate(image, self.CAPTION_TILT)
            anchor = (center_x - 20 * scale + shadow, desk_top - 8 * scale - since * 16 + shadow)
            surface.blit(image, image.get_rect(midright=anchor))
