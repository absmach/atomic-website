# Atomic product website

A responsive, dependency-free, multi-page product site built from the Atomic app and launch plans. Atomic leads the brand; Abstract Machines is identified as the company behind the product. The project lives at the repository root; static hosting serves `dist/`.

## Generate and check

Run `python3 scripts/build_site.py` after changing content or shared markup. Run `python3 scripts/check_site.py` to validate every local page link, fragment, asset, heading, title, ID, and image alt attribute. Check JavaScript syntax with `node --check dist/site.js` and `node --check dist/app.js`.

`content/home.html` contains the original homepage presentation. `scripts/build_site.py` owns the shared navigation and footer, homepage additions, pricing copy, guides, articles, and legal drafts. Generated HTML is committed in `dist/`, so hosting still requires no build or installation. Edit those sources rather than generated HTML. Shared styles and JavaScript in `dist/` are maintained directly.

## Site map

- `/`: product introduction, interactive examples, workspace views, and early-access inquiry.
- `/pricing/`: proposed Free, $25/month Pro, and later $50/month Business plans in USD; no checkout or unverified credit allowance.
- `/docs/`: searchable library with getting-started, building, source/data, and publishing guides. These explain the early-access workflow, not unverified account or interface procedures.
- `/blog/`: two original product-perspective articles. No fabricated launch announcements, customer stories, or release dates.
- `/about/`: Atomic’s purpose and the team at Abstract Machines, with links to the company, Atom, and its public open-source work.
- `/security/`: verified product boundaries and the existing team contact for reporting concerns; no invented certifications or SLA.
- `/legal/`: draft Privacy Notice, Terms of Service, Acceptable Use Policy, DPA, Subprocessor List, and Cookies & Storage Notice. Each draft is clearly marked not effective and excluded from indexing.
- `dist/404.html`: branded fallback for hosts supporting a static 404 page.

The header shows Product, Docs, Pricing, and About, followed by Get early access. Resources is a footer grouping for Documentation, Blog, Security & trust, About Atomic, and Contact; there is no separate Resources page.

Every page includes shared responsive navigation, a skip link, an Atomic-led footer, and larger social placeholders with inline SVG logos and visible channel names, explicitly labeled coming soon. Social labels have no invented account URLs. Nested pages use root-relative links and work on a host serving `dist/` at its root.

## Before public launch

The website structure and content are prepared; operational and commercial facts still need confirmation. The legal pages are substantive drafting material, not effective agreements or a completed compliance program.

- Confirm the full contracting/controller entity, registered address, company identifiers, applicable jurisdictions, and legal contacts. Abstract Machines is a brand reference until those details are verified.
- Approve prices, available plan features, credit quantities/rates, retry treatment, hosting allowances, taxes, billing/renewal, cancellation, refunds, and credit expiry. Business is explicitly a later-release proposal.
- Finalize and review the legal drafts with counsel, including consumer rights and limitations of liability. Complete the DPA processing description, verified security measures, transfer clauses, and acceptance mechanism.
- Inventory actual vendors, their roles, processing/access locations, retention, and AI training settings. Publish an approved subprocessor register and change-notification process.
- Verify inquiry, account, prompt, log, billing, and backup retention/deletion rules and the customer data export process.
- Audit cookies, storage, and logging on the actual deployed host, including its access gate. The application itself sets no cookies or persistent browser storage; hosting behavior has not been certified. Add consent controls if the actual technologies require them.
- Replace the email inquiry with the approved onboarding/payment flow when available, add final effective policies and acceptance records, and add verified social URLs.
- The production domain is `atomicapp.dev`, with homepage canonical and social metadata configured. Complete canonical metadata for the remaining pages, submit a domain-specific sitemap, and review indexing before launch. Draft legal pages remain `noindex, nofollow` until finalized.

Legal drafting references reviewed on 19 October 2026: [European Commission transparency and security guidance](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en), [EU cookie guidance](https://europa.eu/youreurope/business/growing/digitalising/online-privacy/index_en.htm), and [European Commission SCC guidance](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/new-standard-contractual-clauses-questions-and-answers-overview_en). Pricing is informed by [Lovable's pricing](https://lovable.dev/pricing); Atomic's draft allowances and commercial terms are not copied from it.

## Preview

Run `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist`, then open http://localhost:4173.

## Page and interactions

- `dist/index.html`: page copy, examples, metadata, and native email-draft dialog.
- `dist/styles.css`: shared visual system and responsive layouts.
- `dist/launch.css`: centered prompt opening, app preview cards, and framed product showcase.
- `dist/app.js`: product image switch, booking/shop/portal demos, and early-access email preparation.
- `dist/site.js`: shared mobile navigation, footer year, and documentation filtering.
- `dist/pages.css`: shared brand and header styling for every page, multi-page shell, pricing, resource cards, articles, legal layouts, and footer.
- `dist/assets/`: local brand mark, product images, fonts, and font licenses.

The booking example supports requesting a session, reviewing it as the studio owner, confirming, updating, and resetting. The shop supports adding sample items and clearing the bag. The portal switches project milestones. All example state is in memory and resets on reload; nothing is booked, purchased, or sent to a server.

The page opens with an idea composer. Suggested prompts fill the input, and the app preview cards open their matching interactive demos. Both the opening composer and closing early-access form validate an idea and open a review dialog. Ctrl+Enter or Command+Enter also submits the idea. The visitor can open a prefilled email addressed to `info@absmach.eu`, or copy the draft. This prepares an early-access inquiry; it does not generate an app, collect a signup, or send email automatically. The address was verified on https://www.absmach.eu/. Replace this workflow with the production signup URL or an approved signup service when available.

## Content boundaries

The composer cycles through example ideas only while empty and unfocused. It preserves typed text, includes a pause control, and respects reduced-motion preferences. Keyboard focus is shown on the outer composer rather than the inner textarea. App thumbnails use colored compositions; the workspace uses a layered frame, and the Atom diagram is responsive HTML/SVG.

Pricing now shows proposed launch prices; final entitlements and launch date remain unannounced. Complete app packaging and deployment choice remain roadmap items. Source export does not include users, business data, or hosting; frontend rollback does not restore business data. Do not represent the interactive examples or supplied product images as live customer results.

Product images and the Atomic mark come from `~/ideas/vc/atomic/pitch-deck`. Images are illustrative sample-app views and are labeled on the page. The three `*-preview.png` thumbnails are browser captures of this page’s interactive examples. Typography consistently uses the locally hosted, preloaded Manrope variable font. Font licenses are included under `dist/assets/fonts/`.

## Social preview

The page includes Open Graph and X large-image card metadata pointing to
`https://atomicapp.dev/assets/atomic-social-v1.png`. The 1200 × 630 PNG uses the
existing Atomic mark, palette, and bundled Manrope font. Regenerate it with
`python3 scripts/render-social-card.py` (requires Pillow with FreeType/WOFF2
support for authoring; the website still has no runtime dependencies).

Deploy `dist/index.html` and the image together to the public domain. Verify
that the image URL returns an actual PNG without authentication. When changing
the artwork, use a new versioned filename and update both image meta tags to
avoid stale image caches. Social platforms may retain previously fetched cards.

## Hosting

The site deploys to Cloudflare as a static-assets Worker on every push to `main`, through Cloudflare Workers Builds connected to this repository. `wrangler.jsonc` names the Worker (`atomic-website`) and serves `dist/`. No build step or package installation is required. The site has no external fonts, analytics, or runtime dependencies.

Workers Builds settings (Cloudflare dashboard → Workers & Pages → `atomic-website` → Settings → Build):

- Git repository: `absmach/atomic-website`, production branch `main`
- Build command: empty
- Deploy command: `npx wrangler deploy`
- Root directory: `/`

Custom domains `atomicapp.dev` and `www.atomicapp.dev` are declared in `wrangler.jsonc` routes; deploy creates their DNS records and certificates. The `atomicapp.dev` zone must be in the same Cloudflare account, with no other DNS records on those hostnames.

Manual deploy from the repository root: `npx wrangler deploy`.

`.openai/hosting.json` retains the existing Sites identity and also uses `dist` as the public directory.
