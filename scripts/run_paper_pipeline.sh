#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
python -m simulation.experiments
python -m simulation.pi_groups
python -m simulation.symbolic_checks
python scripts/audit_openscad.py
python scripts/generate_paper_figures.py
python scripts/build_research_paper.py
echo "Done: papers/Black_2026_CHORUS_SGH1_PoC.pdf"
