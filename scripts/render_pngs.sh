#!/usr/bin/env bash
# Rasterise the shared SVG figures to PNG for the slide deck.
#   scripts/render_pngs.sh
# Produces deck/png/<name>.png from assets/diagrams/<name>.svg
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$SCRIPT_DIR/.."
mkdir -p deck/png
for svg in assets/diagrams/fig-*.svg; do
  soffice --headless --convert-to png:"draw_png_Export" --outdir deck/png "$svg" >/dev/null 2>&1
done
ls -1 deck/png
