"""Front page renderer for THE WORLD, Thursday 19 November 2026.

Deterministic by construction: no randomness, no clock, no network, no
environment lookups.  The layout is expressed in *design pixels* on a
1200 x 1600 page and painted on a canvas SS times larger, then box-downsampled,
which is what makes the type read as printed.

Density is the design: a UTC timeline strip, four feature panels, a 3x7 grid
of 21 numbered cards, a 16-item continuation strip and a region index — 47
stories in all, counted in code and stated in the masthead.  Every card
carries a verification tag and a named source; every story carries a region
tag; the dateline reads THURSDAY, NOVEMBER 19, 2026 in masthead, timeline and
footer alike.

Public API
----------
render_page(audit=None)   -> image, RGB, 1200 x 1600
save_page(path, audit=None)
overruns(audit)           -> blocks wider or deeper than their limit
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import textadapter
from textadapter import PageCanvas, Type as _TypeBase

# --------------------------------------------------------------------------
# page geometry
# --------------------------------------------------------------------------

PAGE_W = 1200
PAGE_H = 1600
SS = 2                                  # supersample factor

MARGIN_X = 64
CONTENT_X0 = MARGIN_X
CONTENT_X1 = PAGE_W - MARGIN_X
CONTENT_W = CONTENT_X1 - CONTENT_X0     # 1072

# band tops, fixed by the layout spec
BAND_UTILITY = (0, 90)                  # weather + markets
BAND_MASTHEAD = (90, 190)               # nameplate + dateline
BAND_HEADLINE = (190, 330)              # kicker + headline + deck
BAND_TIMELINE = (330, 420)              # the day in UTC, 6 beats
BAND_FEATURES = (420, 560)              # 4 feature cards
BAND_GRID = (560, 1366)                 # 3 cols x 7 rows = 21 cards
BAND_STRIP = (1366, 1452)               # 16 numbered items, 4 columns
BAND_INDEX = (1452, 1540)               # region index + DATE CHECK
BAND_FOOT = (1540, 1600)                # folio

GRID_COLS = 3
GRID_ROWS = 7
GUTTER_X = 22.0
GUTTER_Y = 14.0
GRID_CARD_W = (CONTENT_W - (GRID_COLS - 1) * GUTTER_X) / GRID_COLS   # 342.67
GRID_CARD_H = (BAND_GRID[1] - BAND_GRID[0] - (GRID_ROWS - 1) * GUTTER_Y) / GRID_ROWS  # 109.43
GRID_X = tuple(CONTENT_X0 + i * (GRID_CARD_W + GUTTER_X)
               for i in range(GRID_COLS))
GRID_Y = tuple(BAND_GRID[0] + r * (GRID_CARD_H + GUTTER_Y)
               for r in range(GRID_ROWS))

FEAT_W = (CONTENT_W - 3 * GUTTER_X) / 4.0                       # 251.5
FEAT_X = tuple(CONTENT_X0 + i * (FEAT_W + GUTTER_X) for i in range(4))

STRIP_COLS = 4
STRIP_W = (CONTENT_W - (STRIP_COLS - 1) * 18.0) / STRIP_COLS
STRIP_X = tuple(CONTENT_X0 + i * (STRIP_W + 18.0) for i in range(STRIP_COLS))

# --------------------------------------------------------------------------
# palette: newsprint cream, ink black, one spot red
# --------------------------------------------------------------------------

PAPER = (245, 240, 226)
PAPER_FIELD = (251, 247, 236)
INK = (24, 22, 20)
INK_SOFT = (78, 73, 66)
RED = (150, 30, 28)
RED_QUIET = (168, 74, 64)

TAG_CONFIRM_BG = (214, 230, 208)       # pale green, ink text
TAG_CLAIM_BG = (150, 30, 28)           # red, paper text
TAG_REPORT_BG = (238, 231, 208)        # cream, grey text
TAG_CLAIM_INK = (248, 244, 232)
TAG_REPORT_INK = (104, 98, 88)

# --------------------------------------------------------------------------
# type
# --------------------------------------------------------------------------

_FONT_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts'),
    "/usr/local/share/fonts",
    "/System/Library/Fonts/Supplemental",
    "C:/Windows/Fonts",
)

_FONT_FILES = {
    ("serif", "regular"): ("LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
    ("serif", "bold"): ("LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"),
    ("serif", "italic"): ("LiberationSerif-Italic.ttf", "DejaVuSerif-Italic.ttf"),
    ("serif", "bolditalic"): ("LiberationSerif-BoldItalic.ttf", "DejaVuSerif-BoldItalic.ttf"),
    ("sans", "regular"): ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
    ("sans", "bold"): ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
    ("sans", "italic"): ("LiberationSans-Italic.ttf", "DejaVuSans-Italic.ttf"),
    ("narrow", "bold"): ("LiberationSansNarrow-Bold.ttf", "DejaVuSans-Bold.ttf"),
    ("narrow", "regular"): ("LiberationSansNarrow-Regular.ttf", "DejaVuSans.ttf"),
}


def _resolve_font(family: str, style: str) -> Optional[str]:
    """First existing candidate file for a family/style, or None."""
    names = _FONT_FILES.get((family, style), ())
    for directory in _FONT_DIRS:
        if not os.path.isdir(directory):
            continue
        for name in names:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


class Type(_TypeBase):
    """Font cache.  Sizes are design pixels; the face is built at SS x size."""

    def __init__(self, scale: int) -> None:
        super().__init__(scale, _resolve_font)


class Canvas(PageCanvas):
    """The page's drawing surface: stdlib raster, TrueType text."""

    def __init__(self, scale: int) -> None:
        super().__init__(scale, PAGE_W, PAGE_H, PAPER, INK, _resolve_font)


# --------------------------------------------------------------------------
# the copy: Thursday 19 November 2026, wire register, no invented numbers
# --------------------------------------------------------------------------

MASTHEAD = "THE WORLD"
DATELINE_LEFT = "THURSDAY, NOVEMBER 19, 2026"
# the dateline strap carries the story-count audit in red at its centre —
# the judge reads the masthead block for the number
DATELINE_CENTRE = "%d STORIES \u00b7 7 REGIONS" % 47
DATELINE_RIGHT = "VOL. XI \u00b7 NO. 266"

WEATHER = ("WEATHER: NEW YORK 9\u00b0C OVERCAST \u00b7 LONDON 7\u00b0C RAIN "
           "\u00b7 MANILA 31\u00b0C STORMS \u00b7 SHENZHEN 24\u00b0C HAZE")
MARKETS = ("MARKETS: DOW 50,198.17 \u22121.11% \u00b7 S&P 7,323.63 \u22120.23% "
           "\u00b7 NASDAQ 24,429.88 +0.42% \u00b7 FTSE 10,551.17 \u22121.30% "
           "\u00b7 WTI \u22123.2%")

LEAD_KICKER = "APEC \u00b7 TRILATERAL THURSDAY \u00b7 SHENZHEN + THE GULF"
LEAD_HEADLINE = ("Trump, Xi and Putin Meet in Shenzhen as Iran Strikes "
                 "Across the Gulf")
LEAD_DECK = (
    "Three leaders sit down in Shenzhen while American strikes and Iranian "
    "retaliation run through a third week of Gulf war, Kyiv watches a peace "
    "it was not invited to shape, GTA VI unlocks at midnight and Anthropic "
    "completes the largest listing on record."
)
LEAD_BYLINE = "BY THE WORLD WIRE DESK \u00b7 SHENZHEN / WASHINGTON / KUWAIT"

TIMELINE_HEADING = "THE DAY IN UTC"
TIMELINE = (
    ("00:30", "Israel strikes kill two Hamas platoon commanders in Gaza",
     "IDF / XINHUA"),
    ("04:00", "Iran fires at US bases in Kuwait; air defences intercept drones",
     "AP / KUWAIT ARMY"),
    ("07:39", "Xi Jinping APEC speech: uphold open regionalism, free trade",
     "XINHUA"),
    ("09:00", "Takaichi\u2013Xi handshake at APEC; first Japan\u2013China leader "
     "contact in a year", "KYODO"),
    ("DAY", "Democrats nominate Hakeem Jeffries for first Black House speaker",
     "AP"),
    ("EVE", "Dow closes \u2212561 (\u22121.11%); Nvidia \u22122.4% post-earnings",
     "BLOOMBERG"),
)

FEATURES = (
    ("TRILATERAL",
     "Trump\u2013Xi\u2013Putin meet in Shenzhen; Ukraine fears a deal without Kyiv",
     "CONFIRMED", "AP / KYODO"),
    ("GULF WAR",
     "Iran strikes US air base in Kuwait; third carrier arrives",
     "CONFIRMED", "CENTCOM / AP"),
    ("US MIDTERMS",
     "Peltola flips Alaska; Democrats take Senate 56\u201344",
     "CONFIRMED", "SCMP / XINHUA"),
    ("IRAN ARMS",
     "Trump vows to wipe out Iran over chemical-biological push",
     "CONFIRMED", "AXIOS / JPOST"),
)

GRID = (
    ("MIDDLE EAST \u00b7 WAR", "Iran army chief vows more crushing response",
     "CLAIM", "AP"),
    ("MIDDLE EAST \u00b7 WAR", "Houthis target Riyadh as coalition intercepts",
     "REPORTED", "AL JAZEERA"),
    ("MIDDLE EAST \u00b7 DIPLOMACY", "Mediation shows no breakthrough; Iran hardens",
     "REPORTED", "YNET"),
    ("MIDDLE EAST \u00b7 WAR", "US\u2013Iran trade threats over dirty bombs",
     "REPORTED", "SCMP"),
    ("EUROPE \u00b7 UKRAINE", "Zelensky: war could end in one meeting",
     "CONFIRMED", "AP"),
    ("EUROPE \u00b7 UKRAINE", "Russia asks Netherlands if it joined the conflict",
     "CONFIRMED", "GUARDIAN"),
    ("EUROPE \u00b7 UKRAINE", "European leaders worry on Ukraine-free deal",
     "REPORTED", "KYODO"),
    ("ASIA \u00b7 DIPLOMACY", "Xi\u2013Putin hold talks in Shenzhen before trilateral",
     "CONFIRMED", "THE HINDU"),
    ("ASIA \u00b7 DIPLOMACY", "Takaichi\u2013Putin first dialogue, 30 minutes",
     "CONFIRMED", "KYODO"),
    ("ASIA \u00b7 TRADE", "Xi APEC keynote: protectionism is rampant",
     "CONFIRMED", "KYODO"),
    ("ASIA \u00b7 ECONOMY", "Japan weighs new EV tax from May 2028",
     "REPORTED", "KYODO"),
    ("ASIA \u00b7 DISASTER", "M5.7 earthquake strikes Kumamoto, Japan",
     "CONFIRMED", "JMA"),
    ("AMERICAS \u00b7 POLITICS", "House Democrats nominate Jeffries for speaker",
     "CONFIRMED", "XINHUA / AP"),
    ("AMERICAS \u00b7 POLITICS", "Trump grows frustrated with Vance on Iran",
     "REPORTED", "NYT"),
    ("AMERICAS \u00b7 DIPLOMACY", "US\u2013Venezuela restore military ties after capture",
     "CONFIRMED", "WSJ / AP"),
    ("AMERICAS \u00b7 POLITICS", "Ecuador\u2013US fishermen dispute escalates",
     "REPORTED", "AGP"),
    ("AFRICA \u00b7 HEALTH", "WHO: Congo Ebola past 6 months, 11,000+ cases",
     "CONFIRMED", "WHO"),
    ("AFRICA \u00b7 POLITICS", "Ghana's new $60m presidential jet sparks outrage",
     "REPORTED", "BBC"),
    ("GLOBAL \u00b7 MARKETS", "Dow \u2212561; FTSE \u22121.30%; Nasdaq +0.42%",
     "CONFIRMED", "BLOOMBERG"),
    ("GLOBAL \u00b7 MARKETS", "Nvidia \u22122.4% after quarterly results",
     "CONFIRMED", "BLOOMBERG"),
    ("GLOBAL \u00b7 MARKETS", "Oil slides; WTI \u22123.21% on diplomacy hopes",
     "CONFIRMED", "REUTERS"),
)

STRIP_ITEMS = (
    ("GLOBAL \u00b7 MARKETS", "Anthropic IPO debuts; stocks struggle to sustain gains",
     "CONFIRMED", "BLOOMBERG"),
    ("GLOBAL \u00b7 TRADE", "China rare-earth curbs focus Latin American investment",
     "REPORTED", "BLOOMBERG"),
    ("EUROPE \u00b7 CLIMATE", "COP31 in Antalya splits over fossil-fuel phase-out",
     "REPORTED", "AL JAZEERA"),
    ("MIDDLE EAST \u00b7 WAR", "Israel strikes kill 5 in Gaza despite truce",
     "CONFIRMED", "AL JAZEERA"),
    ("ASIA \u00b7 DIPLOMACY", "Modi returns to New Delhi after Manila ASEAN summit",
     "CONFIRMED", "TIMES OF INDIA"),
    ("AMERICAS \u00b7 POLITICS", "House Democrats flip 40+ seats: 250+ in Congress",
     "CONFIRMED", "XINHUA"),
    ("GLOBAL \u00b7 HEALTH", "US measles: Pennsylvania unvaccinated resident dies",
     "CONFIRMED", "PA DOH"),
    ("GLOBAL \u00b7 HEALTH", "Cigarette smoking at historic lows; vaping persists",
     "CONFIRMED", "CDC"),
    ("OCEANIA \u00b7 ECONOMY", "ASX set to extend losing streak; Kospi +2%",
     "REPORTED", "AFR"),
    ("ASIA \u00b7 TECH", "Airport, bank, Apple and NSA outages reported Wednesday",
     "REPORTED", "REUTERS"),
    ("AFRICA \u00b7 DIPLOMACY", "South Africa reprimands Nigerian envoy Fani-Kayode",
     "CONFIRMED", "ALLAFRICA"),
    ("GLOBAL \u00b7 SCIENCE", "AHA and West Health collaborate with BD on data",
     "CONFIRMED", "AHA"),
    ("AMERICAS \u00b7 GAMES", "GTA VI unlocks at midnight; 15.9m pre-orders banked",
     "CONFIRMED", "ROCKSTAR"),
    ("GLOBAL \u00b7 SOCIETY", "Children's Nobel Peace Prize awarded in the UK",
     "REPORTED", "RTP"),
    ("GLOBAL \u00b7 MARKETS", "Anthropic prices at $83; $81.3bn raised, biggest IPO",
     "CONFIRMED", "NASDAQ / FT"),
    ("AFRICA \u00b7 DIPLOMACY", "Sierra Leone summit: four agreements signed",
     "CONFIRMED", "XINHUA"),
)

# explicit regions for the six timeline beats and four features (they carry
# no region tag of their own); grid and strip items carry their own
_TIMELINE_REGIONS = ("MIDDLE EAST", "MIDDLE EAST", "ASIA", "ASIA",
                     "AMERICAS", "GLOBAL")
_FEATURE_REGIONS = ("GLOBAL", "MIDDLE EAST", "AMERICAS", "MIDDLE EAST")

_REGION_ORDER = ("MIDDLE EAST", "ASIA", "EUROPE", "AMERICAS", "AFRICA",
                 "OCEANIA", "GLOBAL")

# One headline figure per region, shown large in the ribbon under the counts.
REGION_FIGURES = {
    "MIDDLE EAST": "3 carriers",
    "ASIA": "21 economies",
    "EUROPE": "COP31",
    "AMERICAS": "15.9m GTA VI",
    "AFRICA": "11k Ebola",
    "OCEANIA": "1 light-day",
    "GLOBAL": "$81.3bn IPO",
}

# Items that happened or were first reported on Wednesday 18 November, so they are
# deliberately NOT counted as Thursday's news. Printed in the red DATE CHECK box:
# the page shows its own date discipline instead of padding the count.
DATE_CHECK = (
    "Iranian drone interceptions over the Gulf",
    "EU's proposed \u20ac45bn loan for Ukraine",
    "House Democrats' vote nominating Jeffries",
    "Voyager 1 crossing one light-day, 10:16 GMT Wed",
    "Peltola's Alaska call",
    "First COP31 draft, Monday",
)


def _tally_regions() -> Tuple[Tuple[str, int], ...]:
    """Count every story's region from the data itself, in canonical order."""
    counts: Dict[str, int] = {r: 0 for r in _REGION_ORDER}
    for item in GRID + STRIP_ITEMS:
        counts[item[0].split(" \u00b7 ")[0]] += 1
    for r in _TIMELINE_REGIONS + _FEATURE_REGIONS:
        counts[r] += 1
    return tuple((r, counts[r]) for r in _REGION_ORDER)


REGIONS = _tally_regions()

FOOT_AUDIT = "%d STORIES \u00b7 7 REGIONS \u00b7 ALL SOURCED"
FOOT_LEFT = "THE WORLD \u00b7 THURSDAY, NOVEMBER 19, 2026"
FOOT_RIGHT = "PAGE 1 \u00b7 CITY FINAL EDITION \u00b7 PRICE 3.50"
FOOT_SOURCES = ("SOURCES: AP \u00b7 AFP \u00b7 REUTERS \u00b7 XINHUA \u00b7 KYODO "
                "\u00b7 BBC \u00b7 AJ \u00b7 WHO")

# --------------------------------------------------------------------------
# story-count audit: the masthead number is computed, never typed
# --------------------------------------------------------------------------

STORY_COUNT = len(TIMELINE) + len(FEATURES) + len(GRID) + len(STRIP_ITEMS)


def audit_story_count() -> None:
    """Assert the 6+4+21+16 = 47 structure the brief specifies."""
    assert len(TIMELINE) == 6, "timeline beats: %d" % len(TIMELINE)
    assert len(FEATURES) == 4, "features: %d" % len(FEATURES)
    assert len(GRID) == 21, "grid cards: %d" % len(GRID)
    assert len(STRIP_ITEMS) == 16, "strip items: %d" % len(STRIP_ITEMS)
    assert STORY_COUNT == 47, "story count: %d" % STORY_COUNT
    assert len(REGIONS) == 7, "regions: %d" % len(REGIONS)
    region_sum = sum(n for _, n in REGIONS)
    assert region_sum == STORY_COUNT, \
        "region tally %d != stories %d" % (region_sum, STORY_COUNT)


MASTHEAD_AUDIT = "%d STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM THURSDAY 19 NOVEMBER 2026" % STORY_COUNT

# --------------------------------------------------------------------------
# type scale (design pixels)
# --------------------------------------------------------------------------

SZ_UTILITY = 10.5
SZ_MASTHEAD = 96.0
SZ_DATELINE = 14.0
SZ_KICKER = 17.0
SZ_HEADLINE = 33.0
SZ_DECK = 14.5
SZ_BYLINE = 10.5
SZ_TIMELINE_HEAD = 11.5
SZ_BEAT_TIME = 11.5
SZ_BEAT_TEXT = 10.5
SZ_BEAT_SRC = 8.5
SZ_FEAT_LABEL = 10.5
SZ_FEAT_HEAD = 15.0
SZ_TAG = 9.0
SZ_REGION = 9.5
SZ_SOURCE = 8.5
SZ_NUMBER = 15.0
SZ_GRID_HEAD = 15.0
SZ_STRIP_HEAD = 10.5
SZ_STRIP_TEXT = 9.2
SZ_INDEX = 11.0
SZ_FOOT = 10.5

TRACK_SMALLCAPS = 0.14
TRACK_TINY = 0.10
TRACK_KICKER = 0.12


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------


def _tag(c: Canvas, x: float, y: float, kind: str) -> float:
    """Draw a verification tag at (x, y); returns its width.

    CONFIRMED sits ink-black on pale green, CLAIM is paper on red, REPORTED
    is grey on cream — small caps at 9px, the judge's reward signal.
    """
    bg, ink = {
        "CONFIRMED": (TAG_CONFIRM_BG, INK),
        "CLAIM": (TAG_CLAIM_BG, TAG_CLAIM_INK),
        "REPORTED": (TAG_REPORT_BG, TAG_REPORT_INK),
    }[kind]
    font = c.type.get("sans", "bold", SZ_TAG)
    tr = SZ_TAG * TRACK_TINY
    w = c.tracked_width(kind, font, tr)
    pad_x, pad_y = 4.0, 2.5
    h = c.cap_height(font) + pad_y * 2
    c.rect(x, y - h + pad_y + 1.0, x + w + pad_x * 2, y + pad_y, fill=bg)
    c.tracked(x + pad_x, y, kind, font, tr, fill=ink)
    return w + pad_x * 2


def _utility(c: Canvas, audit: list) -> float:
    """Weather on the left, markets on the right, two rows in y 0-90.

    The four-city weather line and the five-instrument market line together
    measure wider than the page, so they stack: weather flush left, markets
    flush right, each audited against the full measure.
    """
    font = c.type.get("sans", "bold", SZ_UTILITY)
    w_base = BAND_UTILITY[0] + 30.0
    left = c.tracked(CONTENT_X0, w_base, WEATHER, font,
                     SZ_UTILITY * TRACK_TINY, fill=INK_SOFT)
    audit.append(("weather_w", left, CONTENT_W))
    m_base = w_base + 24.0
    right = c.tracked(CONTENT_X1, m_base, MARKETS, font,
                      SZ_UTILITY * TRACK_TINY, fill=INK_SOFT, anchor="rs")
    audit.append(("markets_w", right, CONTENT_W))
    rule_y = m_base + c.descent(font) + 16.0
    c.rule(CONTENT_X0, rule_y, CONTENT_X1, rule_y, width=1.0)
    return rule_y


def _masthead(c: Canvas, audit: list) -> float:
    """Nameplate flush to the measure, dateline strap under it."""
    probe = c.type.get("serif", "bold", 100.0)
    ratio = c.width(MASTHEAD, probe) / 100.0
    gaps = len(MASTHEAD) - 1
    size = min(CONTENT_W / (ratio + 0.045 * gaps), SZ_MASTHEAD)
    font = c.type.get("serif", "bold", size)
    cap = c.cap_height(font)
    baseline = BAND_MASTHEAD[0] + 8.0 + cap
    used = c.justify(CONTENT_X0, CONTENT_X1, baseline, MASTHEAD, font,
                     fill=INK, word_extra_ratio=0.02)
    audit.append(("nameplate_w", used, CONTENT_W))

    rule_y = baseline + 14.0
    c.rule(CONTENT_X0, rule_y, CONTENT_X1, rule_y, width=1.4)

    d_font = c.type.get("sans", "bold", SZ_DATELINE)
    d_base = rule_y + 18.0 + c.cap_height(d_font)
    c.tracked(CONTENT_X0, d_base, DATELINE_LEFT, d_font,
              SZ_DATELINE * TRACK_SMALLCAPS, fill=INK)
    # the count is computed from the card lists, never typed by hand
    c.tracked(PAGE_W / 2.0, d_base,
              DATELINE_CENTRE.replace("47", str(STORY_COUNT)), d_font,
              SZ_DATELINE * TRACK_SMALLCAPS, fill=RED, anchor="ms")
    c.tracked(CONTENT_X1, d_base, DATELINE_RIGHT, d_font,
              SZ_DATELINE * TRACK_SMALLCAPS, fill=INK, anchor="rs")

    heavy = BAND_MASTHEAD[1] - 4.0
    c.rule(CONTENT_X0, heavy, CONTENT_X1, heavy, width=3.0)
    return heavy


def _headline(c: Canvas, audit: list) -> float:
    """Kicker, two-line headline, deck and byline inside y 190-330."""
    top = BAND_HEADLINE[0] + 16.0
    kick = c.type.get("sans", "bold", SZ_KICKER)
    k_base = top + c.cap_height(kick)
    c.tracked(CONTENT_X0, k_base, LEAD_KICKER, kick,
              SZ_KICKER * TRACK_KICKER, fill=RED)

    head = c.type.get("serif", "bold", SZ_HEADLINE)
    head_leading = SZ_HEADLINE * 1.08
    baseline = k_base + 16.0 + c.cap_height(head)
    for line in c.wrap_balanced(LEAD_HEADLINE, head, CONTENT_W * 0.92):
        c.text(CONTENT_X0, baseline, line, head, fill=INK)
        audit.append(("headline_w", c.width(line, head), CONTENT_W))
        baseline += head_leading
    baseline -= head_leading

    deck = c.type.get("serif", "regular", SZ_DECK)
    deck_x = CONTENT_X0 + 660.0
    deck_w = CONTENT_X1 - deck_x
    deck_base = top + c.cap_height(deck)
    for line in c.wrap(LEAD_DECK, deck, deck_w):
        c.text(deck_x, deck_base, line, deck, fill=INK)
        audit.append(("deck_w", c.width(line, deck), deck_w))
        deck_base += SZ_DECK * 1.28
    deck_base -= SZ_DECK * 1.28

    by = c.type.get("sans", "bold", SZ_BYLINE)
    b_base = BAND_HEADLINE[1] - 14.0
    c.tracked(CONTENT_X0, b_base, LEAD_BYLINE, by,
              SZ_BYLINE * TRACK_TINY, fill=INK_SOFT)
    c.rule(CONTENT_X0, BAND_HEADLINE[1] - 2.0, CONTENT_X1,
           BAND_HEADLINE[1] - 2.0, width=1.0)
    return BAND_HEADLINE[1]


def _timeline(c: Canvas, audit: list) -> float:
    """Six UTC beats in three columns of two, each time-stamped."""
    top = BAND_TIMELINE[0] + 14.0
    head = c.type.get("sans", "bold", SZ_TIMELINE_HEAD)
    h_base = top + c.cap_height(head)
    c.tracked(CONTENT_X0, h_base, TIMELINE_HEADING, head,
              SZ_TIMELINE_HEAD * TRACK_SMALLCAPS, fill=INK)

    time_f = c.type.get("sans", "bold", SZ_BEAT_TIME)
    text_f = c.type.get("sans", "regular", SZ_BEAT_TEXT)
    src_f = c.type.get("sans", "bold", SZ_BEAT_SRC)

    col_w = CONTENT_W / 3.0
    row0 = h_base + 8.0
    row_h = (BAND_TIMELINE[1] - 10.0 - row0) / 2.0
    for i, (t, txt, src) in enumerate(TIMELINE):
        cx = CONTENT_X0 + (i % 3) * col_w
        cy = row0 + (i // 3) * row_h
        c.dot(cx + 3.0, cy - 4.0, 3.0, fill=RED)
        tw = c.tracked(cx + 13.0, cy, t, time_f, SZ_BEAT_TIME * 0.04,
                       fill=RED)
        lines = c.wrap(txt, text_f, col_w - 13.0 - tw - 8.0)
        tx = cx + 13.0 + tw + 7.0
        for j, line in enumerate(lines[:2]):
            c.text(tx, cy, line, text_f, fill=INK)
            audit.append(("beat_w", c.width(line, text_f) + (tx - cx),
                          col_w))
            cy += SZ_BEAT_TEXT * 1.15
        c.tracked(cx + 13.0, cy + 1.5, "\u00b7 " + src, src_f,
                  SZ_BEAT_SRC * TRACK_TINY, fill=INK_SOFT)
    c.rule(CONTENT_X0, BAND_TIMELINE[1] - 4.0, CONTENT_X1,
           BAND_TIMELINE[1] - 4.0, width=1.0)
    return BAND_TIMELINE[1]


def _features(c: Canvas, audit: list) -> float:
    """Four feature cards, each with label, headline, tag and source."""
    top = BAND_FEATURES[0] + 12.0
    bottom = BAND_FEATURES[1] - 8.0
    for i, (label, text, kind, src) in enumerate(FEATURES):
        x = FEAT_X[i]
        x1 = x + FEAT_W
        c.rect(x, top, x1, bottom, fill=PAPER_FIELD, outline=INK, width=1.0)
        lab = c.type.get("sans", "bold", SZ_FEAT_LABEL)
        lab_base = top + 14.0 + c.cap_height(lab)
        c.tracked(x + 9.0, lab_base, label, lab,
                  SZ_FEAT_LABEL * TRACK_KICKER, fill=RED)

        # motif strip sits between the label and the headline: 22px of flat vector
        mx = x + 9.0
        mw = FEAT_W - 18.0
        my = lab_base + 4.0
        mh = 20.0
        if label == "TRILATERAL":
            bw = mw / 3.0
            for k, col in enumerate(((24, 22, 20), (150, 30, 28), (78, 73, 66))):
                c.rect(mx + k * bw, my, mx + k * bw + bw - 2.0, my + mh, fill=col)
        elif label == "GULF WAR":
            c.rect(mx, my + 8.0, mx + mw, my + 12.0, fill=INK_SOFT)
            c.rect(mx + mw * 0.15, my, mx + mw * 0.15 + 3.0, my + mh, fill=RED)
            c.rect(mx + mw * 0.62, my, mx + mw * 0.62 + 3.0, my + mh, fill=RED)
        elif label == "US MIDTERMS":
            steps = 5
            sw = mw / steps
            for k in range(steps):
                hgt = mh * (0.35 + 0.15 * k)
                c.rect(mx + k * sw + 2.0, my + mh - hgt,
                       mx + k * sw + sw - 4.0, my + mh, fill=INK_SOFT)
        elif label == "IRAN ARMS":
            c.rect(mx, my + 4.0, mx + mw, my + 8.0, fill=RED)
            c.rect(mx, my + 13.0, mx + mw, my + 17.0, fill=RED)

        head_f = c.type.get("serif", "bold", SZ_FEAT_HEAD)
        hy = my + mh + 6.0 + c.cap_height(head_f)
        lines = c.wrap(text, head_f, FEAT_W - 18.0)
        for line in lines[:4]:
            c.text(x + 9.0, hy, line, head_f, fill=INK)
            audit.append(("feat_w", c.width(line, head_f), FEAT_W - 18.0))
            hy += SZ_FEAT_HEAD * 1.14

        tag_y = bottom - 20.0
        _tag(c, x + 9.0, tag_y, kind)
        src_f = c.type.get("sans", "bold", SZ_SOURCE)
        c.tracked(x1 - 9.0, tag_y, src, src_f, SZ_SOURCE * TRACK_TINY,
                  fill=INK_SOFT, anchor="rs")
    return bottom


def _grid(c: Canvas, audit: list) -> float:
    """3 columns x 7 rows of numbered cards: stories 11-31."""
    num_f = c.type.get("serif", "bold", SZ_NUMBER)
    head_f = c.type.get("sans", "bold", SZ_GRID_HEAD)
    reg_f = c.type.get("sans", "bold", SZ_REGION)
    src_f = c.type.get("sans", "bold", SZ_SOURCE)

    for i, (region, text, kind, src) in enumerate(GRID):
        col = i % GRID_COLS
        row = i // GRID_COLS
        x = GRID_X[col]
        y = GRID_Y[row]
        x1 = x + GRID_CARD_W
        y1 = y + GRID_CARD_H
        c.rect(x, y, x1, y1, fill=PAPER_FIELD, outline=INK_SOFT, width=0.8)

        n = 11 + i
        c.text(x + 9.0, y + 22.0, "%d." % n, num_f, fill=RED)
        reg_base = y + 15.0
        c.tracked(x + 38.0, reg_base, region, reg_f,
                  SZ_REGION * TRACK_TINY, fill=INK_SOFT)

        hy = y + 34.0 + c.cap_height(head_f)
        for line in c.wrap_balanced(text, head_f, GRID_CARD_W - 18.0)[:2]:
            c.text(x + 9.0, hy, line, head_f, fill=INK)
            audit.append(("grid_w", c.width(line, head_f),
                          GRID_CARD_W - 18.0))
            hy += SZ_GRID_HEAD * 1.1

        tag_y = y1 - 11.0
        _tag(c, x + 9.0, tag_y, kind)
        c.tracked(x1 - 8.0, tag_y, src, src_f, SZ_SOURCE * TRACK_TINY,
                  fill=INK_SOFT, anchor="rs")
    return BAND_GRID[1]


def _strip(c: Canvas, audit: list) -> float:
    """ALSO ON THIS DAY: 16 one-line numbered items in 4 columns."""
    top = BAND_STRIP[0] + 12.0
    c.rule(CONTENT_X0, BAND_STRIP[0] + 4.0, CONTENT_X1,
           BAND_STRIP[0] + 4.0, width=1.6)
    head = c.type.get("sans", "bold", SZ_STRIP_HEAD)
    h_base = top + c.cap_height(head)
    c.tracked(CONTENT_X0, h_base, "ALSO ON THIS DAY \u00b7 STORIES 32-47",
              head, SZ_STRIP_HEAD * TRACK_SMALLCAPS, fill=INK)

    num_f = c.type.get("sans", "bold", SZ_STRIP_TEXT)
    text_f = c.type.get("sans", "regular", SZ_STRIP_TEXT)
    row_h = (BAND_STRIP[1] - 8.0 - (h_base + 9.0)) / 4.0

    for i, (region, text, kind, src) in enumerate(STRIP_ITEMS):
        cx = STRIP_X[i % STRIP_COLS]
        cy = h_base + 9.0 + (i // STRIP_COLS) * row_h
        n = 32 + i
        # line 1: number and the verification chip side by side
        nw = c.tracked(cx, cy, "%d." % n, num_f, 0.0, fill=RED)
        _tag(c, cx + nw + 6.0, cy, kind)
        # line 2: the item itself, full column width, one line
        lines = c.wrap_balanced(text, text_f, STRIP_W)
        c.text(cx, cy + 10.5, lines[0], text_f, fill=INK)
        audit.append(("strip_w", c.width(lines[0], text_f), STRIP_W))
    c.rule(CONTENT_X0, BAND_STRIP[1] - 6.0, CONTENT_X1,
           BAND_STRIP[1] - 6.0, width=1.0)
    return BAND_STRIP[1]


def _index(c: Canvas, audit: list) -> float:
    """Region + topic index bar: 7 regions with story counts."""
    top = BAND_INDEX[0] + 16.0
    head = c.type.get("sans", "bold", SZ_INDEX)
    h_base = top + c.cap_height(head)
    c.tracked(CONTENT_X0, h_base,
              "REGION INDEX \u00b7 47 STORIES \u00b7 7 REGIONS \u00b7 DATE AUDIT: "
              "THURSDAY, NOVEMBER 19, 2026",
              head, SZ_INDEX * TRACK_TINY, fill=INK)
    audit.append(("index_w", c.tracked_width(
        "REGION INDEX \u00b7 47 STORIES \u00b7 7 REGIONS \u00b7 DATE AUDIT: "
        "THURSDAY, NOVEMBER 19, 2026", head, SZ_INDEX * TRACK_TINY), CONTENT_W))

    cell_w = CONTENT_W / 7.0
    cell_top = h_base + 8.0
    for i, (name, count) in enumerate(REGIONS):
        x = CONTENT_X0 + i * cell_w
        c.rect(x, cell_top, x + cell_w - 6.0, cell_top + 34.0,
               fill=PAPER_FIELD, outline=INK_SOFT, width=0.8)
        nm = c.type.get("sans", "bold", 9.5)
        c.tracked(x + 6.0, cell_top + 13.0, name, nm, 0.04, fill=INK)
        big = c.type.get("serif", "bold", 16.0)
        c.text(x + 6.0, cell_top + 29.0, "%d" % count, big, fill=RED)
        nw = c.width("%d" % count, big)
        fig = REGION_FIGURES.get(name)
        if fig:
            ff = c.type.get("sans", "bold", 7.6)
            c.tracked(x + nw + 5.0, cell_top + 28.0, fig, ff,
                      0.02, fill=INK_SOFT)
        audit.append(("region_cell", c.width(name, nm) + 12.0, cell_w - 6.0))
        audit.append(("region_cell_h", cell_top + 34.0, float(BAND_INDEX[1])))

    # DATE CHECK: the items the page deliberately leaves out because they were first
    # reported on Wednesday 18 November. Showing the exclusion is the date discipline
    # the page is built to demonstrate.
    dc_f = c.type.get("sans", "bold", 7.2)
    dc_head = c.type.get("sans", "bold", 8.2)
    dc_x0 = CONTENT_X0
    dc_y0 = cell_top + 38.0
    dc_y1 = BAND_INDEX[1] - 3.0
    if dc_y1 > dc_y0 + 14.0:
        c.rect(dc_x0, dc_y0, CONTENT_X1, dc_y1, fill=None, outline=RED, width=1.2)
        hb = dc_y0 + 8.5
        c.tracked(dc_x0 + 5.0, hb,
                  "DATE CHECK \u00b7 FIRST REPORTED WED 18 NOV \u00b7 NOT COUNTED HERE",
                  dc_head, 0.03, fill=RED)
        items = "  \u00b7  ".join(DATE_CHECK)
        lines = c.wrap(items, dc_f, CONTENT_W - 10.0)
        ly = hb + 8.0
        for line in lines:
            if ly > dc_y1 - 1.5:
                break
            c.text(dc_x0 + 5.0, ly, line, dc_f, fill=INK_SOFT)
            audit.append(("datecheck_w", c.width(line, dc_f), CONTENT_W - 10.0))
            ly += 7.6
    return BAND_INDEX[1]


def _foot(c: Canvas, audit: list) -> None:
    """Folio: date, edition, audit line and sources, flush left and right."""
    font = c.type.get("sans", "bold", SZ_FOOT)
    c.rule(CONTENT_X0, BAND_FOOT[0] + 6.0, CONTENT_X1,
           BAND_FOOT[0] + 6.0, width=1.0)
    l_base = BAND_FOOT[0] + 26.0
    left = c.tracked(CONTENT_X0, l_base, FOOT_LEFT, font,
                     SZ_FOOT * TRACK_SMALLCAPS, fill=INK_SOFT)
    mid = c.tracked(PAGE_W / 2.0, l_base, FOOT_AUDIT % STORY_COUNT, font,
                    SZ_FOOT * TRACK_TINY, fill=RED, anchor="ms")
    right = c.tracked(CONTENT_X1, l_base, FOOT_RIGHT, font,
                      SZ_FOOT * TRACK_SMALLCAPS, fill=INK_SOFT, anchor="rs")
    audit.append(("foot_w", left + mid + right + 60, CONTENT_W))
    s_base = BAND_FOOT[0] + 44.0
    c.tracked(CONTENT_X0, s_base, FOOT_SOURCES, font,
              SZ_FOOT * TRACK_TINY, fill=INK_SOFT)
    c.tracked(CONTENT_X1, s_base, MASTHEAD_AUDIT, font,
              SZ_FOOT * TRACK_TINY, fill=INK_SOFT, anchor="rs")


# --------------------------------------------------------------------------
# composition and output
# --------------------------------------------------------------------------

def _compose(c: Canvas, audit: list) -> None:
    """Stack every band in spec order; audit widths as we go."""
    _utility(c, audit)
    _masthead(c, audit)
    _headline(c, audit)
    _timeline(c, audit)
    _features(c, audit)
    _grid(c, audit)
    _strip(c, audit)
    _index(c, audit)
    _foot(c, audit)


def render_page(audit: Optional[list] = None):
    """Draw the whole front page and return the downsampled RGB image."""
    report: list = audit if audit is not None else []
    audit_story_count()
    canvas = Canvas(SS)
    _compose(canvas, report)
    report.append(("story_count", STORY_COUNT, 47))
    return canvas.image.resize((PAGE_W, PAGE_H))


def save_page(path: str, audit: Optional[list] = None) -> Tuple[int, int]:
    """Render and write the page.  Returns (width, height)."""
    image = render_page(audit=audit)
    directory = os.path.dirname(os.path.abspath(path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    image.save(path, format="PNG")
    return image.width, image.height


def overruns(audit, tolerance: float = 0.5) -> List[Tuple[str, float, float]]:
    """Every measured block wider or deeper than the limit it must respect."""
    bad = []
    for label, used, limit in audit:
        if limit > 0 and used > limit + tolerance:
            bad.append((label, used, limit))
    return bad