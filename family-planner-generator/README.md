# Family Success Planner generator

Generates the adorable printable planner pages as a print-ready PDF, for any
year, any family, any colours.

```
python planner.py fonts     # once - downloads the three display fonts
python planner.py ui        # visual editor + live preview
python planner.py build     # or straight to out/2027-Family-Planner.pdf
```

That's it. No config file needed to get the default 30-page planner.

## What it makes

Thirty 8.5x11" pages at exactly letter size, with real vector text (searchable,
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

## The visual editor

```
python planner.py ui
```

Opens a local app at `http://127.0.0.1:8733` with a live preview of the real
rendered page - same code path as `build`, so what you see is what prints.

- year, family name, paper size, week start, dated or blank grids
- colour themes and typeface sets as pickable cards, applied instantly
- tracker rows added and named inline
- every page toggled in or out, with a `view` button to jump the preview to it
- **Build PDF** runs the real build; **Save config** writes `family.yaml`
- `Ctrl/Cmd+B` builds, `Ctrl/Cmd+S` saves

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
python planner.py build -n Ramirez   # "The Ramirez Family" on the cover
python planner.py build --undated    # blank month grids instead of real dates
python planner.py build --only cover,months,year_end

python planner.py build --theme berry    # recolour with a preset
python planner.py build --fonts rounded  # different typefaces

python planner.py pages              # list what would be built
python planner.py themes             # list the colour presets
python planner.py typefaces          # list the typeface sets
python planner.py months             # per-month colours, motifs and taglines
python planner.py init               # write a starter family.yaml
python planner.py fonts              # download the display fonts
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

Seven colour presets ship with the generator:

```
python planner.py themes                       # list them with swatches
python planner.py build --theme pastel         # whole book
python planner.py build --theme berry --only year_goals --png   # one page
```

`classic` `pastel` `bold` `ocean` `berry` `forest` `slate`

Set `theme: pastel` in your config to make it the default. A theme is only a
starting point - your own `palette:` block is applied on top, so you can take
`forest` and override just its pink.

### Typefaces

Six typeface sets ship with the generator. Each fills three roles: `display`
(chunky headings), `script` (handwritten lines) and `body` (everything else).

```
python planner.py typefaces                    # see the sets
python planner.py fonts --fonts rounded        # download that set
python planner.py build --fonts rounded        # build with it
```

| set | display | script | body |
|---|---|---|---|
| `classic` | Fredoka | Pacifico | Nunito |
| `rounded` | Baloo 2 | Caveat | Quicksand |
| `modern` | Poppins | Sacramento | Inter |
| `elegant` | Playfair Display | Great Vibes | Lato |
| `bubbly` | Baloo 2 | Pacifico | Rubik |
| `neat` | Montserrat | Kalam | Open Sans |

Or name **any** Google Fonts families you like:

```yaml
fonts:
  display: Chewy
  script: Gloria Hallelujah
  body: Rubik
```

Then `python planner.py fonts` downloads them. The visual editor picks a
custom trio up too: it appears in TYPE as a **Custom** card, selected, above
the six presets. If a family does not publish a
weight the planner asks for, the closest available weight is substituted and
the swap is reported, rather than the build failing.

The things people change most:

- **`year`** - monthly grids and the year-at-a-glance page are dated from this.
- **`family_name`** - printed on the cover and used in the output filename.
- **`members`** - one row per person on the health tracker. Add or remove
  entries to change how many rows it has; names are optional.
- **`theme`** - a colour preset applied before `palette`.
- **`fonts`** - a typeface set name, or a mapping of
  `display`/`script`/`body` to any Google Fonts families.
- **`palette`** - twelve colour tokens. Change `teal` once and every teal
  element across all thirty pages follows.
- **`months`** - each month's accent colour, seasonal motif, greeting strip and
  footer line. Positional, January first, and partial lists are fine.
- **`pages`** - the running order. Comment out a line to drop that page.
- **`dated_months: false`** - blank grids to fill in by hand, which is what the
  original printable did.

Available motifs: `snowman`, `hearts`, `sprout`, `tulips`, `flowers`, `sun`,
`beach`, `school`, `pumpkin`, `leaves`, `snowflake`.

## Printing

Print at **100% / "Actual size"**. Do not let the printer "fit to page" - that
shrinks the sheet and throws off the margins. The pages are designed for
single-sided printing on letter paper; set `page_size: a4` for A4.

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
- Illustrations are hand-drawn inline SVG (`templates/art.html`) and a 72-icon
  sprite (`templates/icons.html`). Nothing is loaded from the network at build
  time, so the HTML is fully self-contained.
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
   `config.py` to put it in the default book.

Preview it on its own while you work:

```
python planner.py build --only my_page --png --dpi 110
```

Filenames starting with `_` are treated as partials and skipped, as is
`monthly.html`, which the `months` keyword renders twelve times.

## Requirements

- Python 3.10+
- `Jinja2` and `PyYAML` (`pip install -r requirements.txt`)
- Google Chrome, Microsoft Edge, Chromium or Brave, for the PDF step. The
  build finds it automatically; override with `--browser PATH` or by setting
  `CHROME_PATH`.

The three display fonts (Fredoka, Nunito, Pacifico) are optional. Without them
the pages fall back to system fonts and still build; with them they look right.
All three are SIL Open Font License, so the PDFs you make are yours to print,
give away or sell.

## Differences from the original printable

- The original's twelve monthly pages had **blank** grids, plus one extra dated
  January - 31 sheets with a duplicate. This generates the twelve months
  correctly dated for whatever year you ask for, so it's 30 unique pages. Use
  `--undated` for the original's blank grids.
- The original's artwork is AI-generated raster art baked into the page.
  Here the illustrations are redrawn as flat vector SVG in the same style, so
  they stay sharp at any size and re-colour with the palette.
