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
  * winding consistency (round 2 addition): a mesh can be edge-paired
    "closed" (every undirected edge has exactly 2 incident triangles)
    yet still not be a true, orientable manifold if the two triangles
    sharing an edge both traverse it in the *same* direction instead of
    opposite directions. This produces a shell that looks watertight to
    a naive edge-count check but has inconsistent/flipped face normals
    -- a real defect class edge-pairing alone misses. Detected here via
    directed-edge counting.
  * ASCII-format STL rejection (round 2 addition): openscad's
    `--export-format=binstl` always produces binary STL, but a
    misconfigured export or hand-edited file could produce ASCII
    ("solid ... facet normal ...") STL instead, which this binary
    reader would otherwise misparse as garbage triangle data. The
    ASCII `solid` header is sniffed explicitly and reported as a
    distinct, specific error rather than a generic "too small"/garbled
    failure.

This is a real, if intentionally lightweight, watertightness check --
it will catch the overwhelming majority of "this STL is not
3D-printable" defects (open shells, missing faces, degenerate
triangles, inconsistent winding, wrong export format) without requiring
any external tooling beyond what `openscad --export-format=binstl`
itself produces.
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
    inconsistent_winding_edges: int
    watertight: bool
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            self.triangle_count > 0
            and self.degenerate_triangles == 0
            and self.watertight
            and self.inconsistent_winding_edges == 0
            and not self.errors
        )


def _looks_like_ascii_stl(data: bytes) -> bool:
    """Sniff for the ASCII STL text header ('solid ...', case-insensitive).

    Note the 80-byte binary STL header is also allowed (by the format
    spec) to start with the literal bytes "solid" for historical
    reasons, so this alone is not conclusive -- it is combined with a
    failed/mismatched binary-triangle-count parse by the caller before
    being reported as a genuine ASCII-format rejection.
    """
    head = data[:5].lower()
    return head == b"solid"


def _read_binary_stl_triangles(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    """Return a list of triangles, each a 3-tuple of (x, y, z) vertex tuples."""
    data = path.read_bytes()
    if len(data) < 84:
        if _looks_like_ascii_stl(data):
            raise ValueError(
                f"file appears to be ASCII-format STL, not binary: {path}. "
                "Re-export with `openscad --export-format=binstl`."
            )
        raise ValueError(f"file too small to be a binary STL: {path}")

    n_tri = struct.unpack_from("<I", data, 80)[0]
    expected_len = 84 + n_tri * 50
    if len(data) < expected_len:
        if _looks_like_ascii_stl(data):
            raise ValueError(
                f"file appears to be ASCII-format STL, not binary: {path}. "
                "Re-export with `openscad --export-format=binstl`."
            )
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
            inconsistent_winding_edges=0,
            watertight=False,
            errors=[str(exc)],
        )

    degenerate = 0
    edge_counts: Counter[tuple[tuple[float, float, float], tuple[float, float, float]]] = Counter()
    directed_edge_counts: Counter[tuple[tuple[float, float, float], tuple[float, float, float]]] = Counter()

    for tri in triangles:
        verts = [_round_vertex(v) for v in tri]
        if verts[0] == verts[1] or verts[1] == verts[2] or verts[0] == verts[2]:
            degenerate += 1
            continue
        for a, b in ((verts[0], verts[1]), (verts[1], verts[2]), (verts[2], verts[0])):
            edge = tuple(sorted((a, b)))
            edge_counts[edge] += 1
            directed_edge_counts[(a, b)] += 1

    open_edges = sum(1 for c in edge_counts.values() if c == 1)
    non_manifold_edges = sum(1 for c in edge_counts.values() if c > 2)

    # Winding consistency: for a properly-oriented closed edge (count == 2
    # in the undirected count), the two incident triangles should traverse
    # it in OPPOSITE directions -- i.e. directed (a,b) and (b,a) should
    # each appear once. If the same directed edge appears twice (both
    # triangles traverse a->b), the two faces are inconsistently wound
    # even though the undirected edge-pairing check alone would call this
    # "closed".
    inconsistent_winding = 0
    seen_undirected: set[tuple[tuple[float, float, float], tuple[float, float, float]]] = set()
    for (a, b), count in directed_edge_counts.items():
        edge = tuple(sorted((a, b)))
        if edge in seen_undirected:
            continue
        if edge_counts.get(edge, 0) != 2:
            continue  # not a simple 2-triangle edge; open/non-manifold cases already flagged
        seen_undirected.add(edge)
        forward = directed_edge_counts.get((a, b), 0)
        backward = directed_edge_counts.get((b, a), 0)
        if forward != 1 or backward != 1:
            inconsistent_winding += 1

    watertight = (
        open_edges == 0
        and non_manifold_edges == 0
        and inconsistent_winding == 0
        and len(triangles) > 0
    )

    return StlMeshReport(
        triangle_count=len(triangles),
        degenerate_triangles=degenerate,
        open_edges=open_edges,
        non_manifold_edges=non_manifold_edges,
        inconsistent_winding_edges=inconsistent_winding,
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
