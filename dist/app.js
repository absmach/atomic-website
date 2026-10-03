// UI state is local to this page. Demos never make booking or payment requests.
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
window.matchMedia('(min-width: 801px)').addEventListener('change', event => { if (event.matches) closeMenu(); });
document.getElementById('year').textContent = new Date().getFullYear();

const views = {
  builder: { src: 'assets/builder.png', alt: 'Illustrative Atomic builder with a conversation and studio booking app preview.', caption: 'A conversation on the left. Your app coming to life on the right.' },
  source: { src: 'assets/source.png', alt: 'Illustrative Atomic source browser showing the booking app source files and code.', caption: 'See what was built. Browse your files. Keep your source.' }
};
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
  const view = views[button.dataset.view];
  const image = document.getElementById('product-image');
  image.src = view.src; image.alt = view.alt;
  document.getElementById('product-caption').textContent = view.caption;
  document.querySelectorAll('[data-view]').forEach(item => {
    item.classList.toggle('selected', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
}));

// These examples run only in this page. No backend or generation request is made.
const demoContent = {
  booking: { prompt: '“Let my clients pick a service and request a time that works for them.”', description: 'Try the customer’s side, then see how the studio handles the request.' },
  shop: { prompt: '“Create a shop for my small collection, with a product catalog and a shopping bag.”', description: 'Explore the collection. Add an item and see the bag update.' },
  portal: { prompt: '“Give my clients a space to see project progress and understand what comes next.”', description: 'Explore the milestones and see the project from your client’s perspective.' }
};
let currentDemo = 'booking';
function setDemo(name) {
  currentDemo = name;
  document.getElementById('demo-title').textContent = {booking:'STUDIO SESSIONS',shop:'FORM & FIELD',portal:'COMMON GROUND'}[name];
  document.querySelectorAll('[data-demo]').forEach(button => {
    const active = button.dataset.demo === name;
    button.classList.toggle('selected', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelectorAll('.demo-app').forEach(app => { app.hidden = app.id !== `${name}-demo`; });
  document.getElementById('demo-prompt').textContent = demoContent[name].prompt;
  document.getElementById('demo-description').textContent = demoContent[name].description;
}
document.querySelectorAll('[data-demo]').forEach(button => button.addEventListener('click', () => setDemo(button.dataset.demo)));
document.querySelectorAll('[data-open-demo]').forEach(link => link.addEventListener('click', () => setDemo(link.dataset.openDemo)));

let selectedTime = 'Monday, 10:00';
let booking = null;
const bookingFeedback = document.getElementById('booking-feedback');
function setRole(role) {
  document.querySelectorAll('[data-role]').forEach(button => {
    const active = button.dataset.role === role;
    button.classList.toggle('selected', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.getElementById('customer-view').hidden = role !== 'customer';
  document.getElementById('owner-view').hidden = role !== 'owner';
  if (!booking) bookingFeedback.textContent = 'Try a request. No real appointment will be made.';
  else if (booking.confirmed) bookingFeedback.textContent = `Demo booking confirmed: ${booking.service} · ${booking.time}. No real appointment was made.`;
  else bookingFeedback.textContent = role === 'owner' ? 'One sample request is waiting for your review.' : 'Demo request received. Switch to Studio owner to review it.';
}
document.querySelectorAll('[data-role]').forEach(button => button.addEventListener('click', () => setRole(button.dataset.role)));
document.querySelectorAll('[data-time]').forEach(button => button.addEventListener('click', () => {
  selectedTime = button.dataset.time;
  document.querySelectorAll('[data-time]').forEach(item => {
    item.classList.toggle('selected', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
}));
function renderBooking() {
  document.getElementById('request-count').textContent = booking && !booking.confirmed ? '1' : '0';
  const container = document.getElementById('owner-requests');
  container.replaceChildren();
  if (!booking) {
    container.innerHTML = '<div class="empty-requests"><span aria-hidden="true">▦</span><h4>Your next booking starts here.</h4><p>Switch to Customer and request a session to see it arrive.</p></div>';
    return;
  }
  const card = document.createElement('article');
  card.className = 'request-card';
  const name = document.createElement('span'); name.className = 'app-eyebrow'; name.textContent = 'ALEX MORGAN · SAMPLE CLIENT';
  const heading = document.createElement('h4'); heading.textContent = booking.service;
  const time = document.createElement('p'); time.textContent = `${booking.time} · Video call`;
  const status = document.createElement('span'); status.className = 'booking-status'; status.textContent = booking.confirmed ? 'Confirmed in demo' : 'Awaiting your confirmation';
  card.append(name, heading, time, status);
  if (!booking.confirmed) {
    const confirm = document.createElement('button'); confirm.className = 'sample-primary'; confirm.textContent = 'Confirm sample booking';
    confirm.addEventListener('click', () => {
      booking.confirmed = true;
      renderBooking();
      setRole('owner');
      // Keep keyboard focus after replacing the confirmation control.
      document.querySelector('[data-role="customer"]').focus({preventScroll:true});
    });
    card.append(confirm);
  }
  container.append(card);
}
document.getElementById('request-booking').addEventListener('click', () => {
  booking = { service: document.querySelector('input[name="service"]:checked').value, time: selectedTime, confirmed: false };
  renderBooking();
  setRole('customer');
  document.getElementById('request-booking').textContent = 'Update sample request';
});

let bag = { notebook: 0, tote: 0 };
function renderBag() {
  document.getElementById('bag-count').textContent = bag.notebook + bag.tote;
  document.getElementById('bag-total').textContent = `€${bag.notebook * 18 + bag.tote * 24}`;
  document.getElementById('clear-bag').disabled = bag.notebook + bag.tote === 0;
}
document.querySelectorAll('[data-add]').forEach(button => button.addEventListener('click', () => {
  bag[button.dataset.add] += 1;
  renderBag();
  document.getElementById('shop-feedback').textContent = `${button.dataset.add === 'notebook' ? 'Notebook' : 'Tote'} added. ${bag.notebook + bag.tote} items in your sample bag. No purchase is made.`;
}));
function clearBag() {
  bag = {notebook:0,tote:0}; renderBag();
  document.getElementById('shop-feedback').textContent = 'Demo collection. No checkout or payment is connected.';
}
document.getElementById('clear-bag').addEventListener('click', () => {
  clearBag(); document.querySelector('[data-add="notebook"]').focus({preventScroll:true});
});
const milestones = {
  discovery: ['01 / DISCOVERY', 'A shared starting point.', 'Your goals, audience, and inspiration are collected in the project brief. This phase is complete, and the creative direction is taking shape.'],
  design: ['02 / DESIGN DIRECTION', 'Your first look.', 'The initial identity is ready for your feedback. Review the direction together before moving into the final details.'],
  delivery: ['03 / FINAL DELIVERY', 'Everything, ready to use.', 'Once the design is approved, the final identity files and brand guidelines will be prepared for handover. This milestone is up next.']
};
function setMilestone(name) {
  document.querySelectorAll('[data-milestone]').forEach(button => {
    const active = button.dataset.milestone === name;
    button.classList.toggle('selected', active); button.setAttribute('aria-pressed', String(active));
  });
  ['label','title','copy'].forEach((field,index) => {document.getElementById(`milestone-${field}`).textContent = milestones[name][index];});
}
document.querySelectorAll('[data-milestone]').forEach(button => button.addEventListener('click', () => setMilestone(button.dataset.milestone)));
document.getElementById('reset-demo').addEventListener('click', () => {
  if (currentDemo === 'booking') {
    booking = null; selectedTime = 'Monday, 10:00';
    document.querySelector('input[name="service"]').checked = true;
    document.querySelector('[data-time="Monday, 10:00"]').click();
    document.getElementById('request-booking').textContent = 'Request this session';
    renderBooking(); setRole('customer');
  } else if (currentDemo === 'shop') clearBag();
  else setMilestone('design');
});

const ideaForm = document.getElementById('idea-form');
const ideaInput = document.getElementById('idea');
const emailDialog = document.getElementById('email-dialog');
const emailDraft = document.getElementById('email-draft');
const emailStatus = document.getElementById('email-status');
ideaInput.addEventListener('input', () => ideaInput.setCustomValidity(''));
ideaForm.addEventListener('submit', event => {
  event.preventDefault();
  const idea = ideaInput.value.trim();
  if (!idea) {
    ideaInput.setCustomValidity('Tell us a little about the app you want to build.');
    ideaInput.reportValidity();
    return;
  }
  const body = `Hi Atomic team,\n\nI’d like to ask about early access. Here’s what I want to build:\n\n${idea}\n\nPlease let me know when I can try Atomic.\n\nThank you!`;
  emailDraft.textContent = body;
  document.getElementById('send-email').href = `mailto:info@absmach.eu?subject=${encodeURIComponent('Atomic early access')}&body=${encodeURIComponent(body)}`;
  emailStatus.textContent = 'Your message has not been sent.';
  emailDialog.showModal();
});
document.getElementById('close-dialog').addEventListener('click', () => emailDialog.close());
emailDialog.addEventListener('click', event => {
  const box = emailDialog.getBoundingClientRect();
  if (event.target === emailDialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) emailDialog.close();
});
document.getElementById('copy-email').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(`To: info@absmach.eu\nSubject: Atomic early access\n\n${emailDraft.textContent}`);
    emailStatus.textContent = 'Copied. Paste into your email app and send when you’re ready.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange(); range.selectNodeContents(emailDraft);
    selection.removeAllRanges(); selection.addRange(range);
    emailStatus.textContent = 'Automatic copying is unavailable. The draft is selected so you can copy it manually.';
  }
});
// Keep sequential keyboard navigation within the open email draft.
emailDialog.addEventListener('keydown', event => {
  if (event.key !== 'Tab') return;
  const controls = [...emailDialog.querySelectorAll('button:not([disabled]), a[href], [tabindex="0"]')];
  const first = controls[0];
  const last = controls[controls.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
});
