# Web IDE (`web/index.html`)

The full Brimstone experience in a browser: gauges, pillars, and all five
hazards are always live — no toggles, exactly like the terminal IDE. The
interface is plain two-color, VS Code-like, and entirely text-driven except
the **Save** and **Load** buttons.

## Running it

Open `web/index.html` in any modern browser. No build step, no install.

```sh
# any static server works; so does double-clicking the file
python3 -m http.server -d web 8666
# then visit http://localhost:8666
```

**Internet required for execution:** code runs on real Python via
[Pyodide](https://pyodide.org) (Python compiled to WebAssembly), loaded
lazily from a CDN the first time you `func compile`. Editing, saving, and
loading work fully offline.

## Layout (top to bottom)

1. **Gauge header** — `TEMP [#####.....] 50%   RISK [..........] 0%`,
   updated in real time, plus `[FROZEN]` / `[BLAZING]` tags.
2. **Top bar** — filename box and the only two buttons: **Save** and
   **Load**. Everything else is typed.
3. **ASCII flame rows** — appear above and below the editor when
   temperature exceeds 75%.
4. **Editor** — line-numbered, autosaves to localStorage on every keystroke.
5. **Output panel** — translated Python and program output
   (`[COMPILE OK]` / `[DAMNATION]`). `demand()` prompts in a dialog.
6. **Status line** — what the IDE thinks of you right now.

## Commands

Type a command as a line and press Enter. Commands are intercepted — they
never enter your file and never trigger hazards.

| Command | Effect |
|---------|--------|
| `func compile` | Translate to Python and run it |
| `func holywater tg: fire` | Temperature −40% |
| `func coal` | Temperature +40% — the ONLY input accepted while `[FROZEN]` |
| `func shield` | Survive a solar flare (3-second window) |
| `func exorcise tg: ghost` | Revert all ghost commits |
| `func pythonize` | Convert the buffer Brimstone → Python (filename → `.py`) |
| `func brimstonify` | Convert the buffer Python → Brimstone (filename → `.bs`) |
| `func theme tg: dark` / `func theme tg: light` | Switch theme |
| `func help` | List all commands in the output panel |

## The converter

`func pythonize` and `func brimstonify` transmute the whole buffer in
place, in either direction, and adjust the filename extension so **Save**
exports the right file type. Typical flows:

- **Export to Python:** write Brimstone → `func pythonize` → Save → you
  have a runnable `.py`.
- **Import from Python:** Load a `.py` file → `func brimstonify` → you are
  now editing Brimstone.

The two translators are exact inverses, so round-trips are lossless.

## Autocomplete

VS Code-style suggestions appear as you type: keywords (`manifest`,
`suffer`, `atone`...), snippets, and — when a line starts with `func` —
full command completions. Navigate with ↑/↓, accept with Tab or Enter,
dismiss with Escape. Use it: misspelled keywords are a hazard (see below).

## The hazards (all active, always)

Everything from the [Hazard Registry](Hazard-Registry.md) applies. "The
file" means the editor buffer plus its localStorage autosave; death
consumes both. Files downloaded via **Save** are beyond the demons' reach.

- **Temperature / Instability** gauges tick per committed line, with
  ASCII flame borders past 75%, buffer-burn at 100%, and a `[FROZEN]`
  input lock below 10% (only `func coal` is typeable).
- **Load-bearing pillars** anchor one random character per committed line.
  The editor diffs every edit you make: deleting or overwriting an
  anchored character collapses the file instantly, no warning. Insertions
  and edits elsewhere shift the anchors fairly.
- **The Memory Demon** (1-in-15 per line): full-screen quote for exactly
  5 seconds, then a visible 30-second countdown to retype it perfectly.
- **Typo Ransomware:** misspell a keyword (edit distance 1) and the editor
  locks behind a 50-character ransom string; each typo while paying
  silently deletes 5 random lines.
- **Solar Flares** (random): 3 seconds to type `func shield`, or the
  display scrambles for 30 seconds while the buffer underneath stays
  intact.
- **Ghost Commits:** every 60 seconds, one conditional operator silently
  inverts. No notification, ever. `func exorcise tg: ghost` is the cure.
- **The Lactose Intolerant Compiler:** `copy`, `paste`, `loop`, `while`,
  duplicate lines — and actual clipboard pastes — feed the hidden Dairy
  Meter. At 100% your work is force-downloaded as `.spoiled` and the IDE
  crashes.

Dying clears the buffer and autosave, then offers rebirth with reset
gauges. Save to disk early and often.
