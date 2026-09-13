# From idea to launch: production readiness

This is a practical document for taking a rough product idea all the way to something that can be shipped, monitored, and maintained. It combines:

1. a workflow for building and verifying the product;
2. the actual things that must be true before you call it "可上线";
3. references from GitHub projects focused on production readiness, agent-driven SDLC, and release engineering.

## 0. What "production-ready" really means

It does not mean:

```text
code looks finished
one demo works
README exists
tests pass
```

It means:

```text
users can use it safely
the product has telemetry
you can roll back a bad change
you can reproduce and diagnose failures
you know how to operate it while asleep
```

A good test: when something breaks at 3am, someone can figure it out from logs, metrics, traces, and docs without reinventing the product.

---

## 1. Reference points from GitHub

| Repository | Stars | Contribution |
| --- | ---: | --- |
| `addyosmani/agent-skills` | ~94k | Strong production-engineering agent skills: spec → plan → build → test → review → ship, each with concrete quality gates |
| `anthropics/skills` | ~176k | Clean, reusable skill structure and workflow segmentation |
| `obra/superpowers` | ~285k | Full agent-driven development methodology with plans, TDD, debugging, verification, and review |
| `maxritter/pilot-shell` | ~2k | Professional harness engineering around Codex/Claude Code: spec-driven development, persistent memory, runtime verification |
| `saadjangda/shipwright` | multi-star (recent) | Production-first release skill: code health, backend, tests, security, UI, a11y, performance, CI/CD, observability, docs |
| `mercari/production-readiness-checklist` | ~944 | Clear production gates for service-level readiness |
| `kgoralski/microservice-production-readiness-checklist` | ~218 | Useful microservice pre-production principles |
| `telecomprofi/observability-gap-analysis-checklist` | recent | Good SRE/observability readiness questions |
| `devops-rob/Vault-Production-Readiness-Checklist` | recent | Strong example of hardening a stateful system before launch |

These are not the only useful repositories; they are useful as a pattern library.

---

## 2. The pipeline

Use this as the spine:

```text
idea
→ spec
→ MVP plan
→ implementation slices
→ test
→ verify
→ review
→ preview
→ production launch
→ monitor / maintain
```

The relevant star repos align with this.

### Example mapping

| Source | What to borrow |
| --- | --- |
| `addyosmani/agent-skills` | `spec → plan → build → test → review → ship` |
| `obra/superpowers` | plan writing, TDD, systematic debugging, verification gate |
| `saadjangda/shipwright` | 12-phase ship mode: code health, scalability, tests, security, UI, a11y, performance, CI/CD, observability, docs |
| `mercari` | Pre-production readiness checklist |
| `observability-gap-analysis-checklist` | SRE/observability readiness &
 health metrics |
| `maxritter/pilot-shell` | Persistent context and runtime verification |

---

## 3. The 8 gates before saying "ready"

### Gate 1 — Define the product

Before engineering:

1. What is the core user value?
2. What's the smallest loop that proves the value?
3. What are the primary user paths?
4. What are you explicitly not doing in this release?
5. What metrics prove the product works?

### Gate 2 — Design the system, not just code

Before building:

1. architecture / module boundaries;
2. data model;
3. API surface;
4. security model;
5. storage strategy;
6. migration strategy;
7. failure strategy;
8. observability strategy;
9. rollback strategy.

### Gate 3 — Build in testable slices

For each slice:

1. smallest diff;
2. predictable inputs;
3. observable outputs;
4. test first;
5. verify build;
6. review diff;
7. commit.

### Gate 4 — Production pipeline

Before "launch":

1. build works in CI;
2. tests run in CI;
3. staging environment exists;
4. deploy is repeatable;
5. rollback is tested;
6. backups are confirmed;
7. health checks exist.

### Gate 5 — Observability

You need at least:

1. structured logs;
2. error monitoring;
3. latency / traffic / errors / saturation metrics;
4. alerting;
5. traces for important user paths;
6. business metrics;
7. health endpoint;
8. incident runbook.

This is not "nice to have". It's how you don't wake up blind at 3am.

### Gate 6 — Security

1. authentication;
2. authorization;
3. direct object references;
4. data encryption;
5. secrets management;
6. rate limits;
7. account recovery;
8. logging and audit trail;
9. dependency scanning;
10. image audit.

### Gate 7 — Accessibility and UX

1. core user path is usable;
2. error states are meaningful;
3. empty/loading/edge states handled;
4. mobile / responsive layouts tested;
5. keyboard + assistive tech not broken;
6. contrast / labels / semantics fine;
7. performance metrics met.

### Gate 8 — Operational launch

1. cryptographic / privacy / compliance reviewed if relevant;
2. terms and privacy updated if user data involved;
3. analytics events meaningful;
4. version controlled;
5. on-call knows the runbook;
6. rollback exists and has been tested;
7. launch canary or staged rollout if risk is high.

---

## 4. Minimal launch checklist

```text
1. ready to build
2. ready to test
3. ready to review
4. ready to deploy
5. ready to observe
6. ready to roll back
7. ready to operate
8. ready to grow
```

For each, there should be a concrete ask:

- how do I deploy?
- how do I test?
- what does a healthy service look like?
- what do I do if it breaks?
- who owns it?
- how do I roll back?

If nothing can answer those, the product is not ready.

---

## 5. How to use the issue at night

For a nightly build, split the work into six phases:

```text
0. Define the product and scope
1. Define the architecture and data model
2. Build the smallest working slice
3. Build the "happy path + primary edge cases"
4. Add observability + deployment
5. Security, performance, accessibility audit
6. Docs / release readiness
```

Each phase gets:

```text
1. a small diff;
2. a test;
3. a build/verify command;
4. a commit;
5. a "how to reproduce" note;
6. a "known risk" note;
7. a rollback.
```

The phase isn't done until the build and test prove it works.

---

## 6. Sample "ship gate" prompt

```text
Before you say this is ready to ship, please answer:
1. What is the user value?
2. What is the smallest working slice that proves it?
3. What commands prove build and tests pass?
4. What are the edge cases?
5. What happens when it fails?
6. How do I roll back?
7. Where are logs / metrics / traces?
8. How do I know the service is healthy?
9. What security mechanisms exist?
10. What objects could break in production?
11. What docs exist?
12. What's the next step after launch?
```

Do not say "ready" until each has a concrete answer.

---

## 7. Anti-patterns

1. Build first, think later.
2. Treat tests as something done after coding.
3. Accept a green build as proof of quality.
4. Ship without observability.
5. Add a huge feature without a small slice test.
6. Use a large skill dictionary as a substitute for a clean loop.
7. Have no rollback.
8. Confirm release readiness via gut feeling.

---

## 8. Bottom line

You can use these star repos as a toolset, but the core pattern stays the same:

```text
spec
→ plan
→ verify the plan
→ build in slices
→ test
→ verify
→ review
→ ship
→ measure
→ iterate
```

The differentiator isn't more tokens.
It's a reliable loop plus hard evidence.
