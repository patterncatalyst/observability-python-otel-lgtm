#!/usr/bin/env bash
# Place one order through the external REST edge. This is the request the whole
# talk traces: it fans out to inventory (gRPC), payment (gRPC), Postgres, and
# Kafka. Prints the JSON response (includes the order_id you can feed to the
# other scripts).
#
#   tools/curl/place-order.sh [SKU] [QUANTITY] [CUSTOMER_ID]
set -euo pipefail
ORDER_URL="${ORDER_URL:-http://localhost:8080}"
SKU="${1:-WIDGET-001}"
QTY="${2:-1}"
CUSTOMER="${3:-cust-42}"

curl -sS -X POST "$ORDER_URL/orders" \
  -H 'Content-Type: application/json' \
  -d "{\"customer_id\":\"$CUSTOMER\",\"sku\":\"$SKU\",\"quantity\":$QTY}" | tee /dev/stderr
echo
