"""The donut on the budget page prints as a whole circle, in a real browser.

The ring is drawn with a thick stroke, so its outer edge sits further out
than the circle's radius. If that edge passes the SVG's viewBox, the browser
cuts the ring off flat on every side (an SVG clips to its own box), and a
card or page that hides overflow can cut it too.

For a spread of designs and page sizes this prints the budget page and
checks, from the ring's own geometry:

- the ring's outer box is square (a circle, not an oval);
- it lies inside the SVG's box and inside every box that clips it.

Every design shares budget.html and the .pie rules in planner.css. On
2026-10-11 all 13 looks, 12 layouts, blank and original were checked at
all three sizes; see HANDOFF.md, "Budget donut".
"""

from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from familyplanner import config, designs, render, typefaces

CASES = [("editorial", "letter"), ("coastal", "letter"), ("02a", "letter"),
         ("06b", "letter"), ("06b", "5.5x8"), ("06b", "6x9"), ("11a", "letter"),
         ("12c", "letter"), ("blank", "letter"), ("original", "6x9")]

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const out = {problems: []};
  const svg = document.querySelector('svg.pie');
  if (!svg) out.problems.push('no donut');
  else {
    const c = svg.querySelector('circle');
    const r = c.r.baseVal.value + parseFloat(c.getAttribute('stroke-width')) / 2;
    const cx = c.cx.baseVal.value, cy = c.cy.baseVal.value, m = c.getScreenCTM();
    const pts = [[cx - r, cy - r], [cx + r, cy - r], [cx - r, cy + r], [cx + r, cy + r]]
      .map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
    const ring = {l: Math.min(...pts.map(p => p.x)), t: Math.min(...pts.map(p => p.y)),
                  r: Math.max(...pts.map(p => p.x)), b: Math.max(...pts.map(p => p.y))};
    const w = ring.r - ring.l, h = ring.b - ring.t;
    out.ring = [w, h];
    if (w < 40) out.problems.push('donut is only ' + w.toFixed(1) + 'px wide');
    if (Math.abs(w - h) > 0.5) out.problems.push('donut is not round: ' + w.toFixed(1) + ' x ' + h.toFixed(1));
    for (let el = svg; el && el !== document.documentElement; el = el.parentElement) {
      const cs = getComputedStyle(el);
      if (el !== svg && el.tagName !== 'SECTION' && cs.overflowX === 'visible' && cs.overflowY === 'visible') continue;
      const b = el.getBoundingClientRect();
      const cut = Math.max(b.left - ring.l, b.top - ring.t, ring.r - b.right, ring.b - b.bottom);
      if (cut > 0.5) out.problems.push('donut cut ' + cut.toFixed(1) + 'px by ' + el.tagName + '.' + (el.getAttribute('class') || ''));
    }
  }
  const pre = document.createElement('pre'); pre.id = 'donut';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""


def _document(design: str, size: str) -> str:
    cfg = config.load(None)
    cfg.design, cfg.page_size, cfg.pages = designs.resolve(design), size, ["budget"]
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg = config.validate(cfg)
    page = render.render_html(cfg, render.plan_pages(cfg), standalone=True)
    return page.replace("</body>", MEASURE + "</body>")


def _measure(browser: Path, design: str, size: str) -> dict:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="donut-") as tmp:
        page = Path(tmp) / "budget.html"
        page.write_text(_document(design, size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=15000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="donut">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{design} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], dict]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: _measure(browser, *case), CASES)))


@pytest.mark.parametrize("design,size", CASES)
def test_budget_donut_is_a_whole_circle(design, size, measured):
    assert measured[(design, size)]["problems"] == []
