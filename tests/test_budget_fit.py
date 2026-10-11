"""Every card on the budget page fits on a small page, in a real browser.

At 5.5x8 and 6x9 the budget page used to push its right-hand cards
(Expenses Summary, Expenses Breakdown) past the right margin and off the
page, and in many designs the Notes card and footer off the bottom. Card
content sized for letter (a 1.3in donut, the legend, 1.5in total boxes,
long write-on lines) did not shrink with the page.

For a spread of designs at both small sizes this prints the budget page and
checks:

- every card is inside the page margins (sides and bottom), and the footer
  is on the page;
- everything in a card stays inside it; a card tab, which hangs over the
  card's top edge, stays inside the side margins, and a full-width heading
  bar (which some looks run past the margins on purpose) stays on the page;
- no text runs out of its box, and the parts of a row (legend, $ lines,
  total bars, the CATEGORY/BUDGET header) do not overlap.

On 2026-10-11 all 27 designs were checked at all three sizes, and every
letter page was pixel-identical before and after; see HANDOFF.md,
"Budget donut".
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

CASES = [(design, size) for design in ("editorial", "gazette", "02b", "06a", "06b", "11a", "12c", "blank")
         for size in ("5.5x8", "6x9")]

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const P = [], T = 0.5, sec = document.querySelector('section.page');
  const cs = getComputedStyle(sec), sr = sec.getBoundingClientRect();
  const left = sr.left + parseFloat(cs.paddingLeft), right = sr.right - parseFloat(cs.paddingRight);
  const bottom = sr.bottom - parseFloat(cs.paddingBottom);
  const name = el => el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '').split(' ').join('.')
    + (el.textContent.trim() ? ' "' + el.textContent.trim().replace(/\s+/g, ' ').slice(0, 24) + '"' : '');
  for (const card of sec.querySelectorAll('.card')) {
    const c = card.getBoundingClientRect();
    if (c.left < left - T || c.right > right + T) P.push(name(card) + ' outside the side margins');
    if (c.bottom > bottom + T) P.push(name(card) + ' below the bottom margin');
    for (const el of card.querySelectorAll('*')) {
      if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
      const r = el.getBoundingClientRect();
      if (!r.width && !r.height) continue;
      if (el.closest('.card-tab')) {
        if (r.left < left - T || r.right > right + T) P.push(name(el) + ' tab outside the side margins');
      } else if (el.closest('.card-head')) {
        if (r.left < sr.left - T || r.right > sr.right + T) P.push(name(el) + ' off the page');
      } else if (r.left < c.left - T || r.right > c.right + T || r.top < c.top - T || r.bottom > c.bottom + T) {
        P.push(name(el) + ' leaves its card');
      }
      if (!(el instanceof SVGElement) && getComputedStyle(el).display !== 'inline'
          && el.scrollWidth > el.clientWidth + 1) P.push(name(el) + ' text runs out');
    }
    for (const row of card.querySelectorAll('.key-row, .ie-row, .total-bar, .ie-head, .pie-wrap')) {
      const kids = [...row.children].map(k => k.getBoundingClientRect()).filter(r => r.width);
      for (let i = 1; i < kids.length; i++)
        if (kids[i].left < kids[i - 1].right - T) P.push('parts overlap in ' + name(row));
    }
  }
  const foot = sec.querySelector('.page-footer');
  if (foot && foot.getBoundingClientRect().bottom > sr.bottom + T) P.push('footer off the page');
  const pre = document.createElement('pre'); pre.id = 'fit';
  pre.textContent = JSON.stringify(P); document.body.appendChild(pre);
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


def _measure(browser: Path, design: str, size: str) -> list[str]:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="budget-fit-") as tmp:
        page = Path(tmp) / "budget.html"
        page.write_text(_document(design, size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=15000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="fit">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{design} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], list[str]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: _measure(browser, *case), CASES)))


@pytest.mark.parametrize("design,size", CASES)
def test_budget_cards_fit_a_small_page(design, size, measured):
    assert sorted(set(measured[(design, size)])) == []
