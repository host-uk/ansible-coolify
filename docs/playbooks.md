### Playbook Organization

Playbooks are located in `playbooks/` and follow a hierarchical structure to improve maintainability and discovery.

#### Core Coolify Playbooks (`playbooks/coolify/`)

- `create.yml`: Performs a fresh installation and initial configuration of a Coolify controller and its workers.
- `backup.yml`: Triggers a full backup of the Coolify state to the local machine.
- `restore.yml`: Restores a Coolify controller from a local backup.
- `reinstall.yml`: Orchestrates a safe reinstallation (Backup -> Uninstall -> Install -> Restore).
- `uninstall.yml`: Removes Coolify and its data from the host.

#### Resource Playbooks

These playbooks are specialized for managing individual resources via the Coolify API.

- **Applications** (`playbooks/coolify/application/`)
    - `create.yml`: Deploy a new application.
    - `restore.yml`: Restore an application from a known state.
    - `sync.yml`: Synchronize applications between two Coolify controllers (e.g., dev to prod).
    - `uninstall.yml`: Remove an application.

- **Databases** (`playbooks/coolify/database/`)
    - `create.yml`, `restore.yml`, `uninstall.yml`.

- **Services** (`playbooks/coolify/service/`)
    - `create.yml`, `restore.yml`, `uninstall.yml`.

- **Environment** (`playbooks/coolify/environment/`)
    - `clone.yml`: Clones an entire environment (apps, dbs, services) from one project/environment to another.
    - `empty.yml`: Deletes all resources within a specific environment.
    - `restore.yml`: Restores services from local state folder to Coolify API.
    - `move.yml`: Moves/clones services between environments with optional source deletion.
    - `sync_test.yml`: Demonstrates environment sync and comparison patterns.

- **Templates** (`playbooks/coolify/template/`)
    - `save.yml`: Save environment as reusable template.
    - `apply.yml`: Create services from saved template.
    - `list.yml`: List available templates.

- **Backup Detection** (`playbooks/coolify/`)
    - `backup_check.yml`: Compare local state against live API to detect NEW/MODIFIED/DELETED resources.

#### Running Playbooks

It is recommended to run playbooks via the `Makefile` to ensure correct inventory and environment variable handling.

Example:
```bash
# Deploy to development
make dev-deploy

# Backup production
make prod-backup
```
