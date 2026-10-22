#!/usr/bin/env python3
"""Check generated page structure and all local links, assets, and fragments."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent / 'dist'
CONTENT = ROOT.parent / 'content' / 'docs'

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.h1, self.title, self.errors = path, set(), [], 0, 0, []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.title += 1
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append(f'duplicate id: {a["id"]}')
            self.ids.add(a['id'])
        for attribute in ('href', 'src'):
            if attribute in a: self.links.append(a[attribute])
        if tag == 'img' and 'alt' not in a: self.errors.append('image missing alt attribute')
        if tag == 'img' and not ('width' in a and 'height' in a): self.errors.append(f'image missing width/height: {a.get("src")}')

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

if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages, {len(guides)} guides; local links, fragments, assets, titles, headings, IDs, image alt text and sizes, and the docs index and menus.')
