"""Which typefaces the planner is set in.

Three roles, used consistently by every page:

    display  the chunky uppercase headings ("JANUARY", "BUDGET")
    script   the handwritten lines ("Family Planner", footer taglines)
    body     everything else - labels, tables, checklists

Pick a named preset, or name any three Google Fonts families yourself:

    fonts: rounded
    fonts:
      display: Baloo 2
      script: Caveat
      body: Quicksand
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Weights each role asks for. If a family does not publish one, the closest
# available weight is substituted rather than failing the build.
ROLE_WEIGHTS: dict[str, list[int]] = {
    "display": [600, 700],
    "script": [400],
    "body": [400, 700, 800],
}

# Generic families appended to every CSS stack, so a missing download still
# lands on something sensible rather than Times New Roman.
ROLE_FALLBACKS: dict[str, str] = {
    "display": '"Segoe UI", system-ui, sans-serif',
    "script": '"Segoe Script", "Brush Script MT", cursive',
    "body": '"Segoe UI", system-ui, -apple-system, sans-serif',
}

PRESETS: dict[str, dict[str, str]] = {
    # The reference planner's look: chunky rounded caps, bouncy brush script.
    "classic": {"display": "Fredoka", "script": "Pacifico", "body": "Nunito"},

    # Softer and more childlike; Caveat reads like a felt-tip pen.
    "rounded": {"display": "Baloo 2", "script": "Caveat", "body": "Quicksand"},

    # Crisp geometric headings with a fine joined script.
    "modern": {"display": "Poppins", "script": "Sacramento", "body": "Inter"},

    # Serif headings and copperplate script - the keepsake end of the range.
    "elegant": {"display": "Playfair Display", "script": "Great Vibes", "body": "Lato"},

    # Loud and bubbly, closest to a kids' activity book.
    "bubbly": {"display": "Baloo 2", "script": "Pacifico", "body": "Rubik"},

    # Tidy and neutral, with a relaxed handwriting accent.
    "neat": {"display": "Montserrat", "script": "Kalam", "body": "Open Sans"},
}

DEFAULT_SET = "classic"


@dataclass(frozen=True)
class Typefaces:
    """The three resolved family names, plus the CSS stacks built from them."""

    display: str
    script: str
    body: str
    preset: str = ""

    @property
    def roles(self) -> dict[str, str]:
        return {"display": self.display, "script": self.script, "body": self.body}

    def stack(self, role: str) -> str:
        """A CSS font stack for one role: chosen family, then fallbacks."""
        return f'"{self.roles[role]}", {ROLE_FALLBACKS[role]}'

    def wanted(self) -> list[tuple[str, int]]:
        """(family, weight) pairs this choice needs downloaded, de-duplicated."""
        pairs: list[tuple[str, int]] = []
        for role, family in self.roles.items():
            for weight in ROLE_WEIGHTS[role]:
                if (family, weight) not in pairs:
                    pairs.append((family, weight))
        return pairs


def slug(family: str, weight: int) -> str:
    """Filename for a downloaded face: 'Playfair Display' 700 -> playfair-display-700."""
    stem = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    return f"{stem}-{weight}.woff2"


def names() -> list[str]:
    rest = sorted(n for n in PRESETS if n != DEFAULT_SET)
    return [DEFAULT_SET, *rest]


def resolve(spec: str | dict | None) -> Typefaces:
    """Turn a preset name or a {display, script, body} mapping into Typefaces."""
    if not spec:
        spec = DEFAULT_SET

    if isinstance(spec, str):
        key = spec.strip().lower()
        if key not in PRESETS:
            raise KeyError(f"unknown typeface set '{spec}'. Available: {', '.join(names())}")
        return Typefaces(preset=key, **PRESETS[key])

    if isinstance(spec, dict):
        unknown = set(spec) - set(ROLE_WEIGHTS)
        if unknown:
            raise KeyError(
                f"unknown font role(s) {sorted(unknown)}; expected display, script, body"
            )
        base = dict(PRESETS[DEFAULT_SET])
        base.update({k: str(v).strip() for k, v in spec.items() if v})
        return Typefaces(preset="", **base)

    raise KeyError("fonts must be a preset name or a mapping of display/script/body")
