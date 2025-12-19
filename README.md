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

## Systems and Hosts

- **Marketing Website**: https://host.uk.com
- **Ordering System**: https://order.host.uk.com
- **Controllers**:
    - `noc.host.uk.com` (Production Controller - Runs Beszel, Sentry.io)
    - `lab.snider.dev` (Development Controller - Public URL), `dev.host.uk.com` (Endpoint)
- **Workers**:
    - `de.host.uk.com` (App Server - dc14)
    - `de2.host.uk.com` (App Server - dc13)
    - `build.de.host.uk.com` (Docker Build Server)

## S3 Storage
- **Endpoint**: `fsn1.your-objectstorage.com` (Hetzner S3)

