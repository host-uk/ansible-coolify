# Docker Development Environment

The `docker_dev` role creates a local Docker-based development environment that simulates a multi-node Coolify deployment.

## Overview

This role creates systemd-enabled Docker containers with Docker-in-Docker (DinD) support, allowing you to:

- Test Coolify installation in isolated containers
- Simulate multi-node deployments (controller + workers)
- Develop and test Ansible roles without cloud resources
- Run the full test suite locally

## Quick Start

```bash
# Start development environment
make docker-dev-up

# Check status
make docker-dev-status

# SSH into controller
make docker-dev-ssh

# View logs
make docker-dev-logs

# Stop environment
make docker-dev-down

# Full cleanup
make docker-dev-clean
```

## Architecture

### Default Container Configuration

| Container | Role | IP | SSH Port | Purpose |
|-----------|------|-----|----------|---------|
| controller | controller | 172.28.0.10 | 2210 | Coolify host |
| app-server-1 | server | 172.28.0.20 | 2220 | Application server |
| app-server-2 | server | 172.28.0.21 | 2221 | Application server |
| builder | builder, server | 172.28.0.30 | 2230 | Build server |

### Container Features

Each container includes:

- **Ubuntu 24.04** base image
- **systemd** init system (for service management)
- **Docker-in-Docker** with VFS storage driver
- **SSH server** with key-based authentication
- **Common tools**: curl, wget, git, jq, vim

### Network

Containers run on an isolated Docker network:

- **Development**: `172.28.0.0/16` (coolify-dev-net)
- **Testing**: `172.29.0.0/16` (coolify-test-net)

## Configuration

### Inventory Variables

Configure in `inventory/group_vars/development/docker_dev.yml`:

```yaml
docker_dev_enabled: true
docker_dev_name_prefix: "coolify-dev"
docker_dev_network_name: "coolify-dev-net"
docker_dev_network_subnet: "172.28.0.0/16"
docker_dev_network_gateway: "172.28.0.1"
docker_dev_compose_path: "./docker-dev"
docker_dev_logs_path: "./docker-dev-logs"
docker_dev_ssh_keys_path: "~/.ssh"

docker_dev_containers:
  - name: controller
    hostname: dev-controller.lan
    ip: "172.28.0.10"
    labels: [controller]
    resources:
      cpu: "2"
      memory: "4g"
    ports:
      - "2210:22"
      - "8000:8000"   # Coolify UI
      - "6001:6001"   # WebSocket
      - "6002:6002"   # Realtime

  - name: app-server-1
    hostname: dev-app-server-1.lan
    ip: "172.28.0.20"
    labels: [server]
    resources:
      cpu: "2"
      memory: "2g"
    ports:
      - "2220:22"

  - name: app-server-2
    hostname: dev-app-server-2.lan
    ip: "172.28.0.21"
    labels: [server]
    resources:
      cpu: "2"
      memory: "2g"
    ports:
      - "2221:22"

  - name: builder
    hostname: dev-builder.lan
    ip: "172.28.0.30"
    labels: [builder, server]
    resources:
      cpu: "4"
      memory: "4g"
    ports:
      - "2230:22"
```

### Container Labels

Labels determine how nodes are registered in Coolify:

| Label | Purpose |
|-------|---------|
| `controller` | Runs Coolify itself |
| `server` | Available for deployments |
| `builder` | Used for building images |

## Makefile Targets

| Target | Description |
|--------|-------------|
| `docker-dev-up` | Create and start containers |
| `docker-dev-down` | Stop containers (preserve data) |
| `docker-dev-status` | Show container status |
| `docker-dev-logs` | Tail container logs |
| `docker-dev-ssh` | SSH into controller |
| `docker-dev-clean` | Remove containers and volumes |
| `docker-dev-rebuild` | Rebuild and restart containers |

## SSH Access

SSH keys are automatically generated for each container:

```bash
# Keys stored in ~/.ssh/
~/.ssh/dev-controller.lan
~/.ssh/dev-controller.lan.pub

# SSH via Makefile
make docker-dev-ssh

# SSH directly
ssh -i ~/.ssh/dev-controller.lan root@localhost -p 2210
```

## Logs

Container logs are persisted to `./docker-dev-logs/<container>/`:

```
docker-dev-logs/
├── controller/
│   └── journal.log
├── app-server-1/
│   └── journal.log
├── app-server-2/
│   └── journal.log
└── builder/
    └── journal.log
```

## Docker-in-Docker

Each container runs its own Docker daemon:

```bash
# Check Docker status inside container
docker exec coolify-dev-controller docker info

# List containers inside controller (includes Coolify containers)
docker exec coolify-dev-controller docker ps

# Pull an image inside container
docker exec coolify-dev-controller docker pull nginx
```

**Note**: Docker-in-Docker uses the VFS storage driver for compatibility. This is slower than overlay2 but works reliably in nested container environments.

## Installing Coolify

After containers are running:

```bash
# SSH into controller
make docker-dev-ssh

# Download and run Coolify installer
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Or via Ansible
make dev-deploy
```

Access Coolify UI at `http://localhost:8000`

## Troubleshooting

### Containers Not Starting

```bash
# Check Docker daemon
docker info

# View container logs
docker logs coolify-dev-controller

# Check systemd inside container
docker exec coolify-dev-controller systemctl status
```

### SSH Connection Refused

```bash
# Check if SSH is running
docker exec coolify-dev-controller systemctl status ssh

# Check port mapping
docker port coolify-dev-controller

# Verify SSH key permissions
ls -la ~/.ssh/dev-controller.lan
```

### Docker-in-Docker Issues

```bash
# Check Docker daemon inside container
docker exec coolify-dev-controller systemctl status docker

# View Docker logs
docker exec coolify-dev-controller journalctl -u docker

# Check storage driver
docker exec coolify-dev-controller docker info | grep "Storage Driver"
```

### Port Conflicts

If ports are already in use:

1. Check what's using the port: `ss -tlnp | grep 2210`
2. Modify port mappings in inventory configuration
3. Rebuild containers: `make docker-dev-rebuild`

### Cleanup Issues

Docker-in-Docker creates files owned by root. Use sudo for cleanup:

```bash
sudo rm -rf ./docker-dev ./docker-dev-logs
```

## Resource Requirements

Minimum recommended resources:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB | 50 GB |

Coolify installation within the controller container requires additional resources for its internal containers (coolify, postgres, redis, etc.).
