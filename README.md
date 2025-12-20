# Bare Metal Coolify Infrastructure

This repository contains Ansible playbooks to set up and harden bare metal servers running Ubuntu 24.04 LTS for use with [Coolify](https://coolify.io).

## Project Structure

- `ansible/`: Contains Ansible configuration, inventory, and playbooks.
- `docs/`: Documentation for the setup.

## Quick Start

1. Update `ansible/inventory/inventory.yml` with your server details (Production and/or Development).
2. Ensure your SSH public key is in `/secrets/ssh_key.pub` (if using Docker).
3. Run the playbook with the desired limit: 
   - Production: `ansible-playbook -l production playbooks/coolify_create.yml`
   - Development: `ansible-playbook -l development playbooks/coolify_create.yml`

For more details, see [Quick Start Guide](docs/docs/quick_start.md).

## Systems and Hosts (Example)

- **Marketing Website**: https://example.com
- **Ordering System**: https://order.example.com
- **Controllers**:
    - `controller.example.com` (Production Controller)
    - `controller.lan` (Development Controller)
- **Workers**:
    - `worker1.example.com` (App Server)
    - `worker2.example.com` (App Server)
    - `build.example.com` (Docker Build Server)

## S3 Storage
- **Endpoint**: `fsn1.your-objectstorage.com` (S3 Compatible Storage)

