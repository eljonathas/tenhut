from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.core import Phase, Theme

from ..geometry import Point
from .ambience import Ambience
from .balloon_flock import BalloonFlock
from .bunting import Bunting
from .confetti_shower import ConfettiShower
from .jet_squadron import JetSquadron
from .layer_cache import LayerCache
from .microphone import Microphone
from .outdoor_scene import OutdoorScene
from .parade_frame import ParadeFrame
from .parade_street import ParadeStreet
from .perspective_grid import PerspectiveGrid
from .podium import Podium
from .scene_anchors import SceneAnchors
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext
from .side import Side
from .sky_mask import SkyMask
from .street_banner import StreetBanner
from .street_builder import StreetBuilder
from .streetscape import Streetscape


class ParadeScene(OutdoorScene):
    """The victory parade: an avenue of cheering crowds, banners, bunting, jets and balloons, seen from the podium."""

    theme: ClassVar[Theme] = Theme.PARADE
    CLOUD_COLOR: ClassVar[None] = None

    PARTY_PHASES: ClassVar[frozenset[Phase]] = frozenset({Phase.VICTORY, Phase.SHORT, Phase.LONG})
    SKY_OVERLAP: ClassVar[int] = 4
    BUNTING_DEPTHS: ClassVar[tuple[float, ...]] = (5.5, 3.2, 2.0)
    BUNTING_DROP: ClassVar[float] = 0.15
    BANNER_ROOF_DEPTH: ClassVar[float] = 1.4
    MICROPHONE_OFFSET: ClassVar[int] = 10

    def __init__(self, ambience: Ambience, cache: LayerCache) -> None:
        super().__init__(ambience, cache)
        self._confetti = ConfettiShower()
        self._balloons = BalloonFlock()
        self._jets = JetSquadron()

    def _paint_background(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        sky = self._ambience.sky(self.theme, context.phase)
        sky.paint_gradient(canvas, pygame.Rect(0, 0, viewport.width, viewport.horizon_y + self.SKY_OVERLAP))
        sky.paint_body(canvas, viewport)
        bare_sky = canvas.surface.copy()
        grid = PerspectiveGrid(viewport)
        street = ParadeStreet(grid)
        street.paint(canvas)
        street.paint_skyline(canvas, sky.horizon_color)
        streetscape = StreetBuilder(grid).build(canvas)
        self._hang_decorations(canvas, grid, streetscape)
        anchors.crowd = streetscape.life.crowd
        anchors.banners = streetscape.life.banners
        mask = SkyMask(bare_sky, canvas.surface, viewport.horizon_y + self.SKY_OVERLAP)
        anchors.sky_mask = mask.surface

    def _hang_decorations(self, canvas: SceneCanvas, grid: PerspectiveGrid, streetscape: Streetscape) -> None:
        for depth in self.BUNTING_DEPTHS:
            left, right = grid.point_at(depth, Side.LEFT), grid.point_at(depth, Side.RIGHT)
            lower_roof = max(streetscape.roof_y(depth, Side.LEFT), streetscape.roof_y(depth, Side.RIGHT))
            top = lower_roof + (left.y - lower_roof) * self.BUNTING_DROP
            Bunting(depth, Point(left.x, top), Point(right.x, top)).draw(canvas)
        roofs = (
            streetscape.roof_corner(Side.LEFT, self.BANNER_ROOF_DEPTH),
            streetscape.roof_corner(Side.RIGHT, self.BANNER_ROOF_DEPTH),
        )
        StreetBanner(roofs, grid.vanishing_x, grid.horizon_y).draw(canvas)

    def _paint_foreground(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        Podium().draw(canvas, viewport)
        Microphone(viewport.vanishing_x + self.MICROPHONE_OFFSET, viewport.desk_y).draw(canvas)

    def _draw_scenery(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        frame = ParadeFrame(self._ambience.elapsed, context.phase in self.PARTY_PHASES, self._ambience.randomness)
        elapsed = self._ambience.elapsed
        if anchors.crowd is not None:
            anchors.crowd.draw(canvas, frame)
        for banner in anchors.banners:
            banner.draw(canvas, elapsed)
        self._confetti.draw(canvas, frame)
        self._balloons.draw(canvas, frame)
        self._jets.draw(canvas, frame, anchors.sky_mask)
