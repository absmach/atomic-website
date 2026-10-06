# Atomic launch website

A responsive, dependency-free marketing site built from the Atomic app and launch plans. The project lives at the repository root; static hosting serves `dist/`.

## Preview

Run `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist`, then open http://localhost:4173.

## Page and interactions

- `dist/index.html`: page copy, examples, metadata, and native email-draft dialog.
- `dist/styles.css`: shared visual system and responsive layouts.
- `dist/launch.css`: centered prompt opening, app preview cards, and framed product showcase.
- `dist/app.js`: mobile navigation, product image switch, booking/shop/portal demos, and early-access email preparation.
- `dist/assets/`: local brand mark, product images, fonts, and font licenses.

The booking example supports requesting a session, reviewing it as the studio owner, confirming, updating, and resetting. The shop supports adding sample items and clearing the bag. The portal switches project milestones. All example state is in memory and resets on reload; nothing is booked, purchased, or sent to a server.

The page opens with an idea composer. Suggested prompts fill the input, and the app preview cards open their matching interactive demos. Both the opening composer and closing early-access form validate an idea and open a review dialog. Ctrl+Enter or Command+Enter also submits the idea. The visitor can open a prefilled email addressed to `info@absmach.eu`, or copy the draft. This prepares an early-access inquiry; it does not generate an app, collect a signup, or send email automatically. The address was verified on https://www.absmach.eu/. Replace this workflow with the production signup URL or an approved signup service when available.

## Content boundaries

The composer cycles through example ideas only while empty and unfocused. It preserves typed text, includes a pause control, and respects reduced-motion preferences. Keyboard focus is shown on the outer composer rather than the inner textarea. App thumbnails use colored compositions; the workspace uses a layered frame, and the Atom diagram is responsive HTML/SVG.

Final pricing and launch date remain unannounced. Complete app packaging and deployment choice remain roadmap items. Source export does not include users, business data, or hosting; frontend rollback does not restore business data. Do not represent the interactive examples or supplied product images as live customer results.

Product images and the Atomic mark come from `~/ideas/vc/atomic/pitch-deck`. Images are illustrative sample-app views and are labeled on the page. The three `*-preview.png` thumbnails are browser captures of this page’s interactive examples. Typography consistently uses the locally hosted, preloaded Manrope variable font. Font licenses are included under `dist/assets/fonts/`.

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
