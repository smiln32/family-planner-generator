"""Planner layouts (designs 02a-12c): daily, weekly and layout monthly pages."""

import pytest

from familyplanner import config, designs, render


@pytest.fixture
def cfg():
    return config.load(None)


def test_layout_ids_are_designs():
    for look in ("02", "06", "11", "12"):
        for layout in "abc":
            assert designs.resolve(f"{look}{layout}") == f"{look}{layout}"
    assert designs.names()[-1] == "blank"


def test_parts():
    assert designs.parts("06b") == {"base": "06", "layout": "b", "box": "06b"}
    assert designs.parts("original")["layout"] == ""


def test_default_book_unchanged(cfg):
    assert "daily" not in [p.slug for p in render.plan_pages(cfg)]


@pytest.mark.parametrize("design", list(designs.LAYOUT_PRESETS))
def test_layout_book_renders(cfg, design):
    cfg.design = design
    pages = render.plan_pages(cfg)
    slugs = [p.slug for p in pages]
    assert slugs.index("weekly") < slugs.index("daily") < slugs.index("january")
    html = render.render_html(cfg, pages)
    base = design[:2]
    assert f'<body class="design-{base} design-{design}">' in html
    assert html.count(f"box-{design} lx-") == 14  # weekly, daily, twelve months


def test_page_list_can_place_daily_itself(cfg):
    cfg.design = "11c"
    cfg.pages = ["cover", "daily", "months"]
    slugs = [p.slug for p in render.plan_pages(cfg)]
    assert slugs[:2] == ["cover", "daily"] and "weekly" not in slugs


def test_daily_and_weekly_render_without_a_layout(cfg):
    cfg.pages = ["daily", "weekly"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    assert "box-plain" in html
