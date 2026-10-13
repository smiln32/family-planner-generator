# Family Success Planner generator

[![tests](https://github.com/smiln32/family-planner-generator/actions/workflows/tests.yml/badge.svg)](https://github.com/smiln32/family-planner-generator/actions/workflows/tests.yml)

Tests run on Windows and Linux for each push and pull request, and the PDF tests skip when no browser is installed.

Generates the adorable printable planner pages as a print-ready PDF, for any
year, any family, any colours.

**If you just want to make a book:** double-click `start-planner.bat`. Keep that
window open. Your browser is the app. Click **Make PDF** when the pages look
right.

```
python planner.py ui        # visual editor + live preview
python planner.py build     # or straight to out/2027-Family-Planner.pdf
```

That's it. No config file needed to get the default 30-page planner: the
Editorial look, set in Bodoni Moda and Archivo. The typefaces for every look
and every built-in typeface set are already in the repo, in
`familyplanner/static/fonts/`, with each family's licence (see the README
there). There is no download step.

## Workspace layout

This repo is an [Interpretable Context Methodology](https://arxiv.org/abs/2603.16021) workspace. Numbered `stages/` folders are the agent pipeline (intake → customize → build → review). Markdown contracts tell an agent what to load. `planner.py` is the local app that does the mechanical rendering.

Start at `CLAUDE.md` and `CONTEXT.md`. Factory rules live in `_config/`. Per-run files go in `stages/*/output/`.

## What it makes

Thirty pages at the chosen paper size (5.5×8, 6×9, or 8.5×11), with real vector text (searchable,
crisp at any zoom, no upscaled bitmaps):

| # | Page | # | Page |
|---|------|---|------|
| 1 | Cover | 12 | Family Health & Wellness Tracker |
| 2 | This Planner Belongs To | 13 | Emergency Contacts & Important Info |
| 3 | How To Use This Planner | 14 | School & Activities Schedule |
| 4 | Family Vision & Mission | 15 | Family Time Planner |
| 5 | Family Goals | 16-27 | January - December monthly planners |
| 6 | Family Values Worksheet | 28 | Vacation & Travel Planner |
| 7 | Annual Family Calendar | 29 | Home Maintenance Checklist |
| 8 | Family Budget Overview | 30 | Year-End Family Reflection |
| 9 | Household Chores Planner | | |
| 10 | Weekly Meal Planning Sheet | | |
| 11 | Grocery Shopping List | | |

## Looks

Thirteen looks, each with its own cover, monthly page, worksheet chrome,
colours and typefaces. Covers are type, colour and geometry only. As
designed they print no name or date; you can turn those on (see Cover
options below).

`editorial` (default) `midcentury` `nordic` `farmhouse` `deco` `swiss`
`retro` `bauhaus` `almanac` `terracotta` `cottage` `gazette` `coastal`

```
python planner.py build --design deco
```

A look brings its own colours and its own lettering. A `theme` recolours
any look (colours the theme does not name stay the look's own), and your
own `palette:` block goes over both. A `fonts:` entry replaces the look's
typeface set. Leave `theme` and `fonts` unset to print the look as designed.

### Cover options

Three settings put your own words on a look cover. All three are off at
first, so the cover prints exactly as designed. Whatever you turn on prints
in one small spot, in that look's own fonts and colours.

- **`cover_show_family: true`** prints "The [family name] Family". It needs a
  `family_name`.
- **`cover_show_year`** is `off`, `year` (the planner year) or `custom` (the
  `cover_text` line, such as `2026–27`).
- **`cover_line`** is one extra line of your own, such as `Our year together`.

Text limits: family name 60 characters, `cover_text` and `cover_line` 80
each. Longer lines print smaller so they stay in the spot. The editor has
the same settings under **Personalize the cover**. On the command line:

```
python planner.py build -n Ramirez --cover-show-family
python planner.py build --cover-show-year custom --cover-text "2026–27"
python planner.py build --cover-line "Our year together"
python planner.py build -c family.yaml --no-cover-show-family
```

Blank, the retired looks and the layouts ignore these three. Their covers
print the family name and the year by themselves (see `cover_year` below).

## The visual editor

```
python planner.py ui
```

Opens a local app at `http://127.0.0.1:8733` with a live preview of the real
rendered page - same code path as `build`, so what you see is what prints.

On Windows, `start-planner.bat` does this without typing a command. If the
planner is already running, it just opens the browser again.

- year, family name (optional), paper size, week start, dated or blank grids
- page looks named in plain language, each with a strip of its own colours
- **Personalize the cover**: the family name, the year (or your own text) and
  one extra line on a look cover, all off at first
- theme cards for every look, starting with "Design's own colours", and a colour picker to replace any of the twelve print colours
- paper, week start and lettering size sit under **Paper and lettering size**
- tracker rows added and named inline
- every page toggled in or out; click a page name to jump the preview to it
- **Make PDF** builds the book and offers to open it
- **Download plan** saves a `.md` file you can keep, use next year, or send to a friend
- **Open a plan** loads that file (or an older `family.yaml`)
- **Start over** clears the name and people
- `Ctrl/Cmd+B` builds, `Ctrl/Cmd+S` downloads the plan file

It binds to loopback only and runs builds on request, so treat it as a local
tool rather than something to expose on a network.

## Commands

```
python planner.py ui                 # visual editor with live preview
python planner.py build              # PDF into out/
python planner.py build --png        # ...plus one 300 dpi PNG per page
python planner.py build --dpi 150    # smaller PNGs
python planner.py build --html-only  # just the HTML, to inspect in a browser
python planner.py build -y 2031      # a different year
python planner.py build -n Ramirez   # family name, used in the file name
python planner.py build -n Ramirez --cover-show-family   # ...and on a look cover
python planner.py build --cover-show-year year           # the year on a look cover
python planner.py build --cover-line "Our year together" # one extra cover line
python planner.py build --undated    # blank month grids instead of real dates
python planner.py build --only cover,months,year_end

python planner.py build --design coastal --theme adventure   # a look, recoloured
python planner.py build --fonts italics  # different typefaces

python planner.py pages              # list what would be built
python planner.py themes             # list the colour presets
python planner.py chrome             # every design's component treatments (--current, --diff)
python planner.py typefaces          # list the typeface sets
python planner.py months             # per-month colours, motifs and taglines
python planner.py init               # write a starter family.yaml
python planner.py fonts              # fetch your own custom typefaces (built-in ones ship in the repo)
python planner.py fonts --all        # refresh or re-download every built-in set
python planner.py fonts --looks      # refresh or re-download the thirteen looks' sets
```

`build` picks up `./family.yaml` automatically if it exists; `-c other.yaml`
points it somewhere else. Command-line flags always win over the file.

## The digital edition

```
python planner.py build --linked
```

Adds tab-rail navigation and a linked contents page, for reading on a tablet
(GoodNotes, Notability, any PDF reader):

- a **Contents** sheet at the front, every line tapping through to its page
- a **month tab rail** down the outside edge of every sheet, the current month
  highlighted, plus a home tab back to the contents
- 434 real PDF link annotations across 31 pages, not just visual tabs

The rail sits inside the same page box, so the trim size and printed margins
are identical to the print build. The two editions come from one command each:

```
python planner.py build            # 30 pages, flat, for paper
python planner.py build --linked   # 31 pages, tappable, for a tablet
```

## Customising

```
python planner.py init      # writes family.yaml, fully commented
```

### Ready-made themes

Colour presets ship with the generator. A theme recolours any look or
layout: its colours go over the look's own, and the colours it does not name
stay the look's. With no theme a look prints as designed; Blank and the
retired looks then print in `linen`, warm taupe, dusty rose and clay on ivory
paper. `classic` keeps the original bright jewel-tone printable.

```
python planner.py themes                       # list them with swatches
python planner.py build --theme pastel                        # editorial, recoloured
python planner.py build --design coastal --theme adventure    # another look
python planner.py build --design blank --theme berry --only year_goals --png   # one page
```

`linen` `classic` `amber` `berry` `bold` `citrus` `forest` `meadow` `ocean` `pastel` `poppy` `blues` `adventure` `goal`

`adventure` and `goal` set only the headings, main accent, weekend red and
paper, so most of the look shows through. Set `theme: adventure` in your
config to make it the default. A theme is only a starting point - your own
`palette:` block is applied on top of the look and the theme, so you can take
`forest` and override just its pink, or replace one colour on any look with
no theme at all.

### Typefaces

Fifty-two typeface sets ship with the generator: six general ones, in the
table below, two pairings for each retired look, and one set for each of the
thirteen looks (Swiss grid uses `grotesk-red`). Each fills three roles:
`display` (chunky headings), `script` (handwritten lines) and `body`
(everything else). The set once called `terracotta` is now `boho-brush`
(Tenor Sans, Caveat Brush, Mulish), so it is not mixed up with the
Terracotta look, which uses `home-base`; old files that say
`fonts: terracotta` still work.

```
python planner.py typefaces                    # see the sets
python planner.py build --fonts italics        # build with it
```

The font files for all fifty-two sets are in the repo, so any set builds
straight away. `python planner.py fonts --all` refreshes or re-downloads them
from Google Fonts if you ever need to (`--force` fetches every file again).

| set | display | script | body |
|---|---|---|---|
| `elegant` | Playfair Display | Great Vibes | Lato |
| `classic` | Open Sans | Open Sans | Open Sans |
| `playful` | Fredoka | Pacifico | Nunito |
| `modern` | Oxygen | Oxygen | Oxygen |
| `italics` | Courgette | Courgette | Courgette |
| `neat` | Montserrat | Kalam | Open Sans |

The other sets have names like `home-edition`, `sunday-kitchen`, `ledger`,
`boho-brush` and `wedding-album`; `python planner.py typefaces` lists all of
them. A look or layout sets its own lettering (Editorial uses `home-edition`:
Bodoni Moda and Archivo) unless you set `fonts:`. Blank and the retired looks
use `elegant` unless you set `fonts:`.

Or name **any** Google Fonts families you like:

```yaml
fonts:
  display: Chewy
  script: Gloria Hallelujah
  body: Rubik
```

Families outside the built-in sets are not in the repo, so run
`python planner.py fonts` once to download them. The visual editor picks a
custom trio up too: it appears in TYPE as a **Custom** card, selected, above
the presets. If a family does not publish a
weight the planner asks for, the closest available weight is substituted and
the swap is reported, rather than the build failing.

### Planner layouts

Twelve layouts turn the book into a boxed planner: `02a` `02b` `02c`, `06a`
`06b` `06c`, `11a` `11b` `11c`, `12a` `12b` `12c`. The digits pick a page
look, the letter a structure (`a` split, `b` stacked bands, `c` sidebar).
A layout swaps in a boxed monthly page and adds a Weekly Plan and a Daily
Plan before the months, so the book is 32 pages. The family worksheets stay.

```
python planner.py build --design 06b     # set in composition-book, its own typefaces
```

Set `design: 06b` in your config, or pick it in the editor's look picker.
Each layout has its own cover (title, year and the twelve months at a
glance) and its own typeface set: `02` ledger, `06` composition-book, `11`
boardroom, `12` garden-party. Set `fonts:` to use another.

The things people change most:

- **`year`** - monthly grids and the year-at-a-glance page are dated from this.
- **`cover_text`** - printed on the Family Goals and annual calendar
  mastheads instead of `year` (for example `Our` or `2027-2028`), and on the
  cover of Blank, the retired looks and the layouts. A look cover prints it
  only with `cover_show_year: custom`. Leave empty to use the year.
- **`family_name`** - used in the output filename and printed on the cover of
  Blank, the retired looks and the layouts. A look cover prints it only with
  `cover_show_family: true`.
- **`cover_show_family`**, **`cover_show_year`**, **`cover_line`** - the
  optional words on a look cover; see Cover options above.
- **`members`** - one row per person on the health tracker. Add or remove
  entries to change how many rows it has; names are optional.
- **`theme`** - a colour preset laid over the look's own colours, on any
  look or layout, and applied before `palette`. Leave it out to print the
  look as designed.
- **`fonts`** - a typeface set name, or a mapping of
  `display`/`script`/`body` to any Google Fonts families.
- **`palette`** - twelve colour tokens. The worksheets use them by role
  (one structure colour for headers and tabs, one weekend accent, four season
  colours for the months; see `_config/design-system.md`), so a changed token
  follows into every page that role appears on.
- **`months`** - each month's accent colour (`season` by default: its season's
  colour), seasonal motif, greeting strip and footer line. Positional, January first, and partial lists are fine. Only
  Blank and the retired looks print these; a look or layout month page uses
  its own wording.
- **`pages`** - the running order. Comment out a line to drop that page.
- **`dated_months: false`** - blank grids to fill in by hand, which is what the
  original printable did. On Blank, the retired looks and the layouts, the
  cover year becomes fill-in blanks unless you set `cover_text` (print that
  line), `cover_year: omit` (hide it) or `cover_year: print` (keep the
  digits).

Available motifs: `snowman`, `hearts`, `sprout`, `tulips`, `flowers`, `sun`,
`beach`, `school`, `pumpkin`, `leaves`, `snowflake`.

## Printing

Print at **100% / "Actual size"**. Do not let the printer "fit to page" - that
shrinks the sheet and throws off the margins. The pages are designed for
single-sided printing on paper that matches the size you picked (`page_size`:
`5.5x8`, `6x9`, or `letter` for 8.5×11).

## Consistency rules

The book only looks right if every sheet obeys the same rules. Three are
enforced centrally rather than per page:

- **One printed margin.** `--page-pad-*` in `book.html` sets the page box for
  all 30 sheets. Dense pages buy room with interior spacing, never by shrinking
  their margin - so nothing shifts when you flip through the stack.
- **One card-tab size.** `.card-tab` is 8pt everywhere. If a label does not
  fit, shorten the label rather than adding a per-page override.
- **One way to close a page.** Every page ends with `{{ footer("...") }}`,
  except the four with their own bottom art (cover, belongs_to, how_to_use,
  values).

Colour, typeface and page-order choices are all named tokens resolved in one
place, so `--theme`, `--fonts` and `palette:` reach every page at once.

## How it works

- Each page is a Jinja template in `familyplanner/templates/pages/` that
  renders one `<section class="page">`.
- `familyplanner/static/planner.css` is the whole design system: page box,
  type scale, cards, write-on rules, calendar grids and tables.
- Illustrations are hand-drawn inline SVG (`familyplanner/templates/art.html`)
  and a 72-icon sprite (`familyplanner/templates/icons.html`). Nothing is loaded
  from the network at build time, so the HTML is fully self-contained.
- `familyplanner/render.py` renders the book to one HTML file, then drives a
  headless Chrome/Edge/Chromium to print it to PDF and to screenshot pages.

### Adding a page

1. Write `familyplanner/templates/pages/my_page.html` - start by copying
   `example_gratitude.html`; `{% from "macros.html" import ... with context %}`
   gives you the masthead, cards, checklists, numbered lines and footer. Name
   the page on its first line:

       {# title: My Page #}

   Without that line the title is derived from the filename. Templates are
   discovered from the folder, so there is no list to register it in.
2. Add the slug to `pages:` in your config, or to `DEFAULT_PAGES` in
   `familyplanner/config.py` to put it in the default book. Also add it to
   `_config/page-catalog.md` so the agent pipeline stays in sync.

Preview it on its own while you work:

```
python planner.py build --only my_page --png --dpi 110
```

Filenames starting with `_` are treated as partials and skipped, as is
`monthly.html`, which the `months` keyword renders twelve times.

## Requirements

Python 3.10+ and a Chromium-family browser (Chrome, Edge, Chromium or Brave).
Install and check steps, including tests, are in
[`stages/03-build/references/tool-setup.md`](stages/03-build/references/tool-setup.md).

The typefaces ship in the repo, so there is nothing to download. They are
under the SIL Open Font License 1.1 (77 families) or the Apache License 2.0
(6 families); each family's licence is in `familyplanner/static/fonts/licenses/`.
Both licences let you print, give away or sell the PDFs you make. If a font
file is missing, the pages fall back to system fonts and still build.

## Differences from the original printable

- The original's twelve monthly pages had **blank** grids, plus one extra dated
  January - 31 sheets with a duplicate. This generates the twelve months
  correctly dated for whatever year you ask for, so it's 30 unique pages. Use
  `--undated` for the original's blank grids.
- The original's artwork is AI-generated raster art baked into the page.
  Here the illustrations are redrawn as flat vector SVG in the same style, so
  they stay sharp at any size and re-colour with the palette.
