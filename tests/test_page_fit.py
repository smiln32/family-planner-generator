"""Every card and table fits its page, on every page, in a real browser.

Carla saw the third card at the foot of the Family Time page ("Monthly
Family Tradition") run off the right edge of a letter page in a layout.
The budget page had the same kind of fault at the small sizes, and
tests/test_budget_fit.py guards that one page. This test does the same
checks on every page a book can hold, cover excepted:

- every card, box, table, mini month and strip is inside the page margins
  (sides and bottom), and the footer is on the page;
- everything inside a card or box stays inside it; a card tab, which hangs
  over the card's top edge, stays within the card's sides (a long tab wraps
  onto a second line), and a full-width heading bar (which some looks run
  past the margins on purpose) stays on the page;
- nothing runs off the page, and no text runs out of its box.

The full matrix (all 27 designs at letter, 5.5x8 and 6x9, every page) was
run on 2026-10-12 with a scratch script; see HANDOFF.md. Here every design
is checked at letter and a spread of designs at the two small sizes, to keep
the suite's running time reasonable.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from _browser_pages import DESIGNS, WORKSHEETS, measure

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const T = 0.75, out = [];
  const BOX = '.card, .lx-box, .tbl, .mini, .focus-strip, .cal, .goal-box, .vm-box, .howto-box, '
    + '.belongs-card, .lkm-grid, .lkm-note, .values-note, .index-row, .famtime-meta, .school-meta, '
    + '.vac-meta, .maint-meta, .emg-top, .health-meta, .lx-cal, .lx-year';
  // Parts that run to the paper edge by design, and the title machinery,
  // which measures text in hidden copies.
  const BLEED = '.lkm-head, .lkm-band, .tab-rail, .masthead';
  const SKIP = '.pt-fit, .pt-probe, .cf, svg *';
  const name = el => el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '').trim().split(/\s+/).join('.')
    + (el.textContent.trim() ? ' "' + el.textContent.trim().replace(/\s+/g, ' ').slice(0, 24) + '"' : '');
  const shown = el => { const cs = getComputedStyle(el), r = el.getBoundingClientRect();
                        return cs.display !== 'none' && cs.visibility !== 'hidden' && (r.width || r.height); };
  for (const sec of document.querySelectorAll('section.page')) {
    const P = [];
    const cs = getComputedStyle(sec), sr = sec.getBoundingClientRect();
    // A worksheet on a small page is scaled (CSS zoom): its padding is read
    // unscaled, its boxes scaled.
    const z = sec.currentCSSZoom || 1;
    const left = sr.left + parseFloat(cs.paddingLeft) * z, right = sr.right - parseFloat(cs.paddingRight) * z;
    const bottom = sr.bottom - parseFloat(cs.paddingBottom) * z;
    for (const el of sec.querySelectorAll('*')) {
      if (el.matches(SKIP) || !shown(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.left < sr.left - T || r.right > sr.right + T || r.bottom > sr.bottom + T)
        P.push(name(el) + ' runs off the page');
      // Text that runs out: an element's own words past the edge of its box.
      if (!(el instanceof SVGElement) && getComputedStyle(el).display !== 'inline') {
        for (const n of el.childNodes) {
          if (n.nodeType !== 3 || !n.textContent.trim()) continue;
          const range = document.createRange(); range.selectNodeContents(n);
          const t = range.getBoundingClientRect();
          const across = getComputedStyle(el).writingMode.startsWith('horizontal')
            ? t.left < r.left - T || t.right > r.right + T : t.top < r.top - T || t.bottom > r.bottom + T;
          if (t.width && across) { P.push(name(el) + ' text runs out'); break; }
        }
      }
    }
    for (const box of sec.querySelectorAll(BOX)) {
      if (!shown(box) || box.closest(BLEED)) continue;
      const c = box.getBoundingClientRect();
      if (c.left < left - T || c.right > right + T) P.push(name(box) + ' outside the side margins');
      if (c.bottom > bottom + T) P.push(name(box) + ' below the bottom margin');
      if (!box.matches('.card, .lx-box')) continue;
      for (const el of box.querySelectorAll('*')) {
        if (el.matches(SKIP) || !shown(el)) continue;
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
        const r = el.getBoundingClientRect();
        if (el.closest('.card-tab, .lx-hd')) {
          // A tab hangs over the card's top edge but not past its sides
          // (a rotated tape tab may lean out by a hair).
          if (r.left < c.left - 2 || r.right > c.right + 2) P.push(name(el) + ' tab wider than its card');
        } else if (el.closest('.card-head')) {
          if (r.left < sr.left - T || r.right > sr.right + T) P.push(name(el) + ' off the page');
        } else if (r.left < c.left - T || r.right > c.right + T || r.top < c.top - T || r.bottom > c.bottom + T) {
          P.push(name(el) + ' leaves its card');
        }
      }
    }
    const foot = sec.querySelector('.page-footer');
    if (foot && shown(foot) && foot.getBoundingClientRect().bottom > sr.bottom + T) P.push('footer off the page');
    out.push({page: sec.dataset.page, problems: [...new Set(P)]});
  }
  const pre = document.createElement('pre'); pre.id = 'fit';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""

PAGES = WORKSHEETS + ["months"]
SMALL = ["editorial", "deco", "swiss", "cottage", "gazette", "02a", "06b", "11c", "12a", "blank", "original"]
CASES = [(d, "letter") for d in DESIGNS] + [(d, s) for d in SMALL for s in ("5.5x8", "6x9")]


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], list[dict]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = pool.map(lambda case: measure(browser, *case, PAGES, MEASURE, "fit"), CASES)
        return dict(zip(CASES, results))


@pytest.mark.parametrize("design,size", CASES)
def test_every_page_fits(design, size, measured):
    problems = [f"{r['page']}: {p}" for r in measured[(design, size)] for p in r["problems"]]
    assert problems == []
