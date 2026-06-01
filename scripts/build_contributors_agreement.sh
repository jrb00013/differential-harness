#!/usr/bin/env bash
# Build CHORUS-SGH-1 Contributors Agreement PDF via pdf-genesis (compile mode).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PDF_GENESIS="${PDF_GENESIS:-$HOME/Documents/pdf-genesis}"
OUT="$ROOT/docs/legal/CHORUS_SGH1_Contributors_Agreement.pdf"

if [[ ! -d "$PDF_GENESIS" ]]; then
  echo "Clone pdf-genesis to ~/Documents/pdf-genesis (or set PDF_GENESIS=...)" >&2
  exit 1
fi

python3 -m venv "$PDF_GENESIS/.venv" 2>/dev/null || true
# shellcheck disable=SC1091
source "$PDF_GENESIS/.venv/bin/activate"
pip install -q -e "$PDF_GENESIS"

python3 <<PY
from pathlib import Path
from pdf_genesis.repo.manifest import RepoManifest, CompileConfig
from pdf_genesis.repo.compile import compile_repo_pdf

root = Path("$ROOT").resolve()
repo = RepoManifest(
    root=root,
    title="CHORUS-SGH-1 Contributors Agreement",
    subtitle="differential-harness · IP, inventorship & credit allocation",
    author="Joseph Black",
    organization="CHORUS Research Program",
    footer="CHORUS-SGH-1 · Contributors Agreement · Not legal advice",
    compile=CompileConfig(
        include_globs=["docs/legal/CHORUS_SGH1_Contributors_Agreement.md"],
        exclude=[],
        figures_glob="nonexistent/*.png",
        exports=[],
        output="docs/legal/CHORUS_SGH1_Contributors_Agreement.pdf",
    ),
)
path = compile_repo_pdf(repo)
print(f"Wrote {path} ({path.stat().st_size:,} bytes)")
PY
