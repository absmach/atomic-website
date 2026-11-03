import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const source = readFileSync(new URL('../dist/site.js', import.meta.url), 'utf8');
const KEY = 'atomic-cookie-consent-v2';

// Run the actual shared script with a minimal DOM: no vendor network calls.
function browser(initial = {}, lang = 'en') {
  const storage = new Map(Object.entries(initial));
  const scripts = [];
  const nodes = [];
  let reloads = 0;
  class Element {
    constructor() {
      this.listeners = {}; this.children = new Map(); this.dataset = {};
      this.hidden = false;
      this.classList = { contains: () => false, add() {}, remove() {}, toggle() {} };
    }
    addEventListener(name, callback) { this.listeners[name] = callback; }
    setAttribute() {}
    append() {}
    focus() {}
    querySelector(selector) {
      if (!this.children.has(selector)) this.children.set(selector, new Element());
      return this.children.get(selector);
    }
    querySelectorAll() { return []; }
    click() { this.listeners.click?.(); }
  }
  const menu = new Element();
  const root = new Element(); root.lang = lang;
  const document = {
    documentElement: root,
    head: { append: node => scripts.push(node.src) },
    body: { append() {} },
    querySelector: selector => selector === '.menu-toggle' ? menu : null,
    querySelectorAll: () => [],
    getElementById: () => new Element(),
    addEventListener() {},
    createElement: () => { const node = new Element(); nodes.push(node); return node; },
  };
  const window = {
    matchMedia: () => ({ matches: false, addEventListener() {} }),
    dispatchEvent() {},
  };
  vm.runInNewContext(source, {
    document, window, Date,
    localStorage: {
      getItem: key => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
      removeItem: key => storage.delete(key),
    },
    location: { reload: () => { reloads++; } },
    CustomEvent: class {},
  });
  const panel = nodes.find(node => node.className === 'cookie-panel');
  return { storage, scripts, window, panel, get reloads() { return reloads; } };
}

function choice(analytics, marketing, savedAt = new Date().toISOString()) {
  return JSON.stringify({ version: 2, analytics, marketing, savedAt });
}

test('no consent and invalid, old or future consent never load GTM', () => {
  for (const initial of [
    {},
    { [KEY]: 'invalid json' },
    { [KEY]: choice(true, true, 'not a date') },
    { [KEY]: choice(true, true, new Date(Date.now() - 200 * 86400000).toISOString()) },
    { [KEY]: choice(true, true, new Date(Date.now() + 86400000).toISOString()) },
    { 'atomic-cookie-consent-v1': JSON.stringify({ version: 1, analytics: true, marketing: true }) },
  ]) {
    const b = browser(initial);
    assert.equal(b.scripts.length, 0);
    assert.equal(b.window.atomicConsentAllows('analytics'), false);
    assert.equal(b.panel.hidden, false);
  }
});

test('a recent refusal is remembered without loading GTM', () => {
  const b = browser({ [KEY]: choice(false, false) });
  assert.equal(b.scripts.length, 0);
  assert.equal(b.panel.hidden, true);
});

test('category consent stays separate; withdrawing it stops future activation', () => {
  const b = browser({ [KEY]: choice(true, false) });
  assert.equal(b.scripts.length, 1);
  assert.equal(b.window.atomicConsentAllows('analytics'), true);
  assert.equal(b.window.atomicConsentAllows('marketing'), false);
  b.panel.querySelector('[data-cookie="reject"]').click();
  assert.equal(b.reloads, 1);
  assert.equal(b.window.atomicConsentAllows('analytics'), false);
  const afterReload = browser(Object.fromEntries(b.storage));
  assert.equal(afterReload.scripts.length, 0);
  assert.equal(afterReload.panel.hidden, true);
});

test('fresh acceptance records both choices and consent date', () => {
  const b = browser();
  b.panel.querySelector('[data-cookie="accept"]').click();
  const saved = JSON.parse(b.storage.get(KEY));
  assert.equal(saved.version, 2);
  assert.equal(saved.analytics, true);
  assert.equal(saved.marketing, true);
  assert.ok(Number.isFinite(Date.parse(saved.savedAt)));
  assert.equal(b.scripts.length, 1);
});

test('French language controls link to the downloadable French notice', () => {
  const b = browser({}, 'fr');
  assert.match(b.panel.innerHTML, /campagnes publicitaires/);
  assert.match(b.panel.innerHTML, /\/legal\/downloads\/atomic-documents-juridiques-fr\.pdf/);
  assert.match(b.panel.innerHTML, /Refuser/);
});
