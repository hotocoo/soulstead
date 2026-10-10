# THE ASHFALL CHRONICLE

The lore novel of SOULSTEAD. Two hundred and ten days, ten wielders, nine graves, five
endings, and one ledger that refuses to settle anything.

It is not a companion document. It is the Chronicle itself: the append-only ledger kept in
the Hearth of Ashfall Hold, cut in four hands, copied three times, carried out of the Vale
by Wayfarers, and compiled by its fourth Teller, Grieve Mourne, who states his rule on the
first page and keeps it to the last.

> I record what was said. I do not settle it.

## Authority files, read in this order

| File | What it is |
|---|---|
| [`CANON.md`](CANON.md) | The bible. Metaphysics, ash, economy, factions, bestiary, blades, rites, bonds, gazetteer, prohibitions. Outranks everything. |
| [`LEDGER.md`](LEDGER.md) | The master ledger. Eighteen verbs with exact weights, the five endings with exact thresholds, the lineage, and all fifty-nine entries with cumulative standings and drift. |
| [`STYLE.md`](STYLE.md) | The prose contract. Three registers, hard rules, chapter file format, continuity duties. |
| [`OUTLINE-A.md`](OUTLINE-A.md) | Briefs for chapters 1 to 34. |
| [`OUTLINE-B.md`](OUTLINE-B.md) | Briefs for chapters 35 to 52 and the eight appendices. |

## Reading order

**Part I — The Loosing** (chapters 1 to 6). Before and at the founding. How a valley with
good soil discovered what its soil does to the dead, and invented a funeral by argument.

**Part II — The First Blade** (7 to 12). Rin Ashfall, fourteen days, and the widow who
picked up the sword.

**Part III — The Ledger and the Four Readings** (13 to 18). The board, and the four
arguments the Vale has never finished: Memory against Oblivion, Mercy against Ruin,
Communion against Isolation, Dominion against Surrender. Nobody in this part is wrong.

**Part IV — The Side Roads** (19 to 34). Sixteen roads, out of chronological order,
grouped by road and not by year. Every chapter carries a section called **The Other
Roads**: how the same road went in another valley, with the exact numbers it moved and the
ending it bent toward. This is the part that proves the Chronicle is a branching document
and always was.

**Part V — The Lineage** (35 to 42). Eight wielders, chronological, saga-tight. Rival,
sibling, stranger, friend, rival, friend, spouse. The roads are behind them and the line
only goes forward.

**Part VI — The Five Last Pages** (43 to 47). All five endings, fully realised, all true
at once, because they belong to five different holds: The Wake is Ashfall's, The Long Hold
is Vane's, Ash Inheritance is Verren's, The Open Hearth is Holt Vale's, and The Quiet
Field is an unsigned fragment from a hold whose name was never cut anywhere.

**Part VII — Beyond** (48 to 52). Each ending taken forward past its last page, to the
road-shrine, to the next excavation, to the hand that may or may not still be Grieve's, to
eleven valleys writing in each other's books, and to the beginning of a second volume.

**Appendices A to H.** In-world documents: the verbs, the endings, the bestiary, the
blades, the rites, the bonds, the gazetteer, and the names, days and words.

## How the lore and the game agree

Every number in this book comes out of `game/src/core/codex.gd` and
`game/src/core/chronicle.gd`. The lore explains the numbers and never overrides them.
Mechanical exactness is confined to the Ledger blocks and the appendices, because those are
in-world documents and a ledger is allowed to be a ledger. The prose never says *stat*.

If a balance pass changes a weight, `LEDGER.md` is the only file that must be recomputed,
and the chapters' Ledger blocks follow from it.

## Files

```
lore/
├── CANON.md
├── LEDGER.md
├── STYLE.md
├── OUTLINE-A.md
├── OUTLINE-B.md
├── README.md
├── novel/       ch01 … ch52
└── appendix/    A … H
```
