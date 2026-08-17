"""Tests for scripts/calibrate_constants.py.

All data here is synthetic (numpy-generated in-memory or hand-written
CSV fixtures) -- never claimed as real hardware data. These tests
validate the fitting math itself: given a known-slope relationship, the
fit should recover it, and every code path must be provenance-labeled
as simulated/synthetic, never "real".
"""

from __future__ import annotations

import csv

import numpy as np
import pytest

from scripts.calibrate_constants import calibrate, fit_rpm_torque


def test_fit_rpm_torque_recovers_known_linear_slope():
    true_slope = 4.0e-4  # Nm per rpm
    rpm = np.linspace(10, 200, 20)
    omega_rad_s = rpm * (2 * np.pi / 60.0)
    torque = true_slope * rpm
    power = torque * omega_rad_s

    fit = fit_rpm_torque(rpm, power)
    assert fit["sufficient_data"] is True
    assert fit["slope_Nm_per_rpm"] == pytest.approx(true_slope, rel=1e-6)
    assert fit["r_squared"] == pytest.approx(1.0, abs=1e-9)


def test_fit_rpm_torque_reports_insufficient_data():
    fit = fit_rpm_torque(np.array([0.0, 0.0]), np.array([0.0, 0.0]))
    assert fit["sufficient_data"] is False


def test_calibrate_labels_simulated_csv_as_simulated(tmp_path):
    csv_path = tmp_path / "fake_bench.csv"
    fieldnames = [
        "t_s",
        "P_feed_bar",
        "P_draw_bar",
        "Q_feed_L_min",
        "Q_draw_L_min",
        "cond_feed_mS_cm",
        "cond_draw_mS_cm",
        "T_feed_C",
        "T_draw_C",
        "P_elec_W",
        "P_pump_W",
        "P_us_W",
        "P_spin_motor_W",
        "P_net_W",
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for t in range(20):
            w.writerow(
                {
                    "t_s": t,
                    "P_feed_bar": 0.5,
                    "P_draw_bar": 34.0,
                    "Q_feed_L_min": 2.0,
                    "Q_draw_L_min": 0.15,
                    "cond_feed_mS_cm": 8.0,
                    "cond_draw_mS_cm": 85.0,
                    "T_feed_C": 22.0,
                    "T_draw_C": 23.0,
                    "P_elec_W": 1.7,
                    "P_pump_W": 0.35,
                    "P_us_W": 0.0,
                    "P_spin_motor_W": 0.0,
                    "P_net_W": 0.25,
                }
            )

    result = calibrate([csv_path])
    assert result["L_p_fits"][0]["data_provenance"] == "simulated"
    # No RPM variation in this fixture -> falls back to the synthetic demo path
    assert result["rpm_torque_fit"]["synthetic_demo"] is True
    assert "real" not in result["status"].lower() or "not been collected" in result["status"].lower()
