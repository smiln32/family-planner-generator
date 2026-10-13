"""The catalog variants (Phase 2 step 4): the approved trio prints its intended
spec through `static/chrome.css` and a few template branches, and loses no
content doing it.

Editorial, Farmhouse and Mid-century are the designs the owner approved for
refinement (2026-10-12). Their worksheets must keep every write-on line,
table row and cell, check box and numbered mark, and every heading and label,
that Blank's have (Blank is the untouched reference); the calendars must
print the same dates; and every text the variants set on a fill must read at
4.5:1 with no theme and with each theme.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser

import pytest

from familyplanner import chrome, colours, config, designs, render, themes, typefaces

TRIO = ("editorial", "farmhouse", "midcentury")
WORKSHEETS = ["family_time", "emergency", "vacation", "chores", "annual_calendar",
              "year_goals", "grocery", "health_tracker", "school_activities",
              "home_maintenance"]
LABEL_CLASSES = {"card-tab", "card-head", "label", "famtime-label", "maint-label", "emg-head",
                 "mini-head", "banner", "pill", "caps", "hl-q", "appt-head", "page-title",
                 "th-fill", "rowlabel", "area-name", "slotcell", "dayname"}


def _page_html(design: str, slug: str, theme: str = "") -> str:
    cfg = config.load(None)
    cfg.design = designs.resolve(design)
    cfg.theme = theme
    if designs.look_fonts(cfg.design):
        cfg.faces = typefaces.resolve(designs.look_fonts(cfg.design))
    cfg.pages = [slug]
    cfg = config.validate(cfg)
    pages = render.plan_pages(cfg)
    html = render.render_html(cfg, pages, standalone=True)
    return html.split("<body", 1)[1]


class _Counter(HTMLParser):
    """Counts the write-on surfaces and collects the label texts of a page."""

    def __init__(self):
        super().__init__()
        self.counts = {"lines": 0, "rows": 0, "cells": 0, "checks": 0, "nums": 0}
        self.labels: set[str] = set()
        self._open: list[tuple[str, bool]] = []   # (tag, collects text)
        self._text: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        classes = set((dict(attrs).get("class") or "").split())
        if classes & {"dot-line", "solid-line"}:
            self.counts["lines"] += 1
        if tag == "tr":
            self.counts["rows"] += 1
        if tag in ("td", "th"):
            self.counts["cells"] += 1
        if "check" in classes:
            self.counts["checks"] += 1
        if "num" in classes:
            self.counts["nums"] += 1
        collects = bool(classes & LABEL_CLASSES) or tag == "th"
        self._open.append((tag, collects))
        if collects:
            self._text.append([])

    def handle_data(self, data):
        for buf in self._text:
            buf.append(data)

    def handle_endtag(self, tag):
        while self._open:
            open_tag, collects = self._open.pop()
            if collects:
                text = " ".join("".join(self._text.pop()).split()).lower()
                if text:
                    self.labels.add(text)
            if open_tag == tag:
                break


def _measure(design: str, slug: str) -> _Counter:
    counter = _Counter()
    counter.feed(_page_html(design, slug))
    return counter


def _texts(html: str, pattern: str) -> list[str]:
    """The text of every match of `pattern` (a regex with one group), tags stripped."""
    return [" ".join(re.sub(r"<[^>]+>", " ", m).split()) for m in re.findall(pattern, html, re.S)]


# --- writing space and content, against Blank ---------------------------------

@pytest.mark.parametrize("slug", WORKSHEETS)
@pytest.mark.parametrize("design", TRIO)
def test_writing_space_and_labels_equal_blanks(design, slug):
    ours, blank = _measure(design, slug), _measure("blank", slug)
    assert ours.counts == blank.counts, slug
    assert ours.labels == blank.labels, slug
    assert ours.counts["lines"] > 0 and ours.labels


@pytest.mark.parametrize("design", TRIO)
def test_calendars_print_blanks_dates(design):
    ours, blank = _page_html(design, "annual_calendar"), _page_html("blank", "annual_calendar")
    tables = r"<table>(.*?)</table>"
    assert _texts(ours, tables) == _texts(blank, tables)
    assert len(_texts(ours, tables)) == 12
    months = r'<div class="mini-head">(.*?)</div>'
    assert _texts(ours, months) == _texts(blank, months)
    # January: the same 31 dates in the same order, the same weekday heads.
    ours, blank = _page_html(design, "january"), _page_html("blank", "january")
    dates = [int(n) for n in re.findall(r"<b[^>]*>(\d{1,2})</b>", ours)]
    assert dates == list(range(1, 32))
    # Blank's grid also shows the neighbouring months' days around them.
    blanks = [int(n) for n in re.findall(r'<span class="n[^"]*"[^>]*>(\d{1,2})</span>', blank)]
    assert blanks[blanks.index(1):blanks.index(1) + 31] == dates
    cfg = config.load(None)
    for name in render.calendars.day_names(cfg.sunday_first):
        assert name[:3].lower() in re.sub(r"<[^>]+>", "", ours).lower()


@pytest.mark.parametrize("design", TRIO)
def test_page_list_is_blanks(design):
    cfg = config.load(None)
    cfg.design = design
    cfg.pages = ["cover", *WORKSHEETS, "months"]
    ours = [p.slug for p in render.plan_pages(config.validate(cfg))]
    cfg.design = "blank"
    assert ours == [p.slug for p in render.plan_pages(config.validate(cfg))]


# --- the spec that prints -------------------------------------------------------

def _body_classes(design: str) -> list[str]:
    html = _page_html(design, "chores")
    return html.split('class="', 1)[1].split('"', 1)[0].split()


@pytest.mark.parametrize("design", TRIO)
def test_the_trio_carries_its_intended_spec(design):
    entry = chrome.get(design)
    assert entry.approved and entry.active == entry.components
    classes = _body_classes(design)
    assert [c for c in classes if c.startswith("c-")] == entry.components.classes()


@pytest.mark.parametrize("design", [d for d in designs.names() if not chrome.get(d).approved])
def test_an_unapproved_design_carries_todays_spec(design):
    entry = chrome.get(design)
    assert entry.active == entry.current != entry.components
    classes = _body_classes(design)
    assert [c for c in classes if c.startswith("c-")] == entry.current.classes()


def test_the_approved_set():
    approved = {entry.id for entry in chrome.CATALOG.values() if entry.approved}
    assert approved == {"editorial", "farmhouse", "midcentury",
                        "blank", "original", "coastal", "06b", "06c", "12a"}
    for entry in chrome.CATALOG.values():
        if entry.id not in TRIO:
            assert entry.approved == (entry.components == entry.current), entry.id


def test_variant_sheet_reads_only_catalog_classes():
    """Every `c-` class chrome.css selects is a `c-<field>-<value>` of the
    vocabulary, and the other two sheets select none."""
    css = (render.STATIC_DIR / "chrome.css").read_text(encoding="utf-8")
    valid = {cls for entry in chrome.CATALOG.values()
             for cls in chrome.Components(**{f: v for f, v in entry.components.as_dict().items()}).classes()}
    valid |= {f"c-{f.replace('_', '-')}-{v}" for f, vs in chrome.VOCAB.items() for v in vs}
    used = set(re.findall(r"\.(c-[a-z-]+)", css))
    assert used and used <= valid, used - valid
    for name in ("planner.css", "looks.css"):
        assert not re.search(r"\.c-[a-z]", (render.STATIC_DIR / name).read_text(encoding="utf-8")), name


def test_a_retired_look_without_an_entry_prints_the_shared_defaults():
    html = _page_html("07", "annual_calendar")
    assert 'class="' in html and "c-" not in html.split('class="', 1)[1].split('"', 1)[0]
    assert html.count('<use href="#i-heart"/>') >= 10   # the dates card's hearts stay


@pytest.mark.parametrize("design, bullet", [("editorial", None), ("farmhouse", "mark-box"),
                                            ("midcentury", "mark-dot"), ("blank", "i-heart")])
def test_the_dates_bullet_follows_the_catalog(design, bullet):
    html = _page_html(design, "annual_calendar")
    card = html.split('class="card annual-dates"', 1)[1].split('class="page-footer"', 1)[0]
    rows = card.count('<div class="row">')
    assert rows == 10
    if bullet is None:
        assert 'class="bullet' not in card and "ico bullet" not in card
    else:
        assert card.count(bullet) == 10


# --- contrast on every theme --------------------------------------------------------

@pytest.mark.parametrize("theme", [""] + themes.names())
@pytest.mark.parametrize("design", TRIO)
def test_variant_text_reads_on_its_fill(design, theme):
    """Text the variants set: column heads and day tags as bare text in the
    structure or weekend colour on paper (Editorial), month names on a season
    bar (Farmhouse), labels on structure and weekend fills (all three), the
    chores day initials on the day-head wash."""
    cfg = config.load(None)
    cfg.design, cfg.theme = design, theme
    cfg = config.validate(cfg)
    roles, palette = render.colour_roles(cfg), cfg.palette
    paper = palette["paper"]
    for who in ("structure", "weekend"):
        assert colours.contrast(roles[who], paper) >= colours.TEXT_CONTRAST, who
        assert colours.contrast(roles[f"{who}-on"], roles[who]) >= colours.TEXT_CONTRAST, who
    for season in colours.SEASONS:
        assert colours.contrast(roles[f"{season}-on"], roles[season]) >= colours.TEXT_CONTRAST, season
    wash = colours.mix("#FFFFFF", roles["structure"], 0.04)
    for who in ("structure", "weekend"):
        assert colours.contrast(roles[who], wash) >= colours.TEXT_CONTRAST, who
