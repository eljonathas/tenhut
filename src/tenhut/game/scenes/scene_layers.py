from __future__ import annotations

from dataclasses import dataclass

import pygame

from .scene_anchors import SceneAnchors


@dataclass(frozen=True, slots=True)
class SceneLayers:
    """A scene's cached static art: what is behind the general, what is in front, and the placed objects."""

    background: pygame.Surface
    foreground: pygame.Surface
    anchors: SceneAnchors
