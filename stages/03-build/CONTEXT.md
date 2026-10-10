# Build

Render the book with the local Python app. Do not rewrite templates or restyle CSS in this stage.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-customize/output/` | The run's `*-family.yaml` | Config |
| Commands | `references/build-commands.md` | Full file | Exact CLI |
| Tools | `references/tool-setup.md` | Only if the build fails to start | Python and browser install |
| Design | `../../_config/design-system.md` | Page box | Print reminder only |

## Process

1. Confirm the customize YAML exists. If missing, stop and send the user to stage 02.
2. From the repo root, run the build command in `references/build-commands.md`, writing into this stage's `output/`.
3. The built-in typefaces ship in the repo. If the YAML names its own font families and headings look generic, run `python planner.py fonts -c <yaml>` once to download them, then rebuild.
4. Run the audit below. If a check fails, fix the cause and rebuild.
5. Record the PDF path, page count, and any CLI errors in `output/[slug]-build-notes.md`.

## Audit

| Check | Pass Condition |
|-------|----------------|
| Render | The build command exits without an error |
| Files | `output/` holds a new HTML and PDF for this run |
| Count | PDF page count equals the list from `python planner.py pages -c <yaml>` |
| Fonts | `python planner.py fonts -c <yaml>` reports every face present |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Book | `output/` | HTML and PDF from the CLI (`-o` this folder) |
| Notes | `output/[slug]-build-notes.md` | Markdown: command, result, errors |
