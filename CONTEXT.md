# Workspace routing

Layer 1. Given what the user wants, go to one stage. Then load only that stage's `CONTEXT.md`.

## Task to stage

| If the user wants to | Go to | Then |
|----------------------|-------|------|
| Configure the factory (brand, defaults, paper) | `setup/questionnaire.md` | `setup` trigger |
| Start a new planner for a family or year | `stages/01-intake/` | Collect this run only |
| Pick theme, fonts, pages, month lines | `stages/02-customize/` | Needs 01 output |
| Produce HTML/PDF/PNG | `stages/03-build/` | Needs 02 `family.yaml` |
| Check the built book | `stages/04-review/` | Needs 03 output |
| Use the visual editor | `planner.py ui` | Local app, not a stage |
| Change a prompt or step | that stage's `CONTEXT.md` | Edit markdown, do not add code |
| Change print look (margin, type, cards) | `_config/design-system.md` | Then templates/CSS if needed |

## Shared resources

| Need | Load |
|------|------|
| Print and layout rules | `_config/design-system.md` |
| Cover and worksheet tone | `_config/voice.md` |
| Default 30-page order | `_config/page-catalog.md` |
| YAML keys the app accepts | `config.example.yaml` |
| Cross-stage decisions | `shared/` |
| Page looks 02–16 (unfinished) | `shared/looks-handoff.md` |

## Session start

1. Read this file.
2. If they said a trigger, follow `CLAUDE.md`.
3. Otherwise match the table above.
4. Read that stage's `CONTEXT.md` next. Do not open sibling stages.
