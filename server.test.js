import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { app } from "./server.js";

async function withServer(run) {
  const server = createServer(app);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  try {
    await run(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
}

test("health endpoint reports service status", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/healthz`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { status: "ok", service: "lmlm-api" });
  });
});

test("chat endpoint preserves mock response for valid messages", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/api/chat`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ message: "hello" }),
    });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      reply: 'You said: "hello". This is a test AI reply.',
    });
  });
});

test("chat endpoint rejects missing and invalid messages", async () => {
  await withServer(async (base) => {
    for (const body of [{}, { message: 42 }, { message: "   " }]) {
      const response = await fetch(`${base}/api/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      assert.equal(response.status, 400);
    }
  });
});

test("joke proxy rejects unsupported query values before making a request", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/api/joke?category=https%3A%2F%2Fexample.com`);
    assert.equal(response.status, 400);
    assert.deepEqual(await response.json(), {
      error: "Unsupported joke category, type, or language",
    });
  });
});

test("CORS does not reflect an untrusted origin", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/healthz`, {
      headers: { origin: "https://untrusted.example" },
    });
    assert.equal(response.headers.get("access-control-allow-origin"), null);
  });
});
