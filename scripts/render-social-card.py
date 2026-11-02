"""Compatibility entry point for the SVG-based social-card renderer.

Requires Node, Playwright and Chromium for authoring. Set PLAYWRIGHT_MODULE and
CHROME_BIN to use existing installations. Generated PNG is committed.
"""
from pathlib import Path
import subprocess
subprocess.run(['node', str(Path(__file__).with_suffix('.mjs'))], check=True)
