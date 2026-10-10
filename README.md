# SOULSTEAD

**A Successor-Sim.** Soulslike weight, colony-sim memory, and a world that never rewinds.

> You never respawn. You are inherited.
> Dark Souls' weight. RimWorld's memory. You die, and the widow picks up the sword.

Godot 4.7, GDScript, 3D (Forward+). No model, texture or audio files ship with the project:
terrain, characters, props and lighting are all generated at load.

## The pitch in five mechanics

1. **Death is inheritance.** No respawn. A real villager, with a real relationship to the
   person who just died, picks up the blade. Their bond sets your Composure and Resolve.
2. **Your corpse is the enemy.** The body stays where it fell and rises as an **Echo**
   carrying your build. Ignore it and it tiers up on the world clock, roams, corrupts the
   region, and finally raids the settlement. The hardest fight in the game is your last build.
3. **Grief is a resource.** Deaths raise settlement grief, which suppresses work. Vigils spend
   grief to buy permanent **Legacies** every future successor inherits. Failure generates
   content instead of a run-back.
4. **Every action moves the ending.** The Chronicle records each verb against four axes
   (Memory, Mercy, Communion, Dominion) and projects the ending live on the settlement's
   ledger board.
5. **Multiplayer shares consequence, not loot.** Friends anywhere on the internet join with a
   lobby code. Their choices bend your ending, and yours bend theirs.

## Layout

```
soulstead/
├── README.md
├── docs/
│   ├── RESEARCH.md      market research: where the 2026 gap actually is
│   ├── GENRE.md         the Successor-Sim genre definition
│   ├── DESIGN.md        systems design for the vertical slice
│   └── MULTIPLAYER.md   online play, relay deployment, async Echo drift
├── game/                the Godot project
│   ├── project.godot
│   ├── scenes/main.tscn
│   ├── src/
│   │   ├── core/        codex (data), world state, chronicle, flow, look (3D art)
│   │   ├── world/       terrain, map generator, terrain mesh builder, expedition
│   │   ├── combat/      combatant base, player, enemies, echoes
│   │   ├── settlement/  hub scene, villagers, hearth, memorial, ledger, lobby stone
│   │   ├── net/         online session, asynchronous Echo exchange
│   │   └── ui/          theme, field HUD, settlement panels, succession, endings
│   └── tests/           headless smoke, scene-flow, and online tests
└── server/              headless relay server (Godot), Dockerfile, fly.toml
```

## Run it

```bash
# Play
godot --path game

# Headless tests
godot --headless --path game res://tests/smoke.tscn       # simulation, saves, echoes
godot --headless --path game res://tests/flow_smoke.tscn  # settlement -> field -> death
godot --path game res://tests/screenshot.tscn             # renders PNGs to user://shots

# Online (two terminals)
godot --headless --path server
SOULSTEAD_RELAY=ws://127.0.0.1:8080 godot --path game
```

## Controls

| Key | Action |
|---|---|
| WASD | Move |
| J / left mouse | Light attack |
| K / right mouse | Heavy attack |
| L | Parry |
| Space | Dodge (invulnerable at the front of the roll) |
| Q | Ash Flask |
| E | Interact |

## Status

Vertical slice. Working end to end: procedural 3D world, committed melee with Composure,
poise and i-frames, enemy tells, death into Echo, Echo tiering and reclaim, succession with
bonds, grief and vigils into legacies, live-projected endings, JSON save/load, online lobbies
over a relay with shared Chronicle, and asynchronous Echo drift between settlements.
