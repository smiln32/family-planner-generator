"""Page-look presets for the whole book.

Colour is `theme`. Typefaces are `fonts`. This module is a third axis: a class
on <body> restyles paper and chrome. Cover markup for alternate looks lives in
`templates/pages/cover.html`. Looks 02–17 are unfinished; see
`shared/looks-handoff.md`.
"""

from __future__ import annotations

DEFAULT_DESIGN = "original"

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

# id -> short label for the picker. Notes are for the UI, not print.
PRESETS: dict[str, dict[str, str]] = {
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
    "blank": {"label": "Blank", "note": "Bare sheets to build on"},
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

# Font sets the layouts were drawn with. Suggested, not enforced.
LAYOUT_FONTS: dict[str, str] = {
    "02": "ledger",
    "06": "composition-book",
    "11": "boardroom",
    "12": "garden-party",
}

# Pages a layout design adds to the book when the page list names neither.
LAYOUT_PAGES: list[str] = ["weekly", "daily"]

# Keep blank last in the picker.
_blank = PRESETS.pop("blank")
PRESETS.update(LAYOUT_PRESETS)
PRESETS["blank"] = _blank


def parts(design: str) -> dict[str, str]:
    """Split a design id into its look, layout and box style.

    `02b` -> base 02, layout b, box 02b. Plain looks have no layout; their
    daily and weekly sheets use layout a with a neutral box.
    """
    if design in LAYOUT_PRESETS:
        return {"base": design[:2], "layout": design[2], "box": design}
    return {"base": design, "layout": "", "box": "plain"}


def names() -> list[str]:
    return list(PRESETS)


def resolve(spec: str | None) -> str:
    key = (spec or DEFAULT_DESIGN).strip().lower()
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
