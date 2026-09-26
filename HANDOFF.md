# Handoff, 2026-09-24

**Why parked:** end of day after a security and privacy pass. Everything is committed and pushed; the working tree is clean. The only open product work is the paused page-looks design.

## What this is

Family Success Planner is an ICM factory (`CLAUDE.md` → `CONTEXT.md` → stage `CONTEXT.md`) for printable planner books, plus a local Python app (`planner.py`, `familyplanner/`) that renders them. The repo may be made public, so it must never carry a real family's name (see Locked decisions).

## Where everything lives

- Repo root: `C:\Users\smiln\apps from Kingston\Apps just for me\family-planner-generator`
- Remote: `git@github.com:smiln32/family-planner-generator.git` (SSH; see Environment notes)
- Layer 0/1: `CLAUDE.md`, `CONTEXT.md`
- Stage pipeline: `stages/01-intake/` → `02-customize/` → `03-build/` → `04-review/` (each has `CONTEXT.md`, `references/`, `output/`)
- Design rules: `_config/design-system.md`, `_config/voice.md`, `_config/page-catalog.md`
- Cross-stage notes: `shared/decisions.md`, `shared/looks-handoff.md` (read before touching any cover/look work)
- Renderer/app: `familyplanner/config.py` (loading plus the shared validators), `designs.py`, `render.py`, `server.py`, `templates/`, `static/`
- Tests: `tests/` (`python -m pytest`; install with `pip install -r requirements-dev.txt`)
- Run outputs under `stages/*/output/` are gitignored and stay on the machine that made them. Use `status` to see what exists locally.

## Build status

| Unit | State |
|------|-------|
| ICM structure | Done. Layers 0–1 and all four stages match `CLAUDE.md`'s folder map |
| Palette colour editor (theme, then replace any of the twelve print colours; round-trips through the plan file) | Committed. Covered by unit and API tests; **not yet exercised by hand in `planner.py ui`** |
| Look 17 "Intention", look 12 renamed "Beautiful day" | Committed. Mechanical only; see looks row |
| Security pass: `/api/save` removed, sanitized output stems, hex/font/month validation, escaped tab rail, one validator set for YAML, CLI and UI, Host/Origin/JSON guard on the local API, clean CLI `error:` lines for file errors | Done, 74 tests |
| Privacy: run outputs untracked; history rewritten to drop real family names and the original source pack (reference PDF + `JPG/` page scans); author email replaced with the GitHub noreply address | Done 2026-09-24. GitHub repo deleted and recreated from the clean history, so no old commits exist there. Repo is ~185 KB and still **private** |
| Looks 02–17 design quality | **Not done.** Human paused look design; covers are not print-quality. Only mechanical implementation from approved references should continue |
| Last local book build | Predates the looks and security work. Re-run stage 03 before printing |

## Locked decisions

- No real family names in the repo: not in docs, examples, tests, commit messages or run outputs. Use blank or made-up names (the code uses "Ramirez"). Personalisation happens in `family.yaml` or the UI, never by committing a run.
- Original illustrated house cover (`design: original`) stays as-is; never restyle it and present it as a new look.
- Looks `02`–`17` are unfinished. Do not invent cover art, florals or notebook chrome in chat without a human-approved reference image or written layout (see `shared/looks-handoff.md` → "Do not").
- Every value from YAML, CLI flags or the UI goes through the validators in `config.py`. New fields get a `check_*` helper and a test; nothing reaches a template or a file path unchecked.
- The local server answers only its own page. Keep all UI calls on the JSON `api()` helper in `ui.js`; a plain form post or `text/plain` fetch will get a 403.
- `out/` and root `family.yaml` are gitignored local scratch.
- One stage, one job; no coordinator script; reorder stages by renaming the numbered folders only.

## Environment notes

- Windows Smart App Control blocks Git for Windows' unsigned `libcurl-4.dll`, so HTTPS push and fetch fail or hang. This repo pushes over SSH with `core.sshCommand = C:/Windows/System32/OpenSSH/ssh.exe`. Do not switch the remote back to HTTPS.
- Any clone made before 2026-09-24 has the old history. Delete it and re-clone; never push from it, or the names and source pack return.
- The original source pack (reference planner PDF and 31 page JPGs) lives outside the repo at `..\planner-source-pack\`. Do not copy it back in; it must not be published.
- `git-filter-repo` is installed (`python -m git_filter_repo`) if history ever needs scrubbing again.

## What to do on resume

1. Read this file, then `git status`. It should be clean.
2. Run `python -m pytest`. All tests should pass.
3. If asked to print a book: route through stage 03 (`build`), then stage 04 review.
4. Worth doing: open `python planner.py ui` and exercise the colour editor by hand (change a colour, preview, download the plan, open it again).
5. If asked to continue look design, follow `shared/looks-handoff.md` exactly: get an approved reference first, implement one look at a time, then stop.
6. Making the repo public is a human call (GitHub Settings → Danger Zone → Change visibility). Nothing in the history blocks it.
7. Do not read previous run outputs (`stages/*/output/`) to learn style. `_config/` is the quality source.

> FIRST TURN: read the referenced docs ONE AT A TIME (no parallel tool calls, no batched reads). Parallel reads on the first turn can wedge a new session; sequential reads avoid it.
