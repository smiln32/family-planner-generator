"""Who decides a book's colours: the look when it has its own, else the theme.

The editor, plan files and `build` all follow the same rule, so no screen
offers a colour choice the printed page would ignore.
"""

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from familyplanner import cli, config, designs, server, themes


@pytest.fixture
def cfg():
    return config.load(None)


def _linen(token):
    return config.theme_palette("linen")[token]


# --- config ---------------------------------------------------------------

def test_look_book_ignores_theme(cfg):
    cfg.design = "editorial"
    cfg.theme, cfg.palette = "linen", config.theme_palette("linen")
    linen = config.effective_palette(cfg)
    cfg.theme, cfg.palette = "ocean", config.theme_palette("ocean")
    assert config.effective_palette(cfg) == linen
    assert linen["teal"] == designs.LOOKS["editorial"]["palette"]["teal"]


def test_blank_book_follows_theme(cfg):
    cfg.design = "blank"
    cfg.theme, cfg.palette = "ocean", config.theme_palette("ocean")
    assert config.effective_palette(cfg) == config.theme_palette("ocean")


@pytest.mark.parametrize("design", ["editorial", "nordic", "06b"])
def test_uses_theme_only_without_look_colours(design):
    assert not config.uses_theme(design)
    assert config.uses_theme("blank")
    assert config.uses_theme("original")


def test_replacement_matching_theme_still_wins(tmp_path):
    """A colour set on purpose prints even when it equals the theme's value."""
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: editorial\ntheme: linen\npalette:\n  teal: '{_linen('teal')}'\n",
                    encoding="utf-8")
    loaded = config.load(plan)
    assert config.effective_palette(loaded)["teal"] == _linen("teal")
    assert _linen("teal") != designs.LOOKS["editorial"]["palette"]["teal"]


def test_overrides_compare_against_the_look():
    look = designs.LOOKS["editorial"]["palette"]
    picked = {"teal": look["teal"], "navy": "#123456"}
    assert config.palette_overrides("linen", picked, "editorial") == {"navy": "#123456"}
    # Without a design the old theme-only comparison still applies.
    assert config.palette_overrides("linen", {"teal": _linen("teal")}) == {}


# --- the editor's API -----------------------------------------------------

@pytest.fixture
def api(cfg, tmp_path):
    handler = type("H", (server.Handler,), {"base_config": cfg, "out_dir": tmp_path})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def test_state_says_which_designs_bring_colours(api):
    meta = _get(f"{api}/api/state")
    by_id = {d["id"]: d for d in meta["designs"]}
    for look in designs.LOOKS:
        assert by_id[look]["palette"] == designs.LOOKS[look]["palette"]
    assert by_id["blank"]["palette"] is None
    assert meta["currentDesign"]["id"] == designs.DEFAULT_DESIGN
    assert meta["currentDesign"]["palette"] == designs.LOOKS[designs.DEFAULT_DESIGN]["palette"]


def test_state_for_a_retired_look_offers_the_theme(tmp_path):
    plan = tmp_path / "family.yaml"
    plan.write_text("design: original\ntheme: ocean\n", encoding="utf-8")
    handler = type("H", (server.Handler,), {"base_config": config.load(plan), "out_dir": tmp_path})
    state = handler._state(handler.__new__(handler))
    assert state["currentDesign"] == {"id": "original", "label": "Original", "palette": None}
    assert state["config"]["palette"] == {}


def test_state_reports_replacements_against_the_look(tmp_path):
    look = designs.LOOKS["editorial"]["palette"]
    plan = tmp_path / "family.yaml"
    plan.write_text(f"design: editorial\npalette:\n  teal: '{look['teal']}'\n  navy: '#123456'\n",
                    encoding="utf-8")
    handler = type("H", (server.Handler,), {"base_config": config.load(plan), "out_dir": tmp_path})
    assert handler._state(handler.__new__(handler))["config"]["palette"] == {"navy": "#123456"}


def test_preview_prints_replacement_matching_theme(cfg):
    out = server._config_from({"design": "editorial", "theme": "linen",
                               "palette": {"teal": _linen("teal")}}, cfg)
    assert config.effective_palette(out)["teal"] == _linen("teal")


def test_theme_does_not_change_a_look_preview(api):
    a = _post(f"{api}/api/preview", {"design": "editorial", "theme": "linen", "preview": "chores"})
    b = _post(f"{api}/api/preview", {"design": "editorial", "theme": "ocean", "preview": "chores"})
    assert a["html"] == b["html"]
    c = _post(f"{api}/api/preview", {"design": "blank", "theme": "linen", "preview": "chores"})
    d = _post(f"{api}/api/preview", {"design": "blank", "theme": "ocean", "preview": "chores"})
    assert c["html"] != d["html"]


def test_plan_round_trip_keeps_look_replacements(api):
    picked = {"teal": _linen("teal"), "navy": designs.LOOKS["editorial"]["palette"]["navy"]}
    plan = _post(f"{api}/api/export", {"design": "editorial", "theme": "linen", "palette": picked})
    back = _post(f"{api}/api/import", {"text": plan["markdown"]})["config"]
    # navy equals the look's own colour, so there is nothing to keep.
    assert back["palette"] == {"teal": _linen("teal")}
    assert back["design"] == "editorial"


# --- build ----------------------------------------------------------------

@pytest.mark.parametrize("text, noted", [
    ("design: editorial\ntheme: ocean\n", True),
    ("design: blank\ntheme: ocean\n", False),
    ("design: editorial\n", False),
])
def test_build_notes_an_unused_theme(capsys, tmp_path, text, noted):
    plan = tmp_path / "family.yaml"
    plan.write_text(text, encoding="utf-8")
    assert cli.main(["build", "--html-only", "-c", str(plan), "-o", str(tmp_path)]) == 0
    assert ("theme 'ocean' is not used" in capsys.readouterr().out) is noted


def test_build_notes_an_unused_theme_flag(capsys, tmp_path):
    assert cli.main(["build", "--html-only", "--theme", "berry", "-o", str(tmp_path)]) == 0
    assert "theme 'berry' is not used" in capsys.readouterr().out
    assert themes.DEFAULT_THEME == "linen"


def _flag_config(tmp_path, text, *flags):
    plan = tmp_path / "family.yaml"
    plan.write_text(text, encoding="utf-8")
    args = cli.build_parser().parse_args(["build", "-c", str(plan), *flags])
    return cli._resolve_config(args)


@pytest.mark.parametrize("old", ["linen", "ocean", "berry"])
def test_theme_flag_on_a_look_book_keeps_the_look_paper(tmp_path, old):
    """`--theme` must not leave the old theme's colours behind as replacements."""
    cfg = _flag_config(tmp_path, f"design: editorial\ntheme: {old}\n", "--theme", "blues")
    printed = config.effective_palette(cfg)
    assert printed["paper"] == designs.LOOKS["editorial"]["palette"]["paper"]
    assert printed == config.base_palette("blues", "editorial")


def test_theme_flag_on_a_blank_book_uses_the_new_theme(tmp_path):
    cfg = _flag_config(tmp_path, "design: blank\ntheme: ocean\n", "--theme", "bold")
    assert config.effective_palette(cfg) == config.theme_palette("bold")


def test_theme_flag_keeps_colours_the_file_sets(tmp_path):
    cfg = _flag_config(tmp_path, "design: editorial\ntheme: ocean\npalette:\n  navy: '#123456'\n",
                       "--theme", "blues")
    printed = config.effective_palette(cfg)
    assert printed["navy"] == "#123456"
    assert printed["paper"] == designs.LOOKS["editorial"]["palette"]["paper"]
