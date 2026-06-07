#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run.sh — launcher for the OpenTelemetry talk demos.
#
#   ./demos/run.sh             # interactive menu
#   ./demos/run.sh 2           # run demo 2 only
#   ./demos/run.sh all         # the full walkthrough, in order
#   ./demos/run.sh list        # list the demos
#   ./demos/run.sh check       # preflight: tools + stack reachability
#
# Each demo is also runnable on its own, e.g.  ./demos/01-trace-for-free.sh
# Runs fine from a zsh prompt — the scripts use a bash shebang.
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail
DEMOS="$(cd "$(dirname "$0")" && pwd)"
source "$DEMOS/lib/_demo.sh"

mapfile -t FILES < <(ls "$DEMOS"/[0-9][0-9]-*.sh 2>/dev/null | sort)

_label() { sed -n '2s/^# //p' "$1"; }   # the "Demo N — …" summary on line 2

list() {
    echo
    printf '%b\n' "${BOLD}OpenTelemetry talk demos${NC}"
    echo
    local i f
    for i in "${!FILES[@]}"; do
        f="${FILES[$i]}"
        printf "  ${BOLD}%d${NC}  %s\n" "$((i+1))" "$(_label "$f")"
    done
    echo
}

check() {
    echo
    printf '%b\n' "${BOLD}Preflight${NC}"
    echo
    printf '%b\n' "  ${BOLD}Endpoints${NC} (override via env before launching):"
    printf "    GRAFANA_URL = %s\n" "$GRAFANA_URL"
    printf "    ORDER_URL   = %s\n" "$ORDER_URL"
    printf "    REVIEW_URL  = %s\n" "$REVIEW_URL"
    echo
    printf '%b\n' "  ${BOLD}Tools${NC}:"
    local t
    for t in podman curl jq; do
        if command -v "$t" >/dev/null 2>&1; then
            printf "    ${GREEN}✓${NC} %-7s %s\n" "$t" "$(command -v "$t")"
        else
            printf "    ${RED}✗${NC} %-7s ${DIM}(missing — see _docs/01-prerequisites.md)${NC}\n" "$t"
        fi
    done
    echo
    printf '%b\n' "  ${BOLD}Stack${NC}:"
    if curl -sf -o /dev/null --max-time 3 "$ORDER_URL/health" 2>/dev/null; then
        printf "    ${GREEN}✓${NC} order service answering at %s\n" "$ORDER_URL"
    else
        printf "    ${RED}✗${NC} order service not answering at %s\n" "$ORDER_URL"
        say "Bring the stack up before the talk:  (cd \"$STACK_DIR\" && podman compose up -d)"
    fi
    if curl -sf -o /dev/null --max-time 3 "$GRAFANA_URL/api/health" 2>/dev/null; then
        printf "    ${GREEN}✓${NC} Grafana answering at %s\n" "$GRAFANA_URL"
    else
        printf "    ${YELLOW}?${NC} Grafana not answering at %s (it's where every demo ends — make sure it's up)\n" "$GRAFANA_URL"
    fi
    echo
    say "Before a talk: bring the stack up, place a few warm-up orders so Tempo \
and the dashboards aren't empty, and have $GRAFANA_URL open in a tab. Demo 2 \
recreates a few services to toggle Kafka propagation, so allow a few seconds \
there."
    echo
}

run_one() {
    local idx=$(( $1 - 1 )) f
    if (( idx < 0 || idx >= ${#FILES[@]} )); then
        printf '%b\n' "${RED}No demo numbered $1.${NC} Try: ./demos/run.sh list"
        return 1
    fi
    f="${FILES[$idx]}"
    bash "$f"
}

walkthrough() {
    echo
    printf '%b\n' "${BOLD}${MAGENTA}Full walkthrough — ${#FILES[@]} demos, in order.${NC}"
    say "Each demo stops between steps and again before the next. Press Enter to \
advance; Ctrl-C to bail at any point. Have the browser open at $GRAFANA_URL."
    pause
    local n
    for n in $(seq 1 "${#FILES[@]}"); do run_one "$n"; done
    echo
    printf '%b\n' "${BOLD}${GREEN}That's the set. Thanks for following along.${NC}"
    echo
}

menu() {
    while true; do
        list
        printf '%b' "  ${BOLD}Pick a number, ${NC}a${BOLD} for all, ${NC}c${BOLD} to check, ${NC}q${BOLD} to quit:${NC} "
        IFS= read -r choice </dev/tty 2>/dev/null || choice="q"
        case "$choice" in
            [1-9]|[1-9][0-9]) run_one "$choice" ;;
            a|A|all)          walkthrough ;;
            c|C|check)        check ;;
            q|Q|quit|exit|"") echo; break ;;
            *) printf '%b\n' "  ${YELLOW}Didn't catch that.${NC}" ;;
        esac
    done
}

case "${1:-menu}" in
    menu)            menu ;;
    list|ls)         list ;;
    check|preflight) check ;;
    all|a)           walkthrough ;;
    [0-9]*)          run_one "$1" ;;
    -h|--help|help)  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//' ;;
    *) printf '%b\n' "${RED}Unknown argument: $1${NC}"; sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
