const ideas = {
  booking: { prompt: '“Let my customers book a session, choose a service, and find a time that works.”', features: ['Service selection', 'Appointment requests', 'Owner dashboard'], audience: 'For studios, coaches, and people who make time for others.' },
  commerce: { prompt: '“Give my products a home, let customers explore the collection, and keep track of orders.”', features: ['Product catalog', 'Customer accounts', 'Order management'], audience: 'For independent makers, small shops, and your next side project.' },
  portal: { prompt: '“Create one place where my clients can follow their projects and see what’s coming next.”', features: ['Client sign-in', 'Project updates', 'Shared information'], audience: 'For freelancers, agencies, and businesses built on relationships.' }
};

document.querySelectorAll('[data-idea]').forEach(button => {
  button.addEventListener('click', () => {
    const idea = ideas[button.dataset.idea];
    document.querySelectorAll('[data-idea]').forEach(item => {
      const selected = item === button;
      item.classList.toggle('selected', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    document.getElementById('idea-prompt').textContent = idea.prompt;
    document.getElementById('idea-audience').textContent = idea.audience;
    document.getElementById('idea-features').replaceChildren(...idea.features.map(label => {
      const tag = document.createElement('span');
      tag.textContent = label;
      return tag;
    }));
  });
});

const views = {
  builder: { src: 'assets/builder.png', alt: 'Illustrative Atomic builder: a conversation creates a studio booking app with service selection and appointment times.', caption: 'A conversation on the left. Your app coming to life on the right.' },
  source: { src: 'assets/source.png', alt: 'Illustrative Atomic source browser showing the booking app source files and code.', caption: 'See what was built. Browse your files. Keep your source.' }
};
document.querySelectorAll('[data-view]').forEach(button => {
  button.addEventListener('click', () => {
    const view = views[button.dataset.view];
    const image = document.getElementById('product-image');
    image.src = view.src;
    image.alt = view.alt;
    document.getElementById('product-caption').textContent = view.caption;
    document.querySelectorAll('[data-view]').forEach(item => {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
  });
});

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
  if (event.key === 'Escape' && !mobileNav.hidden) {
    closeMenu();
    menuButton.focus();
  }
});
document.getElementById('year').textContent = new Date().getFullYear();
