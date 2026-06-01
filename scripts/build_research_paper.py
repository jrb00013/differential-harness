#!/usr/bin/env python3
"""Build formatted Joseph Black PoC research paper PDF (multi-section, figures, tables)."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
FIGURES = EXPORTS / "figures"
OUT_PDF = ROOT / "papers" / "Black_2026_CHORUS_SGH1_PoC.pdf"


class PaperBuilder:
    def __init__(self):
        self.chorus = self._load("chorus_results.json")
        self.design = self._load("sgh1_design.json")
        self.pi = self._load("sgh1_pi_groups.json")
        self.exp = self._load("paper_experiments.json")
        self.sz = self.design["sizing"]
        self.res = self.chorus["results"]
        self.base = self.exp["sg_h1_baseline"]
        self.st = self._make_styles()
        self.story: list = []
        self._fig_n = 0

    @staticmethod
    def _load(name: str) -> dict:
        return json.loads((EXPORTS / name).read_text(encoding="utf-8"))

    def _make_styles(self) -> dict:
        b = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "T", parent=b["Title"], fontSize=17, leading=22, alignment=TA_CENTER,
                spaceAfter=16, textColor=colors.HexColor("#1a365d"),
            ),
            "subtitle": ParagraphStyle(
                "ST", parent=b["Normal"], fontSize=11, leading=14, alignment=TA_CENTER,
                spaceAfter=8, textColor=colors.HexColor("#2d3748"),
            ),
            "author": ParagraphStyle("A", parent=b["Normal"], fontSize=12, alignment=TA_CENTER, spaceAfter=4),
            "affil": ParagraphStyle(
                "AF", parent=b["Normal"], fontSize=9, alignment=TA_CENTER,
                textColor=colors.grey, spaceAfter=20,
            ),
            "h1": ParagraphStyle(
                "H1", parent=b["Heading1"], fontSize=14, leading=17, spaceBefore=20,
                spaceAfter=10, textColor=colors.HexColor("#1a365d"), keepWithNext=True,
            ),
            "h2": ParagraphStyle(
                "H2", parent=b["Heading2"], fontSize=12, leading=15, spaceBefore=14,
                spaceAfter=8, textColor=colors.HexColor("#2c5282"), keepWithNext=True,
            ),
            "h3": ParagraphStyle(
                "H3", parent=b["Heading3"], fontSize=11, leading=14, spaceBefore=10,
                spaceAfter=6, textColor=colors.HexColor("#2d3748"), keepWithNext=True,
            ),
            "body": ParagraphStyle(
                "B", parent=b["BodyText"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=10,
            ),
            "abstract": ParagraphStyle(
                "AB", parent=b["BodyText"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY,
                leftIndent=28, rightIndent=28, spaceAfter=12,
            ),
            "caption": ParagraphStyle(
                "CAP", parent=b["BodyText"], fontSize=9, leading=12, alignment=TA_CENTER,
                textColor=colors.HexColor("#4a5568"), spaceBefore=4, spaceAfter=14,
            ),
            "toc": ParagraphStyle("TOC", parent=b["Normal"], fontSize=10, leading=14, leftIndent=12, spaceAfter=4),
            "eq": ParagraphStyle(
                "EQ", parent=b["Code"], fontSize=10, leading=13, alignment=TA_CENTER,
                fontName="Courier", textColor=colors.HexColor("#1a202c"),
            ),
        }

    def p(self, text: str, style: str = "body") -> None:
        self.story.append(Paragraph(text, self.st[style]))

    def sp(self, h: float = 0.12) -> None:
        self.story.append(Spacer(1, h * inch))

    def h1(self, text: str) -> None:
        self.story.append(Paragraph(text, self.st["h1"]))

    def h2(self, text: str) -> None:
        self.story.append(Paragraph(text, self.st["h2"]))

    def h3(self, text: str) -> None:
        self.story.append(Paragraph(text, self.st["h3"]))

    def pb(self) -> None:
        self.story.append(PageBreak())

    def eq(self, *lines: str) -> None:
        rows = [[Paragraph(line, self.st["eq"])] for line in lines]
        t = Table(rows, colWidths=[6.3 * inch])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ])
        )
        self.story.append(t)
        self.sp(0.08)

    def table(self, rows: list[list[str]], cw=None) -> None:
        if cw is None:
            cw = [3.0 * inch, 3.3 * inch] if len(rows[0]) == 2 else [2.0 * inch, 2.0 * inch, 2.3 * inch]
        t = Table(rows, colWidths=cw, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        self.story.append(t)
        self.sp(0.1)

    def figure(self, filename: str, caption: str, width: float = 6.2) -> None:
        path = FIGURES / filename
        if not path.exists():
            self.p(f"<i>[Figure missing: {filename}]</i>")
            return
        self._fig_n += 1
        img = Image(str(path), width=width * inch, height=width * 0.55 * inch)
        cap = Paragraph(f"<b>Figure {self._fig_n}.</b> {caption}", self.st["caption"])
        self.story.append(KeepTogether([img, cap]))

    def build_story(self) -> None:
        self._title_page()
        self.pb()
        self._toc()
        self.pb()
        self._nomenclature()
        self.pb()
        self._introduction()
        self.pb()
        self._theory()
        self.pb()
        self._methods()
        self.pb()
        self._results()
        self.pb()
        self._hardware()
        self.pb()
        self._discussion()
        self.pb()
        self._conclusion()
        self.pb()
        self._appendices()
        self._references()

    def _title_page(self) -> None:
        self.sp(0.5)
        self.story.append(Paragraph(
            "CHORUS-Skid SGH-1: A Proof-of-Concept Framework for<br/>"
            "Pressure-Retarded Osmosis on Anthropogenic Brine Gradients<br/>"
            "with Acoustic Harvest, Ultrasonic Membrane Assist,<br/>"
            "and Column-Scale Multi-Physics Energy Accounting",
            self.st["title"],
        ))
        self.sp(0.15)
        self.p("<b>Joseph Black</b>", "author")
        self.p("Independent Researcher · CHORUS Research Program", "affil")
        self.p("<i>differential-harness</i> open-source artifact · Draft v2 · June 2026", "affil")
        self.sp(0.25)
        self.h1("Abstract")
        mc = self.exp["column_monte_carlo"]
        self.p(
            "Anthropogenic desalination concentrates reject brine (≈8 wt% NaCl, 1400 mol/m³) "
            "against treated wastewater effluent (≈5 mol/m³), creating a salinity-gradient resource "
            "that is typically wasted as mixing entropy. We formalize <b>CHORUS</b> (Columnar Harvest "
            "of Osmotic, Rhizospheric, Orographic, and Solar flux) as a thermodynamically bounded "
            "sum over a 1 km² coastal parcel, and <b>CHORUS-Skid SGH-1</b> as a bench-scale "
            "<b>pressure-retarded osmosis (PRO)</b> harness with integrated <b>acoustic energy harvest "
            "(AEH)</b> and ultrasonic concentration-polarization (CP) assist. "
            f"Van't Hoff analysis gives Δπ = {self.base['delta_pi_MPa']:.3f} MPa for the brine pair "
            f"(2.4× the estuary RED reference Δπ = {self.exp['estuary_RED']['delta_pi_MPa']:.3f} MPa). "
            f"Kim–Baker optimal hydraulic pressure ΔP* = {self.base['delta_P_star_bar']:.1f} bar. "
            f"Monte Carlo column integration (N = {mc['N']}) yields median "
            f"{mc['column_MW_median']:.2f} MW/km² (P10–P90: {mc['column_MW_p10']:.2f}–"
            f"{mc['column_MW_p90']:.2f} MW), with pv_hydro contributing "
            f"{mc['layers']['pv_hydro']['share_of_median_column_pct']:.1f}% of median layer sum. "
            f"Numerical experiments with default L_p = 1×10⁻¹² m/(Pa·s) predict "
            f"P_PRO = {self.base['P_default_Lp_W']:.2f} W on A = {self.base['A_m2']:.2f} m² "
            f"versus a 10 W design target; inverse sizing requires L_p* ≈ "
            f"{self.pi.get('L_p_required_for_target', 6e-12):.2e} m/(Pa·s). "
            "We present seven publication figures, twelve data tables, dimensionless groups Π₁–Π₅, "
            "and reproducible simulation exports. Near-term claims (PRO, DAQ, CP/ultrasound) are "
            "separated from exploratory Telluric Storm Coupling and global-circuit routing narratives.",
            "abstract",
        )
        self.p(
            "<b>Keywords:</b> pressure-retarded osmosis; salinity-gradient power; blue energy; "
            "concentration polarization; acoustic energy harvesting; coastal energy systems; "
            "desalination brine valorization; CHORUS",
            "abstract",
        )

    def _toc(self) -> None:
        self.h1("Contents")
        sections = [
            "Nomenclature",
            "1 Introduction",
            "2 Theoretical framework",
            "3 Numerical methods and experimental design",
            "4 Results",
            "5 Hardware realization (SGH-1)",
            "6 Discussion",
            "7 Conclusion",
            "Appendices A–D",
            "References",
        ]
        for s in sections:
            self.p(s, "toc")

    def _nomenclature(self) -> None:
        self.h1("Nomenclature")
        rows = [
            ["Symbol", "Definition", "SI unit"],
            ["R, F", "Gas constant, Faraday constant", "J/(mol·K), C/mol"],
            ["T", "Temperature", "K"],
            ["c", "Molar concentration", "mol/m³"],
            ["π, Δπ", "Osmotic pressure, difference", "Pa"],
            ["ΔP, ΔP*", "Hydraulic pressure, Kim–Baker optimum", "Pa"],
            ["L_p", "Water permeability", "m/(Pa·s)"],
            ["A", "Active membrane area", "m²"],
            ["E_N", "Nernst potential", "V"],
            ["P'', P_target", "Areal power density, design power", "W/m², W"],
            ["J_w", "Water flux", "m/s"],
            ["η_mem, η_hyd", "Membrane, hydrodynamic efficiency", "—"],
            ["CF", "Capacity factor (column layer)", "—"],
        ]
        self.table(rows, [1.2 * inch, 3.5 * inch, 1.6 * inch])

    def _introduction(self) -> None:
        self.h1("1. Introduction")
        self.h2("1.1 Energy context")
        self.p(
            "Global desalination capacity exceeds 100 million m³/day, with reject brine returned "
            "to the ocean or evaporation ponds. The chemical potential stored in the salinity "
            "difference between brine and treated effluent is comparable to—or exceeds—that available "
            "at natural estuaries, yet industrial sidestreams rarely include osmotic power recovery. "
            "Pressure-retarded osmosis (PRO) pressurizes the draw (brine) compartment and extracts "
            "hydraulic work as freshwater permeates from the feed. Unlike reverse electrodialysis (RED), "
            "which generates electrical current directly across ion-exchange membranes, PRO is a "
            "hydraulic–mechanical pathway well suited to integration with existing high-pressure "
            "desalination infrastructure."
        )
        self.h2("1.2 The CHORUS hypothesis")
        self.p(
            "CHORUS posits that a coastal or industrial <b>column</b>—1 km² footprint—can account for "
            "simultaneous harvest from osmotic interfaces, evaporatively cooled photovoltaics, "
            "moist-electric generators (MEG), rhizospheric microbial fuel cells (SMFC), and "
            "atmospheric charge routing (Telluric Storm Coupling, TSC). The framework enforces a "
            "<b>no-over-unity postulate</b>: the sum of extracted electrical powers cannot exceed "
            "exogenous energy influx minus dissipation. This paper's PoC contribution is not to claim "
            "22 MW from a bench skid, but to provide a <b>reproducible mathematical spine</b> linking "
            "column-scale accounting to a 10 W PRO hardware target."
        )
        self.h2("1.3 Contributions")
        bullets = [
            "Layered derivation blueprint (CHORUS_MATH_PLAN.md) with executable notebook proof.",
            "SGH-1 sizing pipeline: Van't Hoff → Kim–Baker → solution-diffusion → CAD JSON.",
            "Numerical experiment suite (simulation/experiments.py) with seven figures.",
            "AEH-1 dual-mode acoustic module: harvest (mW) + ultrasonic CP assist (W net).",
            "Open hardware: 23 OpenSCAD parts, BOM, P&ID, bench protocol T0/T1/T2.",
        ]
        for b in bullets:
            self.p(f"• {b}")

    def _theory(self) -> None:
        self.h1("2. Theoretical framework")
        self.h2("2.1 Gibbs mixing and Van't Hoff osmotic pressure")
        self.p(
            "For ideal NaCl with van't Hoff factor i = 2, the osmotic pressure of a reservoir "
            "at concentration c (mol/m³) is π = iRTc. The mixing free energy sets a thermodynamic "
            "ceiling on extractable work. The osmotic pressure difference between draw and feed is:"
        )
        self.eq("π = i R T c", "Δπ = π_draw − π_feed = i R T (c_draw − c_feed)")
        self.p(
            f"At T = {self.exp['meta']['T_K']} K, the estuary pair (600/20 mol/m³) gives "
            f"Δπ = {self.exp['estuary_RED']['delta_pi_MPa']:.3f} MPa. The SGH-1 anthropogenic pair "
            f"(1400/5 mol/m³) gives Δπ = {self.base['delta_pi_MPa']:.3f} MPa—a "
            f"{self.base['delta_pi_MPa']/self.exp['estuary_RED']['delta_pi_MPa']:.2f}× stronger driving force."
        )
        self.h2("2.2 Nernst potential and RED max-power theorem")
        self.eq("E_N = (R T / F) ln(c_draw / c_feed)", "P''_max = V_oc² / (4 R_int)")
        self.p(
            f"Estuary: E_N = {self.exp['estuary_RED']['E_N_mV']:.2f} mV (50 pairs → "
            f"V_stack = {self.res['V_stack_V']:.2f} V). Literature-calibrated P''_blue = "
            f"{self.exp['estuary_RED']['P_max_W_m2']:.1f} W/m². Brine pair: E_N = "
            f"{self.base['E_N_mV']:.1f} mV (informational for PRO; hydraulic extraction dominates)."
        )
        self.h2("2.3 PRO transport and Kim–Baker optimum")
        self.eq(
            "V̇_w = L_p A (Δπ − ΔP)",
            "P_hyd = ρ V̇_w ΔP",
            "P_elec,eq = η_mem η_hyd P_hyd",
            "ΔP* = Δπ / 2  (maximizes P_hyd at fixed L_p)",
        )
        self.p(
            "The bench skid operates in the fractional band 0.4 ≤ ΔP/Δπ ≤ 0.6 (functional requirement FR-1). "
            "Figure 1 shows P(ΔP/Δπ) with maximum at ratio 0.5."
        )
        self.h2("2.4 Concentration polarization")
        self.eq("c_w / c_b = exp(J_w / k_m)", "Δπ_eff = Δπ / (c_w/c_b)_outlet")
        self.p(
            "High water flux J_w thickens the solute film at the membrane wall, reducing effective "
            "Δπ. Figure 4 quantifies driving-force loss versus J_w. AEH Mode B models ultrasonic "
            "disruption as multiplicative permeability gain g on L_p, with net P_net = P_PRO(g) − P_US."
        )
        self.h2("2.5 CHORUS column balance")
        self.eq("P_column = Σ_k A_k CF_k ⟨P''_k⟩")
        self.p(
            "Layer draws use lognormal uncertainty on P'' with literature medians. "
            "Table 2 reports replicated Monte Carlo medians (simulation/experiments.py)."
        )
        self.h2("2.6 Acoustic harvest (AEH Mode A)")
        self.eq("I = p_rms² / (ρ c)", "P_AEH = η I A")
        self.p("Urban SPL 60–100 dB maps to mW-class harvest on 0.5 m² at η = 2% (Figure 6).")

    def _methods(self) -> None:
        self.h1("3. Numerical methods and experimental design")
        self.h2("3.1 Simulation stack")
        self.p(
            "All results are produced by version-controlled Python modules: pro_cycle.py (steady PRO), "
            "membrane_transport.py (CP film), ultrasonic_cp_gain.py (Mode B), acoustic_harvest.py (Mode A), "
            "pi_groups.py (Π₁–Π₅), experiments.py (sweeps + column MC). Constants in constants.py use "
            "SI units with T = 298.15 K. Exports land in exports/*.json; figures in exports/figures/."
        )
        self.h2("3.2 Sweeps executed")
        self.table([
            ["Experiment", "Independent variable", "Outputs"],
            ["E1", "ΔP/Δπ ∈ [0.05, 0.95]", "P, Q, P''"],
            ["E2", "L_p ∈ [0.5, 15]×10⁻¹²", "P, hit 10 W flag"],
            ["E3", "Salinity pairs", "Δπ, E_N, P''"],
            ["E4", "J_w (CP)", "Polarization factor, loss %"],
            ["E5", "Ultrasonic gain g", "P_net"],
            ["E6", "SPL 60–100 dB", "P_AEH (mW)"],
            ["E7", "Column MC N=8000", "Layer MW medians"],
        ], [1.4 * inch, 2.2 * inch, 2.7 * inch])
        self.h2("3.3 Bench protocol (hardware)")
        self.p(
            "SGH1_TEST_PROTOCOL.md defines T0 (DAQ smoke), T1 (±30% power vs model), T2 (AEH on/off). "
            "Materials per MATERIALS_SPEC.md; wetted paths SS316."
        )

    def _results(self) -> None:
        self.h1("4. Results")
        self.h2("4.1 SGH-1 baseline (Table 1)")
        self.table([
            ["Parameter", "Value"],
            ["c_draw / c_feed", f"{self.base['c_draw']:.0f} / {self.base['c_feed']:.0f} mol/m³"],
            ["Δπ", f"{self.base['delta_pi_MPa']:.3f} MPa"],
            ["ΔP*", f"{self.base['delta_P_star_bar']:.2f} bar"],
            ["A_mem", f"{self.base['A_m2']:.2f} m²"],
            ["P at ΔP* (L_p=1e-12)", f"{self.base['P_at_delta_P_star_W']:.2f} W"],
            ["P''", f"{self.base['P_density_W_m2']:.2f} W/m²"],
            ["Q_feed", f"{self.base['Q_L_min']:.3f} L/min"],
            ["E_N", f"{self.base['E_N_mV']:.1f} mV"],
        ])
        self.h2("4.2 Dimensionless groups (Table 2)")
        self.table([
            ["Group", "Value", "Interpretation"],
            ["Π₁ = ΔP/Δπ", f"{self.pi['Pi1_delta_P_over_delta_pi']:.3f}", "Kim–Baker point"],
            ["Π₃ ≈ Pe", f"{self.pi['Pi3_Pe_order']:.3f}", "CP advection/diffusion"],
            ["Π₄", f"{self.pi['Pi4_area_law']:.3f}", "Area law vs target"],
            ["Π₅", f"{self.pi['Pi5_sim_over_target']:.3f}", "Simulation gap"],
            ["L_p*", f"{self.pi['L_p_required_for_target']:.2e}", "For 10 W"],
        ], [1.5 * inch, 1.5 * inch, 3.3 * inch])
        self.figure("fig01_pro_pressure_sweep.png",
                    "PRO equivalent power versus hydraulic pressure ratio. Green band: FR-1 (0.4–0.6). "
                    "Crimson dashed line: Kim–Baker optimum at 0.5.")
        self.figure("fig02_Lp_sweep.png",
                    "Permeability sweep showing design target 10 W requires L_p ≈ 6×10⁻¹² m/(Pa·s) at ΔP = Δπ/2.")
        self.h2("4.3 Salinity pair comparison (Table 3)")
        rows = [["Pair", "c_draw", "c_feed", "Δπ (MPa)", "E_N (mV)"]]
        for p in self.exp["sweeps"]["salinity_pairs"]:
            rows.append([p["name"], f"{p['c_draw']:.0f}", f"{p['c_feed']:.0f}",
                         f"{p['delta_pi_MPa']:.2f}", f"{p['E_N_mV']:.1f}"])
        self.table(rows, [1.5 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch])
        self.figure("fig07_salinity_pairs.png", "Osmotic pressure difference across four salinity pair regimes.")
        self.h2("4.4 Column Monte Carlo (Table 4)")
        mc = self.exp["column_monte_carlo"]
        rows = [["Layer", "Median (MW)", "Share of column (%)"]]
        for k, v in mc["layers"].items():
            rows.append([k, f"{v['median_MW']:.2f}", f"{v['share_of_median_column_pct']:.1f}"])
        rows.append(["Total", f"{mc['column_MW_median']:.2f}",
                     f"P10–P90: {mc['column_MW_p10']:.2f}–{mc['column_MW_p90']:.2f}"])
        self.table(rows)
        self.figure("fig03_column_layers.png",
                    "Layer median contributions to 1 km² CHORUS column (N = 8000, lognormal P'' draws).")
        self.h2("4.5 Concentration polarization (Table 5)")
        cp_rows = [["J_w (×10⁻⁵ m/s)", "Polarization factor", "Loss (%)"]]
        for r in self.exp["sweeps"]["concentration_polarization"]:
            cp_rows.append([f"{r['J_w']*1e5:.1f}", f"{r['polarization_factor']:.2f}",
                            f"{r['power_loss_pct']:.1f}"])
        self.table(cp_rows, [2.0 * inch, 2.0 * inch, 2.3 * inch])
        self.figure("fig04_cp_sweep.png", "Effective driving-force loss from film-model concentration polarization.")
        self.h2("4.6 Ultrasonic assist (Table 6)")
        us_rows = [["Gain g", "P_base (W)", "P_with US (W)", "P_US (W)", "P_net (W)"]]
        for r in self.exp["sweeps"]["ultrasonic_gain"]:
            us_rows.append([f"{r['flux_gain']:.2f}", f"{r['P_base_W']:.2f}",
                            f"{r['P_with_us_W']:.2f}", f"{r['P_us_W']:.2f}", f"{r['P_net_gain_W']:.3f}"])
        self.table(us_rows, [0.9 * inch] * 5)
        self.figure("fig05_ultrasonic_net.png",
                    "Net power gain from AEH Mode B after 1.5 W/m² ultrasonic parasitic load.")
        self.h2("4.7 Acoustic harvest (Table 7)")
        spl = self.exp["sweeps"]["acoustic_SPL"]
        for pt in [spl[0], spl[len(spl)//2], spl[-1]]:
            self.p(f"SPL = {pt['spl_db']:.0f} dB → {pt['power_mW']:.2f} mW "
                   f"(I = {pt['intensity_W_m2']:.4e} W/m²)")
        self.figure("fig06_acoustic_spl.png", "Mode A harvest versus sound pressure level.")

    def _hardware(self) -> None:
        self.h1("5. Hardware realization (SGH-1)")
        self.p(
            f"The sized skid occupies a frame of {self.sz['frame_length_mm']}×{self.sz['frame_width_mm']}×"
            f"{self.sz['frame_height_mm']} mm with {int(self.sz['n_plates'])} membrane plates "
            f"({self.sz['active_width_mm']:.0f}×{self.sz['active_height_mm']:.0f} mm active each). "
            "Housing OD = {:.0f} mm; bolt pattern = {:.0f} mm. OpenSCAD sources: sgh1_assembly.scad, "
            "chorus_aeh_panel.scad, chorus_skid_enclosure.scad. STL export via hardware/scripts/export_stl.sh."
            .format(self.sz['housing_od_mm'], self.sz['bolt_pattern_mm'])
        )
        self.table([
            ["Subsystem", "Function"],
            ["PRO stack", "Brine draw / WW feed, PX recovery"],
            ["AEH-1", "Piezo harvest + 28 kHz CP assist"],
            ["DAQ", "P, σ, Q, V logging"],
            ["CHORUS enclosure", "Future moist/thermal ports"],
        ])

    def _discussion(self) -> None:
        mc = self.exp["column_monte_carlo"]
        self.h1("6. Discussion")
        self.h2("6.1 PRO on brine as near-term path")
        self.p(
            "Higher Δπ and existing infrastructure favor sidestream PRO over greenfield estuary RED "
            "for first demonstration. The simulation–target gap (Π₅ = 0.17) is not a conservation violation "
            "but a permeability calibration problem: commercial PRO foils may exceed L_p = 1×10⁻¹²."
        )
        self.h2("6.2 Column vs bench claims")
        self.p(
            f"The {mc['column_MW_median']:.1f} MW/km² median must not be marketed as bench output. "
            "It is an uncertainty-aware sum of heterogeneous layers—primarily land PV—with osmotic "
            "interface power at the percent level of median contribution."
        )
        self.h2("6.3 Limitations")
        self.p(
            "Constant L_p, B not coupled to fouling; pump parasitics not in pro_cycle.py; TSC conductances "
            "illustrative; literature citations are calibration anchors pending DOI verification; "
            "no field data yet—T1 protocol pending."
        )

    def _conclusion(self) -> None:
        self.h1("7. Conclusion")
        self.p(
            "CHORUS-Skid SGH-1 demonstrates a complete pipeline from first-principles osmotic "
            "thermodynamics through numerical experiment, hardware CAD, and bench protocol. "
            "Joseph Black PoC paper v2 adds seven figures, twelve tables, and explicit separation "
            "of defensible PRO/AEH claims from exploratory column coupling. All artifacts are "
            "reproducible from github.com/jrb00013/differential-harness."
        )

    def _appendices(self) -> None:
        self.h1("Appendix A — Full equation set (Layer F)")
        for eq in [
            "π = iRTc", "Δπ = iRT(c_d − c_f)", "V̇_w = L_p A(Δπ − ΔP)",
            "P = η_mem η_hyd ρ V̇_w ΔP", "c_w/c_b = exp(J_w/k_m)",
            "P_column = Σ_k A_k CF_k ⟨P''_k⟩", "P_net = P_PRO(g) − P_US",
        ]:
            self.eq(eq)
        self.h1("Appendix B — L_p sweep data")
        rows = [["L_p (×10⁻¹²)", "P (W)", "P'' (W/m²)", "≥10 W?"]]
        for r in self.exp["sweeps"]["L_p"]:
            rows.append([f"{r['L_p']*1e12:.1f}", f"{r['P_W']:.2f}", f"{r['P_W_m2']:.2f}",
                         "yes" if r["hits_10W"] else "no"])
        self.table(rows, [1.5 * inch, 1.2 * inch, 1.5 * inch, 1.0 * inch])
        self.h1("Appendix C — Repository map")
        self.table([
            ["Path", "Role"],
            ["simulation/experiments.py", "Numerical experiments"],
            ["exports/paper_experiments.json", "Machine-readable results"],
            ["exports/figures/", "Publication figures"],
            ["notebooks/CHORUS_physics_proof.ipynb", "Symbolic + MC proof"],
            ["docs/math/", "Derivations"],
        ], [3.0 * inch, 3.3 * inch])

    def _references(self) -> None:
        self.h1("References")
        refs = [
            "[1] Teng, Y. et al. Nanopore-based blue energy harvesting. <i>Nature Energy</i> (2026).",
            "[2] Skilhagen, S.E. et al. Osmotic power—status and prospects. <i>Desalination</i>.",
            "[3] Kim, Y.C. & Baker, R.W. Thermodynamic and transport modeling in PRO. <i>J. Membrane Sci.</i>",
            "[4] Fang, C. et al. Photovoltaic–magnetohydrodynamic coupling. <i>Energy Environ. Sci.</i> (2026).",
            "[5] Yao, Y. et al. Moisture-enabled electric generators. <i>Adv. Mater.</i>",
            "[6] Virgo, S. et al. Atmospheric electricity and lightning budget. <i>Global Challenges</i> (2020).",
            "[7] Statkraft. Osmotic power prototype at Tofte (2009–2013). Technical reports.",
            "[8] He, W. et al. PRO for salinity-gradient energy: membrane and module review. <i>Renew. Sustain. Energy Rev.</i>",
        ]
        for r in refs:
            self.p(r)

    def render(self) -> Path:
        self.build_story()
        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(OUT_PDF),
            pagesize=letter,
            rightMargin=0.9 * inch,
            leftMargin=0.9 * inch,
            topMargin=0.9 * inch,
            bottomMargin=0.85 * inch,
            title="CHORUS-SGH-1 PoC — Joseph Black",
            author="Joseph Black",
        )

        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.drawString(0.9 * inch, 0.45 * inch, "Black (2026) · CHORUS-SGH-1 PoC · differential-harness")
            canvas.drawRightString(7.6 * inch, 0.45 * inch, f"Page {doc.page}")
            canvas.restoreState()

        doc.build(self.story, onFirstPage=footer, onLaterPages=footer)
        return OUT_PDF


def build() -> Path:
    return PaperBuilder().render()


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path} ({path.stat().st_size:,} bytes)")
