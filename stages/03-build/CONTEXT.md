# Build

Render the book with the local Python app. Do not rewrite templates or restyle CSS in this stage.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-customize/output/` | The run's `*-family.yaml` | Config |
| Commands | `references/build-commands.md` | Full file | Exact CLI |
| Design | `../../_config/design-system.md` | Page box | Print reminder only |

## Process

1. Confirm the customize YAML exists. If missing, stop and send the user to stage 02.
2. From the repo root, run the build command in `references/build-commands.md`, writing into this stage's `output/`.
3. If fonts are missing and headings look generic, run `python planner.py fonts -c <yaml>` once, then rebuild.
4. Record the PDF path, page count, and any CLI errors in `output/[slug]-build-notes.md`.

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Book | `output/` | HTML and PDF from the CLI (`-o` this folder) |
| Notes | `output/[slug]-build-notes.md` | Markdown: command, result, errors |

## Routing

Next: `../04-review/`. For a live preview instead of a PDF, `python planner.py ui -c <yaml>` from the repo root.
