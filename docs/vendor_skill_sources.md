# Vendor/source skill additions

These sources do not replace the current agent workflow. Each one is used as a compact
pattern library mapped to an existing phase or module skill in this repository.

## Core vendor sources

| Source | What to borrow | Integrated into |
| --- | --- | --- |
| `google/skills` | skill-level execution shape and product-tool grounding | phase skills |
| `google/agents-cli` | agent creation, evaluation, and deployment loop | `verify`, `ops` |
| `google/mantis` | security review, vulnerability reproduction, and safe patch flow | `review`, `backend`, `api` |
| `google/rust-skills` | language-specific quality gates | phase skills |
| `microsoft/skills` | SDK/API grounding and agent instruction packaging | phase skills |
| `microsoft/hve-core` | instructions, prompts, agents, and project onboarding structure | phase skills |
| `NVIDIA/skills` | CUDA/simulation/robotics workflow packaging | phase skills |
| `NVIDIA/SkillSpector` | skill safety, prompt injection, and dependency risk review | `review`, `ops` |
| `NVIDIA/TileGym` | GPU/kernel tutorial and benchmarking structure | phase skills |
| `NVIDIA/SkillEvaluator` | multi-tier skill-quality evaluation and behavior measurement | `test`, `verify` |

## Team-focused sources

| Source | What to borrow | Integrated into |
| --- | --- | --- |
| `boshu2/agentops` | independent judgment, `PASS/FAIL/NOT_PROVEN`, evidence contracts | `review`, `verify` |
| `danielvm-git/bigpowers` | solo development discipline and implementation guardrails | `implement`, `test` |
| `addxai/enterprise-harness-engineering` | engineering, DevOps, SRE, and security style skill catalogs | all module skills |
| `Stanshy/AgentHub` | multi-agent operations, hooks, persistence, and traceability | phase skills |
| `dwmkerr/claude-toolkit` | compact problem-solving and slide/engineering utilities | phase skills |
| `mhattingpete/claude-skills-marketplace` | Git, test, and code-review workflow skills | `implement`, `review` |

## Integration rules

1. Prefer the company/workflow discipline, not the tool-specific install mechanism.
2. Every borrowed behavior must become a check, artifact, command, or failure protocol.
3. Keep skills concise; link a source only when it adds a pattern not already encoded.
4. Before claiming readiness, run the phase's verification command; a reference repo does not prove your code works.
