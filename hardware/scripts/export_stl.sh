#!/usr/bin/env bash
set -euo pipefail
DH="$(cd "$(dirname "$0")/../.." && pwd)"
SCAD="$DH/hardware/openscad"
OUT="$DH/hardware/stl"
PY="$DH/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

mkdir -p "$OUT"
cd "$DH"
"$PY" simulation/run_sizing.py --power "${POWER_W:-10}" --density "${POWER_DENSITY:-8}"

PARTS=(
  sgh1_membrane_plate
  sgh1_end_cap
  sgh1_membrane_housing
  sgh1_manifold_feed
  sgh1_manifold_draw
  sgh1_pressure_vessel_ring
  sgh1_skid_frame
  chorus_skid_enclosure
  chorus_aeh_panel
  sgh1_pump_mount
  sgh1_sensor_bracket
  sgh1_px_module
  sgh1_turbine_housing
  sgh1_relief_valve_block
  sgh1_drip_tray
  sgh1_mount_rail
  sgh1_feed_tank_adapter
  sgh1_brine_tank_adapter
  sgh1_flange_adapter
  sgh1_us_mount_ring
  sgh1_red_cartridge_v2
  sgh1_assembly
  sgh1_exploded_assembly
)

if ! command -v openscad &>/dev/null; then
  echo "openscad not installed — $(ls "$SCAD"/*.scad | wc -l) .scad files ready in $SCAD"
  echo "  sudo apt install -y openscad && $0"
  exit 0
fi

for p in "${PARTS[@]}"; do
  echo "STL: $p"
  openscad -o "$OUT/$p.stl" "$SCAD/$p.scad" 2>/dev/null || echo "  WARN: $p failed"
done
echo "Exported → $OUT ($(ls "$OUT"/*.stl 2>/dev/null | wc -l) files)"
