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

    # Violet headings, gold banners. Complements: purple / yellow.
    "amber": {
        "navy": "#2A1548", "teal": "#A67C00", "pink": "#E0B429",
        "orange": "#E8A317", "green": "#B8952A", "purple": "#6B3D9E",
        "blue": "#4A2F78", "red": "#C45C1A", "brown": "#7A5410",
        "ink": "#221530", "paper": "#FFF9EF", "rule": "#E4D5B8",
    },

    # Plum pages, lime banners. Complements: magenta / yellow-green.
    "berry": {
        "navy": "#3A1030", "teal": "#5C8C1A", "pink": "#E21B64",
        "orange": "#E8C547", "green": "#6FA82A", "purple": "#9A1B70",
        "blue": "#6B2458", "red": "#C1124A", "brown": "#6B3A28",
        "ink": "#2A1220", "paper": "#FFF8FB", "rule": "#E2C9D6",
    },

    # Electric cyan against vermillion. Complements: blue-green / red-orange.
    "bold": {
        "navy": "#081428", "teal": "#00A0C0", "pink": "#FF3B1A",
        "orange": "#FF8A00", "green": "#00A090", "purple": "#E82A00",
        "blue": "#0078C8", "red": "#FF1E00", "brown": "#8A3C10",
        "ink": "#0D1520", "rule": "#B7C9D4",
    },

    # Cobalt and tangerine. Complements: blue / orange.
    "citrus": {
        "navy": "#0E2A52", "teal": "#1E6BB8", "pink": "#F26A21",
        "orange": "#F5A201", "green": "#2E7D9A", "purple": "#C45C12",
        "blue": "#245EA8", "red": "#E03E12", "brown": "#A35A1A",
        "ink": "#1A2433", "paper": "#F7FAFF", "rule": "#C5D0DE",
    },

    # Moss headings, clay accents. Complements: green / red-orange.
    "forest": {
        "navy": "#1A3324", "teal": "#3B7A48", "pink": "#D46A45",
        "orange": "#E0945A", "green": "#4A8F3C", "purple": "#B85A3A",
        "blue": "#2A5A3C", "red": "#B33A28", "brown": "#6B4228",
        "ink": "#1A241C", "paper": "#F7F6F0", "rule": "#D4CFC2",
    },

    # Deep green with rose. Complements: green / magenta.
    "meadow": {
        "navy": "#143528", "teal": "#2E8F5B", "pink": "#D9367A",
        "orange": "#E07A45", "green": "#3FA36A", "purple": "#A8326C",
        "blue": "#1F6B4A", "red": "#C41E4A", "brown": "#6B3E28",
        "ink": "#1A2B22", "paper": "#F7FBF6", "rule": "#C9D9CE",
    },

    # Sea and coral only. Complements: teal / red-orange.
    "ocean": {
        "navy": "#062A3F", "teal": "#148A9A", "pink": "#FF6A4D",
        "orange": "#FF8A3D", "green": "#1A7A78", "purple": "#D45A45",
        "blue": "#0B5A78", "red": "#E24A3C", "brown": "#A35A40",
        "ink": "#122830", "paper": "#F4FBFC", "rule": "#C2D6DC",
    },

    # Dusty periwinkle against peach. Complements: blue-violet / orange, muted.
    "pastel": {
        "navy": "#4A4E86", "teal": "#8A9AD4", "pink": "#E8A888",
        "orange": "#E8C090", "green": "#A8B8E0", "purple": "#D4A090",
        "blue": "#7A8EC8", "red": "#D49088", "brown": "#C4A890",
        "ink": "#3A3A55", "paper": "#FBF8F6", "rule": "#E0DCE8",
    },

    # Wine headings, cyan banners. Complements: red / cyan.
    "poppy": {
        "navy": "#3A1218", "teal": "#0098A8", "pink": "#E31C3D",
        "orange": "#F05A20", "green": "#1A9B9A", "purple": "#A81828",
        "blue": "#0D7A88", "red": "#D01020", "brown": "#8A3E2A",
        "ink": "#241014", "paper": "#FFF7F7", "rule": "#E4C9CC",
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
