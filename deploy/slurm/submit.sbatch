#!/usr/bin/env bash
#SBATCH --job-name=ctdna-loci
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=ctdna-loci-%j.log

REPO="${REPO:-${SLURM_SUBMIT_DIR:-$PWD}}"
CONTROLS="${CONTROLS:-$REPO/examples/controls.tsv}"
COUNTS="${COUNTS:-$REPO/examples/samples.tsv}"
OUTDIR="${OUTDIR:-$REPO/results/${SLURM_JOB_ID}}"

export CONTROLS COUNTS OUTDIR

bash "$REPO/scripts/run.sh"
