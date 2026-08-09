/**
 * Renan the Teacher — AI English Teacher backend
 * -----------------------------------------------------------------
 * Deployed as a Cloudflare Worker (NOT part of the GitHub Pages
 * static site — this file lives outside assets/ and is deployed
 * separately via `wrangler deploy`). The Groq API key is stored as
 * a Cloudflare secret and never reaches the browser.
 *
 * Responsibilities:
 *   1. CORS: only accept requests from the course website's origin.
 *   2. Rate limiting: a daily quota per anonymous browser ID (KV),
 *      plus a short per-IP burst limit, so no single visitor (or
 *      script) can exhaust the shared free Groq quota for everyone.
 *   3. Call Groq (openai/gpt-oss-120b primary, falling back to
 *      openai/gpt-oss-20b if the primary model's daily quota is
 *      already used up) with a scoped English-teacher system prompt.
 *   4. Return only the reply text to the browser — nothing else.
 *
 * See worker/README.md for setup and deployment instructions.
 */

// ---- Configuration -------------------------------------------------

// Update this to your real GitHub Pages origin (no trailing slash).
const ALLOWED_ORIGIN = "https://renangrossi.github.io";

// Anonymous, per-browser daily quota. Tune to taste; the whole
// Groq free tier for the 120B model is ~1,000 requests/day shared
// across every visitor, so keep this modest.
const DAILY_LIMIT_PER_ANON = 20;

// Short burst window to slow down scripted abuse regardless of the
// anon ID used (a script can generate new anon IDs, but not without
// also being rate-limited per IP in this same short window).
const BURST_LIMIT_PER_IP = 8;
const BURST_WINDOW_SECONDS = 60;

const MAX_MESSAGE_LENGTH = 600; // characters, matches the frontend's maxlength
const MAX_HISTORY_MESSAGES = 12; // 6 user/assistant turns
const MAX_REPLY_TOKENS = 350; // keeps answers focused and keeps costs/latency low

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const PRIMARY_MODEL = "openai/gpt-oss-120b";
const FALLBACK_MODEL = "openai/gpt-oss-20b";

const SYSTEM_PROMPT = `You are the AI English Teacher for "Renan the Teacher's English Course," a CEFR-aligned (A1-C2) English learning website.

Your role:
- Help students with English grammar, vocabulary, pronunciation guidance, sentence construction, reading, writing, speaking and listening.
- Explain clearly, adapt to the student's apparent level, and give short examples.
- When correcting a mistake, explain WHY it's wrong before giving the correct form.
- When asked for an exercise, create one appropriate to the requested (or implied) CEFR level.
- End many answers with a short follow-up practice question or prompt, to encourage active learning.
- Keep answers concise and focused — a few short paragraphs at most, not an essay, unless the student explicitly asks for something longer (like a full exercise set).

Strict scope:
- You are ONLY the English-course assistant. If a student asks something unrelated to learning English (general chit-chat, other subjects, personal advice, current events, etc.), politely say you're the English course assistant and steer them back to an English-learning question. Do this briefly and kindly, without lecturing.
- Never claim a fact, resource, or exercise is "from the course" unless the student's own message already told you it is — you don't have direct access to the site's file contents, only to this instruction.
- Never ask for or store personal information. If a student shares personal details, respond helpfully to the English content without dwelling on the personal information.

Style:
- Warm, encouraging, and patient — this is often a student's first interaction with the site.
- Use simple, clear language yourself, especially for lower-level (A1-A2) questions.
- Use CEFR terminology (A1, A2, B1, B2, C1, C2) naturally when relevant.`;

// ---- Helpers ---------------------------------------------------------

function corsHeaders(origin) {
  var allow = origin === ALLOWED_ORIGIN ? origin : ALLOWED_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function jsonResponse(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: Object.assign({ "Content-Type": "application/json" }, corsHeaders(origin)),
  });
}

function dayKey() {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD, UTC
}

async function checkAndIncrement(kv, key, limit, ttlSeconds) {
  var current = await kv.get(key);
  var count = current ? parseInt(current, 10) : 0;
  if (count >= limit) return false;
  await kv.put(key, String(count + 1), { expirationTtl: ttlSeconds });
  return true;
}

async function callGroq(env, model, messages) {
  var res = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + env.GROQ_API_KEY,
    },
    body: JSON.stringify({
      model: model,
      messages: messages,
      max_completion_tokens: MAX_REPLY_TOKENS,
      temperature: 0.4,
    }),
  });
  return res;
}

// ---- Main handler ------------------------------------------------

export default {
  async fetch(request, env, ctx) {
    var origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders(origin) });
    }
    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed" }, 405, origin);
    }
    if (origin !== ALLOWED_ORIGIN) {
      return jsonResponse({ error: "Origin not allowed" }, 403, origin);
    }

    var payload;
    try {
      payload = await request.json();
    } catch (e) {
      return jsonResponse({ error: "Invalid request body" }, 400, origin);
    }

    var message = (payload.message || "").toString().trim();
    var anonId = (payload.anonId || "").toString().slice(0, 80);
    var historyIn = Array.isArray(payload.history) ? payload.history : [];

    if (!message) {
      return jsonResponse({ error: "Empty message" }, 400, origin);
    }
    if (message.length > MAX_MESSAGE_LENGTH) {
      return jsonResponse({ error: "Message too long" }, 400, origin);
    }
    if (!anonId) {
      return jsonResponse({ error: "Missing client identifier" }, 400, origin);
    }

    // --- Rate limiting -------------------------------------------------
    var ip = request.headers.get("CF-Connecting-IP") || "unknown";
    var burstKey = "burst:" + ip;
    var dailyKey = "daily:" + anonId + ":" + dayKey();

    var burstOk = await checkAndIncrement(env.AI_TEACHER_KV, burstKey, BURST_LIMIT_PER_IP, BURST_WINDOW_SECONDS);
    if (!burstOk) {
      return jsonResponse({ error: "Too many requests, please slow down." }, 429, origin);
    }
    var dailyOk = await checkAndIncrement(env.AI_TEACHER_KV, dailyKey, DAILY_LIMIT_PER_ANON, 60 * 60 * 24);
    if (!dailyOk) {
      return jsonResponse({ error: "Daily limit reached" }, 429, origin);
    }

    // --- Build the message list for Groq --------------------------
    var cleanHistory = historyIn
      .filter(function (m) { return m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string"; })
      .slice(-MAX_HISTORY_MESSAGES)
      .map(function (m) { return { role: m.role, content: String(m.content).slice(0, MAX_MESSAGE_LENGTH) }; });

    var messages = [{ role: "system", content: SYSTEM_PROMPT }]
      .concat(cleanHistory)
      .concat([{ role: "user", content: message }]);

    // --- Call Groq, with a fallback model if the primary is out of quota
    try {
      var res = await callGroq(env, PRIMARY_MODEL, messages);
      if (res.status === 429) {
        res = await callGroq(env, FALLBACK_MODEL, messages);
      }
      if (!res.ok) {
        var errText = await res.text();
        console.error("GROQ_BODY: " + res.status + " " + errText);
        return jsonResponse({ error: "AI provider error" }, 502, origin);
      }
      var data = await res.json();
      var reply = data && data.choices && data.choices[0] && data.choices[0].message
        ? data.choices[0].message.content
        : "Sorry, I couldn't generate a response. Please try again.";
      return jsonResponse({ reply: reply }, 200, origin);
    } catch (err) {
      console.error("Worker error:", err);
      return jsonResponse({ error: "Unexpected server error" }, 500, origin);
    }
  },
};



