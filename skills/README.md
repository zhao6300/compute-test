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

## Execution rules

1. Execute the phases in order unless the user changes scope.
2. Enter the next skill only when the previous skill has its required artifact, command, and recorded result.
3. Keep each skill small enough to finish before committing.
4. Store project documents in a project-local `docs/` directory.
5. Do not treat these templates as a generator; edit files from them, and delete sections that cannot be evidenced.
