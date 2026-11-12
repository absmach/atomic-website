#!/usr/bin/env python3
"""Generate portable static pages. Run from any directory with Python 3."""
from pathlib import Path
from html import escape
import re
from solutions import render_solutions

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
CONTACT = 'mailto:info@absmach.eu'
# Social preview card for every page; regenerate with scripts/render-social-card.py.
SOCIAL_IMAGE = 'https://atomicapp.dev/assets/atomic-social-v8.png'
SOCIAL_ALT = 'Atomic — Imagine it. Build it.'
FAVICON_LINKS = '<link rel="icon" href="/favicon.ico?v=20261102" sizes="any" /><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png?v=20261102" /><link rel="icon" type="image/svg+xml" href="/favicon.svg?v=20261102" /><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=20261102" />'
NAV = [('Product', '/'), ('Solutions', '/solutions/'), ('Docs', '/docs/'), ('Blog', '/blog/'), ('Pricing', '/pricing/'), ('About', '/about/')]

# Light or dark, set before anything is drawn so a dark page never flashes
# light: the visitor's choice, or their system's when they made none.
THEME_HEAD = '<script>(function(){var c;try{c=localStorage.getItem("atomic-theme")}catch(e){}if(c!=="light"&&c!=="dark")c="system";var d=document.documentElement;d.dataset.themeChoice=c;d.dataset.theme=c==="dark"||(c==="system"&&matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light"})()</script><link rel="stylesheet" href="/dark.css?v=20261102-dark" />'

THEME_TOGGLE = ('<button class="theme-toggle" type="button" data-theme-toggle aria-label="Theme: match system" title="Theme: match system">'
    '<svg class="theme-icon-system" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>'
    '<svg class="theme-icon-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    '<svg class="theme-icon-dark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>'
    '</button>')

def link(label, url, active=''):
    current = ' aria-current="page"' if url == active else (' aria-current="true"' if url == '/solutions/' and active.startswith('/solutions/') else '')
    return f'<a href="{url}"{current}>{label}</a>'

def header(active):
    links = ''.join(link(label, url, active) for label, url in NAV)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-row"><a class="brand" href="/" aria-label="Atomic home"><img class="brand-light" src="/assets/atomic-logo-lowercase-v3.svg" width="1462" height="512" alt="" /><img class="brand-dark" src="/assets/atomic-logo-lowercase-v3-dark.svg" width="1462" height="512" alt="" /></a><nav class="desktop-nav" aria-label="Main navigation">{links}</nav><div class="header-actions">{THEME_TOGGLE}<a class="button button-small" href="/early-access/"><span class="cta-full">Request early access</span><span class="cta-short">Early access</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open navigation"><span></span><span></span></button></div></div><nav id="mobile-nav" class="mobile-nav" aria-label="Mobile navigation" hidden>{links}<a href="/early-access/">Request early access</a></nav></header>'''

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
        ('Product', [('Explore examples', '/#examples'), ('How it works', '/#how-it-works'), ('Why Atomic', '/#foundation'), ('Pricing', '/pricing/'), ('Early access', '/early-access/')]),
        ('Solutions', [('All solutions', '/solutions/'), ('Websites', '/solutions/websites/'), ('Online stores', '/solutions/online-stores/'), ('Booking apps', '/solutions/booking-apps/'), ('Client portals', '/solutions/client-portals/'), ('Internal tools', '/solutions/internal-tools/'), ('Prototypes', '/solutions/prototypes/')]),
        ('Resources', [('Documentation', '/docs/'), ('Blog', '/blog/'), ('Press kit', '/press/'), ('Security & trust', '/security/'), ('About Atomic', '/about/'), ('Contact the team', CONTACT)]),
        ('Legal', [('Legal notice', '/legal/notice/'), ('Terms of Service', '/legal/terms/'), ('Privacy & cookies', '/legal/privacy/'), ('Customer DPA', '/legal/dpa/'), ('All legal documents', '/legal/')])
    ]
    menus = ''.join(f'<nav class="footer-column" aria-label="{title}"><h2>{title}</h2>{"".join(link(label,url) for label,url in items)}</nav>' for title, items in columns)
    return f'''<footer class="site-footer"><div class="container"><div class="footer-grid"><div class="footer-brand"><a class="brand" href="/" aria-label="Atomic home"><img class="brand-light" src="/assets/atomic-logo-lowercase-v3.svg" width="1462" height="512" alt="" /><img class="brand-dark" src="/assets/atomic-logo-lowercase-v3-dark.svg" width="1462" height="512" alt="" /></a><p>Small idea. Real possibilities.<br />Build what comes next.</p><div class="social-placeholders" role="group" aria-label="Atomic and Abstract Machines social channels">{social_links()}</div><p class="social-note">Follow Atomic and Abstract Machines</p></div>{menus}</div><div class="footer-bottom"><span>© <span id="year">2026</span> Atomic. A product by <a href="https://absmach.eu" target="_blank" rel="noopener noreferrer">Abstract Machines</a>.</span><span>Describe it. Shape it. Make it real.</span></div></div></footer>'''

def page(path, title, description, body, active='', draft=False, extra_head='', canonical='', social_card=None, lang='en'):
    folder = DIST / path
    folder.mkdir(parents=True, exist_ok=True)
    robots = '<meta name="robots" content="noindex, nofollow" />' if draft else ''
    # Pages use the shared social card unless a specific media cover is supplied.
    image_url,image_alt,image_width,image_height=social_card or (SOCIAL_IMAGE,SOCIAL_ALT,1200,630)
    if not canonical and not draft and path != '_not-found':
        canonical = f'/{path}/'
    if canonical:
        extra_head += f'<link rel="canonical" href="https://atomicapp.dev{canonical}" /><meta property="og:url" content="https://atomicapp.dev{canonical}" />'
    extra_head += f'<meta property="og:image" content="{image_url}" /><meta property="og:image:type" content="image/png" /><meta property="og:image:width" content="{image_width}" /><meta property="og:image:height" content="{image_height}" /><meta property="og:image:alt" content="{image_alt}" /><meta name="twitter:card" content="summary_large_image" /><meta name="twitter:image" content="{image_url}" /><meta name="twitter:image:alt" content="{image_alt}" />'
    robots += extra_head
    html = f'''<!doctype html><html lang="{lang}"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><meta name="theme-color" content="#191329" /><title>{escape(title)} — Atomic</title><meta name="description" content="{escape(description, quote=True)}" /><meta property="og:title" content="{escape(title, quote=True)} — Atomic" /><meta property="og:description" content="{escape(description, quote=True)}" /><meta property="og:type" content="website" />{robots}{FAVICON_LINKS}{THEME_HEAD}<link rel="preload" href="/assets/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin /><link rel="stylesheet" href="/styles.css" /><link rel="stylesheet" href="/pages.css?v=20261102-lowercase" /><link rel="stylesheet" href="/early-access.css?v=20261029-early-access-page" /><script src="/site.js?v=20261103-legal" defer></script><script src="/early-access.js?v=20261103-legal-contact" defer></script></head><body>{header(active)}<main id="main">{body}</main>{footer()}</body></html>'''
    (folder / 'index.html').write_text(html)

def hero(kicker, title, intro, center=False, extra=''):
    return f'<section class="page-hero{" center" if center else ""}"><div class="container"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{intro}</p>{extra}</div></section>'

def cta():
    return '<section class="mini-cta"><div class="container"><div><h2>Your next idea starts here.</h2><p>Tell us what you want to build with Atomic.</p></div><a class="button button-primary" href="/early-access/">Get early access <span aria-hidden="true">↗</span></a></div></section>'

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
home = re.sub(r'<link[^>]+rel="(?:icon|apple-touch-icon)"[^>]*>', '', home)
home = re.sub(r'(?m)^[ \t]+$', '', home)
home = home.replace('</head>', FAVICON_LINKS + '\n  ' + THEME_HEAD + '\n</head>')
home = re.sub(r'  <a class="skip-link".*?</header>', header('/'), home, count=1, flags=re.S)
home = re.sub(r'<footer class="site-footer">.*?</footer>', footer(), home, count=1, flags=re.S)
home = home.replace('<script src="app.js" defer></script>', '<link rel="stylesheet" href="/pages.css?v=20261102-lowercase" />\n  <script src="/site.js?v=20261103-legal" defer></script>\n  <script src="/app.js?v=20261102-lowercase" defer></script>')
home = home.replace('<script src="early-access.js" defer></script>', '<script src="/early-access.js?v=20261103-legal-contact" defer></script>')
home = home.replace('We’ll share availability and final plan details as launch approaches.', 'Explore our <a class="text-action" href="/pricing/">proposed launch plans</a>, with Free, Builder, and Pro. Subscriptions are not open yet.')
home = home.replace('<section class="faq-section', '<section class="home-pricing"><div class="container"><div><p class="eyebrow">ROOM FOR YOUR NEXT IDEA</p><h2>Start small. Build from there.</h2><p>Proposed launch plans: Free, Builder at $9/month, and Pro at $25/month. Subscriptions are not open yet.</p></div><a href="/pricing/" class="button button-secondary">Explore launch plans <span aria-hidden="true">↗</span></a></div></section>\n<section class="faq-section')
home = home.replace('Early access opens soon. Share your idea to join the waitlist.</p>', 'Early access opens soon. Share your idea to join the waitlist. <a href="/legal/privacy/">Privacy policy</a>.</p>')
(DIST / 'index.html').write_text(home)

# Pricing: agreed launch proposal; subscriptions remain closed.
plans = [
    {
        'name': 'Free', 'price': '$0', 'badge': 'Explore the idea', 'featured': False,
        'description': 'Build your first app on your own, see it working, and read its source.',
        'credits': '250', 'credit_label': 'credits to start', 'apps': '1', 'app_label': 'published app',
        'groups': [
            ('Create and refine', ['AI generation and revisions', 'Visual canvas and in-place text editing', 'Theme, typography, and layout controls', 'Screen previews and visual annotations', 'Image and design-reference uploads']),
            ('Keep and share your work', ['A backend, database, and user sign-in for every app', 'Private projects', 'Browse generated source', 'The latest version of each app, and one to go back to', 'Publish on an Atomic subdomain, with a “Made with Atomic” badge'])
        ],
        'boundary': 'Solo building · A backend for every app. The proposal reserves source downloads, searchable logs, no badge and top-ups for paid plans, and collaboration for Pro. Integrations and custom domains are planned.'
    },
    {
        'name': 'Builder', 'price': '$9', 'badge': 'Start building', 'featured': True,
        'description': 'Build and launch your own apps, and top up when you need more room.',
        'credits': '900', 'credit_label': 'credits each month', 'apps': '2', 'app_label': 'published apps',
        'groups': [
            ('Everything in Free, plus', ['Download your apps’ source', 'Searchable preview logs', 'No “Made with Atomic” badge', 'The last 100 versions of each app', 'Integrations (coming soon)']),
            ('Room to keep going', ['Up to 5 apps', '2 app previews open at once', '10 GB of storage', 'Unused credits carry over for a month', 'On-demand credit top-ups'])
        ],
        'boundary': 'Solo building. Building and metered hosting use your credits. Top-ups: $10 for 1,000 credits, used within 12 months.'
    },
    {
        'name': 'Pro', 'price': '$25', 'badge': 'Build together', 'featured': False,
        'description': 'Everything Atomic offers: build with your team, connect your own domains, and keep every version.',
        'credits': '3,000', 'credit_label': 'credits each month', 'apps': '20', 'app_label': 'published apps',
        'groups': [
            ('Everything in Builder, plus', ['Shared team workspaces', 'Unlimited invited collaborators', 'Editor and Admin collaborator roles', 'Up to 10 custom domains (planned)', 'Every version of every app, kept', 'Advanced metrics and monitoring (coming soon)', 'Single sign-on (coming soon)']),
            ('More room', ['More credits per dollar than Builder', '20 published apps at once', 'Up to 50 apps', '5 app previews open at once', '100 GB of storage'])
        ],
        'boundary': 'For teams and client work. Unused credits carry over for a month; top-ups keep the same $10 for 1,000 credits.'
    }
]
pricecards = ''
for plan in plans:
    name = plan['name']
    groups = ''.join('<section class="plan-feature-group"><h3>'+escape(title)+'</h3><ul class="plan-features">'+''.join('<li>'+escape(feature)+'</li>' for feature in features)+'</ul></section>' for title,features in plan['groups'])
    pricecards += f'''<article class="price-card{' featured' if plan['featured'] else ''}" aria-labelledby="plan-{name.lower()}">
<div class="plan-overview"><span class="pill">{plan['badge']}</span><h2 id="plan-{name.lower()}">{name}</h2><p class="plan-description">{plan['description']}</p><p class="price">{plan['price']}<small> / month</small></p><a class="button {'button-primary' if plan['featured'] else 'button-secondary'}" href="/early-access/">Ask about early access</a></div>
<dl class="plan-allowances"><div><dt>{plan['credit_label']}</dt><dd>{plan['credits']}</dd></div><div><dt>{plan['app_label']}</dt><dd>{plan['apps']}</dd></div></dl>
<div class="plan-details">{groups}<p class="plan-boundary">{plan['boundary']}</p></div></article>'''
pricing = hero('PLANS FOR WHAT COMES NEXT','A little idea.<br /><em>Room to grow.</em>','Start for free. Choose more room to build and run your apps when you need it.',True,'<span class="pill">Launch preview · Subscriptions are not open yet</span>')
pricing += f'<section class="page-section"><div class="container"><div class="price-grid">{pricecards}</div><p class="pricing-footnote">Proposed launch plans in USD, billed monthly. These are indicative service prices, not a consumer offer. The final consumer offer will display the total including applicable taxes before ordering. Free allowances and collaboration limits are subject to launch validation. Storage, bandwidth, and concurrency limits will be published before subscriptions open. No payment is collected here.</p><div class="enterprise-strip"><div><h3>Something bigger in mind?</h3><p>Tell us about your organization, deployment needs, and support requirements.</p></div><a class="text-action" href="{CONTACT}?subject=Atomic%20organization%20inquiry">Talk to the Atomic team ↗</a></div></div></section>'
comparison_rows = [
    ('Best for', 'Explore an idea on your own', 'Launch your own apps', 'Build and run apps with a team'),
    ('Credits', '250 once', '900 each month', '3,000 each month'),
    ('Unused plan credits', 'Given once', 'Carry over one month', 'Carry over one month'),
    ('Published apps at once', '1', '2', '20'),
    ('Invited collaborators per app', 'Not included', 'Not included', 'Unlimited'),
    ('Editor and Admin collaborator roles', 'Not included', 'Not included', 'Included'),
    ('Shared workspaces and team collaboration', 'Not included', 'Not included', 'Included'),
    ('Custom domains (planned)', 'Atomic subdomain only', 'Atomic subdomain only', 'Planned: up to 10'),
    ('“Made with Atomic” badge on published apps', 'Shown', 'Removed', 'Removed'),
    ('Apps', 'Up to 3', 'Up to 5', 'Up to 50'),
    ('App previews open at once', '1', '2', '5'),
    ('Storage', '2 GB', '10 GB', '100 GB'),
    ('AI generation and revisions', 'Full app', 'Full app', 'Full app'),
    ('Visual canvas, text edits, and theme controls', 'Included', 'Included', 'Included'),
    ('Screen previews and visual annotations', 'Included', 'Included', 'Included'),
    ('Image and design-reference uploads', 'Included', 'Included', 'Included'),
    ('App backend, database, and user authentication', 'Every app', 'Every app', 'Every app'),
    ('App-user access controls', 'Every app', 'Every app', 'Every app'),
    ('Deployment history and frontend rollback', 'Included', 'Included', 'Included'),
    ('Searchable preview logs', 'Not included', 'Included', 'Included'),
    ('Private projects and source browsing', 'Included', 'Included', 'Included'),
    ('Download your app’s source', 'Not included', 'Included', 'Included'),
    ('Integrations', 'Not included', 'Coming soon', 'Coming soon'),
    ('Advanced metrics and monitoring', 'Not included', 'Not included', 'Coming soon'),
    ('Single sign-on (SSO)', 'Not included', 'Not included', 'Coming soon'),
    ('Version history and source restore', 'Latest version and one to go back to', 'Last 100 versions', 'Every version'),
    ('Per-app build and usage history', 'Included', 'Included', 'Included'),
    ('Hosting and persistent storage', 'Uses available credits', 'Uses available credits', 'Uses available credits'),
    ('Buy additional credits', 'Upgrade to a paid plan', '$10 for 1,000 credits, used within 12 months', '$10 for 1,000 credits, used within 12 months')
]
comparison = ''.join('<tr><th scope="row">'+label+'</th>'+''.join('<td>'+value+'</td>' for value in values)+'</tr>' for label,*values in comparison_rows)
pricing += '<section class="page-section"><div class="container"><div class="section-intro"><div><p class="eyebrow">WHAT YOUR PLAN MAKES POSSIBLE</p><h2>Start with one app. Grow into many.</h2></div><p>Free gives you visual editing, version history, source browsing, and a backend with user sign-in for every app, to build on your own. Builder adds source downloads, searchable logs and room for a couple of live apps, for building on your own. Pro adds team collaboration, custom domains (planned), every version kept, and more credits for each dollar.</p></div><div class="table-wrap pricing-comparison" role="region" aria-label="Compare launch plan features" tabindex="0"><table><caption>Proposed launch features. On small screens, scroll horizontally to compare plans.</caption><thead><tr><th scope="col">What you get</th><th scope="col">Free · $0/month</th><th scope="col">Builder · $9/month</th><th scope="col">Pro · $25/month</th></tr></thead><tbody>'+comparison+'</tbody></table></div><p class="pricing-footnote">Collaborator limits are proposed and count people invited to an app, excluding its owner. They are not limits on the people using your finished app. Shared workspaces and collaboration require Pro; workspace membership is separate from the per-app collaborator limit. Building by collaborators uses the app owner’s credits. A source download includes code, not app users or business data; version restore changes code, not data. Custom domains are planned and are not available in the current early-access interface. Domain registration will be purchased separately.</p></div></section>'
pricing += '<section class="page-section"><div class="container"><div class="section-intro"><h2>One credit value. Every plan.</h2><p><strong>100 credits = $1 of Atomic usage.</strong> Credits pay for building and running your apps at Atomic’s usage rates. The same work uses the same credits on every plan; charges can be fractional, based on the resources used. For example, 15 credits means $0.15 of Atomic usage. A credit is not a message or a completed app.</p></div><div class="resource-grid">'+card('01 / BUILD','Shape your app.','AI generation, revisions, suggestions, dictation, and the build environment draw from your credits. A small change can use less than a complex build.','/docs/usage-and-credits/','Understand your usage')+card('02 / RUN','Give it a home.','Metered app hosting and persistent storage use credits too. Published-app slots are capacity limits, not unlimited hosting. A protected hosting budget is planned so building cannot spend the credits you set aside to run your apps.','/docs/publishing/','Prepare to publish')+card('03 / TOP UP','More room when you need it.','On Builder and Pro, add 1,000 credits for $10. Bought credits last 12 months and are used after your monthly allowance. No automatic overage charges.','/pricing/#credit-rules','Read the credit rules')+'</div></div></section>'
pricing += '<section id="credit-rules" class="page-section"><div class="container faq-layout"><div><p class="eyebrow">A FEW PRACTICAL DETAILS</p><h2>Before you choose.</h2></div><div class="faq-list">'
for q,a in [
    ('Can I subscribe today?','Not yet. These are proposed launch plans. The early-access form adds you to the waitlist; it does not create an account, reserve a price, or start a subscription.'),
    ('What is included in the subscription?','Builder includes 900 monthly credits, up to 5 apps and 2 published apps for $9/month, for building on your own. Pro includes 3,000 monthly credits, up to 50 apps and 20 published apps for $25/month, with team collaboration: shared workspaces and unlimited invited collaborators with Editor and Admin roles, building with the app owner’s credits. Custom domains are planned for Pro. Both include a backend, database, user authentication, private projects, source downloads and searchable logs under the proposed offer. Your subscription pays for the platform as well as the included usage.'),
    ('How does Free work?','The proposed Free plan gives you 250 credits once; they do not renew each month. Build on your own and publish one app on an Atomic subdomain, with a small “Made with Atomic” badge. Every app can have a backend, database, and user sign-in. You can browse your apps’ source; downloading it, searchable logs, removing the badge and credit purchases require Builder or Pro; collaboration and custom domains require Pro. When all 250 are used, upgrade to keep building.'),
    ('Do unused credits expire?','Unused monthly credits carry over into the next month, then expire; the oldest are always used first. Bought top-up credits last 12 months from purchase and are used after your monthly credits. Carried-over credits end if you move back to Free. Free’s 250 credits are given once and do not renew.'),
    ('Is hosting included?','Your included credits can pay for metered hosting and persistent storage. Hosting is not unlimited, and storage can still cost credits when an app is stopped. We plan to let you protect part of your balance for hosting. Storage, bandwidth, concurrency limits, and hosting exhaustion and retention rules will be published before billing opens.'),
    ('What happens when my credits run out?','There are no automatic overage charges. New builds require enough available credits. On Free, upgrade once all 250 are used. On Builder and Pro, you can buy 1,000 more credits for $10 or wait for your monthly allowance to renew. Hosting suspension, restart, retention and warning arrangements will be stated in the final offer before billing opens. The planned hosting-budget control will let you set aside credits that building cannot spend.'),
    ('Will there be annual billing?','The launch proposal is monthly billing only. Annual plans and discounts have not been announced.'),
    ('What happens if I cancel?','Cancellation, data retention, export access, and the behavior of published apps will be specified in the final subscription terms before checkout becomes available.')]:
    pricing += f'<details><summary>{q}</summary><p>{a}</p></details>'
pricing += '</div></div></section>'+cta()
page('pricing','Pricing','Explore Atomic’s launch plans: Free, Builder at $9/month with 900 credits, and Pro at $25/month with 3,000 credits. Paid-plan top-ups: $10 for 1,000 credits.',pricing,'/pricing/')

# Early access: a page of its own for sharing; early-access.js puts the wizard in the card.
access = '<section class="access-page"><div class="container access-page-layout"><div class="access-page-intro"><p class="eyebrow">EARLY ACCESS</p><h1>Your idea,<br /><em>first in line.</em></h1><p class="lead">Atomic is preparing for early access. Tell us what you want to build, and we’ll invite shortlisted applicants to the free trial.</p></div>'
access += '<div id="access-page" class="access-wizard access-card"><noscript><p>Enable JavaScript to request early access, or email <a href="mailto:info@absmach.eu?subject=Atomic%20early%20access">info@absmach.eu</a>.</p></noscript></div>'
access += '<ol class="access-next" aria-label="What happens next"><li><span><strong>Share your idea.</strong>Three short steps: your idea, a little about you, and where to reach you.</span></li><li><span><strong>We review requests.</strong>We look at what people want to build and who it’s for.</span></li><li><span><strong>Shortlisted applicants hear from us.</strong>We email an invitation to the free trial.</span></li></ol></div></section>'
page('early-access','Request early access','Tell us what you want to build with Atomic and request a place in the early-access free trial.',access,canonical='/early-access/')

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
        guide('custom-domains', 'DOMAINS', 'Publishing', 'Custom domains', 'Custom-domain availability and your current published address.',
              'Custom-domain connection is planned. Publish to the Atomic address shown in your Dashboard for now.'),
        guide('deployments', 'DEPLOYMENTS', 'Publishing', 'Deployments and rollback', 'See what is live and serve an earlier release again.',
              'Review retained publications, see what is live, and serve an eligible earlier release again.'),
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
        guide('usage-and-credits', 'USAGE', 'Usage', 'Usage and credits', 'Current usage and the proposed credit offer.',
              'Review model usage, current allowances and the separate credit-based launch proposal.'),
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
docs += '<section class="page-section"><div class="container">'+'<div class="search-field"><label for="guide-search">Find a guide</label><input id="guide-search" type="search" placeholder="Try “source” or “publish”" aria-describedby="search-status" /></div><p id="search-status" class="search-status" role="status" aria-live="polite">'+f'{len(GUIDES)} guides available</p>'
for key, name, blurb, guides in DOCS:
    docs += f'<section class="docs-group" id="{key}" data-guide-group aria-labelledby="{key}-title"><div class="docs-group-intro"><h2 id="{key}-title">{name}</h2><p>{blurb}</p></div><div class="resource-grid two-cols">' + ''.join(card(g['kicker'], g['title'], g['summary'], f'/docs/{g["slug"]}/', guide=True, level=3) for g in guides) + '</div></section>'
docs += '</div></section>'+cta()
page('docs','Documentation','Learn how to describe, shape, review, and prepare an app with Atomic.',docs,'/docs/')
for index in range(len(GUIDES)):
    guide_page(index)

POSTS = [
    ('BUILDING USEFUL SOFTWARE','Start with one useful thing','A smaller first version makes it easier to discover what your business actually needs.','/blog/start-with-one-useful-thing/','One task.<br />Done well.'),
    ('THE ATOMIC APPROACH','Your app is more than its interface','Why identity, data, permissions, and source access belong in the conversation from the beginning.','/blog/more-than-an-interface/','Beyond<br />the screen.')
]
blog = hero('THE ATOMIC BLOG','Notes on making<br /><em>ideas real.</em>','Thoughts on useful software, small beginnings, and building with a foundation you can understand.')
blog += '<section class="page-section"><div class="container"><div class="resource-grid two-cols">'
for tag,title,desc,url,cover in POSTS:
    blog += f'<a class="resource-card article-card" href="{url}"><div class="article-cover" aria-hidden="true">{cover}</div><div class="article-copy"><p class="eyebrow">{tag}</p><h2>{title}</h2><p>{desc}</p><span class="card-link">Read the story <span aria-hidden="true">↗</span></span></div></a>'
blog += '</div></div></section>'+cta()
page('blog','Blog','Field notes from Atomic on useful software, building apps, and turning ideas into something real.',blog,'/blog/')
article('blog/start-with-one-useful-thing','Start with one useful thing','Your first app does not have to run your whole business. It needs to make one part of it easier.',[
    ('friction','Start where the friction is','<p>A studio owner answers the same scheduling questions every week. A small shop shares product details across a string of messages. A freelancer sends another email explaining where a project stands.</p><p>Each is a modest problem with a recognizable cost: time, attention, or uncertainty. Each is also a useful starting point for an app.</p>'),
    ('small','Make the first version small','<p>It is tempting to add a dashboard, notifications, payments, and a loyalty program before anyone has tried the main workflow. But each addition introduces another decision and another way for the experience to become confusing.</p><p>For a booking app, the first useful version might let someone choose a service and request a time, then let the owner confirm it. That is enough to ask whether the app makes the exchange clearer.</p>'),
    ('learn','Use the app to learn','<p>Show the first version to someone who would use it. Ask them to complete the task without explaining every screen. Notice where they hesitate and which information they look for.</p><p>The next improvement may be a better label or a clearer confirmation, not a new feature. A narrow first version makes those observations easier to act on.</p>'),
    ('atomic','Bring that focus to Atomic','<p>Atomic starts with a description of what you want to build. The more clearly you can explain the person, the task, and the result, the better a starting point you have for reviewing the app.</p><p>Think of your first brief as a hypothesis: this small piece of software will make this particular job easier. Build enough to try it, then decide what comes next.</p><p><a href="/docs/getting-started/">Write your first app brief →</a></p>')
],category='Field notes',active='/blog/',meta='Atomic · Product perspective · 3 min read')
article('blog/more-than-an-interface','Your app is more than its interface','The screen is what people see. The foundation determines what they can safely do.',[
    ('screen','A good screen is the beginning','<p>A booking form can look finished before it answers the most important questions. Where does the request go? Who can change it? Can another customer see it? What happens when the owner confirms?</p><p>These questions turn a collection of screens into an application. They are part of the product experience, even when users never see the machinery underneath.</p>'),
    ('foundation','Identity, data, and permissions','<p>Atomic uses Atom as its open-source backend foundation. Identity establishes who is using an app. Data holds the records that make it useful. Permissions determine who can read and change them.</p><p>Those pieces still need careful configuration and testing. An open-source foundation gives you code you can inspect; it is not a substitute for checking the behavior of your particular application.</p>'),
    ('control','Keep the boundaries visible','<p>Source access is another part of that foundation. Browsing generated code helps you understand what was built. Source downloads, included in the proposed paid plans, let you keep a copy of your work.</p><p>But source is not customer data, and neither is hosting. Atomic treats those as distinct concerns. Broader packaging and deployment options remain on the roadmap; we want the current boundaries to be clear while that work develops.</p>'),
    ('build','Build with the whole app in mind','<p>When you describe an app, include who uses it, which records they work with, and what each person may do. When you review it, test those relationships as carefully as the layout.</p><p>The ambition is simple: useful software that looks good, behaves clearly, and gives you a foundation you can understand.</p><p><a href="/docs/source-and-data/">Read about source, data, and hosting →</a></p>')
],category='Field notes',active='/blog/',meta='Atomic · Product perspective · 3 min read')

security = hero('SECURITY & TRUST','Build with<br /><em>your eyes open.</em>','Understand the foundation, know the boundaries, and bring the right checks to every app you publish.')
security += '<section class="page-section"><div class="container"><div class="resource-grid">'+card('FOUNDATION','Identity & permissions','Atom provides the backend foundation. Each generated app still needs its access rules reviewed and tested.','/docs/publishing/','Review before publishing')+card('VISIBILITY','Source you can inspect','Browse generated source; downloads are included in the proposed paid plans. Data records, infrastructure, and source history remain separate concerns.','/docs/source-and-data/','Understand the boundaries')+card('DATA','Clear responsibilities','The website privacy notice and customer DPA explain the split between Atomic’s service and your own app.','/legal/','Read the legal documents')+'</div></div></section>'
security += '<section class="page-section"><div class="container"><div class="notice"><strong>Security information for early access</strong>We are preparing the operational security documentation. This page does not assert a certification, compliance status, uptime guarantee, data-residency commitment, or completed independent audit.</div><div class="section-intro"><h2>Report a security concern.</h2><p>If you find a potential vulnerability, send the affected page, steps to reproduce, and the likely impact. Avoid including secrets or other people’s personal data.</p></div><a class="button button-secondary" href="mailto:info@absmach.eu?subject=Atomic%20security%20report">Contact the Atomic team ↗</a></div></section>'
page('security','Security & trust','Understand Atomic’s security boundaries, data responsibilities, and security reporting contact.',security)

# Company context supports the product; sources are linked in the page.
about = hero('ABOUT ATOMIC','Good ideas deserve<br /><em>a way forward.</em>','We’re building Atomic for the moment you know what your business needs—and want to make it real.')
about += '''<section class="page-section"><div class="container about-intro"><h2>Useful software starts<br />with your world.</h2><div class="prose"><p>A studio that needs a better way to take bookings. A small brand ready for its first shop. A team that wants to keep clients in the loop. The people closest to a business often know exactly what would make it work better.</p><p>Atomic gives those ideas a place to take shape: describe the app, refine it in conversation, review the result, and prepare it for the people who will use it.</p></div></div></section>
<section class="page-section"><div class="container"><div class="resource-banner about-company"><div><p class="eyebrow">THE TEAM BEHIND THE PRODUCT</p><h2>Built by<br />Abstract Machines.</h2><p>Atomic is a product of Abstract Machines, an open-source infrastructure company based in Paris. The team’s work spans identity, messaging, connected systems, and edge computing.</p><a class="button button-light" href="https://www.absmach.eu/" target="_blank" rel="noopener noreferrer">Meet Abstract Machines <span aria-hidden="true">↗</span></a></div><div class="about-evidence"><div><span class="eyebrow">01 / THE FOUNDATION</span><h3>We build the layers underneath.</h3><p>The same company develops Atom, the open-source identity and authorization foundation used by Atomic.</p><a href="https://www.absmach.eu/products/atom/" target="_blank" rel="noopener noreferrer">Explore Atom <span aria-hidden="true">↗</span></a></div><div><span class="eyebrow">02 / WORK YOU CAN EXPLORE</span><h3>A practice of building openly.</h3><p>Explore Abstract Machines’ public repositories to see its open-source work, development history, and contributions.</p><a href="https://github.com/absmach" target="_blank" rel="noopener noreferrer">Browse the open-source projects <span aria-hidden="true">↗</span></a></div></div></div></div></section>
<section class="page-section"><div class="container"><div class="section-intro"><h2>What matters to us.</h2></div><div class="about-principles"><article><span class="eyebrow">01 / USEFULNESS</span><h3>Start with a real task.</h3><p>A good app helps someone do something that matters. We start with the workflow and shape the experience around it.</p></article><article><span class="eyebrow">02 / VISIBILITY</span><h3>Understand what you build.</h3><p>Previews, source access, and clear product boundaries help you review your app and make informed decisions.</p></article><article><span class="eyebrow">03 / CONTROL</span><h3>Keep a hand in the process.</h3><p>Describe the direction, inspect the result, and choose what to publish. Your judgment belongs in every step.</p></article></div></div></section>'''+cta()
page('about','About Atomic','Meet Atomic and Abstract Machines, the open-source infrastructure company behind the product.',about,'/about/')

# Public legal copy and translations; operational evidence remains in private/legal/.
from legal_content import render_legal_pages
render_legal_pages(page, hero)

# Useful fallback for hosts that support a static 404 document.
page('_not-found','Page not found','Find your way back to Atomic.',hero('404 / A SMALL DETOUR','This idea isn’t here.<br /><em>Let’s find another.</em>','The page may have moved. Explore the product, browse the docs, or head back to the beginning.')+'<section class="page-section"><div class="container"><a class="button button-primary" href="/">Back to Atomic</a> <a class="button button-secondary" href="/docs/">Explore the docs</a></div></section>')
(DIST / '404.html').write_text((DIST / '_not-found/index.html').read_text())
(DIST / '_not-found/index.html').unlink()
(DIST / '_not-found').rmdir()
render_solutions(page)
# The approved press index is maintained as content, with compact local previews.
press_content=(ROOT/'content/press.html').read_text()
press_cover=re.search(r'href="([^"]*/06-social/atomic-launch-widescreen-cover\.png)"',press_content)
if not press_cover:raise ValueError('The press page needs its matching widescreen cover.')
page('press','Press kit','Read the Atomic press book and download product information, editorial documents, screenshots, logos and launch films.',press_content,extra_head='<link rel="stylesheet" href="/press.css?v=20261103-monochrome" />',social_card=('https://atomicapp.dev'+press_cover[1],'Atomic — Big idea? Make it real.',1920,1080))
print(f'Generated {len(list(DIST.rglob("*.html")))} HTML pages.')
