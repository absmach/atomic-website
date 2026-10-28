// Shared navigation for all pages; product demos live in app.js.
const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.getElementById('mobile-nav');
function closeMenu() {
  mobileNav.hidden = true;
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Open navigation');
}
menuButton.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  mobileNav.hidden = !open;
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileNav.hidden) { closeMenu(); menuButton.focus(); }
});
window.matchMedia('(min-width: 961px)').addEventListener('change', event => { if (event.matches) closeMenu(); });
document.getElementById('year').textContent = new Date().getFullYear();

const search = document.getElementById('guide-search');
if (search) {
  const cards = [...document.querySelectorAll('[data-guide]')];
  const groups = [...document.querySelectorAll('[data-guide-group]')];
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    cards.forEach(card => { card.hidden = !card.textContent.toLowerCase().includes(query); });
    // A section whose guides all miss hides with its heading.
    groups.forEach(group => { group.hidden = !group.querySelector('[data-guide]:not([hidden])'); });
    const count = cards.filter(card => !card.hidden).length;
    document.getElementById('search-status').textContent = count ? `${count} guide${count === 1 ? '' : 's'} available` : 'No matching guides. Try “source”, “publish”, or “idea”.';
  });
}

// The docs menu scrolls on its own on wide screens. Keep it where the reader
// left it when they follow one of its links, and otherwise bring the current
// guide into view, so the next guide is a click away rather than a scroll.
const docsNav = document.querySelector('.docs-nav');
if (docsNav) {
  const key = 'atomic-docs-nav-scroll';
  docsNav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    try { sessionStorage.setItem(key, String(docsNav.scrollTop)); } catch {}
  }));
  if (docsNav.scrollHeight > docsNav.clientHeight) {
    let saved = null;
    try { saved = sessionStorage.getItem(key); sessionStorage.removeItem(key); } catch {}
    const current = docsNav.querySelector('[aria-current="page"]');
    if (saved !== null) docsNav.scrollTop = Number(saved);
    if (current) {
      const top = current.offsetTop, bottom = top + current.offsetHeight;
      if (saved === null || top < docsNav.scrollTop || bottom > docsNav.scrollTop + docsNav.clientHeight)
        docsNav.scrollTop = top - (docsNav.clientHeight - current.offsetHeight) / 2;
    }
  }
}


// Privacy-first marketing tags. GTM is loaded only after optional consent.
(() => {
  const KEY = 'atomic-cookie-consent-v1';
  const ID = 'GTM-NDHNWJMJ';
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('consent', 'default', {
    analytics_storage: 'denied', ad_storage: 'denied',
    ad_user_data: 'denied', ad_personalization: 'denied',
    functionality_storage: 'granted', security_storage: 'granted',
    wait_for_update: 500
  });
  let saved = null;
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY));
    if (parsed && parsed.version === 1 && typeof parsed.analytics === 'boolean' && typeof parsed.marketing === 'boolean') saved = parsed;
  } catch {}
  let choice = saved;
  let loaded = false;
  const allowed = group => !!choice && choice[group] === true;
  window.atomicConsentAllows = allowed;
  function loadGtm() {
    if (loaded || !choice || (!choice.analytics && !choice.marketing)) return;
    loaded = true;
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(ID);
    document.head.append(tag);
    // Equivalent to the GTM noscript fallback for JavaScript-enabled visitors;
    // no unconditional noscript iframe is installed because it bypasses consent.
  }
  function updateGoogle() {
    window.gtag('consent', 'update', {
      analytics_storage: allowed('analytics') ? 'granted' : 'denied',
      ad_storage: allowed('marketing') ? 'granted' : 'denied',
      ad_user_data: allowed('marketing') ? 'granted' : 'denied',
      ad_personalization: allowed('marketing') ? 'granted' : 'denied'
    });
  }
  if (choice) { updateGoogle(); loadGtm(); }

  const footer = document.querySelector('.site-footer .footer-bottom');
  const privacyLinks = document.createElement('nav');
  privacyLinks.className = 'footer-privacy';
  privacyLinks.setAttribute('aria-label', 'Privacy and cookie controls');
  const privacyLink = document.createElement('a');
  privacyLink.href = '/legal/privacy/';
  privacyLink.textContent = 'Privacy Policy';
  const link = document.createElement('button');
  link.type = 'button';
  link.className = 'cookie-preferences-link';
  link.innerHTML = '<span class="cookie-choice-icon" aria-hidden="true">✓ ×</span><span>Cookie Preferences</span>';
  link.addEventListener('click', () => show(true));
  privacyLinks.append(privacyLink, link);
  footer?.append(privacyLinks);

  const wrap = document.createElement('section');
  wrap.className = 'cookie-panel';
  wrap.setAttribute('aria-label', 'Cookie preferences');
  wrap.innerHTML = '<div class="cookie-panel-inner"><div class="cookie-intro"><h2>Cookie preferences</h2><p>Necessary storage keeps Atomic working. Optional analytics helps us understand visits; marketing measures campaigns. <a href="/legal/privacy/">Privacy</a> · <a href="/legal/cookies/">Cookies</a>. Change this anytime in the footer.</p></div><div class="cookie-options" hidden><label><span><strong>Necessary</strong><small>Essential site functionality and your consent choice</small></span><input type="checkbox" checked disabled /></label><label><span><strong>Analytics</strong><small>Understand visits and early-access requests</small></span><input id="cookie-analytics" type="checkbox" /></label><label><span><strong>Marketing</strong><small>Measure advertising campaigns</small></span><input id="cookie-marketing" type="checkbox" /></label></div><div class="cookie-actions"><button type="button" class="button button-secondary" data-cookie="reject">Reject optional</button><button type="button" class="button button-secondary" data-cookie="customize">Customize</button><button type="button" class="button button-secondary" data-cookie="accept">Accept all</button><button type="button" class="button button-primary" data-cookie="save" hidden>Save choices</button></div></div>';
  document.body.append(wrap);
  const options = wrap.querySelector('.cookie-options');
  const customize = wrap.querySelector('[data-cookie="customize"]');
  const saveButton = wrap.querySelector('[data-cookie="save"]');
  function show(custom) {
    wrap.hidden = false;
    wrap.classList.toggle("is-customizing", custom);
    options.hidden = !custom;
    customize.hidden = custom;
    saveButton.hidden = !custom;
    wrap.querySelector('#cookie-analytics').checked = allowed('analytics');
    wrap.querySelector('#cookie-marketing').checked = allowed('marketing');
    if (custom) wrap.querySelector('#cookie-analytics').focus();
  }
  function save(analytics, marketing) {
    const revoked = !!choice && ((choice.analytics && !analytics) || (choice.marketing && !marketing));
    choice = { version: 1, analytics, marketing, savedAt: new Date().toISOString() };
    try { localStorage.setItem(KEY, JSON.stringify(choice)); } catch {}
    updateGoogle();
    wrap.hidden = true;
    window.dispatchEvent(new CustomEvent('atomic:consent', { detail: { analytics, marketing } }));
    // Reload after withdrawal so previously loaded third-party scripts cannot continue.
    if (revoked) location.reload();
    else loadGtm();
  }
  wrap.querySelector('[data-cookie="reject"]').addEventListener('click', () => save(false, false));
  wrap.querySelector('[data-cookie="accept"]').addEventListener('click', () => save(true, true));
  customize.addEventListener('click', () => show(true));
  saveButton.addEventListener('click', () => save(
    wrap.querySelector('#cookie-analytics').checked,
    wrap.querySelector('#cookie-marketing').checked
  ));
  if (!choice) show(false);
  else wrap.hidden = true;
})();
