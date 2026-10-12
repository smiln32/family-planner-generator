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
    assert f'<body class="design-{base} design-{design} layout box-{design}">' in html
    assert html.count(f"box-{design} lx-") == 15  # cover, weekly, daily, twelve months
    assert 'class="page lx lx-' in html and "lx-cover" in html
    assert 'class="famcover' not in html      # the parent look's cover is gone


def test_layout_book_uses_its_look_colours_and_fonts(cfg):
    cfg.design = "06b"
    palette = config.effective_palette(cfg)
    assert palette["navy"] == "#1A2744" and palette["paper"] == "#FFFDF5"
    cfg.palette_set["pink"] = "#123456"      # the config's own replacement still wins
    config.validate(cfg)
    assert config.effective_palette(cfg)["pink"] == "#123456"
    plain = config.load(None)
    plain.design = "original"                # a retired look starts from linen
    assert config.effective_palette(plain)["navy"] == config.DEFAULT_PALETTE["navy"]
    assert designs.look_fonts("06b") == "composition-book"
    assert designs.look_fonts("06") == "" and designs.look_palette("original") == {}


def test_layout_fonts_default_from_file(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: 11a\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "boardroom"
    plan.write_text("design: 11a\nfonts: neat\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "neat"


def test_worksheets_render_in_a_layout_book(cfg):
    cfg.design = "02a"
    cfg.pages = ["budget", "chores"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    assert 'class="card has-tab' in html and "#111111" in html


def test_page_list_can_place_daily_itself(cfg):
    cfg.design = "11c"
    cfg.pages = ["cover", "daily", "months"]
    slugs = [p.slug for p in render.plan_pages(cfg)]
    assert slugs[:2] == ["cover", "daily"] and "weekly" not in slugs


def test_daily_and_weekly_render_without_a_layout(cfg):
    cfg.pages = ["daily", "weekly"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    assert "box-plain" in html
