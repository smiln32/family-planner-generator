# Page looks — handoff for the next agent

Updated 3 Sep 2026. Family title covers 02–10 and daily covers 11–16 now have **their own markup** in `cover.html` (`.famcover-*` and `.daily-*`). Original house cover is hidden for those looks.

Still not reference-perfect: daily density and brush/floral drawing vs the chat images. Re-ask the human if those files are not in the thread. Check Cover first in `python planner.py ui`.

## What “good” is

Only one cover composition has been accepted:

- **Family Success Planner as a sparse title page:** stacked FAMILY / SUCCESS / PLANNER, motto, script family line (e.g. The Ramirez Family), five coloured pills under that block, most of the lower page empty. One variant had a thin **red rail** on the left (Swiss). Another was the **same title job on graph paper** (four short dashes above the stack, tiny hearts around the motto, centered). These are *new cover layouts*, not the illustrated house cover with a skin.

A **daily** that is the quality bar (not yet matched in the app):

- **Grounded. Grateful. Growing.** Cream page, script title, DATE + family name, rounded modules, dusty-rose / sage **brushstroke headers**, schedule 6 AM–9 PM on the right, top priorities + to-do on the left, notes with dot grid, “Today I Will” with hearts, footer *You don't have to be perfect to make progress.*

## What failed

Looks 02–16 were implemented as **one family book with a CSS costume**: hide house art, recolour banners. Looks 11–16 later got extra daily markup on the cover, but still did not match the references (same skeleton, wrong density, leftover Family Success stack, or a generic grid with `content:` labels).

The human: *“Each page is a lame variation on the original instead of completely new designs.”* Then: only the first (sparse family cover) looks good; give the rest to Claude.

## Do not

- Restyle the original cover HTML and call it a new planner.
- Share one `.look-sheet` / one daily grid and remap it with CSS `grid-area` and `::after` titles.
- Leave the illustrated house / “Family Success Planner” stack visible on daily looks.
- Treat interiors as finished because banners changed colour.

## What to build

1. **Original** stays the illustrated Family Success Planner.
2. **Family looks (~02–10):** each look needs its **own cover composition** in the spirit of the sparse title page and the graph-paper title page (alignment, rail vs grid vs empty field, where pills sit). Family *worksheet content* can stay; chrome must not be a tinted original masthead.
3. **Daily looks (11–16):** each cover **is** that daily page only, rebuilt against references until layout matches, not just palette.

   | Look | Intended cover |
   |------|----------------|
   | 11 Executive | DAILY PLAN — navy, DATE box, goals 1–2–3, timed schedule 6 AM–9 PM, tasks, calls/emails, dotted notes, tomorrow’s focus, `///` footer |
   | 12 Bloom | Today, with Grace — pink bars, hour schedule, top 3, to-do, notes, self-care & gratitude (and/or “Today is a Beautiful Day” cottagecore: full-width top 3, florals) |
   | 13 Boho | Grounded. Grateful. Growing. — as in the accepted daily description above |
   | 14 Scrapbook | Good Things / Are happening — tabs, this week, must do, little wins, fuel & hydrate, brain dump, notes; **no** hourly schedule |
   | 15 Street | LET’S GET IT — graph or doodle grid, 7 AM–10 PM, don’t forget, brush banners |
   | 16 Reset | Reset & Refocus — sage/terracotta, intentions, water/habits, schedule, mantra *Focus on progress, not perfection.* |

4. **One real structure per look** (or a few real layouts), not one template restyled.
5. Check **Cover first** in `python planner.py ui`, then one interior. If a family cover still shows the house in the lower half, it failed.

## Code today

- Cover: `familyplanner/templates/pages/cover.html` — original house cover, nine `.famcover-02` … `-10` title pages, six `.daily-11` … `-16` dailies. CSS shows one of those and hides `.cover-body` / `.cover-scene` / `.cover-feet`.
- Looks CSS: `familyplanner/static/planner.css` (`body.design-*`).
- Preset names: `familyplanner/designs.py`.
- Print rules: `_config/design-system.md`.
- Editor: `familyplanner/static/ui/` — look picker; Windows start: `Start Planner.bat`.

References were given as chat images (executive daily, Grace/bloom, street doodle, reset, cottagecore floral, boho daily, scrapbook Good Things, sparse Swiss family cover, graph-paper family cover). Re-ask the human if those files are not in the thread.

## Out of scope unless asked

- Changing Original’s illustrated cover.
- Replacing chores/budget/months with daily modules (those stay family sheets unless new examples arrive).
