#!/usr/bin/env python3
"""Compress rendered press PDFs and package them within the static-host limit."""
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / 'dist/assets/press/2026-11-03-v22'


def main():
    with tempfile.TemporaryDirectory(prefix='atomic-press-pdf-') as temp:
        for source in (BASE / '01-documents').glob('*.pdf'):
            target = Path(temp) / source.name
            subprocess.run([
                'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.7',
                '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dBATCH', '-dQUIET',
                '-sOutputFile=' + str(target), str(source),
            ], check=True)
            if target.stat().st_size < source.stat().st_size:
                source.write_bytes(target.read_bytes())
    archive = BASE / 'atomic-editorial-documents-v22.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for file in sorted((BASE / '01-documents').iterdir()):
            bundle.write(file, '01-documents/' + file.name)
        bundle.write(BASE / 'DOCUMENTS.txt', 'DOCUMENTS.txt')
    if archive.stat().st_size >= 25_000_000:
        raise ValueError('The documents archive exceeds the static-host size budget')
    page = ROOT / 'content/press.html'
    text = page.read_text()
    text = re.sub(r'Download documents · ZIP, [0-9.]+ MB',
                  f'Download documents · ZIP, {archive.stat().st_size / 1e6:.1f} MB', text)
    book = BASE / '01-documents/00-complete-press-book.pdf'
    text = re.sub(r'Read the press book · PDF, [0-9.]+ MB',
                  f'Read the press book · PDF, {book.stat().st_size / 1e6:.1f} MB', text)
    page.write_text(text)
    print(f'Packaged {archive.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
