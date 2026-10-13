# Factory reference (Layer 3)

Stable across runs. Load only the file, or the section, that a stage Inputs table names.

| File | What it is |
|------|------------|
| `design-system.md` | Margin, type, cards, footer, colour tokens, month motifs |
| `chrome-catalog.md` | The chrome axis contract: vocabulary, families, rules; the catalog itself is `familyplanner/chrome.py` |
| `voice.md` | How page copy should sound, and how to print family names |
| `page-catalog.md` | Default running order and slugs |
| `../config.example.yaml` | Every generator key, with comments |

Do not put per-family names or a specific year in these files. Those belong in stage output.
