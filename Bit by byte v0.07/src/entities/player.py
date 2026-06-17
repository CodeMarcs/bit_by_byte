"""
entities/player.py — Player stats, levelling, inventory.
"""
from src.settings import (
    PLAYER_BASE_HP, PLAYER_BASE_ATK, PLAYER_BASE_DEF,
    PLAYER_BASE_SPEED, EXP_PER_LEVEL, SPECIALS,
)


class Player:
    def __init__(self):
        self.level   = 1
        self.exp     = 0
        self.coins   = 0
        self.max_hp  = PLAYER_BASE_HP
        self.hp      = self.max_hp
        self.atk     = PLAYER_BASE_ATK
        self.def_    = PLAYER_BASE_DEF
        self.speed   = PLAYER_BASE_SPEED
        self.items   = []        # list of item dicts from SHOP_ITEMS
        self.stunned = False     # set by breakpoint skill

    # ── Combat ──────────────────────────────────────────────────────────────
    def attack_damage(self) -> int:
        import random
        base = max(1, self.atk - 2 + random.randint(0, 4))
        return base

    def special_damage(self, special_index: int, enemy) -> dict:
        """Return a result dict: {dmg, heal, cost, stun, msg}."""
        import random
        sp = SPECIALS[special_index]
        cost = sp["cost"]
        result = {"dmg": 0, "heal": 0, "cost": cost,
                  "stun": False, "msg": sp["name"]}
        if "dmg_mult" in sp:
            base = self.atk * sp["dmg_mult"]
            result["dmg"] = int(max(1, base - 2 + random.randint(0, 4)))
        if "heal_pct" in sp:
            result["heal"] = int(self.max_hp * sp["heal_pct"])
        if sp["name"] == "Breakpoint":
            result["stun"] = True
        return result

    def take_damage(self, amount: int) -> int:
        """Apply damage after defence; return actual damage taken."""
        actual = max(1, amount - self.def_)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        prev = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - prev

    def is_alive(self) -> bool:
        return self.hp > 0

    # ── Progression ─────────────────────────────────────────────────────────
    def gain_exp(self, amount: int) -> list[str]:
        """Add EXP; handle multi-level-ups.  Returns list of event strings."""
        events = []
        self.exp += amount
        events.append(f"+{amount} EXP")
        while self.exp >= self._exp_needed():
            self.exp -= self._exp_needed()
            self._level_up()
            events.append(f"Level Up! → Lv {self.level}")
        return events

    def _exp_needed(self) -> int:
        return EXP_PER_LEVEL * self.level

    def _level_up(self):
        self.level  += 1
        self.max_hp += 20
        self.hp      = min(self.hp + 20, self.max_hp)
        self.atk    += 3
        self.def_   += 1

    def earn_coins(self, amount: int):
        self.coins += amount

    def exp_progress(self) -> float:
        """Return 0-1 for EXP bar."""
        return min(1.0, self.exp / self._exp_needed())

    def hp_progress(self) -> float:
        return self.hp / self.max_hp

    # ── Shop ────────────────────────────────────────────────────────────────
    def apply_item(self, item: dict) -> str:
        t = item["type"]
        if t == "heal":
            gained = self.heal(item["value"])
            return f"Restored {gained} HP"
        elif t == "full_heal":
            gained = self.heal(self.max_hp)
            return "Fully restored HP"
        elif t == "atk":
            self.atk += item["value"]
            return f"+{item['value']} ATK"
        elif t == "def":
            self.def_ += item["value"]
            return f"+{item['value']} DEF"
        elif t == "both":
            self.atk += 15
            self.def_ += 5
            return "+15 ATK, +5 DEF"
        return "Used item"

    def spend_coins(self, amount: int) -> bool:
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False