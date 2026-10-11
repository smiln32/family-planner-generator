"""The typeface files ship in the repo, each family with its licence.

The cover-fit test skips a look whose fonts are missing. This test is what
makes a missing file fail instead, so a skip can never hide one.
"""

from familyplanner import render, typefaces

FONT_DIR = render.STATIC_DIR / "fonts"
LICENSE_DIR = FONT_DIR / "licenses"


def _built_in_families() -> dict[str, set[str]]:
    """family -> the upright files the built-in sets need from it."""
    families: dict[str, set[str]] = {}
    for name in typefaces.names():
        for family, weight in typefaces.resolve(name).wanted():
            families.setdefault(family, set()).add(typefaces.slug(family, weight))
    return families


def _family_base(family: str) -> str:
    return typefaces.slug(family, 400)[: -len("-400.woff2")]


def test_every_built_in_set_has_its_font_files():
    missing, broken = [], []
    for files in _built_in_families().values():
        for name in sorted(files):
            path = FONT_DIR / name
            if not path.is_file():
                missing.append(name)
            elif path.read_bytes()[:4] != b"wOF2":
                broken.append(name)
    assert missing == []
    assert broken == []


def test_every_family_has_one_licence_file():
    readme = (FONT_DIR / "README.md").read_text(encoding="utf-8")
    for family in _built_in_families():
        base = _family_base(family)
        licences = [n for n in (f"{base}-OFL.txt", f"{base}-Apache-2.0.txt")
                    if (LICENSE_DIR / n).is_file()]
        assert len(licences) == 1, f"{family}: {licences}"
        text = (LICENSE_DIR / licences[0]).read_text(encoding="utf-8")
        assert "SIL Open Font License" in text or "Apache License" in text, family
        assert f"| {family} |" in readme, f"{family} missing from fonts/README.md"
