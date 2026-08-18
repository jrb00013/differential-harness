"""Tests for the geometry-check integration in scripts/audit_openscad.py.

Covers both branches: openscad binary absent (explicit skip reason) and
present-but-failing render, using monkeypatched shutil.which/subprocess
so the test suite does not depend on openscad being installed.
"""

from __future__ import annotations

from pathlib import Path

import scripts.audit_openscad as audit


def test_geometry_check_reports_explicit_skip_when_openscad_absent(tmp_path):
    fake_scad = tmp_path / "part.scad"
    fake_scad.write_text("cube([1,1,1]);\n")
    result = audit.geometry_check(fake_scad, binary=None)
    assert result["watertight"] is None
    assert "skipped" in result["geometry_check"]
    assert "openscad" in result["geometry_check"]


def test_geometry_check_reports_failure_when_render_errors(tmp_path, monkeypatch):
    fake_scad = tmp_path / "broken.scad"
    fake_scad.write_text("this is not valid scad(((\n")

    class FakeProc:
        returncode = 1
        stderr = "ERROR: parse error"
        stdout = ""

    def fake_run(cmd, capture_output, text, timeout):
        return FakeProc()

    monkeypatch.setattr(audit.subprocess, "run", fake_run)
    result = audit.geometry_check(fake_scad, binary="/usr/bin/openscad")
    assert result["watertight"] is False
    assert "failed" in result["geometry_check"]


def test_openscad_binary_returns_none_when_not_on_path(monkeypatch):
    monkeypatch.setattr(audit.shutil, "which", lambda name: None)
    assert audit.openscad_binary() is None


def test_main_audit_export_marks_gap_when_openscad_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(audit, "openscad_binary", lambda: None)
    monkeypatch.setattr(audit, "EXPORT", tmp_path / "openscad_audit.json")
    audit.main()
    import json

    payload = json.loads((tmp_path / "openscad_audit.json").read_text())
    assert payload["openscad_binary_found"] is False
    assert payload["geometry_checked_count"] == 0
    assert all(p["geometry_check"].startswith("skipped") for p in payload["parts"])
