# Agent skill scaffold

This directory turns the gathered production skill patterns into a repeatable execution loop.

## Ordered skills

| Phase | Skill | Primary output |
| --- | --- | --- |
| 1 | [`spec`](spec/SKILL.md) | `SPEC.md` |
| 2 | [`plan`](plan/SKILL.md) | `PLAN.md`, `ARCHITECTURE.md` |
| 3 | [`implement`](implement/SKILL.md) | smallest working slice |
| 4 | [`test`](test/SKILL.md) | `TEST_PLAN.md`, passing verification |
| 5 | [`review`](review/SKILL.md) | `REVIEW.md`, diff comments |
| 6 | [`verify`](verify/SKILL.md) | `VERIFY.md`, readiness evidence |
| 7 | [`ship`](ship/SKILL.md) | `RELEASE.md`, deploy/rollback path |

## Module skills

When the plan names the target modules, use the specialist skills during phases 2–5:

| Module | Skill | Extra quality focus |
| --- | --- | --- |
| UI / frontend | [`modules/frontend/SKILL.md`](modules/frontend/SKILL.md) | usable states, accessibility, performance, responsive behavior |
| Backend service | [`modules/backend/SKILL.md`](modules/backend/SKILL.md) | contracts, failures, observability, resource safety |
| Data / storage | [`modules/data/SKILL.md`](modules/data/SKILL.md) | schema ownership, migrations, integrity, rollback |
| External API | [`modules/api/SKILL.md`](modules/api/SKILL.md) | versioning, validation, authz, rate limits |
| Operations | [`modules/ops/SKILL.md`](modules/ops/SKILL.md) | deploy, rollback, health, runbooks, alerts |

Module skills do not replace the ordered phase skills; they constrain what a slice must include.

## Execution rules

1. Execute the phases in order unless the user changes scope.
2. Enter the next skill only when the previous skill has its required artifact, command, and recorded result.
3. Keep each skill small enough to finish before committing.
4. Store project documents in a project-local `docs/` directory.
5. Do not treat these templates as a generator; edit files from them, and delete sections that cannot be evidenced.
