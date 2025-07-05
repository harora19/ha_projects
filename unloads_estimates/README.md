# Redshift to S3 Load Testing Utility

This project is designed to perform load testing on AWS S3 buckets and AWS Redshift clusters. It uses multi-threading to unload (export) data from an AWS Redshift cluster and dump it into an S3 bucket. The source data is specified via a configurable table list, and credentials are securely managed using HashiCorp Vault.

> **Note:** Metrics evaluation and third-party monitoring tool configuration are out of scope for this repository.

## Features

- Multi-threaded data unload from AWS Redshift to S3
- Table list configurable via [`rs_tab_list.py`](rs_tab_list.py)
- Secure credential retrieval using HashiCorp Vault
- Dockerfile for containerized execution
- GitLab CI/CD integration

## Requirements

- Python 3.9+
- AWS Redshift cluster and S3 bucket access
- HashiCorp Vault for secrets management

Install Python dependencies:
```sh
pip install -r requirements.txt
```

## Usage

1. **Set required environment variables:**
   - `aws_access_key_id`
   - `aws_secret_access_key`
   - `VAULT_URL`
   - `VAULT_SECRET_ID`
   - `VAULT_APPROLE`
   - `SSL_URL`

2. **Run the script:**
   ```sh
   python unload.py <redshift_user>
   ```
   Example:
   ```sh
   python unload.py dw
   ```

3. **Table List:**
   - Edit [`rs_tab_list.py`](rs_tab_list.py) to specify the Redshift tables to unload.

## Docker

Build and run using Docker:
```sh
docker build -t redshift-unload .
docker run --env-file <your_env_file> redshift-unload python unload.py dw
```

## CI/CD

See [.gitlab-ci.yml](.gitlab-ci.yml) for GitLab pipeline configuration.

## License

See [LICENSE](LICENSE) (if applicable).

---
*Metrics evaluation and third-party monitoring tool configuration are not included in this repository.*