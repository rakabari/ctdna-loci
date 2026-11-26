#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${AWS_BUCKET:?AWS_BUCKET is required}"
: "${AWS_SUBNET_ID:?AWS_SUBNET_ID is required}"
: "${AWS_SECURITY_GROUP_ID:?AWS_SECURITY_GROUP_ID is required}"
: "${AWS_INSTANCE_PROFILE:?AWS_INSTANCE_PROFILE is required}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_INSTANCE_TYPE="${AWS_INSTANCE_TYPE:-t3.large}"
PREFIX="${AWS_PREFIX:-ctdna-loci/$(date -u +%Y%m%dT%H%M%SZ)}"
ARCHIVE="$(mktemp --suffix=.zip)"
USER_DATA="$(mktemp)"
trap 'rm -f "$ARCHIVE" "$USER_DATA"' EXIT
(
  cd "$ROOT"
  python3 - "$ARCHIVE" <<'PY'
import sys, zipfile
from pathlib import Path
out = Path(sys.argv[1])
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
    for folder in ('ctdna_loci', 'scripts', 'examples'):
        for file in sorted(Path(folder).rglob('*')):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file)
PY
)
aws --region "$AWS_REGION" s3 cp "$ARCHIVE" "s3://${AWS_BUCKET}/${PREFIX}/source.zip"
AMI_ID="$(aws --region "$AWS_REGION" ssm get-parameter --name \
  /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query 'Parameter.Value' --output text)"
{
  printf '#!/usr/bin/env bash\nset -euo pipefail\n'
  printf 'CTDNA_BUCKET=%q\nCTDNA_PREFIX=%q\n' "$AWS_BUCKET" "$PREFIX"
  tail -n +2 "$ROOT/deploy/aws/bootstrap.sh"
} > "$USER_DATA"
INSTANCE_ID="$(aws --region "$AWS_REGION" ec2 run-instances \
  --image-id "$AMI_ID" --instance-type "$AWS_INSTANCE_TYPE" --count 1 \
  --subnet-id "$AWS_SUBNET_ID" --security-group-ids "$AWS_SECURITY_GROUP_ID" \
  --iam-instance-profile "Name=$AWS_INSTANCE_PROFILE" \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":40,"VolumeType":"gp3"}}]' \
  --user-data "file://$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=ctdna-loci}]" \
  --query 'Instances[0].InstanceId' --output text)"
printf 'instance_id=%s\nregion=%s\noutput=s3://%s/%s/results/\n' \
  "$INSTANCE_ID" "$AWS_REGION" "$AWS_BUCKET" "$PREFIX"
