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

# Names this server answers to. Anything else in Host is a DNS-rebinding
# attempt; anything else in Origin is another website posting to us.
LOCAL_HOSTS = ("127.0.0.1", "localhost")


class RequestError(Exception):
    """A request the server cannot read. Answered with `status` and a plain message."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


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
    # Not on the form, but carried in plan files; the editor passes them back.
    if "title" in payload:
        cfg.title = str(payload["title"] or "")
    if "subtitle" in payload:
        cfg.subtitle = str(payload["subtitle"] or "")
    if "linked" in payload:
        cfg.linked = bool(payload["linked"])
    if "months" in payload:
        cfg.months = config.merge_months(payload["months"])

    cfg.theme = config.check_theme(payload.get("theme"))
    # The UI sends only the colours someone replaced; the look or theme
    # supplies the rest at render time (config.effective_palette).
    replaced = config.sanitize_palette(payload.get("palette"))
    palette = config.theme_palette(cfg.theme)
    palette.update(replaced)
    cfg.palette = palette
    cfg.palette_set = replaced

    cfg.faces = config.check_fonts(payload.get("fonts") or typefaces.DEFAULT_SET)
    cfg.design = config.check_design(payload.get("design") or designs.DEFAULT_DESIGN)
    cfg.type_size = config.check_type_size(payload.get("type_size"))
    # Same rules as `planner.py build`, so the UI cannot reach the renderer
    # with a value the command line would have refused.
    return config.validate(cfg)


def _fonts_for_save(value) -> str | dict:
    """Preserve a custom {display, script, body} trio; otherwise a preset name.

    Both go through the same check as everywhere else, so a bad set name
    fails on export instead of writing a plan that will not open.
    """
    faces = config.check_fonts(value or typefaces.DEFAULT_SET)
    if isinstance(value, dict):
        return {"display": faces.display, "script": faces.script, "body": faces.body}
    return faces.preset


def _months_for_save(value) -> list[dict]:
    """Only what differs from the built-in months, so a plan stays short.

    An empty mapping keeps a month as it is; trailing ones are dropped.
    """
    months = config.merge_months(value)
    changes = [
        {key: text for key, text in month.items() if default.get(key) != text}
        for month, default in zip(months, config.DEFAULT_MONTHS)
    ]
    while changes and not changes[-1]:
        changes.pop()
    return changes


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

    def _content_length(self) -> int | None:
        """The Content-Length header as a whole number, or None if it is not one."""
        raw = (self.headers.get("Content-Length") or "0").strip()
        if not raw.isdigit():
            return None
        return int(raw)

    def _read_json(self) -> dict:
        """The request body as a JSON object. Raises RequestError otherwise."""
        length = self._content_length()
        if length is None:
            raise RequestError(400, "The request was not sent properly. Please try again.")
        if length > MAX_BODY:
            # Not read: a body this big is not from the planner's own page.
            raise RequestError(413, "That request is too large.")
        if length == 0:
            return {}
        try:
            payload = json.loads(self.rfile.read(length))
        except ValueError as exc:  # bad JSON, or bytes that are not text
            raise RequestError(400, "The request was not valid JSON.") from exc
        if not isinstance(payload, dict):
            raise RequestError(400, "The request must be a set of settings, not a list or a value.")
        return payload

    def _reject(self) -> None:
        """Answer 403, reading the body first so the reply gets through.

        Closing a socket with unread bytes makes Windows send a reset, and a
        client that sees the reset drops the reply it was about to read. An
        oversized body, or one with a length that is not a number, is left
        alone; that sender gets the reset on purpose.
        """
        length = self._content_length()
        if length is not None and 0 < length <= MAX_BODY:
            self.rfile.read(length)
        self._send(403, b"forbidden", "text/plain; charset=utf-8")

    def _static(self, directory: Path, name: str) -> None:
        target = (directory / name).resolve()
        if not target.is_file() or directory.resolve() not in target.parents:
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        ctype = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), ctype)

    def _local_request(self, post: bool) -> bool:
        """True when the request came from this app's own page.

        Browsers let any website send a simple POST to 127.0.0.1, so a page
        open in another tab could otherwise start builds or open files. The
        Host check stops DNS rebinding; the Origin check stops cross-site
        posts; requiring JSON forces a CORS preflight we never answer.
        """
        port = self.server.server_address[1]
        allowed = {f"{host}:{port}" for host in LOCAL_HOSTS}
        if (self.headers.get("Host") or "").lower() not in allowed:
            return False
        if not post:
            return True
        origin = (self.headers.get("Origin") or "").lower()
        if origin and origin not in {f"http://{a}" for a in allowed}:
            return False
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        return ctype == "application/json"

    # --- routes -----------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if not self._local_request(post=False):
            self._reject()
            return
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
        if not self._local_request(post=True):
            self._reject()
            return
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
        except RequestError as exc:
            self._json({"error": exc.message}, status=exc.status)
            return
        try:
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
                "title": cfg.title,
                "subtitle": cfg.subtitle,
                "linked": cfg.linked,
                "months": _months_for_save(cfg.months),
                "palette": config.palette_overrides(
                    cfg.theme, config.effective_palette(cfg), cfg.design),
            },
            "paletteRoles": [
                {"id": key, "label": label} for key, label in config.PALETTE_ROLES
            ],
            "themePalettes": {
                name: config.theme_palette(name) for name in themes.names()
            },
            "themes": [
                {"name": name,
                 "swatches": [config.theme_palette(name)[k]
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
                {"id": name, **designs.PRESETS[name],
                 # A layout book brings its own sheets and typeface set.
                 "adds": designs.LAYOUT_PAGES if designs.parts(name)["layout"] else [],
                 "fonts": designs.look_fonts(name),
                 # The look's own colours, or null when the theme decides them.
                 "palette": designs.look_palette(name) or None}
                for name in designs.names()
            ],
            # The design open now may be a retired look the picker no longer
            # lists; the colour panel still needs to know who owns its colours.
            "currentDesign": {
                "id": cfg.design,
                "label": {**designs.LEGACY, **designs.PRESETS}
                         .get(cfg.design, {}).get("label", cfg.design),
                "palette": designs.look_palette(cfg.design) or None,
            },
            "typeSizeRange": {
                key: {"min": lo, "max": hi, "value": designs.DEFAULT_TYPE_SIZE[key]}
                for key, (lo, hi) in designs.TYPE_SIZE_RANGE.items()
            },
            "catalogue": [{"slug": slug, "title": title}
                          for slug, title in catalogue.items()],
            "months": [m["name"] for m in cfg.months],
            "defaultPages": config.DEFAULT_PAGES,
            # What "Start over" puts back for the settings that are not on the form.
            "factory": {"title": config.DEFAULT_CONFIG["title"],
                        "subtitle": config.DEFAULT_CONFIG["subtitle"]},
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
        base = self.base_config
        body = {
            "year": config.check_year(payload.get("year", base.year)),
            "family_name": config.check_field_text("family_name", payload.get("family_name")),
            "week_starts": config.check_week_starts(payload.get("week_starts")),
            "dated_months": bool(payload.get("dated_months", True)),
            "cover_year": config.check_cover_year(payload.get("cover_year")),
            "cover_text": config.check_field_text("cover_text", payload.get("cover_text")),
            "page_size": config.normalize_page_size(payload.get("page_size", "letter")),
            "members": config.check_members(payload.get("members")),
            "theme": config.check_theme(payload.get("theme")),
            "fonts": _fonts_for_save(payload.get("fonts")),
            "design": config.check_design(payload.get("design") or designs.DEFAULT_DESIGN),
            "type_size": config.check_type_size(payload.get("type_size")),
            "pages": config.check_str_list(payload.get("pages"), "pages"),
            "title": config.check_field_text("title", payload.get("title", base.title)),
            "subtitle": config.check_field_text("subtitle", payload.get("subtitle", base.subtitle)),
            "linked": bool(payload.get("linked", base.linked)),
            "months": _months_for_save(payload.get("months", base.months)),
        }
        body["palette"] = config.palette_overrides(
            body["theme"], payload.get("palette"), body["design"])
        # output_name is left out on purpose (see config.PLAN_OUTPUT_NAME_NOTE).
        return body

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
            "design": designs.DEFAULT_DESIGN,
            "type_size": {},
            "pages": list(config.DEFAULT_PAGES),
            "palette": {},
            "title": config.DEFAULT_CONFIG["title"],
            "subtitle": config.DEFAULT_CONFIG["subtitle"],
            "linked": False,
            "months": [],
        }
        merged = {**seed, **loaded}
        # A plan that names no lettering is set in its look's own typefaces.
        if not merged.get("fonts"):
            design = config.check_design(merged.get("design") or designs.DEFAULT_DESIGN)
            merged["fonts"] = designs.look_fonts(design) or typefaces.DEFAULT_SET
        self._json({"config": self._plan_fields(merged)})

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
