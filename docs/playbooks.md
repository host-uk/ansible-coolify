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

- **Galera Cluster** (`playbooks/coolify/galera/`)
    - `deploy.yml`: Deploy full 4-node MariaDB Galera cluster via Coolify Services.
    - `status.yml`: Check cluster health and wsrep status.
    - `recover.yml`: Recover failed nodes or bootstrap from total failure.
    - `backup.yml`: Create cluster backup using mariadb-dump.
    - `restore.yml`: Restore cluster from backup.
    - `maintenance/rolling_upgrade.yml`: Rolling MariaDB version upgrade.

- **Redis Sentinel Cluster** (`playbooks/coolify/redis/`)
    - `deploy.yml`: Deploy Redis Sentinel cluster with automatic failover.
    - `status.yml`: Check cluster health and replication status.
    - `backup.yml`: Create RDB snapshot backup.
    - `failover.yml`: Trigger manual Sentinel failover.

- **PostgreSQL Patroni Cluster** (`playbooks/coolify/postgresql/`)
    - `deploy.yml`: Deploy PostgreSQL Patroni cluster with etcd.
    - `status.yml`: Check cluster health and leader status.
    - `backup.yml`: Create pg_dump backup from replica.
    - `switchover.yml`: Planned switchover to different node.

- **One-Click Apps** (`playbooks/coolify/oneclick/`)
    - `deploy.yml`: Deploy one-click app with auto-detected database configuration.
    - `list.yml`: List available one-click apps with database requirements.
    - `detect.yml`: Detect database requirements for a service type.

- **Cluster Orchestration** (`playbooks/coolify/cluster/`)
    - `deploy.yml`: Deploy complete shared infrastructure (Galera + Redis + PostgreSQL).
    - `status.yml`: Check status of all clusters.
    - `backup.yml`: Backup all clusters.

#### Running Playbooks

It is recommended to run playbooks via the `Makefile` to ensure correct inventory and environment variable handling.

Example:
```bash
# Deploy to development
make dev-deploy

# Backup production
make prod-backup
```
