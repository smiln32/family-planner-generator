"""Command line entry point: build, preview, months, fonts, pages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, config, designs, render, themes, typefaces
from .config import Config, ConfigError
from .render import RenderError

DEFAULT_CONFIG_PATH = Path("family.yaml")


def _resolve_config(args: argparse.Namespace) -> Config:
    """Load the config file if one was named or family.yaml happens to exist."""
    path: Path | None
    if args.config:
        path = Path(args.config)
    elif DEFAULT_CONFIG_PATH.exists():
        path = DEFAULT_CONFIG_PATH
    else:
        path = None

    cfg = config.load(path)

    # Command-line flags win over the file, so one config can serve many years.
    if getattr(args, "year", None):
        cfg.year = args.year
    if getattr(args, "family_name", None):
        cfg.family_name = args.family_name
    if getattr(args, "undated", False):
        cfg.dated_months = False
    if getattr(args, "linked", False):
        cfg.linked = True
        # The contents page is only useful when the tabs are tappable.
        if "index" not in cfg.pages:
            cfg.pages = ["index", *cfg.pages]
    if getattr(args, "only", None):
        cfg.pages = [p.strip() for p in args.only.split(",") if p.strip()]
    if getattr(args, "fonts", None):
        try:
            cfg.faces = typefaces.resolve(args.fonts)
        except KeyError as exc:
            raise ConfigError(str(exc).strip("\"'")) from exc
    if getattr(args, "theme", None):
        try:
            preset = themes.resolve(args.theme)
        except KeyError as exc:
            raise ConfigError(str(exc).strip("\"'")) from exc
        cfg.theme = args.theme.lower()
        cfg.palette.update(preset)
        # A palette block in the config file still outranks the flag.
        if cfg.source is not None:
            import yaml
            own = (yaml.safe_load(cfg.source.read_text(encoding="utf-8")) or {})
            cfg.palette.update(config.sanitize_palette(own.get("palette")))
    if getattr(args, "design", None):
        try:
            cfg.design = designs.resolve(args.design)
        except KeyError as exc:
            raise ConfigError(str(exc).strip("\"'")) from exc
    return config.validate(cfg)


def _page_label(index: int, total: int, page: render.Page) -> str:
    return f"  [{index:>2}/{total}] {page.title}"


def cmd_build(args: argparse.Namespace) -> int:
    cfg = _resolve_config(args)
    pages = render.plan_pages(cfg)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Family Success Planner {cfg.year}"
          + (f" - {cfg.family_name}" if cfg.family_name else ""))
    if cfg.source:
        print(f"config: {cfg.source}")
    print(f"{len(pages)} pages:")
    for i, page in enumerate(pages, start=1):
        print(_page_label(i, len(pages), page))

    html = render.render_html(cfg, pages)
    html_path = config.output_path(out_dir, cfg.stem, ".html")
    html_path.write_text(html, encoding="utf-8")
    print(f"\n  html -> {html_path}")

    if args.html_only:
        print("\nStopped after HTML (--html-only). Open it in a browser to check the layout.")
        return 0

    browser = render.find_browser(args.browser)
    print(f"  using {browser.name} for printing")

    pdf_path = config.output_path(out_dir, cfg.stem, ".pdf")
    render.html_to_pdf(html_path, pdf_path, browser)
    size_mb = pdf_path.stat().st_size / 1_048_576
    print(f"  pdf  -> {pdf_path}  ({len(pages)} pages, {size_mb:.1f} MB)")

    if args.png:
        _write_pngs(cfg, pages, out_dir, browser, args.dpi)

    print("\nDone. Print at 100% / 'Actual size' - do not let the printer scale to fit.")
    return 0


def _write_pngs(cfg: Config, pages: list[render.Page], out_dir: Path,
                browser: Path, dpi: int) -> None:
    """One PNG per page, rendered individually so each is exactly one sheet."""
    png_dir = out_dir / "png"
    png_dir.mkdir(parents=True, exist_ok=True)

    # Clear PNGs from a previous run so a shorter book does not leave orphans
    # behind that look like part of the current one.
    wanted = {f"{i:02d}-{page.slug}.png" for i, page in enumerate(pages, start=1)}
    for stale in png_dir.glob("*.png"):
        if stale.name not in wanted:
            stale.unlink()

    width_in, height_in = cfg.page_inches
    css_w, css_h = round(width_in * 96), round(height_in * 96)
    scale = dpi / 96
    print(f"  png  -> {png_dir}  ({dpi} dpi, {round(width_in*dpi)}x{round(height_in*dpi)} px)")

    for index, page in enumerate(pages, start=1):
        single = render.render_html(cfg, [page], standalone=True, nav_pages=pages)
        tmp_html = png_dir / f".{index:02d}-{page.slug}.html"
        tmp_html.write_text(single, encoding="utf-8")
        try:
            render.html_to_png(
                tmp_html, png_dir / f"{index:02d}-{page.slug}.png",
                browser, css_w, css_h, scale,
            )
        finally:
            tmp_html.unlink(missing_ok=True)
        print(f"    {index:>2}/{len(pages)} {page.slug}.png")


def cmd_pages(args: argparse.Namespace) -> int:
    cfg = _resolve_config(args)
    pages = render.plan_pages(cfg)
    print(f"{len(pages)} pages for {cfg.year}:")
    for i, page in enumerate(pages, start=1):
        print(f"  {i:>2}. {page.slug:<22} {page.title}")
    return 0


def cmd_months(args: argparse.Namespace) -> int:
    cfg = _resolve_config(args)
    print(f"Month styling for {cfg.year} "
          f"({'dated' if cfg.dated_months else 'undated'} grids):\n")
    print(f"  {'#':<3} {'MONTH':<10} {'ACCENT':<8} {'MOTIF':<10} TAGLINE")
    for i, month in enumerate(cfg.months, start=1):
        print(f"  {i:<3} {month['name']:<10} {month['accent']:<8} "
              f"{month['motif']:<10} {month['tagline']}")
    print("\nOverride any of these in the `months:` block of your config.")
    return 0


def cmd_themes(args: argparse.Namespace) -> int:
    base = config.DEFAULT_PALETTE
    swatch_order = ["navy", "teal", "pink", "orange", "green", "purple", "blue"]
    print("Built-in colour presets:")
    print()
    for name in themes.names():
        palette = dict(base)
        palette.update(themes.resolve(name))
        swatches = "  ".join(palette[k] for k in swatch_order)
        print(f"  {name:<9} {swatches}")
    print()
    print("Use one with:  python planner.py build --theme pastel")
    print("Or set `theme: pastel` in your config. Your own `palette:` block")
    print("still overrides individual colours on top of the theme.")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path)
    if target.exists() and not args.force:
        print(f"{target} already exists (use --force to overwrite)", file=sys.stderr)
        return 1
    example = Path(__file__).parent.parent / "config.example.yaml"
    target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {target}. Edit it, then run:  python planner.py build")
    return 0


def cmd_ui(args: argparse.Namespace) -> int:
    from .server import serve
    cfg = _resolve_config(args)
    return serve(cfg, Path(args.out), port=args.port, open_browser=not args.no_open)


def cmd_typefaces(args: argparse.Namespace) -> int:
    print("Built-in typeface sets:")
    print()
    print(f"  {'':<20} {'DISPLAY':<24} {'SCRIPT':<22} BODY")
    for name in typefaces.names():
        faces = typefaces.resolve(name)
        print(f"  {name:<20} {faces.display:<24} {faces.script:<22} {faces.body}")
    print()
    print("Use one with:  python planner.py build --fonts italics")
    print("Or name any Google Fonts families yourself in your config:")
    print("    fonts:")
    print("      display: Open Sans")
    print("      script: Courgette")
    print("      body: Oxygen")
    print("Then run `python planner.py fonts` to download them.")
    return 0


def cmd_fonts(args: argparse.Namespace) -> int:
    from .fonts import fetch_fonts
    dest = Path(__file__).parent / "static" / "fonts"
    if getattr(args, "all", False):
        worst = 0
        for name in typefaces.names():
            worst = max(worst, fetch_fonts(dest, typefaces.resolve(name), force=args.force))
            print()
        return worst
    cfg = _resolve_config(args)
    return fetch_fonts(dest, cfg.faces, force=args.force)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="planner.py",
        description="Generate printable Family Success Planner pages.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def shared(p: argparse.ArgumentParser) -> None:
        p.add_argument("-c", "--config", metavar="FILE",
                       help="YAML config (default: ./family.yaml if present)")
        p.add_argument("-y", "--year", type=int, help="override the planner year")
        p.add_argument("-n", "--family-name", metavar="NAME",
                       help="family name for the cover and filename")
        p.add_argument("--undated", action="store_true",
                       help="print blank month grids instead of real dates")
        p.add_argument("--linked", action="store_true",
                       help="add tab-rail navigation and an index (digital edition)")
        p.add_argument("--only", metavar="LIST",
                       help="comma-separated page names to build (see `pages`)")
        p.add_argument("--theme", metavar="NAME",
                       help="colour preset: " + ", ".join(themes.names()))
        p.add_argument("--fonts", metavar="NAME",
                       help="typeface set: " + ", ".join(typefaces.names()))
        p.add_argument("--design", metavar="NAME",
                       help="page look: " + ", ".join(designs.names()))

    b = sub.add_parser("build", help="render the planner to PDF")
    shared(b)
    b.add_argument("-o", "--out", default="out", help="output directory (default: out)")
    b.add_argument("--png", action="store_true", help="also write one PNG per page")
    b.add_argument("--dpi", type=int, default=300, help="PNG resolution (default: 300)")
    b.add_argument("--html-only", action="store_true", help="stop after writing HTML")
    b.add_argument("--browser", metavar="PATH", help="path to Chrome/Edge/Chromium")
    b.set_defaults(func=cmd_build)

    u = sub.add_parser("ui", help="open the visual preview and build interface")
    shared(u)
    u.add_argument("-o", "--out", default="out", help="output directory (default: out)")
    u.add_argument("--port", type=int, default=8733, help="port (default: 8733)")
    u.add_argument("--no-open", action="store_true", help="do not open a browser")
    u.set_defaults(func=cmd_ui)

    p = sub.add_parser("pages", help="list the pages that would be built")
    shared(p)
    p.set_defaults(func=cmd_pages)

    m = sub.add_parser("months", help="show per-month colours, motifs and taglines")
    shared(m)
    m.set_defaults(func=cmd_months)

    t = sub.add_parser("themes", help="list the built-in colour presets")
    t.set_defaults(func=cmd_themes)

    tf = sub.add_parser("typefaces", help="list the built-in typeface sets")
    tf.set_defaults(func=cmd_typefaces)

    i = sub.add_parser("init", help="write a starter config file")
    i.add_argument("path", nargs="?", default="family.yaml")
    i.add_argument("--force", action="store_true")
    i.set_defaults(func=cmd_init)

    f = sub.add_parser("fonts", help="download the typefaces for best fidelity")
    shared(f)
    f.add_argument("--force", action="store_true", help="re-download existing fonts")
    f.add_argument("--all", action="store_true", help="download every built-in typeface set")
    f.set_defaults(func=cmd_fonts)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, RenderError) as exc:
        print(f"\nerror: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        # Unwritable -o, a file where a folder should be, a locked PDF.
        where = f": {exc.filename}" if exc.filename else ""
        print(f"\nerror: {exc.strerror or exc}{where}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
