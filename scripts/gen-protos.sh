#!/usr/bin/env bash
# gen-protos.sh — compile the shared protos under proto/ into Python stubs.
#
# Stubs are generated into a `generated/` package inside each service that needs
# them (the order service needs the inventory + payment clients; inventory and
# payment need their own server stubs). They are build artifacts — ignored by
# git and regenerated here and in each service's container build.
#
# Usage:  scripts/gen-protos.sh [target_dir]
#   target_dir defaults to a shared ./generated at the repo root for local dev;
#   the container build calls it with the in-image site-packages path.
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$(dirname "$0")")"

OUT="${1:-generated}"
mkdir -p "$OUT"

# grpcio-tools provides the protoc plugin for Python + gRPC.
python -m grpc_tools.protoc \
  -I proto \
  --python_out="$OUT" \
  --grpc_python_out="$OUT" \
  --pyi_out="$OUT" \
  proto/shop/common/v1/common.proto \
  proto/shop/inventory/v1/inventory.proto \
  proto/shop/payment/v1/payment.proto

# Make every generated package directory importable.
find "$OUT" -type d -exec sh -c 'touch "$1/__init__.py"' _ {} \;

echo "Generated gRPC stubs into $OUT/"
