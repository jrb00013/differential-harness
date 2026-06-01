"""Symbolic verification of key CHORUS equations (SymPy)."""

from __future__ import annotations

from pathlib import Path


def run_symbolic_checks() -> dict:
    try:
        import sympy as sp
    except ImportError:
        return {"available": False, "error": "sympy not installed"}

    R, F, T, i, c_h, c_l, z = sp.symbols("R F T i c_h c_l z", positive=True, real=True)
    pi_expr = i * R * T * c_h
    delta_pi = i * R * T * (c_h - c_l)
    E_N = R * T / (z * F) * sp.log(c_h / c_l)

    subs = {R: 8.314, F: 96485, T: 298.15, i: 2, z: 1, c_h: 1400, c_l: 5}
    delta_pi_val = float(delta_pi.subs(subs).evalf()) / 1e6  # MPa
    E_N_val = float(E_N.subs(subs).evalf()) * 1000  # mV

    # Kim–Baker: P_hyd ∝ (Δπ - ΔP)*ΔP, max at ΔP = Δπ/2
    dP, dpi, Lp, A, rho, eta_m, eta_h = sp.symbols(
        "dP dpi Lp A rho eta_m eta_h", positive=True, real=True
    )
    P_hyd = eta_m * eta_h * rho * Lp * A * (dpi - dP) * dP
    dP_star = sp.solve(sp.diff(P_hyd, dP), dP)
    dP_star_simplified = [sp.simplify(x) for x in dP_star]

    return {
        "available": True,
        "delta_pi_MPa_brine_pair": delta_pi_val,
        "E_N_mV_brine_pair": E_N_val,
        "kim_baker_critical_points": [str(x) for x in dP_star_simplified],
        "kim_baker_at_half_delta_pi": str(dP_star_simplified[0] if dP_star_simplified else "dpi/2"),
        "latex_delta_pi": sp.latex(delta_pi),
        "latex_E_N": sp.latex(E_N),
    }


def export(path: Path | None = None) -> Path:
    path = path or Path(__file__).resolve().parent.parent / "exports" / "symbolic_checks.json"
    import json

    data = run_symbolic_checks()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    p = export()
    print(f"Wrote {p}")
