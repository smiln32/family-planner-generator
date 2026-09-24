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
