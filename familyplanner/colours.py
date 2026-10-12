"""Colour roles: which palette colour goes where on the worksheet pages.

Carla approved this rule on 2026-10-12, for every page in every design:

1. Structure. One colour per design (its title colour, the palette's `navy`)
   for every table header, card tab or heading, section label, column header,
   banner and badge circle.
2. Weekend. One accent per design (its `red`) for Saturday and Sunday labels,
   day pills and weekend dates, and for nothing else on a worksheet.
3. Seasons. Four colours drawn from the design's own palette, one for each
   season: winter (December, January, February), spring (March to May),
   summer (June to August), autumn (September to November). They colour the
   month boxes on the annual calendar, the month entries in the contents and
   the month accents of the pages that show one.
4. Neutral fills (row stripes, cell backgrounds, paper) are left alone.

`roles()` picks these from a palette. No new hues: a role takes a palette
colour as it is, or, when a palette has too few distinct colours (Swiss grid,
Boxed records, School notebook), a tint or shade of one of its own colours.
Every role also gets an `-on` colour for text set on it (white or the
palette's ink), with a contrast of at least 4.5:1; where neither reaches
that, the role colour is darkened toward the ink until white does.

The renderer passes these to the templates (as `p.structure`, `p.weekend`,
`p.winter`, ...) and to the CSS as custom properties (`--c-structure`,
`--c-structure-on`, `--c-weekend`, ...). See `_config/design-system.md`.
"""

from __future__ import annotations

SEASONS: tuple[str, ...] = ("winter", "spring", "summer", "autumn")

# Month number (1-12) to season.
MONTH_SEASON: dict[int, str] = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn",
}

ROLES: tuple[str, ...] = ("structure", "weekend") + SEASONS

# Palette tokens each season tries first, in order: blues for winter, greens
# for spring, warm golds and pinks for summer, browns and rusts for autumn.
SEASON_TOKENS: dict[str, tuple[str, ...]] = {
    "winter": ("blue", "teal", "purple", "green"),
    "spring": ("green", "teal", "blue", "pink"),
    "summer": ("orange", "pink", "teal", "green"),
    "autumn": ("brown", "purple", "orange", "pink", "red"),
}
WEEKEND_TOKENS: tuple[str, ...] = ("red", "pink", "teal", "orange", "purple")

# Hand-picked roles for the designs with their own colours: the thirteen
# looks and the four layout families (02, 06, 11, 12). A value is a palette
# token, so a config `palette:` block still reaches it, or a hex colour for a
# look colour that is not a token (Bauhaus butter, Almanac gold, the
# Terracotta sun) or a tint or shade of the design's own colours where its
# palette has too few (Swiss grid, Boxed records, School notebook, Executive
# desk, Midnight deco, Family gazette, Coastal stripe, Beautiful day). The
# weekend is the palette's red unless named. Each season is darkened toward
# the ink only if neither white nor ink text would reach 4.5:1 on it.
PICKS: dict[str, dict[str, str]] = {
    "editorial": {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "purple"},
    "midcentury": {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "brown"},
    "nordic": {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "brown"},
    "farmhouse": {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "brown"},
    "deco": {"winter": "#6B7589", "spring": "purple", "summer": "orange", "autumn": "brown"},
    "swiss": {"winter": "#474747", "spring": "#919191", "summer": "#BDBDBD", "autumn": "#6B6B6B"},
    "retro": {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "#8C7163"},
    "bauhaus": {"winter": "teal", "spring": "#7B8FC6", "summer": "#F2C94C", "autumn": "brown"},
    # Almanac's red is too close to its oxblood titles, so its weekend is the ochre.
    "almanac": {"weekend": "orange", "winter": "blue", "spring": "green",
                "summer": "#C9A464", "autumn": "pink"},
    "terracotta": {"winter": "blue", "spring": "green", "summer": "#E8A86E", "autumn": "brown"},
    "cottage": {"winter": "blue", "spring": "green", "summer": "#CBAE85", "autumn": "brown"},
    "gazette": {"winter": "blue", "spring": "#7E9DBC", "summer": "rule", "autumn": "brown"},
    "coastal": {"winter": "blue", "spring": "green", "summer": "#C9BFB2", "autumn": "brown"},
    # Boxed records is black and white only: a grey weekend and four greys.
    "02": {"weekend": "#707070", "winter": "#333333", "spring": "#A3A3A3",
           "summer": "#CCCCCC", "autumn": "#525252"},
    "06": {"winter": "rule", "spring": "blue", "summer": "#E6A5A5", "autumn": "#6E3140"},
    "11": {"winter": "#333333", "spring": "#7F8DA3", "summer": "#CDD3DD", "autumn": "#A6B0C0"},
    "12": {"weekend": "red", "winter": "purple", "spring": "green", "summer": "pink", "autumn": "#957F75"},
}

# Blank and the retired looks print in a theme (themes.PRESETS), keyed here
# as "theme:<name>". The weekend is worked out (the theme's red unless it is
# too close to the titles) unless named.
_TOKENS = {"winter": "blue", "spring": "green", "summer": "orange", "autumn": "brown"}
PICKS.update({f"theme:{name}": dict(_TOKENS) for name in (
    "linen", "classic", "amber", "berry", "bold", "citrus", "forest", "pastel", "poppy")})
PICKS.update({
    "theme:meadow": {"weekend": "brown", "winter": "blue", "spring": "green",
                     "summer": "pink", "autumn": "orange"},
    "theme:ocean": {"weekend": "orange", "winter": "purple", "spring": "green",
                    "summer": "pink", "autumn": "brown"},
    "theme:blues": {"weekend": "brown", "winter": "teal", "spring": "orange",
                    "summer": "rule", "autumn": "purple"},
})

# How far apart (CIE76 delta E) two roles must be to read as different.
MIN_WEEKEND_GAP = 30.0
MIN_SEASON_GAP = 18.0
MIN_SEASON_GAP_TIGHT = 11.0
MIN_WEEKEND_FALLBACK = 12.0
TEXT_CONTRAST = 4.5
WHITE = "#FFFFFF"


def _rgb(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02X}" for c in rgb)


def mix(a: str, b: str, t: float) -> str:
    """`a` moved a fraction `t` of the way to `b`, in sRGB (like CSS color-mix)."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))  # type: ignore[arg-type]


def _linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    r, g, b = (_linear(c) for c in _rgb(hex_colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _lab(hex_colour: str) -> tuple[float, float, float]:
    r, g, b = (_linear(c) for c in _rgb(hex_colour))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e(a: str, b: str) -> float:
    return sum((p - q) ** 2 for p, q in zip(_lab(a), _lab(b))) ** 0.5


def on_colour(background: str, ink: str) -> str:
    """White or ink for text on `background`, whichever reads better."""
    return WHITE if contrast(background, WHITE) >= contrast(background, ink) else ink


def readable(colour: str, ink: str) -> str:
    """`colour`, darkened toward the ink (then black) until text on it reads."""
    if max(contrast(colour, WHITE), contrast(colour, ink)) >= TEXT_CONTRAST:
        return colour
    for target in (ink, "#000000"):
        for step in range(1, 21):
            darker = mix(colour, target, step / 20)
            if contrast(darker, WHITE) >= TEXT_CONTRAST:
                return darker
    return "#000000"


def _text_safe(colour: str, paper: str) -> str:
    """`colour`, darkened (toward black, which keeps its hue) until it reads
    as text on paper."""
    for step in range(0, 21):
        darker = mix(colour, "#000000", step / 40) if step else colour
        if contrast(darker, paper) >= TEXT_CONTRAST:
            return darker
    return "#000000"


def _far(colour: str, taken: list[str], gap: float) -> bool:
    return all(delta_e(colour, other) >= gap for other in taken)


def _resolve(spec: str, palette: dict[str, str]) -> str:
    return palette[spec] if spec in palette else spec


def roles(palette: dict[str, str], family: str = "") -> dict[str, str]:
    """The six colour roles and their `-on` text colours for a palette.

    `family` is a look id (`editorial`), a layout's parent look (`06` for
    06a to 06c) or `theme:<name>` for Blank and the retired looks. Those have
    their seasons chosen by hand in `PICKS`; any other palette gets them
    worked out by `_pick()`.
    """
    ink, paper = palette["ink"], palette["paper"]
    structure = readable(palette["navy"], ink)
    weekend, seasons = _pick(palette, structure)
    pick = PICKS.get(family)
    if pick:
        if "weekend" in pick:
            weekend = _text_safe(_resolve(pick["weekend"], palette), paper)
        seasons = {s: readable(_resolve(pick[s], palette), ink) for s in SEASONS}
    out = {"structure": structure, "weekend": weekend, **seasons}
    for name in list(out):
        out[f"{name}-on"] = on_colour(out[name], ink)
    return out


def _usable(colour: str) -> bool:
    """Not so dark it reads as black, nor so light it vanishes on paper."""
    return 24 <= _lab(colour)[0] <= 90


def _pick(palette: dict[str, str], structure: str) -> tuple[str, dict[str, str]]:
    """Weekend and season colours for a palette without hand-picked ones."""
    ink, paper = palette["ink"], palette["paper"]

    # Weekend: the palette's red, or the first accent far enough from the
    # structure colour; failing that the accent farthest from it, and for a
    # palette with no accent at all (Boxed records) a lighter shade of its ink.
    options = [_text_safe(palette[token], paper) for token in WEEKEND_TOKENS]
    weekend = next((c for c in options if delta_e(c, structure) >= MIN_WEEKEND_GAP), "")
    if not weekend:
        best = max(options, key=lambda c: delta_e(c, structure))
        if delta_e(best, structure) >= MIN_WEEKEND_FALLBACK:
            weekend = best
    if not weekend:
        for step in range(20, 0, -1):
            candidate = mix(structure, paper, step / 20)
            if contrast(candidate, paper) >= TEXT_CONTRAST:
                weekend = candidate
                break
        weekend = weekend or structure

    # Seasons: palette colours first, then tints and shades of them. A season
    # keeps well clear of the weekend accent, so a month never reads as one.
    seasons: dict[str, str] = {}

    def free(colour: str, gap: float) -> bool:
        return (_usable(colour)
                and _far(colour, [structure, paper, *seasons.values()], gap)
                and delta_e(colour, weekend) >= MIN_WEEKEND_GAP)

    for season in SEASONS:
        pick = ""
        for token in SEASON_TOKENS[season]:
            candidate = readable(palette[token], ink)
            if free(candidate, MIN_SEASON_GAP):
                pick = candidate
                break
        sources = [palette[t] for t in SEASON_TOKENS[season]] + [structure]
        variants = [readable(mix(source, target, t / 10), ink)
                    for t in (3, 5, 2, 7, 4, 6, 8) for source in sources
                    for target in (WHITE, "#000000")]
        for gap in (MIN_SEASON_GAP, MIN_SEASON_GAP_TIGHT):
            if pick:
                break
            pick = next((c for c in variants if free(c, gap)), "")
        seasons[season] = pick or structure
    return weekend, seasons


def month_role(month_number: int) -> str:
    return MONTH_SEASON[month_number]
