# Redis Sentinel Cluster

Deploy and manage a Redis Sentinel Cluster via Coolify Services API.

## Overview

Redis Sentinel provides high availability for Redis through automatic failover. Sentinel monitors master and replica nodes, automatically promoting a replica to master if the current master fails.

## Architecture

```
+-------------------+       +-------------------+
|  app-server-1.lan |<----->|  app-server-2.lan |
|  172.28.0.20      |       |  172.28.0.21      |
|  REDIS MASTER     |       |  REDIS REPLICA    |
|  SENTINEL         |       |  SENTINEL         |
+--------+----------+       +----------+--------+
         |    Replication Stream      |
+--------+----------+       +----------+--------+
|  controller.lan   |<----->|  builder.lan      |
|  172.28.0.10      |       |  172.28.0.30      |
|  REDIS REPLICA    |       |  REDIS REPLICA    |
|  SENTINEL         |       |  SENTINEL         |
+-------------------+       +-------------------+
```

### Service Discovery

All nodes resolve `cache.host.uk.com` to their local Redis container:
- Applications connect to `cache.host.uk.com:6379`
- Sentinel available on port 26379
- Automatic failover with quorum-based consensus

## Quick Start

### Deploy Cluster

```bash
# Deploy full 4-node cluster
ansible-playbook -i inventory/ -l development playbooks/coolify/redis/deploy.yml

# Or use Makefile
make dev-redis-deploy
```

### Check Status

```bash
# Check cluster health
ansible-playbook -i inventory/ playbooks/coolify/redis/status.yml

# Or use Makefile
make dev-redis-status
```

### Backup

```bash
# Create RDB snapshot backup
ansible-playbook -i inventory/ playbooks/coolify/redis/backup.yml

# Or use Makefile
make dev-redis-backup
```

### Manual Failover

```bash
# Trigger Sentinel failover
ansible-playbook -i inventory/ playbooks/coolify/redis/failover.yml

# Or use Makefile
make dev-redis-failover
```

## Configuration

### Default Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `redis_hostname` | `cache.host.uk.com` | Service discovery hostname |
| `redis_cluster_name` | `coolify_redis` | Cluster identifier |
| `redis_port` | `6379` | Redis server port |
| `redis_sentinel_port` | `26379` | Sentinel port |
| `redis_sentinel_quorum` | `2` | Votes needed for failover |
| `redis_maxmemory` | `1gb` | Maximum memory limit |
| `redis_maxmemory_policy` | `allkeys-lru` | Eviction policy |

### Node Configuration

Override `redis_nodes` to customize your cluster:

```yaml
redis_nodes:
  - name: "redis-node-1"
    host: "server1.example.com"
    ip: "10.0.1.10"
    role: "master"

  - name: "redis-node-2"
    host: "server2.example.com"
    ip: "10.0.1.11"
    role: "replica"

  - name: "redis-node-3"
    host: "server3.example.com"
    ip: "10.0.1.12"
    role: "replica"
```

### Application Connection

For applications using Redis:

```yaml
REDIS_HOST: cache.host.uk.com
REDIS_PORT: 6379
REDIS_PASSWORD: <from state/redis/password.txt>
REDIS_URL: redis://:password@cache.host.uk.com:6379
```

For Sentinel-aware clients:

```yaml
REDIS_SENTINEL_HOST: cache.host.uk.com
REDIS_SENTINEL_PORT: 26379
REDIS_MASTER_NAME: coolify_redis
```

## Maintenance

### Check Sentinel Status

```bash
# From any node
redis-cli -p 26379 SENTINEL masters
redis-cli -p 26379 SENTINEL replicas coolify_redis
```

### Force Failover

```bash
# Trigger manual failover via Sentinel
redis-cli -p 26379 SENTINEL failover coolify_redis
```

### Add New Replica

New replicas are automatically discovered by Sentinel when they connect to the master.

## Monitoring

### Key Metrics

Check these Redis INFO fields:

| Field | Expected | Description |
|-------|----------|-------------|
| `role` | master/slave | Node role |
| `connected_slaves` | N-1 | Replicas connected to master |
| `master_link_status` | up | Replica connection to master |
| `sentinel_masters` | 1 | Masters monitored by Sentinel |

### Health Check Commands

```bash
# Redis health
redis-cli PING

# Replication info
redis-cli INFO replication

# Sentinel status
redis-cli -p 26379 SENTINEL master coolify_redis
```

## Troubleshooting

### Replica Not Syncing

1. Check network connectivity
2. Verify master is accepting connections
3. Check replica logs: `docker logs redis-node-X`
4. Verify password matches

### Sentinel Not Detecting Failover

1. Check quorum setting (`redis_sentinel_quorum`)
2. Verify Sentinel connectivity between nodes
3. Review Sentinel logs

### Split-Brain Prevention

Sentinel uses quorum voting to prevent split-brain:
- Minimum 3 Sentinel nodes recommended
- Quorum should be majority (N/2 + 1)

## Files

| Path | Description |
|------|-------------|
| `playbooks/coolify/redis/deploy.yml` | Deploy full cluster |
| `playbooks/coolify/redis/status.yml` | Check cluster status |
| `playbooks/coolify/redis/backup.yml` | Create RDB backup |
| `playbooks/coolify/redis/failover.yml` | Trigger failover |
| `playbooks/roles/coolify-redis-sentinel/` | Redis Sentinel role |
| `state/redis/` | Passwords and backups |
