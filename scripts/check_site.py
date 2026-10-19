#!/usr/bin/env python3
"""Check generated page structure and all local links, assets, and fragments."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent / 'dist'

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
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} pages; local links, fragments, assets, titles, headings, IDs, and image alt attributes.')
