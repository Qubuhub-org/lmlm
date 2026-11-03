> For clean Markdown of any page on these docs, append `.md` to the page URL
> Full documentation index: https://you.com/docs/llms.txt
> Search over these docs using a free, read-only MCP server (it is the best way to pick the right API(s) for the job and understand how to use them): https://you.com/docs/_mcp/server
> Access web search, web fetch, and deep research tools using our product MCP server: https://api.you.com/mcp (use `/mcp/research` and `/mcp/finance` paths for Research and Finance Research respectively)
> Call live Web Search for free: append `?profile=free` to the MCP server path
> OpenAPI spec index: https://you.com/docs/openapi.json
> How to authenticate: https://you.com/docs/using-the-api/authentication
> Changelog: https://you.com/docs/changelog
> Full onboarding instructions for agents: https://you.com/SKILL.md

# Answer API Overview

> **Tip**
>
> The Answer API is REST-only—Product MCP has no `you-answer` tool. For search, contents, research, and finance, use [Product MCP](/docs/build-with-agents/mcp-server). Keyless `you-search` and `you-discover` are available at `https://api.you.com/mcp?profile=free`.

> **Install the Docs MCP server**
>
> The Docs MCP server lets your agent search over the entirety of these docs. Free to use.
>
> Install `https://you.com/docs/_mcp/server`. See the [Docs MCP Server guide](/docs/agents/docs-mcp-server) to learn more.

---

## What Is the Answer API?

The Answer API returns a synthesized natural-language answer with citations and the web results used to generate it.
Send a `query` with optional freshness, locale, domain, and explicit-content controls. The API retrieves web results and synthesizes an answer with inline citations.

Unknown or extra request fields are rejected.

---

## Endpoints

Each API has its own endpoint. Every request sends your API key in the `X-API-Key` header, except Inference Router requests, which send it as `Authorization: Bearer`.

| API                  | Endpoint                                                                                                                             | Guide                                     | API reference                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| Web Search API       | `POST https://ydc-index.io/v1/search` (also `GET`)                                                                                   | [Overview](/docs/guides/search)           | [/v1/search](/docs/api-reference/search/v1-search)                                  |
| Inference Router API | `POST https://api.you.com/v1/chat/completions` (OpenAI-compatible) and `POST https://api.you.com/v1/messages` (Anthropic-compatible) | [Overview](/docs/guides/inference-router) | [/v1/chat/completions](/docs/api-reference/inference-router/create-chat-completion) |
| Contents API         | `POST https://ydc-index.io/v1/contents`                                                                                              | [Overview](/docs/guides/contents)         | [/v1/contents](/docs/api-reference/contents)                                        |
| Answer API           | `POST https://api.you.com/v1/answer`                                                                                                 | [Overview](/docs/guides/answer)           | [/v1/answer](/docs/api-reference/answer/v1-answer)                                  |
| Research API         | `POST https://api.you.com/v1/research`                                                                                               | [Overview](/docs/guides/research)         | [/v1/research](/docs/api-reference/research/v1-research)                            |
| Finance Research API | `POST https://api.you.com/v1/finance_research`                                                                                       | [Overview](/docs/guides/finance-research) | [/v1/finance_research](/docs/api-reference/finance-research/v1-finance_research)    |

The Inference Router, Answer, Research, and Finance Research APIs run only on `api.you.com`. Sending one of those paths to `ydc-index.io` returns `403` with `{"message": "Missing Authentication Token"}`, even when the key is valid.

---

## How It Works

The Answer API runs a managed pipeline over the same retrieval and extraction infrastructure as the Web Search API and Contents API. For each query, it retrieves web results, pulls the most relevant supporting content, and synthesizes a cited answer in a single request. You don't configure search strategy, page reads, prompts, or model selection.

The API verifies that every citation exists in the source text and supports the answer before returning it. The `excerpts` in each citation are the verbatim passages the LLM used to construct the answer, so you can confirm accuracy without trusting the model alone.

On the SimpleQA benchmark, the Answer API reports 93.48% accuracy. Typical p50 latency is 2.67 seconds. There are no effort tiers to tune, so latency and cost stay predictable across queries.

---

## When to Use the Answer API

Use the Answer API when you want a cited Markdown answer from real-time web results in one call, with no `research_effort` or `output_schema` to configure.

Own the pipeline with the [Web Search API](/docs/guides/search) and [Contents API](/docs/guides/contents) when you need to choose the model, prompt, and citation logic yourself. Use the [Research API](/docs/guides/research) when you need `lite` through `frontier` depth, `source_control`, or structured JSON. If you already have URLs, need a finance-optimized index, or want MCP instead of REST, [Choose the Right API](/docs/choose-the-right-api) maps those jobs.

---

## What You Get

Every Answer API response includes:

* **`answer`**: A Markdown-formatted answer with numbered inline citations, such as `[[1, 2]]`, that reference items in the `citations` array.
* **`citations`**: The sources cited in the answer, in citation order. Each item contains a `source` URL and the verbatim `excerpts` the LLM used to construct the answer.
* **`results.web`**: All web results considered during answer synthesis, whether cited or not.

Each item in `results.web` includes a URL, title, and snippets. Source metadata can include `description`, `thumbnail_url`, and `page_age`, an ISO 8601 publication timestamp.

```json maxLines=30
{
  "answer": "The aurora borealis is caused by charged particles ejected from the Sun—carried by the solar wind and often intensified by solar flares or coronal mass ejections—that travel to Earth, are funneled by Earth's magnetic field toward the polar regions, and collide with oxygen and nitrogen atoms in the upper atmosphere. These collisions excite the atoms, which then release photons of light, creating the visible northern lights. [[1, 2]]",
  "citations": [
    {
      "source": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
      "excerpts": [
        "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions. These natural light shows are caused by magnetic storms that have been triggered by solar activity."
      ]
    },
    {
      "source": "https://www.valofinland.com/what-causes-the-colours-in-aurora-borealis/",
      "excerpts": [
        "When these particles reach Earth, they collide with gases in our atmosphere, such as oxygen and nitrogen. These collisions excite the gas particles, causing them to emit light."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
        "title": "How Auroras Form",
        "snippets": [
          "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions."
        ]
      }
    ]
  }
}
```

---

## Parameters

`query` is required. All other fields are optional.

| Parameter         | Type      | Required | Description                                                                                                                                                         |
| ----------------- | --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `query`           | string    | Yes      | The question or prompt to answer. Limited to 400 characters. Cannot be blank.                                                                                       |
| `freshness`       | string    | No       | `day`, `week`, `month`, `year`, or a date range in `YYYY-MM-DDtoYYYY-MM-DD` format                                                                                  |
| `country`         | string    | No       | Country code from the [supported set](/docs/api-reference/answer/v1-answer), such as `US`, `GB`, or `FR`, that determines the geographical focus of the web results |
| `language`        | string    | No       | Language tag from the [supported set](/docs/api-reference/answer/v1-answer), such as `EN`, `EN-GB`, or `FR`, that determines the language of the web results        |
| `safesearch`      | string    | No       | Explicit-content filtering for web results: `off`, `moderate` (default), or `strict`                                                                                |
| `include_domains` | string\[] | No       | Only return results from these domains. Max 500 domains. Cannot be used with `exclude_domains` or `boost_domains`                                                   |
| `exclude_domains` | string\[] | No       | Exclude results from these domains. Max 500 domains. Cannot be used with `include_domains`. Can be used with `boost_domains`                                        |
| `boost_domains`   | string\[] | No       | Prefer results from these domains without excluding other domains. Max 500 domains. Can be used with `exclude_domains`, but not with `include_domains`              |

[View full API reference](/docs/api-reference/answer/v1-answer)

Steer results with freshness, locale, domain filters, and safesearch. See [Search Controls](/docs/guides/answer/search-controls).

---

## Common Use Cases

### Question Answering in AI Applications

Use the Answer API in applications that need grounded, cited responses, including chatbots, copilots, and research tools. Send a question and get a sourced answer without configuring research effort.

### Content Pipelines

Use the Answer API as a research step before writing: ask a question, get a well-cited answer, and use that as source material for reports, articles, or briefings.

### Internal Knowledge Tools

Let employees ask complex questions—product comparisons, regulatory summaries, technical deep dives—and get sourced answers without manually reading dozens of pages.

---

## Best Practices

### Write Specific Questions for Better Answers

For complex topics, include context, constraints, or the specific angle you want covered. "What are the tradeoffs between PostgreSQL and MongoDB for a write-heavy workload at 10M rows?" produces a more focused answer than "Compare databases."

### Target Results with Search Controls

Set `freshness` when you need recent information. Select `country` and `language` from the [supported values](/docs/api-reference/answer/v1-answer) to control the region and language of web results. Set `safesearch` to control explicit-content filtering. Use `include_domains` for a strict allowlist, `exclude_domains` to remove unwanted sources, or `boost_domains` to prefer selected sources without filtering out other results. See [Search Controls](/docs/guides/answer/search-controls).

### Verify Citations for High-Stakes Use Cases

The inline citation numbers map to the `citations` array. For legal, financial, or medical contexts, build a step that follows each `source` URL and checks the supporting `excerpts` before surfacing claims to users.

### Use Research When Depth Matters More Than Speed

If your use case requires choosing between a quick factual answer and an exhaustive or frontier analysis, the Research API's `research_effort` parameter gives you that control.

---

## Pricing

See the [Billing page](/docs/administration/billing#answer-api) for complete pricing details.

For volume discounts, annual pricing, or enterprise features, visit [you.com/pricing](https://you.com/pricing) or contact [api@you.com](mailto:api@you.com).

---

## Data Retention

Organizations operating under strict privacy, compliance, or security mandates can add Zero Data Retention (ZDR) to an enterprise agreement. ZDR restricts retention of Answer API request and response content account-wide and requires no changes to your integration. See [Zero Data Retention](/docs/administration/zero-data-retention) for what it covers and how to enable it.

---

## Next Steps

#### [Quickstart](/docs/guides/answer/quickstart)

Make your first Answer API request

#### [Search Controls](/docs/guides/answer/search-controls)

Freshness, locale, domain filters, and safesearch

#### [API Reference](/docs/api-reference/answer/v1-answer)

Full parameter reference, request/response schemas, and interactive playground

#### [Research API](/docs/guides/research)

Control research depth with effort levels when thoroughness matters
