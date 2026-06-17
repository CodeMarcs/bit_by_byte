"""
screens/stage_screen.py — Stage-select map with node progression.
"""
import math
import pygame

from src.settings import (
    SCREEN_W, SCREEN_H, UI_BG, UI_ACCENT, UI_TEXT, draw_background,
    UI_HIGHLIGHT, UI_SUBTEXT, UI_BORDER, UI_DANGER, UI_GOLD,
    UI_PANEL, FONT_MD, FONT_SM, FONT_LG, FONT_XL, FONT_XS,
    TOTAL_STAGES, STAGE_NAMES, STAGE_COLORS,
    DIFFICULTIES,
    STATE_BATTLE, STATE_MENU,
)
from src.ui.button import Button
from src.ui.hud import draw_player_hud, text, panel
from src.sound  import SFX


# Node positions (x%, y%) relative to screen
_NODE_POSITIONS = [
    (0.15, 0.70),
    (0.32, 0.45),
    (0.50, 0.65),
    (0.68, 0.38),
    (0.85, 0.55),
]


class StageScreen:
    def __init__(self, player, current_stage: int, completed_stages: set, difficulty: str = "normal"):
        self.player           = player
        self.current_stage    = current_stage    # 0-indexed, stage to play next
        self.completed_stages = completed_stages  # set of completed 0-indices
        self.difficulty       = difficulty
        self._t               = 0.0
        self._next_state: str | None = None
        self._selected_stage: int | None = None
        self._hovered_node: int | None   = None   # visual highlight only
        self._active_node: int | None    = None   # persists after click; drives the Enter button
        self._title_font  = pygame.font.SysFont("Alagard",
                                                 FONT_XL, bold = False)
        self._label_font  = pygame.font.SysFont("Alagard",
                                                 FONT_SM, bold = True)
        self._small_font  = pygame.font.SysFont("Arial",
                                                 FONT_XS, bold = True)
        self._buttons: list[Button] = []
        self._build_bottom_bar()

    # ── Helpers ───────────────────────────────────────────────────────────
    def _build_bottom_bar(self):
        self._buttons = [
            Button(20, SCREEN_H - 60, 140, 44, "MENU",
                   colour_border=(100, 80, 180)),
        ]
        # "Enter stage" button — only shown when a playable node is selected
        self._enter_btn = Button(SCREEN_W // 2 - 110, SCREEN_H - 64,
                                 220, 48, "ENTER STAGE",
                                 colour_border=UI_ACCENT)

    def _node_rect(self, idx: int) -> pygame.Rect:
        xp, yp = _NODE_POSITIONS[idx]
        cx = int(xp * SCREEN_W)
        cy = int(yp * SCREEN_H)
        r  = 32
        return pygame.Rect(cx - r, cy - r, r * 2, r * 2)

    def _node_state(self, idx: int) -> str:
        if idx in self.completed_stages:
            return "done"
        if idx == self.current_stage:
            return "current"
        return "locked"

    # ── Public ────────────────────────────────────────────────────────────
    @property
    def next_state(self):
        return self._next_state

    @property
    def selected_stage(self):
        return self._selected_stage

    def reset_transition(self):
        self._next_state     = None
        self._selected_stage = None

    # ── Update ────────────────────────────────────────────────────────────
    def update(self, dt: float, events: list):
        self._t += dt
        mx, my  = pygame.mouse.get_pos()

        # Hover is purely visual — recalculated every frame
        self._hovered_node = None
        for i in range(TOTAL_STAGES):
            nr = self._node_rect(i)
            if nr.collidepoint(mx, my) and self._node_state(i) != "locked":
                self._hovered_node = i
                break

        for btn in self._buttons:
            btn.update(dt)
        self._enter_btn.update(dt)

        for ev in events:
            for btn in self._buttons:
                if btn.handle_event(ev):
                    SFX.play("btn_click")
                    self._next_state = STATE_MENU

            # Clicking a node persists the selection so the Enter button stays visible
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i in range(TOTAL_STAGES):
                    nr = self._node_rect(i)
                    if nr.collidepoint(ev.pos) and self._node_state(i) != "locked":
                        SFX.play("stage_select")
                        self._active_node = i
                        break

            # Enter button driven by _active_node (not _hovered_node)
            if self._enter_btn.handle_event(ev) and self._active_node is not None:
                SFX.play("btn_click")
                self._selected_stage = self._active_node
                self._next_state     = STATE_BATTLE

    # ── Draw ──────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        draw_background(surface, "stage_select")
        self._draw_grid(surface)
        self._draw_paths(surface)
        self._draw_nodes(surface)
        self._draw_title(surface)
        self._draw_player_panel(surface)
        for btn in self._buttons:
            btn.draw(surface)
        if self._active_node is not None:
            self._enter_btn.draw(surface)
        self._draw_stage_info(surface)

    def _draw_grid(self, surface):
        for x in range(0, SCREEN_W, 40):
            pygame.draw.line(surface, (20, 28, 45), (x, 0), (x, SCREEN_H))
        for y in range(0, SCREEN_H, 40):
            pygame.draw.line(surface, (20, 28, 45), (0, y), (SCREEN_W, y))

    def _draw_paths(self, surface):
        for i in range(TOTAL_STAGES - 1):
            x1p, y1p = _NODE_POSITIONS[i]
            x2p, y2p = _NODE_POSITIONS[i + 1]
            cx1 = int(x1p * SCREEN_W); cy1 = int(y1p * SCREEN_H)
            cx2 = int(x2p * SCREEN_W); cy2 = int(y2p * SCREEN_H)
            done = i in self.completed_stages
            col  = UI_ACCENT if done else (40, 55, 80)
            pygame.draw.line(surface, col, (cx1, cy1), (cx2, cy2), 3)

    def _draw_nodes(self, surface):
        bob = int(math.sin(self._t * 2.5) * 4)
        for i in range(TOTAL_STAGES):
            nr    = self._node_rect(i)
            state = self._node_state(i)
            xp, yp = _NODE_POSITIONS[i]
            cx = int(xp * SCREEN_W)
            cy = int(yp * SCREEN_H)

            if state == "current":
                cy += bob   # bob animation on current node

            if state == "done":
                fill = (30, 100, 60); border = UI_ACCENT
            elif state == "current":
                fill = (20, 60, 100); border = UI_HIGHLIGHT
            else:
                fill = (20, 25, 40); border = (40, 50, 70)

            hovered  = (i == self._hovered_node)
            selected = (i == self._active_node)
            if selected:
                # Solid pulsing ring for selected node
                pulse = abs(math.sin(self._t * 3)) * 3
                pygame.draw.circle(surface, UI_HIGHLIGHT, (cx, cy), int(40 + pulse), 3)
            elif hovered:
                pygame.draw.circle(surface, UI_HIGHLIGHT, (cx, cy), 38, 2)

            pygame.draw.circle(surface, fill,   (cx, cy), 30)
            pygame.draw.circle(surface, border, (cx, cy), 30, 2)

            # Stage number / icon
            num_s = self._label_font.render(
                "DONE" if state == "done" else f"{i+1}",
                True,
                UI_GOLD if state == "done" else (UI_TEXT if state == "current" else (60, 70, 90)))
            surface.blit(num_s, (cx - num_s.get_width() // 2,
                                 cy - num_s.get_height() // 2))

            # Stage name label below node
            lbl   = self._small_font.render(STAGE_NAMES[i], True,
                                            UI_SUBTEXT if state == "locked" else UI_TEXT)
            surface.blit(lbl, (cx - lbl.get_width() // 2, cy + 36))

    def _draw_title(self, surface):
        s = self._title_font.render("SELECT STAGE", True, UI_ACCENT)
        surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2, 18))
        # Difficulty badge
        diff = DIFFICULTIES.get(self.difficulty, DIFFICULTIES["normal"])
        badge = self._small_font.render(f"Difficulty: {diff['label']}", True, diff["color"])
        surface.blit(badge, (SCREEN_W // 2 - badge.get_width() // 2, 68))

    def _draw_player_panel(self, surface):
        r = pygame.Rect(SCREEN_W - 200, 70, 185, 110)
        draw_player_hud(surface, self.player, r)

    def _draw_stage_info(self, surface):
        display_node = self._active_node if self._active_node is not None else self._hovered_node
        if display_node is not None:
            i     = display_node
            state = self._node_state(i)
            sr    = pygame.Rect(SCREEN_W // 2 - 140, SCREEN_H - 130, 280, 58)
            panel(surface, sr)
            label = (f"Stage {i+1}: {STAGE_NAMES[i]}"
                     + ("[COMPLETED]" if state == "done" else ""))
            text(surface, label, sr.centerx, sr.top + 12,
                 FONT_XS, UI_HIGHLIGHT, anchor="midtop")
            hint = "Click to select  •  then press ENTER STAGE" if self._active_node is None else "Press ENTER STAGE to begin"
            text(surface, hint, sr.centerx, sr.top + 32,
                 FONT_XS, UI_SUBTEXT, anchor="midtop")