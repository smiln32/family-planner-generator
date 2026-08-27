"""Named colour presets.

A theme is a partial palette: it overrides some of the twelve tokens in
config.DEFAULT_PALETTE and leaves the rest alone. Anything you set under
`palette:` in your own config is applied on top, so a theme is a starting
point rather than a straitjacket.

    python planner.py themes                       # list them
    python planner.py build --theme pastel         # whole book
    python planner.py build --theme berry --only year_goals   # one page
"""

from __future__ import annotations

PRESETS: dict[str, dict[str, str]] = {
    # The look of the original printable. Deliberately empty: it is the
    # DEFAULT_PALETTE as-is.
    "classic": {},

    # Muted and chalky. Reads gently on cream or recycled paper.
    "pastel": {
        "navy": "#4A4E69", "teal": "#7FB2AC", "pink": "#E39AAE",
        "orange": "#E8B87F", "green": "#9DBF8E", "purple": "#A99CC4",
        "blue": "#8FA9CE", "red": "#D98B8B", "brown": "#B79B84",
        "ink": "#3D3D4E", "rule": "#CFD4DE",
    },

    # Higher saturation than classic. Good for kids' pages and fridge doors.
    "bold": {
        "navy": "#101A3C", "teal": "#00A6A6", "pink": "#FF2E63",
        "orange": "#FF9F1C", "green": "#57B203", "purple": "#7B2CBF",
        "blue": "#1B6CF2", "red": "#E01E1E", "brown": "#7A4A21",
    },

    # Cool blues and sea greens, with coral as the warm accent.
    "ocean": {
        "navy": "#0B2B4A", "teal": "#1B9AAA", "pink": "#EF6461",
        "orange": "#F4A259", "green": "#4C9F70", "purple": "#5C6BC0",
        "blue": "#2A6FB0", "red": "#D64550", "brown": "#7A6252",
    },

    # Warm jewel tones - deep pinks, plum and gold.
    "berry": {
        "navy": "#3D2645", "teal": "#7A9E9F", "pink": "#D81E5B",
        "orange": "#F0A202", "green": "#6A994E", "purple": "#8E44AD",
        "blue": "#5B5F97", "red": "#C1121F", "brown": "#7F5539",
    },

    # Earthy and calm - moss, clay and bark.
    "forest": {
        "navy": "#22333B", "teal": "#3E7C77", "pink": "#C97C5D",
        "orange": "#D4A373", "green": "#5A8F3D", "purple": "#7D6B91",
        "blue": "#4A7C92", "red": "#A63A2B", "brown": "#6B4F3A",
    },

    # One hue in seven steps. Cheapest to print and the quietest to look at.
    "slate": {
        "navy": "#16325F", "teal": "#34527A", "pink": "#4E6C99",
        "orange": "#6B85AC", "green": "#8399BE", "purple": "#9BADCF",
        "blue": "#2A4470", "red": "#16325F", "brown": "#5A6B85",
        "ink": "#1F2933", "rule": "#C3CCD8",
    },
}

DEFAULT_THEME = "classic"


def names() -> list[str]:
    """Preset names, classic first and the rest alphabetical."""
    rest = sorted(n for n in PRESETS if n != DEFAULT_THEME)
    return [DEFAULT_THEME, *rest]


def resolve(name: str) -> dict[str, str]:
    """Return a theme's overrides, or raise KeyError naming the valid options."""
    key = (name or DEFAULT_THEME).strip().lower()
    if key not in PRESETS:
        raise KeyError(f"unknown theme '{name}'. Available: {', '.join(names())}")
    return dict(PRESETS[key])
