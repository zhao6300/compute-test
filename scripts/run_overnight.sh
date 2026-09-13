#!/usr/bin/env bash

set -euo pipefail

skills=(
  skills/spec/SKILL.md
  skills/plan/SKILL.md
  skills/implement/SKILL.md
  skills/test/SKILL.md
  skills/review/SKILL.md
  skills/verify/SKILL.md
  skills/ship/SKILL.md
)

if [[ ! -f PLAN.md || ! -f AGENTS.md ]]; then
  echo "Run scripts/run_overnight.sh from the repository root." >&2
  exit 1
fi

printf '%s\n' "Agent overnight workflow"
for index in "${!skills[@]}"; do
  skill=${skills[$index]}
  phase=$((index + 1))
  printf '\n[%s/7] %s\n' "$phase" "$skill"
  sed -n '1,40p' "$skill"
  while IFS= read -r -p "Input '$phase' completed and verified? [y/N] " answer; do
    [[ "$answer" == y || "$answer" == Y ]] && break
  done
done

printf '\nAll seven phase gates acknowledged.\n'
