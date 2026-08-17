"""Tests for scripts/stl_check.py's pure-python binary STL manifold checker.

Uses hand-built synthetic STL fixtures (a closed tetrahedron vs. the
same tetrahedron missing one face) -- no CAD tooling required.
"""

from __future__ import annotations

from scripts.stl_check import check_stl_manifold, write_binary_stl

# A regular tetrahedron: 4 vertices, 4 triangular faces -> closed/manifold mesh.
V0 = (0.0, 0.0, 0.0)
V1 = (1.0, 0.0, 0.0)
V2 = (0.0, 1.0, 0.0)
V3 = (0.0, 0.0, 1.0)

CLOSED_TETRAHEDRON = [
    (V0, V1, V2),
    (V0, V1, V3),
    (V0, V2, V3),
    (V1, V2, V3),
]


def test_closed_tetrahedron_is_watertight(tmp_path):
    path = tmp_path / "closed.stl"
    write_binary_stl(path, CLOSED_TETRAHEDRON)
    report = check_stl_manifold(path)
    assert report.triangle_count == 4
    assert report.degenerate_triangles == 0
    assert report.open_edges == 0
    assert report.watertight is True
    assert report.ok is True


def test_open_shell_missing_one_face_is_not_watertight(tmp_path):
    open_shell = CLOSED_TETRAHEDRON[:3]  # drop the last face -> one open boundary
    path = tmp_path / "open.stl"
    write_binary_stl(path, open_shell)
    report = check_stl_manifold(path)
    assert report.triangle_count == 3
    assert report.open_edges > 0
    assert report.watertight is False
    assert report.ok is False


def test_degenerate_triangle_is_detected(tmp_path):
    degenerate = [(V0, V0, V1)]  # zero-area, coincident vertices
    path = tmp_path / "degenerate.stl"
    write_binary_stl(path, degenerate)
    report = check_stl_manifold(path)
    assert report.degenerate_triangles == 1
    assert report.ok is False


def test_truncated_file_reports_error_not_crash(tmp_path):
    path = tmp_path / "truncated.stl"
    path.write_bytes(b"\x00" * 10)
    report = check_stl_manifold(path)
    assert report.errors
    assert report.ok is False


def test_empty_mesh_is_not_ok(tmp_path):
    path = tmp_path / "empty.stl"
    write_binary_stl(path, [])
    report = check_stl_manifold(path)
    assert report.triangle_count == 0
    assert report.ok is False
