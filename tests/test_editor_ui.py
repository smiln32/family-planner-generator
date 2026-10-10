"""Static checks on the editor's own page (static/ui): keyboard focus in the
pickers, contrast, text size, click targets and the favicon.

These read the files rather than drive a browser. The contrast, text size
and click-target tests check real values. The rest are loose guard rails
against old patterns coming back, not behaviour tests; the behaviour itself
was checked by hand in Chrome.
"""

from __future__ import annotations

import re

import pytest

from familyplanner import server

UI = server.UI_DIR
CSS = (UI / "ui.css").read_text(encoding="utf-8")
JS = (UI / "ui.js").read_text(encoding="utf-8")
HTML = (UI / "index.html").read_text(encoding="utf-8")


def _luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted([_luminance(a), _luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def token(name: str) -> str:
    match = re.search(rf"--{name}:\s*(#[0-9A-Fa-f]{{6}})", CSS)
    assert match, f"--{name} is not a hex token in ui.css"
    return match.group(1)


def rule(selector: str) -> str:
    """The declarations of the first rule whose selector list is exactly `selector`."""
    match = re.search(rf"(?:^|\}})\s*{re.escape(selector)}\s*\{{([^}}]*)\}}", CSS, re.M)
    assert match, f"no rule for {selector}"
    return match.group(1)


def function_text(name: str) -> str:
    """From `function name(` to the next top-level function, or the end."""
    match = re.search(rf"^(?:async\s+)?function\s+{name}\s*\(.*?(?=^(?:async\s+)?function\s|\Z)",
                      JS, re.M | re.S)
    assert match, f"no function {name} in ui.js"
    return match.group(0)


# --- keyboard focus in the pickers -------------------------------------------

@pytest.mark.parametrize("name", ["renderDesigns", "renderTypefaces", "renderThemes"])
def test_pickers_do_not_rebuild_on_every_change(name):
    """Rebuilding the radio group on each arrow key dropped keyboard focus."""
    # Guard rail, not a behaviour test: each picker still uses the helpers.
    body = function_text(name)
    for helper in ("sameCards", "syncCards", "finishCards"):
        assert re.search(rf"\b{helper}\s*\(", body), helper


@pytest.mark.parametrize("card", [".design-card", ".type-card", ".swatch"])
def test_picker_cards_show_keyboard_focus(card):
    match = re.search(rf"{re.escape(card)}:has\(input:focus-visible\)[^{{]*\{{([^}}]*)\}}", CSS)
    assert match, f"{card} has no focus-visible style"
    assert re.search(r"outline:\s*\d+px\s+solid\s+var\(--navy\)", match.group(1))
    assert contrast(token("navy"), token("paper")) >= 3
    assert contrast(token("navy"), "#FFFFFF") >= 3


# --- contrast -----------------------------------------------------------------

def test_control_outlines_reach_three_to_one():
    line = token("control-line")
    for background in ("#FFFFFF", token("paper"), token("wash")):
        assert contrast(line, background) >= 3, background
    assert "var(--control-line)" in rule('input[type="text"], input[type="number"], select')
    assert "var(--control-line)" in rule(".page-row .box")
    assert "var(--control-line)" in rule(".switch .track")


def test_switch_knob_stands_out_from_the_off_track():
    assert contrast("#FFFFFF", token("control-line")) >= 3


def test_placeholder_reaches_four_and_a_half_to_one():
    assert re.search(r"color:\s*var\(--placeholder\)", CSS)
    assert contrast(token("placeholder"), "#FFFFFF") >= 4.5


def test_muted_text_reaches_four_and_a_half_to_one():
    for background in ("#FFFFFF", token("paper"), token("wash")):
        assert contrast(token("muted"), background) >= 4.5


# --- text size, targets, motion -----------------------------------------------

def test_no_text_under_twelve_pixels():
    sizes = [float(px) for px in re.findall(r"font-size:\s*([\d.]+)px", CSS)]
    assert sizes and min(sizes) >= 12


@pytest.mark.parametrize("selector", [".icon-btn", ".member button"])
def test_small_buttons_are_at_least_32px(selector):
    body = rule(selector)
    assert "width: 32px" in body and "height: 32px" in body


def test_reduced_motion_keeps_a_gentle_spinner():
    block = CSS[CSS.index("@media (prefers-reduced-motion: reduce)"):]
    # Guard rail: the reduced-motion block still swaps in the pulse.
    assert ".spinner" in block
    assert re.search(r"animation:\s*pulse\b", block)
    assert "@keyframes pulse" in CSS


def test_action_messages_stay_at_least_fifteen_seconds():
    match = re.search(r"\baction:\s*(\d+)", JS)
    assert match and int(match.group(1)) >= 15000
    assert "toast-close" in JS


# --- favicon, labels -------------------------------------------------

def test_favicon_uses_the_editor_palette():
    assert f"%23{token('navy')[1:]}" in HTML
    assert f"%23{token('teal')[1:]}" in HTML


def test_zoom_label_matches_the_script():
    # Guard rail: the label the page starts with is one the script also sets.
    match = re.search(r'id="zoom-level"[^>]*>\s*([^<]+?)\s*<', HTML)
    assert match, "no starting text in #zoom-level"
    assert f'"{match.group(1)}"' in JS


# --- the year on the cover row ----------------------------------------------------

def _row_classes(field_id: str) -> str:
    """The class list of the .field-row that holds the field's label."""
    match = re.search(rf'<div class="([^"]*)"[^>]*>\s*<label for="{field_id}"', HTML)
    assert match, f"no field row for #{field_id}"
    return match.group(1)


def test_year_on_the_cover_select_gets_the_whole_panel_width():
    """At full desktop width the label column squeezed this select and cut off
    its longest choice ("Blank lines to writ"). Its label now sits above it."""
    assert "stack" in _row_classes("cover-year").split()
    body = rule(".field-row.stack")
    assert re.search(r"grid-template-columns:\s*1fr\s*;", body)


def test_hidden_field_rows_stay_hidden():
    """`.field-row { display: grid }` beat the [hidden] attribute, so the
    "Year on the cover" row showed even for dated books."""
    assert 'class="field-row stack" id="cover-year-row" hidden' in HTML
    assert re.search(r"\.field-row\[hidden\]\s*\{\s*display:\s*none", CSS)
