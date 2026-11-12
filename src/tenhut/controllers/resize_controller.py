from __future__ import annotations

from tenhut.ui.layout import LogicalScreen

from .gesture_controller import GestureController
from .resize_listener import ResizeListener
from .window_control import WindowControl


class ResizeController:
    """Adapts the logical screen, the stage and the page to a new window size."""

    def __init__(
        self,
        screen: LogicalScreen,
        window: WindowControl,
        gestures: GestureController,
        *,
        listeners: list[ResizeListener],
    ) -> None:
        self._screen = screen
        self._window = window
        self._gestures = gestures
        self._listeners = listeners

    def resize(self, force: bool = False) -> None:
        if not self._screen.resize(self._window.size, force=force):
            return
        self._gestures.cancel_poke()
        for listener in self._listeners:
            listener.layout_changed()
