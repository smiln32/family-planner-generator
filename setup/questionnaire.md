# Setup questionnaire

Ask these once. Answers configure the factory, not a single family's book. Per-run year and names belong in stage 01.

Ask all questions in one pass. Use the default if they skip.

1. Default paper size? (`5.5x8` / `6x9` / `letter`) Default: letter (8.5 by 11 in).
   - Derived: `page_size` in future `planner.py init` files and `_config/design-system.md` if they did not keep letter.
2. Default week start? (`sunday` / `monday`) Default: sunday.
3. Default theme name? (`linen` `classic` `amber` `berry` `bold` `citrus` `forest` `meadow` `ocean` `pastel` `poppy` `slate`) Default: linen.
4. Default typeface set? (`elegant` `classic` `playful` `modern` `italics` `neat`) Default: elegant.
5. Typical household size for blank tracker rows? Number. Default: 5.
6. Do you want dated monthly grids by default? (`yes` / `no`) Default: yes.

After answers: write them into `config.example.yaml` comments or values only where they are factory defaults, and replace any `{{PLACEHOLDER}}` left in `_config/`. Do not put a specific family name into `_config/`.
