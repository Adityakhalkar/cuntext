# Contributing to cuntext

This covers two things: (a) writing `.cuntext` files for your own API or knowledge base, (b) contributing to the cuntext spec and examples in this repo.

---

## Writing cuntext files for your context

### 1. Start with the goals block

Before writing any fragments, answer: **what would an agent want to do with this context?**

Not "what does my API have" — not "what topics do my docs cover" — what are the actual agent intents?

```
# Wrong: structure-oriented
goals:
  GET /users          → fragments/users.cuntext
  POST /sessions      → fragments/sessions.cuntext

# Right: goal-oriented
goals:
  authenticate-user   → fragments/auth.cuntext
  manage-session      → fragments/sessions.cuntext
  run-code            → fragments/exec.cuntext
```

This applies equally to non-API contexts:

```
# Codebase context
goals:
  add-feature         → fragments/architecture.cuntext
  debug-issue         → fragments/patterns.cuntext
  write-tests         → fragments/testing.cuntext

# Policy context
goals:
  check-data-handling → fragments/gdpr.cuntext
  review-retention    → fragments/retention.cuntext
```

### 2. Write focused fragments

Each fragment should be self-contained for its goal:

- Include only the operations or knowledge needed for that goal
- Add `deps=` if the fragment assumes another is loaded
- Write one `ex:` block showing real usage
- Add `note:` for any non-obvious constraint

### 3. Keep it dense

No prose. No section headers. No explanatory sentences. Write like you're paying per token — because agents are.

```
# Wrong
## Create a session
To create a new session, send a POST request to the /sessions endpoint.
The request body should include the optional ttl_secs parameter...

# Right
session.create:
  POST /sessions
  body: {ttl_secs?:int}
  → {session_id:str, expires_at:iso8601}
```

### 4. Declare deps honestly

If your fragment uses concepts or types defined elsewhere, declare them:

```
CHECKOUT [process a payment]
deps=index.cuntext products.cuntext auth.cuntext
```

### 5. Token targets

- `index.cuntext`: aim for ≤ 250 tokens
- Each fragment: aim for ≤ 400 tokens
- If a fragment exceeds 400 tokens, split it by goal — not by topic

### 6. The quick-ref test

Read only your `index.cuntext`. Could an agent infer enough to attempt the most common operation without loading any fragment? If yes, your quick-ref is good. If no, add more hints.

---

## File checklist

- [ ] `index.cuntext` starts with `{NAME} v{VERSION}` on line 1
- [ ] `base=` is present
- [ ] At least 3 goals mapped to fragments
- [ ] `quick-ref:` has enough hints to infer common operations
- [ ] `auth-setup=` present if auth is required
- [ ] `on-error:` covers the most common failure codes (if applicable)
- [ ] Each fragment declares `deps=` if it assumes other fragments
- [ ] Each fragment has at least one `ex:` block
- [ ] Token count: index ≤ 250, each fragment ≤ 400

---

## Contributing to this repo

### Adding an example

Examples live in `examples/{name}/`. A good example:

- Represents a real or realistic context (not toy data)
- Has a goals block with ≥ 4 intents
- Has ≥ 3 fragments
- Is **not** another REST API if we already have REST API examples — show a different context type (codebase, workflow, policy, domain knowledge)
- Includes a brief README explaining what the context represents and what kind of agent would load it

Submit as a PR.

### Proposing spec changes

1. Open an issue describing the problem
2. Reference the SPEC.md section you're proposing to change
3. Include a motivating example showing what the current spec can't express
4. Show the before/after token impact if relevant

Spec changes that add new syntax require at least one example implementation before merging.
