import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame


def export_sprites():
    """One-time export of all sprites to assets/images/sprites/*.bmp"""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    from src.pixel_art import SPRITES, sprite_surface, PIXEL_SCALE
    folder = os.path.join(os.path.dirname(__file__), "assets", "images", "sprites")
    os.makedirs(folder, exist_ok=True)
    scale = 4
    for name in SPRITES:
        path = os.path.join(folder, f"{name}.bmp")
        surf = sprite_surface(name, scale)
        # BMP doesn't support alpha; convert transparent to magenta
        out  = pygame.Surface(surf.get_size())
        out.fill((255, 0, 255))
        out.blit(surf, (0, 0))
        pygame.image.save(out, path)
        print(f"  Saved {path}")
    print("All sprites exported! Edit them, then re-run the game.")
    pygame.quit()
    sys.exit(0)


def main():
    if "--export-sprites" in sys.argv:
        export_sprites()

    from src.sound import init_mixer, SFX

    init_mixer()        # 1. lock mixer format via pre_init
    pygame.init()       # 2. finish pygame startup
    pygame.font.init()
    SFX.load()          # 3. decode all WAVs NOW — after mixer format is finalised

    from src.game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()