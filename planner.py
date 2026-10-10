#!/usr/bin/env python3
"""Family Success Planner generator.

    python planner.py init            # write a starter family.yaml
    python planner.py build           # render the planner to out/*.pdf
    python planner.py build --png     # ...and one 300 dpi PNG per page
    python planner.py pages           # list the pages that would be built
    python planner.py months          # show per-month colours and taglines
    python planner.py fonts           # fetch custom typefaces (built-in sets ship in the repo)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from familyplanner.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
