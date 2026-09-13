# Review skill

## Trigger

Run this skill before declaring a slice or release candidate reviewed.

## Objective

Audit the working diff against intent, boundaries, security, UX, operations, and maintainability.

## Review checklist

### Product
- Does it implement the selected slice, not a new desire?
- Does each visible behavior match the acceptance criterion?

### Correctness
- Are contracts, ownership, boundaries, and failure paths correct?
- Are resources released and transactions idempotent where needed?

### Security
- Validate input and encode output at boundaries.
- Enforce authorization on every sensitive action and object.
- Keep secrets and credentials outside source.
- Rate limit public or expensive operations.
- Log security events without leaking secrets or personal identifiers.

### UX / UI
- The user can understand what happened.
- Loading, empty, error, retry, permission-denied, mobile, and keyboard paths are usable.
- Copy has no internal jargon; technical details are not exposed as end-user choices.

### Backend
- Contracts are explicit.
- Data integrity, transactions, retries, timeouts, and backpressure are clear.
- Observability exists for errors, latency, and important business state.

### Maintainability
- Names explain the domain.
- Tests do not over-couple to private details.
- Dependencies are justified.
- Operations have a rollback and recovery path.

## Output

Create or update `docs/REVIEW.md` with:

```markdown
# Review

## Verdict
<!-- Approve / approve with follow-ups / request changes. -->

## Evidence
<!-- Reviewed diff range, commands, screenshots, manual results. -->

## Findings
| Severity | Finding | Action | Owner |
| --- | --- | --- | --- |
| blocker | ... | ... | ... |

## Residual risks
...
```

## Verification

```bash
git diff --check
git diff --stat
rg -n "TODO|FIXME|HACK" affected-files
```

Do not approve while a blocker or unexplained security/authorization finding remains.

## Done

- Every finding has one owner and one action.
- There is evidence, not a general impression.
- No release blocker is unresolved.
