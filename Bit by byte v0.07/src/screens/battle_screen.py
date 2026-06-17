"""
screens/battle_screen.py — Turn-based battle system.
"""
import math
import random
import pygame

from src.settings import (
    SCREEN_W, SCREEN_H, UI_BG, UI_ACCENT, UI_TEXT, UI_SUBTEXT,
    UI_HIGHLIGHT, UI_DANGER, UI_SUCCESS, UI_GOLD,
    UI_PANEL, UI_BORDER, UI_PANEL2,
    FONT_XS, FONT_SM, FONT_MD, FONT_LG,
    STAGE_ENEMIES, SPECIALS, PIXEL_SCALE,
    DIFFICULTIES,
    STATE_SHOP, STATE_GAME_OVER,
)
from src.entities.player  import Player
from src.entities.enemy   import Enemy
from src.ui.button        import Button
from src.ui.hud           import (
    draw_player_hud, draw_enemy_hud, BattleLog, FloatingText,
    panel, text, bar,
)
from src.pixel_art        import draw_sprite, draw_battle_bg
from src.sound            import SFX


# ── Battle phases ─────────────────────────────────────────────────────────────
PHASE_PLAYER   = "player"
PHASE_ANIM     = "anim"       # short pause after action
PHASE_ENEMY    = "enemy"
PHASE_RESULT   = "result"     # win/lose transition
PHASE_BETWEEN  = "between"    # between enemies in same stage

ANIM_DURATION  = 0.6


class BattleScreen:
    BTN_W, BTN_H = 200, 46

    def __init__(self, player: Player, stage_index: int, difficulty: str = "normal"):
        self.player        = player
        self.stage_index   = stage_index
        self.difficulty    = difficulty

        # Apply difficulty multipliers to a copy of the enemy definitions
        diff = DIFFICULTIES.get(difficulty, DIFFICULTIES["normal"])
        scaled_enemies = []
        for d in STAGE_ENEMIES[stage_index]:
            sd = dict(d)
            sd["hp"]     = int(d["hp"]     * diff["hp_mult"])
            sd["atk"]    = int(d["atk"]    * diff["atk_mult"])
            sd["def_"]   = int(d["def_"]   * diff["def_mult"])
            sd["exp"]    = int(d["exp"]    * diff["exp_mult"])
            sd["coins"]  = int(d["coins"]  * diff["coins_mult"])
            scaled_enemies.append(sd)

        self._enemy_queue  = [Enemy(d) for d in scaled_enemies]
        self._enemy_idx    = 0
        self.enemy         = self._enemy_queue[0]

        self._phase        = PHASE_PLAYER
        self._anim_t       = 0.0
        self._t            = 0.0
        self._flash_player = 0.0  # seconds left for red-flash on player hit
        self._flash_enemy  = 0.0
        self._shake        = 0.0  # camera shake magnitude
        self._shake_offset = (0, 0)
        self._floats: list[FloatingText] = []
        self._log          = BattleLog(pygame.Rect(10, SCREEN_H - 130, 380, 120))
        self._next_state: str | None = None
        self._victory      = False
        self._defeat       = False
        self._between_t    = 0.0

        self._log.add(f"Stage {stage_index + 1} begins!", UI_HIGHLIGHT)
        self._log.add(f"A wild {self.enemy.name} appears!", UI_DANGER)

        self._font_md   = pygame.font.SysFont("Alagard", FONT_MD, bold=True)
        self._font_sm   = pygame.font.SysFont("Alagard", FONT_SM, bold=True)

        self._build_buttons()

    # ── UI build ─────────────────────────────────────────────────────────
    def _build_buttons(self):
        bx = SCREEN_W - self.BTN_W - 20
        by = SCREEN_H - 220
        gap = self.BTN_H + 8
        self._action_btns = [
            Button(bx, by,            self.BTN_W, self.BTN_H, "[Q] ATTACK"),
            Button(bx, by + gap,      self.BTN_W, self.BTN_H, "[W] SPECIAL",
                   colour_border=(180, 80, 220)),
            Button(bx, by + gap * 2,  self.BTN_W, self.BTN_H, "[E] ITEM",
                   colour_border=(80, 180, 120)),
            Button(bx, by + gap * 3,  self.BTN_W, self.BTN_H, "RUN",
                   colour_border=(100, 100, 100)),
        ]
        # Special sub-menu
        self._special_btns = [
            Button(bx - 220, by + i * gap, 210, self.BTN_H,
                   f"[{i + 1}] {sp['name']}  (MP:{sp['cost']})",
                   font_size=FONT_XS,
                   colour_border=(160, 60, 200))
            for i, sp in enumerate(SPECIALS)
        ]
        self._item_btns: list[Button] = []
        self._show_special = False
        self._show_items   = False
        # Confirm button for between-enemies
        self._continue_btn = Button(SCREEN_W//2 - 110, SCREEN_H//2 + 60,
                                    220, 50, "CONTINUE")

    def _refresh_item_buttons(self):
        bx = SCREEN_W - self.BTN_W - 250
        by = SCREEN_H - 220
        gap = self.BTN_H + 6
        items = self.player.items
        self._item_btns = [
            Button(bx, by + i * gap, 230, self.BTN_H - 2,
                   items[i]["name"], font_size=FONT_XS,
                   colour_border=(60, 180, 110))
            for i in range(min(4, len(items)))
        ]
        if not items:
            self._item_btns = [
                Button(bx, by, 230, self.BTN_H - 2,
                       "No items", disabled=True)
            ]

    # ── Public ────────────────────────────────────────────────────────────
    @property
    def next_state(self):
        return self._next_state

    def reset_transition(self):
        self._next_state = None

    # ── Update ────────────────────────────────────────────────────────────
    def update(self, dt: float, events: list):
        self._t     += dt
        self._anim_t = max(0.0, self._anim_t - dt)

        # Shake decay
        self._shake = max(0.0, self._shake - dt * 8)
        if self._shake > 0:
            self._shake_offset = (
                random.randint(-int(self._shake), int(self._shake)),
                random.randint(-int(self._shake), int(self._shake)),
            )
        else:
            self._shake_offset = (0, 0)

        self._flash_player = max(0.0, self._flash_player - dt)
        self._flash_enemy  = max(0.0, self._flash_enemy  - dt)

        for ft in self._floats:
            ft.update(dt)
        self._floats = [f for f in self._floats if not f.done]

        if self._phase == PHASE_BETWEEN:
            self._between_t += dt
            self._continue_btn.update(dt)
            for ev in events:
                if self._continue_btn.handle_event(ev):
                    self._advance_enemy()
            return

        if self._phase == PHASE_RESULT:
            self._between_t += dt
            if self._between_t > 2.0:
                self._next_state = STATE_SHOP if self._victory else STATE_GAME_OVER
            return

        if self._phase == PHASE_ANIM:
            if self._anim_t <= 0:
                self._phase = PHASE_PLAYER
            return

        if self._phase == PHASE_ENEMY:
            self._do_enemy_turn()
            return

        # ── Player turn ─────────────────────────────────────────────────
        for btn in self._action_btns:
            btn.update(dt)
        if self._show_special:
            for b in self._special_btns:
                b.update(dt)
        if self._show_items:
            for b in self._item_btns:
                b.update(dt)

        for ev in events:
            self._handle_player_event(ev)

    def _handle_player_event(self, ev: pygame.event.Event):
        # Keyboard hotkeys: Q = Attack, W = Special, E = Item
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_q:
                self._show_special = False
                self._show_items   = False
                self._player_attack()
                return
            if ev.key == pygame.K_w:
                self._show_special = not self._show_special
                self._show_items   = False
                return
            if ev.key == pygame.K_e:
                self._show_items   = not self._show_items
                self._show_special = False
                self._refresh_item_buttons()
                return
            # 1/2/3 — fire special skill directly (opens sub-menu if closed)
            special_keys = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}
            if ev.key in special_keys:
                idx = special_keys[ev.key]
                if idx < len(SPECIALS):
                    self._show_special = False
                    self._show_items   = False
                    self._player_special(idx)
                return

        # Attack
        if self._action_btns[0].handle_event(ev):
            self._show_special = False
            self._show_items   = False
            self._player_attack()
            return

        # Special sub-menu toggle
        if self._action_btns[1].handle_event(ev):
            self._show_special = not self._show_special
            self._show_items   = False
            return

        # Item sub-menu toggle
        if self._action_btns[2].handle_event(ev):
            self._show_items   = not self._show_items
            self._show_special = False
            self._refresh_item_buttons()
            return

        # Run
        if self._action_btns[3].handle_event(ev):
            SFX.play("btn_click")
            self._log.add("You fled! (lost 10 coins)", UI_SUBTEXT)
            self.player.coins = max(0, self.player.coins - 10)
            self._next_state  = STATE_GAME_OVER
            return

        if self._show_special:
            for i, b in enumerate(self._special_btns):
                if b.handle_event(ev):
                    self._show_special = False
                    self._player_special(i)
                    return

        if self._show_items:
            for i, b in enumerate(self._item_btns):
                if b.handle_event(ev) and i < len(self.player.items):
                    item = self.player.items.pop(i)
                    msg  = self.player.apply_item(item)
                    self._log.add(f"Used {item['name']}: {msg}", UI_SUCCESS)
                    self._show_items = False
                    self._end_player_turn()
                    return

    # ── Combat actions ────────────────────────────────────────────────────
    def _player_attack(self):
        SFX.play("attack")
        dmg    = self.player.attack_damage()
        actual = self.enemy.take_damage(dmg)
        self._log.add(f"You hit {self.enemy.name} for {actual}!", UI_TEXT)
        self._floats.append(FloatingText(f"-{actual}", 640, 200, UI_DANGER))
        self._flash_enemy = 0.25
        self._shake       = 4.0
        SFX.play("enemy_hit")
        self._end_player_turn()

    def _player_special(self, idx: int):
        sp = SPECIALS[idx]
        # Spend HP as "MP" cost (simple approach)
        cost = sp["cost"]
        if self.player.hp <= cost + 5:
            self._log.add("Not enough HP for that!", UI_DANGER)
            return
        self.player.hp -= cost
        SFX.play("special")
        res = self.player.special_damage(idx, self.enemy)

        if res["dmg"] > 0:
            actual = self.enemy.take_damage(res["dmg"])
            self._log.add(f"{sp['name']}! Hit for {actual}!", UI_HIGHLIGHT)
            self._floats.append(FloatingText(f"-{actual}", 640, 200, UI_HIGHLIGHT))
            self._flash_enemy = 0.35
            self._shake       = 6.0
            SFX.play("enemy_hit")

        if res["heal"] > 0:
            gained = self.player.heal(res["heal"])
            self._log.add(f"Healed {gained} HP!", UI_SUCCESS)
            self._floats.append(FloatingText(f"+{gained} HP", 260, 200, UI_SUCCESS))

        if res["stun"]:
            self.enemy.stunned = True
            SFX.play("stun")
            self._log.add(f"{self.enemy.name} is stunned!", UI_ACCENT)

        self._end_player_turn()

    def _end_player_turn(self):
        if not self.enemy.is_alive():
            self._on_enemy_defeated()
            return
        self._phase  = PHASE_ANIM
        self._anim_t = ANIM_DURATION
        # After anim we go to enemy turn (set in update)
        self._phase  = PHASE_ENEMY

    def _do_enemy_turn(self):
        if self.enemy.stunned:
            self._log.add(f"{self.enemy.name} is stunned, skips turn.", UI_ACCENT)
            self.enemy.stunned = False
            self._phase = PHASE_PLAYER
            return

        action = self.enemy.choose_action()
        dmg    = self.enemy.action_damage(action)
        msg    = self.enemy.action_message(action)
        self._log.add(msg, UI_DANGER)

        if dmg > 0:
            actual = self.player.take_damage(dmg)
            SFX.play("player_hit")
            self._log.add(f"You took {actual} damage!", UI_TEXT)
            self._floats.append(FloatingText(f"-{actual}", 260, 200, UI_DANGER))
            self._flash_player = 0.25
            self._shake        = 3.0

        if not self.player.is_alive():
            self._log.add("You were defeated!", UI_DANGER)
            self._phase     = PHASE_RESULT
            self._between_t = 0.0
            self._defeat    = True
            return

        self._phase = PHASE_PLAYER

    def _on_enemy_defeated(self):
        SFX.play("enemy_defeated")
        events_list = self.player.gain_exp(self.enemy.exp_rew)
        self.player.earn_coins(self.enemy.coin_rew)
        for ev in events_list:
            self._log.add(ev, UI_GOLD)
        self._log.add(f"+{self.enemy.coin_rew} coins", UI_GOLD)

        if self._enemy_idx + 1 < len(self._enemy_queue):
            self._phase     = PHASE_BETWEEN
            self._between_t = 0.0
        else:
            # All enemies defeated
            self._log.add("Stage cleared!", UI_SUCCESS)
            self._victory   = True
            self._phase     = PHASE_RESULT
            self._between_t = 0.0

    def _advance_enemy(self):
        self._enemy_idx += 1
        self.enemy = self._enemy_queue[self._enemy_idx]
        self._log.add(f"{self.enemy.name} appears!", UI_DANGER)
        self._phase = PHASE_PLAYER

    # ── Draw ──────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        ox, oy = self._shake_offset
        draw_battle_bg(surface, self.stage_index)

        self._draw_enemy_sprite(surface, ox, oy)
        self._draw_player_sprite(surface, ox, oy)
        self._draw_huds(surface)
        self._log.draw(surface)
        for ft in self._floats:
            ft.draw(surface)

        if self._phase == PHASE_PLAYER:
            self._draw_action_menu(surface)
        elif self._phase == PHASE_BETWEEN:
            self._draw_between_panel(surface)
        elif self._phase == PHASE_RESULT:
            self._draw_result_overlay(surface)

        self._draw_stage_label(surface)

    def _draw_enemy_sprite(self, surface, ox, oy):
        scale = PIXEL_SCALE + 2
        x = SCREEN_W - 16 * scale - 120 + ox
        y = SCREEN_H // 2 - 16 * scale // 2 - 40 + oy
        if self._flash_enemy > 0:
            s = pygame.Surface((16 * scale, 16 * scale), pygame.SRCALPHA)
            s.fill((255, 80, 80, 160))
            surface.blit(s, (x, y))
        bob = int(math.sin(self._t * 2.0) * 4)
        draw_sprite(surface, self.enemy.sprite, x, y + bob, scale, flip_x=False)

    def _draw_player_sprite(self, surface, ox, oy):
        scale = PIXEL_SCALE + 2
        x = 120 + ox
        y = SCREEN_H // 2 - 16 * scale // 2 - 40 + oy
        if self._flash_player > 0:
            s = pygame.Surface((16 * scale, 16 * scale), pygame.SRCALPHA)
            s.fill((255, 0, 0, 140))
            surface.blit(s, (x, y))
        frame = "player" if int(self._t * 2) % 2 == 0 else "player_2"
        draw_sprite(surface, frame, x, y, scale, flip_x=False)

    def _draw_huds(self, surface):
        pr = pygame.Rect(10, 10, 270, 110)
        draw_player_hud(surface, self.player, pr)
        er = pygame.Rect(SCREEN_W - 280, 10, 270, 70)
        draw_enemy_hud(surface, self.enemy, er)

    def _draw_action_menu(self, surface):
        for btn in self._action_btns:
            btn.draw(surface)
        if self._show_special:
            for b in self._special_btns:
                b.draw(surface)
            # Tooltip
            text(surface, "Cost = HP  |  Stun skips enemy turn",
                 SCREEN_W - self.BTN_W - 230, SCREEN_H - 50,
                 FONT_XS, UI_SUBTEXT)
        if self._show_items:
            for b in self._item_btns:
                b.draw(surface)

    def _draw_between_panel(self, surface):
        r = pygame.Rect(SCREEN_W//2 - 180, SCREEN_H//2 - 60, 360, 140)
        panel(surface, r, fill=(15, 25, 15), border=UI_SUCCESS)
        text(surface, f"{self.enemy.name} defeated!", r.centerx,
             r.top + 18, FONT_MD, UI_SUCCESS, anchor="midtop")
        text(surface, "Next enemy incoming", r.centerx,
             r.top + 50, FONT_SM, UI_TEXT, anchor="midtop")
        self._continue_btn.draw(surface)

    def _draw_result_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        if self._victory:
            overlay.fill((0, 30, 0, 160))
            surface.blit(overlay, (0, 0))
            text(surface, "STAGE CLEAR!", SCREEN_W//2, SCREEN_H//2 - 30,
                 FONT_LG, UI_SUCCESS, anchor="midtop")
            text(surface, "Heading to the shop", SCREEN_W//2, SCREEN_H//2 + 20,
                 FONT_SM, UI_SUBTEXT, anchor="midtop")
        else:
            overlay.fill((40, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            text(surface, "DEFEATED", SCREEN_W//2, SCREEN_H//2 - 30,
                 FONT_LG, UI_DANGER, anchor="midtop")

    def _draw_stage_label(self, surface):
        from src.settings import STAGE_NAMES
        lbl = f"Stage {self.stage_index + 1} | {STAGE_NAMES[self.stage_index]}"
        text(surface, lbl, SCREEN_W // 2, 14, FONT_XS, UI_SUBTEXT, anchor="midtop")
        # Difficulty badge top-right
        diff = DIFFICULTIES.get(self.difficulty, DIFFICULTIES["normal"])
        diff_lbl = f"[{diff['label']}]"
        text(surface, diff_lbl, SCREEN_W - 12, 14, FONT_XS, diff["color"], anchor="topright")