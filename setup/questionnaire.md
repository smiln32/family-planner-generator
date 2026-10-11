# Setup questionnaire

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions
     in one conversational pass so the user can answer in a single message. Use the
     default for anything they skip. Answers configure the factory, not a single
     family's book. Per-run year and names are collected by stage 01. -->

### Q1: Default paper size?
- Files: `config.example.yaml` (`page_size`)
- Type: selection
- Options: `5.5x8`, `6x9`, `letter`
- Default: `letter` (8.5 by 11 in)
- Derived: if not `letter`, update the Page box section of `_config/design-system.md`

### Q2: Default week start?
- Files: `config.example.yaml` (`week_starts`)
- Type: selection
- Options: `sunday`, `monday`
- Default: `sunday`

### Q3: Default look?
- Files: `config.example.yaml` (`design`)
- Type: selection
- Options: the thirteen looks, the planner layouts and `blank`, as listed in the `design` comment of `config.example.yaml`
- Default: `editorial`
- Derived: a look or layout brings its own colours and typeface set, so Q4 and Q5 only matter for `blank` or when the owner wants a different set

### Q4: Default colour theme (Blank look only)?
- Files: `config.example.yaml` (`theme`)
- Type: selection
- Options: the theme names listed in the `theme` comment of `config.example.yaml`
- Default: `linen`

### Q5: Default typeface set?
- Files: `config.example.yaml` (`fonts`)
- Type: selection
- Options: "the look's own set" (leave `fonts:` commented out), or a set name listed in the `fonts` comment of `config.example.yaml`
- Default: the look's own set (`home-edition` for `editorial`)

### Q6: Typical household size, for blank tracker rows?
- Files: `config.example.yaml` (number of empty `members` entries)
- Type: number
- Default: 5

### Q7: Dated monthly grids by default?
- Files: `config.example.yaml` (`dated_months`)
- Type: yes/no
- Default: yes

---

## After onboarding

Tell the user which defaults changed and that `python planner.py init` now writes them into new `family.yaml` files. Do not put a specific family name into `_config/` or `config.example.yaml`.

Then scan `_config/` and `stages/` for any remaining `{{` patterns. This file is the source of the questions, not a target, so skip it. If any remain, ask for the missing information.
