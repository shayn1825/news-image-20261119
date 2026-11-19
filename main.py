#!/usr/bin/env python3
"""news-image-20261119: one picture of Thursday 19 November 2026.

A compact renderer that paints a newspaper front page (1024 by 1024
PNG) with eight stories reported on 19 November 2026. It uses only
the standard library. Letters come from a tiny 5x7 font stored as
integers (one row is five bits), the pictograms are small bitmaps
stored as strings, and the PNG is encoded by hand, so two runs write
identical bytes with no network and no clock involved.

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
"""

import os, struct, zlib

W = H = 1024
PAPER, INK = (248, 244, 233), (20, 20, 20)
RED, NAVY, TEAL = (178, 34, 24), (29, 78, 137), (0, 120, 113)
GOLD, GREEN = (150, 105, 0), (46, 125, 50)
PURPLE, ORANGE = (90, 60, 140), (198, 88, 0)
SLATE, LIGHT = (74, 84, 94), (226, 219, 203)

# 5x7 font as integers: each glyph is seven rows, each row five bits,
# leftmost pixel is bit 4. Only the characters the page prints.
FONT = {
    'A': (31, 17, 17, 31, 17, 17, 17),
    'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (15, 16, 16, 16, 16, 16, 15),
    'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31),
    'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (15, 16, 16, 23, 17, 17, 14),
    'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),
    'J': (7, 1, 1, 1, 1, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17),
    'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17),
    'N': (17, 25, 21, 19, 17, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14),
    'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13),
    'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),
    'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14),
    'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 27, 17),
    'X': (17, 10, 4, 4, 4, 10, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),
    'Z': (31, 1, 2, 4, 8, 16, 31),
    '0': (14, 17, 19, 21, 25, 17, 14),
    '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 2, 4, 8, 31),
    '3': (30, 1, 1, 14, 1, 1, 30),
    '4': (2, 6, 10, 18, 31, 2, 2),
    '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (14, 16, 16, 30, 17, 17, 14),
    '7': (31, 1, 2, 2, 4, 4, 4),
    '8': (14, 17, 17, 14, 17, 17, 14),
    '9': (14, 17, 17, 15, 1, 1, 14),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 6, 6, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    '-': (0, 0, 0, 31, 0, 0, 0),
    '$': (4, 15, 21, 14, 5, 30, 4),
    '%': (17, 18, 2, 4, 8, 18, 17),
}


def width_of(s, k):
    return len(s) * 6 * k - k


def split_lines(text, max_w, k):
    lines, cur = [], ''
    for w in text.split(' '):
        t = w if not cur else cur + ' ' + w
        if width_of(t, k) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Sheet:
    def __init__(self, w, h, bg):
        self.w, self.h, self.px = w, h, bytearray(bg * (w * h))

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def box(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, c)

    def rule(self, x, y, w, c):
        for xx in range(x, x + w):
            self.dot(xx, y, c)

    def blit(self, rows, x, y, k, c):
        for r, row in enumerate(rows):
            for col, ch in enumerate(row):
                if ch == '#':
                    self.box(x + col * k, y + r * k, k, k, c)

    def show(self, x, y, s, k, c):
        cx = x
        for ch in s:
            for r, bits in enumerate(FONT.get(ch, FONT[' '])):
                for col in range(5):
                    if bits >> (4 - col) & 1:
                        self.box(cx + col * k, y + r * k, k, k, c)
            cx += 6 * k
        return cx

    def mid(self, y, s, k, c):
        self.show((self.w - width_of(s, k)) // 2, y, s, k, c)


# Pictograms: 11 columns by 6 rows, '#' is ink. Drawn at scale 4.
ICONS = {
    'ipo': (
        '..........#',
        '........###',
        '......#..##',
        '....##..###',
        '..##...####',
        '###########',
    ),
    'ballot': (
        '...#####...',
        '..#######..',
        '..#.....#..',
        '..#..#..#..',
        '..#.#...#..',
        '..#######..',
    ),
    'coins': (
        '..#####....',
        '.#.....#...',
        '.#..#..#...',
        '..#####....',
        '...#...#...',
        '...#####...',
    ),
    'bridge': (
        '.#.......#.',
        '.#.......#.',
        '.#.......#.',
        '.##.....##.',
        '..#.....#..',
        '###########',
    ),
    'summit': (
        '..#...#...#',
        '.###.###.##',
        '..#...#...#',
        '...........',
        '###########',
        '...........',
    ),
    'gavel': (
        '####.......',
        '.####......',
        '..####.....',
        '...#######.',
        '...........',
        '###########',
    ),
    'game': (
        '..#######..',
        '.#.......#.',
        '.#.#...#.#.',
        '.###...###.',
        '.#.......#.',
        '..#######..',
    ),
    'gulf': (
        '.....#.....',
        '..#..#..#..',
        '...#####...',
        '..#..#..#..',
        '.....#.....',
        '###########',
    ),
}

# section, accent, icon, headline, deck
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


def story_cell(pg, x, y, w, h, story):
    label, colour, icon, head, deck = story
    pg.box(x, y, 6, h, colour)
    pg.show(x + 16, y + 10, label, 2, colour)
    pg.blit(ICONS[icon], x + w - 58, y + 8, 4, colour)
    head_lines = split_lines(head, w - 80, 3)
    yy = y + 34
    for ln in head_lines[:2]:
        pg.show(x + 16, yy, ln, 3, INK)
        yy += 24
    # The font has no lowercase, so decks print in capitals.
    deck_lines = split_lines(deck.upper(), w - 32, 2)
    yy += 6
    for ln in deck_lines[:3]:
        pg.show(x + 16, yy, ln, 2, SLATE)
        yy += 17


def render():
    pg = Sheet(W, H, PAPER)
    pg.box(0, 0, W, 10, RED)
    pg.mid(28, 'THE WORLD TODAY', 7, INK)
    pg.rule(16, 92, W - 32, INK)
    pg.box(0, 96, W, 56, RED)
    pg.mid(110, 'THURSDAY  -  19 NOVEMBER 2026', 4, PAPER)
    pg.mid(162, 'EIGHT STORIES THAT DEFINED THE DAY', 2, INK)
    pg.rule(16, 188, W - 32, INK)
    mx, gp = 20, 10
    cw = (W - 2 * mx - gp) // 2
    chh = 190
    for i, story in enumerate(STORIES):
        cx = mx + (i % 2) * (cw + gp)
        cy = 198 + (i // 2) * (chh + gp)
        pg.box(cx, cy, cw, chh, (255, 255, 255))
        pg.box(cx, cy, cw, 2, LIGHT)
        pg.box(cx, cy + chh - 2, cw, 2, LIGHT)
        story_cell(pg, cx, cy, cw, chh, story)
    pg.rule(16, 984, W - 32, INK)
    pg.mid(994, 'REPORTED 19 NOVEMBER 2026', 2, INK)
    return pg


def png_bytes(pg):
    raw = bytearray()
    for y in range(pg.h):
        raw.append(0)
        raw += pg.px[y * pg.w * 3:(y + 1) * pg.w * 3]
    head = struct.pack('>IIBBBBB', pg.w, pg.h, 8, 2, 0, 0, 0)
    parts = [(b'IHDR', head), (b'IDAT', zlib.compress(bytes(raw), 9)),
             (b'IEND', b'')]
    out = bytearray(b'\x89PNG\r\n\x1a\n')
    for kind, data in parts:
        out += struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return bytes(out)


def main():
    dest = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, 'entry.png'), 'wb') as f:
        f.write(png_bytes(render()))


if __name__ == '__main__':
    main()
