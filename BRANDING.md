# Branding addition (fork)

This fork adds two things to the upstream
[Hipo/university-domains-list](https://github.com/Hipo/university-domains-list)
dataset:

1. **`brand.json`** — one entry per institution with `domain`, `name`,
   `country` (ISO-3166 alpha-2) and a `branding` object pointing to
   image files in this repo.
2. **`logos/`** — the actual asset files (SVG / PNG / JPG), named
   `<domain>_<kind>.<ext>` (kind = `logo` | `shield` | `wordmark`).

### Format

```json
{
  "domain": "abdn.ac.uk",
  "name": "University of Aberdeen",
  "country": "GB",
  "branding": {
    "logo":     "logos/abdn.ac.uk_logo.svg",
    "shield":   "logos/abdn.ac.uk_shield.svg",
    "wordmark": null
  }
}
```

- All three slots are always present; `null` means "searched, none
  found" (not "not yet checked").
- Paths are relative to the repo root. Consumers can construct raw URLs
  as
  `https://raw.githubusercontent.com/<owner>/university-domains-list/<branch>/<path>`.

### Conventions for asset classification

- **logo**: full identifying mark with the institution name in stylised
  lettering. Typically wider than it is tall.
- **shield**: heraldic crest, badge or square emblem. Typically square
  or taller than wide.
- **wordmark**: the institution's name set in a custom typeface, no
  symbol.

Most assets here were sourced from each institution's official site or
its Wikipedia infobox. Many crests are trademarked — this repo does not
relicense them; consumers are responsible for their own use.

### Browse the assets

A static copy is rendered to [`preview/index.html`](preview/index.html) on
every preview run and committed to the repo, so you can view it directly:
<https://htmlpreview.github.io/?https://github.com/benwhalley/universities-domains-list/blob/main/preview/index.html>

To regenerate / browse locally:

```sh
uv run preview.py            # writes preview/index.html, then serves on :8000
uv run preview.py --static   # write the static copy only, no server
```

Visit <http://localhost:8000/> for a searchable grid of every entry
(filter by domain / name / country, toggle missing-logo / missing-shield).
The page is rendered from `brand.json` on each request, so edits show
up on a refresh.

### Provenance

Generated from a working dataset of ~1,000 institutions. Quality is
mixed: some entries are perfect, others have only a shield (no
wordmark), a handful have only the wordmark. PRs to fill gaps are
welcome.
