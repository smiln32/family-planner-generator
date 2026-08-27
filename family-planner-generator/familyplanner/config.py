"""Loading, validating and defaulting the planner configuration."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import themes, typefaces

# The brand palette lifted from the reference planner. Every template reaches
# for these through CSS custom properties, so re-theming the whole 31-page book
# is a matter of editing the `palette` block in the config.
DEFAULT_PALETTE: dict[str, str] = {
    "navy": "#16325F",
    "teal": "#14A0A5",
    "pink": "#EF3E63",
    "orange": "#F7A81B",
    "green": "#6DB033",
    "purple": "#7C4DA0",
    "blue": "#2F6FD1",
    "red": "#D93025",
    "brown": "#8A5A2B",
    "ink": "#1F2933",
    "paper": "#FFFFFF",
    "rule": "#B9C3CF",
}

# Per-month personality: accent colour, seasonal motif, greeting strip and the
# footer line. `planner.py months` prints this table so it is easy to edit.
DEFAULT_MONTHS: list[dict[str, str]] = [
    {"name": "January", "accent": "teal", "motif": "snowman",
     "tagline": "A New Month, New Memories Together!",
     "footer": "Together is our favorite place to be."},
    {"name": "February", "accent": "pink", "motif": "hearts",
     "tagline": "Love Grows Here",
     "footer": "Making time together makes the best memories."},
    {"name": "March", "accent": "green", "motif": "sprout",
     "tagline": "Fresh Starts and Happy Hearts",
     "footer": "Little moments make the biggest memories."},
    {"name": "April", "accent": "green", "motif": "tulips",
     "tagline": "Make Every Day a Beautiful Memory",
     "footer": "Family time is the best time."},
    {"name": "May", "accent": "pink", "motif": "flowers",
     "tagline": "Bloom Together, Grow Together",
     "footer": "Home is where our story begins."},
    {"name": "June", "accent": "orange", "motif": "sun",
     "tagline": "Sunshine, Smiles and Family Time",
     "footer": "Make every sunny day count."},
    {"name": "July", "accent": "blue", "motif": "beach",
     "tagline": "Adventure Awaits Our Family",
     "footer": "Collect moments, not things."},
    {"name": "August", "accent": "purple", "motif": "sun",
     "tagline": "Soak Up Every Last Sunny Day",
     "footer": "The best memories are made together."},
    {"name": "September", "accent": "teal", "motif": "school",
     "tagline": "New Routines, New Adventures",
     "footer": "One family, one team."},
    {"name": "October", "accent": "orange", "motif": "pumpkin",
     "tagline": "Cozy Days and Family Ways",
     "footer": "Grateful hearts, happy home."},
    {"name": "November", "accent": "brown", "motif": "leaves",
     "tagline": "Grateful Together, Always",
     "footer": "Thankful for every moment together."},
    {"name": "December", "accent": "red", "motif": "snowflake",
     "tagline": "Make Every Day a Beautiful Memory",
     "footer": "Family Together - A Season of Love!"},
]

DEFAULT_CONFIG: dict[str, Any] = {
    "year": 2027,
    "title": "Family Success Planner",
    "subtitle": "Plan Together. Grow Together. Succeed Together.",
    "family_name": "",
    # Sunday-first matches the reference planner; "monday" gives ISO weeks.
    "week_starts": "sunday",
    # True prints real dates in the monthly grids. False reproduces the
    # reference book's undated (write-your-own) grids.
    "dated_months": True,
    # Adds tab-rail navigation and an index, for reading on a tablet.
    "linked": False,
    # Rows on the shared trackers, so a family of three is not stuck with five.
    "members": ["", "", "", "", ""],
    "theme": "classic",
    "fonts": "classic",
    "palette": {},
    "months": [],
    "pages": [],
    "page_size": "letter",
    "output_name": "",
}

# The 31-page running order of the reference planner.
DEFAULT_PAGES: list[str] = [
    "cover",
    "belongs_to",
    "how_to_use",
    "vision_mission",
    "year_goals",
    "values",
    "annual_calendar",
    "budget",
    "chores",
    "meal_plan",
    "grocery",
    "health_tracker",
    "emergency",
    "school_activities",
    "family_time",
    "months",
    "vacation",
    "home_maintenance",
    "year_end",
]

PAGE_SIZES: dict[str, tuple[float, float]] = {
    "letter": (8.5, 11.0),
    "a4": (8.27, 11.69),
}


class ConfigError(ValueError):
    """Raised when a config file is present but unusable."""


@dataclass
class Config:
    year: int
    title: str
    subtitle: str
    family_name: str
    week_starts: str
    dated_months: bool
    linked: bool
    theme: str
    faces: typefaces.Typefaces
    members: list[str]
    palette: dict[str, str]
    months: list[dict[str, str]]
    pages: list[str]
    page_size: str
    output_name: str
    source: Path | None = field(default=None)

    @property
    def page_inches(self) -> tuple[float, float]:
        return PAGE_SIZES[self.page_size]

    @property
    def sunday_first(self) -> bool:
        return self.week_starts == "sunday"

    @property
    def stem(self) -> str:
        """Filename stem for the built PDF, e.g. 2027-Ramirez-Family-Planner."""
        if self.output_name:
            return self.output_name
        parts = [str(self.year)]
        if self.family_name:
            parts.append(self.family_name.replace(" ", "-"))
        parts.append("Family-Planner")
        return "-".join(parts)


def load(path: Path | None) -> Config:
    """Read `path` (YAML) over the defaults, or return pure defaults if None."""
    data = copy.deepcopy(DEFAULT_CONFIG)

    if path is not None:
        if not path.exists():
            raise ConfigError(f"config file not found: {path}")
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"{path} is not valid YAML: {exc}") from exc
        if not isinstance(loaded, dict):
            raise ConfigError(f"{path} must contain a YAML mapping at the top level")
        unknown = set(loaded) - set(DEFAULT_CONFIG)
        if unknown:
            raise ConfigError(
                f"{path}: unknown option(s) {sorted(unknown)}; "
                f"valid options are {sorted(DEFAULT_CONFIG)}"
            )
        data.update(loaded)

    # Palette resolution, lowest precedence first: the built-in defaults, then
    # the named theme, then whatever the config's own `palette:` block sets.
    try:
        preset = themes.resolve(str(data.get("theme") or themes.DEFAULT_THEME))
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc
    palette = dict(DEFAULT_PALETTE)
    palette.update(preset)
    palette.update(data.get("palette") or {})

    try:
        faces = typefaces.resolve(data.get("fonts"))
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc

    months = _merge_months(data.get("months") or [])
    pages = list(data.get("pages") or DEFAULT_PAGES)
    members = [str(m) for m in (data.get("members") or [])]

    week_starts = str(data["week_starts"]).lower()
    if week_starts not in {"sunday", "monday"}:
        raise ConfigError("week_starts must be sunday or monday")

    page_size = str(data["page_size"]).lower()
    if page_size not in PAGE_SIZES:
        raise ConfigError(f"page_size must be one of {sorted(PAGE_SIZES)}")

    try:
        year = int(data["year"])
    except (TypeError, ValueError) as exc:
        raise ConfigError("year must be a whole number") from exc
    if not 1900 <= year <= 2999:
        raise ConfigError("year must be between 1900 and 2999")

    return Config(
        year=year,
        title=str(data["title"]),
        subtitle=str(data["subtitle"]),
        family_name=str(data["family_name"]),
        week_starts=week_starts,
        dated_months=bool(data["dated_months"]),
        linked=bool(data.get("linked", False)),
        theme=str(data.get("theme") or themes.DEFAULT_THEME).lower(),
        faces=faces,
        members=members,
        palette=palette,
        months=months,
        pages=pages,
        page_size=page_size,
        output_name=str(data["output_name"]),
        source=path,
    )


def _merge_months(overrides: list[Any]) -> list[dict[str, str]]:
    """Overlay a partial months list onto the twelve defaults, by position."""
    months = copy.deepcopy(DEFAULT_MONTHS)
    if not overrides:
        return months
    if len(overrides) > 12:
        raise ConfigError("months may not have more than 12 entries")
    for i, override in enumerate(overrides):
        if override is None:
            continue
        if not isinstance(override, dict):
            raise ConfigError(f"months[{i}] must be a mapping")
        unknown = set(override) - set(months[i])
        if unknown:
            raise ConfigError(f"months[{i}]: unknown key(s) {sorted(unknown)}")
        months[i].update({k: str(v) for k, v in override.items()})
    return months
