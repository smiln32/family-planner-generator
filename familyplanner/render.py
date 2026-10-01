"""Turn the page templates into HTML, then into a print-ready PDF and PNGs.

Rendering goes through a headless Chromium (Chrome, Edge or Brave - whichever
is installed). That buys real vector text in the PDF, correct web-font
rendering and CSS grid support, without asking anyone to install a print stack.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from calendar import monthrange
from dataclasses import dataclass, replace
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import escape

from . import calendars, config, designs
from .config import Config

TEMPLATE_DIR = Path(__file__).parent / "templates"

# SVG <text> cannot read CSS custom properties, so the chosen families are
# passed into the templates as plain stacks alongside the CSS variables.
STATIC_DIR = Path(__file__).parent / "static"

NEWLINE = chr(10)

# Checked in order; the first one that exists wins. CHROME_PATH overrides all.
BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
]


class RenderError(RuntimeError):
    """Raised when the browser step fails or no browser can be found."""


@dataclass(frozen=True)
class Page:
    """One rendered page: which template, what to call it, what it needs."""

    slug: str
    title: str
    template: str
    context: dict


def find_browser(explicit: str | None = None) -> Path:
    """Locate a Chromium-family browser to print with."""
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("CHROME_PATH"):
        candidates.append(os.environ["CHROME_PATH"])
    candidates.extend(BROWSER_CANDIDATES)

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    for name in ("chrome", "google-chrome", "chromium", "msedge", "brave"):
        found = shutil.which(name)
        if found:
            return Path(found)

    raise RenderError(
        "No Chromium-based browser found. Install Google Chrome or Microsoft "
        "Edge, or point CHROME_PATH at one:\n"
        r"  CHROME_PATH='C:\Program Files\Google\Chrome\Application\chrome.exe'"
    )


def build_environment() -> Environment:
    """Jinja env with StrictUndefined so a typo in a template fails loudly."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["month_grid"] = calendars.month_grid
    env.globals["compact_grid"] = calendars.compact_grid
    env.globals["day_names"] = calendars.day_names
    env.globals["day_initials"] = calendars.day_initials
    env.globals["range"] = range
    env.globals["month_days"] = lambda year, month: monthrange(year, month)[1]
    env.globals["abbr"] = lambda text, n=3: str(text)[:n]
    env.globals["looks"] = designs.LOOKS
    return env


# "months" is a keyword in the page list, not a template; monthly.html is
# rendered twelve times by it rather than standing alone as a page.
MONTHS_KEYWORD = "months"
NON_PAGE_TEMPLATES = {"monthly"}

# Optional first-line declaration: {# title: Weekly Gratitude Journal #}
TITLE_RE = re.compile(r"\{#\s*title:\s*(.+?)\s*#\}")


def discover_pages() -> dict[str, str]:
    """Map slug -> title for every template in templates/pages.

    Dropping a new .html file in that folder is all it takes to register a
    page; there is no list to keep in sync. A template may name itself with a
    `{# title: ... #}` comment on its first line, otherwise the filename is
    prettified into a title.
    """
    found: dict[str, str] = {}
    for path in sorted((TEMPLATE_DIR / "pages").glob("*.html")):
        slug = path.stem
        if slug in NON_PAGE_TEMPLATES or slug.startswith("_"):
            continue
        head = path.read_text(encoding="utf-8")[:400]
        match = TITLE_RE.search(head)
        found[slug] = match.group(1) if match else slug.replace("_", " ").title()
    return found


def plan_pages(cfg: Config) -> list[Page]:
    """Expand the configured page list into concrete pages, in order."""
    known = discover_pages()

    def monthly(index: int, month: dict) -> Page:
        return Page(
            slug=month["name"].lower(),
            title=f"{month['name']} Family Planner",
            template="pages/monthly.html",
            context={"month": month, "month_number": index},
        )

    # `pages` prints month slugs like "january", so accept them individually
    # as well as through the "months" keyword.
    by_month = {m["name"].lower(): (i, m) for i, m in enumerate(cfg.months, start=1)}

    names = list(cfg.pages)
    # A planner layout brings its weekly and daily sheets along, just before
    # the months, unless the page list already places one of them.
    if designs.parts(cfg.design)["layout"] and not set(designs.LAYOUT_PAGES) & set(names):
        at = names.index(MONTHS_KEYWORD) if MONTHS_KEYWORD in names else len(names)
        names[at:at] = designs.LAYOUT_PAGES

    pages: list[Page] = []
    for name in names:
        if name == MONTHS_KEYWORD:
            for index, month in enumerate(cfg.months, start=1):
                pages.append(monthly(index, month))
        elif name.lower() in by_month:
            pages.append(monthly(*by_month[name.lower()]))
        elif name in known:
            pages.append(Page(
                slug=name,
                title=known[name],
                template=f"pages/{name}.html",
                context={},
            ))
        else:
            raise RenderError(
                f"unknown page '{name}'. Valid pages: "
                + ", ".join(sorted(known) + [MONTHS_KEYWORD]
                            + [m["name"].lower() for m in cfg.months])
            )
    accents = ["teal", "pink", "orange", "green", "purple", "blue"]
    toc = [
        {"slug": page.slug, "title": page.title, "number": number,
         "accent": (page.context.get("month", {}).get("accent")
                    if page.template == "pages/monthly.html"
                    else accents[number % len(accents)])}
        for number, page in enumerate(pages, start=1)
    ]
    for index, page in enumerate(pages):
        if page.slug == "index":
            pages[index] = replace(page, context={"toc": toc})
    return pages


def render_html(cfg: Config, pages: list[Page], standalone: bool = False,
                font_base: str | None = None,
                nav_pages: list[Page] | None = None) -> str:
    """Render every page into one HTML document (the whole book, in order).

    `font_base` swaps the embedded file:// font URLs for a URL prefix. The
    preview server needs this because a page served over http:// is not
    allowed to load file:// resources.

    `nav_pages` is the whole book, used to build the tab rail. It matters when
    rendering a single sheet for a preview or a PNG: without it the rail would
    be built from that one page and the current month would fill the strip.
    """
    nav = nav_pages if nav_pages is not None else pages
    env = build_environment()
    look = designs.parts(cfg.design)
    # A layout book prints in its look's colours; see config.effective_palette.
    cfg = replace(cfg, palette=config.effective_palette(cfg))
    shell = env.get_template("book.html")
    page_template_cache: dict[str, object] = {}

    bodies = []
    for page in pages:
        template = page_template_cache.get(page.template)
        if template is None:
            template = env.get_template(page.template)
            page_template_cache[page.template] = template
        rendered = template.render(
            cfg=cfg, page=page, p=cfg.palette,
            script_stack=cfg.faces.stack("script"),
            body_stack=cfg.faces.stack("body"),
            look=look,
            **page.context,
        )
        bodies.append(_decorate(rendered, cfg, nav, page))

    width_in, height_in = cfg.page_inches
    return shell.render(
        cfg=cfg,
        look=look,
        pages=pages,
        bodies=bodies,
        css=(STATIC_DIR / "planner.css").read_text(encoding="utf-8")
        + NEWLINE + (STATIC_DIR / "looks.css").read_text(encoding="utf-8"),
        fonts_css=_fonts_css(cfg, font_base),
        font_display=cfg.faces.stack("display"),
        font_script=cfg.faces.stack("script"),
        font_body=cfg.faces.stack("body"),
        page_width_in=width_in,
        page_height_in=height_in,
        standalone=standalone,
    )


def _fonts_css(cfg: Config, font_base: str | None = None) -> str:
    """@font-face rules for whichever faces this build's typeface set needs.

    Missing files are simply skipped, so an unprovisioned checkout still
    renders using the fallback stacks declared in planner.css.
    """
    from .typefaces import slug

    font_dir = STATIC_DIR / "fonts"
    faces = []
    for family, weight in cfg.faces.wanted():
        path = font_dir / slug(family, weight)
        if not path.is_file():
            continue
        uri = f"{font_base}/{path.name}" if font_base else path.resolve().as_uri()
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url('{uri}') format('woff2');}}"
        )
    for family, weight in cfg.faces.wanted_italic():
        path = font_dir / slug(family, weight, italic=True)
        if not path.is_file():
            continue
        uri = f"{font_base}/{path.name}" if font_base else path.resolve().as_uri()
        faces.append(
            f"@font-face{{font-family:'{family}';font-style:italic;"
            f"font-weight:{weight};font-display:block;"
            f"src:url('{uri}') format('woff2');}}"
        )
    return NEWLINE.join(faces)


def _run_browser(browser: Path, args: list[str], what: str) -> None:
    """Invoke headless Chromium with a scratch profile and surface failures."""
    with tempfile.TemporaryDirectory(prefix="planner-profile-") as profile:
        cmd = [
            str(browser),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--allow-file-access-from-files",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=15000",
            f"--user-data-dir={profile}",
            *args,
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired as exc:
            raise RenderError(f"{what}: browser timed out after 300s") from exc
        except OSError as exc:
            raise RenderError(f"{what}: could not launch {browser}: {exc}") from exc

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[-1200:]
        raise RenderError(f"{what}: browser exited {proc.returncode}\n{detail}")


def html_to_pdf(html_path: Path, pdf_path: Path, browser: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_path.resolve()
    _run_browser(
        browser,
        [
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        what=f"writing {pdf_path.name}",
    )
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise RenderError(f"browser reported success but {pdf_path} is empty")


def html_to_png(html_path: Path, png_path: Path, browser: Path,
                width_px: int, height_px: int, scale: float) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path = png_path.resolve()
    _run_browser(
        browser,
        [
            "--hide-scrollbars",
            "--default-background-color=FFFFFFFF",
            f"--force-device-scale-factor={scale}",
            f"--window-size={width_px},{height_px}",
            f"--screenshot={png_path}",
            html_path.resolve().as_uri(),
        ],
        what=f"writing {png_path.name}",
    )
    if not png_path.is_file() or png_path.stat().st_size == 0:
        raise RenderError(f"browser reported success but {png_path} is empty")


# Every page template opens with <section class="page ...">, which the README
# documents as a rule. The digital edition uses that to add an anchor id and a
# tab rail centrally, so none of the page templates need to know about linking.
SECTION_RE = re.compile(r'(<section class="page\b[^"]*")')


def _tab_rail(cfg: Config, pages: list[Page], current: Page) -> str:
    """Vertical month tabs plus an index tab, for the linked edition."""
    months = [p for p in pages if p.template == "pages/monthly.html"]
    has_index = any(p.slug == "index" for p in pages)

    tabs = []
    if has_index:
        on = " on" if current.slug == "index" else ""
        tabs.append(
            f'<a class="tab tab-home{on}" href="#index" '
            f'style="--c:{escape(cfg.palette["navy"])}" aria-label="Contents">'
            f'<svg viewBox="0 0 24 24"><use href="#i-home"/></svg></a>'
        )
    for page in months:
        month = page.context["month"]
        on = " on" if page.slug == current.slug else ""
        tabs.append(
            f'<a class="tab{on}" href="#{escape(page.slug)}" '
            f'style="--c:{escape(cfg.palette[month["accent"]])}">'
            f'{escape(month["name"][:3].upper())}</a>'
        )
    if not tabs:
        return ""
    return '<nav class="tab-rail" aria-label="Planner sections">' + "".join(tabs) + "</nav>"


def _decorate(body: str, cfg: Config, pages: list[Page], page: Page) -> str:
    """Give a rendered page its anchor id, and the rail when linking is on."""
    body = SECTION_RE.sub(lambda m: m.group(1) + f' id="{escape(page.slug)}"', body, count=1)
    if not cfg.linked:
        return body
    rail = _tab_rail(cfg, pages, page)
    if not rail:
        return body
    # The body starts with the <section> tag, so the first ">" closes it.
    head, sep, tail = body.partition(">")
    return head + sep + rail + tail
