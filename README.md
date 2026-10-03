# Atomic launch website

A responsive, dependency-free marketing site based on the Atomic application and October 2026 launch deck. The site is in `dist/`; it can be served by any static host.

## Preview

From this directory run `python3 -m http.server 4173 --directory dist`, then open http://localhost:4173.

## Content and launch configuration

- Edit `dist/index.html` for copy and the primary early-access destination (`#access-link`). The default destination is the existing Abstract Machines website; there is no signup service or email collection attached.
- Edit `dist/styles.css` for the visual design, and `dist/app.js` for product-view and use-case switches.
- Final pricing and launch date are intentionally not published. Planned app packaging and deployment choice are identified as roadmap items in the FAQ.
- Product images are the illustrative sample-app assets from `~/ideas/vc/atomic/pitch-deck`, not customer screenshots. They are labeled on the site.
- Local fonts and their licenses are included in `dist/assets/fonts/`. The Atomic mark comes from the same pitch deck.

There are no tracking scripts, external font requests, forms, or runtime dependencies. `.openai/hosting.json`, when present, contains the Sites publishing identity.
