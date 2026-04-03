# cuntext

The file format for context engineering.

Not just API documentation. Any structured knowledge an agent might need — APIs, codebases, workflows, policies, domain knowledge — encoded as static files that agents load surgically, paying only for what the task requires.

---

## The problem

LLM agents are expensive. Not because of compute — because of context.

Every tool, API, codebase, or knowledge base an agent might reference gets loaded up front. Most of it is irrelevant to the actual task. Formats designed for humans (Markdown, OpenAPI, llms.txt) don't know what the agent is trying to do, so they can't filter.

Context engineering — deciding what enters an LLM's context window, when, and how much — is already a discipline. cuntext is its file format.

---

## Design principles

**Goal-oriented.** Agents know what they want to do, not what knowledge exists. cuntext indexes are keyed by intent: `debug-issue`, `run-code`, `process-refund` — not by endpoint, topic, or category.

**Two-level.** A tiny index (~200 tokens) is always loaded. Fragments (~100–400 tokens each) are loaded on demand. The agent pays only for what the task requires.

**Static.** Just files. Serve them anywhere. No embedding pipelines, no running servers, no infrastructure.

**Dense.** No prose, no decorators. Pattern-matchable schema optimized for machine parsing, not human reading.

---

## What it covers

cuntext encodes any structured knowledge:

| Context type | Without cuntext | With cuntext |
|---|---|---|
| REST API | OpenAPI (3k–15k tokens) | index + fragment (~300–600t) |
| Codebase | README + grep | goal-oriented architecture map |
| Workflow | Prose SOP | step-indexed fragment set |
| Policy / rules | Full document | indexed by scenario |
| Domain knowledge | Full corpus | indexed by task |
| Agent memory | Ad-hoc prompt injection | structured preference fragments |

The invariant: **agents know what they want to do. cuntext meets them there.**

---

## Token comparison

| Format | Typical tokens | Lazy loading |
|--------|---------------|--------------|
| OpenAPI spec | 3,000–15,000 | No |
| Markdown README | 500–3,000 | No |
| llms.txt | 300–1,000 | No |
| cuntext index | ~200 | — |
| cuntext index + fragment | ~300–600 | Yes |

---

## Examples

- [`examples/greed-compute/`](examples/greed-compute/) — REST API documentation (reference implementation)
- [`examples/nextjs-project/`](examples/nextjs-project/) — codebase context for coding agents

---

## The format

### index.cuntext

```
{NAME} v{VERSION}
base={url_or_path}
[auth=header:{HeaderName}]
[auth-setup={how to get credentials}]
[format=json content-type=application/json]

goals:
  {what the agent wants to do}  → fragments/{name}.cuntext

quick-ref:
  {label}  {compact reference}

[on-error: {code}={brief} ...]
[errors: → fragments/errors.cuntext]
```

### fragments/*.cuntext

```
{NAME} [{human description}]
[deps={space-separated fragment names}]

{operation}:
  {METHOD} /path
  [body: {field:type, optional?:type}]
  → {response shape}
  [note: caveat]

[ex:
  # inline example]
```

---

## Type conventions

`str` `int` `float` `bool` `any` `[type]` `type|null` — `field?` = optional — `→` = response — `ex:` = example block — `note:` = caveat — `deps=` = also load these — `[SSE]` = server-sent events

---

## Discovery

Serve your index at `yourdomain.com/llms.cuntext`. Agents find it without being told.

Static files. Zero infrastructure.

---

## Spec

[SPEC.md](SPEC.md) — formal grammar, all field definitions, versioning.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) — how to write `.cuntext` files for your own context.
