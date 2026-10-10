# SOULSTEAD — Systems Design (vertical slice)

Engine: Godot 4.7, GDScript, **3D (Forward+)**, procedural art only - no model,
texture or audio files. Camera is third-person on a spring arm, pitched about
55 degrees, so the field reads tactically while bodies still have weight.
Target: a playable vertical slice that proves the Successor-Sim loop end to end.

## Core loop

```
Settlement (sim, paused world clock)
   -> choose a successor, take the sword, set out
Expedition (real-time souls combat, world clock runs)
   -> kill, loot, reclaim Echoes, fail forward
Death (always eventually)
   -> body drops, becomes an Echo carrying your build
Return to Settlement
   -> Grief rises, Vigils convert Grief into permanent Legacies
   -> next successor inherits Legacies, not gear
```

## 1. Combat model (souls feel, no punishment contract)

- **Commitment:** attacks have startup / active / recovery frames. No cancelling out of
  recovery. Movement is locked during active frames.
- **Composure** (stamina analogue): spent by attack, dodge, sprint, and by taking hits at low
  poise. Regenerates only when not attacking, with a delay.
  `max_composure = base(successor) + relationship_modifier + legacy_bonus + region_modifier`
- **Poise:** absorbing hits without stagger. Heavy enemies have high poise; breaking it opens
  a critical window.
- **Dodge:** 0.18s of invulnerability inside a 0.42s roll with recovery. Dodging costs
  Composure; dodging at zero Composure is a slow sidestep with no i-frames.
- **Parry:** 0.12s window, refunds Composure and breaks poise on success. High risk, high skill
  ceiling — the mastery outlet.
- **Damage:** `dmg = weapon_power * motion_value * (1 - defence_reduction) * poise_break_bonus`.
- **No healing spam:** a limited **Ash Flask** charge count, refilled only at the settlement or
  at a Vigil site.

## 2. Death and the Echo

On death:
1. Record a `DeathRecord`: who died, where, killed-by, region, world-day, carried loadout.
2. Spawn a persistent **Echo** entity at the death position with the dead character's
   weapon, Composure pool, and a subset of their behaviours.
3. Return control to the settlement for Succession.

Echo rules:
- Reclaim (defeat it) to recover the full loadout.
- Every N world-days unreclaimed, the Echo gains a **tier** (+HP, +damage, +one behaviour).
- At tier 3 an Echo leaves its death site and **roams the region**, corrupting tiles.
- At tier 5 it **raids the settlement**: a defence encounter against your own old build.
- Killing an Echo also releases stored Grief and produces a **Relic** for the memorial.

## 3. Succession

On Succession the player sees 3 candidate villagers with:
- Name, age, job, portrait (procedural).
- Stat spread: Vigour / Strength / Dexterity / Resolve.
- **Bond to the deceased** (spouse, sibling, rival, friend, stranger) driving the modifiers:

| Bond | Composure | Resolve | Flavour effect |
|---|---|---|---|
| Spouse | -15% | +25% | Damage bonus near the deceased's Echo |
| Sibling | -5% | +10% | Reclaiming their Echo grants a free Legacy |
| Rival | +10% | -10% | Ignores the deceased's Echo aura entirely |
| Friend | 0 | +5% | Cheaper Vigils |
| Stranger | +15% | -20% | No grief penalty in the settlement |

Taking a villager out of the labour pool costs the settlement their job output. Succession is
therefore a real settlement decision, not a menu of stat rolls.

## 4. Grief, Vigils, Legacies

- Every death adds `grief = 10 + 3 * deceased_bonds` to the settlement pool.
- Grief reduces settlement work output: `output *= clamp(1 - grief/200, 0.35, 1.0)`.
- **Vigils** (built at the memorial) each consume grief and grant a permanent **Legacy**:

| Vigil | Grief cost | Legacy |
|---|---|---|
| Burial | 20 | +6 max HP for all future successors |
| Pyre (burn their gear) | 30 | +1 Ash Flask charge |
| Telling (recount their death) | 25 | +8% Composure regeneration |
| Monument (needs a Relic) | 40 | Unlocks a weapon art from the deceased's build |
| Wake (whole settlement) | 60 | Clears all remaining grief; +5% damage permanently |

Legacies are inherited by every future successor. The lineage gets stronger *because* people
died, which is the genre's central inversion.

## 5. World clock and decay

- One expedition minute = one world-hour; time only runs while outside the settlement.
- Region decay `0..4` rises from: unreclaimed Echoes, NPC deaths, ignored incursions.
- Decay changes the sky and fog, the encounter table, and enemy scaling in the region.
- Decay never reverses on its own — it is pushed back only by reclaiming Echoes and completing
  region rites. The world you leave behind is the world you come back to.

## 6. Settlement layer

- Villagers: name, age, job, traits, bonds, mood, schedule. They walk to jobs on a tile grid.
- Buildings: Hearth (hub, save), Memorial (Vigils), Smithy (weapon upgrades via Relics),
  Fields/Workshop (output), Palisade (raid defence value).
- Output feeds materials; materials build buildings; buildings raise successor floors.
- The settlement is the save file. Quitting always returns you here.

## 7. Data and persistence

Single JSON save under `user://soulstead_save.json`:

```
{ world_seed, world_day, grief, legacies[], materials{},
  villagers[{id,name,age,job,traits[],bonds{},alive}],
  lineage[{name,died_day,killed_by,region}],
  echoes[{id,owner,tier,pos,region,loadout}],
  regions[{id,decay}], buildings[{id,level}] }
```

Everything is plain dictionaries so balance passes stay in one place and saves stay
inspectable.

## 8. Art direction

100% procedural, generated at load:
- Palette: ash grey, ember orange, bone white, moss green. Single accent = ember orange.
- Terrain is one vertex-coloured `ArrayMesh` built from the tile grid (one draw call for the
  whole map), with skirts under raised tiles so rock and walls read as volumes. Collision is
  merged boxes per row, not a trimesh, so the character controller slides predictably.
- Trees are `MultiMeshInstance3D` batches; nothing is hand-placed.
- Characters are capsule-and-sphere figures with a blade stub that shows facing. Echoes are
  the same silhouette in near-black with an ember rim light (cold blue when the Echo drifted
  in from another player's settlement).
- Mood comes from lighting: one directional sun, depth fog, procedural sky. Region decay
  shifts sky, fog colour and fog density toward ember, so the world's state is legible before
  any number is read.
- UI: one panel style, one accent, diegetic labels ("Composure", "Grief", "Vigil").

## 10. Consequence: every action moves the ending

The Chronicle (`src/core/chronicle.gd`) is an append-only ledger. Every meaningful verb the
player performs is recorded with weights on four axes:

| Axis | Poles |
|---|---|
| memory | Memory vs Oblivion |
| mercy | Mercy vs Ruin |
| communion | Communion vs Isolation |
| dominion | Dominion vs Surrender |

Recorded verbs include: reclaiming or abandoning an Echo, letting an Echo raid the
settlement, holding or skipping a Vigil, pulling a villager out of the labour pool, sparing or
killing an enemy, spending a relic, saving or losing a region, reviving or abandoning a
downed ally, sending an Echo to another settlement, and killing or burying a stranger's Echo.

Endings resolve from the axes plus hard gates, and are *projected live* - the settlement
ledger board shows which ending the current drift points at, so consequence is felt during
play rather than revealed at the credits. Shipped endings: The Wake, The Long Hold, Ash
Inheritance, The Open Hearth, The Quiet Field.

## 11. Multiplayer: shared consequence

Online play is consequence-sharing, not damage-sharing. Peers exchange Chronicle entries
through a public relay, so an ally's cruelty or mercy bends *your* ending too. Because the
relay is the only public host, friends on different networks join with a six-character lobby
code and nobody forwards a port. Full detail and deployment in `MULTIPLAYER.md`.

## 12. Vertical-slice scope (what the code must deliver)

1. One region map with decay states.
2. Real-time combat: light/heavy attack, dodge i-frames, parry, Composure, poise.
3. Three enemy archetypes with readable tells.
4. Death -> Echo spawn -> Echo tiering -> reclaim.
5. Succession screen driven by real villagers and bonds.
6. Settlement with Hearth, Memorial, and at least three working Vigils.
7. Save/load of the full state above.
