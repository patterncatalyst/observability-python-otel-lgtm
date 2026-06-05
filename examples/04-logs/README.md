# Demo 4 — logs that link to traces

The shared logging config emits JSON and stamps every record with the active
`trace_id`/`span_id`. In Grafana, a log in Loki links to its trace in Tempo and
back again — the ids are the join key.

```bash
./demo.sh
```
