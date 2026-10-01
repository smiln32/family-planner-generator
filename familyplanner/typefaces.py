"""Which typefaces the planner is set in.

Three roles, used consistently by every page:

    display  the chunky uppercase headings ("JANUARY", "BUDGET")
    script   the handwritten lines ("Family Planner", footer taglines)
    body     everything else - labels, tables, checklists

Pick a named preset, or name any three Google Fonts families yourself:

    fonts: classic
    fonts:
      display: Open Sans
      script: Open Sans
      body: Open Sans
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Weights each role asks for. If a family does not publish one, the closest
# available weight is substituted rather than failing the build.
ROLE_WEIGHTS: dict[str, list[int]] = {
    "display": [400, 600, 700],
    "script": [400],
    "body": [400, 700, 800],
}

# Italic faces each role asks for. The looks set accents in italic (Bodoni,
# Lora, Garamond); without a real italic file the browser slants the upright
# face, which looks cheap in print. Families with no italic simply skip it.
ROLE_ITALIC_WEIGHTS: dict[str, list[int]] = {
    "display": [400],
    "script": [400],
    "body": [400],
}

# Generic families appended to every CSS stack, so a missing download still
# lands on something sensible rather than Times New Roman.
ROLE_FALLBACKS: dict[str, str] = {
    "display": '"Segoe UI", system-ui, sans-serif',
    "script": '"Segoe Script", "Brush Script MT", cursive',
    "body": '"Segoe UI", system-ui, -apple-system, sans-serif',
}

PRESETS: dict[str, dict[str, str]] = {
    # Clean sans throughout.
    "classic": {"display": "Open Sans", "script": "Open Sans", "body": "Open Sans"},

    # Chunky caps and a brush script, the former classic set.
    "playful": {"display": "Fredoka", "script": "Pacifico", "body": "Nunito"},

    # Geometric sans throughout.
    "modern": {"display": "Oxygen", "script": "Oxygen", "body": "Oxygen"},

    # Serif headings and copperplate script - the keepsake end of the range.
    "elegant": {"display": "Playfair Display", "script": "Great Vibes", "body": "Lato"},

    # A single italic script for headings, greetings and body.
    "italics": {"display": "Courgette", "script": "Courgette", "body": "Courgette"},

    # Tidy and neutral, with a relaxed handwriting accent.
    "neat": {"display": "Montserrat", "script": "Kalam", "body": "Open Sans"},

    # The thirteen looks (designs.LOOKS). Each look is set in its own trio by
    # default; Swiss grid uses grotesk-red, below. The gazette's script role is
    # its blackletter nameplate.
    "home-edition": {"display": "Bodoni Moda", "script": "Bodoni Moda", "body": "Archivo"},
    "family-plan": {"display": "Jost", "script": "Jost", "body": "Jost"},
    "hem": {"display": "DM Serif Display", "script": "DM Serif Display", "body": "DM Sans"},
    "home-grown": {"display": "Zilla Slab", "script": "Libre Baskerville", "body": "Zilla Slab"},
    "household": {"display": "Italiana", "script": "Italiana", "body": "Josefin Sans"},
    "good-days": {"display": "Shrikhand", "script": "Shrikhand", "body": "Jost"},
    "plan-make-do": {"display": "Space Grotesk", "script": "Space Grotesk", "body": "Space Grotesk"},
    "almanac": {"display": "EB Garamond", "script": "EB Garamond", "body": "EB Garamond"},
    "home-base": {"display": "Young Serif", "script": "Young Serif", "body": "DM Sans"},
    "life-at-home": {"display": "Lora", "script": "Lora", "body": "DM Sans"},
    "gazette": {"display": "Abril Fatface", "script": "UnifrakturMaguntia", "body": "Old Standard TT"},
    "anchored": {"display": "Bricolage Grotesque", "script": "Bricolage Grotesque", "body": "Bricolage Grotesque"},

    # Look original (Original) pairings.
    "sunday-kitchen": {"display": "Baloo 2", "script": "Caveat", "body": "Nunito"},
    "heirloom": {"display": "DM Serif Display", "script": "Homemade Apple", "body": "Source Sans 3"},

    # Look 02 (Boxed records) pairings.
    "ledger": {"display": "IBM Plex Sans Condensed", "script": "Nothing You Could Do", "body": "IBM Plex Sans"},
    "carbon-copy": {"display": "Libre Baskerville", "script": "Reenie Beanie", "body": "Libre Franklin"},

    # Look 03 (Botanical) pairings.
    "herbarium": {"display": "Cormorant Garamond", "script": "Pinyon Script", "body": "Mulish"},
    "eucalyptus": {"display": "Lora", "script": "Parisienne", "body": "Work Sans"},

    # Look 04 (Marker journal) pairings.
    "sharpie": {"display": "Permanent Marker", "script": "Kalam", "body": "Nunito Sans"},
    "fineliner": {"display": "Space Grotesk", "script": "Shadows Into Light", "body": "Space Grotesk"},

    # Look 05 (Soft intention) pairings.
    "morning-pages": {"display": "Cormorant", "script": "Allura", "body": "Nunito"},
    "linen-and-clay": {"display": "Josefin Sans", "script": "Sacramento", "body": "Josefin Sans"},

    # Look 06 (School notebook) pairings.
    "composition-book": {"display": "Oswald", "script": "Indie Flower", "body": "Nunito"},
    "pencil-case": {"display": "Fredoka", "script": "Gochi Hand", "body": "Andika"},

    # Look 07 (Editorial) pairings.
    "magazine": {"display": "Bodoni Moda", "script": "Mrs Saint Delafield", "body": "Public Sans"},
    "quarterly": {"display": "Instrument Serif", "script": "Dancing Script", "body": "Instrument Sans"},

    # Look 08 (Stamp frame) pairings.
    "par-avion": {"display": "Alfa Slab One", "script": "Yellowtail", "body": "Zilla Slab"},
    "post-office-green": {"display": "Abril Fatface", "script": "Satisfy", "body": "Cabin"},

    # Look 09 (Swiss grid) pairings.
    "grotesk-red": {"display": "Archivo", "script": "Archivo", "body": "Archivo"},
    "zurich-blue": {"display": "Manrope", "script": "Manrope", "body": "Manrope"},

    # Look 10 (Keepsake) pairings.
    "wedding-album": {"display": "Cormorant Garamond", "script": "Great Vibes", "body": "EB Garamond"},
    "midnight-keepsake": {"display": "Cinzel", "script": "Alex Brush", "body": "Lato"},

    # Look 11 (Executive desk) pairings.
    "boardroom": {"display": "Montserrat", "script": "Montserrat", "body": "Source Sans 3"},
    "charcoal": {"display": "Barlow Condensed", "script": "Barlow", "body": "Barlow"},

    # Look 12 (Beautiful day) pairings.
    "garden-party": {"display": "Lora", "script": "Dancing Script", "body": "Quicksand"},
    "wildflower": {"display": "Amatic SC", "script": "Caveat", "body": "Nunito"},

    # Look 13 (Boho earth) pairings.
    "terracotta": {"display": "Tenor Sans", "script": "Caveat Brush", "body": "Mulish"},
    "desert-sun": {"display": "Yeseva One", "script": "Reenie Beanie", "body": "Karla"},

    # Look 14 (Scrapbook) pairings.
    "cut-and-paste": {"display": "Chewy", "script": "Gochi Hand", "body": "Nunito"},
    "sticker-sheet": {"display": "Rubik", "script": "Covered By Your Grace", "body": "Rubik"},

    # Look 15 (Street journal) pairings.
    "sticker-bomb": {"display": "Anton", "script": "Permanent Marker", "body": "Archivo"},
    "zine": {"display": "Big Shoulders Display", "script": "Rock Salt", "body": "Space Mono"},

    # Look 16 (Reset) pairings.
    "sage-and-terracotta": {"display": "Crimson Pro", "script": "La Belle Aurore", "body": "Nunito Sans"},
    "clean-slate": {"display": "Outfit", "script": "Caveat", "body": "Outfit"},

    # Look 17 (Intention) pairings.
    "pastel-modules": {"display": "Quicksand", "script": "Homemade Apple", "body": "Quicksand"},
    "blush-and-stone": {"display": "Jost", "script": "Allura", "body": "Jost"},
}

# Old config files that still name retired sets.
_ALIASES = {"rounded": "italics", "bubbly": "playful"}

DEFAULT_SET = "elegant"

# Google Fonts family names are ASCII letters, digits and single spaces. The
# name lands inside CSS quotes and a download URL, so nothing else gets in.
FAMILY_NAME_RE = re.compile(r"[A-Za-z0-9]+(?: [A-Za-z0-9]+){0,7}")


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

    def wanted_italic(self) -> list[tuple[str, int]]:
        """(family, weight) italic pairs, de-duplicated. Missing ones are skipped."""
        pairs: list[tuple[str, int]] = []
        for role, family in self.roles.items():
            for weight in ROLE_ITALIC_WEIGHTS[role]:
                if (family, weight) not in pairs:
                    pairs.append((family, weight))
        return pairs


def slug(family: str, weight: int, italic: bool = False) -> str:
    """Filename for a downloaded face: 'Playfair Display' 700 -> playfair-display-700.

    Italics get an i suffix: playfair-display-400i.woff2.
    """
    stem = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    return f"{stem}-{weight}{'i' if italic else ''}.woff2"


def names() -> list[str]:
    rest = sorted(n for n in PRESETS if n != DEFAULT_SET)
    return [DEFAULT_SET, *rest]


def resolve(spec: str | dict | None) -> Typefaces:
    """Turn a preset name or a {display, script, body} mapping into Typefaces."""
    if not spec:
        spec = DEFAULT_SET

    if isinstance(spec, str):
        key = spec.strip().lower()
        key = _ALIASES.get(key, key)
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
        for role, family in base.items():
            if not FAMILY_NAME_RE.fullmatch(family):
                raise KeyError(
                    f"font {role} {family!r} is not a font family name; "
                    "use letters, digits and spaces, like 'Playfair Display'"
                )
        return Typefaces(preset="", **base)

    raise KeyError("fonts must be a preset name or a mapping of display/script/body")
