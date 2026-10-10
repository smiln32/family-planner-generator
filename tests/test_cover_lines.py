"""Optional cover lines on the thirteen looks: family name, year, extra line.

All three are off by default, so a look cover renders exactly as designed.
Each one is turned on by itself (cover_show_family, cover_show_year,
cover_line). Blank, the retired looks and the layouts ignore them.

Phase 1: only the looks in designs.COVER_LINE_LOOKS have the cover spot.
The tests for the other ten are marked xfail (strict), so they start
failing the day a look gets its spot and the mark must come off.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from familyplanner import cli, config, designs, render, server
from familyplanner.config import ConfigError

NAME = "Sample"
LINE = "Our year together"
SCHOOL_YEAR = "2026–27"


def _look_params():
    """Every look, with the ones that have no cover spot yet marked xfail."""
    return [
        look if look in designs.COVER_LINE_LOOKS else pytest.param(
            look, marks=pytest.mark.xfail(strict=True, reason="no cover spot yet (phase 1)"))
        for look in designs.LOOKS
    ]


def _cfg(design="editorial", **fields):
    cfg = config.load(None)
    cfg.design = design
    cfg.pages = ["cover"]
    for key, value in fields.items():
        setattr(cfg, key, value)
    return config.validate(cfg)


def _cover(cfg) -> str:
    """The cover <section> of a rendered book, and nothing else."""
    body = render.render_html(cfg, render.plan_pages(cfg)).split("<body", 1)[1]
    start = body.index('<section class="page')
    return body[start:body.index("</section>", start)]


ALL_ON = {"family_name": NAME, "cover_show_family": True, "cover_show_year": "custom",
          "cover_text": SCHOOL_YEAR, "cover_line": LINE}


# --- off by default ---------------------------------------------------------

def test_defaults_are_off():
    cfg = config.load(None)
    assert (cfg.cover_show_year, cfg.cover_show_family, cfg.cover_line) == ("off", False, "")
    assert cfg.cover_extras == []


@pytest.mark.parametrize("look", list(designs.LOOKS))
def test_default_look_cover_has_no_name_year_or_line(look):
    # A family name and year text are set, as in an old family.yaml, but
    # nothing is turned on: the cover is the same as with neither set.
    cover = _cover(_cfg(look, family_name=NAME, cover_text=SCHOOL_YEAR))
    assert NAME not in cover and SCHOOL_YEAR not in cover
    assert "lk-own" not in cover
    assert cover == _cover(_cfg(look))


def test_an_old_family_yaml_gives_a_clean_look_cover(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: editorial\nfamily_name: {NAME}\ncover_year: print\n"
                    f"cover_text: Our Year\n", encoding="utf-8")
    cfg = config.load(plan)
    cfg.pages = ["cover"]
    assert cfg.cover_extras == []
    assert "lk-own" not in _cover(cfg) and NAME not in _cover(cfg)


# --- each opt-in on every look ----------------------------------------------

@pytest.mark.parametrize("look", _look_params())
def test_family_name_prints_on_the_look_cover(look):
    cover = _cover(_cfg(look, family_name=NAME, cover_show_family=True))
    assert f'<div class="lko-family">The {NAME} Family</div>' in cover
    assert f"lko-{look}" in cover


@pytest.mark.parametrize("look", _look_params())
def test_planner_year_prints_on_the_look_cover(look):
    cover = _cover(_cfg(look, year=2031, cover_show_year="year"))
    assert '<div class="lko-year">2031</div>' in cover


@pytest.mark.parametrize("look", _look_params())
def test_custom_year_text_prints_on_the_look_cover(look):
    cover = _cover(_cfg(look, cover_show_year="custom", cover_text=SCHOOL_YEAR))
    assert f'<div class="lko-year">{SCHOOL_YEAR}</div>' in cover


@pytest.mark.parametrize("look", _look_params())
def test_extra_line_prints_on_the_look_cover(look):
    cover = _cover(_cfg(look, cover_line=LINE))
    assert f'<div class="lko-line">{LINE}</div>' in cover


@pytest.mark.parametrize("look", designs.COVER_LINE_LOOKS)
def test_the_spot_has_its_own_styles(look):
    css = (render.STATIC_DIR / "looks.css").read_text(encoding="utf-8")
    for kind in ("family", "year", "line"):
        assert re.search(rf"\.lko-{look} \.lko-{kind}\b", css), kind


def test_all_three_print_in_order():
    cfg = _cfg(**ALL_ON)
    assert [kind for kind, _ in cfg.cover_extras] == ["family", "year", "line"]
    cover = _cover(cfg)
    assert cover.index("lko-family") < cover.index("lko-year") < cover.index("lko-line")


def test_family_switch_with_no_name_prints_nothing():
    cfg = _cfg(family_name="  ", cover_show_family=True)
    assert cfg.cover_extras == []
    assert "lk-own" not in _cover(cfg)


def test_custom_year_with_no_text_prints_nothing():
    assert _cfg(cover_show_year="custom", cover_text="").cover_extras == []


def test_year_off_ignores_the_year_text():
    assert _cfg(cover_show_year="off", cover_text=SCHOOL_YEAR).cover_extras == []


# --- escaping and limits ----------------------------------------------------

@pytest.mark.parametrize("field, extra", [
    ("cover_text", {"cover_show_year": "custom"}),
    ("cover_line", {}),
    ("family_name", {"cover_show_family": True}),
])
def test_cover_text_is_escaped(field, extra):
    cover = _cover(_cfg(**{field: "<b>x</b>&", **extra}))
    assert "<b>x" not in cover
    assert "&lt;b&gt;x&lt;/b&gt;&amp;" in cover


@pytest.mark.parametrize("field", ["cover_text", "cover_line"])
def test_cover_text_is_length_limited(field):
    limit = config.TEXT_LIMITS[field]
    assert limit == 80
    with pytest.raises(ConfigError, match=f"{limit} or fewer"):
        _cfg(**{field: "a" * (limit + 1)})


def test_cover_line_is_one_line_of_text():
    assert _cfg(cover_line="Our\nyear\x07").cover_line == "Our year"


# --- checking the switches ----------------------------------------------------

@pytest.mark.parametrize("raw, want", [
    (None, "off"), ("", "off"), ("off", "off"), (False, "off"), ("YEAR", "year"),
    (True, "year"), (" custom ", "custom"),
])
def test_year_mode_values(raw, want):
    assert config.check_cover_show_year(raw) == want


@pytest.mark.parametrize("raw", ["print", "blank", "sideways", 3])
def test_bad_year_mode_is_refused(raw):
    with pytest.raises(ConfigError, match="cover_show_year must be off, year, or custom"):
        config.check_cover_show_year(raw)


@pytest.mark.parametrize("raw, want", [
    (None, False), (False, False), (True, True), ("false", False), ("no", False),
    ("True", True), ("yes", True), (0, False), (1, True),
])
def test_flag_values(raw, want):
    assert config.check_flag(raw, "cover_show_family") is want


@pytest.mark.parametrize("raw", ["maybe", 2, [], {}])
def test_bad_flag_is_refused(raw):
    with pytest.raises(ConfigError, match="cover_show_family must be true or false"):
        config.check_flag(raw, "cover_show_family")


def test_yaml_reads_bare_off_and_on(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("cover_show_year: off\ncover_show_family: on\n", encoding="utf-8")
    cfg = config.load(plan)
    assert cfg.cover_show_year == "off" and cfg.cover_show_family is True


def test_yaml_with_every_opt_in(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text(f"family_name: {NAME}\ncover_show_family: true\n"
                    f"cover_show_year: custom\ncover_text: '{SCHOOL_YEAR}'\n"
                    f"cover_line: {LINE}\n", encoding="utf-8")
    cfg = config.load(plan)
    assert cfg.cover_extras == [("family", f"The {NAME} Family"),
                                ("year", SCHOOL_YEAR), ("line", LINE)]


def test_yaml_with_a_bad_mode_fails(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("cover_show_year: print\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="cover_show_year"):
        config.load(plan)


# --- covers that are not looks keep their behaviour ---------------------------

@pytest.mark.parametrize("design", ["blank", "original", "02", "10", "17", "06b", "12c"])
def test_other_covers_ignore_the_opt_ins(design):
    base = {"family_name": NAME, "cover_text": SCHOOL_YEAR}
    plain = _cover(_cfg(design, **base))
    turned_on = _cover(_cfg(design, **base, cover_show_family=True,
                            cover_show_year="year", cover_line=LINE))
    assert turned_on == plain
    assert LINE not in turned_on and "lk-own" not in turned_on


def test_blank_cover_still_prints_name_and_year_text():
    cover = _cover(_cfg("blank", family_name=NAME, cover_text=SCHOOL_YEAR))
    # The year mark sets each character in its own <span>.
    text = re.sub(r"<[^>]+>", "", cover)
    assert f"The {NAME} Family" in text and SCHOOL_YEAR in text


# --- the year drives the calendars and the file name ------------------------

def test_2026_and_2027_books_get_different_file_names(tmp_path):
    for year in ("2026", "2027"):
        code = cli.main(["build", "--html-only", "--only", "cover,january",
                         "-y", year, "-n", NAME, "--cover-show-year", "custom",
                         "--cover-text", SCHOOL_YEAR, "-o", str(tmp_path)])
        assert code == 0
    names = sorted(p.name for p in tmp_path.glob("*.html"))
    assert names == [f"2026-{NAME}-Family-Planner.html", f"2027-{NAME}-Family-Planner.html"]
    # The calendars still follow `year`, whatever the cover says.
    months = [(tmp_path / name).read_text(encoding="utf-8").split('class="page lk-month', 1)[1]
              for name in names]
    assert months[0] != months[1]


# --- the command line -------------------------------------------------------

def test_cli_flags_set_every_opt_in():
    args = cli.build_parser().parse_args([
        "build", "-n", NAME, "--cover-show-family", "--cover-show-year", "custom",
        "--cover-text", SCHOOL_YEAR, "--cover-line", LINE])
    cfg = cli._resolve_config(args)
    assert cfg.cover_extras == [("family", f"The {NAME} Family"),
                                ("year", SCHOOL_YEAR), ("line", LINE)]


def test_cli_can_turn_the_family_line_off_again(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text(f"family_name: {NAME}\ncover_show_family: true\n", encoding="utf-8")
    args = cli.build_parser().parse_args(["build", "-c", str(plan), "--no-cover-show-family"])
    assert cli._resolve_config(args).cover_show_family is False


def test_cli_refuses_a_bad_mode(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.build_parser().parse_args(["build", "--cover-show-year", "print"])
    assert exit_info.value.code == 2


def test_cli_too_long_line_is_one_error_line(capsys, tmp_path):
    code = cli.main(["build", "--html-only", "--cover-line", "x" * 81, "-o", str(tmp_path)])
    err = capsys.readouterr().err
    assert code == 1 and "Extra cover line is too long" in err and "Traceback" not in err


# --- the editor's API and plan files ----------------------------------------

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
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_preview_prints_the_opt_ins(api):
    status, body = _post(f"{api}/api/preview", {**ALL_ON, "design": "editorial",
                                                "preview": "cover"})
    assert status == 200
    assert f"The {NAME} Family" in body["html"] and LINE in body["html"]


def test_preview_text_false_does_not_turn_the_family_line_on(api):
    status, body = _post(f"{api}/api/preview", {"family_name": NAME, "cover_show_family": "false",
                                                "design": "editorial", "preview": "cover"})
    assert status == 200 and "lk-own" not in body["html"]


@pytest.mark.parametrize("route", ["preview", "export"])
def test_api_refuses_a_bad_mode(api, route):
    status, body = _post(f"{api}/api/{route}", {"cover_show_year": "sideways"})
    assert status == 400 and "cover_show_year" in body["error"]


def test_round_trip_keeps_the_opt_ins(api):
    status, plan = _post(f"{api}/api/export", {**ALL_ON, "design": "cottage"})
    assert status == 200
    saved = config.parse_plan_text(plan["markdown"])
    assert saved["cover_show_year"] == "custom" and saved["cover_show_family"] is True
    assert saved["cover_line"] == LINE and saved["cover_text"] == SCHOOL_YEAR
    status, back = _post(f"{api}/api/import", {"text": plan["markdown"]})
    assert status == 200
    for key, value in ALL_ON.items():
        assert back["config"][key] == value, key


def test_old_plan_file_without_opt_ins_opens_clean(api):
    old = (f"---\nyear: 2027\nfamily_name: {NAME}\ndesign: editorial\n"
           "cover_year: auto\ncover_text: ''\n---\n\n# Family Success Planner\n")
    status, back = _post(f"{api}/api/import", {"text": old})
    assert status == 200
    got = back["config"]
    assert (got["cover_show_year"], got["cover_show_family"], got["cover_line"]) == ("off", False, "")
    status, body = _post(f"{api}/api/preview", {**got, "preview": "cover"})
    assert status == 200 and "lk-own" not in body["html"] and NAME not in body["html"].split("<body", 1)[1]


def test_state_says_how_each_cover_treats_the_settings(api):
    with urllib.request.urlopen(f"{api}/api/state", timeout=20) as resp:
        state = json.loads(resp.read())
    kinds = {d["id"]: d["cover"] for d in state["designs"]}
    assert all(kinds[look] == "lines" for look in designs.COVER_LINE_LOOKS)
    assert all(kinds[look] == "soon" for look in designs.LOOKS
               if look not in designs.COVER_LINE_LOOKS)
    assert kinds["blank"] == "own" and kinds["06b"] == "own"
    assert state["config"]["cover_show_year"] == "off"
