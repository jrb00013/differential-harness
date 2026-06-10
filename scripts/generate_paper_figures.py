#!/usr/bin/env python3
"""Generate matplotlib figures for the research paper."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
FIGURES = EXPORTS / "figures"


def _load():
    return json.loads((EXPORTS / "paper_experiments.json").read_text())


def fig_pro_pressure_sweep(data: dict) -> Path:
    sweep = [p for p in data["sweeps"]["delta_P_ratio"] if "ratio" in p]
    x = [p["ratio"] for p in sweep]
    y = [p["P_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "b-", lw=2)
    ax.axvline(0.5, color="crimson", ls="--", label="Kim–Baker ΔP*/Δπ = 0.5")
    ax.axvspan(0.4, 0.6, alpha=0.12, color="green", label="FR-1 operating band")
    ax.set_xlabel("Hydraulic pressure ratio ΔP / Δπ")
    ax.set_ylabel("PRO equivalent power P (W)")
    ax.set_title("SGH-1: PRO power vs hydraulic pressure ratio (A = 0.72 m², L_p = 1×10⁻¹²)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig01_pro_pressure_sweep.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_Lp_sweep(data: dict) -> Path:
    sweep = data["sweeps"]["L_p"]
    x = [p["L_p"] * 1e12 for p in sweep]
    y = [p["P_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.semilogx(x, y, "o-", color="#2c5282", lw=2, markersize=6)
    ax.axhline(10, color="crimson", ls="--", label="Design target 10 W")
    ax.set_xlabel("Water permeability L_p (×10⁻¹² m/(Pa·s))")
    ax.set_ylabel("PRO power P (W)")
    ax.set_title("Permeability sensitivity — inverse sizing for bench validation")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    out = FIGURES / "fig02_Lp_sweep.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_column_layers(data: dict) -> Path:
    layers = data["column_monte_carlo"]["layers"]
    names = list(layers.keys())
    medians = [layers[k]["median_MW"] for k in names]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    colors = ["#1a365d", "#38a169", "#d69e2e", "#805ad5"]
    bars = ax.bar(names, medians, color=colors)
    ax.set_ylabel("Median layer contribution (MW)")
    ax.set_title("CHORUS column (1 km²) — Monte Carlo layer medians (N = 8000)")
    for b, v in zip(bars, medians):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f"{v:.2f}", ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    out = FIGURES / "fig03_column_layers.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_cp_sweep(data: dict) -> Path:
    sweep = data["sweeps"]["concentration_polarization"]
    x = [p["J_w"] * 1e5 for p in sweep]
    y = [p["power_loss_pct"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "s-", color="#c05621", lw=2)
    ax.set_xlabel("Water flux J_w (×10⁻⁵ m/s)")
    ax.set_ylabel("Effective driving-force loss (%)")
    ax.set_title("Concentration polarization — film model c_w/c_b = exp(J_w/k_m)")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig04_cp_sweep.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_ultrasonic(data: dict) -> Path:
    sweep = data["sweeps"]["ultrasonic_gain"]
    g = [p["flux_gain"] for p in sweep]
    net = [p["P_net_gain_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(g, net, "o-", color="#319795", lw=2)
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("Ultrasonic flux gain g (Mode B)")
    ax.set_ylabel("Net power gain P_net (W)")
    ax.set_title("AEH Mode B: net PRO gain after 1.5 W/m² US parasitic")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig05_ultrasonic_net.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_acoustic(data: dict) -> Path:
    sweep = data["sweeps"]["acoustic_SPL"]
    x = [p["spl_db"] for p in sweep]
    y = [p["power_mW"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "-", color="#553c9a", lw=2)
    ax.set_xlabel("Sound pressure level (dB re 20 µPa)")
    ax.set_ylabel("Harvested power (mW)")
    ax.set_title("AEH Mode A: piezo harvest vs SPL (A = 0.5 m², η = 2%)")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig06_acoustic_spl.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_salinity_comparison(data: dict) -> Path:
    pairs = data["sweeps"]["salinity_pairs"]
    names = [p["name"] for p in pairs]
    dpi = [p["delta_pi_MPa"] for p in pairs]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.barh(names, dpi, color=["#4299e1", "#e53e3e", "#ed8936", "#9f7aea"])
    ax.set_xlabel("Osmotic pressure difference Δπ (MPa)")
    ax.set_title("Salinity pair comparison — estuary RED vs anthropogenic PRO")
    ax.grid(True, axis="x", alpha=0.3)
    out = FIGURES / "fig07_salinity_pairs.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_red_river(data: dict) -> Path:
    sweep = data["sweeps"]["red_river_c"]
    x = [p["c_river"] for p in sweep]
    y = [p["P_max_W_m2"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "g-", lw=2)
    ax.axhline(15, color="gray", ls="--", label="Literature anchor 15 W/m²")
    ax.set_xlabel("River concentration c_river (mol/m³)")
    ax.set_ylabel("P''_max (W/m²)")
    ax.set_title("Estuary RED: max power vs river salinity (c_sea = 600)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig08_red_river_sweep.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_temperature(data: dict) -> Path:
    sweep = data["sweeps"]["temperature"]
    T = [p["T_K"] - 273.15 for p in sweep]
    P = [p["P_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(T, P, "o-", color="#c05621", lw=2)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("PRO power P (W)")
    ax.set_title("SGH-1 PRO power vs temperature (brine pair)")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig09_temperature.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_net_energy(data: dict) -> Path:
    rows = data["sweeps"]["net_energy"]
    names = [r["scenario"] for r in rows]
    P_net = [r["P_net_W"] for r in rows]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    colors = ["#2c5282", "#e53e3e", "#805ad5", "#d69e2e"]
    ax.barh(names, P_net, color=colors[: len(names)])
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Net skid power P_net (W)")
    ax.set_title("Skid energy balance scenarios (parasitics model)")
    ax.grid(True, axis="x", alpha=0.3)
    out = FIGURES / "fig10_net_energy.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_tsc_injection(data: dict) -> Path:
    sweep = data["tsc"]["injection_sweep"]
    x = [p["I_soil_A"] * 1e6 for p in sweep]
    y = [p["P_dissipated_uW"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "-", color="#553c9a", lw=2)
    ax.set_xlabel("Injected soil current (µA)")
    ax.set_ylabel("TSC dissipated power (µW)")
    ax.set_title("Telluric Storm Coupling — illustrative 3-node network")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig11_tsc_injection.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_brine_pairs(data: dict) -> Path:
    sweep = data["sweeps"].get("brine_feed_pairs", data["sweeps"]["salinity_pairs"])
    names = [p["name"][:18] for p in sweep]
    dpi = [p["delta_pi_MPa"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.barh(names, dpi, color=["#e53e3e", "#dd6b20", "#3182ce", "#38a169"][: len(names)])
    ax.set_xlabel("Δπ (MPa)")
    ax.set_title("Literature-backed salinity pairs — osmotic driving force")
    ax.grid(True, axis="x", alpha=0.3)
    out = FIGURES / "fig12_brine_feed_pairs.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_design_vs_literature(data: dict) -> Path:
    rw = data.get("real_world", {})
    a = 0.72
    labels = ["SGH-1 model\n(L_p=1e-12)", "Perth-class\npair", "Lit. 6.3 W/m²\n@0.72 m²"]
    p_vals = [
        data["sg_h1_baseline"]["P_default_Lp_W"],
        rw.get("perth_sidestream_pro", {}).get("P_W_Lp1e12", 0),
        6.3 * a,
    ]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(labels, p_vals, color=["#2c5282", "#ed8936", "#48bb78"])
    ax.axhline(10, color="crimson", ls="--", label="10 W target")
    ax.set_ylabel("Power (W)")
    ax.set_title("Model vs real-world calibrated scenarios")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    out = FIGURES / "fig13_literature_calibration.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_udt_eta_tink(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E14_udt_eta_tink", [])
    x = [p["eta_tink"] for p in sweep]
    y = [p["P_net_gain_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "o-", color="#805ad5", lw=2)
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("η_tink (Tink coupling)")
    ax.set_ylabel("UDT net PRO gain (W)")
    ax.set_title("E14: UDT η_tink vs net power gain")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig14_udt_eta_tink.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_aor_column(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E15_aor_column_height", [])
    x = [p["height_m"] for p in sweep]
    y = [p["P_net_W"] for p in sweep]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(x, y, "s-", color="#dd6b20", lw=2)
    ax.set_xlabel("Resonant column height H (m)")
    ax.set_ylabel("P_net (W)")
    ax.set_title("E15: AOR column height vs net power")
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig15_aor_column.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_voh_omega(data: dict) -> Path:
    vs = data.get("vision_stack", {})
    sweep = vs.get("E16_voh_omega", [])
    rpm = [p["rpm"] for p in sweep]
    y = [p["P_net_W"] for p in sweep]
    flat = vs.get("E16_flat_vs_voh", {}).get("flat_P_net_W", y[0] if y else 0)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(rpm, y, "o-", color="#2b6cb0", lw=2, label="VOH P_net(ω)")
    ax.axhline(flat, color="crimson", ls="--", label=f"Flat baseline ({flat:.2f} W)")
    be = vs.get("E16_breakeven_omega")
    if be:
        ax.axvline(be["rpm"], color="green", ls=":", label=f"Breakeven {be['rpm']:.0f} RPM")
    ax.set_xlabel("Spin rate (RPM)")
    ax.set_ylabel("P_net (W)")
    ax.set_title("E16: VOH spin vs no-spin — Z-Hydro")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    out = FIGURES / "fig16_voh_omega.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


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
