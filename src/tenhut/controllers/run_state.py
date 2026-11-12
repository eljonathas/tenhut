from __future__ import annotations


class RunState:
    """Whether the main loop keeps going, and whether the window has focus or is hidden."""

    def __init__(self) -> None:
        self._running = True
        self._focused = True
        self._hidden = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def focused(self) -> bool:
        return self._focused

    @property
    def hidden(self) -> bool:
        return self._hidden

    def stop(self) -> None:
        self._running = False

    def focus(self, focused: bool) -> None:
        self._focused = focused

    def hide(self, hidden: bool) -> None:
        self._hidden = hidden
