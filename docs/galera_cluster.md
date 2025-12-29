# MariaDB Galera Cluster

Deploy and manage a MariaDB Galera Cluster via Coolify Services API.

## Overview

Galera Cluster provides synchronous multi-master replication for MariaDB. All nodes can accept read and write operations, with automatic failover and data consistency guarantees.

## Architecture

```
+-------------------+       +-------------------+
|  app-server-1.lan |<----->|  app-server-2.lan |
|  172.28.0.20      |       |  172.28.0.21      |
|  PRIMARY WRITE    |       |  PRIMARY WRITE    |
+--------+----------+       +----------+--------+
         |    Galera Sync Ring         |
+--------+----------+       +----------+--------+
|  controller.lan   |<----->|  builder.lan      |
|  172.28.0.10      |       |  172.28.0.30      |
|  READ REPLICA     |       |  READ REPLICA     |
+-------------------+       +-------------------+
```

### Service Discovery

All nodes resolve `db.host.uk.com` to their local Galera container:
- Applications connect to `db.host.uk.com:3306`
- Connection automatically uses the local node
- If local node fails, applications can reconnect to any available node

## Quick Start

### Deploy Cluster

```bash
# Deploy full 4-node cluster
ansible-playbook -i inventory/ -l development playbooks/coolify/galera/deploy.yml
```

### Check Status

```bash
# Basic status
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml

# With wsrep details
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml -e check_wsrep=true
```

### Backup

```bash
# Backup from slave node (default)
ansible-playbook -i inventory/ playbooks/coolify/galera/backup.yml

# Backup from specific node
ansible-playbook -i inventory/ playbooks/coolify/galera/backup.yml -e backup_node=app-server-2.lan
```

### Restore

```bash
# List available backups
ls -la state/galera/backups/

# Restore (requires confirmation)
ansible-playbook -i inventory/ playbooks/coolify/galera/restore.yml \
  -e backup_file=galera_backup_20240101T120000.sql.gz \
  -e confirm_restore=true
```

## Configuration

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `galera_hostname` | `db.host.uk.com` | Service discovery hostname |
| `galera_cluster_name` | `coolify_galera` | Cluster identifier |
| `galera_mariadb_version` | `11.4` | MariaDB version |
| `galera_port` | `3306` | MySQL port |
| `galera_memory_limit` | `2g` | Container memory limit |
| `galera_cpu_limit` | `2` | Container CPU limit |

### Node Configuration

Override `galera_nodes` to customize your cluster:

```yaml
galera_nodes:
  - name: "galera-node-1"
    host: "server1.example.com"
    ip: "10.0.1.10"
    role: "master"

  - name: "galera-node-2"
    host: "server2.example.com"
    ip: "10.0.1.11"
    role: "master"

  - name: "galera-node-3"
    host: "server3.example.com"
    ip: "10.0.1.12"
    role: "slave"
```

### Application Connection

Applications should use:

```yaml
DB_CONNECTION: mysql
DB_HOST: db.host.uk.com
DB_PORT: 3306
DB_DATABASE: application
DB_USERNAME: app_user
DB_PASSWORD: <from state/galera/app_password.txt>
```

## Maintenance

### Rolling Upgrade

```bash
ansible-playbook -i inventory/ playbooks/coolify/galera/maintenance/rolling_upgrade.yml \
  -e new_version=11.5
```

### Recover Failed Node

```bash
# Single node recovery
ansible-playbook -i inventory/ playbooks/coolify/galera/recover.yml \
  -e recover_node=app-server-1.lan
```

### Full Cluster Recovery

Only use this after total cluster failure:

```bash
ansible-playbook -i inventory/ playbooks/coolify/galera/recover.yml \
  -e bootstrap_node=app-server-2.lan \
  -e force_bootstrap=true
```

## Monitoring

### Key Metrics

Check these wsrep status variables:

| Variable | Expected | Description |
|----------|----------|-------------|
| `wsrep_cluster_size` | 4 | Number of nodes in cluster |
| `wsrep_cluster_status` | Primary | Node is part of primary component |
| `wsrep_local_state_comment` | Synced | Node is synchronized |
| `wsrep_ready` | ON | Node accepts queries |

### Health Check Query

```sql
SHOW STATUS LIKE 'wsrep_%';
```

## Troubleshooting

### Node Won't Join Cluster

1. Check wsrep status: `-e check_wsrep=true`
2. Verify network connectivity between nodes
3. Check Galera ports (4567, 4568, 4444)
4. Review container logs: `docker logs galera-node-X`

### Split-Brain Recovery

1. Identify primary partition: `wsrep_cluster_status = Primary`
2. Stop non-primary nodes
3. Restart from primary partition

### SST Timeout

For large databases, increase timeouts:

```yaml
galera_sst_timeout: 3600  # 1 hour
```

## Files

| Path | Description |
|------|-------------|
| `playbooks/coolify/galera/deploy.yml` | Deploy full cluster |
| `playbooks/coolify/galera/status.yml` | Check cluster status |
| `playbooks/coolify/galera/recover.yml` | Node/cluster recovery |
| `playbooks/coolify/galera/backup.yml` | Create backup |
| `playbooks/coolify/galera/restore.yml` | Restore from backup |
| `playbooks/roles/coolify-galera/` | Galera role |
| `state/galera/` | Passwords and backups |
