#!/bin/bash
# Galera Health Check Script
# Returns 0 if node is healthy and part of cluster

set -e

MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-}"

# Check if MariaDB is responding
if ! mariadb-admin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD}" --silent; then
    echo "MariaDB is not responding"
    exit 1
fi

# Check if node is part of primary component
CLUSTER_STATUS=$(mariadb -u root -p"${MYSQL_ROOT_PASSWORD}" -N -e "SHOW STATUS LIKE 'wsrep_cluster_status';" 2>/dev/null | awk '{print $2}')
if [ "$CLUSTER_STATUS" != "Primary" ]; then
    echo "Node is not part of primary component: $CLUSTER_STATUS"
    exit 1
fi

# Check if node is synced
LOCAL_STATE=$(mariadb -u root -p"${MYSQL_ROOT_PASSWORD}" -N -e "SHOW STATUS LIKE 'wsrep_local_state_comment';" 2>/dev/null | awk '{print $2}')
if [ "$LOCAL_STATE" != "Synced" ]; then
    echo "Node is not synced: $LOCAL_STATE"
    exit 1
fi

# Get cluster size
CLUSTER_SIZE=$(mariadb -u root -p"${MYSQL_ROOT_PASSWORD}" -N -e "SHOW STATUS LIKE 'wsrep_cluster_size';" 2>/dev/null | awk '{print $2}')
echo "Healthy: Cluster size $CLUSTER_SIZE, Status: $CLUSTER_STATUS, State: $LOCAL_STATE"
exit 0
