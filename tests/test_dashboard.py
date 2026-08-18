"""Tests for daq/dashboard.py: live-dashboard endpoint over a fixture CSV.

Starts the real ThreadingHTTPServer on an ephemeral port (no mocking of
the HTTP layer) and hits it with urllib, to prove the JSON/HTML
endpoints actually work end-to-end.
"""

from __future__ import annotations

import json
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
