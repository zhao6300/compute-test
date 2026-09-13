# GitHub high-star skill research

## Scope

This note summarizes a rapid scan of high-star GitHub repositories focused on "agent skills" and
software engineering. It is not a survey of all agents, nor a thematic classification.
It picks the most relevant repositories whose README, structure, or "skill shape" suggest
practice-worthy patterns for building larger engineering projects with an agent.

## Repositories reviewed

| Repository | Stars | Why useful |
| --- | ---: | --- |
| `obra/superpowers` | 285,806 | Strong general `SDLC` skill set; good on plans, TDD, review, debug, evidence-based verification |
| `anthropics/skills` | 176,000 | Anthropic's public skill catalog; good example of clean skill structure |
| `addyosmani/agent-skills` | 93,748 | Strong production-oriented engineering skills spanning design, CI/CD, quality, debugging, security, and observability |
| `vercel-labs/skills` | 31,487 | Practical organization and invocation patterns of plugin-style skills |
| `agentskills/agentskills` | 25,258 | Clear example of skill metadata / reusable skill packaging |
| `github/awesome-copilot` | 38,938 | Community instructions, agents, and skill-style configurations for Copilot-like agents |
| `composio-community/awesome-codex-skills` | 16,406 | Codex-specific curated list |
| `maxritter/pilot-shell` | 2,071 | Strong harness engineering around Codex/Claude Code: spec-driven development, TDD, verification gates, persistent memory |
| `thientv/godmode` | 94 | Good engineering flow: orientation → design → implementation plan → TDD → review → completion verification |
| `nocodeMrLi/mini-program-engineering-skill-suite` | 60 | Useful example of multi-stage "mini-program" development lifecycle |

Approximate stars were read from repository metadata during the scan.

## Patterns observed

### SDLC-driven approach

Most relevant repositories describe development as explicit phases:

1. Understand the intent.
2. Build a spec or plan.
3. Then implementation.
4. Then review.
5. Then verification.

The clearest SDLC pipelines include:

- `obra/superpowers`
- `thientv/godmode`
- `maxritter/pilot-shell`

They share the same discipline:

```text
spec → plan → implement → test → review → verify
```

### Verification-first mindset

High-signal skills insist that "done" is not an opinion:

- run build / test / lint commands every time;
- avoid unverified green paths;
- prevent "looks done" handoffs.

Examples include:

- `obra/superpowers::verification-before-completion`
- `thientv/godmode::completion-verification`
- `maxritter/pilot-shell::verification gates`

### Debugging via root cause

Several skills deliberately constrain the agent from patching symptoms:

1. Read error carefully.
2. Reproduce.
3. Collect evidence.
4. Identify the failure surface.
5. Only then propose a fix.

`obra/superpowers::systematic-debugging` is the clearest example.

### Separation between planning and implementation

Top skills distinguish:

```text
plan writing
→ plan execution
→ verification
```

as separate steps. This prevents "I am confident" behavior from becoming premature code generation.

### Role separation

Several repos explicitly partition agent responsibility:

1. Implementer builds.
2. Reviewer reviews.
3. Builder does fix loops.
4. Evidence collector validates.

`obra/superpowers`, `thientv/godmode`, `maxritter/pilot-shell`, and `addyosmani/agent-skillss`
all emphasize this.

### Verification is not test-only

Beyond `make test`, mature skills add:

- lint / typecheck;
- integration smoke tests;
- browser automation;
- architecture assertions;
- behavioral test;
- runtime evidence.

`addyosmani/agent-skills` is the best example, with broad coverage of
performance, observability, and hardening.

## Practical takeaways

For a night-long Codex run, copy the spirit rather than the exact skill set.

Minimum structure:

```text
AGENTS.md
PLAN.md
README.md
Makefile
src/
tests/
```

Minimum cycle:

```text
target clarification
→ plan milestone
→ diff minimal
→ run test
→ verify diff
→ commit
→ next milestone
```

Minimum evidence expectation:

```text
do not call work complete without running the verification command
```

## Candidate next moves

1. Add a skills/agents README that unifies these patterns.
2. Add a `PLAN.md` style skeleton for phases.
3. Add a `tests/Makefile` or a minimal "episode" runner.
4. Add a minimal "evidence-report" prompt to a phase template.
5. Add a `docs/refactoring-skills.md` checklist from the high-star repos.
6. Add a CI job that logs whether tests were run in an episode.

## What to avoid

- Relying on vibes like "looks done".
- Letting a large prompt generate an entire project.
- Accepting a plan only in prose, with no checkpoints.
- Treating a large skill dictionary as a magic substitute for a clean loop.
- Ignoring failure evidence because a later green test appears.

No one repo is the absolute best; their value is in the common rhythm of
**specification, plan, implementation, verification, review**. As we scale a project,
the same rhythm stays useful.
