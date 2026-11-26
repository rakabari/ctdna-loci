#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTROLS="${CONTROLS:-$ROOT/examples/controls.tsv}"
COUNTS="${COUNTS:-$ROOT/examples/samples.tsv}"
OUTDIR="${OUTDIR:-$ROOT/results}"
mkdir -p "$OUTDIR"
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m ctdna_loci.cli fit \
  --controls "$CONTROLS" --output "$OUTDIR/background.json"
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m ctdna_loci.cli call \
  --counts "$COUNTS" --background "$OUTDIR/background.json" \
  --output "$OUTDIR/calls.json"
sha256sum "$CONTROLS" "$COUNTS" "$OUTDIR/background.json" "$OUTDIR/calls.json" > "$OUTDIR/checksums.sha256"
