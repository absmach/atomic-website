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
