#!/bin/sh
# Redis Sentinel health check script

# Check if redis-cli is available
if ! command -v redis-cli >/dev/null 2>&1; then
    echo "redis-cli not found"
    exit 1
fi

# Check Redis server (if running)
if [ -n "${REDIS_PORT:-}" ]; then
    if ! redis-cli -p "${REDIS_PORT:-6379}" -a "${REDIS_PASSWORD:-}" ping | grep -q PONG; then
        echo "Redis server ping failed"
        exit 1
    fi
fi

# Check Sentinel (if running)
if [ -n "${SENTINEL_PORT:-}" ]; then
    if ! redis-cli -p "${SENTINEL_PORT:-26379}" ping | grep -q PONG; then
        echo "Sentinel ping failed"
        exit 1
    fi
fi

echo "Health check passed"
exit 0
