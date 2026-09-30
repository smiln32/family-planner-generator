# Handoff, 2026-09-30

**Why parked:** end of three short sessions. 2026-09-28 reworked the colour theme presets so each one actually looks like its name, fixed a text-overlap bug on one unfinished cover look, and made a small copy fix permanent at the source instead of a per-run edit. 2026-09-29 and 2026-09-30 brought in the owner's design export: 34 typeface sets (two per look), `fonts --all`, and twelve planner layouts with Weekly Plan and Daily Plan sheets. The 2026-09-28 work is pushed; the export commit is local until the owner pushes it. There are no other branches. Open work: the editor audit list and the paused page-looks design, both unchanged from before (see the 2026-09-26 notes further down).

## Sessions 2026-09-29 and 2026-09-30: the design export

Everything here was copied in from the owner's design export, kept outside the repo (in Downloads: `Look pairings and color exploration (1)\export`, with a `LAYOUTS.md` listing the files). It is owner-supplied design, not a chat invention. All twelve files from the export are in; the `cli.py` and `typefaces.py` half landed on 2026-09-29, the layouts on 2026-09-30.

- **34 typeface sets added** in `familyplanner/typefaces.py`: two named pairings for the original and for each of looks `02` to `17` (for example `sunday-kitchen` and `heirloom` for the original, `wedding-album` and `midnight-keepsake` for Keepsake). There are 40 sets now. The six general ones (`elegant`, `classic`, `playful`, `modern`, `italics`, `neat`) are unchanged and `elegant` is still the default. `python planner.py typefaces` lists them all, with wider columns to fit the longer names.
- **A set is not tied to a look.** The grouping by look is only a comment in `typefaces.py`, and `designs.LAYOUT_FONTS` is a suggestion the code never applies. Picking `design: 06b` does not change the fonts; set `fonts:` separately in the config or the editor.
- **`python planner.py fonts --all`** is new and downloads every built-in set. All 40 sets are already downloaded on this machine (`familyplanner/static/fonts/` is gitignored), so a fresh clone needs `fonts --all` once before building with one of the new sets.
- **Twelve planner layouts** `02a` to `12c`: looks `02`, `06`, `11`, `12` crossed with `a` split, `b` stacked bands, `c` sidebar. `designs.py` gains `LAYOUT_PRESETS`, `parts()`, `LAYOUT_PAGES` and `LAYOUT_FONTS`; the ids sit in the normal picker list with `blank` kept last. `render.py` passes `look` to every template, adds the `month_days` and `abbr` globals, and inserts `weekly` and `daily` just before the months when a layout is chosen and the page list does not already place one of them. `book.html` gives the body both classes (`design-06 design-06b`) so the parent look's CSS still applies. `pages/monthly.html` includes `layout_monthly.html` for a layout. New templates: `layout_kit.html` (boxes, lines, schedule, calendar, habit grid), `layout_monthly.html`, `pages/daily.html`, `pages/weekly.html`. `planner.css` has a "planner layouts" section appended at the end; sizes there use `--u`, 1/300 of the page width.
- **Verified 2026-09-30:** the default book is unchanged at 30 pages. `--design 06b` from the example config builds a 32-page PDF; `06b`, `11a`, `12c` and `02c` were also built to PNG and the weekly, daily and January pages looked right (boxes filled the sheet, calendar dated, week order followed the config). Not checked: the other eight layouts by eye, page sizes other than letter, the `--linked` edition with a layout, and the editor's look picker with 30 cards.
- **The editor's TYPE picker reads the same list**, so it now shows 40 cards plus Custom. Not looked at by hand yet.
- **Tests:** 103 tests (`tests/test_layouts.py` adds 17), all passing. `test_security.py` resolves every set name; nothing covers `fonts --all`. A Windows flake was fixed on 2026-09-30: the server answered a rejected POST with 403 without reading the request body, so the socket closed with unread bytes, Windows sent a reset, and the client dropped the reply (`ConnectionAbortedError` in about half of full runs). `server.py` now drains a body up to `MAX_BODY` in `_reject()` before replying. Eight full runs passed in a row after the fix.
- **Docs updated to match:** README (typefaces, `fonts --all`, planner layouts, and the `linen` description, which still said "sage" from before the theme rework; the `themes.py` comment too), `config.example.yaml` (font sets, layout ids), `_config/design-system.md` (sets, layouts, one em dash removed), `_config/page-catalog.md` (`weekly`, `daily`), `shared/looks-handoff.md` (a row for the layouts, files table).

## Session 2026-09-28: themes

- **Themes reworked to match their names.** Several presets did not look like what they were called: `citrus` was mostly cobalt blue, `ocean` leaned on coral and red, `poppy` had cyan running through it, and `meadow` was close enough to `classic`'s rainbow to be hard to tell apart in the picker. Fixed:
  - `linen` (the default): sage-green cast replaced with warm taupe/beige/ivory.
  - `citrus`: no more blue; headings changed from dark olive-green to a deep mustard gold. Lemon/lime/tangerine family throughout.
  - `ocean`: no more coral or red; blue/green/seafoam/indigo only.
  - `poppy`: no more cyan, and no dark colours at all. The near-black wine heading and dark maroon accent are now bright crimson and bright rose. Pink/red family throughout, one leaf-green accent.
  - `forest`: light touch. Accent tokens shifted from peachy orange-red to soil-brown, so it reads as green-and-brown, not green-and-orange.
  - `meadow`: rebuilt as shades of green (pine to fresh grass); no more pink/magenta, so it no longer looks like `classic`.
  - `amber`: the dark violet "purple" token replaced with a rust tone.
  - `slate` **renamed to `blues`** everywhere (theme file, README, config.example.yaml). Any old `family.yaml` with `theme: slate` will now fail to load; reopen it and pick `blues`.
  - All 12 named presets: `linen classic amber berry bold citrus forest meadow ocean pastel poppy blues`.
- **January's tagline** no longer ends in "!". Fixed in the factory default (`familyplanner/config.py`), not a per-run override, so it applies automatically to every future run.
- **Keepsake cover (look 10) overlap fixed.** The script "Family" heading's descender was colliding with "SUCCESS PLANNER" underneath it. Added line-height and bottom padding to clear it. This is a spacing bug fix only. Keepsake is still an unfinished look per `shared/looks-handoff.md`; nothing about its content or layout changed.
- Commit: `18957da Rework theme palettes to match their names, fix Keepsake cover overlap`. Pushed.
- **Not done / still open from this session:** the other four themes (`classic`, `berry`, `bold`, `pastel`) were not touched, only the ones flagged in conversation. If any of those also feel mismatched to their name, that's a new ask, not something already covered.
- The real, already-printed run (local only; see `status`) was built before this session's theme changes and uses `linen`. Its cover wording is unaffected, but if it's ever rebuilt, `linen`'s look will be slightly different (warmer, less sage-green) than the PDF already printed.

Everything below this point is from the 2026-09-26 session and earlier; still accurate except where the notes above override it (theme names/colours, January's tagline, the typeface sets).

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
| Editor audit (`/impeccable audit`) | Scored 12/20 before fixes. Fixed: `--muted` now `#6A655C` (4.8:1+), error toast on new `--error` `#96564E` (5.6:1), page-list names are real buttons beside the checkbox with `aria-current`, "Add a person", `.linky` and `.palette-undo` on new `--teal-deep` (5.2:1). Detector reports no low-contrast text now. Remaining items below |
| Week order on weekly pages | Done 2026-09-26. Meal plan, chores, health tracker, school, family time and the example gratitude page follow `week_starts` via `day_names`/`day_initials(cfg.sunday_first)`. No template has a fixed day order now. Meal plan and gratitude key each day's tint/glyph by name; the others keep their decorative colour runs positional |
| Palette colour editor | Committed, covered by unit and API tests; **still not exercised by hand in `planner.py ui`** |
| Theme presets | Reworked 2026-09-28 so each named theme (`citrus`, `ocean`, `poppy`, `meadow`, `linen`, `amber`, `forest`) actually matches its name; `slate` renamed to `blues`. See "Session 2026-09-28" above. Not hand-checked in the UI yet; do that alongside item 5 below |
| Typeface sets | 40 since 2026-09-29: the six general sets plus two pairings per look, and `fonts --all` to download them. TYPE picker not hand-checked with 40 cards |
| Planner layouts `02a`–`12c` | In since 2026-09-30 from the owner's export, with Weekly Plan and Daily Plan sheets and a boxed monthly page. Built and eyeballed for four of the twelve at letter size; see "the design export" above for what is not checked |
| Security pass (validators, local API guard, clean CLI errors) | Done. Suite is 86 tests, all passing |
| Privacy: run outputs untracked, history rewritten, GitHub repo recreated | Done 2026-09-24. Repo still **private**. 2026-09-26: local reflogs expired and `gc --prune=now --aggressive` run; name and `family.yaml` greps across all objects and commits are empty, no dangling objects. This is the only clone on the machine. A GitHub Support purge request was drafted but not sent; send it only if the repo is going public |
| Looks 02–17 design quality | **Not done.** Human paused look design; covers are not print-quality |
| Local book build | A run was rebuilt on 2026-09-26 after the week-order fix. Its files are local only |
| PDF path | Verified 2026-09-26 from the example config: exit 0, 30 pages matching the HTML, US Letter, no blank pages, fonts embedded. Chrome embeds Playfair Display as a Type 3 font; fine for home printing, but some print-shop preflight checks flag Type 3 |

## Editor audit: still open

In priority order. None block use at the normal full-screen desktop width.

1. **Narrow windows (P2):** below 900px the layout stacks and the preview sits under the whole settings panel; at phone width the page overflows sideways and the preview shrinks to a strip. `ui.css` responsive block. Suggested: `/impeccable adapt`.
2. **Small, flat type (P2):** section heads 12px, labels 11px, body 10.5–11.5px. Suggested: `/impeccable typeset`.
3. **Leftover blue-grey colours (P2):** about 20 hard-coded values outside `:root`, many from an older navy/bright-teal scheme (`#B8C4D4` hover borders, `rgba(20,160,165,.16)` selection ring, `rgba(22,50,95,…)` sheet shadow, `#A6B2C2` placeholder, `#CBD5E1` switch-off track). Map them to tokens.
4. **Faint control outlines (P2):** input borders 1.4:1, page checkboxes 1.8:1, switch-off track 1.3:1; controls need 3:1.
5. **Small targets (P2):** member remove buttons 24px, zoom buttons 26px.
6. **Reduced motion (P3):** the global `.01ms` rule freezes the loading spinner; keep a gentle pulse instead.
7. **Favicon (P3):** `index.html` still uses the old navy and bright teal.

The project has no `PRODUCT.md`; `/impeccable init` writes one before any redesign. Finish with `/impeccable polish`, then re-run `/impeccable audit`.

## Locked decisions

- No real family names in the repo: not in docs, examples, tests, commit messages or run outputs. Use blank or made-up names (the code uses "Ramirez"). Personalisation happens in `family.yaml` or the UI, never by committing a run.
- Original illustrated house cover (`design: original`) stays as-is; never restyle it and present it as a new look.
- Looks `02`–`17` are unfinished. Do not invent cover art, florals or notebook chrome in chat without a human-approved reference image or written layout (see `shared/looks-handoff.md` → "Do not").
- Every value from YAML, CLI flags or the UI goes through the validators in `config.py`. New fields get a `check_*` helper and a test; nothing reaches a template or a file path unchecked.
- The local server answers only its own page. Keep all UI calls on the JSON `api()` helper in `ui.js`; a plain form post or `text/plain` fetch will get a 403.
- ICM rules from the conventions: references point one way (stages point to `_config/`, `shared/` and earlier stages' `output/`, never forward); one canonical home per fact; CONTEXT.md files route and stay under 80 lines; no em dashes; no spaces in file names.
- `out/` and root `family.yaml` are gitignored local scratch. A run's settings live only in `stages/02-customize/output/`; do not copy them to a root `family.yaml`. With no root file, `start-planner.bat` and plain `planner.py ui` open a blank planner; open a run with **Open a plan** or `planner.py ui -c <stage 02 yaml>`.
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
5. Worth doing: open `python planner.py ui` and exercise the colour editor by hand (change a colour, preview, download the plan, open it again). While there, click through every theme in the picker (especially `citrus`, `ocean`, `poppy`, `meadow`, `linen`, `amber`) to confirm the 2026-09-28 rework actually reads right on screen, not just in the hex values. Also scroll the TYPE picker, which now holds 40 sets, and pick one of the new ones; then pick a planner layout such as `06b` in the look picker and check the Weekly Plan, Daily Plan and a month at letter and at `5.5x8`.
6. If asked to continue look design, follow `shared/looks-handoff.md` exactly: get an approved reference first, implement one look at a time, then stop.
7. Making the repo public is a human call (GitHub Settings → Danger Zone → Change visibility). Nothing in the history blocks it.
8. Do not read previous run outputs (`stages/*/output/`) to learn style. `_config/` is the quality source.

> FIRST TURN: read the referenced docs ONE AT A TIME (no parallel tool calls, no batched reads). Parallel reads on the first turn can wedge a new session; sequential reads avoid it.
