# Hazard Registry

Everything in this document is trying to destroy your file. Hazards apply
fully in the Terminal IDE; in the Web IDE they apply only when
**Damnation Mode** is enabled, and "the file" means the editor buffer plus
its autosave.

## The Gauges

### 🔥 Temperature — starts at 50%

- **+5%** per committed line.
- **Over 75%:** procedural flames render on the editor borders. Cosmetic.
  For now.
- **100%:** the file burns. Buffer destroyed, session over.
- **Under 10%:** `[FROZEN]`. All typing is blocked; the only accepted input
  is `func coal`.
- Remedies: `func holywater tg: fire` (−40%), `func coal` (+40%).

Temperature management is the core economy: every line heats you, holy
water cools you, and over-cooling freezes you. The stable strategy is one
holy water roughly every eight lines — but see Instability.

### 🎲 Instability Risk — starts at 0%

- **+2%** per committed line, no remedy, no ceiling below 100.
- Every commit rolls 1d100 against the current risk. Roll under it and the
  file self-deletes behind an ASCII demon face.

Instability is the doom clock: by line 25 you carry a 50% risk *per line*.
Brimstone programs are short out of necessity, not style.

## 🏛️ The Load-Bearing Pillars (hidden)

Every committed line silently anchors **one random character** of the file
as load-bearing. Deleting or changing an anchored character instantly
collapses the file. There is no warning, no indicator, and no list of
anchored positions.

Practical consequences:

- Appending new lines is always safe — pillars live in already-committed text.
- Editing or deleting *previous* lines (backspacing past the start of the
  current line in the terminal IDE) is Russian roulette with roughly one
  bullet per line you've written.
- Ghost commits and ransomware penalties are *system* edits; they re-anchor
  pillars rather than triggering them. Only your hand can break a pillar.

## The Five Hazards

### Hazard A — The Memory Demon (1-in-15 per line)

The IDE pauses. A quote appears for **exactly 5 seconds**, then vanishes. A
visible **30-second** countdown begins; you must reproduce the quote
perfectly, including punctuation. Failure or timeout deletes the file.

### Hazard B — Typo Ransomware

Misspelling any Brimstone keyword (edit distance 1 — `manifst`, `sufer`,
`atome`...) locks the editor behind a **50-character random alphanumeric
ransom string**. You must retype it exactly. Each typo *during* the ransom
silently deletes **5 random lines** of your code, and the lock remains until
you pay in full.

### Hazard C — Solar Flare (random, ~1-in-20 per line)

`[WARNING: SOLAR FLARE DETECTED]` flashes; you have **3 seconds** to type
`func shield`. Failure scrambles every character on screen into random
symbols for **30 seconds**. The underlying buffer is untouched — you simply
cannot read it. Touch-typists prosper.

### Hazard D — Ghost Commits (every 60 seconds)

A background timer silently inverts one conditional operator in your code:
`==`↔`!=`, `<=`↔`>=`, `<`↔`>`. **No notification is given, ever.** The only
remedy is noticing your logic has gone wrong and casting
`func exorcise tg: ghost`, which reverts all hauntings.

### Hazard E — The Lactose Intolerant Compiler

The words `copy`, `paste`, `loop`, `while`, or any **exact duplicate line**
feed a hidden Dairy Meter (+25% per offense). At 100% the IDE crashes and
your output file curdles from `.bs` to `.spoiled`.

## Hazard interaction notes

- Hazards roll in a fixed order per commit: burn check → instability roll →
  pillar anchoring → dairy → ransomware → memory demon → solar flare. A
  sufficiently cursed line can chain several.
- Ransomware line-deletion can remove a ghost-haunted line; exorcism then
  restores only lines that still exist.
- The Memory Demon can interrupt a flare scramble. The countdown is still
  visible. The quote you must retype is not. Good luck.
