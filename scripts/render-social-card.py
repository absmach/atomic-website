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
        glow = 0.72 * exp(-(((x - 1090) / 530) ** 2 + ((y - 570) / 380) ** 2))
        pixels[x, y] = tuple(round(a + (b - a) * glow) for a, b in zip(PAPER, (217, 202, 250)))
card = background.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.Resampling.BICUBIC)
draw = ImageDraw.Draw(card)


def label(x, y, text, size, color=INK, weight=650):
    draw.text((x * SCALE, y * SCALE), text, font=font(size, weight), fill=color, anchor="lt")


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


atom(86, 87, 48, VIOLET, 3.4)
label(123, 65, "atomic", 43, weight=750)
label(64, 202, "Imagine it.", 88, weight=750)
label(64, 303, "Build it", 88, VIOLET, weight=750)

DESCRIPTION = (
    "Turn your ideas into powerful, functional applications with AI. "
    "Just describe what you need, and let Atomic bring it to life"
)
body = font(24, 500)
line, y = "", 431
for word in DESCRIPTION.split():
    trial = f"{line} {word}".strip()
    if draw.textlength(trial, font=body) > 640 * SCALE:
        label(68, y, line, 24, "#4a4358", weight=500)
        line, y = word, y + 36
    else:
        line = trial
label(68, y, line, 24, "#4a4358", weight=500)

# An oversized brand tile stays recognizable when the card is reduced in a feed.
draw.rounded_rectangle((778 * SCALE, 161 * SCALE, 1132 * SCALE, 515 * SCALE),
                       radius=66 * SCALE, fill="#dfd4f6")
draw.rounded_rectangle((770 * SCALE, 149 * SCALE, 1124 * SCALE, 503 * SCALE),
                       radius=66 * SCALE, fill=VIOLET)
atom(947, 326, 306, "#ffffff", 13)

draw.line((68 * SCALE, 554 * SCALE, 1132 * SCALE, 554 * SCALE), fill="#ded6e9", width=SCALE)
label(68, 577, "FROM IDEA TO APP", 14, "#696471", weight=750)
label(965, 573, "atomicapp.dev", 21, weight=650)

output = ROOT / "dist/assets/atomic-social-v2.png"
card.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(output, optimize=True)
print(f"Rendered {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")
