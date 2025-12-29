#!/bin/sh
# PostgreSQL Patroni health check script

# Check Patroni REST API
if [ -n "${PATRONI_PORT:-}" ]; then
    if ! curl -sf "http://localhost:${PATRONI_PORT:-8008}/health" > /dev/null; then
        echo "Patroni health check failed"
        exit 1
    fi
fi

# Check PostgreSQL connection
if [ -n "${PGPASSWORD:-}" ]; then
    if ! psql -U "${PGUSER:-postgres}" -c "SELECT 1;" > /dev/null 2>&1; then
        echo "PostgreSQL connection check failed"
        exit 1
    fi
fi

echo "Health check passed"
exit 0
