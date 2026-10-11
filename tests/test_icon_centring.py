"""Icons sit in the middle of their round badges, printed in a real browser.

Carla saw on 2026-10-11 that the icons in the Emergency Contacts list were
not centred in their circles. The badge (`chip()` in macros.html) centres
the icon's 24x24 box exactly; the drawings inside some boxes were off
centre (the flame two units to the right, the tooth one to the left, wifi
low, the drop high...), so the ink sat off the middle of the circle.

For each badge this finds where the icon's ink really is (the symbol drawn
into a canvas and its pixels scanned) and checks that the middle of the
ink is within half a pixel of the middle of the circle, across and down.
The Emergency page is checked in every design, and every page that has
badges in a look, a layout and the original design.
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

TOLERANCE_PX = 0.5
BADGE_PAGES = ["belongs_to", "how_to_use", "vision_mission", "year_goals", "values", "budget",
               "chores", "grocery", "health_tracker", "emergency", "school_activities",
               "family_time", "january", "december", "vacation", "home_maintenance", "year_end"]

MEASURE = r"""
<script>
window.addEventListener('load', async () => {
  await document.fonts.ready;
  const N = 480, ink = {};
  async function inkOf(id) {
    if (ink[id]) return ink[id];
    const sym = document.getElementById(id);
    const vb = sym.getAttribute('viewBox').split(/[\s,]+/).map(Number);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${N}" height="${N}" viewBox="${vb.join(' ')}">`
      + sym.innerHTML.replace(/opacity="[^"]*"/g, '') + '</svg>';
    const img = new Image(); img.src = 'data:image/svg+xml,' + encodeURIComponent(svg); await img.decode();
    const c = document.createElement('canvas'); c.width = c.height = N;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0);
    const d = x.getImageData(0, 0, N, N).data;
    let l = N, t = N, r = -1, b = -1;
    for (let j = 0; j < N; j++) for (let i = 0; i < N; i++)
      if (d[(j * N + i) * 4 + 3] > 5) { l = Math.min(l, i); r = Math.max(r, i); t = Math.min(t, j); b = Math.max(b, j); }
    // Middle of the ink as a fraction of the drawn box (0.5 = centred).
    return ink[id] = {fx: (l + r + 1) / 2 / N, fy: (t + b + 1) / 2 / N};
  }
  const out = [];
  for (const sec of document.querySelectorAll('section.page')) {
    for (const chip of sec.querySelectorAll('.chip')) {
      const c = chip.getBoundingClientRect();
      if (!c.width || getComputedStyle(chip).display === 'none') continue;
      const svg = chip.querySelector('svg'), s = svg.getBoundingClientRect();
      const id = svg.querySelector('use').getAttribute('href').slice(1);
      const m = await inkOf(id);
      const dx = s.left + s.width * m.fx - (c.left + c.width / 2);
      const dy = s.top + s.height * m.fy - (c.top + c.height / 2);
      out.push({page: sec.dataset.page, icon: id, size: +c.width.toFixed(1), dx: +dx.toFixed(2), dy: +dy.toFixed(2)});
    }
  }
  const pre = document.createElement('pre'); pre.id = 'icons';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
});
</script>
"""


def _document(design: str, pages: list[str], size: str) -> str:
    cfg = config.load(None)
    cfg.design, cfg.page_size = designs.resolve(design), size
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg = config.validate(cfg)
    chosen = [p for p in render.plan_pages(cfg) if p.slug in pages]
    page_html = render.render_html(cfg, chosen, standalone=True)
    parts = page_html.split('<section class="page')
    tagged = [parts[0]] + [f'<section data-page="{p.slug}" class="page' + s for p, s in zip(chosen, parts[1:])]
    return "".join(tagged).replace("</body>", MEASURE + "</body>")


def _measure(browser: Path, design: str, pages: tuple[str, ...], size: str) -> list[dict]:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="icons-") as tmp:
        page = Path(tmp) / "icons.html"
        page.write_text(_document(design, list(pages), size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=20000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="icons">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{design} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))


CASES = ([(d, ("emergency",), "letter") for d in designs.names() + ["original"]]
         + [(d, tuple(BADGE_PAGES), size) for d in ("editorial", "06b", "original")
            for size in ("letter", "5.5x8")])


@pytest.fixture(scope="module")
def measured(browser):
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: _measure(browser, *case), CASES)))


@pytest.mark.parametrize("design,pages,size", CASES,
                         ids=[f"{d}-{'emergency' if len(p) == 1 else 'all'}-{s}" for d, p, s in CASES])
def test_icons_are_centred_in_their_badges(design, pages, size, measured):
    results = measured[(design, pages, size)]
    off = sorted({f"{r['page']} {r['icon']} in a {r['size']}px badge: {r['dx']:+.2f}px across, {r['dy']:+.2f}px down"
                  for r in results if abs(r["dx"]) > TOLERANCE_PX or abs(r["dy"]) > TOLERANCE_PX})
    assert off == []


def test_emergency_contacts_have_badges():
    # The layouts on looks 02 and 11 hide badges by design; every other design shows them.
    html = _document("editorial", ["emergency"], "letter")
    assert html.count('class="chip') >= 20
