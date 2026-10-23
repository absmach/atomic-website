# Atomic product website

A responsive, dependency-free, multi-page product site built from the Atomic app and launch plans. Atomic leads the brand; Abstract Machines is identified as the company behind the product. The project lives at the repository root; static hosting serves `dist/`.

## Generate and check

Run `python3 scripts/build_site.py` after changing content or shared markup. Run `python3 scripts/check_site.py` to validate every local page link, fragment, asset, heading, title, ID, and image alt attribute. Check JavaScript syntax with `node --check dist/site.js`, `node --check dist/app.js`, and `node --check dist/early-access.js`. Run the Worker tests with `node --test src/worker.test.js`.

`content/home.html` contains the original homepage presentation. `scripts/build_site.py` owns the shared navigation and footer, homepage additions, pricing copy, articles, and legal drafts.

Each documentation guide's body is `content/docs/<section>/<slug>.html`: a run of `<section id="…"><h2>…</h2>…</section>` blocks, from which the page's contents list is read. `DOCS` in `scripts/build_site.py` lists the sections and, in order, each guide's slug, title, card summary, introduction and reading time. The docs index, the docs menu on every guide and the previous/next links follow that order. A guide is served at `/docs/<slug>/` whichever section holds it, so moving it between sections keeps its address. To add a guide, write its content file and add it to `DOCS`. Reading times are computed from each guide's words.

Documentation screenshots in `dist/assets/docs/` are 1440 px wide captures of a local Atomic Builder (cropped to one section where a guide is about that section), using an app created from the Salon Booking template so no model was called. Retake them when the screens they show change. Every `<img>` needs `width` and `height` that match the file; `check_site.py` compares them. `check_site.py` fails when a content file and its generated page do not match one to one, or when a guide is missing from the index or a menu. Generated HTML is committed in `dist/`, so hosting still requires no build or installation. Edit those sources rather than generated HTML. Shared styles and JavaScript in `dist/` are maintained directly.

## Site map

- `/`: product introduction, interactive examples, workspace views, and early-access inquiry.
- `/pricing/`: proposed Free, $25/month Builder (2,500 credits), and $50/month Pro (5,000 credits) plans in USD. Free includes 250 credits once at signup, with no recurring allowance. Paid-plan top-ups are $10 for 1,000 credits. One credit is $0.01 of Atomic usage; charges can be fractional, monthly credits reset, and purchased credits do not expire. The feature comparison retains 1 / 3 / 10 published apps and proposes 0 / 5 / 10 invited collaborators per app, excluding the owner. Free is a solo, frontend-only plan with no backend, database, user authentication, or collaboration; Builder and Pro include those features. Cards group concrete building, publishing, and collaboration tools below a price/CTA panel and credit/app capacity strip, inspired by Lovable’s feature hierarchy. The comparison also covers canvas/theme controls, annotations, design references, app access, frontend rollback, preview logs, source downloads, and usage history. No SSO, SCIM, priority support, or other unqualified enterprise feature is promised. No checkout is open.
- `/docs/`: searchable product documentation, 28 guides in seven sections (Get started, Build, Canvas, Data and users, Publish and run, Versions and source, Usage and help), each guide with the docs menu, an on-page contents list and previous/next links. Guides describe the product as it works in the Atomic repository's `main`; plan amounts are left to `/pricing/`. These explain the early-access workflow, not unverified account or interface procedures.
- `/blog/`: two existing product-perspective articles; launch and later posts can be added separately.
- `/about/`: Atomic’s purpose and the team at Abstract Machines, with links to the company, Atom, and its public open-source work.
- `/security/`: verified product boundaries and the existing team contact for reporting concerns; no invented certifications or SLA.
- `/legal/`: Privacy Policy (final, covering the website and early-access sign-up), draft Terms of Service, Acceptable Use Policy, DPA, Subprocessor List, and Cookies & Storage Notice. Each draft is clearly marked not effective and excluded from indexing; the Privacy Policy is indexable.
- `dist/404.html`: branded fallback for hosts supporting a static 404 page.

The header shows Product, Docs, Blog, Pricing, and About, followed by Get early access. Resources is a footer grouping for Documentation, Blog, Security & trust, About Atomic, and Contact; there is no separate Resources page.

Every page includes shared responsive navigation, a skip link, and an Atomic-led footer. The footer links to Atomic's X and Instagram profiles and Abstract Machines' GitHub and LinkedIn profiles. Nested pages use root-relative links and work on a host serving `dist/` at its root.

## Before public launch

The website structure and content are prepared; operational and commercial facts still need confirmation. The legal pages are substantive drafting material, not effective agreements or a completed compliance program.

- Confirm the full contracting/controller entity, registered address, company identifiers, applicable jurisdictions, and legal contacts. Abstract Machines is a brand reference until those details are verified.
- Implement and validate the proposed Free, Builder, and Pro catalog and credit rules before opening subscriptions, including Free’s frontend-only publishing and backend/collaboration restrictions. Confirm Free grant expiry, collaboration, storage, bandwidth, and concurrency limits; qualify hosting rates and protected budgets; finalize retry treatment, taxes, cancellation, refunds, and retention rules.
- Finalize and review the legal drafts with counsel, including consumer rights and limitations of liability. Complete the DPA processing description, verified security measures, transfer clauses, and acceptance mechanism.
- Inventory actual vendors, their roles, processing/access locations, retention, and AI training settings. Publish an approved subprocessor register and change-notification process.
- Verify inquiry, account, prompt, log, billing, and backup retention/deletion rules and the customer data export process.
- Audit cookies, storage, and logging on the actual deployed host, including its access gate. The application itself sets no cookies or persistent browser storage; hosting behavior has not been certified. Add consent controls if the actual technologies require them.
- Replace the early-access waitlist with the approved onboarding/payment flow when available, add final effective policies and acceptance records, and add any remaining social channels when their official URLs are confirmed.
- The production domain is `atomicapp.dev`, with homepage canonical and social metadata configured. Complete canonical metadata for the remaining pages, submit a domain-specific sitemap, and review indexing before launch. Draft legal pages remain `noindex, nofollow` until finalized.

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

The composer cycles through example ideas only while empty and unfocused. It preserves typed text, includes a pause control, and respects reduced-motion preferences. Keyboard focus is shown on the outer composer rather than the inner textarea. App thumbnails use colored compositions; the workspace uses a layered frame, and the Atom diagram is responsive HTML/SVG.

Pricing shows the agreed launch proposal with credit quantities and top-up rules. The launch date, operational limits, and protected hosting controls remain to be confirmed. The internal 3× direct-cost multiplier is a commercial modeling assumption, not public pricing copy or a backend change in this repository. Complete app packaging and deployment choice remain roadmap items. Source export does not include users, business data, or hosting; frontend rollback does not restore business data. Do not represent the interactive examples or supplied product images as live customer results.

Product images and the Atomic mark come from `~/ideas/vc/atomic/pitch-deck`. Images are illustrative sample-app views and are labeled on the page. The three `*-preview.png` thumbnails are browser captures of this page’s interactive examples. Typography consistently uses the locally hosted, preloaded Manrope variable font. Font licenses are included under `dist/assets/fonts/`.

## Social preview

The page includes Open Graph and X large-image card metadata pointing to
`https://atomicapp.dev/assets/atomic-social-v2.png`. The 1200 × 630 PNG uses the
existing Atomic mark, palette, and bundled Manrope font. Regenerate it with
`python3 scripts/render-social-card.py` (requires Pillow with FreeType/WOFF2
support for authoring; the website still has no runtime dependencies).

Deploy `dist/index.html` and the image together to the public domain. Verify
that the image URL returns an actual PNG without authentication. When changing
the artwork, use a new versioned filename and update both image meta tags to
avoid stale image caches. Social platforms may retain previously fetched cards.

## Early access signup

`wrangler.jsonc` sets `main` to `src/worker.js` and runs the Worker first only for `/api/*`; everything else is served as static assets. Configuration:

- Vars in `wrangler.jsonc`: `LISTMONK_URL`, `LISTMONK_LIST_ID`, `LISTMONK_API_USER`, `LISTMONK_WELCOME_TEMPLATE_ID`, `LISTMONK_FROM_EMAIL`, `TURNSTILE_HOSTNAMES`.
- Secrets: `LISTMONK_API_TOKEN`, `TURNSTILE_SECRET` (`wrangler secret put <name>`, or `.dev.vars` locally; copy `.dev.vars.example`).
- Public Turnstile site key: `TURNSTILE_SITEKEY` in `scripts/build_site.py`, then rebuild.

Subscriber attributes written to Listmonk: `idea`, `app_type`, `stage`, `role`, `company`, `source`, `applied_at`, any `utm_source`, `utm_medium`, `utm_campaign`, `utm_term` and `utm_content` from the page URL, plus `app_type_other` and `role_other` when "Something else" is chosen. Radio values in `content/home.html` must match `CHOICES` in `src/worker.js`.

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
