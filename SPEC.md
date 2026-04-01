# cuntext Specification v0.1

## Overview

cuntext is a file format for machine-consumable context. A cuntext document encodes structured knowledge as a two-level hierarchy: an index and a set of fragments. The design principle is goal-orientation — content is indexed by what an agent wants to accomplish, not by what content exists.

cuntext is domain-agnostic. It works equally for API documentation, codebase knowledge, workflow definitions, policy references, domain expertise, and agent memory.

---

## File format

- Extension: `.cuntext`
- Encoding: UTF-8
- Line endings: LF
- No binary content
- No required dependencies or tooling — plain text files

---

## Index file

Filename: `index.cuntext`

### Structure

```
{NAME} v{VERSION}
{key=value metadata lines}

goals:
  {intent}  → fragments/{fragment-name}.cuntext
  ...

quick-ref:
  {label}  {reference}
  ...

[on-error: {code}={summary} ...]
[errors: → fragments/errors.cuntext]
```

### Line 1: header

Must be the first line. Format: `{NAME} v{VERSION}`

- `NAME`: uppercase, hyphenated identifier for the context (e.g. `GREED-COMPUTE`, `NEXTJS-PROJECT`)
- `VERSION`: semver or single integer (e.g. `1`, `1.2`)

### Metadata keys

Key-value pairs on lines immediately following the header.

| Key | Required | Description |
|-----|----------|-------------|
| `base` | Yes | Base URL or path. URL for remote contexts, `./` for local codebase contexts |
| `auth` | No | Auth scheme: `header:{HeaderName}`, `bearer`, or `none` |
| `auth-setup` | No | How to obtain credentials |
| `format` | No | Default request format (e.g. `json`) |
| `content-type` | No | Default content-type header value |

### goals block

Required. Maps agent intent strings to fragment files.

```
goals:
  run-code                  → fragments/exec.cuntext
  save-restore-state        → fragments/checkpoint.cuntext
```

- Intent strings: lowercase, hyphenated natural language describing what the agent wants to do
- One mapping per line, two-space indent
- `→` separator (U+2192) or ASCII `->` both accepted

### quick-ref block

Optional. Compact one-line references — enough for an agent to infer patterns without loading fragments.

```
quick-ref:
  session.create  POST /sessions
  checkpoint      POST /sessions/{id}/checkpoint  body:{name:str}
```

### on-error

Optional. Inline error summaries for common codes so agents can handle routine failures without loading the errors fragment.

```
on-error: 401=missing-or-invalid-key 429=rate-limited-backoff-and-retry
```

---

## Fragment files

Filename: `fragments/{name}.cuntext`

Names: lowercase, hyphenated.

### Structure

```
{NAME} [{human description}]
[deps={space-separated fragment filenames}]

{operation-name}:
  {METHOD} /path
  [body: {field:type, field?:type}]
  → {response shape}
  [note: caveat]

[ex:
  # example lines]
```

### Line 1: header

Format: `{NAME} [{description}]`

- `NAME`: uppercase identifier matching the fragment purpose
- `description`: optional, bracket-enclosed human label

### deps

Declares other fragments the agent should also load for complete context. Space-separated filenames.

```
deps=index.cuntext exec.cuntext
```

Advisory — agents may load transitively. Load order is not specified.

### Operation blocks

Each block describes one operation or concept.

```
operation-name:
  METHOD /path
  body: {field:type, optional?:type}
  → {response shape}
  note: important caveat
```

- `body:` omitted if no request body
- `→` response shape uses the same type system
- `note:` for non-obvious constraints, one line
- Multiple operations per fragment are allowed

### ex block

Inline example. Use `#` for comments.

```
ex:
  # create a session
  POST /sessions {} → {"session_id":"abc123"}
```

---

## Type system

| Symbol | Meaning |
|--------|---------|
| `str` | String |
| `int` | Integer |
| `float` | Floating point |
| `bool` | Boolean |
| `any` | Any JSON value |
| `[type]` | Array of type |
| `type\|null` | Nullable |
| `field?` | Optional field |
| `→` | Response shape |
| `ex:` | Example block |
| `note:` | Caveat or constraint |
| `deps=` | Fragment dependencies |
| `[SSE]` | Server-sent events stream |
| `iso8601` | ISO 8601 datetime string |
| `204` | Empty response (HTTP 204 No Content) |

---

## Discovery

A conforming index file served at `{origin}/llms.cuntext` is the standard auto-discovery path.

```
GET https://yourdomain.com/llms.cuntext
```

Alternate conventional path: `{base}/cuntext/index.cuntext`

Agents discovering a new base URL should check the discovery path before requesting documentation through other means.

---

## Versioning

- Index files declare version in the header line: `NAME v{MAJOR}` or `NAME v{MAJOR}.{MINOR}`
- Breaking changes (removed goals, changed fragment paths, incompatible type changes) increment MAJOR
- Additive changes (new goals, new operations, new fields) increment MINOR
- Fragment files do not independently version; they inherit the index version

---

## Conformance

A conforming **index file** MUST:
- Begin with `{NAME} v{VERSION}` on line 1
- Include a `base=` metadata key
- Include a `goals:` block with at least one entry
- Use UTF-8 encoding
- Target ≤ 250 tokens (advisory)

A conforming **fragment file** MUST:
- Begin with `{NAME}` on line 1
- Contain at least one operation or reference block
- Declare `deps=` if it assumes context from another fragment
- Target ≤ 400 tokens (advisory)

---

## Relation to prior art

| Format | Designed for | Lazy loading | Goal-oriented | Zero infrastructure |
|--------|-------------|:------------:|:-------------:|:-------------------:|
| OpenAPI | Code generation | No | No | Yes |
| llms.txt | LLM context | No | No | Yes |
| MCP | Tool execution | — | No | No |
| RAG | Semantic retrieval | Yes | No | No |
| **cuntext** | **Agent context** | **Yes** | **Yes** | **Yes** |

---

## Changelog

### v0.1
- Two-level index + fragment model
- Goal-oriented indexing
- `deps=` transitive loading
- Type system
- Discovery convention at `/llms.cuntext`
- Domain-agnostic: APIs, codebases, workflows, any structured knowledge
