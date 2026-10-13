"""Recipes (Phase 2 step 5, 2026-10-13): the owner's chosen directions for
Editorial, Farmhouse and Mid-century, built as catalog-driven recipes.

A recipe (chrome.Recipe) adds a type scale, spacing, text colour policy,
title area, icons, motif, section language, content exceptions and, per page
type, a shared composition (templates/compose/). Here:

- recipes validate, and an unknown layout id (or any other value outside the
  closed vocabularies) fails with a clear message;
- a design without a recipe prints the default recipe, which adds nothing;
- each trio page uses the composition the owner chose;
- Mid-century prints no text in the ink colour on any page, and every text
  reads at 4.5:1 on its ground;
- every text of the trio prints at or above the adopted print minimums,
  at letter and at the small sizes;
- the annual calendar leaves no empty band of 10% of the page or more;
- the calendars print the right dates for 2027 and 2028 (a leap year),
  checked against Python's calendar module;
- a theme, a palette block and a typeface set still take effect on the
  composed pages, and repeated builds are byte-identical.
"""

from __future__ import annotations

import calendar
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

from _browser_pages import measure
from familyplanner import chrome, config, designs, render, themes, typefaces

TRIO = ("editorial", "farmhouse", "midcentury")

# The owner's decisions (2026-10-13).
CHOSEN = {
    "editorial": {"family_time": "department", "annual_calendar": "broadsheet", "emergency": "department"},
    "farmhouse": {"family_time": "recipe", "annual_calendar": "recipe", "emergency": "recipe"},
    "midcentury": {"family_time": "band", "annual_calendar": "shapegrid", "emergency": "shapegrid"},
}


def _cfg(design: str, pages: list[str], **kw):
    cfg = config.load(None)
    cfg.design = designs.resolve(design)
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg.pages = list(pages)
    for k, v in kw.items():
        setattr(cfg, k, v)
    return config.validate(cfg)


def _html(design: str, pages: list[str], **kw) -> str:
    cfg = _cfg(design, pages, **kw)
    return render.render_html(cfg, render.plan_pages(cfg), standalone=True)


# --- validation ---------------------------------------------------------------

def test_an_unknown_layout_id_fails_clearly():
    with pytest.raises(ValueError, match=r"unknown layout id 'magazine' for family_time; choose one of "
                                         r"default, department, recipe, band"):
        chrome.Recipe(id="x", layouts={"family_time": "magazine"})
    with pytest.raises(ValueError, match="no layout variants for page type 'chores'"):
        chrome.Recipe(id="x", layouts={"chores": "default"})


@pytest.mark.parametrize("kwargs, message", [
    ({"title_area": "banner"}, "title_area='banner' is not one of"),
    ({"text": "black"}, "text='black' is not one of"),
    ({"icons": "emoji"}, "icons='emoji' is not one of"),
    ({"motif": "flowers"}, "motif='flowers' is not one of"),
    ({"sections": "cards"}, "sections='cards' is not one of"),
    ({"omit": {"emergency": ("checklist",)}}, "section 'checklist' cannot be left out"),
    ({"omit": {"family_time": ("ideas",)}}, "omittable: none"),
    ({"print_min": {"body": 5}}, "under the adopted 7.0pt"),
    ({"print_min": {"sparkle": 7}}, "unknown role"),
    ({"type": {"sparkle": chrome.TypeRole("body", 9)}}, "unknown type role"),
    ({"type": {"body": chrome.TypeRole("body", 6.5)}}, "body is 6.5pt at letter, under its 7.0pt"),
    ({"space": (0.1, 0.2)}, "seven steps"),
    ({"kicker": "<b>bold</b>"}, "short plain line"),
])
def test_a_recipe_outside_the_vocabulary_fails_clearly(kwargs, message):
    with pytest.raises(ValueError, match=re.escape(message)):
        chrome.Recipe(id="x", **kwargs)


@pytest.mark.parametrize("kwargs, message", [
    ({"weight": 500}, "type weight 500 is not one of"),
    ({"face": "handwriting"}, "type face 'handwriting'"),
    ({"case": "title"}, "type case 'title'"),
    ({"size": 80}, "out of range"),
])
def test_a_type_role_outside_the_vocabulary_fails_clearly(kwargs, message):
    args = {"face": "body", "size": 9.0, **kwargs}
    with pytest.raises(ValueError, match=re.escape(message)):
        chrome.TypeRole(**args)


def test_the_default_recipe_adds_nothing():
    rc = chrome.DEFAULT_RECIPE
    assert rc.classes() == [] and rc.tokens() == {}
    assert all(rc.layout(page) == "default" for page in chrome.LAYOUT_VARIANTS)
    for entry in chrome.CATALOG.values():
        if entry.id not in TRIO:
            assert entry.recipe is None and entry.active_recipe is rc, entry.id
            assert " rx" not in f" {entry.body_classes()} ", entry.id


def test_only_the_trio_has_a_recipe_and_its_fonts_are_bundled():
    for design in TRIO:
        entry = chrome.get(design)
        assert entry.approved and entry.active_recipe is entry.recipe
        assert chrome.missing_font_files(entry.recipe, entry.fonts_ref) == []
        classes = entry.body_classes().split()
        assert classes[-7:] == entry.recipe.classes()


def test_an_unapproved_design_never_prints_a_recipe():
    entry = replace(chrome.get("editorial"), id="draft", approved=False,
                    current=chrome.get("nordic").current)
    assert entry.active_recipe is chrome.DEFAULT_RECIPE


# --- compositions -----------------------------------------------------------------

@pytest.mark.parametrize("design", TRIO)
def test_each_trio_page_uses_its_chosen_layout(design):
    assert chrome.get(design).recipe.layouts == CHOSEN[design]
    html = _html(design, list(CHOSEN[design]))
    for page, layout in CHOSEN[design].items():
        cls = {"family_time": "famtime-page", "annual_calendar": "annual-page",
               "emergency": "emergency-page"}[page]
        assert f'class="page {cls} rx-page lay-{layout}' in html, (page, layout)


def test_a_design_without_a_recipe_keeps_the_default_compositions():
    html = _html("blank", list(chrome.LAYOUT_VARIANTS))
    assert "rx-page" not in html.split("<body", 1)[1]
    for cls in ("famtime-page", "annual-page", "emergency-page"):
        assert f'class="page {cls}"' in html


@pytest.mark.parametrize("design", ["blank", "nordic", "editorial", "farmhouse"])
def test_every_other_design_keeps_the_family_emergency_plan(design):
    html = _html(design, ["emergency"])
    assert "Family Emergency Plan" in html and "Meeting place (near home):" in html


def test_midcenturys_emergency_page_has_no_family_plan():
    html = _html("midcentury", ["emergency"])
    body = html.split("<body", 1)[1]
    assert "Family Emergency Plan" not in body and "Meeting place" not in body
    assert 'data-section="family_plan"' not in body


# --- dates --------------------------------------------------------------------------

def _month_tables(html: str) -> list[list[list[str]]]:
    """Each annual-calendar month as rows of cell texts (head row first)."""
    tables = re.findall(r"<table>(.*?)</table>", html, re.S)
    out = []
    for t in tables:
        rows = re.findall(r"<tr>(.*?)</tr>", t, re.S)
        out.append([[re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
                    for r in rows])
    return out


@pytest.mark.parametrize("year", [2027, 2028])
@pytest.mark.parametrize("week_starts", ["sunday", "monday"])
@pytest.mark.parametrize("design", TRIO)
def test_calendar_dates_match_pythons_calendar(design, year, week_starts):
    html = _html(design, ["annual_calendar"], year=year, week_starts=week_starts)
    months = _month_tables(html)
    assert len(months) == 12
    first = calendar.SUNDAY if week_starts == "sunday" else calendar.MONDAY
    cal = calendar.Calendar(firstweekday=first)
    for m, rows in enumerate(months, start=1):
        head, weeks = rows[0], rows[1:]
        names = [calendar.day_abbr[(first + i) % 7][0] for i in range(7)]
        assert head == names, (year, m)
        expected = [[str(d) if d else "" for d in week] for week in cal.monthdayscalendar(year, m)]
        assert weeks == expected, (design, year, m)
    if year == 2028:
        feb = [c for row in months[1][1:] for c in row if c]
        assert feb[-1] == "29"


# --- the other axes --------------------------------------------------------------------

def _root(html: str) -> dict[str, str]:
    root = html.split(":root", 1)[1].split("}", 1)[0]
    root = re.sub(r"/\*.*?\*/", "", root, flags=re.S)
    return {k.strip(): v.strip() for k, v in
            (pair.split(":", 1) for pair in root.strip("{ \n").split(";") if ":" in pair)}


@pytest.mark.parametrize("design", TRIO)
def test_theme_palette_and_fonts_still_apply_to_the_composed_pages(design):
    html = _html(design, list(CHOSEN[design]), theme="goal", palette_set={"teal": "#123456"},
                 faces=typefaces.resolve("elegant"))
    root = _root(html)
    assert root["--navy"] == themes.PRESETS["goal"]["navy"]
    assert root["--c-structure"] == themes.PRESETS["goal"]["navy"]
    assert root["--teal"] == "#123456"
    elegant = typefaces.resolve("elegant")
    assert elegant.display in root["--font-display"] and elegant.body in root["--font-body"]
    # The scale reads the build's faces through the role variables, not the design's own fonts.
    assert root["--t-title-font"].startswith("var(--font-")
    for page, layout in CHOSEN[design].items():
        assert f"lay-{layout}" in html
    css = (render.STATIC_DIR / "recipes.css").read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"/\*.*?\*/", "", css, flags=re.S))


@pytest.mark.parametrize("design", TRIO)
def test_repeated_composed_builds_are_byte_identical(design):
    pages = ["cover", *CHOSEN[design], "chores", "year_goals", "meal_plan", "vacation"]
    first = _html(design, pages)
    assert _html(design, pages) == first


# --- in a browser: ink, contrast, print minimums, empty bands --------------------------

PAGES = ["cover", "family_time", "annual_calendar", "emergency", "chores", "year_goals", "meal_plan",
         "vacation", "grocery", "health_tracker", "school_activities", "home_maintenance", "budget",
         "values", "vision_mission", "how_to_use", "belongs_to", "year_end", "reading_log",
         "example_gratitude", "months"]

# Printed minimum (pt) by the role an element plays (2026-10-13 audit, part B):
# calendar weekday initials and helper lines 6pt, everything else 6.5pt.
SCRIPT = r"""
<script>
window.addEventListener('load', () => { document.fonts.ready.then(() => {
  const c = document.createElement('canvas').getContext('2d', {willReadFrequently: true});
  const rgba = x => { c.clearRect(0, 0, 1, 1); c.fillStyle = '#000'; c.fillStyle = x; c.fillRect(0, 0, 1, 1); return c.getImageData(0, 0, 1, 1).data; };
  const hex = x => { const d = rgba(x); return d[3] < 128 ? null : '#' + [d[0], d[1], d[2]].map(v => v.toString(16).padStart(2, '0')).join(''); };
  const lum = h => { const v = [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255).map(x => x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4);
                     return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
  const ink = hex(getComputedStyle(document.body).getPropertyValue('--ink').trim());
  const paper = hex(getComputedStyle(document.body).getPropertyValue('--paper').trim());
  const SIX = '.mini th, .lkm-dow, .week-head, em, .t-helper, .blurb, .rx-lead, .tradition-lead';
  const out = [];
  for (const sec of document.querySelectorAll('section.page')) {
    const z = sec.currentCSSZoom || 1, sr = sec.getBoundingClientRect();
    const small = [], inkText = [], low = [], ys = [];
    const w = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) {
      if (!n.textContent.trim()) continue;
      const el = n.parentElement, st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility !== 'visible' || el.closest('svg, .pt-probe')) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      const r = range.getBoundingClientRect(); if (!r.width) continue;
      ys.push([r.top, r.bottom]);
      const pt = parseFloat(st.fontSize) * 0.75 * z, floor = el.closest(SIX) ? 6 : 6.5;
      const t = n.textContent.trim().slice(0, 24);
      if (pt < floor - 0.01) small.push(pt.toFixed(2) + 'pt ' + t);
      const col = hex(st.color);
      if (col === ink) inkText.push(t);
      let bg = null;
      for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const b = hex(getComputedStyle(e).backgroundColor); if (b) { bg = b; break; } }
      bg = bg || paper;
      const L1 = lum(col), L2 = lum(bg), cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      if (cr < 4.5) low.push(cr.toFixed(2) + ' ' + t);
    }
    for (const el of sec.querySelectorAll('.dot-line, .solid-line, .mini')) {
      const r = el.getBoundingClientRect(); if (r.width && r.height >= 0) ys.push([r.top, r.bottom]);
    }
    ys.sort((a, b) => a[0] - b[0]);
    let gap = 0, reach = ys.length ? ys[0][1] : 0;
    for (const [t, b] of ys) { gap = Math.max(gap, t - reach); reach = Math.max(reach, b); }
    out.push({page: sec.dataset.page, small, ink: inkText, low, gap: gap / sr.height});
  }
  const pre = document.createElement('pre'); pre.id = 'rx'; pre.textContent = JSON.stringify(out); document.body.appendChild(pre);
}); });
</script>
"""

CASES = [(d, s) for d in TRIO for s in ("letter", "5.5x8", "6x9")]


@pytest.fixture(scope="module")
def measured(browser):
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(CASES, pool.map(lambda case: measure(browser, *case, PAGES, SCRIPT, "rx"), CASES)))


@pytest.mark.parametrize("design,size", CASES)
def test_every_text_meets_the_print_minimums(design, size, measured):
    problems = [f"{r['page']}: {s}" for r in measured[(design, size)] for s in r["small"]
                if r["page"] != "cover"]
    assert problems == []


@pytest.mark.parametrize("size", ["letter", "5.5x8", "6x9"])
def test_midcentury_prints_no_ink_text_and_every_text_reads(size, measured):
    results = measured[("midcentury", size)]
    assert len(results) >= len(PAGES) - 1 + 12
    assert [f"{r['page']}: {t}" for r in results for t in r["ink"]] == []
    assert [f"{r['page']}: {t}" for r in results for t in r["low"]] == []


@pytest.mark.parametrize("design,size", CASES)
def test_the_annual_calendar_leaves_no_empty_band(design, size, measured):
    annual = next(r for r in measured[(design, size)] if r["page"] == "annual_calendar")
    assert annual["gap"] < 0.10, f"{annual['gap']:.1%} of the page is one empty band"
