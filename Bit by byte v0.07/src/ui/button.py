"""
ui/button.py — Pixel-art styled Button component.

You can subclass or swap draw() to load a BMP image as the button face.
"""
import pygame
from src.settings import (
    UI_PANEL, UI_PANEL2, UI_BORDER, UI_TEXT,
    UI_HIGHLIGHT, UI_ACCENT, FONT_MD, FONT_SM,
)


class Button:
    """Rectangular pixel-art button with hover/press states."""

    def __init__(self, x: int, y: int, w: int, h: int,
                 label: str, font_size: int = FONT_MD,
                 colour_idle  = UI_PANEL,
                 colour_hover = UI_PANEL2,
                 colour_text  = UI_TEXT,
                 colour_border= UI_BORDER,
                 disabled: bool = False,
                 tag=None):
        self.rect          = pygame.Rect(x, y, w, h)
        self.label         = label
        self.font_size     = font_size
        self.col_idle      = colour_idle
        self.col_hover     = colour_hover
        self.col_text      = colour_text
        self.col_border    = colour_border
        self.disabled      = disabled
        self.tag           = tag          # arbitrary payload
        self._hovered      = False
        self._pressed      = False
        self._anim_t       = 0.0          # 0-1 hover blend
        self._font: pygame.font.Font | None = None

    # ── Font lazy-loader ──────────────────────────────────────────────────
    def _get_font(self) -> pygame.font.Font:
        if self._font is None:
            self._font = pygame.font.SysFont("Alagard", self.font_size, bold = True)
        return self._font

    # ── Update / event ───────────────────────────────────────────────────
    def update(self, dt: float):
        mx, my = pygame.mouse.get_pos()
        self._hovered = self.rect.collidepoint(mx, my) and not self.disabled
        target = 1.0 if self._hovered else 0.0
        self._anim_t += (target - self._anim_t) * min(1.0, dt * 12)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True if clicked."""
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self._pressed = False
                return True
            self._pressed = False
        return False

    # ── Draw ─────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        t   = self._anim_t
        # Blend idle → hover colour
        def blend(a, b):
            return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

        fill   = blend(self.col_idle, self.col_hover)
        border = UI_HIGHLIGHT if self._hovered else self.col_border

        if self.disabled:
            fill   = (30, 30, 40)
            border = (50, 50, 60)

        # Shadow
        shadow_r = self.rect.move(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 120), shadow_r, border_radius=4)
        # Fill
        pygame.draw.rect(surface, fill, self.rect, border_radius=4)
        # Border (2-px pixel-art style)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=4)

        # Pressed indent
        text_off = 2 if self._pressed else 0

        # Label
        col_txt = (80, 80, 100) if self.disabled else self.col_text
        if self._hovered and not self.disabled:
            col_txt = UI_HIGHLIGHT
        font   = self._get_font()
        text_s = font.render(self.label, True, col_txt)
        tr     = text_s.get_rect(center=self.rect.center)
        tr.y  += text_off
        surface.blit(text_s, tr)


class IconButton(Button):
    """Button with a small icon drawn to its left."""

    def __init__(self, *args, icon: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = icon

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        if self.icon:
            font  = pygame.font.SysFont("Segoe UI Emoji,Apple Color Emoji", self.font_size)
            icon_s = font.render(self.icon, True, UI_ACCENT)
            ir     = icon_s.get_rect(
                midleft=(self.rect.left + 10, self.rect.centery))
            surface.blit(icon_s, ir)