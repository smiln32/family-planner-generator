# Design system

Canonical print rules for the Family Success Planner. Templates and `familyplanner/static/planner.css` implement these. Change a rule here first, then the CSS or templates.

## Page box

- Three paper sizes: `5.5x8` (5.5 by 8 in), `6x9` (6 by 9 in), and `letter` (8.5 by 11 in). Default is `letter`.
- One printed margin for every sheet, set on the page box in `templates/book.html` (`--page-pad-*`). Dense pages tighten interior spacing. They never shrink the outer margin.
- Print at 100% / Actual size. Do not fit-to-page. Use paper that matches `page_size`.

## Type

Three roles, filled by a named typeface set in config (`elegant`, `classic`, `playful`, `modern`, `italics`, `neat`) or a custom `display` / `script` / `body` trio. The factory default is `elegant` (Playfair Display, Great Vibes, Lato).

- Display: chunky headings
- Script: handwritten greeting lines
- Body: worksheets, tables, footers
- Masthead titles (the stacked lines in the top centre) share one display size (`type_size.title`, default 30pt) and sit at the top of the header row, not vertically centred on the house art. Cover stack uses `type_size.cover`. Banners stay their own role; sliders in the visual editor change the four `type_size` values.
- `design: original` is the illustrated Family Success Planner (house scene, side badges, footer chips).
- Looks `02`–`10` each have their own **family title cover** (stacked Family / Success / Planner, motto, family line, five pills, empty lower field). They do not show the house. Interior family sheets keep their jobs; chrome follows that look.
- Looks `11`–`16` replace the cover with a **daily planner page** (executive, bloom, boho, scrapbook, street, reset). Interiors stay family worksheets with that look’s chrome.
- `blank` hides illustration.

Colour is twelve tokens on the palette (`navy`, `teal`, `pink`, `orange`, `green`, `purple`, `blue`, `red`, `brown`, `ink`, `paper`, `rule`). The default `linen` theme is sage, dusty rose and clay. `classic` is the original bright printable. A config `palette:` block overrides individual tokens.

## Cards and chrome

- `.card-tab` is 8pt everywhere. If a label does not fit, shorten the label.
- Every page ends with the shared footer macro, except cover, belongs_to, how_to_use, and values, which have their own bottom art.
- Illustrations are inline SVG in `templates/art.html` and the icon sprite in `templates/icons.html`. No network images at build time.

## Months

Twelve monthly sheets share `monthly.html`. Each month has accent, motif, tagline, and footer line from config. Dated grids use `year` and `week_starts`. `dated_months: false` prints blank grids.

Available motifs: snowman, hearts, sprout, tulips, flowers, sun, beach, school, pumpkin, leaves, snowflake.
