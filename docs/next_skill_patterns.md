# Agent Skill Patterns for Autonomous High-Quality Software Development

This document condenses a broad scan of high-star GitHub skills repositories into
practical patterns rather than 

The purpose is that we can build agents that autonomously and reliably produce high-quality
software without relying on a single "magic prompt".

## 1. The big picture

Strong skills aren't scripts for every action.
They give agents:

- clear outcomes;
- explicit constraints;
- a concrete workflow;
- proof of completion.

The best repos on this front work by giving agents:

```text
understanding
→ planning
→ implementation
→ verification
→ review
→ release
```

not just "ask for code".

## 2. Source landscape

The scan found a clear hierarchy of high-star skill-based repos.

### General software-engineering skill stacks

| Repo | Stars | Value |
|---|---:|---|
| `obra/superpowers` | ~286k | Full SDLC skill stack: plans, TDD, debugging, review, verification |
| `anthropics/skills` | ~176k | Good example of reusable `SKILL.md`-driven skill packaging |
| `addyosmani/agent-skills` | ~94k | Production-grade engineering skill collection with concrete quality phases |
| `vercel-labs/skills` | ~31k | Adapter skill catalog and easy install path |
| `agentskills/agentskills` | ~25k | Good sample of a clean `SKILL.md` library |
| `owainlewis/blueprint` | ~4k | Focused 10-skill architecture / design / delivery workflow |

### Autonomous / single-agent harnesses

| Repo | Stars | Core idea |
|---|---:|---|
| `maxritter/pilot-shell` | ~2k | Spec-driven development plus persistent memory and verification gates |
| `CodeAlive-AI/ai-driven-development` | ~136 | Clear agent-driven dev process |
| `simota/agent-skills` | ~77 | Big catalog with many domain-specific skill packs |
| `smixs/disruptor-skills` | ~18 | Gated idea-to-ship pipeline |

### Active multi-agent orchestration

| Repo | Stars | Insight |
|---|---:|---|
| `obra/superpowers` | ~285k | Great examples of subagent-driven development |
| `addyosmani/agent-skills` | ~94k | Encourages command-level role separation |
| `owainlewis/blueprint` | ~4k | Clean task-to-PR delivery chain |
| `agent-skills/agentskills` | ~25k | Clean reusable skill format |

## 3. Patterns we can copy

### Pattern 1: Translate intent into spec, not code

Top skills first derive:

```text
user value
→ clarity
→ scope
→ architecture
→ milestones
→ acceptance commands
```

The best examples explicitly disallow "vibe writing".

### Pattern 2: Plan first, but make it executable

A plan is only useful if it has:

1. scope;
2. exit conditions;
3. acceptance commands;
4. tests;
5. file boundaries;
6. rollback;
7. review / merge requirements.

`obra/superpowers` and `maxritter/pilot-shell` both make this explicit.

### Pattern 3: Use small, reviewable slices

Each slice should have:

1. clear scope;
2. clean file boundaries;
3. a single commit;
4. hide risk behind explicit acceptance tests.

Matches `addyosmani/agent-skills` (build one slice per task) and
`owainlewis/blueprint` (task-to-PR).

### Pattern 4: Test as evidence, not as paperwork

Best skills use:

1. unit tests
2. integration tests
3. runtime smoke
4. regression tests
5. build checks
6. typecheck
7. lint
8. security scan
9. performance baseline

They don't accept "looks done".

### Pattern 5: Keep completion as an assertion, not a feeling

The highest-quality skills force an evidence path:

```text
run tests
read logs
verify diff
consider edge cases
update docs
then claim done
```

This is what makes automation "hard", but valuable.

### Pattern 6: Separate roles

Strong skill stacks split work into roles:

```text
spec
plan
implementer
reviewer
verifier
release operator
```

It avoids one agent doing everything with one enormous context.

### Pattern 7: Keep the inspection part separate from the implementation

Reviewing a change should not require the implementation context.
It should look at:

1. diff;
2. test coverage;
3. boundary correctness;
4. runtime behavior;
5. risk;
6. rollback.

This is the same idea behind subagent-driven development in `obra/superpowers`.

### Pattern 8: Use skills for one thing

The cleanest skills:

1. have one clear servo;
2. have one trigger;
3. stay short;
4. make auditability easy.

Avoid mega-prompts that try to solve everything.

## 4. A concrete agent workflow

The synthesis is:

```text
1. understand
2. specify
3. plan
4. design
5. implement
6. debug
7. test
8. review
9. verify
10. deliver
11. release
```

Each step should have a skill and a verification.

## 5. Useful minimal skill set

If you only want one minimal set, use:

1. `understand`
2. `spec`
3. `plan`
4. `implement`
5. `test`
6. `debug`
7. `review`
8. `verify`
9. `ship`

This is enough for a high-quality autonomous agent.

## 6. Optional, add when risk grows

Skills to add once complexity appears:

1. `architecture-review`
2. `performance-optimization`
3. `security-audit`
4. `observability`
5. `release-engineering`
6. `docs-and-adr`
7. `ci-cd`

But don't add them before the base loop is safe.

## 7. Build principles

When writing your own skills:

1. one skill, one trigger, one outcome;
2. no deep nesting;
3. commands should be copy-paste safe;
4. outputs should write to files;
5. policies live in `AGENTS.md`, not inside one skill;
6. skills should be small enough to read in 1 minute.

## 8. UI and frontend skills

Frontend skills should ask:

1. what's the goal;
2. what states you must cover;
3. what's interactive;
4. what's responsive;
5. what must be accessible;
6. what kind of visual review do we need.

You can then bind to:

```text
UI plan
→ component tree
→ interaction spec
→ design tokens
→ tests
→ visual review
```

This is cleaner than "design a website".

## 9. Backend and API skills

For backend, use:

```text
data model
→ API contract
→ persistence boundaries
→ validation
→ observability
→ migration
→ integration tests
```

This is what makes an agent work like a backend engineer, not a script writer.

## 10. Release & production

Release-specific skills should ask:

1. deployable artifact?
2. rollback path?
3. can we reproduce the failure?
4. observability ready?
5. security scanning pass?
6. performance baseline recorded?
7. alerts defined?
8. runbook exists?

This is the same "production readiness" pattern in `addyosmani/agent-skills`.

## 11. Synthesis

If we want high-quality autonomous project work, the goal is not to have 500 skills.
The goal is to have 8–12 high-signal skills that enforce:

```text
spec
→ plan
→ build
→ test
→ review
→ verify
→ ship
```

The rest is to prevent drift and complexity creep.
