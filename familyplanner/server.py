"""A local preview UI for the planner.

Serves a single-page app on 127.0.0.1 that renders real pages through the
same code path as `planner.py build`, so what you see is what prints.

    python planner.py ui

Bound to loopback only. It runs builds on request, so it is a local tool, not
something to expose on a network.
"""

from __future__ import annotations

import json
import threading
import webbrowser
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import config, render, themes, typefaces
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
        cfg.year = int(payload["year"])
    if "family_name" in payload:
        cfg.family_name = str(payload["family_name"])
    if "week_starts" in payload:
        cfg.week_starts = str(payload["week_starts"])
    if "dated_months" in payload:
        cfg.dated_months = bool(payload["dated_months"])
    if "page_size" in payload:
        cfg.page_size = str(payload["page_size"])
    if "members" in payload:
        cfg.members = [str(m) for m in payload["members"]]
    if "pages" in payload and payload["pages"]:
        cfg.pages = [str(p) for p in payload["pages"]]

    palette = dict(config.DEFAULT_PALETTE)
    palette.update(themes.resolve(str(payload.get("theme") or "classic")))
    palette.update(payload.get("palette") or {})
    cfg.palette = palette
    cfg.theme = str(payload.get("theme") or "classic")

    cfg.faces = typefaces.resolve(payload.get("fonts") or "classic")
    return cfg


def _fonts_for_save(value) -> str | dict:
    """Preserve a custom {display, script, body} trio; otherwise a preset name."""
    if isinstance(value, dict):
        faces = typefaces.resolve(value)
        return {"display": faces.display, "script": faces.script, "body": faces.body}
    return str(value or "classic")


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
            elif path == "/api/save":
                self._save(payload)
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
                "page_size": cfg.page_size,
                "members": cfg.members,
                "pages": cfg.pages,
                "theme": cfg.theme,
                "fonts": cfg.faces.preset or {
                    "display": cfg.faces.display,
                    "script": cfg.faces.script,
                    "body": cfg.faces.body,
                },
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
            "catalogue": [{"slug": slug, "title": title}
                          for slug, title in catalogue.items()],
            "months": [m["name"] for m in cfg.months],
            "defaultPages": config.DEFAULT_PAGES,
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

        html_path = out / f"{cfg.stem}.html"
        html_path.write_text(render.render_html(cfg, pages), encoding="utf-8")

        pdf_path = out / f"{cfg.stem}.pdf"
        render.html_to_pdf(html_path, pdf_path, render.find_browser())
        self._json({
            "pdf": str(pdf_path.resolve()),
            "pages": len(pages),
            "megabytes": round(pdf_path.stat().st_size / 1_048_576, 1),
        })

    def _save(self, payload: dict) -> None:
        import yaml

        target = Path(payload.get("path") or "family.yaml")
        body = {
            "year": int(payload.get("year", self.base_config.year)),
            "family_name": str(payload.get("family_name", "")),
            "week_starts": str(payload.get("week_starts", "sunday")),
            "dated_months": bool(payload.get("dated_months", True)),
            "page_size": str(payload.get("page_size", "letter")),
            "members": [str(m) for m in payload.get("members", [])],
            "theme": str(payload.get("theme") or "classic"),
            "fonts": _fonts_for_save(payload.get("fonts")),
            "pages": [str(p) for p in payload.get("pages", [])],
        }
        target.write_text(
            "# Written by `planner.py ui`. Edit freely.\n"
            + yaml.safe_dump(body, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        self._json({"saved": str(target.resolve())})


def serve(cfg: Config, out_dir: Path, port: int = 8733, open_browser: bool = True) -> int:
    """Run the preview UI until interrupted. Returns a process exit code."""
    Handler.base_config = cfg
    Handler.out_dir = out_dir

    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    except OSError as exc:
        print(f"Could not start the UI on port {port}: {exc}")
        print("Another copy may already be running. Try --port 8734.")
        return 1

    url = f"http://127.0.0.1:{httpd.server_port}/"
    print("Family Success Planner - preview UI")
    print(f"  {url}")
    print("  Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
    return 0
