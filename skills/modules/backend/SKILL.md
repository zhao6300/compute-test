# Backend service skill

## Use

Apply this skill to workflows, services, background jobs, integrations, and database-facing code.

## Required definition

For each operation, define:

1. Responsible service or worker.
2. Inputs, outputs, and status codes as typed schemas, not prose only.
3. Permissions checked at the resource level, not just at authentication.
4. Valid and invalid state transitions.
5. Retry, timeout, idempotency, and compensation semantics.
6. Rollback behavior.
7. Internal diagnostics and user-safe response copy.

Do not create "temporary only" backend endpoints without they own test and removal plan.

## Failure rules

1. External calls need timeouts and bounded retry.
2. User-visible actions handle duplicate submission safely.
3. Multi-write paths use transactions or an explicit compensating action.
4. Partial failures never leave silently inconsistent state.
5. Infrastructure failures are distinguishable from normal business validation failures.
6. Authentication and authorization are logged or observed at boundaries.
7. Rate limits and quotas are considered for public or expensive operations.

## Observability

Before release, the operation must expose:

1. Structured logs with request ID and operation result.
2. Error rate.
3. Request duration.
4. Request volume.
5. Critical state changes or business events.
6. Dependency failure and saturation metrics.
7. A runbook message for the expected alert.

Core tenant, permission, administrative, and destructive actions should have audit traces.

## Verification

Run a test or demo showing:

1. The success HTTP response and persisted state.
2. One invalid input rejection with a clear error.
3. One unauthorized resource denial.
4. One dependency timeout or failure handled safely.
5. One idempotency or duplicate-action check.
6. Metric or trace evidence for a call.

Do not claim done from code inspection alone when the operation changes user-visible state.
