"""
screens/shop_screen.py — Between-stage item shop.
"""
import pygame

from src.settings import (
    SCREEN_W, SCREEN_H, SHOP_ITEMS,
    UI_BG, UI_PANEL, UI_PANEL2, UI_BORDER, UI_TEXT, UI_SUBTEXT, draw_background,
    UI_HIGHLIGHT, UI_DANGER, UI_SUCCESS, UI_GOLD, UI_ACCENT,
    FONT_XS, FONT_SM, FONT_MD, FONT_LG, FONT_XL,
    STATE_STAGE_SELECT,
)
from src.entities.player import Player
from src.ui.button       import Button
from src.ui.hud          import draw_player_hud, panel, text, bar
from src.sound           import SFX


COLS, ROWS = 4, 2
CARD_W, CARD_H = (SCREEN_W - 80) // COLS, 160


class ShopScreen:
    def __init__(self, player: Player, completed_stage: int):
        self.player          = player
        self.completed_stage = completed_stage
        self._next_state: str | None = None
        self._message        = ""
        self._msg_t          = 0.0
        self._msg_col        = UI_SUCCESS
        self._t              = 0.0

        self._title_font = pygame.font.SysFont("Alagard", FONT_XL, bold=True)

        self._buy_buttons: list[Button] = []
        self._build_buy_buttons()

        self._continue_btn = Button(SCREEN_W // 2 - 130, SCREEN_H - 66,
                                    260, 50, "CONTINUE TO MAP",
                                    colour_border=UI_ACCENT)

    def _build_buy_buttons(self):
        self._buy_buttons = []
        for i, item in enumerate(SHOP_ITEMS):
            col = i % COLS
            row = i // COLS
            x   = 40 + col * (CARD_W + 6)
            y   = 160 + row * (CARD_H + 10)
            btn = Button(x + CARD_W // 2 - 60, y + CARD_H - 42,
                         120, 34,
                         f"Buy {item['cost']}g",
                         font_size=FONT_XS,
                         tag=i,
                         colour_border=UI_GOLD)
            self._buy_buttons.append(btn)

    # ── Public ────────────────────────────────────────────────────────────
    @property
    def next_state(self):
        return self._next_state

    def reset_transition(self):
        self._next_state = None

    # ── Update ────────────────────────────────────────────────────────────
    def update(self, dt: float, events: list):
        self._t     += dt
        self._msg_t  = max(0.0, self._msg_t - dt)

        for btn in self._buy_buttons:
            btn.update(dt)
        self._continue_btn.update(dt)

        for ev in events:
            for btn in self._buy_buttons:
                if btn.handle_event(ev):
                    self._on_buy(btn.tag)

            if self._continue_btn.handle_event(ev):
                SFX.play("btn_click")
                self._next_state = STATE_STAGE_SELECT

    def _on_buy(self, item_idx: int):
        item = SHOP_ITEMS[item_idx]
        if self.player.spend_coins(item["cost"]):
            SFX.play("buy")
            if item["type"] in ("heal", "full_heal"):
                msg = self.player.apply_item(item)
                self._show_msg(f"Used instantly: {msg}", UI_SUCCESS)
            else:
                self.player.items.append(item)
                msg = self.player.apply_item(item)
                self._show_msg(f"Bought {item['name']}: {msg}", UI_SUCCESS)
        else:
            SFX.play("buy_fail")
            self._show_msg("Not enough coins!", UI_DANGER)

    def _show_msg(self, msg: str, col=UI_SUCCESS):
        self._message  = msg
        self._msg_t    = 2.5
        self._msg_col  = col

    # ── Draw ──────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        draw_background(surface, "shop")
        self._draw_grid(surface)
        self._draw_title(surface)
        self._draw_player_panel(surface)
        self._draw_items(surface)
        self._draw_message(surface)
        self._continue_btn.draw(surface)

    def _draw_grid(self, surface):
        for x in range(0, SCREEN_W, 40):
            pygame.draw.line(surface, (18, 26, 42), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 40):
            pygame.draw.line(surface, (18, 26, 42), (0, y), (SCREEN_W, y))

    def _draw_title(self, surface):
        s = self._title_font.render("SHOP", True, UI_GOLD)
        surface.blit(s, (40, 20))
        sub = f"Stage {self.completed_stage + 1} complete!  Spend your hard-earned coins."
        fs = pygame.font.SysFont("Arial", FONT_SM)
        ss = fs.render(sub, True, UI_SUBTEXT)
        surface.blit(ss, (40, 20 + s.get_height() + 4))

    def _draw_player_panel(self, surface):
        r = pygame.Rect(SCREEN_W - 210, 14, 195, 120)
        draw_player_hud(surface, self.player, r)

    def _draw_items(self, surface):
        for i, item in enumerate(SHOP_ITEMS):
            col = i % COLS
            row = i // COLS
            x   = 40 + col * (CARD_W + 6)
            y   = 160 + row * (CARD_H + 10)
            r   = pygame.Rect(x, y, CARD_W, CARD_H)
            can_afford = self.player.coins >= item["cost"]

            fill_col = UI_PANEL if can_afford else (18, 20, 28)
            bord_col = UI_BORDER if can_afford else (40, 40, 60)
            panel(surface, r, fill=fill_col, border=bord_col)

            # Icon
            icon_f = pygame.font.SysFont("Segoe UI Emoji,Apple Color Emoji", 28)
            icon_s = icon_f.render(item.get("icon", "?"), True, UI_TEXT)
            surface.blit(icon_s, (x + 10, y + 10))

            # Name
            text(surface, item["name"], x + 50, y + 12, FONT_SM,
                 UI_TEXT if can_afford else UI_SUBTEXT)
            # Desc
            text(surface, item["desc"], x + 10, y + 48, FONT_XS, UI_SUBTEXT)
            # Cost badge
            cost_col = UI_GOLD if can_afford else (80, 70, 30)
            pygame.draw.rect(surface, (20, 18, 8),
                             pygame.Rect(x + CARD_W - 72, y + 8, 64, 26), border_radius=4)
            text(surface, f"{item['cost']}g", x + CARD_W - 40, y + 12,
                 FONT_XS, cost_col, anchor="midtop")

            self._buy_buttons[i].draw(surface)

    def _draw_message(self, surface):
        if self._msg_t > 0:
            alpha = int(255 * min(1.0, self._msg_t))
            mr    = pygame.Rect(SCREEN_W // 2 - 220, SCREEN_H - 120, 440, 44)
            panel(surface, mr, fill=(10, 20, 12))
            text(surface, self._message, mr.centerx, mr.centery,
                 FONT_SM, self._msg_col, anchor="center")