#!/usr/bin/env bash
# One-shot: size → drawings md → STLs → design PDF
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${ROOT}/.venv/bin/python"

[ -x "$PY" ] || { python3 -m venv .venv && PY="${ROOT}/.venv/bin/python" && "$PY" -m pip install -q -e .; }

"$PY" simulation/run_sizing.py --power "${POWER_W:-10}" --density "${POWER_DENSITY:-8}"
"$PY" scripts/generate_drawings_md.py
bash hardware/scripts/export_stl.sh

if [ -d ../pdf-genesis/.venv ] || [ -d ../pdf-genesis/src ]; then
  (cd ../pdf-genesis && [ -x .venv/bin/python ] || python3 -m venv .venv && .venv/bin/pip install -q -e .)
  ../pdf-genesis/.venv/bin/python -m pdf_genesis.cli \
    "$ROOT/exports/sgh1_design.json" \
    -o "$ROOT/exports/SGH1_Design_Report.pdf" || true
fi

echo "=== CHORUS-SGH-1 build complete ==="
echo "  CAD:     hardware/openscad/ ($(ls hardware/openscad/*.scad | wc -l) files)"
echo "  STL:     hardware/stl/"
echo "  Drawings: hardware/DRAWINGS_DIMENSIONS.md"
echo "  PDF:     exports/SGH1_Design_Report.pdf"
