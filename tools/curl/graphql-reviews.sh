#!/usr/bin/env bash
# Query an order and its product reviews through the GraphQL read edge. Each
# resolver opens its own span, so this single POST shows up as a resolver tree
# in Tempo.
#   tools/curl/graphql-reviews.sh <ORDER_ID>
set -euo pipefail
REVIEW_URL="${REVIEW_URL:-http://localhost:8081}"
ORDER_ID="${1:?usage: graphql-reviews.sh <ORDER_ID>}"
read -r -d '' QUERY <<GQL || true
{ "query": "{ order(orderId: \"$ORDER_ID\") { orderId sku status reviews { rating body } } }" }
GQL
curl -sS -X POST "$REVIEW_URL/graphql" \
  -H 'Content-Type: application/json' \
  -d "$QUERY"
echo
