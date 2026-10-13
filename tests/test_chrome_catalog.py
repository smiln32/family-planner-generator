"""The chrome catalog (familyplanner/chrome.py): every design's component
treatments, fully resolved, with the intended spec on <body> as classes."""

from __future__ import annotations

import pytest

from familyplanner import chrome, cli, config, designs, render, typefaces

TRIO = ("editorial", "farmhouse", "midcentury")


@pytest.fixture
def cfg():
    return config.load(None)


# --- the catalog's shape -----------------------------------------------------

def test_catalog_ids_are_the_picker_plus_original():
    assert list(chrome.CATALOG) == designs.names() + ["original"]
    assert chrome.names() == list(chrome.CATALOG)
    for entry_id, entry in chrome.CATALOG.items():
        assert entry.id == entry_id


@pytest.mark.parametrize("design", designs.names() + ["original"])
def test_every_resolved_design_has_an_entry(design):
    """config.check_design keeps resolving through designs; a design it
    accepts must have a catalog entry (so a missing one fails here, not in
    a template)."""
    assert config.check_design(design) == design
    assert chrome.for_design(design) is chrome.get(design)


@pytest.mark.parametrize("entry", list(chrome.CATALOG.values()), ids=list(chrome.CATALOG))
def test_entry_is_fully_resolved_and_in_vocabulary(entry):
    for spec in (entry.components, entry.current):
        values = spec.as_dict()
        assert set(values) == set(chrome.VOCAB)
        for field, value in values.items():
            assert value, (entry.id, field)
            assert value in chrome.VOCAB[field], (entry.id, field, value)
    assert entry.family in chrome.families()
    assert entry.status in chrome.STATUSES
    for prose in ("character", "header", "headings", "borders", "decoration",
                  "density", "alignment", "calendar", "print"):
        assert getattr(entry, prose).strip(), (entry.id, prose)
    assert entry.label == {**designs.LEGACY, **designs.PRESETS}[entry.id]["label"]


def test_vocabulary_is_closed():
    with pytest.raises(ValueError, match="corners=.*not one of"):
        chrome.Components(**{**chrome.SHARED.as_dict(), "corners": "wobbly"})
    with pytest.raises(ValueError, match="family"):
        chrome.Chrome(**{**chrome.get("blank").__dict__, "family": "nope"})


def test_families_are_the_closed_list():
    assert chrome.families() == chrome.FAMILIES
    used = {entry.family for entry in chrome.CATALOG.values()}
    assert used <= set(chrome.FAMILIES)
    assert chrome.get("blank").family == "minimal"
    assert chrome.get("original").family == "legacy"


# --- references, not copies --------------------------------------------------

@pytest.mark.parametrize("entry", list(chrome.CATALOG.values()), ids=list(chrome.CATALOG))
def test_palette_and_fonts_refs_resolve_to_the_design(entry):
    if entry.palette_ref == "linen":
        assert not designs.look_palette(entry.id)
        assert config.resolve_palette(entry.id, "", {}) == {
            k: v.upper() for k, v in config.DEFAULT_PALETTE.items()}
    else:
        via_ref = config.resolve_palette(entry.palette_ref, "", {})
        assert via_ref == config.resolve_palette(entry.id, "", {})
        own = {k: config.normalize_hex(v) for k, v in designs.look_palette(entry.id).items()}
        assert via_ref == own
    faces = typefaces.resolve(entry.fonts_ref)
    assert faces.preset == entry.fonts_ref
    own_set = designs.look_fonts(entry.id)
    assert entry.fonts_ref == (own_set or "elegant")


# --- looks, layouts, blank, original -----------------------------------------

@pytest.mark.parametrize("look", list(designs.LOOKS))
def test_looks_have_no_layout_letters(look):
    entry = chrome.get(look)
    assert entry.status == "look"
    assert entry.layouts == ()
    assert entry.base == look


@pytest.mark.parametrize("design", list(designs.LAYOUT_PRESETS))
def test_layouts_point_at_their_family(design):
    entry = chrome.get(design)
    parts = designs.parts(design)
    assert entry.status == "layout"
    assert entry.base == parts["base"]
    assert parts["layout"] in entry.layouts
    assert entry.layouts == ("a", "b", "c")


def test_blank_is_an_explicit_entry():
    blank = chrome.get("blank")
    assert blank.status == "blank"
    assert blank.components == blank.current
    assert blank.components == chrome.Components(
        corners="square", heads="pill", strip="boxed", table_head="filled",
        table_corners="rounded", checks="rounded", marks="circle", lines="dotted",
        calendar_head="pill", calendar_tile="rounded", labels="caps-heavy",
        footer="script", ornaments="sprigs", page="plain")
    assert "not the implicit default" in blank.character


def test_original_is_retired_and_locked():
    original = chrome.get("original")
    assert original.status == "retired"
    assert original.components == original.current == chrome.SHARED
    assert "do not restyle" in original.character.lower()
    # The other retired looks have no entry and render without a spec.
    assert chrome.for_design("07") is None


def test_unknown_chrome_lists_the_available_ids():
    with pytest.raises(KeyError) as err:
        chrome.get("nope")
    message = str(err.value)
    assert "unknown chrome 'nope'" in message
    for entry_id in chrome.names():
        assert entry_id in message


# --- intended against current -------------------------------------------------

def test_the_trio_gap_is_what_the_audit_flagged():
    assert chrome.get("editorial").gap() == {
        "strip": ("ruled", "boxed"), "table_head": ("rule", "filled"),
        "table_corners": ("square", "rounded"), "checks": ("square", "rounded"),
        "marks": ("text", "circle"), "calendar_head": ("rule", "pill"),
        "calendar_tile": ("open", "rounded"), "ornaments": ("none", "hearts"),
    }
    assert chrome.get("farmhouse").gap() == {
        "strip": ("framed", "boxed"),
        "table_corners": ("square", "rounded"), "checks": ("square", "rounded"),
        "calendar_head": ("bar", "pill"), "calendar_tile": ("square", "rounded"),
    }
    assert chrome.get("midcentury").gap() == {"labels": ("lower", "caps-heavy")}
    farmhouse = chrome.get("farmhouse").components
    assert (farmhouse.corners, farmhouse.strip, farmhouse.ornaments) == ("square", "framed", "stripe")
    midcentury = chrome.get("midcentury").components
    assert (midcentury.heads, midcentury.calendar_head, midcentury.ornaments) == ("pill", "pill", "corner")


def test_designs_the_audit_passed_print_as_intended():
    for design in ("coastal", "06b", "06c", "12a", "blank", "original"):
        assert chrome.get(design).gap() == {}, design


# --- the body carries the spec ------------------------------------------------

def _body_classes(cfg, design):
    cfg.design = design
    cfg.pages = ["cover", "chores"]
    html = render.render_html(cfg, render.plan_pages(cfg))
    return html.split('<body class="', 1)[1].split('"', 1)[0].split()


@pytest.mark.parametrize("design", ["editorial", "06b", "blank"])
def test_body_carries_one_class_per_field(cfg, design):
    """An approved design (the trio, and one that prints as intended)."""
    classes = _body_classes(cfg, design)
    entry = chrome.get(design)
    assert entry.approved
    expected = entry.components.classes()
    assert len(expected) == len(chrome.VOCAB)
    assert [c for c in classes if c.startswith("c-")] == expected
    for field, value in entry.components.as_dict().items():
        assert f"c-{field.replace('_', '-')}-{value}" in classes
    # The existing classes stay exactly as they were, first.
    assert classes[0] == f"design-{designs.parts(design)['base']}"


def test_body_classes_follow_the_intended_spec_once_approved(cfg):
    classes = _body_classes(cfg, "editorial")
    assert "c-strip-ruled" in classes and "c-strip-boxed" not in classes
    # An unapproved design carries today's spec, so nothing it prints moves
    # until the owner looks at it (tests/test_chrome_variants.py).
    classes = _body_classes(cfg, "nordic")
    nordic = chrome.get("nordic")
    assert not nordic.approved and nordic.active == nordic.current
    assert "c-strip-boxed" in classes and "c-strip-ruled" not in classes
    assert [c for c in classes if c.startswith("c-")] == nordic.current.classes()


def test_retired_look_without_an_entry_still_renders(cfg):
    classes = _body_classes(cfg, "07")
    assert classes == ["design-07"]


def test_only_the_variant_sheet_reads_the_spec_classes():
    """Step 4: static/chrome.css styles the `c-` classes; the shared chrome
    and the looks read none (tests/test_chrome_variants.py checks the
    variant sheet's classes against the vocabulary)."""
    for name in ("planner.css", "looks.css"):
        css = (render.STATIC_DIR / name).read_text(encoding="utf-8")
        assert ".c-" not in css, name
    assert ".c-strip-ruled" in (render.STATIC_DIR / "chrome.css").read_text(encoding="utf-8")


# --- the command ------------------------------------------------------------

@pytest.mark.parametrize("argv", [["chrome"], ["chrome", "--current"], ["chrome", "--diff"]])
def test_chrome_command_lists_every_id(capsys, argv):
    assert cli.main(argv) == 0
    out = capsys.readouterr().out
    for entry_id in chrome.names():
        assert f"  {entry_id:<11}" in out, entry_id


def test_chrome_diff_names_the_trio_gaps(capsys):
    assert cli.main(["chrome", "--diff"]) == 0
    out = capsys.readouterr().out
    assert "editorial   strip: ruled (now boxed)" in out
    assert "midcentury  labels: lower (now caps-heavy)" in out
    assert "farmhouse   strip: framed (now boxed)" in out
    assert "coastal     as it prints today" in out
    assert out.count("[approved: the intended spec prints]") == 3
