# PROSE CONTRACT

Binding on every chapter and appendix of *The Ashfall Chronicle*.

## 1. Register

The base voice is **saga-laconic**. Objective narration. Character revealed through
action and speech, never through explained interiority. Minimal authorial intrusion.
Violence described flatly and briefly, with no rise in temperature: the flatness is the
effect. The model sentence at the height of a death is not a scream, it is an
observation about the weather or the ground.

> He looked at the slope above the fence and said the grass was worth cutting. Then he
> went down on one knee and did not get up.

Three registers are permitted, and no others.

**Saga.** Default. Short declaratives. Load-bearing dialogue, sparse, unquoted where it
reads better as reported speech. Genealogy stated as structure, not decoration:
*Orrin Dunn, who was Ketil Dunn's son, who had the eastern furlong off Bran Holt.*

**Elegiac.** For ruins, for the Ashlands, for the Vane Road, for anything about time.
Longer lines, catalogue and repetition, the *where has it gone* figure, the work of
giants figure. Use sparingly. Two or three passages a chapter at most, and never in a
chapter that also has a fight.

**Clerical.** For the Ledger blocks, the appendices, the board, the panes, the rite
liturgies, and any quoted document. Flat, numbered, exact. This is the only place
numbers are allowed.

## 2. Hard rules

- **No em-dashes.** Not in prose, not in dialogue, not in the appendices. Use commas,
  colons, semicolons, full stops, and paragraph breaks.
- **No mechanics named as mechanics** in narration. Never *stat, hit points, stamina bar,
  cooldown, invulnerability, respawn, run, build, player, level up, XP, buff, debuff,
  i-frames, tick, roll RNG*. Write bodies, ground, weather, tools, arithmetic the
  villagers themselves would do.
- **Permitted in-world vocabulary:** hold, the Loosing, the Holding, the Keeping, Echo,
  Husk, Vigil, Legacy, grief, Composure, poise, the board, the panes, the Chronicle, the
  Readings, drawn-ash, fall-ash, locked ground, pearl, lye, relic, drift, tell.
- **Composure and poise are said out loud** by Wardens, as trade words, the way a
  carpenter says plumb. Everything else stays implicit.
- **Numbers only in clerical passages.** A Warden may say *three flasks* or *twelve
  hundredths*, because those are trade facts. The narrator never says *plus eight
  Memory* outside a Ledger block.
- **No modern idiom.** No *okay, fine, look, honestly, sure, I guess, sort of, kind of,
  basically*.
- **No gods, prophecy, chosen one, magic system, cure, or outside rescue.**
- **No faction is evil.** If a reader finishes a chapter certain that one side is
  correct, the chapter is a draft.
- **Never resolve a contradiction between two accounts.** Where sources differ, write
  both and move on. The formula is available and should be used two or three times a
  chapter in Grieve's compiling voice: *Bran's hand says the gate was open. Asha wrote
  over it that it was not. I record what was said.*
- **Do not explain hold.** By chapter fifteen a reader should understand the whole
  metaphysics and never have been told it in one place.
- **Do not foreshadow with authorial nudges.** No *little did they know*. The Chronicle
  is written after the fact by someone who refuses to arbitrate, so it can state a later
  fact flatly and early, saga-fashion: *He had four days left.* That is permitted and
  encouraged. Coyness is not.

## 3. Chapter file format

Exact. Copy it.

```markdown
# Chapter <N>: <Title>

> *<epigraph, one to three lines>*
> Recorded: <in-world attribution: a pane, a board, a hand, a Wayfarer's copy>

**Hand:** <Sila Carver | Bran Holt | Asha Vane | Grieve Mourne, compiling>
**Days:** <n> to <n>
**Place:** <region>

<prose. 2,800 to 4,200 words. Break sections with a line containing only:>

·  ·  ·

<continue>

---

## The Other Roads

<Part IV side-road chapters only. Two to four branch variants. Each variant: a short
titled passage of 150 to 350 words in the Teller's compiling voice reporting how the
same road went in another valley, or how it nearly went here, followed by that branch's
exact ledger movement and the ending it pushes toward. Format:>

### <Branch name>
<passage>

`<verb>` <subject> · Memory <+/-n> · Mercy <+/-n> · Communion <+/-n> · Dominion <+/-n>
**Pressure:** <which ending this road bends toward, and why>

---

## Ledger

<one block per entry assigned to this chapter, from LEDGER.md, exactly>

```
Day <n> · <verb> · <subject>
"<the line the Teller wrote>"
Memory <+/-n>   Mercy <+/-n>   Communion <+/-n>   Dominion <+/-n>
```

**Standing:** Memory <+n> · Mercy <+n> · Communion <+n> · Dominion <+n>
**Drifting toward:** <ending>
```

## 4. Length

2,800 to 4,200 words of prose per chapter, not counting the Ledger and Other Roads
blocks. Appendices 1,500 to 3,000 words. Keep every file under 800 lines.

## 5. Continuity duties

- Read `CANON.md` and `LEDGER.md` before writing a word. They outrank your brief.
- Use only the eighteen given names and twelve family names in `CANON.md` section 9.
- Never contradict the numbers in `CANON.md` sections 6, 7, 8, 9 or `LEDGER.md`.
- Your chapter's Ledger block must match `LEDGER.md` rows exactly, including drift.
- If your brief and `CANON.md` disagree, `CANON.md` wins, and mention the conflict in
  your completion report.
- Plant at least one physical object, sentence, or habit that a later chapter can pick
  up. Name it plainly. Do not explain it.
