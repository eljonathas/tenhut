from __future__ import annotations

import pygame

from tenhut.controllers.page_id import PageId

from .application_options import ApplicationOptions
from .application_parts import ApplicationParts
from .assembly.application_assembly import ApplicationAssembly
from .controllers.fps_policy import FpsPolicy


class Application:
    """The running application: builds everything, then pumps events, ticks and draws until the soldier leaves."""

    MAX_FRAME_SECONDS = 0.5

    def __init__(self, options: ApplicationOptions | None = None) -> None:
        pygame.init()
        self._parts = ApplicationAssembly(options or ApplicationOptions()).assemble()
        controllers = self._parts.controllers
        self._parts.resizing.resize(force=True)
        controllers.navigator.open(PageId.MAIN)
        controllers.greeter.greet()
        pygame.key.start_text_input()

    @property
    def parts(self) -> ApplicationParts:
        return self._parts

    def resize(self) -> None:
        self._parts.resizing.resize()

    def handle(self, event: pygame.event.Event) -> None:
        self._parts.router.dispatch(event)

    def tick(self, dt: float) -> None:
        for ticker in self._parts.tickers:
            ticker.tick(dt)

    def draw(self) -> None:
        self._parts.renderer.draw()

    def run(self) -> None:
        clock = pygame.time.Clock()
        state = self._parts.controllers.run_state
        try:
            while state.running:
                dt = min(self.MAX_FRAME_SECONDS, clock.tick(FpsPolicy.frames_per_second(state)) / 1000)
                for event in pygame.event.get():
                    self.handle(event)
                self.tick(dt)
                if not state.hidden:
                    self.draw()
        finally:
            self.shutdown()
            pygame.quit()

    def shutdown(self) -> None:
        controllers = self._parts.controllers
        self._parts.world.session.save()
        controllers.camera_holder.shutdown()
        controllers.blocking.lock_for_exit()
