# Chrome catalog

The contract for the chrome axis (`design`). Phase 2 step 3, 2026-10-12; step 4 (the variants that print it), 2026-10-13; step 5 (recipes: composition, type scale, text colour, content exceptions), 2026-10-13.

## What it is

The catalog is the authoritative definition of each design's intended component treatments: how its cards, headings, meta strips, tables, check boxes, numbered marks, write-on lines, annual calendar, labels, footer, ornaments and page edge are meant to look. Colour is not here (see "Colour roles" in `design-system.md`); the catalog covers shape and placement, which a palette then colours.

- Source of truth: `familyplanner/chrome.py` (`CATALOG`, one `Chrome` entry per design, with its prose and its two `Components` specs). Per-design prose lives there, not in this file.
- How to read it: `python planner.py chrome` (intended treatments), `chrome --current` (what each design prints today), `chrome --diff` (only where the two differ).
- Each entry holds `components` (intended) and `current` (what prints today, per the override audit of 2026-10-12, inherited defaults included), so the gap is explicit per design, and `approved`: whether the owner has approved the intended spec, so that it prints. `Chrome.active` is the spec that prints: `components` when approved, else `current`.
- How it prints (step 4): `render.render_html` writes `active` on `<body>` as one `c-<field>-<value>` class per field and passes it to the templates as `cc`. `familyplanner/static/chrome.css` (loaded after `planner.css`, before `looks.css`) holds one block per value that differs from the shared chrome's base value, selected by those classes: the catalog-driven variants of the shared components (meta strips, table heads and corners, check boxes, numbered marks and day tags, the annual calendar's tiles and heads, labels). Template branches read `cc` only where CSS cannot do the job: the Important Dates bullet (`annual_calendar.html`) and the footer hearts (`macros.html`); the table head and day tag fills moved from inline styles to classes (`th-fill`, `pill we`) so a variant can lift them. No template is duplicated per design.

## Rules

1. Every design is fully resolved. An entry may be built from a reusable family base, but what is stored has every field set to a vocabulary value. Nothing inherits at use time.
2. Blank is one explicit entry, not the implicit default. The shared CSS defaults it prints are written into its entry like any other design's.
3. The vocabulary is closed (`chrome.VOCAB`): a value outside it fails at import. Refine a name by changing the vocabulary and every entry that uses it.
4. `palette_ref` and `fonts_ref` are references to the design's own palette and typeface set (`designs.look_palette`, `designs.look_fonts`; `linen` and `elegant` for Blank and `original`), never copies.
5. The retired looks `02` to `17` have no entry (locked, not offered); `original` has one, locked, with intended equal to current. A layout that builds on a retired look has its own entry. A retired look without an entry renders with the shared defaults (`chrome.SHARED`) as `cc` and no `c-` classes.
6. The shared chrome in `planner.css` is the base value of every field (the rounded `boxed` strip, `filled` table heads with `rounded` corners, `rounded` checks, `circle` marks, `pill` month heads on `rounded` tiles, `caps-heavy` labels, the heart bullet, dotted lines). A base value has no rule in `chrome.css`; a value that differs has one block.
7. A new value for an existing field, or a new block for an existing value, must reproduce today's look for every design that already carries that value through its own CSS (Swiss grid's square checks and marks, the layouts' square table corners): the same computed value, so the design prints pixel for pixel as before. Prove it as step 4 did (HANDOFF.md, "Step 4"): render the unapproved designs before and after and diff the pixels.
8. Fields the look CSS already produces per design (`corners`, `heads`, `lines`, `footer`, `page`) have no block in `chrome.css` yet; the body carries them for a later step.

## Vocabulary

One line per field; values in order.

| Field | Values | Meaning |
|---|---|---|
| `corners` | `square`, `soft`, `rounded`, `pill`, `arch` | Card body corners (the strip's own shape is the `strip` field) |
| `heads` | `bar`, `rule`, `text`, `outlined`, `pill`, `tape`, `inset`, `script` | A card's section heading: filled bar, label over a rule, plain text, outlined label, pill, tape label, label set into the frame line, script heading |
| `strip` | `boxed`, `framed`, `ruled`, `bare` | The meta strip at the top of a worksheet: the shared rounded box, a square frame in the frame colour, a ruled row, bare |
| `table_head` | `filled`, `rule`, `outlined` | A table's header row |
| `table_corners` | `square`, `rounded` | The header row's top corners |
| `checks` | `square`, `rounded`, `round` | Check boxes |
| `marks` | `circle`, `square`, `text` | Numbered marks: filled circle, filled square, bare number |
| `lines` | `dotted`, `solid`, `hairline` | Write-on lines |
| `calendar_head` | `pill`, `bar`, `rule`, `text` | The month heading on the annual calendar's tiles |
| `calendar_tile` | `rounded`, `square`, `open` | The tile: rounded box, square box, no box |
| `labels` | `caps-heavy`, `caps-light`, `lower`, `sentence`, `italic` | Section labels, column heads and tab text |
| `footer` | `caps`, `script`, `rule`, `lower`, `fleuron` | The page footer line |
| `ornaments` | `none`, `hearts`, `sprigs`, `dots`, `stripe`, `frame`, `corner` | The design's own ornament set beyond the page edge |
| `page` | `plain`, `band`, `frame`, `stripe`, `ruled` | The page edge: nothing, a band across the top, an inset frame, a stripe down one side, ruled paper |

## Families

`minimal` (editorial, nordic, swiss, blank), `classic` (deco, almanac, gazette, 11a to 11c), `botanical` (cottage), `modern-geometric` (midcentury, bauhaus, terracotta, 02a to 02c), `coastal` (coastal), `rustic` (farmhouse), `playful` (retro, 06a to 06c, 12a to 12c), `legacy` (original). A family groups shared treatments for reuse in `chrome.py`; it decides nothing at render time.

## Approval

`approved` (on `Chrome`) decides which spec prints. The owner approved the intended specs of Editorial, Farmhouse and Mid-century on 2026-10-12 (`approved=True` in their entries; they print since step 4, 2026-10-13). A design whose intended spec is what it prints already (Coastal, `06b`, `06c`, `12a`, Blank, `original`) has nothing to approve and counts as approved. Every other design's intended values follow the override audit's findings and await her look; until she approves one it renders as today (`active` is `current`), pixel for pixel. To approve a design: set `approved=True` on its entry, check that `chrome.css` has a block for every value its spec needs, render it and look.

Step 4 also refined the vocabulary: `strip` gained `framed` (a square 1.4px frame in the frame colour) and `boxed` now means only the shared rounded box; Farmhouse, the classic family (Deco, Almanac, Bauhaus) and the `02` and `11` layouts carry `framed` as their intended strip.

## Recipes (Phase 2 step 5, 2026-10-13)

The fourteen fields above say what a component looks like. A recipe says what they cannot: proportion, hierarchy and arrangement. It is an optional `Recipe` on `Chrome` (`chrome.py`), with closed vocabularies like `Components`, validated at import; a value outside them fails with a message that names the allowed values (an unknown layout id: "unknown layout id 'x' for family_time; choose one of default, department, recipe, band").

- `active_recipe` is the design's recipe once the design is `approved`, else `DEFAULT_RECIPE`. The default recipe adds no class, no token and no font, so a design without a recipe prints exactly as before (pixel proof below).
- `render.render_html` passes it to the templates as `rc`, writes its classes on the body (`rx rx-<id> r-title-* r-text-* r-icons-* r-motif-* r-sections-*`) and its tokens on `:root`, and embeds the font cuts its type scale asks for (`Recipe.font_needs`). `static/recipes.css` (loaded last) holds everything the classes and tokens select.

| Field | Values | Meaning |
|---|---|---|
| `layouts` | page type to composition id (`LAYOUT_VARIANTS`) | `family_time`: `default`, `department`, `recipe`, `band`; `annual_calendar`: `default`, `broadsheet`, `recipe`, `shapegrid`; `emergency`: `default`, `department`, `recipe`, `shapegrid`. A page type not named prints `default`. `Recipe.calendar` is the annual calendar's id |
| `title_area` | `masthead`, `nameplate`, `centred`, `shapegrid` | How the masthead of every default-composition worksheet is set: today's; ears with the kicker over a left title (Editorial); a centred title with an italic second voice (Farmhouse); a left title beside three shapes (Mid-century) |
| `text` | `ink`, `structure` | The text colour: the ink token, or the structure role (Mid-century: no ink text). A role, so a theme recolours it |
| `icons` | `disc`, `bare`, `none` | Row and strip icons: today's filled discs, a bare icon in the structure colour, or none |
| `motif` | `none`, `ticking`, `shapes` | The page's one motif: the ticking band under the masthead (it replaces the top-edge ticks), or the cover's shapes (they replace the corner circle) |
| `sections` | `default`, `rules`, `frames`, `blocks` | How the default compositions draw their cards, table heads, numerals and totals: as today; open under rules; double-rule frames with the heading set into the top rule; tinted blocks |
| `type` | role to `TypeRole(face, size, weight, tracking, case, italic, leading)` | The type scale at letter. Roles: `kicker`, `title`, `deck`, `section`, `index`, `label`, `field`, `body`, `helper`, `numeral`, `cal_month`, `cal_date`, `cal_weekday`, `footer`; roles not named come from `BASE_TYPE`. Faces are roles (`display`, `script`, `body`), so `fonts:` still changes them. Weights are 400, 600, 700 or 800 (the bundled cuts; no face has a 500) |
| `space` | seven steps in inches | `--s1` to `--s7` (1, 2, 3, 4, 6, 8, 12 sixteenths by default) |
| `print_min` | role to pt | Printed minimums; never under `PRINT_MINIMUMS` |
| `omit` | page type to section ids (`OMITTABLE`) | Owner-approved content exceptions. Only `emergency: family_plan` exists |
| `kicker` | a short plain line | The design's kicker over a title ("The home edition", "the family plan") |

**Compositions.** `templates/compose/<page>-<layout>.html`, built from the shared macros (`field`, `checklist`, `numbered`, `lines`, `footer`) and the parts in `compose/kit.html` (masthead forms, section heads, day names, shapes, the month tile, the dates card) and `compose/emergency-kit.html` (the Emergency sections). A composition keeps every write-on line, row, cell, check box, numbered mark and label of the default page (`tests/test_chrome_variants.py`) and the same month tiles and dates, and is selected by its page class (`lay-<id>`), never by a design name, so any design may pick it. `default` is the page template as it was; the page template includes the composition when the recipe names another (`family_time.html`, `annual_calendar.html`, `emergency.html`).

**Type and print minimums.** Each role prints as `--t-<role>-font`, `-size`, `-weight`, `-track`, `-case`, `-style`, `-lh` and the class `.t-<role>`. A size token is `max(letter size, minimum / --page-zoom)`, so a role never prints under its minimum on 5.5x8 or 6x9. Adopted minimums (2026-10-13 audit, part B; pt as printed): calendar date 6.5, weekday initial 6, table head and column label 6.5, field label 6.5, section label 7.5, body 7, tracked caps 6.5, footer 6.5, helper 6. The default compositions' small text that the shared CSS fixes in points is floored the same way in `recipes.css` ("Print minimums on the default compositions").

**Text colour policy.** `text: structure` sets `--t-text` to the structure role, and every text the shared CSS prints in ink reads it; a look's light accent text (Mid-century's cover kicker, its month band kicker) is deepened or lightened from the palette to read at 4.5:1. Checked in Chrome on every page (`tests/test_recipes.py`).

**Content exceptions.** A template marks an omittable section with `data-section="<id>"` (the default Emergency page marks its family plan). A composition leaves it out when `rc.omits(page, id)`. `tests/test_chrome_variants.py` takes exactly that section out of Blank's counts and labels before comparing, and `tests/test_recipes.py` checks that only Mid-century omits it.

**The three recipes (owner's decisions, 2026-10-13).**

| | Editorial | Farmhouse | Mid-century |
|---|---|---|---|
| Family Time | `department` (Department page) | `recipe` (Recipe card) | `band` (band and tinted blocks, carrying the shape-grid shapes) |
| Annual Calendar | `broadsheet` (Broadsheet) | `recipe` | `shapegrid` (Shape grid) |
| Emergency | `department` | `recipe` | `shapegrid`, without the Family Emergency Plan |
| Title area, sections | `nameplate`, `rules` | `centred`, `frames` | `shapegrid`, `blocks` |
| Text, icons, motif | ink, none, none | ink, bare, ticking | structure (no ink text), bare, shapes |

The month pages and covers keep their owner-approved designs; the recipe adds only the text-colour fixes above to them.

**Pixel proof.** Before any edit and after, the 24 other designs (cover, family_time, emergency, annual_calendar, chores, january, year_goals, meal_plan, weekly, daily, then budget, grocery, health_tracker, school_activities, home_maintenance, vacation, year_end, example_gratitude, index, reading_log) at letter 100 dpi: 504 page pairs, Pillow difference 0 on every pair, including the inline styles moved to classes (page title colour, banner sizes, meal-plan day cells, total bars).

**Approval.** The trio's recipes print because the owner chose their directions; the built pages await independent visual QA and her approval (`stages/04-review/output/phase2-trio-final/`). Another design gets a recipe only after her look: add a `Recipe` to its entry, pick compositions from `LAYOUT_VARIANTS` (or add a shared one), render, measure and look.

## Defects

Two chrome defects found by the audit are recorded, with impact and fix, under "Defects recorded" in the Phase 2 section of `HANDOFF.md`. Both are deferred.
