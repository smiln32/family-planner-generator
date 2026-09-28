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
    # Default: sage, dusty rose and clay. Empty because it is DEFAULT_PALETTE.
    "linen": {},

    # The original bright printable: jewel navy, hot pink, citrus, lime.
    "classic": {
        "navy": "#16325F", "teal": "#14A0A5", "pink": "#EF3E63",
        "orange": "#F7A81B", "green": "#6DB033", "purple": "#7C4DA0",
        "blue": "#2F6FD1", "red": "#D93025", "brown": "#8A5A2B",
        "ink": "#1F2933", "paper": "#FFFFFF", "rule": "#B9C3CF",
    },

    # Violet headings, gold banners, rust instead of purple.
    "amber": {
        "navy": "#2A1548", "teal": "#A67C00", "pink": "#E0B429",
        "orange": "#E8A317", "green": "#B8952A", "purple": "#A0421E",
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

    # Lemon, lime and tangerine. No cool blues, no dark green; headings are
    # a deep mustard gold instead.
    "citrus": {
        "navy": "#8C6F00", "teal": "#A8C23F", "pink": "#E8637A",
        "orange": "#F2811D", "green": "#5D8C3C", "purple": "#C2410C",
        "blue": "#4C7A5D", "red": "#D64526", "brown": "#8B5A2B",
        "ink": "#2E2A1E", "paper": "#FFFBF0", "rule": "#E9E2C9",
    },

    # Moss and soil, top to bottom. Complements stay in the green/brown family.
    "forest": {
        "navy": "#1A3324", "teal": "#3B7A48", "pink": "#A85D3A",
        "orange": "#C97F3E", "green": "#4A8F3C", "purple": "#7A4A2E",
        "blue": "#2A5A3C", "red": "#8C3A24", "brown": "#6B4228",
        "ink": "#241D14", "paper": "#F7F6F0", "rule": "#D4CFC2",
    },

    # Shades of green top to bottom, pine to fresh grass. No pink or magenta,
    # so it reads distinctly from `classic`'s jewel-tone rainbow.
    "meadow": {
        "navy": "#12321F", "teal": "#3F8F52", "pink": "#8FC49A",
        "orange": "#6B8F3C", "green": "#4FA85D", "purple": "#1F4A34",
        "blue": "#2E7A6B", "red": "#355C2E", "brown": "#5C4A2E",
        "ink": "#1A2A1F", "paper": "#F7FBF6", "rule": "#C9D9CE",
    },

    # Blues, greens and seafoam only. No coral or red; warm accent is driftwood.
    "ocean": {
        "navy": "#062A3F", "teal": "#148A9A", "pink": "#6FBFB8",
        "orange": "#C9A672", "green": "#2E8F72", "purple": "#3A4E8C",
        "blue": "#0B5A78", "red": "#1C4E52", "brown": "#8A7A64",
        "ink": "#102A30", "paper": "#F4FBFC", "rule": "#CBE0DD",
    },

    # Dusty periwinkle against peach. Complements: blue-violet / orange, muted.
    "pastel": {
        "navy": "#4A4E86", "teal": "#8A9AD4", "pink": "#E8A888",
        "orange": "#E8C090", "green": "#A8B8E0", "purple": "#D4A090",
        "blue": "#7A8EC8", "red": "#D49088", "brown": "#C4A890",
        "ink": "#3A3A55", "paper": "#FBF8F6", "rule": "#E0DCE8",
    },

    # Bright pinks and reds throughout, no dark or muted tones, one leaf-green
    # accent. No cyan.
    "poppy": {
        "navy": "#E0132E", "teal": "#C4177C", "pink": "#E31C3D",
        "orange": "#F05A20", "green": "#7CB342", "purple": "#E0457B",
        "blue": "#D6336C", "red": "#D01020", "brown": "#8A3E2A",
        "ink": "#241014", "paper": "#FFF7F7", "rule": "#E4C9CC",
    },

    # One hue in seven steps. Cheapest to print and the quietest to look at.
    "blues": {
        "navy": "#16325F", "teal": "#34527A", "pink": "#4E6C99",
        "orange": "#6B85AC", "green": "#8399BE", "purple": "#9BADCF",
        "blue": "#2A4470", "red": "#16325F", "brown": "#5A6B85",
        "ink": "#1F2933", "rule": "#C3CCD8",
    },
}

DEFAULT_THEME = "linen"


def names() -> list[str]:
    """Preset names, the factory default first and the rest alphabetical."""
    rest = sorted(n for n in PRESETS if n != DEFAULT_THEME)
    return [DEFAULT_THEME, *rest]


def resolve(name: str) -> dict[str, str]:
    """Return a theme's overrides, or raise KeyError naming the valid options."""
    key = (name or DEFAULT_THEME).strip().lower()
    if key not in PRESETS:
        raise KeyError(f"unknown theme '{name}'. Available: {', '.join(names())}")
    return dict(PRESETS[key])
