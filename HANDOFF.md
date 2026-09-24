# Handoff — 2026-09-15

**Why parked:** session end / continuity checkpoint. Two threads are open at once: (1) an ICM structure cleanup just finished, (2) a page-looks feature (color picker + look 17) sits fully edited but uncommitted in the working tree.

## What this is

Family Success Planner is an ICM factory (`CLAUDE.md` → `CONTEXT.md` → stage `CONTEXT.md`) for printable planner books, plus a local Python app (`planner.py`, `familyplanner/`) that renders them. This session (a) verified the repo's folder structure matches the documented ICM contract and (b) found pre-existing uncommitted code/doc changes for the "page looks" feature that were not made this session — they were already in the working tree when it started.

## Where everything lives

- Repo root: `C:\Users\smiln\Desktop\family-success-planner`
- Layer 0/1: `CLAUDE.md`, `CONTEXT.md`
- Stage pipeline: `stages/01-intake/` → `02-customize/` → `03-build/` → `04-review/` (each has `CONTEXT.md`, `references/`, `output/`)
- Design rules: `_config/design-system.md`, `_config/voice.md`, `_config/page-catalog.md`
- Cross-stage notes: `shared/decisions.md`, `shared/looks-handoff.md` (the existing handoff doc *for the looks feature specifically* — read it before touching any cover/look work)
- Renderer/app: `familyplanner/config.py`, `designs.py`, `server.py`, `templates/pages/cover.html`, `static/planner.css`, `static/ui/*`
- One run has been completed locally. Run outputs under `stages/*/output/` are gitignored, so family names never reach the repo; use `status` to see what exists on this machine.

## Build status

| Unit | State |
|------|-------|
| ICM structure conformance audit | Done — Layer 0–1 and all four stages already match `CLAUDE.md`'s folder map |
| `family.yaml` (root) untracked + gitignored | Done, staged in the index (`git rm --cached`), not yet committed |
| Palette color-picker feature (`config.py`: `normalize_hex`, `sanitize_palette`, `palette_overrides`, `PALETTE_ROLES`) | Uncommitted, appears complete — not written this session, not yet reviewed/tested by me |
| Look 17 "Intention" + look 12 renamed "Beautiful day" (`designs.py`, `cover.html`, `planner.css`, docs) | Uncommitted, appears complete — not written this session, not yet reviewed/tested by me |
| Doc updates reflecting 02–17 range (`CONTEXT.md`, `shared/CONTEXT.md`, `shared/decisions.md`, `_config/design-system.md`, `stages/02-customize/references/yaml-shape.md`, `README.md`) | Uncommitted, consistent with the code changes above |
| Looks 02–17 overall design quality | **Not done** — per `shared/looks-handoff.md`, human paused look design; covers are not print-quality; only mechanical implementation from approved references should continue |

## Locked decisions

- Original illustrated house cover (`design: original`) stays as-is; never restyle it and present it as a new look.
- Looks `02`–`17` are unfinished. Do not invent cover art, florals, or notebook chrome in chat without a human-approved reference image or written layout (see `shared/looks-handoff.md` → "Do not").
- `out/` and now `family.yaml` are intentionally gitignored/untracked local-app scratch — the canonical per-run artifacts live under `stages/*/output/`, not the repo root.
- One stage, one job; do not add a coordinator script; reorder stages by renaming the numbered folders only.

## What to do on resume

1. Read this file, then `shared/looks-handoff.md`, then `git status` and `git diff --stat` — confirm the uncommitted diff list still matches the Build status table above (nothing else changed it in the meantime).
2. Decide whether to commit the `.gitignore` + `family.yaml` untrack as its own commit (recommended, since it's an unrelated structural cleanup) separately from the palette/look-17 feature commit.
3. Before committing the palette/look feature: actually run `python planner.py ui`, exercise the new color picker, and check look 17 / renamed look 12 render correctly — none of this was verified this session.
4. If asked to continue look design work, follow `shared/looks-handoff.md` exactly: get an approved reference first, implement one look at a time, then stop.
5. Do not read previous run outputs (`stages/*/output/`) to learn style — `_config/` is the quality source.

> FIRST TURN: read the referenced docs ONE AT A TIME (no parallel tool calls, no batched reads). Parallel reads on the first turn can wedge a new session; sequential reads avoid it.
