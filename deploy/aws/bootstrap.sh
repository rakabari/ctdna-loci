#!/usr/bin/env bash
set -euo pipefail
exec > >(tee -a /var/log/ctdna-loci.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 unzip awscli
mkdir -p /opt/ctdna-loci
aws s3 cp "s3://${CTDNA_BUCKET}/${CTDNA_PREFIX}/source.zip" /tmp/ctdna-source.zip
unzip -q /tmp/ctdna-source.zip -d /opt/ctdna-loci
cd /opt/ctdna-loci
CONTROLS="/opt/ctdna-loci/examples/controls.tsv" \
COUNTS="/opt/ctdna-loci/examples/samples.tsv" \
OUTDIR="/opt/ctdna-loci/results" bash scripts/run.sh
aws s3 cp /opt/ctdna-loci/results/ "s3://${CTDNA_BUCKET}/${CTDNA_PREFIX}/results/" --recursive
