#!/usr/bin/env bash
# Put load directly on the inventory gRPC service with `ghz`, bypassing the order
# service — useful for seeing one service's spans/metrics in isolation. Uses the
# shared proto at proto/ so ghz knows the message shape.
#
#   tools/load/ghz-inventory.sh [REQUESTS] [CONCURRENCY]
#
# Install ghz:  https://ghz.sh/docs/install
#
# Note: inventory's gRPC port is internal to the compose network. To hit it from
# the host, either publish 50051 on the inventory service or run ghz from inside
# the network (e.g. `podman run --network observability ...`).
set -euo pipefail
INVENTORY_ADDR="${INVENTORY_ADDR:-localhost:50051}"
N="${1:-2000}"
C="${2:-50}"
REPO_ROOT="$(git rev-parse --show-toplevel)"

command -v ghz >/dev/null || { echo "ghz not found — see https://ghz.sh/docs/install"; exit 1; }

ghz --insecure \
  --proto "$REPO_ROOT/proto/mesh/inventory/v1/inventory.proto" \
  --import-paths "$REPO_ROOT/proto" \
  --call mesh.inventory.v1.InventoryService.CheckStock \
  -d '{"sku":"WIDGET-001","quantity":1}' \
  -n "$N" -c "$C" \
  "$INVENTORY_ADDR"
