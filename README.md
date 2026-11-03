# Atomic product website

A responsive, dependency-free, multi-page product site built from the Atomic app and launch plans. Atomic leads the brand; Abstract Machines is identified as the company behind the product. The project lives at the repository root; static hosting serves `dist/`.

## Generate and check

Run `python3 scripts/build_site.py` after changing content or shared markup. Run `python3 scripts/check_site.py` to validate every local page link, fragment, asset, heading, title, ID, and image alt attribute. Check JavaScript syntax with `node --check dist/site.js`, `node --check dist/app.js`, and `node --check dist/early-access.js`. Run signup and consent regression tests with `node --test src/worker.test.js src/consent.test.js`.

`content/home.html` contains the original homepage presentation. `scripts/build_site.py` owns the shared navigation and footer, homepage additions, pricing copy and articles. `scripts/legal_content.py` contains the legal notices. Its English/French privacy sections cover the marketing website, early-access requests and the Atomic service; keep both languages aligned. Terms of Service are edited in `content/legal/terms/en.html` and `fr.html`, with their version and status in `metadata.json`; see [the editing guide](content/legal/terms/README.md). Run `python3 scripts/build_legal_pdf.py` after legal-copy changes to refresh the French download (requires Pandoc, XeLaTeX and Noto Serif).

Each documentation guide's body is `content/docs/<section>/<slug>.html`: a run of `<section id="…"><h2>…</h2>…</section>` blocks, from which the page's contents list is read. `DOCS` in `scripts/build_site.py` lists the sections and, in order, each guide's slug, title, card summary, introduction and reading time. The docs index, the docs menu on every guide and the previous/next links follow that order. A guide is served at `/docs/<slug>/` whichever section holds it, so moving it between sections keeps its address. To add a guide, write its content file and add it to `DOCS`. Reading times are computed from each guide's words.

Documentation screenshots in `dist/assets/docs/` are 1440 px wide captures of a local Atomic Builder (cropped to one section where a guide is about that section), using an app created from the Salon Booking template so no model was called. Retake them when the screens they show change. Every `<img>` needs `width` and `height` that match the file; `check_site.py` compares them. `check_site.py` fails when a content file and its generated page do not match one to one, or when a guide is missing from the index or a menu. Generated HTML is committed in `dist/`, so hosting still requires no build or installation. Edit those sources rather than generated HTML. Shared styles and JavaScript in `dist/` are maintained directly.

## Site map

- `/solutions/`: audience-filtered solutions hub with six focused pages: `/solutions/websites/`, `/solutions/online-stores/`, `/solutions/booking-apps/`, `/solutions/client-portals/`, `/solutions/internal-tools/`, and `/solutions/prototypes/`. Original copy is in `content/solutions.json`; `scripts/solutions.py` owns the reusable layout and illustrative HTML/CSS app compositions. Styles and filters live in `dist/solutions.css` and `dist/solutions.js`. During early access, every solutions hero uses “Request Early Access” as its primary CTA; the hub’s secondary CTA is “Find your starting point”. The original per-solution launch labels remain in the content catalogue for use after launch. Early-access buttons and links point to `/early-access/`. A plain click opens the wizard in a dialog where the visitor is; opened in a new tab, shared, or without JavaScript, the link opens the page. Older `/#early-access` links open the dialog too, and still land at the homepage hero when visited directly. The closing idea forms open the wizard too, at the second step when an idea was typed and at the first when not. Starter briefs prefill the homepage composer for review before the visitor submits it to open the wizard; no app is generated or signup sent by following a prompt. The URL's idea parameter is removed after prefilling. See [research and design rationale](docs/solutions-design.md) and [photography sources](dist/assets/solutions/README.md).

- `/`: product introduction, interactive examples, workspace views, and early-access inquiry.
- `/early-access/`: the early-access wizard as a page of its own, with a link that can be shared or used in campaigns (UTM tags are kept). `dist/early-access.js` puts the wizard in the page’s card here and in a dialog on every other page. `?idea=` fills in the idea and starts at the second step, then is removed from the URL.
- `/pricing/`: proposed Free, $25/month Builder (2,500 credits), and $50/month Pro (5,000 credits) plans in USD. Free gives 250 credits once (they do not renew), and can browse but not download source; searchable preview logs are a paid plan's. Paid-plan top-ups are $10 for 1,000 credits. One credit is $0.01 of Atomic usage; charges can be fractional, monthly credits reset, and purchased credits do not expire. The feature comparison lists 1 / 10 / 20 published apps and proposes 0 / 5 / 10 invited collaborators per app, excluding the owner. Free is a solo plan with a backend, database, and user authentication for one app, a “Made with Atomic” badge on its published app, and each app's latest version plus one to go back to; Builder and Pro include backends for every app, collaboration, no badge, and 100 versions or every version of history. The comparison also lists custom domains (0 / 1 / 10), apps (3 / 20 / 50), previews open at once (1 / 3 / 5) and storage (2 / 25 / 100 GB). Cards group concrete building, publishing, and collaboration tools below a price/CTA panel and credit/app capacity strip, inspired by Lovable’s feature hierarchy. The comparison also covers canvas/theme controls, annotations, design references, app access, frontend rollback, preview logs, source downloads, and usage history. Integrations (Builder and Pro), advanced metrics and monitoring, and single sign-on (Pro) are listed as coming soon, not as available; no SCIM, priority support, or other unqualified enterprise feature is promised. No checkout is open.
- `/docs/`: searchable product documentation, 28 guides in seven sections (Get started, Build, Canvas, Data and users, Publish and run, Versions and source, Usage and help), each guide with the docs menu, an on-page contents list and previous/next links. Guides describe the product as it works in the Atomic repository's `main`; plan amounts are left to `/pricing/`. These explain the early-access workflow, not unverified account or interface procedures.
- `/blog/`: two existing product-perspective articles; launch and later posts can be added separately.
- `/press/`: the public visual press-kit index, including editorial documents, logos, all product screenshots, videos, portraits, social artwork and media contact. The ZIP and original screenshots/portraits download from the published GitHub release; previews and documents are static website assets.
- `/about/`: Atomic’s purpose and the team at Abstract Machines, with links to the company, Atom, and its public open-source work.
- `/security/`: verified product boundaries and the existing team contact for reporting concerns; no invented certifications or SLA.
- `/legal/`: three concise documents: Terms & company details (including acceptable use), Privacy & Cookies (including provider information), and a customer DPA. French text is one downloadable PDF linked from the legal documents hub, not from each product page or individual agreement; no separate French pages. Legal enquiries use info@absmach.eu. The published terms apply when accepted with an offer; the DPA requires acceptance with its completed processing schedule. Publication does not certify operational compliance. Old legal URLs redirect to the relevant sections. Private review evidence stays in ignored `private/legal/`.
- `dist/404.html`: branded fallback for hosts supporting a static 404 page.

The header has the logo on the left, Product, Solutions, Docs, Blog, Pricing, and About centred, and a Request early access button on the right; the mobile menu ends with the same link. The footer includes all six solution pages. Resources is a footer grouping for Documentation, Blog, Security & trust, About Atomic, and Contact; there is no separate Resources page.

Every page has a light and a dark theme. It follows the visitor's system until they choose with the header's theme button (match system, light, dark), which is remembered in the browser. A script in each page's head applies it before the page is drawn; `dist/dark.css` holds the dark rules, all under `html[data-theme=dark]`. Pictures of apps (the home page's examples and demo, solution mock-ups, product screenshots) keep their light colours in both themes.

Every page includes shared responsive navigation, a skip link, and an Atomic-led footer. The footer links to Atomic's X and Instagram profiles and Abstract Machines' GitHub and LinkedIn profiles. Nested pages use root-relative links and work on a host serving `dist/` at its root.

## Before public launch

The website structure and content are prepared; operational and commercial facts still need confirmation. The legal pages are substantive drafting material, not effective agreements or a completed compliance program.

- Company identity is verified in the legal notice. A company telephone number is still required for the current legal notice under LCEN Article 1-1; do not publish a personal number. Appoint the consumer mediator before offering consumer contracts.
- Implement and validate the proposed Free, Builder, and Pro catalog and credit rules before opening subscriptions, including Free’s one-backend-app and collaboration restrictions. Confirm collaboration, storage, bandwidth, and concurrency limits; qualify hosting rates and protected budgets; finalize retry treatment, taxes, cancellation, refunds, and retention rules.
- Finalize and review the legal drafts with counsel, including consumer rights and limitations of liability. Complete the DPA processing description, verified security measures, transfer clauses, and acceptance mechanism.
- Inventory actual vendors, their roles, processing/access locations, retention, and AI training settings. Supply the approved subprocessor register privately with the customer DPA and implement written change notifications. Public notices disclose meaningful recipient categories without publishing sensitive infrastructure details.
- Verify inquiry, account, prompt, log, billing, and backup retention/deletion rules and the customer data export process.
- Link `/legal/privacy/` from the product's signup and account/privacy settings before collecting product information. The notice describes supported data uses, not proof of the active deployment: verify enabled sign-in, dictation, AI and payment providers, actual retention criteria (including recordings, provider copies and backups), and vendor data-use settings before onboarding. The DPA's restriction on independent model training is not a verified blanket statement about every vendor.
- Audit cookies, storage, and logging on the actual deployed host, including its access gate. The website stores consent and theme preferences locally and documentation navigation in session storage; deployed hosting/tag behavior has not been certified. Add consent controls if the actual technologies require them.
- Replace the early-access waitlist with the approved onboarding/payment flow when available, add final effective policies and acceptance records, and add any remaining social channels when their official URLs are confirmed.
- The production domain is `atomicapp.dev`, with homepage canonical and social metadata configured. Complete canonical metadata for the remaining pages, submit a domain-specific sitemap, and review indexing before launch. Published legal documents are indexable; the French download is excluded from indexing.

Legal drafting references reviewed on 19 October 2026: [European Commission transparency and security guidance](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en), [EU cookie guidance](https://europa.eu/youreurope/business/growing/digitalising/online-privacy/index_en.htm), and [European Commission SCC guidance](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/new-standard-contractual-clauses-questions-and-answers-overview_en). Pricing is informed by [Lovable's pricing](https://lovable.dev/pricing); Atomic's draft allowances and commercial terms are not copied from it.

## Preview

Run `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist`, then open http://localhost:4173.

## Page and interactions

- `dist/index.html`: page copy, examples, metadata, and native email-draft dialog.
- `dist/styles.css`: shared visual system and responsive layouts.
- `dist/launch.css`: centered prompt opening, app preview cards, and framed product showcase.
- `dist/app.js`: product image switch, booking/shop/portal demos, and the idea composer.
- `dist/early-access.js`, `dist/early-access.css`: early-access wizard.
- `src/worker.js`: `/api/early-access` endpoint (Turnstile verification, Listmonk subscriber upsert).
- `dist/site.js`: shared mobile navigation, footer year, and documentation filtering.
- `dist/pages.css`: shared brand and header styling for every page, multi-page shell, pricing, resource cards, articles, legal layouts, and footer.
- `dist/assets/`: local brand mark, product images, fonts, and font licenses.

The booking example supports requesting a session, reviewing it as the studio owner, confirming, updating, and resetting. The shop supports adding sample items and clearing the bag. The portal switches project milestones. All example state is in memory and resets on reload; nothing is booked, purchased, or sent to a server.

The page opens with an idea composer. Suggested prompts fill the input, and the app preview cards open their matching interactive demos. Submitting either the opening composer or the closing form opens the early-access wizard (`dist/early-access.js`, styles in `dist/early-access.css`): idea, project, role, then name and email with a Cloudflare Turnstile check. The answers are posted to `/api/early-access`, handled by `src/worker.js`, which verifies the Turnstile token and stores the subscriber and answers as attributes in Listmonk. See "Early access signup" below.

## Content boundaries

The composer cycles through example ideas only while empty and unfocused. It preserves typed text and respects reduced-motion preferences. Keyboard focus is shown on the outer composer rather than the inner textarea. App thumbnails use colored compositions; the workspace uses a layered frame, and the Atom diagram is responsive HTML/SVG.

Pricing shows the agreed launch proposal with credit quantities and top-up rules. The launch date, operational limits, and protected hosting controls remain to be confirmed. The internal 3× direct-cost multiplier is a commercial modeling assumption, not public pricing copy or a backend change in this repository. Complete app packaging and deployment choice remain roadmap items. Source export does not include users, business data, or hosting; frontend rollback does not restore business data. Do not represent the interactive examples or supplied product images as live customer results.

Product images and the Atomic mark come from `~/ideas/vc/atomic/pitch-deck`. Images are illustrative sample-app views and are labeled on the page. The three `*-preview.png` thumbnails are browser captures of this page’s interactive examples. Typography consistently uses the locally hosted, preloaded Manrope variable font. Font licenses are included under `dist/assets/fonts/`.

## Social preview

Every page includes Open Graph and X large-image card metadata (`SOCIAL_IMAGE` in
`scripts/build_site.py`; the homepage's tags are in `content/home.html`) pointing to
`https://atomicapp.dev/assets/atomic-social-v4.png`. The 1200 × 630 PNG shows only
the Atomic mark and name with the tagline “Imagine it. Build it.”, centred on the
site’s paper background with a soft lavender glow, using the brand palette and the
bundled Manrope font at the header and hero letter-spacing. Regenerate it with
`python3 scripts/render-social-card.py` (requires Node, Playwright and Chromium
for authoring; the website still has no runtime dependencies).

Deploy `dist/index.html` and the image together to the public domain. Verify
that the image URL returns an actual PNG without authentication. When changing
the artwork, use a new versioned filename, then update `SOCIAL_IMAGE` and the two
image meta tags in `content/home.html` to avoid stale image caches. Social platforms may retain previously fetched cards.

## Early access signup

`wrangler.jsonc` sets `main` to `src/worker.js` and runs the Worker first only for `/api/*`; everything else is served as static assets. Configuration:

- Vars in `wrangler.jsonc`: `LISTMONK_URL`, `LISTMONK_LIST_ID`, `LISTMONK_API_USER`, `LISTMONK_WELCOME_TEMPLATE_ID`, `LISTMONK_FROM_EMAIL`, `TURNSTILE_HOSTNAMES`.
- Secrets: `LISTMONK_API_TOKEN`, `TURNSTILE_SECRET` (`wrangler secret put <name>`, or `.dev.vars` locally; copy `.dev.vars.example`).
- Public Turnstile site key: `sitekey` in `dist/early-access.js`.

The signup request includes `noticeVersion: "2026-11-03"`; the Worker rejects missing/obsolete notice versions and records the permission scope and version. This permission covers application review and related trial emails, not unrelated marketing. Previously unsubscribed addresses require assistance instead of automatic resubscription. Supplier error response bodies are not logged.

Subscriber attributes written to Listmonk: `idea`, `app_type`, `stage`, `role`, `company`, `source`, `applied_at`, any `utm_source`, `utm_medium`, `utm_campaign`, `utm_term` and `utm_content` from the page URL, plus `app_type_other` and `role_other` when "Something else" is chosen. Radio values in `dist/early-access.js` must match `CHOICES` in `src/worker.js`.

Local run: `npx wrangler dev` serves the site and the Worker together.

### Thank-you email

New subscribers get a branded email through Listmonk's transactional API. The template lives in Listmonk, not in this repo: Campaigns, Templates, type Transactional, subject "Thanks for requesting early access to Atomic". Its ID is `LISTMONK_WELCOME_TEMPLATE_ID`, and the template loads the Atomic mark as a PNG from the Abstract Machines image CDN, because Gmail blocks SVG images. The API user needs the `tx:send` permission, and `LISTMONK_FROM_EMAIL` must be an address the Listmonk SMTP account may send from. Until the ID is set the Worker skips the email. People who are or were on the list, blocklisted addresses, and failed sends never block or repeat a sign-up.

## Hosting

The site deploys to Cloudflare as a static-assets Worker on every push to `main`, through Cloudflare Workers Builds connected to this repository. `wrangler.jsonc` names the Worker (`atomic-website`) and serves `dist/`. No build step or package installation is required. The site has no external fonts, analytics, or runtime dependencies.

Workers Builds settings (Cloudflare dashboard → Workers & Pages → `atomic-website` → Settings → Build):

- Git repository: `absmach/atomic-website`, production branch `main`
- Build command: empty
- Deploy command: `npx wrangler deploy`
- Root directory: `/`

Custom domains `atomicapp.dev` and `www.atomicapp.dev` are declared in `wrangler.jsonc` routes; deploy creates their DNS records and certificates. The `atomicapp.dev` zone must be in the same Cloudflare account, with no other DNS records on those hostnames.

Manual deploy from the repository root: `npx wrangler deploy`.

Other branches deploy a Preview with `npx wrangler preview`, which reads the `previews` block of `wrangler.jsonc`. Its variables set list `0`, so `/api/early-access` answers 503 in a Preview and never writes to the production Listmonk list.

`.openai/hosting.json` retains the existing Sites identity and also uses `dist` as the public directory.


## Marketing analytics and consent (October 2026)

The shared `dist/site.js` adds a small consent card (bottom-left on desktop, a slim bar on phones, below the builder on the mobile homepage) with one sentence, a Cookie policy link, and equally styled Reject and Accept buttons; the Necessary, Analytics and Marketing categories are under Settings. It also adds a footer Cookie Preferences control and Google Consent Mode v2 default-denied behavior. It injects GTM `GTM-NDHNWJMJ` dynamically only after analytics or marketing is accepted; intentionally no unconditional GTM noscript iframe is installed, because that would bypass consent. Preferences are stored as `atomic-cookie-consent-v2` in localStorage and renewed after six months. Earlier notice versions, invalid dates and future dates require a new choice. Consent controls also support French text when a page declares that language. Withdrawing a previously granted category reloads the page to stop already loaded third-party scripts. The `atomic_early_access_success` dataLayer event fires only after a successful API response and only when analytics consent is granted; it contains no personal details.

In GTM, configure GA4 Measurement ID `G-0516MSWR7R` with analytics consent checks and avoid duplicate pageviews. Add Meta Pixel and LinkedIn Insight Tag only after their IDs are supplied and configure marketing-consent requirements. Test with Tag Assistant and a clean browser session; don't publish tags until consent behavior is verified. Campaign UTM values are already stored with early-access subscriber attributes in Listmonk by the Worker regardless of optional analytics choice.

Legal review is required before launch to finalize processor/provider details, actual tracker/cookie lifetimes and cross-border transfer disclosures. The cookie notice now describes the verified source behavior and identifies the remaining deployment checks. Updating notices is not a certification of external tag configuration.

## Press kit

`content/press.html` leads with the illustrated press book and nine individual documents, supplied as PDF, editable Word and plain text. Product screenshots can be viewed and downloaded directly from the page. Logos, portraits, three launch-film formats and their covers are also available. The Resources footer links to `/press/` on every page.

The current edition is `2026-11-03-v21`, with assets under `dist/assets/press/2026-11-03-v21/`. The book is 23 pages. The complete ZIP and original screenshots/portraits are attached to the public release at `https://github.com/absmach/atomic-website/releases/tag/press-kit-2026-11-03`. Use `atomic-press-kit-2026-11-03-v21.zip` for the current kit; its checksum is supplied alongside it.

`dist/press.css` provides the responsive page layout. Screenshot previews use optimized WebP files with explicit dimensions and lazy loading. Videos use `preload="none"`; the press page uses the approved widescreen launch cover for social sharing.

For a new edition, use a new asset directory and versioned ZIP filename under the existing release tag. Update the document and media links, file sizes and metadata, then regenerate and check the site. Keep the ZIP out of `dist/` and Git history because of the Workers Static Assets per-file limit. Preserve earlier release files so previously shared links remain usable.

Editorial requirement: the first product screenshot in every standalone product document must be the main page (`01-home.png`), including the product overview, announcement, facts sheet and FAQ. Verify the exported PDF and Word images, not only the book cover. The facts sheet uses the main page first and the builder second.

The team documents include the approved business portraits, corrected Filip Bugarski biography and LinkedIn/X links for all three team members. Portrait downloads have edition-specific filenames so earlier release links remain intact.

## Favicons

All pages use the shared Atomic SVG favicon, a multi-size `/favicon.ico`, a 32px PNG fallback and a 180px Apple touch icon. To regenerate raster icons after editing `dist/favicon.svg`, run `python3 scripts/generate-favicons.py` (requires Pillow and `rsvg-convert`), then rebuild the pages.

## November 2 brand refresh

The approved logo uses **Inter SemiBold (600)**, with lowercase `atomic`.
See [Brand identity](docs/brand-identity.txt) for the source SVGs, verification,
and the decision to retain the supplied weight. The previous orbit logo used
Manrope 600; website text typography is separate from the current wordmark.

The shared header and footer use the supplied lowercase atomic SVG lockup, with
its original outlined lettering. Composer and solution icons use the new gradient
symbol. `dist/assets/brand/originals/` retains all 12 supplied source files,
including the lowercase and dark-background alternatives. Monochrome black and white SVG masters are in `dist/assets/brand/monochrome/`; use their separated shapes instead of flattening the coloured symbol. Brand URLs, favicon
queries, shared styles and the social card are versioned to refresh caches.

The v21 press edition uses the lowercase logo in documents, gallery frames and
social covers. Updated screenshots in `dist/assets/screenshots-v16/` preserve
the original UI image and annotations, with the supplied vector logo composited
in its original position. The press ZIP includes SVG screenshot masters and
full-resolution PNG exports. All three launch films use the current lowercase identity throughout, including the opening and closing scenes, template and Canvas recordings, action icon and source screenshot. The closing symbol and wordmark are white on purple, using the corrected monochrome master with four separate shapes and transparent overlap gaps. The source-code scene shows the white logo. The atomicapp.dev address appears only in the opening header, vertically centered with the logo, and in the closing button. All three covers are captured from a fresh timeline with the complete opening headline visible. Original narration, music, captions and timing are preserved. Earlier press assets remain available at their original
URLs. New release attachments use edition-specific filenames, including screenshots.

Import a prepared kit with `PRESS_KIT_DIR=/absolute/path/to/atomic-press-kit-2026-11-03-v21
PRESS_RELEASE_STAGE=/absolute/path/to/release-staging python3 scripts/import-press-kit.py`
(as one command), then run the normal site build and checks. Upload the staged
attachments to the existing `press-kit-2026-11-03` GitHub release before deploying
the page. The ZIP stays outside Git and the static hosting directory.

For social-card rendering, set `PLAYWRIGHT_MODULE` to an installed Playwright
module and `CHROME_BIN` to Chromium if those are not available by default.
`python3 scripts/render-social-card.py` calls the SVG-based browser renderer;
it uses the exact supplied Inter SemiBold logo and the bundled Manrope font for surrounding copy.

## Concise legal and editorial revision

The legal set has two public notices/contracts plus a customer DPA. Edit the ToS clause files and version metadata as described in `content/legal/terms/README.md`; regenerate the French PDF after any legal change. Statutory deadlines remain, while optional fixed retention and service deadlines have been removed. A revision does not amend existing customer agreements automatically.

The press page now serves v22 corrected editorial PDF, DOCX and TXT files and a local documents-only ZIP. Media assets remain from the approved v21 edition; older editions stay at their existing URLs as historical assets. `content/press-documents/` holds the retained print layouts. `scripts/revise_press_documents.py ORIGINAL_V21_KIT` prepares the revised sources and Word/text formats; `scripts/render_press_documents.mjs ORIGINAL_V21_KIT` renders PDFs with the original approved media. Rendering requires Playwright and Chromium; `PLAYWRIGHT_MODULE` and `CHROME_EXECUTABLE` can select existing installations. Run `python3 scripts/package_press_documents.py` after rendering to compress the PDFs with Ghostscript, rebuild the documents ZIP and update its displayed size; it enforces the static-host size budget. Do not reimport v21 over the corrections.
