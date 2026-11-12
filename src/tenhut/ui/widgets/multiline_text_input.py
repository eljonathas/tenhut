from __future__ import annotations

from tenhut.game.geometry import Point
from tenhut.ui.painting import TextStyle, TextWrapper, UiCanvas

from .text_input import TextInput


class MultilineTextInput(TextInput):
    """A text field that wraps its text over several lines and shows the last ones."""

    LINE_HEIGHT = 13
    PADDING_Y = 4
    VERTICAL_MARGIN = 6

    def _draw_text(self, canvas: UiCanvas, shown: str, style: TextStyle) -> None:
        caret = self.CARET if self._caret_visible() else ""
        lines = TextWrapper(style.font).lines(shown + caret, self._rect.w - self.INNER_MARGIN)
        capacity = max(1, (self._rect.h - self.VERTICAL_MARGIN) // self.LINE_HEIGHT)
        for index, line in enumerate(lines[-capacity:]):
            canvas.write(
                line,
                Point(self._rect.x + self.PADDING_X, self._rect.y + self.PADDING_Y + index * self.LINE_HEIGHT),
                style,
            )

    def _clipboard_text(self, clipboard: str) -> str:
        return clipboard
