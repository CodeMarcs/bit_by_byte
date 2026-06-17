"""
screens/difficulty_screen.py — Difficulty selection screen shown after NEW GAME.
"""
import math
import pygame

from src.settings import (
    SCREEN_W, SCREEN_H,
    UI_BG, UI_ACCENT, UI_TEXT, UI_SUBTEXT, UI_HIGHLIGHT, UI_PANEL, UI_BORDER,
    UI_GOLD, UI_DANGER, UI_SUCCESS,
    FONT_XS, FONT_SM, FONT_MD, FONT_LG, FONT_XL, FONT_TITLE,
    DIFFICULTIES,
    STATE_STAGE_SELECT, STATE_MENU,
    draw_background,
)
from src.ui.button import Button
from src.ui.hud import text, panel
from src.sound import SFX


_DIFF_ORDER = ["easy", "normal", "hard"]

# Card dimensions
_CARD_W = 290
_CARD_H = 270
_CARD_GAP = 36
_CARDS_TOTAL_W = _CARD_W * 3 + _CARD_GAP * 2
_CARD_START_X = (SCREEN_W - _CARDS_TOTAL_W) // 2
_CARD_Y = SCREEN_H // 2 - _CARD_H // 2 - 10


class DifficultyScreen:
    def __init__(self):
        self._t = 0.0
        self._next_state: str | None = None
        self._selected: str | None = None       # key chosen by player
        self._hovered: str | None = None
        self._active: str | None = "normal"     # highlighted by click

        self._title_font = pygame.font.SysFont("Alagard", FONT_XL, bold=False)
        self._label_font = pygame.font.SysFont("Alagard", FONT_LG, bold=True)
        self._body_font  = pygame.font.SysFont("Arial",   FONT_XS, bold=False)
        self._hint_font  = pygame.font.SysFont("Alagard", FONT_XS, bold=False)

        self._back_btn = Button(20, SCREEN_H - 60, 140, 44, "BACK",
                                colour_border=(100, 80, 180))
        self._confirm_btn = Button(SCREEN_W // 2 - 110, SCREEN_H - 90,
                                   220, 48, "CONFIRM",
                                   colour_border=UI_ACCENT)

    # ── Card rects ────────────────────────────────────────────────────────
    def _card_rect(self, idx: int) -> pygame.Rect:
        x = _CARD_START_X + idx * (_CARD_W + _CARD_GAP)
        return pygame.Rect(x, _CARD_Y, _CARD_W, _CARD_H)

    # ── Public interface ──────────────────────────────────────────────────
    @property
    def next_state(self):
        return self._next_state

    @property
    def selected_difficulty(self) -> str:
        """Returns the chosen difficulty key (easy/normal/hard)."""
        return self._selected or "normal"

    def reset_transition(self):
        self._next_state = None
        self._selected = None

    # ── Update ────────────────────────────────────────────────────────────
    def update(self, dt: float, events: list):
        self._t += dt
        mx, my = pygame.mouse.get_pos()

        self._hovered = None
        for i, key in enumerate(_DIFF_ORDER):
            if self._card_rect(i).collidepoint(mx, my):
                self._hovered = key
                break

        self._back_btn.update(dt)
        self._confirm_btn.update(dt)

        for ev in events:
            if self._back_btn.handle_event(ev):
                SFX.play("btn_click")
                self._next_state = STATE_MENU

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, key in enumerate(_DIFF_ORDER):
                    if self._card_rect(i).collidepoint(ev.pos):
                        SFX.play("stage_select")
                        self._active = key
                        break

            if self._confirm_btn.handle_event(ev):
                SFX.play("btn_click")
                self._selected = self._active or "normal"
                self._next_state = STATE_STAGE_SELECT

    # ── Draw ──────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        draw_background(surface, "menu")
        self._draw_scanlines(surface)
        self._draw_title(surface)
        self._draw_cards(surface)
        self._back_btn.draw(surface)
        self._confirm_btn.draw(surface)
        self._draw_hint(surface)

    def _draw_scanlines(self, surface):
        scan = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 4):
            pygame.draw.line(scan, (0, 0, 0, 25), (0, y), (SCREEN_W, y))
        surface.blit(scan, (0, 0))

    def _draw_title(self, surface):
        s = self._title_font.render("SELECT DIFFICULTY", True, UI_ACCENT)
        surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2, 22))

    def _draw_cards(self, surface):
        for i, key in enumerate(_DIFF_ORDER):
            d = DIFFICULTIES[key]
            r = self._card_rect(i)
            selected = (key == self._active)
            hovered  = (key == self._hovered)
            color    = d["color"]

            # Card background
            bg_alpha = 200 if selected else (160 if hovered else 120)
            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((*UI_PANEL, bg_alpha))
            surface.blit(bg, r.topleft)

            # Border — pulse if selected
            border_col = color if selected else (
                tuple(min(255, c + 40) for c in color) if hovered else (50, 65, 95)
            )
            border_w = 3 if selected else 2
            if selected:
                pulse = abs(math.sin(self._t * 3)) * 2
                pygame.draw.rect(surface, color,
                                 r.inflate(int(pulse * 2), int(pulse * 2)), 3)
            pygame.draw.rect(surface, border_col, r, border_w)

            cx = r.centerx

            # Label
            lbl = self._label_font.render(d["label"], True, color)
            surface.blit(lbl, (cx - lbl.get_width() // 2, r.top + 18))

            # Separator
            pygame.draw.line(surface, (*color, 100),
                             (r.left + 20, r.top + 60),
                             (r.right - 20, r.top + 60), 1)

            # Stat modifiers
            stats = [
                ("Enemy HP",     d["hp_mult"]),
                ("Enemy ATK",    d["atk_mult"]),
                ("Enemy DEF",    d["def_mult"]),
                ("EXP gained",   d["exp_mult"]),
                ("Coins gained", d["coins_mult"]),
            ]
            for j, (stat_name, mult) in enumerate(stats):
                sy = r.top + 72 + j * 22
                # Stat name
                ns = self._body_font.render(stat_name, True, UI_SUBTEXT)
                surface.blit(ns, (r.left + 18, sy))
                # Multiplier with colour coding
                if mult < 1.0:
                    mc = (60, 200, 100)   # green — easier
                    label_str = f"×{mult:.2f} ▼"
                elif mult > 1.0:
                    mc = (220, 80, 80)    # red — harder
                    label_str = f"×{mult:.2f} ▲"
                else:
                    mc = UI_TEXT
                    label_str = f"×{mult:.2f}"
                ms = self._body_font.render(label_str, True, mc)
                surface.blit(ms, (r.right - ms.get_width() - 18, sy))

            # Description text (wrapped)
            desc_y = r.top + 192
            pygame.draw.line(surface, (*color, 80),
                             (r.left + 20, desc_y - 8),
                             (r.right - 20, desc_y - 8), 1)
            words = d["desc"].split()
            line_buf, lines = [], []
            for w in words:
                test = " ".join(line_buf + [w])
                if self._body_font.size(test)[0] > r.w - 28:
                    lines.append(" ".join(line_buf))
                    line_buf = [w]
                else:
                    line_buf.append(w)
            if line_buf:
                lines.append(" ".join(line_buf))
            for li, line in enumerate(lines):
                ls = self._body_font.render(line, True, UI_SUBTEXT)
                surface.blit(ls, (cx - ls.get_width() // 2, desc_y + li * 16))

            # "SELECTED" badge
            if selected:
                badge = self._body_font.render("SELECTED", True, color)
                surface.blit(badge, (cx - badge.get_width() // 2, r.bottom - 22))

    def _draw_hint(self, surface):
        hint = "Click a card to select | CONFIRM to start"
        hs = self._hint_font.render(hint, True, UI_SUBTEXT)
        surface.blit(hs, (SCREEN_W // 2 - hs.get_width() // 2, SCREEN_H - 24))
