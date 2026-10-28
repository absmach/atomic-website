// Homepage product demonstrations and email draft flow. Shared navigation is in site.js.
const views = {
  builder: { src: 'assets/builder.png', alt: 'Illustrative Atomic builder with a conversation and studio booking app preview.', caption: 'A conversation on the left. Your app coming to life on the right.' },
  source: { src: 'assets/source.png', alt: 'Illustrative Atomic source browser showing the booking app source files and code.', caption: 'See what was built. Browse your files. Keep your source.' }
};
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => {
  const view = views[button.dataset.view];
  const image = document.getElementById('product-image');
  image.src = view.src; image.alt = view.alt;
  document.getElementById('window-view-label').textContent = button.dataset.view === 'builder' ? 'Builder preview' : 'Source explorer';
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

const heroIdea = document.getElementById('hero-idea');

// Animate inspiration only in an empty, unfocused field. Never change an idea.
const ideaMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const defaultPlaceholder = heroIdea.placeholder;
const exampleIdeas = [
  'Build a booking app for my studio…',
  'Build an online shop for my small brand…',
  'Build a client portal for my next project…'
];
let ideaTimer;
let ideaIndex = 0;
function canAnimateIdeas() {
  return !ideaMotion.matches && !document.hidden && !heroIdea.value && document.activeElement !== heroIdea;
}
function animateNextIdea() {
  if (!canAnimateIdeas()) return;
  const phrase = exampleIdeas[ideaIndex];
  let length = 0;
  function typeCharacter() {
    if (!canAnimateIdeas()) return;
    heroIdea.placeholder = phrase.slice(0, ++length);
    if (length < phrase.length) ideaTimer = setTimeout(typeCharacter, 38);
    else {
      ideaIndex = (ideaIndex + 1) % exampleIdeas.length;
      ideaTimer = setTimeout(animateNextIdea, 2700);
    }
  }
  typeCharacter();
}
function syncIdeaAnimation() {
  clearTimeout(ideaTimer);
  heroIdea.placeholder = defaultPlaceholder;
  if (canAnimateIdeas()) ideaTimer = setTimeout(animateNextIdea, 900);
}
['focus', 'blur', 'input'].forEach(event => heroIdea.addEventListener(event, syncIdeaAnimation));
ideaMotion.addEventListener('change', syncIdeaAnimation);
document.addEventListener('visibilitychange', syncIdeaAnimation);
syncIdeaAnimation();

for (const [formId, inputId] of [['hero-idea-form', 'hero-idea'], ['idea-form', 'idea']]) {
  const form = document.getElementById(formId);
  const input = document.getElementById(inputId);
  form.addEventListener('submit', event => { event.preventDefault(); openEarlyAccess(input.value); });
  input.addEventListener('keydown', event => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) { event.preventDefault(); form.requestSubmit(); }
  });
}
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {
  heroIdea.value = button.dataset.prompt;
  heroIdea.focus({preventScroll: true});
  heroIdea.setSelectionRange(heroIdea.value.length, heroIdea.value.length);
}));
