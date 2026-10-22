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
  website: "",
  turnstileToken: "token",
};

const turnstileOk = { success: true, action: "early_access", hostname: "atomicapp.dev" };

const realFetch = globalThis.fetch;
let calls;
let responders;

// Each responder handles one outbound request, in order.
beforeEach(() => {
  calls = [];
  responders = [];
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

function submit(body, method = "POST") {
  const request = new Request("https://atomicapp.dev/api/early-access", {
    method,
    body: method === "POST" ? JSON.stringify(body) : undefined,
  });
  return worker.fetch(request, env);
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
  responders = [reply(turnstileOk), reply({ data: { id: 1 } })];
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

test("stores the free-text detail when someone picks something else", async () => {
  responders = [reply(turnstileOk), reply({ data: { id: 1 } })];
  const res = await submit({ ...valid, role: "other", roleOther: "Potter", roleIgnored: "x" });
  assert.equal(res.status, 200);
  const { attribs } = JSON.parse(calls[1].init.body);
  assert.equal(attribs.role, "other");
  assert.equal(attribs.role_other, "Potter");
  assert.equal(attribs.heard_from_other, undefined);
});

test("adds an existing subscriber to the list and keeps their other lists", async () => {
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
  responders = [
    reply(turnstileOk),
    reply({ message: "exists" }, 409),
    reply({ data: { results: [existing] } }),
    reply({ data: existing }),
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
