# Agent workspace rules

## Goal

Use this repository as a **product engineering workspace**, not a code dump.

## Execute through skills

Use the ordered phases in [`skills/README.md`](skills/README.md). They keep work
reviewable and avoid the common failure of doing setup, claims, and scope creep
without a verified product loop.

## Workflow

1. Read `README.md`, `AGENTS.md`, `PLAN.md`, and the relevant `skills/<phase>/SKILL.md`.
2. State the target and success criteria in the current reply.
3. Make a small, reversible diff.
4. Run the narrow relevant verification command before broader checks.
5. Explain what changed, what command ran, and what result was observed.
6. Commit when the phase artifact is complete and verified.

## Useful verification commands

```bash
git status --short
bash -n scripts/run_overnight.sh
make
```

## Hard rules

- [ ] Do not create large changes in one pass.
- [ ] Do not add dependencies without asking.
- [ ] Do not modify unrelated files.
- [ ] Do not make repeated speculative fixes.
- [ ] Do not claim done without evidence.
- [ ] Do not edit tests solely to make them pass.
- [ ] Do not add ceremonies instead of work.
- [ ] Do not pretend that one prompt is enough for a whole project.

## Useful commands

```bash
git status --short
make
```

If tests are not present, build the smallest meaningful one first.

## Definition of done

For each phase:

1. a small diff;
2. a repeatable verification command;
3. evidence from the command output;
4. a short report;
5. a next step;
6. a commit when the user has asked for one.

## Important

Prefer moving one phase forward over inventing new features.
If the next step is unclear, ask instead of **making it up**.
