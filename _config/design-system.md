# Design system

Canonical print rules for the Family Success Planner. Templates and `familyplanner/static/planner.css` implement these. Change a rule here first, then the CSS or templates.

## Page box

- Three paper sizes: `5.5x8` (5.5 by 8 in), `6x9` (6 by 9 in), and `letter` (8.5 by 11 in). Default is `letter`.
- One printed margin for every sheet, set on the page box in `templates/book.html` (`--page-pad-*`). Dense pages tighten interior spacing. They never shrink the outer margin.
- Print at 100% / Actual size. Do not fit-to-page. Use paper that matches `page_size`.

## Type

Three roles, filled by a named typeface set in config or a custom `display` / `script` / `body` trio. There are 52 sets, defined in `familyplanner/typefaces.py` and listed by `python planner.py typefaces`: six general sets (`elegant`, `classic`, `playful`, `modern`, `italics`, `neat`), two pairings for each retired look (for example `boho-brush`, once called `terracotta`; the old name still works), and one set for each of the thirteen looks (Swiss grid uses `grotesk-red`).

One rule for lettering: a look or layout sets its own typeface set, and a `fonts:` entry in the config (or a set picked in the editor) overrides it. The default book is the `editorial` look in `home-edition` (Bodoni Moda, Archivo). Blank and the retired looks have no set of their own, so they use `elegant` (Playfair Display, Great Vibes, Lato) unless `fonts:` names another.

- Display: chunky headings
- Script: handwritten greeting lines
- Body: worksheets, tables, footers
- Masthead titles (the stacked lines in the top centre) share one display size (`type_size.title`, default 30pt) and sit at the top of the header row, not vertically centred on the house art. Cover stack uses `type_size.cover`. Banners stay their own role; sliders in the visual editor change the four `type_size` values.
- The book has thirteen looks (`designs.LOOKS`): `editorial` (default), `midcentury`, `nordic`, `farmhouse`, `deco`, `swiss`, `retro`, `bauhaus`, `almanac`, `terracotta`, `cottage`, `gazette`, `coastal`. Each brings its own cover (`templates/look_cover.html`), monthly page (`templates/look_monthly.html`), worksheet chrome and colour palette (`static/looks.css`) and typeface set. Approved by the owner on 2026-09-30 from the design canvas `Planner Styles.dc.html`.
- Covers are type, colour and geometry only, with no illustration. As designed they print no family name and no year. Three opt-in settings, all off by default, add words in one small spot per look (`.lko-<look>` in `static/looks.css`), set in that look's own fonts and colours and placed in its open space without moving anything else: `cover_show_family` ("The [name] Family"), `cover_show_year` (`off`, `year`, or `custom` for the `cover_text` line) and `cover_line` (one extra line, 80 characters). Long lines step down in size (`cfg.cover_fit`: `.lko-fit2`, `.lko-fit3`), and a word too long for the spot breaks inside it. With all three off, a look cover is pixel-identical to the approved design. Cover and monthly sizes are in `--k` (1/408 of the page width).
- A look's palette goes over the theme, so a theme has no visible effect on a look or layout book; a config `palette:` block still wins. The editor shows theme cards only for books without their own colours (Blank and the retired looks), and its colour pickers start from the look's colours. `build` prints a note when a config names a theme the look ignores. Lettering follows the one rule under Type above.
- Look monthly pages close with their own write-on blocks, not the footer macro.
- Retired looks (`original`, `02`–`17`) still resolve so old plan files build, but are not offered in the picker.
- Planner layouts `02a` to `12c` cross one of looks `02`, `06`, `11`, `12` with a page structure (`a` split, `b` stacked bands, `c` sidebar). The body carries both classes (`design-06 design-06b`), so the look's paper and chrome still apply; the layout adds its own box style (`box-06b`) to its own cover (title, year and the twelve months at a glance), a boxed monthly page and the `weekly` and `daily` sheets. A layout book is 32 pages by default. Each layout family has its own typeface set: `02` ledger, `06` composition-book, `11` boardroom, `12` garden-party. Parts live in `templates/layout_kit.html`, `templates/layout_monthly.html`, `templates/pages/daily.html`, `templates/pages/weekly.html` and the "planner layouts" section at the end of `planner.css`. Sizes there are in `--u` (1/300 of the page width) so a sheet keeps its proportions at every page size. Added 2026-09-30 from the owner's design export.
- `blank` hides illustration.

Colour is twelve tokens on the palette (`navy`, `teal`, `pink`, `orange`, `green`, `purple`, `blue`, `red`, `brown`, `ink`, `paper`, `rule`). The default `linen` theme is warm beige and ivory. `classic` is the original bright printable. Each named theme should read as its name at a glance (`citrus` stays lemon/lime/tangerine, `ocean` stays blue/green/seafoam with no coral or red, `forest` stays green/brown, `poppy` stays pink/red with no cyan). When adding or editing a theme, keep its twelve tokens inside that colour family rather than defaulting to a generic dark-navy-plus-bright-accent scheme. A config `palette:` block overrides individual tokens.

## Cards and chrome

- `.card-tab` is 8pt everywhere. If a label does not fit, shorten the label.
- Every page ends with the shared footer macro, except cover, belongs_to, how_to_use, and values, which have their own bottom art.
- Illustrations are inline SVG in `templates/art.html` and the icon sprite in `templates/icons.html`. No network images at build time.

## Months

Twelve monthly sheets share `monthly.html`. Dated grids use `year` and `week_starts`. `dated_months: false` prints blank grids.

- Blank and the retired looks print each month's accent, motif, tagline and footer line from config.
- The thirteen looks use `look_monthly.html` and the layouts use `layout_monthly.html`. Both print the month name with the look's own wording and write-on blocks; they ignore the config's taglines, motifs, accents and footer lines.

Available motifs: snowman, hearts, sprout, tulips, flowers, sun, beach, school, pumpkin, leaves, snowflake.
