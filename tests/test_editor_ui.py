"""Static checks on the editor's own page (static/ui): keyboard focus in the
pickers, contrast, text size, click targets and leftover colours.

These read the files rather than drive a browser, so they guard against the
old patterns coming back. The behaviour itself was checked by hand in Chrome.
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


def function_body(name: str) -> str:
    start = JS.index(f"function {name}(")
    end = JS.index("\n}\n", start)
    return JS[start:end]


# --- keyboard focus in the pickers -------------------------------------------

@pytest.mark.parametrize("name", ["renderDesigns", "renderTypefaces", "renderThemes"])
def test_pickers_do_not_rebuild_on_every_change(name):
    """Rebuilding the radio group on each arrow key dropped keyboard focus."""
    body = function_body(name)
    clear = body.index('host.textContent = ""')
    assert "sameCards(host, key)" in body[:clear]
    assert "syncCards(host" in body[:clear]
    assert "finishCards(host, key, hadFocus)" in body[clear:]


@pytest.mark.parametrize("card", [".design-card", ".type-card", ".swatch"])
def test_picker_cards_show_keyboard_focus(card):
    match = re.search(rf"{re.escape(card)}:has\(input:focus-visible\)[^{{]*\{{([^}}]*)\}}", CSS)
    assert match, f"{card} has no focus-visible style"
    assert "outline: 3px solid var(--navy)" in match.group(1)
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
    assert "color: var(--placeholder)" in CSS
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
    assert ".spinner span" in block
    assert "animation: pulse" in block
    assert "@keyframes pulse" in CSS


def test_action_messages_stay_at_least_fifteen_seconds():
    match = re.search(r"action:\s*(\d+)", JS[JS.index("const TOAST_MS"):])
    assert match and int(match.group(1)) >= 15000
    assert "toast-close" in JS


# --- leftover colours, labels -------------------------------------------------

@pytest.mark.parametrize("old", [
    "#B8C4D4", "#A6B2C2", "#CBD5E1", "#D6DEE9", "#DDE4EE", "#46556A", "#12776F",
    "rgba(20,160,165", "rgba(22,50,95", "rgba(244, 246, 250",
])
def test_old_blue_grey_colours_are_gone(old):
    assert old.lower() not in CSS.lower()


def test_favicon_uses_the_editor_palette():
    assert "%2316325F" not in HTML and "%2314A0A5" not in HTML
    assert f"%23{token('navy')[1:]}" in HTML
    assert f"%23{token('teal')[1:]}" in HTML


def test_zoom_label_matches_the_script():
    assert '<span id="zoom-level">Fit page</span>' in HTML
    assert '"Fit page"' in JS


def test_header_does_not_start_with_a_made_up_page_count():
    assert "30 pages" not in HTML
