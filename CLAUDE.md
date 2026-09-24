# Family Success Planner

Layer 0 identity. This workspace is an Interpretable Context Methodology (ICM) factory for printable Family Success Planner books, plus a local Python app that renders them.

You are one agent. Folders, not a framework, decide what you load. Read down the five layers and stop when you have enough:

0. This file: where you are
1. `CONTEXT.md`: which stage handles the task
2. That stage's `CONTEXT.md`: what to do
3. Only the reference files listed in Inputs
4. Only the working artifacts listed in Inputs

Do not load every stage. Do not read previous run outputs to learn style. Docs in `_config/` are the quality source.

## Folder map

```
CLAUDE.md                 Layer 0 (this file)
CONTEXT.md                Layer 1 routing
_config/                  Layer 3 factory: design, voice, page catalog
shared/                   Layer 3 cross-stage notes
setup/questionnaire.md    One-time factory setup
stages/
  01-intake/              This run's family brief
  02-customize/           family.yaml for this run
  03-build/               HTML/PDF via local scripts
  04-review/              Human-readable quality notes
planner.py                App entry: ui, build, fonts, init
familyplanner/            Renderer, templates, preview UI
config.example.yaml       Canonical YAML keys for the generator
```

## Local app (no AI)

Mechanical work lives in Python. Do not reimplement rendering in chat.

```
python planner.py ui       preview editor at http://127.0.0.1:8733
python planner.py build    print-ready PDF
python planner.py pages    list the running order
python planner.py init     write family.yaml from the example
```

Stage 03 calls `build`. Humans who skip the agent pipeline can use `ui` alone.

## Triggers

| Say | Do |
|-----|-----|
| `setup` | Read `setup/questionnaire.md`, ask once, bake answers into `_config/` and defaults |
| `status` | Scan `stages/*/output/` (ignore `.gitkeep`) and print the pipeline diagram |
| `ui` | Start or confirm `python planner.py ui`; do not invent a second frontend |
| `build` | Route to stage 03 if a customize output exists; otherwise start at 01 |

## Rules

- One stage, one job. Intake does not render. Build does not rewrite copy.
- Stage contracts are Inputs, Process, Outputs. Follow them.
- Output folders are the handoff. If a human edited a file there, use that version.
- Placeholders look like `{{SCREAMING_SNAKE_CASE}}`. After setup, none should remain in `_config/` or `setup/`.
- Numbered stage folders encode order. Rename to reorder; do not add a coordinator script.
- No real family names in the repo. Run outputs are gitignored and stay local; docs, examples and tests use blank or made-up names.
