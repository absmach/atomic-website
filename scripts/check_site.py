#!/usr/bin/env python3
"""Check generated page structure and all local links, assets, and fragments."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import struct
import json

ROOT = Path(__file__).resolve().parent.parent / 'dist'
CONTENT = ROOT.parent / 'content' / 'docs'

def pixel_size(path):
    """A PNG's or JPEG's width and height, read from its header."""
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n': return struct.unpack('>II', data[16:24])
    i = 2
    while i + 9 < len(data):
        marker, length = data[i + 1], struct.unpack('>H', data[i + 2:i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2): return struct.unpack('>HH', data[i + 5:i + 9])[::-1]
        i += 2 + length

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.h1, self.title, self.errors = path, set(), [], 0, 0, []
        self.solution_cards = []
        self.canonical = ''
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'data-solution-category' in a: self.solution_cards.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href', '')
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append(f'duplicate id: {a["id"]}')
            self.ids.add(a['id'])
        for attribute in ('href', 'src'):
            if attribute in a: self.links.append(a[attribute])
        if tag == 'img' and 'alt' not in a: self.errors.append('image missing alt attribute')
        if tag == 'img' and not ('width' in a and 'height' in a): self.errors.append(f'image missing width/height: {a.get("src")}')
        elif tag == 'img' and a.get('src', '').startswith('/') and a['src'].endswith(('.jpg', '.png')):
            source = ROOT / a['src'].lstrip('/')
            if source.exists() and pixel_size(source) != (int(a['width']), int(a['height'])):
                self.errors.append(f'image size {a["width"]}x{a["height"]} is not the file\'s {pixel_size(source)}: {a["src"]}')

pages = {p.resolve(): Page(p) for p in ROOT.rglob('*.html')}
errors = []
for path, page in pages.items():
    if page.h1 != 1: page.errors.append(f'expected one h1, got {page.h1}')
    if page.title != 1: page.errors.append('expected one title')
    for url in page.links:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc: continue
        if not parsed.path:
            target = path
        elif parsed.path.startswith('/'):
            target = ROOT / unquote(parsed.path.lstrip('/'))
        else:
            target = path.parent / unquote(parsed.path)
        if target.is_dir(): target /= 'index.html'
        target = target.resolve()
        if not target.exists(): page.errors.append(f'missing target: {url}')
        elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
            page.errors.append(f'missing fragment: {url}')
    errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in page.errors)

# Every guide has one content file and one generated page, and is reachable
# from the docs index and from the menu on every other guide.
guides = {p.parent.name for p in (ROOT / 'docs').glob('*/index.html')}
sources = {}
for source in CONTENT.rglob('*.html'):
    if source.stem in sources: errors.append(f'content/docs: {source.stem} is in two sections')
    sources[source.stem] = source
errors.extend(f'content/docs: {slug} has no generated page' for slug in sorted(set(sources) - guides))
errors.extend(f'docs/{slug}/index.html: no content file (stale generated page?)' for slug in sorted(guides - set(sources)))
index = pages[(ROOT / 'docs' / 'index.html').resolve()]
for slug in sorted(guides):
    if f'/docs/{slug}/' not in index.links: errors.append(f'docs/index.html: {slug} is not listed')
    for other in guides:
        if f'/docs/{slug}/' not in pages[(ROOT / 'docs' / other / 'index.html').resolve()].links:
            errors.append(f'docs/{other}/index.html: menu does not link {slug}')

# Keep the solutions catalogue and its generated routes in sync, and ensure
# every use case is reachable from the actual hub cards (not only the footer).
solutions = json.loads((ROOT.parent / 'content/solutions.json').read_text())
slugs = [item['slug'] for item in solutions]
if len(slugs) != len(set(slugs)): errors.append('content/solutions.json: duplicate solution slug')
solution_routes = {p.parent.name for p in (ROOT / 'solutions').glob('*/index.html')}
if solution_routes != set(slugs): errors.append('solutions: generated routes do not match the content catalogue')
hub = pages.get((ROOT / 'solutions/index.html').resolve())
if not hub or sorted(hub.solution_cards) != sorted(f'/solutions/{slug}/' for slug in slugs):
    errors.append('solutions/index.html: expected one hub card for every solution')
for slug in ['', *slugs]:
    route = '/solutions/' + (slug + '/' if slug else '')
    solution_page = pages.get((ROOT / route.lstrip('/') / 'index.html').resolve())
    if not solution_page or solution_page.canonical != 'https://atomicapp.dev' + route:
        errors.append(f'{route}: missing page or incorrect canonical URL')

if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, {len(guides)} guides, {len(slugs)} solutions; local links, fragments, assets, titles, headings, IDs, image alt text and sizes, docs index and menus, solution routes, cards and canonicals.')
