#!/usr/bin/env python3
"""Lightweight live dashboard for an in-progress daq/logger.py bench session.

Deliberately stdlib-only (http.server + json), matching pyproject.toml's
zero-extra-dependency footprint -- no Flask/websocket dependency is
introduced. The server tails the target bench CSV on every request (a
CSV file being actively appended to by daq/logger.py or
daq/serial_sensors.py) and serves:

  * GET /api/latest  -> JSON of the most recent row + a bounded window
                        of recent rows for sparklines
  * GET /             -> a small polling HTML page rendering the above

Usage:
    python -m daq.dashboard --csv data/bench/T1_baseline_20260609_235853.csv --port 8765
"""

from __future__ import annotations

import argparse
import csv
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_WINDOW = 120  # rows kept for sparklines
SPARKLINE_FIELDS = [
    "P_feed_bar",
    "P_draw_bar",
    "Q_feed_L_min",
    "Q_draw_L_min",
    "P_elec_W",
    "P_net_W",
]

PAGE_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>CHORUS-SGH-1 Bench Dashboard</title>
<meta http-equiv="refresh" content="0">
<style>
  body {{ font-family: monospace; background:#111; color:#eee; margin:2rem; }}
  h1 {{ font-size: 1.1rem; color:#8fd; }}
  table {{ border-collapse: collapse; margin-top: 1rem; }}
  td, th {{ padding: 0.25rem 0.75rem; border-bottom: 1px solid #333; text-align: right; }}
  th {{ color:#8fd; }}
  .stale {{ color: #f66; }}
</style>
</head>
<body>
<h1>CHORUS-SGH-1 bench dashboard -- {csv_name}</h1>
<div id="status">Loading...</div>
<table id="table"></table>
<script>
async function tick() {{
  const res = await fetch('/api/latest');
  const data = await res.json();
  document.getElementById('status').innerText =
    data.n_rows + ' rows, last at t=' + (data.latest ? data.latest.t_s.toFixed(1) : 'n/a') + 's';
  if (!data.latest) return;
  let rows = '<tr><th>field</th><th>latest</th></tr>';
  for (const k in data.latest) {{
    rows += '<tr><td>' + k + '</td><td>' + data.latest[k] + '</td></tr>';
  }}
  document.getElementById('table').innerHTML = rows;
}}
tick();
setInterval(tick, 2000);
</script>
</body>
</html>
"""


def read_latest_window(csv_path: Path, window: int = DEFAULT_WINDOW) -> dict:
    """Read the tail of csv_path. Safe to call while the file is being appended to."""
    if not csv_path.exists():
        return {"n_rows": 0, "latest": None, "window": []}

    try:
        with csv_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as exc:  # file mid-write / transient race
        return {"n_rows": 0, "latest": None, "window": [], "error": str(exc)}

    if not rows:
        return {"n_rows": 0, "latest": None, "window": []}

    # A `window <= 0` should mean "no history, just the latest row" -- note
    # that Python's `rows[-0:]` is `rows[0:]` (the WHOLE list), not empty,
    # so window<=0 is special-cased rather than falling through to the
    # slice below.
    tail = rows[-window:] if window > 0 else rows[-1:]

    def _coerce(row: dict) -> dict:
        out = {}
        for k, v in row.items():
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = v
        return out

    tail_coerced = [_coerce(r) for r in tail]
    return {
        "n_rows": len(rows),
        "latest": tail_coerced[-1],
        "window": tail_coerced,
        "sparkline_fields": SPARKLINE_FIELDS,
    }


def make_handler(csv_path: Path, window: int):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # quiet default stdout spam
            pass

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/latest":
                payload = json.dumps(read_latest_window(csv_path, window)).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            elif path == "/":
                body = PAGE_TEMPLATE.format(csv_name=csv_path.name).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

    return Handler


def serve(csv_path: Path, host: str = "127.0.0.1", port: int = 8765, window: int = DEFAULT_WINDOW):
    """Start the dashboard HTTP server. Blocks until interrupted."""
    server = ThreadingHTTPServer((host, port), make_handler(csv_path, window))
    print(f"CHORUS-SGH-1 dashboard serving {csv_path} at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
    return server


def serve_in_background(csv_path: Path, host: str = "127.0.0.1", port: int = 0, window: int = DEFAULT_WINDOW):
    """Start the server on a background thread and return (server, thread).

    port=0 lets the OS pick a free ephemeral port (used by tests); read
    it back via server.server_address[1].
    """
    server = ThreadingHTTPServer((host, port), make_handler(csv_path, window))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main() -> None:
    p = argparse.ArgumentParser(description="Live dashboard for an active bench CSV")
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--host", type=str, default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    args = p.parse_args()
    serve(args.csv, host=args.host, port=args.port, window=args.window)


if __name__ == "__main__":
    main()
