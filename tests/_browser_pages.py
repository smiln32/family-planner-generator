"""Shared helper for the browser tests that check every page of a book.

`measure(browser, design, size, pages, script, result_id)` renders those pages
of a design at a page size, tags each `<section class="page">` with
`data-page="<slug>"`, appends `script` (which must write its JSON result into
`<pre id="<result_id>">`), prints the DOM with headless Chrome and returns the
parsed JSON. Used by test_colour_roles.py and test_page_fit.py.
"""

from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
import tempfile
from pathlib import Path

from familyplanner import config, designs, render, typefaces

DESIGNS = designs.names() + ["original"]

# Every page a book can hold except the cover (each look's own artwork) and
# the twelve months, which `month_pages` adds where a test wants them.
WORKSHEETS = ["belongs_to", "how_to_use", "vision_mission", "year_goals", "values",
              "annual_calendar", "budget", "chores", "meal_plan", "grocery",
              "health_tracker", "emergency", "school_activities", "family_time",
              "vacation", "home_maintenance", "year_end", "index", "reading_log",
              "example_gratitude", "weekly", "daily"]


def document(design: str, size: str, pages: list[str], script: str) -> str:
    cfg = config.load(None)
    cfg.design, cfg.page_size, cfg.pages = designs.resolve(design), size, list(pages)
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg = config.validate(cfg)
    months = "months" in pages
    planned = [p for p in render.plan_pages(cfg)
               if p.slug in pages or (months and p.template == "pages/monthly.html")]
    page_html = render.render_html(cfg, planned, standalone=True, nav_pages=render.plan_pages(cfg))
    sections = page_html.split('<section class="page')
    tagged = [sections[0]] + [f'<section data-page="{p.slug}" class="page' + s
                              for p, s in zip(planned, sections[1:])]
    return "".join(tagged).replace("</body>", script + "</body>")


def measure(browser: Path, design: str, size: str, pages: list[str], script: str,
            result_id: str):
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="pages-") as tmp:
        page = Path(tmp) / "pages.html"
        page.write_text(document(design, size, pages, script), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=20000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(rf'<pre id="{result_id}">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{design} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))
