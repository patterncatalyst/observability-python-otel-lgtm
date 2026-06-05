# proto/

Shared Protocol Buffers contracts for the mesh's **gRPC** hops, kept at the repo
top level (as in the data-mesh reference architecture) so every service compiles
against one copy of the truth rather than vendoring its own.

```
proto/mesh/
  common/v1/common.proto       # shared types (Money)
  inventory/v1/inventory.proto # InventoryService: CheckStock, Reserve
  payment/v1/payment.proto     # PaymentService: Authorize
```

Compile to Python stubs with:

```bash
scripts/gen-protos.sh            # → ./generated/ for local dev
```

The generated `*_pb2.py` / `*_pb2_grpc.py` files are **build artifacts** — they
are git-ignored and regenerated both here and inside each service's container
build. Only the `.proto` files are source.

These contracts cover only the synchronous service-to-service calls. The
asynchronous hops use **Kafka** with JSON event payloads (see
`services/*/events.py` and the `order.placed` event), and the external edges are
**REST** (order service) and **GraphQL** (review service) — none of which need a
proto.
