"""The thirteen looks (designs.LOOKS): covers, monthly pages, colours, fonts."""

import pytest

from familyplanner import config, designs, render, typefaces


@pytest.fixture
def cfg():
    return config.load(None)


def test_default_is_a_look():
    assert designs.DEFAULT_DESIGN in designs.LOOKS
    assert config.load(None).design == designs.DEFAULT_DESIGN


def test_picker_offers_looks_then_layouts_then_blank():
    ids = designs.names()
    assert ids[: len(designs.LOOKS)] == list(designs.LOOKS)
    assert ids[-1] == "blank"
    assert "original" not in ids and "07" not in ids


@pytest.mark.parametrize("old", ["original", "02", "07", "17"])
def test_retired_looks_still_resolve(old):
    assert designs.resolve(old) == old


@pytest.mark.parametrize("look", list(designs.LOOKS))
def test_look_is_complete(look):
    spec = designs.LOOKS[look]
    assert set(spec["palette"]) == set(config.DEFAULT_PALETTE)
    assert spec["fonts"] in typefaces.PRESETS
    assert designs.look_fonts(look) == spec["fonts"]
    assert designs.look_palette(look) == spec["palette"]
    assert 1 <= len(spec["month"]["notes"]) <= 3


@pytest.mark.parametrize("look", list(designs.LOOKS))
def test_look_book_renders(cfg, look):
    cfg.design = look
    cfg.pages = ["cover", "january", "budget", "chores"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    assert f'<body class="design-{look} lk">' in html
    assert f'class="page lk-cover lkc-{look}"' in html
    assert f'class="page lk-month lkm-{look}"' in html
    assert '<svg class="cover-scene"' not in html   # the retired house cover is gone


def test_look_cover_prints_no_name_or_year(cfg):
    cfg.design = "editorial"
    cfg.family_name = "Ramirez"
    cfg.pages = ["cover"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    body = html.split("<body", 1)[1]
    assert "Ramirez" not in body.split("</section>")[0]
    assert str(cfg.year) not in body.split('class="page lk-cover', 1)[1].split("</section>")[0]


def test_look_palette_goes_over_theme_but_config_wins(cfg):
    cfg.design = "swiss"
    assert config.effective_palette(cfg)["red"] == "#E2321C"
    cfg.palette["red"] = "#123456"
    assert config.effective_palette(cfg)["red"] == "#123456"


def test_look_fonts_default_from_file(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: gazette\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "gazette"
    plan.write_text("design: gazette\nfonts: neat\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "neat"


def test_italic_slug():
    assert typefaces.slug("Bodoni Moda", 400, italic=True) == "bodoni-moda-400i.woff2"
    assert typefaces.slug("Bodoni Moda", 400) == "bodoni-moda-400.woff2"


COVER_PARTS = ["cover-body", "cover-scene", "cover-feet",
               *[f"famcover-{n:02d}" for n in range(2, 11)],
               *[f"daily-{n}" for n in range(11, 18)]]


SHARED_COVER = {"cover-body", "cover-scene", "cover-feet"}


def test_every_retired_cover_has_one_block_in_the_template():
    import re
    source = (render.TEMPLATE_DIR / "pages" / "cover.html").read_text(encoding="utf-8")
    blocks = re.findall(r'\{% if look\.base == "(\d\d)" %\}', source)
    assert sorted(blocks) == sorted(designs.RETIRED_COVERS)


@pytest.mark.parametrize("design, wanted", [
    ("original", SHARED_COVER),
    ("blank", SHARED_COVER),
    *[(n, {f"famcover-{n}" if int(n) <= 10 else f"daily-{n}"})
      for n in designs.RETIRED_COVERS],
])
def test_retired_and_blank_covers_render_only_their_own_variant(cfg, design, wanted):
    import re
    cfg.design = design
    cfg.pages = ["cover"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    body = html.split("<body", 1)[1]
    found = {part for part in COVER_PARTS
             if re.search(rf'class="[^"]*\b{part}\b', body)}
    assert found == wanted


# --- the typeface set once called "terracotta" ---------------------------------

def test_renamed_set_is_listed_under_its_new_name():
    assert "boho-brush" in typefaces.names()
    assert "terracotta" not in typefaces.names()
    assert "terracotta" not in typefaces.PRESETS


def test_old_set_name_still_resolves(tmp_path):
    faces = typefaces.resolve("terracotta")
    assert faces.preset == "boho-brush"
    assert faces.roles == {"display": "Tenor Sans", "script": "Caveat Brush", "body": "Mulish"}
    plan = tmp_path / "family.yaml"
    plan.write_text("fonts: terracotta\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "boho-brush"


def test_old_set_name_works_on_the_command_line(tmp_path):
    from familyplanner import cli
    args = cli.build_parser().parse_args(["build", "--fonts", "Terracotta"])
    assert cli._resolve_config(args).faces.preset == "boho-brush"


def test_old_plan_file_with_old_set_name_still_opens():
    from familyplanner import server
    handler = type("H", (server.Handler,), {"base_config": config.load(None), "out_dir": "."})
    out = handler.__new__(handler)
    plan = "---\ndesign: editorial\nfonts: terracotta\n---\n\n# Family Success Planner\n"
    config_out = out._plan_fields({**config.parse_plan_text(plan)})
    assert config_out["fonts"] == "boho-brush"
    assert server._config_from({"fonts": "terracotta"}, config.load(None)).faces.preset == "boho-brush"
