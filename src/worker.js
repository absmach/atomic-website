const TURNSTILE_ACTION = "early_access";
const TURNSTILE_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Keep in sync with the radio values in content/home.html.
const CHOICES = {
  appType: ["booking", "shop", "portal", "internal", "other"],
  stage: ["idea", "building", "running"],
  role: ["founder", "owner", "freelancer", "developer", "other"],
  heardFrom: ["search", "x", "linkedin", "github", "youtube", "friend", "event", "other"],
};
const ATTRIBUTE_NAMES = { appType: "app_type", stage: "stage", role: "role", heardFrom: "heard_from" };

export default {
  async fetch(request, env, ctx) {
    if (new URL(request.url).pathname !== "/api/early-access") {
      return new Response("Not found", { status: 404 });
    }
    if (request.method !== "POST") {
      return json({ error: "Method not allowed." }, 405, { Allow: "POST" });
    }
    return handleApplication(request, env, ctx);
  },
};

async function handleApplication(request, env, ctx) {
  const listId = Number(env.LISTMONK_LIST_ID);
  if (!env.TURNSTILE_SECRET || !env.LISTMONK_API_TOKEN || !(listId > 0)) {
    console.error("early access is missing configuration");
    return json({ error: "Early access is not available right now." }, 503);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Invalid request." }, 400);
  }

  // Real visitors never see this field.
  if (str(body.website) !== "") return json({ ok: true });

  const application = parseApplication(body);
  if (!application) return json({ error: "Check your answers and try again." }, 400);

  const verified = await verifyTurnstile(
    str(body.turnstileToken),
    request.headers.get("CF-Connecting-IP"),
    env,
  );
  if (!verified) return json({ error: "Verification failed. Please try again." }, 403);

  const outcome = await saveSubscriber(application, listId, env);
  if (!outcome) return json({ error: "Could not save your request. Please try again." }, 502);

  // Repeat submissions from someone already on the list don't get another email.
  if (outcome !== "already") ctx.waitUntil(sendThanksEmail(application.email, env));
  return json({ ok: true });
}

function parseApplication(body) {
  const idea = str(body.idea);
  const name = str(body.name);
  const company = str(body.company);
  const email = str(body.email);
  if (!idea || idea.length > 1200) return null;
  if (!name || name.length > 100 || company.length > 100) return null;
  if (!EMAIL_RE.test(email) || email.length > 254) return null;
  if (body.consent !== true) return null;

  const attribs = { idea, company, source: "website", applied_at: new Date().toISOString() };
  for (const [field, allowed] of Object.entries(CHOICES)) {
    if (!allowed.includes(body[field])) return null;
    attribs[ATTRIBUTE_NAMES[field]] = body[field];
    if (body[field] === "other") {
      const detail = str(body[`${field}Other`]);
      if (!detail || detail.length > 100) return null;
      attribs[`${ATTRIBUTE_NAMES[field]}_other`] = detail;
    }
  }
  return { email, name, attribs };
}

// Fails closed on any error. Tokens are single-use, so replays fail too.
async function verifyTurnstile(token, clientIp, env) {
  const hostnames = (env.TURNSTILE_HOSTNAMES ?? "")
    .split(",")
    .map((h) => h.trim())
    .filter(Boolean);
  if (token === "" || token.length > 2048 || hostnames.length === 0) return false;

  const params = new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token });
  if (clientIp) params.set("remoteip", clientIp);

  try {
    const res = await fetch(TURNSTILE_URL, {
      method: "POST",
      body: params,
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) return false;
    const result = await res.json();
    return (
      result.success === true &&
      result.action === TURNSTILE_ACTION &&
      hostnames.includes(result.hostname)
    );
  } catch (err) {
    console.error("turnstile verification failed", err);
    return false;
  }
}

function listmonk(env, path, init = {}) {
  return fetch(`${env.LISTMONK_URL}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `token ${env.LISTMONK_API_USER}:${env.LISTMONK_API_TOKEN}`,
    },
    signal: AbortSignal.timeout(10_000),
  });
}

async function saveSubscriber({ email, name, attribs }, listId, env) {
  try {
    const res = await listmonk(env, "/subscribers", {
      method: "POST",
      body: JSON.stringify({
        email,
        name,
        status: "enabled",
        lists: [listId],
        attribs,
        preconfirm_subscriptions: true,
      }),
    });
    if (res.status === 409) return await updateExisting(email, attribs, listId, env);
    if (!res.ok) console.error("listmonk create failed", res.status, await res.text());
    return res.ok && "created";
  } catch (err) {
    console.error("listmonk create error", err);
    return false;
  }
}

// The address is already in listmonk (another list, or an earlier request).
// Add it to ours and overwrite the answers, leaving its other lists alone.
// Returns "added" if it joined our list now, "already" if it was on it, or false.
async function updateExisting(email, attribs, listId, env) {
  const search = await listmonk(env, `/subscribers?search=${encodeURIComponent(email)}`);
  if (!search.ok) {
    console.error("listmonk search failed", search.status);
    return false;
  }
  const { data } = await search.json();
  const existing = data?.results?.find((s) => s.email.toLowerCase() === email.toLowerCase());
  if (!existing) {
    console.error("existing subscriber not visible to the API user");
    return false;
  }
  if (existing.status === "blocklisted") return "already";

  const lists = new Set(
    existing.lists.filter((l) => l.subscription_status !== "unsubscribed").map((l) => l.id),
  );
  // Someone who left our list earlier is put back without another email.
  const wasOnList = existing.lists.some((l) => l.id === listId);
  lists.add(listId);

  const res = await listmonk(env, `/subscribers/${existing.id}`, {
    method: "PUT",
    body: JSON.stringify({
      email: existing.email,
      name: existing.name,
      status: existing.status,
      lists: [...lists],
      attribs: { ...existing.attribs, ...attribs },
      preconfirm_subscriptions: true,
    }),
  });
  if (!res.ok) console.error("listmonk update failed", res.status, await res.text());
  return res.ok && (wasOnList ? "already" : "added");
}

// Best effort: a failed email should not fail the request. Skipped until a
// template ID is configured.
async function sendThanksEmail(email, env) {
  const templateId = Number(env.LISTMONK_WELCOME_TEMPLATE_ID);
  if (!(templateId > 0)) return;
  try {
    const res = await listmonk(env, "/tx", {
      method: "POST",
      body: JSON.stringify({
        subscriber_email: email,
        template_id: templateId,
        from_email: env.LISTMONK_FROM_EMAIL,
        content_type: "html",
      }),
    });
    if (!res.ok) console.error("thank-you email failed", res.status, await res.text());
  } catch (err) {
    console.error("thank-you email error", err);
  }
}

function str(value) {
  return typeof value === "string" ? value.trim() : "";
}

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}
