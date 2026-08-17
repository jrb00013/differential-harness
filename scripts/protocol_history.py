#!/usr/bin/env python3
"""CLI to inspect protocol-run history across data/bench/*/checkpoint.json.

Round 1 added checkpointing to scripts/run_test_protocol.py, but
checkpoint.json/manifest.json were only ever consumed by the runner
itself -- answering "which bench sessions have I completed, and did
they pass?" meant manually grepping JSON files across every
`data/bench/<TEST>_<date>/` directory. This CLI aggregates that into a
table (or `--json` for scripting).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "bench"


@dataclass
class RunRecord:
    out_dir: str
    test: str | None
    completed_steps: list[str]
    n_completed: int
    n_runs_in_manifest: int | None
    pass_t1: bool | None
    last_modified: float | None


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def scan_run_dir(run_dir: Path) -> RunRecord | None:
    """Build a RunRecord for one data/bench/<TEST>_<date>/ directory.

    Returns None if the directory has neither a checkpoint.json nor a
    manifest.json (i.e. it isn't a protocol-run output directory at all).
    """
    checkpoint = _read_json(run_dir / "checkpoint.json")
    manifest = _read_json(run_dir / "manifest.json")
    if checkpoint is None and manifest is None:
        return None

    completed = sorted((checkpoint or {}).get("completed_steps", {}).keys())

    validation = _read_json(run_dir / "bench_validation.json")
    pass_t1 = validation.get("pass_t1") if validation else None

    last_modified = None
    for candidate in (run_dir / "checkpoint.json", run_dir / "manifest.json"):
        if candidate.exists():
            mtime = candidate.stat().st_mtime
            last_modified = mtime if last_modified is None else max(last_modified, mtime)

    return RunRecord(
        out_dir=str(run_dir),
        test=(manifest or {}).get("test"),
        completed_steps=completed,
        n_completed=len(completed),
        n_runs_in_manifest=len((manifest or {}).get("runs", [])) if manifest else None,
        pass_t1=pass_t1,
        last_modified=last_modified,
    )


def scan_history(data_dir: Path = DATA, test_id: str | None = None) -> list[RunRecord]:
    """Scan every immediate subdirectory of data_dir for protocol-run output."""
    if not data_dir.exists():
        return []

    records = []
    for sub in sorted(data_dir.iterdir()):
        if not sub.is_dir():
            continue
        record = scan_run_dir(sub)
        if record is None:
            continue
        if test_id is not None and record.test != test_id:
            continue
        records.append(record)

    records.sort(key=lambda r: (r.last_modified or 0.0))
    return records


def render_table(records: list[RunRecord]) -> str:
    if not records:
        return "No protocol run history found."

    headers = ["test", "out_dir", "steps_done", "pass_t1", "runs_in_manifest"]
    rows = [
        [
            r.test or "?",
            r.out_dir,
            str(r.n_completed),
            "?" if r.pass_t1 is None else str(r.pass_t1),
            "?" if r.n_runs_in_manifest is None else str(r.n_runs_in_manifest),
        ]
        for r in records
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def fmt_row(cells: list[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    lines = [fmt_row(headers), fmt_row(["-" * w for w in widths])]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Inspect checkpointed protocol-run history")
    p.add_argument("--data-dir", type=Path, default=DATA)
    p.add_argument("--test-id", type=str, default=None, help="filter to a single test id, e.g. T1")
    p.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = p.parse_args()

    records = scan_history(args.data_dir, test_id=args.test_id)

    if args.json:
        print(json.dumps([r.__dict__ for r in records], indent=2))
    else:
        print(render_table(records))


if __name__ == "__main__":
    main()
