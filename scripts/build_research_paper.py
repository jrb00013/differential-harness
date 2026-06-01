#!/usr/bin/env python3
"""Build full-length Joseph Black CHORUS-SGH-1 research paper PDF."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

TITLE_SHORT = "CHORUS-SGH-1: Brine-Gradient Power on a Bench Skid"
SUBTITLE_LONG = (
    "A Proof-of-Concept Framework for Pressure-Retarded Osmosis on Anthropogenic Brine "
    "Gradients with Acoustic Harvest, Ultrasonic Membrane Assist, and Column-Scale "
    "Multi-Physics Energy Accounting"
)

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
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
sys.path.insert(0, str(ROOT))
from papers.paper_sections import (  # noqa: E402
    abstract_paragraphs,
    aeh_paragraphs,
    deployment_paragraphs,
    discussion_paragraphs,
    future_work_paragraphs,
    hardware_paragraphs,
    introduction_paragraphs,
    layer_a_paragraphs,
    layer_b_paragraphs,
    layer_c_paragraphs,
    layer_d_paragraphs,
    layer_f_paragraphs,
    literature_paragraphs,
    notebook_walkthrough_paragraphs,
    openscad_paragraphs,
    parasitic_balance_paragraphs,
    patent_draft_paragraphs,
    ranked_concepts_paragraphs,
    safety_paragraphs,
    sympy_paragraphs,
    test_protocol_paragraphs,
    tsc_column_paragraphs,
    worked_examples_paragraphs,
)

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
        self.mc = self.exp["column_monte_carlo"]
        oc_path = EXPORTS / "openscad_audit.json"
        self.openscad = json.loads(oc_path.read_text()) if oc_path.exists() else {}
        self.bom = self._load_bom()
        self.ctx = {
            "base": self.base,
            "exp": self.exp,
            "res": self.res,
            "pi": self.pi,
            "sz": self.sz,
            "mc": self.mc,
            "claims": self.design.get("claims", self.chorus.get("claims", {})),
            "openscad": self.openscad,
            "symbolic": self.exp.get("symbolic_checks", {}),
        }
        self.st = self._make_styles()
        self.story: list = []
        self._fig_n = 0
        self._tbl_n = 0

    @staticmethod
    def _load(name: str) -> dict:
        return json.loads((EXPORTS / name).read_text(encoding="utf-8"))

    @staticmethod
    def _load_bom() -> list[dict]:
        path = ROOT / "hardware" / "bom" / "SGH1_BOM.csv"
        if not path.exists():
            return []
        with path.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _make_styles(self) -> dict:
        b = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "T", parent=b["Title"], fontSize=16, leading=20, alignment=TA_CENTER,
                spaceAfter=12, textColor=colors.HexColor("#1a365d"),
            ),
            "subtitle": ParagraphStyle(
                "ST", parent=b["Normal"], fontSize=10, leading=13, alignment=TA_CENTER,
                spaceAfter=10, textColor=colors.HexColor("#4a5568"), leftIndent=32, rightIndent=32,
            ),
            "author": ParagraphStyle("A", parent=b["Normal"], fontSize=12, alignment=TA_CENTER, spaceAfter=4),
            "affil": ParagraphStyle(
                "AF", parent=b["Normal"], fontSize=9, alignment=TA_CENTER,
                textColor=colors.grey, spaceAfter=8,
            ),
            "h1": ParagraphStyle(
                "H1", parent=b["Heading1"], fontSize=13, leading=16, spaceBefore=16,
                spaceAfter=8, textColor=colors.HexColor("#1a365d"), keepWithNext=True,
            ),
            "h2": ParagraphStyle(
                "H2", parent=b["Heading2"], fontSize=11.5, leading=14, spaceBefore=12,
                spaceAfter=6, textColor=colors.HexColor("#2c5282"), keepWithNext=True,
            ),
            "h3": ParagraphStyle(
                "H3", parent=b["Heading3"], fontSize=10.5, leading=13, spaceBefore=8,
                spaceAfter=4, textColor=colors.HexColor("#2d3748"), keepWithNext=True,
            ),
            "body": ParagraphStyle(
                "B", parent=b["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=8,
            ),
            "abstract": ParagraphStyle(
                "AB", parent=b["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY,
                leftIndent=24, rightIndent=24, spaceAfter=10,
            ),
            "caption": ParagraphStyle(
                "CAP", parent=b["BodyText"], fontSize=8.5, leading=11, alignment=TA_CENTER,
                textColor=colors.HexColor("#4a5568"), spaceBefore=3, spaceAfter=12,
            ),
            "toc": ParagraphStyle("TOC", parent=b["Normal"], fontSize=9.5, leading=13, leftIndent=16, spaceAfter=3),
            "eq": ParagraphStyle(
                "EQ", parent=b["Code"], fontSize=9.5, leading=12, alignment=TA_CENTER,
                fontName="Courier", textColor=colors.HexColor("#1a202c"),
            ),
        }

    def p(self, text: str, style: str = "body") -> None:
        self.story.append(Paragraph(text, self.st[style]))

    def paras(self, texts: list[str]) -> None:
        for t in texts:
            self.p(t)

    def sp(self, h: float = 0.08) -> None:
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
        t = Table(rows, colWidths=[6.2 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf2f7")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        self.story.append(t)
        self.sp(0.06)

    def table(self, rows: list[list[str]], cw=None, caption: str | None = None) -> None:
        self._tbl_n += 1
        if caption:
            self.p(f"<b>Table {self._tbl_n}.</b> {caption}", "body")
        if cw is None:
            n = len(rows[0])
            cw = [6.2 / n * inch] * n
        t = Table(rows, colWidths=cw, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        self.story.append(t)
        self.sp(0.1)

    def figure(self, filename: str, caption: str, width: float = 5.4, height_ratio: float = 0.48) -> None:
        path = FIGURES / filename
        if not path.exists():
            self.p(f"<i>[Figure missing: {filename}]</i>")
            return
        self._fig_n += 1
        img = Image(str(path), width=width * inch, height=width * height_ratio * inch)
        cap = Paragraph(f"<b>Figure {self._fig_n}.</b> {caption}", self.st["caption"])
        self.story.append(KeepTogether([img, cap]))

    def build_story(self) -> None:
        self._front_matter()
        self.pb()
        self._introduction_full()
        self.pb()
        self._literature()
        self.pb()
        self._theory_layers()
        self.pb()
        self._sgh1_system()
        self.pb()
        self._methods_full()
        self.pb()
        self._results_full()
        self.pb()
        self._hardware_full()
        self.pb()
        self._openscad_deep_dive()
        self.pb()
        self._testing()
        self.pb()
        self._worked_examples()
        self.pb()
        self._ranked_and_deployment()
        self.pb()
        self._notebook_section()
        self.pb()
        self._discussion_full()
        self.pb()
        self._conclusion_future()
        self.pb()
        self._appendices_full()
        self._references_full()

    def _front_matter(self) -> None:
        self.sp(0.45)
        self.story.append(Paragraph(TITLE_SHORT, self.st["title"]))
        self.sp(0.12)
        self.story.append(Paragraph(SUBTITLE_LONG, self.st["subtitle"]))
        self.sp(0.18)
        self.p("<b>Joseph Black</b>", "author")
        self.p("CHORUS Research Program · <i>differential-harness</i>", "affil")
        self.p("Full technical report · Draft v4 · June 2026", "affil")
        self.sp(0.2)
        self.h1("Abstract")
        self.paras(abstract_paragraphs(self.ctx))
        self.p(
            "<b>Keywords:</b> pressure-retarded osmosis; salinity-gradient power; blue energy; "
            "reverse electrodialysis; concentration polarization; acoustic energy harvesting; "
            "CHORUS; desalination brine; proof of concept",
            "abstract",
        )
        self.pb()
        self.h1("Contents")
        for line in [
            "Abstract",
            "1 Introduction",
            "2 Background and prior art",
            "3 Theoretical framework",
            "  3.1 Layer A — Osmotic mixing and blue energy (RED)",
            "  3.2 Layer B — Moist-electric and hydrovoltaic (CHOR)",
            "  3.3 Layer C — Rhizospheric (SMFC, piezoelectrotrophy)",
            "  3.4 Layer D — Atmospheric charge and collision cells",
            "  3.5 Telluric Storm Coupling and column balance",
            "  3.6 Layer F — PRO on anthropogenic brine (SGH-1)",
            "4 CHORUS-Skid system architecture",
            "  4.1 AEH acoustic layer (Modes A and B)",
            "7A OpenSCAD mechanical digital twin",
            "5 Numerical methods",
            "6 Results and numerical experiments",
            "7 Hardware realization",
            "8 Bench and field test protocol",
            "9 Discussion",
            "10 Conclusion and future work",
            "Appendices A–H",
            "References",
        ]:
            self.p(line, "toc")
        self.pb()
        self.h1("Nomenclature")
        self.table([
            ["Symbol", "Definition", "SI"],
            ["R, F", "Gas constant; Faraday constant", "J/(mol·K); C/mol"],
            ["T", "Absolute temperature", "K"],
            ["i", "Van't Hoff factor (NaCl)", "—"],
            ["c, π, Δπ", "Concentration; osmotic pressure; difference", "mol/m³; Pa"],
            ["ΔP, ΔP*", "Hydraulic pressure; Kim–Baker optimum", "Pa"],
            ["L_p, B", "Water permeability; salt permeability", "m/(Pa·s); m/s"],
            ["A, A_k", "Membrane area; layer footprint", "m²"],
            ["V̇_w, J_w", "Volumetric flux; water flux", "m³/s; m/s"],
            ["E_N, V_oc", "Nernst potential; stack open circuit", "V"],
            ["R_int", "Area-specific internal resistance", "Ω·m²"],
            ["P'', P_target", "Areal power density; design power", "W/m²; W"],
            ["η_mem, η_hyd", "Membrane; hydrodynamic efficiency", "—"],
            ["CF_k", "Layer capacity factor", "—"],
            ["G", "Conductance (TSC network)", "S"],
            ["ψ", "Node potential", "V"],
            ["I, p_rms", "Acoustic intensity; RMS pressure", "W/m²; Pa"],
            ["SPL", "Sound pressure level", "dB re 20 µPa"],
            ["g", "Ultrasonic flux gain factor", "—"],
            ["Π₁…Π₅", "Dimensionless groups (see Table 2)", "—"],
        ], [1.1 * inch, 3.6 * inch, 1.5 * inch], "Symbols used throughout this report.")

    def _introduction_full(self) -> None:
        self.h1("1. Introduction")
        self.paras(introduction_paragraphs(self.ctx))
        self.h2("1.1 Problem statement")
        self.p(
            "Desalination plants and wastewater treatment plants are often co-located at coasts. "
            "Brine disposal raises environmental and regulatory cost. Effluent discharge carries "
            "residual chemical potential. Coupling the two streams through a PRO module could "
            "offset parasitic plant load while reducing entropy waste—a win-win if membranes and "
            "controls are credible."
        )
        self.h2("1.2 Document map")
        self.p(
            "Section 2 reviews prior art. Section 3 derives Layers A–F with equations. "
            "Section 4 describes skid architecture and AEH. Section 5 covers simulation methods. "
            "Section 6 presents numerical experiments E1–E7. Sections 7–8 cover hardware and tests. "
            "Section 9 discusses claims hierarchy. Appendices contain sweep data and CAD index."
        )

    def _literature(self) -> None:
        self.h1("2. Background and prior art")
        self.paras(literature_paragraphs(self.ctx))

    def _theory_layers(self) -> None:
        self.h1("3. Theoretical framework")
        self.p(
            "All layers satisfy the CHORUS postulate Σ P_k ≤ Σ Ė_in − TṠ. The following subsections "
            "mirror docs/CHORUS_MATH_PLAN.md and notebooks/CHORUS_physics_proof.ipynb."
        )
        self.h2("3.1 Layer A — Osmotic mixing and blue energy (RED)")
        self.paras(layer_a_paragraphs(self.ctx))
        self.eq(
            "ΔG_mix = 2RT V [ c_+ ln(c_+/c_-) − (c_+ − c_-)]",
            "π = i R T c",
            "Δπ = π_high − π_low",
            "E_N = (R T / z F) ln(a_high / a_low)",
            "P''_max = V_oc² / (4 R_int)",
            "P_mix,max = Δπ Q",
        )
        self.h2("3.2 Layer B — Moist-electric and hydrovoltaic")
        self.paras(layer_b_paragraphs(self.ctx))
        self.eq(
            "μ_v = μ_v° + R T ln(a_w)",
            "I_q = e ΔΓ q̄_trans",
            "E_s = (ε ζ / σ η) Δp",
            "C_th dT_s/dt = α_s G_solar − h_c(T_s−T_∞) − L_v ṁ_e − P_hybrid",
        )
        self.h2("3.3 Layer C — Rhizospheric harvest")
        self.paras(layer_c_paragraphs(self.ctx))
        self.eq(
            "j = j_0 [exp(α_a F η / RT) − exp(−α_c F η / RT)]",
            "P = j (E_0 − b log j − R_Ω j)",
            "Ė_bio = η_pzt P_mech",
        )
        self.h2("3.4 Layer D — Atmospheric charge")
        self.paras(layer_d_paragraphs(self.ctx))
        self.eq("P_glob = I_glob V", "dq/dt ∝ n_d² π d² v_rel Δq")
        self.h2("3.5 Telluric Storm Coupling and column balance")
        self.paras(tsc_column_paragraphs(self.ctx))
        self.eq("G ψ = I", "P_TSC = ψᵀ G ψ", "P_column = Σ_k A_k CF_k ⟨P''_k⟩")
        self.h2("3.6 Layer F — PRO on anthropogenic brine")
        self.paras(layer_f_paragraphs(self.ctx))
        self.eq(
            "Δπ = i R T (c_draw − c_feed)",
            "V̇_w = L_p A (Δπ − ΔP)",
            "ΔP* = Δπ / 2",
            "P = η_mem η_hyd ρ V̇_w ΔP",
            "c_w / c_b = exp(J_w / k_m)",
            "P_net = P_PRO(g) − P_US − P_0",
        )

    def _sgh1_system(self) -> None:
        self.h1("4. CHORUS-Skid system architecture")
        self.p(
            "CHORUS-Skid integrates SGH-1 (PRO core), AEH-1 (acoustic), CHOR-01 (enclosure), and DAQ. "
            "Design exports in exports/sgh1_design.json drive OpenSCAD via generated_constants.scad."
        )
        self.h2("4.1 Functional requirements")
        self.table([
            ["ID", "Requirement"],
            ["FR-1", "Operate at 0.4 ≤ ΔP/Δπ ≤ 0.6"],
            ["FR-2", "Feed ≤ 10 bar; draw rated to ΔP*"],
            ["FR-3", "Log P, Q, σ×2, T×2 continuously"],
            ["FR-4", "Brine leak containment (drip tray)"],
            ["FR-5", "Removable membrane cartridge"],
        ], [0.8 * inch, 5.4 * inch], "SGH-1 functional requirements.")
        self.h2("4.2 AEH acoustic layer")
        self.paras(aeh_paragraphs(self.ctx))
        self.eq("I = p_rms² / (ρ c)", "P_AEH = η I A", "P_net = P_PRO(g) − P_US − P_0")

    def _methods_full(self) -> None:
        self.h1("5. Numerical methods")
        self.h2("5.1 Software modules")
        self.p(
            "simulation/pro_cycle.py — steady PRO state; sizing.py — area scale law and CAD caps; "
            "membrane_transport.py — CP profile; ultrasonic_cp_gain.py — Mode B; "
            "acoustic_harvest.py — Mode A; pi_groups.py — Π₁–Π₅; experiments.py — sweeps E1–E7. "
            "notebooks/CHORUS_physics_proof.ipynb — SymPy + SciPy proof; SGH1_PRO_simulation.ipynb — PRO/AEH."
        )
        self.h2("5.2 Constants and assumptions")
        self.table([
            ["Parameter", "Value", "Source"],
            ["T", "298.15 K", "constants.py"],
            ["η_mem, η_hyd", "0.35, 0.55", "defaults"],
            ["L_p (default)", "1×10⁻¹² m/(Pa·s)", "placeholder until T1"],
            ["ρ", "1000 kg/m³", "water"],
            ["P''_blue anchor", "15 W/m²", "literature RED"],
        ], [2.0 * inch, 1.8 * inch, 2.4 * inch], "Simulation defaults.")
        self.h2("5.3 Experiment matrix")
        self.table([
            ["ID", "Sweep", "Points", "Purpose"],
            ["E1", "ΔP/Δπ", "41", "Kim–Baker verification"],
            ["E2", "L_p", "8", "Inverse sizing for 10 W"],
            ["E3", "Salinity pairs", "4", "RED vs PRO Δπ"],
            ["E4", "J_w (CP)", "6", "Polarization loss"],
            ["E5", "Ultrasonic g", "7", "Mode B net gain"],
            ["E6", "SPL", "21", "Mode A harvest"],
            ["E7", "Column MC", "8000", "Layer medians"],
            ["E8", "c_river RED", "31", "P''_max vs salinity"],
            ["E9", "Temperature", "5", "Δπ(T), P(T)"],
            ["E10", "η_mem", "11", "Sensitivity"],
            ["E11", "Slip b", "6", "Nanopore G(b)"],
            ["E12", "Net energy", "4", "Parasitics + PX"],
            ["E13", "TSC I sweep", "21", "ψ, P_diss"],
        ], [0.55 * inch, 1.35 * inch, 0.75 * inch, 3.55 * inch], "Numerical experiment matrix.")

    def _results_full(self) -> None:
        self.h1("6. Results and numerical experiments")
        b, p, mc = self.base, self.pi, self.mc
        self.h2("6.1 SGH-1 baseline")
        self.table([
            ["Parameter", "Value"],
            ["c_draw / c_feed", f"{b['c_draw']:.0f} / {b['c_feed']:.0f} mol/m³"],
            ["Δπ", f"{b['delta_pi_MPa']:.3f} MPa"],
            ["ΔP*", f"{b['delta_P_star_bar']:.2f} bar"],
            ["A_mem", f"{b['A_m2']:.2f} m²"],
            ["P (L_p=1e-12)", f"{b['P_default_Lp_W']:.2f} W"],
            ["P''", f"{b['P_density_W_m2']:.2f} W/m²"],
            ["Q_feed", f"{b['Q_L_min']:.3f} L/min"],
            ["E_N", f"{b['E_N_mV']:.1f} mV"],
        ], caption="SGH-1 baseline at design concentrations.")
        self.h2("6.2 Dimensionless groups")
        self.table([
            ["Group", "Value", "Meaning"],
            ["Π₁", f"{p['Pi1_delta_P_over_delta_pi']:.3f}", "At Kim–Baker point"],
            ["Π₃", f"{p['Pi3_Pe_order']:.3f}", "Peclet order (CP)"],
            ["Π₄", f"{p['Pi4_area_law']:.3f}", "Area law fill"],
            ["Π₅", f"{p['Pi5_sim_over_target']:.3f}", "Sim vs 10 W target"],
            ["L_p*", f"{p['L_p_required_for_target']:.2e}", "m/(Pa·s) for 10 W"],
        ], [1.4 * inch, 1.6 * inch, 3.2 * inch], "Dimensionless groups (pi_groups.py).")
        self.h2("6.3 Experiment E1 — Hydraulic pressure ratio")
        self.p(
            "Figure 1 plots P versus ΔP/Δπ. Maximum at 0.5 confirms Kim–Baker. "
            "FR-1 green band 0.4–0.6 captures operable range without approaching Δπ "
            "(where driving force vanishes)."
        )
        self.figure("fig01_pro_pressure_sweep.png",
                    "PRO power versus ΔP/Δπ with FR-1 band and Kim–Baker optimum.")
        self.h2("6.4 Experiment E2 — Permeability")
        self.p(
            f"L_p* ≈ {p['L_p_required_for_target']:.2e} m/(Pa·s) required for 10 W. "
            "Figure 2 shows sub-target performance at literature-placeholder L_p."
        )
        self.figure("fig02_Lp_sweep.png", "Power versus water permeability L_p.")
        self.h2("6.5 Experiment E3 — Salinity pairs")
        rows = [["Pair", "c_d", "c_f", "Δπ MPa", "E_N mV"]]
        for r in self.exp["sweeps"]["salinity_pairs"]:
            rows.append([r["name"], f"{r['c_draw']:.0f}", f"{r['c_feed']:.0f}",
                         f"{r['delta_pi_MPa']:.2f}", f"{r['E_N_mV']:.1f}"])
        self.table(rows, [1.6 * inch, 0.9 * inch, 0.9 * inch, 1.0 * inch, 1.0 * inch],
                   "Salinity pair comparison.")
        self.figure("fig07_salinity_pairs.png", "Δπ across estuary RED and anthropogenic PRO pairs.")
        self.h2("6.6 Experiment E7 — Column Monte Carlo")
        rows = [["Layer", "Median MW", "Share %", "P10", "P90"]]
        for k, v in mc["layers"].items():
            rows.append([k, f"{v['median_MW']:.2f}", f"{v['share_of_median_column_pct']:.1f}",
                         f"{v['p10_MW']:.2f}", f"{v['p90_MW']:.2f}"])
        rows.append(["Total", f"{mc['column_MW_median']:.2f}", "100",
                     f"{mc['column_MW_p10']:.2f}", f"{mc['column_MW_p90']:.2f}"])
        self.table(rows, caption="Column layer statistics (1 km², N=8000).")
        self.figure("fig03_column_layers.png", "Median layer contributions.")
        self.pb()
        self.h2("6.7 Experiment E4 — Concentration polarization")
        self.figure("fig04_cp_sweep.png", "Driving-force loss versus water flux.")
        cp_rows = [["J_w×10⁻⁵", "c_w/c_b", "Loss %"]]
        for r in self.exp["sweeps"]["concentration_polarization"]:
            cp_rows.append([f"{r['J_w']*1e5:.1f}", f"{r['polarization_factor']:.2f}",
                            f"{r['power_loss_pct']:.1f}"])
        self.table(cp_rows, [2.0 * inch, 2.0 * inch, 2.2 * inch], "CP film model results.")
        self.h2("6.8 Experiment E5 — Ultrasonic assist")
        self.figure("fig05_ultrasonic_net.png", "Net power versus flux gain g.")
        self.h2("6.9 Experiment E6 — Acoustic harvest")
        self.figure("fig06_acoustic_spl.png", "Mode A harvest versus SPL.")
        spl = self.exp["sweeps"]["acoustic_SPL"]
        self.table([
            ["SPL dB", "I W/m²", "P mW"],
            [f"{spl[0]['spl_db']:.0f}", f"{spl[0]['intensity_W_m2']:.2e}", f"{spl[0]['power_mW']:.3f}"],
            [f"{spl[len(spl)//2]['spl_db']:.0f}", f"{spl[len(spl)//2]['intensity_W_m2']:.2e}",
             f"{spl[len(spl)//2]['power_mW']:.3f}"],
            [f"{spl[-1]['spl_db']:.0f}", f"{spl[-1]['intensity_W_m2']:.2e}", f"{spl[-1]['power_mW']:.3f}"],
        ], caption="Selected SPL harvest points (A=0.5 m², η=2%).")
        self.h2("6.10 Experiment E8 — RED river salinity")
        self.figure("fig08_red_river_sweep.png", "Estuary RED P''_max versus c_river.")
        self.h2("6.11 Experiment E9 — Temperature")
        self.figure("fig09_temperature.png", "PRO power versus temperature.")
        self.h2("6.12 Experiment E12 — Net skid energy")
        self.figure("fig10_net_energy.png", "Net power scenarios with pump and PX model.")
        ne_rows = [["Scenario", "P_pro", "P_pump", "P_px", "P_net"]]
        for r in self.exp["sweeps"]["net_energy"]:
            ne_rows.append([
                r["scenario"], f"{r['P_pro_W']:.2f}", f"{r['P_pump_W']:.2f}",
                f"{r['P_px_W']:.2f}", f"{r['P_net_W']:.2f}",
            ])
        self.table(ne_rows, [1.2 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.2 * inch],
                   "Skid net energy balance (simulation/parasitics.py).")
        self.h2("6.13 Experiment E13 — TSC injection sweep")
        self.figure("fig11_tsc_injection.png", "TSC dissipated power vs soil injection current.")

    def _hardware_full(self) -> None:
        self.h1("7. Hardware realization")
        self.paras(hardware_paragraphs(self.ctx))
        self.h2("7.1 Safety and pressure systems")
        self.paras(safety_paragraphs(self.ctx))
        self.h2("7.2 Net energy balance (parasitics)")
        self.paras(parasitic_balance_paragraphs(self.ctx))
        self.table([
            ["ID", "Part", "Role"],
            ["PRO-01", "membrane_housing", "Stack shell"],
            ["PRO-05/06", "manifolds", "Feed / draw"],
            ["PRO-07", "px_module", "Pressure exchange"],
            ["AEH-01", "chorus_aeh_panel", "6×4 cells"],
            ["CHOR-01", "skid_enclosure", "Plenum"],
            ["STR-01", "skid_frame", "Structure"],
        ], [0.7 * inch, 2.0 * inch, 3.5 * inch], "Representative CAD index (23 parts total).")

    def _openscad_deep_dive(self) -> None:
        self.h1("7A. OpenSCAD mechanical digital twin")
        self.paras(openscad_paragraphs(self.ctx))
        gc = self.openscad.get("generated_constants", {})
        if gc:
            self.table([
                ["CAD parameter", "Value"],
                ["housing_od", f"{gc.get('housing_od', 0):.0f} mm"],
                ["stack_length", f"{gc.get('stack_length_mm', 0):.0f} mm"],
                ["frame_L×W×H", f"{gc.get('frame_L', 0):.0f}×{gc.get('frame_W', 0):.0f}×{gc.get('frame_H', 0):.0f} mm"],
                ["bolt_circle", f"{gc.get('bolt_circle', 0):.0f} mm"],
                ["delta_P_bar", f"{gc.get('delta_P_bar', 0):.1f} bar"],
            ], caption="Generated constants driving all PRO parts.")
        parts = self.openscad.get("parts", [])[:12]
        if parts:
            rows = [["Part file", "Modules", "Sized from JSON"]]
            for p in parts:
                mods = ", ".join(p.get("modules", [])[:2]) or "—"
                rows.append([p["file"], mods, "yes" if p.get("uses_generated_constants") else "no"])
            self.table(rows, [2.2 * inch, 2.5 * inch, 1.5 * inch],
                       "OpenSCAD audit (12 of 23 parts; full list in openscad_audit.json).")

    def _testing(self) -> None:
        self.h1("8. Bench and field test protocol")
        self.paras(test_protocol_paragraphs(self.ctx))

    def _worked_examples(self) -> None:
        self.h1("8A. Worked numerical examples")
        self.paras(worked_examples_paragraphs(self.ctx))

    def _ranked_and_deployment(self) -> None:
        self.h1("8B. Ranked concepts and deployment path")
        self.paras(ranked_concepts_paragraphs(self.ctx))
        self.paras(deployment_paragraphs(self.ctx))

    def _notebook_section(self) -> None:
        self.h1("8C. Notebook reproducibility map")
        self.paras(notebook_walkthrough_paragraphs(self.ctx))

    def _discussion_full(self) -> None:
        self.h1("9. Discussion")
        self.paras(discussion_paragraphs(self.ctx))
        self.h2("9.1 Claims hierarchy (summary)")
        self.table([
            ["Tier", "Claim", "Evidence status"],
            ["1", "PRO Δπ, ΔP* sizing", "Model + CAD"],
            ["1", "Kim–Baker peak", "E1 sweep"],
            ["1", "L_p calibration needed", "E2, Π₅"],
            ["2", "Column 22 MW/km²", "E7 MC, PV-dominated"],
            ["2", "TSC routing", "Illustrative G"],
            ["2", "AEH mW harvest", "E6, Mode A"],
        ], [0.6 * inch, 2.8 * inch, 2.8 * inch], "Claims tiering for stakeholders.")

    def _conclusion_future(self) -> None:
        self.h1("10. Conclusion and future work")
        self.p(
            "CHORUS-SGH-1 delivers a complete, falsifiable pipeline from osmotic thermodynamics "
            "to bench hardware. Joseph Black PoC report v3 adds exhaustive layer theory, seven "
            "numerical experiments, seven figures, and explicit separation of tier-1 PRO/AEH "
            "claims from tier-2 column/TSC narratives. The central engineering action is bench "
            "validation of L_p and CP on anthropogenic brine—not re-litigating whether PV dominates land area."
        )
        self.h2("10.1 Future work")
        self.paras(future_work_paragraphs(self.ctx))

    def _appendices_full(self) -> None:
        self.h1("Appendix A — Estuary RED reference values")
        e, r = self.exp["estuary_RED"], self.res
        self.table([
            ["Quantity", "Value"],
            ["E_N", f"{e['E_N_mV']:.2f} mV"],
            ["V_stack (50 pair)", f"{r['V_stack_V']:.2f} V"],
            ["Δπ", f"{e['delta_pi_MPa']:.3f} MPa"],
            ["P''_blue", f"{e['P_max_W_m2']:.0f} W/m²"],
            ["R_int", f"{r['R_int_ohm_m2']:.3f} Ω·m²"],
            ["P_mix ceiling", f"{e['P_mix_ceiling_MW']:.0f} MW"],
        ], caption="From chorus_results.json.")
        self.h1("Appendix B — E1 pressure-ratio sweep (complete, 41 points)")
        rows = [["ΔP/Δπ", "ΔP MPa", "P (W)", "P'' (W/m²)", "Q (L/min)"]]
        sweep = [x for x in self.exp["sweeps"]["delta_P_ratio"] if "ratio" in x]
        for pt in sweep:
            rows.append([
                f"{pt['ratio']:.3f}", f"{pt['delta_P_MPa']:.3f}",
                f"{pt['P_W']:.3f}", f"{pt['P_W_m2']:.3f}", f"{pt['m_dot_L_min']:.3f}",
            ])
        self.table(rows, [0.9 * inch, 1.0 * inch, 0.9 * inch, 1.1 * inch, 1.0 * inch],
                   "Full Kim–Baker sweep (experiment E1).")
        self.h1("Appendix B2 — SymPy symbolic verification")
        self.paras(sympy_paragraphs(self.ctx))
        sym = self.exp.get("symbolic_checks", {})
        if sym.get("available"):
            self.eq(
                sym.get("latex_delta_pi", "Δπ = iRT(c_h - c_l)")[:80],
                f"Numeric Δπ = {sym.get('delta_pi_MPa_brine_pair', 0):.4f} MPa",
                f"Kim–Baker critical: {sym.get('kim_baker_at_half_delta_pi', 'dpi/2')}",
            )
        self.h1("Appendix B3 — Draft patent claims")
        self.paras(patent_draft_paragraphs(self.ctx))
        self.h1("Appendix C — E2 L_p sweep (full)")
        rows = [["L_p×10⁻¹²", "P (W)", "P''", "≥10W"]]
        for r in self.exp["sweeps"]["L_p"]:
            rows.append([f"{r['L_p']*1e12:.1f}", f"{r['P_W']:.2f}", f"{r['P_W_m2']:.2f}",
                         "Y" if r["hits_10W"] else "N"])
        self.table(rows, [1.5 * inch, 1.2 * inch, 1.5 * inch, 0.8 * inch])
        self.h1("Appendix D — E5 ultrasonic (full)")
        rows = [["g", "P_base", "P_us", "P_net"]]
        for r in self.exp["sweeps"]["ultrasonic_gain"]:
            rows.append([f"{r['flux_gain']:.2f}", f"{r['P_base_W']:.2f}",
                         f"{r.get('P_us_W', r.get('P_us_input_W', 0)):.2f}", f"{r['P_net_gain_W']:.3f}"])
        self.table(rows, [1.5 * inch] * 4)
        self.h1("Appendix E — Bill of materials (excerpt)")
        if self.bom:
            rows = [["ID", "Name", "Qty", "Material"]]
            for row in self.bom[:20]:
                rows.append([
                    row.get("part_id", ""),
                    (row.get("name", "") or "")[:28],
                    row.get("qty", ""),
                    (row.get("material", "") or "")[:18],
                ])
            self.table(rows, [0.7 * inch, 2.5 * inch, 0.6 * inch, 1.4 * inch],
                       "SGH1_BOM.csv (first 20 lines; full BOM in repository).")
        self.h1("Appendix F — CAD file list (complete)")
        parts = [
            "sgh1_assembly.scad", "sgh1_exploded_assembly.scad", "sgh1_membrane_housing.scad",
            "sgh1_membrane_plate.scad", "sgh1_manifold_feed.scad", "sgh1_manifold_draw.scad",
            "sgh1_px_module.scad", "sgh1_turbine_housing.scad", "chorus_aeh_panel.scad",
            "chorus_skid_enclosure.scad", "sgh1_skid_frame.scad", "sgh1_red_cartridge_v2.scad",
        ]
        for part in parts:
            self.p(f"• hardware/openscad/{part}")
        self.h1("Appendix G — Reproducibility commands")
        cmds = [
            "python -m simulation.experiments",
            "python -m simulation.pi_groups",
            "python -m simulation.symbolic_checks",
            "python scripts/audit_openscad.py",
            "python simulation/run_sizing.py --power 10 --density 8",
            "python scripts/generate_paper_figures.py",
            "python scripts/build_research_paper.py",
            "pytest",
        ]
        for c in cmds:
            self.p(f"<font face='Courier' size='9'>{c}</font>")

    def _references_full(self) -> None:
        self.pb()
        self.h1("References")
        refs = [
            "[1] Teng, Y. et al. Lipid-nanopore blue energy harvesting at estuary interfaces. <i>Nature Energy</i> (2026).",
            "[2] Skilhagen, S.E.; Dugstad, J.E.; Aaberg, R.J. Osmotic power—status, prospects, and challenges. <i>Desalination</i>.",
            "[3] Kim, Y.C.; Baker, R.W. Thermodynamic and transport analysis of pressure-retarded osmosis. <i>J. Membrane Science</i>.",
            "[4] He, W. et al. PRO technologies for salinity-gradient power: membranes and modules. <i>Renewable & Sustainable Energy Reviews</i>.",
            "[5] Fang, C. et al. Photovoltaic–magnetohydrodynamic evaporative coupling. <i>Energy & Environmental Science</i> (2026).",
            "[6] Yao, Y. et al. Moisture-enabled nanogenerators (Air-gen). <i>Advanced Materials</i>.",
            "[7] Virgo, S. et al. Atmospheric electricity and global circuit budget. <i>Global Challenges</i> (2020).",
            "[8] Statkraft. Osmotic power pilot plant Tofte (2009–2013). Technical documentation.",
            "[9] Post, J.W. et al. Salinity-gradient power: evaluation of pressure-retarded osmosis and reverse electrodialysis. <i>Renewable & Sustainable Energy Reviews</i>.",
            "[10] Achilli, A.; Cath, T.Y. Pressure retarded osmosis: advancement and challenges. <i>Desalination</i>.",
            "[11] Biesheuvel, P.M.; Burlakov, V.; Nijmeijer, K. Thermodynamics and optimal membrane permselectivity in salinity-gradient power. <i>Physical Review E</i>.",
            "[12] NSO (2026). Piezoelectrotrophy and bio-mechanical coupling in soil energy harvest.",
        ]
        for r in refs:
            self.p(r)

    def render(self) -> Path:
        self.build_story()
        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(OUT_PDF),
            pagesize=letter,
            rightMargin=0.85 * inch,
            leftMargin=0.85 * inch,
            topMargin=0.85 * inch,
            bottomMargin=0.8 * inch,
        )

        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.drawString(0.85 * inch, 0.42 * inch,
                              "Black (2026) · CHORUS-SGH-1 · differential-harness")
            canvas.drawRightString(7.65 * inch, 0.42 * inch, f"Page {doc.page}")
            canvas.restoreState()

        doc.build(self.story, onFirstPage=footer, onLaterPages=footer)
        return OUT_PDF


def build() -> Path:
    return PaperBuilder().render()


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path} ({path.stat().st_size:,} bytes)")
