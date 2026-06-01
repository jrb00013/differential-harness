"""Extended prose sections for Joseph Black CHORUS-SGH-1 research paper."""

from __future__ import annotations


def fmt(ctx: dict, template: str) -> str:
    return template.format(**ctx)


def introduction_paragraphs(ctx: dict) -> list[str]:
    b, e, r, mc = ctx["base"], ctx["exp"], ctx["res"], ctx["mc"]
    return [
        "The twenty-first century expansion of desalination has created an overlooked by-product: "
        "continuous, high-grade salinity gradients at industrial sites. Every reverse-osmosis plant "
        "splits a feed stream into permeate and reject brine. Wastewater treatment plants discharge "
        "effluent at near-fresh salinity. Where these streams are co-located—as they are at coastal "
        "utilities worldwide—the Gibbs free energy of mixing is destroyed in outfalls and mixing zones. "
        "This manuscript asks whether that destruction can be reversed with physics-first engineering, "
        "honest thermodynamic accounting, and a bench-scale proof vehicle.",
        "We introduce <b>CHORUS</b> (Columnar Harvest of Osmotic, Rhizospheric, Orographic, and Solar flux) "
        "as a multi-layer framework for a notional 1 km² coastal or industrial column. CHORUS does not claim "
        "a new fundamental energy source. It claims that <i>already-present</i> fluxes—solar, osmotic, "
        "moist-electric, biological, and atmospheric—can be inventoried, bounded, and partially converted "
        "if each pathway respects the second law. The governing postulate is explicit: "
        "Σ P_extracted ≤ Σ Ė_in − TṠ.",
        f"The near-term hardware anchor is <b>CHORUS-Skid SGH-1</b>, a pressure-retarded osmosis (PRO) "
        f"bench harness sized for {ctx['sz']['P_target_W']:.0f} W equivalent output from anthropogenic "
        f"brine ({b['c_draw']:.0f} mol/m³) against treated wastewater class feed ({b['c_feed']:.0f} mol/m³). "
        f"At T = 298.15 K this pair yields Δπ = {b['delta_pi_MPa']:.2f} MPa—"
        f"{b['delta_pi_MPa']/e['estuary_RED']['delta_pi_MPa']:.1f}× the classic estuary RED reference. "
        "SGH-1 is accompanied by 23 OpenSCAD mechanical parts, a six-module Python simulation stack, "
        "DAQ logging, and test protocols T0–T2.",
        "This paper is deliberately tiered. <b>Tier 1 (defensible)</b> includes Van't Hoff osmotic thermodynamics, "
        "Kim–Baker optimal hydraulic pressure, solution-diffusion water transport, concentration polarization "
        "film theory, and bench-sized PRO geometry. <b>Tier 2 (exploratory)</b> includes Telluric Storm Coupling "
        "(TSC) conductance networks, global fair-weather circuit routing, and column-scale Monte Carlo sums that "
        f"reach {mc['column_MW_median']:.1f} MW/km² median but are dominated by land photovoltaics—not osmotic area.",
        "Readers should leave with three durable conclusions: (i) sidestream PRO on desal brine is the "
        "fastest credible PoC path; (ii) default membrane permeability must be bench-calibrated to close the "
        f"gap between {b['P_default_Lp_W']:.2f} W modeled and {ctx['sz']['P_target_W']:.0f} W targeted; "
        "(iii) CHORUS column narratives are scaling context, not bench claims.",
    ]


def literature_paragraphs(ctx: dict) -> list[str]:
    return [
        "Salinity-gradient power has been pursued along two electrochemical/hydraulic branches. "
        "<b>Reverse electrodialysis (RED)</b> places ion-exchange membranes between fresh and saline streams, "
        "generating Nernstian voltage and electrical current. Teng et al. (2026) report nanopore-engineered "
        "membranes achieving approximately 15 W/m² at estuary-grade concentrations—our Layer A calibration anchor.",
        "<b>Pressure-retarded osmosis (PRO)</b> pressurizes the draw compartment and extracts work via turbine "
        "or pressure exchanger as water permeates from feed. Statkraft's Tofte pilot (2009–2013) demonstrated "
        "feasibility but highlighted fouling, CP, and parasitic pumping as commercial barriers. Anthropogenic "
        "brine pairs can exceed estuary Δπ, trading membrane stress for higher volumetric driving force.",
        "Parallel harvest physics appear in moisture-enabled generators (Air-gen), hydrovoltaic streaming, "
        "evaporatively cooled photovoltaics, and microbial fuel cells. Fang et al. (2026) couple PV waste heat "
        "to magnetohydrodynamic enhancement—a Layer B motif. Virgo et al. (2020) bound atmospheric electricity. "
        "CHORUS integrates these as layers with explicit capacity factors rather than as interchangeable 'green energy'.",
        "Urban acoustic harvesting is not new; piezoelectric panels on noise-facing surfaces produce mW scales. "
        "Our AEH-1 module treats sound as (Mode A) supplemental rectified power and (Mode B) ultrasonic CP disruption "
        "on the PRO feed path—a coupling uncommon in osmotic power literature.",
    ]


def layer_a_paragraphs(ctx: dict) -> list[str]:
    e, r = ctx["exp"]["estuary_RED"], ctx["res"]
    return [
        "<b>Layer A</b> models osmotic mixing and blue energy at estuary-grade interfaces. For ideal NaCl "
        "with van't Hoff factor i = 2, π = iRTc. Mixing free energy for concentrated solutions underlies "
        "both RED and PRO; the difference is extraction mechanism (electrical vs hydraulic).",
        f"For c_sea = 600 mol/m³ and c_river = 20 mol/m³ at 298.15 K: Δπ = {e['delta_pi_MPa']:.3f} MPa. "
        f"Single-pair Nernst potential E_N = {e['E_N_mV']:.2f} mV; fifty pairs yield V_oc = {r['V_stack_V']:.2f} V. "
        "The electrical max-power theorem for linear internal resistance gives P''_max = V_oc²/(4R_int). "
        f"Calibrating to literature P_blue = {e['P_max_W_m2']:.0f} W/m² implies R_int = {r['R_int_ohm_m2']:.3f} Ω·m².",
        f"The Gibbs hydraulic mixing ceiling P_mix = Δπ·Q with illustrative Q = 500 m³/s gives "
        f"{e['P_mix_ceiling_MW']:.0f} MW—an upper bound on mechanical work available if all fresh water "
        "flux could be converted reversibly. Real membranes achieve a fraction of this; RED demonstrations "
        "target interface power density, not bulk mixing flow.",
        "Nanopore conductance models introduce slip length b: G(b) = G₀(1 + 2b/h). Higher slip increases "
        "areal conductance and hence power at fixed Δπ. This is a materials-science lever distinct from "
        "stacking more membrane area—important when land or interface area is constrained.",
    ]


def layer_b_paragraphs(ctx: dict) -> list[str]:
    r = ctx["res"]
    return [
        "<b>Layer B</b> addresses moist-electric and hydrovoltaic pathways (CHOR sub-layer). Water vapor "
        "chemical potential μ_v = μ_v° + RT ln(a_w) drives Fickian flux through porous media. Asymmetric "
        "nanopores with different top/bottom opening areas produce net charge separation (Air-gen class): "
        "I_q = e ΔΓ q̄_trans.",
        "Helmholtz–Smoluchowski streaming links pressure gradients in fine channels to streaming potential "
        "E_s = (εζ/ση) Δp. Power densities are typically mW/m² unless channel density and wetting are extreme.",
        f"The coupled PV–thermal node in our notebook solves C_th dT_s/dt = α_s G_solar − h_c(T_s−T_∞) − L_v ṁ_e − P_hybrid. "
        f"Steady evaporative cooling yields P_pv'' ≈ {r['P_pv_W_m2']:.1f} W/m² with incremental gain "
        f"ΔP'' ≈ {r['P_pv_gain_W_m2']:.1f} W/m² versus uncooled baseline—dominant in column Monte Carlo.",
        "CHORUS-Skid reserves plenum volume in chorus_skid_enclosure.scad for future moist-electric panels; "
        "v1 hardware validates PRO and AEH while keeping thermal ports on the critical path for v2 integration.",
    ]


def layer_c_paragraphs(ctx: dict) -> list[str]:
    r = ctx["res"]
    return [
        "<b>Layer C</b> covers rhizospheric harvest: sediment microbial fuel cells (SMFC) and piezoelectrotrophy. "
        "Butler–Volmer kinetics j = j₀[exp(α_a Fη/RT) − exp(−α_c Fη/RT)] bound anodic current. "
        "Power density P = j(E₀ − b log j − R_Ω j) peaks at intermediate current density.",
        f"Notebook §V reports P_MFC'' ≈ {r['P_mfc_uW_m2']:.1f} µW/m²—real biology, not a land-area leader. "
        "Piezoelectrotrophy couples mechanical stress from root growth, rain, or freeze–thaw to "
        "η_pzt P_mech feeding parallel bioelectrogenic pathways (NSO 2026 paradigm).",
        "In column accounting, SMFC receives full 1 km² area with CF = 1.0 but tiny P''—its median contribution "
        "is orders of magnitude below pv_hydro. CHORUS includes SMFC to avoid cherry-picking layers, not to sell soil power.",
    ]


def layer_d_paragraphs(ctx: dict) -> list[str]:
    r = ctx["res"]
    return [
        "<b>Layer D</b> bounds atmospheric charge harvest. Fair-weather global circuit current I_glob ~ 1–3 kA "
        "across ionosphere–surface potential 200–400 kV gives P_glob ~ 0.25–0.9 GW planet-wide.",
        f"Our illustrative anchor P_glob = {r['P_glob_GW']:.1f} GW implies areal mean ~10⁻⁴ W/m²—useful for "
        "order-of-magnitude routing stories, not farm-scale revenue.",
        "Mason-type collision charging dq/dt ∝ n_d² π d² v_rel Δq produces episodic power in storm cells. "
        "Tornado kinetic energy K = ½ρ V_tor π(D/2)² H is included as sanity check only—GW episodic, not baseload.",
    ]


def tsc_column_paragraphs(ctx: dict) -> list[str]:
    mc = ctx["mc"]
    return [
        "<b>Telluric Storm Coupling (TSC)</b> models atmosphere (a), soil (s), and estuary/water (w) as a "
        "three-node conductance network Gψ = I. Dissipated power P_TSC = ψᵀGψ routes charge—it does not create it.",
        "High-impedance harvesters (MEG, SMFC) benefit if a low-impedance path exists to a sink. TSC is "
        "architectural coupling for utilization, analogous to power electronics MPPT rather than a new turbine.",
        "Conductances G_as, G_sw, G_a0 in the notebook are <i>illustrative Siemens</i> pending field instrumentation. "
        "PoC papers must label TSC figures as scenario analysis, not measured coastal data.",
        f"The column balance P_column = Σ_k A_k CF_k ⟨P''_k⟩ is evaluated with lognormal uncertainty on each layer's "
        f"areal power density. Replicated Monte Carlo (N = {mc['N']}) gives median {mc['column_MW_median']:.2f} MW, "
        f"P10 {mc['column_MW_p10']:.2f} MW, P90 {mc['column_MW_p90']:.2f} MW for a 1 km² parcel.",
        f"Layer median shares: blue_energy {mc['layers']['blue_energy']['share_of_median_column_pct']:.1f}%, "
        f"pv_hydro {mc['layers']['pv_hydro']['share_of_median_column_pct']:.1f}%, "
        f"meg {mc['layers']['meg']['share_of_median_column_pct']:.2f}%, "
        f"smfc {mc['layers']['smfc']['share_of_median_column_pct']:.2f}%. "
        "Policy and civilizational narratives must respect this hierarchy.",
    ]


def layer_f_paragraphs(ctx: dict) -> list[str]:
    b, p = ctx["base"], ctx["pi"]
    sz = ctx["sz"]
    return [
        "<b>Layer F</b> is the engineering core: PRO on anthropogenic brine. Draw concentration c_d ≈ 1400 mol/m³ "
        "(~8 wt% NaCl reject) and feed c_f ≈ 5 mol/m³ (treated wastewater class) give the strongest Δπ in our study.",
        f"Δπ = {b['delta_pi_MPa']:.3f} MPa; Kim–Baker optimum ΔP* = {b['delta_P_star_bar']:.1f} bar. "
        "Water permeates according to V̇_w = L_p A(Δπ − ΔP). Hydraulic power P_hyd = ρ V̇_w ΔP; "
        "equivalent electrical power applies η_mem η_hyd.",
        f"SGH-1 targets P_target = {sz['P_target_W']:.0f} W at P''_design = {sz['P_density_W_m2']:.0f} W/m², "
        f"yielding A_mem = {sz['A_mem_m2']:.2f} m² implemented as {int(sz['n_plates'])} plates of "
        f"{sz['active_width_mm']:.0f}×{sz['active_height_mm']:.0f} mm active area each.",
        f"With default L_p = 1×10⁻¹² m/(Pa·s), steady model predicts P = {b['P_default_Lp_W']:.2f} W "
        f"(Π₅ = {p['Pi5_sim_over_target']:.3f}). Inverse sizing gives L_p* = {p['L_p_required_for_target']:.2e} m/(Pa·s) "
        "to hit 10 W—primary bench acceptance metric for T1 (±30%).",
        "Concentration polarization c_w/c_b = exp(J_w/k_m) reduces effective Δπ. Ultrasonic assist (AEH Mode B) "
        "models permeability gain g; net power subtracts P_US driver load. Feed flow Q_feed from model sets "
        f"hydraulic residence time; simulated Q = {b['Q_L_min']:.3f} L/min must be validated against rotameters.",
        "Functional requirement FR-1 mandates 0.4 ≤ ΔP/Δπ ≤ 0.6. Numerical experiment E1 confirms maximum at 0.5. "
        "Operating outside this band sacrifices power or risks over-pressurization relative to membrane burst pressure.",
    ]


def aeh_paragraphs(ctx: dict) -> list[str]:
    return [
        "<b>AEH-1 (Acoustic Energy Harvest)</b> mounts on the CHORUS skid frame with six-by-four Helmholtz-inspired "
        "cells (chorus_aeh_panel.scad). <b>Mode A</b> converts incident acoustic intensity I = p_rms²/(ρc) to "
        "electrical power P = η I A. At η = 2% and A = 0.5 m², urban SPL 90–96 dB yields sub-watt to few-mW harvest—"
        "supplemental to DAQ, not baseload.",
        "<b>Mode B</b> drives 28 kHz ultrasonic transducers on the feed manifold to disrupt CP. Modeled as multiplicative "
        "gain g on L_p, net benefit requires P_PRO(g) − P_US − P_0 > 0. Experiment E5 shows crossover near g ≈ 1.5 "
        "at 1.5 W/m² ultrasonic parasitic for A = 0.72 m².",
        "Co-location with traffic, desal pumps, and HVAC plant noise is deliberate: Layer E in the original CHORUS "
        "vision treats cities as acoustic environments. Honest accounting keeps Mode A at mW and Mode B contingent on bench proof.",
    ]


def hardware_paragraphs(ctx: dict) -> list[str]:
    sz = ctx["sz"]
    return [
        f"The CHORUS-Skid frame ({sz['frame_length_mm']}×{sz['frame_width_mm']}×{sz['frame_height_mm']} mm) supports "
        f"a membrane housing OD {sz['housing_od_mm']:.0f} mm, length {sz['housing_length_mm']} mm, bolt circle "
        f"{sz['bolt_pattern_mm']:.0f} mm. PRO fluid path includes feed/draw manifolds, pressure vessel rings, "
        "end caps, PX module, turbine housing, and relief valve block.",
        "PRO-01 through PRO-09 cover the wetted stack. CHOR-01 enclosure provides thermal/moist plenum. "
        "AEH-01 panel and AEH-02 ultrasonic mount ring attach without penetrating the high-pressure draw circuit. "
        "STR-01 frame, STR-02 drip tray, STR-03 rails contain brine leaks per FR-4.",
        "Utilities UT-01–UT-05 include pump mount, sensor bracket, and tank adapters (feed/brine/flange). "
        "v2 module RED-01 red_cartridge_v2.scad shares bolt pattern for nanopore RED experiments on the same skid.",
        "Materials: SS316 wetted paths; EPDM gaskets; membrane sheet vendor TBD (FO/PRO class). "
        "P&ID: low-sal tank → feed pump → prefilter → feed manifold → membrane stack → draw manifold → "
        "PX/throttle → turbine/motor load → brine return. Rupture disk at 1.2× ΔP*.",
        "Electrical: GFCI on pump/DAQ; piezo rectifier to supplemental bus; US driver on isolated supply. "
        "See hardware/bom/SGH1_BOM.csv for 35+ line items and hardware/electrical/WIRING.md for channel map.",
    ]


def test_protocol_paragraphs(ctx: dict) -> list[str]:
    return [
        "<b>T0 — Coupon test:</b> Air leak test 3 bar, 10 min; water flush; establish feed 5 g/L and draw 80 g/L "
        "simulant; ramp ΔP from 0 → 0.5Δπ → ΔP* over 30 min; log at 1 Hz. Pass: no leaks, positive steady power 15 min.",
        "<b>T1 — Full stack:</b> Hydrotest draw at 1.25× ΔP*; 1 h steady run; compare P'' to simulation ±30%. "
        "This directly tests L_p calibration and CP losses.",
        "<b>T2 — Field sidestream:</b> Utility NDA; tie-in to real brine and effluent; replicate logging.",
        "<b>AEH tests:</b> SPL meter at panel; Voc into 1 MΩ; US on/off comparison for Mode B flux gain.",
    ]


def discussion_paragraphs(ctx: dict) -> list[str]:
    mc, b, p = ctx["mc"], ctx["base"], ctx["pi"]
    return [
        "Sidestream PRO wins the near-term race because infrastructure exists: tanks, pumps, permits, and operators. "
        "Estuary RED requires greenfield environmental permitting and long membrane interfaces in biofouling waters.",
        f"The {b['P_default_Lp_W']:.2f} W vs {ctx['sz']['P_target_W']:.0f} W gap is the central honest tension. "
        "It is not fraud—it is an explicit call for membrane characterization. Literature PRO foils after "
        "conditioning often exceed bare 1×10⁻¹² m/(Pa·s).",
        f"Column median {mc['column_MW_median']:.1f} MW/km² is a thought experiment with PV-dominated area weights. "
        "Investors and policymakers must not conflate it with SGH-1 bench watts.",
        "TSC and global circuit layers are valuable for systems storytelling and patent differentiation but must "
        "not appear in spec sheets as measured performance.",
        "Ultrasonic CP assist is promising where feed salinity is high and J_w is large enough that polarization "
        "loss exceeds driver parasitics—exactly the brine/effluent regime.",
        "Open-source release (differential-harness) enables third-party falsification—critical for pre-revenue hardware science.",
    ]


def worked_examples_paragraphs(ctx: dict) -> list[str]:
    b, e, r = ctx["base"], ctx["exp"]["estuary_RED"], ctx["res"]
    return [
        "<b>Worked example 1 (estuary RED):</b> With c_sea = 600, c_river = 20 mol/m³, T = 298.15 K, "
        f"E_N = {e['E_N_mV']:.2f} mV per pair. Fifty pairs → V_oc = {r['V_stack_V']:.2f} V. "
        f"If P''_max = {e['P_max_W_m2']:.0f} W/m², then R_int = V_oc²/(4 P'') = {r['R_int_ohm_m2']:.3f} Ω·m².",
        "<b>Worked example 2 (brine PRO):</b> c_draw = 1400, c_feed = 5 → "
        f"Δπ = {b['delta_pi_MPa']:.2f} MPa. At ΔP = Δπ/2, L_p = 1×10⁻¹², A = 0.72 m², "
        f"η_mem η_hyd = 0.35×0.55 → P ≈ {b['P_default_Lp_W']:.2f} W. To reach 10 W, scale L_p to "
        f"{ctx['pi']['L_p_required_for_target']:.2e} m/(Pa·s) or add membrane area beyond twelve plates.",
        "<b>Worked example 3 (mixing ceiling):</b> Δπ_estuary × Q = "
        f"{e['P_mix_ceiling_MW']:.0f} MW at Q = 500 m³/s illustrates that bulk mixing power is enormous "
        "but inaccessible without controlled interface area and membrane technology.",
    ]


def ranked_concepts_paragraphs(ctx: dict) -> list[str]:
    c = ctx.get("claims", {})
    return [
        "The CHORUS notebook exports four ranked concept tags used throughout the program:",
        f"<b>Safest:</b> {c.get('safest', 'PRO salinity-gradient core')}. "
        f"<b>Smartest:</b> {c.get('smartest', 'Ultrasonic CP + PRO')}. "
        f"<b>Strangest:</b> {c.get('strangest', 'TSC + AEH urban panel')}. "
        f"<b>Civilization-scale:</b> {c.get('civilization', 'Co-located brine + column')}.",
        "These tags are communication devices, not performance guarantees. Safest maps to Tier-1 bench PRO. "
        "Smartest maps to AEH Mode B contingent on positive E5 net gain. Strangest maps to Tier-2 TSC. "
        "Civilization maps to column Monte Carlo only.",
    ]


def deployment_paragraphs(ctx: dict) -> list[str]:
    return [
        "Deployment targets co-located desalination and wastewater treatment plants where brine and "
        "effluent are available without new intake infrastructure. SGH1_PATENT_AND_DEPLOYMENT.md outlines "
        "claim focus on PRO-on-brine plus ultrasonic CP assist plus integrated DAQ—not on column MW totals.",
        "Outreach sequence: (1) bench T0/T1 at lab simulant; (2) pilot T2 at utility sidestream; "
        "(3) scale membrane area or plate count toward kW-class if L_p validates. "
        "Regulatory path follows existing industrial water handling, not new estuary impingement.",
        "Economic viability requires net positive skid power after pump, pretreatment, and US parasitics—"
        "a calculation deferred until parasitics.py is integrated. Even at 10 W bench proof, "
        "the learning value is membrane characterization under real Δπ, not immediate LCOE competitiveness.",
    ]


def notebook_walkthrough_paragraphs(ctx: dict) -> list[str]:
    return [
        "notebooks/CHORUS_physics_proof.ipynb implements §I–VIII: symbolic Gibbs and Nernst (SymPy); "
        "RED slip conductance sweep (NumPy); MEG flux (NumPy); PV thermal ODE (SciPy solve_ivp); "
        "Butler–Volmer SMFC; global circuit; TSC Kirchhoff; column Monte Carlo with boxplots.",
        "The final cell exports chorus_results.json consumed by this paper and pdf-genesis. "
        "notebooks/SGH1_PRO_simulation.ipynb repeats PRO sizing with AEH sweeps for hardware teams.",
        "Re-running notebooks after parameter changes is mandatory for publication integrity—"
        "JSON exports are the single source of truth for tables in Section 6 and Appendix A.",
    ]


def safety_paragraphs(ctx: dict) -> list[str]:
    b = ctx["base"]
    return [
        f"Draw-side pressure rating must exceed 1.25× test pressure per SGH1_TEST_PROTOCOL. "
        f"Rupture disk set at 1.2× ΔP* ≈ {1.2 * b['delta_P_star_bar']:.0f} bar protects housing and manifolds.",
        "Brine chemistry requires eye wash, chemical-resistant gloves, and drip tray containment (FR-4). "
        "No hydrotest with glass viewport components. Electrical GFCI on all pump and DAQ circuits.",
        "Ultrasonic drivers are isolated from low-voltage DAQ to prevent ground loops. "
        "Acoustic panel mounting avoids resonant contact with draw high-pressure piping.",
    ]


def parasitic_balance_paragraphs(ctx: dict) -> list[str]:
    b = ctx["base"]
    return [
        "Complete skid net power P_net = P_PRO + P_AEH + P_US,net − P_pump − P_aux is not yet closed in code. "
        f"Feed pump power scales roughly with Q × ΔP_pump / η_pump. At Q = {b['Q_L_min']:.2f} L/min and "
        "ΔP_pump ~ 1–3 bar for pretreatment, parasitics may be comparable to modeled PRO output until "
        "PX recovery is included—PRO-07 px_module is the designed mitigation path.",
        "Pressure exchangers can return a fraction of draw-side pressurization energy to the feed path, "
        "dramatically improving net efficiency in commercial PRO. SGH-1 includes PX housing in CAD to "
        "train integrators even before turbine/generator substitution is finalized.",
        "DAQ budget under 2 W is negligible versus PRO target. Ultrasonic driver at 1.5 W/m² × 0.72 m² ≈ 1.08 W "
        "is material and appears in E5 as P_US.",
    ]


def future_work_paragraphs(ctx: dict) -> list[str]:
    return [
        "Integrate pump parasitics and PX efficiency into simulation/parasitics.py for net skid energy balance.",
        "Couple salt permeability B to draw dilution over time (transient PRO).",
        "Field T2 at co-located desal + WWTP; publish bench CSV alongside model.",
        "Validate TSC conductances with soil–water–atmosphere potential monitoring.",
        "v2 RED cartridge swap experiments on shared bolt pattern.",
        "Publish peer-reviewed version with verified DOIs for calibration anchors.",
    ]


def abstract_paragraphs(ctx: dict) -> list[str]:
    b, e, mc, p = ctx["base"], ctx["exp"]["estuary_RED"], ctx["mc"], ctx["pi"]
    return [
        f"Anthropogenic desalination reject ({b['c_draw']:.0f} mol/m³) against treated effluent ({b['c_feed']:.0f} mol/m³) "
        f"creates Δπ = {b['delta_pi_MPa']:.2f} MPa—{b['delta_pi_MPa']/e['delta_pi_MPa']:.1f}× estuary RED reference. "
        "We present CHORUS multi-layer column accounting and CHORUS-Skid SGH-1 PRO bench hardware with AEH acoustic coupling.",
        f"Kim–Baker ΔP* = {b['delta_P_star_bar']:.0f} bar. Monte Carlo column (N={mc['N']}): median {mc['column_MW_median']:.1f} MW/km². "
        f"PRO model: {b['P_default_Lp_W']:.2f} W vs {ctx['sz']['P_target_W']:.0f} W target; L_p* = {p['L_p_required_for_target']:.2e}. "
        "Seven figures, full layer derivations (A–F), 23-part CAD, T0–T2 protocols. Tier-1 vs tier-2 claims explicit.",
    ]
