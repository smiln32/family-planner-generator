"""A local preview UI for the planner.

Serves a single-page app on 127.0.0.1 that renders real pages through the
same code path as `planner.py build`, so what you see is what prints.

    python planner.py ui

Bound to loopback only. It runs builds on request, so it is a local tool, not
something to expose on a network.
"""

from __future__ import annotations

import errno
import json
import threading
import webbrowser
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import config, designs, render, themes, typefaces
from .config import Config, ConfigError
from .render import RenderError

UI_DIR = Path(__file__).parent / "static" / "ui"
FONT_DIR = Path(__file__).parent / "static" / "fonts"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".woff2": "font/woff2",
    ".svg": "image/svg+xml",
}

MAX_BODY = 1 << 20  # 1 MB is far more than any config payload needs.


def _config_from(payload: dict, base: Config) -> Config:
    """Build a Config from the UI's form state, on top of the loaded defaults."""
    cfg = replace(base)

    if "year" in payload:
        cfg.year = payload["year"]
    if "family_name" in payload:
        cfg.family_name = str(payload["family_name"])
    if "week_starts" in payload:
        cfg.week_starts = str(payload["week_starts"])
    if "dated_months" in payload:
        cfg.dated_months = bool(payload["dated_months"])
    if "cover_year" in payload:
        cfg.cover_year = str(payload["cover_year"])
    if "cover_text" in payload:
        cfg.cover_text = str(payload["cover_text"])
    if "page_size" in payload:
        cfg.page_size = config.normalize_page_size(payload["page_size"])
    if "members" in payload:
        cfg.members = config.check_str_list(payload["members"], "members")
    if "pages" in payload and payload["pages"]:
        cfg.pages = config.check_str_list(payload["pages"], "pages")

    cfg.theme = config.check_theme(payload.get("theme"))
    palette = config.theme_palette(cfg.theme)
    palette.update(config.sanitize_palette(payload.get("palette")))
    cfg.palette = palette

    cfg.faces = config.check_fonts(payload.get("fonts") or typefaces.DEFAULT_SET)
    cfg.design = config.check_design(payload.get("design") or designs.DEFAULT_DESIGN)
    cfg.type_size = config.check_type_size(payload.get("type_size"))
    # Same rules as `planner.py build`, so the UI cannot reach the renderer
    # with a value the command line would have refused.
    return config.validate(cfg)


def _fonts_for_save(value) -> str | dict:
    """Preserve a custom {display, script, body} trio; otherwise a preset name."""
    if isinstance(value, dict):
        faces = config.check_fonts(value)
        return {"display": faces.display, "script": faces.script, "body": faces.body}
    return str(value or typefaces.DEFAULT_SET)


class Handler(BaseHTTPRequestHandler):
    """Routes: static UI assets, fonts, and a small JSON API."""

    server_version = "FamilyPlanner"
    base_config: Config
    out_dir: Path

    def log_message(self, fmt, *args):  # noqa: D102 - keep the console quiet
        pass

    # --- plumbing ---------------------------------------------------------

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, status: int = 200) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def _static(self, directory: Path, name: str) -> None:
        target = (directory / name).resolve()
        if not target.is_file() or directory.resolve() not in target.parents:
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        ctype = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    # --- routes -----------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._static(UI_DIR, "index.html")
        elif path.startswith("/ui/"):
            self._static(UI_DIR, path[len("/ui/"):])
        elif path.startswith("/fonts/"):
            self._static(FONT_DIR, path[len("/fonts/"):])
        elif path == "/api/state":
            self._json(self._state())
        else:
            self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/preview":
                self._preview(payload)
            elif path == "/api/build":
                self._build(payload)
            elif path == "/api/export":
                self._export(payload)
            elif path == "/api/import":
                self._import(payload)
            elif path == "/api/open":
                self._open(payload)
            else:
                self._send(404, b"not found", "text/plain; charset=utf-8")
        except (ConfigError, RenderError, KeyError, ValueError) as exc:
            self._json({"error": str(exc)}, status=400)
        except Exception as exc:  # surface anything else to the UI, not the console
            self._json({"error": f"{type(exc).__name__}: {exc}"}, status=500)

    # --- API implementations ---------------------------------------------

    def _state(self) -> dict:
        cfg = self.base_config
        catalogue = render.discover_pages()
        return {
            "config": {
                "year": cfg.year,
                "family_name": cfg.family_name,
                "week_starts": cfg.week_starts,
                "dated_months": cfg.dated_months,
                "cover_year": cfg.cover_year,
                "cover_text": cfg.cover_text,
                "page_size": cfg.page_size,
                "members": cfg.members,
                "pages": cfg.pages,
                "theme": cfg.theme,
                "fonts": cfg.faces.preset or {
                    "display": cfg.faces.display,
                    "script": cfg.faces.script,
                    "body": cfg.faces.body,
                },
                "design": cfg.design,
                "type_size": cfg.type_size,
            },
            "themes": [
                {"name": name,
                 "swatches": [dict(config.DEFAULT_PALETTE, **themes.resolve(name))[k]
                              for k in ("navy", "teal", "pink", "orange", "green", "purple")]}
                for name in themes.names()
            ],
            "typefaces": [
                {"name": name,
                 "display": typefaces.resolve(name).display,
                 "script": typefaces.resolve(name).script,
                 "body": typefaces.resolve(name).body}
                for name in typefaces.names()
            ],
            "designs": [
                {"id": name, **designs.PRESETS[name]}
                for name in designs.names()
            ],
            "typeSizeRange": {
                key: {"min": lo, "max": hi, "value": designs.DEFAULT_TYPE_SIZE[key]}
                for key, (lo, hi) in designs.TYPE_SIZE_RANGE.items()
            },
            "catalogue": [{"slug": slug, "title": title}
                          for slug, title in catalogue.items()],
            "months": [m["name"] for m in cfg.months],
            "defaultPages": config.DEFAULT_PAGES,
            "pageSizes": [
                {"id": name, "label": config.PAGE_SIZE_LABELS[name],
                 "width": size[0], "height": size[1]}
                for name, size in config.PAGE_SIZES.items()
            ],
        }

    def _preview(self, payload: dict) -> None:
        cfg = _config_from(payload, self.base_config)
        wanted = payload.get("preview")
        pages = render.plan_pages(cfg)
        if wanted:
            pages = [p for p in pages if p.slug == wanted] or pages[:1]
        else:
            pages = pages[:1]
        html = render.render_html(cfg, pages, standalone=True, font_base="/fonts",
                                  nav_pages=render.plan_pages(cfg))
        self._json({"html": html, "slug": pages[0].slug, "title": pages[0].title})

    def _build(self, payload: dict) -> None:
        cfg = _config_from(payload, self.base_config)
        pages = render.plan_pages(cfg)
        out = self.out_dir
        out.mkdir(parents=True, exist_ok=True)

        html_path = config.output_path(out, cfg.stem, ".html")
        html_path.write_text(render.render_html(cfg, pages), encoding="utf-8")

        pdf_path = config.output_path(out, cfg.stem, ".pdf")
        render.html_to_pdf(html_path, pdf_path, render.find_browser())
        self._json({
            "pdf": str(pdf_path.resolve()),
            "pages": len(pages),
            "megabytes": round(pdf_path.stat().st_size / 1_048_576, 1),
        })

    def _plan_fields(self, payload: dict) -> dict:
        return {
            "year": config.check_year(payload.get("year", self.base_config.year)),
            "family_name": str(payload.get("family_name") or ""),
            "week_starts": config.check_week_starts(payload.get("week_starts")),
            "dated_months": bool(payload.get("dated_months", True)),
            "cover_year": config.check_cover_year(payload.get("cover_year")),
            "cover_text": str(payload.get("cover_text") or ""),
            "page_size": config.normalize_page_size(payload.get("page_size", "letter")),
            "members": config.check_str_list(payload.get("members"), "members"),
            "theme": config.check_theme(payload.get("theme")),
            "fonts": _fonts_for_save(payload.get("fonts")),
            "design": config.check_design(payload.get("design") or designs.DEFAULT_DESIGN),
            "type_size": config.check_type_size(payload.get("type_size")),
            "pages": config.check_str_list(payload.get("pages"), "pages"),
        }

    def _export(self, payload: dict) -> None:
        body = self._plan_fields(payload)
        self._json({
            "markdown": config.render_plan_markdown(body),
            "filename": config.plan_filename(body),
        })

    def _import(self, payload: dict) -> None:
        loaded = config.parse_plan_text(str(payload.get("text") or ""))
        seed = {
            "year": config.DEFAULT_CONFIG["year"],
            "family_name": "",
            "week_starts": "sunday",
            "dated_months": True,
            "cover_year": "auto",
            "cover_text": "",
            "page_size": "letter",
            "members": [],
            "theme": themes.DEFAULT_THEME,
            "fonts": typefaces.DEFAULT_SET,
            "design": designs.DEFAULT_DESIGN,
            "type_size": {},
            "pages": list(config.DEFAULT_PAGES),
        }
        self._json({"config": self._plan_fields({**seed, **loaded})})

    def _open(self, payload: dict) -> None:
        """Open a PDF this session wrote, in the computer's usual reader."""
        raw = Path(str(payload.get("path") or ""))
        if not raw.parts:
            raise ValueError("Make a PDF first, then open it from here.")
        target = raw.resolve()
        out = self.out_dir.resolve()
        if target.parent != out:
            raise ValueError("Could not open that file. Make a PDF again, then open it from here.")
        if not target.is_file() or target.suffix.lower() != ".pdf":
            raise ValueError("The PDF is missing. Make a PDF again.")
        webbrowser.open(target.as_uri())
        self._json({"opened": str(target)})


def serve(cfg: Config, out_dir: Path, port: int = 8733, open_browser: bool = True) -> int:
    """Run the preview UI until interrupted. Returns a process exit code."""
    Handler.base_config = cfg
    Handler.out_dir = out_dir

    url = f"http://127.0.0.1:{port}/"
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as exc:
        busy = (
            getattr(exc, "winerror", None) == 10048
            or getattr(exc, "errno", None) in (errno.EADDRINUSE, 48, 98)
            or "already in use" in str(exc).lower()
        )
        if busy:
            print("The planner is already open.")
            print(f"  {url}")
            if open_browser:
                webbrowser.open(url)
            return 0
        print(f"Could not start the planner on port {port}: {exc}")
        print("Close other copies, or start again with a different port.")
        return 1

    url = f"http://127.0.0.1:{httpd.server_port}/"
    print("Family Success Planner is open in your browser.")
    print(f"  {url}")
    print("  Keep this window open. Close it when you are finished.")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0
