# Vendor/source skill additions

These sources do not replace the current agent workflow. Each one is used as a compact
pattern library mapped to an existing phase or module skill in this repository.

## Core vendor sources

| Source | What to borrow | Integrated into |
| --- | --- | --- |
| [`google/skills`](https://github.com/google/skills) | skill-level execution shape and product-tool grounding | phase skills |
| [`google/agents-cli`](https://github.com/google/agents-cli) | agent creation, evaluation, and deployment loop | `verify`, `ops` |
| [`google/mantis`](https://github.com/google/mantis) | security review, vulnerability reproduction, and safe patch flow | `review`, `backend`, `api` |
| [`google/rust-skills`](https://github.com/google/rust-skills) | language-specific quality gates | phase skills |
| [`microsoft/skills`](https://github.com/microsoft/skills) | SDK/API grounding and agent instruction packaging | phase skills |
| [`microsoft/hve-core`](https://github.com/microsoft/hve-core) | instructions, prompts, agents, and project onboarding structure | phase skills |
| [`NVIDIA/skills`](https://github.com/NVIDIA/skills) | CUDA/simulation/robotics workflow packaging | phase skills |
| [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector) | skill safety, prompt injection, and dependency risk review | `review`, `ops` |
| [`NVIDIA/TileGym`](https://github.com/NVIDIA/TileGym) | GPU/kernel tutorial and benchmarking structure | phase skills |
| [`NVIDIA/SkillEvaluator`](https://github.com/NVIDIA/SkillEvaluator) | multi-tier skill-quality evaluation and behavior measurement | `test`, `verify` |

## Team-focused sources

| Source | What to borrow | Integrated into |
| --- | --- | --- |
| [`boshu2/agentops`](https://github.com/boshu2/agentops) | independent judgment, `PASS/FAIL/NOT_PROVEN`, evidence contracts | `review`, `verify` |
| [`danielvm-git/bigpowers`](https://github.com/danielvm-git/bigpowers) | solo development discipline and implementation guardrails | `implement`, `test` |
| [`addxai/enterprise-harness-engineering`](https://github.com/addxai/enterprise-harness-engineering) | engineering, DevOps, SRE, and security style skill catalogs | all module skills |
| [`Stanshy/AgentHub`](https://github.com/Stanshy/AgentHub) | multi-agent operations, hooks, persistence, and traceability | phase skills |
| [`dwmkerr/claude-toolkit`](https://github.com/dwmkerr/claude-toolkit) | compact problem-solving and slide/engineering utilities | phase skills |
| [`mhattingpete/claude-skills-marketplace`](https://github.com/mhattingpete/claude-skills-marketplace) | Git, test, and code-review workflow skills | `implement`, `review` |

## Integration rules

1. Prefer the company/workflow discipline, not the tool-specific install mechanism.
2. Every borrowed behavior must become a check, artifact, command, or failure protocol.
3. Keep skills concise; link a source only when it adds a pattern not already encoded.
4. Before claiming readiness, run the phase's verification command; a reference repo does not prove your code works.

## Corresponding slices

The production loop remains anchored to seven persistent phase slices. Each slice
is deliberately non-reproducible and should remain separated in memory rather than
hidden inside a one-shot prompt.

### Spec

- Purpose: freeze the core user action and the minimum behavior change.
- Current source: [`skills/spec/SKILL.md`](../skills/spec/SKILL.md).
- Vendor inspiration: `google/skills`, `microsoft/skills`.

### Plan

- Purpose: turn the product loop into bounded implementation and data-work slices.
- Current source: [`skills/plan/SKILL.md`](../skills/plan/SKILL.md).
- Vendor inspiration: `microsoft/hve-core`, `boshu2/agentops`.

### Implementation

- Purpose: produce a narrow, reviewable, state-changing slice with failures handled.
- Current source: [`skills/implement/SKILL.md`](../skills/implement/SKILL.md).
- Vendor inspiration: `danielvm-git/bigpowers`, `google/agents-cli`.

### Test

- Purpose: prove acceptance, failure, authorization, and regression behavior.
- Current source: [`skills/test/SKILL.md`](../skills/test/SKILL.md).
- Vendor inspiration: `NVIDIA/SkillEvaluator`, `mhattingpete/claude-skills-marketplace`.

### Review

- Purpose: inspect the diff and visible UX with knowledge the implementer did not have.
- Current source: [`skills/review/SKILL.md`](../skills/review/SKILL.md).
- Vendor inspiration: `google/mantis`, `boshu2/agentops`.

### Verify

- Purpose: collect a complete launch/readiness evidence trail, not just tests.
- Current source: [`skills/verify/SKILL.md`](../skills/verify/SKILL.md).
- Vendor inspiration: `NVIDIA/SkillEvaluator`, `addxai/enterprise-harness-engineering`.

### Ship

- Purpose: release behind an externally callable rollback/audit path, then collect adoption evidence.
- Current source: [`skills/ship/SKILL.md`](../skills/ship/SKILL.md).
- Vendor inspiration: `Stanshy/AgentHub`, `google/agents-cli`.
