"""A look cover fits its title when another typeface set is chosen.

Each of the thirteen look covers was drawn for its own typeface set. In the
editor any of the 52 sets can be picked for any look, and before
2026-10-11 a wider or taller set could push a cover title off the page
(Editorial's "HOME", the Gazette's name), out of its oval (Cottage) or
across a rule. Now each title line keeps to its room and scales down
(fit() in templates/look_cover.html, ".cf" in static/looks.css).

For every look at every page size this prints the cover in its own set and
in six others chosen to stress it: the widest display face (carbon-copy),
two heavy display faces (par-avion, good-days), the tallest script
(heirloom), a wide caps face (midnight-keepsake) and the narrowest
(wildflower). In each other set:

- every piece of text (its ink, from the font's real glyph bounds) stays
  on the page and inside any box that clips it;
- no text newly crosses another text or a drawn shape (a block of colour,
  a rule, a frame or the oval) that it was clear of, or wholly inside, in
  the look's own set.

In the look's own set the cover prints exactly as designed: no fit markup
at all, so it is pixel-identical to the approved cover (checked
2026-10-11 for all 39 covers). The first test guards that.

On 2026-10-11 all 52 sets were checked this way for all 13 looks at all 3
sizes, with no problems; see HANDOFF.md.
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

OTHER_SETS = ["carbon-copy", "par-avion", "good-days", "heirloom", "midnight-keepsake", "wildflower"]

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const T = 0.5;
  const ctx = document.createElement('canvas').getContext('2d');
  function inkOf(el) {
    let u = null;
    const cs = getComputedStyle(el);
    ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    ctx.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
    for (const n of el.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      const m = ctx.measureText(n.textContent.trim());
      const fh = m.fontBoundingBoxAscent + m.fontBoundingBoxDescent;
      const r0 = document.createRange(); r0.selectNodeContents(n);
      for (const r of r0.getClientRects()) {
        if (!r.width) continue;
        const s = r.height / fh;   // a transform scales the box
        const box = {l: r.left, r: r.right,
                     t: r.top + (m.fontBoundingBoxAscent - m.actualBoundingBoxAscent) * s,
                     b: r.top + (m.fontBoundingBoxAscent + m.actualBoundingBoxDescent) * s};
        u = u ? {l: Math.min(u.l, box.l), t: Math.min(u.t, box.t), r: Math.max(u.r, box.r), b: Math.max(u.b, box.b)} : box;
      }
    }
    return u;
  }
  const painted = el => { const cs = getComputedStyle(el);
    return (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') || cs.backgroundImage !== 'none'
      || ['Top','Right','Bottom','Left'].some(s => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none')
      || cs.boxShadow !== 'none' || el.tagName.toLowerCase() === 'svg'; };
  function rel(a, o) {
    const cs = getComputedStyle(o), r = o.getBoundingClientRect();
    const filled = (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== 'transparent') || cs.backgroundImage !== 'none';
    const bw = k => parseFloat(cs['border' + k + 'Width']) || 0;
    const outer = B(r);
    if (!hit(a, outer)) return 'out';
    const inner = filled ? outer : {l: r.left + bw('Left'), t: r.top + bw('Top'), r: r.right - bw('Right'), b: r.bottom - bw('Bottom')};
    const round = parseFloat(cs.borderTopLeftRadius) >= Math.min(r.width, r.height) / 2 - 1 && cs.borderTopLeftRadius.includes('%') || cs.borderTopLeftRadius === '50%';
    let inside;
    if (round) {
      const cx = (inner.l + inner.r) / 2, cy = (inner.t + inner.b) / 2, rx = (inner.r - inner.l) / 2, ry = (inner.b - inner.t) / 2;
      inside = [[a.l, a.t], [a.r, a.t], [a.l, a.b], [a.r, a.b]].every(([x, y]) => ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0);
    } else inside = a.l >= inner.l - T && a.r <= inner.r + T && a.t >= inner.t - T && a.b <= inner.b + T;
    return inside ? 'in' : 'cross';
  }
  const hit = (a, b) => a.l < b.r - T && b.l < a.r - T && a.t < b.b - T && b.t < a.b - T;
  const B = r => ({l: r.left, t: r.top, r: r.right, b: r.bottom});
  const txt = el => { const c = el.cloneNode(true); c.querySelectorAll('.cf-probe').forEach(p => p.remove()); return c.textContent.trim().replace(/\s+/g, ' ').slice(0, 18); };
  const path = el => { const p = []; for (let x = el; x && !x.matches('section'); x = x.parentElement)
      p.unshift((x.getAttribute('class') || x.tagName.toLowerCase()).split(' ')[0] + ':' + [...x.parentElement.children].indexOf(x)); return p.join('>'); };
  const name = el0 => { const el = el0.matches('.cf-text') ? el0.closest('.cf').parentElement : el0;
    return path(el) + (txt(el) ? ' "' + txt(el) + '"' : ''); };
  const out = [];
  for (const sec of document.querySelectorAll('section.page')) {
    const els = [...sec.querySelectorAll('*')].filter(e => getComputedStyle(e).visibility === 'visible');
    const texts = els.map(e => [e, inkOf(e)]).filter(([e, i]) => i);
    const shapes = els.filter(e => painted(e)).map(e => [e, B(e.getBoundingClientRect())]);
    const found = {set: sec.dataset.set, problems: [], pairs: []};
    out.push(found);
    for (const [e, ink] of texts) {
      for (let box = e; box; box = box.parentElement) {
        const cs = getComputedStyle(box);
        if (box === sec || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
          const r = box.getBoundingClientRect();
          if (ink.l < r.left - T || ink.t < r.top - T || ink.r > r.right + T || ink.b > r.bottom + T)
            found.problems.push(name(e) + ' leaves ' + (box === sec ? 'the page' : name(box)));
          if (box === sec) break;
        }
      }
      for (const [o, ob] of texts) {
        if (o === e || o.contains(e) || e.contains(o)) continue;
        found.pairs.push(['text ' + name(e) + ' x ' + name(o), hit(ink, ob) ? 'cross' : 'out']);
      }
      for (const [o, ob] of shapes) {
        if (o === e || o.contains(e) || e.contains(o)) continue;
        found.pairs.push(['shape ' + name(e) + ' x ' + name(o), rel(ink, o)]);
      }
    }
  }
  const pre = document.createElement('pre'); pre.id = 'cover-type';
  pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""


def _cfg(look: str, size: str, set_name: str) -> config.Config:
    cfg = config.load(None)
    cfg.design, cfg.page_size, cfg.pages = look, size, ["cover"]
    cfg.faces = typefaces.resolve(set_name)
    return config.validate(cfg)


def _cover(cfg: config.Config) -> str:
    body = render.render_html(cfg, render.plan_pages(cfg), standalone=True).split("<body", 1)[1]
    start = body.index('<section class="page')
    return body[start:body.index("</section>", start) + len("</section>")]


def _document(look: str, size: str) -> str:
    """One HTML file: the cover in the look's own set, then in each other set.

    Each section sets its own font variables, and the head carries every
    set's @font-face rules, so all of them print side by side.
    """
    own = designs.look_fonts(look)
    names = [own] + [s for s in OTHER_SETS if s != own]
    shell = render.render_html(_cfg(look, size, own), render.plan_pages(_cfg(look, size, own)), standalone=True)
    head, rest = shell.split("<body", 1)
    body_open = rest[:rest.index(">") + 1]
    fonts, sections = set(), []
    for name in names:
        cfg = _cfg(look, size, name)
        fonts.update(render._fonts_css(cfg).splitlines())
        f = cfg.faces
        style = html_lib.escape(f"--font-display:{f.stack('display')};--font-script:{f.stack('script')};"
                                f"--font-body:{f.stack('body')}")
        sections.append(_cover(cfg).replace(
            '<section class="page', f'<section data-set="{name}" style="{style}" class="page', 1))
    head = head.replace("</style>", "\n".join(sorted(fonts)) + "\n</style>", 1)
    return f"{head}<body{body_open}{''.join(sections)}{MEASURE}</body></html>"


def _measure(browser: Path, look: str, size: str) -> dict[str, list[str]]:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="cover-type-") as tmp:
        page = Path(tmp) / "cover.html"
        page.write_text(_document(look, size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=20000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="cover-type">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{look} {size}: no result from the browser\n{proc.stderr[-600:]}"
    results = json.loads(html_lib.unescape(found.group(1)))
    own = dict(map(tuple, results[0]["pairs"]))
    out = {}
    for r in results[1:]:
        crossed = {f"{key}: {own.get(key)} in the own set, crossing here"
                   for key, rel in map(tuple, r["pairs"]) if rel == "cross" and own.get(key) in ("out", "in")}
        out[r["set"]] = r["problems"] + sorted(crossed)
    return out


def test_own_set_cover_prints_no_fit_markup():
    """The look's own set prints the cover as designed; another set gets the fit."""
    for look in designs.LOOKS:
        own = _cover(_cfg(look, "letter", designs.look_fonts(look)))
        assert 'class="cf' not in own, look
        other = "wildflower" if designs.look_fonts(look) != "wildflower" else "carbon-copy"
        assert 'class="cf' in _cover(_cfg(look, "letter", other)), look


CASES = [(look, size) for look in designs.LOOKS for size in config.PAGE_SIZES]


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], dict[str, list[str]]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: _measure(browser, *case), CASES)))


@pytest.mark.parametrize("look,size", CASES)
def test_cover_title_fits_in_other_typeface_sets(look, size, measured):
    results = measured[(look, size)]
    assert set(results) == {s for s in OTHER_SETS if s != designs.look_fonts(look)}
    problems = [f"{name}: {p}" for name, found in results.items() for p in found]
    assert problems == []
