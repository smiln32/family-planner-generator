# Intake

Collect this run's family facts. Do not pick colours, fonts, or render a PDF.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Template | `references/brief-template.md` | Full file | Shape of the brief |
| Catalog | `../../_config/page-catalog.md` | Default table | Know which sheets exist |
| Voice | `../../_config/voice.md` | Names section | How to write the family line |

## Process

1. Ask only what this run needs: year, family name (or generic), members, week start, dated or blank months, paper size if not the factory default.
2. Derive a topic slug from the family name and year (`ramirez-2027`, or `family-2027` if unnamed).
3. Fill the brief template. Leave theme, fonts, and page toggles to stage 02.
4. Pause at the checkpoint before writing.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|----------------|---------------|
| 3 | Year, name, member list, dated vs blank | Confirm or edit |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Brief | `output/[slug]-brief.md` | Markdown from the template |

## Routing

Next: `../02-customize/`. If they only wanted the visual editor, stop and run `python planner.py ui`.
