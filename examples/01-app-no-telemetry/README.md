# Demo 1 — the app, end to end, with no telemetry

This is the baseline the whole talk builds on: a working FastAPI service whose
requests make an async round trip through Kafka and Postgres, and a Grafana
stack that — for now — shows nothing about it.

## What it demonstrates

- The compute service running end to end: `POST /compute` publishes a job to the
  `compute.requests` Kafka topic, the worker reads it, does a read-then-write
  round trip against Postgres, and publishes the answer to `compute.replies`,
  which the API consumes and returns to the caller.
- That a healthy app is *opaque*: the LGTM stack is up, but with telemetry
  disabled there are no traces, no metrics, and no logs to look at. That gap is
  what every later demo fills.

## How to drive it

```bash
cd examples/01-app-no-telemetry
./demo.sh            # bring the shared stack up and POST one request
./demo.sh drive      # POST another request against an already-up stack
./demo.sh down       # stop the stack (keep volumes)
```

`POST /compute {"n": 100}` returns `{"request_id": "…", "n": 100, "result": 5050}`
— the worker computes the triangular number `n·(n+1)/2` times the `multiplier`
config row (which seeds to `1`).

## What to look for

- The HTTP response comes back only after the reply has travelled all the way
  around — API → Kafka → worker → Postgres → Kafka → API.
- Open Grafana at <http://localhost:3000>. Explore — and notice there is nothing
  about this request anywhere. That is the baseline.
- (Optional) Open the Kafka UI at <http://localhost:8090> to watch messages land
  on the two topics, and connect to Postgres to see the `jobs` row appear.

## Verification status

<span class="status status--unverified">unverified</span> — written carefully
but not yet run end to end. A real run must confirm, on Fedora and on macOS
(Podman machine): the stack comes up cleanly from a cold `podman compose up
--build`; the API reaches healthy; `POST /compute {"n":100}` returns
`result: 5050`; a `jobs` row is written; and the app image builds on the chosen
UBI Python base (the Python 3.14 base-image tag is an open question — see the
reconciliation plan).
