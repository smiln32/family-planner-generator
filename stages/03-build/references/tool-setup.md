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

Optional. `python planner.py fonts` downloads your book's typefaces once (`fonts --all` downloads every set). Without them pages fall back to system fonts and still build.

## Tests

For code changes only: `pip install -r requirements-dev.txt`, then `python -m pytest`.
