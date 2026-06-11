# Web IDE (`web/index.html`)

A clean, VS Code-like Brimstone editor in the browser: write, run, save,
and load `.bs` files. No terminal required.

## Running it

Open `web/index.html` in any modern browser. No build step, no install.

```sh
# any static server works; so does double-clicking the file
python3 -m http.server -d web 8666
# then visit http://localhost:8666
```

**Internet required for execution:** code runs on real Python via
[Pyodide](https://pyodide.org) (Python compiled to WebAssembly), loaded
lazily from a CDN the first time you press **▶ Run**. Editing, saving, and
loading work fully offline.

## Layout

The IDE is split into three sections:

- **Top bar:** filename input, Run button, Converter button, Save/Load
  buttons, theme toggle (dark/light).
- **Editor:** your `.bs` code, with line numbers in a gutter. Autosaves to
  `localStorage` on every keystroke.
- **Output panel:** execution results (stdout/stderr), with `[OK]` or
  `[ERROR]` status. `demand()` prompts you in a browser dialog.

## The converter

Press the **⇄ Convert** button to open a split-panel modal:

- **Left pane:** paste Python code
- **Right pane:** paste Brimstone code
- **Buttons:**
  - **→** Translate Python → Brimstone
  - **←** Translate Brimstone → Python
  - **Copy BS / Copy Py:** copy the respective pane to clipboard
  - **Insert BS to Editor:** load the Brimstone code into the main editor

The converter is bidirectional: both directions are exact opposites, so you
can round-trip code (Brimstone → Python → Brimstone) without loss.
