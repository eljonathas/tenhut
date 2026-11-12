"""Gera o ícone do app (estilo macOS: squircle 824/1024 com sombra) a partir do sprite do general.

    uv run python tools/make_icon.py

Saída: assets/icons/icon-<tamanho>.png (16 … 1024). Sem texto: só o general dos ombros para cima.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tenhut.game.character import Character, Mood, PoseName  # noqa: E402
from tenhut.game.geometry import Point  # noqa: E402

CANVAS = 1024
BODY = 824  # grade de ícones do macOS (Big Sur+): corpo 824x824 centrado, sobra para a sombra
GRID = 63  # arte em pixels "de verdade", ampliada 13x (819 px) dentro do corpo
SCALE = 13
OUT_DIR = ROOT / "src" / "tenhut" / "assets" / "icons"
SIZES = [16, 24, 32, 48, 64, 128, 256, 512, 1024]


def squircle_mask(size: int, n: float = 5.0, ss: int = 4) -> pygame.Surface:
    """Máscara de superelipse (|x|^n + |y|^n = 1) com antialias por supersampling."""
    big = size * ss
    m = pygame.Surface((big, big), pygame.SRCALPHA)
    a = big / 2
    for y in range(big):
        v = abs((y + 0.5 - a) / a)
        if v >= 1:
            continue
        half = a * (1 - v**n) ** (1 / n)
        pygame.draw.line(m, (255, 255, 255, 255), (a - half, y), (a + half - 1, y))
    return pygame.transform.smoothscale(m, (size, size))


def blur(surf: pygame.Surface, radius: int) -> pygame.Surface:
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // radius), max(1, h // radius)))
    for _ in range(2):
        small = pygame.transform.smoothscale(
            small, (max(1, small.get_width() // 2 * 2), max(1, small.get_height() // 2 * 2))
        )
    return pygame.transform.smoothscale(small, (w, h))


def art() -> pygame.Surface:
    """Arte em 63x63 px: raios de sol estilo medalha + general dos ombros para cima, bem de perto."""
    s = pygame.Surface((GRID, GRID))
    c = GRID // 2
    # fundo: raios alternados saindo de trás da cabeça
    cy = 24
    s.fill((214, 120, 52))
    for i in range(16):
        a0 = i / 16 * math.tau
        a1 = (i + 0.5) / 16 * math.tau
        r = GRID * 2
        col = (242, 168, 70) if i % 2 == 0 else (226, 140, 58)
        pygame.draw.polygon(
            s,
            col,
            [(c, cy), (c + math.cos(a0) * r, cy + math.sin(a0) * r), (c + math.cos(a1) * r, cy + math.sin(a1) * r)],
        )
    # vinheta em degraus (escurece as bordas, mantém o pixel art)
    for k, alpha in ((0, 40), (3, 28), (6, 16)):
        ov = pygame.Surface((GRID, GRID), pygame.SRCALPHA)
        pygame.draw.rect(ov, (90, 30, 20, alpha), ov.get_rect(), 3 + k)
        s.blit(ov, (0, 0))
    # brilho atrás da cabeça
    pygame.draw.circle(s, (250, 196, 96), (c, cy), 21)
    pygame.draw.circle(s, (254, 214, 120), (c, cy), 15)
    # o general: sério, olhando para você, sem piscar
    general = Character()
    general.show(Mood.STERN, PoseName.BEHIND)
    general.freeze(elapsed=1.4, look=Point(0.0, 0.15))  # breathing at its neutral point
    spr = general.render()  # 74x98 com contorno
    crop = spr.subsurface((5, 0, 64, 56)).copy()  # cabeça + ombros (dragonas e medalhas)
    s.blit(crop, ((GRID - 64) // 2, GRID - 56 + 3))
    return s


def build() -> pygame.Surface:
    pygame.init()
    body = pygame.Surface((BODY, BODY), pygame.SRCALPHA)
    body.fill((214, 120, 52))
    body.blit(pygame.transform.scale_by(art(), SCALE), ((BODY - GRID * SCALE) // 2, (BODY - GRID * SCALE) // 2))
    # brilho sutil no topo (como os ícones do macOS)
    hi = pygame.Surface((BODY, BODY // 2), pygame.SRCALPHA)
    for y in range(BODY // 2):
        hi.fill((255, 255, 255, int(26 * (1 - y / (BODY / 2)))), (0, y, BODY, 1))
    body.blit(hi, (0, 0))
    mask = squircle_mask(BODY)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    canvas = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    off = (CANVAS - BODY) // 2
    # sombra projetada suave
    shadow = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    sm = mask.copy()
    sm.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sm.set_alpha(110)
    shadow.blit(sm, (off, off + 14))
    canvas.blit(blur(shadow, 24), (0, 0))
    canvas.blit(body, (off, off))
    return canvas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    icon = build()
    for size in SIZES:
        img = icon if size == CANVAS else pygame.transform.smoothscale(icon, (size, size))
        pygame.image.save(img, OUT_DIR / f"icon-{size}.png")
    print("ícones em", OUT_DIR)


if __name__ == "__main__":
    main()
