"""Download plan / Open plan: what goes into a plan file comes back out."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from dataclasses import asdict
from http.server import ThreadingHTTPServer

import pytest

from familyplanner import config, designs, server


@pytest.fixture
def cfg():
    return config.load(None)


@pytest.fixture
def api(cfg, tmp_path):
    handler = type("H", (server.Handler,), {"base_config": cfg, "out_dir": tmp_path})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _settings(cfg):
    """Every Config field a plan should carry, for comparing two configs."""
    out = asdict(cfg)
    for key in ("source", "output_name"):
        out.pop(key)
    return out


BOOKS = {
    "look": {"design": "farmhouse", "fonts": "home-grown",
             "palette": {"navy": "#123456"}},
    "layout": {"design": "06b", "fonts": "composition-book"},
    "blank": {"design": "blank", "theme": "ocean", "fonts": "classic",
              "palette": {"teal": "#ABCDEF"}},
}


@pytest.mark.parametrize("book", list(BOOKS))
def test_round_trip_keeps_the_whole_config(api, cfg, book):
    payload = {
        **BOOKS[book],
        "year": 2029, "family_name": "Ramirez", "week_starts": "monday",
        "dated_months": False, "cover_year": "blank", "cover_text": "Our Year",
        "cover_show_year": "custom", "cover_show_family": True, "cover_line": "Our year together",
        "page_size": "6x9", "members": ["Ana", "Ben", "Cy"],
        "type_size": {"title": 40},
        "pages": ["cover", "index", "months", "year_end"],
        "title": "Our Family Planner", "subtitle": "One day at a time",
        "linked": True,
        "months": [{"tagline": "Snow days"}, None, {"name": "Marzo", "accent": "red"}],
    }
    status, plan = _post(f"{api}/api/export", payload)
    assert status == 200, plan
    status, back = _post(f"{api}/api/import", {"text": plan["markdown"]})
    assert status == 200, back
    loaded = back["config"]

    want = server._config_from(payload, cfg)
    got = server._config_from(loaded, cfg)
    assert _settings(got) == _settings(want)
    assert got.title == "Our Family Planner" and got.linked is True
    assert got.months[0]["tagline"] == "Snow days"
    assert got.months[2]["name"] == "Marzo"

    # A second trip changes nothing.
    status, again = _post(f"{api}/api/export", loaded)
    assert (config.parse_plan_text(again["markdown"])
            == config.parse_plan_text(plan["markdown"]))


def test_output_name_is_left_out_and_the_file_says_so(api):
    status, plan = _post(f"{api}/api/export", {"output_name": "Old-Name"})
    assert status == 200
    assert "Old-Name" not in plan["markdown"]
    assert "# output_name" in plan["markdown"]
    status, back = _post(f"{api}/api/import",
                         {"text": "design: editorial\noutput_name: Old-Name\n"})
    assert status == 200 and "output_name" not in back["config"]


def test_export_rejects_an_unknown_font_set(api):
    status, body = _post(f"{api}/api/export", {"fonts": "no-such-set"})
    assert status == 400
    assert "no-such-set" in body["error"]


@pytest.mark.parametrize("look", ["farmhouse", "gazette", "06b"])
def test_import_without_fonts_uses_the_look_typefaces(api, look):
    status, back = _post(f"{api}/api/import", {"text": f"design: {look}\nyear: 2028\n"})
    assert status == 200
    assert back["config"]["fonts"] == designs.look_fonts(look)


def test_import_without_fonts_on_blank_uses_the_default_set(api):
    status, back = _post(f"{api}/api/import", {"text": "design: blank\n"})
    assert status == 200
    assert back["config"]["fonts"] == "elegant"


def test_import_rejects_a_bad_month(api):
    status, body = _post(f"{api}/api/import",
                         {"text": "months:\n  - name: '<b>'\n"})
    assert status == 400
