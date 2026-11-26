# Execution

The analysis requires Python 3.10+ and the standard library. Input paths are passed through `CONTROLS` and `COUNTS`; results are written to `OUTDIR`. The example tables contain constructed molecule counts.

## Local

```bash
bash scripts/run.sh
```

## AWS EC2

```bash
AWS_REGION=us-east-1 \
AWS_BUCKET=ctdna-research-artifacts \
AWS_SUBNET_ID=subnet-xxxxxxxx \
AWS_SECURITY_GROUP_ID=sg-xxxxxxxx \
AWS_INSTANCE_PROFILE=ctdna-loci-ec2 \
  bash deploy/aws/launch.sh
```

The launcher uses the Ubuntu 24.04 public SSM AMI parameter, uploads a source snapshot to S3, and starts a 40-GB EC2 instance. EC2 user data runs the analysis and uploads results under the same S3 prefix. The instance is not automatically terminated.

```bash
aws ec2 describe-instances --region us-east-1 --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[].Instances[].State.Name' --output text
aws s3 ls "s3://$AWS_BUCKET/$AWS_PREFIX/results/"
aws ec2 terminate-instances --region us-east-1 --instance-ids "$INSTANCE_ID"
```

The instance profile needs read/write access to the output prefix. `AWS_BUCKET`, `AWS_SUBNET_ID`, `AWS_SECURITY_GROUP_ID`, and `AWS_INSTANCE_PROFILE` are environment-specific identifiers. The example values in this section are syntactic identifiers, not deployed resources.

## Google Compute Engine

```bash
GCP_PROJECT=project-id \
GCP_ZONE=us-central1-a \
  bash deploy/gcp/launch.sh
```

The launcher creates an Ubuntu 24.04 VM, copies the project snapshot, executes the Python workflow over SSH, and retrieves outputs to `results/gcp-<instance>/`. The instance remains running after collection.

```bash
gcloud compute instances list --project "$GCP_PROJECT"
gcloud compute instances delete "$GCP_VM" --project "$GCP_PROJECT" \
  --zone "$GCP_ZONE" --quiet
```

## Slurm

```bash
sbatch --export=ALL,CONTROLS="$PWD/examples/controls.tsv",COUNTS="$PWD/examples/samples.tsv",OUTDIR="$PWD/results/slurm" \
  deploy/slurm/submit.sbatch
```

```bash
squeue --me
sacct -j "$SLURM_JOB_ID" --format=JobID,State,Elapsed,MaxRSS
```

SLURM uses Python directly; Apptainer is not required because this package has no external runtime dependencies. The input-count generation workflow may use separate UMI processing containers.

## Output

- `background.json`: locus-specific posterior parameters and aggregated control counts.
- `calls.json`: sample-level evidence statistics and QC status.
- `checksums.sha256`: SHA-256 hashes of input tables and output artifacts.

The AWS and GCP launchers are intended for straightforward VM execution and have not undergone provider-level integration testing. Cloud execution requires egress and applicable permissions.
