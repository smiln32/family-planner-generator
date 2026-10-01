"""Page-look presets for the whole book.

Colour is `theme`. Typefaces are `fonts`. This module is a third axis: a class
on <body> restyles paper and chrome.

The book's looks are the thirteen in `LOOKS` (editorial, midcentury, ...). Each
one brings its own cover (`templates/look_cover.html`), monthly page
(`templates/look_monthly.html`), worksheet chrome (`static/looks.css`),
colours and typeface set. The planner layouts `02a`-`12c` sit beside them.

The retired looks (`original`, `02`-`17`) still resolve so old plan files
open, and their CSS stays because the layouts build on looks 02, 06, 11 and
12. They are no longer offered in the picker. See `shared/looks-handoff.md`.
"""

from __future__ import annotations

DEFAULT_DESIGN = "editorial"

# Title / cover / body / script sizes in points. The UI sliders write these.
DEFAULT_TYPE_SIZE: dict[str, float] = {
    "title": 30,
    "cover": 66,
    "body": 9,
    "script": 13,
}

TYPE_SIZE_RANGE: dict[str, tuple[float, float]] = {
    "title": (12, 72),
    "cover": (18, 96),
    "body": (6, 16),
    "script": (8, 36),
}

# The book's looks. Each brings its cover, monthly page, worksheet chrome,
# twelve palette tokens and a typeface set from typefaces.PRESETS. "month"
# holds the monthly page's wording: a kicker over the month name, a sub line
# under it, and the labels of the write-on blocks at the foot of the page.
# No look prints a family name or a year on its cover.
LOOKS: dict[str, dict] = {
    "editorial": {
        "label": "Editorial", "note": "Red nameplate, Bodoni, cover lines",
        "fonts": "home-edition",
        "palette": {"navy": "#1B1A17", "teal": "#C8452D", "pink": "#C8452D", "orange": "#9A6B3F",
                    "green": "#5E6B4E", "purple": "#7A3B2E", "blue": "#3D4A5C", "red": "#C8452D",
                    "brown": "#6B5A48", "ink": "#1B1A17", "paper": "#F2EDE4", "rule": "#CFC4B1"},
        "month": {"kicker": "The Home Edition", "sub": "Monthly",
                  "notes": ["On the agenda", "Worth remembering"]},
    },
    "midcentury": {
        "label": "Mid-century", "note": "Teal, mustard and rust shapes",
        "fonts": "family-plan",
        "palette": {"navy": "#1F5B5A", "teal": "#1F5B5A", "pink": "#C4562C", "orange": "#DDA23A",
                    "green": "#6E8B3D", "purple": "#8C4A2F", "blue": "#2F6F8A", "red": "#C4562C",
                    "brown": "#7A5230", "ink": "#2A2620", "paper": "#F1E6D0", "rule": "#D8C8A8"},
        "month": {"kicker": "the family plan", "sub": "", "notes": ["this month we'll"]},
    },
    "nordic": {
        "label": "Soft Scandinavian", "note": "Oat, clay and sage, lots of air",
        "fonts": "hem",
        "palette": {"navy": "#3A3A37", "teal": "#7F8A74", "pink": "#B88C70", "orange": "#C7A288",
                    "green": "#8E9A82", "purple": "#8A7A72", "blue": "#7C8A93", "red": "#A8705A",
                    "brown": "#7A6455", "ink": "#3A3A37", "paper": "#ECE6DC", "rule": "#C9C4B6"},
        "month": {"kicker": "", "sub": "", "notes": ["focus", "notes"]},
    },
    "farmhouse": {
        "label": "Farmhouse", "note": "Grain-sack stripe, barn red",
        "fonts": "home-grown",
        "palette": {"navy": "#2E2B28", "teal": "#8E2F25", "pink": "#8E2F25", "orange": "#A9773B",
                    "green": "#5E6B4A", "purple": "#6B3A2E", "blue": "#3E4C5A", "red": "#8E2F25",
                    "brown": "#6E5238", "ink": "#2E2B28", "paper": "#F3EADB", "rule": "#C9B38C"},
        "month": {"kicker": "", "sub": "at our house", "notes": ["Around the house"]},
    },
    "deco": {
        "label": "Midnight deco", "note": "Navy and champagne gold",
        "fonts": "household",
        "palette": {"navy": "#131B2D", "teal": "#A88A4E", "pink": "#8C6D3F", "orange": "#B8975A",
                    "green": "#2C3A57", "purple": "#3B2E4F", "blue": "#2C3A57", "red": "#8C3A3A",
                    "brown": "#6B5434", "ink": "#131B2D", "paper": "#F6F1E6", "rule": "#DCCFB3"},
        "month": {"kicker": "The Household", "sub": "", "notes": ["Of note"]},
    },
    "swiss": {
        "label": "Swiss grid", "note": "Black, white and one red",
        "fonts": "grotesk-red",
        "palette": {"navy": "#111111", "teal": "#E2321C", "pink": "#E2321C", "orange": "#111111",
                    "green": "#111111", "purple": "#E2321C", "blue": "#111111", "red": "#E2321C",
                    "brown": "#555555", "ink": "#111111", "paper": "#F5F4F0", "rule": "#BDBBB4"},
        "month": {"kicker": "", "sub": "", "notes": ["Priorities", "Events", "Don't miss"]},
    },
    "retro": {
        "label": "Retro sunset", "note": "Rainbow arcs, 70s brown and orange",
        "fonts": "good-days",
        "palette": {"navy": "#5A3420", "teal": "#D5632A", "pink": "#C9705F", "orange": "#D99A2B",
                    "green": "#7A7A32", "purple": "#A0472A", "blue": "#4E6E6A", "red": "#C2482A",
                    "brown": "#5A3420", "ink": "#3E2616", "paper": "#F8EDD6", "rule": "#D5B98F"},
        "month": {"kicker": "", "sub": "", "notes": ["Groovy plans"]},
    },
    "bauhaus": {
        "label": "Bauhaus blocks", "note": "Cobalt, coral, butter, black",
        "fonts": "plan-make-do",
        "palette": {"navy": "#16161A", "teal": "#2446A0", "pink": "#E0533E", "orange": "#16161A",
                    "green": "#2446A0", "purple": "#E0533E", "blue": "#16161A", "red": "#E0533E",
                    "brown": "#5A5048", "ink": "#16161A", "paper": "#EFEBE2", "rule": "#BDB6A8"},
        "month": {"kicker": "", "sub": "", "notes": ["Plan", "Make", "Do"]},
    },
    "almanac": {
        "label": "Clothbound almanac", "note": "Oxblood cloth, gold rules",
        "fonts": "almanac",
        "palette": {"navy": "#5E1A20", "teal": "#5E1A20", "pink": "#8A5A3A", "orange": "#94702F",
                    "green": "#4A5A3A", "purple": "#5E1A20", "blue": "#3A4658", "red": "#7D2A2A",
                    "brown": "#7D5A3A", "ink": "#2A1E1A", "paper": "#F4EEE2", "rule": "#B79A86"},
        "month": {"kicker": "The Family Almanac", "sub": "", "notes": ["Observances", "Memoranda"]},
    },
    "terracotta": {
        "label": "Terracotta arches", "note": "Sand, clay, plum and sage",
        "fonts": "home-base",
        "palette": {"navy": "#5B2E3A", "teal": "#B65A3A", "pink": "#C77A5E", "orange": "#C27D42",
                    "green": "#7E8A6A", "purple": "#5B2E3A", "blue": "#6F7F8A", "red": "#A44A30",
                    "brown": "#7A4E36", "ink": "#3E2228", "paper": "#F3E9DA", "rule": "#D7C3A5"},
        "month": {"kicker": "Home Base", "sub": "", "notes": ["On the calendar", "Little joys"]},
    },
    "cottage": {
        "label": "Cottage gingham", "note": "Sage check, blush, Lora italic",
        "fonts": "life-at-home",
        "palette": {"navy": "#3F5A47", "teal": "#6F8F6C", "pink": "#C98F86", "orange": "#B98F5A",
                    "green": "#6F8F6C", "purple": "#9A7A8C", "blue": "#7090A0", "red": "#B5675E",
                    "brown": "#7A6450", "ink": "#33443A", "paper": "#FBF8F1", "rule": "#C9D6C5"},
        "month": {"kicker": "", "sub": "", "notes": ["From the kitchen", "In the garden"]},
    },
    "gazette": {
        "label": "Family gazette", "note": "Newsprint, blackletter nameplate",
        "fonts": "gazette",
        "palette": {"navy": "#181715", "teal": "#181715", "pink": "#2F5D8A", "orange": "#181715",
                    "green": "#2F5D8A", "purple": "#181715", "blue": "#2F5D8A", "red": "#8A2E2E",
                    "brown": "#4A4740", "ink": "#181715", "paper": "#ECE7DC", "rule": "#A9A396"},
        "month": {"kicker": "The Family Gazette", "sub": "Monthly Edition",
                  "notes": ["Headlines", "Coming Up", "Notices"]},
    },
    "coastal": {
        "label": "Coastal stripe", "note": "Navy Breton stripe, coral dot",
        "fonts": "anchored",
        "palette": {"navy": "#1E3354", "teal": "#1E3354", "pink": "#E0644A", "orange": "#5B83A6",
                    "green": "#2F7A7A", "purple": "#1E3354", "blue": "#5B83A6", "red": "#E0644A",
                    "brown": "#7A6A58", "ink": "#1E2A3A", "paper": "#FAF8F3", "rule": "#B9CCDB"},
        "month": {"kicker": "Anchored", "sub": "", "notes": ["Tide's coming in"]},
    },
}

# Retired looks. They still resolve (old plan files, and the layouts build on
# 02, 06, 11 and 12) but the picker no longer offers them.
LEGACY: dict[str, dict[str, str]] = {
    "original": {"label": "Original", "note": "This Family Success Planner"},
    "02": {"label": "Boxed records", "note": "Black on white"},
    "03": {"label": "Botanical", "note": "Sage and florals"},
    "04": {"label": "Marker journal", "note": "Grid and doodles"},
    "05": {"label": "Soft intention", "note": "Pastel modules"},
    "06": {"label": "School notebook", "note": "Blue rules"},
    "07": {"label": "Editorial", "note": "Wide type and air"},
    "08": {"label": "Stamp frame", "note": "Double rule"},
    "09": {"label": "Swiss grid", "note": "Flush and red"},
    "10": {"label": "Keepsake", "note": "Ornaments and script"},
    "11": {"label": "Executive desk", "note": "Daily Plan, navy bars"},
    "12": {"label": "Beautiful day", "note": "Cottagecore florals"},
    "13": {"label": "Boho earth", "note": "Grounded, grateful"},
    "14": {"label": "Scrapbook", "note": "Good Things collage"},
    "15": {"label": "Street journal", "note": "Let's Get It"},
    "16": {"label": "Reset", "note": "Reset & Refocus"},
    "17": {"label": "Intention", "note": "Plan with intention"},
}

PRESETS: dict[str, dict[str, str]] = {
    key: {"label": look["label"], "note": look["note"]} for key, look in LOOKS.items()
}

# Planner layouts: a look (02, 06, 11, 12) crossed with a page structure
# (a split, b stacked bands, c sidebar). Each id keeps its parent look's
# colours and chrome and adds its own box style. Monthly pages switch to the
# layout version, and a weekly and a daily sheet join the book.
LAYOUTS: dict[str, str] = {
    "a": "Split",
    "b": "Stacked",
    "c": "Sidebar",
}

LAYOUT_PRESETS: dict[str, dict[str, str]] = {
    "02a": {"label": "Boxed records A", "note": "Split, black header bars"},
    "02b": {"label": "Boxed records B", "note": "Stacked, double-rule frames"},
    "02c": {"label": "Boxed records C", "note": "Sidebar, ledger rules"},
    "06a": {"label": "School notebook A", "note": "Split, ruled paper with red margin"},
    "06b": {"label": "School notebook B", "note": "Stacked, washi-tape labels"},
    "06c": {"label": "School notebook C", "note": "Sidebar, index cards"},
    "11a": {"label": "Executive desk A", "note": "Split, navy header bars"},
    "11b": {"label": "Executive desk B", "note": "Stacked, hairline rules"},
    "11c": {"label": "Executive desk C", "note": "Sidebar, framed with inset titles"},
    "12a": {"label": "Beautiful day A", "note": "Split, rounded cards with pill tabs"},
    "12b": {"label": "Beautiful day B", "note": "Stacked, soft tinted panels"},
    "12c": {"label": "Beautiful day C", "note": "Sidebar, stitched borders"},
}

# Font sets the layouts were drawn with. A layout book uses its look's set
# unless the config or the command line names one.
LAYOUT_FONTS: dict[str, str] = {
    "02": "ledger",
    "06": "composition-book",
    "11": "boardroom",
    "12": "garden-party",
}

# Colours the layouts were drawn with, as the twelve palette tokens, so the
# worksheets match the month, weekly and daily sheets. A layout book puts
# these over the theme; the config's own `palette:` block still wins.
LOOK_PALETTES: dict[str, dict[str, str]] = {
    "02": {"navy": "#111111", "teal": "#111111", "pink": "#444444", "orange": "#444444",
           "green": "#444444", "purple": "#444444", "blue": "#444444", "red": "#111111",
           "brown": "#444444", "ink": "#111111", "paper": "#FFFFFF", "rule": "#111111"},
    "06": {"navy": "#1A2744", "teal": "#C23B3B", "pink": "#C23B3B", "orange": "#C23B3B",
           "green": "#1A2744", "purple": "#1A2744", "blue": "#4A6FA5", "red": "#C23B3B",
           "brown": "#1A2744", "ink": "#1A2744", "paper": "#FFFDF5", "rule": "#A7C4E0"},
    "11": {"navy": "#1B365D", "teal": "#4A5A72", "pink": "#4A5A72", "orange": "#4A5A72",
           "green": "#4A5A72", "purple": "#1B365D", "blue": "#1B365D", "red": "#4A5A72",
           "brown": "#4A5A72", "ink": "#1B365D", "paper": "#FFFFFF", "rule": "#D5DBE4"},
    "12": {"navy": "#5C4033", "teal": "#8FAE8A", "pink": "#E8B4BE", "orange": "#E8B4BE",
           "green": "#8FAE8A", "purple": "#D4C0E0", "blue": "#D4C0E0", "red": "#C98A94",
           "brown": "#5C4033", "ink": "#5C4033", "paper": "#FBF7F2", "rule": "#E8D4D0"},
}

# Pages a layout design adds to the book when the page list names neither.
LAYOUT_PAGES: list[str] = ["weekly", "daily"]

# Layouts after the looks, blank last.
PRESETS.update(LAYOUT_PRESETS)
PRESETS["blank"] = {"label": "Blank", "note": "Bare sheets to build on"}


def parts(design: str) -> dict[str, str]:
    """Split a design id into its look, layout and box style.

    `02b` -> base 02, layout b, box 02b. Plain looks have no layout; their
    daily and weekly sheets use layout a with a neutral box.
    """
    if design in LAYOUT_PRESETS:
        return {"base": design[:2], "layout": design[2], "box": design}
    return {"base": design, "layout": "", "box": "plain"}


def look_fonts(design: str) -> str:
    """The typeface set a look or layout book uses by default; '' otherwise."""
    if design in LOOKS:
        return LOOKS[design]["fonts"]
    look = parts(design)
    return LAYOUT_FONTS.get(look["base"], "") if look["layout"] else ""


def look_palette(design: str) -> dict[str, str]:
    """The palette tokens a look or layout book puts over its theme; {} otherwise."""
    if design in LOOKS:
        return dict(LOOKS[design]["palette"])
    look = parts(design)
    return dict(LOOK_PALETTES.get(look["base"], {})) if look["layout"] else {}


def names() -> list[str]:
    """Ids offered in the picker: the looks, the layouts, then blank."""
    return list(PRESETS)


def resolve(spec: str | None) -> str:
    key = (spec or DEFAULT_DESIGN).strip().lower()
    if key in LEGACY:
        return key
    if key not in PRESETS:
        raise KeyError(f"unknown design '{spec}'. Available: {', '.join(names())}")
    return key


def clamp_type_size(raw: dict | None) -> dict[str, float]:
    """Merge a partial mapping onto the defaults and clamp each role."""
    out = dict(DEFAULT_TYPE_SIZE)
    if not raw:
        return out
    for key, (lo, hi) in TYPE_SIZE_RANGE.items():
        if key not in raw or raw[key] in (None, ""):
            continue
        try:
            value = float(raw[key])
        except (TypeError, ValueError) as exc:
            raise KeyError(f"type_size.{key} must be a number") from exc
        out[key] = max(lo, min(hi, round(value, 1)))
    unknown = set(raw) - set(TYPE_SIZE_RANGE)
    if unknown:
        raise KeyError(f"unknown type_size key(s) {sorted(unknown)}")
    return out
