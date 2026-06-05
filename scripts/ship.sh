#!/usr/bin/env bash
# ship.sh — the going-forward workflow: stage everything, commit, push, then
# watch the GitHub Actions run that the push triggers.
#
# Usage:
#   scripts/ship.sh "your commit message"
#   scripts/ship.sh                       # opens $EDITOR for the message
#
# Run from anywhere inside the repo.
set -euo pipefail

# Move to the repo root so `git add -A` stages the whole tree regardless of cwd.
cd "$(git rev-parse --show-toplevel)"

git add -A

if git diff --cached --quiet; then
  echo "Nothing staged — working tree is clean. Skipping commit/push."
else
  if [[ $# -ge 1 ]]; then
    git commit -m "$*"
  else
    git commit            # falls back to $EDITOR
  fi
  git push
fi

# Watch the most recent run on this branch. The run can take a moment to
# register after the push, so retry briefly before giving up.
echo "Waiting for the Actions run to register…"
for _ in 1 2 3 4 5 6; do
  if gh run watch --exit-status 2>/dev/null; then
    exit 0
  fi
  sleep 3
done

# Fall back to listing if watch couldn't attach (e.g. Actions disabled).
echo "Couldn't attach to a run automatically; recent runs:"
gh run list --limit 5
