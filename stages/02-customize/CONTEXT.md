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
2. Choose `design` and `fonts` from the built-in names unless the brief asks otherwise. Set `theme` only with `design: blank` or a retired look; the thirteen looks bring their own colours. Use `palette:` to replace a single colour on any look.
3. Set `pages` only if the brief drops or adds sheets. Otherwise omit `pages` so defaults apply.
4. Override `months` entries only when the brief asks for new taglines.
5. Pause at the checkpoint, then write YAML.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|----------------|---------------|
| 4 | Design, fonts, page list summary | Approve or change |

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
