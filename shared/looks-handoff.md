# Page looks handoff

Updated 6 Sep 2026. Human stopped look design: covers are not at print quality. Do not keep drawing flora, notebook chrome, or new cover layouts in chat. Next look work needs approved reference images (or a designer), then mechanical implementation only.

## What this factory is

`design: original` is the illustrated Family Success Planner (house cover, 30 family worksheets). Looks `02`–`10` are meant to be different **family title covers**. Looks `11`–`17` are meant to be different **daily-planner covers**. Interiors stay the family worksheets and only pick up that look’s paper/chrome.

The visual editor is `python planner.py ui`. Check **Cover** first.

## Human verdicts (do not argue)

| Look | Status | Notes |
|------|--------|--------|
| Original cover | Keep | Illustrated house, badges, footer chips. Do not restyle it and call it a new planner. |
| Original interiors | Worksheets exist | 6 Sep: Belongs To, Vision & Mission, and Family Goals were filled with write-on structure (they had been empty boxes). Other catalog sheets were already dense. Do not “design” them further unless asked. |
| 02 Boxed records | Cover markup exists | Ledger / belongs-to / numbered index. Not accepted as a finished look. |
| 03 Botanical | **Rejected** | First version was ellipse/circle blobs. Human: embarrassing. A denser SVG spray was swapped in without approval. Treat as failed; do not iterate blobs or fake florals. |
| 04 Marker journal | Cover markup exists | Graph paper, dashes, title stack. Closer to an earlier accepted *composition* (empty-field title), not signed off as a product. |
| 05 Soft intention | Cover markup exists | Plan / Rest / Gather cards. Unfinished. |
| 06 School notebook | **Rejected as incomplete** | Ruled paper + three fields was empty. A contents / if-found first page was added without approval. Human: incomplete; stop designing. |
| 07 Editorial | Cover markup exists | Giant “Family” + contents. Unfinished. |
| 08 Stamp frame | Cover markup exists | Postage block. Unfinished. |
| 09 Swiss grid | Cover markup exists | Red word, empty field. Unfinished. |
| 10 Keepsake | Cover markup exists | Photo well + script. Unfinished. |
| 11–17 dailies | Cover markup exists | Built to match chat reference *layouts* (see table below). Interiors are still family worksheets with restyled chrome. Not a replacement book. Human did not accept these as done in this session. |
| blank | Mechanical | Hides illustration. Fine. |
| 02a–12c layouts | Owner-supplied, 2026-09-30 | Twelve planner layouts from the owner's own design export ("Look pairings and color exploration"), copied in mechanically: looks 02, 06, 11, 12 crossed with a split / stacked / sidebar page structure. Each adds a boxed monthly page plus Weekly Plan and Daily Plan sheets. The cover is still the parent look's unfinished cover. Not a chat invention; do not restyle them without the owner. |

## What “good” was supposed to be

A new look is a **different page**, not a costume on Family / Success / Planner.

- Family covers (02–10): their own job and empty field. One accepted *direction* earlier was a sparse stacked title (motto, family line, pills, lots of paper). Graph-paper variant of that same job. **That is not the illustrated house cover.**
- Daily covers (11–17): match the **reference layout** (modules, density, drawing, paper). Do not share one daily grid and remap it with CSS `grid-area`.

## Looks 11–17 (code intent, not a quality pass)

| Look | Cover in `cover.html` |
|------|------------------------|
| 11 Executive | DAILY PLAN: navy, DATE, goals 1–2–3, schedule 6:00 AM–9:00 PM, tasks, calls/emails, notes, tomorrow’s focus |
| 12 Beautiful day | Today is a Beautiful Day: florals (still simple shapes), top 3, schedule + to-do + notes + self-care |
| 13 Boho | Grounded. Grateful. Growing. Brush headers, schedule right, pot, Psalm 118:24 |
| 14 Scrapbook | Good Things / Are happening: collage, no hourly schedule |
| 15 Street | LET’S GET IT: graph paper, 7 AM–10 PM |
| 16 Reset | Reset & Refocus: sage/terracotta, habits |
| 17 Intention | plan with intention: pastel modules, gratitude + hydrate |

## Files

| File | Role |
|------|------|
| `familyplanner/designs.py` | Look ids and UI labels (`original`, `02`–`17`, `02a`–`12c`, `blank`); `parts()` splits a layout id into look, layout and box style |
| `familyplanner/templates/pages/cover.html` | Original house cover + `famcover-02`…`10` + `daily-11`…`17` |
| `familyplanner/templates/layout_kit.html`, `layout_monthly.html`, `pages/daily.html`, `pages/weekly.html` | The planner layouts' boxes, lines, schedule, calendar and habit grid; the layout monthly page; the Weekly Plan and Daily Plan sheets |
| `familyplanner/static/planner.css` | `.design-02`…`.design-17` paper/chrome; `.famcover-*` and `.daily-*` layouts; "planner layouts" section (`.lx-*`, `.box-*`) at the end |
| `familyplanner/typefaces.py` | Two suggested font pairings per look (`ledger`, `composition-book`, `boardroom`, `garden-party` and the rest). Suggestions only; a look does not switch fonts |
| `familyplanner/static/ui/` | Look picker copy |
| `_config/design-system.md` | Print rules; looks are named there, not blessed |

House cover HTML stays in the file and is hidden with CSS when `body` is not `design-original`.

## Do not

- Restyle the original cover and call it a new planner.
- Invent botanical or notebook decoration without a human-approved reference.
- Replace chores / budget / months with daily modules unless asked.
- Treat current 02–17 as shippable looks.
- Load previous look CSS as a style guide.

## If asked to continue looks

1. Get a reference image (or a written layout) the human accepts.
2. Implement **that** cover in `cover.html` + CSS. One look at a time.
3. Verify Cover in `python planner.py ui` at letter and at least one small size.
4. Stop. Do not “improve” the other looks in the same pass.
