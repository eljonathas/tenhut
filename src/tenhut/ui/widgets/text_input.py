from __future__ import annotations

from collections.abc import Callable

import pygame

from tenhut.game.geometry import Point
from tenhut.game.painting import Rgb
from tenhut.ui.painting import TextStyle, UiCanvas, UiPalette

from .widget import Widget


class TextInput(Widget):
    """A one-line text field with a blinking caret."""

    DEFAULT_MAX_LENGTH = 300
    CARET = "▌"
    BLINKS_PER_SECOND = 2
    PADDING_X = 5
    INNER_MARGIN = 10
    BASELINE_LIFT = 7
    NON_TEXT_KEYS = (pygame.K_TAB, pygame.K_ESCAPE)

    def __init__(
        self, rect: pygame.Rect | tuple[int, int, int, int], placeholder: str = "", max_length: int = DEFAULT_MAX_LENGTH
    ) -> None:
        self._rect = pygame.Rect(rect)
        self._text = ""
        self._placeholder = placeholder
        self._max_length = max_length
        self._focused = False
        self._age = 0.0
        self._on_submit: Callable[[], None] | None = None
        self._handlers = {
            pygame.MOUSEBUTTONDOWN: self._on_click,
            pygame.TEXTINPUT: self._on_text,
            pygame.KEYDOWN: self._on_key,
        }
        self._key_actions = {
            pygame.K_BACKSPACE: self._backspace,
            pygame.K_RETURN: self._submit,
            pygame.K_KP_ENTER: self._submit,
            pygame.K_v: self._paste,
        }

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, focused: bool) -> None:
        self._focused = focused

    def on_submit(self, action: Callable[[], None]) -> None:
        """Runs ``action`` when Enter is pressed in the field."""
        self._on_submit = action

    def clear(self) -> None:
        self._text = ""

    def update(self, dt: float) -> None:
        self._age += dt

    def handle_event(self, event: pygame.event.Event) -> bool:
        handler = self._handlers.get(event.type)
        if handler is None:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            return handler(event)
        return self._focused and handler(event)

    def draw(self, canvas: UiCanvas) -> None:
        canvas.shapes.rect(UiPalette.INK, self._rect)
        canvas.shapes.rect(UiPalette.PAPER if self._focused else UiPalette.FIELD_IDLE, self._rect.inflate(-2, -2))
        shown, color = self._shown_text()
        self._draw_text(canvas, shown, TextStyle(canvas.fonts.body, color))

    def _shown_text(self) -> tuple[str, Rgb]:
        if not self._text and not self._focused:
            return self._placeholder, UiPalette.FIELD_HINT
        return self._text, UiPalette.INK

    def _caret_visible(self) -> bool:
        return self._focused and int(self._age * self.BLINKS_PER_SECOND) % 2 == 0

    def _draw_text(self, canvas: UiCanvas, shown: str, style: TextStyle) -> None:
        inner_width = self._rect.w - self.INNER_MARGIN
        while style.font.size(shown + self.CARET)[0] > inner_width and shown:
            shown = shown[1:]
        if self._caret_visible():
            shown += self.CARET
        canvas.write(shown, Point(self._rect.x + self.PADDING_X, self._rect.centery - self.BASELINE_LIFT), style)

    def _clipboard_text(self, clipboard: str) -> str:
        return clipboard.replace("\n", " ")

    def _on_click(self, event: pygame.event.Event) -> bool:
        if event.button != pygame.BUTTON_LEFT:
            return False
        self._focused = self._rect.collidepoint(event.pos)
        return self._focused

    def _on_text(self, event: pygame.event.Event) -> bool:
        if len(self._text) < self._max_length:
            self._text += event.text
        return True

    def _on_key(self, event: pygame.event.Event) -> bool:
        action = self._key_actions.get(event.key)
        if action is None:
            return event.key not in self.NON_TEXT_KEYS
        action(pygame.key.get_mods())
        return True

    def _backspace(self, modifiers: int) -> None:
        if modifiers & pygame.KMOD_CTRL:
            stripped = self._text.rstrip()
            self._text = stripped[: stripped.rfind(" ") + 1] if " " in stripped else ""
        else:
            self._text = self._text[:-1]

    def _submit(self, modifiers: int) -> None:
        if self._on_submit:
            self._on_submit()

    def _paste(self, modifiers: int) -> None:
        if not modifiers & pygame.KMOD_CTRL:
            return
        try:
            clipboard = pygame.scrap.get_text() or ""
        except (pygame.error, AttributeError):
            clipboard = ""
        self._text = (self._text + self._clipboard_text(clipboard))[: self._max_length]
