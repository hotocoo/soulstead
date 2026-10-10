# SOULSTEAD — CANON BIBLE

Authority file for *The Ashfall Chronicle*. Every chapter writer must obey this.
Nothing here may be contradicted. Anything not here may be invented, provided it
does not contradict here.

Source of truth for numbers: `game/src/core/codex.gd`, `game/src/core/chronicle.gd`,
`game/src/core/world_state.gd`, `docs/GENRE.md`, `docs/DESIGN.md`, `docs/MULTIPLAYER.md`.
The lore explains the numbers. It never overrides them.

---

## 1. THE ONE IDEA

What survives a person is not a soul. It is a **hold**: the grip a life had on the
world. Habits, gear, the worn dip in a doorstone, the way a hand knew a haft. Death
releases the person. The hold stays where the body stopped.

Two things can happen to a hold, and only two.

- **The dead keep it.** An unclaimed hold thickens around the corpse and stands it
  up. This is an **Echo**. It is not the person. It is the person's grip, still
  closed, with nothing inside it.
- **The living are given it.** A rite converts the hold into something the whole
  settlement carries. This is a **Legacy**. Every successor after inherits it.

Grief is the third state: **hold that has been released and not yet given**. Unspent.
It sits in the settlement like standing water and it makes the work go badly.

Echo, Legacy, Grief are one substance in three postures. This is the spine of
everything. Every mechanic in the game is a statement about which posture a hold is in.

| Posture | Where it sits | Game surface |
|---|---|---|
| Kept by the dead | corpse, death site, region soil | Echo, tiering, region decay |
| Unspent | the settlement | Grief pool, work-output penalty |
| Given to the living | the lineage | Legacy, successor floors |

**The Vigil is a machine that moves hold from the first posture to the third.**
That is all a funeral has ever been.

### The three motions (in-world liturgy)

Every rite in the Vale names three motions, in this order, always:

1. **The Loosing.** The person leaves. Nobody does this; it happens.
2. **The Holding.** The interval. The hold is closed and unclaimed. Dangerous. Its
   length is not fixed, and the Vale's whole political history is an argument about
   how long it should be allowed to run.
3. **The Keeping.** The rite. The hold is opened and shared out.

A settlement that cannot complete the Keeping is a settlement stuck in the Holding.
Region decay is what a long Holding does to ground.

---

## 2. THE ASH

The Mourne is a dead fire-mountain at the north head of the Vale. Its last breath laid
a hand's depth of grey ash over everything, once, before the Hold. That ash is why
people came.

**Ash ground is the best ground and the worst ground.** It is loose, warm, holds water,
and tills like flour. It also locks. Something in it binds the field's own goodness
where roots cannot reach it, so the first two seasons after an ashfall are the richest
anyone has seen and the fifth is famine on soil that looks identical. The Vale's
answer, learned hard: **bone.** Ground bone, burnt shell from Kettlemere, and lye from
the pyres put back into the furrows. The Hold feeds its fields its dead. Not as
metaphor. As agronomy.

Nobody in the Vale has the words *phosphorus* or *allophane*. They have the words
**locked ground** and **the fields are hungry again**. Writers: never supply the modern
word. Supply the practice.

**The ash of the Ashlands is different.** That is not fall-ash. That is what ground
becomes where hold has been drawn out and never put back. An Echo feeds. It pulls hold
from the soil around its death site to grow itself, and what it leaves behind goes grey,
loose, sterile, and quiet. Fall-ash grows barley. Drawn-ash grows nothing and never
will. They are the same colour. Telling them apart is a Forager's whole craft.

Region decay is drawn-ash saturation. It never reverses on its own because nothing in
the Vale puts hold back into ground except a completed Keeping.

**Decay states** (0 to 4), the names used on the ledger board:

| Value | Name | What it looks like |
|---|---|---|
| 0 | **Quick** | green, wet, loud with insects |
| 1 | **Turning** | grass going pale at the root, birds thinner |
| 2 | **Greying** | ash in the seams of everything, colour draining |
| 3 | **Ashen** | drawn-ash over soil, trees standing dead upright |
| 4 | **Gone** | no sound, no growth, ash to the ankle, routes closed |

---

## 3. THE ASH ECONOMY

Pyres are not only piety. Ash is the Vale's only manufacture.

- Ash steeped in water and drawn off clear gives **lye**. Lye gives soap, and soap is
  the only thing Ashfall Hold has ever sold to anyone.
- Lye boiled dry in the pot gives **pot-ash**. Pot-ash refined again gives a finer white
  powder the Carvers call **pearl**.
- Pearl put into sand at the Smithy's hot end lets glass run at a heat a wood fire can
  actually reach. Without pearl there is no glass in the Vale.
- **The Memorial's name-panes are glass.** Each pane is fluxed with pearl drawn from the
  pyre of the person whose name is cut into it. A name is written in the substance of
  the named. This is the single most important physical fact about the Memorial and it
  should be stated plainly once, early, and then never explained again.
- Lye and bone go back to the fields. See section 2.

**The Ash Flask.** Not a potion. Pyre-ash steeped, settled three days, drawn off clear,
and cut with hearth-water until it will not strip a throat. It is drunk. It burns going
down and keeps burning. What it does is close a loosened grip: it gives a body back
hold it has spent, briefly, at cost. Three is the standing ration and three is not
caution, it is the dose above which people have died at the Hearth with their teeth
grey. The Pyre rite raises the ration by one because a pyre yields the ash. The Healers
of the Hold ration the Flask and have gone to the palisade over it.

**Relics.** When an Echo is put down, the grief it had stored comes out all at once, and
in that release a little of the hold hardens. What is left is a **relic**: a dense
knuckle of matter, warm, slightly wrong to hold, shaped nothing like anything. A relic
is hold that will not go back to being anybody's. The Smithy can bind one into steel,
and the steel then remembers a motion the dead knew. This is how a weapon art passes
down. The Carvers can set one under a stone, and the stone then holds ground against
drawn-ash. This is what a Monument physically does.

---

## 4. THE BODY: COMPOSURE, POISE, THE BLADE

Never write the words *stamina*, *stat*, *hit points*, *cooldown*, *i-frames*, or
*player*. Write bodies.

**Composure** is how much of your own hold you can spend before your grip opens.
Swinging spends it. Rolling spends it. Sprinting spends it. Being hit while your poise
is low spends it. It comes back only when you are not swinging, and not at once.

Composure is not a fixed quantity of a person. It is set by where you are standing and
who you are standing near.

- At the Memorial, where your hold is already shared out, spending is cheap.
- Near the Echo of someone who loved you, spending is expensive. You and it are closing
  on the same hold and it is closer to it than you are. This is why a widow fights hard
  and tires fast.
- In a region your lineage has died in repeatedly, the ground itself is already holding
  a great deal that used to be yours. Spending is expensive there too.

This is the canon explanation for `max_composure = base(successor) + relationship_modifier
+ legacy_bonus + region_modifier`. A grieving spouse has less because more of what they
had is out there in the field with their dead. A stranger has more because they have
nothing invested in the corpse at all.

**Poise** is borrowed hold worn on the body. Heavy armour is heavy because it is packed.
A Gravewarden has enormous poise for exactly this reason and no other. Break the packing
and the wearer is briefly only a person, and that is the window.

**Commitment.** A swing is a thing you agree to before it happens. Startup, active,
recovery. You cannot take it back partway. This is not a rule of combat, it is the
Vale's entire moral position rendered as frames.

**Parry** is not a block. It is meeting another body's spending with your own timing so
precisely that the spending comes back to you instead. Twelve hundredths of a second.
The Wardens of the Hold teach it and almost nobody learns it.

---

## 5. THE FOUR READINGS

There is no priesthood in the Vale. There is an argument, and it has four axes, and
every settlement in every valley sits somewhere on all four. The ledger board in the
Hearth shows where Ashfall sits. It is read aloud at the turn of every season.

| Axis | Poles | The argument |
|---|---|---|
| **Memory / Oblivion** | keep the name, or take it off | Does remembering the dead hold the living together, or does it hold the dead here? |
| **Mercy / Ruin** | spare it, or end it | Is a thing that carries hold owed anything? |
| **Communion / Isolation** | open the gate, or hold the line | Is another lineage's dead your business? |
| **Dominion / Surrender** | take the ground, or give it | Is the Vale something you hold, or something you are in? |

The board shows a signed number on each axis, between minus one hundred and plus one
hundred, and below them one line: **Drifting toward**, and the name of an ending.

### The factions

None of them are villains. Each is a correct reading of a real problem. Writers who
make the Unnaming into a cult of evil have failed.

**The Tellers** (Memory). Keep the Chronicle, cut the panes, say the names at the turn
of the season. Doctrine: the bond does not end, it changes shape, and a settlement that
carries its dead forward is a settlement with more in it than the living could manage
alone. Every Legacy in the Vale exists because a Teller held a rite. Their weakness:
they will hold a Telling for a name when the settlement needs the grief spent on
something faster.

**The Unnaming** (Oblivion). Not a cult. A working theory, and a defensible one: **an
Echo grows because it is being called.** Names are what keep a hold closed. Shave the
name off the pane, stop saying it, and the grip opens on its own with nobody having to
walk out to it with a maul. They point out, correctly, that the Vale's dead did not
walk before the Vale started writing them down. They practise the shaving in the dark
because the Tellers hang people for it. Their weakness: it has never once been
demonstrated to work, and settlements that go far down this road stop being able to say
who anyone is, including themselves.

**The Hearthkeepers** (Mercy). Healers. Doctrine: a Husk is a person who was failed.
You do not owe it a blade, you owe it a rite. They quarantine instead of culling, they
ration the Flask, they will lift a stranger off the ground. Their weakness: the
Brackwood sickness, and what mercy cost there.

**The Cull** (Ruin). Wardens, mostly, and Foragers who have seen a region go Gone.
Doctrine: hold is contagion. Anything carrying it, anything that might carry it, goes
down early and goes down cheap, and that includes the sick, and they will say so out
loud. They are the reason the Hold is still standing after the third Greying and they
know it. Their weakness: a settlement that has culled enough stops being able to name
a reason to defend itself.

**The Open Road** (Communion). Wayfarers. Gravediggers with no valley. They carry
copies of chronicles between holds, they bury strangers' Echoes for nothing, and they
argue that hold does not recognise a palisade so neither should a rite. They are how
any of this is known outside one vale. Their weakness: they bring other valleys' dead
with them, and other valleys' arguments.

**The Long Hold** (Isolation). Doctrine: one lineage, one wall, one ledger, and nothing
from outside. Named after Vane Hold, which held the line perfectly and is a ruin on the
Vane Road with the gate still barred from inside.

**The Gravewardens** (Dominion). Was an order of people. Bound relics into their own
armour, plate by plate, on the theory that a body carrying enough borrowed hold cannot
be opened by anything. They were right. That was the problem. They are still standing
in the Stonewake barrows, upright, packed, not dead and not anybody, and they will
speak names of people whose holds are in their plating. The Hold's word for the enemy
archetype and the Hold's word for the old order are the same word, and that is
deliberate, and characters should be uncomfortable about it.

**The Yielding** (Surrender). Walk into the Ashlands. Sit down. Let the ground take the
hold back early and unclosed, on the argument that the Vale is owed it and the rite was
always a theft. They leave no Echo. That fact is the strongest argument anyone in the
Vale has ever made for anything, and everyone hates it.

---

## 6. THE BESTIARY (exact)

| | Ash Husk | Cinder Stalker | Gravewarden |
|---|---|---|---|
| health | 46 | 34 | 90 |
| damage | 9 | 12 | 18 |
| poise | 20 | 12 | 55 |
| speed | 34 | 64 | 30 |
| tell | 0.45 s | 0.26 s | 0.62 s |
| reach | 22 | 20 | 30 |
| posture | shambler | darter | bulwark |
| relics | 0 | 0 | 1 |

**Ash Husk.** A villager whose hold was never taken up. It walks its last chore. Husks
found in the fields carry the motion of reaping; Husks found at the Hearth carry the
motion of setting a table. Its tell is long and slow and forgiving, and that is the
worst thing about it, because it means you have time to recognise the motion.

**Cinder Stalker.** Not a person. Vale animals, changed by drawn-ash, that learned hold
is food. Thin, quick, low-packed, and they come out of tall grass and out of ash where
the ground is Greying or worse. A quarter-second tell. They die to one clean swing and
they do not come alone.

**Gravewarden.** See section 5. Packed with borrowed hold, slow, enormous reach, a tell
you can see coming from across a barrow and cannot afford to be wrong about. Breaking
the packing is the only way in. It drops one relic, and the relic is somebody.

**Echoes** are their own category and are never called enemies on the board. They are
called by the name of the person. Always. A Warden who says *the husk in the west field*
about a wielder's Echo is corrected, coldly, by whoever hears it.

Echo growth: a tier every two world-days unclaimed. At tier 3 it leaves the death site
and roams, and the ground it crosses goes toward Ashen. At tier 5 it comes to the
palisade. It fights with the build it died with, at the skill it died with, plus
everything the Vale has fed it since.

---

## 7. THE FOUR BLADES (exact)

| | Ashblade | Reaper Pike | Widow's Maul | Hearth Knife |
|---|---|---|---|---|
| power | 16 | 13 | 24 | 9 |
| reach | 26 | 40 | 24 | 18 |
| arc | 1.4 | 0.6 | 1.9 | 1.2 |
| light startup/active/recovery | .10/.10/.20 | .14/.09/.24 | .20/.12/.32 | .06/.08/.14 |
| light cost / poise | 12 / 14 | 13 / 10 | 20 / 26 | 8 / 6 |
| heavy startup/active/recovery | .28/.14/.38 | .34/.12/.40 | .46/.16/.52 | .18/.10/.26 |
| heavy cost / poise | 26 / 34 | 28 / 26 | 36 / 60 | 18 / 16 |

**Ashblade.** The Hold's first weapon and its only sword. Forged in year one out of a
plough coulter and the iron off a cart. Carried by the first wielder. The blade every
successor is handed by default, which is why *taking the sword* and *taking the blade*
mean succession in every sentence anyone in the Vale speaks.

**Reaper Pike.** A Field-hand's tool with the head reforged. Forty of reach and a
one-body arc. It is the weapon of somebody who has decided never to be close to
anything again. Colm Grey's.

**Widow's Maul.** Twenty-four of power, a two-body arc, and a heavy swing that takes
just under half a second to arrive. Made at Maren Verren's request out of the quarry
sledge, and named by the Hold before she could stop them.

**Hearth Knife.** Eighteen of reach. Nine of power. Six hundredths of a second from
decision to edge. A kitchen tool. It is on this list because Sable Kettle carried
nothing else and lived longer than three people who carried better.

---

## 8. THE RITES (exact)

| Vigil | Grief | Relic | Legacy | In-world |
|---|---|---|---|---|
| **Burial** | 20 | 0 | +6 max health, all later successors | Body into ground, whole, with its gear. Slowest Keeping, deepest. |
| **Pyre** | 30 | 0 | +1 Ash Flask charge | Body and gear burned together. Yields the ash the Flask is cut from. |
| **Telling** | 25 | 0 | +8% Composure regeneration | The death recounted aloud, in full, in front of everyone, by someone who saw it. |
| **Monument** | 40 | 1 | +10% weapon power | Stone raised over a *reclaimed* Echo, relic set beneath. Holds ground. |
| **Wake** | 60 | 0 | +5% damage, **clears all grief** | The whole Hold drinks. Everything unspent is spent at once. |

Rules that must never be broken in prose:

- A **Monument** requires a reclaimed Echo and a relic. You cannot raise stone over
  somebody still standing in a field.
- A **Wake** takes sixty of grief and leaves none. A Hold cannot Wake its way out of a
  shortage; it can only Wake out of a surplus.
- Grief per death: `10 + 3 x (number of bonds the dead had)`. The well-loved cost more.
  This is the cruellest arithmetic in the Vale and everyone knows it.
- Grief suppresses work: `output x clamp(1 - grief/200, 0.35, 1.0)`. At two hundred of
  grief a Hold works at just over a third and cannot build its way out.
- Legacies are inherited by **every** future successor, forever, and cannot be lost.
  The lineage gets stronger because people died. State this once, flatly, and let it
  sit.
- **An Echo is a purse.** While it stands it stores what the ground draws and what the
  Hold could not spend. When it is put down, all of that grief arrives at the settlement
  at once. This is why a Hold that reclaims can afford its funerals and a Hold that
  leaves its dead in the fields cannot. Established day 19, Bran Holt's observation:
  *the ones who go and get them can pay for the funerals. The ones who do not, cannot.*
- **An Echo does not leave its ring until the third growth.** Below that it will come to
  the rim of the bent grass and stop. At the third growth it leaves and roams, and that
  single change is the only reason a palisade has ever had to be defended.
- **The ring.** An Echo bends the grass inward around itself and pales the root out to
  the rim. Three paces on the first day, eleven by the fourth. A reclaiming stands the
  ring back up in the time it takes to draw a breath, and the pale stops spreading that
  hour and never resumes. A Monument's stone holds its own eleven paces against decay
  permanently, which is why there is Quick grass in the middle of Gone ground at
  Wrenfield.

---

## 9. SUCCESSION AND BONDS (exact)

On a death the Hold holds a **Succession**: three villagers are named, and one takes the
blade. Taking them out of the labour pool costs the Hold their job output. A Succession
is a staffing decision and a funeral at the same time.

| Bond | Composure | Resolve | Effect | Line said at the Succession |
|---|---|---|---|---|
| Spouse | x0.85 | x1.25 | damage bonus near the deceased's Echo | *They shared a roof with the dead.* |
| Sibling | x0.95 | x1.10 | reclaiming the Echo grants a free Legacy | *Blood of the fallen.* |
| Rival | x1.10 | x0.90 | ignores the deceased's Echo aura entirely | *Never liked them. Will still carry the blade.* |
| Friend | x1.00 | x1.05 | cheaper Vigils | *Drank with the dead most nights.* |
| Stranger | x1.15 | x0.80 | no grief penalty inside the settlement | *Never learned their name.* |

Base: 100 health, 100 composure, 3 Flasks.

**Jobs:** Field-hand, Smith, Forager, Warden, Healer, Carver. Six, no others.

**Traits:** Steady (+12 composure, *hands do not shake*), Reckless (-8 composure, +0.15
resolve, *swings first*), Scarred (+0.10 resolve, *has survived worse*), Tender (+6
composure, -0.05 resolve, *heals faster at the Hearth*), Grim (+4 composure, +0.05
resolve, *grief lands lighter*), Quick (+10 composure, -0.05 resolve, *rolls come
cheap*). Six, no others.

**Given names** (the only given names in the Vale): Rin, Sable, Oda, Maren, Colm, Yeva,
Tarn, Bel, Halde, Nix, Orrin, Sila, Grieve, Wren, Tove, Ketil, Asha, Bran.

**Family names** (the only ones): Ashfall, Grey, Holt, Verren, Stonewake, Ember, Dunn,
Mourne, Kettle, Vane, Brack, Rowan.

Do not invent a name outside these lists. If you need more people, combine differently.
The smallness of the name-stock is a fact about the Vale and the novel should feel it.

---

## 10. THE VALE (gazetteer)

Ninety-six by seventy-two, one region at a time, which is as much ground as one body can
cross in a day and get back.

- **Ashfall Hold.** The settlement. Hearth (hub, the ledger board, the only safe fire),
  Memorial (the name-panes, where Vigils are held), Smithy (relic-binding, glass),
  Fields and Workshop (output), Palisade (what stands between the Hold and a tier five).
- **Wrenfield.** The near fields and, past the last fence, the long grass. Grass and
  tall grass. Where the Hold eats from and where Stalkers come out of.
- **The Grey Ash.** North, under the Mourne. Drawn-ash and fall-ash mixed past telling
  apart. The Yielding walk here.
- **Stonewake Scarp.** Rock. Quarry, lime-kilns, and the Gravewarden barrows above.
- **Kettlemere.** The lake the Kettle feeds. Low Kettle is under it: a village drowned
  before the Hold, whose dead are in the intermediate posture and have been for a very
  long time, at a depth nobody can walk to.
- **Brackwood.** Trees. Charcoal burners, the quarantine huts, the sickness.
- **The Vane Road.** Wall. Vane Hold's ruin, gate barred from inside, ledger board still
  legible. Work of giants, in the elegiac sense: nobody now living could build it and
  nobody now living knows why they would.

Tile substances, canon: water, sand, grass, tall grass, ash, rock, tree, wall.
Encounters come out of tall grass and ash, and out of nothing else.

---

## 11. TIME

One expedition minute is one world-hour. The clock runs only when a body is outside the
palisade. Inside the Hold, nothing moves.

This is not a convenience. It is the Vale's oldest observed fact and its central horror:
**the world only decays while somebody is out in it.** The Unnaming built a whole
doctrine on this. The Tellers have never had a good answer. Nobody has ever tested the
obvious experiment, because the obvious experiment is to send nobody out ever again,
and that is what Vane Hold did.

Day one is the raising of the Hearth. The Chronicle counts from there.

### World-days are not calendar days. This is load-bearing and absolute.

The board counts **world-days**: days the Vale spent moving. The Vale moves only while a
body is beyond the last fence. Work in the near rows, inside the fence line, is inside.
The long grass past the last fence, the scarp, Brackwood, the mere road, the Grey Ash and
the Vane Road are outside.

So the two hundred and ten days of this Chronicle are two hundred and ten days of the
world's own accounting, and they are spread across **rather more than twenty calendar
years** of a settlement's life, because a Hold of twenty-odd people sends one body past
the fence and otherwise stays in and gets nothing but older.

Consequences that every writer must honour:

- **People age normally. The board does not.** Grieve Mourne is nine on world-day 55,
  twelve on world-day 72, and thirty-two on world-day 209, and there is no contradiction,
  because seventeen world-days were three summers and a hundred and thirty-seven were
  twenty years.
- Bel Brack is eleven in the yard on world-day 16 and seventeen at the fire on world-day
  31. Six calendar years, fifteen world-days.
- Maren Verren's sixty-nine days with the blade are sixty-nine world-days and most of a
  working life.
- A season, a harvest, a marriage, a child growing up: these are counted in the Hold's own
  talk, in seasons and years, and never in board-days. A villager says *the spring before
  last*. A Teller says *the hundred and thirtieth*. They are two different instruments and
  characters switch between them without noticing.
- An Echo grows a tier every two world-days, which is why an Echo left in a field can grow
  a tier across a fortnight of calendar time in which nobody happened to go out, and why
  it can grow two in an afternoon when three Foragers are at the kilns. Chapter 11
  establishes this: Rin Ashfall's Echo tiered because two people were burning shell at
  Stonewake and did not know anybody had died.
- **This is the Vale's central horror and it is stated once, plainly, and then lived with:
  the world only decays while somebody is out in it.** It is also the correct premise from
  which Vane Hold reasoned, and they barred the gate, and they were right, and it did not
  matter.
- Grieve compiling can therefore say *forty years cold*, *twenty years apart*, *I have
  thought about that entry for eleven years*, and be exact.

---

## 12. THE CHRONICLE, AND THE RULE OF THE TELLER

The novel *is* the Chronicle: an append-only ledger, kept in the Hearth, cut in hands of
different quality, copied three times and carried out of the Vale by Wayfarers.

Every meaningful act is one line. The line has a day, a verb, a subject, the four
numbers it moved, and the sentence the Teller wrote. There are eighteen verbs and there
have only ever been eighteen. See `LEDGER.md`.

**The Teller's rule, stated in chapter one and obeyed to the last page:**

> I record what was said. I do not settle it.

The Chronicle contains contradictions on purpose. Two hands give two accounts of the
same afternoon and both stay in. Where the copies disagree, the disagreement is copied
too. The Teller does not arbitrate, does not harmonise, and does not know the ending
while writing toward it, only the board's line: *Drifting toward*.

This is the licence for the book to hold five endings and every branch of every side
road without lying. It is not a trick. It is what a ledger is.

**The hands** (who wrote what):

- **First hand, Sila Carver.** Founding to day 20. Cramped, abbreviated, cuts letters
  to save wax. Records weather with suspicion.
- **Second hand, Bran Holt.** Days 20 to 96. Legible, dull, complete. Hated by later
  Tellers for recording nothing he was not asked to.
- **Third hand, Asha Vane.** Days 96 to 140. Fast, angry, argues with the entries she is
  copying. Conscripted on day 95 and wrote the board from inside a Warden's kit.
- **Fourth hand, Grieve Mourne.** Day 140 to the last page. Compiler and narrator of
  this book. Assembles the three earlier hands, villager testimony, the Memorial panes,
  the Vane Road board, and Wayfarer copies of four other valleys' chronicles. Does not
  settle anything.

---

## 13. THE FIVE LAST PAGES

Endings resolve from the four numbers plus hard gates, checked in this exact order,
first match winning. A positive requirement is a floor; a negative requirement is a
ceiling.

| Order | Ending | Requires | Gate |
|---|---|---|---|
| 1 | **The Wake** | Memory >= 45, Communion >= 40 | every Echo reclaimed, lineage not empty |
| 2 | **The Long Hold** | Dominion >= 50, Mercy <= -20 | none |
| 3 | **Ash Inheritance** | Memory <= -40 | none |
| 4 | **The Open Hearth** | Communion >= 55, Mercy >= 35 | none |
| 5 | **The Quiet Field** | nothing | none |

Because The Long Hold is checked before The Open Hearth, a settlement that is both
generous and ruthless is remembered for the ruthlessness. Because The Wake is checked
first but gated on every Echo reclaimed, it is the only ending you cannot drift into by
accident: somebody has to go out and get all of them.

**The Quiet Field is not a failure state.** It is what happens to almost everyone, and
the novel must treat it with more respect than the other four.

Canon assignment of the five, so that all five are true at once without contradiction:

- **The Wake** is Ashfall Hold's, day 210. The mainline.
- **The Long Hold** is Vane Hold's, ended before the Hold was founded, recovered as a
  barred ruin and a legible board on the Vane Road.
- **Ash Inheritance** is Verren Hold's, two valleys east, known from a Wayfarer copy in
  which the last forty pages are in one hand writing under a name that is not its own.
- **The Open Hearth** is Holt Vale's, concurrent with Ashfall, known because their
  wielder and ours lifted each other off the ground on day 180.
- **The Quiet Field** is from an unsigned fragment of a chronicle from a hold whose name
  was never cut anywhere. It is the commonest ending in the world and the only one with
  no monument.

---

## 14. MULTIPLAYER, DIEGETICALLY

Four lineages at most can share a season. A **lobby code** is, in the world, a
Wayfarer's route-mark: six characters cut into a post at a crossing, meaning *a hold
this way is keeping a board you can write on*.

What crosses between holds is not the world. It is **entries**. Wayfarers carry ledger
lines, not maps. So two holds that share a season share consequences and not ground: a
cruelty done in your valley moves the number on my board because my Teller copied your
line.

An Echo that goes unclaimed long enough and roams far enough **drifts**, and can arrive
in another valley entirely, carrying its owner's name and the build it died with. What
the receiving hold does with it, burying it or putting it down, is written back into the
sending hold's Chronicle. This is `echo_sent`, `foreign_echo_honoured`,
`foreign_echo_slain`, and it is how The Open Hearth becomes reachable at all.

---

## 15. HARD PROHIBITIONS

- No gods. No afterlife. No prophecy. Nobody is chosen. There is no dark lord, no
  ancient evil, and no cure.
- No magic system. Hold is a material with rules, described by people without
  instruments.
- No em-dashes anywhere in any lore file. Commas, colons, semicolons, full stops.
- No modern register. No *okay*, *fine*, *look*, *honestly*, *I guess*.
- Never name a mechanic as a mechanic in narration. Mechanical exactness lives in the
  **Ledger** blocks and the appendices, which are in-world documents, and nowhere else.
- Never resolve a contradiction between two accounts.
- Never make a faction evil.
- Never let the Hold be saved by an outsider, a discovery, or a weapon.
- Nobody ever explains the metaphysics in a lecture. It accrues. A reader should
  understand hold by chapter fifteen without having been told it in one place.

---

## 16. ESTABLISHED IN PROSE

Facts fixed by chapters already written. Binding on every later chapter. Append to this
list when you establish something a later chapter will need.

**People and habits**
- **Oda Ashfall** died day 6 of an ordinary thing, had nine bonds, grief 37, buried whole
  with her knife day 9. Her Husk still walks the reaping motion in the west field after
  the Burial and no two accounts agree how that is possible.
- **Rin Ashfall**, nineteen, had five bonds, grief 25. Touched the doorstone with the flat
  of two fingers every time she went out. Killed by four Cinder Stalkers (Ketil says four,
  Bran's copy says three, Bel says four then says he assumed the fourth) on loose ash at
  the foot of the cut bank on the west slope of Wrenfield.
- **Maren Verren**, twenty-six, Field-hand, Steady and Scarred, flat scar on the forearm
  from before the Vale, never explained. Never touched the doorstone. Held the blade 69
  days, the longest of anyone.
- **Bel Brack**, Ketil's apprentice: eleven years old in Part II, constantly on things he
  should not be on, the only witness to Rin's death from the palisade frame. Dies at the
  fire at seventeen on day 31 and is the subject of the Pyre in chapter 19.
- **Bran Holt**, fifty-one, bad hip, tally board. Works out on day 20 that the clock
  belongs to whoever is outside, so the Hold counts **days-lying-out**, not days since
  death. His line: *the ones who go and get them can pay for the funerals. The ones who do
  not, cannot.*
- **Sila Carver**, first hand, died day 28 in bed at fifty-four of nothing in particular.
  Cut the first two panes in the Vale. Her own pane has the S wrong and was not restarted.
- **Ketil Brack**, thirty-eight, Smith. Made the Ashblade in two days out of a plough
  coulter and cart iron and was not proud of it. Puts his hand on the back of a boy's neck
  to mean be quiet immediately.
- **Grieve Mourne**: nine years old in chapter 24, twelve and apprenticed in chapter 33
  (cuts Bel Kettle's pane and gets the K wrong), thirty-two in chapter 43. Cuts glass and
  wax since twelve and has the forearms for it and nothing else.

- **Sila Grey**, Forager. A girl in the yard on world-day 16, sixty-one in the last
  chapter. She is the Unnaming's advocate in the Hold: chapters 15, 24, 25, 52. She is
  liked, she is never a villain, she is present at the beginning, and she has spent her
  whole life arguing that a Hold should stop saying its dead out loud. She told Grieve
  about Maren Verren and the doorstone twice, twenty years apart, in the same words. In
  chapter 52 she wins the scraping of the eleven waxed boards.

**Objects**
- **The doorstone.** Worn dip where Oda stood to watch the weather. Warmer than the stone
  around it since day 6, and still warm. Every Teller has checked, every Teller has
  recorded that they checked, and none has written down what they think.
- **The cup.** Maren's, on the table from breakfast on day 14, unmoved for five days
  because nothing in the Hold moved. Someone moved it on the night of day 19 and neither
  she nor Sila ever said which of them did.
- **The coulter's curve.** Ketil could not hammer it out, so the Ashblade comes off a
  downstroke a hair wider than it should. That hair killed the third Stalker on day 14.
- **The Widow's Maul.** Reforged from a post-driver in a day and a half. Head drawn down,
  striking face dished, set on the haft with a **wedge instead of a pin** so it can be
  reset in the field, which is the first piece of design in the Vale made because a person
  was expected to be out for days. Ketil also ground a **short edge into the trailing
  side** without asking and never explained it; it saved Maren twice and saves Grieve once
  on day 210. Named by eleven-year-old Bel Brack in the yard on day 16: *that is a widow's
  maul.* Maren let it stand and accounts differ on why. On the wall above the Hearth from
  day 140; the wedge has been reset nine times and you can count the seatings.
- **The Ashblade** hangs on a hook on the Smithy wall from day 19 to day 110, when Yeva
  Holt takes it down.

**Rules established in prose**
- A **Friend pays four in five** for any rite. Observed day 141, unexplained. This is why
  the Wake on day 210 cost forty-eight and not sixty.
- **Healers cannot be called at a Succession.** Standing law of the Hold from day 24,
  never once suspended.
- **Three names are always called** at a Succession, and a called name may be declined.
- *Took up the blade* is the verb on the board for all ten wielders including the two who
  never carried a sword.
- The **hillside line** recurs at every wielder's death. Rin: *the hillside was worth
  looking at.* Sable said it in Wrenfield when Wrenfield was Gone. Wren said it at the
  ninth ring on ground with nothing on it. Seven of eleven accounts of nine deaths contain
  it and four of those seven are certainly invention.
- The Grey Ash contains **nine old rings** mapped by Foragers and never entered, from
  failures that predate Bran Holt's counting, so there is no entry for any of them.
- Ashfall Hold's population: twenty-two working people in Part II, twenty-six by chapter
  24, thirty-one on day 209 of whom nine are children and four are the surviving Brackwood
  sick.

**Fixed by chapters 4, 5, 6, 19, 20 and 21**
- **The three motions were named in the Hearth on the evening of day 8** and the wording is
  fixed: *The loosing. That one is done. Nobody did it and nobody can undo it. / The
  holding. That is where we are. It is closed and it is nobody's. / The keeping. That is
  ours, and we have not done it.* The words are husbandry, not liturgy: you loose a beast
  off a tether, a holding is ground you have not settled, hay goes in the keeping.
  Attribution is permanently disputed. Sila Carver credits nobody: *we found the words in
  the night.* Ketil Brack credits himself. Sable Kettle credits Rin Ashfall. Bran Holt
  records only that they were said and were good words. Grieve has refused eleven requests
  to make the plural singular, four of them from Tellers who wanted the line clean for a
  Telling.
- **Nine days is the argued measure, three days is what happened.** Oda Ashfall fell on day
  6 and was Kept on day 9. Nine entered the room twice, through Ketil Brack's stray-beast
  proverb and through the Hearth being nine days old, and the Vale's standing measure of
  *too long* is nine. Grieve declines to say which gave the number its number.
- **Twenty and six.** Bran Holt's twenty was half-days of lost labour on six tally sticks
  and his six was the dusk count over his morning forecast, and he never wrote of what.
  Every hold in four valleys now says *twenty and six* and none of them mean half-days and
  hurdles.
- **Oda Ashfall's pane is the Memorial's permanent anomaly.** She was buried, so there is no
  pearl of hers, and her pane is cut into the sheet of glass she carried across two valleys
  herself out of a house that was not hers. The name is cut small in the top corner and the
  rest of the glass is left empty. It is the oldest pane in the valley and the only one with
  room left on it.
- **The step cut into the long sides of every grave in the Vale** is taught and never
  explained. There are two spoil heaps at the Memorial and nothing has ever grown on the
  northern one.
- **The Low Kettle cairn** stands eleven paces west of the Hearth door, older than the Hold,
  and the Memorial ground was founded beside it. The board has never counted it and none of
  the eighteen verbs fit it.
- **The pyre floor.** Four Carvers laid four flags in an afternoon on day 31 because the
  Hold's first Pyre had nowhere to happen. Every cake of soap, every pane and every flask in
  the book comes off those flags. Same-day keeping on the flags means no Holding, no ring
  and no purse, which is the ground the Cull's argument stands on.
- **Bel Brack** had six bonds (Ketil Brack, Maren Verren, Bran Holt, Rin Ashfall, Sila
  Carver, Yeva Holt), so grief 28. Pool 22 after the day-21 Telling, plus 28 is 50; the Pyre
  spends 30 and leaves 20.
- **Water starves an Echo.** An Echo feeds by drawing hold out of soil and there is no soil
  under a lake, so Bel Kettle sat at the second growth for forty years, never roamed, never
  came up the mere road, and her purse held only twenty-one against the forty-five that
  Rin's four-day ring in fed barley yielded. This is what makes the unsurveyed lake
  survivable rather than absurd. The dry summer is what made day 38 happen: the water
  dropped a hand and four paces of pale rim came ashore.
- **What came back out of the mere:** a kitchen knife and one shoe, the left one, a child's.
  The knife hung at the Hearth for a hundred and three days and Sable Kettle took it off the
  wall on day 141. That is the Hearth Knife's provenance. Bran Holt entered the shoe, and he
  is the only one of the four hands who would have.
- **The nine sick of Brackwood:** Oda Rowan, Sila Dunn, Rin Kettle, Tove Mourne, Ketil
  Stonewake, Nix Holt, Yeva Ember, Sable Vane, Colm Brack. Colm Brack is the one who can no
  longer hold a cup. Tove Mourne is Grieve's father's sister. The four Cull signers are
  Orrin Dunn, Tarn Stonewake, Yeva Holt and Nix Ember, and **every signer has kin on the
  list he signed.** That is the Cull's defence and it is a good one.

**Fixed by chapters 32 and 43**
- **A Wake takes sixty and then clears whatever remains.** Sixty is the price; the clearing
  is what it buys. So a Hold cannot Wake out of a shortage, and cannot afford a Wake until
  something has gone badly enough wrong to produce sixty. Two Wakes in the book: day 136
  (pool stood at 68, paid 60, the other 8 went with it) and day 210 (Grieve paid 48 as a
  Friend).
- **A Wake has no liturgy.** No cutting, no raising, no fire. The Hold and a cask in the
  yard, every name spoken once, oldest first. People stay out until light.
- **The palisade is stone for two thirds of its length and timber on the north-east arc
  above the mere road**, because Asha Vane was conscripted out of the Carvers' shed on day
  95 and the Hold's four Carvers became three. Relic set at the stone corners. Yeva Holt's
  Echo came over the timber on day 134 by driving the Ashblade into it twice at head height
  and using the blade as a step. No Husk, Stalker or Gravewarden has ever done that.
- **An Echo at the fifth growth walks a country out**, one decay state per region crossed.
  The map of Yeva Holt's four-day walk is cut into a board in the Hearth and is the reason
  the Hold understands decay at all. The low rows have never fully come back.
- **The ring by the mere gate.** Six paces of the Hold's own yard, greener than the rest,
  where Yeva Holt's Echo went down. Nobody mows it and nobody has said why not.
- **Orrin Dunn** has a shoulder that went wrong on day 109 and stayed wrong for life. He
  was Warden before he was wielder.
- **Asha Vane wrote nothing for six days**, days 130 to 136, and the board for that week was
  reconstructed from spear tallies and Forager maps, so three entries stand in the wrong
  order in the original and every hand since has left them wrong. Her reason: *a Teller
  writes down what happened, and for six days I was one of the things that was happening.*
- **Tarn Stonewake took the Widow's Maul off the wall on day 122**, which the Hold read as
  arrogance and which was the opposite. He said Yeva Holt's name correctly at her Wake,
  having never learned it when he took the blade from her.
- **The Foragers' nine rings** in the Grey Ash, and the eleven-pace Quick circle around the
  Wrenfield Monument in Gone ground, are both walked to and neither is talked about.

**Fixed by chapter 30 (Vane Hold). Chapter 44 must not contradict any of this.**
- **Vane Hold's board, exact and final: Memory +9 · Mercy -23 · Communion -44 · Dominion
  +51. Drifting toward: The Long Hold.** Dominion 51 is the highest figure in any copy.
  Memory 9 is the detail nobody expects: they were not an Unnaming hold, they kept cutting
  panes, and nine is a hold that was still trying.
- The wall: **stone all the way, four hundred paces straight, level courses, relic set at
  the corners, no seam you can feel.** Nobody now living could build it. A beam has failed
  inward at the north-east corner and that is the only way in.
- The gate is barred with **two arms' worth of timber in iron brackets set into the stone**,
  made for the purpose, by a smith, on a day when the gate was still being opened. The
  timber is scored; Grieve counted the marks on day 210 and there were a great many and they
  were all recent.
- **One hundred and sixteen Husks**, counted twice by Asha Vane, every one caught performing
  an ordinary duty: at the looms, in the doorways, one at a table with both hands flat on a
  bench worn to its shape, one at the well handle, two in the lane between byre and workshop
  three feet apart facing each other, eleven on the benches in the stone Hearth with a cask.
  No breach, no burning, no bones in the lanes.
- **No Echoes at Vane Hold at all.** Their four wielders died outside in thirty days and
  were left, and their rings are nowhere within a morning's walk. Four Vane Echoes have been
  roaming and drifting and feeding for a very long time. The illegible fourth growth that
  killed Orrin Dunn at Ashfall's palisade on day 196 may be one of them. Nobody claims it.
  Nobody in the Hold wants to discuss it twice.
- Their board's last legible dozen entries are `vigil_skipped` repeated with no deaths
  recorded between them.
- Asha Vane's line, now used in the Hold about all sorts of things: **they were not wrong,
  they were only finished.** Bran Holt's note on the copy: *the board does not lie. It also
  does not help.*
- Vane Hold's central and correct insight: **the decay comes from us being out in it.** They
  stopped going out. The ground east of their wall has not gone one state worse since. What
  they could not solve is that a Keeping costs grief, grief is only spent at a rite, a rite
  needs somebody to hold it, and their fields were outside the gate.
- Twelve family names exist and **eleven of them are on the wall at Vane Hold in some
  order**. Asha Vane is a Vane out of Brack, no relation, and is tired of being asked. Four
  of Grieve Mourne's own names are on that wall and nobody has ever asked him.
**Fixed by chapter 45 (Verren Hold, Ash Inheritance). Chapter 25's Other Roads must agree.**
- The motion to shave the panes oldest-first was **carried 71 to 44** on Verren's day 34, by
  a hold of a hundred and fifteen working people, at the end of a long evening, on a
  testable proposition. The losing forty-four stayed. It is not a cult and not a coup.
- **It worked, measurably, for sixty days.** Their day 46: a ring in the north rows opened
  by itself with nobody within two hundred paces, and the whole roll came out to look at
  grass. Nothing in Ashfall's Chronicle has ever done that. Their grief pool reached nothing
  on their day 61 with no Wake held for it, and their output ran full for two seasons, and
  for a stretch Verren Hold was the hold the Wayfarers walked to.
- **The bill, found by their second hand on their day 96:** six Legacies, all from before
  their day 34, because a Legacy comes only from a rite, a rite costs grief, and grief comes
  only from a death entered with a name and a count of bonds. After day 34 every successor
  started at a hundred of health, a hundred in the purse, three flasks and a blade.
- **Eight wielders in fifty-one days**, their days 139 to 190, every one of them left where
  they fell.
- **Sila Verren** was their wielder from their day 157, fell at the west ditch on their day
  163, was abandoned on their 165, left the valley by their 178, and is the drifted Echo
  Ashfall buried on Ashfall's day 70. Their third hand entered Ashfall's line on their day
  186 and wrote *I do not know what to do with it*, and noted that he had shaved the blank
  pane waiting for her himself on their day 55.
- **Their day 191 entry is one line: `Mem -41`.**
- From their day 210 the third and fourth hands are **the same fifth hand**, which is none of
  the four, and which is better than all four: same pressure, same breath, same line break
  at nine words, level lines, arithmetic correct on every leaf. From their day 203 the
  entries are signed **Kept by N. Verren**, and Nix Verren fell on their day 203, and the
  entry recording it is in the same hand as the signatures. Thirty-seven signed entries.
  Their day 240 is not the end of the leaf; there are four inches of clean vellum under it
  and the hand does not come back.
- Something at the second or third growth walks Verren's north rows, and the people still
  there call it by a name, and they call it **correctly**, and they are not frightened of it.
- Sila Grey has read the copy and returned it with one judgement: **they did it in the wrong
  order.** Scrape the boards, keep the book. They scraped the glass, which is the part a
  person walks past, and left every name on the board at eye height to be read aloud at the
  turn of every season. That is not unnaming.
- Grieve has read the copy nine times, the ninth after the Wake, as a man who had won the
  argument, and did not feel as though he had won the argument.

**Fixed by chapter 47 (the unsigned fragment, The Quiet Field).**
- Seven leaves, folded twice, used as packing to keep rain off the third part of the Verren
  copy. The rest of that hold's book was used the same way by other people.
- **Its Teller counted weather, not board-days.** Every entry is dated *second spring, ninth
  day*, *first frost, third day*, *barley down, fourth day*. This is why the hold cannot be
  placed: a board-day can be laid against any other valley's board-day, and a spring cannot.
  Grieve has laid the fragment against eleven boards and it touches none of them. Whoever
  kept it was writing for the people in the room.
- Eleven of its entries record that there was no entry. *Rain. Nothing entered.*
- Its people: Bel Rowan (wielder, forty-four, slow left hand, a hundred and forty board-days
  and eleven years by the weather), Oda Kettle (took the blade alive), Ketil Grey (fell at
  the east ditch, fifty-four, nine bonds, grief 37, reclaimed and given a Monument), Sila
  Grey (died in bed at seventy-one, six bonds, grief 28, buried with her spindle and the
  good knife, Telling given by Oda Kettle who sat with her, told wrong in one place and
  corrected and both put in), Bran Kettle (fell in the west rows, thirty-one, four bonds,
  grief 22, abandoned because the pool stood at twelve), Nix Grey (born, nine pounds, no
  verb, entered in words).
- **Bel Rowan declined her own name at the Succession and handed the blade to Oda Kettle in
  the yard with everybody there, and nobody died.** There is no verb for it. Their Teller
  entered a Succession, the nearest thing the board has, and wrote that it is not the same
  and that whoever reads this should know it is not the same.
- **Their fifth line appears in the hand, mid-leaf, four days later, in an ordinary week**,
  in the same letters and depth and breath as the lambing entry above it. Either the Teller
  went in and read the board while everybody was alive and nothing was resolved, or they
  wrote it because it was true and the board agreed afterwards. Untestable.
- The arithmetic that makes this the saddest ending: a Burial costs twenty, Bran Kettle was
  worth twenty-two, and the pool stood at twelve because they had spent everything on Ketil
  Grey's Monument and relic a season earlier. **They had the will and not the grief. Ashfall
  on day 128 had the grief and not the will. Both boards move identically.**
- Grieve copied all seven leaves into the Chronicle in full on **leaf seventy**, with the
  tear, the fold and the missing top third marked, so that the hold exists in two places
  instead of one. He calls it the nearest thing to a Keeping a Teller can perform on
  strangers, and the appendix carries the list of rites he tried and failed.

- The Wayfarers proposed a **road-shrine** at Vane Hold on day 101. Colm Grey refused it
  because the Hold had three Carvers and a wall to finish. Chapter 48 builds it in a
  different ending.
