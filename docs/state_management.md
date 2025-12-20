### State Management

To ensure that infrastructure can be reconstructed and critical application data is never lost, this project implements a "State Store" pattern using the local directory `ansible/state`.

#### The `ansible/state` Directory

This directory is host-specific and is ignored by git to protect secrets and large binary dumps. It is structured as follows:

```text
ansible/state/
└── <inventory_hostname>/
    ├── .ssh/
    │   └── ssh_host_*         # Public and private host keys retrieved from the baremetal host (/etc/ssh and /root/.ssh)
    └── backups/
        └── coolify/
            ├── .env           # Coolify controller environment file
            ├── APP_KEY        # The encryption key for Coolify
            ├── coolify_db.dump # PostgreSQL dump of the Coolify database
            ├── coolify_ssh_keys.tar.gz # Archive of Coolify's managed SSH keys
            └── <key_name>.pub  # Public keys managed within the Coolify UI
    └── hetzner/
        ├── hcloud_server.json      # Full HCloud server configuration
        ├── hcloud_ssh_keys.json    # List of SSH keys in HCloud
        ├── hcloud_certificates.json # List of HCloud certificates
        └── robot_info.json         # Baremetal server configuration
```

#### Why we store state locally

1.  **Disaster Recovery**: If the controller host is destroyed, we have everything needed to restore the exact state on a new instance.
2.  **API Access**: The `ansible-token` is stored on the remote host but generated via Ansible, allowing subsequent runs to authenticate without manual intervention.
3.  **Key Management**: Coolify manages its own set of SSH keys for talking to workers. By backing these up locally, we ensure that worker connectivity is preserved after a restore.

#### Backup and Restore Workflow

1.  **Backup**: Run `make dev-backup`. This triggers a series of `ansible.builtin.fetch` tasks that pull state from the remote host to `ansible/state`.
2.  **S3 Remote Backup**: After the local backup is complete, the state directory is compressed, encrypted using the `hostuk` SSH key, and uploaded to the private **HostUK S3 Storage** (Hetzner Object Storage) for disaster recovery.
3.  **Restore**: Run `make dev-restore`. This pushes the local state back to a fresh instance and runs the installation script to "heal" the environment.

#### S3 Storage Configuration

This project distinguishes between two separate S3-compatible buckets, both hosted at Hetzner Object Storage:

1.  **HostUK Private Storage (`hostuk`)**: Used for encrypted infrastructure backups (State Store).
2.  **Coolify Public Storage (`host-uk`)**: Used for public application files (assets, uploads, etc.).

The configuration is primarily managed in `ansible/inventory/inventory.yml` under the `all.vars` section, allowing for environment-specific overrides:

**Private Storage (Infrastructure Backups):**
- `hostuk_s3_enabled`: Enable/disable S3 backup.
- `hostuk_s3_endpoint`: S3-compatible endpoint (e.g., `https://fsn1.your-objectstorage.com`).
- `hostuk_s3_bucket`: Destination bucket (`hostuk`).
- `hostuk_s3_path`: Base path within the bucket.
- `hostuk_backup_encryption_key_path`: Path to the SSH key used for encryption (defined in `roles/coolify/defaults/main.yml`).

**Public Storage (Application Files):**
- `coolify_s3_app_enabled`: Enable/disable app storage configuration.
- `coolify_s3_app_endpoint`: S3-compatible endpoint.
- `coolify_s3_app_bucket`: Destination bucket (`host-uk`).
- `coolify_s3_app_region`: S3 region (e.g., `fsn1`).

Credentials should be provided via environment variables:
- `HETZNER_S3_ACCESS_KEY` (Private)
- `HETZNER_S3_SECRET_KEY` (Private)
- `HETZNER_S3_APP_ACCESS_KEY` (Public - falls back to Private if not set)
- `HETZNER_S3_APP_SECRET_KEY` (Public - falls back to Private if not set)
