"""
ui/hud.py — Reusable HUD drawing helpers (bars, panels, text).
"""
import pygame
from src.settings import (
    UI_BG, UI_PANEL, UI_BORDER, UI_TEXT, UI_SUBTEXT,
    UI_HIGHLIGHT, UI_DANGER, UI_SUCCESS, UI_GOLD, UI_ACCENT,
    FONT_XS, FONT_SM, FONT_MD,
)


# ── Font cache ────────────────────────────────────────────────────────────────
_FONTS: dict[int, pygame.font.Font] = {}

def _font(size: int, bold: bool = True) -> pygame.font.Font:
    key = size * 10 + (1 if bold else 0)
    if key not in _FONTS:
        _FONTS[key] = pygame.font.SysFont("Alagard", size, bold=bold)
    return _FONTS[key]


# ── Primitives ────────────────────────────────────────────────────────────────

def text(surface, msg: str, x: int, y: int,
         size: int = FONT_SM, colour=UI_TEXT,
         bold: bool = True, anchor: str = "topleft") -> pygame.Rect:
    """Blit text and return its rect."""
    rendered = _font(size, bold).render(str(msg), True, colour)
    r = rendered.get_rect()
    setattr(r, anchor, (x, y))
    surface.blit(rendered, r)
    return r


def panel(surface, rect: pygame.Rect,
          fill=UI_PANEL, border=UI_BORDER, radius: int = 4):
    """Draw a rounded-rect panel with border."""
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


def bar(surface, x: int, y: int, w: int, h: int,
        pct: float, fill_col, bg_col=(30, 30, 50),
        border_col=UI_BORDER, label: str = ""):
    """Draw a progress bar (pct 0-1)."""
    bg_r    = pygame.Rect(x, y, w, h)
    fill_w  = int(w * max(0.0, min(1.0, pct)))
    fill_r  = pygame.Rect(x, y, fill_w, h)
    # Background
    pygame.draw.rect(surface, bg_col,    bg_r, border_radius=3)
    # Fill
    if fill_w > 0:
        pygame.draw.rect(surface, fill_col, fill_r, border_radius=3)
    # Border
    pygame.draw.rect(surface, border_col, bg_r, 1, border_radius=3)
    # Label
    if label:
        text(surface, label, x + w // 2, y + h // 2,
             size=FONT_XS, colour=UI_TEXT, anchor="center")


# ── Stat panel (drawn in battle screen) ──────────────────────────────────────

def draw_player_hud(surface, player, rect: pygame.Rect):
    """Draw the player stat panel inside rect."""
    panel(surface, rect)
    mx = rect.left + 12
    y  = rect.top  + 10

    text(surface, f"Lv {player.level}  {player.hp}/{player.max_hp} HP",
         mx, y, FONT_SM, UI_TEXT)
    y += 22
    hp_col = UI_DANGER if player.hp_progress() < 0.3 else UI_SUCCESS
    bar(surface, mx, y, rect.width - 24, 12, player.hp_progress(),
        hp_col, label=f"HP")
    y += 18
    bar(surface, mx, y, rect.width - 24, 8,  player.exp_progress(),
        UI_ACCENT, label="EXP")
    y += 16
    text(surface, f"ATK {player.atk}   DEF {player.def_}",
         mx, y, FONT_XS, UI_SUBTEXT)
    y += 18
    text(surface, f"Coins: {player.coins}", mx, y, FONT_XS, UI_GOLD)


def draw_enemy_hud(surface, enemy, rect: pygame.Rect):
    """Draw the enemy stat panel inside rect."""
    panel(surface, rect, fill=(35, 15, 15), border=UI_DANGER)
    mx = rect.left + 12
    y  = rect.top  + 10

    text(surface, enemy.name, mx, y, FONT_SM, UI_DANGER)
    y += 22
    hp_col = UI_DANGER if enemy.hp_progress() < 0.3 else (200, 80, 80)
    bar(surface, mx, y, rect.width - 24, 12, enemy.hp_progress(),
        hp_col, label=f"{enemy.hp}/{enemy.max_hp}")


# ── Battle log ────────────────────────────────────────────────────────────────

class BattleLog:
    """Scrollable log of battle messages."""

    MAX_LINES = 6

    def __init__(self, rect: pygame.Rect):
        self.rect   = rect
        self.lines: list[tuple[str, tuple]] = []  # (msg, colour)

    def add(self, msg: str, colour=UI_TEXT):
        self.lines.append((msg, colour))
        if len(self.lines) > self.MAX_LINES:
            self.lines.pop(0)

    def draw(self, surface: pygame.Surface):
        panel(surface, self.rect, fill=(10, 15, 25))
        y = self.rect.top + 8
        for msg, col in self.lines:
            text(surface, msg, self.rect.left + 12, y, FONT_XS, col)
            y += 18


# ── Floating damage numbers ───────────────────────────────────────────────────

class FloatingText:
    def __init__(self, msg: str, x: int, y: int,
                 colour=UI_DANGER, duration: float = 1.2):
        self.msg      = msg
        self.x        = float(x)
        self.y        = float(y)
        self.colour   = colour
        self.duration = duration
        self.t        = 0.0
        self.done     = False

    def update(self, dt: float):
        self.t   += dt
        self.y   -= 40 * dt
        if self.t >= self.duration:
            self.done = True

    def draw(self, surface: pygame.Surface):
        alpha = max(0, int(255 * (1 - self.t / self.duration)))
        size  = FONT_MD + int(6 * (1 - self.t / self.duration))
        rendered = _font(size).render(self.msg, True, self.colour)
        rendered.set_alpha(alpha)
        surface.blit(rendered, (int(self.x) - rendered.get_width() // 2,
                                int(self.y)))