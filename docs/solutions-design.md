# Solutions: research and design direction

Reviewed 26 October 2026. These pages borrow the competitors' information architecture, not their copy or product promises.

| Reference | Observed approach | Atomic adaptation |
| --- | --- | --- |
| [Replit website builder](https://replit.com/usecases/ai-website-builder) | Accessible outcome-led opening, product demonstration, visual editing benefits, four-step workflow, FAQs. Navigation separates roles from use cases. | Lead with what the visitor wants to make. Show a recognisable app, then explain describing, editing, testing and publishing. |
| [Lovable websites](https://lovable.dev/use-cases/websites) | Large editor imagery; benefits grouped around design, backend, and discovery; specific website types. | Use generous app illustrations, separate visual refinement from app functionality, and give concrete starting ideas. |
| [Bolt website builder](https://bolt.new/use-cases/ai-website-builder) | Prompt-led conversion, short capability cards, three-step process, reusable example prompts, FAQs and a closing CTA. | Make starter briefs useful links into Atomic's existing early-access wizard; keep the conversion honest about availability. |

Also reviewed each homepage: [Replit](https://replit.com/), [Lovable](https://lovable.dev/home), [Bolt](https://bolt.new/). Their broad idea-to-product narrative supports a hub organised around outcomes rather than technical features.

## Page family

- `/solutions/`: overview, app collage, six use cases, audience filters, shared product benefits, closing idea form.
- `/solutions/websites/`: business sites, portfolios and landing pages.
- `/solutions/online-stores/`: catalogues, carts and order workflows.
- `/solutions/booking-apps/`: services, availability and booking management.
- `/solutions/client-portals/`: client-specific project updates and requests.
- `/solutions/internal-tools/`: CRMs, help desks and team workflows.
- `/solutions/prototypes/`: testable screens, roles and feedback before launch.

Each detail page uses one reusable layout: breadcrumb → outcome and CTA → distinct app illustration → three specific benefits → example prompts → describe/refine/publish workflow → contextual FAQs → related solutions → early access.

## Visual direction

Retain Atomic's local Manrope font, warm paper, violet, dark plum, buttons, header and footer. Add spacious editorial headings, softly tinted app stages, compact browser frames, real photographic content, and small product-specific UI details. Use responsive HTML/CSS illustrations rather than baked-in UI text or modified product screenshots. The supplied `atomic-marketing/00-canvas-workspace-hero.png` informs the service-card organisation; the product docs inform canvas, role preview and publishing language. Label all mock apps as illustrative sample data. Decorative mock UI has no inert buttons or links.

## Copy and claim boundaries

Source of truth: repository documentation, particularly templates, canvas/editing, screens and roles, source exports, publishing and launch pricing. Emphasise plain-language briefs, editable screens, previewing roles, real app data on paid plans, verified builds, source downloads and publishing. Avoid guaranteed build times, conversion/revenue claims, invented customers, endorsements, payment integrations, SEO guarantees, or enterprise certifications. Storefront checkout is an order workflow; live payment processing needs a separately configured and tested provider. Plan qualifications belong beside relevant features and in FAQs. Early access remains a request, not immediate signup or app generation.

## Delivery and validation

Build in the isolated `feat/solutions-pages` worktree. Commit research, implementation, then validation/polish. Run the existing generator and site checker, JavaScript syntax checks, Worker regression tests and desktop/mobile browser checks. Check prompt handoff, filters, FAQ keyboard access, navigation, page metadata, image loading and overflow. Push the branch and open a PR; do not deploy.

### Validation results

- Generator: 51 pages. Site checker: 28 guides and six solution routes; links, fragments, assets, image dimensions, headings, catalogue cards and canonical URLs pass.
- Chrome: all seven solutions pages checked at 1440, 1024, 768, 390 and 320 px. Images loaded, one H1 per page, no horizontal overflow.
- Interaction checks: all audience filters and the live status; mobile menu open/Escape/focus return; native FAQ keyboard activation; starter briefs and native idea forms prefill the homepage hero with literal special characters; submitting the hero composer opens step 2 of early access. Generic early-access links land on the hero without opening a dialog and preserve campaign parameters. No JavaScript exceptions.
- Visual review: hub, detail heroes, solution cards, starter prompts, FAQs, closing form and mobile app illustrations. Adjusted photography crop and card composition so real imagery is visible.
- JavaScript syntax checks and existing Worker tests pass. No form was submitted to the live signup endpoint, and no deployment was performed.

### Early-access CTA policy (27 October 2026)

The hub and individual solution heroes use **Request Early Access** until launch. The hub’s secondary CTA, **Find your starting point**, links to its solution catalogue. All `#early-access` links target the homepage hero, not the closing “What’s yours?” section, and do not open a dialog by themselves. Starter briefs prefill the hero composer; the visitor reviews and submits the idea to open the existing wizard. Both homepage idea forms still open the wizard on submit.

After early access ends, update the primary CTA label and destination together. Preserve the original per-solution `cta` values in `content/solutions.json` until then; comments in `scripts/solutions.py` and `dist/early-access.js` explain the temporary flow.

Follow-up Chrome checks at 390 and 1440 px pass: primary/secondary CTA order and labels, all six detail-page CTA destinations, no horizontal overflow, hero navigation without automatic dialogs, exact starter-brief preservation and URL cleanup, both homepage form submissions, literal special characters, campaign parameters, and native hero anchors with JavaScript disabled. No browser exceptions or live signup submissions.
