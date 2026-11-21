import { WorkerEntrypoint } from "cloudflare:workers";

// Named service binding entrypoint; configure the binding as WORKER_B.
export class WorkerB extends WorkerEntrypoint {
  async fetch() {
    return new Response(null, { status: 404 });
  }

  async add(a, b) {
    if (!Number.isFinite(a) || !Number.isFinite(b)) {
      throw new TypeError("add expects finite numbers");
    }
    return a + b;
  }
}

// Default HTTP entrypoint. Keep one default export per ES module.
export default {
  async fetch(_request, env) {
    const result = await env.WORKER_B.add(1, 2);
    return new Response(String(result), {
      headers: { "content-type": "text/plain; charset=utf-8" },
    });
  },
};
