# Handoff, 2026-09-25

**Why parked:** end of a session that brought the workspace into line with the ICM conventions and fixed the editor's worst accessibility findings. `main` is pushed and matches GitHub; there are no other branches. Open work: the rest of the editor audit list below, and the paused page-looks design.

## What this is

Family Success Planner is an ICM factory (`CLAUDE.md` → `CONTEXT.md` → stage `CONTEXT.md`) for printable planner books, plus a local Python app (`planner.py`, `familyplanner/`) that renders them. The repo may be made public, so it must never carry a real family's name (see Locked decisions).

## Where everything lives

- Repo root: `C:\Users\smiln\apps from Kingston\Apps just for me\family-planner-generator`
- Remote: `git@github.com:smiln32/family-planner-generator.git` (SSH; see Environment notes)
- Layer 0/1: `CLAUDE.md`, `CONTEXT.md`
- Stage pipeline: `stages/01-intake/` → `02-customize/` → `03-build/` → `04-review/` (each has `CONTEXT.md`, `references/`, `output/`)
- Factory reference: `_config/CONTEXT.md` routes to `design-system.md`, `voice.md`, `page-catalog.md`; `config.example.yaml` is the one source for generator keys
- Cross-stage notes: `shared/decisions.md`, `shared/looks-handoff.md` (read before touching any cover/look work)
- Renderer/app: `familyplanner/config.py` (loading plus the shared validators), `designs.py`, `render.py`, `server.py`, `templates/`, `static/`
- Editor UI: `familyplanner/static/ui/` (`index.html`, `ui.css`, `ui.js`); Windows launcher `start-planner.bat`
- Tool install guide: `stages/03-build/references/tool-setup.md` (README points here)
- Tests: `tests/` (`python -m pytest`; install with `pip install -r requirements-dev.txt`)
- Run outputs under `stages/*/output/` are gitignored and stay on the machine that made them. Use `status` to see what exists locally.

## Build status

| Unit | State |
|------|-------|
| ICM conformance | Done 2026-09-25, checked against `_core/CONVENTIONS.md` in github.com/RinDig/Interpretable-Context-Methodology. Stage contracts have no Routing sections (they pointed forward); stage 03 has an Audit; duplicate reference files removed; templates followed for Layer 0/1 and the questionnaire; no em dashes; launcher renamed from `Start Planner.bat` |
| ICM deviations kept on purpose | Stage folders use `01-` (the conventions and reference repo do; the paper shows `01_`). `familyplanner/` has no hyphen (Python package). `README.md` is over 200 lines (human doc, agents do not load it). Built PDFs keep the `<year>-<family>-Family-Planner` name |
| Editor audit (`/impeccable audit`) | Scored 12/20 before fixes. Fixed: `--muted` now `#6A655C` (4.8:1+), error toast on new `--error` `#96564E` (5.6:1), page-list names are real buttons beside the checkbox with `aria-current`, "Add a person" on new `--teal-deep` (5.2:1). Detector reports no low-contrast text now. Remaining items below |
| Palette colour editor | Committed, covered by unit and API tests; **still not exercised by hand in `planner.py ui`** |
| Security pass (validators, local API guard, clean CLI errors) | Done, 74 tests pass |
| Privacy: run outputs untracked, history rewritten, GitHub repo recreated | Done 2026-09-24. Repo still **private** |
| Looks 02–17 design quality | **Not done.** Human paused look design; covers are not print-quality |
| Local book build | A run was rebuilt and reviewed on 2026-09-25 after the looks and security work. Its files are local only |

## Editor audit: still open

In priority order. None block use at the normal full-screen desktop width.

1. **Narrow windows (P2):** below 900px the layout stacks and the preview sits under the whole settings panel; at phone width the page overflows sideways and the preview shrinks to a strip. `ui.css` responsive block. Suggested: `/impeccable adapt`.
2. **Small, flat type (P2):** section heads 12px, labels 11px, body 10.5–11.5px. Suggested: `/impeccable typeset`.
3. **Leftover blue-grey colours (P2):** about 20 hard-coded values outside `:root`, many from an older navy/bright-teal scheme (`#B8C4D4` hover borders, `rgba(20,160,165,.16)` selection ring, `rgba(22,50,95,…)` sheet shadow, `#A6B2C2` placeholder, `#CBD5E1` switch-off track). Map them to tokens.
4. **Faint control outlines (P2):** input borders 1.4:1, page checkboxes 1.8:1, switch-off track 1.3:1; controls need 3:1.
5. **Two links at 4.2:1:** "Show every page" and "Use theme colours" use `--teal` on the panel. Switching `.linky` and `.palette-undo` to `--teal-deep` fixes both.
6. **Small targets (P2):** member remove buttons 24px, zoom buttons 26px.
7. **Reduced motion (P3):** the global `.01ms` rule freezes the loading spinner; keep a gentle pulse instead.
8. **Favicon (P3):** `index.html` still uses the old navy and bright teal.

The project has no `PRODUCT.md`; `/impeccable init` writes one before any redesign. Finish with `/impeccable polish`, then re-run `/impeccable audit`.

## Locked decisions

- No real family names in the repo: not in docs, examples, tests, commit messages or run outputs. Use blank or made-up names (the code uses "Ramirez"). Personalisation happens in `family.yaml` or the UI, never by committing a run.
- Original illustrated house cover (`design: original`) stays as-is; never restyle it and present it as a new look.
- Looks `02`–`17` are unfinished. Do not invent cover art, florals or notebook chrome in chat without a human-approved reference image or written layout (see `shared/looks-handoff.md` → "Do not").
- Every value from YAML, CLI flags or the UI goes through the validators in `config.py`. New fields get a `check_*` helper and a test; nothing reaches a template or a file path unchecked.
- The local server answers only its own page. Keep all UI calls on the JSON `api()` helper in `ui.js`; a plain form post or `text/plain` fetch will get a 403.
- ICM rules from the conventions: references point one way (stages point to `_config/`, `shared/` and earlier stages' `output/`, never forward); one canonical home per fact; CONTEXT.md files route and stay under 80 lines; no em dashes; no spaces in file names.
- `out/` and root `family.yaml` are gitignored local scratch.
- One stage, one job; no coordinator script; reorder stages by renaming the numbered folders only.

## Environment notes

- Windows Smart App Control blocks Git for Windows' unsigned `libcurl-4.dll`, so HTTPS push and fetch fail or hang. This repo pushes over SSH with `core.sshCommand = C:/Windows/System32/OpenSSH/ssh.exe`. Do not switch the remote back to HTTPS.
- The owner runs pushes. When asked, give the git commands one at a time and wait for "done" between them. Last push (2026-09-25) worked from PowerShell in the repo root.
- Any clone made before 2026-09-24 has the old history. Delete it and re-clone; never push from it, or the names and source pack return.
- The original source pack (reference planner PDF and 31 page JPGs) lives outside the repo at `..\planner-source-pack\`. Do not copy it back in; it must not be published.
- `git-filter-repo` is installed (`python -m git_filter_repo`) if history ever needs scrubbing again.
- To stop a test copy of the editor, kill only the PID listening on its port (`netstat -ano`), never every `python.exe`.

## What to do on resume

1. Read this file, then `git status`. It should be clean.
2. Run `python -m pytest`. All tests should pass.
3. If asked to print a book: route through stage 03 (`build`), then stage 04 review.
4. If asked to continue the editor work: take "Editor audit: still open" in order.
5. Worth doing: open `python planner.py ui` and exercise the colour editor by hand (change a colour, preview, download the plan, open it again).
6. If asked to continue look design, follow `shared/looks-handoff.md` exactly: get an approved reference first, implement one look at a time, then stop.
7. Making the repo public is a human call (GitHub Settings → Danger Zone → Change visibility). Nothing in the history blocks it.
8. Do not read previous run outputs (`stages/*/output/`) to learn style. `_config/` is the quality source.

> FIRST TURN: read the referenced docs ONE AT A TIME (no parallel tool calls, no batched reads). Parallel reads on the first turn can wedge a new session; sequential reads avoid it.
