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
