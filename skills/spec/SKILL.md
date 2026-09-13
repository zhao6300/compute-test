# Spec skill

## Trigger

Run this skill when the request is still an idea, a feature description, or a vague release goal.

## Objective

Turn the idea into one working loop with explicit scope.

## Inputs

1. Original user idea.
2. Existing README, docs, tests, and deployment notes.
3. Any non-negotiable constraints or dates.

## Output

Create or update `docs/SPEC.md` with:

```markdown
# Spec

## Product statement
<!-- One sentence: who gets what value and why it is better than the current workflow. -->

## Target users
<!-- Primary persona, secondary persona, and their current pain. -->

## Core loop
1. <!-- User action. -->
2. <!-- System behavior. -->
3. <!-- Observable result. -->
4. <!-- Way to know it is successful. -->

## Scope
### In
<!-- Release behavior only, not implementation details. -->

### Out
<!-- Explicitly excluded so scope cannot silently expand. -->

## Acceptance criteria
<!-- Given / when / then; every item must be testable. -->

## Success metrics
<!-- Product and health metrics, with your minimum acceptable values. -->

## Primary risks
<!-- Technical, product, operational, legal, or data risks. -->
```

## Quality checks

1. No criterion requires “good”, “fast”, or “robust” as a subjective gate.
2. The loop does not need hidden steps or unexplained data.
3. A critical failure, a major dependency, and a delivery risk are identified.
4. `Out` is not empty.
5. At least one acceptance criterion covers an edge case.

## Verification

Ask and document concrete answers:

```bash
rg -n "^## Product statement|^## Core loop|^## Acceptance criteria|^## Out|^## Primary risks" docs/SPEC.md
```
* Verify `Product statement`, `Core loop`, `Acceptance criteria`, `Out`, and `Primary risks` all exist.
* Verify each acceptance criterion has a testable given / when / then form.
* Verify the core loop is the smallest version with observable value.
* Verify every listed risk has a plan entry in `PLAN.md`. If not, update `plan/SKILL.md` output.
* Do not start implementation until no required check remains unanswered.

## Done

- `docs/SPEC.md` exists and names the target user, core loop, acceptance criteria, out-of-scope, and risks.
- Another engineer can infer what to build and what not to build without asking you for interpretation.
- No required spec section is missing.
