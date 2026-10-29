// Public Cloudflare Turnstile site key for the early-access form (not a secret).
const sitekey = '0x4AAAAAAFfPJS0NJjFeyiuj';

// /early-access/ shows the wizard in the page, so it has a link people can
// share. Every other page gets it as a dialog that early-access links open.
const pageSlot = document.getElementById('access-page');
const doneAction = pageSlot
  ? '<a class="button button-primary" href="/">Back to Atomic</a>'
  : '<button class="button button-primary" type="button" data-close>Done</button>';
const wizard = `
  <form id="access-form" novalidate>
    <p class="eyebrow">EARLY ACCESS</p>
    <progress id="access-progress" max="3" value="1" aria-label="Progress"></progress>
    <p id="access-count" class="step-count"></p>
    <fieldset data-step="1">
      <legend><h2 id="access-title" tabindex="-1">What would you like to build?</h2></legend>
      <label class="sr-only" for="access-idea">Describe your app idea</label>
      <textarea id="access-idea" name="idea" rows="5" maxlength="1200" required placeholder="A booking app for my studio, where clients can choose a service and request a time…"></textarea>
    </fieldset>
    <fieldset data-step="2" hidden>
      <legend><h2 tabindex="-1">Tell us about you and the project.</h2></legend>
      <p class="field-label" id="app-type-label">It looks most like</p>
      <div class="choices" role="group" aria-labelledby="app-type-label"><label class="choice"><input type="radio" name="appType" value="booking" required /><span>Bookings</span></label><label class="choice"><input type="radio" name="appType" value="shop" required /><span>An online shop</span></label><label class="choice"><input type="radio" name="appType" value="portal" required /><span>A client portal</span></label><label class="choice"><input type="radio" name="appType" value="internal" required /><span>An internal tool</span></label><label class="choice"><input type="radio" name="appType" value="other" required /><span>Something else</span></label></div><input class="other" id="appType-other" name="appTypeOther" type="text" maxlength="100" placeholder="Tell us more" aria-label="Describe the kind of app" hidden />
      <p class="field-label" id="stage-label">Where are you today?</p>
      <div class="choices" role="group" aria-labelledby="stage-label"><label class="choice"><input type="radio" name="stage" value="idea" required /><span>Just an idea</span></label><label class="choice"><input type="radio" name="stage" value="building" required /><span>Working on it</span></label><label class="choice"><input type="radio" name="stage" value="running" required /><span>Already running</span></label></div>
      <p class="field-label" id="role-label">I am a</p>
      <div class="choices" role="group" aria-labelledby="role-label"><label class="choice"><input type="radio" name="role" value="founder" required /><span>Founder</span></label><label class="choice"><input type="radio" name="role" value="owner" required /><span>Small business owner</span></label><label class="choice"><input type="radio" name="role" value="freelancer" required /><span>Freelancer or agency</span></label><label class="choice"><input type="radio" name="role" value="developer" required /><span>Developer</span></label><label class="choice"><input type="radio" name="role" value="other" required /><span>Something else</span></label></div><input class="other" id="role-other" name="roleOther" type="text" maxlength="100" placeholder="Tell us more" aria-label="Describe your role" hidden />
    </fieldset>
    <fieldset data-step="3" hidden>
      <legend><h2 tabindex="-1">Where should we reach you?</h2></legend>
      <label class="field-label" for="access-name">Name</label>
      <input id="access-name" name="name" type="text" autocomplete="name" maxlength="100" required />
      <label class="field-label" for="access-company">Company or project <small>(optional)</small></label>
      <input id="access-company" name="company" type="text" autocomplete="organization" maxlength="100" />
      <label class="field-label" for="access-email">Email</label>
      <input id="access-email" name="email" type="email" autocomplete="email" maxlength="254" required />
      <input class="trap" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" />
      <div id="access-turnstile"></div>
    </fieldset>
    <p id="access-error" class="form-error" role="alert"></p>
    <div class="dialog-actions">
      <button id="access-back" class="button button-secondary" type="button">Back</button>
      <button id="access-next" class="button button-primary" type="submit">Continue</button>
    </div>
    <p class="consent-note">By submitting this form, you agree that Atomic may store your answers and email you about early access. <a href="/legal/privacy/" target="_blank" rel="noopener">Privacy policy</a></p>
  </form>
  <div id="access-done" tabindex="-1" hidden>
    <p class="eyebrow">YOU’RE ON THE LIST</p>
    <h2>Thanks, we’ve got your request.</h2>
    <p>If you’re shortlisted for the free trial, we’ll email you at <strong id="access-done-email"></strong>.</p>
    <div class="dialog-actions">${doneAction}</div>
  </div>
`;
if (pageSlot) pageSlot.insertAdjacentHTML('beforeend', wizard);
else document.body.insertAdjacentHTML('beforeend', `<dialog id="access-dialog" class="access-wizard" aria-labelledby="access-title"><button class="dialog-close" type="button" data-close aria-label="Close">×</button>${wizard}</dialog>`);

const dialog = document.getElementById('access-dialog');
const form = document.getElementById('access-form');
const done = document.getElementById('access-done');
const steps = [...form.querySelectorAll('fieldset[data-step]')];
const progress = document.getElementById('access-progress');
const count = document.getElementById('access-count');
const errorBox = document.getElementById('access-error');
const backButton = document.getElementById('access-back');
const nextButton = document.getElementById('access-next');
const turnstileBox = document.getElementById('access-turnstile');

let current = 0;
let widgetId;
let token = '';
let submitting = false;

function showStep(index, focus = true) {
  current = index;
  steps.forEach((step, i) => { step.hidden = i !== index; });
  progress.value = index + 1;
  count.textContent = `Step ${index + 1} of ${steps.length}`;
  backButton.hidden = index === 0;
  const last = index === steps.length - 1;
  nextButton.textContent = last ? 'Request early access' : 'Continue';
  nextButton.disabled = last && !token;
  errorBox.textContent = '';
  if (focus) steps[index].querySelector('h2').focus();
  if (last) loadTurnstile();
}

function validStep(step) {
  for (const field of step.querySelectorAll('input:not(.trap), textarea')) {
    if (field.type === 'radio' && !step.querySelector(`input[name="${field.name}"]:checked`)) {
      errorBox.textContent = 'Choose one option for each question.';
      field.focus();
      return false;
    }
    if (!field.checkValidity()) {
      errorBox.textContent = field.validationMessage;
      field.focus();
      return false;
    }
  }
  return true;
}

// "Something else" reveals a text box that must then be filled in.
form.addEventListener('change', event => {
  if (event.target.type !== 'radio') return;
  const detail = form.elements[`${event.target.name}Other`];
  if (!detail) return;
  detail.hidden = event.target.value !== 'other';
  detail.required = !detail.hidden;
  if (!detail.hidden) detail.focus();
});

function loadTurnstile() {
  if (widgetId !== undefined || document.getElementById('turnstile-script')) return;
  if (!sitekey) {
    errorBox.textContent = 'Early access sign-up is not available yet.';
    return;
  }
  const script = document.createElement('script');
  script.id = 'turnstile-script';
  script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
  script.async = true;
  script.onload = () => {
    widgetId = window.turnstile.render(turnstileBox, {
      sitekey,
      action: 'early_access',
      appearance: 'interaction-only',
      callback: value => setToken(value),
      'expired-callback': () => setToken(''),
      'error-callback': () => {
        setToken('');
        errorBox.textContent = 'We could not verify your browser. Reload the page and try again.';
      },
    });
  };
  document.head.append(script);
}

function setToken(value) {
  token = value;
  if (current === steps.length - 1 && !submitting) nextButton.disabled = !token;
}

// Campaign tags from the link the visitor arrived on, if it had any.
function campaignParams() {
  const params = new URLSearchParams(location.search);
  const tags = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];
  return Object.fromEntries(tags.filter(tag => params.get(tag)).map(tag => [tag, params.get(tag)]));
}

async function submit() {
  const data = new FormData(form);
  submitting = true;
  nextButton.disabled = true;
  nextButton.textContent = 'Sending…';
  errorBox.textContent = '';

  const payload = { ...Object.fromEntries(data), ...campaignParams(), turnstileToken: token };
  let message = '';
  try {
    const response = await fetch('/api/early-access', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      message = body.error || 'Something went wrong. Please try again.';
    }
  } catch {
    message = 'Check your connection and try again.';
  }

  submitting = false;
  // Tokens are single use, so any further attempt needs a fresh one.
  token = '';
  if (widgetId !== undefined) window.turnstile.reset(widgetId);
  nextButton.textContent = 'Request early access';

  if (message) {
    errorBox.textContent = message;
    return;
  }
  // Notify GTM only when the server confirms success; never include PII.
  if (window.atomicConsentAllows?.('analytics')) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: 'atomic_early_access_success' });
  }
  document.getElementById('access-done-email').textContent = payload.email;
  form.reset();
  form.querySelectorAll('.other').forEach(input => { input.hidden = true; input.required = false; });
  form.hidden = true;
  done.hidden = false;
  done.focus();
}

form.addEventListener('submit', event => {
  event.preventDefault();
  if (submitting || !validStep(steps[current])) return;
  if (current < steps.length - 1) showStep(current + 1);
  else submit();
});

backButton.addEventListener('click', () => showStep(current - 1));

if (dialog) {
  dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
}

function openEarlyAccess(idea = '') {
  // On /early-access/ itself, bring the wizard into view and keep its progress.
  if (!dialog) {
    pageSlot.scrollIntoView({ behavior: 'smooth', block: 'start' });
    (done.hidden ? steps[current].querySelector('h2') : done).focus({ preventScroll: true });
    return;
  }
  if (done.hidden === false) {
    done.hidden = true;
    form.hidden = false;
  }
  const field = document.getElementById('access-idea');
  if (idea.trim()) field.value = idea.trim();
  dialog.showModal();
  // With an idea from the page, ask for the email next; otherwise start at the idea.
  showStep(idea.trim() ? 1 : 0);
}

// Every early-access link opens the wizard where the visitor is. Opened in a
// new tab, shared, or without JavaScript, /early-access/ is a page of its own.
// Older /#early-access links are handled the same way. Starter-brief links
// carry an idea and go to the homepage composer instead.
function isEarlyAccessLink(url) {
  if (url.origin !== location.origin || url.searchParams.has('idea')) return false;
  return url.pathname === '/early-access/' || (url.pathname === '/' && url.hash === '#early-access');
}

document.addEventListener('click', event => {
  const link = event.target.closest('a[href]');
  if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  if (!isEarlyAccessLink(new URL(link.href))) return;
  event.preventDefault();
  openEarlyAccess();
});

// The idea parameter is read once and removed, keeping it out of copied URLs
// and campaign submissions.
function takeIdeaParam() {
  const params = new URLSearchParams(location.search);
  const idea = (params.get('idea') || '').trim().slice(0, 1200);
  if (params.has('idea')) {
    params.delete('idea');
    const query = params.toString();
    history.replaceState(null, '', location.pathname + (query ? `?${query}` : '') + location.hash);
  }
  return idea;
}

if (pageSlot) {
  const idea = takeIdeaParam();
  if (idea) document.getElementById('access-idea').value = idea;
  showStep(idea ? 1 : 0, false);
}

const heroInput = document.getElementById('hero-idea');
if (heroInput && location.hash === '#early-access') {
  // Starter briefs land in the hero composer for review before requesting access.
  const idea = takeIdeaParam();
  if (idea) {
    heroInput.value = idea;
    heroInput.dispatchEvent(new Event('input'));
  }
}
