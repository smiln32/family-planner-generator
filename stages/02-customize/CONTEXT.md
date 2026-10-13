# Customize

Turn the intake brief into a generator config. Do not run Chrome or write a PDF.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-intake/output/` | The run's `*-brief.md` | Family facts |
| YAML shape | `../../config.example.yaml` | Full file | Keys the app accepts |
| Catalog | `../../_config/page-catalog.md` | Full file | Default pages |
| Design | `../../_config/design-system.md` | Type, Four axes, Colour roles, Months | Chrome, colours, type and month rules |
| Chrome | `../../_config/chrome-catalog.md` | Full file, then `python planner.py chrome` | What each design's components are meant to look like |
| Themes | `python planner.py themes` | Its output | The colour presets and their swatches |
| Voice | `../../_config/voice.md` | Sound like, Do not | Taglines if you rewrite months |

## Process

1. Read the brief. Copy year, name, members, week start, dated flag, paper size into YAML.
2. Four independent choices, each its own key. Decide them one at a time:
   - **Pages** (`pages`): set only if the brief drops or adds sheets. Otherwise omit `pages` so the defaults apply. Page ids are checked when the book is planned, so an unknown id fails at build.
   - **Chrome** (`design`): choose from the built-in names (`_config/design-system.md`, Type) unless the brief asks otherwise; `_config/chrome-catalog.md` and `python planner.py chrome` say how each design treats its components. The design also brings a default palette and a default typeface set; both are fallbacks only.
   - **Colours** (`theme`, `palette`): the theme choice is available for every design. Precedence, lowest first: the design's own palette (`linen` for Blank and the retired looks), then the named `theme`, then the `palette:` block; each layer replaces only the colours it names. Omit `theme` to print the design as designed. `python planner.py themes` lists the presets. Use `palette:` to replace single colours on any design.
   - **Type** (`fonts`): resolved on its own, apart from colour. Omit `fonts` to use the design's own set (Blank and the retired looks use `elegant`). Name a set, or a `display`/`script`/`body` trio, only to use something else; explicit fonts win whatever the design or theme.
3. Cover words, from the brief's "cover words" line. On one of the thirteen looks all three are off unless asked: `cover_show_family: true` (needs `family_name`), `cover_show_year: year` or `custom` with `cover_text` (such as "2026–27"), and `cover_line` (one short line). Limits: family name 60 characters, `cover_text` and `cover_line` 80. On Blank, a retired look or a layout these three do nothing; the cover prints `family_name` and the year by itself (`cover_year`, `cover_text`). Override `months` taglines only when the brief asks, and only on Blank or a retired look; look and layout month pages do not print them.
4. Pause at the checkpoint, then write YAML.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|----------------|---------------|
| 3 | Pages, design, theme, fonts, cover words summary | Approve or change |

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
