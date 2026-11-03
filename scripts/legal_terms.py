"""Load editable, versioned ToS clauses without publishing internal notes."""
from datetime import date
from html import unescape
import json
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parent.parent / 'content/legal/terms'


def read_clauses(language):
    source = (SOURCE / f'{language}.html').read_text()
    pattern = r'<section id="([a-z0-9-]+)">\s*<h2>(.*?)</h2>\s*(.*?)\s*</section>'
    clauses = re.findall(pattern, source, re.DOTALL)
    if not clauses or re.sub(pattern, '', source, flags=re.DOTALL).strip():
        raise ValueError(f'Terms {language}: expected section IDs, h2 titles and clause bodies')
    ids = [clause[0] for clause in clauses]
    if len(set(ids)) != len(ids):
        raise ValueError(f'Terms {language}: duplicate clause IDs')
    return clauses


def load_terms():
    metadata = json.loads((SOURCE / 'metadata.json').read_text())
    revision = date.fromisoformat(metadata['version'])
    if metadata['status'] not in ('proposed', 'effective'):
        raise ValueError('Terms status must be proposed or effective')
    en, fr = read_clauses('en'), read_clauses('fr')
    if [c[0] for c in en] != [c[0] for c in fr]:
        raise ValueError('English and French terms must have matching clause IDs and order')
    months_en = ('January February March April May June July August September October November December').split()
    months_fr = ('janvier février mars avril mai juin juillet août septembre octobre novembre décembre').split()
    return dict(
        slug='terms', titles=metadata['titles'], intros=metadata['intros'],
        draft=metadata['status'] == 'proposed', version=metadata['version'],
        updated_en=f'{revision.day} {months_en[revision.month - 1]} {revision.year}',
        updated_fr=f'{revision.day} {months_fr[revision.month - 1]} {revision.year}',
        sections=[(e[0], (unescape(e[1]), unescape(f[1])), (e[2], f[2])) for e, f in zip(en, fr)],
    )
