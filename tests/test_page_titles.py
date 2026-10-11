"""Every worksheet title is one colour and one line, printed in a real browser.

Carla asked on 2026-10-11 for the masthead title on every inside page
(Household Chores, Home Maintenance Checklist, Grocery Shopping, ...) to be
one colour and on one line in every design. Before, many designs split the
words over two or three lines and in two or more colours (a dark first word,
then a green word or multicoloured letters).

For every design (the thirteen looks, the twelve layouts, blank and the
retired original) at every page size, each page with a masthead is printed
and its title checked:

- all visible title text has one computed colour;
- the title is one line: every piece of it sits on the same line, and the
  title box is no taller than that line;
- it fits: nothing runs past the title's own box or off the page;
- it is no smaller than it must be: a title under the full title size
  (`type_size.title`) fills the width of its box.

The tagline or subtitle under the title (the banner, the strapline, the
year) is not part of the title and is left alone. Covers and month pages
have no masthead title of this kind and are not checked here.
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

DESIGNS = designs.names() + ["original"]
PAGES = ["vision_mission", "year_goals", "values", "annual_calendar", "budget", "chores",
         "meal_plan", "grocery", "health_tracker", "emergency", "school_activities",
         "family_time", "vacation", "home_maintenance", "year_end", "index",
         "reading_log", "example_gratitude"]

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const T = 0.75, out = [];
  for (const sec of document.querySelectorAll('section.page')) {
    const heads = sec.querySelector('.masthead .headings');
    const found = {page: sec.dataset.page, problems: []};
    out.push(found);
    if (!heads) { found.problems.push('no masthead'); continue; }
    const skip = '.year-tint, .annual-year, .year-blank, .banner, .strapline';
    const parts = [...heads.querySelectorAll('h1, .display')].filter(el =>
      !el.closest(skip) && !el.parentElement.closest('h1, .display')
      && getComputedStyle(el).visibility === 'visible' && getComputedStyle(el).display !== 'none');
    if (!parts.length) { found.problems.push('no title'); continue; }
    const colours = new Set(), rects = [];
    let lineH = 0;
    for (const part of parts) {
      const walk = document.createTreeWalker(part, NodeFilter.SHOW_TEXT);
      while (walk.nextNode()) {
        const n = walk.currentNode, el = n.parentElement;
        if (!n.textContent.trim()) continue;
        const cs = getComputedStyle(el);
        if (cs.visibility !== 'visible' || cs.display === 'none') continue;
        colours.add(cs.color);
        lineH = Math.max(lineH, parseFloat(cs.fontSize) * Math.max(1, parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) || 1.2));
        const range = document.createRange(); range.selectNodeContents(n);
        for (const r of range.getClientRects()) if (r.width) rects.push(r);
      }
    }
    if (colours.size !== 1) found.problems.push('colours: ' + [...colours].join(' | '));
    if (!rects.length) { found.problems.push('no visible title text'); continue; }
    const tops = rects.map(r => r.top), bottoms = rects.map(r => r.bottom);
    const minTop = Math.min(...tops), maxTop = Math.max(...tops);
    if (maxTop - minTop > T) found.problems.push('more than one line (' + rects.length + ' boxes, tops ' + minTop.toFixed(1) + '..' + maxTop.toFixed(1) + ')');
    const boxes = parts.map(p => p.getBoundingClientRect());
    const boxH = Math.max(...boxes.map(b => b.bottom)) - Math.min(...boxes.map(b => b.top));
    if (boxH > lineH * 1.3 + T) found.problems.push('title box ' + boxH.toFixed(1) + 'px tall for a ' + lineH.toFixed(1) + 'px line');
    const hb = heads.getBoundingClientRect(), sb = sec.getBoundingClientRect();
    const l = Math.min(...rects.map(r => r.left)), rr = Math.max(...rects.map(r => r.right));
    if (l < hb.left - T || rr > hb.right + T) found.problems.push('runs out of its box (' + (rr - l).toFixed(1) + 'px in ' + hb.width.toFixed(1) + 'px)');
    if (l < sb.left || rr > sb.right || Math.max(...bottoms) > sb.bottom) found.problems.push('off the page');
    // Shrunk only as far as needed: a title under the full title size fills its box.
    const full = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--type-title')) * 4 / 3;
    const size = Math.min(...parts.map(p => parseFloat(getComputedStyle(p).fontSize)));
    if (size < full - 0.1 && rr - l < hb.width * 0.95)
      found.problems.push('shrunk to ' + size.toFixed(1) + 'px but fills only ' + (rr - l).toFixed(0) + ' of ' + hb.width.toFixed(0) + 'px');
  }
  const pre = document.createElement('pre'); pre.id = 'titles';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""


def _document(design: str, size: str) -> str:
    cfg = config.load(None)
    cfg.design, cfg.page_size, cfg.pages = designs.resolve(design), size, list(PAGES)
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg = config.validate(cfg)
    pages = [p for p in render.plan_pages(cfg) if p.slug in PAGES]
    page_html = render.render_html(cfg, pages, standalone=True)
    sections = page_html.split('<section class="page')
    tagged = [sections[0]] + [f'<section data-page="{p.slug}" class="page' + s
                              for p, s in zip(pages, sections[1:])]
    return "".join(tagged).replace("</body>", MEASURE + "</body>")


def _measure(browser: Path, design: str, size: str) -> list[dict]:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="titles-") as tmp:
        page = Path(tmp) / "titles.html"
        page.write_text(_document(design, size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=15000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="titles">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{design} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))


CASES = [(design, size) for design in DESIGNS for size in config.PAGE_SIZES]


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], list[dict]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: _measure(browser, *case), CASES)))


@pytest.mark.parametrize("design,size", CASES)
def test_page_titles_are_one_colour_on_one_line(design, size, measured):
    results = measured[(design, size)]
    assert sorted(r["page"] for r in results) == sorted(PAGES)
    problems = [f"{r['page']}: {p}" for r in results for p in r["problems"]]
    assert problems == []
