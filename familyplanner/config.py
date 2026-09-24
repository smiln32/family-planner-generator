"""Loading, validating and defaulting the planner configuration."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import designs, themes, typefaces

# Factory colours: sage, dusty rose and clay on warm paper. Token names stay
# the same (navy, teal, …) so templates do not care which look is default.
DEFAULT_PALETTE: dict[str, str] = {
    "navy": "#3E5344",
    "teal": "#5F7A62",
    "pink": "#C4A09A",
    "orange": "#C9956A",
    "green": "#8AA084",
    "purple": "#A0909C",
    "blue": "#7A8B88",
    "red": "#B56858",
    "brown": "#8A6B52",
    "ink": "#3A3F3A",
    "paper": "#F6F1E8",
    "rule": "#DDD6CC",
}

# Plain-language names for the visual editor. Token keys stay as templates use them.
PALETTE_ROLES: list[tuple[str, str]] = [
    ("navy", "Headings"),
    ("teal", "Main accent"),
    ("pink", "Soft accent"),
    ("orange", "Warm accent"),
    ("green", "Green"),
    ("purple", "Purple"),
    ("blue", "Blue"),
    ("red", "Red"),
    ("brown", "Brown"),
    ("ink", "Body text"),
    ("paper", "Paper"),
    ("rule", "Lines"),
]

_HEX_RE = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


def normalize_hex(raw: str) -> str:
    """Accept #rgb or #rrggbb (optional leading #) and return #RRGGBB."""
    text = str(raw or "").strip()
    if text and not text.startswith("#"):
        text = f"#{text}"
    if not _HEX_RE.fullmatch(text):
        raise ConfigError(f"colour must be a hex value like #3E5344 (got {raw!r})")
    if len(text) == 4:
        text = "#" + "".join(ch * 2 for ch in text[1:])
    return text.upper()


def theme_palette(theme: str) -> dict[str, str]:
    """Twelve tokens for a named theme, before any personal replacements."""
    merged = dict(DEFAULT_PALETTE)
    merged.update(themes.resolve(theme or themes.DEFAULT_THEME))
    return {key: normalize_hex(value) for key, value in merged.items()}


def sanitize_palette(raw: Any) -> dict[str, str]:
    """Keep only known tokens with valid hex values."""
    if not raw:
        return {}
    if not isinstance(raw, dict):
        raise ConfigError("palette must map colour names to hex values")
    out: dict[str, str] = {}
    for key, value in raw.items():
        name = str(key)
        if name not in DEFAULT_PALETTE:
            raise ConfigError(
                f"unknown palette colour {name!r}; "
                f"valid names are {list(DEFAULT_PALETTE)}"
            )
        out[name] = normalize_hex(value)
    return out


def palette_overrides(theme: str, palette: Any) -> dict[str, str]:
    """Tokens that differ from the chosen theme, for saving in a plan file."""
    base = theme_palette(theme)
    cleaned = sanitize_palette(palette)
    return {key: value for key, value in cleaned.items() if value != base[key]}


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
    # Cover year when the book is undated: auto (fill-in blanks), print, blank, omit.
    "cover_year": "auto",
    # Printed on the cover and year mastheads instead of the numeric year.
    # Empty means use `year`. "Our" or "2027-2028" are typical overrides.
    "cover_text": "",
    # Adds tab-rail navigation and an index, for reading on a tablet.
    "linked": False,
    # Rows on the shared trackers, so a family of three is not stuck with five.
    "members": ["", "", "", "", ""],
    "theme": "linen",
    "fonts": "elegant",
    "design": "original",
    "type_size": {},
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
    "5.5x8": (5.5, 8.0),
    "6x9": (6.0, 9.0),
    "letter": (8.5, 11.0),
}

PAGE_SIZE_LABELS: dict[str, str] = {
    "5.5x8": "5.5 × 8 in",
    "6x9": "6 × 9 in",
    "letter": "8.5 × 11 in",
}

# Older configs and typed-in sizes land on one of the three names above.
PAGE_SIZE_ALIASES: dict[str, str] = {
    "a4": "letter",
    "8.5x11": "letter",
    "usletter": "letter",
    "us-letter": "letter",
}


def normalize_page_size(raw: str | None) -> str:
    """Map a config or UI value onto one of PAGE_SIZES."""
    key = str(raw or "letter").strip().lower().replace(" ", "").replace("×", "x")
    key = PAGE_SIZE_ALIASES.get(key, key)
    if key not in PAGE_SIZES:
        raise ConfigError(
            f"page_size must be one of {list(PAGE_SIZES)} (got {raw!r})"
        )
    return key


PLAN_NOTE = """# Family Success Planner

Keep this file.

- Next year, open the planner, click **Open a plan**, then change the year.
- Send a copy to a friend if they want the same look. They can change the family name.
"""


def render_plan_markdown(data: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    return f"---\n{dumped}---\n\n{PLAN_NOTE}"


def parse_plan_text(text: str) -> dict[str, Any]:
    """Read a downloaded plan (.md with YAML front matter) or a raw YAML file."""
    body = (text or "").lstrip("\ufeff").strip()
    if not body:
        raise ConfigError("that file is empty")
    if body.startswith("---"):
        rest = body[3:].lstrip("\n")
        end = rest.find("\n---")
        if end < 0:
            raise ConfigError("that plan file is missing the closing ---")
        raw = rest[:end]
    else:
        raw = body
    try:
        loaded = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not read that plan file: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError("that plan file must start with settings, not a list")
    unknown = set(loaded) - set(DEFAULT_CONFIG)
    if unknown:
        raise ConfigError(f"unknown option(s) {sorted(unknown)}")
    if "page_size" in loaded:
        loaded["page_size"] = normalize_page_size(loaded["page_size"])
    return loaded


def plan_filename(data: dict[str, Any]) -> str:
    year = data.get("year") or "planner"
    name = str(data.get("family_name") or "family").strip() or "family"
    return f"{safe_stem(f'{year}-{name}-planner', 'planner')}.md"


class ConfigError(ValueError):
    """Raised when a config file is present but unusable."""


# Windows refuses these as filenames whatever the extension.
_RESERVED_STEMS = {"CON", "PRN", "AUX", "NUL",
                   *(f"COM{i}" for i in range(1, 10)),
                   *(f"LPT{i}" for i in range(1, 10))}


def safe_stem(text: str, fallback: str = "Family-Planner") -> str:
    """A filename stem that stays inside its folder on every OS.

    Letters (any language), digits, `-`, `_` and `.` survive; everything
    else, path separators included, becomes a single dash. Leading dots are
    dropped so `..` can never name a parent folder.
    """
    kept = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in str(text or ""))
    kept = re.sub(r"[-.]{2,}", "-", kept).strip("-.")[:120].strip("-.")
    if not kept or kept.upper().split(".")[0] in _RESERVED_STEMS:
        return fallback
    return kept


def output_path(out_dir: Path, stem: str, suffix: str) -> Path:
    """`out_dir/stem.suffix`, refusing anything that resolves elsewhere."""
    root = Path(out_dir).resolve()
    target = (root / f"{safe_stem(stem)}{suffix}").resolve()
    if target.parent != root:
        raise ConfigError(f"refusing to write outside {root}: {target}")
    return target


# --- field validators, shared by the YAML loader, the CLI and the UI --------

WEEK_STARTS = ("sunday", "monday")
COVER_YEAR_MODES = ("auto", "print", "blank", "omit")
YEAR_RANGE = (1900, 2999)

# Month names become page ids and tab labels, so keep them to plain words.
_MONTH_NAME_RE = re.compile(r"^[^\W\d_](?:[^\W_]|[ .'-]){0,29}$")


def check_year(raw: Any) -> int:
    try:
        year = int(raw)
    except (TypeError, ValueError) as exc:
        raise ConfigError("year must be a whole number") from exc
    lo, hi = YEAR_RANGE
    if not lo <= year <= hi:
        raise ConfigError(f"year must be between {lo} and {hi}")
    return year


def check_week_starts(raw: Any) -> str:
    value = str(raw or "sunday").strip().lower()
    if value not in WEEK_STARTS:
        raise ConfigError("week_starts must be sunday or monday")
    return value


def check_cover_year(raw: Any) -> str:
    value = str(raw or "auto").strip().lower()
    if value not in COVER_YEAR_MODES:
        raise ConfigError("cover_year must be auto, print, blank, or omit")
    return value


def check_theme(raw: Any) -> str:
    name = str(raw or themes.DEFAULT_THEME).strip().lower()
    try:
        themes.resolve(name)
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc
    return name


def check_fonts(raw: Any) -> typefaces.Typefaces:
    try:
        return typefaces.resolve(raw)
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc


def check_design(raw: Any) -> str:
    try:
        return designs.resolve(raw)
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc


def check_type_size(raw: Any) -> dict[str, float]:
    if raw and not isinstance(raw, dict):
        raise ConfigError("type_size must map display/body to numbers")
    try:
        return designs.clamp_type_size(raw or {})
    except KeyError as exc:
        raise ConfigError(str(exc).strip("\"'")) from exc


def check_str_list(raw: Any, name: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, (list, tuple)):
        raise ConfigError(f"{name} must be a list")
    return [str(item) for item in raw]


@dataclass
class Config:
    year: int
    title: str
    subtitle: str
    family_name: str
    week_starts: str
    dated_months: bool
    cover_year: str
    cover_text: str
    linked: bool
    theme: str
    design: str
    type_size: dict[str, float]
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
    def cover_year_display(self) -> str:
        """What to print where the year goes: custom cover line, or the year."""
        text = (self.cover_text or "").strip()
        return text if text else str(self.year)

    @property
    def cover_year_is_word(self) -> bool:
        """True when the cover line is not a date-like numeral (skip uppercase)."""
        compact = "".join(ch for ch in self.cover_year_display if ch.isalnum())
        return bool(compact) and not compact.isdigit()

    @property
    def year_on_cover(self) -> str:
        """Cover year treatment: print, blank (fill-in), or omit.

        Dated books always print the cover line (custom text, or the year).
        Undated books default to fill-in blanks; a non-empty cover_text prints
        instead of blanks. `omit` hides the line.
        """
        if self.dated_months:
            return "print"
        mode = (self.cover_year or "auto").lower()
        if mode == "omit":
            return "omit"
        if (self.cover_text or "").strip():
            return "print"
        if mode == "print":
            return "print"
        return "blank"

    @property
    def stem(self) -> str:
        """Filename stem for the built PDF, e.g. 2027-Ramirez-Family-Planner.

        Always a bare name: separators and leading dots are stripped, so a
        family name or output_name can never point outside the output folder.
        """
        if self.output_name.strip():
            return safe_stem(self.output_name)
        parts = [str(self.year)]
        if self.family_name.strip():
            parts.append(self.family_name)
        parts.append("Family-Planner")
        return safe_stem("-".join(parts))


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
    theme = check_theme(data.get("theme"))
    palette = theme_palette(theme)
    palette.update(sanitize_palette(data.get("palette")))

    return Config(
        year=check_year(data["year"]),
        title=str(data["title"]),
        subtitle=str(data["subtitle"]),
        family_name=str(data["family_name"] or ""),
        week_starts=check_week_starts(data["week_starts"]),
        dated_months=bool(data["dated_months"]),
        cover_year=check_cover_year(data.get("cover_year")),
        cover_text=str(data.get("cover_text") or ""),
        linked=bool(data.get("linked", False)),
        theme=theme,
        design=check_design(data.get("design")),
        type_size=check_type_size(data.get("type_size")),
        faces=check_fonts(data.get("fonts")),
        members=check_str_list(data.get("members"), "members"),
        palette=palette,
        months=_merge_months(data.get("months") or []),
        pages=check_str_list(data.get("pages"), "pages") or list(DEFAULT_PAGES),
        page_size=normalize_page_size(data["page_size"]),
        output_name=str(data["output_name"] or ""),
        source=path,
    )


def validate(cfg: Config) -> Config:
    """Re-check a Config after the CLI or the UI has changed fields on it.

    `load` validates what it reads; this covers values set afterwards, so
    every entry point reaches the renderer through the same rules.
    """
    cfg.year = check_year(cfg.year)
    cfg.week_starts = check_week_starts(cfg.week_starts)
    cfg.cover_year = check_cover_year(cfg.cover_year)
    cfg.theme = check_theme(cfg.theme)
    cfg.design = check_design(cfg.design)
    cfg.type_size = check_type_size(cfg.type_size)
    cfg.faces = check_fonts(cfg.faces.preset or cfg.faces.roles)
    cfg.page_size = normalize_page_size(cfg.page_size)
    cfg.members = check_str_list(cfg.members, "members")
    cfg.pages = check_str_list(cfg.pages, "pages") or list(DEFAULT_PAGES)
    cfg.family_name = str(cfg.family_name or "")
    cfg.cover_text = str(cfg.cover_text or "")
    cfg.output_name = str(cfg.output_name or "")

    palette = dict(DEFAULT_PALETTE)
    palette.update(sanitize_palette(cfg.palette))
    cfg.palette = palette
    cfg.months = _check_months(cfg.months)
    return cfg


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
    return _check_months(months)


def _check_months(months: list[dict[str, str]]) -> list[dict[str, str]]:
    """Month names become page ids and accents index the palette; check both."""
    if len(months) != 12:
        raise ConfigError("months must describe exactly twelve months")
    seen: set[str] = set()
    for i, month in enumerate(months):
        name = str(month.get("name", "")).strip()
        if not _MONTH_NAME_RE.fullmatch(name):
            raise ConfigError(
                f"months[{i}].name must be a plain word like 'January' (got {name!r})"
            )
        if name.lower() in seen:
            raise ConfigError(f"months[{i}].name {name!r} is used twice")
        seen.add(name.lower())
        accent = str(month.get("accent", ""))
        if accent not in DEFAULT_PALETTE:
            raise ConfigError(
                f"months[{i}].accent must be a palette name like 'teal' (got {accent!r})"
            )
        month["name"] = name
    return months
