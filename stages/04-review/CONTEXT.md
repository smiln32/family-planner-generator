# Review

Read the built book against the factory rules. Do not rebuild unless the human asks.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Build | `../03-build/output/` | HTML/PDF and `*-build-notes.md` | What was produced |
| Design | `../../_config/design-system.md` | Full file | Pass conditions |
| Voice | `../../_config/voice.md` | Full file | Copy checks |
| Catalog | `../../_config/page-catalog.md` | Default table | Missing or extra sheets |
| Config | `../02-customize/output/` | The run's YAML | Expected year and name |

## Process

1. Confirm page count matches the config (30 with default pages and twelve months; 31 if `index` / linked).
2. Run the audit table against the HTML or PDF.
3. Write findings. Separate blockers from nits.
4. If a blocker is a config mistake, point back to stage 02. If it is a template bug, say which template.
5. If the human wants changes applied, they are made in stage 02 and rebuilt in stage 03. This stage does not rebuild.

## Audit

| Check | Pass Condition |
|-------|----------------|
| Count | Page list matches `pages` / defaults |
| Cover | Year and family line match the YAML |
| Margin | No page visibly tighter at the trim than the others |
| Months | Twelve unique months, dates match `year` if dated |
| Footer | Shared footer on pages that are supposed to have it |
| Voice | No scolding copy; taglines are one line |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Review | `output/[slug]-review.md` | Markdown: pass/fail per check, notes |
