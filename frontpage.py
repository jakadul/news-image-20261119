"""One day of world news in one picture: Thursday 19 November 2026.

The page is a modular editorial infographic rather than a broadsheet: a black
strapline band, a poster-scale date with a red date box, a six-beat UTC
timeline, three illustrated lead cards, four secondary cards, then a world map
beside a two-column list of the day's remaining stories and a red date-check
footer.

Drawn with the standard library only, from the repository's bundled fonts, so
the program renders identically in an offline container. Every figure comes
from the data below; the renderer only measures and paints.

Public API
----------
render_page(audit=None)   -> RGB raster, 1024 x 1024
save_page(path, audit=None)
overruns(audit)
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from canvas import downsample, write_png
from textadapter import PageCanvas, Type as _TypeBase

# --------------------------------------------------------------------------
# page geometry: the contest caps an image at 1024 by 1024 pixels
# --------------------------------------------------------------------------

PAGE_W = 1024
PAGE_H = 1024
SS = 2

PAD_X = 22
CONTENT_X0 = float(PAD_X)
CONTENT_X1 = float(PAGE_W - PAD_X)
CONTENT_W = CONTENT_X1 - CONTENT_X0

# vertical bands, from the layout blueprint
BAND_STRAP = (0.0, 30.0)
BAND_MAST = (30.0, 140.0)
BAND_TIME = (140.0, 200.0)
BAND_ROW3 = (210.0, 462.0)
BAND_ROW4 = (472.0, 640.0)
BAND_MAP = (650.0, 950.0)
BAND_FOOT = (958.0, 1024.0)

# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------

PAPER = (244, 244, 244)
INK = (26, 26, 26)
MUTED = (90, 95, 102)
LINE = (201, 198, 190)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
DARK_RED = (139, 0, 0)
GOLD = (242, 193, 78)

EU = (31, 92, 139)
AM = (46, 125, 79)
AP = (178, 34, 34)
ME = (194, 94, 0)
AF = (107, 46, 143)
OC = (18, 121, 110)
WO = (62, 67, 74)

# --------------------------------------------------------------------------
# fonts
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
    for name in _FONT_FILES.get((family, style), ()):
        for directory in _FONT_DIRS:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


class Type(_TypeBase):
    def __init__(self, scale: int) -> None:
        super().__init__(scale, _resolve_font)


class Canvas(PageCanvas):
    def __init__(self, scale: int) -> None:
        super().__init__(scale, PAGE_W, PAGE_H, PAPER, INK, _resolve_font)


# --------------------------------------------------------------------------
# the day
# --------------------------------------------------------------------------

STRAP_LEFT = "ONE DAY OF WORLD NEWS \u00b7 ONE PICTURE"
STRAP_RIGHT = "%d STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE FROM THIS THURSDAY"
DAY_TITLE = "Thursday 19 November 2026"
DAY_SUB = ("Everything on this page happened, or was first reported, on Thursday "
           "19 November 2026: three leaders meet in Shenzhen, Iran strikes US "
           "bases in Kuwait, GTA VI ships after thirteen years, Anthropic "
           "completes the largest listing on record.")

TIMELINE = (
    ("00:30", "Israel strikes kill two Hamas commanders in Gaza", "IDF / Xinhua"),
    ("04:00", "Iran fires at US bases in Kuwait; drones intercepted", "AP / Kuwait Army"),
    ("07:39", "Xi opens APEC: open regionalism, free trade", "Xinhua"),
    ("09:00", "Takaichi and Xi shake hands at APEC", "Kyodo"),
    ("All day", "Jeffries nominated for first Black speaker", "AP"),
    ("Close", "Dow \u2212561 at \u22121.11%; Nvidia \u22122.4%", "Bloomberg"),
)

LEADS = (
    ("summit", "Asia \u00b7 Summit",
     "Trump, Xi and Putin hold the first three-way summit",
     "Arms control and the Gulf war top the agenda in Shenzhen; Kyiv watches a "
     "peace it was not invited to shape."),
    ("bridge", "Europe \u00b7 War",
     "Bridge attacked again as Ukraine watches from outside",
     "Traffic halted on the Kerch crossing; Kyiv fears a peace shaped without it "
     "as the Shenzhen talks open."),
    ("games", "Americas \u00b7 Games",
     "GTA VI arrives after a thirteen-year wait",
     "Unlocks at midnight country by country, New Zealand first; 15.9m "
     "pre-orders banked at $79.99."),
)

SECONDS = (
    ("court", "The Hague \u00b7 Law", "World Court rules on Myanmar's Rohingya case",
     "The ICJ reads its judgment in The Gambia's case."),
    ("ipo", "Americas \u00b7 IPO", "Anthropic debuts in the biggest IPO on record",
     "Priced above range, raising $81.3bn near a $1.5tn value."),
    ("gaza", "Middle East \u00b7 Gaza", "Israeli tanks cross the Yellow Line in a rare raid",
     "Hamas calls it a truce breach; strikes kill five despite the deal."),
    ("storm", "Asia \u00b7 Weather", "Cyclone Akvan bears down as 200,000 flee",
     "Red alerts in 11 districts; landfall near Puri due Friday."),
)

MORE = (
    ("Antalya", "COP31 enters its final 48 hours"),
    ("Shenzhen", "APEC adopts the Shenzhen Declaration"),
    ("Kuwait", "Iran strikes US bases; drones downed"),
    ("Kyiv", "left off the Shenzhen agenda"),
    ("Florida", "flooded, more rain coming"),
    ("Science", "Earth's missing billion years"),
    ("Paris", "Melenchon could win, minister says"),
    ("Jazan", "Saudi all-clear after missile downed"),
    ("Benghazi", "cocaine and pills seized"),
    ("London", "Van Gogh $190.4m record"),
    ("Mexico City", "Banxico cuts to 0.25%"),
    ("Canberra", "sanctions on settlers"),
    ("Mogadishu", "UAE bases claim"),
    ("Frankfurt", "$582bn in Epstein-linked deals"),
    ("Washington", "AI threats outpace defences"),
    ("Ottawa", "Carney rethinks China ties"),
    ("New Delhi", "Modi back from Manila"),
    ("Tokyo", "India-Japan 2+2 defence talks"),
    ("Bengaluru", "Amazon $7bn renewables"),
    ("Baghdad", "six ISIL jailed for life"),
    ("Nairobi", "floods kill six"),
    ("Caracas", "US military deal signed"),
    ("Manama", "Bapco refinery restarts"),
    ("Riyadh", "Gulf leaders urge restraint"),
    ("Sacramento", "atmospheric river warning"),
    ("La Paz", "El Nino emergency"),
    ("Kumamoto", "M5.7 quake, no tsunami"),
    ("Brussels", "45bn-euro Ukraine loan weighed"),
    ("New York", "Dow \u2212561, Nvidia \u22122.4%"),
)

DATE_CHECK = (
    "Gulf drone interceptions", "EU 45bn loan", "Jeffries nomination vote",
    "Voyager 1 light-day at 10:16 GMT", "Peltola's Alaska call",
    "first COP31 draft",
)

FOOT_SOURCES = ("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 KYODO "
                "\u00b7 XINHUA \u00b7 AL JAZEERA \u00b7 BLOOMBERG \u00b7 WHO \u00b7 ICJ")


def story_count() -> int:
    """Stories counted from the card lists: 6 timeline beats, 3 leads, 4 seconds, 29 more."""
    return len(TIMELINE) + len(LEADS) + len(SECONDS) + len(MORE)


# --------------------------------------------------------------------------
# drawing helpers
# --------------------------------------------------------------------------


def _cap(c: Canvas, size: float, style: str = "bold") -> object:
    return c.type.get("sans", style, size)


def _ser(c: Canvas, size: float, style: str = "bold") -> object:
    return c.type.get("serif", style, size)


def _box(c: Canvas, x0: float, y0: float, x1: float, y1: float,
         fill=None, outline=None, width: float = 1.0) -> None:
    c.rect(x0, y0, x1, y1, fill=fill, outline=outline, width=width)


def _text(c: Canvas, x: float, y: float, s: str, font, fill=INK,
          anchor: str = "ls") -> None:
    c.text(x, y, s, font, fill=fill, anchor=anchor)


def _wrap_lines(c: Canvas, s: str, font, width: float, limit: int) -> List[str]:
    return c.wrap(s, font, width)[:limit]


# --------------------------------------------------------------------------
# zone 1: black strapline band
# --------------------------------------------------------------------------


def _strap(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_STRAP
    _box(c, 0, y0, PAGE_W, y1, fill=INK)
    f = _cap(c, 8.4)
    base = y0 + (y1 - y0) / 2.0 + 3.0
    c.tracked(CONTENT_X0, base, STRAP_LEFT, f, 1.4, fill=WHITE)
    w = c.tracked_width(STRAP_RIGHT, f, 1.4)
    right = STRAP_RIGHT % story_count()
    w = c.tracked_width(right, f, 1.4)
    c.tracked(CONTENT_X1 - w, base, right, f, 1.4, fill=WHITE)
    audit.append(("strap", w, CONTENT_W))


# --------------------------------------------------------------------------
# zone 2: masthead with the red date box
# --------------------------------------------------------------------------


def _masthead(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_MAST
    box_w = 150.0
    text_w = CONTENT_W - box_w - 18.0

    h1 = _ser(c, 60.0)
    size = 60.0
    while size > 34.0 and c.width(DAY_TITLE, h1) > text_w:
        size -= 2.0
        h1 = _ser(c, size)
    base = y0 + 42.0
    _text(c, CONTENT_X0, base, DAY_TITLE, h1)
    audit.append(("day_title", c.width(DAY_TITLE, h1), text_w))

    sub = _cap(c, 9.4, "regular")
    sy = base + 14.0
    for line in _wrap_lines(c, DAY_SUB, sub, text_w, 3):
        _text(c, CONTENT_X0, sy, line, sub, fill=(60, 66, 74))
        audit.append(("day_sub", c.width(line, sub), text_w))
        sy += 13.0

    # red date box, flush right
    bx0 = CONTENT_X1 - box_w
    by0 = y0 + 18.0
    by1 = by0 + 74.0
    _box(c, bx0, by0, CONTENT_X1, by1, fill=RED)
    mid = (bx0 + CONTENT_X1) / 2.0
    mf = _cap(c, 9.0)
    _text(c, mid, by0 + 15.0, "NOV", mf, fill=WHITE, anchor="ms")
    df = _ser(c, 36.0)
    _text(c, mid, by0 + 50.0, "19", df, fill=WHITE, anchor="ms")
    yf = _cap(c, 9.4)
    _text(c, mid, by1 - 8.0, "2026", yf, fill=WHITE, anchor="ms")


# --------------------------------------------------------------------------
# zone 3: six-beat UTC timeline
# --------------------------------------------------------------------------


def _timeline(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_TIME
    head_w = 86.0
    c.rule(CONTENT_X0, y0, CONTENT_X1, y0, width=2.0)
    c.rule(CONTENT_X0, y1, CONTENT_X1, y1, width=2.0)
    _box(c, CONTENT_X0, y0, CONTENT_X0 + head_w, y1, fill=DARK_RED)

    hf = _cap(c, 7.6)
    mid = y0 + (y1 - y0) / 2.0
    _text(c, CONTENT_X0 + head_w / 2.0, mid - 4.0, "THE DAY", hf,
          fill=WHITE, anchor="ms")
    _text(c, CONTENT_X0 + head_w / 2.0, mid + 6.0, "IN UTC", hf,
          fill=WHITE, anchor="ms")

    seg = (CONTENT_W - head_w) / float(len(TIMELINE))
    tf = _cap(c, 7.4)
    hf2 = _cap(c, 8.6)
    sf = _cap(c, 6.6, "regular")
    for i, (time, head, src) in enumerate(TIMELINE):
        x0 = CONTENT_X0 + head_w + i * seg
        if i:
            c.rule(x0, y0 + 4.0, x0, y1 - 4.0, width=1.0, fill=LINE)
        inner = seg - 14.0
        _text(c, x0 + 7.0, y0 + 16.0, time, tf, fill=RED)
        lines = _wrap_lines(c, head, hf2, inner, 2)
        ty = y0 + 29.0
        for line in lines:
            _text(c, x0 + 7.0, ty, line, hf2)
            audit.append(("tl_head", c.width(line, hf2), inner))
            ty += 10.0
        _text(c, x0 + 7.0, y1 - 7.0, src, sf, fill=MUTED)


# --------------------------------------------------------------------------
# card bodies
# --------------------------------------------------------------------------


def _card(c: Canvas, audit: list, x0: float, y0: float, w: float, h: float,
          number: int, kicker: str, headline: str, body: str,
          art: str, big: bool) -> None:
    _box(c, x0, y0, x0 + w, y0 + h, fill=WHITE, outline=(51, 51, 51), width=1.0)
    art_h = 76.0 if big else 52.0
    _art(c, art, x0 + 1.0, y0 + 1.0, w - 2.0, art_h)

    pad = 7.0
    inner = w - pad * 2.0
    ny = y0 + art_h + 16.0
    nf = _ser(c, 17.0 if big else 13.0)
    nw = c.width(str(number), nf)
    _text(c, x0 + pad, ny, str(number), nf, fill=RED)
    kf = _cap(c, 6.8)
    c.tracked(x0 + pad + nw + 5.0, ny, kicker.upper(), kf, 0.5, fill=MUTED)

    hf = _ser(c, 15.0 if big else 11.4)
    hy = ny + 5.0 + c.cap_height(hf)
    limit = 3 if big else 3
    for line in _wrap_lines(c, headline, hf, inner, limit):
        _text(c, x0 + pad, hy, line, hf)
        audit.append(("card_head", c.width(line, hf), inner))
        hy += (hf_size(big) * 1.16)

    pf = _cap(c, 8.0 if big else 7.0, "regular")
    py = hy + 1.0
    room = y0 + h - 4.0 - py
    max_lines = max(0, int(room / (8.0 if big else 7.0) / 1.4))
    for line in _wrap_lines(c, body, pf, inner, max_lines):
        _text(c, x0 + pad, py, line, pf, fill=(70, 76, 85))
        audit.append(("card_body", c.width(line, pf), inner))
        py += (9.6 if big else 8.6)


def hf_size(big: bool) -> float:
    return 15.0 if big else 11.4


# --------------------------------------------------------------------------
# illustrations, drawn from primitives
# --------------------------------------------------------------------------


def _art(c: Canvas, kind: str, x0: float, y0: float, w: float, h: float) -> None:
    if kind == "summit":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(220, 232, 242))
        base = y0 + h - 4.0
        c.rule(x0 + 6.0, base, x0 + w - 6.0, base, width=1.4)
        slot = (w - 24.0) / 3.0
        bars = ((EU, 0.48), (AP, 0.64), (AM, 0.40))
        labels = ("US", "CN", "RU")
        ff = _cap(c, 11.0)
        for i, ((colour, ratio), label) in enumerate(zip(bars, labels)):
            bx = x0 + 12.0 + i * slot
            bw = slot * 0.62
            bh = (base - y0 - 12.0) * ratio
            _box(c, bx, base - bh, bx + bw, base, fill=colour)
            fy0 = base - bh - 18.0
            _box(c, bx, fy0, bx + bw, fy0 + 16.0, fill=WHITE,
                 outline=INK, width=1.0)
            _text(c, bx + bw / 2.0, fy0 + 12.0, label, ff, anchor="ms")
    elif kind == "bridge":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(16, 26, 46))
        c.polygon([(x0 + w * 0.05, y0 + h), (x0 + w * 0.20, y0 + h * 0.42),
                   (x0 + w * 0.35, y0 + h)], outline=None, fill=(43, 58, 85))
        c.polygon([(x0 + w * 0.28, y0 + h), (x0 + w * 0.44, y0 + h * 0.30),
                   (x0 + w * 0.60, y0 + h)], outline=None, fill=(31, 44, 68))
        _box(c, x0 + w * 0.48, y0 + h * 0.22, x0 + w * 0.54, y0 + h, fill=RED)
        _box(c, x0 + w * 0.57, y0 + h * 0.38, x0 + w * 0.61, y0 + h,
             fill=(90, 95, 102))
        c.dot(x0 + w * 0.38, y0 + h * 0.66, h * 0.17, fill=(232, 163, 61))
        lf = _cap(c, 10.0)
        _text(c, x0 + w * 0.66, y0 + h * 0.70, "KYIV", lf, fill=GOLD)
    elif kind == "games":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(23, 15, 46))
        c.dot(x0 + w * 0.78, y0 + h * 0.40, h * 0.24, fill=(243, 156, 18))
        _box(c, x0, y0 + h * 0.72, x0 + w, y0 + h, fill=(10, 7, 22))
        for off, ratio in ((0.04, 0.42), (0.15, 0.58), (0.25, 0.36), (0.86, 0.50)):
            tx = x0 + w * off
            tw = w * 0.08
            th = h * ratio
            _box(c, tx, y0 + h - th, tx + tw, y0 + h, fill=(43, 28, 82))
        nf = _cap(c, 17.0)
        _text(c, x0 + w * 0.40, y0 + h * 0.62, "VICE CITY", nf,
              fill=(255, 62, 165))
    elif kind == "court":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(232, 238, 244))
        cx = x0 + w / 2.0
        _box(c, cx - 12.0, y0 + h * 0.18, cx + 12.0, y0 + h * 0.34, fill=EU)
        _box(c, cx - 4.0, y0 + h * 0.34, cx + 4.0, y0 + h * 0.70, fill=EU)
        c.rule(x0 + w * 0.20, y0 + h * 0.78, x0 + w * 0.80, y0 + h * 0.78,
               width=4.0, fill=RED)
    elif kind == "ipo":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(233, 242, 236))
        pts = [(x0 + w * (0.07 + 0.80 * i / 6.0),
                y0 + h * (0.86 - 0.70 * (i / 6.0) ** 0.9)) for i in range(7)]
        for i in range(len(pts) - 1):
            c.rule(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                   width=3.0, fill=AM)
        c.dot(pts[-1][0], pts[-1][1], 4.0, fill=AM)
        f = _cap(c, 10.0)
        _text(c, x0 + w * 0.08, y0 + h * 0.26, "ANT $83", f, fill=AM)
    elif kind == "gaza":
        _box(c, x0, y0, x0 + w, y0 + h, fill=(244, 237, 227))
        _box(c, x0 + w * 0.08, y0 + h * 0.14, x0 + w * 0.34, y0 + h * 0.70,
             fill=(216, 207, 192))
        _box(c, x0 + w * 0.64, y0 + h * 0.14, x0 + w * 0.90, y0 + h * 0.70,
             fill=(216, 207, 192))
        _box(c, x0 + w * 0.34, y0 + h * 0.52, x0 + w * 0.64, y0 + h * 0.66,
             fill=(232, 163, 61))
        _box(c, x0 + w * 0.46, y0 + h * 0.14, x0 + w * 0.50, y0 + h * 0.44,
             fill=RED)
    else:  # storm
        _box(c, x0, y0, x0 + w, y0 + h, fill=(228, 241, 240))
        cx = x0 + w / 2.0
        cy = y0 + h / 2.0
        c.ring(cx, cy, h * 0.30, width=3.0, fill=OC)
        c.polygon([(cx, cy - h * 0.30), (cx + h * 0.12, cy),
                   (cx, cy + h * 0.30), (cx - h * 0.12, cy)],
                  outline=None, fill=OC)
        c.rule(cx - w * 0.20, cy, cx + w * 0.20, cy, width=2.4, fill=RED)


# --------------------------------------------------------------------------
# card rows
# --------------------------------------------------------------------------


def _row3(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_ROW3
    gap = 10.0
    w = (CONTENT_W - gap * 2.0) / 3.0
    for i, (art, kicker, head, body) in enumerate(LEADS):
        x0 = CONTENT_X0 + i * (w + gap)
        _card(c, audit, x0, y0, w, y1 - y0, i + 1, kicker, head, body, art, True)


def _row4(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_ROW4
    gap = 10.0
    w = (CONTENT_W - gap * 3.0) / 4.0
    for i, (art, kicker, head, body) in enumerate(SECONDS):
        x0 = CONTENT_X0 + i * (w + gap)
        _card(c, audit, x0, y0, w, y1 - y0, i + 4, kicker, head, body, art, False)


# --------------------------------------------------------------------------
# map and the list of remaining stories
# --------------------------------------------------------------------------


def _map(c: Canvas, x0: float, y0: float, w: float, h: float) -> None:
    _box(c, x0, y0, x0 + w, y0 + h, fill=(233, 230, 221))
    shapes = (
        ((0.04, 0.26), (0.13, 0.18), (0.21, 0.24), (0.22, 0.38), (0.17, 0.51),
         (0.12, 0.49), (0.07, 0.37)),
        ((0.16, 0.57), (0.22, 0.56), (0.24, 0.70), (0.22, 0.88), (0.18, 0.81),
         (0.16, 0.68)),
        ((0.38, 0.18), (0.47, 0.14), (0.49, 0.25), (0.45, 0.33), (0.39, 0.31)),
        ((0.40, 0.37), (0.47, 0.35), (0.50, 0.50), (0.46, 0.68), (0.42, 0.64),
         (0.39, 0.50)),
        ((0.51, 0.16), (0.69, 0.12), (0.74, 0.27), (0.71, 0.44), (0.61, 0.50),
         (0.53, 0.40)),
        ((0.67, 0.68), (0.75, 0.65), (0.77, 0.77), (0.72, 0.86), (0.67, 0.78)),
    )
    for shape in shapes:
        c.polygon([(x0 + px * w, y0 + py * h) for px, py in shape],
                  outline=None, fill=(207, 201, 187))

    nf = _cap(c, 9.0)
    for number, (mx, my) in enumerate(((0.17, 0.36), (0.34, 0.43), (0.57, 0.30)),
                                      start=1):
        c.dot(x0 + mx * w, y0 + my * h, 8.0, fill=RED)
        _text(c, x0 + mx * w, y0 + my * h + 3.0, str(number), nf,
              fill=WHITE, anchor="ms")
    for mx, my in ((0.45, 0.25), (0.47, 0.45), (0.71, 0.75), (0.15, 0.62),
                   (0.63, 0.37)):
        c.dot(x0 + mx * w, y0 + my * h, 4.0, fill=(140, 140, 140))


def _bottom(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_MAP
    c.rule(CONTENT_X0, y0, CONTENT_X1, y0, width=2.0)
    map_w = 380.0
    head = _cap(c, 8.0)
    top = y0 + 10.0
    c.tracked(CONTENT_X0, top, "WHERE IT HAPPENED", head, 1.0)
    _map(c, CONTENT_X0, top + 6.0, map_w, 168.0)
    note = _cap(c, 6.4, "regular")
    _text(c, CONTENT_X0, top + 186.0,
          "Red numbers mark the lead stories; grey dots mark the briefs opposite.",
          note, fill=MUTED)

    list_x = CONTENT_X0 + map_w + 16.0
    list_w = CONTENT_X1 - list_x
    c.tracked(list_x, top, "ALSO ON THURSDAY 19 NOVEMBER \u2014 %d MORE STORIES"
              % len(MORE), head, 1.0)

    col_w = (list_w - 12.0) / 2.0
    per_col = (len(MORE) + 1) // 2
    num_f = _cap(c, 7.2)
    city_f = _cap(c, 7.2)
    body_f = _cap(c, 7.2, "regular")
    row_h = 13.4
    start = top + 14.0
    for i, (city, text) in enumerate(MORE):
        col = i // per_col
        row = i % per_col
        x0 = list_x + col * (col_w + 12.0)
        yy = start + row * row_h
        label = "%d" % (i + 8)
        nw = c.width(label, num_f)
        _text(c, x0, yy, label, num_f, fill=RED)
        cw = c.tracked(x0 + nw + 4.0, yy, city.upper(), city_f, 0.3)
        room = col_w - (nw + 4.0 + cw + 4.0)
        line = c.wrap(text, body_f, room)[0] if room > 10 else ""
        if line:
            _text(c, x0 + nw + 4.0 + cw + 4.0, yy, line, body_f, fill=(70, 76, 85))
            audit.append(("more_line", c.width(line, body_f), room))


# --------------------------------------------------------------------------
# footer: date check and sources
# --------------------------------------------------------------------------


def _foot(c: Canvas, audit: list) -> None:
    y0, y1 = BAND_FOOT
    c.rule(CONTENT_X0, y0, CONTENT_X1, y0, width=2.0)
    dc_w = 470.0
    top = y0 + 8.0
    _box(c, CONTENT_X0, top, CONTENT_X0 + dc_w, y1 - 6.0, outline=RED, width=1.5)

    hf = _cap(c, 6.4)
    c.tracked(CONTENT_X0 + 5.0, top + 10.0,
              "DATE CHECK \u00b7 FIRST REPORTED WED 18 NOV \u00b7 NOT COUNTED HERE",
              hf, 0.5, fill=RED)
    bf = _cap(c, 6.2, "regular")
    items = " \u00b7 ".join(DATE_CHECK)
    yy = top + 20.0
    for line in c.wrap(items, bf, dc_w - 10.0)[:3]:
        _text(c, CONTENT_X0 + 5.0, yy, line, bf, fill=(74, 80, 88))
        audit.append(("date_check", c.width(line, bf), dc_w - 10.0))
        yy += 8.0

    src_x = CONTENT_X0 + dc_w + 14.0
    sf = _cap(c, 6.0, "regular")
    _text(c, src_x, top + 10.0,
          "Every story happened or was first reported on 19 November 2026.",
          sf, fill=MUTED)
    _text(c, src_x, top + 20.0, FOOT_SOURCES, sf, fill=MUTED)
    audit.append(("sources", c.width(FOOT_SOURCES, sf), CONTENT_X1 - src_x))


# --------------------------------------------------------------------------
# composition
# --------------------------------------------------------------------------


def _compose(c: Canvas, audit: list) -> None:
    _strap(c, audit)
    _masthead(c, audit)
    _timeline(c, audit)
    _row3(c, audit)
    _row4(c, audit)
    _bottom(c, audit)
    _foot(c, audit)


def render_page(audit: Optional[list] = None):
    """Draw the page and return the downsampled 1024x1024 raster."""
    report: list = audit if audit is not None else []
    canvas = Canvas(SS)
    _compose(canvas, report)
    report.append(("story_count", 0.0, 0.0))
    return downsample(canvas.canvas, SS)


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
