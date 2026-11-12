from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

import pygame

from tenhut.core import Theme

from ..geometry import Point
from .ambience import Ambience
from .desk_state import DeskState
from .layer_cache import LayerCache
from .scene_anchors import SceneAnchors
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext
from .scene_key import SceneKey
from .scene_layers import SceneLayers

TRANSPARENT = (0, 0, 0, 0)


class Scene(ABC):
    """One campaign stage seen from the soldier's seat.

    The static art lives in two cached layers: the background (behind the general) and the foreground
    (the desk in front of him). Each frame only the animated objects are drawn on top of those.
    """

    theme: ClassVar[Theme]

    def __init__(self, ambience: Ambience, cache: LayerCache) -> None:
        self._ambience = ambience
        self._cache = cache

    def background_layer(self, context: SceneContext) -> pygame.Surface:
        return self._layers(context).background

    def foreground_layer(self, context: SceneContext) -> pygame.Surface:
        return self._layers(context).foreground

    def draw_background(self, surface: pygame.Surface, context: SceneContext) -> None:
        fitted = context.fitted_to(surface.get_size())
        self._ambience.resize(fitted.viewport.size)
        layers = self._layers(fitted)
        surface.blit(layers.background, (0, 0))
        canvas = SceneCanvas(surface)
        self._draw_weather(canvas, fitted)
        self._draw_scenery(canvas, fitted, layers.anchors)
        self._ambience.fireworks.draw(canvas)

    def draw_foreground(self, surface: pygame.Surface, context: SceneContext, desk: DeskState) -> None:
        layers = self._layers(context.fitted_to(surface.get_size()))
        surface.fill(TRANSPARENT)
        surface.blit(layers.foreground, desk.shake)
        canvas = SceneCanvas(surface)
        anchors, shake = layers.anchors, desk.shake
        if anchors.clipboard is not None:
            anchors.clipboard.draw(canvas, desk.tasks, Point(shake.x, shake.y - desk.hop // 2))
        if anchors.mug is not None:
            anchors.mug.draw(canvas, self._ambience.elapsed, Point(shake.x, shake.y - desk.hop))
        self._ambience.confetti.draw(canvas)

    @abstractmethod
    def _paint_background(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None: ...

    @abstractmethod
    def _paint_foreground(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None: ...

    @abstractmethod
    def _draw_scenery(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        """The animated objects of this scene, drawn over the cached background every frame."""

    @abstractmethod
    def _draw_weather(self, canvas: SceneCanvas, context: SceneContext) -> None:
        """Clouds and birds, drawn before the scene's own animated objects."""

    def _layers(self, context: SceneContext) -> SceneLayers:
        key = SceneKey.of(self.theme, context)
        layers = self._cache.get(key)
        if layers is None:
            layers = self._build_layers(context)
            self._cache.put(key, layers)
        return layers

    def _build_layers(self, context: SceneContext) -> SceneLayers:
        size = context.viewport.size
        background = pygame.Surface(size)
        foreground = pygame.Surface(size, pygame.SRCALPHA)
        anchors = SceneAnchors()
        self._paint_background(SceneCanvas(background), context, anchors)
        self._paint_foreground(SceneCanvas(foreground), context, anchors)
        return SceneLayers(background, foreground, anchors)
