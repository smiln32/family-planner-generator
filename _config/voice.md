# Voice

How printed copy should sound. Worksheets are mostly write-on lines; keep printed words short.

## Sound like

Warm, clear, and specific. Families of mixed ages should get the page without a legend. Headings name the job of the sheet ("Weekly Meal Planning Sheet"), not a metaphor.

Cover subtitle default: "Plan Together. Grow Together. Succeed Together."

Month taglines are one cheerful line, present tense, about being together. Footers are even shorter: one sentence, no exclamation unless December.

## Do not

- Do not lecture or shame ("stop wasting money").
- Do not use slang that will date the book in a year.
- Do not pack a paragraph onto a write-on page. Prefer a label and a line.
- Do not invent new section titles that fight the page catalog. Change `_config/page-catalog.md` if the sheet itself changes.

## Names

Each of the thirteen looks has its own cover, unique to that style. As designed it prints no family name and no year (see `design-system.md`). Add them only when the family asks: `cover_show_family: true` prints "The [family name] Family", `cover_show_year` prints the year or a `cover_text` line such as "2026–27", and `cover_line` adds one short line of their own ("Our year together"). Keep that line short, warm and in the family's words. `family_name` also names the file and page title; Blank, the retired looks and the layouts print "The [family name] Family" on the cover whenever it is set. Tracker rows may be blank for handwriting.
