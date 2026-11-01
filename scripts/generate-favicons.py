"""Rasterize the existing Atomic SVG mark for browser and Apple icon support.

Run with Python, Pillow and rsvg-convert installed. Generated files are tracked.
"""
from pathlib import Path
from io import BytesIO
import subprocess
from PIL import Image

dist = Path(__file__).resolve().parent.parent / 'dist'
svg = dist / 'favicon.svg'
for size, name in [(32, 'favicon-32x32.png'), (180, 'apple-touch-icon.png')]:
    subprocess.run(['rsvg-convert', '-w', str(size), '-h', str(size), '-o', str(dist / name), str(svg)], check=True)
png = subprocess.check_output(['rsvg-convert', '-w', '64', '-h', '64', str(svg)])
Image.open(BytesIO(png)).save(dist / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
