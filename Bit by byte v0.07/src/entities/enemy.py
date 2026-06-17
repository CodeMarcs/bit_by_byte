"""
entities/enemy.py — Enemy stats and AI.
"""
import random


class Enemy:
    def __init__(self, data: dict):
        self.name     = data["name"]
        self.max_hp   = data["hp"]
        self.hp       = self.max_hp
        self.atk      = data["atk"]
        self.def_     = data["def_"]
        self.exp_rew  = data["exp"]
        self.coin_rew = data["coins"]
        self.sprite   = data["sprite"]
        self.stunned  = False
        self._turn    = 0

    # ── Combat ──────────────────────────────────────────────────────────────
    def attack_damage(self) -> int:
        return max(1, self.atk - 2 + random.randint(0, 4))

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.def_)
        self.hp = max(0, self.hp - actual)
        return actual

    def is_alive(self) -> bool:
        return self.hp > 0

    def hp_progress(self) -> float:
        return self.hp / self.max_hp

    def choose_action(self) -> str:
        """Simple AI: attacks every turn, heals at low HP (rare)."""
        self._turn += 1
        if self.hp < self.max_hp * 0.25 and random.random() < 0.25:
            return "defend"
        if self._turn % 4 == 0:
            return "heavy"    # 1.5× damage
        return "attack"

    def action_damage(self, action: str) -> int:
        base = self.attack_damage()
        if action == "heavy":
            return int(base * 1.5)
        if action == "defend":
            return 0
        return base

    def action_message(self, action: str) -> str:
        if action == "heavy":
            return f"{self.name} launches a critical strike!"
        if action == "defend":
            return f"{self.name} recompiles itself…"
        return f"{self.name} attacks!"