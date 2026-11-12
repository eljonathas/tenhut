from __future__ import annotations

from tenhut.game.scenes import Viewport

from .layout import Layout
from .layout_strategy import LayoutStrategy
from .mini_layout import MiniLayout
from .size import Size
from .tall_layout import TallLayout
from .wide_layout import WideLayout


class LayoutFactory:
    """Picks the layout mode that fits a logical screen size and works out the scene geometry."""

    DOUBLING_MIN_WIDTH = 260
    BELT_HEIGHT = 66
    MIN_SKY_HEIGHT = 64
    EYE_LEVEL = 40
    MIN_HORIZON = 12
    DESK_CLEARANCE = 10

    def __init__(self, strategies: tuple[LayoutStrategy, ...] | None = None) -> None:
        self._strategies = strategies or (WideLayout(), TallLayout(), MiniLayout())

    def strategy_for(self, size: Size) -> LayoutStrategy:
        return next(strategy for strategy in self._strategies if strategy.accepts(size))

    def create(self, size: Size) -> Layout:
        strategy = self.strategy_for(size)
        frame = strategy.frame(size)
        scene = frame.scene
        doubled = scene.h >= strategy.doubling_height and scene.w >= self.DOUBLING_MIN_WIDTH
        scale = 2 if doubled else 1
        world = Size(-(-scene.w // scale), -(-scene.h // scale))
        desk_top = Viewport.desk_top_for(world.height)
        general_scale = self._general_scale(scale, desk_top * scale)
        general_top = scene.y + desk_top * scale - self.BELT_HEIGHT * general_scale
        horizon = max(
            self.MIN_HORIZON,
            min(desk_top - self.DESK_CLEARANCE, (general_top + self.EYE_LEVEL * general_scale - scene.y) // scale),
        )
        vanishing_x = (frame.general_x - scene.x) // scale
        return Layout(size, strategy, frame, scale, world, vanishing_x, horizon, desk_top, general_scale, general_top)

    def _general_scale(self, world_scale: int, desk_offset: int) -> int:
        scale = world_scale + 1
        if desk_offset - self.BELT_HEIGHT * scale < self.MIN_SKY_HEIGHT:
            return world_scale
        return scale
