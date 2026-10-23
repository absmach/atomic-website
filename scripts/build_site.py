#!/usr/bin/env python3
"""Generate portable static pages. Run from any directory with Python 3."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
CONTACT = 'mailto:info@absmach.eu'
# Public Cloudflare Turnstile site key for the early-access form (not a secret).
TURNSTILE_SITEKEY = '0x4AAAAAAFfPJS0NJjFeyiuj'
NAV = [('Product', '/'), ('Docs', '/docs/'), ('Blog', '/blog/'), ('Pricing', '/pricing/'), ('About', '/about/')]

def link(label, url, active=''):
    current = ' aria-current="page"' if url == active else ''
    return f'<a href="{url}"{current}>{label}</a>'

def header(active):
    links = ''.join(link(label, url, active) for label, url in NAV)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-row"><a class="brand" href="/" aria-label="Atomic home"><img src="/assets/atomic.svg" width="33" height="33" alt="" />atomic</a><nav class="desktop-nav" aria-label="Main navigation">{links}</nav><div class="header-actions"><a class="button button-small" href="/#early-access">Get early access</a><button class="menu-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open navigation"><span></span><span></span></button></div></div><nav id="mobile-nav" class="mobile-nav" aria-label="Mobile navigation" hidden>{links}<a href="/#early-access">Get early access</a></nav></header>'''

def social_links():
    icons = {
        'GitHub': '<path d="M12 .8a11.2 11.2 0 0 0-3.54 21.83c.56.1.77-.24.77-.54v-2.1c-3.12.68-3.78-1.33-3.78-1.33-.51-1.3-1.24-1.65-1.24-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.73 1.16 1.73 1.16 1 1.72 2.62 1.22 3.26.93.1-.73.39-1.22.71-1.5-2.49-.29-5.11-1.25-5.11-5.54 0-1.23.44-2.23 1.15-3.02-.12-.28-.5-1.43.11-2.98 0 0 .94-.3 3.08 1.15a10.76 10.76 0 0 1 5.6 0c2.14-1.45 3.08-1.15 3.08-1.15.61 1.55.23 2.7.11 2.98.71.79 1.15 1.79 1.15 3.02 0 4.3-2.62 5.25-5.12 5.53.4.35.76 1.03.76 2.08v3.11c0 .3.21.65.77.54A11.2 11.2 0 0 0 12 .8Z"/>',
        'LinkedIn': '<path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2ZM8 19H5V9h3ZM6.5 7.7a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4ZM19 19h-3v-5.2c0-1.2-.1-2.7-1.7-2.7s-2 1.3-2 2.6V19h-3V9h2.9v1.4h.1c.4-.8 1.4-1.7 2.9-1.7 3.1 0 3.8 2 3.8 4.5Z"/>',
        'X': '<path d="M18.9 2H22l-6.8 7.8L23.2 22h-6.3L12 14.6 5.5 22H2.3l8.2-9.4L.8 2h6.5l5.9 7.9L18.9 2ZM17.8 20h1.8L6.3 3.9H4.4L17.8 20Z"/>',
        'Instagram': '<path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7Zm5 3a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.5-2.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Z"/>'
    }
    profiles = [
        ('X', 'Atomic', 'https://x.com/atomicappdev'),
        ('Instagram', 'Atomic', 'https://www.instagram.com/atomicapp.dev/'),
        ('GitHub', 'Abstract Machines', 'https://github.com/absmach'),
        ('LinkedIn', 'Abstract Machines', 'https://www.linkedin.com/company/abstract-machines/'),
    ]
    return ''.join(f'<a class="social-placeholder social-link" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{brand} on {name}"><span class="social-icon"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false">{icons[name]}</svg></span></a>' for name,brand,url in profiles)

def footer():
    columns = [
        ('Product', [('Explore examples', '/#examples'), ('How it works', '/#how-it-works'), ('Why Atomic', '/#foundation'), ('Pricing', '/pricing/'), ('Early access', '/#early-access')]),
        ('Resources', [('Documentation', '/docs/'), ('Blog', '/blog/'), ('Security & trust', '/security/'), ('About Atomic', '/about/'), ('Contact the team', CONTACT)]),
        ('Legal', [('Legal overview', '/legal/'), ('Privacy', '/legal/privacy/'), ('Terms of Service', '/legal/terms/'), ('Acceptable Use', '/legal/acceptable-use/'), ('Data Processing', '/legal/dpa/'), ('Subprocessors', '/legal/subprocessors/'), ('Cookies & storage', '/legal/cookies/')])
    ]
    menus = ''.join(f'<nav class="footer-column" aria-label="{title}"><h2>{title}</h2>{"".join(link(label,url) for label,url in items)}</nav>' for title, items in columns)
    return f'''<footer class="site-footer"><div class="container"><div class="footer-grid"><div class="footer-brand"><a class="brand" href="/" aria-label="Atomic home"><img src="/assets/atomic.svg" width="29" height="29" alt="" />atomic</a><p>Small idea. Real possibilities.<br />Build what comes next.</p><div class="social-placeholders" role="group" aria-label="Atomic and Abstract Machines social channels">{social_links()}</div><p class="social-note">Follow Atomic and Abstract Machines</p></div>{menus}</div><div class="footer-bottom"><span>© <span id="year">2026</span> Atomic. A product by <a href="https://absmach.eu" target="_blank" rel="noopener noreferrer">Abstract Machines</a>.</span><span>Describe it. Shape it. Make it real.</span></div></div></footer>'''

def page(path, title, description, body, active='', draft=False):
    folder = DIST / path
    folder.mkdir(parents=True, exist_ok=True)
    robots = '<meta name="robots" content="noindex, nofollow" />' if draft else ''
    html = f'''<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><meta name="theme-color" content="#191329" /><title>{escape(title)} — Atomic</title><meta name="description" content="{escape(description, quote=True)}" /><meta property="og:title" content="{escape(title, quote=True)} — Atomic" /><meta property="og:description" content="{escape(description, quote=True)}" /><meta property="og:type" content="website" />{robots}<link rel="icon" type="image/svg+xml" href="/assets/atomic.svg" /><link rel="preload" href="/assets/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin /><link rel="stylesheet" href="/styles.css" /><link rel="stylesheet" href="/pages.css" /><script src="/site.js" defer></script></head><body>{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''
    (folder / 'index.html').write_text(html)

def hero(kicker, title, intro, center=False, extra=''):
    return f'<section class="page-hero{" center" if center else ""}"><div class="container"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{intro}</p>{extra}</div></section>'

def cta():
    return '<section class="mini-cta"><div class="container"><div><h2>Your next idea starts here.</h2><p>Tell us what you want to build with Atomic.</p></div><a class="button button-primary" href="/#early-access">Get early access <span aria-hidden="true">↗</span></a></div></section>'

def card(kicker, title, text, url, action='Read the guide', guide=False, level=2):
    return f'<a class="resource-card" href="{url}"{" data-guide" if guide else ""}><p class="eyebrow">{kicker}</p><h{level}>{title}</h{level}><p>{text}</p><span class="card-link">{action} <span aria-hidden="true">↗</span></span></a>'

def notice(title, text):
    return f'<div class="notice"><strong>{title}</strong>{text}</div>'

def article(path, title, intro, sections, category='Documentation', active='/docs/', note='', meta='', related='', draft=None):
    home = '/legal/' if category == 'Legal' else '/blog/' if category == 'Field notes' else '/docs/'
    crumb = f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="{home}">{category}</a><span aria-hidden="true">/</span><span aria-current="page">{title}</span></nav>'
    heading = f'<section class="page-hero"><div class="container">{crumb}<p class="eyebrow">{category}</p><h1>{title}</h1><p class="lead">{intro}</p><p class="article-meta">{meta}</p></div></section>'
    toc = '<nav class="contents" aria-label="On this page"><strong>On this page</strong>' + ''.join(f'<a href="#{sid}">{name}</a>' for sid,name,_ in sections) + '</nav>'
    content = ''.join(f'<section id="{sid}"><h2>{name}</h2>{text}</section>' for sid,name,text in sections)
    page(path,title,intro,heading+f'<div class="container reading-layout">{toc}<article class="prose">{note}{content}{related}</article></div>',active,draft=(category=='Legal') if draft is None else draft)

# Homepage retains its original, interactive product presentation.
home = (ROOT / 'content/home.html').read_text()
home = re.sub(r'  <a class="skip-link".*?</header>', header('/'), home, count=1, flags=re.S)
home = re.sub(r'<footer class="site-footer">.*?</footer>', footer(), home, count=1, flags=re.S)
home = home.replace('<script src="app.js" defer></script>', '<link rel="stylesheet" href="/pages.css" />\n  <script src="/site.js" defer></script>\n  <script src="/app.js" defer></script>')
home = home.replace('<script src="early-access.js" defer></script>', '<script src="/early-access.js" defer></script>').replace('__TURNSTILE_SITEKEY__', TURNSTILE_SITEKEY)
home = home.replace('We’ll share availability and final plan details as launch approaches.', 'Explore our <a class="text-action" href="/pricing/">proposed launch plans</a>, with Free, Builder, and Pro. Subscriptions are not open yet.')
home = home.replace('<section class="faq-section', '<section class="home-pricing"><div class="container"><div><p class="eyebrow">ROOM FOR YOUR NEXT IDEA</p><h2>Start small. Build from there.</h2><p>Start with Free, build with Builder at $25/month, or grow with Pro at $50/month.</p></div><a href="/pricing/" class="button button-secondary">Explore launch plans <span aria-hidden="true">↗</span></a></div></section>\n<section class="faq-section')
home = home.replace('Early access opens soon. Share your idea to join the waitlist.</p>', 'Early access opens soon. Share your idea to join the waitlist. <a href="/legal/privacy/">Privacy policy</a>.</p>')
(DIST / 'index.html').write_text(home)

# Pricing: agreed launch proposal; subscriptions remain closed.
plans = [
    {
        'name': 'Free', 'price': '$0', 'badge': 'Explore the idea', 'featured': False,
        'description': 'Design your first frontend. Build on your own, see it working, and keep the source.',
        'credits': '250', 'credit_label': 'credits at signup', 'apps': '1', 'app_label': 'published frontend app',
        'groups': [
            ('Create and refine', ['AI frontend generation and revisions', 'Visual canvas and in-place text editing', 'Theme, typography, and layout controls', 'Screen previews and visual annotations', 'Image and design-reference uploads']),
            ('Keep and share your work', ['Private projects', 'Browse and download generated source', 'Version history and source restore', 'Publish on an Atomic subdomain'])
        ],
        'boundary': 'Frontend only · Solo building. Backend, database, authentication, and collaboration start with Builder.'
    },
    {
        'name': 'Builder', 'price': '$25', 'badge': 'Start building', 'featured': True,
        'description': 'Turn your idea into a working app, with accounts, real data, and people building beside you.',
        'credits': '2,500', 'credit_label': 'credits each month', 'apps': '3', 'app_label': 'published apps',
        'groups': [
            ('Everything in Free, plus', ['App backend and persistent database', 'User sign-in and app access controls', 'Connect your own custom domain', 'Deployment history and frontend rollback', 'Build checks and searchable preview logs']),
            ('Build together', ['Shared team workspaces', '5 invited collaborators per app', 'Editor and Admin collaborator roles', 'Per-app build and credit usage history', 'On-demand credit top-ups'])
        ],
        'boundary': 'Building and metered hosting use your credits. Top-ups: $10 for 1,000 credits, with no expiry.'
    },
    {
        'name': 'Pro', 'price': '$50', 'badge': 'Keep growing', 'featured': False,
        'description': 'Keep several apps moving with a bigger team and more room to build, refine, and publish.',
        'credits': '5,000', 'credit_label': 'credits each month', 'apps': '10', 'app_label': 'published apps',
        'groups': [
            ('Everything in Builder, plus', ['Backend, database, and user authentication', 'Custom domains for your published apps', 'Version restore and frontend rollback', 'Build checks and searchable preview logs', 'Source downloads for every app']),
            ('More room for your team', ['10 invited collaborators per app', 'Shared workspaces with Editor and Admin roles', '2× Builder’s monthly credit allowance', 'Per-app build and credit usage history', 'On-demand credit top-ups'])
        ],
        'boundary': 'All Builder tools, with more credits, apps, and collaborators. Top-ups keep the same rate on both paid plans.'
    }
]
pricecards = ''
for plan in plans:
    name = plan['name']
    groups = ''.join('<section class="plan-feature-group"><h3>'+escape(title)+'</h3><ul class="plan-features">'+''.join('<li>'+escape(feature)+'</li>' for feature in features)+'</ul></section>' for title,features in plan['groups'])
    pricecards += f'''<article class="price-card{' featured' if plan['featured'] else ''}" aria-labelledby="plan-{name.lower()}">
<div class="plan-overview"><span class="pill">{plan['badge']}</span><h2 id="plan-{name.lower()}">{name}</h2><p class="plan-description">{plan['description']}</p><p class="price">{plan['price']}<small> / month</small></p><a class="button {'button-primary' if plan['featured'] else 'button-secondary'}" href="{CONTACT}?subject=Atomic%20{name}%20early%20access">Ask about early access</a></div>
<dl class="plan-allowances"><div><dt>{plan['credit_label']}</dt><dd>{plan['credits']}</dd></div><div><dt>{plan['app_label']}</dt><dd>{plan['apps']}</dd></div></dl>
<div class="plan-details">{groups}<p class="plan-boundary">{plan['boundary']}</p></div></article>'''
pricing = hero('PLANS FOR WHAT COMES NEXT','A little idea.<br /><em>Room to grow.</em>','Start for free. Choose more room to build and run your apps when you need it.',True,'<span class="pill">Launch preview · Subscriptions are not open yet</span>')
pricing += f'<section class="page-section"><div class="container"><div class="price-grid">{pricecards}</div><p class="pricing-footnote">Proposed launch plans in USD, billed monthly. Applicable taxes are extra and will be shown before purchase. Free allowances and collaboration limits are subject to launch validation. Storage, bandwidth, and concurrency limits will be published before subscriptions open. No payment is collected here.</p><div class="enterprise-strip"><div><h3>Something bigger in mind?</h3><p>Tell us about your organization, deployment needs, and support requirements.</p></div><a class="text-action" href="{CONTACT}?subject=Atomic%20organization%20inquiry">Talk to the Atomic team ↗</a></div></div></section>'
comparison_rows = [
    ('Best for', 'Explore a frontend idea on your own', 'Launch and refine your apps', 'Build several apps with a team'),
    ('Published apps at once', '1 frontend app within the trial allowance', '3', '10'),
    ('Invited collaborators per app', 'Not included', '5', '10'),
    ('Editor and Admin collaborator roles', 'Not included', 'Included', 'Included'),
    ('Shared workspaces and team collaboration', 'Not included', 'Included', 'Included'),
    ('Custom domains', 'Atomic subdomain only', 'Connect your own domain', 'Connect your own domains'),
    ('AI generation and revisions', 'Frontend only', 'Full app', 'Full app'),
    ('Visual canvas, text edits, and theme controls', 'Included', 'Included', 'Included'),
    ('Screen previews and visual annotations', 'Included', 'Included', 'Included'),
    ('Image and design-reference uploads', 'Included', 'Included', 'Included'),
    ('App backend, database, and user authentication', 'Not included', 'Included', 'Included'),
    ('App-user access controls', 'Not included', 'Included', 'Included'),
    ('Deployment history and frontend rollback', 'Not included in the Free proposal', 'Included', 'Included'),
    ('Searchable preview logs', 'Not included in the Free proposal', 'Included', 'Included'),
    ('Private projects and source downloads', 'Included', 'Included', 'Included'),
    ('Version history and source restore', 'Included', 'Included', 'Included'),
    ('Per-app build and usage history', 'Included', 'Included', 'Included'),
    ('Hosting and persistent storage', 'Frontend hosting uses trial credits; no backend storage', 'Uses available credits', 'Uses available credits'),
    ('Buy additional credits', 'Upgrade to a paid plan', '$10 for 1,000 credits', '$10 for 1,000 credits')
]
comparison = ''.join('<tr><th scope="row">'+label+'</th>'+''.join('<td>'+value+'</td>' for value in values)+'</tr>' for label,*values in comparison_rows)
pricing += '<section class="page-section"><div class="container"><div class="section-intro"><p class="eyebrow">WHAT YOUR PLAN MAKES POSSIBLE</p><h2>Start with the frontend. Grow into a full app.</h2><p>Free gives you visual editing, version history, and source downloads to explore a frontend idea on your own. Builder adds a backend, database, user authentication, team collaboration, custom domains, and room for several live apps. Pro gives a larger team more credits and publishing capacity.</p></div><div class="table-wrap pricing-comparison" role="region" aria-label="Compare launch plan features" tabindex="0"><table><caption>Proposed launch features. On small screens, scroll horizontally to compare plans.</caption><thead><tr><th scope="col">What you get</th><th scope="col">Free · $0/month</th><th scope="col">Builder · $25/month</th><th scope="col">Pro · $50/month</th></tr></thead><tbody>'+comparison+'</tbody></table></div><p class="pricing-footnote">Collaborator limits are proposed and count people invited to an app, excluding its owner. They are not limits on the people using your finished app. Shared workspaces and collaboration require a paid plan; workspace membership is separate from the per-app collaborator limit. Building by collaborators uses the app owner’s credits. A source download includes code, not app users or business data; version restore changes code, not data. Custom-domain registration is purchased separately.</p></div></section>'
pricing += '<section class="page-section"><div class="container"><div class="section-intro"><h2>One credit value. Every plan.</h2><p><strong>100 credits = $1 of Atomic usage.</strong> Credits pay for building and running your apps at Atomic’s usage rates. The same work uses the same credits on every plan; charges can be fractional, based on the resources used. For example, 15 credits means $0.15 of Atomic usage. A credit is not a message or a completed app.</p></div><div class="resource-grid">'+card('01 / BUILD','Shape your app.','AI generation, revisions, suggestions, dictation, and the build environment draw from your credits. A small change can use less than a complex build.','/docs/usage-and-credits/','Understand your usage')+card('02 / RUN','Give it a home.','Metered app hosting and persistent storage use credits too. Published-app slots are capacity limits, not unlimited hosting. A protected hosting budget is planned so building cannot spend the credits you set aside to run your apps.','/docs/publishing/','Prepare to publish')+card('03 / TOP UP','More room when you need it.','On Builder and Pro, add 1,000 credits for $10. Purchased credits do not expire and are used after your monthly allowance. No automatic overage charges.','/pricing/#credit-rules','Read the credit rules')+'</div></div></section>'
pricing += '<section id="credit-rules" class="page-section"><div class="container faq-layout"><div><p class="eyebrow">A FEW PRACTICAL DETAILS</p><h2>Before you choose.</h2></div><div class="faq-list">'
for q,a in [
    ('Can I subscribe today?','Not yet. These are proposed launch plans. The early-access form adds you to the waitlist; it does not create an account, reserve a price, or start a subscription.'),
    ('What is included in the subscription?','Builder includes 2,500 monthly credits and up to 3 published apps for $25/month. Pro includes 5,000 monthly credits and up to 10 published apps for $50/month. Both include a backend, database, user authentication, team collaboration, custom domains, private projects, and source downloads. Builder proposes 5 invited collaborators per app; Pro proposes 10. Collaborators can work together with Editor and Admin roles, using the app owner’s credits. Your subscription pays for the platform as well as the included usage.'),
    ('How does Free work?','The proposed Free plan includes 250 credits once at signup, with no monthly refill. Build on your own and publish one frontend-only app on an Atomic subdomain within your available trial allowance. Free does not include a backend, database, user authentication, or collaboration. Those features, custom domains, and credit purchases require Builder or Pro. When the signup credits are used, upgrade to Builder or Pro to continue building.'),
    ('Do unused credits expire?','Monthly subscription credits reset at renewal and do not roll over. Purchased top-up credits do not expire. Monthly credits are used before purchased credits. Free receives only its one-time signup grant, with no monthly refill; its expiry terms will be confirmed before launch.'),
    ('Is hosting included?','Your included credits can pay for metered hosting and persistent storage. Hosting is not unlimited, and storage can still cost credits when an app is stopped. We plan to let you protect part of your balance for hosting. Storage, bandwidth, concurrency limits, and hosting exhaustion and retention rules will be published before billing opens.'),
    ('What happens when my credits run out?','There are no automatic overage charges. New builds require enough available credits. Free users can upgrade when their signup credits run out. On Builder and Pro, you can buy 1,000 more credits for $10 or wait for your monthly allowance to renew. Running apps also need available hosting funds. The planned hosting-budget control will let you set aside credits that building cannot spend.'),
    ('Will there be annual billing?','The launch proposal is monthly billing only. Annual plans and discounts have not been announced.'),
    ('What happens if I cancel?','Cancellation, data retention, export access, and the behavior of published apps will be specified in the final subscription terms before checkout becomes available.')]:
    pricing += f'<details><summary>{q}</summary><p>{a}</p></details>'
pricing += '</div></div></section>'+cta()
page('pricing','Pricing','Explore Atomic’s launch plans: Free, Builder at $25/month with 2,500 credits, and Pro at $50/month with 5,000 credits. Paid-plan top-ups: $10 for 1,000 credits.',pricing,'/pricing/')

# Documentation: each guide's body is content/docs/<section>/<slug>.html, a run
# of <section id="..."><h2>...</h2>...</section> blocks; the contents list is
# read from those headings. DOCS orders the sections and their guides; the docs
# index, the docs menu and the previous/next links all follow it. A guide's
# address is /docs/<slug>/ whichever section holds it.
def guide(slug, kicker, label, title, summary, intro, note=False):
    return dict(slug=slug, kicker=kicker, label=label, title=title, summary=summary, intro=intro, note=note)

DOCS = [
    ('get-started', 'Get started', 'What Atomic is, your account and workspace, and your first app.', [
        guide('what-is-atomic', 'OVERVIEW', 'Overview', 'What is Atomic', 'How an idea becomes a running app, and the words you will meet on the way.',
              'Atomic builds web apps from a description. Here is how the pieces fit together, from your first message to a published app.'),
        guide('account', 'ACCOUNT', 'Account', 'Create an account and sign in', 'Sign up, verify your email, and manage your settings.',
              'Create your Atomic account, verify your email address, and find your way around your settings.'),
        guide('workspaces', 'WORKSPACES', 'Workspaces', 'Workspaces and teammates', 'Group apps and invite the people who build them with you.',
              'A workspace holds your apps and the teammates who build them. Choose where new apps go and invite people to help.'),
        guide('getting-started', 'START HERE', 'Getting started', 'From idea to first app', 'Turn a business need into a useful, testable first brief.',
              'Give Atomic a clear starting point: who the app helps, what they need to do, and what a successful result looks like.', note=True),
        guide('templates', 'TEMPLATES', 'Templates', 'Start from a template', 'Try a complete app on sample data, then make it yours.',
              'A template is a complete Atomic app — screens, backend and believable sample data — that you can try first and then make your own.', note=True),
    ]),
    ('build', 'Build', 'Describe your app, make the first design choices and follow each build.', [
        guide('describe-your-app', 'DESCRIBE', 'Build', 'Describe your app', 'Start an app, borrow a look, and attach images or Figma designs.',
              'Start a new app with a description. Borrow a look from a website, a screenshot or a Figma design, and choose how Atomic should respond.'),
        guide('design-choices', 'DESIGN', 'Build', 'Design choices before the first build', 'Pick colors, type and layout, or skip straight to building.',
              'Before the first build, Atomic offers a few optional choices about how your app should look.'),
        guide('builds-and-checks', 'BUILDS', 'Build', 'Builds and checks', 'Follow a build, read its result, and find every build in one place.',
              'Every request starts a build that Atomic checks before you use it. Here is what happens and how to follow it.'),
        guide('building-with-atomic', 'BUILD & REFINE', 'Build & refine', 'Building with Atomic', 'Work in small steps, review the preview, and check the result.',
              'Describe a change, inspect the result, and move forward with a version you understand.', note=True),
    ]),
    ('canvas', 'Canvas', 'See every screen at once, edit it directly and ask for changes in place.', [
        guide('canvas', 'CANVAS', 'Canvas', 'The canvas', 'Every screen on one board, running on sample data.',
              'The canvas shows every screen of your app at once, running on sample data, so you can try it as each kind of user and edit it in place.'),
        guide('editing', 'EDIT', 'Canvas', 'Editing on the canvas', 'Select an element and change its text, layout and style.',
              'Select any element on a screen to change its text, position, size and style, or the theme of the whole app, then apply your changes.'),
        guide('screens-and-roles', 'SCREENS', 'Canvas', 'Screens, states and roles', 'How an app’s screens, states and roles fit together.',
              'Every app keeps a list of its screens, the states you can open them in, and the roles that decide who can see each one.'),
        guide('comments', 'ANNOTATE', 'Canvas', 'Annotations', 'Comment on an element and ask Atomic for a change there.',
              'Describe a change right beside the element it is about, and follow Atomic’s work in a thread.'),
    ]),
    ('data-and-users', 'Data and users', 'Where your app keeps its data, and who can use and build it.', [
        guide('app-data', 'DATA', 'Data', 'How your app’s data works', 'Sample data, preview data and real data, and who sees which records.',
              'Every app has its own backend for accounts and records. Know which data is sample, which is temporary, and which belongs to your users.'),
        guide('app-access', 'ACCESS', 'Access', 'Who can use your app', 'Access modes, app users and your first admin.',
              'Choose how people get into your finished app, invite them, and give them the right roles.'),
        guide('collaborators', 'COLLABORATORS', 'Collaborators', 'Collaborators', 'Invite people to build one app with you.',
              'Invite people to build a single app with you in Atomic, and decide what each of them can do.'),
    ]),
    ('publish-and-run', 'Publish and run', 'Check the real experience, publish it, and look after it once it is live.', [
        guide('publishing', 'PUBLISHING', 'Publishing', 'Before your app goes live', 'A practical guide to reviewing a customer-facing app.',
              'A working preview is a starting point. Review the real customer experience before sharing a published version.', note=True),
        guide('publish-your-app', 'PUBLISH', 'Publishing', 'Publish your app', 'Put a verified version live at its own address.',
              'Publishing serves a verified version of your app at its own address, with its own users and data.'),
        guide('custom-domains', 'DOMAINS', 'Publishing', 'Custom domains', 'Serve your app at a subdomain you own, with HTTPS.',
              'Connect a subdomain you own to a published app. Atomic sets up HTTPS and keeps checking the connection.'),
        guide('deployments', 'DEPLOYMENTS', 'Publishing', 'Deployments and rollback', 'See what is live and serve an earlier release again.',
              'Every publication is kept. See what is live, and serve an earlier release again if something goes wrong.'),
        guide('logs', 'LOGS', 'Debugging', 'Logs', 'What the app said while you tried it.',
              'Logs show what your app did in its preview: its console, its requests and its server, side by side.'),
    ]),
    ('versions-and-source', 'Versions and source', 'What your source, your versions and your app’s data each cover.', [
        guide('versions', 'VERSIONS', 'Versions', 'Version history', 'Every verified checkpoint, and how to go back to one.',
              'Each verified build becomes a version. Look back through them and restore an earlier one.'),
        guide('code', 'CODE', 'Source', 'Browse and download code', 'Read your app’s source and download it.',
              'Read your app’s source from any verified version and download it as an archive.'),
        guide('source-and-data', 'SOURCE & DATA', 'Source & data', 'What you can take with you', 'Understand generated source, app data, and hosting.',
              'Generated source, business data, and hosting are separate parts of your app. Understand each one before you plan a move.'),
    ]),
    ('help', 'Usage and help', 'Credits and usage, fixing common problems, and the words and limits to know.', [
        guide('usage-and-credits', 'USAGE', 'Usage', 'Usage and credits', 'What credits measure and where they went.',
              'Building uses credits. See what they measure, what happens when they run out, and where they went.'),
        guide('troubleshooting', 'HELP', 'Help', 'Troubleshooting', 'What to do when something does not work.',
              'Common problems while building, publishing and inviting people, and what to do about each.'),
        guide('glossary', 'REFERENCE', 'Reference', 'Glossary', 'Every term used in these guides.',
              'The words used across Atomic and these guides, in one place.'),
        guide('limits', 'REFERENCE', 'Reference', 'Current limits', 'What Atomic does not do yet, in one list.',
              'What to know before you rely on Atomic: the current limits that affect building, data, access and publishing.'),
    ]),
]
GUIDES = [dict(guide, section=key, section_title=name) for key, name, _, guides in DOCS for guide in guides]
guide_note = notice('Before you start','Atomic is preparing for early access. The examples on this website are local demonstrations using sample data; they do not generate or host an app.')

def docs_menu(current):
    def item(guide):
        here = ' aria-current="page"' if guide['slug'] == current else ''
        return f'<li><a href="/docs/{guide["slug"]}/"{here}>{guide["title"]}</a></li>'
    groups = ''.join(f'<div class="docs-nav-group"><p class="docs-nav-title">{name}</p><ul>' + ''.join(item(g) for g in guides) + '</ul></div>' for _, name, _, guides in DOCS)
    return f'<nav class="docs-nav" aria-label="Documentation"><a class="docs-nav-home" href="/docs/">All documentation</a>{groups}</nav>'

def pager(index):
    def side(guide, rel, label):
        return f'<a class="pager-{rel}" href="/docs/{guide["slug"]}/" rel="{rel}"><span>{label}</span>{guide["title"]}</a>' if guide else '<span></span>'
    previous = GUIDES[index - 1] if index > 0 else None
    following = GUIDES[index + 1] if index + 1 < len(GUIDES) else None
    return f'<nav class="pager" aria-label="Previous and next guides">{side(previous, "prev", "Previous")}{side(following, "next", "Next")}</nav>'

def guide_page(index):
    guide = GUIDES[index]
    body = (ROOT / 'content/docs' / guide['section'] / f'{guide["slug"]}.html').read_text().strip()
    headings = re.findall(r'<section id="([^"]+)"><h2>(.*?)</h2>', body)
    # Reading time from the guide's own words (figures aside), at 200 a minute.
    words = len(re.sub(r'<[^>]+>', ' ', re.sub(r'<figure.*?</figure>', '', body, flags=re.S)).split())
    meta = f'{guide["label"]} · {max(1, -(-words // 200))} min read'
    crumb = f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/docs/">Documentation</a><span aria-hidden="true">/</span><a href="/docs/#{guide["section"]}">{guide["section_title"]}</a><span aria-hidden="true">/</span><span aria-current="page">{guide["title"]}</span></nav>'
    heading = f'<section class="page-hero"><div class="container">{crumb}<p class="eyebrow">{guide["section_title"].upper()}</p><h1>{guide["title"]}</h1><p class="lead">{guide["intro"]}</p><p class="article-meta">{meta}</p></div></section>'
    toc = '<nav class="contents" aria-label="On this page"><strong>On this page</strong>' + ''.join(f'<a href="#{sid}">{name}</a>' for sid, name in headings) + '</nav>'
    note = guide_note if guide['note'] else ''
    page('docs/' + guide['slug'], guide['title'], guide['intro'], heading + f'<div class="container docs-layout">{docs_menu(guide["slug"])}{toc}<article class="prose">{note}{body}{pager(index)}</article></div>', '/docs/')

docs = hero('ATOMIC DOCUMENTATION','A good idea.<br /><em>A clear next step.</em>','Practical guides to describing, shaping, and reviewing your app. Start with the essentials.')
docs += '<section class="page-section"><div class="container">'+notice('Early-access guides','These guides describe Atomic as it works in early access. Screens and steps may change as the product develops, and plan limits are not final.')+'<div class="search-field"><label for="guide-search">Find a guide</label><input id="guide-search" type="search" placeholder="Try “source” or “publish”" aria-describedby="search-status" /></div><p id="search-status" class="search-status" role="status" aria-live="polite">'+f'{len(GUIDES)} guides available</p>'
for key, name, blurb, guides in DOCS:
    docs += f'<section class="docs-group" id="{key}" data-guide-group aria-labelledby="{key}-title"><div class="docs-group-intro"><h2 id="{key}-title">{name}</h2><p>{blurb}</p></div><div class="resource-grid two-cols">' + ''.join(card(g['kicker'], g['title'], g['summary'], f'/docs/{g["slug"]}/', guide=True, level=3) for g in guides) + '</div></section>'
docs += '</div></section>'+cta()
page('docs','Documentation','Learn how to describe, shape, review, and prepare an app with Atomic.',docs,'/docs/')
for index in range(len(GUIDES)):
    guide_page(index)

POSTS = [
    ('INTRODUCING ATOMIC','Introducing Atomic: from idea to application','Meet Atomic, a new way to build and refine web apps through conversation. Early-access requests are open.','/blog/introducing-atomic/','From idea<br />to app.'),
    ('BUILDING USEFUL SOFTWARE','Start with one useful thing','A smaller first version makes it easier to discover what your business actually needs.','/blog/start-with-one-useful-thing/','One task.<br />Done well.'),
    ('THE ATOMIC APPROACH','Your app is more than its interface','Why identity, data, permissions, and source access belong in the conversation from the beginning.','/blog/more-than-an-interface/','Beyond<br />the screen.')
]
blog = hero('THE ATOMIC BLOG','Notes on making<br /><em>ideas real.</em>','Thoughts on useful software, small beginnings, and building with a foundation you can understand.')
blog += '<section class="page-section"><div class="container"><div class="resource-grid two-cols">'
for tag,title,desc,url,cover in POSTS:
    blog += f'<a class="resource-card article-card" href="{url}"><div class="article-cover" aria-hidden="true">{cover}</div><div class="article-copy"><p class="eyebrow">{tag}</p><h2>{title}</h2><p>{desc}</p><span class="card-link">Read the story <span aria-hidden="true">↗</span></span></div></a>'
blog += '</div></div></section>'+cta()
page('blog','Blog','Field notes from Atomic on useful software, building apps, and turning ideas into something real.',blog,'/blog/')
article('blog/introducing-atomic','Introducing Atomic: from idea to application','Meet Atomic, a new way to build and refine web apps through conversation. Early-access requests are open.',[
    ('why','Why we’re building Atomic','<p>Good ideas for software often come from people who understand a problem firsthand. A founder sees a better way to serve customers. A small team needs a tool that fits the way it works. A developer has a product idea and wants to find out if people will use it.</p><p>Yet getting from an idea to something people can try still takes time and technical work. At Abstract Machines, we’re building Atomic to make that first step easier. Today, we’re introducing it and inviting people to request early access.</p><figure class="launch-video"><video controls preload="metadata" playsinline poster="/assets/video/atomic-promo-poster.jpg" aria-label="Atomic promotional video"><source src="/assets/video/atomic-promo-canvas.mp4" type="video/mp4" /><a href="/assets/video/atomic-promo-canvas.mp4">Download the Atomic promotional video</a></video><figcaption>See the idea behind Atomic in 40 seconds.</figcaption></figure>'),
    ('conversation','Start with a conversation','<p>Tell Atomic what you want to build, who it’s for, and what those people need to do. Atomic generates a web application you can preview. From there, you can describe what needs to change and build another version. The first result gives you something concrete to react to.</p><p>It might be a customer portal, an internal tool, or the first version of a new product. Seeing an app take shape while the idea is still fresh helps you decide what it really needs.</p><!-- Launch asset: approved Builder screenshot showing the prompt and resulting app preview. Provide descriptive alt text and caption. -->'),
    ('beyond','Keep building from there','<p>The first preview is a beginning. Builders can inspect generated source, review verified versions, and choose a version to publish. That gives you a way to understand and improve the app as your idea develops.</p><p>Atomic builds on Atom, Abstract Machines’ open-source foundation for identity, permissions, and data. A useful app needs those pieces as well as an interface. As with any generated software, review and test your app before using it with real customers or important data.</p><!-- Launch asset: approved Builder screenshot of source and verified versions, or a real published app. Confirm the depicted feature is available to invited users. -->'),
    ('access','Help shape what comes next','<p>We’re starting with a limited number of builders so we can learn from the people using Atomic. We want to see what you try to make, where the experience helps, and where it gets in your way. We’ll review requests and invite selected people in batches as the product develops.</p><p>Requesting access does not create a Builder account or guarantee an invitation. If you have an idea you want to try, tell us what it is, who would use it, and how you handle that work today. We’d love to hear about it.</p><p><a class="button button-primary" href="/#early-access">Tell us your idea and request early access <span aria-hidden="true">↗</span></a></p>'),
],category='Field notes',active='/blog/',meta='Abstract Machines · 27 October 2026 · 3 min read')
article('blog/start-with-one-useful-thing','Start with one useful thing','Your first app does not have to run your whole business. It needs to make one part of it easier.',[
    ('friction','Start where the friction is','<p>A studio owner answers the same scheduling questions every week. A small shop shares product details across a string of messages. A freelancer sends another email explaining where a project stands.</p><p>Each is a modest problem with a recognizable cost: time, attention, or uncertainty. Each is also a useful starting point for an app.</p>'),
    ('small','Make the first version small','<p>It is tempting to add a dashboard, notifications, payments, and a loyalty program before anyone has tried the main workflow. But each addition introduces another decision and another way for the experience to become confusing.</p><p>For a booking app, the first useful version might let someone choose a service and request a time, then let the owner confirm it. That is enough to ask whether the app makes the exchange clearer.</p>'),
    ('learn','Use the app to learn','<p>Show the first version to someone who would use it. Ask them to complete the task without explaining every screen. Notice where they hesitate and which information they look for.</p><p>The next improvement may be a better label or a clearer confirmation, not a new feature. A narrow first version makes those observations easier to act on.</p>'),
    ('atomic','Bring that focus to Atomic','<p>Atomic starts with a description of what you want to build. The more clearly you can explain the person, the task, and the result, the better a starting point you have for reviewing the app.</p><p>Think of your first brief as a hypothesis: this small piece of software will make this particular job easier. Build enough to try it, then decide what comes next.</p><p><a href="/docs/getting-started/">Write your first app brief →</a></p>')
],category='Field notes',active='/blog/',meta='Atomic · Product perspective · 3 min read')
article('blog/more-than-an-interface','Your app is more than its interface','The screen is what people see. The foundation determines what they can safely do.',[
    ('screen','A good screen is the beginning','<p>A booking form can look finished before it answers the most important questions. Where does the request go? Who can change it? Can another customer see it? What happens when the owner confirms?</p><p>These questions turn a collection of screens into an application. They are part of the product experience, even when users never see the machinery underneath.</p>'),
    ('foundation','Identity, data, and permissions','<p>Atomic uses Atom as its open-source backend foundation. Identity establishes who is using an app. Data holds the records that make it useful. Permissions determine who can read and change them.</p><p>Those pieces still need careful configuration and testing. An open-source foundation gives you code you can inspect; it is not a substitute for checking the behavior of your particular application.</p>'),
    ('control','Keep the boundaries visible','<p>Source access is another part of that foundation. Being able to browse and download generated code helps you understand what was built and keep a copy of your work.</p><p>But source is not customer data, and neither is hosting. Atomic treats those as distinct concerns. Broader packaging and deployment options remain on the roadmap; we want the current boundaries to be clear while that work develops.</p>'),
    ('build','Build with the whole app in mind','<p>When you describe an app, include who uses it, which records they work with, and what each person may do. When you review it, test those relationships as carefully as the layout.</p><p>The ambition is simple: useful software that looks good, behaves clearly, and gives you a foundation you can understand.</p><p><a href="/docs/source-and-data/">Read about source, data, and hosting →</a></p>')
],category='Field notes',active='/blog/',meta='Atomic · Product perspective · 3 min read')

security = hero('SECURITY & TRUST','Build with<br /><em>your eyes open.</em>','Understand the foundation, know the boundaries, and bring the right checks to every app you publish.')
security += '<section class="page-section"><div class="container"><div class="resource-grid">'+card('FOUNDATION','Identity & permissions','Atom provides the backend foundation. Each generated app still needs its access rules reviewed and tested.','/docs/publishing/','Review before publishing')+card('VISIBILITY','Source you can inspect','Browse and download generated source. Data records, infrastructure, and source history remain separate concerns.','/docs/source-and-data/','Understand the boundaries')+card('DATA','Clear responsibilities','The draft privacy notice and DPA describe the intended split between Atomic’s service and your own app.','/legal/','Review the legal drafts')+'</div></div></section>'
security += '<section class="page-section"><div class="container"><div class="notice"><strong>Security information for early access</strong>We are preparing the operational security documentation. This page does not assert a certification, compliance status, uptime guarantee, data-residency commitment, or completed independent audit.</div><div class="section-intro"><h2>Report a security concern.</h2><p>If you find a potential vulnerability, send the affected page, steps to reproduce, and the likely impact. Avoid including secrets or other people’s personal data.</p></div><a class="button button-secondary" href="mailto:info@absmach.eu?subject=Atomic%20security%20report">Contact the Atomic team ↗</a></div></section>'
page('security','Security & trust','Understand Atomic’s security boundaries, data responsibilities, and security reporting contact.',security)

# Company context supports the product; sources are linked in the page.
about = hero('ABOUT ATOMIC','Good ideas deserve<br /><em>a way forward.</em>','We’re building Atomic for the moment you know what your business needs—and want to make it real.')
about += '''<section class="page-section"><div class="container about-intro"><h2>Useful software starts<br />with your world.</h2><div class="prose"><p>A studio that needs a better way to take bookings. A small brand ready for its first shop. A team that wants to keep clients in the loop. The people closest to a business often know exactly what would make it work better.</p><p>Atomic gives those ideas a place to take shape: describe the app, refine it in conversation, review the result, and prepare it for the people who will use it.</p></div></div></section>
<section class="page-section"><div class="container"><div class="resource-banner about-company"><div><p class="eyebrow">THE TEAM BEHIND THE PRODUCT</p><h2>Built by<br />Abstract Machines.</h2><p>Atomic is a product of Abstract Machines, an open-source infrastructure company based in Paris. The team’s work spans identity, messaging, connected systems, and edge computing.</p><a class="button button-light" href="https://www.absmach.eu/" target="_blank" rel="noopener noreferrer">Meet Abstract Machines <span aria-hidden="true">↗</span></a></div><div class="about-evidence"><div><span class="eyebrow">01 / THE FOUNDATION</span><h3>We build the layers underneath.</h3><p>The same company develops Atom, the open-source identity and authorization foundation used by Atomic.</p><a href="https://www.absmach.eu/products/atom/" target="_blank" rel="noopener noreferrer">Explore Atom <span aria-hidden="true">↗</span></a></div><div><span class="eyebrow">02 / WORK YOU CAN EXPLORE</span><h3>A practice of building openly.</h3><p>Explore Abstract Machines’ public repositories to see its open-source work, development history, and contributions.</p><a href="https://github.com/absmach" target="_blank" rel="noopener noreferrer">Browse the open-source projects <span aria-hidden="true">↗</span></a></div></div></div></div></section>
<section class="page-section"><div class="container"><div class="section-intro"><h2>What matters to us.</h2></div><div class="about-principles"><article><span class="eyebrow">01 / USEFULNESS</span><h3>Start with a real task.</h3><p>A good app helps someone do something that matters. We start with the workflow and shape the experience around it.</p></article><article><span class="eyebrow">02 / VISIBILITY</span><h3>Understand what you build.</h3><p>Previews, source access, and clear product boundaries help you review your app and make informed decisions.</p></article><article><span class="eyebrow">03 / CONTROL</span><h3>Keep a hand in the process.</h3><p>Describe the direction, inspect the result, and choose what to publish. Your judgment belongs in every step.</p></article></div></div></section>'''+cta()
page('about','About Atomic','Meet Atomic and Abstract Machines, the open-source infrastructure company behind the product.',about,'/about/')

# Legal copy is original drafting material. Unknown facts remain explicit.
LEGAL_NOTICE = notice('Draft for review · Not yet effective','Prepared 19 October 2026. This is proposed wording for Atomic’s launch, not an effective agreement or a completed compliance statement. Items marked “To finalize” require company verification and legal review before activation.')
LEGAL = [
    ('privacy','Privacy Policy','What we collect through this website and early-access requests, why, and your rights.'),
    ('terms','Terms of Service','The proposed relationship between Atomic and the people using it.'),
    ('acceptable-use','Acceptable Use Policy','Rules for responsible use of the builder, infrastructure, and published apps.'),
    ('dpa','Data Processing Agreement','Proposed obligations when Atomic processes personal data on a customer’s behalf.'),
    ('subprocessors','Subprocessor List','The register of providers that must be verified before customer data processing begins.'),
    ('cookies','Cookies & Storage Notice','What the current website does locally and what must be checked in hosting.')
]
legal = hero('THE LEGAL LIBRARY','Clear terms.<br /><em>Shared understanding.</em>','Policies for the way we build, use, and look after Atomic. Review the launch drafts in one place.')
legal += '<section class="page-section"><div class="container">'+LEGAL_NOTICE+'<div class="legal-list">'+''.join(f'<a class="legal-row" href="/legal/{slug}/"><h2>{title}</h2><p>{desc}</p><span aria-hidden="true">↗</span></a>' for slug,title,desc in LEGAL)+'</div></div></section>'
page('legal','Legal','Atomic’s privacy policy, draft terms, acceptable use, DPA, subprocessors, and cookie information.',legal,draft=True)

def legal_article(slug, sections, final=''):
    _,title,intro = next(item for item in LEGAL if item[0]==slug)
    article('legal/'+slug,title,intro,sections,category='Legal',active='',note='' if final else LEGAL_NOTICE,meta=final or 'Draft version 0.1 · Prepared 19 October 2026',draft=not final,related='<div class="related"><a href="/legal/">← All legal documents</a><a href="mailto:info@absmach.eu?subject=Atomic%20legal%20inquiry">Contact the Atomic team</a></div>')

legal_article('privacy',[
    ('who','1. Who we are','<p>Atomic is built by Abstract Machines. We decide why and how the information described here is used. Contact us at <a href="mailto:info@absmach.eu">info@absmach.eu</a> with any privacy question or request.</p>'),
    ('collect','2. What we collect','<p>When you request early access, you give us:</p><ul><li>the idea you describe, which may include personal details if you write them in, so please leave out anything confidential;</li><li>the kind of project, your stage, and your role, including any detail you add under “Something else”;</li><li>your name, your email address, and your company or project if you choose to give one.</li></ul><p>We also record the time of your request and, if the link you arrived on carried campaign tags such as utm_source, those tags, so we know which link brought you here. Our hosting provider processes technical data such as your IP address and request logs to deliver and protect the site. This website does not use advertising or analytics trackers.</p>'),
    ('use','3. Why we use it','<p>We use your answers to decide who to invite to the Atomic free trial, to email you about early access, and to understand what people want to build. You agree to this when you submit the early-access form, which tells you this beneath its button, and you can withdraw that agreement at any time. Withdrawing does not affect what we did before.</p><p>We use technical data to run the site, block automated sign-ups, and keep it secure. We do that because it is necessary to operate the website safely.</p><p>We do not sell your information, and we do not use it for advertising.</p>'),
    ('processors','4. Who handles it','<ul><li><strong>Cloudflare</strong> hosts this website and runs Turnstile, the check that tells people from bots. Turnstile looks at signals from your browser when you request early access.</li><li><strong>Our mailing-list service</strong> (Listmonk, run by Abstract Machines) stores your answers and sends our emails.</li><li><strong>Our email delivery provider</strong> carries the emails we send you.</li></ul><p>These providers act on our instructions, except Cloudflare, which also acts for its own security purposes under its own privacy policy. We share information with authorities only when the law requires it.</p>'),
    ('transfers','5. Where it goes','<p>Cloudflare serves the site from locations around the world. If your information is transferred outside your country, we rely on the safeguards the law provides for that, such as standard contractual clauses. Ask us at the address above for details.</p>'),
    ('retention','6. How long we keep it','<p>We keep early-access applications until the early-access programme ends, or until you ask us to delete yours, whichever comes first. If you become a customer, a separate notice will explain what we keep for your account. Hosting logs are kept by Cloudflare for the period its settings specify.</p>'),
    ('rights','7. Your rights','<p>Depending on where you live, you can ask us to give you a copy of your information, correct it, delete it, restrict or object to how we use it, or move it to another service. You can also withdraw your agreement to emails at any time, either by asking us or with the unsubscribe link in any message. Email <a href="mailto:info@absmach.eu">info@absmach.eu</a> and we will reply within one month. You may also complain to your local data protection authority.</p>'),
    ('storage','8. Cookies and browser storage','<p>The site itself sets no cookies and uses no browser storage. Turnstile, which loads from Cloudflare only when you reach the last step of the early-access form, may use limited browser storage to complete its check.</p>'),
    ('changes','9. Changes','<p>If we change this policy in a way that matters, we will update the date below and, where we have your email address, tell you.</p>'),
],final='Effective 21 October 2026')

legal_article('terms',[
    ('agreement','1. Agreement and eligibility','<p>These proposed terms govern access to Atomic’s app builder and associated services. Once finalized, they will identify the legal provider and explain how you accept the agreement. A person accepting on behalf of an organization must have authority to bind it.</p><p><strong>To finalize:</strong> provider legal name, address, registration, minimum age, service territories, effective date, and acceptance flow. This draft does not create a subscription or bind a visitor merely by viewing it.</p>'),
    ('service','2. The service and early access','<p>Atomic helps users describe, generate, refine, inspect, and publish applications. AI-generated results may be incomplete, inaccurate, insecure, or unsuitable for a particular use. You must review and test results before using them with real users or data.</p><p>Early-access features may change, have limited availability, or be withdrawn. Roadmap descriptions are not delivery commitments. Homepage demonstrations use local sample data and do not create live applications or transactions.</p>'),
    ('accounts','3. Accounts and workspace access','<p>You are responsible for providing accurate account information, protecting credentials, and controlling access granted to your workspace. Notify the team promptly if you suspect unauthorized access. Do not share credentials in prompts, source repositories, or support messages.</p><p>Organizations are responsible for the actions of authorized users within their workspace, subject to applicable law and the final agreement.</p>'),
    ('billing','4. Plans, fees, and credits','<p>The pricing page currently describes proposed plans, not an offer to start a paid subscription. The final checkout must disclose the plan, currency, taxes, billing frequency, included usage, extra charges, renewal terms, and cancellation process before payment.</p><p>Any credit system must define how units are consumed, how failed or retried operations are treated, when balances expire, and whether unused balances roll over. Auto-renewal, top-ups, and automatic replenishment require clear disclosure and any required authorization.</p><p><strong>To finalize:</strong> all allowances and rates, payment provider, renewal notices, cancellation method, credit expiry, refunds, charge disputes, and applicable consumer withdrawal rights. Mandatory consumer rights prevail over conflicting terms; no blanket non-refundable rule is established by this draft.</p>'),
    ('content','5. Content, source, and licenses','<p>You retain rights you hold in the content you provide. As between you and the provider, the proposed arrangement is that you receive the provider’s transferable rights, if any, in generated output, subject to applicable law and third-party rights. AI output may not be unique or eligible for intellectual-property protection.</p><p>You grant the provider the limited rights needed to process your content to supply, secure, and support the service on your instructions. The provider retains rights in Atomic’s platform, branding, and pre-existing materials. Third-party dependencies and open-source components retain their own license terms.</p><p><strong>To finalize:</strong> confirm output-rights language against model-provider contracts and approve any separate training or improvement use. This clause does not authorize unrestricted training on customer data.</p>'),
    ('responsibilities','6. Your apps and responsibilities','<p>You are responsible for the information you submit, rights to use supplied materials, and the apps you choose to publish. Review generated code, permissions, business rules, notices, and third-party integrations. Follow the <a href="/legal/acceptable-use/">Acceptable Use Policy</a>.</p><p>You are responsible for your relationship with the people using your app, including appropriate privacy notices, lawful data collection, customer support, and any regulated activity. Atomic’s own policies do not replace the documents your app may require.</p>'),
    ('data','7. Privacy, data, and portability','<p>The <a href="/legal/privacy/">Privacy Notice</a> describes the provider’s own processing. A completed <a href="/legal/dpa/">DPA</a> governs processing on a customer’s behalf where applicable.</p><p>Source downloads do not include customer accounts, business records, or hosting infrastructure. Restoring source or rolling back a frontend release does not restore business data. Broader packaging and deployment options are roadmap items. Confirm supported export and recovery procedures before relying on them.</p>'),
    ('suspension','8. Suspension and termination','<p>The proposed service terms allow proportionate restrictions where necessary to address unlawful use, a material breach, nonpayment, or a credible security risk. Where appropriate, the provider should explain the issue and allow an opportunity to resolve it, except where immediate action or confidentiality is required.</p><p><strong>To finalize:</strong> notice periods, appeal process, consequences of cancellation, app availability, export access, deletion timing, prepaid-fee treatment, and treatment of unused credits. These consequences must be disclosed before a subscription begins.</p>'),
    ('risk','9. Warranties and liability','<p>Generated output requires review, and no early-access material should be read as a guarantee of uninterrupted availability, error-free software, regulatory compliance, or fitness for a particular purpose. Any agreed service levels must be documented separately.</p><p><strong>To finalize with counsel:</strong> express warranties, permissible disclaimers, liability caps and exclusions, intellectual-property claims, indemnities if appropriate, and exceptions for liability that cannot legally be limited. No numerical liability cap is established in this draft.</p>'),
    ('general','10. Changes, disputes, and contact','<p>Material contractual changes should be communicated in advance as required by applicable law and the final agreement. Any separate signed order or enterprise agreement should specify how it interacts with these terms.</p><p>Contact <a href="mailto:info@absmach.eu">info@absmach.eu</a> about a service or contractual concern.</p><p><strong>To finalize:</strong> governing law, courts or dispute mechanism, consumer protections, notice methods and periods, assignment, severability, and order of precedence. No jurisdiction is inferred from a brand name or website address.</p>')
])

legal_article('acceptable-use',[
    ('scope','1. Scope','<p>This proposed policy covers use of Atomic’s builder, prompts, generated applications, hosted resources, and integrations. It is intended to form part of the final Terms of Service. You are responsible for authorized users and applications you operate.</p>'),
    ('harm','2. Unlawful or harmful activity','<p>Do not use the service to commit fraud, facilitate exploitation, threaten or harass people, distribute unlawful content, or violate another person’s privacy or intellectual-property rights. Child sexual abuse material and sexual exploitation of minors are prohibited.</p><p>Do not impersonate a person or organization deceptively, build phishing experiences, steal credentials, facilitate scams, or distribute malware.</p>'),
    ('systems','3. Protect systems and resources','<p>Do not attempt unauthorized access, bypass authentication or billing controls, extract another customer’s data, evade usage limits, or interfere with service availability. Do not use the service for denial-of-service activity, abusive automated traffic, unsolicited bulk messaging, or unauthorized resource consumption.</p><p>Security testing must stay within an expressly authorized scope. A vulnerability report is not permission to access other users’ records, persist access, or disrupt operations.</p>'),
    ('data','4. Handle data responsibly','<p>Only submit information you have the right and lawful basis to process. Do not place secrets, credentials, or unnecessary personal data into prompts or public source files. Configure access controls for your app’s actual audience.</p><p>Do not use the standard service for sensitive or regulated records, including protected health information, payment-card data, or special-category personal data, unless a written agreement and the deployed safeguards explicitly support that use.</p>'),
    ('review','5. Review generated applications','<p>Do not represent generated output as professionally certified, secure, or legally compliant without an appropriate basis. Test your applications before publication and take reasonable steps to address reported vulnerabilities and harmful behavior.</p><p>Third-party integrations may impose their own lawful-use requirements. You are responsible for services you connect directly and for your app’s relationship with its users.</p>'),
    ('enforcement','6. Reports and enforcement','<p>Report suspected abuse to <a href="mailto:info@absmach.eu?subject=Atomic%20abuse%20report">info@absmach.eu</a>. Include the relevant URL, a description, and supporting context without unnecessarily sharing personal information.</p><p>Proposed responses include requesting remediation, restricting a feature, removing unlawful content, or suspending access according to the seriousness and urgency of the issue. Where appropriate, the provider should explain the action and allow review, subject to legal and security constraints.</p><p><strong>To finalize:</strong> verify the operating abuse process, appeals, response ownership, evidence retention, and any hosting-platform notice obligations before this policy becomes effective.</p>')
])

legal_article('dpa',[
    ('parties','1. Parties, roles, and precedence','<p>This draft Data Processing Agreement is intended to supplement a finalized Atomic service agreement when the provider processes personal data on a customer’s behalf. The customer acts as controller or as a processor authorized by its controller; the provider acts as processor or subprocessor respectively.</p><p>The provider’s own account, billing, and business-contact processing is separately described in its Privacy Notice. This DPA should prevail for conflicts concerning the processing it covers; mandatory transfer clauses take precedence where required.</p><p><strong>To finalize:</strong> identify both legal parties, the underlying agreement, applicable data-protection laws, and the acceptance or signature mechanism. This draft is not an executed DPA.</p>'),
    ('instructions','2. Documented instructions','<p>The provider shall process customer personal data only on documented instructions to provide the agreed service, including instructions about international transfers, unless applicable law requires otherwise. Where legally permitted, it shall inform the customer of a mandatory processing requirement before processing.</p><p>The provider shall promptly inform the customer if, in its opinion, an instruction infringes applicable data-protection law. The customer is responsible for lawful instructions, required notices, and a valid basis for providing the personal data.</p>'),
    ('people','3. Confidentiality and security','<p>The provider shall ensure that persons authorized to process personal data are subject to appropriate confidentiality obligations and receive access only as needed for their duties.</p><p>The provider shall implement appropriate technical and organizational measures proportionate to the processing risks. The completed security annex must describe actual safeguards, including access controls, encryption where appropriate, tenant separation, vulnerability management, recovery, and review of security effectiveness.</p><p><strong>To finalize:</strong> complete Annex B with verified measures and operational owners. This draft does not certify that a particular control is currently implemented.</p>'),
    ('subprocessors','4. Subprocessors','<p>The proposed arrangement is general written authorization for the specifically disclosed subprocessors in the completed register, with advance written notice of additions or replacements and a meaningful opportunity for the customer to object on data-protection grounds.</p><p>The provider shall impose equivalent applicable data-protection obligations on subprocessors and remain responsible to the customer for their performance as required by law.</p><p><strong>To finalize:</strong> the initial approved list, notice period, notification channel, objection process, and resolution or termination rights. No unidentified vendor is approved by this draft.</p>'),
    ('assistance','5. Assistance and rights requests','<p>Taking account of the nature of processing and information available, the provider shall assist the customer with data-subject requests, security obligations, breach notifications, impact assessments, and prior consultation with authorities where required.</p><p>The provider shall notify the customer of relevant requests received directly and shall not respond on the customer’s behalf except as instructed or required by law. Any fees for assistance beyond the agreed service must be specified in the final agreement and must not prevent compliance with mandatory obligations.</p>'),
    ('incident','6. Personal-data breaches','<p>The provider shall notify the customer without undue delay after becoming aware of a personal-data breach affecting the covered data. Notification shall include available information about its nature, affected categories and approximate scale, likely consequences, mitigation, and a contact point.</p><p>Information may be provided in phases as it becomes available. The provider shall cooperate in investigation, containment, and remediation. The customer remains responsible for controller notifications to authorities and individuals unless otherwise required by law.</p><p><strong>To finalize:</strong> incident contacts, secure notification channel, escalation process, and any shorter contractual notification target.</p>'),
    ('transfers','7. International transfers','<p>The provider shall not transfer covered data in violation of applicable transfer rules. Required safeguards must be identified and completed before the transfer, including the appropriate module and annexes of Standard Contractual Clauses or other applicable mechanisms where needed.</p><p><strong>To finalize:</strong> actual locations, remote-access locations, transfer mechanism, assessments and supplementary measures, and any UK or Swiss adaptations. Merely linking to standard clauses does not complete their incorporation.</p>'),
    ('end','8. Return and deletion','<p>At the customer’s choice at the end of the processing service, the provider shall return or delete covered personal data and delete existing copies unless law requires retention. Any lawfully retained information remains protected and restricted to the required purpose.</p><p><strong>To finalize:</strong> supported return format, export window, live-data deletion deadline, backup deletion schedule, and confirmation process. A source-code download is not a return of all customer personal data.</p>'),
    ('audit','9. Demonstrating compliance','<p>The provider shall make available information necessary to demonstrate compliance with its applicable processor obligations and allow and contribute to appropriate audits and inspections by the customer or an authorized auditor.</p><p>Reasonable confidentiality, security, notice, and scheduling arrangements may apply, but must not defeat statutory rights or urgent regulatory requirements. The final agreement must define an operational process for these requests.</p>'),
    ('annex-a','Annex A · Processing details','<p><strong>Subject matter:</strong> the agreed Atomic app-building, preview, publishing, and hosting services, limited to the features actually contracted.</p><p><strong>Nature and purpose:</strong> receipt, storage, organization, retrieval, transmission, and deletion of customer-directed data to provide those services, as applicable.</p><p><strong>To finalize:</strong> duration; customer instructions; actual service scope; categories of data subjects and personal data; frequency of transfers; retention; authorized contacts; and any expressly permitted sensitive data with additional safeguards. Typical possibilities such as app users or booking records are not a substitute for a completed customer-specific description.</p>'),
    ('annex-b','Annex B · Security measures','<p><strong>To finalize before execution:</strong> document and verify identity and access management, privileged access, transport and storage protection, isolation, logging, vulnerability handling, incident response, backup and recovery, deletion, personnel confidentiality, and security review practices. Record the applicable deployment and any customer configuration responsibilities.</p>'),
    ('annex-c','Annex C · Subprocessors and transfers','<p>Complete the <a href="/legal/subprocessors/">subprocessor register</a> with provider legal names, functions, processing locations, data categories, and transfer mechanisms. Attach any required transfer clauses with populated annexes. The current register is a review worksheet, not an approved production vendor list.</p>')
])

legal_article('subprocessors',[
    ('status','1. Register status','<p>No verified production subprocessor inventory has been supplied for this launch draft. The categories below are an inventory to complete, not vendor disclosures or a claim that Atomic uses no subprocessors.</p><p>A provider belongs on the customer-data subprocessor list only where its actual role supports that classification. Providers handling the company’s own business records may instead be recipients described in the Privacy Notice.</p>'),
    ('register','2. Providers to verify','<div class="table-wrap"><table><caption>Draft inventory · Every provider and location remains unconfirmed</caption><thead><tr><th scope="col">Service category</th><th scope="col">Details required</th></tr></thead><tbody><tr><th scope="row">Hosting, database & storage</th><td>Legal provider, data categories, processing and access locations, retention, transfer basis</td></tr><tr><th scope="row">AI inference</th><td>Legal provider, prompt/code handling, model routing, training restrictions, retention, locations</td></tr><tr><th scope="row">Email & support</th><td>Legal provider, message and attachment handling, locations, retention, contractual role</td></tr><tr><th scope="row">Monitoring & diagnostics</th><td>Legal provider if used, log fields, redaction, locations, retention</td></tr><tr><th scope="row">Billing & payments</th><td>Legal provider if used, payment-data flow, controller/processor role, locations</td></tr></tbody></table></div>'),
    ('changes','3. Changes and objections','<p>The finalized DPA should specify advance notification of additions or replacements and the customer’s opportunity to object on relevant data-protection grounds. A website update alone must not be assumed to satisfy a contractual notice obligation.</p><p><strong>To finalize:</strong> versioned register, effective dates, notification mechanism, notice period, and objection-resolution process.</p>'),
    ('contact','4. Request information','<p>For supplier or data-processing questions, contact <a href="mailto:info@absmach.eu?subject=Atomic%20subprocessor%20inquiry">info@absmach.eu</a>. Obtain the finalized register and applicable DPA before relying on Atomic to process production personal data.</p>')
])

legal_article('cookies',[
    ('scope','1. Scope of this notice','<p>This draft covers cookies and similar storage or access technologies on the Atomic marketing website. It describes the checked application source, not a completed audit of every hosting, authentication, or third-party layer.</p>'),
    ('local','2. Current application behavior','<p>The current marketing application does not set cookies or use browser local storage or session storage. Demo bookings, the sample shopping bag, project selections, and typed ideas are held in page memory and reset when the page reloads.</p><p>The site uses locally hosted fonts and images. Its source includes no advertising pixels or analytics scripts. The email flow prepares a draft locally and opens your chosen email application only when you follow the email link. The optional copy button writes the draft to your clipboard after you select it.</p>'),
    ('hosting','3. Hosting and external services','<p>Hosting and access-control infrastructure may independently use cookies, identifiers, or request logs. External destinations and email applications operate under their own notices when you choose to use them.</p><p><strong>To finalize:</strong> audit the actual public deployment, any access gate, response headers, injected scripts, and storage behavior. Record each technology’s name, provider, purpose, type, and lifetime. Do not treat a source-code review as proof that the deployed site uses no cookies.</p>'),
    ('choices','4. Consent and choices','<p>Where applicable law requires consent for a technology, it must not activate before a valid choice. A finalized implementation should explain purposes clearly, allow refusal and later withdrawal, and avoid treating continued browsing as consent. Strictly necessary technologies may have an exemption under applicable rules.</p><p>No marketing consent manager has been added to the current application because the site code does not add optional tracking. That choice must be reassessed after the hosting audit and whenever analytics, advertising, or other integrations are introduced.</p>'),
    ('updates','5. Updates and contact','<p>Update this notice when storage behavior changes and review whether renewed consent is required. Contact <a href="mailto:info@absmach.eu?subject=Atomic%20privacy%20inquiry">info@absmach.eu</a> with questions about the website’s behavior.</p>')
])

# Useful fallback for hosts that support a static 404 document.
page('_not-found','Page not found','Find your way back to Atomic.',hero('404 / A SMALL DETOUR','This idea isn’t here.<br /><em>Let’s find another.</em>','The page may have moved. Explore the product, browse the docs, or head back to the beginning.')+'<section class="page-section"><div class="container"><a class="button button-primary" href="/">Back to Atomic</a> <a class="button button-secondary" href="/docs/">Explore the docs</a></div></section>')
(DIST / '404.html').write_text((DIST / '_not-found/index.html').read_text())
(DIST / '_not-found/index.html').unlink()
(DIST / '_not-found').rmdir()
print(f'Generated {len(list(DIST.rglob("*.html")))} HTML pages.')
