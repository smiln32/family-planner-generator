"""Untrusted input from family.yaml, CLI flags or the preview UI must not
escape the output folder or break out of the HTML/CSS it lands in."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from dataclasses import replace
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from familyplanner import config, render, server, typefaces
from familyplanner.config import ConfigError


@pytest.fixture
def cfg():
    return config.load(None)


# --- output file names ------------------------------------------------------

@pytest.mark.parametrize("name", [
    "../../evil",
    "..\\..\\evil",
    "/etc/passwd",
    "C:\\Windows\\evil",
    "..",
    "a/../../b",
])
def test_family_name_cannot_leave_out_dir(cfg, name, tmp_path):
    cfg.family_name = name
    target = config.output_path(tmp_path, cfg.stem, ".html")
    assert target.parent == tmp_path.resolve()
    assert "/" not in cfg.stem and "\\" not in cfg.stem
    assert not cfg.stem.startswith(".")


@pytest.mark.parametrize("name", ["../../evil", "..", "CON", "nul.txt", "", "   "])
def test_output_name_is_sanitized(cfg, name, tmp_path):
    cfg.output_name = name
    target = config.output_path(tmp_path, cfg.stem, ".pdf")
    assert target.parent == tmp_path.resolve()
    assert target.stem.upper() not in {"CON", "NUL"}


def test_normal_stem_unchanged(cfg):
    cfg.family_name = "Van der Berg"
    assert cfg.stem == "2027-Van-der-Berg-Family-Planner"
    cfg.family_name = "Muñoz"
    assert cfg.stem == "2027-Muñoz-Family-Planner"


def test_plan_filename_is_sanitized():
    name = config.plan_filename({"year": 2027, "family_name": "../x"})
    assert "/" not in name and not name.startswith(".")
    assert name.endswith(".md")


# --- palette and fonts ------------------------------------------------------

@pytest.mark.parametrize("value", [
    "red;}</style><script>alert(1)</script>",
    "#12345",
    "url(javascript:1)",
    "#FFF\"",
])
def test_palette_rejects_non_hex(value):
    with pytest.raises(ConfigError):
        config.sanitize_palette({"navy": value})


def test_palette_rejects_unknown_token():
    with pytest.raises(ConfigError):
        config.sanitize_palette({"background-image": "#FFFFFF"})


@pytest.mark.parametrize("family", [
    "Lato'; } body { display:none",
    "Lato</style><script>alert(1)</script>",
    'Lato", evil',
    "Lato\nX",
])
def test_custom_font_names_rejected(family):
    with pytest.raises(KeyError):
        typefaces.resolve({"display": family})
    with pytest.raises(ConfigError):
        config.check_fonts({"body": family})


def test_real_font_names_accepted():
    faces = typefaces.resolve({"display": "Playfair Display", "script": "M PLUS 1p",
                               "body": "Noto Sans JP"})
    assert faces.display == "Playfair Display"
    for name in typefaces.names():
        typefaces.resolve(name)


# --- months and the tab rail ------------------------------------------------

def test_month_name_injection_rejected():
    with pytest.raises(ConfigError):
        config._merge_months([{"name": 'Jan"><script>alert(1)</script>'}])


def test_month_accent_must_be_palette_token():
    with pytest.raises(ConfigError):
        config._merge_months([{"accent": "navy;background:url(x)"}])


def test_accented_month_names_allowed():
    months = config._merge_months([{"name": "Janvier"}, {"name": "Février"},
                                   {"name": "Março"}])
    assert months[1]["name"] == "Février"


def test_tab_rail_escapes_values(cfg):
    cfg.linked = True
    cfg.pages = ["months"]
    pages = render.plan_pages(cfg)
    # Bypass validation to prove the rail escapes on its own.
    cfg.palette = {**cfg.palette, "teal": '"><script>x</script>'}
    rail = render._tab_rail(cfg, pages, pages[0])
    assert "<script>" not in rail
    assert "&#34;&gt;&lt;script&gt;" in rail


def test_rendered_book_escapes_family_name(cfg):
    cfg.family_name = "<script>alert(1)</script>"
    cfg.pages = ["cover", "belongs_to"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    assert "<script>alert(1)</script>" not in html


# --- one set of rules for the YAML, the CLI and the UI ----------------------

@pytest.mark.parametrize("field,value", [
    ("year", 1200),
    ("year", "soon"),
    ("week_starts", "friday"),
    ("cover_year", "sideways"),
    ("theme", "no-such-theme"),
    ("design", "no-such-design"),
    ("page_size", "a0"),
    ("fonts", {"display": "x;}"}),
    ("palette", {"navy": "red"}),
    ("members", "not-a-list"),
])
def test_ui_uses_same_validators_as_yaml(cfg, tmp_path, field, value):
    yaml_file = tmp_path / "family.yaml"
    yaml_file.write_text(json.dumps({field: value}), encoding="utf-8")
    with pytest.raises(ConfigError):
        config.load(yaml_file)
    with pytest.raises((ConfigError, ValueError)):
        server._config_from({field: value}, cfg)


def test_validate_catches_cli_style_overrides(cfg):
    bad = replace(cfg, year=99999)
    with pytest.raises(ConfigError):
        config.validate(bad)


def test_valid_ui_payload_passes(cfg):
    out = server._config_from({
        "year": "2028", "family_name": "Ramirez", "week_starts": "Monday",
        "cover_year": "print", "theme": "linen", "fonts": "classic",
        "palette": {"navy": "123"}, "page_size": "6x9",
    }, cfg)
    assert out.year == 2028
    assert out.week_starts == "monday"
    assert out.palette["navy"] == "#112233"


# --- the HTTP API -----------------------------------------------------------

@pytest.fixture
def api(cfg, tmp_path):
    handler = type("H", (server.Handler,), {"base_config": cfg, "out_dir": tmp_path})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def _post(url: str, payload: dict) -> tuple[int, dict | bytes]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_save_endpoint_is_gone(api, tmp_path):
    target = tmp_path / "planted.yaml"
    status, _ = _post(f"{api}/api/save", {"path": str(target)})
    assert status == 404
    assert not target.exists()


def test_export_rejects_bad_year(api):
    status, _ = _post(f"{api}/api/export", {"year": 5})
    assert status == 400


def test_preview_rejects_bad_palette(api):
    status, _ = _post(f"{api}/api/preview", {"palette": {"navy": "</style>"}})
    assert status == 400


def test_open_refuses_files_outside_out_dir(api, tmp_path):
    outside = tmp_path.parent / "elsewhere.pdf"
    status, _ = _post(f"{api}/api/open", {"path": str(outside)})
    assert status == 400


def test_preview_and_export_still_work(api):
    status, body = _post(f"{api}/api/preview", {"family_name": "Ramirez", "preview": "cover"})
    assert status == 200 and body["slug"] == "cover"
    status, body = _post(f"{api}/api/export", {"family_name": "../Ramirez", "year": 2028})
    assert status == 200
    assert body["filename"] == "2028-Ramirez-planner.md"
    status, body = _post(f"{api}/api/import", {"text": body["markdown"]})
    assert status == 200 and body["config"]["year"] == 2028
