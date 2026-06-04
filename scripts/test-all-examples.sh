#!/usr/bin/env bash
# scripts/test-all-examples.sh — bring up the shared stack, run each example's
# test in order, then tear down. The automated gate referenced in the PRD.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STACK="$REPO_ROOT/stack"
trap '( cd "$STACK" && podman compose down -v ) || true' EXIT
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done
fail=0
for d in "$REPO_ROOT"/examples/*/; do
  if [ -x "$d/test.sh" ]; then
    echo "=== ${d} ==="
    ( cd "$d" && ./test.sh ) || { echo "FAILED: $d"; fail=1; }
  fi
done
exit $fail
