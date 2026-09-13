# Test skill

## Trigger

Run this skill after an implementation slice appears locally complete.

## Objective

Prove acceptance behavior, boundaries, failures, and regressions with repeatable checks.

## Output

Create or update `docs/TEST_PLAN.md` with:

| Case | Level | Input | Expected | Automation |
| --- | --- | --- | --- | --- |
| Core loop | integration | ... | ... | command |
| Validation | unit | invalid input | safe error | command |
| Permission | integration | unauthorized user | denied | command |
| Empty state | UI/component | no data | meaningful state | command/manual |
| Failure path | integration | dependency down | recoverable error | command/manual |
| Long task | UI/component | slow request | progress/cancel | command/manual |

## Coverage by severity

1. **P0** blocks release and must be automated when technically possible.
2. **P1** blocks launch and should include data, permission, and error behavior.
3. **P2** can target UX consistency, accessibility, and infrastructure.
4. **P3** targets durability, migration, upgrade, and disaster recovery.

## Required gates

1. Formatting.
2. Type checking.
3. Unit tests.
4. One end-to-end core loop test.
5. Migration up/down where database changes exist.
6. Dependency / security scan.
7. Accessibility and responsive UI checks for user-facing changes.

## Verification

```bash
<format command>
<typecheck command>
<unit test command>
<integration/e2e command>
<security scan command>
```

Record the exact commands and evidence. A skipped gate needs a named reason and follow-up.

## Done

- Every acceptance criterion has a pass case.
- At least one failure path and one unauthorized actor have tests.
- No test was edited only to make a failure disappear.
- Commands are deterministic enough to run again.
