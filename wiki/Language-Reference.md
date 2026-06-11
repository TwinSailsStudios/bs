# Language Reference

Brimstone is translated to Python keyword-for-keyword at compile time, then
executed by a real Python interpreter. Anything that isn't a Brimstone
keyword passes through untouched — so all of Python's operators, literals,
indentation rules, and standard library are available, provided you summon
them politely.

## Keywords

| Brimstone | Python | Notes |
|-----------|--------|-------|
| `manifest(...)` | `print(...)` | Speak into the void |
| `demand(...)` | `input(...)` | The void speaks back |
| `summon X` | `import X` | Bind a module to your will |
| `rite name(...):` | `def name(...):` | Define a ritual |
| `suffer x in y:` | `for x in y:` | Bounded suffering |
| `suffer cond:` | `while cond:` | Unbounded suffering |
| `PURE` | `True` | |
| `CORRUPT` | `False` | |
| `sin:` | `try:` | Attempt the forbidden |
| `atone:` | `except:` | Pay for it |

### The two faces of `suffer`

`suffer` is the only context-sensitive keyword. The compiler checks whether
the line contains the word `in` after `suffer`:

```brimstone
suffer soul in damned:      # → for soul in damned:
suffer hope > 0:            # → while hope > 0:
```

If you write a while-loop whose condition happens to contain the word `in`
(e.g. `suffer "x" in s:`), it becomes a for-loop and fails. This is
considered a feature.

### Forbidden vocabulary

The words `copy`, `paste`, `loop`, and `while` are contraband anywhere in
your source — including comments and strings. Each use feeds the hidden
Dairy Meter (see [Hazard Registry](Hazard-Registry.md), Hazard E). The
blessed loop construct is `suffer`; it translates away before the compiler
can smell it.

## Worked example

```brimstone
summon random

rite judge(soul):
    sin:
        verdict = random.choice([PURE, CORRUPT])
        suffer verdict == CORRUPT:
            manifest("burn")
            verdict = PURE
        manifest("released")
    atone:
        manifest("the paperwork was lost")

suffer i in range(3):
    judge(i)
```

Translates to:

```python
import random

def judge(soul):
    try:
        verdict = random.choice([True, False])
        while verdict == False:
            print("burn")
            verdict = True
        print("released")
    except:
        print("the paperwork was lost")

for i in range(3):
    judge(i)
```

## Errors

Runtime errors are reported as `[DAMNATION] <type>: <message>`. A clean run
ends with `[COMPILE OK] It ran. Somehow.` Neither outcome protects the file
from anything described in the [Hazard Registry](Hazard-Registry.md).
