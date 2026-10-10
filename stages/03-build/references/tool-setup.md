# Tool setup

The build needs two things on the computer: Python and a Chromium-family browser. Install them once.

## Python

Python runs `planner.py`, the local app that renders the book.

1. Install Python 3.10 or newer from python.org. On Windows, tick "Add python.exe to PATH".
2. From the repo root, run `pip install -r requirements.txt`. This installs Jinja2 and PyYAML.
3. Check it: `python planner.py pages` prints the page list.

## Browser

The PDF step prints the HTML with a browser. Google Chrome, Microsoft Edge, Chromium, or Brave all work.

1. Install any one of them. Windows already has Edge.
2. The build finds it on its own. To pick a different one, pass `--browser PATH` or set `CHROME_PATH`.
3. Check it: a build that ends with `pdf  -> ...` found the browser. Without one, `--html-only` still builds the HTML.

## Fonts

Nothing to install. The typefaces for every look and every built-in typeface set are in the repo, in `familyplanner/static/fonts/`, with their licences. Only a config that names its own Google Fonts families needs `python planner.py fonts -c <yaml>` once to download those. `fonts --all` refreshes or re-downloads the built-in sets. A missing font never stops a build: pages fall back to system fonts.

## Tests

For code changes only: `pip install -r requirements-dev.txt`, then `python -m pytest`.
