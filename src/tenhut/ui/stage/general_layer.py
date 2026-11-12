from __future__ import annotations

import pygame

from tenhut.game.character import Character
from tenhut.game.painting import Canvas
from tenhut.ui.layout import Layout

from .general_overlay import GeneralOverlay


class GeneralLayer:
    """The general's sprite and the marks around it, drawn on a small transparent layer and scaled onto the scene."""

    SIZE = (110, 112)
    SPRITE_ORIGIN = (18, 12)
    LAYER_ANCHOR = (55, 12)
    CLEAR = (0, 0, 0, 0)

    def __init__(
        self, general: Character, exclusive: tuple[GeneralOverlay, ...], extra: tuple[GeneralOverlay, ...]
    ) -> None:
        self._general = general
        self._exclusive = exclusive
        self._extra = extra
        self._layer = pygame.Surface(self.SIZE, pygame.SRCALPHA)

    def draw_onto(self, scene: pygame.Surface, layout: Layout) -> None:
        layer = self._layer
        layer.fill(self.CLEAR)
        jitter = self._general.jitter()
        layer.blit(self._general.render(), (self.SPRITE_ORIGIN[0] + jitter.x, self.SPRITE_ORIGIN[1] + jitter.y))
        canvas = Canvas(layer)
        first = next((overlay for overlay in self._exclusive if overlay.applies()), None)
        for overlay in (first, *self._extra):
            if overlay is not None and overlay.applies():
                overlay.draw(canvas)
        scale = layout.general_scale
        image = pygame.transform.scale_by(layer, scale) if scale > 1 else layer
        scene.blit(
            image,
            (
                layout.general_x - self.LAYER_ANCHOR[0] * scale - layout.scene.x,
                layout.general_top - self.LAYER_ANCHOR[1] * scale - layout.scene.y,
            ),
        )
