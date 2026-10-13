"""The book's CSS never fixes a colour per design (Phase 2 step 1, 2026-10-12).

Carla's rule: "when a theme is selected it must also control the colours
used for frames, marks, borders and decorative accents. Chrome controls
their shape and placement, not fixed colours." So `planner.css` and
`looks.css` read the twelve palette tokens and the `--c-*` roles that
`book.html` writes on `:root` (config.resolve_palette, colours.roles) and
never redefine them, and no rule outside `:root` prints a chromatic hex of
its own: not a design-scoped rule (step 1), not the shared worksheet
chrome (step 2: meta strips, table and calendar hairlines, write-on lines,
the day pill wash) and not the catalog variants in `chrome.css` (step 4)
either. The retired looks, which are not offered and keep
their old CSS, the three look-art colours and the budget donut (a chart) are
allowed by name below, each with its reason.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from familyplanner import colours, config
from familyplanner.render import STATIC_DIR

FILES = ["planner.css", "chrome.css", "looks.css"]

TOKENS = tuple(f"--{name}" for name in config.DEFAULT_PALETTE)
ROLE_PROPS = tuple(f"--c-{role}" for role in colours.ALL_ROLES) + tuple(
    f"--c-{role}-on" for role in colours.ALL_ROLES)

# Rules scoped to a design, a box style, the layout kit, a look or a retired
# daily cover: chrome, so it must read tokens and roles.
SCOPED = re.compile(r"\.design-|\.box-|\.lx|\.lk|\.d1|\.daily-")

# Allowed to keep their own colours, and why:
# - the retired looks 03 to 05, 07 to 10 and 13 to 17 (designs.LEGACY) are not
#   offered in the picker; their body-class token blocks and chrome literals
#   stay so an old plan file prints as it did ("the retired looks last or
#   never", HANDOFF.md). 02, 06, 11 and 12 are NOT here: they are the layout
#   families' chrome.
# - `.famcover-*`: the retired looks' own title pages (pages/cover.html).
# - `.daily-11` to `.daily-17` and `.d11-*` to `.d17-*`: the retired looks'
#   daily covers. 11 and 12 read the roles where a colour was a token or a
#   role already; their slate and sage greys stay.
# - `.fc02-*` to `.fc10-*`: the parts inside those `.famcover-NN` title pages
#   (Botanical's book, School notebook's red holes and blue rules, Swiss
#   grid's red, Keepsake's gold frame). pages/cover.html reaches them only
#   for a retired base look: a layout (`02a`, `06b`) takes the `look.layout`
#   branch first.
RETIRED = re.compile(
    r"\.design-(0[345789]|10|1[34567])\b|\.famcover-|\.daily-1[1-7]\b|\.d1[1-7]-|\.fc(0[2-9]|10)-")

# The budget donut (pages/budget.html `.pie`): a chart needs one colour per
# category, so its rule may keep a colour. Today the template sets each arc's
# stroke from the palette (`p[colour]`) and the rule holds none.
CHART = re.compile(r"\.pie\b")

# looks.css look art: colours a look keeps as its own that are not tokens
# (Bauhaus butter, Almanac gold, the Terracotta sun; _config/design-system.md,
# "Colour roles", exceptions). Only these custom properties may be a hex.
LOOK_ART = ("--gold", "--gold-lt", "--butter", "--sun")

# The layout kit's colour tokens: defaults only, each a var() of a token or role.
LX_COLOURS = ("--lx-ink", "--lx-line", "--lx-frame", "--lx-cal-line", "--lx-mark",
              "--lx-mark-ink", "--lx-paper")

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
NEUTRAL_CHROMA = 6.0


def rules(name: str) -> list[tuple[str, str, str]]:
    """(file, selector, declarations) for every rule in a stylesheet."""
    text = (STATIC_DIR / name).read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return [(name, sel.strip(), body) for sel, body in RULE.findall(text)]


def declarations(body: str) -> list[tuple[str, str]]:
    out = []
    for part in body.split(";"):
        if ":" in part:
            prop, value = part.split(":", 1)
            out.append((prop.strip(), value.strip()))
    return out


def chroma(hex_colour: str) -> float:
    digits = hex_colour.lstrip("#")
    if len(digits) in (4, 8):          # drop alpha
        digits = digits[:3] if len(digits) == 4 else digits[:6]
    _, a, b = colours._lab("#" + digits)
    return math.hypot(a, b)


def retired(selector: str) -> bool:
    return all(RETIRED.search(part) for part in selector.split(","))


ALL_RULES = [rule for name in FILES for rule in rules(name)]


def test_the_stylesheets_parse_to_rules():
    assert len(ALL_RULES) > 1000
    assert any(sel == ":root" for _, sel, _ in ALL_RULES)


def test_only_root_declares_tokens_and_roles():
    """No body-class rule redefines a palette token or a colour role: a theme
    on :root reaches every var() in the page (the retired looks aside)."""
    bad = []
    for name, selector, body in ALL_RULES:
        if selector == ":root" or retired(selector):
            continue
        for prop, value in declarations(body):
            if prop in TOKENS or prop in ROLE_PROPS:
                bad.append(f"{name}: {selector} {{ {prop}: {value} }}")
    assert bad == []


def allowed(name: str, selector: str, prop: str) -> bool:
    """A rule that may keep a colour of its own, and why (see the lists above)."""
    if retired(selector):                                 # retired looks' CSS
        return True
    if name == "looks.css" and prop in LOOK_ART:          # look art tokens
        return True
    if all(CHART.search(part) for part in selector.split(",")):  # the donut
        return True
    return False


def fixed_colours(scoped_only: bool = False) -> list[str]:
    """Every chromatic hex (Lab chroma 6 or more; a neutral white, paper or
    grey may stay a literal) in a rule outside `:root` that is not allowed."""
    bad = []
    for name, selector, body in ALL_RULES:
        if selector == ":root" or (scoped_only and not SCOPED.search(selector)):
            continue
        for prop, value in declarations(body):
            if allowed(name, selector, prop):
                continue
            for hex_colour in HEX.findall(value):
                if chroma(hex_colour) >= NEUTRAL_CHROMA:
                    bad.append(f"{name}: {selector} {{ {prop}: {value} }}")
    return bad


def test_design_scoped_rules_print_no_fixed_colour():
    """Step 1: the design-scoped chrome reads tokens and roles."""
    assert fixed_colours(scoped_only=True) == []


def test_no_rule_outside_root_prints_a_fixed_colour():
    """Step 2: the shared chrome too. The meta strips, the table and calendar
    hairlines, the write-on lines, the check boxes and the day pill wash read
    `--c-frame`, `--c-line` and a wash of `--c-structure`, so every design
    and every theme colours them; a fixed colour cannot be reached by a theme
    and looked wrong on the black-and-white and Deco designs."""
    assert fixed_colours() == []


def test_the_allow_lists_name_only_what_they_say():
    """Each allow-list entry matches what its reason describes."""
    assert allowed("planner.css", ".famcover-03 .fc03-book", "color")
    assert allowed("planner.css", ".fc06-holes i", "box-shadow")
    assert allowed("looks.css", ".design-bauhaus", "--butter")
    assert not allowed("planner.css", ".design-bauhaus", "--butter")
    assert allowed("planner.css", ".pie circle", "stroke")
    assert not allowed("planner.css", ".pie-key, .card", "color")
    assert not allowed("planner.css", ".famtime-meta", "border")
    assert not allowed("planner.css", ".fc-fam", "color")


def test_layout_kit_colour_tokens_read_only_vars():
    """--lx-* colours are var(--token) or var(--c-role), never a literal, and
    no design sets them: a design sets only the shape tokens."""
    seen = []
    for name, selector, body in ALL_RULES:
        for prop, value in declarations(body):
            if prop in LX_COLOURS:
                seen.append((selector, prop, value))
                assert re.fullmatch(r"var\(--[\w-]+\)", value), f"{name}: {selector} {{ {prop}: {value} }}"
                assert not SCOPED.search(selector.replace(".lx", "").replace(".layout", "")), \
                    f"{name}: {selector} sets {prop}"
    assert {prop for _, prop, _ in seen} == set(LX_COLOURS)
    assert {sel for sel, _, _ in seen} == {".page.lx", ".layout .page"}


@pytest.mark.parametrize("family", ["02", "06", "11", "12"])
def test_layout_families_have_no_token_block(family):
    assert not any(sel == f".design-{family}" for _, sel, _ in ALL_RULES)


def test_retired_allow_list_is_only_the_retired_looks():
    """The allow-list names nothing offered in the picker."""
    from familyplanner import designs
    for design in designs.names():
        base = designs.parts(design)["base"]
        assert not retired(f".design-{base}"), design
    assert retired(".design-03 .page") and retired(".d11-rule") and retired(".famcover-07 .x")
    assert not retired(".design-02 .card, .design-03 .card")
    assert Path(STATIC_DIR / "planner.css").is_file()
