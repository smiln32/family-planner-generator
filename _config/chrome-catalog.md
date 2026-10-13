# Chrome catalog

The contract for the chrome axis (`design`). Phase 2 step 3, 2026-10-12.

## What it is

The catalog is the authoritative definition of each design's intended component treatments: how its cards, headings, meta strips, tables, check boxes, numbered marks, write-on lines, annual calendar, labels, footer, ornaments and page edge are meant to look. Colour is not here (see "Colour roles" in `design-system.md`); the catalog covers shape and placement, which a palette then colours.

- Source of truth: `familyplanner/chrome.py` (`CATALOG`, one `Chrome` entry per design, with its prose and its two `Components` specs). Per-design prose lives there, not in this file.
- How to read it: `python planner.py chrome` (intended treatments), `chrome --current` (what each design prints today), `chrome --diff` (only where the two differ).
- Each entry holds `components` (intended) and `current` (what prints today, per the override audit of 2026-10-12, inherited defaults included), so the gap is explicit per design. The body of a rendered book carries the intended spec as one `c-<field>-<value>` class per field; no stylesheet reads those classes until step 4, which will print them through catalog-driven variants of the shared components (annual calendar, meta strips, headings, tables, ornaments), not duplicated templates.

## Rules

1. Every design is fully resolved. An entry may be built from a reusable family base, but what is stored has every field set to a vocabulary value. Nothing inherits at use time.
2. Blank is one explicit entry, not the implicit default. The shared CSS defaults it prints are written into its entry like any other design's.
3. The vocabulary is closed (`chrome.VOCAB`): a value outside it fails at import. Refine a name by changing the vocabulary and every entry that uses it.
4. `palette_ref` and `fonts_ref` are references to the design's own palette and typeface set (`designs.look_palette`, `designs.look_fonts`; `linen` and `elegant` for Blank and `original`), never copies.
5. The retired looks `02` to `17` have no entry (locked, not offered); `original` has one, locked, with intended equal to current. A layout that builds on a retired look has its own entry.

## Vocabulary

One line per field; values in order.

| Field | Values | Meaning |
|---|---|---|
| `corners` | `square`, `soft`, `rounded`, `pill`, `arch` | Card body corners; the meta strips follow the same corners |
| `heads` | `bar`, `rule`, `text`, `outlined`, `pill`, `tape`, `inset`, `script` | A card's section heading: filled bar, label over a rule, plain text, outlined label, pill, tape label, label set into the frame line, script heading |
| `strip` | `boxed`, `ruled`, `bare` | The meta strip at the top of a worksheet |
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

The intended specs of Editorial, Farmhouse and Mid-century are the three the owner approved for Phase 2 (2026-10-12). Every other design's intended values follow the override audit's findings and await her look; where the audit found a design fits as it prints, intended equals current and the entry's `character` says so.

## Defects

Two chrome defects found by the audit are recorded, with impact and fix, under "Defects recorded" in the Phase 2 section of `HANDOFF.md`. Both are deferred.
