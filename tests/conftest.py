"""Shared test helpers.

Most tests never start a browser: they check the HTML, the config and the
local server. A test that really prints a PDF or PNG must ask for the
`browser` fixture, so it skips with a clear reason on a machine (or a CI
runner) that has no Chrome, Edge, Chromium or Brave.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from familyplanner import render


@pytest.fixture(scope="session")
def browser() -> Path:
    """Path to a Chromium-family browser, or skip the test if none is found."""
    try:
        return render.find_browser()
    except render.RenderError:
        pytest.skip("No Chromium-based browser found (set CHROME_PATH to run PDF/PNG tests)")
