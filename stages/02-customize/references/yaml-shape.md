# YAML shape

Canonical keys live in `config.example.yaml` at the repo root. This file is a reminder, not a second spec.

Required for a typical run:

- `year` integer
- `family_name` string, may be empty
- `week_starts` `sunday` or `monday`
- `dated_months` boolean
- `page_size` `letter` or `a4`
- `members` list of strings
- `theme` one of classic, amber, berry, bold, citrus, forest, meadow, ocean, pastel, poppy, slate
- `fonts` a set name, or a mapping of display, script, body

Optional: `pages`, `palette`, `months`, `title`, `subtitle`, `output_name`, `linked`.

Unknown keys make `planner.py` fail. Do not invent keys.
