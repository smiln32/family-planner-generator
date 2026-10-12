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

import re
from concurrent.futures import ThreadPoolExecutor

import pytest

from _browser_pages import DESIGNS, WORKSHEETS, measure
from familyplanner import colours as roles

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
  // Colour maths for the stricter checks: CIE Lab, delta E, contrast, and
  // CSS colour-mix in sRGB.
  const rgb = c => parse(c).slice(0, 3);
  const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const lab = c => { const [r, g, b] = rgb(c).map(lin);
    const f = t => t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;
    const x = f((0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047), y = f(0.2126 * r + 0.7152 * g + 0.0722 * b),
          z = f((0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883);
    return [116 * y - 16, 500 * (x - y), 200 * (y - z)]; };
  const dE = (a, b) => { const p = lab(a), q = lab(b); return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]); };
  const chroma = c => { const [, a, b] = lab(c); return Math.hypot(a, b); };
  const contrast = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const mixed = (a, b, t) => { const p = rgb(a), q = rgb(b); return 'rgb(' + p.map((v, i) => v + (q[i] - v) * t).join(', ') + ')'; };
  const body = getComputedStyle(document.body);
  const paper = norm(body.getPropertyValue('--paper').trim());
  // A wash: the colour lies on the line from `base` to white or paper.
  const washOf = (c, base) => {
    for (const to of ['rgb(255, 255, 255)', paper]) for (let t = 0; t <= 1.0001; t += 0.02)
      if (dE(c, mixed(base, to, t)) < 3) return true;
    return false; };
  // Colours a fill may be: the palette (as the body sees it, since a design
  // class may set its own tokens), the roles, the look's own colours, and
  // washes of those; or a near-neutral (paper, white, greys).
  const PALETTE = ['navy', 'teal', 'pink', 'orange', 'green', 'purple', 'blue', 'red', 'brown', 'ink', 'paper', 'rule',
                   'butter', 'gold', 'gold-lt', 'sun'].map(n => norm(body.getPropertyValue('--' + n).trim()))
    .concat(['structure', 'weekend', 'winter', 'spring', 'summer', 'autumn'].map(role))
    .filter(c => c !== 'none');
  const allowedFill = c => chroma(c) < 6 || PALETTE.some(p => washOf(c, p));
  // The colour behind an element: its own fill or the nearest one under it.
  const behind = el => { for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const bg = norm(getComputedStyle(e).backgroundColor); if (bg !== 'none') return bg; }
    return paper; };
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
      // A tab, banner or header with a light fill: the fill is a wash of the
      // structure colour or a neutral, never another palette colour.
      const bg = norm(getComputedStyle(el).backgroundColor);
      if (bg !== 'none' && bg !== R.structure && chroma(bg) >= 6 && !washOf(bg, R.structure))
        P.push('structure fill: ' + name(el) + ' is filled ' + bg);
    }
    for (const el of sec.querySelectorAll('[data-day]')) {
      if (!visible(el)) continue;
      const k = key(el), we = el.dataset.day === 'weekend';
      if (we && k !== R.weekend) P.push('weekend: ' + name(el) + ' is ' + k);
      // Weekend text reads: 4.5:1 on whatever is behind it (or the pill's
      // text on the weekend fill).
      const text = norm(getComputedStyle(el).color), under = behind(el);
      if (we && text !== 'none' && contrast(text, under) < 4.5)
        P.push('weekend text ' + contrast(text, under).toFixed(2) + ':1 on ' + under + ': ' + name(el));
      if (!we && k === R.weekend) P.push('weekday in the weekend accent: ' + name(el));
    }
    // No stray fills: every solid fill (art aside) is a palette colour, a
    // role, a look's own colour, a wash of one, or a neutral.
    for (const el of sec.querySelectorAll('*')) {
      if (el.closest(ART) || el.closest('svg') || !visible(el)) continue;
      const bg = norm(getComputedStyle(el).backgroundColor);
      if (bg !== 'none' && !allowedFill(bg)) P.push('stray fill ' + bg + ' on ' + name(el));
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
    out.push({page, problems: [...new Set(P)], minis, roles: R,
              seasons: ['winter', 'spring', 'summer', 'autumn'].map(role)});
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


# Swiss grid and Boxed records have no colours to spare: their months stay in
# the structure colour and the season icons carry the season (coordinator
# decision, 2026-10-12, pending Carla's look).
SEASONS_OFF = {"swiss", "02a", "02b", "02c"}
MIN_SEASON_DELTA_E = 15


def _hex(css_rgb: str) -> str:
    return "#" + "".join(f"{int(v):02X}" for v in re.findall(r"\d+", css_rgb)[:3])


@pytest.mark.parametrize("design", DESIGNS)
def test_annual_calendar_months_follow_the_seasons(design, measured):
    annual = next(r for r in measured[design] if r["page"] == "annual_calendar")
    minis = annual["minis"]
    assert {season: len(colours) for season, colours in minis.items()} == \
        {"winter": 3, "spring": 3, "summer": 3, "autumn": 3}
    for season, colours in minis.items():
        assert len(set(colours)) == 1, f"{season} months differ: {colours}"
    four = {colours[0] for colours in minis.values()}
    if design in SEASONS_OFF:
        assert four == {annual["roles"]["structure"]}
        return
    assert len(four) == 4, f"seasons not distinct: {minis}"
    assert not four & {annual["roles"]["weekend"]}
    # The four read as four: far enough apart from each other.
    hexes = [_hex(c) for c in annual["seasons"]]
    for i, a in enumerate(hexes):
        for b in hexes[i + 1:]:
            assert roles.delta_e(a, b) >= MIN_SEASON_DELTA_E, f"seasons {a} and {b} too close"
