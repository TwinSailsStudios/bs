# Web IDE — The Web Inferno (`web/index.html`)

A browser-based Brimstone environment: write, run, save, and load `.bs`
files with no terminal anywhere in sight. Fully hell-themed — molten
gauges, flickering title, flame borders when you run hot.

## Running it

Open `web/index.html` in any modern browser. No build step, no install.

```sh
# any static server works; so does double-clicking the file
python3 -m http.server -d web 8666
# then visit http://localhost:8666
```

**Internet required for execution:** code runs on real Python via
[Pyodide](https://pyodide.org) (Python compiled to WebAssembly), loaded
lazily from a CDN the first time you press **func compile**. Editing,
saving, and loading work fully offline.

## The interface

| Control | What it does |
|---------|--------------|
| **🔥 func compile** | Translate to Python, show the translation, execute it |
| **Save .bs** | Download the buffer as a `.bs` file (name from the filename box) |
| **Load .bs** | Open a `.bs` (or `.spoiled`) file from disk into the editor |
| **New** | Clear the buffer (asks first) |
| **DAMNATION MODE** | Toggle the hazard engine on/off |

- The right panel shows the **translated Python** on top and the
  **Hellmouth output** (stdout/stderr, `[COMPILE OK]` / `[DAMNATION]`)
  below.
- `demand()` pops a browser prompt for input.
- The buffer **autosaves to localStorage** on every keystroke and is
  restored when you return. Downloaded `.bs` files are the durable copy —
  Damnation Mode deaths consume the autosave.

## Damnation Mode

Off by default: the Web Inferno is, by default, merely ominous. Flip the
toggle and the gauges appear, and every Enter key commits a line against
the hazard engine:

- **Temperature / Instability** gauges, with flame borders past 75%,
  buffer-burn at 100%, and `[FROZEN]` input lockout below 10%. Holy Water,
  Coal, and Exorcise are buttons on the gauge bar.
- **Ghost commits** run on the 60-second background timer, silently
  flipping one conditional operator. The **✟ Exorcise** button reverts them.
- **Solar flares** open a full-screen QTE: type `func shield` within 3
  seconds or spend 30 seconds with the editor display scrambled (the buffer
  underneath is untouched).
- **The Dairy Meter** is hidden, as is tradition. At 100% your work is
  force-downloaded as `.spoiled` and the buffer curdles.
- Death clears the buffer **and** the localStorage autosave, then offers
  rebirth with reset gauges. Files you previously saved to disk are beyond
  the demon's reach.

Differences from the terminal IDE: load-bearing pillars, the Memory Demon,
and typo ransomware are not enforced in the browser — free-form mouse
editing makes "one character at a fixed index" meaningless. The wiki
considers the web heretics softened, but tolerated.
