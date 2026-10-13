# Chrome catalog

The contract for the chrome axis (`design`). Phase 2 step 3, 2026-10-12; step 4 (the variants that print it), 2026-10-13.

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

## Defects

Two chrome defects found by the audit are recorded, with impact and fix, under "Defects recorded" in the Phase 2 section of `HANDOFF.md`. Both are deferred.
