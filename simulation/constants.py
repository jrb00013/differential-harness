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

# UDT / AOR / VOH vision stack (docs/UDT_PHYSICS.md, docs/VOH_PHYSICS.md)
C_SOUND_WATER = 1500.0  # m/s
F_US_DEFAULT = 28_000.0  # Hz — e90 ultrasonic carrier
LAMBDA_E90_REF_M = 1.0  # normalization for byte_len scaling
N_RAYS_DEFAULT = 64534  # design-point ray mesh; bench uses fewer transducers
ETA_TINK_DEFAULT = 0.15  # Tink coupling efficiency — calibrate T1b
E0_JOULES = 1e-6  # particle-byte energy quantum
TAU_SPIN_DEFAULT_NM = 0.012  # bench motor torque — calibrate T1c
RPM_TO_RAD_S = 2 * 3.141592653589793 / 60.0


def tau_spin_from_rpm(rpm: float, tau_at_100rpm_Nm: float = TAU_SPIN_DEFAULT_NM * (100.0 / 60.0)) -> float:
    """Map bench RPM to motor torque (linear placeholder until T1c fit)."""
    return tau_at_100rpm_Nm * (rpm / 100.0)


def rpm_from_omega(omega_rad_s: float) -> float:
    return omega_rad_s * 60.0 / (2 * 3.141592653589793)
