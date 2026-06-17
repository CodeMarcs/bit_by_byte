# Debug Quest RPG

A pixel-art, turn-based RPG where you play a programmer fighting software bugs.

---

## Project Structure

```
bit_by_byte_console_rpg/
├── run.py                          ← Entry point
├── requirements.txt
├── README.md
│
├── assets/
│   ├── fonts/                      ← Drop .ttf fonts here (optional)
│   └── images/
│       ├── sprites/                ← BMP sprite files (auto-generated, editable!)
│       ├── backgrounds/            ← Custom background BMPs (optional)
│       └── ui/                     ← UI element BMPs (optional)
│
└── src/
    ├── settings.py                 ← ALL constants: colours, stats, stages, items
    ├── pixel_art.py                ← Sprite definitions + BMP export/import
    ├── game.py                     ← State machine & main loop
    │
    ├── ui/
    │   ├── button.py               ← Button component (supports BMP faces)
    │   └── hud.py                  ← Health bars, EXP bars, battle log, floats
    │
    ├── entities/
    │   ├── player.py               ← Player stats, levelling, inventory
    │   └── enemy.py                ← Enemy stats + AI
    │
    └── screens/
        ├── menu_screen.py          ← Animated start menu
        ├── stage_screen.py         ← Stage-select map with node progression
        ├── battle_screen.py        ← Turn-based combat
        ├── shop_screen.py          ← Between-stage item shop
        └── gameover_screen.py      ← Win / lose screens
```

---

## Setup

```bash
pip install pygame
python run.py
```

---

## Editing Sprites (BMP workflow)

Export all sprites to `assets/images/sprites/` as editable BMP files:

```bash
python run.py --export-sprites
```

Each BMP is `64×64` pixels (16×16 sprite at 4× scale).
Magenta `(255, 0, 255)` = transparent.

Edit in any pixel-art editor (Aseprite, LibreSprite, GIMP, MS Paint).
The game automatically loads your edited BMPs on next launch.

### Adding a new sprite

1. Add a new entry to `SPRITES` dict in `src/pixel_art.py`
2. Reference it in an enemy/player definition in `src/settings.py`
3. Run `--export-sprites` to generate the BMP template

---

## Controls

- **Mouse** — all interactions
- Hover nodes on the map to see stage info
- In battle: Attack / Special / Item / Run

---

## Customisation

| File | What to change |
|---|---|
| `src/settings.py` | Enemy stats, shop items, player base stats, stage names/colours |
| `src/pixel_art.py` | PALETTE colours, SPRITES pixel arrays |
| `src/entities/enemy.py` | Enemy AI behaviour |
| `src/entities/player.py` | Special ability effects |
| `src/ui/button.py` | Button appearance |

---

## Enemy Roster

| Stage | Enemies |
|---|---|
| 1 — Runtime Realm | Syntax Error, Off-by-One |
| 2 — Stack Swamp | Null Pointer, Type Mismatch |
| 3 — Heap Hollow | Memory Leak, Dangling Ptr |
| 4 — Memory Maze | Stack Overflow, Race Condition |
| 5 — Kernel Keep | **Segfault** (Boss) |

---

## Player Specials (cost HP as "MP")

| Name | Effect | Cost |
|---|---|---|
| Breakpoint | 2× damage + stun enemy | 20 HP |
| Hot Fix | Heal 35% max HP | 15 HP |
| Deploy | 3× damage | 30 HP |


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Background Image Configuration ─────────────────────────────────────────
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# HOW TO USE:
#   Set BG_IMAGE_PATH to the path of your image file (PNG, JPG, etc.).
#   The image will be scaled to fill the screen automatically.
#   Leave BG_IMAGE_PATH as None to use the solid colour fallback instead.
#
# Per-screen overrides:
#   Set a screen key to a file path string to use a different image for that
#   screen, or to None to use the solid colour fallback for just that screen.
#   Omit a key (or leave it as None) to inherit the global BG_IMAGE_PATH.
#
# Examples:
#   BG_IMAGE_PATH = "assets/images/bg_global.png"
#   BG_IMAGES = {
#       "menu":         "assets/images/bg_menu.png",
#       "stage_select": "assets/images/bg_map.png",
#       "battle":       "assets/images/bg_battle.png",
#       "shop":         "assets/images/bg_shop.png",
#       "game_over":    "assets/images/bg_gameover.png",
#   }
#


# screens/intro_screen.py — Video intro screen using pyvidplayer2.

# HOW TO USE INTRO SCREEN FUNCTION FOR NOOBS
──────────
1. Install the dependency (once):
       pip install pyvidplayer2

2. Drop your video file anywhere in the project, e.g.:
       assets/videos/intro.mp4   (MP4, AVI, MKV, GIF all work)

3. Set the path in settings.py:
       INTRO_VIDEO_PATH = "assets/videos/intro.mp4"

4. Done — the intro plays automatically on launch and the player
   can skip it at any time by pressing ANY key or clicking.

# If pyvidplayer2 is not installed, or the file is missing, the intro
# is silently skipped and the game goes straight to the menu.
