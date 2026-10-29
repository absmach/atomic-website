"""Render the checked-in social card: python3 scripts/render-social-card.py.

Requires Pillow with FreeType/WOFF2 support (authoring only; no website dependency).
Uses the site's bundled Manrope font and the geometry of assets/atomic.svg.
"""

from math import cos, exp, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 2
WIDTH, HEIGHT = 1200, 630
PAPER = (251, 250, 248)
INK = "#221c30"
VIOLET = "#6544ed"


def font(size, weight=650):
    face = ImageFont.truetype(
        str(ROOT / "dist/assets/fonts/manrope-latin.woff2"), size * SCALE
    )
    face.set_variation_by_axes([weight])
    return face


# A restrained lavender glow echoes the site's opening section.
background = Image.new("RGB", (WIDTH, HEIGHT))
pixels = background.load()
for y in range(HEIGHT):
    for x in range(WIDTH):
        glow = 0.6 * exp(-(((x - 600) / 640) ** 2 + ((y - 700) / 330) ** 2))
        pixels[x, y] = tuple(round(a + (b - a) * glow) for a, b in zip(PAPER, (217, 202, 250)))
card = background.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.Resampling.BICUBIC)
draw = ImageDraw.Draw(card)


def atom(cx, cy, size, color, stroke):
    """The three ellipses and nucleus from the existing Atomic brand mark."""
    unit = size / 28
    for angle in (0, pi / 3, 2 * pi / 3):
        mask = Image.new("L", card.size)
        pen = ImageDraw.Draw(mask)
        for offset, fill in ((stroke / 2, 255), (-stroke / 2, 0)):
            points = []
            for step in range(360):
                theta = step * pi / 180
                x = (11.2 * unit + offset) * cos(theta)
                y = (4.6 * unit + offset) * sin(theta)
                points.append((round((cx + x * cos(angle) - y * sin(angle)) * SCALE),
                               round((cy + x * sin(angle) + y * cos(angle)) * SCALE)))
            pen.polygon(points, fill=fill)
        card.paste(color, (0, 0), mask)
    r = 3.1 * unit
    draw.ellipse(((cx - r) * SCALE, (cy - r) * SCALE,
                  (cx + r) * SCALE, (cy + r) * SCALE), fill=color)


def width(text, face, tracking=0.0):
    """Advance of the text in card pixels, with CSS-style letter-spacing in em."""
    return draw.textlength(text, font=face) / SCALE + tracking * face.size / SCALE * len(text)


def tracked(x, y, text, face, color, tracking):
    """Draw text left-aligned at its vertical middle, keeping kerning and adding tracking."""
    for i, char in enumerate(text):
        offset = draw.textlength(text[:i], font=face) / SCALE + tracking * face.size / SCALE * i
        draw.text(((x + offset) * SCALE, y * SCALE), char, font=face, fill=color, anchor="lm")


# Just the brand, as in the site header (weight 600, -0.075em, mark about
# 1.1x the type), with the hero's tagline (weight 650, -0.052em) beneath.
# Compact previews such as Slack's show a square thumbnail cropped from the
# centre, so the lockup is sized to fill the middle 630 x 630 with a margin.
SAFE_WIDTH = 560
NAME, NAME_TRACK, TAG_TRACK = "atomic", -0.075, -0.052
first, second = "Imagine it. ", "Build it."


def lockup_width(name_size):
    name = font(name_size, 600)
    mark_width = name_size * 1.1 * 22.4 / 28 + name_size * 0.06
    row = mark_width + name_size * 0.24 + width(NAME, name, NAME_TRACK)
    tag = width(first + second, font(round(name_size * 0.53), 650), TAG_TRACK)
    return max(row, tag)


NAME_SIZE = 100
while lockup_width(NAME_SIZE + 1) <= SAFE_WIDTH:
    NAME_SIZE += 1
TAG_SIZE = round(NAME_SIZE * 0.53)
name, tagline = font(NAME_SIZE, 600), font(TAG_SIZE, 650)
MARK, STROKE, GAP = NAME_SIZE * 1.1, NAME_SIZE * 0.06, NAME_SIZE * 0.24
mark_width = MARK * 22.4 / 28 + STROKE

# Centre the two lines as one block: name row, a gap, then the tagline.
ROW_HEIGHT, LINE_GAP = MARK * 0.85, NAME_SIZE * 0.42
block = ROW_HEIGHT + LINE_GAP + TAG_SIZE
row_y = (HEIGHT - block) / 2 + ROW_HEIGHT / 2
tag_y = row_y + ROW_HEIGHT / 2 + LINE_GAP + TAG_SIZE / 2

row = mark_width + GAP + width(NAME, name, NAME_TRACK)
left = (WIDTH - row) / 2
atom(left + mark_width / 2, row_y, MARK, VIOLET, STROKE)
tracked(left + mark_width + GAP, row_y - NAME_SIZE * 0.05, NAME, name, INK, NAME_TRACK)

x = (WIDTH - width(first + second, tagline, TAG_TRACK)) / 2
tracked(x, tag_y, first, tagline, INK, TAG_TRACK)
tracked(x + width(first, tagline, TAG_TRACK), tag_y, second, tagline, VIOLET, TAG_TRACK)
print(f"Name {NAME_SIZE}px, tagline {TAG_SIZE}px, lockup {lockup_width(NAME_SIZE):.0f}px wide")

output = ROOT / "dist/assets/atomic-social-v3.png"
card.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(output, optimize=True)
print(f"Rendered {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")
