#!/usr/bin/env python3
"""Build the French legal download. Requires Pandoc and XeLaTeX."""
from html import escape
from pathlib import Path
import re
import subprocess
import tempfile

from legal_content import DOCUMENTS, DOCUMENT_ORDER, FRENCH_PDF, UPDATED_FR

ROOT = Path(__file__).resolve().parent.parent


def build():
    documents = {d['slug']: d for d in DOCUMENTS}
    parts = ['<html><head><meta charset="utf-8"></head><body>',
             '<p>Les conditions de service s’appliquent à l’offre Atomic acceptée. '
             'L’accord de traitement s’applique après acceptation avec sa fiche de traitement. '
             'La notice de confidentialité précise les traitements qu’elle couvre.</p>']
    for slug in DOCUMENT_ORDER:
        d = documents[slug]
        status = 'Projet d’accord — Pas encore en vigueur' if d['draft'] else ('Notice de confidentialité' if slug == 'privacy' else 'Version')
        parts.append(f'<h1 id="{slug}">{escape(d["titles"][1])}</h1>'
                     f'<p><strong>{status}</strong> · {d.get("updated_fr", UPDATED_FR)}</p>'
                     f'<p>{escape(d["intros"][1])}</p>')
        if d['draft']:
            parts.append('<p>Les prérequis opérationnels et contractuels indiqués '
                         'doivent être complétés avant acceptation.</p>')
        for sid, titles, texts in d['sections']:
            parts.append(f'<h2 id="{slug}-{sid}">{escape(titles[1])}</h2>{texts[1]}')
    parts.append('</body></html>')
    html = ''.join(parts)
    # Cross-references stay inside the downloadable document.
    html = re.sub(r'href="/legal/fr/([^/]+)/#([^"]+)"', r'href="#\1-\2"', html)
    html = re.sub(r'href="/legal/fr/([^/]+)/"', r'href="#\1"', html)
    html = html.replace('href="/legal/fr/"', 'href="#notice"')
    html = re.sub(r'href="/(?!/)([^"]*)"', r'href="https://atomicapp.dev/\1"', html)
    output = ROOT / 'dist' / FRENCH_PDF.lstrip('/')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='atomic-legal-') as temp:
        source = Path(temp) / 'legal-fr.html'
        source.write_text(html)
        header = Path(temp) / 'language.tex'
        header.write_text(r'\AtBeginDocument{\hypersetup{pdflang={fr-FR}}}' + '\n' + r'\renewcommand{\contentsname}{Sommaire}')
        subprocess.run([
            'pandoc', str(source), '--from=html', '--pdf-engine=xelatex',
            '--toc', '--toc-depth=1', '--metadata=toc-title:Sommaire',
            '--metadata=title:Atomic — Documents juridiques',
            '--metadata=author:Abstract Machines SAS',
            f'--metadata=date:{UPDATED_FR}',
            '--variable=papersize:a4', '--variable=geometry:margin=22mm', '--variable=fontsize:10pt',
            '--variable=mainfont:Noto Serif', '--variable=colorlinks:true',
            '--include-in-header', str(header), '--output', str(output),
        ], check=True)
    print(f'Generated {output.relative_to(ROOT)}')


if __name__ == '__main__':
    build()
