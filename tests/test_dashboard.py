"""Tests for daq/dashboard.py: live-dashboard endpoint over a fixture CSV.

Starts the real ThreadingHTTPServer on an ephemeral port (no mocking of
the HTTP layer) and hits it with urllib, to prove the JSON/HTML
endpoints actually work end-to-end. Round 2 adds coverage for the
actual operating condition (a CSV being actively appended to while
served), concurrent requests, window boundary behavior, and malformed
numeric fields.
"""

from __future__ import annotations

import concurrent.futures
import csv
import json
import threading
import time
import urllib.error
import urllib.request

from daq.dashboard import read_latest_window, serve_in_background

FIELDNAMES = ["t_s", "P_feed_bar", "P_draw_bar", "P_elec_W"]


def _write_csv(path, n_rows=5):
    import csv

    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for i in range(n_rows):
            w.writerow({"t_s": i, "P_feed_bar": 0.5 + i * 0.01, "P_draw_bar": 34.0, "P_elec_W": 1.7})


def test_read_latest_window_on_missing_file(tmp_path):
    result = read_latest_window(tmp_path / "does_not_exist.csv")
    assert result["n_rows"] == 0
    assert result["latest"] is None


def test_read_latest_window_returns_tail(tmp_path):
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, n_rows=10)
    result = read_latest_window(csv_path, window=3)
    assert result["n_rows"] == 10
    assert len(result["window"]) == 3
    assert result["latest"]["t_s"] == 9.0


def test_dashboard_server_serves_json_and_html(tmp_path):
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, n_rows=4)

    server, thread = serve_in_background(csv_path, port=0)
    try:
        port = server.server_address[1]

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/latest", timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert payload["n_rows"] == 4
        assert payload["latest"]["t_s"] == 3.0

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            html = resp.read().decode("utf-8")
        assert "CHORUS-SGH-1" in html
        assert "bench.csv" in html

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/unknown", timeout=5) as resp:
            pass
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    finally:
        server.shutdown()


def test_read_latest_window_boundary_window_larger_than_file(tmp_path):
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, n_rows=3)
    result = read_latest_window(csv_path, window=1000)
    assert result["n_rows"] == 3
    assert len(result["window"]) == 3  # capped at available rows, no crash/pad


def test_read_latest_window_zero_window_still_returns_latest(tmp_path):
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, n_rows=5)
    result = read_latest_window(csv_path, window=0)
    # window=0 must not be interpreted as Python's rows[-0:] (== whole list);
    # it should mean "no history rows", but latest is still populated.
    assert result["latest"]["t_s"] == 4.0
    assert len(result["window"]) <= 1


def test_read_latest_window_handles_malformed_numeric_field(tmp_path):
    csv_path = tmp_path / "bench.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerow({"t_s": 0, "P_feed_bar": "NaN-sensor-error", "P_draw_bar": 34.0, "P_elec_W": 1.7})
        w.writerow({"t_s": 1, "P_feed_bar": 0.51, "P_draw_bar": 34.0, "P_elec_W": 1.7})

    result = read_latest_window(csv_path)
    assert result["n_rows"] == 2
    # malformed field falls back to the raw string rather than crashing
    assert result["window"][0]["P_feed_bar"] == "NaN-sensor-error"
    assert result["window"][1]["P_feed_bar"] == 0.51


def test_read_latest_window_survives_truncated_row_mid_write(tmp_path):
    """Simulates reading a CSV while a writer's last line is only partially flushed."""
    csv_path = tmp_path / "bench.csv"
    header = ",".join(FIELDNAMES) + "\n"
    complete_row = "0,0.5,34.0,1.7\n"
    partial_row = "1,0.51,3"  # truncated mid-field, no newline
    csv_path.write_text(header + complete_row + partial_row, encoding="utf-8")

    result = read_latest_window(csv_path)
    # Should not raise; at minimum the complete row is readable.
    assert result["n_rows"] >= 1
    assert result["latest"] is not None


def test_dashboard_survives_concurrent_appends_while_serving(tmp_path):
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, n_rows=1)

    server, thread = serve_in_background(csv_path, port=0)
    stop = threading.Event()

    def writer():
        i = 1
        while not stop.is_set():
            with csv_path.open("a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=FIELDNAMES)
                w.writerow({"t_s": i, "P_feed_bar": 0.5, "P_draw_bar": 34.0, "P_elec_W": 1.7})
            i += 1
            time.sleep(0.005)

    writer_thread = threading.Thread(target=writer, daemon=True)
    writer_thread.start()
    try:
        port = server.server_address[1]
        errors = []

        def hit():
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/latest", timeout=5) as resp:
                    json.loads(resp.read().decode("utf-8"))
            except Exception as exc:  # pragma: no cover - failure path under test
                errors.append(exc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(hit) for _ in range(40)]
            concurrent.futures.wait(futures)

        assert not errors, f"concurrent requests during active writes raised: {errors}"
    finally:
        stop.set()
        writer_thread.join(timeout=2)
        server.shutdown()
