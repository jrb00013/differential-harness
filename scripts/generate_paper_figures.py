#!/usr/bin/env python3
"""Generate matplotlib figures for the research paper.

Every figure shares one visual system (colorblind-safe palette, consistent
type, 300 dpi raster output) supplied by ``pdf_genesis.plotstyle`` so the
figures read as one document instead of sixteen independently-styled plots.
Each figure also carries a small provenance footnote stating whether the
data shown is simulated, bench-measured, literature-cited, or a mix -- no
figure claims uncertainty (error bars/CI) that the underlying data does not
actually support.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from pdf_genesis.plotstyle import PALETTE, ROLE, apply_house_style, provenance_caption

apply_house_style(matplotlib)

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
FIGURES = EXPORTS / "figures"
DATA = ROOT / "data"

DPI = 300


def _load():
    return json.loads((EXPORTS / "paper_experiments.json").read_text())


def _load_bench_validation():
    p = EXPORTS / "bench_validation.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _load_bench_csv(name: str):
    path = DATA / "bench" / name
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def _save(fig, out: Path) -> Path:
    fig.tight_layout()
    fig.savefig(out, dpi=DPI)
    plt.close(fig)
    return out


def fig_pro_pressure_sweep(data: dict) -> Path:
    sweep = [p for p in data["sweeps"]["delta_P_ratio"] if "ratio" in p]
    x = [p["ratio"] for p in sweep]
    y = [p["P_W"] for p in sweep]
    peak_i = int(np.argmax(y))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "-", color=ROLE["primary"], lw=2, label="Model: P(ΔP/Δπ)")
    ax.plot(x[peak_i], y[peak_i], "o", color=ROLE["highlight"], ms=7, zorder=5)
    ax.annotate(
        f"peak {y[peak_i]:.2f} W",
        (x[peak_i], y[peak_i]),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
    )
    ax.axvline(0.5, color=ROLE["secondary"], ls="--", lw=1.5, label="Kim–Baker optimum ΔP*/Δπ = 0.5")
    ax.axvspan(0.4, 0.6, alpha=0.12, color=ROLE["tertiary"], label="FR-1 operating band")
    ax.set_xlabel("Hydraulic pressure ratio, ΔP / Δπ (dimensionless)")
    ax.set_ylabel("PRO equivalent power, P (W)")
    ax.set_title("SGH-1: PRO power vs. hydraulic pressure ratio\n(A = 0.72 m², L_p = 1×10⁻¹² m/(Pa·s))")
    ax.legend(loc="best")
    provenance_caption(ax, "delta_P_ratio sweep, exports/paper_experiments.json", kind="simulated")
    out = FIGURES / "fig01_pro_pressure_sweep.png"
    return _save(fig, out)


def fig_Lp_sweep(data: dict) -> Path:
    sweep = data["sweeps"]["L_p"]
    x = [p["L_p"] * 1e12 for p in sweep]
    y = [p["P_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.semilogx(x, y, "o-", color=ROLE["primary"], lw=2, markersize=5)
    ax.axhline(10, color=ROLE["secondary"], ls="--", lw=1.5, label="Design target: 10 W")
    fitted = data.get("real_world", {})
    lp_fit = None
    bv = _load_bench_validation()
    if bv.get("L_p_fit_m_Pa_s"):
        lp_fit = bv["L_p_fit_m_Pa_s"] * 1e12
        ax.axvline(lp_fit, color=ROLE["tertiary"], ls=":", lw=1.5,
                    label=f"Bench-fit L_p = {lp_fit:.2f}×10⁻¹²")
    ax.set_xlabel("Water permeability, L_p (×10⁻¹² m/(Pa·s))")
    ax.set_ylabel("PRO power, P (W)")
    ax.set_title("Permeability sensitivity — inverse sizing for bench validation")
    ax.legend()
    provenance_caption(
        ax,
        "L_p sweep is simulated; bench-fit marker from data/bench/T1_baseline CSV regression",
        kind="mixed" if lp_fit else "simulated",
    )
    out = FIGURES / "fig02_Lp_sweep.png"
    return _save(fig, out)


def fig_column_layers(data: dict) -> Path:
    layers = data["column_monte_carlo"]["layers"]
    names = list(layers.keys())
    medians = [layers[k]["median_MW"] for k in names]
    p10 = [layers[k].get("p10_MW") for k in names]
    p90 = [layers[k].get("p90_MW") for k in names]
    has_ci = all(v is not None for v in p10 + p90)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [ROLE["primary"], ROLE["tertiary"], ROLE["highlight"], ROLE["literature"]][: len(names)]
    if has_ci:
        lo = [m - a for m, a in zip(medians, p10)]
        hi = [b - m for m, b in zip(medians, p90)]
        bars = ax.bar(names, medians, color=colors, yerr=[lo, hi], capsize=4,
                       error_kw={"ecolor": "#333333", "elinewidth": 1})
    else:
        bars = ax.bar(names, medians, color=colors)
    ax.set_ylabel("Layer power contribution, median (MW)")
    ax.set_title("CHORUS column (1 km²) — Monte Carlo layer medians (N = 8000)")
    for b, v in zip(bars, medians):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    provenance_caption(
        ax,
        "column_monte_carlo layer medians, N=8000 draws" + (" with P10-P90 band" if has_ci else " (point estimate; P10/P90 not exported)"),
        kind="simulated" if has_ci else "point_estimate",
    )
    out = FIGURES / "fig03_column_layers.png"
    return _save(fig, out)


def fig_cp_sweep(data: dict) -> Path:
    sweep = data["sweeps"]["concentration_polarization"]
    x = [p["J_w"] * 1e5 for p in sweep]
    y = [p["power_loss_pct"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "s-", color=ROLE["secondary"], lw=2, markersize=4)
    ax.set_xlabel("Water flux, J_w (×10⁻⁵ m/s)")
    ax.set_ylabel("Effective driving-force loss (%)")
    ax.set_title("Concentration polarization — film model  c_w/c_b = exp(J_w / k_m)")
    provenance_caption(ax, "concentration_polarization sweep, film-theory model", kind="simulated")
    out = FIGURES / "fig04_cp_sweep.png"
    return _save(fig, out)


def fig_ultrasonic(data: dict) -> Path:
    sweep = data["sweeps"]["ultrasonic_gain"]
    g = [p["flux_gain"] for p in sweep]
    net = [p["P_net_gain_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(g, net, "o-", color=ROLE["tertiary"], lw=2)
    ax.axhline(0, color="#666666", lw=0.8)
    crossover = None
    for i in range(1, len(net)):
        if (net[i - 1] < 0) != (net[i] < 0):
            crossover = g[i - 1] + (g[i] - g[i - 1]) * (0 - net[i - 1]) / (net[i] - net[i - 1])
            break
    if crossover is not None:
        ax.axvline(crossover, color=ROLE["secondary"], ls="--", lw=1.2, label=f"Break-even gain ≈ {crossover:.2f}")
        ax.legend()
    ax.set_xlabel("Ultrasonic flux gain, g (Mode B, dimensionless)")
    ax.set_ylabel("Net power gain, P_net (W)")
    ax.set_title("AEH Mode B: net PRO gain after 1.5 W/m² ultrasonic parasitic load")
    provenance_caption(ax, "ultrasonic_gain sweep, parasitics model", kind="simulated")
    out = FIGURES / "fig05_ultrasonic_net.png"
    return _save(fig, out)


def fig_acoustic(data: dict) -> Path:
    sweep = data["sweeps"]["acoustic_SPL"]
    x = [p["spl_db"] for p in sweep]
    y = [p["power_mW"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "-", color=ROLE["literature"], lw=2)
    ax.set_xlabel("Sound pressure level (dB re 20 µPa)")
    ax.set_ylabel("Harvested power (mW)")
    ax.set_title("AEH Mode A: piezoelectric harvest vs. SPL (A = 0.5 m², η = 2%)")
    provenance_caption(ax, "acoustic_SPL sweep, piezo transduction model", kind="simulated")
    out = FIGURES / "fig06_acoustic_spl.png"
    return _save(fig, out)


def fig_salinity_comparison(data: dict) -> Path:
    pairs = data["sweeps"]["salinity_pairs"]
    names = [p["name"] for p in pairs]
    dpi = [p["delta_pi_MPa"] for p in pairs]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [ROLE["primary"], ROLE["secondary"], ROLE["highlight"], ROLE["literature"]][: len(names)]
    bars = ax.barh(names, dpi, color=colors)
    for b, v in zip(bars, dpi):
        ax.text(v, b.get_y() + b.get_height() / 2, f" {v:.2f}", va="center", fontsize=9)
    ax.set_xlabel("Osmotic pressure difference, Δπ (MPa)")
    ax.set_title("Salinity pair comparison — estuary RED vs. anthropogenic PRO")
    provenance_caption(ax, "salinity_pairs, van't Hoff estimate from cited concentrations", kind="simulated")
    out = FIGURES / "fig07_salinity_pairs.png"
    return _save(fig, out)


def fig_red_river(data: dict) -> Path:
    sweep = data["sweeps"]["red_river_c"]
    x = [p["c_river"] for p in sweep]
    y = [p["P_max_W_m2"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "-", color=ROLE["tertiary"], lw=2)
    ax.axhline(15, color=ROLE["secondary"], ls="--", lw=1.5, label="Statkraft Tofte pilot ≈ 15 W/m²")
    ax.set_xlabel("River concentration, c_river (mol/m³)")
    ax.set_ylabel("Max power density, P″_max (W/m²)")
    ax.set_title("Estuary RED: max power density vs. river salinity (c_sea = 600 mol/m³)")
    ax.legend(fontsize=8)
    provenance_caption(ax, "red_river_c sweep; reference line from exports/real_world_calibration.json", kind="mixed")
    out = FIGURES / "fig08_red_river_sweep.png"
    return _save(fig, out)


def fig_temperature(data: dict) -> Path:
    sweep = data["sweeps"]["temperature"]
    T = [p["T_K"] - 273.15 for p in sweep]
    P = [p["P_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(T, P, "o-", color=ROLE["secondary"], lw=2)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("PRO power, P (W)")
    ax.set_title("SGH-1 PRO power vs. temperature (brine/wastewater pair)")
    provenance_caption(ax, "temperature sweep, van't Hoff temperature dependence of Δπ", kind="simulated")
    out = FIGURES / "fig09_temperature.png"
    return _save(fig, out)


def fig_net_energy(data: dict) -> Path:
    rows = data["sweeps"]["net_energy"]
    names = [r["scenario"] for r in rows]
    P_net = [r["P_net_W"] for r in rows]
    bv = _load_bench_validation()
    if bv:
        names = names + ["T1 bench (measured)"]
        P_net = P_net + [bv["P_net_mean_W"]]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    colors = [ROLE["primary"], ROLE["secondary"], ROLE["literature"], ROLE["highlight"], ROLE["tertiary"]]
    bars = ax.barh(names, P_net, color=colors[: len(names)])
    if bv:
        bars[-1].set_hatch("//")
    ax.axvline(0, color="black", lw=0.8)
    for b, v in zip(bars, P_net):
        ax.text(v, b.get_y() + b.get_height() / 2, f" {v:.3f} W", va="center", fontsize=8)
    ax.set_xlabel("Net skid power, P_net (W)")
    ax.set_title("Skid energy balance — simulated scenarios vs. measured T1 baseline")
    provenance_caption(
        ax,
        "simulated scenarios from parasitics model; hatched bar is bench-measured mean from data/bench/T1_baseline CSV (n=30 samples, single run)",
        kind="mixed" if bv else "simulated",
    )
    out = FIGURES / "fig10_net_energy.png"
    return _save(fig, out)


def fig_tsc_injection(data: dict) -> Path:
    sweep = data["tsc"]["injection_sweep"]
    x = [p["I_soil_A"] * 1e6 for p in sweep]
    y = [p["P_dissipated_uW"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "-", color=ROLE["literature"], lw=2)
    ax.set_xlabel("Injected soil current (µA)")
    ax.set_ylabel("TSC dissipated power (µW)")
    ax.set_title("Telluric Storm Coupling — illustrative 3-node network")
    provenance_caption(ax, "tsc.injection_sweep, illustrative circuit model (not bench-validated)", kind="point_estimate")
    out = FIGURES / "fig11_tsc_injection.png"
    return _save(fig, out)


def fig_brine_pairs(data: dict) -> Path:
    sweep = data["sweeps"].get("brine_feed_pairs", data["sweeps"]["salinity_pairs"])
    names = [p["name"][:22] for p in sweep]
    dpi = [p["delta_pi_MPa"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    colors = [ROLE["secondary"], ROLE["highlight"], ROLE["primary"], ROLE["tertiary"]][: len(names)]
    bars = ax.barh(names, dpi, color=colors)
    for b, v in zip(bars, dpi):
        ax.text(v, b.get_y() + b.get_height() / 2, f" {v:.2f}", va="center", fontsize=9)
    ax.set_xlabel("Osmotic pressure difference, Δπ (MPa)")
    ax.set_title("Literature-backed salinity pairs — osmotic driving force")
    provenance_caption(ax, "brine_feed_pairs, van't Hoff estimate from cited feed concentrations", kind="literature")
    out = FIGURES / "fig12_brine_feed_pairs.png"
    return _save(fig, out)


# Approximate public coordinates for the named real-world case-study sites
# already cited in exports/real_world_calibration.json. These are geographic
# reference points for the pilot/plant locations, not simulated or fitted
# quantities.
_SITE_COORDS = {
    "Statkraft Tofte": (59.60, 10.42),   # Hurum, Norway
    "REAPower Trapani": (38.02, 12.53),  # Trapani, Italy
    "Perth PSDP": (-32.25, 115.77),      # Kwinana, Australia
}


def fig_design_vs_literature(data: dict) -> Path:
    rw = data.get("real_world", {})
    bv = _load_bench_validation()
    a = 0.72
    labels = ["SGH-1 model\n(L_p=1e-12)", "Perth-class\npair (calc.)", "Lit. 6.3 W/m²\n@0.72 m²"]
    p_vals = [
        data["sg_h1_baseline"]["P_default_Lp_W"],
        rw.get("perth_sidestream_pro", {}).get("P_W_Lp1e12", 0),
        6.3 * a,
    ]
    colors = [ROLE["primary"], ROLE["highlight"], ROLE["literature"]]
    if bv:
        labels.append("T1 bench\n(measured)")
        p_vals.append(bv["P_net_mean_W"])
        colors.append(ROLE["tertiary"])

    cases = data.get("real_world_case_studies") or []
    sites = [(name, lat, lon) for name, (lat, lon) in _SITE_COORDS.items()]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), gridspec_kw={"width_ratios": [1, 1.3]})

    ax0 = axes[0]
    bars = ax0.bar(labels, p_vals, color=colors)
    for b, v in zip(bars, p_vals):
        ax0.text(b.get_x() + b.get_width() / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    ax0.axhline(10, color=ROLE["secondary"], ls="--", lw=1.5, label="10 W design target")
    ax0.set_ylabel("Power (W)")
    ax0.set_title("(a) Model vs. literature vs. bench-measured")
    ax0.legend(fontsize=7, loc="upper left")
    ax0.tick_params(axis="x", labelsize=7)

    ax1 = axes[1]
    for name, lat, lon in sites:
        ax1.scatter(lon, lat, s=90, color=ROLE["secondary"], edgecolor="black", zorder=3)
        ax1.annotate(name, (lon, lat), xytext=(6, 4), textcoords="offset points", fontsize=8)
    ax1.axhline(0, color="#999999", lw=0.6)
    ax1.set_xlim(-30, 150)
    ax1.set_ylim(-45, 70)
    ax1.set_xlabel("Longitude (°)")
    ax1.set_ylabel("Latitude (°)")
    ax1.set_title("(b) Real-world PRO/RED pilot sites cited in this study")
    ax1.grid(True, alpha=0.3)

    provenance_caption(
        axes[0],
        "(a) simulated model + literature (Pedersen 2024 SSRN 4944813) + bench-measured T1; "
        "(b) plain lat/lon scatter of real cited pilot locations, no basemap imagery used",
        kind="mixed",
    )
    out = FIGURES / "fig13_literature_calibration.png"
    return _save(fig, out)


def fig_udt_eta_tink(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E14_udt_eta_tink", [])
    x = [p["eta_tink"] for p in sweep]
    y = [p["P_net_gain_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "o-", color=ROLE["literature"], lw=2)
    ax.axhline(0, color="#666666", lw=0.8)
    ax.set_xlabel("η_tink — Tink coupling efficiency (dimensionless)")
    ax.set_ylabel("UDT net PRO gain (W)")
    ax.set_title("E14: UDT η_tink vs. net power gain")
    provenance_caption(ax, "vision_stack.E14_udt_eta_tink, exploratory model (not bench-validated)", kind="point_estimate")
    out = FIGURES / "fig14_udt_eta_tink.png"
    return _save(fig, out)


def fig_aor_column(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E15_aor_column_height", [])
    x = [p["height_m"] for p in sweep]
    y = [p["P_net_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(x, y, "s-", color=ROLE["highlight"], lw=2)
    peak_i = int(np.argmax(y)) if y else 0
    if y:
        ax.plot(x[peak_i], y[peak_i], "o", color=ROLE["secondary"], ms=7, zorder=5)
        ax.annotate(f"peak H={x[peak_i]:.2f} m", (x[peak_i], y[peak_i]), xytext=(6, 6),
                     textcoords="offset points", fontsize=8)
    ax.set_xlabel("Resonant column height, H (m)")
    ax.set_ylabel("Net power, P_net (W)")
    ax.set_title("E15: AOR column height vs. net power (Acoustic-Osmotic Ram)")
    provenance_caption(ax, "vision_stack.E15_aor_column_height, exploratory model (not bench-validated)", kind="point_estimate")
    out = FIGURES / "fig15_aor_column.png"
    return _save(fig, out)


def fig_voh_omega(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E16_voh_omega", [])
    rpm = [p["rpm"] for p in sweep]
    y = [p["P_net_W"] for p in sweep]
    flat = vs.get("E16_flat_vs_voh", {}).get("flat_P_net_W", y[0] if y else 0)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(rpm, y, "o-", color=ROLE["primary"], lw=2, label="VOH P_net(ω)")
    ax.axhline(flat, color=ROLE["secondary"], ls="--", lw=1.5, label=f"Flat baseline ({flat:.2f} W)")
    be = vs.get("E16_breakeven_omega")
    if be:
        ax.axvline(be["rpm"], color=ROLE["tertiary"], ls=":", lw=1.5, label=f"Breakeven {be['rpm']:.0f} RPM")
    ax.set_xlabel("Spin rate (RPM)")
    ax.set_ylabel("Net power, P_net (W)")
    ax.set_title("E16: VOH spin vs. no-spin — Z-Hydro")
    ax.legend(fontsize=8)
    provenance_caption(ax, "vision_stack.E16_voh_omega, exploratory model (not bench-validated)", kind="point_estimate")
    out = FIGURES / "fig16_voh_omega.png"
    return _save(fig, out)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    data = _load()
    paths = [
        fig_pro_pressure_sweep(data),
        fig_Lp_sweep(data),
        fig_column_layers(data),
        fig_cp_sweep(data),
        fig_ultrasonic(data),
        fig_acoustic(data),
        fig_salinity_comparison(data),
        fig_red_river(data),
        fig_temperature(data),
        fig_net_energy(data),
        fig_tsc_injection(data),
        fig_brine_pairs(data),
        fig_design_vs_literature(data),
    ]
    if "vision_stack" in data:
        paths.extend([
            fig_udt_eta_tink(data),
            fig_aor_column(data),
            fig_voh_omega(data),
        ])
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
