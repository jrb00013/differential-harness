"""SI constants and literature anchors.

Real-world backing: docs/math/REAL_WORLD_DATA.md
"""

R_GAS = 8.314462618  # J/(mol·K)
F_FARADAY = 96485.33212  # C/mol
T_REF = 298.15  # K
I_NACL = 2.0  # van't Hoff factor

# Concentrations mol/m³ (NaCl equivalent, i=2)
C_SEAWATER = 600.0  # ~35 g/L TDS — Perth/estuary feed class
C_RIVER = 20.0  # Statkraft / estuary RED low stream
C_BRINE_8PCT = 1400.0  # ~8 wt% — upper sidestream reject (SGH-1 nominal)
C_BRINE_PERth = 1200.0  # ~70 g/L SWRO brine — Perth / WaterReuse 1.5–2× seawater
C_TREATED_WW = 5.0  # Treated effluent / river diluate class

# Literature anchors (W/m²)
P_BLUE_W_M2 = 15.0  # High-performance RED lab/demo ceiling (verify per paper)
P_PRO_COMMERCIAL_W_M2 = 6.3  # Pedersen et al. 2024 — RO membrane PRO @ 30°C, seawater
P_STATKRAFT_TOFTE_W_M2 = 1.0  # Tofte pilot initial membrane level
P_PRO_VIABILITY_THRESHOLD = 5.0  # Industry threshold W/m²

# Perth desalination (for parasitic fraction examples)
PERTH_DESAL_M3_PER_DAY = 144_000.0
PERTH_DESAL_KWH_PER_M3 = 3.5

ETA_MEM_DEFAULT = 0.35
ETA_HYD_DEFAULT = 0.55
