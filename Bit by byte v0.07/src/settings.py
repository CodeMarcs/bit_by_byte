import os
import pygame

"""
settings.py — All global constants, colours, and configuration.
Edit PIXEL_SCALE to change the display size of sprites.
"""

# ── Window ─────────────────────────────────────────────────────────────────
SCREEN_W   = 1200
SCREEN_H   = 700
FPS        = 60
TITLE      = "Bit By Byte: A Debugging Adventure"
PIXEL_SCALE = 4          # sprite pixels per screen pixel (16 px sprite → 64 px)

# ── Colour palette ──────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (220,  50,  50)
GREEN      = ( 50, 200,  80)
BLUE       = ( 50, 100, 220)
YELLOW     = (255, 220,   0)
PURPLE     = (150,  50, 200)
CYAN       = (  0, 200, 220)
ORANGE     = (255, 140,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = ( 40,  40,  40)
LIGHT_GRAY = (180, 180, 180)

# UI theme
UI_BG        = (0,   0,   0)
UI_PANEL     = (22,  32,  52)
UI_PANEL2    = (255,  255,  255)
UI_BORDER    = (255, 255, 255)
UI_ACCENT    = (255, 255, 255)
UI_TEXT      = (200, 220, 255)
UI_SUBTEXT   = (120, 150, 200)
UI_HIGHLIGHT = (180, 180,  180)
UI_DANGER    = (220,  60,  60)
UI_SUCCESS   = (60, 200, 100)
UI_GOLD      = (255, 200,  50)

# ── Font sizes ──────────────────────────────────────────────────────────────
FONT_XS    = 12
FONT_SM    = 16
FONT_MD    = 22
FONT_LG    = 30
FONT_XL    = 42
FONT_TITLE = 64

# ── Game states ─────────────────────────────────────────────────────────────
STATE_MENU             = "menu"
STATE_STAGE_SELECT     = "stage_select"
STATE_DIFFICULTY_SELECT = "difficulty_select"
STATE_BATTLE           = "battle"
STATE_SHOP             = "shop"
STATE_GAME_OVER        = "game_over"
STATE_VICTORY          = "victory"
STATE_INTRO            = "intro"

# ── Difficulty settings ──────────────────────────────────────────────────────
# Each entry: (label, description, hp_mult, atk_mult, def_mult, exp_mult, coins_mult, color)
DIFFICULTIES = {
    "easy": {
        "label":      "EASY",
        "desc":       "Chill mode — enemies are weaker, rewards are normal",
        "hp_mult":    0.65,
        "atk_mult":   0.65,
        "def_mult":   0.65,
        "exp_mult":   1.0,
        "coins_mult": 1.0,
        "color":      (60, 200, 100),   # green
    },
    "normal": {
        "label":      "NORMAL",
        "desc":       "Balanced challenge — the intended experience",
        "hp_mult":    1.0,
        "atk_mult":   1.0,
        "def_mult":   1.0,
        "exp_mult":   1.0,
        "coins_mult": 1.0,
        "color":      (180, 180, 255),  # blue-white
    },
    "hard": {
        "label":      "HARD",
        "desc":       "Punishing — enemies are much stronger, extra coins to compensate",
        "hp_mult":    1.6,
        "atk_mult":   1.5,
        "def_mult":   1.4,
        "exp_mult":   1.2,
        "coins_mult": 1.5,
        "color":      (220, 60, 60),    # red
    },
}

# ── Player base stats ───────────────────────────────────────────────────────
PLAYER_BASE_HP    = 120
PLAYER_BASE_ATK   = 10
PLAYER_BASE_DEF   = 6
PLAYER_BASE_SPEED = 10
EXP_PER_LEVEL     = 100   # EXP needed per level (multiplied by current level)

# ── Stages ──────────────────────────────────────────────────────────────────
TOTAL_STAGES = 5

STAGE_NAMES = [
    "The Creation Myth",
    "The Debugging Depths",
    "Pre-production Pits",
    "Testing Tundra",
    "Doom Launch",
]

STAGE_COLORS = [
    (  10,  10,  10),
    (  50,  40,  80),
    (  80,  50,  30),
    (  30,  60,  80),
    (  80,  30,  30),
]

# ── Enemy definitions per stage ─────────────────────────────────────────────
STAGE_ENEMIES = [
    # Stage 1
    [
        {"name": "Syntax Error",   "hp": 50,  "atk": 10, "def_": 2,  "exp": 30,  "coins": 15, "sprite": "syntax_error"},
        {"name": "Off-by-One",     "hp": 60,  "atk": 12,  "def_": 3,  "exp": 40,  "coins": 20, "sprite": "off_by_one"},
    ],
    # Stage 2
    [
        {"name": "Null Pointer",   "hp": 80,  "atk": 16,  "def_": 4,  "exp": 60,  "coins": 30, "sprite": "null_pointer"},
        {"name": "Type Mismatch",  "hp": 90,  "atk": 18,  "def_": 5,  "exp": 70,  "coins": 35, "sprite": "type_mismatch"},
    ],
    # Stage 3
    [
        {"name": "Memory Leak",    "hp": 120, "atk": 22,  "def_": 7,  "exp": 100, "coins": 50, "sprite": "memory_leak"},
        {"name": "Dangling Ptr",   "hp": 110, "atk": 24,  "def_": 6,  "exp": 90,  "coins": 45, "sprite": "dangling_ptr"},
    ],
    # Stage 4
    [
        {"name": "Stack Overflow", "hp": 150, "atk": 28,  "def_": 9,  "exp": 140, "coins": 70, "sprite": "stack_overflow"},
        {"name": "Race Condition", "hp": 140, "atk": 30,  "def_": 8,  "exp": 130, "coins": 65, "sprite": "race_condition"},
    ],
    # Stage 5 — BOSS
    [
        {"name": "Segfault",       "hp": 220, "atk": 38,  "def_": 14, "exp": 250, "coins": 150, "sprite": "segfault"},
    ],
]

# ── Shop items ───────────────────────────────────────────────────────────────
SHOP_ITEMS = [
    {"name": "Energy Drink",  "cost": 30,  "desc": "Restore 40 HP",         "type": "heal",      "value": 40,  "icon": "🥤"},
    {"name": "Rubber Duck",   "cost": 50,  "desc": "+6 ATK forever",        "type": "atk",       "value": 6,   "icon": "🦆"},
    {"name": "Stack Trace",   "cost": 45,  "desc": "+4 DEF forever",        "type": "def",       "value": 4,   "icon": "📋"},
    {"name": "IDE Dark Mode", "cost": 70,  "desc": "Fully restore HP",      "type": "full_heal", "value": 0,   "icon": "💻"},
    {"name": "Git Commit",    "cost": 90,  "desc": "+12 ATK forever",       "type": "atk",       "value": 12,  "icon": "📦"},
    {"name": "Firewall",      "cost": 80,  "desc": "+8 DEF forever",        "type": "def",       "value": 8,   "icon": "🛡"},
    {"name": "Hot Patch",     "cost": 60,  "desc": "Restore 80 HP",         "type": "heal",      "value": 80,  "icon": "🩹"},
    {"name": "Code Review",   "cost": 110, "desc": "+15 ATK, +5 DEF",       "type": "both",      "value": 0,   "icon": "🔍"},
]

# ── Player special abilities ──────────────────────────────────────────────────
SPECIALS = [
    {"name": "Breakpoint",  "desc": "Heavy hit, skip enemy next turn",  "cost": 20, "dmg_mult": 2.0},
    {"name": "Update",     "desc": "Heal 35% of max HP",               "cost": 15, "heal_pct": 0.35},
    {"name": "Deploy",      "desc": "Massive damage (high cost)",       "cost": 30, "dmg_mult": 3.0},
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Intro Video Configuration ───────────────────────────────────────────────
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Set INTRO_VIDEO_PATH to your video file (MP4, AVI, MKV, GIF).
# Leave as None to skip the intro entirely.
#
# Example:
#   INTRO_VIDEO_PATH = "assets/videos/intro.mp4"
#
INTRO_VIDEO_PATH: str | None = None   # ← set your video path here

# ── Global fallback image (used when no per-screen override is set) ──────────
BG_IMAGE_PATH: str | None = None    # e.g. "assets/images/background.png"

# ── Per-screen image overrides ───────────────────────────────────────────────
BG_IMAGES: dict[str, str | None] = {
    "menu":         "assets/images/bg_menu.gif",   # e.g. "assets/images/bg_menu.png"
    "stage_select": "assets/images/bg_select_stage.png",
    "battle":       "assets/images/bg_battle.png",
    "shop":         "assets/images/bg_shop.png",
    "game_over":    "assets/images/bg_gameover.png",
}

# ── Overlay opacity (0 = no overlay, 255 = fully opaque) ────────────────────
# A dark overlay is drawn on top of the image to keep UI elements readable.
BG_OVERLAY_ALPHA: int = 120   # 0–255

# ── Solid colour fallback (used when no image is configured) ─────────────────
BG_FALLBACK_COLOR = UI_BG      # change to any (R, G, B) tuple

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Background drawing helper ───────────────────────────────────────────────
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Internal cache — avoids reloading the image from disk every frame
_bg_cache: dict[str, pygame.Surface] = {}


def _load_bg(path: str) -> pygame.Surface | None:
    """Load and scale a background image, with caching. Returns None on error."""
    if path in _bg_cache:
        return _bg_cache[path]
    if not os.path.isfile(path):
        print(f"[settings] WARNING: background image not found: {path!r}")
        _bg_cache[path] = None
        return None
    try:
        img = pygame.image.load(path).convert()
        img = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        _bg_cache[path] = img
        print(f"[settings] Loaded background image: {path!r}")
        return img
    except Exception as exc:
        print(f"[settings] WARNING: could not load background image {path!r}: {exc}")
        _bg_cache[path] = None
        return None


def draw_background(surface: pygame.Surface, screen_key: str = "") -> None:
    """
    Draw the background for any screen.

    Call this at the top of every screen's draw() method instead of
    ``surface.fill(UI_BG)``.

    Parameters
    ----------
    surface    : The pygame surface to draw onto.
    screen_key : One of "menu", "stage_select", "battle", "shop", "game_over".
                 Leave empty to use only the global fallback.
    """
    # Resolve which path to use: per-screen override → global → None
    path: str | None = BG_IMAGES.get(screen_key, None) or BG_IMAGE_PATH

    if path:
        img = _load_bg(path)
        if img is not None:
            surface.blit(img, (0, 0))
            # Dark overlay to keep UI readable
            if BG_OVERLAY_ALPHA > 0:
                overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, BG_OVERLAY_ALPHA))
                surface.blit(overlay, (0, 0))
            return

    # Fallback: solid colour fill
    surface.fill(BG_FALLBACK_COLOR)
