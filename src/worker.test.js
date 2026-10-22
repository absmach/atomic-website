import assert from "node:assert/strict";
import { afterEach, beforeEach, test } from "node:test";
import worker from "./worker.js";

const env = {
  LISTMONK_URL: "https://mail.example",
  LISTMONK_API_USER: "atomic-website",
  LISTMONK_API_TOKEN: "secret-token",
  LISTMONK_LIST_ID: "12",
  TURNSTILE_SECRET: "turnstile-secret",
  TURNSTILE_HOSTNAMES: "atomicapp.dev,www.atomicapp.dev",
  LISTMONK_WELCOME_TEMPLATE_ID: "5",
  LISTMONK_FROM_EMAIL: "Atomic <hello@example.com>",
};

const valid = {
  idea: "A booking app for my pottery studio.",
  appType: "booking",
  stage: "idea",
  role: "owner",
  heardFrom: "friend",
  company: "Clay & Co",
  name: "Ada Obi",
  email: "ada@example.com",
  consent: true,
  website: "",
  turnstileToken: "token",
};

const turnstileOk = { success: true, action: "early_access", hostname: "atomicapp.dev" };

const realFetch = globalThis.fetch;
let calls;
let responders;
let background;

// Each responder handles one outbound request, in order.
beforeEach(() => {
  calls = [];
  responders = [];
  background = [];
  globalThis.fetch = async (url, init) => {
    calls.push({ url: String(url), init });
    const respond = responders.shift();
    assert.ok(respond, `unexpected request to ${url}`);
    return respond();
  };
});
afterEach(() => {
  globalThis.fetch = realFetch;
});

const reply = (body, status = 200) => () => Response.json(body, { status });

// Waits for work the Worker hands to ctx.waitUntil, such as the thank-you email.
const ctx = { waitUntil: (promise) => background.push(promise) };

async function submit(body, method = "POST", config = env) {
  const request = new Request("https://atomicapp.dev/api/early-access", {
    method,
    body: method === "POST" ? JSON.stringify(body) : undefined,
  });
  const res = await worker.fetch(request, config, ctx);
  await Promise.all(background);
  return res;
}

test("rejects methods other than POST", async () => {
  const res = await submit(valid, "GET");
  assert.equal(res.status, 405);
});

test("rejects incomplete or invalid answers before calling any service", async () => {
  for (const patch of [
    { idea: "" },
    { name: "" },
    { email: "not-an-email" },
    { role: "astronaut" },
    { role: "other" },
    { heardFrom: "other", heardFromOther: " " },
    { company: "x".repeat(101) },
    { consent: false },
  ]) {
    const res = await submit({ ...valid, ...patch });
    assert.equal(res.status, 400, JSON.stringify(patch));
  }
  assert.equal(calls.length, 0);
});

test("silently accepts honeypot submissions without saving them", async () => {
  const res = await submit({ ...valid, website: "https://spam.example" });
  assert.equal(res.status, 200);
  assert.equal(calls.length, 0);
});

test("rejects a failed or mismatched Turnstile result", async () => {
  for (const result of [
    { success: false },
    { ...turnstileOk, action: "newsletter_signup" },
    { ...turnstileOk, hostname: "evil.example" },
  ]) {
    responders = [reply(result)];
    const res = await submit(valid);
    assert.equal(res.status, 403);
  }
  assert.equal(calls.length, 3);
});

test("creates a subscriber with the answers as attributes", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } }), reply({ data: true })];
  const res = await submit(valid);
  assert.equal(res.status, 200);

  const [, create] = calls;
  assert.equal(create.url, "https://mail.example/api/subscribers");
  assert.equal(create.init.headers.Authorization, "token atomic-website:secret-token");
  const sent = JSON.parse(create.init.body);
  assert.deepEqual(sent.lists, [12]);
  assert.equal(sent.email, "ada@example.com");
  assert.equal(sent.attribs.idea, valid.idea);
  assert.equal(sent.attribs.app_type, "booking");
  assert.equal(sent.attribs.source, "website");
  assert.equal(sent.attribs.heard_from, "friend");
  assert.equal(sent.attribs.company, "Clay & Co");
});

test("sends the thank-you email to a new subscriber", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } }), reply({ data: true })];
  await submit(valid);

  const email = calls[2];
  assert.equal(email.url, "https://mail.example/api/tx");
  assert.deepEqual(JSON.parse(email.init.body), {
    subscriber_email: "ada@example.com",
    template_id: 5,
    from_email: "Atomic <hello@example.com>",
    content_type: "html",
  });
});

test("still succeeds when the thank-you email fails", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } }), reply({ message: "smtp down" }, 500)];
  const res = await submit(valid);
  assert.equal(res.status, 200);
});

test("skips the email until a template is configured", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } })];
  const res = await submit(valid, "POST", { ...env, LISTMONK_WELCOME_TEMPLATE_ID: "" });
  assert.equal(res.status, 200);
  assert.equal(calls.length, 2);
});

test("stores the free-text detail when someone picks something else", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } }), reply({ data: true })];
  const res = await submit({ ...valid, role: "other", roleOther: "Potter", roleIgnored: "x" });
  assert.equal(res.status, 200);
  const { attribs } = JSON.parse(calls[1].init.body);
  assert.equal(attribs.role, "other");
  assert.equal(attribs.role_other, "Potter");
  assert.equal(attribs.heard_from_other, undefined);
});

const existing = {
  id: 7,
  email: "Ada@Example.com",
  name: "Ada",
  status: "enabled",
  attribs: { city: "Nairobi" },
  lists: [
    { id: 3, subscription_status: "confirmed" },
    { id: 4, subscription_status: "unsubscribed" },
  ],
};

test("adds an existing subscriber to the list, keeps their other lists, and emails them", async () => {
  responders = [
    reply(turnstileOk),
    reply({ message: "exists" }, 409),
    reply({ data: { results: [existing] } }),
    reply({ data: existing }),
    reply({ data: true }),
  ];
  const res = await submit(valid);
  assert.equal(res.status, 200);

  const update = calls[3];
  assert.equal(update.url, "https://mail.example/api/subscribers/7");
  assert.equal(update.init.method, "PUT");
  const sent = JSON.parse(update.init.body);
  assert.deepEqual(sent.lists.sort((a, b) => a - b), [3, 12]);
  assert.equal(sent.attribs.city, "Nairobi");
  assert.equal(sent.attribs.role, "owner");
  assert.equal(calls[4].url, "https://mail.example/api/tx");
});

test("does not email someone who is on the list, left it earlier, or is blocklisted", async () => {
  const onList = { ...existing, lists: [{ id: 12, subscription_status: "confirmed" }] };
  const left = { ...existing, lists: [{ id: 12, subscription_status: "unsubscribed" }] };
  const blocked = { ...existing, status: "blocklisted" };
  for (const found of [onList, left, blocked]) {
    calls = [];
    responders = [
      reply(turnstileOk),
      reply({ message: "exists" }, 409),
      reply({ data: { results: [found] } }),
      ...(found === blocked ? [] : [reply({ data: found })]),
    ];
    const res = await submit(valid);
    assert.equal(res.status, 200);
    assert.ok(calls.every((c) => !c.url.endsWith("/api/tx")));
  }
});

test("reports a listmonk failure", async () => {
  responders = [reply(turnstileOk), reply({ message: "boom" }, 500)];
  const res = await submit(valid);
  assert.equal(res.status, 502);
});

test("refuses to run without its configuration", async () => {
  const res = await worker.fetch(
    new Request("https://atomicapp.dev/api/early-access", {
      method: "POST",
      body: JSON.stringify(valid),
    }),
    { ...env, LISTMONK_LIST_ID: "" },
  );
  assert.equal(res.status, 503);
});
