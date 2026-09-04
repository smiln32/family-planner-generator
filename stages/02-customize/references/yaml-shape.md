# YAML shape

Canonical keys live in `config.example.yaml` at the repo root. This file is a reminder, not a second spec.

Required for a typical run:

- `year` integer
- `family_name` string, may be empty
- `week_starts` `sunday` or `monday`
- `dated_months` boolean
- `cover_year` `auto`, `blank`, `omit`, or `print` (cover year when undated)
- `cover_text` string, may be empty (printed instead of `year` on cover/mastheads)
- `page_size` `5.5x8`, `6x9`, or `letter` (8.5 by 11 in)
- `members` list of strings
- `theme` one of linen, classic, amber, berry, bold, citrus, forest, meadow, ocean, pastel, poppy, slate
- `fonts` a set name (default `elegant`), or a mapping of display, script, body
- `design` `original`, `02`–`16`, or `blank`
- `type_size` optional mapping of `title`, `cover`, `body`, `script` (points)

Optional: `pages`, `palette`, `months`, `title`, `subtitle`, `output_name`, `linked`.

Unknown keys make `planner.py` fail. Do not invent keys.
