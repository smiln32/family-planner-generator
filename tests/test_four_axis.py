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
import re
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


# --- chrome roles: a theme reaches the layout chrome (Phase 2 step 1) ---------

# The colours the layouts were drawn with, as planner.css fixed them before
# the chrome read the roles (frame, mark, title, trim, line). With no theme
# the roles must still be exactly these.
CHROME_TODAY = {
    "02a": {"frame": "#111111", "mark": "#111111", "title": "#111111",
            "trim": "#111111", "line": "#111111"},
    "06a": {"frame": "#A7C4E0", "mark": "#C23B3B", "title": "#1A2744",
            "trim": "#A7C4E0", "line": "#A7C4E0"},
    "11a": {"frame": "#1B365D", "mark": "#1B365D", "title": "#1B365D",
            "trim": "#D5DBE4", "line": "#C8CED8"},
    "12a": {"frame": "#D4C0E0", "mark": "#8FAE8A", "title": "#C46A78",
            "trim": "#C9D4B8", "line": "#E8D4D0"},
}


def _roles(design, theme="", palette_set=None):
    cfg = config.load(None)
    cfg.design, cfg.theme, cfg.palette_set = design, theme, dict(palette_set or {})
    cfg = config.validate(cfg)
    return render.colour_roles(cfg), cfg.palette


@pytest.mark.parametrize("design", list(CHROME_TODAY))
def test_chrome_roles_without_a_theme_are_the_drawn_colours(design):
    roles, _ = _roles(design)
    assert {role: roles[role] for role in colours.CHROME_ROLES} == CHROME_TODAY[design]
    for role in colours.CHROME_ROLES:
        assert roles[f"{role}-on"] in (colours.WHITE, _base(design)["ink"])
    assert roles["mark-on"] == ("#5C4033" if design == "12a" else "#FFFFFF")


@pytest.mark.parametrize("design", list(CHROME_TODAY))
def test_theme_reaches_the_layout_chrome(design):
    """With a theme every chrome role is the theme's: frame, mark and title
    its structure colour, trim and line its rule on the merged palette."""
    roles, palette = _roles(design, "adventure")
    assert roles["structure"] == "#3D4A3C"
    assert roles["frame"] == roles["mark"] == roles["title"] == "#3D4A3C"
    assert roles["trim"] == roles["line"] == palette["rule"]
    assert roles["mark-on"] == roles["frame-on"] == "#FFFFFF"
    assert all(roles[role] != CHROME_TODAY[design][role] for role in ("frame", "mark", "title"))
    goal, _ = _roles(design, "goal")
    assert goal["frame"] == goal["mark"] == goal["title"] == "#1A1A2E"
    # A `palette:` block moves the token the theme's picks resolve against.
    picked, _ = _roles(design, "adventure", {"navy": "#123456", "rule": "#ABCDEF"})
    assert picked["frame"] == picked["mark"] == picked["title"] == "#123456"
    assert picked["trim"] == picked["line"] == "#ABCDEF"


def test_palette_block_reaches_a_token_named_chrome_pick():
    roles, _ = _roles("06a", "", {"rule": "#ABCDEF", "red": "#654321"})
    assert roles["frame"] == "#ABCDEF" and roles["line"] == "#ABCDEF"
    assert roles["mark"] == "#654321"
    roles, _ = _roles("12a", "", {"blue": "#123456", "green": "#234567", "red": "#345678"})
    assert roles["frame"] == "#123456" and roles["mark"] == "#234567"
    # A hex pick is the design's own and a palette block does not move it.
    assert roles["title"] == "#C46A78" and roles["trim"] == "#C9D4B8"


def test_chrome_roles_default_for_every_family():
    for family in ("", "editorial", "theme:linen", "theme:ocean", "blank"):
        palette = config.resolve_palette("editorial", "ocean", {})
        roles = colours.roles(palette, family)
        assert roles["frame"] == roles["mark"] == roles["title"] == roles["structure"]
        assert roles["trim"] == roles["line"] == palette["rule"]
    for name in themes.names():
        assert not set(colours.CHROME_ROLES) & set(colours.PICKS.get(f"theme:{name}", {}))


def test_build_with_a_theme_recolours_the_layout_chrome(tmp_path):
    assert cli.main(["build", "--design", "02a", "--theme", "adventure", "--only", "months,weekly",
                     "--html-only", "-o", str(tmp_path)]) == 0
    html = next(tmp_path.glob("*.html")).read_text(encoding="utf-8")
    root = {k.strip(): v.strip() for k, v in _root_vars(html).items()}
    assert root["--navy"] == "#3D4A3C"
    for role in ("frame", "mark", "title"):
        assert root[f"--c-{role}"] == "#3D4A3C"
    assert root["--c-mark-on"] == "#FFFFFF"
    assert root["--c-line"] == root["--rule"] == "#111111"
    # The CSS inside the book no longer fixes the layout's colours on its
    # body class, so `.cal-cell .n { color: var(--navy) }` prints the theme.
    assert ".design-02 {" not in html
    assert "--lx-frame: var(--c-frame)" in html
    assert re.search(r"\.cal-cell \.n\s*\{[^}]*color:\s*var\(--navy\)", html)


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


# Phase 2 step 2 (2026-10-12): the shared worksheet chrome reads roles. The
# day pill on a month grid is a light wash of the structure colour
# (planner.css `.cal-cell .n.pill`: 4% structure in white, the --c-wash
# recipe; 4% is the strongest wash on which the poppy and citrus navies, at
# 4.6:1 on bare paper, still read), the chores tracker's day initials sit on
# the same wash (`.chores-tbl .day-head th`, since Phase 2 step 4; a wash in
# the paper colour, even 2%, falls under 4.5:1 on the poppy theme), and two
# muted labels (`.emg-name em`, `.index-lede`) print in the structure colour. Text on the pill (a weekday in
# navy, a weekend day in the weekend accent) and the muted labels on paper
# must read at 4.5:1 for every design, with no theme and with each theme.
PILL_WASH = 0.04


@pytest.mark.parametrize("theme", [""] + themes.names())
@pytest.mark.parametrize("design", designs.names() + ["original"])
def test_text_reads_on_the_shared_chrome_washes(design, theme):
    roles, palette = _roles(design, theme)
    pill = colours.mix("#FFFFFF", roles["structure"], PILL_WASH)
    for who in ("weekend", "structure"):
        assert colours.contrast(roles[who], pill) >= colours.TEXT_CONTRAST, (who, pill)
    for token in ("navy", "ink"):
        assert colours.contrast(palette[token], pill) >= colours.TEXT_CONTRAST, (token, pill)
    assert colours.contrast(roles["structure"], palette["paper"]) >= colours.TEXT_CONTRAST
    # The strip border (the frame role) and the hairlines (the line role) are
    # visible on paper.
    assert colours.contrast(roles["frame"], palette["paper"]) >= 1.5
    assert colours.contrast(roles["line"], palette["paper"]) >= 1.1


# --- Phase 2 step 4: the trio's variants leave the four axes independent ------------

TRIO = ("editorial", "farmhouse", "midcentury")


@pytest.mark.parametrize("design", TRIO)
def test_the_other_axes_still_take_effect_on_a_refined_design(tmp_path, design):
    """A theme, a `palette:` block, a typeface set and a page list each take
    effect on a design that prints its intended chrome spec, and the chrome
    classes on the body do not move with them."""
    from familyplanner import chrome
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: {design}\npalette:\n  teal: '#123456'\n", encoding="utf-8")
    assert cli.main(["build", "-c", str(plan), "--theme", "goal", "--fonts", "elegant",
                     "--only", "cover,chores,annual_calendar", "--html-only",
                     "-o", str(tmp_path)]) == 0
    html = next(tmp_path.glob("*.html")).read_text(encoding="utf-8")
    root = {k.strip(): v.strip() for k, v in _root_vars(html).items()}
    assert root["--navy"] == themes.PRESETS["goal"]["navy"]
    assert re.search(r"--c-structure:\s*" + root["--navy"], html)
    assert root["--teal"] == "#123456"
    elegant = typefaces.resolve("elegant")
    assert elegant.display in root["--font-display"] and elegant.body in root["--font-body"]
    assert html.count('<section class="page') == 3
    assert 'class="page chores-page"' in html and 'class="page annual-page"' in html
    body = html.split('<body class="', 1)[1].split('"', 1)[0].split()
    assert [c for c in body if c.startswith("c-")] == chrome.get(design).components.classes()
    # No theme, own fonts, every page: the same chrome classes.
    plan.write_text(f"design: {design}\n", encoding="utf-8")
    cfg = config.load(plan)
    html = render.render_html(cfg, render.plan_pages(cfg))
    body = html.split('<body class="', 1)[1].split('"', 1)[0].split()
    assert [c for c in body if c.startswith("c-")] == chrome.get(design).components.classes()
    assert designs.LOOKS[design]["palette"]["navy"].upper() in html.split(":root", 1)[1][:2000]


@pytest.mark.parametrize("design", TRIO)
def test_repeated_builds_are_byte_identical(design):
    cfg = config.load(None)
    cfg.design = design
    cfg.pages = ["cover", "family_time", "annual_calendar", "january"]
    cfg = config.validate(cfg)
    first = render.render_html(cfg, render.plan_pages(cfg))
    again = config.load(None)
    again.design, again.pages = design, list(cfg.pages)
    again = config.validate(again)
    assert render.render_html(again, render.plan_pages(again)) == first
