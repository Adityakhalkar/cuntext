# nextjs-project example

**What this is:** Codebase context for a coding agent working on a Next.js 14 project. Not an API — no HTTP endpoints, no auth headers. This demonstrates that cuntext is not limited to API documentation: it encodes *any* structured knowledge an agent needs.

**What kind of agent loads this:** A coding agent (e.g. Claude Code, Cursor, a custom agent) dropped into an unfamiliar Next.js codebase. Instead of grep-ing through files or loading the full README, it loads the index to orient itself, then pulls only the fragment relevant to its task.

**`base=./`** — the base is the local filesystem, not a URL. Fragments contain architectural knowledge, not endpoint definitions.

**Files:**
- `index.cuntext` — stack, file layout, quick-ref to entry points (~150 tokens)
- `fragments/architecture.cuntext` — routing conventions, component rules, how to add a feature
- `fragments/patterns.cuntext` — common errors, debugging, server action patterns
- `fragments/testing.cuntext` — test setup, what to test, example patterns
- `fragments/styling.cuntext` — Tailwind conventions, shadcn/ui, dark mode
- `fragments/data-flow.cuntext` — read/write paths, caching, auth guard, pagination

**Typical agent load:**
- Adding a feature: index + architecture (~330 tokens)
- Debugging: index + patterns (~350 tokens)
- Writing tests: index + testing + architecture (~550 tokens)

**How to use:** Copy and adapt `index.cuntext` for your own project. Update stack, file paths, and goals to match. Add or remove fragments as needed.
