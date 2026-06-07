#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# _demo.sh — shared presentation engine for the OpenTelemetry talk demos.
#
# Source this from each demos/NN-*.sh. It provides:
#   • the narrate → stop → run rhythm used throughout the presentation,
#   • a browser() excursion helper that cues stepping out to Grafana / Tempo
#     and stops, since the payoff of every demo is in the UI,
#   • colour/formatting helpers,
#   • endpoint shortcuts (GRAFANA_URL / ORDER_URL / REVIEW_URL),
#   • a soft stack check that SKIPS gracefully instead of crashing, and
#   • automatic cleanup of anything a demo spawns.
#
# Design goal: a live demo must never die on stage. Commands that touch the
# stack are run "soft" — a failure prints an explanation and the show goes on.
# The only hard rule is: keep talking, keep moving.
#
# These demos drive the SAME services and stack as the tutorial, but they are
# presenter-driven (narrate, run live, step to the browser), not step-by-step
# build instructions — that's what examples/ and _docs/ are for.
#
# Not meant to be executed directly.
# ─────────────────────────────────────────────────────────────────────────────

# No `set -e`: a flaky request must not abort the talk. We manage exit codes
# by hand and let run_soft/run_fail report them.
set -uo pipefail

# ── Colours (auto-disabled when stdout isn't a tty) ─────────────────────────
if [[ -t 1 ]]; then
    GREEN=$'\033[0;32m'; RED=$'\033[0;31m';  YELLOW=$'\033[1;33m'
    CYAN=$'\033[0;36m';  BLUE=$'\033[0;34m'; MAGENTA=$'\033[0;35m'
    BOLD=$'\033[1m';     DIM=$'\033[2m';     NC=$'\033[0m'
else
    GREEN=''; RED=''; YELLOW=''; CYAN=''; BLUE=''; MAGENTA=''
    BOLD=''; DIM=''; NC=''
fi

# ── Endpoint shortcuts ──────────────────────────────────────────────────────
# Override before launching, e.g.  GRAFANA_URL=http://box:3000 ./demos/run.sh 1
: "${GRAFANA_URL:=http://localhost:3000}"   # Grafana (traces, metrics, logs, graph)
: "${ORDER_URL:=http://localhost:8080}"     # order service — REST edge
: "${REVIEW_URL:=http://localhost:8081}"    # review service — GraphQL edge
export GRAFANA_URL ORDER_URL REVIEW_URL

# Path to the stack/ dir, for the bring-up hint.
DEMOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$DEMOS_ROOT/.." && pwd)"
: "${STACK_DIR:=$REPO_ROOT/stack}"

# Set DEMO_NO_PAUSE=1 to auto-advance (handy for a dry run / recording).
: "${DEMO_NO_PAUSE:=}"

_WIDTH=74
_RULE_CHAR='─'
_rule() { local n="${1:-70}"; printf '%b' "${DIM}"; printf "${_RULE_CHAR}%.0s" $(seq 1 "$n"); printf '%b\n' "${NC}"; }

# ── Cleanup bookkeeping ─────────────────────────────────────────────────────
declare -a _DEMO_PIDS=()
track_pid() { _DEMO_PIDS+=("$1"); }   # a background load generator to kill on exit

_demo_cleanup() {
    local p
    for p in "${_DEMO_PIDS[@]:-}"; do
        [[ -n "$p" ]] && kill "$p" >/dev/null 2>&1 || true
    done
}

# ── Narration ───────────────────────────────────────────────────────────────

# Big banner that opens a demo. Installs the cleanup trap.
# Usage: demo_title 1 "A trace for free"
demo_title() {
    local n="$1"; shift
    local title="$*"
    trap _demo_cleanup EXIT
    echo
    printf '%b\n' "${BOLD}${MAGENTA}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    printf '%b\n' "${BOLD}${MAGENTA}║${NC}  ${BOLD}DEMO ${n}${NC}  ·  ${BOLD}${title}${NC}"
    printf '%b\n' "${BOLD}${MAGENTA}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

demo_intro() { say "$@"; pause; }

section() { echo; printf '%b\n' "${BOLD}${CYAN}━━ $* ${NC}"; }

say() { echo; printf '%s\n' "$*" | fold -s -w "$_WIDTH" | sed 's/^/  /'; }

note()    { echo; printf '%b\n' "  ${YELLOW}▸ $*${NC}"; }
caution() { echo; printf '%b\n' "  ${RED}⚠ $*${NC}"; }
watch()   { echo; printf '%b\n' "  ${BLUE}👀 Watch for:${NC} $*"; }
good()    { printf '%b\n' "  ${GREEN}✓ $*${NC}"; }

# An explicit stop. The audience reads the screen; presenter narrates; Enter moves on.
pause() {
    [[ -n "$DEMO_NO_PAUSE" ]] && { echo; return 0; }
    echo
    _rule 70
    printf '%b' "  ${DIM}▸ press ${NC}${BOLD}Enter${NC}${DIM} to continue${NC}  "
    IFS= read -r _ </dev/tty 2>/dev/null || true
    echo
}

# ── The browser excursion ───────────────────────────────────────────────────
# The whole point of these demos is what you SEE. browser() prints a clear
# "step out to the browser" callout with the URL and what to look at, then stops
# so you can drive the UI live and talk over it.
# Usage: browser "$GRAFANA_URL/explore" "Pick the Tempo data source, Search, and open the most recent POST /orders trace."
browser() {
    local url="$1"; shift
    echo
    printf '%b\n' "  ${BOLD}${BLUE}🌐 Step out to the browser${NC}"
    printf '%b\n' "     ${BOLD}${url}${NC}"
    [[ $# -gt 0 ]] && say "$*"
    pause
}

# ── Running commands ────────────────────────────────────────────────────────
# Each runner shows the command first, STOPS (so you can talk over it), then
# executes. Output streams live. Nothing here aborts the script.
_show_cmd() { echo; printf '%b\n' "  ${BOLD}${GREEN}\$ $1${NC}"; }
_stop_then_run() {
    [[ -n "$DEMO_NO_PAUSE" ]] || {
        printf '%b' "  ${DIM}▸ ${NC}${BOLD}Enter${NC}${DIM} to run${NC}  "
        IFS= read -r _ </dev/tty 2>/dev/null || true
    }
    echo
}

run() {
    local cmd="$1"
    _show_cmd "$cmd"
    _stop_then_run
    eval "$cmd"
    local rc=$?
    [[ $rc -ne 0 ]] && printf '%b\n' "  ${DIM}(command exited ${rc})${NC}"
    return 0
}

# A command we EXPECT to fail (e.g. a decline → HTTP 402). The non-zero exit
# is the teaching point and is reported as success.
run_fail() {
    local cmd="$1"
    _show_cmd "$cmd"
    _stop_then_run
    eval "$cmd"
    local rc=$?
    echo
    if [[ $rc -ne 0 ]]; then
        good "…and it returned non-zero (exit ${rc}) — that's the point."
    else
        note "That exited 0; the demo data may differ. Worth a look on screen."
    fi
    return 0
}

# Stack/network step that may not complete. A failure degrades to a note.
run_soft() {
    local cmd="$1"
    _show_cmd "$cmd"
    _stop_then_run
    eval "$cmd"
    local rc=$?
    echo
    if [[ $rc -ne 0 ]]; then
        note "That step didn't complete (exit ${rc}) — often the stack still warming"
        printf '%b\n' "    ${YELLOW}  up or a service restarting. The explanation above is what matters.${NC}"
    fi
    return 0
}

# ── Preflight ───────────────────────────────────────────────────────────────
require_tools() {
    local missing=() t
    for t in "$@"; do command -v "$t" >/dev/null 2>&1 || missing+=("$t"); done
    if (( ${#missing[@]} )); then
        caution "Skipping — these tools aren't on PATH: ${missing[*]}"
        say "Install them first (see _docs/01-prerequisites.md), then re-run this demo."
        return 1
    fi
    return 0
}

# Soft check that the stack is up. SKIPs the demo (exit 0) rather than crash.
require_stack() {
    if ! curl -sf -o /dev/null --max-time 3 "$ORDER_URL/health" 2>/dev/null; then
        caution "The stack isn't answering at $ORDER_URL."
        say "Bring it up first, then re-run:  (cd \"$STACK_DIR\" && podman compose up -d)"
        say "Give it a moment to go healthy — the order service waits on Postgres, Kafka, and the LGTM backend."
        return 1
    fi
    return 0
}

# ── Load helpers ────────────────────────────────────────────────────────────
# Place a healthy order (quantity 1 → well under the payment ceiling).
order_ok() {
    curl -sS -X POST "$ORDER_URL/orders" -H 'Content-Type: application/json' \
        -d '{"customer_id":"demo","sku":"WIDGET-001","quantity":1}'
}
# Place an order that declines at payment (quantity 60 × 1999 > the 100000 ceiling → HTTP 402).
order_declined() {
    curl -sS -o /dev/null -w 'HTTP %{http_code}\n' -X POST "$ORDER_URL/orders" \
        -H 'Content-Type: application/json' \
        -d '{"customer_id":"demo","sku":"WIDGET-001","quantity":60}'
}
# Background load so a graph/metric has something to show. Auto-killed on exit.
load_start() {
    local n="${1:-300}"
    ( for _ in $(seq 1 "$n"); do
        curl -sf -o /dev/null -X POST "$ORDER_URL/orders" -H 'Content-Type: application/json' \
            -d '{"customer_id":"load","sku":"WIDGET-001","quantity":1}' 2>/dev/null
        curl -sf -o /dev/null "$ORDER_URL/health" 2>/dev/null
      done ) &
    track_pid "$!"
    note "Background load started (pid $!) — it will stop automatically when the demo ends."
}

# ── Demo closer ─────────────────────────────────────────────────────────────
demo_end() {
    echo
    printf '%b\n' "  ${BOLD}${MAGENTA}── end of demo ─────────────────────────────────────────────────────${NC}"
    [[ $# -gt 0 ]] && say "$@"
    pause
}
