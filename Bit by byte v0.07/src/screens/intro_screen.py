import pygame


from src.settings import (
    SCREEN_W, SCREEN_H,
    UI_BG, UI_TEXT, UI_SUBTEXT,
    FONT_SM,
    STATE_MENU,
    INTRO_VIDEO_PATH,
)


class IntroScreen:
    """Plays a video file as a skippable intro before the main menu."""

    def __init__(self):
        self._next_state: str | None = None
        self._done   = False
        self._video  = None          # pyvidplayer2.Video instance (or None)
        self._font   = pygame.font.SysFont("Arial", FONT_SM)
        self._t      = 0.0           # elapsed time (seconds)

        self._try_load_video()

        # If nothing to play, skip straight to menu
        if self._video is None:
            self._finish()

    # ── Public interface (matches every other screen) ─────────────────────

    @property
    def next_state(self):
        return self._next_state

    def reset_transition(self):
        self._next_state = None

    # ── Internal helpers ──────────────────────────────────────────────────

    def _try_load_video(self):
        """Try to import pyvidplayer2 and load the configured video."""
        if not INTRO_VIDEO_PATH:
            return
        try:
            from pyvidplayer2 import Video
            import os
            if not os.path.isfile(INTRO_VIDEO_PATH):
                print(f"[intro] Video file not found: {INTRO_VIDEO_PATH!r} — skipping intro.")
                return
            self._video = Video(INTRO_VIDEO_PATH)
            print(f"[intro] Loaded intro video: {INTRO_VIDEO_PATH!r}")
        except ImportError:
            print("[intro] pyvidplayer2 not installed — skipping intro.")
            print("        Install it with:  pip install pyvidplayer2")
        except Exception as exc:
            print(f"[intro] Could not load video: {exc} — skipping intro.")

    def _finish(self):
        """End the intro and move to the main menu."""
        if self._video is not None:
            try:
                self._video.stop()
            except Exception:
                pass
        self._done = True
        self._next_state = STATE_MENU

    # ── Update & draw ─────────────────────────────────────────────────────

    def update(self, dt: float, events: list):
        if self._done:
            return

        self._t += dt

        # Skip on any key press or mouse click
        for ev in events:
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._finish()
                return

        # Video finished on its own
        if self._video is not None and not self._video.active:
            self._finish()

    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))

        if self._video is not None and not self._done:
            # Draw the video frame centred on screen
            self._video.draw(surface, (0, 0), force_draw=True)

        # "Press any key to skip" hint — fades in after 0.5 s
        if self._t > 0.5:
            alpha = min(255, int((self._t - 0.5) * 255))
            hint  = self._font.render("Press any key to skip", True, UI_SUBTEXT)
            hint.set_alpha(alpha)
            surface.blit(hint, (SCREEN_W - hint.get_width() - 18,
                                SCREEN_H - hint.get_height() - 14))
