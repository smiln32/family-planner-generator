"""Every typed text field has a length limit and loses control characters,
through the YAML loader, config.validate (CLI) and the editor's API."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from dataclasses import replace
from http.server import ThreadingHTTPServer

import pytest

from familyplanner import config, server
from familyplanner.config import ConfigError

FIELDS = list(config.TEXT_LIMITS.items())


@pytest.fixture
def cfg():
    return config.load(None)


def _yaml(tmp_path, data: dict):
    path = tmp_path / "family.yaml"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- the loader -------------------------------------------------------------

@pytest.mark.parametrize("field,limit", FIELDS)
def test_yaml_field_at_limit_passes(tmp_path, field, limit):
    loaded = config.load(_yaml(tmp_path, {field: "a" * limit}))
    assert getattr(loaded, field) == "a" * limit


@pytest.mark.parametrize("field,limit", FIELDS)
def test_yaml_field_over_limit_fails(tmp_path, field, limit):
    with pytest.raises(ConfigError) as err:
        config.load(_yaml(tmp_path, {field: "a" * (limit + 1)}))
    message = str(err.value)
    assert config.TEXT_LABELS[field] in message
    assert f"{limit} or fewer" in message


def test_yaml_member_name_limit(tmp_path):
    limit = config.MEMBER_NAME_LIMIT
    loaded = config.load(_yaml(tmp_path, {"members": ["Ana", "b" * limit]}))
    assert loaded.members[1] == "b" * limit
    with pytest.raises(ConfigError, match="Name 2 under People is too long"):
        config.load(_yaml(tmp_path, {"members": ["Ana", "b" * (limit + 1)]}))


@pytest.mark.parametrize("key", ["tagline", "footer", "motif"])
def test_yaml_month_text_limit(tmp_path, key):
    limit = config.MONTH_TEXT_LIMITS[key]
    ok = config.load(_yaml(tmp_path, {"months": [None, {key: "c" * limit}]}))
    assert ok.months[1][key] == "c" * limit
    with pytest.raises(ConfigError, match=f"The February {key} is too long"):
        config.load(_yaml(tmp_path, {"months": [None, {key: "c" * (limit + 1)}]}))


def test_month_name_too_long_names_the_month():
    with pytest.raises(ConfigError, match="The March name is too long"):
        config.merge_months([None, None, {"name": "M" * 31}])


def test_control_characters_are_removed(tmp_path):
    loaded = config.load(_yaml(tmp_path, {
        "family_name": "Ra\x00mi\x1brez",
        "title": "Our\nPlanner",
        "subtitle": "Plan\ttogether\x7f",
        "members": ["Ma\x07ya"],
        "months": [{"tagline": "New\r\nyear here"}],
    }))
    assert loaded.family_name == "Ramirez"
    assert loaded.title == "Our Planner"
    assert loaded.subtitle == "Plan together"
    assert loaded.members == ["Maya"]
    assert loaded.months[0]["tagline"] == "New  year here"


def test_letters_from_any_language_are_kept(tmp_path):
    loaded = config.load(_yaml(tmp_path, {"family_name": "Nguyễn-Müller 山田"}))
    assert loaded.family_name == "Nguyễn-Müller 山田"


def test_empty_title_is_not_the_word_none(tmp_path):
    path = tmp_path / "family.yaml"
    path.write_text("title:\n", encoding="utf-8")
    assert config.load(path).title == ""


# --- validate (the CLI path) ------------------------------------------------

@pytest.mark.parametrize("field,limit", FIELDS)
def test_validate_checks_length(cfg, field, limit):
    assert getattr(config.validate(replace(cfg, **{field: "a" * limit})), field) == "a" * limit
    with pytest.raises(ConfigError, match=config.TEXT_LABELS[field]):
        config.validate(replace(cfg, **{field: "a" * (limit + 1)}))


def test_validate_checks_members_and_strips_controls(cfg):
    out = config.validate(replace(cfg, members=["Jo\x00e"], family_name="A\x1bB"))
    assert out.members == ["Joe"] and out.family_name == "AB"
    with pytest.raises(ConfigError, match="Name 1 under People"):
        config.validate(replace(cfg, members=["x" * (config.MEMBER_NAME_LIMIT + 1)]))


# --- the editor's API -------------------------------------------------------

@pytest.fixture
def api(cfg, tmp_path):
    handler = type("H", (server.Handler,), {"base_config": cfg, "out_dir": tmp_path})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_port}"
    httpd.shutdown()
    httpd.server_close()


def _post(url: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


# output_name is not on the form or in plan files, so the API never takes it.
API_FIELDS = [(f, n) for f, n in FIELDS if f != "output_name"]


@pytest.mark.parametrize("route", ["preview", "export"])
@pytest.mark.parametrize("field,limit", API_FIELDS)
def test_api_field_limits(api, route, field, limit):
    status, _ = _post(f"{api}/api/{route}", {field: "a" * limit, "preview": "cover"})
    assert status == 200
    status, body = _post(f"{api}/api/{route}", {field: "a" * (limit + 1), "preview": "cover"})
    assert status == 400
    assert config.TEXT_LABELS[field] in body["error"]
    assert f"{limit} or fewer" in body["error"]


@pytest.mark.parametrize("route", ["preview", "export"])
def test_api_member_limit(api, route):
    limit = config.MEMBER_NAME_LIMIT
    status, _ = _post(f"{api}/api/{route}", {"members": ["m" * limit]})
    assert status == 200
    status, body = _post(f"{api}/api/{route}", {"members": ["Ana", "m" * (limit + 1)]})
    assert status == 400
    assert "Name 2 under People is too long" in body["error"]


def test_api_month_limit(api):
    long_tagline = [{"tagline": "t" * (config.MONTH_TEXT_LIMITS["tagline"] + 1)}]
    for route in ("preview", "export"):
        status, body = _post(f"{api}/api/{route}", {"months": long_tagline})
        assert status == 400
        assert "The January tagline is too long" in body["error"]


def test_plan_import_checks_length(api):
    text = "---\nfamily_name: " + "f" * 61 + "\n---\n"
    status, body = _post(f"{api}/api/import", {"text": text})
    assert status == 400
    assert "Family name is too long" in body["error"]


def test_plan_import_strips_controls(api):
    status, body = _post(f"{api}/api/export", {"family_name": "Ra\u0007mirez"})
    assert status == 200 and "\u0007" not in body["markdown"]
    status, body = _post(f"{api}/api/import", {"text": body["markdown"]})
    assert status == 200 and body["config"]["family_name"] == "Ramirez"


# --- the editor's inputs match -----------------------------------------------

def test_editor_inputs_carry_the_same_limits():
    ui = server.UI_DIR
    html = (ui / "index.html").read_text(encoding="utf-8")
    js = (ui / "ui.js").read_text(encoding="utf-8")
    assert f'id="family" type="text" placeholder="Ramirez" autocomplete="off" ' \
           f'maxlength="{config.TEXT_LIMITS["family_name"]}"' in html
    assert f'maxlength="{config.TEXT_LIMITS["cover_text"]}"' in html
    assert f"maxLength: {config.MEMBER_NAME_LIMIT}" in js
