#!/bin/bash
# Cleanup script for Docker dev test environment
# Removes all test artifacts including containers, networks, and SSH keys

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${RED}[WARN]${NC} $1"; }

log_info "Starting cleanup..."

cd "$PROJECT_ROOT"

# Stop and remove test containers
log_info "Removing test containers..."
docker compose -f ./docker-test/docker-compose.yml down -v 2>/dev/null || true

# Remove test directories
log_info "Removing test directories..."
rm -rf ./docker-test ./docker-test-logs 2>/dev/null || true

# Remove test SSH keys
log_info "Removing test SSH keys..."
rm -f ~/.ssh/test-*.lan ~/.ssh/test-*.lan.pub 2>/dev/null || true

# Remove orphan networks
log_info "Cleaning up orphan networks..."
docker network prune -f 2>/dev/null || true

# Remove dangling images (optional)
if [[ "${PRUNE_IMAGES:-false}" == "true" ]]; then
    log_info "Pruning dangling images..."
    docker image prune -f 2>/dev/null || true
fi

log_info "Cleanup complete!"
