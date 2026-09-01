# Build commands

Run from the repository root. Replace the yaml path and keep `-o` on this stage's output folder.

```
python planner.py build -c stages/02-customize/output/[slug]-family.yaml -o stages/03-build/output
```

Useful flags:

```
python planner.py build -c <yaml> -o stages/03-build/output --html-only
python planner.py build -c <yaml> -o stages/03-build/output --png --dpi 110
python planner.py pages -c <yaml>
python planner.py fonts -c <yaml>
python planner.py ui -c <yaml>
```

Needs Python 3.10+, `pip install -r requirements.txt`, and Chrome, Edge, Chromium, or Brave for PDF. `--html-only` is enough to inspect layout without a browser print step.
