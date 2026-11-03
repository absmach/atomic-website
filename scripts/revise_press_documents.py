#!/usr/bin/env python3
"""Prepare corrected press documents, retaining the approved layout and images.

Run with the original v21 offline press-kit directory as the sole argument.
The original kit and earlier public editions remain unchanged.
"""
from pathlib import Path
import json
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
EDITION = '2026-11-03-v22'
REPLACEMENTS = {
    'Launch date': 'Press-kit edition',
    'Use the confirmed plan prices above for editorial copy.':
        'Prices are proposed; subscriptions are not open. Final consumer totals include applicable taxes.',
    'Free ($0), Builder at $25/month, and Pro at $50/month.':
        'Proposed plans: Free ($0), Builder $25/month, Pro $50/month. Subscriptions are not open; final consumer totals include applicable taxes.',
    'Source downloads are available on Builder and Pro.':
        'Source downloads are included in the proposed Builder and Pro plans.',
    'Source downloads, searchable preview logs and collaboration require Builder or Pro.':
        'Source downloads, searchable preview logs and collaboration are included in the proposed paid plans.',
    'Builder and Pro support collaboration.':
        'The proposed Builder and Pro plans include collaboration.',
    'Builder and Pro let you download the app’s source code.':
        'The proposed Builder and Pro plans include app source downloads.',
    'Searchable preview logs on Builder and Pro':
        'Searchable preview logs, included in the proposed paid plans,',
    'Recent-session usage and account billing views show credits, time spent and plan information':
        'Usage and account views show recorded activity and available billing information',
}


def revise(text):
    for before, after in REPLACEMENTS.items():
        text = text.replace(before, after)
    return text


def main():
    kit = Path(sys.argv[1]).resolve()
    public = ROOT / 'dist/assets/press' / EDITION / '01-documents'
    sources = ROOT / 'content/press-documents'
    public.mkdir(parents=True, exist_ok=True)
    sources.mkdir(parents=True, exist_ok=True)
    for source in sorted((kit / '01-documents').iterdir()):
        if source.suffix in ('.html', '.css'):
            (sources / source.name).write_text(revise(source.read_text()))
        elif source.suffix == '.txt':
            (public / source.name).write_text(revise(source.read_text()))
        elif source.suffix == '.docx':
            target = public / source.name
            with zipfile.ZipFile(source) as original, zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as out:
                for item in original.infolist():
                    data = original.read(item.filename)
                    if item.filename == 'word/document.xml':
                        root = ET.fromstring(data)
                        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        for paragraph in root.findall('.//w:p', ns):
                            nodes = paragraph.findall('.//w:t', ns)
                            before = ''.join(n.text or '' for n in nodes)
                            after = revise(before)
                            if before != after:
                                nodes[0].text = after
                                for node in nodes[1:]:
                                    node.text = ''
                        data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    out.writestr(item, data)
    print(json.dumps({'sources': str(sources), 'output': str(public), 'media_kit': str(kit)}))


if __name__ == '__main__':
    main()
