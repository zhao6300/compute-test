# Agent product workflow plan

This is the roadmap for moving from a rough idea to a production-ready product.

The executable skill entries live in `skills/`. Follow the ordered skills listed in
`skills/README.md`, and use `scripts/run_overnight.sh` as a manual gate-by-gate runbook.

Before a long autonomous run, record these facts in the project workspace:

1. Target product and non-negotiable constraints.
2. Assigned sources of truth (not guesses that block later progress).
3. Sandbox, secrets, credentials, and network intake rules.
4. Deployment authorization state (`local-only`, `authorized`, `unauthorized`, or `blocked`).
5. Error policy for blocked external resources: use the assigned source, ask, or record and continue with a reversible best-effort version.
6. Local build/test/deploy commands, plus their timeout and approval requirements.
7. Stop, retry, and escalation rules for hanging commands, failed dependency installs, repeated errors, or missing products.
8. Progress and evidence reporting cadence, including exact commands and observed output.

## Phases

### Phase 01 — Clarify the target

Skill: [`skills/spec/SKILL.md`](skills/spec/SKILL.md)

- [ ] Re-state the core value.
- [ ] Identify primary users.
- [ ] Identify the first end-to-end loop.
- [ ] Define what is **not** in this project.
- [ ] Write one success criterion.

Exit criteria:

```text
Core loop, target user, accept criteria, and out-of-scope are clear.
```

### Phase 02 — Spec and architecture skeleton

Skill: [`skills/plan/SKILL.md`](skills/plan/SKILL.md)

- [ ] Produce a short spec.
- [ ] List the minimal UI / API surfaces.
- [ ] Define the data model.
- [ ] Identify backend, frontend, and storage boundaries.
- [ ] Record risks and rollback.

Exit criteria:

```text
ARCHITECTURE.md exists and shows the minimal path.
```

### Phase 03 — Working slice

Skill: [`skills/implement/SKILL.md`](skills/implement/SKILL.md)

- [ ] Build the narrowest slice that proves value.
- [ ] Use minimal dependencies.
- [ ] Create the first test.
- [ ] Run the build.

Exit criteria:

```text
One user scenario runs locally.
At least one test passes.
```

### Phase 04 — Deepen quality

Skill: [`skills/test/SKILL.md`](skills/test/SKILL.md)

- [ ] Add validation.
- [ ] Add logging.
- [ ] Add observability.
- [ ] Add error state tests.

Exit criteria:

```text
The agent can run the full build without manual help.
```

### Phase 05 — Production readiness

Skills: [`skills/review/SKILL.md`](skills/review/SKILL.md), [`skills/verify/SKILL.md`](skills/verify/SKILL.md)

- [ ] Add deployment plan.
- [ ] Add rollback.
- [ ] Add audit points.
- [ ] Add security walkthrough.
- [ ] Add known issues list.

Exit criteria:

```text
Deployment plan, rollback, and audit path are documented.
```

### Phase 06 — Ship and iterate

Skill: [`skills/ship/SKILL.md`](skills/ship/SKILL.md)

- [ ] Publish a working version.
- [ ] Verify deploy works.
- [ ] List next batch of improvements.

Exit criteria:

```text
A user can use it, and the agent can recommend the next iteration.
```

## Rules

Each phase must:

1. stay small;
2. create a repeatable verification command;
3. leave a runnable diff;
4. provide content for the next phase;
5. update the README and related docs if behavior changed.
