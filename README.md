# jakadul/news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/jakadul/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/jakadul/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Draws the front page of THE WORLD for **Thursday 19 November 2026**, in one
1200x1600 PNG with a stdlib-only font engine (zero Pillow at runtime). The
page carries **47 stories** — counted in code and stated in the masthead
(`47 STORIES · 7 REGIONS · EVERY ONE FROM THURSDAY 19 NOVEMBER 2026`):

- 6-beat **UTC timeline strip** ("THE DAY IN UTC")
- 4 **feature panels** (Shenzhen trilateral, Gulf war, US midterms, Iran arms)
- 3x7 grid of **21 numbered cards**, each with region tag, verification tag
  (CONFIRMED / CLAIM / REPORTED) and a named source
- **"ALSO ON THIS DAY"** continuation strip, 16 numbered one-line items
- **region index** with story counts for all 7 regions + a date audit line

Date audit: `THURSDAY, NOVEMBER 19, 2026` appears in masthead, dateline,
region index and footer; 19 Nov 2026 is a Thursday. Density over drama:
hairline rules, flat fills, keypad-dense grid, no hero illustration.

No network, no clock, no randomness, no env lookups: two runs write the same
bytes.

## Run it

```sh
python3 -P -s main.py            # writes /output/entry.png
python3 -P -s main.py out        # writes out/entry.png
# MAKEFUN_OUTPUT_DIR=/x python3 main.py   # env wins over argv
```

`main.py` is the entrypoint and stays thin; `frontpage.py` holds the renderer
(layout, type, tags, wrapping, story-count audit) and can be imported and
called on its own: `frontpage.render_page()` returns the image,
`frontpage.save_page(path)` writes it, `frontpage.overruns(audit)` reports
any block wider than its limit, and `frontpage.audit_story_count()` asserts
6 + 4 + 21 + 16 = 47.

## Engine

- `canvas.py` — RGB raster, rules/shapes/coverage blending, PNG encoder
  (adaptive per-scanline filters), box downsample
- `truetype.py` — cmap/loca/glyf/hmtx parser, composite glyph support
- `textrender.py` — quadratic flattening, non-zero winding scanline coverage
  with 4x vertical subsampling, glyph cache
- `textadapter.py` — design-pixel facade: type cache, measuring, greedy /
  balanced / DP wrapping, size fitting

Fonts bundle in `fonts/` (Liberation family); `_FONT_DIRS` prefers the
repo-local `fonts/` directory first.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>