# THE MASTER LEDGER

The Chronicle of Ashfall Hold, day 1 to day 210, as the board recorded it. Fifty-nine
entries. This file is binding: a chapter may not invent a ledger entry that is not here,
may not alter a delta, and may not restate a cumulative total that disagrees with this
table.

Chapter writers: your chapter's **Ledger** block at the foot of the file is copied from
the rows assigned to your chapter, with the cumulative standing and the drift line taken
from the same rows. Nothing else.

---

## 1. The eighteen verbs (exact weights)

Positive shifts the first-named pole. Values from `game/src/core/chronicle.gd`.

| verb | Memory | Mercy | Communion | Dominion | the line the Teller writes |
|---|---:|---:|---:|---:|---|
| `echo_reclaimed` | +6 | +3 | +1 | +2 | Reclaimed the Echo of %s. |
| `echo_abandoned` | -5 | -3 | -2 | -1 | Left the Echo of %s to grow. |
| `echo_raided` | -8 | -6 | -4 | -5 | The Echo of %s reached the palisade. |
| `vigil_held` | +8 | +4 | +5 | 0 | Held a %s. |
| `vigil_skipped` | -3 | 0 | -2 | +2 | Set out with the dead unburied. |
| `wielder_died` | +2 | 0 | 0 | -3 | %s fell. |
| `successor_taken` | 0 | 0 | +2 | +1 | %s took up the blade. |
| `villager_conscripted` | -1 | -4 | -3 | +5 | Pulled %s from their work to fight. |
| `enemy_spared` | 0 | +6 | +2 | -3 | Walked past %s without drawing. |
| `enemy_slain` | 0 | -1 | 0 | +2 | Put down %s. |
| `relic_spent` | +5 | 0 | +3 | +1 | Spent a relic on stone that will outlast you. |
| `region_saved` | +4 | +7 | +6 | +2 | Pushed the decay back from %s. |
| `region_lost` | -4 | -7 | -5 | -4 | %s went to ash. |
| `ally_revived` | +2 | +8 | +9 | -2 | Lifted %s off the ground. |
| `ally_abandoned` | -2 | -8 | -10 | +3 | Left %s where they fell. |
| `echo_sent` | +3 | -2 | +6 | +4 | Sent the Echo of %s drifting into another settlement. |
| `foreign_echo_slain` | +1 | -3 | +4 | +6 | Put down a stranger's Echo: %s. |
| `foreign_echo_honoured` | +6 | +7 | +9 | -1 | Buried a stranger's Echo: %s. |

All four numbers clamp at plus or minus one hundred.

## 2. How the board reads the drift

Checked in order, first match wins. A positive requirement is a floor, a negative
requirement is a ceiling.

1. **The Wake** — Memory >= 45, Communion >= 40, **and no Echo left standing**, and at
   least one name in the lineage.
2. **The Long Hold** — Dominion >= 50, Mercy <= -20.
3. **Ash Inheritance** — Memory <= -40.
4. **The Open Hearth** — Communion >= 55, Mercy >= 35.
5. **The Quiet Field** — always.

Consequence the novel must exploit: Ashfall's board flips between **The Wake** and **The
Open Hearth** eleven times between day 53 and day 210, and it flips on nothing but
whether a body is currently lying in a field unreclaimed. The Hold's whole fate hinges
on housekeeping.

## 3. The lineage

| # | wielder | blade | reign | bond to predecessor | traits | killed by |
|---|---|---|---|---|---|---|
| 1 | **Rin Ashfall** | Ashblade | d11 to d14 | first, none | Reckless, Quick | Cinder Stalker, Wrenfield |
| 2 | **Maren Verren** | Widow's Maul | d15 to d84 | Spouse | Steady, Scarred | Gravewarden, Stonewake Scarp |
| 3 | **Colm Grey** | Reaper Pike | d85 to d109 | Rival | Grim, Steady | Ash Husk, the Grey Ash |
| 4 | **Yeva Holt** | Ashblade | d110 to d121 | Sibling (disputed) | Quick, Reckless | Cinder Stalkers, Brackwood |
| 5 | **Tarn Stonewake** | Widow's Maul | d122 to d140 | Stranger | Steady, Grim | Gravewarden, Stonewake Scarp |
| 6 | **Sable Kettle** | Hearth Knife | d141 to d155 | Friend | Quick, Tender | Cinder Stalkers, Wrenfield as it went Gone |
| 7 | **Nix Ember** | Ashblade | d156 to d172 | Rival | Reckless, Scarred | Ash Husks, the Grey Ash |
| 8 | **Orrin Dunn** | Reaper Pike | d173 to d196 | Friend | Steady, Grim | at the palisade, Echo of nobody's, tier four |
| 9 | **Wren Ashfall** | Ashblade | d197 to d209 | Spouse | Scarred, Tender | Gravewarden, the Grey Ash |
| 10 | **Grieve Mourne** | Ashblade | d209 to the last page | Friend | Grim, Steady | did not fall; wrote this |

Grieve Mourne's bond is Friend, which makes his Vigils cheap, which is the only reason
the Hold could afford a Wake on day 210. The book's ending is paid for by the fact that
the Teller used to drink with the woman who died.

## 4. Outstanding Echoes, by day

The Wake gate opens only when this count is zero.

| span | standing Echoes |
|---|---|
| before d1 to d38 | 1 — Bel Kettle, laid at the Hold before Low Kettle went under |
| d14 to d19 | +1 Rin Ashfall (2 total) |
| d38 to d84 | 0 |
| d70 | +1 briefly, a stranger's Echo arrived and was buried the same day |
| d84 to d91 | 1 Maren Verren |
| d109 to d116 | 1 Colm Grey |
| d121 to d135 | 1 Yeva Holt (abandoned d130, tier five at the palisade d134) |
| d140 to d147 | 1 Tarn Stonewake |
| d155 to d168 | 1 Sable Kettle |
| d172 to d184 | 1 Nix Ember, roaming from d176, sent out of the Vale d184 |
| d196 to d203 | 1 Orrin Dunn |
| d209 to d210 | 1 Wren Ashfall |

**The lake is not counted.** Low Kettle's drowned are in the Holding at a depth no Teller
could ever survey, so they were never entered, so the board never knew about them. The
Wake was declared over a valley with a village still unkept under the water. Grieve
knows. He writes it in the last chapter and does not settle it.

---

## 5. The table

`Δ` columns are the entry's own movement. `M/Me/C/D` are the standing afterwards.
`Drift` is what the board read at that moment.

| # | day | ch | verb | subject | ΔM | ΔMe | ΔC | ΔD | M | Me | C | D | Drift |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 9 | 6 | `vigil_held` | a Burial | +8 | +4 | +5 | 0 | 8 | 4 | 5 | 0 | The Quiet Field |
| 2 | 11 | 7 | `successor_taken` | Rin Ashfall | 0 | 0 | +2 | +1 | 8 | 4 | 7 | 1 | The Quiet Field |
| 3 | 12 | 8 | `enemy_slain` | Cinder Stalkers, two | 0 | -2 | 0 | +4 | 8 | 2 | 7 | 5 | The Quiet Field |
| 4 | 13 | 9 | `enemy_slain` | a Gravewarden | 0 | -1 | 0 | +2 | 8 | 1 | 7 | 7 | The Quiet Field |
| 5 | 14 | 10 | `wielder_died` | Rin Ashfall | +2 | 0 | 0 | -3 | 10 | 1 | 7 | 4 | The Quiet Field |
| 6 | 15 | 11 | `successor_taken` | Maren Verren | 0 | 0 | +2 | +1 | 10 | 1 | 9 | 5 | The Quiet Field |
| 7 | 19 | 12 | `echo_reclaimed` | Rin Ashfall | +6 | +3 | +1 | +2 | 16 | 4 | 10 | 7 | The Quiet Field |
| 8 | 19 | 12 | `vigil_held` | a Monument | +8 | +4 | +5 | 0 | 24 | 8 | 15 | 7 | The Quiet Field |
| 9 | 19 | 12 | `relic_spent` | — | +5 | 0 | +3 | +1 | 29 | 8 | 18 | 8 | The Quiet Field |
| 10 | 21 | 14 | `vigil_held` | a Telling | +8 | +4 | +5 | 0 | 37 | 12 | 23 | 8 | The Quiet Field |
| 11 | 24 | 16 | `enemy_spared` | the Husk of Oda Ashfall | 0 | +6 | +2 | -3 | 37 | 18 | 25 | 5 | The Quiet Field |
| 12 | 27 | 18 | `enemy_slain` | a Gravewarden | 0 | -1 | 0 | +2 | 37 | 17 | 25 | 7 | The Quiet Field |
| 13 | 31 | 19 | `vigil_held` | a Pyre | +8 | +4 | +5 | 0 | 45 | 21 | 30 | 7 | The Quiet Field |
| 14 | 38 | 20 | `echo_reclaimed` | Bel Kettle | +6 | +3 | +1 | +2 | 51 | 24 | 31 | 9 | The Quiet Field |
| 15 | 47 | 22 | `enemy_spared` | the sick of Brackwood | 0 | +6 | +2 | -3 | 51 | 30 | 33 | 6 | The Quiet Field |
| 16 | 47 | 22 | `region_saved` | Brackwood | +4 | +7 | +6 | +2 | 55 | 37 | 39 | 8 | The Quiet Field |
| 17 | 53 | 23 | `enemy_spared` | Halde, a Gravewarden | 0 | +6 | +2 | -3 | 55 | 43 | 41 | 5 | **The Wake** |
| 18 | 61 | 25 | `vigil_held` | a Telling | +8 | +4 | +5 | 0 | 63 | 47 | 46 | 5 | The Wake |
| 19 | 66 | 26 | `ally_revived` | Tove Rowan | +2 | +8 | +9 | -2 | 65 | 55 | 55 | 3 | The Wake |
| 20 | 70 | 27 | `foreign_echo_honoured` | Sila Verren, a stranger | +6 | +7 | +9 | -1 | 71 | 62 | 64 | 2 | The Wake |
| 21 | 74 | 33 | `relic_spent` | — | +5 | 0 | +3 | +1 | 76 | 62 | 67 | 3 | The Wake |
| 22 | 79 | 34 | `enemy_slain` | a Cinder Stalker | 0 | -1 | 0 | +2 | 76 | 61 | 67 | 5 | The Wake |
| 23 | 84 | 35 | `wielder_died` | Maren Verren | +2 | 0 | 0 | -3 | 78 | 61 | 67 | 2 | The Open Hearth |
| 24 | 85 | 35 | `successor_taken` | Colm Grey | 0 | 0 | +2 | +1 | 78 | 61 | 69 | 3 | The Open Hearth |
| 25 | 88 | 28 | `relic_spent` | — | +5 | 0 | +3 | +1 | 83 | 61 | 72 | 4 | The Open Hearth |
| 26 | 91 | 28 | `echo_reclaimed` | Maren Verren | +6 | +3 | +1 | +2 | 89 | 64 | 73 | 6 | **The Wake** |
| 27 | 95 | 29 | `villager_conscripted` | Asha Vane | -1 | -4 | -3 | +5 | 88 | 60 | 70 | 11 | The Wake |
| 28 | 99 | 30 | `vigil_held` | a Burial | +8 | +4 | +5 | 0 | 96 | 64 | 75 | 11 | The Wake |
| 29 | 104 | 31 | `enemy_spared` | the Yielding | 0 | +6 | +2 | -3 | 96 | 70 | 77 | 8 | The Wake |
| 30 | 109 | 36 | `wielder_died` | Colm Grey | +2 | 0 | 0 | -3 | 98 | 70 | 77 | 5 | The Open Hearth |
| 31 | 110 | 36 | `successor_taken` | Yeva Holt | 0 | 0 | +2 | +1 | 98 | 70 | 79 | 6 | The Open Hearth |
| 32 | 116 | 36 | `echo_reclaimed` | Colm Grey | +6 | +3 | +1 | +2 | 100 | 73 | 80 | 8 | **The Wake** |
| 33 | 121 | 37 | `wielder_died` | Yeva Holt | +2 | 0 | 0 | -3 | 100 | 73 | 80 | 5 | The Open Hearth |
| 34 | 122 | 37 | `successor_taken` | Tarn Stonewake | 0 | 0 | +2 | +1 | 100 | 73 | 82 | 6 | The Open Hearth |
| 35 | 128 | 37 | `vigil_skipped` | — | -3 | 0 | -2 | +2 | 97 | 73 | 80 | 8 | The Open Hearth |
| 36 | 130 | 37 | `echo_abandoned` | Yeva Holt | -5 | -3 | -2 | -1 | 92 | 70 | 78 | 7 | The Open Hearth |
| 37 | 134 | 32 | `echo_raided` | Yeva Holt | -8 | -6 | -4 | -5 | 84 | 64 | 74 | 2 | The Open Hearth |
| 38 | 135 | 32 | `echo_reclaimed` | Yeva Holt | +6 | +3 | +1 | +2 | 90 | 67 | 75 | 4 | **The Wake** |
| 39 | 136 | 32 | `vigil_held` | a Wake | +8 | +4 | +5 | 0 | 98 | 71 | 80 | 4 | The Wake |
| 40 | 140 | 38 | `wielder_died` | Tarn Stonewake | +2 | 0 | 0 | -3 | 100 | 71 | 80 | 1 | The Open Hearth |
| 41 | 141 | 38 | `successor_taken` | Sable Kettle | 0 | 0 | +2 | +1 | 100 | 71 | 82 | 2 | The Open Hearth |
| 42 | 147 | 38 | `echo_reclaimed` | Tarn Stonewake | +6 | +3 | +1 | +2 | 100 | 74 | 83 | 4 | **The Wake** |
| 43 | 152 | 39 | `region_lost` | Wrenfield | -4 | -7 | -5 | -4 | 96 | 67 | 78 | 0 | The Wake |
| 44 | 155 | 39 | `wielder_died` | Sable Kettle | +2 | 0 | 0 | -3 | 98 | 67 | 78 | -3 | The Open Hearth |
| 45 | 156 | 39 | `successor_taken` | Nix Ember | 0 | 0 | +2 | +1 | 98 | 67 | 80 | -2 | The Open Hearth |
| 46 | 163 | 40 | `region_saved` | Wrenfield | +4 | +7 | +6 | +2 | 100 | 74 | 86 | 0 | The Open Hearth |
| 47 | 168 | 40 | `echo_reclaimed` | Sable Kettle | +6 | +3 | +1 | +2 | 100 | 77 | 87 | 2 | **The Wake** |
| 48 | 172 | 40 | `wielder_died` | Nix Ember | +2 | 0 | 0 | -3 | 100 | 77 | 87 | -1 | The Open Hearth |
| 49 | 173 | 40 | `successor_taken` | Orrin Dunn | 0 | 0 | +2 | +1 | 100 | 77 | 89 | 0 | The Open Hearth |
| 50 | 180 | 41 | `ally_revived` | Tove Rowan | +2 | +8 | +9 | -2 | 100 | 85 | 98 | -2 | The Open Hearth |
| 51 | 184 | 41 | `echo_sent` | Nix Ember | +3 | -2 | +6 | +4 | 100 | 83 | 100 | 2 | **The Wake** (by arithmetic only) |
| 52 | 190 | 41 | `foreign_echo_honoured` | Nix Ember, buried in Holt Vale | +6 | +7 | +9 | -1 | 100 | 90 | 100 | 1 | The Wake |
| 53 | 196 | 42 | `wielder_died` | Orrin Dunn | +2 | 0 | 0 | -3 | 100 | 90 | 100 | -2 | The Open Hearth |
| 54 | 197 | 42 | `successor_taken` | Wren Ashfall | 0 | 0 | +2 | +1 | 100 | 90 | 100 | -1 | The Open Hearth |
| 55 | 203 | 42 | `echo_reclaimed` | Orrin Dunn | +6 | +3 | +1 | +2 | 100 | 93 | 100 | 1 | **The Wake** |
| 56 | 209 | 43 | `wielder_died` | Wren Ashfall | +2 | 0 | 0 | -3 | 100 | 93 | 100 | -2 | The Open Hearth |
| 57 | 209 | 43 | `successor_taken` | Grieve Mourne | 0 | 0 | +2 | +1 | 100 | 93 | 100 | -1 | The Open Hearth |
| 58 | 210 | 43 | `echo_reclaimed` | Wren Ashfall | +6 | +3 | +1 | +2 | 100 | 96 | 100 | 1 | **The Wake** |
| 59 | 210 | 43 | `vigil_held` | a Wake | +8 | +4 | +5 | 0 | 100 | 100 | 100 | 1 | **locked: The Wake** |

Final standing: **Memory +100 · Mercy +100 · Communion +100 · Dominion +1.**

Two hundred and ten days, ten wielders, nine graves, and the Vale ended one step on the
side of holding rather than being held. Grieve writes that number down twice, once in the
table and once in a sentence, because he does not believe it either.

---

## 6. Notes for writers, per swing of the board

- **Day 47.** Communion stood at thirty-nine. One short. The Wake was one point of
  Communion away for six days and nobody in the Hold knew, because nobody had reclaimed
  anything to look at the board for.
- **Day 53.** The first time the board ever said **The Wake**. It said it because a
  wielder walked past a Gravewarden that had said her mother's name. The Cull have never
  forgiven that day and they are not wrong to bring it up.
- **Day 95.** Dominion peaked at **+11**, the highest the Hold ever reached, when Asha
  Vane was pulled out of the Carvers' shed and put in a Warden's kit. Eleven. The Long
  Hold needed fifty. The novel should make clear how far Ashfall was from it, and how
  close Vane Hold got.
- **Days 128 to 134.** The only stretch where the Hold behaved badly on purpose: a
  Vigil skipped, an Echo abandoned, and six days later Yeva Holt at the palisade, tier
  five, carrying the Ashblade she had died with. Twenty of the Hold's numbers went in six
  days. This is the book's midpoint and its worst week.
- **Day 152 then 163.** Wrenfield went Gone and then was pushed back. Both are in. The
  board does not average them.
- **Day 184.** The board read The Wake while Nix Ember was walking in a valley two
  ridges east. A ledger can only be honest about what somebody entered into it.
- **Day 210.** The Wake was paid for with a Friend's cheap rites and declared over a lake
  full of the Holding.
