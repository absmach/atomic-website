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
  const KEY = 'atomic-cookie-consent-v2';
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
    const selectedAt = new Date(parsed?.savedAt);
    const expiresAt = new Date(selectedAt);
    expiresAt.setUTCMonth(expiresAt.getUTCMonth() + 6);
    if (parsed && parsed.version === 2 && typeof parsed.analytics === 'boolean' && typeof parsed.marketing === 'boolean'
        && Number.isFinite(selectedAt.getTime()) && selectedAt.getTime() <= Date.now() && Date.now() < expiresAt.getTime()) saved = parsed;
    else localStorage.removeItem(KEY);
    // A new notice/purpose version needs a new choice, including for old opt-ins.
    localStorage.removeItem('atomic-cookie-consent-v1');
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
  link.addEventListener('click', () => {
    show(true);
    // Reopening from the footer should take mobile visitors to the
    // in-flow controls, even when they are scrolled far down the page.
    if (wrap.classList.contains('cookie-panel-home')) {
      wrap.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
  privacyLinks.append(privacyLink, link);
  footer?.append(privacyLinks);

  const wrap = document.createElement('section');
  wrap.className = 'cookie-panel';
  wrap.setAttribute('aria-label', 'Cookie preferences');
  // A short first layer with equal Reject and Accept; categories live under Settings.
  const french = document.documentElement.lang === 'fr';
  const labels = french
    ? ['Préférences cookies', 'Avec votre accord, nous utilisons des technologies facultatives de Google pour mesurer les visites et les campagnes publicitaires. Vous pouvez accepter, refuser ou choisir les finalités.', 'Notice cookies', '/legal/downloads/atomic-documents-juridiques-fr.pdf', 'Nécessaires', 'Fonctionnement du site et mémorisation du choix', 'Audience', 'Comprendre les visites et les demandes d’accès anticipé', 'Publicité', 'Mesurer les campagnes publicitaires', 'Réglages', 'Refuser', 'Accepter', 'Enregistrer']
    : ['Cookie settings', 'With your permission, we use optional Google technologies to measure visits and advertising campaigns. You can accept, reject or choose purposes.', 'Cookie policy', '/legal/privacy/#cookies', 'Necessary', 'Essential site functionality and your consent choice', 'Analytics', 'Understand visits and early-access requests', 'Marketing', 'Measure advertising campaigns', 'Settings', 'Reject', 'Accept', 'Save choices'];
  wrap.setAttribute('aria-label', labels[0]);
  if (french) {
    privacyLink.href = '/legal/downloads/atomic-documents-juridiques-fr.pdf';
    privacyLink.textContent = 'Confidentialité';
    link.textContent = 'Préférences cookies';
  }
  wrap.innerHTML = `<div class="cookie-panel-inner"><div class="cookie-intro"><h2 hidden>${labels[0]}</h2><p>${labels[1]} <a href="${labels[3]}">${labels[2]}</a></p></div><div class="cookie-options" hidden><label><span><strong>${labels[4]}</strong><small>${labels[5]}</small></span><input type="checkbox" checked disabled /></label><label><span><strong>${labels[6]}</strong><small>${labels[7]}</small></span><input id="cookie-analytics" type="checkbox" /></label><label><span><strong>${labels[8]}</strong><small>${labels[9]}</small></span><input id="cookie-marketing" type="checkbox" /></label></div><div class="cookie-actions"><button type="button" class="cookie-settings" data-cookie="customize">${labels[10]}</button><button type="button" class="button button-secondary" data-cookie="reject">${labels[11]}</button><button type="button" class="button button-secondary" data-cookie="accept">${labels[12]}</button><button type="button" class="button button-primary" data-cookie="save" hidden>${labels[13]}</button></div></div>`;
  // On phones, the cookie panel follows both the suggested prompts and early-access note.
  // Desktop and inner pages keep the compact viewport-anchored panel.
  const composer = document.querySelector('.prompt-opening .prompt-composer');
  const suggestions = document.querySelector('.prompt-opening .prompt-suggestions');
  const launchNote = document.querySelector('.prompt-opening .prompt-launch-note');
  const mobileLayout = window.matchMedia('(max-width: 700px)');
  function placePanel() {
    if (composer && mobileLayout.matches) {
      (launchNote || suggestions || composer).insertAdjacentElement('afterend', wrap);
      wrap.classList.add('cookie-panel-home');
    } else {
      document.body.append(wrap);
      wrap.classList.remove('cookie-panel-home');
    }
  }
  placePanel();
  mobileLayout.addEventListener('change', placePanel);
  const options = wrap.querySelector('.cookie-options');
  const customize = wrap.querySelector('[data-cookie="customize"]');
  const saveButton = wrap.querySelector('[data-cookie="save"]');
  const title = wrap.querySelector('.cookie-intro h2');
  function show(custom) {
    wrap.hidden = false;
    wrap.classList.toggle("is-customizing", custom);
    options.hidden = !custom;
    title.hidden = !custom;
    customize.hidden = custom;
    saveButton.hidden = !custom;
    wrap.querySelector('#cookie-analytics').checked = allowed('analytics');
    wrap.querySelector('#cookie-marketing').checked = allowed('marketing');
    if (custom) wrap.querySelector('#cookie-analytics').focus();
  }
  function save(analytics, marketing) {
    const revoked = !!choice && ((choice.analytics && !analytics) || (choice.marketing && !marketing));
    choice = { version: 2, analytics, marketing, savedAt: new Date().toISOString() };
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

// Theme: match the system, light, or dark, in turn. The page's head script
// applied the saved choice before drawing; this keeps it and follows the
// system while that is the choice.
{
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const labels = {system: 'Theme: match system', light: 'Theme: light', dark: 'Theme: dark'};
  const next = {system: 'light', light: 'dark', dark: 'system'};
  const apply = choice => {
    root.dataset.themeChoice = choice;
    root.dataset.theme = choice === 'dark' || (choice === 'system' && system.matches) ? 'dark' : 'light';
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.setAttribute('aria-label', labels[choice]);
      button.title = labels[choice];
    });
  };
  apply(root.dataset.themeChoice || 'system');
  document.addEventListener('click', event => {
    if (!event.target.closest('[data-theme-toggle]')) return;
    const choice = next[root.dataset.themeChoice] || 'light';
    try { choice === 'system' ? localStorage.removeItem('atomic-theme') : localStorage.setItem('atomic-theme', choice); } catch (_) {}
    apply(choice);
  });
  system.addEventListener('change', () => apply(root.dataset.themeChoice || 'system'));
}
