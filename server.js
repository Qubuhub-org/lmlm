import express from "express";
import { pathToFileURL } from "node:url";

const app = express();
const PORT = Number.parseInt(process.env.PORT ?? "3000", 10);
const MAX_MESSAGE_LENGTH = 8_000;
const ALLOWED_ORIGINS = new Set(
  (process.env.CORS_ORIGINS ?? "http://localhost:3000,http://127.0.0.1:3000")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean),
);
const JOKE_CATEGORIES = new Set([
  "Any", "Programming", "Misc", "Dark", "Pun", "Spooky", "Christmas",
]);
const JOKE_TYPES = new Set(["Any", "single", "twopart"]);
const JOKE_LANGUAGES = new Set(["en", "es", "de", "fr", "pt", "cs", "it"]);

app.disable("x-powered-by");
app.use((req, res, next) => {
  const origin = req.get("origin");
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Vary", "Origin");
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  }
  if (req.method === "OPTIONS") return res.sendStatus(204);
  return next();
});
app.use(express.json({ limit: "16kb", strict: true }));

app.get("/healthz", (_req, res) => {
  res.json({ status: "ok", service: "lmlm-api" });
});

// This endpoint intentionally remains a mock; it does not call a hosted model.
app.post("/api/chat", (req, res) => {
  const { message } = req.body ?? {};
  if (typeof message !== "string" || message.trim().length === 0) {
    return res.status(400).json({ error: "message must be a non-empty string" });
  }
  if (message.length > MAX_MESSAGE_LENGTH) {
    return res.status(413).json({ error: `message must be at most ${MAX_MESSAGE_LENGTH} characters` });
  }
  return res.json({ reply: `You said: "${message}". This is a test AI reply.` });
});

app.get("/api/joke", async (req, res) => {
  const category = typeof req.query.category === "string" ? req.query.category : "Any";
  const type = typeof req.query.type === "string" ? req.query.type : "Any";
  const lang = typeof req.query.lang === "string" ? req.query.lang : "en";
  const safeMode = req.query.safeMode === "true";

  if (!JOKE_CATEGORIES.has(category) || !JOKE_TYPES.has(type) || !JOKE_LANGUAGES.has(lang)) {
    return res.status(400).json({ error: "Unsupported joke category, type, or language" });
  }

  const url = new URL(`https://v2.jokeapi.dev/joke/${category}`);
  url.search = new URLSearchParams({
    type,
    lang,
    ...(safeMode ? { blacklistFlags: "explicit" } : {}),
  }).toString();

  try {
    const upstream = await fetch(url, { signal: AbortSignal.timeout(5_000) });
    if (!upstream.ok) {
      return res.status(502).json({ error: "Joke provider returned an error" });
    }
    const data = await upstream.json();
    return res.json(data);
  } catch {
    return res.status(502).json({ error: "Joke provider is unavailable" });
  }
});

export { app };

const invokedPath = process.argv[1] ? pathToFileURL(process.argv[1]).href : "";
if (import.meta.url === invokedPath) {
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`LMLM API listening on port ${PORT}`);
  });
}
