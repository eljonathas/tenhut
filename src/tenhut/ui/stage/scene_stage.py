from __future__ import annotations

import pygame

from tenhut.controllers.gestures import Gestures
from tenhut.controllers.resize_listener import ResizeListener
from tenhut.controllers.tickable import Tickable
from tenhut.core import Phase, Session, Theme
from tenhut.game.character import Character
from tenhut.game.geometry import Point
from tenhut.game.scenes import DeskState, SceneContext, SceneRegistry, Viewport
from tenhut.ui.layout import Layout, LayoutProvider

from .general_layer import GeneralLayer
from .stage_transitions import StageTransitions


class SceneStage(ResizeListener, Tickable):
    """The point-of-view scenery: background, the general behind his desk, foreground, then the curtain."""

    INITIAL_WORLD = (280, 180)

    def __init__(
        self,
        scenes: SceneRegistry,
        general: Character,
        session: Session,
        *,
        layouts: LayoutProvider,
        gestures: Gestures,
        transitions: StageTransitions,
        general_layer: GeneralLayer,
    ) -> None:
        self._scenes = scenes
        self._general = general
        self._session = session
        self._layouts = layouts
        self._gestures = gestures
        self._transitions = transitions
        self._general_layer = general_layer
        self._background = pygame.Surface(self.INITIAL_WORLD)
        self._foreground = pygame.Surface(self.INITIAL_WORLD, pygame.SRCALPHA)
        self._surface = pygame.Surface(self.INITIAL_WORLD)

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    def layout_changed(self) -> None:
        layout = self._layouts.layout
        if self._background.get_size() != tuple(layout.world):
            self._background = pygame.Surface(layout.world)
            self._foreground = pygame.Surface(layout.world, pygame.SRCALPHA)
        self._surface = pygame.Surface(layout.scene.size)
        self._transitions.cancel_curtain()

    def tick(self, dt: float) -> None:
        self._transitions.update(dt)
        self._general.update(dt)
        self._scenes.update(dt)

    def render(self) -> pygame.Surface:
        """Draws the current frame of the scene and returns its surface."""
        session = self._session
        theme = Theme.for_progress(session.done_count(), len(session.tasks), session.phase, session.in_mission)
        self._transitions.observe(theme, self._surface)
        self._compose(self._layouts.layout, theme)
        self._transitions.draw_curtain(self._surface)
        return self._surface

    def _compose(self, layout: Layout, theme: Theme) -> None:
        phase = self._session.phase
        self._scenes.fireworks = phase is Phase.VICTORY
        scene = self._scenes.scene_for(theme)
        viewport = Viewport(*self._background.get_size(), layout.vanishing_x, layout.horizon_y)
        context = SceneContext(phase, viewport)
        scene.draw_background(self._background, context)
        slam = self._gestures.slam
        shake, hop = (slam.shake, slam.hop) if slam else (Point(0, 0), 0)
        scene.draw_foreground(self._foreground, context, DeskState(self._session.tasks, shake, hop))
        self._surface.blit(self._scaled(self._background, layout.world_scale), (0, 0))
        self._general_layer.draw_onto(self._surface, layout)
        self._surface.blit(self._scaled(self._foreground, layout.world_scale), (0, 0))
        if slam:
            slam.place(layout.slam_placement())
            slam.draw(self._surface)

    @staticmethod
    def _scaled(surface: pygame.Surface, scale: int) -> pygame.Surface:
        return pygame.transform.scale_by(surface, scale) if scale > 1 else surface
