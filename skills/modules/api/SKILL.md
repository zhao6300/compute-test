# API skill

Use this skill for every public, partner, service-to-service, or generated client API.

## Contract file

Before implementation, record:

1. Resource / operation and its purpose.
2. Request and response schema.
3. Error names and retry behavior.
4. Pagination and filtering rule.
5. Authentication and authorization boundary.
6. Rate limit.
7. Idempotency key when a repeat can be harmful.
8. Deprecation and versioning policy.
9. Breaking-change communication path.
10. Contract test command.

Do not return the storage model directly just because it exists.

## Validation rules

1. Validate type, length, enum, relationship, and permissions.
2. Distinguish client validation failures from server faults.
3. Avoid leaking implementation details as `db error`, raw stack, or internal identifier family.
4. Return stable and explicit error codes.
5. Do not let one tenant query or write another tenant's object through lookup.
6. Keep a single source of truth for schemas across docs, server, clients, and tests.
7. Capture latency and failure metrics per operation.
8. Document how access tokens, credentials, and audit records are protected.

## Verification

Do not declare a contract stable until these pass:

1. A successful call.
2. Invalid input.
3. Missing auth.
4. Cross-tenant or unauthorized access.
5. Not found.
6. Expired/invalid credential.
7. Rate limit.
8. Contract-to-schema comparison.

Record generated client versions or changelog entries so callers can upgrade without guessing.
