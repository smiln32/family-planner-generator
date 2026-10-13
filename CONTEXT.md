# Workspace routing

Layer 1. Given what the user wants, go to one stage. Then load only that stage's `CONTEXT.md`.

## Task routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Configure the factory (defaults, paper) | `setup/questionnaire.md` | `setup` trigger, once per workspace |
| Start a new planner for a family or year | `stages/01-intake/CONTEXT.md` | Collect this run's facts only |
| Pick pages, chrome (design), colours (theme, palette), type (fonts) | `stages/02-customize/CONTEXT.md` | Needs 01 output; the four axes are independent. Chrome choices read `_config/chrome-catalog.md` |
| Produce HTML/PDF/PNG | `stages/03-build/CONTEXT.md` | Needs 02 `family.yaml` |
| Check the built book | `stages/04-review/CONTEXT.md` | Needs 03 output |
| Use the visual editor | `python planner.py ui` | Local app, not a stage |
| Change a prompt or step | that stage's `CONTEXT.md` | Edit markdown, do not add code |
| Change print look (margin, type, cards) | `_config/design-system.md` | Then templates/CSS if needed |

## Shared resources

| Resource | Location | Contains |
|----------|----------|----------|
| Factory reference | `_config/CONTEXT.md` | Design system, voice, page catalog, YAML keys |
| Cross-stage notes | `shared/CONTEXT.md` | Decisions that affect more than one stage |
| Local app | `planner.py` | Rendering. Run it; do not reimplement it in chat |

## Session start

1. Read this file.
2. If they said a trigger, follow `CLAUDE.md`.
3. Otherwise match the task routing table.
4. Read that stage's `CONTEXT.md` next. Do not open sibling stages.
