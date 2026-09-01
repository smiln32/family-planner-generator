# Setup questionnaire

Ask these once. Answers configure the factory, not a single family's book. Per-run year and names belong in stage 01.

Ask all questions in one pass. Use the default if they skip.

1. Default paper size? (`letter` / `a4`) Default: letter.
   - Derived: `page_size` in future `planner.py init` files and `_config/design-system.md` default sentence if they chose A4.
2. Default week start? (`sunday` / `monday`) Default: sunday.
3. Default theme name? (`classic` `amber` `berry` `bold` `citrus` `forest` `meadow` `ocean` `pastel` `poppy` `slate`) Default: classic.
4. Default typeface set? (`classic` `rounded` `modern` `elegant` `bubbly` `neat`) Default: classic.
5. Typical household size for blank tracker rows? Number. Default: 5.
6. Do you want dated monthly grids by default? (`yes` / `no`) Default: yes.

After answers: write them into `config.example.yaml` comments or values only where they are factory defaults, and replace any `{{PLACEHOLDER}}` left in `_config/`. Do not put a specific family name into `_config/`.
