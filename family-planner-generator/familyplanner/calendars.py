"""Month-grid maths shared by the annual calendar and the monthly planners."""

from __future__ import annotations

import calendar
from dataclasses import dataclass

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Full names for the wide monthly grid, initials for the compact year-at-a-glance.
DAY_NAMES_SUN = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DAY_NAMES_MON = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass(frozen=True)
class Day:
    """One cell of a month grid. `number` is None for leading/trailing blanks."""

    number: int | None
    weekend: bool


def day_names(sunday_first: bool) -> list[str]:
    return list(DAY_NAMES_SUN if sunday_first else DAY_NAMES_MON)


def day_initials(sunday_first: bool) -> list[str]:
    return [name[0] for name in day_names(sunday_first)]


def weekend_flags(sunday_first: bool) -> list[bool]:
    """Which columns are Saturday/Sunday, for tinting the year-view numerals."""
    if sunday_first:
        return [True, False, False, False, False, False, True]
    return [False, False, False, False, False, True, True]


def month_grid(year: int, month: int, sunday_first: bool, rows: int = 6) -> list[list[Day]]:
    """Return a `rows` x 7 grid of Day cells for the given month.

    The grid is padded to exactly `rows` weeks so every printed month occupies
    the same height - a 5-row month leaves one blank row rather than stretching
    its cells, which is what keeps the twelve monthly pages visually identical.
    """
    firstweekday = 6 if sunday_first else 0
    cal = calendar.Calendar(firstweekday=firstweekday)
    weekend = weekend_flags(sunday_first)

    weeks: list[list[Day]] = []
    for week in cal.monthdayscalendar(year, month):
        weeks.append([
            Day(number=day or None, weekend=weekend[col])
            for col, day in enumerate(week)
        ])

    if len(weeks) > rows:
        raise ValueError(f"{MONTH_NAMES[month - 1]} {year} needs {len(weeks)} rows")
    blank = [Day(number=None, weekend=weekend[col]) for col in range(7)]
    while len(weeks) < rows:
        weeks.append(list(blank))
    return weeks


def compact_grid(year: int, month: int, sunday_first: bool) -> list[list[Day]]:
    """A tight grid (no padding) for the twelve mini-months on the year page."""
    firstweekday = 6 if sunday_first else 0
    cal = calendar.Calendar(firstweekday=firstweekday)
    weekend = weekend_flags(sunday_first)
    return [
        [Day(number=day or None, weekend=weekend[col]) for col, day in enumerate(week)]
        for week in cal.monthdayscalendar(year, month)
    ]
