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
