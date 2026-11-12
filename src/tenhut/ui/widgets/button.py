from __future__ import annotations

import pygame

from tenhut.game.animations import Lettering
from tenhut.game.geometry import Point
from tenhut.game.painting import Rgb
from tenhut.ui.painting import TextAlign, TextStyle, UiCanvas, UiPalette

from .button_spec import ButtonAction, ButtonSpec
from .button_style import ButtonStyle
from .widget import Widget


class Button(Widget):
    """A pixel-art push button; the action runs when the left button is released over it."""

    PRESS_OFFSET = 2
    FACE_BOTTOM_INSET = 4
    HIGHLIGHT_END_INSET = 3
    SHADOW_OFFSET = 3
    HOVER_GLOW = 22
    HIGHLIGHT_GLOW = 40
    LABEL_MARGIN = 8
    ELLIPSIS_MARGIN = 4
    LABEL_LIFT = 1

    def __init__(self, rect: pygame.Rect | tuple[int, int, int, int], spec: ButtonSpec) -> None:
        self._rect = pygame.Rect(rect)
        self._label = spec.label
        self._action = spec.action
        self._style = spec.style
        self._enabled = spec.enabled
        self._hover = False
        self._down = False
        self._handlers = {
            pygame.MOUSEMOTION: self._on_motion,
            pygame.MOUSEBUTTONDOWN: self._on_press,
            pygame.MOUSEBUTTONUP: self._on_release,
        }

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def label(self) -> str:
        return self._label

    @property
    def action(self) -> ButtonAction:
        return self._action

    @property
    def style(self) -> ButtonStyle:
        return self._style

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    @property
    def hovered(self) -> bool:
        return self._hover

    @property
    def pressed(self) -> bool:
        return self._down

    def handle_event(self, event: pygame.event.Event) -> bool:
        handler = self._handlers.get(event.type)
        return handler(event) if handler else False

    def draw(self, canvas: UiCanvas) -> None:
        shapes = canvas.shapes
        face, shade = self._colors()
        area = self._rect.move(0, self.PRESS_OFFSET if self._down else 0)
        shapes.rect(UiPalette.INK, self._rect.move(0, self.SHADOW_OFFSET))
        shapes.rect(UiPalette.INK, area)
        shapes.rect(shade, area.inflate(-2, -2))
        shapes.rect(face, (area.x + 1, area.y + 1, area.w - 2, area.h - self.FACE_BOTTOM_INSET))
        shapes.line(
            face.brightened(self.HIGHLIGHT_GLOW),
            (area.x + 2, area.y + 2),
            (area.right - self.HIGHLIGHT_END_INSET, area.y + 2),
        )
        self._draw_label(canvas, area)

    def _colors(self) -> tuple[Rgb, Rgb]:
        if not self._enabled:
            return UiPalette.DISABLED_FACE, UiPalette.DISABLED_SHADE
        face, shade = self._style.face, self._style.shade
        return (face.brightened(self.HOVER_GLOW) if self._hover and not self._down else face), shade

    def _draw_label(self, canvas: UiCanvas, area: pygame.Rect) -> None:
        fonts = canvas.fonts
        font = fonts.body if fonts.body.size(self._label)[0] <= area.w - self.LABEL_MARGIN else fonts.small
        label = Lettering(font).fitted(self._label, area.w - self.ELLIPSIS_MARGIN)
        color = UiPalette.INK if self._enabled else UiPalette.DISABLED_TEXT
        center = Point(area.centerx, area.centery - self.LABEL_LIFT)
        canvas.write(label, center, TextStyle(font, color, TextAlign.CENTER))

    def _on_motion(self, event: pygame.event.Event) -> bool:
        self._hover = self._rect.collidepoint(event.pos)
        return False

    def _on_press(self, event: pygame.event.Event) -> bool:
        if event.button == pygame.BUTTON_LEFT and self._rect.collidepoint(event.pos):
            self._down = True
        return False

    def _on_release(self, event: pygame.event.Event) -> bool:
        if event.button != pygame.BUTTON_LEFT:
            return False
        was_down, self._down = self._down, False
        if was_down and self._rect.collidepoint(event.pos) and self._enabled:
            self._action()
            return True
        return False
