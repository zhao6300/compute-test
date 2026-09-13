# Data/storage skill

Use this skill before creating an object, table, index, file store, cache entry, queue item, or migration.

## Required definition

For every entity or store:

1. Owner and lifecycle.
2. Unique identity and collision strategy.
3. Required fields and validation.
4. Optional fields and defaults.
5. Relationships, ownership, and referential integrity.
6. Retention, archival, deletion, and backup behavior.
7. Access-control boundary.
8. Migration and rollback strategy.

Schema changes need a reversible migration path, not only an initial creation script.

## Integrity rules

1. Prefer database constraints over application-only checks.
2. Use transactions for multi-step invariants.
3. Make repeated writes idempotent or guarded by a unique key.
4. Avoid orphaned objects when ownership changes.
5. Preserve audit-relevant events or immutable records that the product needs.
6. Separate migration data changes from release behavior when backward compatibility matters.
7. Make index and lock impact reviewable.

## Verification

For data changes, capture:

1. Migration up.
2. Migration down.
3. Duplicate-write attempt.
4. Invalid write rejection.
5. Missing-owner deletion or an explicit product decision to allow it.
6. Backup and retention confirmation where user data is created.
7. Rollback evidence when schema/behavior is irreversible.

A migration is not safe when it passes only because the table was empty.
