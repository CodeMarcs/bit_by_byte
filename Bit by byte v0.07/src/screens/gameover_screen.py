"""
screens/gameover_screen.py — Game over and final victory screens.
"""
import math
import pygame

from src.settings import (
    SCREEN_W, SCREEN_H, UI_BG, UI_DANGER, UI_SUCCESS, draw_background,
    UI_TEXT, UI_SUBTEXT, UI_GOLD, UI_ACCENT,
    FONT_TITLE, FONT_LG, FONT_MD, FONT_SM, FONT_XS,
    STATE_MENU, STATE_STAGE_SELECT,
)
from src.ui.button  import Button
from src.ui.hud     import text, panel
from src.pixel_art  import draw_sprite


class GameOverScreen:
    def __init__(self, player, victory: bool = False):
        self.player         = player
        self.victory        = victory
        self._t             = 0.0
        self._next_state: str | None = None
        self._title_font    = pygame.font.SysFont(
            "Alagard", FONT_TITLE, bold = True)
        self._sub_font      = pygame.font.SysFont(
            "Arial", FONT_MD, bold = True)

        cx = SCREEN_W // 2
        # On defeat: show retry button above menu button; on victory: just menu
        self._retry_btn = Button(cx - 130, SCREEN_H // 2 + 100, 260, 52,
                                 "RETRY FROM STAGE 1",
                                 colour_border=(180, 60, 60))
        self._btn = Button(cx - 130, SCREEN_H // 2 + 160, 260, 52,
                           "BACK TO MENU",
                           colour_border=(100, 80, 200))

    @property
    def next_state(self):
        return self._next_state

    def reset_transition(self):
        self._next_state = None

    def update(self, dt: float, events: list):
        self._t += dt
        self._btn.update(dt)
        if not self.victory:
            self._retry_btn.update(dt)
        for ev in events:
            if self._btn.handle_event(ev):
                self._next_state = STATE_MENU
            if not self.victory and self._retry_btn.handle_event(ev):
                self._next_state = STATE_STAGE_SELECT

    def draw(self, surface: pygame.Surface):
        draw_background(surface, "game_over")
        self._draw_bg(surface)

        if self.victory:
            self._draw_victory(surface)
        else:
            self._draw_gameover(surface)

        self._draw_stats(surface)
        if not self.victory:
            self._retry_btn.draw(surface)
        self._btn.draw(surface)

    def _draw_bg(self, surface):
        col = (0, 30, 5) if self.victory else (30, 0, 0)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((*col, 180))
        surface.blit(overlay, (0, 0))
        # Scanlines
        for y in range(0, SCREEN_H, 3):
            pygame.draw.line(surface, (0, 0, 0, 40), (0, y), (SCREEN_W, y))

    def _draw_victory(self, surface):
        bob  = int(math.sin(self._t * 2.5) * 5)
        scale = 7
        px   = SCREEN_W // 2 - 10 * scale // 2
        py   = SCREEN_H // 2 - 200 + bob
        draw_sprite(surface, "player", px, py, scale)

        title = "PROGRAM DEBUGGED!"
        for dx, dy, col in [(3, 3, (0, 80, 40)), (-2, -2, (0, 200, 120))]:
            s = self._title_font.render(title, True, col)
            surface.blit(s, (SCREEN_W//2 - s.get_width()//2 + dx,
                             SCREEN_H//2 - 90 + dy))
        s = self._title_font.render(title, True, UI_GOLD)
        surface.blit(s, (SCREEN_W//2 - s.get_width()//2, SCREEN_H//2 - 90))

        sub = "You fixed all the bugs. The code runs clean."
        ss  = self._sub_font.render(sub, True, UI_SUCCESS)
        surface.blit(ss, (SCREEN_W//2 - ss.get_width()//2, SCREEN_H//2 + -30))

    def _draw_gameover(self, surface):
        title = "PRODUCTION FAILURE"
        glitch_x = int(math.sin(self._t * 3.7) * 5)
        for dx, dy, col in [(3, 3, (60, 0, 0)), (-2, -2, (180, 0, 0))]:
            s = self._title_font.render(title, True, col)
            surface.blit(s, (SCREEN_W//2 - s.get_width()//2 + dx + glitch_x,
                             SCREEN_H//2 - 100 + dy))
        s = self._title_font.render(title, True, UI_DANGER)
        surface.blit(s, (SCREEN_W//2 - s.get_width()//2, SCREEN_H//2 - 100))

        sub = "Core dumped. You have been garbage collected."
        ss  = self._sub_font.render(sub, True, (180, 80, 80))
        surface.blit(ss, (SCREEN_W//2 - ss.get_width()//2, SCREEN_H//2 - 30))

    def _draw_stats(self, surface):
        r = pygame.Rect(SCREEN_W//2 - 160, SCREEN_H//2 + 20, 320, 70)
        panel(surface, r)
        cx = r.centerx
        text(surface, f"Level: {self.player.level}   Coins: {self.player.coins}",
             cx, r.top + 17, FONT_SM, UI_TEXT, anchor="midtop")
        text(surface, f"ATK {self.player.atk}  DEF {self.player.def_}  HP {self.player.hp}/{self.player.max_hp}",
             cx, r.top + 42, FONT_XS, UI_SUBTEXT, anchor="midtop")