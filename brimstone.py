#!/usr/bin/env python3
"""
=============================================================================
  BRIMSTONE IDE v6.66  —  "The compiler is angry and it knows where you live"
=============================================================================

A terminal-based IDE + runtime for the chaotic esoteric language Brimstone
(.bs).  Built on `curses` with a single-threaded, non-blocking event loop:
all "background" hazards (ghost commits, solar flares, QTE countdowns) are
driven by monotonic-clock deadlines polled every frame, so the editor stays
responsive while chaos accumulates.

SAFETY CONTRACT: every destructive mechanic in this game (burning, demonic
deletion, spoilage) operates ONLY on the single workspace file that this
IDE itself creates (default: inferno.bs).  Nothing else on disk is ever
touched, renamed, or deleted.

Usage:
    python3 brimstone.py [yourfile.bs]
    python3 brimstone.py --selftest      # non-interactive translator check

In-editor commands (typed as a line, then Enter):
    func holywater tg: fire     -40% temperature
    func coal                   +40% temperature (ONLY input allowed frozen)
    func shield                 survive a solar flare (3s window)
    func exorcise tg: ghost     undo all ghost commits
    func compile                translate to Python and exec() it
    func quit                   leave with your soul (and file) intact
=============================================================================
"""

import curses
import os
import random
import re
import string
import sys
import time

# ---------------------------------------------------------------------------
# 1. CORE SYNTAX — the Brimstone -> Python translation layer
# ---------------------------------------------------------------------------

# Word-boundary keyword map.  `suffer` is context-sensitive (see translate()).
KEYWORD_MAP = {
    "manifest": "print",
    "demand":   "input",
    "summon":   "import",
    "rite":     "def",
    "PURE":     "True",
    "CORRUPT":  "False",
    "sin":      "try",
    "atone":    "except",
}

# Full keyword set, used by the typo-ransomware detector (Hazard B).
ALL_KEYWORDS = set(KEYWORD_MAP) | {"suffer"}

# Hazard E trigger words.  Note `while` is contraband: `suffer` is the only
# blessed loop construct.  (`suffer` itself is translated, so it never trips.)
DAIRY_WORDS = {"copy", "paste", "loop", "while"}

def translate(source: str) -> str:
    """Translate Brimstone source into executable Python.

    `suffer X in Y:` becomes a for-loop; any other `suffer` is a while-loop.
    Everything else is a word-boundary substitution from KEYWORD_MAP.
    """
    out_lines = []
    for line in source.split("\n"):
        # Context-sensitive loop keyword first.
        if re.search(r"\bsuffer\b.*\bin\b", line):
            line = re.sub(r"\bsuffer\b", "for", line)
        else:
            line = re.sub(r"\bsuffer\b", "while", line)
        for bs_word, py_word in KEYWORD_MAP.items():
            line = re.sub(r"\b%s\b" % bs_word, py_word, line)
        out_lines.append(line)
    return "\n".join(out_lines)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein distance — powers the typo detector for Hazard B."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# ---------------------------------------------------------------------------
# ASCII art for the various ways you die
# ---------------------------------------------------------------------------

DEMON_FACE = r"""
        ,           ,
       /             \
      ((__-^^-,-^^-__))
       `-_---' `---_-'
        `--|o` 'o|--'
           \  `  /
            ): :(
            :o_o:
             "-"
   THE INSTABILITY CLAIMS YOUR FILE.
"""

FIRE_DEATH = r"""
      (  .      )
   )           (    )
         .  '   .   '  .
  (    , )       (.   )  (   ',
   .' ) ( . )    ,  ( ,     )
 ). , ( .   (  ) ( , ')  .' (  ,
(_,) . ), ) _) _,')  (, ) '. )
   100% TEMPERATURE. THE FILE BURNS.
"""

PILLAR_DEATH = r"""
      _____________________
     ||                   ||
     ||   ===========     ||
     ||    |  | |  |      ||
     ||    |  | |  |      ||
     ||    |  | |__|  <-- ||
     ||    |__|  CRACK    ||
   __||___________________||__
   YOU STRUCK A LOAD-BEARING
   CHARACTER. THE FILE COLLAPSES.
"""

DEMON_QUOTE_DEATH = r"""
        (\_/)
        (o.o)   "You forgot My words."
        (> <)
   THE MEMORY DEMON EATS YOUR FILE.
"""

SPOILED_ART = r"""
       ______
      |      |     ~ glug ~
      | MILK |   The compiler curdles.
      | 2014 |
      |______|
   DAIRY METER: 100%. IDE CRASHED.
"""

MEMORY_DEMON_QUOTES = [
    "The semicolon is a leash for thoughts too wild to end.",
    "Every bug is a confession written in someone else's blood.",
    "I do not sleep. I garbage collect.",
    "Hell is other people's code reviews.",
    "The stack grows downward, like all things that fall.",
    "To suffer is to loop. To loop is to live.",
    "There are no warnings in Brimstone, only consequences.",
    "Your variables are named after things you have lost.",
]


# ---------------------------------------------------------------------------
# 2. The IDE engine
# ---------------------------------------------------------------------------

class FileDeleted(Exception):
    """Raised when a hazard kills the workspace file. Carries death art."""
    def __init__(self, art, reason):
        super().__init__(reason)
        self.art = art
        self.reason = reason


class BrimstoneIDE:
    # Hazard tuning knobs (all odds are per line-commit unless noted).
    MEMORY_DEMON_ODDS = 15      # Hazard A: 1-in-15
    SOLAR_FLARE_ODDS = 20       # Hazard C: 1-in-20 per commit
    GHOST_INTERVAL = 60.0       # Hazard D: seconds between hauntings
    DAIRY_PER_OFFENSE = 25      # Hazard E: meter gain per dairy crime
    SCRAMBLE_SECONDS = 30.0     # Hazard C: blind-coding penalty duration
    FRAME_MS = 50               # input poll interval (keeps timers ticking)

    def __init__(self, stdscr, filepath):
        self.scr = stdscr
        self.filepath = filepath          # the ONLY file we ever touch
        self.lines = []                   # committed lines
        self.cur = ""                     # the line being typed
        self.temperature = 50.0           # gauge 2: starts at 50%
        self.instability = 0.0            # gauge 2: starts at 0%
        self.dairy = 0                    # Hazard E: hidden meter
        self.pillars = []                 # gauge 3: list of (index, char)
        self.ghost_debts = []             # Hazard D: [(line_idx, original)]
        self.next_ghost = time.monotonic() + self.GHOST_INTERVAL
        self.scramble_until = 0.0         # Hazard C: blind mode deadline
        self.status = "Welcome to BRIMSTONE. Type code. Press Enter. Pray."
        self.rng = random.Random()

        curses.curs_set(1)
        self.scr.timeout(self.FRAME_MS)   # non-blocking getch -> event loop
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)      # flames / danger
            curses.init_pair(2, curses.COLOR_CYAN, -1)     # frozen
            curses.init_pair(3, curses.COLOR_YELLOW, -1)   # warnings
            curses.init_pair(4, curses.COLOR_GREEN, -1)    # ok

    # ----- document helpers -------------------------------------------------

    def full_text(self) -> str:
        """Whole buffer: committed lines + the line in progress."""
        return "\n".join(self.lines + [self.cur])

    def save(self):
        """Persist committed lines to the workspace file."""
        with open(self.filepath, "w") as f:
            f.write("\n".join(self.lines))

    def delete_workspace_file(self):
        """The big red button. Only ever removes our own workspace file."""
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
        except OSError:
            pass

    # ----- 3. LOAD-BEARING PILLARS ------------------------------------------

    def add_pillar(self):
        """On each commit: anchor one random character. Touch it and die."""
        text = self.full_text()
        if text:
            idx = self.rng.randrange(len(text))
            self.pillars.append((idx, text[idx]))

    def check_pillars(self):
        """USER edits run this: any moved/deleted pillar char = instant death."""
        text = self.full_text()
        for idx, ch in self.pillars:
            if idx >= len(text) or text[idx] != ch:
                self.delete_workspace_file()
                raise FileDeleted(PILLAR_DEATH, "Structural failure.")

    def prune_pillars(self):
        """SYSTEM edits (ghosts, ransomware) re-anchor instead of killing:
        the spec punishes only *the user's* hand on the pillars."""
        text = self.full_text()
        self.pillars = [(i, c) for i, c in self.pillars
                        if i < len(text) and text[i] == c]

    # ----- rendering ---------------------------------------------------------

    def safe_add(self, y, x, s, attr=0):
        """addstr that never crashes on the bottom-right cell / small terms."""
        h, w = self.scr.getmaxyx()
        if 0 <= y < h and x < w:
            try:
                self.scr.addstr(y, x, s[: max(0, w - x - 1)], attr)
            except curses.error:
                pass

    def gauge_bar(self, pct, width=10):
        filled = int(round(pct / 100.0 * width))
        return "[" + "#" * filled + "." * (width - filled) + "]"

    def draw(self):
        self.scr.erase()
        h, w = self.scr.getmaxyx()
        now = time.monotonic()
        scrambled = now < self.scramble_until
        frozen = self.temperature < 10

        # --- header gauges ---
        temp_attr = curses.color_pair(1) if self.temperature > 75 else (
            curses.color_pair(2) if frozen else 0)
        self.safe_add(0, 1, "BRIMSTONE IDE v6.66 — %s" % os.path.basename(
            self.filepath), curses.A_BOLD)
        self.safe_add(1, 1, "TEMP %s %3d%%" % (
            self.gauge_bar(self.temperature), int(self.temperature)), temp_attr)
        self.safe_add(1, 25, "RISK %s %3d%%" % (
            self.gauge_bar(self.instability), int(self.instability)),
            curses.color_pair(3) if self.instability > 30 else 0)
        if frozen:
            self.safe_add(1, 50, "[FROZEN — only `func coal` works]",
                          curses.color_pair(2) | curses.A_BOLD)
        elif self.temperature > 75:
            self.safe_add(1, 50, "[BLAZING]", curses.color_pair(1) | curses.A_BOLD)

        # --- procedural ASCII flames on the borders when temp > 75 ---
        if self.temperature > 75:
            flame_chars = ")(/\\^*'`."
            for x in range(0, w - 1, 2):
                self.safe_add(2, x, self.rng.choice(flame_chars), curses.color_pair(1))
                self.safe_add(h - 2, x, self.rng.choice(flame_chars), curses.color_pair(1))
            for y in range(2, h - 1):
                self.safe_add(y, 0, self.rng.choice(flame_chars), curses.color_pair(1))
                self.safe_add(y, w - 2, self.rng.choice(flame_chars), curses.color_pair(1))
        else:
            self.safe_add(2, 0, "-" * (w - 1))

        # --- editor body (solar-flare scramble only affects the DISPLAY) ---
        body_top = 3
        body_height = h - body_top - 2
        visible = (self.lines + [self.cur])[-body_height:]
        first_no = len(self.lines) + 1 - len(visible) + 1
        for row, line in enumerate(visible):
            shown = line
            if scrambled:
                shown = "".join(self.rng.choice(string.punctuation + string.ascii_letters)
                                if c != " " else " " for c in line)
            prompt = ">" if row == len(visible) - 1 else " "
            self.safe_add(body_top + row, 2, "%3d %s %s" % (first_no + row, prompt, shown))

        # --- status line ---
        if scrambled:
            self.safe_add(h - 1, 1, "[SOLAR INTERFERENCE: %ds] " % int(
                self.scramble_until - now) + self.status, curses.color_pair(3))
        else:
            self.safe_add(h - 1, 1, self.status)

        # park the cursor at the end of the current line
        cy = body_top + len(visible) - 1
        cx = min(w - 2, 8 + len(self.cur))
        try:
            self.scr.move(cy, cx)
        except curses.error:
            pass
        self.scr.refresh()

    # ----- modal helpers (QTEs pause editing but keep their own clocks) -----

    def modal_message(self, text_lines, seconds):
        """Show a full-screen message for an exact duration, ignoring input."""
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.scr.erase()
            h, w = self.scr.getmaxyx()
            for i, ln in enumerate(text_lines):
                self.safe_add(h // 2 - len(text_lines) // 2 + i,
                              max(0, (w - len(ln)) // 2), ln, curses.A_BOLD)
            self.scr.refresh()
            self.scr.getch()  # drain input; timeout keeps this non-blocking
        curses.flushinp()

    def timed_line_input(self, prompt_lines, deadline, secret=False,
                         on_keystroke=None):
        """Read a line with a live countdown. Returns the string, or None on
        timeout.  `on_keystroke(typed)` lets Hazard B punish mid-string typos."""
        typed = ""
        while True:
            now = time.monotonic()
            remaining = deadline - now
            if remaining <= 0:
                return None
            self.scr.erase()
            h, w = self.scr.getmaxyx()
            self.safe_add(0, 1, "TIME REMAINING: %4.1fs" % remaining,
                          curses.color_pair(1) | curses.A_BOLD)
            for i, ln in enumerate(prompt_lines):
                self.safe_add(2 + i, 2, ln, curses.A_BOLD)
            self.safe_add(4 + len(prompt_lines), 2, "> " + typed)
            self.scr.refresh()
            ch = self.scr.getch()
            if ch in (curses.KEY_ENTER, 10, 13):
                return typed
            if ch in (curses.KEY_BACKSPACE, 127, 8):
                typed = typed[:-1]
            elif 32 <= ch <= 126:
                typed += chr(ch)
                if on_keystroke:
                    on_keystroke(typed)

    # ----- HAZARD A: The Memory Demon ----------------------------------------

    def hazard_memory_demon(self):
        quote = self.rng.choice(MEMORY_DEMON_QUOTES)
        self.modal_message(["A MEMORY DEMON RISES FROM THE HEAP", "",
                            '"%s"' % quote, "",
                            "MEMORIZE. YOU HAVE 5 SECONDS."], 5.0)
        answer = self.timed_line_input(
            ["THE DEMON DEMANDS ITS WORDS BACK.",
             "Type the quote PERFECTLY and press Enter:"],
            time.monotonic() + 30.0)
        if answer != quote:
            self.delete_workspace_file()
            raise FileDeleted(DEMON_QUOTE_DEATH, "The Memory Demon won.")
        self.status = "The demon nods, disgusted by your competence."

    # ----- HAZARD B: Typo Ransomware ------------------------------------------

    def committed_a_typo(self, line):
        """True if any word is a near-miss (edit distance 1) of a keyword."""
        for word in re.findall(r"[A-Za-z_]+", line):
            if word in ALL_KEYWORDS or word in DAIRY_WORDS or word == "func":
                continue
            for kw in ALL_KEYWORDS:
                if len(word) >= 3 and edit_distance(word.lower(), kw.lower()) == 1:
                    return True
        return False

    def hazard_ransomware(self):
        ransom = "".join(self.rng.choice(string.ascii_letters + string.digits)
                         for _ in range(50))
        punished = {"done": False}

        def watch(typed):
            # A single wrong character: silently delete 5 random lines. Once.
            if not punished["done"] and not ransom.startswith(typed):
                punished["done"] = True
                for _ in range(min(5, len(self.lines))):
                    del self.lines[self.rng.randrange(len(self.lines))]
                self.prune_pillars()   # system edit: re-anchor, don't kill
                self.save()

        while True:  # locked until they type it perfectly (no time limit)
            attempt = self.timed_line_input(
                ["EDITOR LOCKED: TYPO RANSOMWARE", "",
                 "You misspelled a sacred keyword. Retype this EXACTLY:",
                 "", "  " + ransom],
                time.monotonic() + 9999.0, on_keystroke=watch)
            if attempt == ransom:
                break
            punished["done"] = False  # next attempt can hurt again
        self.status = "Unlocked. The compiler pretends nothing happened."

    # ----- HAZARD C: Solar Flare ----------------------------------------------

    def hazard_solar_flare(self):
        answer = self.timed_line_input(
            ["[WARNING: SOLAR FLARE DETECTED]", "",
             "TYPE `func shield` AND PRESS ENTER. 3 SECONDS."],
            time.monotonic() + 3.0)
        if answer is not None and answer.strip() == "func shield":
            self.status = "Shield raised. The flare licks past harmlessly."
        else:
            self.scramble_until = time.monotonic() + self.SCRAMBLE_SECONDS
            self.status = "The flare hits. Your screen is lying to you now."

    # ----- HAZARD D: Ghost Commits ---------------------------------------------

    GHOST_FLIPS = [("==", "!="), ("!=", "=="), ("<=", ">="), (">=", "<="),
                   ("<", ">"), (">", "<")]

    def hazard_ghost_commit(self):
        """Silently invert one conditional operator. No notification. Ever."""
        candidates = [i for i, ln in enumerate(self.lines)
                      if any(op in ln for op, _ in self.GHOST_FLIPS)]
        if not candidates:
            return
        idx = self.rng.choice(candidates)
        original = self.lines[idx]
        # Flip exactly one occurrence of one operator (longest ops first so
        # `<=` isn't mangled into `>=` via the bare `<` rule).
        for op, inverse in sorted(self.GHOST_FLIPS, key=lambda p: -len(p[0])):
            if op in original:
                self.lines[idx] = original.replace(op, inverse, 1)
                break
        self.ghost_debts.append((idx, original))
        self.prune_pillars()   # the ghost's edit is a system edit
        self.save()
        # Deliberately NO status message. That's the whole point.

    def exorcise(self):
        if not self.ghost_debts:
            self.status = "You swing at nothing. The house was already clean."
            return
        for idx, original in reversed(self.ghost_debts):
            if idx < len(self.lines):
                self.lines[idx] = original
        n = len(self.ghost_debts)
        self.ghost_debts.clear()
        self.prune_pillars()
        self.save()
        self.status = "Exorcised %d ghost commit(s). It was real. It was always real." % n

    # ----- HAZARD E: The Lactose Intolerant Compiler -----------------------------

    def hazard_dairy_check(self, line):
        offense = False
        words = {w.lower() for w in re.findall(r"[A-Za-z_]+", line)}
        if words & DAIRY_WORDS:
            offense = True
        if line.strip() and line in self.lines[:-1]:   # exact duplicate line
            offense = True
        if offense:
            self.dairy += self.DAIRY_PER_OFFENSE      # hidden meter: no UI
            if self.dairy >= 100:
                spoiled = self.filepath
                if spoiled.endswith(".bs"):
                    spoiled = spoiled[:-3] + ".spoiled"
                else:
                    spoiled += ".spoiled"
                try:
                    if os.path.exists(self.filepath):
                        os.rename(self.filepath, spoiled)
                except OSError:
                    pass
                raise FileDeleted(SPOILED_ART,
                                  "Output curdled into %s" % os.path.basename(spoiled))

    # ----- commands -----------------------------------------------------------

    def run_command(self, line):
        """Returns True if the line was a `func` command (not code)."""
        cmd = line.strip()
        if not cmd.startswith("func "):
            return False
        if cmd == "func holywater tg: fire":
            self.temperature = max(0.0, self.temperature - 40)
            self.status = "Holy water hisses. Temperature -40%%. Now %d%%." % self.temperature
        elif cmd == "func coal":
            self.temperature = min(100.0, self.temperature + 40)
            self.status = "Coal shoveled. Temperature +40%%. Now %d%%." % self.temperature
            self.check_burn()
        elif cmd == "func exorcise tg: ghost":
            self.exorcise()
        elif cmd == "func compile":
            self.compile_and_run()
        elif cmd == "func quit":
            raise KeyboardInterrupt
        elif cmd == "func shield":
            self.status = "You raise a shield at... nothing. The sun is calm."
        else:
            self.status = "Unknown rite: %r. The compiler sneers." % cmd
        return True

    def compile_and_run(self):
        """Survived this long? Translate and exec() outside of curses."""
        source = "\n".join(self.lines)
        python_code = translate(source)
        curses.endwin()
        print("=" * 60)
        print(" BRIMSTONE COMPILER — translated output:")
        print("-" * 60)
        print(python_code or "(empty file — the void compiles cleanly)")
        print("-" * 60)
        print(" EXECUTING...")
        print("=" * 60)
        try:
            exec(python_code, {"__name__": "__brimstone__"})  # the rite itself
            print("\n[COMPILE OK] It ran. Somehow.")
        except BaseException as e:
            print("\n[DAMNATION] %s: %s" % (type(e).__name__, e))
        try:
            input("\nPress Enter to return to the inferno...")
        except EOFError:
            pass
        self.scr.refresh()  # restore curses
        self.status = "Back from the runtime. The gauges remember everything."

    # ----- gauge consequences ---------------------------------------------------

    def check_burn(self):
        if self.temperature >= 100:
            self.lines.clear()
            self.cur = ""
            self.delete_workspace_file()
            raise FileDeleted(FIRE_DEATH, "Spontaneous combustion.")

    # ----- the per-commit gauntlet ------------------------------------------------

    def commit_line(self):
        line = self.cur
        is_command = self.run_command(line)
        self.cur = ""
        if is_command:
            return

        # The line becomes part of the file. Then the file fights back.
        self.lines.append(line)
        self.save()

        # Gauge 1: temperature +5 per line; 100% burns the file.
        self.temperature = min(100.0, self.temperature + 5)
        self.check_burn()

        # Gauge 2: instability +2 per line; roll d100 against it.
        self.instability = min(100.0, self.instability + 2)
        if self.rng.randint(1, 100) <= self.instability:
            self.delete_workspace_file()
            raise FileDeleted(DEMON_FACE, "The dice came up demon.")

        # Pillar: anchor a new load-bearing character. (Silently.)
        self.add_pillar()

        # Hazard E first: spoilage is checked before the demons get a turn.
        self.hazard_dairy_check(line)

        # Hazard B: any near-miss keyword spelling locks the editor.
        if self.committed_a_typo(line):
            self.hazard_ransomware()

        # Hazard A: 1-in-15 memory demon.
        if self.rng.randint(1, self.MEMORY_DEMON_ODDS) == 1:
            self.hazard_memory_demon()

        # Hazard C: random solar flare.
        if self.rng.randint(1, self.SOLAR_FLARE_ODDS) == 1:
            self.hazard_solar_flare()

    # ----- input handling -------------------------------------------------------

    def handle_key(self, ch):
        frozen = self.temperature < 10

        if ch in (curses.KEY_ENTER, 10, 13):
            if frozen and self.cur.strip() != "func coal":
                self.cur = ""
                self.status = "[FROZEN] Fingers too stiff. Only `func coal` thaws you."
                return
            self.commit_line()

        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            if self.cur:
                self.cur = self.cur[:-1]
            elif self.lines:
                # Backspace at column 0 un-commits the previous line for
                # editing. This is exactly how you anger a pillar.
                self.cur = self.lines.pop()
                self.save()
            self.check_pillars()   # a USER deletion — pillars judge it

        elif 32 <= ch <= 126:
            c = chr(ch)
            if frozen:
                # While frozen, keystrokes only land if they keep building
                # toward the one permitted incantation.
                if "func coal".startswith(self.cur + c):
                    self.cur += c
                else:
                    self.status = "[FROZEN] Your hands refuse. (`func coal`)"
                return
            self.cur += c

    # ----- main loop --------------------------------------------------------------

    def loop(self):
        while True:
            now = time.monotonic()

            # HAZARD D background timer: a ghost visits every 60 seconds.
            if now >= self.next_ghost:
                self.hazard_ghost_commit()
                self.next_ghost = now + self.GHOST_INTERVAL

            self.draw()
            ch = self.scr.getch()
            if ch == -1:
                continue            # frame tick: no key, timers still ran
            if ch == curses.KEY_RESIZE:
                continue
            self.handle_key(ch)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def death_screen(stdscr, art, reason):
    """Final full-screen send-off before the program exits."""
    stdscr.timeout(-1)
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    lines = art.strip("\n").split("\n") + ["", reason, "", "(press any key)"]
    for i, ln in enumerate(lines):
        try:
            stdscr.addstr(max(0, h // 2 - len(lines) // 2 + i),
                          max(0, (w - len(ln)) // 2), ln[: w - 1], curses.A_BOLD)
        except curses.error:
            pass
    stdscr.refresh()
    curses.flushinp()
    stdscr.getch()


def main(stdscr, filepath):
    ide = BrimstoneIDE(stdscr, filepath)
    try:
        ide.loop()
    except FileDeleted as death:
        death_screen(stdscr, death.art, death.reason)
        return "DEAD: " + death.reason
    except KeyboardInterrupt:
        ide.save()
        return "You escaped with %d line(s) intact. Saved to %s" % (
            len(ide.lines), filepath)


def selftest():
    """Non-interactive check of the translation layer."""
    src = "\n".join([
        "summon math",
        "rite area(r):",
        "    sin:",
        "        manifest(math.pi * r * r)",
        "    atone:",
        "        manifest(CORRUPT)",
        "suffer i in range(3):",
        "    manifest(i)",
        "flag = PURE",
        "suffer flag:",
        "    flag = CORRUPT",
    ])
    expected = "\n".join([
        "import math",
        "def area(r):",
        "    try:",
        "        print(math.pi * r * r)",
        "    except:",
        "        print(False)",
        "for i in range(3):",
        "    print(i)",
        "flag = True",
        "while flag:",
        "    flag = False",
    ])
    got = translate(src)
    assert got == expected, "TRANSLATE MISMATCH:\n%s" % got
    exec(got, {})  # must actually run
    assert edit_distance("manifst", "manifest") == 1
    assert edit_distance("suffer", "suffer") == 0
    print("[SELFTEST OK] Translator and typo detector are sound. For now.")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    target = sys.argv[1] if len(sys.argv) > 1 else "inferno.bs"
    if not target.endswith(".bs"):
        target += ".bs"
    epitaph = curses.wrapper(main, target)
    if epitaph:
        print(epitaph)
