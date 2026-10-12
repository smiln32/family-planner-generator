"""Four independent axes: pages, chrome (design), colours (theme, palette)
and type (fonts). Each resolves on its own through the existing config keys.

Colours are three layers, lowest first: the design's own palette (linen for
Blank and the retired looks), a named theme on any design, then the config's
`palette:` block (config.resolve_palette). Fonts are the design's own set
unless `fonts:` names one. Pages are checked at plan time.
"""

from __future__ import annotations

import copy
import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from familyplanner import cli, colours, config, designs, render, server, themes, typefaces
from familyplanner.config import ConfigError

NAMED_NAVY = [name for name in themes.names() if "navy" in themes.PRESETS[name]]
ALL_DESIGNS = designs.names() + ["original", "06"]


def _base(design):
    return config.resolve_palette(design, "", {})


# --- colours: the layer rule ----------------------------------------------

@pytest.mark.parametrize("design", ALL_DESIGNS)
def test_theme_overlays_every_design(design):
    for theme in NAMED_NAVY:
        resolved = config.resolve_palette(design, theme, {})
        assert resolved["navy"] == themes.PRESETS[theme]["navy"].upper(), (design, theme)
        # Tokens the theme does not name fall through to the design.
        for token in set(config.DEFAULT_PALETTE) - set(themes.PRESETS[theme]):
            assert resolved[token] == _base(design)[token], (design, theme, token)


def test_adventure_keeps_the_design_tokens_it_does_not_name():
    coastal = config.resolve_palette("coastal", "adventure", {})
    assert coastal["navy"] == "#3D4A3C" and coastal["paper"] == "#F5F1E8"
    assert coastal["pink"] == designs.LOOKS["coastal"]["palette"]["pink"]
    blank = config.resolve_palette("blank", "adventure", {})
    assert blank["pink"] == config.DEFAULT_PALETTE["pink"]


@pytest.mark.parametrize("design", ["editorial", "06b", "blank"])
def test_palette_block_wins_over_theme_and_design(design):
    resolved = config.resolve_palette(design, "ocean", {"navy": "#123456", "paper": "#fff"})
    assert resolved["navy"] == "#123456" and resolved["paper"] == "#FFFFFF"
    assert resolved["teal"] == themes.PRESETS["ocean"]["teal"]
    plain = config.resolve_palette(design, "", {"navy": "#123456"})
    assert plain["navy"] == "#123456"
    assert plain["teal"] == _base(design)["teal"]


@pytest.mark.parametrize("design", ALL_DESIGNS)
def test_no_theme_keeps_the_design_defaults(design):
    cfg = config.load(None)
    cfg.design = design
    cfg = config.validate(cfg)
    own = designs.look_palette(design) or config.DEFAULT_PALETTE
    assert cfg.theme == ""
    assert cfg.palette == {k: v.upper() for k, v in own.items()}
    assert config.effective_palette(cfg) == cfg.palette


def test_explicit_linen_theme_is_an_empty_overlay():
    """`theme: linen` is a named theme like any other. It names no tokens, so
    the colours stay the look's own; only the season picks follow the theme
    (render.colour_roles)."""
    assert themes.PRESETS["linen"] == {}
    assert config.resolve_palette("editorial", "linen", {}) == config.resolve_palette("editorial", "", {})
    assert config.resolve_palette("editorial", "", {}) != config.theme_palette("linen")
    cfg = config.load(None)
    cfg.theme = "linen"
    cfg = config.validate(cfg)
    assert render.colour_roles(cfg) == colours.roles(cfg.palette, "theme:linen")
    assert render.colour_roles(cfg) != colours.roles(cfg.palette, "editorial")


def test_blank_without_a_theme_is_linen():
    assert config.resolve_palette("blank", "", {}) == config.theme_palette("linen")
    assert config.resolve_palette("original", "", {}) == config.DEFAULT_PALETTE


def test_load_and_validate_agree_with_the_resolver(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: bauhaus\ntheme: goal\npalette:\n  teal: '#abc'\n", encoding="utf-8")
    cfg = config.load(plan)
    want = config.resolve_palette("bauhaus", "goal", {"teal": "#AABBCC"})
    assert cfg.palette == want
    assert config.validate(cfg).palette == want
    assert config.effective_palette(cfg) == want


# --- type: fonts are their own axis ----------------------------------------

@pytest.mark.parametrize("design", ["editorial", "coastal", "06b", "blank"])
def test_fonts_default_to_the_design_and_explicit_fonts_win(tmp_path, design):
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: {design}\ntheme: goal\n", encoding="utf-8")
    assert config.load(plan).faces == typefaces.resolve(
        designs.look_fonts(design) or typefaces.DEFAULT_SET)
    plan.write_text(f"design: {design}\ntheme: goal\nfonts: neat\n", encoding="utf-8")
    assert config.load(plan).faces.preset == "neat"
    plan.write_text(f"design: {design}\nfonts:\n  display: Open Sans\n  script: Courgette\n"
                    "  body: Oxygen\n", encoding="utf-8")
    faces = config.load(plan).faces
    assert (faces.display, faces.script, faces.body) == ("Open Sans", "Courgette", "Oxygen")


def test_theme_flag_does_not_touch_fonts(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: coastal\n", encoding="utf-8")
    args = cli.build_parser().parse_args(["build", "-c", str(plan), "--theme", "adventure"])
    cfg = cli._resolve_config(args)
    assert cfg.faces.preset == designs.look_fonts("coastal")
    args = cli.build_parser().parse_args(["build", "-c", str(plan), "--theme", "adventure",
                                          "--fonts", "neat"])
    assert cli._resolve_config(args).faces.preset == "neat"


# --- pages: untouched by the other axes ------------------------------------

@pytest.mark.parametrize("extra", ["", "theme: goal\n", "fonts: neat\n", "theme: goal\nfonts: neat\n"])
def test_page_selection_is_independent(tmp_path, extra):
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: coastal\n{extra}pages:\n  - cover\n  - months\n  - vacation\n",
                    encoding="utf-8")
    cfg = config.load(plan)
    assert cfg.pages == ["cover", "months", "vacation"]
    slugs = [p.slug for p in render.plan_pages(cfg)]
    assert slugs[0] == "cover" and slugs[-1] == "vacation" and len(slugs) == 14
    args = cli.build_parser().parse_args(["build", "-c", str(plan), "--only", "budget,values"])
    assert [p.slug for p in render.plan_pages(cli._resolve_config(args))] == ["budget", "values"]


# --- existing file formats still load --------------------------------------

@pytest.mark.parametrize("text, theme, navy", [
    ("theme: ocean\n", "ocean", themes.PRESETS["ocean"]["navy"]),
    ("palette:\n  navy: '#123456'\n", "", "#123456"),
    ("", "", designs.LOOKS["editorial"]["palette"]["navy"]),
    ("theme: ''\n", "", designs.LOOKS["editorial"]["palette"]["navy"]),
    ("fonts: neat\n", "", designs.LOOKS["editorial"]["palette"]["navy"]),
    ("fonts:\n  display: Open Sans\n  script: Courgette\n  body: Oxygen\n", "",
     designs.LOOKS["editorial"]["palette"]["navy"]),
])
def test_old_and_new_file_shapes_load(tmp_path, text, theme, navy):
    plan = tmp_path / "family.yaml"
    plan.write_text(text, encoding="utf-8")
    cfg = config.load(plan)
    assert cfg.theme == theme
    assert cfg.palette["navy"] == navy
    assert config.DEFAULT_CONFIG["theme"] == ""


# --- validation: existing errors, design before theme ----------------------

@pytest.mark.parametrize("text, words", [
    ("theme: no-such-theme\n", "unknown theme"),
    ("palette:\n  sky: '#123456'\n", "unknown palette colour"),
    ("palette:\n  navy: blue\n", "hex"),
    ("fonts: no-such-set\n", "no-such-set"),
])
def test_bad_values_are_still_refused(tmp_path, text, words):
    plan = tmp_path / "family.yaml"
    plan.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match=words):
        config.load(plan)


def test_bad_page_id_is_refused_at_plan_time(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("pages:\n  - cover\n  - no_such_page\n", encoding="utf-8")
    cfg = config.load(plan)          # pages are not checked here
    with pytest.raises(render.RenderError, match="no_such_page"):
        render.plan_pages(cfg)


def test_design_error_comes_before_theme_error(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: no-such-design\ntheme: no-such-theme\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown design"):
        config.load(plan)
    cfg = config.load(None)
    cfg.design, cfg.theme = "no-such-design", "no-such-theme"
    with pytest.raises(ConfigError, match="unknown design"):
        config.validate(cfg)
    cfg.design = "coastal"
    with pytest.raises(ConfigError, match="unknown theme"):
        config.validate(cfg)


def test_check_theme_accepts_empty_and_rejects_unknown():
    assert config.check_theme("") == "" and config.check_theme(None) == ""
    assert config.check_theme(" Goal ") == "goal"
    with pytest.raises(ConfigError):
        config.check_theme("no-such-theme")


# --- determinism, no leaks --------------------------------------------------

def test_resolution_is_pure():
    before = (copy.deepcopy(config.DEFAULT_PALETTE), copy.deepcopy(themes.PRESETS),
              copy.deepcopy(designs.LOOKS), copy.deepcopy(designs.LOOK_PALETTES))
    a = config.resolve_palette("coastal", "adventure", {"pink": "#010203"})
    b = config.resolve_palette("coastal", "adventure", {"pink": "#010203"})
    assert a == b and a is not b
    c = config.resolve_palette("bauhaus", "", {})
    assert c["pink"] == designs.LOOKS["bauhaus"]["palette"]["pink"]
    assert c["navy"] == designs.LOOKS["bauhaus"]["palette"]["navy"]
    a["navy"] = "#000000"
    assert config.resolve_palette("coastal", "adventure", {})["navy"] == "#3D4A3C"
    assert (config.DEFAULT_PALETTE, themes.PRESETS, designs.LOOKS, designs.LOOK_PALETTES) == before


def test_one_config_does_not_leak_into_the_next():
    first = config.load(None)
    first.design, first.theme, first.palette_set = "coastal", "adventure", {"pink": "#010203"}
    config.validate(first)
    second = config.load(None)
    second.design = "bauhaus"
    config.validate(second)
    assert second.theme == "" and second.palette_set == {}
    assert second.palette == {k: v.upper() for k, v in designs.LOOKS["bauhaus"]["palette"].items()}


# --- the new themes -----------------------------------------------------------

@pytest.mark.parametrize("name, navy", [("adventure", "#3D4A3C"), ("goal", "#1A1A2E")])
def test_new_themes_are_listed_and_picked(capsys, name, navy):
    assert name in themes.names()
    assert cli.main(["themes"]) == 0
    assert name in capsys.readouterr().out
    assert set(themes.PRESETS[name]) == {"navy", "teal", "red", "paper"}
    assert themes.PRESETS[name]["navy"] == navy
    assert set(colours.PICKS[f"theme:{name}"]) == set(colours.SEASONS)


@pytest.mark.parametrize("name", ["adventure", "goal"])
@pytest.mark.parametrize("design", ["coastal", "bauhaus", "blank", "11a"])
def test_new_theme_roles_read_on_every_design(name, design):
    cfg = config.load(None)
    cfg.design, cfg.theme = design, name
    cfg = config.validate(cfg)
    roles = render.colour_roles(cfg)
    seasons = [roles[s] for s in colours.SEASONS]
    assert len(set(seasons)) == 4
    assert roles["weekend"] != roles["structure"]
    for role in colours.ROLES:
        assert colours.contrast(roles[role], roles[f"{role}-on"]) >= colours.TEXT_CONTRAST, role


@pytest.mark.parametrize("name", ["adventure", "goal"])
def test_new_theme_seasons_are_the_given_hex(name):
    cfg = config.load(None)
    cfg.design, cfg.theme = "coastal", name
    roles = render.colour_roles(config.validate(cfg))
    for season, hex_colour in colours.PICKS[f"theme:{name}"].items():
        assert roles[season] == colours.readable(hex_colour, cfg.palette["ink"])


# --- roles: the theme's picks on any design ------------------------------------

@pytest.mark.parametrize("design", ["editorial", "bauhaus"])
def test_roles_follow_the_theme_when_one_is_named(design):
    cfg = config.load(None)
    cfg.design = design
    own = render.colour_roles(config.validate(cfg))
    expect_own = colours.roles(cfg.palette, design)
    assert own == expect_own
    cfg.theme = "goal"
    themed = render.colour_roles(config.validate(cfg))
    assert themed == colours.roles(cfg.palette, "theme:goal")
    assert [themed[s] for s in colours.SEASONS] != [own[s] for s in colours.SEASONS]


def test_blank_roles_use_linen_picks_without_a_theme():
    cfg = config.validate(config.load(None))
    cfg.design = "blank"
    cfg = config.validate(cfg)
    assert render.colour_roles(cfg) == colours.roles(cfg.palette, "theme:linen")


# --- the editor's server -------------------------------------------------------

@pytest.fixture
def api(tmp_path):
    handler = type("H", (server.Handler,), {"base_config": config.load(None), "out_dir": tmp_path})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def test_ui_config_without_theme_prints_the_design(tmp_path):
    base = config.load(None)
    out = server._config_from({"design": "coastal"}, base)
    assert out.theme == "" and out.palette == _base("coastal")
    themed = server._config_from({"design": "coastal", "theme": "adventure"}, base)
    assert themed.palette == config.resolve_palette("coastal", "adventure", {})
    picked = server._config_from({"design": "coastal", "theme": "adventure",
                                  "palette": {"navy": "#123456"}}, base)
    assert picked.palette["navy"] == "#123456" and picked.palette_set == {"navy": "#123456"}


def test_state_carries_the_file_palette_and_the_theme_tokens(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: coastal\ntheme: goal\npalette:\n  navy: '#123456'\n"
                    f"  pink: '{designs.LOOKS['coastal']['palette']['pink']}'\n",
                    encoding="utf-8")
    handler = type("H", (server.Handler,), {"base_config": config.load(plan), "out_dir": tmp_path})
    state = handler._state(handler.__new__(handler))
    assert state["config"]["theme"] == "goal"
    assert state["config"]["palette"] == {"navy": "#123456",
                                          "pink": designs.LOOKS["coastal"]["palette"]["pink"]}
    assert state["themeTokens"]["goal"] == themes.PRESETS["goal"]
    assert state["themeTokens"]["linen"] == {}
    assert [t["name"] for t in state["themes"]] == themes.names()


def test_plan_round_trip_without_a_theme_keeps_the_design_colours(api):
    plan = _post(f"{api}/api/export", {"design": "bauhaus", "palette": {"teal": "#123456"}})
    assert "theme" not in config.parse_plan_text(plan["markdown"])
    back = _post(f"{api}/api/import", {"text": plan["markdown"]})["config"]
    assert back["theme"] == "" and back["design"] == "bauhaus"
    assert back["palette"] == {"teal": "#123456"}
    cfg = server._config_from(back, config.load(None))
    assert cfg.palette == config.resolve_palette("bauhaus", "", {"teal": "#123456"})


def test_plan_round_trip_keeps_a_theme_on_a_look(api):
    plan = _post(f"{api}/api/export", {"design": "coastal", "theme": "adventure"})
    assert config.parse_plan_text(plan["markdown"])["theme"] == "adventure"
    back = _post(f"{api}/api/import", {"text": plan["markdown"]})["config"]
    assert back["theme"] == "adventure" and back["palette"] == {}


def test_state_offers_the_new_themes(api):
    meta = _get(f"{api}/api/state")
    assert {"adventure", "goal"} <= {t["name"] for t in meta["themes"]}
    assert meta["config"]["theme"] == ""


# --- the command line -------------------------------------------------------------

def _root_vars(html):
    root = html.split(":root", 1)[1].split("}", 1)[0]
    return dict(pair.strip().split(":", 1) for pair in root.strip("{ \n").split(";") if ":" in pair)


@pytest.mark.parametrize("design, theme, only, navy", [
    ("coastal", "adventure", "vacation,months,family_time", "#3D4A3C"),
    ("bauhaus", "goal", "vision_mission,year_goals,values,months", "#1A1A2E"),
])
def test_build_with_a_theme_on_a_look(tmp_path, design, theme, only, navy):
    assert cli.main(["build", "--design", design, "--theme", theme, "--only", only,
                     "--html-only", "-o", str(tmp_path)]) == 0
    html = next(tmp_path.glob("*.html")).read_text(encoding="utf-8")
    root = {k.strip(): v.strip() for k, v in _root_vars(html).items()}
    assert root["--navy"] == navy
    assert root["--paper"] == themes.PRESETS[theme]["paper"]
    picks = colours.PICKS[f"theme:{theme}"]
    ink = config.resolve_palette(design, theme, {})["ink"]
    for season in colours.SEASONS:
        assert root[f"--c-{season}"] == colours.readable(picks[season], ink)
    own = typefaces.resolve(designs.look_fonts(design))
    assert own.display in root["--font-display"] and own.body in root["--font-body"]


def test_build_without_a_theme_prints_the_look_and_no_note(capsys, tmp_path):
    assert cli.main(["build", "--design", "coastal", "--only", "vacation,months",
                     "--html-only", "-o", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "note:" not in out and "not used" not in out
    html = next(tmp_path.glob("*.html")).read_text(encoding="utf-8")
    root = {k.strip(): v.strip() for k, v in _root_vars(html).items()}
    coastal = designs.LOOKS["coastal"]["palette"]
    assert root["--navy"] == coastal["navy"] and root["--paper"] == coastal["paper"]
    assert typefaces.resolve("anchored").display in root["--font-display"]
