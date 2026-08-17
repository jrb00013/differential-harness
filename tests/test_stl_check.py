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

# Consistently, outward-facing (right-hand-rule) wound faces -- verified
# by hand so every shared edge is traversed in OPPOSITE directions by its
# two incident faces (a genuine closed, orientable manifold).
CLOSED_TETRAHEDRON = [
    (V0, V2, V1),  # face opposite V3
    (V0, V1, V3),  # face opposite V2
    (V0, V3, V2),  # face opposite V1
    (V1, V2, V3),  # face opposite V0
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


def test_inconsistent_winding_is_detected(tmp_path):
    # Take the closed tetrahedron and flip one face's winding order so
    # that its shared edge is traversed the SAME direction as its
    # neighbor instead of the opposite direction. Edge-pairing alone
    # still sees this as "closed" (2 triangles per edge), but it is not
    # a consistently-oriented manifold.
    flipped = list(CLOSED_TETRAHEDRON)
    a, b, c = flipped[0]
    flipped[0] = (c, b, a)  # reverse this face's winding direction
    path = tmp_path / "flipped.stl"
    write_binary_stl(path, flipped)
    report = check_stl_manifold(path)
    assert report.inconsistent_winding_edges > 0
    assert report.watertight is False
    assert report.ok is False


def test_consistently_wound_tetrahedron_has_no_winding_defects(tmp_path):
    path = tmp_path / "closed.stl"
    write_binary_stl(path, CLOSED_TETRAHEDRON)
    report = check_stl_manifold(path)
    assert report.inconsistent_winding_edges == 0


def test_ascii_stl_is_rejected_with_specific_error(tmp_path):
    path = tmp_path / "ascii.stl"
    path.write_text(
        "solid test\n"
        "facet normal 0 0 0\n outer loop\n  vertex 0 0 0\n  vertex 1 0 0\n  vertex 0 1 0\n"
        " endloop\nendfacet\nendsolid test\n",
        encoding="utf-8",
    )
    report = check_stl_manifold(path)
    assert report.ok is False
    assert any("ASCII" in e for e in report.errors)


def test_short_ascii_stl_is_also_rejected_as_ascii_not_generic_error(tmp_path):
    path = tmp_path / "tiny_ascii.stl"
    path.write_text("solid x\nendsolid x\n", encoding="utf-8")
    report = check_stl_manifold(path)
    assert any("ASCII" in e for e in report.errors)
