"""The cover spot stays in its place, printed in a real browser.

For every look at every page size, the cover is printed with the optional
lines at their usual length and at their longest (family name 60 characters,
year text and extra line 80, and long single words). In each case:

- every line of the spot is inside the page and inside any box that clips it;
- no line runs out sideways;
- nothing else on the cover moves: each other element has the same box with
  the spot as without it.

The check is only fair in the look's own typefaces: fallback fonts have other
widths, so the lines wrap differently. The font files ship in the repo, and
tests/test_font_files.py fails if any is missing; as a safety net, a look
whose files are missing here is skipped, not failed.

What this cannot see is a line drawn over another part of the cover (a
title, a rule, the edge of a shape). That was checked by eye and by a pixel
script on 2026-10-10; see HANDOFF.md, "Cover options".
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

SETS = {
    "usual": {"family_name": "Sample", "cover_show_family": True, "cover_show_year": "custom",
              "cover_text": "2026–27", "cover_line": "Our year together"},
    "middle": {"family_name": "Castellanos Oyelaran Whitfield", "cover_show_family": True,
               "cover_show_year": "custom", "cover_text": "School year 2026 to 2027",
               "cover_line": "Our year together, one week at a time"},
    "longest": {"family_name": ("Abcdefghij Klmnopqrst " * 3)[:60].strip(), "cover_show_family": True,
                "cover_show_year": "custom",
                "cover_text": ("School year twenty twenty-six to twenty twenty-seven, "
                               "with love from all of us")[:80],
                "cover_line": ("Our year together, with every plan and every meal and "
                               "every small win written")[:80]},
    "long words": {"family_name": "Wolfeschlegelsteinhausen", "cover_show_family": True,
                   "cover_show_year": "custom", "cover_text": "Twentytwentysixtwentyseven",
                   "cover_line": "Supercalifragilisticexpi"},
}

MEASURE = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const R = r => ({x: r.left, y: r.top, w: r.width, h: r.height});
  function ink(el) {
    let u = null;
    const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (walk.nextNode()) {
      const n = walk.currentNode; if (!n.textContent.trim()) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      for (const r of range.getClientRects()) {
        if (!r.width) continue;
        u = u ? {l: Math.min(u.l, r.left), t: Math.min(u.t, r.top), r: Math.max(u.r, r.right), b: Math.max(u.b, r.bottom)}
              : {l: r.left, t: r.top, r: r.right, b: r.bottom};
      }
    }
    return u;
  }
  const inside = (a, r) => a.l >= r.left - 0.5 && a.t >= r.top - 0.5 && a.r <= r.right + 0.5 && a.b <= r.bottom + 0.5;
  const result = [];
  for (const sec of document.querySelectorAll('section.page')) {
    const spot = sec.querySelector('.lk-own');
    const found = {set: sec.dataset.set, problems: []};
    result.push(found);
    if (!spot) { found.problems.push('no spot'); continue; }
    const others = [...sec.querySelectorAll('*')].filter(el => el !== spot && !spot.contains(el) && !el.contains(spot));
    const before = others.map(el => R(el.getBoundingClientRect()));
    for (const line of spot.children) {
      const a = ink(line);
      if (!a) continue;
      if (line.scrollWidth > line.clientWidth + 1) found.problems.push(line.className + ' runs out sideways');
      for (let box = line.parentElement; box && box !== document.body; box = box.parentElement) {
        const cs = getComputedStyle(box);
        if ((box === sec || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') && !inside(a, box.getBoundingClientRect()))
          found.problems.push(line.className + ' leaves ' + (box === sec ? 'the page' : box.className));
      }
    }
    spot.style.display = 'none';
    others.forEach((el, i) => {
      const p = before[i], q = R(el.getBoundingClientRect());
      if (Math.abs(p.x - q.x) + Math.abs(p.y - q.y) + Math.abs(p.w - q.w) + Math.abs(p.h - q.h) > 0.01)
        found.problems.push((el.className || el.tagName) + ' moves');
    });
    spot.style.display = '';
  }
  const pre = document.createElement('pre'); pre.id = 'cover-fit';
  pre.textContent = JSON.stringify(result); document.body.appendChild(pre);
}); });
</script>
"""


FONT_DIR = render.STATIC_DIR / "fonts"


def _missing_fonts(look: str) -> list[str]:
    """Upright font files this look's typeface set needs that are missing.

    Italics are left out: a family may publish none, and then the browser
    slants the upright face on every machine alike.
    """
    faces = typefaces.resolve(designs.look_fonts(look))
    return [name for name in (typefaces.slug(f, w) for f, w in faces.wanted())
            if not (FONT_DIR / name).is_file()]


def _cover_section(cfg, name: str) -> str:
    body = render.render_html(cfg, render.plan_pages(cfg), standalone=True).split("<body", 1)[1]
    start = body.index('<section class="page')
    section = body[start:body.index("</section>", start) + len("</section>")]
    return section.replace('<section class="page', f'<section data-set="{name}" class="page', 1)


def _document(look: str, size: str) -> str:
    """One HTML file holding this look's cover once per text set."""
    cfgs = {}
    for name, fields in SETS.items():
        cfg = config.load(None)
        cfg.design, cfg.page_size, cfg.pages = look, size, ["cover"]
        # Each look is printed in its own typeface set, as a real book is.
        cfg.faces = typefaces.resolve(designs.look_fonts(look))
        for key, value in fields.items():
            setattr(cfg, key, value)
        cfgs[name] = config.validate(cfg)
    shell = render.render_html(cfgs["usual"], render.plan_pages(cfgs["usual"]), standalone=True)
    head, rest = shell.split("<body", 1)
    body_open = rest[:rest.index(">") + 1]
    sections = "".join(_cover_section(cfg, name) for name, cfg in cfgs.items())
    return f"{head}<body{body_open}{sections}{MEASURE}</body></html>"


def _measure(browser: Path, look: str, size: str) -> list[dict]:
    w, h = config.PAGE_SIZES[size]
    with tempfile.TemporaryDirectory(prefix="cover-fit-") as tmp:
        page = Path(tmp) / "cover.html"
        page.write_text(_document(look, size), encoding="utf-8")
        proc = subprocess.run(
            [str(browser), "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
             "--disable-extensions", "--allow-file-access-from-files",
             "--virtual-time-budget=15000", f"--user-data-dir={Path(tmp) / 'profile'}",
             f"--window-size={round(w * 96)},{round(h * 96)}", "--dump-dom", page.as_uri()],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", timeout=300)
    found = re.search(r'<pre id="cover-fit">(.*?)</pre>', proc.stdout, re.S)
    assert found, f"{look} {size}: no result from the browser\n{proc.stderr[-600:]}"
    return json.loads(html_lib.unescape(found.group(1)))


@pytest.fixture(scope="module")
def measured(browser) -> dict[tuple[str, str], list[dict]]:
    """Needs the shared `browser` fixture (tests/conftest.py): skips without one."""
    jobs = [(look, size) for look in designs.LOOKS if not _missing_fonts(look)
            for size in config.PAGE_SIZES]
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = pool.map(lambda job: _measure(browser, *job), jobs)
        return dict(zip(jobs, results))


@pytest.mark.parametrize("size", list(config.PAGE_SIZES))
@pytest.mark.parametrize("look", list(designs.LOOKS))
def test_cover_spot_stays_in_place(look, size, request):
    missing = _missing_fonts(look)
    if missing:
        pytest.skip(f"{look} fonts missing ({len(missing)} files, such as {missing[0]}); "
                    "restore familyplanner/static/fonts/ from git, or run "
                    "`python planner.py fonts --looks`")
    measured = request.getfixturevalue("measured")
    results = measured[(look, size)]
    assert [r["set"] for r in results] == list(SETS)
    problems = [f"{r['set']}: {p}" for r in results for p in r["problems"]]
    assert problems == []
