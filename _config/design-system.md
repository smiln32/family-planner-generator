# Design system

Canonical print rules for the Family Success Planner. Templates and `familyplanner/static/planner.css` implement these. Change a rule here first, then the CSS or templates.

## Page box

- Default paper is US letter, 8.5 by 11 inches. `page_size: a4` is the other option.
- One printed margin for every sheet, set on the page box in `templates/book.html` (`--page-pad-*`). Dense pages tighten interior spacing. They never shrink the outer margin.
- Print at 100% / Actual size. Do not fit-to-page.

## Type

Three roles, filled by a named typeface set in config (`classic`, `rounded`, `modern`, `elegant`, `bubbly`, `neat`) or a custom `display` / `script` / `body` trio.

- Display: chunky headings
- Script: handwritten greeting lines
- Body: worksheets, tables, footers

Colour is twelve tokens on the palette (`navy`, `teal`, `pink`, `orange`, `green`, `purple`, `blue`, `red`, `brown`, `ink`, `paper`, `rule`). Themes are starting points built as complementary pairs (except `classic` and `slate`); a config `palette:` block overrides individual tokens.

## Cards and chrome

- `.card-tab` is 8pt everywhere. If a label does not fit, shorten the label.
- Every page ends with the shared footer macro, except cover, belongs_to, how_to_use, and values, which have their own bottom art.
- Illustrations are inline SVG in `templates/art.html` and the icon sprite in `templates/icons.html`. No network images at build time.

## Months

Twelve monthly sheets share `monthly.html`. Each month has accent, motif, tagline, and footer line from config. Dated grids use `year` and `week_starts`. `dated_months: false` prints blank grids.

Available motifs: snowman, hearts, sprout, tulips, flowers, sun, beach, school, pumpkin, leaves, snowflake.
