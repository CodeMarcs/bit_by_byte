╔══════════════════════════════════════════════════════════╗
║         Bit By Byte — Sound Assets Folder                ║
╚══════════════════════════════════════════════════════════╝

📁 assets/sounds/
├── sfx/        ← Short one-shot sound effects
│   │              Recommended format: .wav (lowest latency)
│   │              Also supported: .ogg
│   │
│   ├── attack.wav          Player basic attack
│   ├── special.wav         Player special ability
│   ├── heal.wav            Player heals HP
│   ├── player_hit.wav      Player takes damage
│   ├── enemy_hit.wav       Enemy takes damage
│   ├── enemy_defeated.wav  Enemy is defeated
│   ├── stun.wav            Enemy gets stunned
│   ├── flee.wav            Player flees battle
│   ├── victory.wav         Stage complete
│   ├── defeat.wav          Player defeated / game over
│   ├── buy.wav             Successful shop purchase
│   ├── buy_fail.wav        Not enough coins
│   ├── btn_click.wav       Generic UI button click
│   ├── stage_select.wav    Stage node selected
│   └── level_up.wav        Player levels up
│
└── music/      ← Background music tracks (streamed)
    │              Recommended format: .ogg
    │              Also supported: .mp3
    │
    ├── intro.ogg           Intro / splash screen
    ├── menu.ogg            Main menu
    ├── stage_select.ogg    Stage selection map
    ├── battle.ogg          Normal battle
    ├── boss.ogg            Boss battle (Stage 5)
    ├── shop.ogg            Shop screen
    ├── victory.ogg         Victory / game complete
    └── game_over.ogg       Defeat / game over screen

HOW TO ADD YOUR SOUNDS
──────────────────────
1. Place your audio files in the folders above.
2. Open  src/sound.py
3. Find the SFX_FILES or MUSIC_FILES dictionary.
4. Set the matching key to your filename, e.g.:

     "attack": "hit_sword.wav"
     "menu":   "menu_theme.ogg"

5. Run the game — sounds load automatically!

TIPS
────
• Use short .wav files for SFX (under 1 second is ideal).
• Use .ogg for music — smaller than MP3, better looping.
• Adjust overall volume in sound.py:
     SFX_VOLUME   = 0.7   (0.0 – 1.0)
     MUSIC_VOLUME = 0.5   (0.0 – 1.0)
• Free sound resources:
     https://freesound.org
     https://opengameart.org
     https://pixabay.com/sound-effects/
