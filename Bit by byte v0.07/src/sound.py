"""
sound.py — Central sound manager for Bit By Byte.

HOW TO ADD SOUNDS
─────────────────
1. Drop your audio files into the correct folder:
      assets/sounds/sfx/       ← short one-shot effects  (.wav or .ogg)
      assets/sounds/music/     ← background music tracks (.mp3 or .ogg)

2. Set the FILENAME ONLY in the SOUND CONFIG section below.
   e.g.  "attack": "attack.wav"   ← just the filename, no folder prefix

3. Call the relevant function anywhere in your code:
      from src.sound import SFX, BGM
      SFX.play("attack")
      BGM.play("battle")

Supported formats
─────────────────
  SFX   → .wav  (recommended, zero latency) or .ogg
  Music → .ogg  (recommended) or .mp3

Volume ranges from 0.0 (silent) to 1.0 (full).
"""

import pygame
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── SOUND CONFIG — edit paths here ─────────────────────────────────────────
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
#  Set each value to the FILENAME ONLY inside assets/sounds/sfx/ or music/.
#  Do NOT include the folder prefix — the manager adds it automatically.
#  Leave as None to silence that slot (no error will be raised).
#

# ── Sound Effects (assets/sounds/sfx/) ──────────────────────────────────────
SFX_FILES: dict[str, str | None] = {

    # ── Battle ──────────────────────────────────────────────────────────────
    "attack":         "attack.wav",          # Player basic attack lands
    "special":        "special.wav",          # Player uses a special ability
    "heal":           None,                   # Player heals HP
    "player_hit":     None,                   # Player takes damage from enemy
    "enemy_hit":      "enemy_hit.wav",        # Enemy takes damage
    "enemy_defeated": "enemy_defeated.wav",   # An enemy is defeated
    "stun":           "stun.wav",             # Enemy is stunned
    "flee":           None,                   # Player flees the battle

    # ── Battle outcome ───────────────────────────────────────────────────────
    "victory":        "victory.wav",          # All enemies in the stage beaten
    "defeat":         "defeat.wav",           # Player is defeated / game over

    # ── Shop ────────────────────────────────────────────────────────────────
    "buy":            "buy.wav",                   # Successful item purchase
    "buy_fail":       "buy_fail.wav",         # Not enough coins

    # ── Navigation / UI ──────────────────────────────────────────────────────
    "btn_click":      "btn_click.wav",        # Generic button click
    "stage_select":   "stage_select.wav",     # Player selects a stage node
    "level_up":       None,                   # Player levels up after battle

}

# ── Background Music (assets/sounds/music/) ──────────────────────────────────
MUSIC_FILES: dict[str, str | None] = {

    "intro":          None,                   # Intro / splash screen
    "menu":           "menu.ogg",             # Main menu
    "stage_select":   "stage_select.ogg",     # Stage selection map
    "battle":         "battle2.ogg",           # Normal battle
    "boss":           "boss.ogg",             # Boss battle (Stage 5)
    "shop":           "shop.ogg",             # Shop screen
    "victory":        "victory.ogg",          # Victory / game complete
    "game_over":      "game_over.ogg",        # Defeat / game over screen

}

# ── Volume ───────────────────────────────────────────────────────────────────
SFX_VOLUME:   float = 0.5    # 0.0 – 1.0
MUSIC_VOLUME: float = 0.3    # 0.0 – 1.0

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Internal implementation — no need to edit below ────────────────────────
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Resolve paths relative to this file so the game works regardless of
# which directory it is launched from.
_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SFX_DIR   = os.path.join(_ROOT, "assets", "sounds", "sfx")
_MUSIC_DIR = os.path.join(_ROOT, "assets", "sounds", "music")

# pygame.mixer reserves this many channels for simultaneous SFX playback.
# The default is only 8, which is enough here, but we reserve a dedicated
# channel per key so rapid calls (e.g. fast clicking) never cut each other off.
_SFX_CHANNELS = 16


class _SFXManager:
    """Loads and plays short sound effects."""

    def __init__(self):
        self._sounds:   dict[str, pygame.mixer.Sound | None] = {}
        self._channels: dict[str, pygame.mixer.Channel]      = {}
        self._loaded = False

    # ------------------------------------------------------------------
    # ROOT CAUSE OF THE SILENCE BUG
    # ------------------------------------------------------------------
    # The previous code called _ensure_loaded() lazily — on the very
    # first SFX.play() call.  At that point pygame.mixer is already
    # running and has initialised its internal resampler with whatever
    # sample-rate / format it negotiated at startup.
    #
    # pygame.mixer.Sound() decodes the WAV and converts it to the mixer's
    # native format at LOAD time, not at play time.  If the mixer was
    # initialised AFTER pygame.init() (which re-initialises the mixer
    # with its own defaults), the channel count or sample format can
    # differ from what init_mixer() requested — and on some platforms
    # (notably Windows WASAPI and certain Linux ALSA configs) a format
    # mismatch between the loaded buffer and the active mixer causes the
    # channel to report "playing" while producing complete silence.
    #
    # THE FIX: expose load() so run.py / game.py can call it explicitly
    # right after init_mixer() + pygame.init(), guaranteeing that every
    # Sound object is decoded against the correct, final mixer format.
    # We also call pygame.mixer.set_num_channels() here so the channel
    # pool is large enough before any Sound is loaded.
    # ------------------------------------------------------------------

    def load(self):
        """
        Pre-load every configured SFX into memory.

        Call this ONCE after init_mixer() and pygame.init() have both
        been called — i.e. after the mixer format is finalised.
        Loading sounds before the mixer is fully ready, or lazily on the
        first play() call, can cause silent playback on some platforms.
        """
        if self._loaded:
            return
        self._loaded = True

        # Expand the channel pool so rapid overlapping SFX don't steal
        # each other's channel and get cut short.
        pygame.mixer.set_num_channels(_SFX_CHANNELS)

        for key, filename in SFX_FILES.items():
            if filename is None:
                self._sounds[key] = None
                continue
            filename = os.path.basename(filename)   # guard against full-path entries
            path = os.path.join(_SFX_DIR, filename)
            if not os.path.isfile(path):
                print(f"[SFX] WARNING: file not found — {path!r}")
                self._sounds[key] = None
                continue
            try:
                snd = pygame.mixer.Sound(path)
                snd.set_volume(SFX_VOLUME)
                self._sounds[key] = snd
                print(f"[SFX] Loaded: {key!r} ← {filename!r}")
            except Exception as exc:
                print(f"[SFX] ERROR loading {path!r}: {exc}")
                self._sounds[key] = None

        # Assign a dedicated mixer channel to every loaded sound so
        # overlapping plays of the same effect don't cancel each other.
        ch = 0
        for key, snd in self._sounds.items():
            if snd is not None and ch < _SFX_CHANNELS:
                self._channels[key] = pygame.mixer.Channel(ch)
                ch += 1

    # Keep backward-compatibility: if someone calls play() without an
    # explicit load(), we still attempt a late load rather than crash.
    def _ensure_loaded(self):
        if not self._loaded:
            print("[SFX] WARNING: load() was not called before play(). "
                  "Call SFX.load() after init_mixer() + pygame.init().")
            self.load()

    def play(self, key: str):
        """Play a sound effect by key name. Silent if not configured."""
        self._ensure_loaded()
        snd = self._sounds.get(key)
        if snd is None:
            return
        ch = self._channels.get(key)
        if ch is not None:
            ch.play(snd)        # dedicated channel — won't cut other sounds
        else:
            snd.play()          # fallback to auto-channel

    def set_volume(self, volume: float):
        """Change SFX volume at runtime (0.0 – 1.0)."""
        global SFX_VOLUME
        SFX_VOLUME = max(0.0, min(1.0, volume))
        self._ensure_loaded()
        for snd in self._sounds.values():
            if snd is not None:
                snd.set_volume(SFX_VOLUME)


class _BGMManager:
    """Streams background music tracks (one at a time)."""

    def __init__(self):
        self._current: str | None = None

    def play(self, key: str, loops: int = -1, fade_ms: int = 800):
        """
        Start a music track.

        Parameters
        ----------
        key     : Key from MUSIC_FILES, e.g. "battle", "menu".
        loops   : -1 = loop forever, 0 = play once, N = repeat N extra times.
        fade_ms : Crossfade duration in milliseconds.
        """
        if self._current == key:
            return   # already playing — don't restart
        filename = MUSIC_FILES.get(key)
        if filename is None:
            self.stop()
            return
        filename = os.path.basename(filename)
        path = os.path.join(_MUSIC_DIR, filename)
        if not os.path.isfile(path):
            print(f"[BGM] WARNING: file not found — {path!r}")
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self._current = key
            print(f"[BGM] Now playing: {key!r} ← {filename!r}")
        except Exception as exc:
            print(f"[BGM] ERROR playing {path!r}: {exc}")

    def stop(self, fade_ms: int = 500):
        """Stop the current music track."""
        pygame.mixer.music.fadeout(fade_ms)
        self._current = None

    def pause(self):
        """Pause the current track."""
        pygame.mixer.music.pause()

    def resume(self):
        """Resume a paused track."""
        pygame.mixer.music.unpause()

    def set_volume(self, volume: float):
        """Change music volume at runtime (0.0 – 1.0)."""
        global MUSIC_VOLUME
        MUSIC_VOLUME = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(MUSIC_VOLUME)

    @property
    def current(self) -> str | None:
        """Key of the currently playing track, or None."""
        return self._current


# ── Module-level singletons ──────────────────────────────────────────────────
# Import and use these anywhere in the project:
#   from src.sound import SFX, BGM
SFX = _SFXManager()
BGM = _BGMManager()


def init_mixer(frequency: int = 44100, channels: int = 2, buffer: int = 512):
    """
    Initialise pygame.mixer with good defaults.

    Call this BEFORE pygame.init() (pre_init locks in the format before
    pygame.init() can override it), then call SFX.load() immediately
    after pygame.init() so sounds are decoded against the finalised mixer.

    Correct call order in run.py
    ─────────────────────────────
        from src.sound import init_mixer, SFX
        init_mixer()        # 1. lock mixer format
        pygame.init()       # 2. finish pygame startup
        pygame.font.init()
        SFX.load()          # 3. decode all WAVs — MUST be after steps 1+2
    """
    pygame.mixer.pre_init(frequency, -16, channels, buffer)
    pygame.mixer.init()
    print(f"[Sound] Mixer initialised — freq={frequency} channels={channels} buffer={buffer}")