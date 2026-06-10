"""Bench CSV validation gates."""

import csv
from pathlib import Path

from simulation.bench_validation import validate_bench_csv


def _write_sim_csv(path: Path, n: int = 120) -> None:
    fields = [
        "t_s", "P_feed_bar", "P_draw_bar", "Q_feed_L_min", "Q_draw_L_min",
        "cond_feed_mS_cm", "cond_draw_mS_cm", "T_feed_C", "T_draw_C",
        "P_elec_W", "P_us_W", "P_pump_W", "P_spin_motor_W", "P_net_W",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i in range(n):
            w.writerow({
                "t_s": float(i),
                "P_feed_bar": 0.5,
                "P_draw_bar": 34.0,
                "Q_feed_L_min": 2.0,
                "Q_draw_L_min": 0.15,
                "cond_feed_mS_cm": 8.0,
                "cond_draw_mS_cm": 85.0,
                "T_feed_C": 22.0,
                "T_draw_C": 23.0,
                "P_elec_W": 1.66,
                "P_us_W": 0.0,
                "P_pump_W": 0.35,
                "P_spin_motor_W": 0.0,
                "P_net_W": 0.5,
            })


def test_synthetic_csv_validates(tmp_path):
    csv_path = tmp_path / "test_run.csv"
    _write_sim_csv(csv_path)
    result = validate_bench_csv(csv_path)
    assert result.n_rows == 120
    assert result.P_net_steady_W > 0
    assert result.L_p_fit_m_Pa_s > 0
