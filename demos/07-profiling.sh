#!/usr/bin/env bash
# Demo 7 — Continuous profiling: the flame graph inside a slow span (a sketch)
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 7 "Continuous profiling — inside the slow span"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "Traces tell you which span was slow; profiling tells you which \
functions inside it burned the CPU — the view the other three signals can't \
give, because they stop at the process boundary. Be candid with the room: this \
is the least-settled signal. It needs an otel-lgtm image that bundles \
Pyroscope, a profiles pipeline in the Collector, and the Pyroscope SDK on the \
service (see _docs/11-profiling.md). With that in place, the link from a span \
to its flame graph is Grafana's tracesToProfiles."

if [[ -z "${PYROSCOPE_ADDRESS:-}" ]]; then
    note "PYROSCOPE_ADDRESS isn't set, so obs.profiling is a no-op and there may be"
    printf '%b\n' "    nothing to show yet. Enable profiling first (see the chapter), or treat this"
    printf '%b\n' "    as the 'here's where it would go' beat."
fi

section "Step 1 — Generate some CPU to profile"
say "Continuous load so the profiler has stacks to sample while we look."
load_start 300

section "Step 2 — Open the flame graph for a slow span"
watch "from a slow /orders trace, 'Profiles for this span' opens the CPU flame \
graph for that service and time window. Read down from the widest frame to the \
function that actually spent the time."
browser "$GRAFANA_URL/explore" "Open a slow trace in Tempo and use 'Profiles \
for this span' (Tempo → Pyroscope via tracesToProfiles) to land in the flame \
graph. If the link or graph is empty, that's the enable-steps caveat above — \
frame it as the standards-track-but-young signal it is."

say "Profiling rounds out the picture: the trace localises the slow span across \
services, and the profile localises the slow function inside one. Honest \
caveat for the audience — the backend ships in the image, but the Python client \
side is still moving."

demo_end "The fourth signal, where the CPU goes inside a slow span — shown for \
what it is, a sketch worth validating. Next: the live picture of the whole \
system at once."
