"""The chrome catalog: every design's component treatments, fully resolved.

Phase 2 step 3 (2026-10-12). The catalog is the authoritative definition of
what each design's chrome is meant to be: how its cards, headings, meta
strips, tables, check boxes, marks, write-on lines, annual calendar,
labels, footer, ornaments and page edge are treated. Blank's appearance is
NOT the implicit default with exceptions for everyone else: Blank is one
explicit entry like any other, and every design's entry is a complete
`Components` with every field set to a vocabulary value, whether or not it
was built from a reusable family base.

Each entry carries two specs:

- `components`: the INTENDED treatment, which step 4 will print through
  catalog-driven variants of the shared components (annual calendar, meta
  strips, headings, tables, ornaments) rather than duplicated templates.
- `current`: what the design prints TODAY, per the override audit of
  2026-10-12 (inherited shared defaults included), so the gap between the
  two is explicit per design (`python planner.py chrome --diff`).

The intended values of Editorial, Farmhouse and Mid-century are the three
the owner approved for Phase 2. Every other design's intended values follow
the audit's findings (where the inherited default contradicted the design's
identity) and await the owner's look; where the audit found the design fits
as it prints, intended equals current and the entry says so.

Nothing here prints yet. `render.render_html` puts the entry in the
template context and `book.html` writes one `c-<field>-<value>` class per
field on `<body>`; no stylesheet reads those classes until step 4.
Colours are not here: `palette_ref` and `fonts_ref` point at the design's
own palette and typeface set (`designs.look_palette`, `designs.look_fonts`).
See `_config/chrome-catalog.md` for the contract.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace

from . import designs

# The closed vocabulary. One tuple per component field; the first value is
# not a default, every entry names its own.
VOCAB: dict[str, tuple[str, ...]] = {
    # Card body corners (the meta strips follow the same corners).
    "corners": ("square", "soft", "rounded", "pill", "arch"),
    # Section heading on a card: a filled bar, a label over a rule, plain
    # text, an outlined label, a pill, a tape label, a label set into the
    # frame line, or a script heading.
    "heads": ("bar", "rule", "text", "outlined", "pill", "tape", "inset", "script"),
    # Meta strip at the top of a worksheet: framed box, a ruled row, or bare.
    "strip": ("boxed", "ruled", "bare"),
    # Table header row: filled with the structure colour, text over a rule,
    # or an outlined row.
    "table_head": ("filled", "rule", "outlined"),
    "table_corners": ("square", "rounded"),
    "checks": ("square", "rounded", "round"),
    # Numbered marks: a filled circle, a filled square, or a bare number.
    "marks": ("circle", "square", "text"),
    # Write-on lines.
    "lines": ("dotted", "solid", "hairline"),
    # Month heading on the annual calendar's twelve tiles.
    "calendar_head": ("pill", "bar", "rule", "text"),
    # The tile itself: a rounded box, a square box, or no box.
    "calendar_tile": ("rounded", "square", "open"),
    # Case and weight of section labels, column heads and tab text.
    "labels": ("caps-heavy", "caps-light", "lower", "sentence", "italic"),
    "footer": ("caps", "script", "rule", "lower", "fleuron"),
    # The design's own ornament set, beyond the page edge.
    "ornaments": ("none", "hearts", "sprigs", "dots", "stripe", "frame", "corner"),
    # The page edge: nothing, a band across the top, an inset frame, a
    # stripe down one side, or ruled paper.
    "page": ("plain", "band", "frame", "stripe", "ruled"),
}

FAMILIES: tuple[str, ...] = (
    "minimal", "classic", "botanical", "modern-geometric", "coastal",
    "rustic", "playful", "legacy",
)

STATUSES: tuple[str, ...] = ("look", "layout", "blank", "retired")


@dataclass(frozen=True)
class Components:
    """One treatment per component, each a value from `VOCAB`."""

    corners: str
    heads: str
    strip: str
    table_head: str
    table_corners: str
    checks: str
    marks: str
    lines: str
    calendar_head: str
    calendar_tile: str
    labels: str
    footer: str
    ornaments: str
    page: str

    def __post_init__(self) -> None:
        for name, allowed in VOCAB.items():
            value = getattr(self, name)
            if value not in allowed:
                raise ValueError(
                    f"chrome component {name}={value!r} is not one of {', '.join(allowed)}")

    def as_dict(self) -> dict[str, str]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def classes(self) -> list[str]:
        """`c-<field>-<value>` for each field, in catalog order."""
        return [f"c-{name.replace('_', '-')}-{value}" for name, value in self.as_dict().items()]

    def diff(self, other: "Components") -> dict[str, tuple[str, str]]:
        """Fields where this spec differs from `other`: name -> (self, other)."""
        mine, theirs = self.as_dict(), other.as_dict()
        return {k: (mine[k], theirs[k]) for k in mine if mine[k] != theirs[k]}


@dataclass(frozen=True)
class Chrome:
    """One design's chrome: its character in prose and its two specs."""

    id: str
    label: str
    family: str
    character: str
    header: str
    headings: str
    borders: str
    decoration: str
    density: str
    alignment: str
    calendar: str
    print: str
    palette_ref: str
    fonts_ref: str
    layouts: tuple[str, ...]
    base: str
    status: str
    components: Components
    current: Components
    corners_note: str = ""

    def __post_init__(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"chrome {self.id}: family {self.family!r} is not one of {FAMILIES}")
        if self.status not in STATUSES:
            raise ValueError(f"chrome {self.id}: status {self.status!r} is not one of {STATUSES}")

    def body_classes(self) -> str:
        """The intended spec as `<body>` classes (book.html)."""
        return " ".join(self.components.classes())

    def gap(self) -> dict[str, tuple[str, str]]:
        """Fields where the intended treatment differs from today's: name -> (intended, current)."""
        return self.components.diff(self.current)


# --- family bases ---------------------------------------------------------
# What the shared CSS prints when a design adds nothing of its own. Every
# stored entry is built from one of these with `replace`, then stored fully
# resolved; nothing reads the bases at use time.

# The shared worksheet defaults (planner.css): rounded cards with pill tabs,
# a boxed strip, filled table heads with rounded top corners, rounded check
# boxes, circle marks, dotted lines, pill month heads on rounded tiles,
# heavy caps labels, a script footer with sprigs and hearts, plain page.
SHARED = Components(
    corners="rounded", heads="pill", strip="boxed", table_head="filled",
    table_corners="rounded", checks="rounded", marks="circle", lines="dotted",
    calendar_head="pill", calendar_tile="rounded", labels="caps-heavy",
    footer="script", ornaments="sprigs", page="plain",
)

# A look (`.lk`, looks.css) on top of the shared defaults: the art, sprigs,
# divider and footer hearts are hidden and the footer is a tracked caps
# line; the annual calendar's heart bullets still print (the audit's
# "ornaments: hearts" residue).
LOOK = replace(SHARED, footer="caps", ornaments="hearts")

# A planner layout (`.layout`): square table corners, 1px solid lines, the
# shared script footer with its two hearts, no sprigs.
LAYOUT = replace(SHARED, table_corners="square", lines="hairline", ornaments="hearts")

# Family bases for the intended specs. Each is the look base with the
# treatments the family shares; a design then names its own.
MINIMAL = replace(LOOK, corners="square", heads="text", strip="ruled", table_head="rule",
                  table_corners="square", checks="square", calendar_head="rule",
                  calendar_tile="open", ornaments="none")
CLASSIC = replace(LOOK, corners="square", heads="bar", table_corners="square",
                  checks="square", calendar_head="bar", calendar_tile="square",
                  ornaments="none")
GEOMETRIC = replace(LOOK, heads="pill")
PLAYFUL = replace(LOOK, corners="rounded", heads="pill")


def _chrome(entry_id: str, **kw) -> Chrome:
    preset = {**designs.LEGACY, **designs.PRESETS}[entry_id]
    kw.setdefault("label", preset["label"])
    return Chrome(id=entry_id, **kw)


# --- the thirteen looks -----------------------------------------------------

_LOOKS: list[Chrome] = [
    _chrome(
        "editorial", family="minimal",
        character="Red nameplate, Bodoni, cover lines. A magazine page: rules, not boxes. "
                  "Owner-approved intended spec (Phase 2 trio).",
        header="Left-aligned masthead over a 2px ink rule; the banner is a red nameplate.",
        headings="Plain tracked caps labels above a 1.5px top rule; no tab pill.",
        borders="Cards are open: a single top rule, no side or bottom border, square.",
        decoration="None. No hearts, sprigs or art; the page is type and rules.",
        density="Generous leading, wide tracking on labels, open tables.",
        alignment="Flush left throughout.",
        calendar="Twelve open months: month name over a rule, no tile box, no pill.",
        print="Rules only, no bleed; ink coverage low.",
        palette_ref="editorial", fonts_ref="home-edition", layouts=(), base="editorial",
        status="look",
        components=replace(MINIMAL, marks="text", footer="rule"),
        current=replace(LOOK, corners="square", heads="text", footer="rule"),
    ),
    _chrome(
        "midcentury", family="modern-geometric",
        character="Teal, mustard and rust shapes; lowercase everywhere. "
                  "Owner-approved intended spec (Phase 2 trio).",
        header="Lowercase masthead; the banner is a pill in the structure colour.",
        headings="Pill tabs on soft-cornered cards, set lowercase like the rest of the page.",
        borders="Soft 0.05in corners on cards and strips.",
        decoration="An orange quarter-circle in the top right corner of every worksheet.",
        density="Even, airy.",
        alignment="Flush left, lowercase labels.",
        calendar="Pill month heads on rounded tiles, as today.",
        print="The corner shape runs to the trim; no other bleed.",
        palette_ref="midcentury", fonts_ref="family-plan", layouts=(), base="midcentury",
        status="look",
        components=replace(GEOMETRIC, corners="soft", labels="lower", footer="lower",
                           ornaments="corner"),
        current=replace(LOOK, corners="soft", footer="lower", ornaments="corner"),
    ),
    _chrome(
        "nordic", family="minimal",
        character="Oat, clay and sage, lots of air; lowercase. Intended values follow the "
                  "override audit (strip, tables, calendar, labels) and await the owner's look.",
        header="Lowercase masthead; the banner is bare lowercase text, widely tracked.",
        headings="Plain lowercase labels above the card; no pill.",
        borders="Hairline rule cards with 2px corners.",
        decoration="None.",
        density="The airiest look: wide gaps, few rules.",
        alignment="Flush left.",
        calendar="Open months with a plain text head.",
        print="Hairlines only.",
        palette_ref="nordic", fonts_ref="hem", layouts=(), base="nordic", status="look",
        components=replace(MINIMAL, corners="soft", checks="rounded", calendar_head="text",
                           labels="lower", footer="lower"),
        current=replace(LOOK, corners="soft", heads="text", footer="lower"),
    ),
    _chrome(
        "farmhouse", family="rustic",
        character="Grain-sack stripe, barn red, square everything. "
                  "Owner-approved intended spec (Phase 2 trio).",
        header="Bold masthead in barn red; the banner is a square ink bar.",
        headings="Square filled tab bars in the ink colour.",
        borders="1.4px ink frames, square; the meta strip is a square box.",
        decoration="The grain-sack stripe band across the top of every worksheet.",
        density="Sturdy: full frames and bars.",
        alignment="Centred masthead, flush-left cards.",
        calendar="Square tiles with a bar month head.",
        print="The stripe band runs to the trim at the top.",
        palette_ref="farmhouse", fonts_ref="home-grown", layouts=(), base="farmhouse",
        status="look",
        components=replace(CLASSIC, strip="boxed", footer="script", ornaments="stripe",
                           page="band"),
        current=replace(LOOK, corners="square", heads="bar", footer="script",
                        ornaments="stripe", page="band"),
    ),
    _chrome(
        "deco", family="classic",
        character="Navy and champagne gold, a gold frame on every page. Intended values "
                  "follow the override audit (table corners, checks, calendar) and await "
                  "the owner's look.",
        header="Wide-tracked masthead; the banner is bare caps between two gold rules.",
        headings="Square navy tab bars with gold text, lightly tracked.",
        borders="A gold hairline with a second gold outline 2px outside it; square.",
        decoration="A gold frame inset on every worksheet.",
        density="Formal, even.",
        alignment="Centred.",
        calendar="Square tiles with bar heads.",
        print="The gold frame sits inside the margin; no bleed.",
        palette_ref="deco", fonts_ref="household", layouts=(), base="deco", status="look",
        components=replace(CLASSIC, labels="caps-light", page="frame"),
        current=replace(LOOK, corners="square", heads="bar", page="frame"),
    ),
    _chrome(
        "swiss", family="minimal",
        character="Black, white and one red; a 3px top rule and nothing round. Intended "
                  "values follow the override audit (strip, tables, calendar, labels) and "
                  "await the owner's look.",
        header="Grotesk masthead under a 3px ink rule; the banner is bare red text.",
        headings="Plain sentence-case labels above a 2px top rule.",
        borders="Top rules only; square.",
        decoration="None.",
        density="Tight grid, strong rules.",
        alignment="Flush left on a grid.",
        calendar="Open months, name over a rule.",
        print="Rules only.",
        palette_ref="swiss", fonts_ref="grotesk-red", layouts=(), base="swiss", status="look",
        components=replace(MINIMAL, marks="square", labels="sentence", footer="rule"),
        current=replace(LOOK, corners="square", heads="text", checks="square",
                        marks="square", footer="rule"),
    ),
    _chrome(
        "retro", family="playful",
        character="Rainbow arcs, 70s brown and orange; rounded. As it prints today, apart "
                  "from sentence-case labels (override audit), awaiting the owner's look.",
        header="Masthead with no caps; the banner is an orange pill.",
        headings="Pill tabs on rounded cards.",
        borders="1.6px frames with 0.14in corners.",
        decoration="The annual calendar's heart bullets stay.",
        density="Chunky.",
        alignment="Centred.",
        calendar="Pill heads on rounded tiles.",
        print="No bleed.",
        palette_ref="retro", fonts_ref="good-days", layouts=(), base="retro", status="look",
        components=replace(PLAYFUL, labels="sentence"),
        current=LOOK,
    ),
    _chrome(
        "bauhaus", family="modern-geometric",
        character="Cobalt, coral, butter, black; square blocks and three dots. Intended "
                  "values follow the override audit (strip, tables, checks, calendar) and "
                  "await the owner's look.",
        header="Bold flush-left masthead; the banner is a square ink bar.",
        headings="Full-width square tab bars set into the top of each card.",
        borders="1.5px ink frames, square.",
        decoration="Three dots (coral, cobalt, butter) in the top right corner.",
        density="Blocky, even.",
        alignment="Flush left.",
        calendar="Square tiles with bar heads.",
        print="No bleed.",
        palette_ref="bauhaus", fonts_ref="plan-make-do", layouts=(), base="bauhaus",
        status="look",
        components=replace(CLASSIC, marks="square", ornaments="dots"),
        current=replace(LOOK, corners="square", heads="bar", ornaments="dots"),
    ),
    _chrome(
        "almanac", family="classic",
        character="Oxblood cloth, gold rules, outlined labels and a fleuron. Intended values "
                  "follow the override audit (tables, checks, calendar, labels) and await "
                  "the owner's look.",
        header="Tracked masthead over a double rule; the banner is italic script.",
        headings="Outlined paper tabs with a navy hairline border, lightly tracked.",
        borders="A 0.75px navy rule with a second outline outside it; square.",
        decoration="A fleuron before the footer line.",
        density="Bookish, even.",
        alignment="Centred.",
        calendar="Square tiles, month name over a rule.",
        print="Fine rules; keep at 100%.",
        palette_ref="almanac", fonts_ref="almanac", layouts=(), base="almanac", status="look",
        components=replace(CLASSIC, heads="outlined", table_head="outlined",
                           calendar_head="rule", labels="caps-light", footer="fleuron"),
        current=replace(LOOK, corners="square", heads="outlined", footer="fleuron"),
    ),
    _chrome(
        "terracotta", family="modern-geometric",
        character="Sand, clay, plum and sage; arched cards. As it prints today, apart from "
                  "sentence-case labels (override audit), awaiting the owner's look.",
        header="Masthead with no caps; the banner is a pill.",
        headings="Pill tabs on arched cards.",
        borders="1.2px frames, arched: 0.18in top corners, 0.04in bottom.",
        decoration="The annual calendar's heart bullets stay.",
        density="Even.",
        alignment="Centred.",
        calendar="Pill heads on rounded tiles.",
        print="No bleed.",
        palette_ref="terracotta", fonts_ref="home-base", layouts=(), base="terracotta",
        status="look",
        components=replace(GEOMETRIC, corners="arch", labels="sentence"),
        current=replace(LOOK, corners="arch"),
    ),
    _chrome(
        "cottage", family="botanical",
        character="Sage check, blush, Lora italic. As it prints today, apart from italic "
                  "labels (override audit), awaiting the owner's look.",
        header="Italic masthead; the banner is a blush pill.",
        headings="Outlined italic tabs on paper with a hairline border.",
        borders="1px dashed frames with 0.1in corners.",
        decoration="The gingham band across the top of every worksheet.",
        density="Soft, even.",
        alignment="Centred.",
        calendar="Pill heads on rounded tiles.",
        print="The gingham band runs to the trim at the top.",
        palette_ref="cottage", fonts_ref="life-at-home", layouts=(), base="cottage",
        status="look",
        components=replace(PLAYFUL, heads="outlined", labels="italic", footer="script",
                           page="band"),
        current=replace(LOOK, heads="outlined", footer="script", page="band"),
    ),
    _chrome(
        "gazette", family="classic",
        character="Newsprint, blackletter nameplate, hairline rules. Intended values follow "
                  "the override audit (strip, tables, checks, lines, calendar, labels) and "
                  "await the owner's look.",
        header="Masthead between a 2.5px and a 0.75px rule; the banner is italic text.",
        headings="Plain display-face labels above a 2px top rule.",
        borders="Top rules only; square.",
        decoration="None.",
        density="Columns and hairlines; dense.",
        alignment="Flush left in columns.",
        calendar="Open months, name over a rule.",
        print="Hairlines; keep at 100%.",
        palette_ref="gazette", fonts_ref="gazette", layouts=(), base="gazette", status="look",
        components=replace(MINIMAL, lines="hairline", labels="sentence", footer="rule"),
        current=replace(LOOK, corners="square", heads="text", footer="rule"),
    ),
    _chrome(
        "coastal", family="coastal",
        character="Navy Breton stripe, coral dot. As it prints today; the override audit "
                  "found its inherited chrome fits.",
        header="Bold masthead; the banner is a soft-cornered blue bar.",
        headings="Pill tabs.",
        borders="1.2px frames with 0.08in corners.",
        decoration="The Breton stripe down the left edge of every worksheet.",
        density="Even.",
        alignment="Centred.",
        calendar="Pill heads on rounded tiles.",
        print="The stripe runs to the trim on the left.",
        palette_ref="coastal", fonts_ref="anchored", layouts=(), base="coastal", status="look",
        components=replace(LOOK, page="stripe"),
        current=replace(LOOK, page="stripe"),
    ),
]


# --- the planner layouts ----------------------------------------------------
# A layout keeps its parent look's paper and chrome and adds its box style
# (designs.LAYOUT_PRESETS). One entry per id; the family base holds what
# the three share.

_LAYOUT_PROSE: dict[str, dict[str, str]] = {
    "02": dict(
        family="modern-geometric",
        header="Caps masthead in the body face; the banner prints as plain tracked text "
               "(defect, see HANDOFF.md).",
        borders="1px ink frames on cards, tables and the focus strip; square.",
        decoration="None intended; the shared footer hearts still print.",
        density="Ledger: every box ruled.",
        alignment="Centred headings.",
        calendar="Square tiles with bar heads intended; pill heads print today.",
        print="Black and white; no bleed.",
    ),
    "06": dict(
        family="playful",
        header="Masthead on ruled paper with a red margin line; the banner prints as plain "
               "tracked text (defect, see HANDOFF.md).",
        borders="Pale blue frames (the rule), rounded; index-card white panels.",
        decoration="Ruled paper on the worksheets; the shared footer hearts.",
        density="Notebook: roomy lines.",
        alignment="Flush left.",
        calendar="Pill heads on rounded tiles.",
        print="The ruled paper runs to the trim.",
    ),
    "11": dict(
        family="classic",
        header="Caps masthead in the body face; the banner prints as plain tracked text "
               "(defect, see HANDOFF.md).",
        borders="Navy frames; square or 2u corners by layout.",
        decoration="None intended; the shared footer hearts still print.",
        density="Desk diary: tight rules.",
        alignment="Flush left.",
        calendar="Square tiles with bar heads intended; pill heads print today.",
        print="No bleed.",
    ),
    "12": dict(
        family="playful",
        header="Rose script masthead; the banner prints as plain tracked text (defect, see "
               "HANDOFF.md).",
        borders="Pink 1.2px frames with 12u corners inside a double inset page border.",
        decoration="The inset page border; the shared footer hearts.",
        density="Soft, roomy.",
        alignment="Centred.",
        calendar="Pill heads on rounded tiles.",
        print="The page border sits inside the margin; no bleed.",
    ),
}

# Today's print per layout family (the look base plus the family's own rules).
_LAYOUT_CURRENT: dict[str, Components] = {
    "02": replace(LAYOUT, corners="square", heads="bar", footer="script"),
    "06": replace(LAYOUT, corners="rounded", heads="script"),
    "11": replace(LAYOUT, corners="soft", heads="bar"),
    "12": replace(LAYOUT, corners="rounded", heads="pill", lines="dotted", page="frame"),
}

# The intended family spec; the audit's findings for each family.
_LAYOUT_INTENDED: dict[str, Components] = {
    "02": replace(_LAYOUT_CURRENT["02"], checks="square", marks="square",
                  calendar_head="bar", calendar_tile="square", footer="caps",
                  ornaments="none"),
    "06": _LAYOUT_CURRENT["06"],
    "11": replace(_LAYOUT_CURRENT["11"], calendar_head="bar", calendar_tile="square",
                  footer="caps", ornaments="none"),
    "12": _LAYOUT_CURRENT["12"],
}

# Each layout's own box style on top of its family: (corners, heads, extras).
_LAYOUT_BOX: dict[str, dict[str, str]] = {
    "02a": {"corners": "square", "heads": "bar"},
    "02b": {"corners": "square", "heads": "inset"},
    "02c": {"corners": "square", "heads": "rule"},
    "06a": {"corners": "rounded", "heads": "script"},
    "06b": {"corners": "rounded", "heads": "tape"},
    "06c": {"corners": "rounded", "heads": "rule"},
    "11a": {"corners": "soft", "heads": "bar"},
    "11b": {"corners": "square", "heads": "rule"},
    "11c": {"corners": "soft", "heads": "inset"},
    "12a": {"corners": "rounded", "heads": "pill"},
    "12b": {"corners": "rounded", "heads": "script"},
    "12c": {"corners": "rounded", "heads": "inset"},
}

# Where a layout's own intended treatment differs from its family (override
# audit): 06a's script headings and 12b and 12c's script headings read
# against heavy caps labels; 11b's hairline rules against a boxed strip.
_LAYOUT_OWN: dict[str, dict[str, str]] = {
    "06a": {"labels": "sentence"},
    "11b": {"strip": "ruled"},
    "12b": {"labels": "sentence"},
    "12c": {"labels": "sentence"},
}

_LAYOUT_HEADINGS: dict[str, str] = {
    "02a": "Filled ink header bars.",
    "02b": "Headings set into the double-rule frame, centred, masked with paper.",
    "02c": "Headings over a 2px top rule, in the frame colour.",
    "06a": "Script headings on index cards beside the margin line.",
    "06b": "Washi-tape labels, tilted 2 degrees (owner-approved, 2026-10-11).",
    "06c": "Headings over a 1.5px rule inside the card.",
    "11a": "Navy header bars with white text.",
    "11b": "Headings over a hairline top rule.",
    "11c": "Headings set into the frame line, in the frame colour.",
    "12a": "Pill tabs in the structure colour on rounded cards.",
    "12b": "Script headings on soft tinted panels.",
    "12c": "Script headings set into a stitched (dashed) border.",
}


def _layout(entry_id: str) -> Chrome:
    base = designs.parts(entry_id)["base"]
    preset = designs.LAYOUT_PRESETS[entry_id]
    box = _LAYOUT_BOX[entry_id]
    current = replace(_LAYOUT_CURRENT[base], **box)
    intended = replace(_LAYOUT_INTENDED[base], **box, **_LAYOUT_OWN.get(entry_id, {}))
    prose = _LAYOUT_PROSE[base]
    verdict = ("As it prints today; the override audit found it fits."
               if intended == current else
               "Intended values follow the override audit and await the owner's look.")
    return Chrome(
        id=entry_id, label=preset["label"], family=prose["family"],
        character=f"{preset['note']}. Layout {entry_id[2]} of {designs.LEGACY[base]['label']}. {verdict}",
        header=prose["header"], headings=_LAYOUT_HEADINGS[entry_id],
        borders=prose["borders"], decoration=prose["decoration"],
        density=prose["density"], alignment=prose["alignment"],
        calendar=prose["calendar"], print=prose["print"],
        palette_ref=entry_id, fonts_ref=designs.look_fonts(entry_id),
        layouts=tuple(sorted(k[2] for k in designs.LAYOUT_PRESETS if k[:2] == base)),
        base=base, status="layout", components=intended, current=current,
    )


_LAYOUTS: list[Chrome] = [_layout(entry_id) for entry_id in designs.LAYOUT_PRESETS]


# --- blank and the retired original ---------------------------------------

_BLANK = _chrome(
    "blank", family="minimal",
    character="Bare sheets to build on. Blank prints the shared CSS defaults (planner.css) "
              "with the art, banner and divider hidden and square cards; those defaults are "
              "written here explicitly, so Blank is one entry, not the implicit default. "
              "As it prints today.",
    header="Plain masthead, no art, no banner.",
    headings="Pill tabs in the heading colour.",
    borders="Hairline rule frames, square.",
    decoration="Footer sprigs and hearts only.",
    density="Shared defaults.",
    alignment="Centred.",
    calendar="Pill heads on rounded tiles.",
    print="No bleed.",
    palette_ref="linen", fonts_ref="elegant", layouts=(), base="blank", status="blank",
    components=replace(SHARED, corners="square"),
    current=replace(SHARED, corners="square"),
)

_ORIGINAL = _chrome(
    "original", family="legacy",
    character="This Family Success Planner: the illustrated house cover and the shared "
              "worksheet chrome as first printed. Locked: do not restyle.",
    header="Masthead beside the house art, with the banner ribbon.",
    headings="Pill tabs on rounded cards.",
    borders="1.4px frames with 0.11in corners.",
    decoration="Illustrations, dividers, sprigs and hearts throughout.",
    density="Shared defaults.",
    alignment="Centred.",
    calendar="Pill heads on rounded tiles.",
    print="No bleed.",
    palette_ref="linen", fonts_ref="elegant", layouts=(), base="original", status="retired",
    components=SHARED, current=SHARED,
)


CATALOG: dict[str, Chrome] = {
    entry.id: entry for entry in [*_LOOKS, *_LAYOUTS, _BLANK, _ORIGINAL]
}


def names() -> list[str]:
    """Catalog ids: the picker's designs in order, then `original`."""
    return list(CATALOG)


def families() -> tuple[str, ...]:
    return FAMILIES


def get(design: str) -> Chrome:
    """The catalog entry for a design id; a clear KeyError for anything else."""
    try:
        return CATALOG[design]
    except KeyError:
        raise KeyError(f"unknown chrome '{design}'. Available: {', '.join(names())}") from None


def for_design(design: str) -> Chrome | None:
    """The entry for a resolved design, or None for a retired look that has
    none (`02` to `17`; they are locked and not offered, and the layouts
    that build on them have their own entries)."""
    return CATALOG.get(design)
