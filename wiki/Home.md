# 🜏 The Brimstone Wiki

> *"There are no warnings in Brimstone, only consequences."*

**Brimstone** (`.bs`) is a chaotic esoteric programming language in which the
development environment is the primary antagonist. The language itself is a
thin, blasphemous skin over Python; the difficulty is that the IDE is on
fire, haunted, lactose intolerant, and structurally dependent on characters
you are not allowed to know about.

## Pages

| Page | Contents |
|------|----------|
| [Language Reference](Language-Reference.md) | Every keyword, with translations and examples |
| [Survival Guide](Survival-Guide.md) | The `func` incantations that keep you alive |
| [Hazard Registry](Hazard-Registry.md) | The five hazards, the two gauges, and the pillars |
| [Terminal IDE](Terminal-IDE.md) | Manual for `brimstone.py`, the curses-based IDE |
| [Web IDE](Web-IDE.md) | Manual for the browser-based Web Inferno |

## Which IDE should I use?

- **Web Inferno** (`web/index.html`) — open it in a browser. Save and load
  `.bs` files, run code with one click, no terminal required. Hazards are
  opt-in via **Damnation Mode**, so it doubles as the "I just want to write
  Brimstone in peace" option.
- **Terminal IDE** (`brimstone.py`) — the authentic experience. The hazards
  are not optional. The file deletion is not metaphorical.

## A first program

```brimstone
summon math

rite circle(r):
    sin:
        manifest(math.pi * r * r)
    atone:
        manifest(CORRUPT)

suffer i in range(3):
    circle(i)
```

Compiles to ordinary Python and prints three circle areas — assuming the
file survives long enough to be compiled.
