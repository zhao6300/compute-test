# Verify skill

## Trigger

Run this skill after review begins or immediately after integration.

## Objective

Create launch evidence from a running, observed process rather than a checklist claim.

## Build evidence

1. Clean install.
2. Build.
3. Lint, typecheck, tests, and migrations.
4. Dependency and secret scanning.
5. Runtime smoke test.

## Runtime evidence

1. Health and readiness endpoints respond correctly.
2. Structured logs include request ID, actor-safe context, and errors.
3. RED metrics are emitted: rate, errors, duration.
4. Slow dependency and normal paths emit traces.
5. Health checks, retries, circuit breaking, timeouts, and recovery behavior are tested.
6. Logs, config, PII, cache, and audit data have retention and purge rules.

## Performance evidence

Record baseline and degradation:

1. Normal load response time.
2. Peak-load response time.
3. Error rate under peak load.
4. Resource saturation.
5. Frontend LCP / INP / CLS for user-visible pages.
6. Parallel/action-launch contention for agent-heavy products.

## Reliability evidence

1. One upstream dependency timeout is handled.
2. One database connection failure is handled.
3. One duplicate request is idempotent.
4. One restart or rollback path works.
5. Rollback is rehearsed, not only documented.

## Output

Create or update `docs/VERIFY.md`:

| Gate | Evidence | Command / operation | Status |
| --- | --- | --- | --- |
| Build | ... | ... | pass |
| Tests | ... | ... | pass |
| Security | ... | ... | pass |
| Performance | ... | ... | pass/targeted |
| Observability | ... | ... | pass |

## Verification

```bash
<smoke command>
<observability evidence collection command>
<one recovery drill>
```

## Done

- Each gate has either pass or explicit `targeted` with a follow-up.
- At least one recovery path is actually demonstrated.
- A human unfamiliar with the code can follow the evidence.
