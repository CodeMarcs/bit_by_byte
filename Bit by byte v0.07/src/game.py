"""
game.py — Top-level game loop and state machine.
"""
import pygame
import sys

from src.settings import (
    SCREEN_W, SCREEN_H, FPS, TITLE, TOTAL_STAGES,
    STATE_MENU, STATE_STAGE_SELECT, STATE_DIFFICULTY_SELECT,
    STATE_BATTLE, STATE_SHOP, STATE_GAME_OVER, STATE_VICTORY, STATE_INTRO,
)
from src.entities.player          import Player
from src.screens.menu_screen      import MenuScreen
from src.screens.stage_screen     import StageScreen
from src.screens.difficulty_screen import DifficultyScreen
from src.screens.battle_screen    import BattleScreen
from src.screens.shop_screen      import ShopScreen
from src.screens.gameover_screen  import GameOverScreen
from src.screens.intro_screen     import IntroScreen
from src.sound import SFX, BGM



class Game:
    def __init__(self):
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()

        self.player           = Player()
        self.completed_stages : set[int] = set()
        self.current_stage    = 0   # 0-indexed next playable stage
        self.last_stage_played: int | None = None
        self.difficulty       = "normal"   # easy / normal / hard

        self._state : str    = STATE_INTRO
        self._screen = None   # current screen object
        self._transition_to(STATE_INTRO)

    # ── State machine ─────────────────────────────────────────────────────
    def _transition_to(self, state: str, **kwargs):
        self._state  = state
        
        if state == STATE_INTRO:
            BGM.play("intro")
            self._screen = IntroScreen()

        if state == STATE_MENU:
            BGM.play("menu")
            self._screen = MenuScreen(self.player)

        elif state == STATE_DIFFICULTY_SELECT:
            BGM.play("menu")
            self._screen = DifficultyScreen()

        elif state == STATE_STAGE_SELECT:
            BGM.play("stage_select")
            self._screen = StageScreen(
                self.player,
                self.current_stage,
                self.completed_stages,
                self.difficulty,
            )

        elif state == STATE_BATTLE:
            stage = kwargs.get("stage", self.current_stage)
            self.last_stage_played = stage
            self.player.stunned = False
            from src.settings import TOTAL_STAGES
            BGM.play("boss" if stage == TOTAL_STAGES - 1 else "battle")
            self._screen = BattleScreen(self.player, stage, self.difficulty)

        elif state == STATE_SHOP:
            BGM.play("shop")
            self._screen = ShopScreen(self.player, self.last_stage_played)

        elif state == STATE_GAME_OVER:
            BGM.play("game_over")
            self._screen = GameOverScreen(self.player, victory=False)

        elif state == STATE_VICTORY:
            BGM.play("victory")
            self._screen = GameOverScreen(self.player, victory=True)

    def _handle_transition(self):
        """Check if the current screen wants to move to a new state."""
        ns = self._screen.next_state
        if ns is None:
            return

        # Read any data from the outgoing screen BEFORE reset_transition clears it
        if ns == STATE_STAGE_SELECT and self._state == STATE_DIFFICULTY_SELECT:
            self.difficulty = getattr(self._screen, "selected_difficulty", "normal")

        self._screen.reset_transition()

        if ns == "quit":
            pygame.quit(); sys.exit()
            
        elif ns == STATE_INTRO:
            self._transition_to(STATE_INTRO)

        elif ns == STATE_MENU:
            # Full reset
            self.player           = Player()
            self.completed_stages = set()
            self.current_stage    = 0
            self._transition_to(STATE_MENU)

        elif ns == STATE_DIFFICULTY_SELECT:
            # Coming from menu — reset everything then pick difficulty
            self.player           = Player()
            self.completed_stages = set()
            self.current_stage    = 0
            self._transition_to(STATE_DIFFICULTY_SELECT)

        elif ns == STATE_STAGE_SELECT:
            if self._state == STATE_GAME_OVER:
                # Coming from game over (defeat) — reset stage progress
                self.completed_stages = set()
                self.current_stage    = 0
                self.player           = Player()
            else:
                # After shop → advance stage counter if stage was completed
                if (self.last_stage_played is not None
                        and self.last_stage_played not in self.completed_stages):
                    self.completed_stages.add(self.last_stage_played)
                    self.current_stage = self.last_stage_played + 1

                # All stages done → victory
                if self.current_stage >= TOTAL_STAGES and len(self.completed_stages) == TOTAL_STAGES:
                    self._transition_to(STATE_VICTORY)
                    return

            self._transition_to(STATE_STAGE_SELECT)

        elif ns == STATE_BATTLE:
            # Stage screen tells us which stage was selected.
            # NOTE: use 'is not None' — stage index 0 is falsy, so 'or' would
            # incorrectly fall back to current_stage (which can be out-of-bounds).
            selected = getattr(self._screen, "selected_stage", None)
            stage = selected if selected is not None else self.current_stage
            # Clamp to valid range just in case
            stage = max(0, min(stage, TOTAL_STAGES - 1))
            self._transition_to(STATE_BATTLE, stage=stage)

        elif ns == STATE_SHOP:
            self._transition_to(STATE_SHOP)

        elif ns == STATE_GAME_OVER:
            self._transition_to(STATE_GAME_OVER)

        elif ns == STATE_VICTORY:
            self._transition_to(STATE_VICTORY)

    # ── Main loop ─────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt     = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for ev in events:
                if ev.type == pygame.QUIT:
                    running = False

            self._screen.update(dt, events)
            self._screen.draw(self.screen)
            pygame.display.flip()
            self._handle_transition()

        pygame.quit()
        sys.exit()