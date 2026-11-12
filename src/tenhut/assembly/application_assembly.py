from __future__ import annotations

from tenhut.application_options import ApplicationOptions
from tenhut.application_parts import ApplicationParts
from tenhut.controllers import ResizeController

from .controller_assembly import ControllerAssembly
from .input_assembly import InputAssembly
from .page_assembly import PageAssembly
from .platform_assembly import PlatformAssembly
from .stage_assembly import StageAssembly
from .world_assembly import WorldAssembly


class ApplicationAssembly:
    """Builds the whole object graph of the application."""

    def __init__(self, options: ApplicationOptions) -> None:
        self._options = options

    def assemble(self) -> ApplicationParts:
        platform = PlatformAssembly().assemble()
        world = WorldAssembly(platform, self._options).assemble()
        controllers = ControllerAssembly(platform, world).assemble()
        stage, renderer = StageAssembly(platform, world, controllers).assemble()
        PageAssembly(platform, world, controllers).assemble()
        resizing = ResizeController(
            world.screen, world.window, controllers.gestures, listeners=[stage, controllers.navigator]
        )
        router = InputAssembly(world, controllers, resizing).assemble()
        tickers = (*controllers.early_tickers, stage, *controllers.late_tickers)
        return ApplicationParts(platform, world, controllers, resizing, stage, renderer, router, tickers)
