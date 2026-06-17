"""
screens/menu_screen.py — Animated start menu.
"""
import math
import random

import pygame

from src.settings import (
    SCREEN_W, SCREEN_H, UI_ACCENT, UI_SUBTEXT,
    draw_background,
    FONT_TITLE, FONT_MD, FONT_XS,
    STATE_STAGE_SELECT, STATE_DIFFICULTY_SELECT,
)
from src.ui.button import Button
from src.sound import SFX


class MenuScreen:
    BTN_W, BTN_H = 260, 54

    def __init__(self, player, save_exists: bool = False):
        self.player = player
        self.save_exists = save_exists
        self._t = 0.0
        self._stars = self._gen_stars(80)
        self._next_state: str | None = None

        self._title_font = pygame.font.SysFont("Alagard", FONT_TITLE, bold=False)
        self._sub_font = pygame.font.SysFont("Alagard", FONT_MD, bold=False)
        self._hint_font = pygame.font.SysFont("Alagard", FONT_XS, bold=False)

        cx = SCREEN_W // 2
        btn_y = SCREEN_H // 2 + 30
        gap = 64
        self.buttons = [
            Button(cx - self.BTN_W // 2, btn_y,
                   self.BTN_W, self.BTN_H, "NEW GAME"),
            Button(cx - self.BTN_W // 2, btn_y + gap,
                   self.BTN_W, self.BTN_H, "QUIT",
                   colour_border=(255, 255, 255)),
        ]

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _gen_stars(n: int):
        return [
            (random.randint(0, SCREEN_W), random.randint(0, SCREEN_H), random.uniform(0.3, 1.0))
            for _ in range(n)
        ]

    # ── Public interface ──────────────────────────────────────────────────

    @property
    def next_state(self):
        return self._next_state

    def reset_transition(self):
        self._next_state = None

    # ── Update ────────────────────────────────────────────────────────────

    def update(self, dt: float, events: list):
        self._t += dt

        for btn in self.buttons:
            btn.update(dt)

        for ev in events:
            if self.buttons[0].handle_event(ev):
                SFX.play("btn_click")
                self._next_state = STATE_DIFFICULTY_SELECT
            if self.buttons[1].handle_event(ev):
                SFX.play("btn_click")
                self._next_state = "quit"

    # ── Draw ──────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        draw_background(surface, "menu")
        self._draw_stars(surface)
        self._draw_scanlines(surface)
        self._draw_title(surface)
        for btn in self.buttons:
            btn.draw(surface)
        self._draw_hint(surface)

    def _draw_stars(self, surface):
        for sx, sy, br in self._stars:
            alpha = int(180 * abs(math.sin(self._t * br + sx)))
            col = (alpha, alpha, min(255, alpha + 40))
            pygame.draw.rect(surface, col, (sx, sy, 2, 2))

    def _draw_scanlines(self, surface):
        scan = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 4):
            pygame.draw.line(scan, (0, 0, 0, 30), (0, y), (SCREEN_W, y))
        surface.blit(scan, (0, 0))

    def _draw_title(self, surface):
        g = int(math.sin(self._t * 2.1) * 3)
        title = "Bit by Byte"
        cx = SCREEN_W // 2
        ty = SCREEN_H // 4

        # Shadow / glow layers
        for dx, dy, col in [
            (4, 4, (0, 0, 0)),
            (-2, -2, (180, 180, 180)),
            (g, 0, (0, 0, 0, 120)),
        ]:
            s = self._title_font.render(title, True, col)
            surface.blit(s, (cx - s.get_width() // 2 + dx, ty - s.get_height() // 2 + dy))

        # Main title
        main_s = self._title_font.render(title, True, UI_ACCENT)
        surface.blit(main_s, (cx - main_s.get_width() // 2, ty - main_s.get_height() // 2))

        # Subtitle
        sub = "A debugging adventure"
        ss = self._sub_font.render(sub, True, UI_SUBTEXT)
        surface.blit(ss, (cx - ss.get_width() // 2, ty + main_s.get_height() // 2 + 4))

    def _draw_hint(self, surface):
        hint = "Use mouse, keyboard to navigate |  v0.6"
        hs = self._hint_font.render(hint, True, UI_SUBTEXT)
        surface.blit(hs, (SCREEN_W // 2 - hs.get_width() // 2, SCREEN_H - 26))