#!/usr/bin/env bash
# set -euo pipefail

###############################################################################
# Usage:  ./sync_s3_prefix_to_multiple_buckets.sh <SOURCE_PREFIX>
#
# <SOURCE_PREFIX> is required.  Include the trailing slash if you want one,
# or pass an empty string ("") to sync the whole bucket.
###############################################################################
# --------------------------------------------------------------------------- #


# DEST_PREFIX="folder1/"       # applied in every destination bucket

SOURCE_BUCKET="vendor-landing"
SOURCE_PREFIX="$1/"
DEST_PREFIX="$1/"

DEST_BUCKETS=(
  sandbox-snow
  dev-snow
  preprod-snow
  prod-snow
)

AWS_REGION="us-west-2"

# If you keep your IAM‑user keys in a named profile, uncomment:
# export AWS_PROFILE="my-sync-user"
# --------------------------------------------------------------------------- #

# Prerequisite checks
if ! command -v aws >/dev/null; then
  echo "The AWS CLI is not installed or not in PATH." >&2
  exit 1
fi

# Function to sync one bucket
sync_to_bucket() {
  local DEST_BUCKET="$1"

  echo "Syncing to $DEST_BUCKET (prefix: '$SOURCE_PREFIX' → '$DEST_PREFIX')"

  aws s3 sync \
    "s3://${SOURCE_BUCKET}/${SOURCE_PREFIX}" \
    "s3://${DEST_BUCKET}/${DEST_PREFIX}" \
    --acl bucket-owner-full-control \
    --region "$AWS_REGION" \
    --exact-timestamps

  # if [[ $? -eq 0 ]]; then
  #   echo "✅  Sync to $DEST_BUCKET completed"
  # else
  #   echo "❌  Sync to $DEST_BUCKET failed" >&2
  # fi
}

# EXIT_CODE=0
# for BUCKET in "${DEST_BUCKETS[@]}"; do
#   sync_to_bucket "$BUCKET" || EXIT_CODE=1
# done

# exit $EXIT_CODE


EXIT_CODE=0
for i in "${!DEST_BUCKETS[@]}"; do
  BUCKET="${DEST_BUCKETS[$i]}"
  sync_to_bucket "$BUCKET" || EXIT_CODE=1
  # Draw a line if not the last bucket
  if [[ $i -lt $((${#DEST_BUCKETS[@]} - 1)) ]]; then
    echo "======================================================"
  fi
done

exit $EXIT_CODE
