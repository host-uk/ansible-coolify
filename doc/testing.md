# Docker Development Testing

This document describes the test suite for the `docker_dev` role and Coolify API integration.

## Overview

The test suite validates the complete Docker development environment workflow, from container creation through Coolify installation and API-driven resource management.

## Test Structure

Tests are located in `tests/docker-dev/` and organized by functionality:

| Test File | Description |
|-----------|-------------|
| `test_01_container_lifecycle.yml` | Container creation, health checks, networking, idempotency |
| `test_02_ssh_connectivity.yml` | SSH key generation, permissions, container connectivity |
| `test_03_makefile_targets.yml` | All `make docker-dev-*` targets |
| `test_04_coolify_install.yml` | Coolify installation on containers |
| `test_05_api_setup.yml` | API token generation, validation, persistence |
| `test_06_node_registration.yml` | SSH key distribution, server registration via API |
| `test_07_full_integration.yml` | Complete end-to-end workflow |

## Running Tests

### Quick Test (Container Lifecycle Only)

```bash
make docker-dev-test-quick
```

### Full Test Suite

```bash
make docker-dev-test-full
```

### Individual Tests

```bash
make docker-dev-test-container   # Container lifecycle
make docker-dev-test-ssh         # SSH connectivity
make docker-dev-test-makefile    # Makefile targets
make docker-dev-test-coolify     # Coolify installation
make docker-dev-test-api         # API setup
make docker-dev-test-node        # Node registration
make docker-dev-test-integration # Full integration
```

### Using ansible-playbook Directly

```bash
ansible-playbook -i inventory/ tests/docker-dev/test_01_container_lifecycle.yml
```

## Test Environment

Tests use an isolated configuration defined in `tests/docker-dev/conftest.yml`:

- **Network**: `172.29.0.0/16` (separate from production `172.28.0.0/16`)
- **Container Prefix**: `coolify-test-`
- **SSH Ports**: `2310`, `2320`, `2330` (not conflicting with dev environment)
- **Coolify UI Port**: `9000` (mapped from container's `8000`)

### Test Containers

| Container | IP | Purpose |
|-----------|-----|---------|
| controller | 172.29.0.10 | Coolify host |
| worker | 172.29.0.20 | Application server |
| builder | 172.29.0.30 | Build server |

For full integration tests, additional containers are created:
- `app-server-1` (172.29.0.20)
- `app-server-2` (172.29.0.21)

## Test Details

### Test 01: Container Lifecycle

Validates the `docker_dev` role:

- Docker availability check
- Container creation via docker-compose
- Health check verification
- Network connectivity between containers
- Idempotency (re-running doesn't create duplicates)
- Container stop/start cycle

### Test 02: SSH Connectivity

Validates SSH infrastructure:

- SSH key generation for each container
- Key file permissions (600 for private, 644 for public)
- SSH connectivity from host to containers
- Container-to-container SSH (controller to worker)

### Test 03: Makefile Targets

Validates all Makefile docker-dev targets:

- `docker-dev-up`
- `docker-dev-down`
- `docker-dev-status`
- `docker-dev-logs`
- `docker-dev-ssh`
- `docker-dev-clean`
- `docker-dev-rebuild`

### Test 04: Coolify Installation

Validates Coolify installation on containers:

- Download install script from `cdn.coollabs.io`
- Execute installation (15-minute timeout)
- Verify `.env` file created
- Verify Coolify containers running (coolify, postgres, redis)
- Verify UI accessible on port 8000
- Docker-in-Docker functionality
- SSH keys directory exists

### Test 05: API Setup

Validates Coolify API configuration:

- Enable API via PHP artisan tinker
- Create user and generate API token
- Verify `/api/v1/version` endpoint
- Test `/api/v1/servers` endpoint
- Test `/api/v1/projects` endpoint
- Verify invalid tokens are rejected (401)
- Token persistence in container filesystem

### Test 06: Node Registration

Validates server registration workflow:

- Generate SSH keypair for Coolify
- Register private key via `/api/v1/security/keys`
- Distribute public key to worker's `authorized_keys`
- Register server via `/api/v1/servers`
- Verify server appears in list
- Test duplicate registration handling (400 response)
- Trigger server validation
- Delete server and verify removal

### Test 07: Full Integration

End-to-end workflow with 4 containers:

1. **Phase 1**: Environment setup (4 containers)
2. **Phase 2**: Coolify installation
3. **Phase 3**: API setup and token generation
4. **Phase 4**: Register all 3 worker nodes
5. **Phase 5**: Create test project
6. **Phase 6**: Cleanup (delete project, servers, keys)
7. **Phase 7**: Verify all resources removed

## Configuration

### conftest.yml

Shared test configuration:

```yaml
test_docker_dev_name_prefix: "coolify-test"
test_docker_dev_network_name: "coolify-test-net"
test_docker_dev_network_subnet: "172.29.0.0/16"
test_docker_dev_network_gateway: "172.29.0.1"
test_docker_dev_compose_path: "./docker-test"
test_docker_dev_logs_path: "./docker-test-logs"
test_docker_dev_ssh_keys_path: "~/.ssh"

test_docker_dev_containers:
  - name: controller
    hostname: test-controller.lan
    ip: "172.29.0.10"
    labels: [controller]
    ports: ["2310:22", "9000:8000"]
  - name: worker
    hostname: test-worker.lan
    ip: "172.29.0.20"
    labels: [server]
    ports: ["2320:22"]
  - name: builder
    hostname: test-builder.lan
    ip: "172.29.0.30"
    labels: [builder, server]
    ports: ["2330:22"]
```

## Cleanup

Tests automatically clean up after themselves:

1. Destroy docker-compose containers
2. Remove test directories (`./docker-test`, `./docker-test-logs`)
3. Remove test SSH keys (if hostname contains `test-`)

If a test fails mid-execution, manual cleanup may be required:

```bash
docker compose -f ./docker-test/docker-compose.yml down -v
rm -rf ./docker-test ./docker-test-logs
```

## Troubleshooting

### Container Health Check Failures

If containers fail to become healthy:

```bash
# Check container logs
docker logs coolify-test-controller

# Check systemd status inside container
docker exec coolify-test-controller systemctl status

# Check Docker-in-Docker status
docker exec coolify-test-controller docker info
```

### Coolify Installation Timeout

Installation has a 15-minute timeout. If it fails:

```bash
# Check installation logs
docker exec coolify-test-controller cat /root/install.log

# Check Coolify containers
docker exec coolify-test-controller docker ps
```

### API Connection Issues

If API tests fail:

```bash
# Test API from host
curl -H "Authorization: Bearer TOKEN" http://172.29.0.10:8000/api/v1/version

# Check Coolify container logs
docker exec coolify-test-controller docker logs coolify
```

### Permission Denied During Cleanup

Some Docker-in-Docker files may be owned by root. Use sudo if needed:

```bash
sudo rm -rf ./docker-test ./docker-test-logs
```
