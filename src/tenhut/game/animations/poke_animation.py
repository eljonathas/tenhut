from __future__ import annotations

import math

import pygame

from tenhut.game.geometry import Point
from tenhut.game.painting import Canvas, Palette

from .animation import Animation
from .animation_palette import AnimationPalette
from .easing import Easing
from .glove_sprite import GloveSprite
from .poke_trajectory import PokeTrajectory


class _PokeTimeline:
    """How far the arm is extended (0 retracted, 1 at the screen) at each moment of the poke."""

    REACH_SECONDS = 0.3
    RETRACT_SECONDS = 0.35
    JAB_WINDOW = 0.07
    JAB_DEPTH = 0.15
    HIT_TIMES = (0.36, 0.58)

    def __init__(self, jabs: int) -> None:
        self.hits = self.HIT_TIMES[:jabs]
        self.duration = 1.25 if jabs == 2 else 1.0

    def reach(self, elapsed: float) -> float:
        if elapsed < self.REACH_SECONDS:
            return Easing.out_cubic(elapsed / self.REACH_SECONDS)
        retract_from = self.duration - self.RETRACT_SECONDS
        if elapsed > retract_from:
            return 1 - Easing.out_cubic((elapsed - retract_from) / self.RETRACT_SECONDS)
        return 1 + self._jab_depth(elapsed)

    def _jab_depth(self, elapsed: float) -> float:
        depth = 0.0
        for hit in self.hits:
            distance = abs(elapsed - hit)
            if distance < self.JAB_WINDOW:
                depth = max(depth, self.JAB_DEPTH * (1 - distance / self.JAB_WINDOW))
        return depth


class _Impact:
    """Where a jab hit the screen and when."""

    def __init__(self, moment: float, position: Point) -> None:
        self.moment = moment
        self.position = position


class PokeAnimation(Animation):
    """The general's arm coming at the screen: reaches out, jabs once or twice, holds and pulls back."""

    TILT_ODD = 12
    TILT_EVEN = -10
    CAPTION_SECONDS = 0.45
    STREAKS = 6

    def __init__(self, trajectory: PokeTrajectory, jabs: int, caption: str, font: pygame.font.Font) -> None:
        self._trajectory = trajectory
        self._timeline = _PokeTimeline(jabs)
        self._caption = caption
        self._font = font
        self._glove = GloveSprite().build()
        self._elapsed = 0.0
        self._jabs_landed = 0
        self._impacts: list[_Impact] = []

    @property
    def finished(self) -> bool:
        return self._elapsed >= self._timeline.duration

    @property
    def jabs_landed(self) -> int:
        """How many jabs hit the screen during the last update."""
        return self._jabs_landed

    def update(self, dt: float) -> None:
        before = self._elapsed
        self._elapsed += dt
        self._jabs_landed = 0
        for hit in self._timeline.hits:
            if before < hit <= self._elapsed:
                self._jabs_landed += 1
                self._impacts.append(_Impact(self._elapsed, self._glove_position(1.15)))

    def draw(self, surface: pygame.Surface) -> None:
        reach = self._timeline.reach(self._elapsed)
        if reach <= 0.01:
            return
        size = self._glove_size(reach)
        center = self._glove_position(reach)
        self._draw_sleeve(surface, center, size)
        glove = pygame.transform.scale(self._glove, (int(size), int(size)))
        surface.blit(glove, glove.get_rect(center=center))
        for impact in self._impacts:
            self._draw_impact(surface, impact, size)

    def _glove_size(self, reach: float) -> float:
        trajectory = self._trajectory
        size = trajectory.small_size + (trajectory.big_size - trajectory.small_size) * min(1.0, reach) ** 1.6
        return size * (1 + max(0.0, reach - 1))

    def _glove_position(self, reach: float) -> Point:
        trajectory = self._trajectory
        return trajectory.shoulder.toward(trajectory.target, min(1.0, reach)).truncated()

    def _draw_sleeve(self, surface: pygame.Surface, glove_center: Point, glove_size: float) -> None:
        """Seen head-on the arm is a short cone of sleeve between the fixed shoulder and the growing glove back."""
        canvas = Canvas(surface)
        shoulder = self._trajectory.shoulder
        shoulder_radius = self._trajectory.sleeve_half_width
        canvas.circle(Palette.OUTLINE, shoulder, shoulder_radius + 2)
        dx, dy = glove_center.x - shoulder.x, glove_center.y - shoulder.y
        length = math.hypot(dx, dy)
        if length > 1:
            self._draw_cone(canvas, glove_center, glove_size * 0.4, (-dy / length, dx / length))
        canvas.circle(Palette.OLIVE, shoulder, shoulder_radius)

    def _draw_cone(self, canvas: Canvas, glove_center: Point, glove_radius: float, normal: tuple[float, float]) -> None:
        shoulder = self._trajectory.shoulder
        shoulder_radius = self._trajectory.sleeve_half_width
        corners = self._cone_corners(shoulder, glove_center, (shoulder_radius, glove_radius), normal)
        outline = self._cone_corners(shoulder, glove_center, (shoulder_radius + 2, glove_radius + 2), normal)
        canvas.polygon(Palette.OUTLINE, outline)
        canvas.polygon(Palette.OLIVE, corners)
        canvas.line(Palette.OLIVE_DARK, corners[3], corners[2], width=max(1, int(shoulder_radius * 0.4)))

    @staticmethod
    def _cone_corners(near: Point, far: Point, radii: tuple[float, float], normal: tuple[float, float]) -> list[Point]:
        near_radius, far_radius = radii
        nx, ny = normal
        return [
            Point(near.x + nx * near_radius, near.y + ny * near_radius),
            Point(far.x + nx * far_radius, far.y + ny * far_radius),
            Point(far.x - nx * far_radius, far.y - ny * far_radius),
            Point(near.x - nx * near_radius, near.y - ny * near_radius),
        ]

    def _draw_impact(self, surface: pygame.Surface, impact: _Impact, glove_size: float) -> None:
        age = self._elapsed - impact.moment
        if age >= self.CAPTION_SECONDS:
            return
        self._draw_caption(surface, impact, age, glove_size)
        self._draw_streaks(surface, impact.position, age, glove_size)

    def _draw_caption(self, surface: pygame.Surface, impact: _Impact, age: float, glove_size: float) -> None:
        tilt = self.TILT_ODD if len(self._impacts) % 2 else self.TILT_EVEN
        hit_x, hit_y = impact.position
        center_x = max(34, hit_x - glove_size * 0.1)
        center_y = max(14, hit_y - glove_size * 0.68 - age * 24)
        for color, shadow_offset in ((Palette.OUTLINE, 2), (AnimationPalette.IMPACT_TEXT, 0)):
            image = pygame.transform.scale_by(self._font.render(self._caption, False, color), 2)
            image = pygame.transform.rotate(image, tilt)
            surface.blit(image, image.get_rect(center=(center_x + shadow_offset, center_y + shadow_offset)))

    def _draw_streaks(self, surface: pygame.Surface, impact: Point, age: float, glove_size: float) -> None:
        canvas = Canvas(surface)
        for index in range(self.STREAKS):
            angle = index / self.STREAKS * math.tau + 0.3
            inner, outer = glove_size * 0.55, glove_size * 0.55 + 10 + age * 30
            start = Point(impact.x + math.cos(angle) * inner, impact.y + math.sin(angle) * inner)
            end = Point(impact.x + math.cos(angle) * outer, impact.y + math.sin(angle) * outer)
            canvas.line(AnimationPalette.IMPACT_STREAK, start, end, width=2)
