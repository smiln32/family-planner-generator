"""The command line reports user mistakes as one `error:` line, never a traceback."""

from __future__ import annotations

import pytest

from familyplanner import cli


def _run(capsys, *argv: str) -> tuple[int, str]:
    code = cli.main(list(argv))
    return code, capsys.readouterr().err


def test_out_dir_is_a_file(capsys, tmp_path):
    blocker = tmp_path / "afile"
    blocker.write_text("x", encoding="utf-8")
    code, err = _run(capsys, "build", "--html-only", "-o", str(blocker))
    assert code == 1
    assert err.strip().startswith("error:")
    assert "Traceback" not in err


def test_bad_month_accent(capsys, tmp_path):
    cfg = tmp_path / "f.yaml"
    cfg.write_text("months:\n  - accent: not_a_colour\n", encoding="utf-8")
    code, err = _run(capsys, "build", "--html-only", "-c", str(cfg), "-o", str(tmp_path))
    assert code == 1
    assert "months[0].accent" in err


def test_bad_palette(capsys, tmp_path):
    cfg = tmp_path / "f.yaml"
    cfg.write_text("palette:\n  navy: not-a-color\n", encoding="utf-8")
    code, err = _run(capsys, "build", "--html-only", "-c", str(cfg), "-o", str(tmp_path))
    assert code == 1
    assert "hex" in err


def test_escaping_output_name_stays_in_out_dir(capsys, tmp_path):
    out = tmp_path / "out"
    cfg = tmp_path / "f.yaml"
    cfg.write_text('output_name: "../escape"\n', encoding="utf-8")
    code, _ = _run(capsys, "build", "--html-only", "-c", str(cfg), "-o", str(out))
    assert code == 0
    assert not (tmp_path / "escape.html").exists()
    assert (out / "escape.html").exists()


def test_unknown_page(capsys, tmp_path):
    code, err = _run(capsys, "build", "--html-only", "--only", "cover,bogus_page",
                     "-o", str(tmp_path))
    assert code == 1
    assert "unknown page 'bogus_page'" in err


def _record_fetches(monkeypatch) -> list[str]:
    """Stand in for the downloader: note each set asked for, touch no network."""
    from familyplanner import fonts
    asked: list[str] = []
    monkeypatch.setattr(fonts, "fetch_fonts", lambda dest, faces, force=False: asked.append(faces.preset) or 0)
    return asked


def test_fonts_looks_fetches_each_look_set_once(monkeypatch, capsys):
    from familyplanner import designs
    asked = _record_fetches(monkeypatch)
    assert cli.main(["fonts", "--looks"]) == 0
    wanted = {designs.look_fonts(look) for look in designs.LOOKS}
    assert set(asked) == wanted
    assert len(asked) == len(wanted)


def test_fonts_all_fetches_every_set(monkeypatch, capsys):
    from familyplanner import typefaces
    asked = _record_fetches(monkeypatch)
    assert cli.main(["fonts", "--all"]) == 0
    assert asked == typefaces.names()


def test_fonts_all_and_looks_are_one_or_the_other(capsys):
    with pytest.raises(SystemExit):
        cli.main(["fonts", "--all", "--looks"])
