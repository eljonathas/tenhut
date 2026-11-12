from __future__ import annotations

from dataclasses import dataclass

import pygame

from .banner import Banner
from .clipboard import Clipboard
from .crowd import Crowd
from .flag import Flag
from .lamp import Lamp
from .mug import Mug
from .wall_clock import WallClock


@dataclass(slots=True)
class SceneAnchors:
    """The animated or per-frame objects a scene placed while painting its static layers."""

    flag: Flag | None = None
    lamp: Lamp | None = None
    clock: WallClock | None = None
    clipboard: Clipboard | None = None
    mug: Mug | None = None
    smoke_source_y: int | None = None
    crowd: Crowd | None = None
    banners: tuple[Banner, ...] = ()
    sky_mask: pygame.Surface | None = None
