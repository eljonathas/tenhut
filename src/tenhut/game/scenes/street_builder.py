from __future__ import annotations

import random
from typing import ClassVar

import pygame

from ..painting import Canvas, Rgb
from .banner import Banner
from .crowd import Crowd
from .crowd_member import CrowdMember
from .facade import Facade
from .perspective_grid import PerspectiveGrid
from .side import Side
from .street_life import StreetLife
from .streetscape import Streetscape


class StreetBuilder:
    """Paints the rows of buildings lining the avenue, inventing their heights, lit windows, banners and crowds.

    Every random draw comes from one seeded generator in a fixed order, so the street looks the same every run.
    """

    SEED: ClassVar[int] = 21
    DEPTHS: ClassVar[tuple[float, ...]] = (9, 6.5, 4.8, 3.5, 2.6, 1.9, 1.4, 1.0)
    TALL_NEAR_DEPTH: ClassVar[float] = 1.4
    FACADE_COLORS: ClassVar[tuple[Rgb, ...]] = (
        Rgb(196, 92, 70),
        Rgb(232, 214, 170),
        Rgb(120, 150, 176),
        Rgb(214, 160, 96),
        Rgb(170, 110, 130),
        Rgb(150, 170, 120),
    )
    RIGHT_SIDE_COLOR_SHIFT: ClassVar[int] = 3
    BANNER_SEGMENTS: ClassVar[tuple[int, ...]] = (2, 4, 5)
    SHIRTS: ClassVar[tuple[Rgb, ...]] = (
        Rgb(200, 60, 60),
        Rgb(60, 90, 170),
        Rgb(240, 240, 240),
        Rgb(80, 140, 80),
        Rgb(230, 180, 60),
    )
    HAIRS: ClassVar[tuple[Rgb, ...]] = (Rgb(70, 46, 30), Rgb(30, 26, 24), Rgb(200, 160, 90), Rgb(120, 80, 50))
    SPECTATORS_PER_BUILDING: ClassVar[int] = 3
    KERB_INSET: ClassVar[float] = 8

    def __init__(self, grid: PerspectiveGrid) -> None:
        self._grid = grid
        self._rng = random.Random(self.SEED)

    def build(self, canvas: Canvas) -> Streetscape:
        facades: list[Facade] = []
        spectators: list[CrowdMember] = []
        banners: list[Banner] = []
        for side in Side:
            for index in range(len(self.DEPTHS) - 1):
                facade = self._new_facade(side, index)
                facade.draw(canvas, self._rng)
                facades.append(facade)
                if index in self.BANNER_SEGMENTS:
                    banners.append(self._banner_on(facade))
                spectators.extend(self._spectators_before(facade))
        return Streetscape(self._grid, facades, StreetLife(Crowd(spectators), tuple(banners)))

    def _new_facade(self, side: Side, index: int) -> Facade:
        far, near = self.DEPTHS[index], self.DEPTHS[index + 1]
        tall = near <= self.TALL_NEAR_DEPTH
        share = self._rng.uniform(0.9, 1.0) if tall else self._rng.uniform(0.42, 0.7)
        shift = self.RIGHT_SIDE_COLOR_SHIFT if side is Side.RIGHT else 0
        color = self.FACADE_COLORS[(index + shift) % len(self.FACADE_COLORS)]
        return Facade(self._grid, side, far, near, share * self._grid.horizon_y, color)

    def _banner_on(self, facade: Facade) -> Banner:
        near = facade.near
        foot = self._grid.point_at(near, facade.side)
        roof_y = facade.roof_y(near)
        width = max(3, int(8 / near))
        left = int(foot.x - facade.side * (5 / near)) - (width if facade.side is Side.RIGHT else 0)
        area = pygame.Rect(left, int(roof_y + (foot.y - roof_y) * 0.12), width, max(6, int(24 / near)))
        return Banner(area, self._rng.uniform(0, 6))

    def _spectators_before(self, facade: Facade) -> list[CrowdMember]:
        members = []
        for spot in range(self.SPECTATORS_PER_BUILDING):
            depth = facade.far + (facade.near - facade.far) * (spot + 0.5) / self.SPECTATORS_PER_BUILDING
            foot = self._grid.point_at(depth, facade.side)
            x = foot.x - facade.side * self.KERB_INSET / depth
            members.append(
                CrowdMember(
                    x,
                    foot.y,
                    1 / depth,
                    self._rng.choice(self.SHIRTS),
                    self._rng.choice(self.HAIRS),
                    self._rng.uniform(0, 6),
                )
            )
        return members
