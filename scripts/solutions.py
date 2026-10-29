"""Reusable, build-time solutions page family; no runtime dependencies."""
import json
from html import escape
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS = json.loads((ROOT / 'content/solutions.json').read_text())
# Early-access phase: keep the primary CTA consistent across the page family.
# Once Atomic is live, replace the hub label/destination with the launch flow
# and use each solution's preserved `cta` wording from content/solutions.json.
EARLY_ACCESS_CTA = 'Request Early Access'


def start_url(prompt):
    return '/?' + urlencode({'idea': prompt}) + '#early-access'


def photo(name, alt='', eager=False):
    sizes = {'architecture': (1100, 760), 'ceramics': (700, 760)}
    width, height = sizes[name]
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="/assets/solutions/{name}.jpg" width="{width}" height="{height}" alt="{alt}" {loading} />'


def artwork(kind, eager=False):
    """Non-interactive app illustrations, intentionally no pretend controls."""
    if kind == 'website':
        body = f'''<div class="mock-site-nav"><strong>form &amp; field<span>ARCHITECTURE STUDIO</span></strong><span>Work &nbsp; Studio &nbsp; Contact ↗</span></div><div class="mock-site-heading"><span>SPACES FOR LIVING</span><div>Considered spaces.<br />Extraordinary everyday.</div></div>{photo('architecture', eager=eager)}<div class="mock-photo-caption"><span>01 / Selected work</span><span>Form. Light. Possibility.</span></div>'''
    elif kind == 'store':
        body = f'''<div class="mock-site-nav"><strong>slow objects.</strong><span>Collection &nbsp; Our story &nbsp; Bag (2)</span></div><div class="mock-shop-layout"><div><span>MADE TO BE KEPT</span><div class="mock-serif">A little less.<br />A little better.</div><p>Thoughtful objects for everyday rituals.</p><span class="mock-action">Explore the collection ↗</span></div>{photo('ceramics', eager=eager)}</div><div class="mock-product-strip"><span>Small-batch ceramics</span><span>Natural materials</span><span>Made with intention</span></div>'''
    elif kind == 'booking':
        body = f'''<div class="mock-site-nav"><strong>still studio<span>A LITTLE TIME FOR YOU</span></strong><span>Your appointments &nbsp; My account</span></div><div class="mock-booking-layout"><div class="mock-booking-intro">{photo('ceramics', eager=eager)}<div>A moment<br />to make.</div></div><div class="mock-booking-form"><span>01 / YOUR SESSION</span><div class="mock-title">Find your next<br />creative moment.</div><div class="mock-service"><strong>Introduction to pottery</strong><span>90 min · Small group</span><b>Selected ✓</b></div><p>Choose a session</p><div class="mock-dates"><span>THU<b>22</b></span><span class="chosen">FRI<b>23</b></span><span>SAT<b>24</b></span></div><div class="mock-times"><span>10:00 AM</span><span>2:00 PM</span></div><span class="mock-action">Request this session ↗</span></div></div>'''
    elif kind == 'portal':
        body = f'''<div class="mock-site-nav"><strong>form &amp; field<span>CLIENT WORKSPACE</span></strong><span>Overview &nbsp; Projects &nbsp; <b class="mock-avatar">JL</b></span></div><div class="mock-dashboard"><span>YOUR PROJECT, TAKING SHAPE</span><div class="mock-title">Good morning, Jamie.</div><p>Here’s where we are with your new space.</p><div class="mock-project">{photo('architecture', eager=eager)}<div><span>RESIDENTIAL / 2026</span><strong>The courtyard house</strong><span class="mock-badge">Design development</span></div></div><div class="mock-milestones"><span class="complete">✓<small>Discovery</small></span><i></i><span class="complete">✓<small>Concept</small></span><i></i><span class="current">3<small>Design</small></span><i></i><span>4<small>Handover</small></span></div><div class="mock-update"><span class="mock-avatar">AF</span><div><strong>A new chapter for your courtyard.</strong><p>Your design update is ready to review.</p></div><span>Today</span></div></div>'''
    elif kind == 'internal':
        columns = [('New leads', [('Northstar Studio', 'Website redesign', '$4,800'), ('Bloom & Co.', 'Brand identity', '$3,200')]), ('In conversation', [('Kinfolk Coffee', 'Online storefront', '$6,400'), ('Paper House', 'Client workspace', '$5,200')]), ('Proposal sent', [('Fieldwork', 'Booking platform', '$8,500')])]
        board = ''.join('<div class="mock-board-column"><div class="mock-column-title">'+title+f'<span>{len(items)}</span></div>'+''.join(f'<div class="mock-deal"><span>{desc}</span><strong>{name}</strong><div><b>{price}</b><span class="mock-avatar">{name[0]}{name.split()[-1][0]}</span></div></div>' for name, desc, price in items)+'</div>' for title, items in columns)
        body = f'''<div class="mock-site-nav"><strong><span class="mock-logo-dot"></span> pipeline</strong><span>Workspace &nbsp; <b class="mock-avatar">AT</b></span></div><div class="mock-dashboard"><span>A CLEARER VIEW OF WHAT’S NEXT</span><div class="mock-title">Your team’s next big thing.</div><div class="mock-metrics"><div><span>Open opportunities</span><strong>12</strong></div><div><span>Pipeline value</span><strong>$42,800</strong></div><div><span>Follow-ups today</span><strong>4</strong></div></div><div class="mock-board">{board}</div></div>'''
    else:
        body = '''<div class="mock-site-nav"><strong>gather<span>GOOD COMPANY, CLOSE BY</span></strong><span>Discover &nbsp; My events &nbsp; <b class="mock-avatar">SK</b></span></div><div class="mock-prototype-body"><span>MAKE ROOM FOR SOMETHING GOOD</span><div class="mock-title">Your kind of people.<br />Your next good plan.</div><div class="mock-event"><div class="mock-event-art"><span>THE<br />CREATIVE<br />TABLE.</span><i>↗</i></div><div><span>FRIDAY / 6:00 PM</span><strong>A little making.<br />A lot of good company.</strong><p>A hands-on evening for curious minds.</p><span class="mock-action">Join the gathering ↗</span></div></div><div class="mock-prototype-note"><span>✳</span><span>“Let’s make the RSVP flow one step simpler.”<small>Design feedback / Round 02</small></span></div></div>'''
    return f'<div class="app-mock mock-{kind}" aria-hidden="true"><div class="mock-browser"><span><i></i><i></i><i></i></span><span>Preview / Sample app</span><span>↗</span></div>{body}</div>'


def solution_card(item):
    return f'''<a class="solution-card" href="/solutions/{item['slug']}/" data-solution-category="{item['category']}"><div class="solution-card-art art-{item['art']}">{artwork(item['art'])}</div><div class="solution-card-copy"><p class="eyebrow">{item['label']}</p><h3>{item['name']} <span aria-hidden="true">↗</span></h3><p>{item['summary']}</p><span class="solution-card-link">Explore {item['name'].lower()} <span aria-hidden="true">→</span></span></div></a>'''


def benefits(title, intro, items):
    cards = ''.join(f'<article><span class="benefit-number">0{i}</span><h3>{heading}</h3><p>{text}</p></article>' for i, (heading, text) in enumerate(items, 1))
    return f'<section class="solution-section"><div class="container"><div class="solution-section-heading"><p class="eyebrow">MADE FOR THE WAY YOU BUILD</p><h2>{title}</h2><p>{intro}</p></div><div class="solution-benefits">{cards}</div></div></section>'


def closing(item=None):
    placeholder = item['prompts'][0][1] if item else 'A booking app for my studio, a portal for my clients, a new idea for my team…'
    return f'''<section class="solution-closing"><div class="container"><div><p class="eyebrow">YOUR IDEA GOES HERE</p><h2>What could you<br /><em>make possible?</em></h2><p>Start with something you wish existed.<br />Tell us about it to request early access.</p></div><form action="/early-access/" method="get" class="solution-idea-form"><label for="solution-idea">What would you like to build?</label><textarea id="solution-idea" name="idea" rows="4" maxlength="1200" placeholder="{escape(placeholder, quote=True)}"></textarea><button class="button button-primary" type="submit">{EARLY_ACCESS_CTA} <span aria-hidden="true">↗</span></button><p>We’re preparing for launch. Three short steps to request early access. <a href="/legal/privacy/">Privacy policy</a>.</p></form></div></section>'''


def render_solutions(page):
    head = '<link rel="stylesheet" href="/solutions.css" /><script src="/solutions.js" defer></script>'
    hub = f'''<section class="solutions-hero"><div class="container"><p class="eyebrow">SMALL IDEA. REAL POSSIBILITIES.</p><h1>What if you<br /><em>just built it?</em></h1><p class="solutions-lead">The website you’ve been putting off. The tool your team needs.<br class="desktop-break" /> The business you can’t stop thinking about. Start with Atomic.</p><div class="solution-actions"><a class="button button-primary" href="/early-access/">{EARLY_ACCESS_CTA} <span aria-hidden="true">↗</span></a><a class="button button-secondary" href="#explore">Find your starting point <span aria-hidden="true">↓</span></a></div><div class="solution-hero-collage">'''
    hub += '<div class="collage-store">'+artwork('store', True)+'</div><div class="collage-site">'+artwork('website', True)+'</div><div class="collage-portal">'+artwork('portal')+'</div><span class="collage-prompt" aria-hidden="true"><img src="/assets/atomic.svg" width="24" height="24" alt="" /> “Make it feel a little more like us.” <span>↗</span></span></div><p class="illustration-caption">Illustrative app concepts · Sample content</p></div></section>'
    filters = ''.join(f'<button type="button" data-solution-filter="{value}" aria-pressed="{str(value == "all").lower()}">{label}</button>' for value, label in [('all', 'All possibilities'), ('business', 'My business'), ('clients', 'My clients'), ('teams', 'My team')])
    hub += f'''<section class="solution-section solution-explore" id="explore"><div class="container"><div class="solution-section-heading split"><div><p class="eyebrow">FIND YOUR STARTING POINT</p><h2>A useful little app.<br />Or your next big thing.</h2></div><p>Pick something you want to make better.<br />We’ll help you see what it could become.</p></div><div class="solution-filters" role="group" aria-label="Filter solutions by audience" hidden>{filters}</div><p class="sr-only" id="solution-filter-status" role="status" aria-live="polite"></p><div class="solutions-grid">{''.join(solution_card(item) for item in SOLUTIONS)}</div></div></section>'''
    hub += benefits('One place to make it happen.', 'Different ideas. The same way to bring them to life: describe, shape, try, and publish.', [('Start with your words', 'Describe what you want to build, or begin with a template. Bring a reference to give your idea a direction.'), ('Shape it as you see it', 'Edit text, change the theme, and annotate the canvas. Try screens and roles before asking for the next change.'), ('Build on a real foundation', 'Add data and accounts on paid plans, check your build, and publish. Browse and download your generated source.')])
    hub += '<div class="container solution-plan-note"><span>✳</span><p>Start with a frontend. Add a backend, database, and user accounts on the proposed Builder and Pro plans. <a href="/pricing/">Explore launch plans ↗</a></p></div>' + closing()
    page('solutions', 'Solutions · What will you build?', 'Explore what you can build with Atomic: websites, online stores, booking apps, client portals, internal tools, and prototypes. Start with your idea.', hub, '/solutions/', extra_head=head, canonical='/solutions/')
    by_slug = {item['slug']: item for item in SOLUTIONS}
    for item in SOLUTIONS:
        url = '/solutions/' + item['slug'] + '/'
        crumb = f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/solutions/">Solutions</a><span aria-hidden="true">/</span><span aria-current="page">{item["name"]}</span></nav>'
        body = f'''<section class="solution-detail-hero"><div class="container">{crumb}<div class="solution-hero-columns"><div><p class="eyebrow">{item['name'].upper()} WITH ATOMIC</p><h1>{item['title']}</h1><p class="solutions-lead">{item['intro']}</p><div class="solution-actions"><a class="button button-primary" href="/early-access/">{EARLY_ACCESS_CTA} <span aria-hidden="true">↗</span></a><a class="solution-secondary-link" href="#starting-ideas">See starting ideas ↓</a></div><p class="solution-access-note">Made for your idea. Preparing for early access.</p></div><figure class="solution-detail-visual art-{item['art']}">{artwork(item['art'], True)}<figcaption>{item['sample']}<span>Illustrative concept · Sample data</span></figcaption></figure></div></div></section>'''
        body += benefits(item['benefit_title'], item['benefit_intro'], item['benefits'])
        prompts = ''.join(f'<a class="solution-prompt" href="{escape(start_url(prompt), quote=True)}"><span class="eyebrow">0{i} / {label}</span><h3>{label}</h3><p>“{prompt}”</p><span class="solution-card-link">Start with this idea <span aria-hidden="true">↗</span></span></a>' for i, (label, prompt) in enumerate(item['prompts'], 1))
        body += f'<section class="solution-section solution-starting" id="starting-ideas"><div class="container"><div class="solution-section-heading"><p class="eyebrow">A FEW IDEAS TO GET YOU GOING</p><h2>Start with a “what if”.</h2><p>Use one of these as a brief, then make it yours on the homepage.</p></div><div class="solution-prompts">{prompts}</div></div></section>'
        steps = ''.join(f'<li><span class="eyebrow">0{i}</span><h3>{heading}</h3><p>{text}</p></li>' for i, (heading, text) in enumerate(zip(['Describe the idea.', 'Make it your own.', 'Check it. Share it.'], item['workflow']), 1))
        body += f'<section class="solution-section"><div class="container"><div class="solution-section-heading split"><div><p class="eyebrow">FROM FIRST THOUGHT TO NEXT STEP</p><h2>Your idea, taking shape.</h2></div><a class="solution-secondary-link" href="/docs/{item["guide"]}/">{item["guide_label"]} ↗</a></div><ol class="solution-workflow">{steps}</ol><p class="solution-workflow-note">Backend, database, authentication, custom domains, and collaboration are part of the proposed paid plans. <a href="/pricing/">See launch plans.</a></p></div></section>'
        questions = ''.join(f'<details><summary>{question}</summary><p>{answer}</p></details>' for question, answer in item['faqs'])
        body += f'<section class="solution-section solution-faq"><div class="container"><div class="solution-section-heading"><p class="eyebrow">BEFORE YOU BEGIN</p><h2>A few things you might be wondering.</h2><p>About building {item["name"].lower()} with Atomic.</p></div><div class="faq-list">{questions}</div></div></section>'
        related = ''.join(f'<a href="/solutions/{slug}/"><span>{by_slug[slug]["name"]}</span><span aria-hidden="true">↗</span></a>' for slug in item['related'])
        body += '<section class="solution-section solution-related"><div class="container"><div class="solution-section-heading split"><h2>More possibilities.</h2><a class="solution-secondary-link" href="/solutions/">Explore all solutions ↗</a></div><nav aria-label="Related solutions">'+related+'</nav></div></section>' + closing(item)
        page('solutions/'+item['slug'], item['name']+' · '+{'websites':'AI website builder','online-stores':'AI storefront builder','booking-apps':'AI booking app builder','client-portals':'AI client portal builder','internal-tools':'AI internal tool builder','prototypes':'AI prototype builder'}[item['slug']], item['description'], body, url, extra_head=head, canonical=url)
