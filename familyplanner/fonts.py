"""Download the chosen typefaces from Google Fonts.

The planner renders without them - planner.css declares fallback stacks - but
the display faces are what give the pages their character. Everything on
Google Fonts is open-licensed (SIL OFL or Apache 2.0), so the PDFs you make
are yours to print, give away or sell.

URLs are resolved from the CSS API rather than hardcoded, because CDN
filenames change whenever a family is revised.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .typefaces import ROLE_WEIGHTS, Typefaces, slug

# A modern browser UA is what makes the API hand back woff2 rather than ttf.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
CSS_ENDPOINT = "https://fonts.googleapis.com/css2"

FACE_RE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
FAMILY_RE = re.compile(r"font-family:\s*['\"]([^'\"]+)['\"]")
WEIGHT_RE = re.compile(r"font-weight:\s*([0-9]+)(?:\s+([0-9]+))?")
URL_RE = re.compile(r"url\((https://[^)]+\.woff2)\)")
RANGE_RE = re.compile(r"unicode-range:\s*([^;]+)")


class FontError(RuntimeError):
    """Raised when a family cannot be found on Google Fonts at all."""


def _fetch(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _css_for(family: str, weights: list[int]) -> str:
    """Fetch the API's CSS for one family, relaxing the request if it 400s.

    Google rejects the whole query if a family does not publish a requested
    weight, so try the exact weights, then a common pair, then the bare family.
    """
    attempts: list[str] = []
    if weights:
        attempts.append(f"{family}:wght@{';'.join(str(w) for w in sorted(set(weights)))}")
        attempts.append(f"{family}:wght@400;700")
    attempts.append(family)

    last: Exception | None = None
    for spec in attempts:
        url = f"{CSS_ENDPOINT}?{urllib.parse.urlencode([('family', spec), ('display', 'block')])}"
        try:
            return _fetch(url).decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code != 400:
                raise
            last = exc
    raise FontError(f"Google Fonts has no family called '{family}'") from last


def _available(css: str, family: str) -> dict[int, str]:
    """weight -> woff2 URL for the basic-latin subset of one family."""
    found: dict[int, str] = {}
    for block in FACE_RE.findall(css):
        family_match = FAMILY_RE.search(block)
        url_match = URL_RE.search(block)
        weight_match = WEIGHT_RE.search(block)
        if not (family_match and url_match):
            continue
        if family_match.group(1).lower() != family.lower():
            continue
        # Google emits one face per unicode subset; basic latin is all we need.
        range_match = RANGE_RE.search(block)
        if range_match and "U+0000-00FF" not in range_match.group(1):
            continue
        if weight_match and weight_match.group(2) is not None:
            # A variable face covers a range - register both ends and the middle.
            low, high = int(weight_match.group(1)), int(weight_match.group(2))
            for w in {low, high, 400, 700}:
                if low <= w <= high:
                    found.setdefault(w, url_match.group(1))
        elif weight_match:
            found.setdefault(int(weight_match.group(1)), url_match.group(1))
        else:
            found.setdefault(400, url_match.group(1))
    return found


def _nearest(available: dict[int, str], weight: int) -> tuple[int, str] | None:
    """Exact weight if published, otherwise the closest one the family has."""
    if not available:
        return None
    if weight in available:
        return weight, available[weight]
    closest = min(available, key=lambda w: (abs(w - weight), w))
    return closest, available[closest]


def fetch_fonts(dest: Path, faces: Typefaces, force: bool = False) -> int:
    """Download whatever `faces` needs into `dest`. Returns a process exit code."""
    dest.mkdir(parents=True, exist_ok=True)

    wanted = faces.wanted()
    pending = [(f, w) for f, w in wanted if force or not _is_present(dest / slug(f, w))]
    skipped = len(wanted) - len(pending)

    label = faces.preset or "custom"
    print(f"Font set: {label}")
    for role, family in faces.roles.items():
        print(f"  {role:<8} {family}")
    print()

    if not pending:
        print(f"All {skipped} faces already present in {dest}")
        return 0

    downloaded = failed = 0
    substituted: list[str] = []
    families = sorted({f for f, _ in pending})

    for family in families:
        weights = [w for f, w in pending if f == family]
        try:
            available = _available(_css_for(family, _weights_for(family, faces)), family)
        except (FontError, urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"  failed  {family}: {exc}")
            failed += len(weights)
            continue

        for weight in weights:
            target = dest / slug(family, weight)
            picked = _nearest(available, weight)
            if picked is None:
                print(f"  failed  {target.name}: no latin face in the API response")
                failed += 1
                continue
            actual, url = picked
            try:
                payload = _fetch(url)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                print(f"  failed  {target.name}: {exc}")
                failed += 1
                continue
            if not payload:
                print(f"  failed  {target.name}: empty response")
                failed += 1
                continue
            target.write_bytes(payload)
            note = "" if actual == weight else f"  (using {actual}, {weight} not published)"
            if note:
                substituted.append(f"{family} {weight} -> {actual}")
            print(f"  ok      {target.name}  ({len(payload) / 1024:.0f} KB){note}")
            downloaded += 1

    print(f"\n{downloaded} downloaded, {skipped} already present, {failed} failed")
    if substituted:
        print("Weight substitutions: " + "; ".join(substituted))
    if failed:
        print("The planner still builds without them, using fallback system fonts.")
        return 1
    print(f"Fonts live in {dest}")
    return 0


def _weights_for(family: str, faces: Typefaces) -> list[int]:
    """Every weight any role wants from this family."""
    weights: list[int] = []
    for role, name in faces.roles.items():
        if name == family:
            weights.extend(ROLE_WEIGHTS[role])
    return sorted(set(weights))


def _is_present(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0
