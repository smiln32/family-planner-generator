"""Calendar maths, page planning and build determinism."""

from __future__ import annotations

import datetime as dt
import re

import pytest

from familyplanner import calendars, config, render
from familyplanner.render import RenderError


# --- calendars, checked against datetime rather than the calendar module the
# code itself uses, so a shared mistake cannot hide ---------------------------

def _days_in(year: int, month: int) -> int:
    nxt = dt.date(year + month // 12, month % 12 + 1, 1)
    return (nxt - dt.timedelta(days=1)).day


@pytest.mark.parametrize("year", [2026, 2027, 2028, 2100])
@pytest.mark.parametrize("sunday_first", [True, False])
def test_month_grid_places_every_day_in_its_weekday_column(year, sunday_first):
    for month in range(1, 13):
        grid = calendars.compact_grid(year, month, sunday_first)
        seen = []
        for row, week in enumerate(grid):
            assert len(week) == 7
            for col, day in enumerate(week):
                if day.number is None:
                    continue
                weekday = dt.date(year, month, day.number).weekday()  # Mon=0
                expected_col = (weekday + 1) % 7 if sunday_first else weekday
                assert col == expected_col, (year, month, day.number)
                seen.append(day.number)
        assert seen == list(range(1, _days_in(year, month) + 1))


def test_leap_years():
    def feb(year):
        return max(d.number or 0 for w in calendars.compact_grid(year, 2, True) for d in w)
    assert feb(2028) == 29
    assert feb(2027) == 28
    assert feb(2100) == 28   # divisible by 100, not 400
    assert feb(2000) == 29   # divisible by 400


@pytest.mark.parametrize("sunday_first", [True, False])
def test_weekend_flags_mark_saturday_and_sunday(sunday_first):
    names = calendars.day_names(sunday_first)
    flags = calendars.weekend_flags(sunday_first)
    assert {n for n, f in zip(names, flags) if f} == {"Saturday", "Sunday"}


def test_month_grid_pads_to_six_rows_and_rejects_overflow():
    grid = calendars.month_grid(2027, 2, True)   # Feb 2027 fits in 4 rows
    assert len(grid) == 6
    assert all(d.number is None for d in grid[-1])
    with pytest.raises(ValueError):
        calendars.month_grid(2027, 5, True, rows=4)


# --- page planning ----------------------------------------------------------

@pytest.fixture
def cfg():
    return config.load(None)


def test_default_book_is_thirty_pages(cfg):
    pages = render.plan_pages(cfg)
    assert len(pages) == 30
    assert pages[0].slug == "cover"
    assert pages[-1].slug == "year_end"


def test_months_keyword_expands_to_twelve_in_order(cfg):
    cfg.pages = ["months"]
    slugs = [p.slug for p in render.plan_pages(cfg)]
    assert slugs == [m.lower() for m in calendars.MONTH_NAMES]


def test_single_month_slug_accepted(cfg):
    cfg.pages = ["cover", "march"]
    pages = render.plan_pages(cfg)
    assert [p.slug for p in pages] == ["cover", "march"]
    assert pages[1].context["month_number"] == 3


def test_unknown_page_raises(cfg):
    cfg.pages = ["cover", "nope_not_a_page"]
    with pytest.raises(RenderError, match="nope_not_a_page"):
        render.plan_pages(cfg)


def test_every_catalogue_page_renders(cfg):
    for slug in render.discover_pages():
        cfg.pages = [slug]
        html = render.render_html(cfg, render.plan_pages(cfg))
        assert f'id="{slug}"' in html


@pytest.mark.parametrize("week_starts, expected", [
    ("sunday", ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]),
    ("monday", ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]),
])
def test_meal_plan_days_follow_week_starts(cfg, week_starts, expected):
    cfg.week_starts = week_starts
    cfg.pages = ["meal_plan"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    days = re.findall(r'<span class="dayname">(\w+)</span>\s*'
                      r'<svg class="ico dayglyph"[^>]*>\s*<use href="#i-(\w+)"', html)
    assert [d for d, _ in days] == expected
    # Each day keeps its own glyph when the order shifts.
    assert {d: g for d, g in days} == {
        "MON": "sun", "TUE": "sun", "WED": "sun", "THU": "sun", "FRI": "sun",
        "SAT": "moon", "SUN": "moon",
    }


# --- determinism --------------------------------------------------------------

def test_same_config_renders_identical_html(cfg):
    first = render.render_html(cfg, render.plan_pages(cfg))
    second = render.render_html(config.load(None), render.plan_pages(config.load(None)))
    assert first == second
