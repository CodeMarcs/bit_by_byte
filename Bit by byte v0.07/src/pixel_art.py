"""
pixel_art.py — Sprite definitions (16×16 char arrays) and helpers.

Each sprite is a list of 16 strings, each 16 chars wide.
Palette key (add new colours here and reference below):
  .  transparent   K  black        W  white
  R  red           G  green        B  blue
  Y  yellow        C  cyan         P  purple
  O  orange        S  dark-gray    L  light-gray
  F  flesh/skin    H  hoodie-blue  D  dark-hoodie
  M  silver        N  near-black   T  teal-dark
  Z  gold/yellow2  E  error-red2   V  violet
  Q  swamp-green   A  amber
"""

import os
import pygame

# ── Pixel palette ─────────────────────────────────────────────────────────────
PALETTE = {
    '.': None,
    'K': (  5,   5,  15),
    'W': (240, 240, 255),
    'R': (220,  50,  50),
    'G': ( 50, 200,  80),
    'B': ( 50, 100, 220),
    'Y': (255, 220,   0),
    'C': (  0, 200, 220),
    'P': (160,  60, 210),
    'O': (255, 140,   0),
    'S': ( 80,  80, 100),
    'L': (170, 180, 200),
    'F': (245, 195, 145),
    'H': ( 40,  80, 180),
    'D': ( 20,  45, 110),
    'M': (190, 200, 220),
    'N': ( 20,  20,  35),
    'T': ( 20,  80,  70),
    'Z': (255, 200,  50),
    'E': (255,  80,  80),
    'V': (180,  80, 240),
    'Q': ( 60, 140,  60),
    'A': (230, 160,  30),
}

# ── Sprite definitions ────────────────────────────────────────────────────────

SPRITES = {

# ── Player (programmer in hoodie) ─────────────────────────────────────────
"player": [
    "................",
    "....DDDDDDDD....",
    "...DHHHHHHHHD...",
    "...DHFFFFFFHD...",
    "...DHFWWFWWHD...",
    "...DHFFFFFFHD...",
    "...DHFF..FFHD...",
    "....DDDDDDDD....",
    "..HHHHHHHHHHHH..",
    ".HHHBBBBBBBHHHH.",
    ".HH.BBBBBBB.HH..",
    "..H.BBBBBBB.H...",
    "....BBBBBBB.....",
    "....BB...BB.....",
    "...NNN...NNN....",
],

# ── Syntax Error (red bug with X eyes) ───────────────────────────────────
"syntax_error": [
    "....RRRRRRRR....",
    "...R........R...",
    "..R.R......R.R..",
    "..R..R....R..R..",
    "..R...RRRR...R..",
    "..R..EEEEEE..R..",
    "..R.E.EEEE.E.R..",
    "..R..EEEEEE..R..",
    "..R..EEEEEE..R..",
    "..R..RRRRRR..R..",
    "...RR.RRRR.RR...",
    "....RRRRRRRR....",
    "....R..RR..R....",
    "....R..RR..R....",
    "...RR..RR..RR...",
    "................",
    "................",
    "................",
],

# ── Off-by-One (small glitchy digit) ────────────────────────────────────
"off_by_one": [
    "................",
    "......OOOO......",
    ".....OOOOOO.....",
    "....OO.OO.OO....",
    "....OO.OO.OO....",
    "....OO.OO.OO....",
    "....OO.OO.OO....",
    "....OOOOOOOO....",
    "....OOOOOOOO....",
    "....OO....OO....",
    "...OOOOOOOOOO...",
    "..OO........OO..",
    "..OO..OOOO..OO..",
    "..OO.OOOOOO.OO..",
    "...OOOOOOOOOO...",
    "................",
],

# ── Null Pointer (ghostly pointer) ───────────────────────────────────────
"null_pointer": [
    "....CCCCCCCC....",
    "...CCWWWWWWCC...",
    "..CCW......WCC..",
    "..CCW.CC.C.WCC..",
    "..CCW......WCC..",
    "..CCW.CCCC.WCC..",
    "..CCW......WCC..",
    "...CCWWWWWWCC...",
    "....CC....CC....",
    "...CCC....CCC...",
    "..CC..CCCC..CC..",
    "..CC..CCCC..CC..",
    "..C....CC....C..",
    "..C....CC....C..",
    "................",
    "................",
],

# ── Type Mismatch (two blocks clashing) ──────────────────────────────────
"type_mismatch": [
    "....BBBB.RRRR...",
    "...BBBBBB.RRRR..",
    "...BBBB.B.RRRR..",
    "...BBBBBB.RRRR..",
    "...BBBB.B..RR...",
    "....BBBB...RR...",
    "........RRRRRR..",
    ".......RRRRRRRR.",
    ".......RR....RR.",
    ".......RRRRRRRR.",
    "........RRRRRR..",
    ".......RR....RR.",
    "........RRRRRR..",
    "................",
    "................",
    "................",
],

# ── Memory Leak (dripping purple blob) ───────────────────────────────────
"memory_leak": [
    "....PPPPPPPP....",
    "...PPPPPPPPPP...",
    "..PPPPPPPPPPPP..",
    "..PP.P....P.PP..",
    "..PP.PPPPPP.PP..",
    "..PP.PPPPPP.PP..",
    "..PP.P....P.PP..",
    "...PPPPPPPPPP...",
    "....PPPPPPPP....",
    ".....PP..PP.....",
    ".....PP..PP.....",
    "......P..P......",
    ".....PP..PP.....",
    ".....P....P.....",
    "................",
    "................",
],

# ── Dangling Pointer (broken chain) ──────────────────────────────────────
"dangling_ptr": [
    "....MMMM........",
    "...MSSSSM.......",
    "...MSSSSM.......",
    "....MMMM........",
    "......MM........",
    "....MMMM........",
    "...MSSSSM.......",
    "...MSSSSM.......",
    "....MMMM........",
    "......MM....MMMM",
    "....MMMM...MSSM.",
    "...MSSSSM..MSSM.",
    "...MSSSSM...MMM.",
    "....MMMM........",
    "................",
    "................",
],

# ── Stack Overflow (tower tipping over) ─────────────────────────────────
"stack_overflow": [
    "....BBBBBBBB....",
    "....BSSSSSSB....",
    "....BBBBBBBB....",
    ".....BBBBBBBB...",
    ".....BSSSSSSB...",
    ".....BBBBBBBB...",
    "......BBBBBBBB..",
    "......BSSSSSSB..",
    "......BBBBBBBB..",
    ".......RRRRRRRR.",
    ".......RESSSSRR.",
    ".......RRRRRRRR.",
    "........RRRRRR..",
    "........RRRRRR..",
    "................",
    "................",
],

# ── Race Condition (two sprites overlapping) ─────────────────────────────
"race_condition": [
    "..GGGG..YYYY....",
    ".GGGGGG.YYYYYY..",
    ".GG..GG..YY..YY.",
    ".GGGGGG..YYYYYY.",
    ".GG..GG..YY..YY.",
    ".GGGGGG..YYYYYY.",
    "..GGGG....YYYY..",
    "....GG..YY......",
    "....GG..YY......",
    "....GG..YY......",
    "....GG..YY......",
    "...GGG..YYY.....",
    "................",
    "................",
    "................",
    "................",
],

# ── Segfault BOSS (skull with circuit) ───────────────────────────────────
"segfault": [
    "...EEEEEEEEEE...",
    "..EEVVVVVVVVEE..",
    ".EEVV........EE.",
    ".EEV.EE..EE.VEE.",
    ".EEV.EE..EE.VEE.",
    ".EEV........VEE.",
    ".EEV..EEEE..VEE.",
    ".EEVV.EEEE.VEE..",
    "..EEEEVVVVEEEE..",
    "...EEEE..EEEE...",
    "..EE.EE..EE.EE..",
    "..EE.EEEEEE.EE..",
    "...EE......EE...",
    "...EEEEEEEEEE...",
    "................",
    "................",
],

# ── Idle animation frame 2 for player (subtle shift) ────────────────────
"player_2": [
    "................",
    "....DDDDDDDD....",
    "...DHHHHHHHHD...",
    "...DHFFFFFFHD...",
    "...DHFWWFWWHD...",
    "...DHFFFFFFHD...",
    "...DHFF..FFHD...",
    "....DDDDDDDD....",
    "..HHHHHHHHHHHH..",
    ".HHHBBBBBBBHHHH.",
    ".HH.BBBBBBB.HH..",
    "..H.BBBBBBB.H...",
    "....BBBBBBB.....",
    "....BB...BB.....",
    "...NNN...NNN....",
    "..NNNN...NNNN...",
],

}

# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_sprite(surface: pygame.Surface, name: str, x: int, y: int,
                scale: int = 4, flip_x: bool = False) -> None:
    """Draw a named sprite at (x, y) pixel-scaled by `scale`."""
    data = SPRITES.get(name)
    if data is None:
        _draw_missing(surface, x, y, scale)
        return
    for row_i, row in enumerate(data):
        for col_i, ch in enumerate(row):
            colour = PALETTE.get(ch)
            if colour is None:
                continue
            px = x + col_i * scale if not flip_x else x + (15 - col_i) * scale
            py = y + row_i * scale
            pygame.draw.rect(surface, colour, (px, py, scale, scale))


def _draw_missing(surface, x, y, scale):
    """Magenta checkerboard for missing sprites."""
    for r in range(16):
        for c in range(16):
            col = (255, 0, 255) if (r + c) % 2 == 0 else (0, 0, 0)
            pygame.draw.rect(surface, col, (x + c * scale, y + r * scale, scale, scale))


def sprite_surface(name: str, scale: int = 4,
                   flip_x: bool = False) -> pygame.Surface:
    """Return a pygame.Surface containing the named sprite."""
    size = 16 * scale
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    draw_sprite(surf, name, 0, 0, scale, flip_x)
    return surf


# ── BMP export / import ───────────────────────────────────────────────────────

def save_sprite_bmp(name: str, folder: str, scale: int = 4) -> str:
    """Save sprite as a BMP so artists can edit it.  Returns the path."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{name}.bmp")
    if not os.path.exists(path):
        surf = sprite_surface(name, scale)
        # Replace alpha with magenta so BMP stays correct
        surf2 = pygame.Surface(surf.get_size())
        surf2.fill((255, 0, 255))
        surf2.blit(surf, (0, 0))
        pygame.image.save(surf2, path)
    return path


def load_sprite_bmp(name: str, folder: str,
                    scale: int = 4) -> pygame.Surface:
    """Load BMP from folder if it exists; fall back to generated sprite."""
    path = os.path.join(folder, f"{name}.bmp")
    if os.path.exists(path):
        img = pygame.image.load(path).convert()
        img.set_colorkey((255, 0, 255))   # magenta = transparent
        return img
    return sprite_surface(name, scale)


def export_all_sprites(folder: str, scale: int = 4) -> None:
    """Export every sprite in SPRITES to BMP files (run once to seed assets)."""
    pygame.display.set_mode((1, 1), pygame.NOFRAME)   # headless surface
    for name in SPRITES:
        save_sprite_bmp(name, folder, scale)


# ── Background drawing ────────────────────────────────────────────────────────

def draw_battle_bg(surface: pygame.Surface, stage: int) -> None:
    """Draw the battle background.

    If a battle background image is configured in settings (via BG_IMAGES["battle"]
    or BG_IMAGE_PATH), it will be used. Otherwise falls back to the procedural
    pixel-art gradient tied to the stage colour.
    """
    import src.settings as S

    # Use image background if configured
    path = S.BG_IMAGES.get("battle") or S.BG_IMAGE_PATH
    if path:
        img = S._load_bg(path)
        if img is not None:
            surface.blit(img, (0, 0))
            if S.BG_OVERLAY_ALPHA > 0:
                overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, S.BG_OVERLAY_ALPHA))
                surface.blit(overlay, (0, 0))
            return

    # Fallback: procedural pixel-art gradient
    w, h = surface.get_size()
    base_col  = S.STAGE_COLORS[stage % len(S.STAGE_COLORS)]
    dark_col  = tuple(max(0, c - 30) for c in base_col)
    light_col = tuple(min(255, c + 20) for c in base_col)

    # Sky gradient (top half)
    for y in range(h // 2):
        t = y / (h / 2)
        r = int(base_col[0] * (1 - t) + dark_col[0] * t)
        g = int(base_col[1] * (1 - t) + dark_col[1] * t)
        b = int(base_col[2] * (1 - t) + dark_col[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

    # Ground (bottom half)
    pygame.draw.rect(surface, dark_col, (0, h // 2, w, h // 2))

    # Scanline grid overlay
    for x in range(0, w, 32):
        pygame.draw.line(surface, light_col, (x, 0), (x, h), 1)
    for y in range(0, h, 32):
        pygame.draw.line(surface, light_col, (0, y), (w, y), 1)