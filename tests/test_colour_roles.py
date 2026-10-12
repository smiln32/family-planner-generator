"""Every page follows the colour rule, measured in a real browser.

Carla found the colours inside the worksheets haphazard (2026-10-12): table
header cells alternating navy and red, day pills alternating, card tabs in
different colours, and the annual calendar's month headers in a random run of
red, navy and blue. She approved this rule for all pages in all designs
(_config/design-system.md, familyplanner/colours.py):

1. Structure: every table header, card tab or heading, section label,
   banner and badge circle is one colour, the design's structure colour.
2. Weekend: Saturday and Sunday labels, pills and dates use the weekend
   accent; weekdays do not; and the accent appears nowhere else on a page.
3. Seasons: the annual calendar's month boxes follow the seasons, December
   to February one colour, March to May one, June to August one, September
   to November one, and the four are different.

For each design every worksheet page and the twelve month pages are printed
and the computed colours read back. An element's colour is its fill when it
has a solid, dark enough fill, and otherwise its text (a light tint behind
dark text is a neutral fill). This file checks letter only; colour does not
change with the page size.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from _browser_pages import DESIGNS, WORKSHEETS, measure

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const root = getComputedStyle(document.documentElement);
  // Any CSS colour (rgb(), color(srgb ...) from color-mix, a hex) as
  // "rgb(r, g, b)" with 0-255 channels, or "none" when it is see-through.
  const ctx = document.createElement('canvas').getContext('2d', {willReadFrequently: true});
  const norm = c => {
    if (!c || c === 'none' || c === 'transparent') return 'none';
    ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
    const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
    return a < 128 ? 'none' : `rgb(${r}, ${g}, ${b})`;
  };
  const role = n => norm(root.getPropertyValue('--c-' + n).trim());
  const R = {structure: role('structure'), weekend: role('weekend')};
  const parse = c => (c.match(/[\d.]+/g) || []).map(Number);
  const lum = c => { const [r, g, b] = parse(c).map(v => v / 255).map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
                     return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const solid = c => c !== 'none';
  const visible = el => { const cs = getComputedStyle(el), r = el.getBoundingClientRect();
                          return cs.display !== 'none' && cs.visibility === 'visible' && r.width > 0 && r.height > 0; };
  // The colour an element shows: a solid dark fill, else its text (or an
  // icon's fill, for a badge on a light wash).
  const key = el => {
    const cs = getComputedStyle(el), bg = norm(cs.backgroundColor);
    if (solid(bg) && lum(bg) < 0.45) return bg;
    if (el.matches('.chip')) { const ico = el.querySelector('.ico'); if (ico) return norm(getComputedStyle(ico).fill); }
    return norm(cs.color);
  };
  const name = el => el.tagName.toLowerCase() + '.' + (el.getAttribute('class') || '').trim().split(/\s+/).join('.')
    + (el.textContent.trim() ? ' "' + el.textContent.trim().replace(/\s+/g, ' ').slice(0, 20) + '"' : '');
  const STRUCT = ['.tbl thead tr:first-child th:not(.corner):not([data-day])', '.card-tab:not([data-day])',
    '.card-head', '.lx-hd:not([data-day])', '.banner', '.chip', '.famtime-label', '.maint-label',
    '.ye-head > span', '.vm-tag', '.howto-title', '.num', '.lx-num', '.dates-label .script',
    '.lk-month:not(.lkm-bauhaus) .lkm-label', '.mini th[data-day="weekday"]'].join(',');
  const ART = '.art, .mark, .mark-lg, .crest, .belongs-foot, .values-foot, .heart-tree, .divider, '
    + '.page-footer, .pie, .pie-key, .masthead h1, .pt-fit, .belongs-top, .howto-top, .lkm-orn, .lkm-band, '
    // Page titles keep their colour (Farmhouse sets its titles and month
    // names in the barn red that is also its weekend accent).
    + '.lkm-name';
  const DAY = '[data-day="weekend"], .we, .lx-we, .lkm-we';
  const out = [];
  for (const sec of document.querySelectorAll('section.page')) {
    const P = [], page = sec.dataset.page;
    for (const el of sec.querySelectorAll(STRUCT)) {
      if (!visible(el) || el.closest(DAY)) continue;
      const k = key(el);
      if (k !== R.structure) P.push('structure: ' + name(el) + ' is ' + k);
    }
    for (const el of sec.querySelectorAll('[data-day]')) {
      if (!visible(el)) continue;
      const k = key(el), we = el.dataset.day === 'weekend';
      if (we && k !== R.weekend) P.push('weekend: ' + name(el) + ' is ' + k);
      if (!we && k === R.weekend) P.push('weekday in the weekend accent: ' + name(el));
    }
    // The weekend accent means the weekend and nothing else.
    for (const el of sec.querySelectorAll('*')) {
      if (el.closest(ART) || el.closest(DAY) || !visible(el)) continue;
      if (el.closest('svg') && !el.matches('svg.ico')) continue;
      const cs = getComputedStyle(el);
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      const used = [];
      if (own && norm(cs.color) === R.weekend) used.push('text');
      if (norm(cs.backgroundColor) === R.weekend) used.push('fill');
      if (el.matches('svg.ico') && norm(cs.fill) === R.weekend) used.push('icon');
      for (const side of ['Top', 'Right', 'Bottom', 'Left'])
        if (parseFloat(cs['border' + side + 'Width']) > 0 && cs['border' + side + 'Style'] !== 'none'
            && norm(cs['border' + side + 'Color']) === R.weekend) { used.push('border'); break; }
      if (used.length) P.push('weekend accent used for ' + used.join('+') + ' on ' + name(el));
    }
    const minis = {};
    for (const m of sec.querySelectorAll('.mini[data-season]')) {
      const head = m.querySelector('.mini-head');
      (minis[m.dataset.season] = minis[m.dataset.season] || []).push(norm(getComputedStyle(head).backgroundColor));
    }
    out.push({page, problems: [...new Set(P)], minis, roles: R});
  }
  const pre = document.createElement('pre'); pre.id = 'roles';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""

PAGES = WORKSHEETS + ["months"]


@pytest.fixture(scope="module")
def measured(browser) -> dict[str, list[dict]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = pool.map(lambda d: measure(browser, d, "letter", PAGES, MEASURE, "roles"), DESIGNS)
        return dict(zip(DESIGNS, results))


@pytest.mark.parametrize("design", DESIGNS)
def test_every_page_follows_the_colour_rule(design, measured):
    results = measured[design]
    assert len(results) >= len(WORKSHEETS) + 12 - 2  # weekly and daily join layout books only
    problems = [f"{r['page']}: {p}" for r in results for p in r["problems"]]
    assert problems == []


@pytest.mark.parametrize("design", DESIGNS)
def test_annual_calendar_months_follow_the_seasons(design, measured):
    annual = next(r for r in measured[design] if r["page"] == "annual_calendar")
    minis = annual["minis"]
    assert {season: len(colours) for season, colours in minis.items()} == \
        {"winter": 3, "spring": 3, "summer": 3, "autumn": 3}
    for season, colours in minis.items():
        assert len(set(colours)) == 1, f"{season} months differ: {colours}"
    four = {colours[0] for colours in minis.values()}
    assert len(four) == 4, f"seasons not distinct: {minis}"
    assert not four & {annual["roles"]["weekend"]}
