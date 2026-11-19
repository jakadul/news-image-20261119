"""A one-image summary of Thursday 19 November 2026, drawn with the standard
library only: a colour-coded infographic rather than a broadsheet.

Five stacked zones carry the page — a poster-scale date, a seven-segment region
ribbon, three illustrated lead cards, an eight-card brief grid, then a map and
a two-column brief list above a red date-check box.  Every figure lives in the
data below; the renderer only measures and paints.

Fonts resolve from the repository's own ``fonts`` directory first, so the page
renders identically inside an offline container with no system fonts installed.

Public API
----------
render_page(audit=None)   -> image, RGB, 1200 x 1600
save_page(path, audit=None)
overruns(audit)           -> rows wider than the measure they were fitted to
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from canvas import Canvas as _Raster, downsample, write_png
from textadapter import PageCanvas, Type as _TypeBase

# --------------------------------------------------------------------------
# page geometry, in design pixels
# --------------------------------------------------------------------------

PAGE_W = 1200
PAGE_H = 1600
OUT_W = 768
OUT_H = 1024
SS = 4                                   # supersample factor for the raster

MARGIN_X = 40
CONTENT_X0 = float(MARGIN_X)
CONTENT_X1 = float(PAGE_W - MARGIN_X)
CONTENT_W = CONTENT_X1 - CONTENT_X0

# --------------------------------------------------------------------------
# palette: warm newsprint, charcoal ink, one spot red, seven region hues
# --------------------------------------------------------------------------

PAPER = (253, 252, 240)
INK = (26, 26, 26)
INK_SOFT = (74, 74, 74)
INK_FAINT = (108, 106, 100)
RED = (192, 57, 43)
RULE = (216, 210, 192)
MAP_BG = (232, 224, 213)
MAP_LAND = (207, 197, 180)

TAG_CONFIRM_BG = (214, 230, 208)
TAG_CLAIM_BG = (192, 57, 43)
TAG_REPORT_BG = (232, 228, 216)
TAG_CLAIM_INK = (250, 246, 236)
TAG_REPORT_INK = (96, 92, 84)

REGION_COLOURS = {
    "EUROPE": (43, 92, 138),
    "AMERICAS": (74, 124, 89),
    "ASIA-PACIFIC": (192, 57, 43),
    "MIDDLE EAST": (211, 84, 0),
    "AFRICA": (108, 52, 131),
    "OCEANIA": (22, 160, 133),
    "WORLD": (127, 140, 141),
}

# --------------------------------------------------------------------------
# fonts: bundled with the repository, resolved relative to this file
# --------------------------------------------------------------------------

_FONT_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
    "/usr/local/share/fonts",
)

_FONT_FILES = {
    ("serif", "regular"): ("LiberationSerif-Regular.ttf",),
    ("serif", "bold"): ("LiberationSerif-Bold.ttf",),
    ("serif", "italic"): ("LiberationSerif-Italic.ttf",),
    ("serif", "bolditalic"): ("LiberationSerif-BoldItalic.ttf",),
    ("sans", "regular"): ("LiberationSans-Regular.ttf",),
    ("sans", "bold"): ("LiberationSans-Bold.ttf",),
    ("sans", "italic"): ("LiberationSans-Italic.ttf",),
    ("narrow", "bold"): ("LiberationSansNarrow-Bold.ttf",),
    ("narrow", "regular"): ("LiberationSansNarrow-Regular.ttf",),
}


def _resolve_font(family: str, style: str) -> Optional[str]:
    """First existing candidate file for a family/style, or None."""
    for name in _FONT_FILES.get((family, style), ()):
        for directory in _FONT_DIRS:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


class Type(_TypeBase):
    """Font cache.  Sizes are design pixels; faces are built at SS x size."""

    def __init__(self, scale: int) -> None:
        super().__init__(scale, _resolve_font)


class Canvas(PageCanvas):
    """The page's drawing surface: stdlib raster, TrueType text."""

    def __init__(self, scale: int) -> None:
        super().__init__(scale, PAGE_W, PAGE_H, PAPER, INK, _resolve_font)


# --------------------------------------------------------------------------
# the day's content
# --------------------------------------------------------------------------

DAY_TITLE = ("Thursday 19", "November 2026")
DAY_STRAP = "THURSDAY'S NEWS \u00b7 ONE PAGE \u00b7 7 REGIONS"
LEAD_SUB = (
    "Three leaders meet in Shenzhen as Iran strikes across the Gulf; GTA VI "
    "arrives after a 13-year wait; Anthropic completes the largest listing on "
    "record."
)

RIBBON = (
    ("EUROPE", "$81.3bn", "raised by Anthropic, the largest IPO on record"),
    ("AMERICAS", "15.9m", "GTA VI pre-orders banked before launch day"),
    ("ASIA-PACIFIC", "200,000", "evacuated ahead of Cyclone Akvan"),
    ("MIDDLE EAST", "3rd", "US carrier arrives as Iran strikes Kuwait bases"),
    ("AFRICA", "11,000", "Ebola cases in Congo, six months uncontrolled"),
    ("OCEANIA", "1 day", "light-travel time out to Voyager 1"),
    ("WORLD", "47", "stories, every one dated to this Thursday"),
)

HEROES = (
    ("summit", "Trump, Xi and Putin hold first three-way summit",
     "Arms control and the Gulf war top the agenda in Shenzhen; Kyiv watches "
     "a peace it was not invited to shape."),
    ("games", "GTA VI arrives after a 13-year wait",
     "Unlocks at midnight country by country, New Zealand first; 15.9m "
     "pre-orders banked at $79.99."),
    ("markets", "Anthropic debuts in the biggest IPO on record",
     "Priced above range, raising $81.3bn at a valuation near $1.5tn; first "
     "trades set the real price."),
)

BRIEFS = (
    ("The Hague \u00b7 Law", "World Court rules on Myanmar's Rohingya case",
     "The ICJ reads its judgment in The Gambia's case over the 2017 campaign."),
    ("Antalya \u00b7 Climate", "COP31 enters its final 48 hours",
     "Ministers take over the text; phase-out and the $120bn adaptation fund "
     "still open."),
    ("Odisha \u00b7 Storm", "Akvan bears down as 200,000 flee the coast",
     "Red alerts in 11 districts, schools shut; landfall near Puri due Friday."),
    ("Kyiv \u00b7 War", "Left off the agenda, Ukraine watches Shenzhen",
     "The war will not be raised at the summit, the White House says."),
    ("Shenzhen \u00b7 Trade", "APEC leaders adopt the Shenzhen Declaration",
     "Twenty-one economies back digital trade and an Asia-Pacific roadmap."),
    ("Florida \u00b7 Weather", "Flooded Florida braces for still more rain",
     "A foot of rain in Hollywood; 300 rescue calls in a single night."),
    ("Science \u00b7 Geology", "Earth's missing billion years are explained",
     "A Nature study blames mantle currents and ancient ice sheets."),
    ("Paris \u00b7 Politics", "Melenchon could win, says justice minister",
     "The hard-left star is a plausible president, the minister concedes."),
)

MORE = (
    ("Gaza", "Israeli tanks cross the Yellow Line in a rare raid; Hamas calls "
             "it a truce breach."),
    ("Crimea", "Bridge attacked again; traffic halted, Russian officials say."),
    ("Kuwait", "Iran strikes US bases; air defences intercept drones, CENTCOM "
               "reports no casualties."),
    ("London", "Van Gogh sells for a record $190.4m after a row over its history."),
    ("Mexico City", "Banxico minutes: board cut rates to 0.25% on a 3-2 vote."),
    ("Canberra", "Australia sanctions West Bank settlers, three people and four "
                 "groups."),
    ("Mogadishu", "Somalia accuses the UAE of secret military bases on its soil."),
    ("Frankfurt", "Deutsche Bank bond handled $582bn in Epstein-linked deals, "
                  "the FT reports."),
    ("Washington", "Senators warn AI cyber threats are outpacing defences."),
    ("Ottawa", "Carney rethinks China ties, seeking the right US deal."),
    ("New Delhi", "Modi returns from the Manila ASEAN summit."),
    ("Tokyo", "India and Japan review defence ties at their 2+2 dialogue."),
    ("Bengaluru", "Amazon pledges $7bn for renewables in India by 2030."),
    ("Sydney", "Duckers 133 puts England in charge of the third ODI."),
    ("Baghdad", "Six ISIL members jailed for life in an Iraqi court."),
    ("Nairobi", "Kenya floods kill six as Ruto gives his state of the nation "
                "address."),
    ("Caracas", "Hegseth signs a US-Venezuela military deal."),
    ("Manama", "Bapco refinery back on its feet after the attacks."),
    ("Riyadh", "Gulf leaders urge Trump not to strike Iran."),
    ("Sacramento", "California braces for an atmospheric river."),
    ("La Paz", "Bolivia declares an El Nino emergency; 78,000 families hit."),
    ("Kumamoto", "M5.7 quake strikes Japan; no tsunami warning issued."),
    ("Manila", "ASEAN summit closes with a supply-chain pact signed."),
    ("Brussels", "EU weighs a 45bn-euro loan package for Ukraine."),
    ("Tehran", "Army chief vows a more crushing response if struck again."),
    ("Kinshasa", "WHO: Ebola passes six months with 11,000 infected."),
    ("Accra", "Ghana's $60m presidential jet sparks public outrage."),
    ("Freetown", "Sierra Leone summit signs four regional agreements."),
    ("New York", "Dow closes -561 at -1.11%; Nvidia -2.4% post-earnings."),
    ("Sao Paulo", "Latin America presses for critical-minerals investment."),
    ("Jakarta", "Indonesia and Sweden launch LeadIT 3.0 at COP31."),
    ("Berlin", "DAX closes -1.19% as mining stocks drag Europe lower."),
)

FOOT_LEFT = "THE WORLD IN ONE DAY \u2014 19 NOVEMBER 2026"
FOOT_SOURCES = ("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 THE HINDU "
                "\u00b7 IMD \u00b7 NASA \u00b7 ICJ")

# --------------------------------------------------------------------------
# measures shared by the cards
# --------------------------------------------------------------------------

HERO_GAP = 18.0
HERO_W = (CONTENT_W - 2 * HERO_GAP) / 3.0
BRIEF_COLS = 4
BRIEF_W = CONTENT_W / BRIEF_COLS
MAP_W = 340.0
MORE_W = CONTENT_W - MAP_W - 22.0


def story_count() -> int:
    """Stories counted from the card lists, never typed by hand."""
    return len(HEROES) + len(BRIEFS) + len(MORE)


TIMELINE = (
    ('00:30', 'Israel strikes kill two Hamas platoon commanders in Gaza', 'IDF / XINHUA'),
    ('04:00', 'Iran fires at US bases in Kuwait; air defences intercept drones', 'AP / KUWAIT ARMY'),
    ('07:39', 'Xi Jinping APEC speech: uphold open regionalism, free trade', 'XINHUA'),
    ('09:00', 'Takaichi–Xi handshake at APEC; first Japan–China leader contact in a year', 'KYODO'),
    ('DAY', 'Democrats nominate Hakeem Jeffries for first Black House speaker', 'AP'),
    ('EVE', 'Dow closes −561 (−1.11%); Nvidia −2.4% post-earnings', 'BLOOMBERG'),
)

FEATURES = (
    ('TRILATERAL', 'Trump–Xi–Putin meet in Shenzhen; Ukraine fears a deal without Kyiv',
     'CONFIRMED', 'AP / KYODO'),
    ('GULF WAR', 'Iran strikes US air base in Kuwait; third carrier arrives',
     'CONFIRMED', 'CENTCOM / AP'),
    ('US MIDTERMS', 'Peltola flips Alaska; Democrats take Senate 56–44',
     'CONFIRMED', 'SCMP / XINHUA'),
    ('IRAN ARMS', 'Trump vows to wipe out Iran over chemical-biological push',
     'CONFIRMED', 'AXIOS / JPOST'),
)

GRID = (
    ('MIDDLE EAST · WAR', 'Iran army chief vows more crushing response',
     'CLAIM', 'AP'),
    ('MIDDLE EAST · WAR', 'Houthis target Riyadh as coalition intercepts',
     'REPORTED', 'AL JAZEERA'),
    ('MIDDLE EAST · DIPLOMACY', 'Mediation shows no breakthrough; Iran hardens',
     'REPORTED', 'YNET'),
    ('MIDDLE EAST · WAR', 'US–Iran trade threats over dirty bombs',
     'REPORTED', 'SCMP'),
    ('EUROPE · UKRAINE', 'Zelensky: war could end in one meeting',
     'CONFIRMED', 'AP'),
    ('EUROPE · UKRAINE', 'Russia asks Netherlands if it joined the conflict',
     'CONFIRMED', 'GUARDIAN'),
    ('EUROPE · UKRAINE', 'European leaders worry on Ukraine-free deal',
     'REPORTED', 'KYODO'),
    ('ASIA · DIPLOMACY', 'Xi–Putin hold talks in Shenzhen before trilateral',
     'CONFIRMED', 'THE HINDU'),
    ('ASIA · DIPLOMACY', 'Takaichi–Putin first dialogue, 30 minutes',
     'CONFIRMED', 'KYODO'),
    ('ASIA · TRADE', 'Xi APEC keynote: protectionism is rampant',
     'CONFIRMED', 'KYODO'),
    ('ASIA · ECONOMY', 'Japan weighs new EV tax from May 2028',
     'REPORTED', 'KYODO'),
    ('ASIA · DISASTER', 'M5.7 earthquake strikes Kumamoto, Japan',
     'CONFIRMED', 'JMA'),
    ('AMERICAS · POLITICS', 'House Democrats nominate Jeffries for speaker',
     'CONFIRMED', 'XINHUA / AP'),
    ('AMERICAS · POLITICS', 'Trump grows frustrated with Vance on Iran',
     'REPORTED', 'NYT'),
    ('AMERICAS · DIPLOMACY', 'US–Venezuela restore military ties after capture',
     'CONFIRMED', 'WSJ / AP'),
    ('AMERICAS · POLITICS', 'Ecuador–US fishermen dispute escalates',
     'REPORTED', 'AGP'),
    ('AFRICA · HEALTH', 'WHO: Congo Ebola past 6 months, 11,000+ cases',
     'CONFIRMED', 'WHO'),
    ('AFRICA · POLITICS', "Ghana's new $60m presidential jet sparks outrage",
     'REPORTED', 'BBC'),
    ('GLOBAL · MARKETS', 'Dow −561; FTSE −1.30%; Nasdaq +0.42%',
     'CONFIRMED', 'BLOOMBERG'),
    ('GLOBAL · MARKETS', 'Nvidia −2.4% after quarterly results',
     'CONFIRMED', 'BLOOMBERG'),
    ('GLOBAL · MARKETS', 'Oil slides; WTI −3.21% on diplomacy hopes',
     'CONFIRMED', 'REUTERS'),
)

STRIP_ITEMS = (
    ('GLOBAL · MARKETS', 'Anthropic IPO debuts; stocks struggle to sustain gains',
     'CONFIRMED', 'BLOOMBERG'),
    ('GLOBAL · TRADE', 'China rare-earth curbs focus Latin American investment',
     'REPORTED', 'BLOOMBERG'),
    ('EUROPE · CLIMATE', 'COP31 in Antalya splits over fossil-fuel phase-out',
     'REPORTED', 'AL JAZEERA'),
    ('MIDDLE EAST · WAR', 'Israel strikes kill 5 in Gaza despite truce',
     'CONFIRMED', 'AL JAZEERA'),
    ('ASIA · DIPLOMACY', 'Modi returns to New Delhi after Manila ASEAN summit',
     'CONFIRMED', 'TIMES OF INDIA'),
    ('AMERICAS · POLITICS', 'House Democrats flip 40+ seats: 250+ in Congress',
     'CONFIRMED', 'XINHUA'),
    ('GLOBAL · HEALTH', 'US measles: Pennsylvania unvaccinated resident dies',
     'CONFIRMED', 'PA DOH'),
    ('GLOBAL · HEALTH', 'Cigarette smoking at historic lows; vaping persists',
     'CONFIRMED', 'CDC'),
    ('OCEANIA · ECONOMY', 'ASX set to extend losing streak; Kospi +2%',
     'REPORTED', 'AFR'),
    ('ASIA · TECH', 'Airport, bank, Apple and NSA outages reported Wednesday',
     'REPORTED', 'REUTERS'),
    ('AFRICA · DIPLOMACY', 'South Africa reprimands Nigerian envoy Fani-Kayode',
     'CONFIRMED', 'ALLAFRICA'),
    ('GLOBAL · SCIENCE', 'AHA and West Health collaborate with BD on data',
     'CONFIRMED', 'AHA'),
    ('AMERICAS · GAMES', 'GTA VI unlocks at midnight; 15.9m pre-orders banked',
     'CONFIRMED', 'ROCKSTAR'),
    ('GLOBAL · SOCIETY', "Children's Nobel Peace Prize awarded in the UK",
     'REPORTED', 'RTP'),
    ('GLOBAL · MARKETS', 'Anthropic prices at $83; $81.3bn raised, biggest IPO',
     'CONFIRMED', 'NASDAQ / FT'),
    ('AFRICA · DIPLOMACY', 'Sierra Leone summit: four agreements signed',
     'CONFIRMED', 'XINHUA'),
)

DATE_CHECK = (
    "Iranian drone interceptions over the Gulf",
    "the EU's proposed \u20ac45bn Ukraine loan",
    "the House Democrats' vote nominating Hakeem Jeffries",
    "Voyager 1 crossing one light-day at 10:16 GMT",
    "Peltola's Alaska call",
    "the first COP31 draft on Monday",
)

# --------------------------------------------------------------------------
# small drawing helpers
# --------------------------------------------------------------------------


def _tag(c: Canvas, x: float, baseline: float, kind: str,
         size: float = 7.2) -> float:
    """A verification chip; returns the width it consumed."""
    bg, ink = {
        "CONFIRMED": (TAG_CONFIRM_BG, INK),
        "CLAIM": (TAG_CLAIM_BG, TAG_CLAIM_INK),
        "REPORTED": (TAG_REPORT_BG, TAG_REPORT_INK),
    }[kind]
    font = c.type.get("sans", "bold", size)
    tracking = size * 0.05
    width = c.tracked_width(kind, font, tracking)
    pad_x, pad_y = 3.2, 1.8
    top = baseline - c.cap_height(font) - pad_y
    c.rect(x, top, x + width + pad_x * 2, baseline + pad_y, fill=bg)
    c.tracked(x + pad_x, baseline, kind, font, tracking, fill=ink)
    return width + pad_x * 2


def _hrule(c: Canvas, y: float, width: float = 1.0, colour=INK) -> None:
    c.rule(CONTENT_X0, y, CONTENT_X1, y, width=width, fill=colour)


# --------------------------------------------------------------------------
# zone 1: strapline and poster-scale date
# --------------------------------------------------------------------------


def _masthead(c: Canvas, audit: list) -> float:
    """Strapline, double rule, then the date at poster scale."""
    top = 34.0
    strap = c.type.get("sans", "bold", 12.5)
    left = c.tracked(CONTENT_X0, top, "THE WORLD IN ONE DAY", strap, 1.4,
                     fill=INK)
    audit.append(("strap_left", left, CONTENT_W))
    right = c.tracked(CONTENT_X1, top, DAY_STRAP, strap, 1.4, fill=INK_FAINT,
                      anchor="rs")
    audit.append(("strap_right", right, CONTENT_W))

    rule_y = top + 9.0
    _hrule(c, rule_y, width=2.0)

    size = 116.0
    display = c.type.get("serif", "bold", size)
    while size > 44.0 and max(c.width(line, display) for line in DAY_TITLE) > CONTENT_W:
        size -= 2.0
        display = c.type.get("serif", "bold", size)

    baseline = rule_y + 18.0 + c.cap_height(display)
    for line in DAY_TITLE:
        width = c.width(line, display)
        c.text(CONTENT_X0, baseline, line, display, fill=INK)
        audit.append(("day_line", width, CONTENT_W))
        baseline += size * 0.94

    sub_font = c.type.get("serif", "italic", 19.0)
    sub_y = baseline - size * 0.94 + 14.0 + c.cap_height(sub_font)
    for line in c.wrap(LEAD_SUB, sub_font, CONTENT_W)[:2]:
        c.text(CONTENT_X0, sub_y, line, sub_font, fill=INK_SOFT)
        audit.append(("lead_sub", c.width(line, sub_font), CONTENT_W))
        sub_y += 19.0
    return sub_y + 4.0


# --------------------------------------------------------------------------
# zone 2: seven-segment region ribbon
# --------------------------------------------------------------------------


def _ribbon(c: Canvas, top: float, audit: list) -> float:
    height = 96.0
    seg_w = CONTENT_W / 7.0
    c.rect(CONTENT_X0, top, CONTENT_X1, top + height, outline=INK, width=2.0)
    lab_font = c.type.get("sans", "bold", 11.5)
    big_font = c.type.get("sans", "bold", 30.0)
    cap_font = c.type.get("sans", "regular", 9.4)

    for i, (name, figure, caption) in enumerate(RIBBON):
        x0 = CONTENT_X0 + i * seg_w
        c.rect(x0 + 1.0, top + 2.0, x0 + seg_w - 1.0, top + height - 2.0,
               fill=REGION_COLOURS[name])
        c.tracked(x0 + 6.0, top + 14.0, name, lab_font, 0.4, fill=PAPER)
        c.text(x0 + 6.0, top + 37.0, figure, big_font, fill=PAPER)
        cap_y = top + 50.0
        for line in c.wrap(caption, cap_font, seg_w - 12.0)[:2]:
            c.text(x0 + 6.0, cap_y, line, cap_font, fill=PAPER)
            audit.append(("ribbon_cap", c.width(line, cap_font), seg_w - 12.0))
            cap_y += 8.0
    return top + height


# --------------------------------------------------------------------------
# zone 3: three illustrated lead cards
# --------------------------------------------------------------------------


def _hero_art(c: Canvas, kind: str, x0: float, y0: float, w: float,
              h: float) -> None:
    """A flat vector illustration for one lead card, primitives only."""
    if kind == "summit":
        c.rect(x0, y0, x0 + w, y0 + h, fill=(239, 234, 217))
        slot = w / 3.0
        for i, (label, colour, ratio) in enumerate(
                (("US", REGION_COLOURS["EUROPE"], 0.52),
                 ("CN", REGION_COLOURS["ASIA-PACIFIC"], 0.70),
                 ("RU", REGION_COLOURS["AMERICAS"], 0.44))):
            bx = x0 + i * slot + slot * 0.24
            bw = slot * 0.52
            bh = h * ratio
            c.rect(bx, y0 + h - bh, bx + bw, y0 + h, fill=colour)
            flag = c.type.get("sans", "bold", 7.6)
            c.text(bx + bw / 2.0, y0 + h - bh + 11.0, label, flag, fill=PAPER,
                   anchor="ms")
    elif kind == "games":
        c.rect(x0, y0, x0 + w, y0 + h, fill=(27, 18, 51))
        c.dot(x0 + w * 0.72, y0 + h * 0.58, h * 0.19, fill=(243, 156, 18))
        c.rect(x0, y0 + h * 0.70, x0 + w, y0 + h, fill=(18, 11, 36))
        for offset, ratio in ((0.06, 0.42), (0.17, 0.60), (0.28, 0.34),
                              (0.84, 0.48)):
            tx = x0 + w * offset
            tw = w * 0.075
            th = h * ratio
            c.rect(tx, y0 + h - th, tx + tw, y0 + h, fill=(58, 35, 97))
        neon = c.type.get("sans", "bold", 14.0)
        c.text(x0 + w * 0.36, y0 + h * 0.42, "VICE CITY", neon,
               fill=(255, 62, 165))
    else:
        c.rect(x0, y0, x0 + w, y0 + h, fill=(14, 43, 34))
        steps = 7
        points = []
        for i in range(steps + 1):
            px = x0 + w * (0.05 + 0.90 * i / steps)
            py = y0 + h * (0.84 - 0.70 * (i / steps) ** 0.75)
            points.append((px, py))
        for i in range(len(points) - 1):
            c.rule(points[i][0], points[i][1], points[i + 1][0],
                   points[i + 1][1], width=3.0, fill=(46, 204, 113))
        c.dot(points[-1][0], points[-1][1], 4.5, fill=(46, 204, 113))
        mark = c.type.get("sans", "bold", 13.0)
        c.text(x0 + w * 0.06, y0 + h * 0.26, "ANT", mark, fill=(46, 204, 113))
        price = c.type.get("sans", "bold", 15.0)
        c.text(x0 + w * 0.94, y0 + h * 0.84, "$83", price, fill=PAPER,
               anchor="rs")


def _heroes(c: Canvas, top: float, audit: list) -> float:
    art_h = 190.0
    num_font = c.type.get("serif", "bold", 38.0)
    head_font = c.type.get("serif", "bold", 25.0)
    body_font = c.type.get("sans", "regular", 11.8)
    deepest = top

    for i, (kind, headline, body) in enumerate(HEROES):
        x0 = CONTENT_X0 + i * (HERO_W + HERO_GAP)
        c.rule(x0, top, x0 + HERO_W, top, width=3.0, fill=INK)
        art_top = top + 7.0
        _hero_art(c, kind, x0, art_top, HERO_W, art_h)

        y = art_top + art_h + 8.0
        c.text(x0, y + 20.0, str(i + 1), num_font, fill=RED)

        head_y = y + 20.0 + c.cap_height(head_font) + 3.0
        for line in c.wrap(headline, head_font, HERO_W)[:3]:
            c.text(x0, head_y, line, head_font, fill=INK)
            audit.append(("hero_head", c.width(line, head_font), HERO_W))
            head_y += 19.0

        body_y = head_y + 2.0
        for line in c.wrap(body, body_font, HERO_W)[:4]:
            c.text(x0, body_y, line, body_font, fill=INK_SOFT)
            audit.append(("hero_body", c.width(line, body_font), HERO_W))
            body_y += 10.6
        deepest = max(deepest, body_y)
    return deepest + 6.0


# --------------------------------------------------------------------------
# zone 4: eight-card brief grid
# --------------------------------------------------------------------------


def _briefs(c: Canvas, top: float, audit: list) -> float:
    kicker_font = c.type.get("sans", "bold", 10.0)
    head_font = c.type.get("serif", "bold", 17.0)
    body_font = c.type.get("sans", "regular", 10.4)
    rows = (len(BRIEFS) + BRIEF_COLS - 1) // BRIEF_COLS
    cell_h = 118.0
    _hrule(c, top, width=2.0)

    for i, (kicker, headline, body) in enumerate(BRIEFS):
        col = i % BRIEF_COLS
        row = i // BRIEF_COLS
        x0 = CONTENT_X0 + col * BRIEF_W
        y0 = top + row * cell_h
        c.rect(x0, y0, x0 + BRIEF_W, y0 + cell_h, outline=RULE, width=0.8)
        c.tracked(x0 + 7.0, y0 + 14.0, kicker.upper(), kicker_font, 0.4,
                  fill=RED)
        y = y0 + 14.0 + c.cap_height(head_font) + 3.0
        for line in c.wrap(headline, head_font, BRIEF_W - 14.0)[:3]:
            c.text(x0 + 7.0, y, line, head_font, fill=INK)
            audit.append(("brief_head", c.width(line, head_font), BRIEF_W - 14.0))
            y += 13.5
        for line in c.wrap(body, body_font, BRIEF_W - 14.0)[:3]:
            c.text(x0 + 7.0, y, line, body_font, fill=INK_SOFT)
            audit.append(("brief_body", c.width(line, body_font), BRIEF_W - 14.0))
            y += 9.2
    return top + rows * cell_h


# --------------------------------------------------------------------------
# zone 5: map, brief list, date check, footer
# --------------------------------------------------------------------------


def _map(c: Canvas, x0: float, y0: float, w: float, h: float) -> None:
    """A stylised world: six muted landmasses, three numbered red markers."""
    c.rect(x0, y0, x0 + w, y0 + h, fill=MAP_BG)
    for shape in (
        ((0.05, 0.24), (0.17, 0.16), (0.27, 0.22), (0.28, 0.38), (0.22, 0.52),
         (0.15, 0.50), (0.10, 0.38)),
        ((0.23, 0.58), (0.29, 0.56), (0.32, 0.70), (0.28, 0.88), (0.24, 0.80),
         (0.22, 0.68)),
        ((0.44, 0.18), (0.55, 0.15), (0.58, 0.25), (0.52, 0.33), (0.45, 0.31)),
        ((0.46, 0.37), (0.56, 0.35), (0.58, 0.51), (0.54, 0.68), (0.48, 0.63),
         (0.45, 0.50)),
        ((0.59, 0.16), (0.82, 0.13), (0.88, 0.28), (0.85, 0.46), (0.72, 0.51),
         (0.62, 0.40)),
        ((0.80, 0.68), (0.90, 0.65), (0.92, 0.77), (0.86, 0.85), (0.80, 0.79)),
    ):
        c.polygon([(x0 + px * w, y0 + py * h) for px, py in shape],
                  outline=None, fill=MAP_LAND)

    marker = c.type.get("sans", "bold", 6.6)
    for number, (mx, my) in enumerate(((0.18, 0.37), (0.35, 0.45),
                                       (0.68, 0.31)), start=1):
        c.dot(x0 + mx * w, y0 + my * h, 6.0, fill=RED)
        c.text(x0 + mx * w, y0 + my * h + 2.3, str(number), marker, fill=PAPER,
               anchor="ms")
    for mx, my in ((0.61, 0.40), (0.52, 0.52), (0.86, 0.74)):
        c.dot(x0 + mx * w, y0 + my * h, 3.2, fill=(138, 138, 138))


def _bottom(c: Canvas, top: float, audit: list) -> float:
    head_font = c.type.get("sans", "bold", 8.2)
    city_font = c.type.get("sans", "bold", 7.0)
    body_font = c.type.get("sans", "regular", 7.0)
    _hrule(c, top, width=2.0)

    map_top = top + 12.0
    c.tracked(CONTENT_X0, map_top, "WHERE IT HAPPENED", head_font, 0.6, fill=INK)
    _map(c, CONTENT_X0, map_top + 8.0, MAP_W, 146.0)
    note = c.type.get("sans", "regular", 6.6)
    c.text(CONTENT_X0, map_top + 168.0,
           "Red numbers mark the lead stories; grey dots the briefs.", note,
           fill=INK_FAINT)

    list_x = CONTENT_X0 + MAP_W + 22.0
    c.tracked(list_x, map_top,
              "ALSO ON THURSDAY \u2014 %d MORE STORIES" % len(MORE),
              head_font, 0.6, fill=INK)

    column_w = (MORE_W - 16.0) / 2.0
    per_column = (len(MORE) + 1) // 2
    row_h = 19.0
    start_y = map_top + 18.0
    for i, (city, text) in enumerate(MORE):
        col = i // per_column
        row = i % per_column
        x0 = list_x + col * (column_w + 16.0)
        line_y = start_y + row * row_h
        label = city.upper()
        c.tracked(x0, line_y, label, city_font, 0.35, fill=RED)
        text_x = x0 + c.tracked_width(label, city_font, 0.35) + 4.0
        room = column_w - (text_x - x0)
        for line in c.wrap(text, body_font, room)[:2]:
            c.text(text_x, line_y, line, body_font, fill=INK_SOFT)
            audit.append(("more_line", c.width(line, body_font), room))
            line_y += 8.2
    return max(map_top + 178.0, start_y + per_column * row_h)


def _date_check(c: Canvas, top: float, audit: list) -> float:
    head_font = c.type.get("sans", "bold", 8.0)
    body_font = c.type.get("sans", "regular", 7.4)
    lines = c.wrap(" \u00b7 ".join(DATE_CHECK), body_font, CONTENT_W - 20.0)
    height = 14.0 + 10.0 + len(lines) * 9.0 + 3.0
    c.rect(CONTENT_X0, top, CONTENT_X1, top + height, outline=RED, width=1.6)
    c.tracked(CONTENT_X0 + 9.0, top + 12.0,
              "DATE CHECK \u00b7 FIRST REPORTED WEDNESDAY 18 NOV \u00b7 NOT "
              "COUNTED HERE", head_font, 0.5, fill=RED)
    y = top + 24.0
    for line in lines:
        c.text(CONTENT_X0 + 9.0, y, line, body_font, fill=INK_SOFT)
        audit.append(("date_check", c.width(line, body_font), CONTENT_W - 20.0))
        y += 9.0
    return top + height


def _foot(c: Canvas, top: float, audit: list) -> float:
    font = c.type.get("sans", "bold", 7.2)
    _hrule(c, top, width=2.0)
    baseline = top + 14.0
    left = c.tracked(CONTENT_X0, baseline, FOOT_LEFT, font, 0.4, fill=INK_SOFT)
    mid = c.tracked(PAGE_W / 2.0, baseline,
                    "%d STORIES \u00b7 7 REGIONS" % story_count(), font, 0.4,
                    fill=RED, anchor="ms")
    right = c.tracked(CONTENT_X1, baseline, FOOT_SOURCES, font, 0.35,
                      fill=INK_FAINT, anchor="rs")
    audit.append(("foot_width", left + mid + right + 80.0, CONTENT_W))
    return baseline + 10.0


# --------------------------------------------------------------------------
# composition and output
# --------------------------------------------------------------------------


def _compose(c: Canvas, audit: list) -> None:
    """Stack the zones in reading order, auditing every measure."""
    y = _masthead(c, audit)
    y = _ribbon(c, y + 14.0, audit)
    y = _heroes(c, y + 16.0, audit)
    y = _briefs(c, y + 8.0, audit)
    y = _bottom(c, y + 12.0, audit)
    y = _date_check(c, y + 10.0, audit)
    _foot(c, y + 8.0, audit)


def render_page(audit: Optional[list] = None):
    """Draw the page, then fit it inside the contest's 1024-pixel cap.

    The page composes at PAGE_W x PAGE_H so the type is drawn at legible
    sizes, then a box filter reduces it to OUT_W x OUT_H: the gate allows at
    most 1024 by 1024 pixels and 1 MiB, so the output is 768 x 1024.
    """
    report: list = audit if audit is not None else []
    canvas = Canvas(SS)
    _compose(canvas, report)
    report.append(("story_count", story_count(), 47))
    page = downsample(canvas.canvas, SS)   # PAGE_W x PAGE_H raster
    return _fit(page, OUT_W, OUT_H)


def _fit(page, out_w: int, out_h: int):
    """Integer box filter from the composed page to the output raster."""
    src_w, src_h = page.w, page.h
    src = page.buf
    out = _Raster(out_w, out_h, scale=1, background=PAPER)
    dst = out.buf
    xr = src_w / float(out_w)
    yr = src_h / float(out_h)
    for y in range(out_h):
        y0 = int(y * yr)
        y1 = min(src_h, max(y0 + 1, int((y + 1) * yr)))
        row_out = y * out_w * 3
        for x in range(out_w):
            x0 = int(x * xr)
            x1 = min(src_w, max(x0 + 1, int((x + 1) * xr)))
            r = g = b = 0
            n = 0
            for sy in range(y0, y1):
                base = (sy * src_w) * 3
                for sx in range(x0, x1):
                    i = base + sx * 3
                    r += src[i]
                    g += src[i + 1]
                    b += src[i + 2]
                    n += 1
            o = row_out + x * 3
            dst[o] = r // n
            dst[o + 1] = g // n
            dst[o + 2] = b // n
    return out


def save_page(path: str, audit: Optional[list] = None) -> Tuple[int, int]:
    """Render and write the page.  Returns (width, height)."""
    page = render_page(audit=audit)
    directory = os.path.dirname(os.path.abspath(path))
    if directory:
        os.makedirs(directory, exist_ok=True)
    write_png(path, page)
    return page.design_w, page.design_h


def overruns(audit, tolerance: float = 0.5) -> List[Tuple[str, float, float]]:
    """Every measured block wider than the limit it must respect."""
    return [row for row in audit if row[2] > 0 and row[1] > row[2] + tolerance]
