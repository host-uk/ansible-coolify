# PostgreSQL Patroni Cluster

Deploy and manage a PostgreSQL Patroni Cluster via Coolify Services API.

## Overview

Patroni is a template for PostgreSQL High Availability with etcd for distributed consensus. It provides automatic failover, switchover capabilities, and cluster management.

## Architecture

```
+-------------------+       +-------------------+
|  app-server-1.lan |<----->|  app-server-2.lan |
|  172.28.0.20      |       |  172.28.0.21      |
|  PATRONI PRIMARY  |       |  PATRONI REPLICA  |
|  ETCD NODE        |       |  ETCD NODE        |
+--------+----------+       +----------+--------+
         |    Streaming Replication   |
+--------+----------+       +----------+--------+
|  controller.lan   |<----->|  builder.lan      |
|  172.28.0.10      |       |  172.28.0.30      |
|  PATRONI REPLICA  |       |  PATRONI REPLICA  |
|  ETCD NODE        |       |  ETCD NODE        |
+-------------------+       +-------------------+
```

### Service Discovery

All nodes resolve `db.postgres.host.uk.com` to their local Patroni container:
- Applications connect to `db.postgres.host.uk.com:5432`
- Patroni REST API on port 8008
- etcd cluster on ports 2379/2380

## Quick Start

### Deploy Cluster

```bash
# Deploy full 4-node cluster
ansible-playbook -i inventory/ -l development playbooks/coolify/postgresql/deploy.yml

# Or use Makefile
make dev-postgresql-deploy
```

### Check Status

```bash
# Check cluster health
ansible-playbook -i inventory/ playbooks/coolify/postgresql/status.yml

# Or use Makefile
make dev-postgresql-status
```

### Backup

```bash
# Create pg_dump backup from replica
ansible-playbook -i inventory/ playbooks/coolify/postgresql/backup.yml

# Or use Makefile
make dev-postgresql-backup
```

### Switchover

```bash
# Planned switchover to different node
ansible-playbook -i inventory/ playbooks/coolify/postgresql/switchover.yml \
  -e target_node=app-server-2.lan

# Or use Makefile
make dev-postgresql-switchover
```

## Configuration

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `postgresql_hostname` | `db.postgres.host.uk.com` | Service discovery hostname |
| `postgresql_cluster_name` | `coolify_postgres` | Patroni cluster name |
| `postgresql_version` | `16` | PostgreSQL version |
| `postgresql_port` | `5432` | PostgreSQL port |
| `etcd_client_port` | `2379` | etcd client port |
| `etcd_peer_port` | `2380` | etcd peer port |
| `patroni_ttl` | `30` | Leader TTL in seconds |
| `patroni_loop_wait` | `10` | Patroni loop interval |
| `patroni_retry_timeout` | `10` | Retry timeout |

### Node Configuration

Override `postgresql_nodes` to customize your cluster:

```yaml
postgresql_nodes:
  - name: "postgres-node-1"
    host: "server1.example.com"
    ip: "10.0.1.10"
    role: "primary"

  - name: "postgres-node-2"
    host: "server2.example.com"
    ip: "10.0.1.11"
    role: "replica"

  - name: "postgres-node-3"
    host: "server3.example.com"
    ip: "10.0.1.12"
    role: "replica"
```

### Application Connection

For applications using PostgreSQL:

```yaml
DB_CONNECTION: pgsql
DB_HOST: db.postgres.host.uk.com
DB_PORT: 5432
DB_DATABASE: application
DB_USERNAME: app_user
DB_PASSWORD: <from state/postgresql/app_password.txt>
DATABASE_URL: postgres://app_user:password@db.postgres.host.uk.com:5432/application
```

## Maintenance

### Check Patroni Cluster Status

```bash
# Via REST API
curl http://localhost:8008/cluster | jq

# Using patronictl (inside container)
docker exec patroni-node-1 patronictl list
```

### Planned Switchover

```bash
# Switchover to specific member
docker exec patroni-node-1 patronictl switchover --master postgres-node-1 --candidate postgres-node-2

# Or via playbook
ansible-playbook -i inventory/ playbooks/coolify/postgresql/switchover.yml \
  -e target_node=postgres-node-2
```

### Reinitialize Failed Replica

```bash
# Inside container
docker exec patroni-node-3 patronictl reinit coolify_postgres postgres-node-3
```

## Monitoring

### Key Metrics

Check these Patroni/PostgreSQL indicators:

| Metric | Expected | Description |
|--------|----------|-------------|
| `state` | running | Patroni state |
| `role` | leader/replica | Node role |
| `timeline` | Same across nodes | WAL timeline |
| `lag` | < 1MB | Replication lag |

### Health Check Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Basic health |
| `GET /primary` | 200 if primary |
| `GET /replica` | 200 if replica |
| `GET /health` | Detailed health |
| `GET /cluster` | Cluster state |

### Example Health Check

```bash
# Check if node is primary
curl -s http://localhost:8008/primary && echo "Is Primary"

# Get cluster info
curl -s http://localhost:8008/cluster | jq '.members[] | {name, role, state, lag}'
```

## Troubleshooting

### Replica Not Streaming

1. Check network connectivity
2. Verify pg_hba.conf allows replication
3. Check replica logs: `docker logs patroni-node-X`
4. Verify replication slot exists

### No Leader Elected

1. Check etcd cluster health
2. Verify quorum (majority of etcd nodes up)
3. Check Patroni logs for errors
4. Verify network between nodes

### etcd Cluster Issues

```bash
# Check etcd health
docker exec etcd-node-1 etcdctl endpoint health

# List etcd members
docker exec etcd-node-1 etcdctl member list
```

### Split-Brain Prevention

Patroni uses etcd for consensus:
- etcd requires majority quorum (N/2 + 1)
- Only leader can accept writes
- Replicas automatically redirect to leader

### Recovery After Total Failure

```bash
# Bootstrap new cluster from backup
ansible-playbook -i inventory/ playbooks/coolify/postgresql/deploy.yml \
  -e restore_from_backup=true \
  -e backup_file=postgres_backup_20240101.sql.gz
```

## Files

| Path | Description |
|------|-------------|
| `playbooks/coolify/postgresql/deploy.yml` | Deploy full cluster |
| `playbooks/coolify/postgresql/status.yml` | Check cluster status |
| `playbooks/coolify/postgresql/backup.yml` | Create pg_dump backup |
| `playbooks/coolify/postgresql/switchover.yml` | Planned switchover |
| `playbooks/roles/coolify-postgresql/` | PostgreSQL Patroni role |
| `state/postgresql/` | Passwords and backups |
