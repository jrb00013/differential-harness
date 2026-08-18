"""Tests for scripts/protocol_history.py using synthetic checkpoint/
manifest/bench_validation fixtures in a tmp directory (no real bench
runs required)."""

from __future__ import annotations

import json

from scripts.protocol_history import render_table, scan_history, scan_run_dir


def _make_run(tmp_path, name, *, test, completed_steps, runs=None, pass_t1=None):
    run_dir = tmp_path / name
    run_dir.mkdir()
    (run_dir / "checkpoint.json").write_text(
        json.dumps({"completed_steps": {s: "some/path.csv" for s in completed_steps}}),
        encoding="utf-8",
    )
    (run_dir / "manifest.json").write_text(
        json.dumps({"test": test, "out_dir": str(run_dir), "runs": runs or []}),
        encoding="utf-8",
    )
    if pass_t1 is not None:
        (run_dir / "bench_validation.json").write_text(
            json.dumps({"pass_t1": pass_t1}), encoding="utf-8"
        )
    return run_dir


def test_scan_run_dir_returns_none_for_unrelated_directory(tmp_path):
    other = tmp_path / "not_a_run"
    other.mkdir()
    (other / "readme.txt").write_text("hello", encoding="utf-8")
    assert scan_run_dir(other) is None


def test_scan_run_dir_reads_checkpoint_manifest_and_validation(tmp_path):
    run_dir = _make_run(
        tmp_path, "T1_20260101",
        test="T1", completed_steps=["T1.baseline", "T1.validate"], runs=["a.csv"], pass_t1=True,
    )
    record = scan_run_dir(run_dir)
    assert record is not None
    assert record.test == "T1"
    assert record.n_completed == 2
    assert record.completed_steps == ["T1.baseline", "T1.validate"]
    assert record.pass_t1 is True
    assert record.n_runs_in_manifest == 1


def test_scan_run_dir_handles_missing_validation_as_unknown(tmp_path):
    run_dir = _make_run(tmp_path, "T0_20260102", test="T0", completed_steps=["T0.leak"])
    record = scan_run_dir(run_dir)
    assert record.pass_t1 is None


def test_scan_history_filters_by_test_id(tmp_path):
    _make_run(tmp_path, "T0_run", test="T0", completed_steps=["T0.leak"])
    _make_run(tmp_path, "T1_run", test="T1", completed_steps=["T1.baseline"])
    (tmp_path / "unrelated").mkdir()

    all_records = scan_history(tmp_path)
    assert len(all_records) == 2

    t1_only = scan_history(tmp_path, test_id="T1")
    assert len(t1_only) == 1
    assert t1_only[0].test == "T1"


def test_scan_history_empty_dir_returns_empty_list(tmp_path):
    empty = tmp_path / "empty_data_dir"
    assert scan_history(empty) == []


def test_render_table_reports_no_history_message():
    assert "No protocol run history" in render_table([])


def test_render_table_includes_key_fields(tmp_path):
    run_dir = _make_run(
        tmp_path, "T1_20260103",
        test="T1", completed_steps=["T1.baseline"], runs=["a.csv"], pass_t1=False,
    )
    record = scan_run_dir(run_dir)
    table = render_table([record])
    assert "T1" in table
    assert "False" in table
    assert str(run_dir) in table
