# Updating the Terms of Service

Edit `en.html` and `fr.html`. Each clause is a `<section id="stable-name">`
containing an `<h2>` title and ordinary HTML paragraphs or lists. Add clauses in
both languages with the same ID and position; keep existing IDs so shared links
continue to work. Renumber visible headings when needed. The build rejects
missing translations, duplicate IDs and mismatched clause order.

Set `version` in `metadata.json` to the revision date (`YYYY-MM-DD`). This sets
the date on the English page and the French PDF's terms section. `status` remains
`proposed` until the agreement and operational prerequisites are ready; changing
it to `effective` is a publication setting, not customer acceptance.

Regenerate and validate:

```sh
python3 scripts/build_legal_pdf.py
python3 scripts/build_site.py
python3 scripts/check_site.py
```

The PDF command requires Pandoc, XeLaTeX and Noto Serif. Outputs are committed
with the source; the production static host needs none of these tools. Both
formats use these same clause files, so do not edit generated pages or PDFs.

Record the change in `CHANGELOG.md`. Keep a dated copy of each agreement actually
accepted by a customer, its order details, acceptance record and applicable
version; the website's latest version must not overwrite those records. Git
history supports editorial review but does not replace customer notices or
delivery on a durable medium.

Typographical clarifications must not silently change rights. Material changes
follow the agreement's notice and consent rules and mandatory consumer law.
Publishing new text does not automatically amend existing contracts. Supplier
changes also follow the separate DPA notification and authorization process.
