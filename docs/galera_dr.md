# Galera Cluster Disaster Recovery

Emergency procedures for Galera cluster failures.

## Quick Reference

| Scenario | Command |
|----------|---------|
| Single node down | `ansible-playbook playbooks/coolify/galera/recover.yml -e recover_node=<host>` |
| Cluster status | `ansible-playbook playbooks/coolify/galera/status.yml -e check_wsrep=true` |
| Full cluster failure | `ansible-playbook playbooks/coolify/galera/recover.yml -e bootstrap_node=<host> -e force_bootstrap=true` |
| Create backup | `ansible-playbook playbooks/coolify/galera/backup.yml` |
| Restore backup | `ansible-playbook playbooks/coolify/galera/restore.yml -e backup_file=<file> -e confirm_restore=true` |

## Scenario 1: Single Node Failure

**Symptoms:**
- One node's service is stopped or unhealthy
- Cluster continues operating with N-1 nodes
- `wsrep_cluster_size` shows reduced count

**Recovery:**

```bash
# 1. Check cluster status
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml

# 2. Identify failed node
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml -e check_wsrep=true

# 3. Recover the node
ansible-playbook -i inventory/ playbooks/coolify/galera/recover.yml \
  -e recover_node=app-server-1.lan

# 4. Verify cluster size restored
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml
```

**Expected outcome:**
- Node restarts and performs IST (Incremental State Transfer)
- Node syncs missed transactions
- Cluster size returns to expected value

## Scenario 2: Network Partition (Split-Brain)

**Symptoms:**
- Cluster splits into multiple partitions
- Some nodes show `wsrep_cluster_status = Non-Primary`
- Write operations fail on non-primary nodes

**Recovery:**

```bash
# 1. Identify which partition has quorum (Primary status)
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml -e check_wsrep=true

# 2. Look for nodes with wsrep_cluster_status = Primary
# These are the "safe" nodes with latest data

# 3. Stop non-primary nodes via Coolify API or directly
# (Let the primary partition continue operating)

# 4. Fix network issue

# 5. Restart non-primary nodes one at a time
ansible-playbook -i inventory/ playbooks/coolify/galera/recover.yml \
  -e recover_node=<non-primary-host>
```

**Prevention:**
- Use odd number of nodes (3, 5) for clear quorum
- Consider arbitrator node (garbd) for even-node clusters

## Scenario 3: Total Cluster Failure

**Symptoms:**
- All nodes are down
- No node has `wsrep_cluster_status = Primary`
- Cluster won't start normally

**Recovery:**

```bash
# 1. Check grastate.dat on all nodes to find most recent data
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml -e check_grastate=true

# 2. Find node with highest seqno (sequence number)
# This node has the most recent committed transactions

# 3. Bootstrap from that node
ansible-playbook -i inventory/ playbooks/coolify/galera/recover.yml \
  -e bootstrap_node=<node-with-highest-seqno> \
  -e force_bootstrap=true

# 4. Verify cluster is operational
ansible-playbook -i inventory/ playbooks/coolify/galera/status.yml
```

**Important:**
- ALWAYS bootstrap from node with highest seqno
- Bootstrapping from wrong node can cause data loss
- force_bootstrap is dangerous - only use for total failure

## Scenario 4: Data Corruption

**Symptoms:**
- Application errors suggesting data inconsistency
- Failed health checks
- Replication errors in logs

**Recovery:**

```bash
# 1. Stop all cluster nodes
# (via Coolify API or manually)

# 2. Identify last known good backup
ls -la state/galera/backups/

# 3. Restore from backup
ansible-playbook -i inventory/ playbooks/coolify/galera/restore.yml \
  -e backup_file=galera_backup_YYYYMMDDTHHMMSS.sql.gz \
  -e confirm_restore=true

# 4. Verify data integrity
```

## Backup Best Practices

### Backup Schedule

| Type | Frequency | Retention |
|------|-----------|-----------|
| Full backup | Daily | 7 days |
| Transaction logs | Continuous | 24 hours |

### Backup Commands

```bash
# Manual backup (runs on slave node by default)
ansible-playbook -i inventory/ playbooks/coolify/galera/backup.yml

# Backup from specific node
ansible-playbook -i inventory/ playbooks/coolify/galera/backup.yml \
  -e backup_node=app-server-2.lan

# Verify backup
ls -la state/galera/backups/
cat state/galera/backups/galera_backup_*.meta
```

### Backup Verification

Periodically test restores to a test environment:

```bash
# Create test restore
docker run -d --name restore-test \
  -e MYSQL_ROOT_PASSWORD=testpw \
  mariadb:11.4

# Wait for startup
sleep 30

# Restore backup
gunzip -c state/galera/backups/galera_backup_*.sql.gz | \
  docker exec -i restore-test mariadb -u root -ptestpw

# Verify data
docker exec restore-test mariadb -u root -ptestpw -e "SHOW DATABASES;"

# Cleanup
docker stop restore-test && docker rm restore-test
```

## Monitoring Alerts

Set up alerts for:

| Condition | Severity | Action |
|-----------|----------|--------|
| `wsrep_cluster_size < expected` | Critical | Investigate failed node |
| `wsrep_cluster_status != Primary` | Critical | Check for split-brain |
| `wsrep_local_state_comment != Synced` | Warning | Node syncing - monitor |
| `wsrep_ready = OFF` | Critical | Node not accepting queries |
| Backup older than 24h | Warning | Check backup job |

## Emergency Contacts

Document your escalation path:

1. **On-call engineer**: Check status, attempt node recovery
2. **Database administrator**: Split-brain, data corruption
3. **Management**: Data loss, extended outage

## Post-Incident

After any incident:

1. Document what happened
2. Update runbooks if needed
3. Review monitoring/alerting gaps
4. Consider preventive measures
