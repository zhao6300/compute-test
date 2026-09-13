# Domain-specific skill scan

This is the second pass over GitHub skill repositories. It focuses on practical
engineering domains instead of just "general agent behavior":

```text
SDLC / project harness
frontend + UI
design systems + tokens
data + backend
performance + observability
architecture / code quality
```

Approach:

1. Start from the broad high-star skill repos.
2. Scan the actual repository structure.
3. Look for the shape of the skill, not just the title.

## SDLC / project harness

| Repository | Stars | Core contribution |
| --- | ---: | --- |
| `obra/superpowers` | 285,806 | Full SDLC skill set; skill-driven plan → task → test → review |
| `anthropics/skills` | 176,000 | Clean skill structure and reusable agent instructions |
| `addyosmani/agent-skills` | 93,748 | Broad production-grade engineering library |
| `maxritter/pilot-shell` | 2,071 | Professional harness engineering for Claude Code and Codex |
| `thientv/godmode` | 94 | Clean focus on plan → implement → test → review |

These are best for learning how to organize **one agent's long project flow**:

```text
intent
→ architecture
→ milestone plan
→ implementation
→ verification
→ review
→ commit
```

They are useful as inspiration rather than as something to import literally.

## Frontend / UI

| Repository | Stars | What to copy |
| --- | ---: | --- |
| `nateherkai/scroll-craft` | 2,370 | Scrolls as content structure, not animation trick |
| `educlopez/ui-craft` | 326 | Design-engineered UI; shipping craft-level quality |
| `arvindrk/extract-design-system` | 214 | Extract design tokens from existing sites |
| `TheGoat395/Codex-Skills` | 124 | Codex-first skill collection for UI, motion, QA, handoff |
| `master5d/claude-design-skills` | 24 | UI/UX, interface, typography, motion as separate skills |
| `feature-sliced/skills` | 97 | Feature-Sliced Design for frontend projects |

These repos are good evidence that a UI skill can be broken into:

```text
structure
→ layout
→ component tree
→ visual system
→ interactions
→ accessibility
→ QA
→ handoff
```

They are useful when building a site is not just "write code" but "think about information flow first".

## Data + backend

| Repository | Stars | What to copy |
| --- | ---: | --- |
| `datopian/portaljs` | 2,350 | Scaffolding a data portal entirely from an intent |
| `cosmicstack-labs/mercury-agent-skills` | 470 | Reproducible skills across 23 categories |
| `omnibusd/craftsman-agent` | 78 | Good baseline for structured agents |
| `ajsmith/ai-backend-builder` | 43 | Useful example of a multi-stage backend builder |

The backend and data skills show a pattern:

```text
domain intent
→ data model
→ access layer
→ adapter layer
→ service layer
→ integration test
```

This is basically the pattern you want for any "full stack scaffold" task.

## Performance / observability

| Repository | Stars | Key signal |
| --- | ---: | --- |
| `cosmicstack-labs/mercury-agent-skills` | 470 | Values human in loop, observability, and multi-domain agent reuse |
| `maxritter/pilot-shell` | 2,071 | Persist context + verification gates |
| `arvindrk/extract-design-system` | 214 | Design token extraction and restructuring |
| `nateherkai/scroll-craft` | 2,370 | Craft-level interaction and verified visuals |
| `educlopez/ui-craft` | 326 | QA before "looks done" |

Performance is not just timings. It is also:

```text
repeatable setup
→ measurement
→ baseline capture
→ improvement
→ verification
→ post check
```

This matters when trying to build an efficient agent workflow.

## Minimum useful patterns to adopt

When building your own nightly project, use this shape:

```text
understand
→ characterize the problem
→ define acceptance criteria
→ make the smallest diff
→ run the smallest test
→ locate regressions
→ update docs only when true
→ commit
```

And use this checklist:

- Do I have a verification command?
- Is there a small test?
- Is there a rollback?
- Is the intent clear?
- Are artifacts persisted?
- Can it survive a restart?
- Does the change reduce manual attention?

## Bottom line

The strongest skills are not "more text".  
They carve out a domain and make the agent work inside a constrained process.

Use the repos as **study material**, not as a "replace your brain" tool.

