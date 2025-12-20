### State Management

To ensure that infrastructure can be reconstructed and critical application data is never lost, this project implements a "State Store" pattern using the local directory `ansible/state`.

#### The `ansible/state` Directory

This directory is host-specific and is ignored by git to protect secrets and large binary dumps. It is structured as follows:

```text
ansible/state/
└── <inventory_hostname>/
    ├── .ssh/
    │   └── ssh_host_*.pub     # Public host keys retrieved from the baremetal host (/etc/ssh)
    └── backups/
        └── coolify/
            ├── .env           # Coolify controller environment file
            ├── APP_KEY        # The encryption key for Coolify
            ├── coolify_db.dump # PostgreSQL dump of the Coolify database
            ├── coolify_ssh_keys.tar.gz # Archive of Coolify's managed SSH keys
            └── <key_name>.pub  # Public keys managed within the Coolify UI
```

#### Why we store state locally

1.  **Disaster Recovery**: If the controller host is destroyed, we have everything needed to restore the exact state on a new instance.
2.  **API Access**: The `ansible-token` is stored on the remote host but generated via Ansible, allowing subsequent runs to authenticate without manual intervention.
3.  **Key Management**: Coolify manages its own set of SSH keys for talking to workers. By backing these up locally, we ensure that worker connectivity is preserved after a restore.

#### Backup and Restore Workflow

1.  **Backup**: Run `make dev-backup`. This triggers a series of `ansible.builtin.fetch` tasks that pull state from the remote host to `ansible/state`.
2.  **Restore**: Run `make dev-restore`. This pushes the local state back to a fresh instance and runs the installation script to "heal" the environment.
