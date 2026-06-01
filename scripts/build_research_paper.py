#!/usr/bin/env python3
"""Build Joseph Black PoC research paper PDF from repository math exports."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
OUT_PDF = ROOT / "papers" / "Black_2026_CHORUS_SGH1_PoC.pdf"


def _load_json(name: str) -> dict:
    return json.loads((EXPORTS / name).read_text(encoding="utf-8"))


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PaperTitle",
            parent=base["Title"],
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=14,
            textColor=colors.HexColor("#1a365d"),
        ),
        "author": ParagraphStyle(
            "Author",
            parent=base["Normal"],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "affil": ParagraphStyle(
            "Affil",
            parent=base["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#2c5282"),
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontSize=11,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "abstract": ParagraphStyle(
            "Abstract",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            leftIndent=24,
            rightIndent=24,
            spaceAfter=10,
        ),
        "kw": ParagraphStyle(
            "KW",
            parent=base["BodyText"],
            fontSize=9,
            leftIndent=24,
            rightIndent=24,
            spaceAfter=12,
        ),
    }


def _table(rows: list[list[str]], col_widths=None) -> Table:
    if col_widths is None:
        col_widths = [2.8 * inch, 2.2 * inch]
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def build() -> Path:
    chorus = _load_json("chorus_results.json")
    design = _load_json("sgh1_design.json")
    pi_path = EXPORTS / "sgh1_pi_groups.json"
    pi = json.loads(pi_path.read_text()) if pi_path.exists() else {}

    sz = design["sizing"]
    res = chorus["results"]
    st = _styles()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=letter,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
    )
    story: list = []

    # Title page
    story.append(Spacer(1, 0.6 * inch))
    story.append(
        Paragraph(
            "CHORUS-Skid SGH-1: A Proof-of-Concept Framework for "
            "Pressure-Retarded Osmosis on Anthropogenic Brine Gradients "
            "with Acoustic Harvest and Column-Scale Energy Accounting",
            st["title"],
        )
    )
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Joseph Black</b>", st["author"]))
    story.append(Paragraph("CHORUS Research — <i>differential-harness</i>", st["affil"]))
    story.append(Paragraph("Draft · June 2026 · Proof of concept", st["affil"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph("<b>Abstract</b>", st["h1"]))
    story.append(
        Paragraph(
            "Coastal and inland desalination plants discharge hypersaline brine while treated "
            "effluent remains at near-fresh salinity. We present <b>CHORUS</b> (Columnar Harvest "
            "of Osmotic, Rhizospheric, Orographic, and Solar flux) as a multi-physics accounting "
            "framework for a 1 km² coastal parcel, and <b>CHORUS-Skid SGH-1</b> as a bench-scale "
            "pressure-retarded osmosis (PRO) harness targeting 10 W from brine (1400 mol/m³) "
            "against wastewater (5 mol/m³). Van't Hoff thermodynamics, Kim–Baker optimal pressure, "
            "and solution-diffusion transport yield Δπ = 6.92 MPa, ΔP* = 34.6 bar, and A_mem = 0.72 m². "
            "Monte Carlo column integration (N = 8000) gives median 22.76 MW/km² (P10–P90: 19.6–26.5 MW), "
            "dominated by evaporatively coupled photovoltaics. Default L_p predicts 1.66 W versus the "
            "10 W design target; inverse sizing gives L_p* ≈ 6.0×10⁻¹² m/(Pa·s). We separate defensible "
            "near-term claims (PRO, acoustic harvest, ultrasonic CP assist) from exploratory Telluric "
            "Storm Coupling and atmospheric routing. Artifacts are open-source in differential-harness.",
            st["abstract"],
        )
    )
    story.append(
        Paragraph(
            "<b>Keywords:</b> pressure-retarded osmosis; salinity-gradient power; blue energy; "
            "concentration polarization; acoustic energy harvest; coastal energy systems",
            st["kw"],
        )
    )
    story.append(PageBreak())

    # 1 Introduction
    story.append(Paragraph("1. Introduction", st["h1"]))
    story.append(Paragraph("1.1 Motivation", st["h2"]))
    story.append(
        Paragraph(
            "Reverse-osmosis desalination produces low-salinity permeate and reject brine often exceeding "
            "7–8 wt% NaCl. Treated wastewater effluent remains at single-digit mol/m³ salinity. The Gibbs "
            "free energy of mixing between these streams is routinely dissipated rather than converted to "
            "work. Pressure-retarded osmosis (PRO) extracts hydraulic work as water permeates from feed into "
            "a pressurized draw compartment. Estuary RED demonstrations approach 15 W/m² electrical density; "
            "sidestream PRO on brine/effluent pairs offers higher Δπ at the cost of fouling and concentration "
            "polarization (CP).",
            st["body"],
        )
    )
    story.append(Paragraph("1.2 Contributions", st["h2"]))
    for item in [
        "Unified mathematical blueprint (Layers A–F) with explicit no-over-unity postulate.",
        "Executable SymPy/NumPy/SciPy proof exporting chorus_results.json.",
        "SGH-1 hardware: 12-plate PRO stack, OpenSCAD CAD, BOM, bench protocol T0/T1/T2.",
        "AEH-1 acoustic module: harvest (Mode A) and ultrasonic CP assist (Mode B).",
        "Honest power-density hierarchy: PV–hydro ≫ blue energy ≫ MEG/SMFC.",
    ]:
        story.append(Paragraph(f"• {item}", st["body"]))

    # 2 Theory
    story.append(Paragraph("2. Theoretical framework", st["h1"]))
    story.append(Paragraph("2.1 Osmotic driving force", st["h2"]))
    story.append(
        Paragraph(
            "For NaCl with van't Hoff factor i = 2: π = iRTc and Δπ = π_draw − π_feed. "
            "Nernst potential E_N = (RT/F) ln(c_draw/c_feed). Estuary reference (600/20 mol/m³): "
            f"E_N = {res['E_N_mV']:.2f} mV, V_stack = {res['V_stack_V']:.2f} V, "
            f"Δπ = {res['delta_pi_MPa']:.3f} MPa. SGH-1 brine pair (1400/5): "
            f"Δπ = {sz['delta_pi_MPa']:.3f} MPa (~2.4× estuary).",
            st["body"],
        )
    )
    story.append(Paragraph("2.2 PRO transport and Kim–Baker optimum", st["h2"]))
    story.append(
        Paragraph(
            "Water flux V̇_w = L_p A(Δπ − ΔP). Optimal hydraulic pressure ΔP* = Δπ/2. "
            "Equivalent electrical power P = η_mem η_hyd ρ V̇_w ΔP. Operating band 0.4–0.6 Δπ "
            "for the bench skid.",
            st["body"],
        )
    )
    story.append(Paragraph("2.3 Column balance (CHORUS)", st["h2"]))
    chorus_rows = [
        ["Quantity", "Value"],
        ["P_column median", f"{res['column_MW_median']:.2f} MW"],
        ["P_column P10 / P90", f"{res['column_MW_p10']:.2f} / {res['column_MW_p90']:.2f} MW"],
        ["P_pv'' (evap-cooled)", f"{res['P_pv_W_m2']:.1f} W/m²"],
        ["P_blue'' (estuary)", f"{res['P_blue_W_m2']:.1f} W/m²"],
        ["P_MFC''", f"{res['P_mfc_uW_m2']:.2f} µW/m²"],
    ]
    story.append(_table(chorus_rows))
    story.append(Spacer(1, 0.1 * inch))
    story.append(
        Paragraph(
            "PV–hydro dominates the column median; osmotic interface power is a credible baseload "
            "supplement, not the land-area leader.",
            st["body"],
        )
    )

    story.append(Paragraph("2.4 Concentration polarization and ultrasonic assist", st["h2"]))
    story.append(
        Paragraph(
            "Film model: c_w/c_b = exp(J_w/k_m). Effective driving force scales as 1/(c_w/c_b)_outlet. "
            "AEH Mode B applies 28 kHz ultrasound to disrupt the polarization layer, modeled as multiplicative "
            "gain g on water permeability L_p. Net power P_net = P_PRO(g) − P_US − P_0. At g = 1.35 and "
            "P_US = 1.5 W/m², net benefit requires bench-validated flux gain exceeding parasitic driver load.",
            st["body"],
        )
    )
    story.append(Paragraph("2.5 Telluric Storm Coupling (TSC)", st["h2"]))
    story.append(
        Paragraph(
            "Three-node conductance network (atmosphere, soil, estuary): Gψ = I. Dissipated power P_TSC = ψᵀGψ. "
            "TSC routes charge between high-impedance harvesters (MEG, SMFC); it does not create new source power. "
            "Illustrative conductances are order-of-magnitude placeholders pending geophysical instrumentation.",
            st["body"],
        )
    )
    story.append(Paragraph("2.6 Rhizospheric and atmospheric bounds", st["h2"]))
    story.append(
        Paragraph(
            "Butler–Volmer kinetics bound microbial fuel-cell current; piezoelectrotrophy couples mechanical "
            f"stress to bioelectrogenesis at µW/m² class (notebook: P_MFC'' = {res['P_mfc_uW_m2']:.1f} µW/m²). "
            f"Fair-weather global circuit P_glob ≈ {res['P_glob_GW']:.1f} GW implies areal mean ~10⁻⁴ W/m² — "
            "relevant for routing narratives, not land-area harvest.",
            st["body"],
        )
    )

    story.append(PageBreak())

    # 3 SGH-1
    story.append(Paragraph("3. CHORUS-Skid SGH-1 system", st["h1"]))
    story.append(
        Paragraph(
            "SGH-1 integrates a 12-plate PRO core (200×300 mm active area), AEH-1 piezo/ultrasonic panel, "
            "CHORUS enclosure for future moist-thermal ports, and DAQ for pressure, conductivity, flow, and voltage.",
            st["body"],
        )
    )
    story.append(Paragraph("3.1 Sizing results", st["h2"]))
    design_rows = [
        ["Parameter", "Value"],
        ["P_target", f"{sz['P_target_W']:.1f} W"],
        ["P''_design", f"{sz['P_density_W_m2']:.1f} W/m²"],
        ["A_mem", f"{sz['A_mem_m2']:.2f} m² ({int(sz['n_plates'])} plates)"],
        ["Δπ", f"{sz['delta_pi_MPa']:.3f} MPa"],
        ["ΔP*", f"{sz['delta_P_star_bar']:.2f} bar"],
        ["Q_feed (model)", f"{sz['Q_feed_L_min']:.3f} L/min"],
        ["Frame (L×W×H)", f"{sz['frame_length_mm']}×{sz['frame_width_mm']}×{sz['frame_height_mm']} mm"],
    ]
    story.append(_table(design_rows))

    if pi:
        story.append(Paragraph("3.2 Dimensionless groups", st["h2"]))
        pi_rows = [
            ["Group", "Value"],
            ["Π₁ = ΔP/Δπ", f"{pi.get('Pi1_delta_P_over_delta_pi', 0):.3f}"],
            ["Π₃ = Pe", f"{pi.get('Pi3_Pe_order', 0):.3f}"],
            ["Π₄ = P''A/P_target", f"{pi.get('Pi4_area_law', 0):.3f}"],
            ["Π₅ = P_sim/P_target", f"{pi.get('Pi5_sim_over_target', 0):.3f}"],
            ["L_p* for 10 W", f"{pi.get('L_p_required_for_target', 0):.2e} m/(Pa·s)"],
            ["P_sim", f"{pi.get('P_sim_W', 0):.2f} W"],
        ]
        story.append(_table(pi_rows))

    # 4 Methods
    story.append(Paragraph("4. Methods", st["h1"]))
    story.append(
        Paragraph(
            "Software: CHORUS_physics_proof.ipynb; simulation/pro_cycle.py, sizing.py, "
            "membrane_transport.py, ultrasonic_cp_gain.py; run_sizing.py; pi_groups.py. "
            "Hardware: 23 OpenSCAD parts, BUILD_BLUEPRINT.md, SGH1_TEST_PROTOCOL.md. "
            "Materials: SS316 wetted paths per MATERIALS_SPEC.md.",
            st["body"],
        )
    )

    # 5 Discussion & Conclusion
    story.append(Paragraph("5. Discussion", st["h1"]))
    story.append(
        Paragraph(
            "PRO on anthropogenic brine leverages existing desal infrastructure. The 10 W target follows "
            "A = P_target/P'' with a twelve-plate CAD cap; default L_p under-predicts at 1.66 W. Bench T1 "
            "(±30%) must validate L_p or revise P''. Mode A acoustic harvest remains mW-class; Mode B net "
            "gain requires flux gain g to exceed ultrasonic parasitics. The 22.8 MW/km² column median is "
            "exploratory and must not be conflated with bench claims.",
            st["body"],
        )
    )
    story.append(Paragraph("6. Conclusion", st["h1"]))
    story.append(
        Paragraph(
            "We presented a physics-first CHORUS framework and a concrete PRO bench skid (SGH-1) for "
            "anthropogenic brine gradients. Near-term work centers on PRO, DAQ, and CP/ultrasonic assist; "
            "column-scale and TSC claims are tiered as context. Every equation is reproducible from "
            "differential-harness open-source artifacts.",
            st["body"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Appendix A — Governing equations (Layer F PRO)", st["h1"]))
    eqs = [
        "π = iRTc",
        "Δπ = iRT(c_draw − c_feed)",
        "V̇_w = L_p A(Δπ − ΔP)",
        "ΔP* = Δπ/2",
        "P_elec = η_mem η_hyd ρ V̇_w ΔP",
        "c_w/c_b = exp(J_w/k_m)",
    ]
    for eq in eqs:
        story.append(Paragraph(f"<font face='Courier'>{eq}</font>", st["body"]))

    story.append(Paragraph("Appendix B — Repository artifacts", st["h1"]))
    repo_rows = [
        ["Path", "Role"],
        ["docs/CHORUS_MATH_PLAN.md", "Master equation list"],
        ["docs/math/PRO_LAYER_DERIVATION.md", "Layer F derivation"],
        ["notebooks/CHORUS_physics_proof.ipynb", "Executable proof"],
        ["exports/chorus_results.json", "Column + estuary numbers"],
        ["exports/sgh1_design.json", "Skid sizing"],
        ["hardware/openscad/", "23-part CAD library"],
    ]
    story.append(_table(repo_rows, col_widths=[3.2 * inch, 2.8 * inch]))

    story.append(Paragraph("References", st["h1"]))
    refs = [
        "[1] Teng et al., Nature Energy (2026) — nanopore blue energy ~15 W/m².",
        "[2] Skilhagen et al., Desalination — PRO fundamentals.",
        "[3] Kim & Baker, J. Membrane Sci. — optimal osmotic pressure.",
        "[4] Fang et al., Energy Environ. Sci. (2026) — PV–MHD coupling.",
        "[5] Yao et al., Advanced Materials — moisture charge separation.",
        "[6] Virgo et al., Global Challenges (2020) — atmospheric electricity.",
    ]
    for r in refs:
        story.append(Paragraph(r, st["body"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(0.85 * inch, 0.5 * inch, "Black (2026) — CHORUS-SGH-1 PoC — differential-harness")
        canvas.drawRightString(7.65 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUT_PDF


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
