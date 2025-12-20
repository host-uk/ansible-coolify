# Bare Metal Coolify Infrastructure

This repository contains Ansible playbooks to set up and harden bare metal servers running Ubuntu 24.04 LTS for use with [Coolify](https://coolify.io).

## Project Structure

- `playbooks/`: Contains Ansible playbooks.
- `roles/`: Contains Ansible roles.
- `inventory/`: Contains inventory configuration.
- `docs/`: Documentation for the setup.

## Quick Start

1. Update `inventory/inventory.yml` with your server details (Production and/or Development).
2. Ensure your SSH keys are available in `~/.ssh/`.
3. Use Docker Compose for a consistent environment:
   - Start the container: `make up`
   - Open a shell: `make shell`
   - Run a playbook: `ansible-playbook -l production playbooks/coolify/create.yml`
4. Alternatively, run natively: 
   - Production: `ansible-playbook -l production playbooks/coolify/create.yml`
   - Development: `ansible-playbook -l development playbooks/coolify/create.yml`

For more details, see [Quick Start Guide](docs/quick_start.md).

## Systems and Hosts (Example)

- **Marketing Website**: https://example.com
- **Ordering System**: https://order.example.com
- **Controllers**:
    - `controller.example.com` (Production Controller)
    - `controller.lan` (Development Controller)
- **Workers**:
    - `worker1.example.com` (Server)
    - `worker2.example.com` (Server)
    - `build.example.com` (Docker Build Server)

## S3 Storage
- **Endpoint**: `fsn1.your-objectstorage.com` (S3 Compatible Storage)

