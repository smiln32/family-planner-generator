# Customize

Turn the intake brief into a generator config. Do not run Chrome or write a PDF.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-intake/output/` | The run's `*-brief.md` | Family facts |
| YAML shape | `../../config.example.yaml` | Full file | Keys the app accepts |
| Catalog | `../../_config/page-catalog.md` | Full file | Default pages |
| Design | `../../_config/design-system.md` | Type, Months | Theme and motifs |
| Voice | `../../_config/voice.md` | Sound like, Do not | Taglines if you rewrite months |

## Process

1. Read the brief. Copy year, name, members, week start, dated flag, paper size into YAML.
2. Choose `design` from the built-in names unless the brief asks otherwise. A look or layout sets its own `fonts`; set `fonts` only to use a different set. Set `theme` only with `design: blank` or a retired look; the thirteen looks bring their own colours. Use `palette:` to replace a single colour on any look.
3. Set `pages` only if the brief drops or adds sheets. Otherwise omit `pages` so defaults apply.
4. Cover words, from the brief's "cover words" line. On one of the thirteen looks all three are off unless asked: `cover_show_family: true` (needs `family_name`), `cover_show_year: year` or `custom` with `cover_text` (such as "2026–27"), and `cover_line` (one short line). Limits: family name 60 characters, `cover_text` and `cover_line` 80. On Blank, a retired look or a layout these three do nothing; the cover prints `family_name` and the year by itself (`cover_year`, `cover_text`). Override `months` taglines only when the brief asks, and only on Blank or a retired look; look and layout month pages do not print them.
5. Pause at the checkpoint, then write YAML.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|----------------|---------------|
| 4 | Design, fonts, cover words, page list summary | Approve or change |

## Audit

| Check | Pass Condition |
|-------|----------------|
| Keys | Only keys from `config.example.yaml` |
| Members | One list entry per person from the brief |
| Year | Matches the brief |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Config | `output/[slug]-family.yaml` | YAML the generator can load |
