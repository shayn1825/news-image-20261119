#!/usr/bin/env python3
"""news-image-20261119 — Sum up Thursday 19 November 2026 in one image.

A deterministic, stdlib-only renderer. It draws a newspaper front page
(1024x1024 PNG) with eight verified stories from 19 November 2026 and
writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

News verified 19 Nov 2026 (live web sources, same day):
 1. Markets: Anthropic priced its IPO at $83 a share and raised
    $81.3 billion, the largest IPO on record; shares start trading
    on Nasdaq today as ANT. (Reuters via BusinessWorld; PYMNTS; CNBC)
 2. USA: Democrats nominated Hakeem Jeffries for Speaker of the
    House, 251-11; he would be the first Black Speaker. The formal
    House vote is in January. (USA Today; Al Jazeera)
 3. Europe: The EU proposed a 45 billion euro loan for Ukraine, to
    be repaid after Russia pays war reparations. (Jagran Josh)
 4. Ukraine: The Kerch Bridge was hit for a third time this week;
    Crimea's chief closed traffic while damage is assessed.
    (AppiSToS; News Media House)
 5. China: Donald Trump arrived in Shenzhen ahead of a trilateral
    APEC summit with Xi Jinping and Vladimir Putin. (CareerIndia)
 6. World Court: The ICJ delivers its judgment today on whether
    Myanmar committed genocide against the Rohingya. (ICJ; Foley Hoag)
 7. Culture: Grand Theft Auto VI began its global rollout; gamers
    enter Vice City, 13 years after GTA V. (Jagran Josh; BBC)
 8. Gulf: Saudi Arabia said the danger has passed in three southern
    cities after missile alerts; a coalition reported a missile
    threat towards Riyadh. (AppiSToS)

No network, no randomness, no timestamps: two runs write identical
bytes. Only the Python standard library is used (zlib, struct, os).
"""

import os
import struct
import zlib

W, H = 1024, 1024

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

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one glyph = 7 rows of 5 pixels ('#' on, '.' off).
FONT = {
    'A': ("#####", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.set(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.set(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                elif abs(d2 - r * r) <= r:
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == '#':
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centre(self, y, s, scale, c):
        self.text((self.w - text_width(s, scale)) // 2, y, s, scale, c)


# ---------------------------------------------------------------- icons
def draw_icon(cv, kind, x, y, c):
    """Small 44x44 pictogram inside the story cell, drawn in colour c."""
    if kind == "gulf":  # explosion + waves
        cx, cy = x + 22, y + 16
        for dx, dy in ((0, -12), (9, -9), (12, 0), (9, 9), (0, 12),
                       (-9, 9), (-12, 0), (-9, -9)):
            cv.line(cx, cy, cx + dx, cy + dy, c)
        cv.circle(cx, cy, 5, c, fill=True)
        for yy in (y + 34, y + 39):
            for xx in range(x + 4, x + 40, 8):
                cv.line(xx, yy, xx + 4, yy, c)
    elif kind == "bridge":  # bridge with a broken span
        cv.line(x + 2, y + 30, x + 18, y + 30, c)
        cv.line(x + 26, y + 30, x + 42, y + 30, c)
        cv.line(x + 6, y + 30, x + 6, y + 12, c)
        cv.line(x + 38, y + 30, x + 38, y + 12, c)
        cv.line(x + 6, y + 12, x + 22, y + 22, c)
        cv.line(x + 38, y + 12, x + 22, y + 22, c)
        cv.line(x + 18, y + 30, x + 18, y + 38, c)
        cv.line(x + 26, y + 30, x + 26, y + 38, c)
    elif kind == "summit":  # three leaders at a table
        for cx in (x + 10, x + 22, x + 34):
            cv.circle(cx, y + 12, 6, c, fill=True)
            cv.rect(cx - 6, y + 20, 12, 10, c)
        cv.line(x + 2, y + 32, x + 42, y + 32, c)
    elif kind == "ballot":  # ballot box + tick
        cv.rect(x + 8, y + 12, 28, 24, c)
        cv.rect(x + 16, y + 6, 12, 6, INK)
        cv.line(x + 12, y + 26, x + 18, y + 32, PAPER)
        cv.line(x + 18, y + 32, x + 32, y + 16, PAPER)
    elif kind == "ipo":  # rising chart
        cv.line(x + 6, y + 36, x + 6, y + 8, c)
        cv.line(x + 6, y + 36, x + 40, y + 36, c)
        cv.line(x + 8, y + 30, x + 18, y + 22, c)
        cv.line(x + 18, y + 22, x + 26, y + 26, c)
        cv.line(x + 26, y + 26, x + 38, y + 10, c)
        cv.line(x + 38, y + 10, x + 32, y + 10, c)
        cv.line(x + 38, y + 10, x + 38, y + 16, c)
    elif kind == "coins":  # stack of coins
        cv.circle(x + 16, y + 30, 9, c)
        cv.circle(x + 28, y + 30, 9, c)
        cv.circle(x + 22, y + 18, 9, c)
        cv.rect(x + 20, y + 15, 4, 7, PAPER)
        cv.rect(x + 14, y + 27, 4, 7, PAPER)
        cv.rect(x + 26, y + 27, 4, 7, PAPER)
    elif kind == "gavel":  # judge's gavel + block
        cv.rect(x + 8, y + 8, 20, 9, c)
        cv.line(x + 28, y + 12, x + 38, y + 26, c)
        cv.line(x + 30, y + 10, x + 40, y + 24, c)
        cv.line(x + 6, y + 36, x + 38, y + 36, c)
        cv.rect(x + 12, y + 32, 24, 4, c)
    elif kind == "game":  # game controller
        cv.rect(x + 6, y + 14, 32, 18, c)
        cv.rect(x + 12, y + 20, 4, 10, PAPER)
        cv.rect(x + 9, y + 23, 10, 4, PAPER)
        cv.circle(x + 30, y + 21, 2, PAPER, fill=True)
        cv.circle(x + 35, y + 26, 2, PAPER, fill=True)


# ---------------------------------------------------------------- stories
# (kicker, colour, icon, headline, deck)
STORIES = [
    ("MARKETS", GREEN, "ipo",
     "ANTHROPIC IPO RAISES $81.3BN",
     "The Claude maker sets the record for the largest IPO ever. "
     "Shares start trading on Nasdaq today as ANT."),
    ("UNITED STATES", GOLD, "ballot",
     "JEFFRIES NOMINATED FOR SPEAKER",
     "Democrats pick Hakeem Jeffries 251-11. He would be the first "
     "Black Speaker of the House."),
    ("EUROPE", NAVY, "coins",
     "EU PROPOSES 45BN UKRAINE LOAN",
     "Brussels offers Kyiv a 45 billion euro loan, to be repaid "
     "after Russia pays war reparations."),
    ("UKRAINE", NAVY, "bridge",
     "KERCH BRIDGE HIT A THIRD TIME",
     "Crimea's chief closes traffic on the bridge after a new "
     "attack. Damage is being assessed."),
    ("CHINA", TEAL, "summit",
     "TRUMP ARRIVES IN SHENZHEN",
     "The US president lands in China for a trilateral APEC summit "
     "with Xi Jinping and Vladimir Putin."),
    ("WORLD COURT", PURPLE, "gavel",
     "ICJ RULES TODAY ON ROHINGYA",
     "The world court delivers its judgment on whether Myanmar "
     "committed genocide against the Rohingya."),
    ("CULTURE", ORANGE, "game",
     "GTA VI ROLLS OUT WORLDWIDE",
     "Gamers enter Vice City as Grand Theft Auto VI begins its "
     "global rollout, 13 years after GTA V."),
    ("THE GULF", RED, "gulf",
     "SAUDI ALERTS LIFTED AFTER SCARE",
     "Saudi Arabia says the danger has passed in three southern "
     "cities after missile alerts."),
]


def draw_story(cv, x, y, w, h, story):
    kicker, colour, icon, headline, deck = story
    cv.rect(x, y, 6, h, colour)
    cv.text(x + 16, y + 10, kicker, 2, colour)
    draw_icon(cv, icon, x + w - 56, y + 6, colour)
    head_w = w - 16 - 64
    lines = wrap(headline, head_w, 3)
    yy = y + 34
    for ln in lines[:2]:
        cv.text(x + 16, yy, ln, 3, INK)
        yy += 24
    # The embedded 5x7 font only defines capitals, digits and punctuation,
    # so decks are rendered in capitals (newspaper style) — lowercase
    # letters would otherwise render as blanks.
    deck_lines = wrap(deck.upper(), w - 32, 2)
    yy += 6
    for ln in deck_lines[:3]:
        cv.text(x + 16, yy, ln, 2, SLATE)
        yy += 17


def draw():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 10, RED)
    cv.text_centre(28, "THE WORLD TODAY", 7, INK)
    cv.hline(16, 92, W - 32, INK)
    cv.rect(0, 100, W, 52, RED)
    cv.text_centre(112, "THURSDAY  -  19 NOVEMBER 2026", 4, PAPER)
    cv.text_centre(164, "EIGHT STORIES THAT DEFINED THE DAY", 2, INK)
    cv.hline(16, 190, W - 32, INK)

    margin, gap = 16, 8
    cell_w = (W - 2 * margin - gap) // 2
    cell_h = 194
    top = 200
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cell_w + gap)
        cy = top + (i // 2) * (cell_h + gap)
        cv.rect(cx, cy, cell_w, cell_h, (255, 255, 255))
        cv.rect(cx, cy, cell_w, 2, LIGHT)
        cv.rect(cx, cy + cell_h - 2, cell_w, 2, LIGHT)
        draw_story(cv, cx, cy, cell_w, cell_h, story)

    cv.hline(16, 988, W - 32, INK)
    cv.text_centre(998, "REPORTED 19 NOVEMBER 2026", 2, INK)
    return cv


# ---------------------------------------------------------------- PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
