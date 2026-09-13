# Ship skill

## Trigger

Run this skill only after verify gates and review blockers are complete.

## Objective

Release a small, reversible, operating increment and prepare the next loop.

## Release readiness

1. All P0 tests and launch gates pass.
2. Review blockers are absent.
3. Changelog and release notes describe the user-facing change.
4. Deployment is versioned and repeatable.
5. Rollback command and trigger points are documented.
6. Monitoring and alerting are enabled before exposure.
7. Canary or staged rollout exists for risky changes.
8. Support, on-call, security, privacy, and compliance owners are informed.

## Output

Create or update `docs/RELEASE.md`:

```markdown
# Release

## Version

## Change summary

## User-facing behavior

## Compatibility and migration

## Deploy
```bash
...
```

## Rollback
```bash
...
```

## Observability
- metric: ...
- alert: ...
- dashboard: ...

## Post-release checks
1. ...
2. ...

## Known follow-ups
- ...
```

## Operational rules

1. Ship a completed phase/rollback, not “almost working”.
2. Keep the rollout reversible.
3. Observe before increasing exposure.
4. Record any workaround as an explicit follow-up.
5. On callout, state symptom, impact, trigger, mitigation, rollback, owner, and next action.
6. Treat user-visible regression as a priority over further feature work.
7. If production behavior differs, stop rollout and reproduce with operational evidence, not by patching in place.
8. Keep an audit trail: who released what, which config/migration ran, and how response works.
9. Escalate to on-call/support/security/compliance when data ownership, customer trust, contractual guarantee, external notice, high blast radius, irreversible write, or unexplained autoscaling/capacity anomaly is involved.
10. Before rollback, preserve enough evidence (config diff, logs, metrics, request IDs) to avoid losing the cause.

## Done

- Release and rollback are executable.
- Observability and post-release checks are active.
- Residual work is committed as follow-ups with owners.
- Next improvement loop has a clear entry.
