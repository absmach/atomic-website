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
const sitekey = form.dataset.sitekey;

let current = 0;
let widgetId;
let token = '';
let submitting = false;

function showStep(index) {
  current = index;
  steps.forEach((step, i) => { step.hidden = i !== index; });
  progress.value = index + 1;
  count.textContent = `Step ${index + 1} of ${steps.length}`;
  backButton.hidden = index === 0;
  const last = index === steps.length - 1;
  nextButton.textContent = last ? 'Request early access' : 'Continue';
  nextButton.disabled = last && !token;
  errorBox.textContent = '';
  steps[index].querySelector('h2').focus();
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

dialog.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => dialog.close()));
dialog.addEventListener('click', event => {
  if (event.target === dialog) dialog.close();
});

function openEarlyAccess(idea = '') {
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

// Early-access links navigate to the homepage hero using its native anchor.
// Only submitting an idea form opens the wizard (see app.js). Keep this flow
// until launch, when signup CTAs and their destinations can be updated together.
if (location.hash === '#early-access') {
  // Starter briefs land in the hero composer for review before requesting access.
  const params = new URLSearchParams(location.search);
  const idea = (params.get('idea') || '').trim().slice(0, 1200);
  if (idea) {
    const heroInput = document.getElementById('hero-idea');
    heroInput.value = idea;
    heroInput.dispatchEvent(new Event('input'));
  }
  // Keep the brief out of subsequent copied URLs and campaign submissions.
  if (params.has('idea')) {
    params.delete('idea');
    const query = params.toString();
    history.replaceState(null, '', location.pathname + (query ? `?${query}` : '') + location.hash);
  }
}
