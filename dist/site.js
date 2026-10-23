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
