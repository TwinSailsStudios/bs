# Terminal IDE (`brimstone.py`)

The original, fully hostile Brimstone environment. Built on Python's
`curses` with a single-threaded, non-blocking event loop: hazard timers tick
between keystrokes, so ghosts and flares arrive while you type.

## Requirements

- Python 3 with the `curses` module (standard on Linux and macOS; on
  Windows, use WSL or `pip install windows-curses`).
- A terminal of reasonable size. The flames need room.

## Running

```sh
python3 brimstone.py             # edits inferno.bs
python3 brimstone.py myfile.bs   # edits a file of your choosing
python3 brimstone.py --selftest  # non-interactive translator check
```

> ⚠️ The IDE creates and owns one workspace file. Every destructive
> mechanic — burning, demonic deletion, spoilage — targets **only that
> file**. Nothing else on disk is ever touched. Still: don't point it at a
> file you love.

## The screen

```
 BRIMSTONE IDE v6.66 — inferno.bs
 TEMP [#####.....]  55%   RISK [#.........]   8%
 ---------------------------------------------------
   1   summon math
   2   rite hello():
   3 >     manifest("...")            ← line being typed
 Welcome to BRIMSTONE. Type code. Press Enter. Pray.   ← status line
```

When temperature exceeds 75%, the horizontal rule and side borders are
replaced by animated procedural flames.

## Editing model

- Type; press **Enter** to commit the line. Commits trigger the entire
  hazard gauntlet (see [Hazard Registry](Hazard-Registry.md)).
- **Backspace** edits the current line freely. Backspacing at column 0
  *un-commits* the previous line for editing — this is the only way to fix
  old code, and it is exactly how pillars get broken.
- The file is saved to disk after every commit, so a crash (yours or the
  IDE's, deliberate or otherwise) loses at most the line in progress.
- **`func quit`** (or Ctrl-C) exits cleanly and reports how many lines
  escaped with you.

## Compiling

`func compile` suspends the UI, prints the translated Python, executes it
with `exec()`, shows `[COMPILE OK]` or `[DAMNATION] <error>`, and returns
you to the editor with all gauges intact. Compiling does not reset anything.
