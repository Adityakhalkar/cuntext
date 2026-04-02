# greed-compute example

**What this is:** `.cuntext` documentation for the [greed-compute](https://deep-ml.com) API — a stateful Python execution service for AI agents.

**What kind of agent loads this:** Any agent that needs to run code, save/restore state, or coordinate parallel workers. The index is small enough to include in every system prompt; fragments are pulled only when needed.

**Files:**
- `index.cuntext` — goals, quick-ref, auth setup, common errors (~200 tokens)
- `fragments/exec.cuntext` — create sessions, run code, stream output
- `fragments/checkpoint.cuntext` — save and restore Python interpreter state
- `fragments/swarm.cuntext` — parallel map-reduce across worker sessions
- `fragments/workspace.cuntext` — shared state across multiple agents and models
- `fragments/billing.cuntext` — usage, quotas, tier limits
- `fragments/errors.cuntext` — full error reference

**Discovery:** greed-compute serves these files directly from the API at:
```
GET https://compute.deep-ml.com/v1/cuntext/index.cuntext
GET https://compute.deep-ml.com/v1/cuntext/fragments/:name
GET https://compute.deep-ml.com/llms.cuntext  (auto-discovery alias)
```

**Typical agent load:** index + exec (~350 tokens total) to run code. Add checkpoint (~250 tokens) only if the agent needs to save state.
