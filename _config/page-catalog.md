# Page catalog

Default running order (`config.DEFAULT_PAGES`). Slug is the template name except `months`, which expands to twelve monthly sheets.

| # | Slug | Title |
|---|------|--------|
| 1 | cover | Cover |
| 2 | belongs_to | This Planner Belongs To |
| 3 | how_to_use | How To Use This Planner |
| 4 | vision_mission | Family Vision & Mission |
| 5 | year_goals | Family Goals |
| 6 | values | Family Values Worksheet |
| 7 | annual_calendar | Annual Family Calendar |
| 8 | budget | Family Budget Overview |
| 9 | chores | Household Chores Planner |
| 10 | meal_plan | Weekly Meal Planning Sheet |
| 11 | grocery | Grocery Shopping List |
| 12 | health_tracker | Family Health & Wellness Tracker |
| 13 | emergency | Emergency Contacts & Important Info |
| 14 | school_activities | School & Activities Schedule |
| 15 | family_time | Family Time Planner |
| 16-27 | months | January through December Family Planner |
| 28 | vacation | Vacation & Travel Planner |
| 29 | home_maintenance | Home Maintenance Checklist |
| 30 | year_end | Year-End Family Reflection |

Optional extras (not in the default book): `index` (digital contents, added by `--linked`), `reading_log`, `example_gratitude`, `weekly` (Weekly Plan) and `daily` (Daily Plan). A layout design (`02a` to `12c`, see `design-system.md`) adds `weekly` and `daily` just before the months on its own, unless `pages:` already places one of them; it also swaps the twelve month pages for the layout's monthly page. That book is 32 pages.

Comment a slug out of `pages:` in family.yaml to drop it. There is no duplicate dated January; twelve unique months is the book.
