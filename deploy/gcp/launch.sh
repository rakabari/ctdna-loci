#!/usr/bin/env bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${GCP_PROJECT:?GCP_PROJECT is required}"
GCP_ZONE="${GCP_ZONE:-us-central1-a}"
GCP_MACHINE_TYPE="${GCP_MACHINE_TYPE:-e2-standard-2}"
GCP_VM="${GCP_VM:-ctdna-loci-$(date -u +%Y%m%d-%H%M%S)}"
ARCHIVE="$(mktemp --suffix=.zip)"

trap 'rm -f "$ARCHIVE"' EXIT
(
  cd "$ROOT"
  python3 - "$ARCHIVE" <<'PY'
import sys, zipfile
from pathlib import Path
with zipfile.ZipFile(sys.argv[1], 'w', zipfile.ZIP_DEFLATED) as archive:
    for folder in ('ctdna_loci', 'scripts', 'examples'):
        for file in sorted(Path(folder).rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file)
PY
)

gcloud compute instances create "$GCP_VM" --project "$GCP_PROJECT" \
  --zone "$GCP_ZONE" --machine-type "$GCP_MACHINE_TYPE" \
  --image-family ubuntu-2404-lts-amd64 --image-project ubuntu-os-cloud \
  --boot-disk-size 40GB --boot-disk-type pd-balanced

gcloud compute scp "$ARCHIVE" "$GCP_VM:~/ctdna-source.zip" \
  --project "$GCP_PROJECT" --zone "$GCP_ZONE"
gcloud compute scp "$ROOT/deploy/gcp/run-remote.sh" "$GCP_VM:~/ctdna-run.sh" \
  --project "$GCP_PROJECT" --zone "$GCP_ZONE"
gcloud compute ssh "$GCP_VM" --project "$GCP_PROJECT" --zone "$GCP_ZONE" \
  --command 'bash ~/ctdna-run.sh'
  
mkdir -p "$ROOT/results/gcp-$GCP_VM"

gcloud compute scp --recurse "$GCP_VM:~/ctdna-loci/results/" \
  "$ROOT/results/gcp-$GCP_VM/" --project "$GCP_PROJECT" --zone "$GCP_ZONE"

printf 'instance=%s\nzone=%s\nresults=%s\n' "$GCP_VM" "$GCP_ZONE" "$ROOT/results/gcp-$GCP_VM"
