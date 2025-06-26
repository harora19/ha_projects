# S3 Bucket Sync Automation

This project provides an automated solution to synchronize files from a source AWS S3 bucket to multiple destination S3 buckets. The automation is designed to run on a schedule using GitLab CI, ensuring that the latest data is always available in the target buckets.

## Features

- Syncs a specified prefix (folder) or the entire contents from a source S3 bucket to multiple destination buckets.
- Uses AWS CLI for efficient and reliable data transfer.
- Runs as a scheduled job in GitLab CI for hands-free, regular synchronization.
- Supports custom prefixes for granular sync control.

## How It Works

1. The core logic is implemented in [`vndr_sync.sh`](vndr_sync.sh), a Bash script that:
   - Accepts a prefix as an argument.
   - Iterates over a list of destination buckets.
   - Uses `aws s3 sync` to copy files from the source to each destination bucket.
2. The process is orchestrated by GitLab CI using the configuration in [`.gitlab-ci.yml`](.gitlab-ci.yml).
   - Installs AWS CLI in the CI environment.
   - Runs the sync script with the desired prefix.

## Usage

### Manual Run

You can run the script locally if you have AWS CLI configured:

```sh
chmod +x [vndr_sync.sh](http://_vscodecontentref_/0)
[vndr_sync.sh](http://_vscodecontentref_/1) $vndr_pre_name