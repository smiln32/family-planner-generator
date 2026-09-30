# Design system

Canonical print rules for the Family Success Planner. Templates and `familyplanner/static/planner.css` implement these. Change a rule here first, then the CSS or templates.

## Page box

- Three paper sizes: `5.5x8` (5.5 by 8 in), `6x9` (6 by 9 in), and `letter` (8.5 by 11 in). Default is `letter`.
- One printed margin for every sheet, set on the page box in `templates/book.html` (`--page-pad-*`). Dense pages tighten interior spacing. They never shrink the outer margin.
- Print at 100% / Actual size. Do not fit-to-page. Use paper that matches `page_size`.

## Type

Three roles, filled by a named typeface set in config or a custom `display` / `script` / `body` trio. Six general sets (`elegant`, `classic`, `playful`, `modern`, `italics`, `neat`) plus two pairings per look, defined in `familyplanner/typefaces.py` and listed by `python planner.py typefaces`. A pairing is a suggestion; choosing a look does not switch the set. The factory default is `elegant` (Playfair Display, Great Vibes, Lato).

- Display: chunky headings
- Script: handwritten greeting lines
- Body: worksheets, tables, footers
- Masthead titles (the stacked lines in the top centre) share one display size (`type_size.title`, default 30pt) and sit at the top of the header row, not vertically centred on the house art. Cover stack uses `type_size.cover`. Banners stay their own role; sliders in the visual editor change the four `type_size` values.
- `design: original` is the illustrated Family Success Planner (house scene, side badges, footer chips).
- Looks `02`–`10` swap in a different **family title cover** (markup in `cover.html`). They do not show the house. Quality is unfinished; see `shared/looks-handoff.md`.
- Looks `11`–`17` swap the cover for a **daily planner page**. Interiors stay family worksheets with that look’s chrome. Unfinished.
- Planner layouts `02a` to `12c` cross one of looks `02`, `06`, `11`, `12` with a page structure (`a` split, `b` stacked bands, `c` sidebar). The body carries both classes (`design-06 design-06b`), so the look's paper and chrome still apply; the layout adds its own box style (`box-06b`) to a boxed monthly page and to the `weekly` and `daily` sheets. Parts live in `templates/layout_kit.html`, `templates/layout_monthly.html`, `templates/pages/daily.html`, `templates/pages/weekly.html` and the "planner layouts" section at the end of `planner.css`. Sizes there are in `--u` (1/300 of the page width) so a sheet keeps its proportions at every page size. Added 2026-09-30 from the owner's design export; see `shared/looks-handoff.md`.
- `blank` hides illustration.

Colour is twelve tokens on the palette (`navy`, `teal`, `pink`, `orange`, `green`, `purple`, `blue`, `red`, `brown`, `ink`, `paper`, `rule`). The default `linen` theme is warm beige and ivory. `classic` is the original bright printable. Each named theme should read as its name at a glance (`citrus` stays lemon/lime/tangerine, `ocean` stays blue/green/seafoam with no coral or red, `forest` stays green/brown, `poppy` stays pink/red with no cyan). When adding or editing a theme, keep its twelve tokens inside that colour family rather than defaulting to a generic dark-navy-plus-bright-accent scheme. A config `palette:` block overrides individual tokens.

## Cards and chrome

- `.card-tab` is 8pt everywhere. If a label does not fit, shorten the label.
- Every page ends with the shared footer macro, except cover, belongs_to, how_to_use, and values, which have their own bottom art.
- Illustrations are inline SVG in `templates/art.html` and the icon sprite in `templates/icons.html`. No network images at build time.

## Months

Twelve monthly sheets share `monthly.html`. Each month has accent, motif, tagline, and footer line from config. Dated grids use `year` and `week_starts`. `dated_months: false` prints blank grids.

Available motifs: snowman, hearts, sprout, tulips, flowers, sun, beach, school, pumpkin, leaves, snowflake.
