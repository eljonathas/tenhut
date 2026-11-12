from __future__ import annotations

from tenhut.controllers import ResizeController
from tenhut.controllers.input import (
    FocusHandler,
    InputRouter,
    KeyHandler,
    MouseMotionHandler,
    MousePressHandler,
    MouseReleaseHandler,
    PointerTranslator,
    PokeBackResponder,
    QuitHandler,
    ResizeHandler,
    TextInputHandler,
    VisibilityHandler,
    WheelHandler,
)

from .controller_parts import ControllerParts
from .world_parts import WorldParts


class InputAssembly:
    """Creates the router that sends each input event to its handler."""

    def __init__(self, world: WorldParts, controllers: ControllerParts, resizing: ResizeController) -> None:
        self._world = world
        self._controllers = controllers
        self._resizing = resizing

    def assemble(self) -> InputRouter:
        world, controllers = self._world, self._controllers
        page, translator = controllers.navigator, PointerTranslator(world.screen)
        return InputRouter(
            [
                QuitHandler(controllers.quitting),
                ResizeHandler(self._resizing),
                FocusHandler(controllers.run_state),
                VisibilityHandler.hiding(controllers.run_state),
                VisibilityHandler.showing(controllers.run_state),
                MouseMotionHandler(page, controllers.attention, translator),
                self._press_handler(translator),
                MouseReleaseHandler(page, translator),
                WheelHandler(page),
                KeyHandler(page),
                TextInputHandler(page),
            ]
        )

    def _press_handler(self, translator: PointerTranslator) -> MousePressHandler:
        world, controllers = self._world, self._controllers
        poke_back = PokeBackResponder(
            world.session,
            world.screen,
            controllers.judge_slot,
            gestures=controllers.gestures,
            balloon=world.balloon,
            speech=controllers.speech,
        )
        return MousePressHandler(
            controllers.navigator,
            translator,
            world.screen,
            navigation=controllers.navigator,
            balloon=world.balloon,
            poke_back=poke_back,
        )
