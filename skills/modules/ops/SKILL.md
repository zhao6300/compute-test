# Operations skill

Use this skill before an operation assumes shell/SSH/local access, an interactive approval step, or use deployment.

## Required definition

For every operational action:

1. Trigger: manual release, alert, scheduled task, or user callback.
2. Permission and audit trail.
3. Runtime environment and dependency source.
4. Health signal.
5. Timeout and retry rule.
6. Success condition.
7. Partial-failure condition.
8. Rollback action.
9. Escalation owner.

Do not call an environment "operational" just because local commands pass locally.

## Deploy/rollback rules

1. Use an offline-built artifact where platform limits shell access.
2. Also support platform-native deployment endpoints: repository import, admin action, client CLI, or git provider integration.
3. Keep one canonical runbook and one concise emergency mode.
4. Expose rollback via UI, CLI, dashboard, or API.
5. Include verification command after rollback.
6. Record release identifier, config/version, who released, and outcome.
7. Separate deployment from customer-facing exposure when canary/staged rollout matters.
8. Ensure secrets, domains, storage, and migration state are represented as mutable environment resources, not only setup steps.

## Monitoring/runbook rules

1. Every critical alert names the symptom, likely impact, first diagnostic command, mitigation, rollback, owner, and next action.
2. Duplicate alerts for the same event must be grouped or deduplicated.
3. Recovery action must not require a code commit.
4. Increment/adoption/response/service health metrics need a persistence definition.
5. Logs, PII, caches, audit data need retention and purge behavior.
6. Third-party dependency status and internal endpoint/route/tenant health need independent observation.

## Verification

No operations path is verified until at least one of these is demonstrated:

1. Reproduce a failure in staging.
2. Exercise the error boundary in a controlled test.
3. Apply rollback in staging and record metric/log recovery.
4. Run rollback command in a controlled environment.
5. Show SRE/test evidence that the runbook works.

Deployment that lacks a documented rollback is not production-ready.
