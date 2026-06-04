#!/usr/bin/env bash
#
# examples/01-app-no-telemetry/demo.sh
#
#   ./demo.sh            # bring the stack up and drive one request (Ctrl-C to stop)
#   ./demo.sh up         # just bring the stack up (detached)
#   ./demo.sh drive      # POST one compute request and print the response
#   ./demo.sh down       # tear the stack down (keep volumes)
#   ./demo.sh clean      # tear down and remove volumes
#
# Demonstrates the app working end to end with NO telemetry: a request rides
# Kafka to the worker, hits Postgres, and returns — and Grafana shows nothing,
# which is the point this chapter starts from.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STACK="$REPO_ROOT/stack"
API="http://localhost:8080"

up() {
  echo "==> bringing up the shared stack (this builds the app image on first run)"
  ( cd "$STACK" && podman compose up --build -d )
  echo "==> waiting for the API to report healthy"
  for i in $(seq 1 60); do
    if curl -sf "$API/health" >/dev/null 2>&1; then echo "    API is up"; return 0; fi
    sleep 2
  done
  echo "!! API did not become healthy in time; check: podman compose -f $STACK/compose.yaml logs api" >&2
  return 1
}

drive() {
  echo "==> POST $API/compute  {\"n\": 100}"
  curl -sf -X POST "$API/compute" -H 'content-type: application/json' -d '{"n": 100}'
  echo
  echo "==> open Grafana at http://localhost:3000 — note there is nothing to see yet."
}

down()  { ( cd "$STACK" && podman compose down ); }
clean() { ( cd "$STACK" && podman compose down -v ); }

case "${1:-run}" in
  up)    up ;;
  drive) drive ;;
  down)  down ;;
  clean) clean ;;
  run)   up && drive ;;
  *)     echo "unknown subcommand: $1" >&2; exit 2 ;;
esac
