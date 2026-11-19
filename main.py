#!/usr/bin/env python3
"""news-image-20261119: one picture of Thursday 19 November 2026.

A small self-contained renderer: it paints a newspaper front page
(1024 by 1024 PNG) carrying eight stories that were reported on
19 November 2026, using only the Python standard library. The glyphs
are stored as one short string per character, the picture is encoded
by hand, and nothing about the run depends on the clock, the network
or chance, so running it twice writes the same bytes twice.

The eight stories, each checked against live reporting on 19 Nov:
 1. MARKETS — Anthropic priced its IPO at $83 a share and raised
    $81.3 billion, the biggest IPO ever; the shares start trading
    on Nasdaq today under the ticker ANT. (Reuters; PYMNTS; CNBC)
 2. UNITED STATES — House Democrats nominated Hakeem Jeffries for
    Speaker, 251 votes to 11; he would be the first Black Speaker.
    The full House votes in January. (USA Today; Al Jazeera)
 3. EUROPE — The EU proposed a 45 billion euro loan for Ukraine, to
    be repaid once Russia pays war reparations. (Jagran Josh)
 4. UKRAINE — The Kerch Bridge was hit for a third time this week;
    Crimea's chief shut traffic while the damage is assessed.
    (AppiSToS; News Media House)
 5. CHINA — Donald Trump landed in Shenzhen for a trilateral APEC
    summit with Xi Jinping and Vladimir Putin. (CareerIndia)
 6. WORLD COURT — The ICJ hands down its judgment today on whether
    Myanmar committed genocide against the Rohingya. (ICJ; Foley Hoag)
 7. CULTURE — Grand Theft Auto VI started its worldwide rollout;
    players return to Vice City, 13 years after GTA V.
    (Jagran Josh; BBC)
 8. THE GULF — Saudi Arabia said the danger had passed in three
    southern cities after missile alerts; a coalition reported a
    missile threat towards Riyadh. (AppiSToS)

Run it with: MAKEFUN_OUTPUT_DIR=out python3 main.py
(that writes out/entry.png; without the variable it writes /output/entry.png)
"""

import os
import struct
import zlib

W = H = 1024
PAPER = (248, 244, 233)
INK = (20, 20, 20)
RED = (178, 34, 24)
NAVY = (29, 78, 137)
TEAL = (0, 120, 113)
GOLD = (150, 105, 0)
GREEN = (46, 125, 50)
PURPLE = (90, 60, 140)
ORANGE = (198, 88, 0)
SLATE = (74, 84, 94)
LIGHT = (226, 219, 203)

# One glyph per line: seven rows of five cells, space separated.
# '#' is ink, '.' is empty. Only the characters the page uses.
FONT = {
    'A': '##### #...# #...# ##### #...# #...# #...#',
    'B': '####. #...# #...# ####. #...# #...# ####.',
    'C': '.#### #.... #.... #.... #.... #.... .####',
    'D': '####. #...# #...# #...# #...# #...# ####.',
    'E': '##### #.... #.... ####. #.... #.... #####',
    'F': '##### #.... #.... ####. #.... #.... #....',
    'G': '.#### #.... #.... #.### #...# #...# .###.',
    'H': '#...# #...# #...# ##### #...# #...# #...#',
    'I': '.###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.',
    'J': '..### ...#. ...#. ...#. ...#. #..#. .##..',
    'K': '#...# #..#. #.#.. ##... #.#.. #..#. #...#',
    'L': '#.... #.... #.... #.... #.... #.... #####',
    'M': '#...# ##.## #.#.# #.#.# #...# #...# #...#',
    'N': '#...# ##..# #.#.# #..## #...# #...# #...#',
    'O': '.###. #...# #...# #...# #...# #...# .###.',
    'P': '####. #...# #...# ####. #.... #.... #....',
    'Q': '.###. #...# #...# #...# #.#.# #..#. .##.#',
    'R': '####. #...# #...# ####. #.#.. #..#. #...#',
    'S': '.#### #.... #.... .###. ....# ....# ####.',
    'T': '##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..',
    'U': '#...# #...# #...# #...# #...# #...# .###.',
    'V': '#...# #...# #...# #...# #...# .#.#. ..#..',
    'W': '#...# #...# #...# #.#.# #.#.# ##.## #...#',
    'X': '#...# .#.#. ..#.. ..#.. ..#.. .#.#. #...#',
    'Y': '#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..',
    'Z': '##### ....# ...#. ..#.. .#... #.... #####',
    '0': '.###. #...# #..## #.#.# ##..# #...# .###.',
    '1': '..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.',
    '2': '.###. #...# ....# ...#. ..#.. .#... #####',
    '3': '####. ....# ....# .###. ....# ....# ####.',
    '4': '...#. ..##. .#.#. #..#. ##### ...#. ...#.',
    '5': '##### #.... ####. ....# ....# #...# .###.',
    '6': '.###. #.... #.... ####. #...# #...# .###.',
    '7': '##### ....# ...#. ...#. ..#.. ..#.. ..#..',
    '8': '.###. #...# #...# .###. #...# #...# .###.',
    '9': '.###. #...# #...# .#### ....# ....# .###.',
    ' ': '..... ..... ..... ..... ..... ..... .....',
    '.': '..... ..... ..... ..... ..... .##.. .##..',
    ',': '..... ..... ..... ..... .##.. .##.. .#...',
    "'": '..#.. ..#.. .#... ..... ..... ..... .....',
    '-': '..... ..... ..... ##### ..... ..... .....',
    '$': '..#.. .#### #.#.# .###. ..#.# ####. ..#..',
    '%': '#...# #..#. ...#. ..#.. .#... #..#. #...#',
}


def glyph_rows(ch):
    return FONT.get(ch, FONT[' ']).split(' ')


def tw(s, scale):
    """Pixel width of s at the given scale."""
    return len(s) * 6 * scale - scale


def wrap(text, max_w, scale):
    out, cur = [], ''
    for word in text.split(' '):
        trial = word if not cur else cur + ' ' + word
        if tw(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


class Page:
    """A 1024x1024 RGB canvas backed by one flat bytearray."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def fill(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.put(xx, y, c)

    def seg(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c, solid=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if solid:
                    if d2 <= r * r:
                        self.put(xx, yy, c)
                elif abs(d2 - r * r) <= r:
                    self.put(xx, yy, c)

    def txt(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            for row, cells in enumerate(glyph_rows(ch)):
                for col, cell in enumerate(cells):
                    if cell == '#':
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def centred(self, y, s, scale, c):
        self.txt((self.w - tw(s, scale)) // 2, y, s, scale, c)


# ------------------------------------------------------------------ icons
def pict(pg, kind, x, y, c):
    """One 44x44 pictogram for a story cell, in colour c."""
    if kind == 'gulf':
        cx, cy = x + 22, y + 16
        for dx, dy in ((0, -12), (9, -9), (12, 0), (9, 9), (0, 12),
                       (-9, 9), (-12, 0), (-9, -9)):
            pg.seg(cx, cy, cx + dx, cy + dy, c)
        pg.disc(cx, cy, 5, c, solid=True)
        for yy in (y + 34, y + 39):
            for xx in range(x + 4, x + 40, 8):
                pg.seg(xx, yy, xx + 4, yy, c)
    elif kind == 'bridge':
        pg.seg(x + 2, y + 30, x + 18, y + 30, c)
        pg.seg(x + 26, y + 30, x + 42, y + 30, c)
        pg.seg(x + 6, y + 30, x + 6, y + 12, c)
        pg.seg(x + 38, y + 30, x + 38, y + 12, c)
        pg.seg(x + 6, y + 12, x + 22, y + 22, c)
        pg.seg(x + 38, y + 12, x + 22, y + 22, c)
        pg.seg(x + 18, y + 30, x + 18, y + 38, c)
        pg.seg(x + 26, y + 30, x + 26, y + 38, c)
    elif kind == 'summit':
        for cx in (x + 10, x + 22, x + 34):
            pg.disc(cx, y + 12, 6, c, solid=True)
            pg.fill(cx - 6, y + 20, 12, 10, c)
        pg.seg(x + 2, y + 32, x + 42, y + 32, c)
    elif kind == 'ballot':
        pg.fill(x + 8, y + 12, 28, 24, c)
        pg.fill(x + 16, y + 6, 12, 6, INK)
        pg.seg(x + 12, y + 26, x + 18, y + 32, PAPER)
        pg.seg(x + 18, y + 32, x + 32, y + 16, PAPER)
    elif kind == 'ipo':
        pg.seg(x + 6, y + 36, x + 6, y + 8, c)
        pg.seg(x + 6, y + 36, x + 40, y + 36, c)
        pg.seg(x + 8, y + 30, x + 18, y + 22, c)
        pg.seg(x + 18, y + 22, x + 26, y + 26, c)
        pg.seg(x + 26, y + 26, x + 38, y + 10, c)
        pg.seg(x + 38, y + 10, x + 32, y + 10, c)
        pg.seg(x + 38, y + 10, x + 38, y + 16, c)
    elif kind == 'coins':
        pg.disc(x + 16, y + 30, 9, c)
        pg.disc(x + 28, y + 30, 9, c)
        pg.disc(x + 22, y + 18, 9, c)
        pg.fill(x + 21, y + 14, 2, 8, PAPER)
        pg.fill(x + 15, y + 26, 2, 8, PAPER)
        pg.fill(x + 27, y + 26, 2, 8, PAPER)
    elif kind == 'gavel':
        pg.fill(x + 8, y + 8, 20, 9, c)
        pg.seg(x + 28, y + 12, x + 38, y + 26, c)
        pg.seg(x + 30, y + 10, x + 40, y + 24, c)
        pg.seg(x + 6, y + 36, x + 38, y + 36, c)
        pg.fill(x + 12, y + 32, 24, 4, c)
    elif kind == 'game':
        pg.fill(x + 6, y + 14, 32, 18, c)
        pg.fill(x + 12, y + 20, 4, 10, PAPER)
        pg.fill(x + 9, y + 23, 10, 4, PAPER)
        pg.disc(x + 30, y + 21, 2, PAPER, solid=True)
        pg.disc(x + 35, y + 26, 2, PAPER, solid=True)


# ---------------------------------------------------------------- stories
# Each story: section label, accent colour, pictogram, headline, deck.
STORIES = [
    ('MARKETS', GREEN, 'ipo', 'ANTHROPIC IPO RAISES $81.3BN',
     'The Claude maker sets the record for the largest IPO ever. '
     'Shares start trading on Nasdaq today as ANT.'),
    ('UNITED STATES', GOLD, 'ballot', 'JEFFRIES NOMINATED FOR SPEAKER',
     'Democrats pick Hakeem Jeffries 251-11. He would be the first '
     'Black Speaker of the House.'),
    ('EUROPE', NAVY, 'coins', 'EU PROPOSES 45BN UKRAINE LOAN',
     'Brussels offers Kyiv a 45 billion euro loan, to be repaid '
     'after Russia pays war reparations.'),
    ('UKRAINE', NAVY, 'bridge', 'KERCH BRIDGE HIT A THIRD TIME',
     "Crimea's chief closes traffic on the bridge after a new "
     'attack. Damage is being assessed.'),
    ('CHINA', TEAL, 'summit', 'TRUMP ARRIVES IN SHENZHEN',
     'The US president lands in China for a trilateral APEC summit '
     'with Xi Jinping and Vladimir Putin.'),
    ('WORLD COURT', PURPLE, 'gavel', 'ICJ RULES TODAY ON ROHINGYA',
     'The world court delivers its judgment on whether Myanmar '
     'committed genocide against the Rohingya.'),
    ('CULTURE', ORANGE, 'game', 'GTA VI ROLLS OUT WORLDWIDE',
     'Gamers enter Vice City as Grand Theft Auto VI begins its '
     'global rollout, 13 years after GTA V.'),
    ('THE GULF', RED, 'gulf', 'SAUDI ALERTS LIFTED AFTER SCARE',
     'Saudi Arabia says the danger has passed in three southern '
     'cities after missile alerts.'),
]


def cell(pg, x, y, w, h, story):
    label, colour, icon, head, deck = story
    pg.fill(x, y, 6, h, colour)
    pg.txt(x + 16, y + 10, label, 2, colour)
    pict(pg, icon, x + w - 56, y + 6, colour)
    lines = wrap(head, w - 80, 3)
    yy = y + 34
    for ln in lines[:2]:
        pg.txt(x + 16, yy, ln, 3, INK)
        yy += 24
    # Decks print in capitals: the font has no lowercase letters.
    deck_lines = wrap(deck.upper(), w - 32, 2)
    yy += 6
    for ln in deck_lines[:3]:
        pg.txt(x + 16, yy, ln, 2, SLATE)
        yy += 17


def build():
    pg = Page(W, H, PAPER)
    pg.fill(0, 0, W, 10, RED)
    pg.centred(28, 'THE WORLD TODAY', 7, INK)
    pg.hline(16, 92, W - 32, INK)
    pg.fill(0, 100, W, 52, RED)
    pg.centred(112, 'THURSDAY  -  19 NOVEMBER 2026', 4, PAPER)
    pg.centred(164, 'EIGHT STORIES THAT DEFINED THE DAY', 2, INK)
    pg.hline(16, 190, W - 32, INK)
    margin, gap = 16, 8
    cw = (W - 2 * margin - gap) // 2
    ch = 194
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cw + gap)
        cy = 200 + (i // 2) * (ch + gap)
        pg.fill(cx, cy, cw, ch, (255, 255, 255))
        pg.fill(cx, cy, cw, 2, LIGHT)
        pg.fill(cx, cy + ch - 2, cw, 2, LIGHT)
        cell(pg, cx, cy, cw, ch, story)
    pg.hline(16, 988, W - 32, INK)
    pg.centred(998, 'REPORTED 19 NOVEMBER 2026', 2, INK)
    return pg


# --------------------------------------------------------------------- PNG
def _chunk(kind, data):
    blob = struct.pack('>I', len(data)) + kind + data
    return blob + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)


def to_png(pg):
    raw = bytearray()
    for y in range(pg.h):
        raw.append(0)
        raw += pg.buf[y * pg.w * 3:(y + 1) * pg.w * 3]
    ihdr = struct.pack('>IIBBBBB', pg.w, pg.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr)
            + _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + _chunk(b'IEND', b''))


def main():
    out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'entry.png'), 'wb') as f:
        f.write(to_png(build()))


if __name__ == '__main__':
    main()
