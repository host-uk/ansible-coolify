# Shared Infrastructure Platform

Deploy and manage a complete shared infrastructure stack for Coolify applications.

## Overview

The Shared Infrastructure Platform provides high-availability database and caching services that can be shared across all applications in a Coolify cluster:

- **MariaDB Galera Cluster**: Multi-master MySQL replication
- **Redis Sentinel Cluster**: High-availability caching with automatic failover
- **PostgreSQL Patroni Cluster**: Automatic failover PostgreSQL with etcd
- **One-Click App Deployment**: Automatic database detection and configuration

## Architecture

```
4-Node Minimum Cluster:
+-------------------+       +-------------------+
|  app-server-1     |<----->|  app-server-2     |
|  [Galera Master]  |       |  [Galera Master]  |
|  [Redis Master]   |       |  [Redis Replica]  |
|  [Patroni Primary]|       |  [Patroni Replica]|
+-------------------+       +-------------------+
         |                           |
+-------------------+       +-------------------+
|  controller       |<----->|  builder          |
|  [Galera Slave]   |       |  [Galera Slave]   |
|  [Redis Replica]  |       |  [Redis Sentinel] |
|  [Patroni Replica]|       |  [Patroni Replica]|
+-------------------+       +-------------------+

Service Discovery Hostnames (each resolves to local node):
- db.host.uk.com        -> MariaDB Galera (port 3306)
- cache.host.uk.com     -> Redis Sentinel (port 6379)
- db.postgres.host.uk.com -> PostgreSQL Patroni (port 5432)
```

## Quick Start

### Deploy Complete Stack

```bash
# Deploy all shared infrastructure (Galera + Redis + PostgreSQL)
make dev-cluster-deploy

# Check status of all clusters
make dev-cluster-status

# Backup all clusters
make dev-cluster-backup
```

### Deploy Individual Components

```bash
# Deploy only Galera
make dev-galera-deploy

# Deploy only Redis Sentinel
make dev-redis-deploy

# Deploy only PostgreSQL Patroni
make dev-postgresql-deploy
```

### Deploy Applications

```bash
# Deploy Chatwoot (auto-configures PostgreSQL + Redis)
make dev-oneclick-deploy APP=chatwoot NAME=support

# Deploy WordPress (auto-configures MariaDB)
make dev-oneclick-deploy APP=wordpress NAME=blog

# Deploy monitoring (no database needed)
make dev-oneclick-deploy APP=uptime-kuma NAME=monitoring
```

## Component Details

### MariaDB Galera Cluster

Synchronous multi-master replication for MySQL/MariaDB workloads.

| Feature | Value |
|---------|-------|
| Hostname | `db.host.uk.com` |
| Port | 3306 |
| Replication | Synchronous multi-master |
| Use Case | WordPress, Ghost, Nextcloud |

See [galera_cluster.md](galera_cluster.md) for details.

### Redis Sentinel Cluster

High-availability Redis with automatic failover.

| Feature | Value |
|---------|-------|
| Hostname | `cache.host.uk.com` |
| Port | 6379 (Redis), 26379 (Sentinel) |
| Replication | Async master-replica |
| Use Case | Session storage, caching, queues |

See [redis_sentinel.md](redis_sentinel.md) for details.

### PostgreSQL Patroni Cluster

Automatic failover PostgreSQL with etcd consensus.

| Feature | Value |
|---------|-------|
| Hostname | `db.postgres.host.uk.com` |
| Port | 5432 |
| Replication | Streaming with automatic failover |
| Use Case | Chatwoot, n8n, Grafana, Metabase |

See [postgresql_patroni.md](postgresql_patroni.md) for details.

### One-Click App Deployment

Automatic database detection for 100+ Coolify services.

| Feature | Value |
|---------|-------|
| PostgreSQL Apps | 40+ services |
| MariaDB Apps | 20+ services |
| Redis Required | 20+ services |
| Standalone | 50+ services |

See [oneclick_apps.md](oneclick_apps.md) for details.

## Service Discovery

All services use local hostname resolution via Docker `extra_hosts`:

```yaml
# In docker-compose template
extra_hosts:
  - "db.host.uk.com:${LOCAL_CONTAINER_IP}"
  - "cache.host.uk.com:${LOCAL_CONTAINER_IP}"
  - "db.postgres.host.uk.com:${LOCAL_CONTAINER_IP}"
```

Benefits:
- Applications always connect to local node
- Automatic failover handled by cluster
- No load balancer required
- Low latency (no network hops)

## State Management

All cluster state is stored locally:

```
state/
├── galera/
│   ├── root_password.txt
│   ├── app_password.txt
│   └── backups/
├── redis/
│   ├── password.txt
│   └── backups/
├── postgresql/
│   ├── superuser_password.txt
│   ├── replication_password.txt
│   └── backups/
└── oneclick/
    └── <app-name>/
```

## Makefile Targets

### Cluster Orchestration

| Target | Description |
|--------|-------------|
| `dev-cluster-deploy` | Deploy all shared infrastructure |
| `dev-cluster-status` | Check status of all clusters |
| `dev-cluster-backup` | Backup all clusters |
| `dev-cluster-test` | Run full integration tests |

### Individual Clusters

| Component | Deploy | Status | Backup | Other |
|-----------|--------|--------|--------|-------|
| Galera | `dev-galera-deploy` | `dev-galera-status` | `dev-galera-backup` | `dev-galera-recover` |
| Redis | `dev-redis-deploy` | `dev-redis-status` | `dev-redis-backup` | `dev-redis-failover` |
| PostgreSQL | `dev-postgresql-deploy` | `dev-postgresql-status` | `dev-postgresql-backup` | `dev-postgresql-switchover` |

### One-Click Apps

| Target | Description |
|--------|-------------|
| `dev-oneclick-deploy APP=X NAME=Y` | Deploy one-click app |
| `dev-oneclick-list` | List available apps |
| `dev-oneclick-detect APP=X` | Detect database requirements |

## Testing

### Run All Cluster Tests

```bash
# Run full test suite
make native-test-verify-all
```

### Individual Tests

| Test | Description |
|------|-------------|
| `native-test-redis-sentinel` | Redis Sentinel cluster tests |
| `native-test-postgresql-patroni` | PostgreSQL Patroni cluster tests |
| `native-test-oneclick-app` | One-Click App deployment tests |
| `native-test-full-cluster` | Full integration tests |
| `native-test-chatwoot-galera` | Chatwoot + Galera integration |

## Region/Environment Model

The shared infrastructure supports multi-region deployments:

- **4-node minimum** per region (scalable by adding nodes)
- **Projects** = Applications (e.g., "web-platform")
- **Environments** = Regions (e.g., "london.prod", "frankfurt.prod")
- **New region** = Deploy new cluster with same roles
- All apps in region share the same infrastructure

## Troubleshooting

### Check All Cluster Health

```bash
# Quick status check
make dev-cluster-status
```

### Cluster-Specific Issues

See individual documentation:
- [galera_cluster.md](galera_cluster.md#troubleshooting)
- [redis_sentinel.md](redis_sentinel.md#troubleshooting)
- [postgresql_patroni.md](postgresql_patroni.md#troubleshooting)

### Common Issues

| Issue | Check |
|-------|-------|
| App can't connect to DB | `make dev-cluster-status` |
| Slow queries | Check cluster replication lag |
| Failover not working | Verify quorum settings |
| Backup failed | Check disk space, permissions |

## Files

| Path | Description |
|------|-------------|
| `playbooks/coolify/cluster/` | Cluster orchestration playbooks |
| `playbooks/coolify/galera/` | Galera playbooks |
| `playbooks/coolify/redis/` | Redis Sentinel playbooks |
| `playbooks/coolify/postgresql/` | PostgreSQL Patroni playbooks |
| `playbooks/coolify/oneclick/` | One-Click App playbooks |
| `playbooks/roles/coolify-galera/` | Galera role |
| `playbooks/roles/coolify-redis-sentinel/` | Redis Sentinel role |
| `playbooks/roles/coolify-postgresql/` | PostgreSQL Patroni role |
| `playbooks/roles/coolify-oneclick-app/` | One-Click App role |
