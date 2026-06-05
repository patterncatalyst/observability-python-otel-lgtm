# tools/

Ways to exercise the running mesh so there is something to look at in Grafana.
Bring the stack up first (`cd stack && podman compose up --build`).

## curl — single requests

```bash
tools/curl/place-order.sh                 # place a default order, prints order_id
tools/curl/place-order.sh GIZMO-003 2     # specific SKU + quantity
tools/curl/get-order.sh <ORDER_ID>        # read it back (REST)
tools/curl/graphql-reviews.sh <ORDER_ID>  # order + reviews (GraphQL)
```

A successful `place-order` produces one trace that spans the order REST handler,
the inventory and payment gRPC calls, the Postgres writes, and the Kafka publish,
plus the shipping and notification consumer spans once the event is processed.

## Postman — a collection of the external edges

Import `postman/observability-mesh.postman_collection.json`. "Place order (REST)"
stashes the returned `order_id` in a collection variable, so "Get order" and the
GraphQL requests work without copy-paste. "Place order — payment declined" pushes
the amount over the payment ceiling to generate an error trace on demand.

## Load generators

```bash
tools/load/hey-orders.sh 500 20      # 500 REST orders, concurrency 20
tools/load/ghz-inventory.sh 2000 50  # 2000 gRPC CheckStock calls, concurrency 50
```

`hey` drives the REST edge end to end; `ghz` drives the inventory gRPC service
directly using the shared proto, which is handy when you want one service's RED
metrics and spans in isolation. Install notes are in each script's header.
