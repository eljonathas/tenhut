from __future__ import annotations

from dataclasses import dataclass

from tenhut.assembly.controller_parts import ControllerParts
from tenhut.assembly.platform_parts import PlatformParts
from tenhut.assembly.world_parts import WorldParts
from tenhut.controllers import ResizeController, Tickable
from tenhut.controllers.input import InputRouter
from tenhut.ui.stage import FrameRenderer, SceneStage


@dataclass(frozen=True, slots=True)
class ApplicationParts:
    """Everything the application is made of."""

    platform: PlatformParts
    world: WorldParts
    controllers: ControllerParts
    resizing: ResizeController
    stage: SceneStage
    renderer: FrameRenderer
    router: InputRouter
    tickers: tuple[Tickable, ...]
