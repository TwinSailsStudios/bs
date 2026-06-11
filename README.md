# Brimstone (.bs)

A chaotic esoteric programming language and its hostile terminal IDE.
The compiler is angry, the file is flammable, and one of your characters
is load-bearing.

📖 **Full documentation lives in the [wiki](wiki/Home.md)** — language
reference, hazard registry, survival guide, and manuals for both IDEs.

## Web IDE (no terminal required)

Open [`web/index.html`](web/index.html) in a browser: a hell-themed editor
with one-click compile (real Python via Pyodide/WebAssembly), save/load of
`.bs` files, localStorage autosave, and an opt-in **Damnation Mode** that
ports the gauges and hazards to the browser. See the
[Web IDE manual](wiki/Web-IDE.md).

## Terminal IDE

```sh
python3 brimstone.py [yourfile.bs]   # defaults to inferno.bs
python3 brimstone.py --selftest      # non-interactive translator check
```

Requires Python 3 with `curses` (standard on Linux/macOS). All destructive
mechanics only ever touch the single `.bs` workspace file the IDE creates.

## The language

| Brimstone            | Python            |
|----------------------|-------------------|
| `manifest()`         | `print()`         |
| `demand()`           | `input()`         |
| `summon`             | `import`          |
| `rite`               | `def`             |
| `suffer x in y:`     | `for x in y:`     |
| `suffer cond:`       | `while cond:`     |
| `PURE` / `CORRUPT`   | `True` / `False`  |
| `sin` / `atone`      | `try` / `except`  |

## Survival commands

| Incantation               | Effect                                      |
|---------------------------|---------------------------------------------|
| `func holywater tg: fire` | −40% temperature                            |
| `func coal`               | +40% temperature (only input while FROZEN)  |
| `func shield`             | survive a solar flare (3-second window)     |
| `func exorcise tg: ghost` | revert all ghost commits                    |
| `func compile`            | translate to Python and `exec()` it         |
| `func quit`               | leave with your file intact                 |

## What is trying to kill you

- **Temperature** starts at 50%, +5% per line. Over 75% the borders catch
  fire; at 100% the file burns. Under 10% you are frozen solid.
- **Instability** starts at 0%, +2% per line. Every commit rolls a d100
  against it. A demon face means it rolled low.
- **Load-bearing pillars**: every commit secretly anchors one character.
  Delete or change an anchored character and the file collapses. No warning.
- **The Memory Demon** (1-in-15 per line): memorize a quote in 5 seconds,
  reproduce it perfectly within 30, or lose the file.
- **Typo Ransomware**: misspell a keyword and the editor locks behind a
  50-character ransom string. A typo while paying costs 5 random lines.
- **Solar Flares**: 3 seconds to type `func shield` or spend 30 seconds
  coding blind through scrambled display output.
- **Ghost Commits**: every 60 seconds a ghost silently inverts one
  conditional operator in your code. You will not be told.
- **The Lactose Intolerant Compiler**: `copy`, `paste`, `loop`, `while`,
  or duplicate lines fill a hidden Dairy Meter. At 100% your `.bs` file
  curdles into `.spoiled` and the IDE crashes.
