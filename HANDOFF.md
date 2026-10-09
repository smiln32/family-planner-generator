# Handoff, 2026-10-09

## Batch A fixes, 2026-10-09 (branch `batch-a-fixes`, not pushed)

Small bug fixes, one commit each, every fix with a test. `python -m pytest`: 204 passed (159 before).

- **Annual calendar:** the weekday header now shades Saturday and Sunday for both week starts (it shaded Monday and Sunday with `week_starts: monday`). No other template shaded weekends by position.
- **`--theme`** rebuilds the palette from the new theme and keeps only the config file's own `palette:` block. Before, a theme without a paper colour (`bold`, `blues`) kept the old paper.
- **Editor server:** a body over 1 MB gets 413; a bad Content-Length, JSON that does not parse, or JSON that is not an object gets 400 with a plain message (was 500 or a silent empty request). The 403 drain for Windows is kept.
- **Plan files** now keep `months` (as changes from the built-in twelve), `title`, `subtitle` and `linked`. `output_name` is left out on purpose: it is not on the form, so a saved one would keep an old file name after the year or family name changed; the plan file says so in a comment. A bad typeface set name fails on export, and a plan with no `fonts:` opens in its look's own set instead of `elegant`.
- **Pages:** the year-end page names the family members (five to a row, blank lines when there are none) instead of Mom/Dad/Child; Belongs To has one row per member, never fewer than five (two columns on the small sizes when more than five). Start over gives five member rows.
- **Retired and Blank covers** render only the chosen variant; checked pixel for pixel against the old output.
- **Typeface set `terracotta` renamed to `boho-brush`** (Tenor Sans, Caveat Brush, Mulish), so it is not mixed up with the Terracotta look, which uses `home-base`. `terracotta` still works as an alias in YAML, `--fonts`, plan files and the editor.
- Not checked by hand in the editor yet; restart it before trying (see Environment notes).


## Sessions 2026-10-01 to 2026-10-03: look covers and colours

Three commits on `main` from the editor sessions of 1 and 2 October, plus this note; all pushed on 2026-10-03.

- **Look covers carry no family line** (`387fe1f`, 2026-10-01). The thirteen looks leave "The [family name] Family" off the cover by design. `_config/voice.md` and the stage 04 audit row used to expect it; both now say a look cover is the look's own, with no family name and no year, and that the retired looks still print the line when `family_name` is set. `family_name` still names the file and the page title.
- **Each look owns its colours in the editor** (`49fc5ca`, 2026-10-02). Before, the colour panel showed theme cards that a look book ignores and put the theme's colours in the pickers instead of what prints. Now a look or layout hides the theme cards, names the look in the colour note and starts the pickers from the look's palette; Blank and the retired looks keep the theme cards. Page look sits above Colour, and each look card shows a strip of its colours. In `config.py`: `base_palette(theme, design)`, `uses_theme(design)`, a `palette_set` field holding the `palette:` block as written, and `palette_overrides(..., design)` so replacements are saved against the look's colours; a colour set on purpose prints even when it equals the theme's value. Switching to a look with different colours clears replacements, as picking a theme already did. `build` prints a note when a config names a theme the look ignores, and `themes` says where a theme applies. README, `_config/design-system.md` and stage 02 updated. `tests/test_colour_source.py` added.
- **Undo after a look clears colours** (`aa9f315`, 2026-10-02). When a new look clears replaced colours, the toast offers Undo, which keeps the new look and puts the replaced colours back on it. `ui.js` only.
- **2026-10-03 (this note):** `config.example.yaml` comments, `CONTEXT.md` and the stage 01 and 02 contracts now say `design` is the choice and a theme applies only to Blank and the retired looks. `shared/looks-handoff.md` was folded into the "Looks" section below and deleted, so there is one handoff; `CLAUDE.md` now lists `HANDOFF.md` in its folder map and routes look work here. `python -m pytest`: 159 passed. The colour panel has not been exercised by hand since the 2 October rework; see "What to do on resume".

## Later on 2026-09-30: thirteen new looks

The owner rejected the old covers and asked for every style to be different. Thirteen looks were designed in `Planner Styles.dc.html` (design canvas, outside the repo), approved by the owner, then built in:

- `designs.LOOKS`: `editorial` (new default), `midcentury`, `nordic`, `farmhouse`, `deco`, `swiss`, `retro`, `bauhaus`, `almanac`, `terracotta`, `cottage`, `gazette`, `coastal`. Each has a palette (applied over the theme, like the layouts), a typeface set and monthly wording. The picker shows the looks, then the layouts, then `blank`. `original` and `02`-`17` moved to `designs.LEGACY`: still valid, not offered.
- New templates `look_cover.html` and `look_monthly.html`, included from `pages/cover.html` and `pages/monthly.html`. New stylesheet `static/looks.css`, appended after `planner.css` by `render.py`. `book.html` adds an `lk` body class for a look book, which hides the house mark, page art, sprigs and hearts on every worksheet and restyles cards, tabs, banners and footers per look.
- `typefaces.py`: twelve new sets (Swiss reuses `grotesk-red`), display role now also downloads weight 400, and every role downloads a 400 italic when the family has one (`slug(..., italic=True)` -> `-400i.woff2`). `fonts.py` fetches italics as a non-fatal second pass. **Run `python planner.py fonts --all` once**, or the new looks fall back to system fonts.
- Defaults: `config.py`, `ui.js` and `config.example.yaml` now default to `editorial` with the `home-edition` set. The example file leaves `fonts:` commented so the look's set applies.
- Tests: `tests/test_looks.py` added; one line in `test_layouts.py` changed (the theme-colours check now uses `design = "original"`). The design environment had no Python, so nothing was run there; see "Applied and verified" below for what was run on this machine.
- The run in `stages/02-customize/output/` still names `design: original`, so it rebuilds exactly as printed.
- Locked decision about the original cover is lifted by the owner: the house cover is retired, not restyled.

### Applied and verified, 2026-09-30 evening

The update arrived as an unzipped copy of the repo in Downloads (`family-planner-generator-updated`). The 19 files it changed were copied in byte for byte; every other tracked file already matched that copy.

- **Commit:** `2163063 Add thirteen new looks with their own covers, monthly pages, colours and fonts`, made on branch `thirteen-looks`, followed by `8d7142d Update handoff and retire stale wording about the old looks`. **Both are merged into `main` (fast-forward) and pushed: `main` and `origin/main` are at `8d7142d`.** The branch `thirteen-looks` was then deleted here and on GitHub; `main` is the only branch. Two later handoff-only commits sit on top; both went up with the 2026-10-03 push.
- **`python planner.py fonts --all`:** exit 0. There are 52 typeface sets now.
- **`python -m pytest`:** 142 passed.
- **Builds:** all thirteen looks built `--only cover,january --png --dpi 110` with exit 0. Every cover and every January was looked at: complete, right fonts and colours, calendar starts Friday 1 January 2027, nothing cut off or blank. Not checked: the other months and the worksheets in each look, page sizes other than letter, the `--linked` edition, and whether each page matches the approved canvas.
- **Low-resolution previews drop hairlines.** At 110 dpi the Gazette month lost two vertical grid lines and the Editorial grid looked uneven. Gazette's grid is a 0.75px gap, which falls under one pixel at that size. At 300 dpi every Gazette line is there. Judge grid lines at 300 dpi or in the PDF, not in a quick preview.
- **Swiss cover:** the "y" of "ily" touches the "P" of "Plan-" below it. Looks like intended tight stacking; the owner has seen the looks in the editor and said they look great. Not raised as a bug.
- **Editor:** the owner opened `planner.py ui` and saw "unknown design 'editorial'" and "unknown typeface set 'home-edition'" with a blank preview. Cause: an editor started before the update was still running the old Python code while serving the new `ui.js`. Restarting it fixed it; the owner confirmed the looks work in the picker. See Environment notes.

### Stale-file check, 2026-09-30 evening

No stale files. Every template is included from somewhere, every tracked file matches the update copy, and nothing untracked sits in the repo apart from the gitignored caches, fonts and run outputs. `example_gratitude` and `reading_log` are optional extras listed in `_config/page-catalog.md`, not leftovers. The CSS for looks `02` to `17` in `planner.css` and their branches in `pages/cover.html` stay on purpose: the legacy ids are still valid and the layouts build on `02`, `06`, `11` and `12`.

Stale wording in files the update did not touch was fixed the same evening, with the owner's go-ahead: the note above the look picker in `static/ui/index.html`, the "paused" rows in `CLAUDE.md` and `CONTEXT.md`, `shared/decisions.md`, `shared/CONTEXT.md`, and the comment above the old covers in `pages/cover.html`. The looks handoff (since folded into this file) was left alone: its top section was current and said the rest was history.

Outside the repo: `Downloads\family-planner-generator-updated` is now identical to the repo and can be deleted by the owner whenever convenient.

**Why parked:** end of three short sessions. 2026-09-28 reworked the colour theme presets so each one actually looks like its name, fixed a text-overlap bug on one unfinished cover look, and made a small copy fix permanent at the source instead of a per-run edit. 2026-09-29 and 2026-09-30 brought in the owner's design export: 34 typeface sets (two per look), `fonts --all`, and twelve planner layouts with Weekly Plan and Daily Plan sheets. The 2026-09-28 work and the export commits are pushed (`main` at `95a032e`). The thirteen looks are merged into `main` and pushed (`8d7142d`). Open work: the editor audit list (see the 2026-09-26 notes further down).

## Sessions 2026-09-29 and 2026-09-30: the design export

Everything here was copied in from the owner's design export, kept outside the repo (in Downloads: `Look pairings and color exploration (1)\export`, with a `LAYOUTS.md` listing the files). It is owner-supplied design, not a chat invention. All twelve files from the export are in; the `cli.py` and `typefaces.py` half landed on 2026-09-29, the layouts on 2026-09-30.

- **34 typeface sets added** in `familyplanner/typefaces.py`: two named pairings for the original and for each of looks `02` to `17` (for example `sunday-kitchen` and `heirloom` for the original, `wedding-album` and `midnight-keepsake` for Keepsake). There are 40 sets now. The six general ones (`elegant`, `classic`, `playful`, `modern`, `italics`, `neat`) are unchanged and `elegant` is still the default. `python planner.py typefaces` lists them all, with wider columns to fit the longer names.
- **A set is not tied to a look.** The grouping by look is only a comment in `typefaces.py`, and `designs.LAYOUT_FONTS` is a suggestion the code never applies. Picking `design: 06b` does not change the fonts; set `fonts:` separately in the config or the editor.
- **`python planner.py fonts --all`** is new and downloads every built-in set. All 40 sets are already downloaded on this machine (`familyplanner/static/fonts/` is gitignored), so a fresh clone needs `fonts --all` once before building with one of the new sets.
- **Twelve planner layouts** `02a` to `12c`: looks `02`, `06`, `11`, `12` crossed with `a` split, `b` stacked bands, `c` sidebar. `designs.py` gains `LAYOUT_PRESETS`, `parts()`, `LAYOUT_PAGES` and `LAYOUT_FONTS`; the ids sit in the normal picker list with `blank` kept last. `render.py` passes `look` to every template, adds the `month_days` and `abbr` globals, and inserts `weekly` and `daily` just before the months when a layout is chosen and the page list does not already place one of them. `book.html` gives the body both classes (`design-06 design-06b`) so the parent look's CSS still applies. `pages/monthly.html` includes `layout_monthly.html` for a layout. New templates: `layout_kit.html` (boxes, lines, schedule, calendar, habit grid), `layout_monthly.html`, `pages/daily.html`, `pages/weekly.html`. `planner.css` has a "planner layouts" section appended at the end; sizes there use `--u`, 1/300 of the page width.
- **Verified 2026-09-30:** the default book is unchanged at 30 pages. `--design 06b` from the example config builds a 32-page PDF; `06b`, `11a`, `12c` and `02c` were also built to PNG and the weekly, daily and January pages looked right (boxes filled the sheet, calendar dated, week order followed the config). Not checked: the other eight layouts by eye, page sizes other than letter, the `--linked` edition with a layout, and the editor's look picker with 30 cards.
- **The editor's TYPE picker reads the same list**, so it now shows 40 cards plus Custom. Not looked at by hand yet.
- **Tests:** 103 tests (`tests/test_layouts.py` adds 17), all passing. `test_security.py` resolves every set name; nothing covers `fonts --all`. A Windows flake was fixed on 2026-09-30: the server answered a rejected POST with 403 without reading the request body, so the socket closed with unread bytes, Windows sent a reset, and the client dropped the reply (`ConnectionAbortedError` in about half of full runs). `server.py` now drains a body up to `MAX_BODY` in `_reject()` before replying. Eight full runs passed in a row after the fix.
- **Docs updated to match:** README (typefaces, `fonts --all`, planner layouts, and the `linen` description, which still said "sage" from before the theme rework; the `themes.py` comment too), `config.example.yaml` (font sets, layout ids), `_config/design-system.md` (sets, layouts, one em dash removed), `_config/page-catalog.md` (`weekly`, `daily`), the looks handoff (a row for the layouts, files table).

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
- **Keepsake cover (look 10) overlap fixed.** The script "Family" heading's descender was colliding with "SUCCESS PLANNER" underneath it. Added line-height and bottom padding to clear it. This is a spacing bug fix only. Keepsake is still an unfinished look (see "Looks" below); nothing about its content or layout changed.
- Commit: `18957da Rework theme palettes to match their names, fix Keepsake cover overlap`. Pushed.
- **Not done / still open from this session:** the other four themes (`classic`, `berry`, `bold`, `pastel`) were not touched, only the ones flagged in conversation. If any of those also feel mismatched to their name, that's a new ask, not something already covered.
- The real, already-printed run (local only; see `status`) was built before this session's theme changes and uses `linen`. Its cover wording is unaffected, but if it's ever rebuilt, `linen`'s look will be slightly different (warmer, less sage-green) than the PDF already printed.

Everything below this point is from the 2026-09-26 session and earlier; still accurate except where the notes above override it (theme names/colours, January's tagline, the typeface sets).

## What this is

Family Success Planner is an ICM factory (`CLAUDE.md` → `CONTEXT.md` → stage `CONTEXT.md`) for printable planner books, plus a local Python app (`planner.py`, `familyplanner/`) that renders them. The repo may be made public, so it must never carry a real family's name (see Locked decisions).

## Where everything lives

- Repo root: the `family-planner-generator` folder on the owner's computer (the only clone; see Environment notes)
- Remote: `git@github.com:smiln32/family-planner-generator.git` (SSH; see Environment notes)
- Layer 0/1: `CLAUDE.md`, `CONTEXT.md`
- Stage pipeline: `stages/01-intake/` → `02-customize/` → `03-build/` → `04-review/` (each has `CONTEXT.md`, `references/`, `output/`)
- Factory reference: `_config/CONTEXT.md` routes to `design-system.md`, `voice.md`, `page-catalog.md`; `config.example.yaml` is the one source for generator keys
- Cross-stage notes: `shared/decisions.md`. Look rules are in "Looks" below; read it before touching any cover or look work
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
| Palette colour editor | Reworked 2026-10-02 so each look owns its colours and Undo restores cleared replacements (see the October section). Unit and API tests cover it (`tests/test_colour_source.py`); **not exercised by hand since the rework** |
| Theme presets | Reworked 2026-09-28 so each named theme (`citrus`, `ocean`, `poppy`, `meadow`, `linen`, `amber`, `forest`) actually matches its name; `slate` renamed to `blues`. See "Session 2026-09-28" above. Not hand-checked in the UI yet; do that alongside item 5 below |
| Typeface sets | 52 since 2026-09-30 (40 on 2026-09-29, plus twelve for the new looks), and `fonts --all` to download them. `terracotta` renamed `boho-brush` on 2026-10-09 (old name still accepted). TYPE picker not hand-checked end to end |
| Thirteen looks (`editorial` to `coastal`) | In `main` since 2026-09-30, owner-approved designs. Cover and January built and checked for all thirteen; owner checked them in the editor |
| Planner layouts `02a`–`12c` | In since 2026-09-30 from the owner's export, with Weekly Plan and Daily Plan sheets and a boxed monthly page. Built and eyeballed for four of the twelve at letter size; see "the design export" above for what is not checked |
| Security pass (validators, local API guard, clean CLI errors) | Done. Bad request bodies get 400 or 413 since 2026-10-09. The whole suite is 204 tests as of 2026-10-09, all passing |
| Privacy: run outputs untracked, history rewritten, GitHub repo recreated | Done 2026-09-24. Repo still **private**. 2026-09-26: local reflogs expired and `gc --prune=now --aggressive` run; name and `family.yaml` greps across all objects and commits are empty, no dangling objects. This is the only clone on the machine. A GitHub Support purge request was drafted but not sent; send it only if the repo is going public |
| Looks 02–17 design quality | **Retired 2026-09-30.** Replaced by the thirteen looks. `original` and `02`–`17` live in `designs.LEGACY`: still valid in a config, not offered in the picker, never finished |
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

## Looks

The print looks and the rules around them. This section replaced `shared/looks-handoff.md` on 2026-10-03; the per-look verdicts on the retired looks are in that file's git history.

- **Thirteen current looks** (`designs.LOOKS`): `editorial` (default), `midcentury`, `nordic`, `farmhouse`, `deco`, `swiss`, `retro`, `bauhaus`, `almanac`, `terracotta`, `cottage`, `gazette`, `coastal`. Owner-approved on 2026-09-30 from the design canvas `Planner Styles.dc.html` (outside the repo). Each has its own cover (`templates/look_cover.html`), monthly page (`templates/look_monthly.html`), worksheet chrome and palette (`static/looks.css`) and typeface set. Covers carry no illustration, family name or year. Apply them as given; do not redesign, restyle or improve them.
- **Retired looks** (`designs.LEGACY`): `original` (the illustrated house cover) and `02` to `17`. They still build from old plan files but are not offered. None of `02` to `17` was ever finished; `03` Botanical and `06` School notebook were rejected outright. Their covers live in `templates/pages/cover.html` and `.design-02` to `.design-17` in `planner.css`, kept because the layouts build on `02`, `06`, `11` and `12`. Do not treat them as shippable and do not iterate on them.
- **Planner layouts** `02a` to `12c`: owner-supplied from the design export of 2026-09-30. Looks `02`, `06`, `11`, `12` crossed with a split, stacked or sidebar page structure, each adding a boxed monthly page and Weekly Plan and Daily Plan sheets. The cover is still the parent look's unfinished cover. Do not restyle them without the owner.
- **`blank`** hides illustration. A theme colours `blank` and the retired looks only.
- **Do not:** invent botanical, notebook or any other decoration without a human-approved reference; restyle a retired cover and call it a new look; replace chores, budget or months with daily modules unless asked; load old look CSS as a style guide.
- **If asked to add or change a look:** get a reference image or written layout the owner accepts; implement that one look in its own template and CSS and nothing else in the same pass; verify the cover in `python planner.py ui` at letter and at least one small size; stop.

## Locked decisions

- No real family names in the repo: not in docs, examples, tests, commit messages or run outputs. Use blank or made-up names (the code uses "Ramirez"). Personalisation happens in `family.yaml` or the UI, never by committing a run.
- The original illustrated house cover (`design: original`) is retired by the owner (2026-09-30), not restyled. It stays buildable as a legacy id so the printed run rebuilds as printed; do not restyle it and present it as a new look.
- The thirteen looks are owner-approved designs. Apply them as given; do not redesign, restyle or "improve" them. Looks `02`–`17` are legacy and unfinished. Do not invent cover art, florals or notebook chrome in chat without a human-approved reference image or written layout (see "Looks" above).
- Every value from YAML, CLI flags or the UI goes through the validators in `config.py`. New fields get a `check_*` helper and a test; nothing reaches a template or a file path unchecked.
- The local server answers only its own page. Keep all UI calls on the JSON `api()` helper in `ui.js`; a plain form post or `text/plain` fetch will get a 403.
- ICM rules from the conventions: references point one way (stages point to `_config/`, `shared/` and earlier stages' `output/`, never forward); one canonical home per fact; CONTEXT.md files route and stay under 80 lines; no em dashes; no spaces in file names.
- `out/` and root `family.yaml` are gitignored local scratch. A run's settings live only in `stages/02-customize/output/`; do not copy them to a root `family.yaml`. With no root file, `start-planner.bat` and plain `planner.py ui` open a blank planner; open a run with **Open a plan** or `planner.py ui -c <stage 02 yaml>`.
- One stage, one job; no coordinator script; reorder stages by renaming the numbered folders only.

## Environment notes

- Windows Smart App Control blocks Git for Windows' unsigned `libcurl-4.dll`, so HTTPS push and fetch fail or hang. This repo pushes over SSH with `core.sshCommand = C:/Windows/System32/OpenSSH/ssh.exe`. Do not switch the remote back to HTTPS.
- The owner runs pushes. When asked, give the git commands one at a time and wait for "done" between them. Last push (2026-10-03, `git push origin main`) was run by the agent because the owner asked for it in that message; it worked over SSH from the repo root.
- Any clone made before 2026-09-24 has the old history. Delete it and re-clone; never push from it, or the names and source pack return.
- The original source pack (reference planner PDF and 31 page JPGs) lives outside the repo at `..\planner-source-pack\`. Do not copy it back in; it must not be published.
- `git-filter-repo` is installed (`python -m git_filter_repo`) if history ever needs scrubbing again.
- To stop a test copy of the editor, kill only the PID listening on its port (`netstat -ano`), never every `python.exe`.
- **Restart the editor after any code change.** A running `planner.py ui` keeps the old Python in memory but serves the new `ui.js` from disk, which shows up as "unknown design" or "unknown typeface set" toasts and a blank preview. Stop the process on port 8733, start it again, then hard-refresh the browser (Ctrl+F5).
- VS Code may show "An Invalid Python interpreter is selected". That is the editor's own setting, not the project. The terminal's Python (3.14, `AppData\Local\Programs\Python\Python314`) runs everything fine; pick it under Select Python Interpreter to clear the popup.

## What to do on resume

1. Read this file, then `git status`. It should be clean. The batch A fixes sit on the local branch `batch-a-fixes` until the owner pushes and merges them; `main` has everything before that.
2. Run `python -m pytest`. All tests should pass.
3. If asked to print a book: route through stage 03 (`build`), then stage 04 review.
4. If asked to continue the editor work: take "Editor audit: still open" in order.
5. Worth doing: open `python planner.py ui` and exercise the colour editor by hand. With a look chosen: the theme cards should be hidden, the pickers should start from the look's colours, a replaced colour should survive download and reopen, and switching to a look with different colours should clear replacements with an Undo in the toast. Then pick `blank`: the theme cards return; click through every theme (especially `citrus`, `ocean`, `poppy`, `meadow`, `linen`, `amber`) to confirm the 2026-09-28 rework reads right on screen, not just in the hex values. Also scroll the TYPE picker, which now holds 40 sets, and pick one of the new ones; then pick a planner layout such as `06b` in the look picker and check the Weekly Plan, Daily Plan and a month at letter and at `5.5x8`.
6. If asked to continue look design, follow "Looks" above exactly: get an approved reference first, implement one look at a time, then stop. The thirteen looks are done; before printing one, build the whole book for that look and page through it, since only the cover and January were checked.
7. Making the repo public is a human call (GitHub Settings → Danger Zone → Change visibility). Nothing in the history blocks it.
8. Do not read previous run outputs (`stages/*/output/`) to learn style. `_config/` is the quality source.

> FIRST TURN: read the referenced docs ONE AT A TIME (no parallel tool calls, no batched reads). Parallel reads on the first turn can wedge a new session; sequential reads avoid it.
