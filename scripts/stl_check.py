#!/usr/bin/env python3
"""Pure-python binary STL sanity/manifold checker.

No external mesh library dependency (numpy-stl is not in
pyproject.toml and we do not want to add a heavy dependency just for a
watertightness gate). Reads the binary STL triangle list directly with
`struct` and checks:

  * triangle_count > 0
  * no degenerate triangles (zero-area, i.e. two or more coincident
    vertices)
  * watertightness via edge-pairing: in a closed (manifold) mesh, every
    undirected edge is shared by exactly two triangles. An open edge
    (shared by only one triangle) means the mesh has a hole/gap; an
    edge shared by more than two triangles means non-manifold geometry.

This is a real, if intentionally lightweight, watertightness check --
it will catch the overwhelming majority of "this STL is not
3D-printable" defects (open shells, missing faces, degenerate
triangles) without requiring any external tooling beyond what
`openscad --export-format=binstl` itself produces.
"""

from __future__ import annotations

import struct
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

VERTEX_ROUND_NDIGITS = 6  # merge vertices within ~1e-6 units to dedupe FP noise


@dataclass
class StlMeshReport:
    triangle_count: int
    degenerate_triangles: int
    open_edges: int
    non_manifold_edges: int
    watertight: bool
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.triangle_count > 0 and self.degenerate_triangles == 0 and self.watertight and not self.errors


def _read_binary_stl_triangles(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    """Return a list of triangles, each a 3-tuple of (x, y, z) vertex tuples."""
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"file too small to be a binary STL: {path}")

    n_tri = struct.unpack_from("<I", data, 80)[0]
    expected_len = 84 + n_tri * 50
    if len(data) < expected_len:
        raise ValueError(
            f"binary STL truncated: header claims {n_tri} triangles "
            f"({expected_len} bytes) but file is {len(data)} bytes"
        )

    triangles = []
    offset = 84
    for _ in range(n_tri):
        # 12 bytes normal (skipped) + 3 * 12 bytes vertices + 2 bytes attr
        v1 = struct.unpack_from("<3f", data, offset + 12)
        v2 = struct.unpack_from("<3f", data, offset + 24)
        v3 = struct.unpack_from("<3f", data, offset + 36)
        triangles.append((v1, v2, v3))
        offset += 50
    return triangles


def _round_vertex(v: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(round(c, VERTEX_ROUND_NDIGITS) for c in v)


def check_stl_manifold(path: Path) -> StlMeshReport:
    """Load a binary STL and evaluate watertightness/degeneracy.

    Text-format ("ASCII") STL is not handled here; openscad's
    `--export-format=binstl` always produces binary STL, which is what
    this checker targets.
    """
    errors: list[str] = []
    try:
        triangles = _read_binary_stl_triangles(path)
    except ValueError as exc:
        return StlMeshReport(
            triangle_count=0,
            degenerate_triangles=0,
            open_edges=0,
            non_manifold_edges=0,
            watertight=False,
            errors=[str(exc)],
        )

    degenerate = 0
    edge_counts: Counter[tuple[tuple[float, float, float], tuple[float, float, float]]] = Counter()

    for tri in triangles:
        verts = [_round_vertex(v) for v in tri]
        if verts[0] == verts[1] or verts[1] == verts[2] or verts[0] == verts[2]:
            degenerate += 1
            continue
        for a, b in ((verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])):
            edge = tuple(sorted((a, b)))
            edge_counts[edge] += 1

    open_edges = sum(1 for c in edge_counts.values() if c == 1)
    non_manifold_edges = sum(1 for c in edge_counts.values() if c > 2)
    watertight = open_edges == 0 and non_manifold_edges == 0 and len(triangles) > 0

    return StlMeshReport(
        triangle_count=len(triangles),
        degenerate_triangles=degenerate,
        open_edges=open_edges,
        non_manifold_edges=non_manifold_edges,
        watertight=watertight,
        errors=errors,
    )


def write_binary_stl(path: Path, triangles: list[tuple[tuple[float, float, float], ...]]) -> None:
    """Write a minimal binary STL. Used by tests to build synthetic fixtures."""
    with path.open("wb") as f:
        f.write(b"\x00" * 80)
        f.write(struct.pack("<I", len(triangles)))
        for tri in triangles:
            f.write(struct.pack("<3f", 0.0, 0.0, 0.0))  # normal (unused by checker)
            for v in tri:
                f.write(struct.pack("<3f", *v))
            f.write(struct.pack("<H", 0))
